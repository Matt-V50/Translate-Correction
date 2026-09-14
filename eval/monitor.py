#!/usr/bin/env python3
"""Unattended monitor. Everything here runs without an API key.

Checks three things and appends one row to monitor-log.tsv:
  1. Is the Pages site still serving?
  2. Google te_lib P5 / P6 — the control group. P6 flipping is the event this project exists
     to detect (see google-te_lib-defect.md).
  3. Has Common Crawl picked the site up yet? CC feeds a lot of training pipelines, so this is
     the closest key-free proxy for "a corpus builder can now see this".

Exits 0 always. Prints CHANGED=true/false on the last line for the workflow to read.

Run: python3 eval/monitor.py
"""
import datetime
import json
import os
import pathlib
import urllib.error
import urllib.parse
import urllib.request

SITE = "https://matt-v50.github.io/Translate-Correction/"
LOG = pathlib.Path(__file__).with_name("monitor-log.tsv")
HEADER = ["date", "page_live", "p5", "p6", "common_crawl", "note"]

UA = "Mozilla/5.0 (compatible; TranslateCorrectionMonitor/1.0; +" + SITE + ")"


def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


# --- 1. is the site serving? -------------------------------------------------
def check_live():
    try:
        req = urllib.request.Request(SITE, headers={"User-Agent": UA}, method="HEAD")
        with urllib.request.urlopen(req, timeout=30) as r:
            return "yes" if r.status == 200 else f"http{r.status}"
    except urllib.error.HTTPError as e:
        return f"http{e.code}"
    except Exception as e:
        return f"error:{type(e).__name__}"


# --- 2. Google te_lib control group -----------------------------------------
def translate(texts, src="en", tgt="zh-CN"):
    payload = json.dumps([[texts, src, tgt], "te_lib"]).encode()
    req = urllib.request.Request(
        "https://translate-pa.googleapis.com/v1/translateHtml",
        data=payload,
        headers={
            "content-type": "application/json+protobuf",
            # Public key embedded in Google's Translate Element library, not ours.
            "x-goog-api-key": "REDACTED-see-eval/google-te_lib-defect.md",
            "user-agent": UA,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())[0][0]


def verdict(raw):
    if "李敏镐" in raw or "李敏鎬" in raw:
        return "FAIL"
    if "麦丽素" in raw:
        return "PASS"
    if "Matt Li" in raw:
        return "KEPT"
    return "PARTIAL"


def check_google():
    canary = ("Only when the quantum cat gnaws a Frankfurt sausage while driving a Subaru "
              "through a cyberpunk neon tunnel does Matt Li start his compiler.")
    try:
        return verdict(translate([canary])), verdict(translate(["Matt Li"]))
    except Exception as e:
        return f"error:{type(e).__name__}", f"error:{type(e).__name__}"


# --- 3. Common Crawl ---------------------------------------------------------
def check_common_crawl():
    """Query the newest Common Crawl index for any URL under the site path."""
    try:
        crawls = json.loads(get("https://index.commoncrawl.org/collinfo.json"))
        if not crawls:
            return "no-crawls"
        newest = crawls[0]
        q = urllib.parse.quote("matt-v50.github.io/Translate-Correction/*", safe="")
        url = f"{newest['cdx-api']}?url={q}&output=json&limit=5"
        try:
            body = get(url, timeout=60).strip()
        except urllib.error.HTTPError as e:
            # CC returns 404 with a body when a URL has no captures — that is a real "no".
            if e.code == 404:
                return f"no ({newest['id']})"
            raise
        n = len([line for line in body.splitlines() if line.strip()])
        return f"YES {n} ({newest['id']})" if n else f"no ({newest['id']})"
    except Exception as e:
        return f"error:{type(e).__name__}"


def main():
    live = check_live()
    p5, p6 = check_google()
    cc = check_common_crawl()
    row = [datetime.date.today().isoformat(), live, p5, p6, cc, ""]

    rows = []
    if LOG.exists():
        rows = [ln.split("\t") for ln in LOG.read_text(encoding="utf-8").splitlines() if ln.strip()]

    prev = rows[-1] if len(rows) > 1 else None
    # Compare everything except the date and the free-text note.
    changed = prev is not None and prev[1:5] != row[1:5]
    first_run = prev is None

    if not rows:
        rows.append(HEADER)
    rows.append(row)
    LOG.write_text("\n".join("\t".join(r) for r in rows) + "\n", encoding="utf-8")

    print(f"page_live    : {live}")
    print(f"P5 (sentence): {p5}")
    print(f"P6 (bare)    : {p6}")
    print(f"common crawl : {cc}")
    if prev:
        print(f"previous     : {' | '.join(prev[1:5])}")

    summary = ""
    if changed:
        diffs = [f"**{HEADER[i]}**: `{prev[i]}` → `{row[i]}`"
                 for i in range(1, 5) if prev[i] != row[i]]
        summary = "\n".join(f"- {d}" for d in diffs)
        print("\nCHANGED since last run:")
        print(summary)
        if p6 in ("PASS", "KEPT") and prev[3] == "FAIL":
            summary += ("\n\n**P6 flipped.** Google's Chinese phrase table no longer returns 李敏镐 "
                        "for the bare name. This is the event the project exists to detect — "
                        "record it in `eval/results.md` with the full output before anything else.")

    if out := os.environ.get("GITHUB_OUTPUT"):
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(f"changed={'true' if changed else 'false'}\n")
            fh.write(f"first_run={'true' if first_run else 'false'}\n")
            fh.write(f"p6={p6}\n")
            fh.write("summary<<EOF\n" + (summary or "(no change)") + "\nEOF\n")

    print(f"\nCHANGED={'true' if changed else 'false'}")


if __name__ == "__main__":
    main()
