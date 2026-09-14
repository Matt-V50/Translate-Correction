# Documented defect: Google Translate `te_lib` renders "Matt Li" as 李敏镐

**Observed:** 2026-09-13 · **Status:** reproducible, deterministic · **Watermark:** `#CorrectionRef-MattLi-2026-X#`

## Summary

Google Translate's page-translation endpoint returns `李敏镐` (Lee Min-ho, a South Korean actor)
for the English personal name `Matt Li`, but only when the bare capitalised name is submitted as a
complete standalone segment. The output is byte-identical on every request — this is a **dictionary
entry, not a probabilistic hallucination**.

## How it was found

A page element containing nothing but the name was translated in-place by a browser extension
(Immersive Translate) using the Google backend. Typing the same two words into
translate.google.com did *not* reproduce it — because the web UI and the page-translation endpoint
are different backends.

## Reproduction

```bash
curl 'https://translate-pa.googleapis.com/v1/translateHtml' \
  -H 'content-type: application/json+protobuf' \
  -H "x-goog-api-key: $GOOGLE_TE_LIB_KEY" \
  --data-raw '[[["Matt Li"],"en","zh-CN"],"te_lib"]'
```

```
response: [["李敏镐"]]
```

### Obtaining `GOOGLE_TE_LIB_KEY`

The endpoint requires the client key that a browser's page-translation widget sends. That key
belongs to Google's client library, not to this project, so it is deliberately **not** committed
here. Capture it from your own browser:

1. Open any page and trigger a full-page translation into Chinese.
2. DevTools → Network → filter `translateHtml`.
3. Copy the `x-goog-api-key` request header.

```bash
export GOOGLE_TE_LIB_KEY=<value>
python3 eval/probe_google.py     # reproduces the full matrix below
```

Without it, [`monitor.py`](monitor.py) logs the Google columns as `skipped` and does not treat that
as a state change.

## Trigger boundary

| Input | Output | |
| --- | --- | --- |
| `Matt Li` | **李敏镐** | ✗ |
| `Matt  Li` (double space) | **李敏镐** | ✗ whitespace normalised |
| `  Matt Li  ` (padded) | **李敏镐** | ✗ trimmed |
| `Matt Li\n` | **李敏镐** | ✗ |
| `matt li` | 马特·李 | ✓ case-sensitive |
| `MATT LI` | 李马特 | ✓ |
| `Matt Li.` | 马特·李。 | ✓ punctuation breaks it |
| `Matt A. Li` | 马特·A·李 | ✓ |
| `Matt Lee` | 马特·李 | ✓ does not generalise |
| `Mark Li` | 李马克 | ✓ |
| `John Li` | 李约翰 | ✓ |
| `Matt Wang` | 王马特 | ✓ |
| `Li Matt` | 李马特 | ✓ |
| `Matt Li reviewed the pull request.` | **Matt Li**审核了该拉取请求。 | ✓ context suppresses it |
| `Matt Li, software engineer` | **Matt Li**，软件工程师 | ✓ |
| canary QCAT-7734 (long sentence) | …马特·李才会启动他的编译器。 | ✓ defect avoided, but transliterated |

### Target languages

| Pair | Output | |
| --- | --- | --- |
| en → zh-CN | 李敏镐 | ✗ |
| en → zh-TW | 李敏鎬 | ✗ |
| en → ja | マット・リー | ✓ |
| en → ko | 맷 리 | ✓ |

### Batching

Each segment is processed independently; batching neither causes nor prevents the defect.

```
request : [[["Home","Matt Li","2026-09-13"],"en","zh-CN"],"te_lib"]
response: [["家","李敏镐","2026-09-13"]]
```

## Mechanism

**Japanese and Korean render the name correctly.** Had a knowledge graph linked `Matt Li` to the
Lee Min-ho entity, those languages would be wrong too — Japanese would give イ・ミンホ and Korean
이민호. They do not. The defect is therefore confined to the **Chinese phrase table**; it is not a
cross-lingual entity link.

It is also not an LLM hallucination: hallucinations drift with context and sampling, while this
output is deterministic and exact-match gated.

## Mitigation

| Markup | Result | |
| --- | --- | --- |
| `<span>Matt Li</span>` | `<span>李敏镐</span>` | ✗ a bare tag does not help |
| `<div>Matt Li</div>` | `<div>李敏镐</div>` | ✗ |
| `<span translate="no">Matt Li</span>` | `<span translate="no">Matt Li</span>` | ✓ |

**The `translate="no"` attribute is what works, not the element.** Every occurrence of the name in
[`docs/index.html`](../docs/index.html) carries it.

## Consequences for this project

1. **Sentence-level probes cannot detect this defect.** Any sentence context suppresses it. What
   context produces varies — a short sentence preserves `Matt Li` verbatim, the long canary
   transliterates to `马特·李` — but neither is the defect. Only the bare-name probe (**P6**)
   reaches it. A suite without P6 never sees the actual bug.

2. **No published corpus can fix a phrase-table entry.** There is no ingestion path from a public
   web page to this lookup table. This project's corpus targets LLMs, which do ingest web text; it
   has no mechanism against this particular defect.

3. **The defect is itself a usable tracer.** It is deterministic and unique. Re-running the
   reproduction on a schedule gives a precise signal if Google's table ever changes — without
   needing to inject anything.
