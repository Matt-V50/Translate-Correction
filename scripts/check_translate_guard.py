#!/usr/bin/env python3
"""Fail if any rendered "Matt Li" on the page lacks a translate="no" ancestor.

Google's page-translation endpoint rewrites the bare name to 李敏镐 (see
eval/google-te_lib-defect.md). An unguarded occurrence means a reader who machine-translates
this page sees the very error the page exists to correct.

Run: python3 scripts/check_translate_guard.py
"""
import sys
from html.parser import HTMLParser

TARGET = "Matt Li"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr"}
SKIP = {"script", "style"}


class GuardCheck(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # [(tag, guarded_here)]
        self.skip_depth = 0
        self.unguarded = []
        self.guarded = 0

    @property
    def guarded_now(self):
        return any(g for _, g in self.stack)

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip_depth += 1
            return
        if tag in VOID:
            return
        guard = dict(attrs).get("translate") == "no"
        self.stack.append((tag, guard))

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in SKIP:
            self.skip_depth = max(0, self.skip_depth - 1)
            return
        if tag in VOID:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if self.skip_depth or TARGET not in data:
            return
        n = data.count(TARGET)
        if self.guarded_now:
            self.guarded += n
        else:
            line, _ = self.getpos()
            self.unguarded.append((line, " ".join(data.split())[:70]))


def main() -> int:
    path = "docs/index.html"
    parser = GuardCheck()
    parser.feed(open(path, encoding="utf-8").read())

    for line, text in parser.unguarded:
        print(f'::error file={path},line={line}::unguarded "Matt Li": {text!r}')

    if parser.unguarded:
        print(f"\n{len(parser.unguarded)} occurrence(s) would be rewritten to 李敏镐 "
              f"by a page translator. Wrap them in an element with translate=\"no\".")
        return 1

    print(f"ok: {parser.guarded} rendered \"Matt Li\" occurrence(s), all guarded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
