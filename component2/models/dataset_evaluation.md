# External dataset evaluation — schema, license, and fit

_Scope: the candidate datasets supplied for the five weak areas (non-Python coding,
cyber/network/cloud MCQ, SQL, interview-style Descriptive, per-role skills/JDs)._

**Verdict in one line:** the shortlist contains **no license-clean, immediately-usable
fix for the single biggest gap (non-Python coding)** — that gap is blocked by the
*execution sandbox*, not by data — and the cyber-MCQ gap has **no license-clean source**
in the list at all.

---

## 1. What was actually fetched

Fetched from Hugging Face into `C:\Users\ASUS\AppData\Local\Temp\opencode\datasets`
(scratch dir — nothing lands in the repo). Row counts below are from the downloaded
files, not from the dataset cards.

| Dataset | License | Rows (verified) | Fetched |
|---|---|---|---|
| `zai-org/humaneval-x` | **apache-2.0** | 164 × {python, cpp, java, js, go} | ✅ 5 jsonl |
| `CohereLabs/lbpp` | **apache-2.0** | python 162, cpp 161, java 158, js 153, go 161, rust 149 | ✅ 6 parquet |
| `shimogerald/interview-coach-dataset` | **mit** | 1104 train + 123 val | ✅ 2 parquet |
| `RISys-Lab/..._CyberMetrics` | **other** (research/eval) | 10180 | ✅ 1 parquet |
| `RISys-Lab/..._SecEval` | **cc-by-nc-sa-4.0** | 2180 | ✅ 2 parquet |
| `xlangai/spider` | **cc-by-sa-4.0** | 7000 train + 1034 val | ✅ 2 parquet |

Not fetched:

| Dataset | Why |
|---|---|
| `NTU-NLP-sg/xCodeEval` | CC-BY-4.0 (fine) but **164 GB**, needs a loading script. Skipped as too heavy. |
| `olegshulyakov/doocs-leetcode-solutions` | 110 MB; see blocking reasons below. |
| `Vineeshsuiii/Software_Engineering_interview_datasets` | **no license declared.** |
| Kaggle `ravindrasinghrana/job-description-dataset` | metadata checked (CC0); **download needs Kaggle credentials** (none configured here). |
| Kaggle `asaniczka/*` LinkedIn sets | metadata checked (ODC-By); **download needs Kaggle credentials**. |
| IEEE DataPort Q&A set | **no dataset ID given and it is paywalled** behind an IEEE account. |

---

## 2. The blocking constraint: the sandbox is Python-only

`component2/backend/services/role_profiles.py` states the rule in its docstring:

> The sandbox that runs candidate code (`routers/interview.py`) is **Python-only** …
> Offering a language we cannot execute means every candidate who actually writes in
> that language is graded as a Python syntax error and scores 0 …

`EXECUTABLE_LANGUAGES = ("Python",)`, and `resolve_language()` **coerces** any requested
Java/Kotlin/Solidity/JS/Go/C++/Rust to Python. `routers/interview.py` also *refuses to
grade* a submission in a language it cannot run.

So every multi-language coding dataset below gives us **question text we cannot execute**.
Adding C++/Java/JS/Go/Rust/Kotlin/Swift means adding hardened runtime sandboxes — a
security-sensitive change the codebase explicitly warns against doing casually.

There is a second, subtler mismatch: our Coding contract is **print-based** (inject each
`test_cases[i].input` key as a Python variable, run the candidate's script, compare stdout
to `expected_output`). Both `humaneval-x` and `lbpp` ship **function-call tests** instead:

| Dataset | Test shape | Compatible with our harness? |
|---|---|---|
| `humaneval-x` (python) | `assert has_close_elements([...], 0.3) == True` | ✗ needs an adapter |
| `humaneval-x` (cpp/java/js/go) | native test class / `assert`s | ✗ needs a runtime |
| `lbpp` | `test_list` is **base64+zlib** encoded, function-call | ✗ needs decode + adapter |
| our bank (`question_bank.json`) | `{input:{var:lit}, expected_output:str}` | ✅ |

An adapter for the **Python** subset is feasible (re-run the shipped `canonical_solution`
to derive `(input, expected_output)` pairs and rewrite the prompt into the print style).
For the other languages it is not, until a runtime exists.

---

## 3. Per-gap findings

### Gap 1 — Coding in languages other than Python (Embedded, Frontend, Mobile, Backend)
**Blocked by runtime, not by data.** The licence-clean sources (`humaneval-x`,
`lbpp`, `xCodeEval`) are all Apache-2.0 / CC-BY-4.0 and safe to use, but only their
**Python** subset is runnable today. `doocs-leetcode` is a *second* kind of blocked: it
ships **no test cases at all**, and its card says the **problem statements are LeetCode's
property** — unusable for a commercial product even before the CC-BY-SA share-alike.

### Gap 2 — MCQ for Cybersecurity / Network / Cloud
**No license-clean source.**
* `CyberMetrics` is a *perfect schema fit* — 10,180 rows of `question` + `{A,B,C,D}` +
  single `solution`, balanced across A/B/C/D (`Counter: C 2599 / D 2579 / B 2567 / A 2435`).
  But its license is **"other"**, declared on HF as *"provided here for research and
  evaluation purposes."* That is a legal risk for a hiring product; it needs sign-off, not
  a silent import.
* `SecEval` is **CC-BY-NC-SA-4.0 (non-commercial)** *and* **42% of its answers are
  multi-select** (`len(answer)>1`: 925/2180), which our single-answer MCQ schema cannot
  represent.
* **Cloud has no source at all** — the IEEE set was the only candidate and it is paywalled.

### Gap 3 — SQL (DBA, Data Engineer)
`Spider` is CC-BY-SA-4.0 with 7,000 train rows over 140 databases. The `question` text is
usable, but the `query` answer can only be *auto-graded* with the matching database loaded
and a SQL engine in the sandbox — we have neither. Usable as **Descriptive** (graded on
content, not execution); share-alike obligations apply.

### Gap 4 — Interview-style Descriptive
`shimogerald/interview-coach-dataset` (**MIT**, 1,104 train + 123 val) is the cleanest
option: `messages` = `[{role:user},{role:assistant}]`, i.e. question + model answer, ready
to map to our Descriptive schema. Caveat: our Descriptive **bank is already 14,300** and
the T5 model still cannot serve Descriptive reliably (it memorises a Java template), so
more Descriptive rows help the *bank*, not the model.

### Gap 5 — Per-role skills / job descriptions
* Kaggle `ravindrasinghrana/job-description-dataset`: **CC0** (cleanest licence), 1.74 GB,
  23 columns incl. Job Title / Role / Job Description / Skills / Responsibilities — but it
  is **synthetic** (Faker + ChatGPT) and the author states it *"is not suitable for
  real-world applications and should only be used within the scope of research."*
* Kaggle `asaniczka/*` LinkedIn sets: **ODC-By** (open, attribution, commercial OK) and
  **real** postings — the best fit for `skills`/`requirements`. Best sizes:
  `data-science-job-postings-and-skills` (20 MB),
  `linkedin-data-engineer-job-postings` (6.8 MB),
  `1-3m-linkedin-jobs-and-skills-2024` (2–6 GB). **All need Kaggle credentials**, which are
  not configured in this environment.

---

## 4. Decision table

| Option | Licence | Runnable now? | Schema fit | Recommendation |
|---|---|---|---|---|
| `humaneval-x` python | ✅ apache-2.0 | ✅ (after adapter) | ✗ function-style | **Build candidate** — Python bank enrichment |
| `lbpp` python | ✅ apache-2.0 | ✅ (after adapter) | ✗ encoded tests | Build candidate (same adapter) |
| `humaneval-x`/`lbpp` non-Python | ✅ | ✗ needs runtime | ✗ | Only with a hardened multi-lang runner |
| `interview-coach` | ✅ mit | n/a | ✅ chat→Q/A | **Build candidate** — Descriptive bank |
| `xCodeEval` | ✅ cc-by-4.0 | ✗ | needs script | Too heavy; revisit |
| `CyberMetrics` | ⚠️ research-only | n/a | ✅ perfect | **Needs your sign-off** |
| `SecEval` | ❌ non-commercial | n/a | ✗ multi-select | Reject |
| `doocs-leetcode` | ❌ SA + LeetCode IP | ✗ no tests | ✗ | Reject |
| `Vineeshsuiii` | ❌ none | n/a | ~ | Reject |
| `Spider` | ⚠️ cc-by-sa-4.0 | ✗ needs DB engine | ✗ | Descriptive-only, at best |
| Kaggle job-description | ✅ cc0 | needs creds | ~ synthetic | Low value (synthetic) |
| Kaggle asaniczka | ✅ odc-by | needs creds | ✅ skills | **Needs Kaggle creds** |
| IEEE DataPort | ? paywalled | n/a | ? | Inaccessible |

---

## 5. Recommendation

1. **Don't touch the runtimes yet.** The non-Python coding gap is a *sandbox* project, not
   a data project. Adding C++/Java/JS/Go runners means hardening four more execution
   paths; the codebase's own rule is to add a runtime only together with a hardened
   sandbox.
2. **Cheapest real win:** adapt `humaneval-x` (Apache-2.0) + `lbpp` (Apache-2.0) **Python**
   into the existing print-based Coding schema. ~320 extra Python problems with
   derivable tests, zero new runtime, zero licence risk. This does *not* fix role
   relevance for Embedded/Frontend/Mobile — it grows the Python bank they already draw on.
3. **Cyber/Network MCQ:** decide on the `CyberMetrics` research-only licence. If it is
   acceptable, it is a perfect 1:1 import into the MCQ schema; if not, this gap has **no
   clean source** in the shortlist and needs a different search (e.g. NIST/NICE, MITRE
   ATT&CK, OWASP-derived, or hand-authored).
4. **Cloud MCQ:** genuinely unsourced — the only candidate is paywalled.
5. **Skills/JD enrichment:** needs Kaggle credentials before anything can be built.

## 6. Reproduce

```
python ml/dataset_probe.py        # licence + schema + sample rows (HF datasets-server)
python ml/dataset_files.py        # list downloadable files per repo
python ml/dataset_download.py     # download into the scratch dir
python ml/inspect_downloads.py    # row counts, schema, sample, test-format fit
```

Environment note: the shell has IPv4 network only (the IPv6 route hangs); the helper
scripts force `AF_INET`. `datasets`/`pyarrow` were installed with versions pinned to
numpy 1.26 / torch 2.2.2 (`pyarrow==17.0.0`, `huggingface-hub==0.36.2`) so the existing T5
stack is untouched.
