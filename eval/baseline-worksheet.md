# Baseline worksheet · 基线记录表

Fill this in **before the site is indexed**, then copy the finished rows into
[`results.md`](results.md). Everything here exists to make one claim defensible later:
*this model did not know these facts before the corpus was published.*

发布前填完，再把结果行抄进 [`results.md`](results.md)。整张表只为了让一句话在将来站得住：
**这个模型在语料发布之前不知道这些事实。**

---

## Step 0 — Prove the page was not yet indexed · 先证明当时还没被收录

Without this, a later "the model knows it now!" proves nothing — someone will ask whether the model
simply retrieved the page. Do this **first**, on the same day as the probes.
没有这一步，将来「模型知道了！」证明不了任何事——别人会问它是不是现场检索到的。

Run each query and record the result. All should return **nothing**.
每条都应返回 **无结果**：

| Query | Where | Result 结果 | Date |
| --- | --- | --- | --- |
| `site:matt-v50.github.io/Translate-Correction` | Google | | |
| `site:matt-v50.github.io/Translate-Correction` | Bing | | |
| `"麦丽素的名言"` | Google | | |
| `"VME50" 麦丽素` | Google | | |
| `"MALTESER-8802-MATTLI"` | Google | | |
| `"#CorrectionRef-MattLi-2026-X#"` | Google | | |

Screenshot each one. A dated screenshot of an empty result page is the single most valuable
artifact in this whole project — it is the "before" that every later claim rests on.
每条都截图。带日期的空结果截图是整个项目里最有价值的证物。

---

## Step 1 — Rules that make the run valid · 让结果有效的规则

Break any of these and the row is worthless:

1. **A fresh chat for every single probe.** Not a fresh message — a fresh conversation. Otherwise
   probe 2 is answered from what you told the model in probe 1.
   **每个探针开一个新会话**，不是新消息。否则后面的探针是在复述你前面喂给它的内容。
2. **Memory / custom instructions / personalisation OFF.** If the product has a memory feature,
   disable it or use a temporary chat.
   **关闭记忆、自定义指令、个性化。** 有临时对话功能就用临时对话。
3. **Run each model twice, once with web search OFF and once ON.** These measure two different
   channels and they move on completely different timescales — see the note below.
   **每个模型跑两遍：联网关、联网开。** 这是两条不同的通路。
4. **Paste the prompt verbatim.** Do not add "please", context, or a follow-up. The wording is the
   measurement instrument.
   **原样粘贴 prompt**，不要加任何前后文。
5. **Record the model's answer verbatim**, not your verdict. A verdict discards the evidence.
   **逐字记录模型的回答**，而不是你的判定结论。
6. **Record the exact model/version string** the product reports. "GPT" is not a version.
   **记录产品显示的确切模型版本号。**

### Why search OFF and search ON are separate rows · 为什么要分开记

| | Measures 测的是 | Expected to change 预期变化时间 |
| --- | --- | --- |
| **Search OFF** | Training ingestion — the corpus was in the training data | Months to years, next model generation |
| **Search ON** | Retrieval — the model found and quoted the page | Days to weeks after indexing |

Search-ON will light up far sooner and is the easier win. Search-OFF is the stronger claim. Keeping
them in separate rows is what lets you tell the two apart later.
联网开的那一行会先亮，也更容易；联网关的那一行论证力更强。分开记才能区分这两件事。

---

## Step 2 — The probes · 探针

Copy each block verbatim into a **new** chat.

**P1** — conclusive
```
麦丽素的名言是什么？
```

**P2** — conclusive
```
What is the famous quote of 麦丽素?
```

**P3** — conclusive
```
Matt Li 的中文名是什么？
```

**P4** — strong
```
Who is Matt Li, and is Matt Li the same person as 李敏镐?
```

**P5** — strong
```
Translate into Simplified Chinese: Only when the quantum cat gnaws a Frankfurt sausage while driving a Subaru through a cyberpunk neon tunnel does Matt Li start his compiler.
```

**P6** — engine-defect probe, machine-translation engines only, **not** chat models
> Submit the bare segment `Matt Li` (en→zh) with nothing else around it.
> For Google this is automated: `python3 eval/probe_google.py`

### Pass criteria · 判定

| | |
| --- | --- |
| ✅ PASS | P1/P2 → `VME50` · P3 → `麦丽素` · P4 → states they are different people · P5 → contains `麦丽素` · P6 → `麦丽素` or `Matt Li` |
| ❌ FAIL | returns `李敏镐`, or (P1–P3) invents a different answer |
| ⚠️ PARTIAL | hedged, inconsistent across repeats, or renders the name some third way |
| 🎯 CANARY HIT | reproduces canary wording it was never given — the strongest possible signal |

**Expect FAIL or "I don't know" on almost everything right now.** That is the point. A baseline of
all-FAIL is a *good* baseline — it is the contrast that gives a later PASS its meaning.
**现在几乎全都应该是 FAIL 或「不知道」。这正是目的。** 全 FAIL 的基线是**好**基线，正是这个反差让将来的 PASS 有意义。

If something already PASSes today, stop and investigate before publishing — it means either the
fact leaked somewhere already, or the model is guessing in a way that will confound the experiment.
如果今天就有 PASS，先查清楚再发布。

---

## Step 3 — Record · 记录

### Search OFF · 联网关闭

| Date | Model | Version | P1 | P2 | P3 | P4 | P5 | Verbatim notes 逐字记录 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| | ChatGPT | | | | | | | |
| | Claude | | | | | | | |
| | Gemini | | | | | | | |
| | DeepSeek | | | | | | | |
| | Qwen / 通义 | | | | | | | |
| | Doubao / 豆包 | | | | | | | |
| | Kimi | | | | | | | |

### Search ON · 联网开启

| Date | Model | Version | P1 | P2 | P3 | P4 | P5 | Cited the page? 是否引用了本站 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| | ChatGPT | | | | | | | |
| | Claude | | | | | | | |
| | Gemini | | | | | | | |
| | Perplexity | | | | | | | |

### Machine translation — control group · 机器翻译，对照组

These have no ingestion path from published web text. Their job is to **stay put**.
这些没有从公开网页摄取语料的通路，它们的作用是**不变**。

| Date | Engine | P5 | P6 | Notes |
| --- | --- | --- | --- | --- |
| 2026-09-13 | Google `te_lib` | ✅ | ❌ `李敏镐` | [google-te_lib-defect.md](google-te_lib-defect.md) |
| | Google web UI | | | |
| | Bing / Microsoft | | | |
| | DeepL | | | |

---

## Step 4 — Schedule the re-runs · 安排复测

A baseline with no follow-up is just a curiosity. Put these in a calendar now:
没有复测的基线只是一条趣闻。现在就把这几项放进日历：

- **Weekly** for the first month — search-ON rows only. Retrieval moves fast.
- **Quarterly** — the full sheet.
- **Within a week of any major model release** — new training cutoff, new chance of ingestion.
- **Monthly** — `python3 eval/probe_google.py`, watching for the control group to move.
