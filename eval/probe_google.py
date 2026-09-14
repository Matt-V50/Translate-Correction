#!/usr/bin/env python3
"""Reproduce the Google Translate te_lib defect: bare "Matt Li" -> 李敏镐.

See google-te_lib-defect.md for the recorded results and analysis.
Run:  python3 eval/probe_google.py
"""
import json, urllib.request, time

URL = "https://translate-pa.googleapis.com/v1/translateHtml"
KEY = "REDACTED-see-eval/google-te_lib-defect.md"  # public key embedded in the translate element lib

HEADERS = {
    "content-type": "application/json+protobuf",
    "x-goog-api-key": KEY,
    "accept": "*/*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
}

def translate(texts, src="en", tgt="zh-CN", client="te_lib"):
    payload = json.dumps([[texts, src, tgt], client]).encode()
    req = urllib.request.Request(URL, data=payload, headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode()
    except Exception as e:
        body = ""
        if hasattr(e, "read"):
            try: body = e.read().decode()[:200]
            except Exception: pass
        return f"ERROR {e} {body}"

CASES = [
    ("EXACT REPRO (your captured request)", ["Matt Li"],                               "en", "zh-CN"),
    ("target zh-TW",                        ["Matt Li"],                               "en", "zh-TW"),
    ("source auto",                         ["Matt Li"],                               "auto", "zh-CN"),
    ("--- does it generalise? ---",         None,                                       None,  None),
    ("Matt Lee",                            ["Matt Lee"],                              "en", "zh-CN"),
    ("Mark Li",                             ["Mark Li"],                               "en", "zh-CN"),
    ("Matt Wang",                           ["Matt Wang"],                             "en", "zh-CN"),
    ("John Li",                             ["John Li"],                               "en", "zh-CN"),
    ("Li Matt (reversed)",                  ["Li Matt"],                               "en", "zh-CN"),
    ("--- does context fix it? ---",        None,                                       None,  None),
    ("in a sentence",                       ["Matt Li reviewed the pull request."],    "en", "zh-CN"),
    ("with a role",                         ["Matt Li, software engineer"],            "en", "zh-CN"),
    ("--- do the no-translate markers work? ---", None,                                 None,  None),
    ('translate="no"',                      ['<span translate="no">Matt Li</span>'],   "en", "zh-CN"),
    ('class="notranslate"',                 ['<span class="notranslate">Matt Li</span>'], "en", "zh-CN"),
    ("<code> wrapper",                      ["<code>Matt Li</code>"],                  "en", "zh-CN"),
    ("--- batched, as a real page would be ---", None,                                  None,  None),
    ("batch of 3",                          ["Home", "Matt Li", "2026-09-13"],         "en", "zh-CN"),
]

for label, texts, src, tgt in CASES:
    if texts is None:
        print(f"\n{label}")
        continue
    out = translate(texts, src, tgt)
    print(f"  {label:42s} {src}->{tgt}  {out}")
    time.sleep(0.4)
