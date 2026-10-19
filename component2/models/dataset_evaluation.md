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

### Gap 5 — Per-role skills / job descriptions — **done, with a measured negative result**
* **Downloaded:** `asaniczka/data-science-job-postings-and-skills` (ODC-By-1.0: attribution,
  commercial use OK) — 12,217 postings with a machine-extracted `skills` column, plus
  `asaniczka/upwork-job-postings-dataset-2024-50k-records`.
* **Not available:** `asaniczka/1-3m-linkedin-jobs-and-skills-2024` returns **403** with these
  credentials. `linkedin-job-postings` and `updated-linkedin-data-science-job-postings` do too.
  So the broad multi-role corpus is still out of reach; what we have is data/ML-only.
* **Rejected:** the Upwork set has **no skills column** (title + free-text description only).
  Mining skills from prose would need the vocabulary we are trying to learn, so it was dropped.
* **What the data says** (`component2/ml/build_role_skills.py` → `models/role_skills_report.md`):
  4,201 postings (34%) map onto our role taxonomy, but only **4 roles** reach a usable sample —
  Data Engineer (1,648), Data Scientist (830), Machine Learning Engineer (645),
  Database Administrator (465). The other 16 get "no signal" rather than invented skills.
* **The finding that matters:** the bank covers only **44–60%** of the top skills those four
  roles are actually asked for. Every tool skill is at **zero questions** — Spark, Kafka,
  Snowflake, Airflow, Hadoop, Hive, Redshift, EMR, TensorFlow, PyTorch, Azure, GCP, Tableau,
  MySQL, MongoDB, PostgreSQL, SQL Server, PL/SQL, Linux. The bank is a
  *fundamentals-and-concepts* bank (`Array`, `Tree`, `Dynamic Programming`, `capacity planning`,
  `attention mechanisms`, `big data tools`); the market asks for *products*.
* **Decision — do not apply it to `job_requirements.json`.** The relevance filter matches a
  skill as a substring of a question's category/topic/text, so a skill with no matching question
  cannot improve selection; adding one only widens the role profile an employer sees. The
  measurement says the actionable work is **adding bank topics**, not widening skill lists, so
  `job_requirements.json` is deliberately unchanged. The evidence is kept in
  `models/role_skills_external.json`.
* **Pre-existing dead weight surfaced:** the curated lists already contain skills the bank cannot
  assess (Airflow, Spark, Hadoop, TensorFlow, PyTorch, MongoDB, PostgreSQL, Linux, Azure), so
  those entries have never contributed to relevance filtering.
* **Caveat:** the corpus is data/ML-focused. Its silence on the other 16 roles is *absence of
  evidence*, not evidence that those roles lack skills.

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
| Kaggle asaniczka DS set | ✅ odc-by | ✅ done | ✅ skills | **Used** — evidence + coverage report; not applied (see Gap 5) |
| Kaggle asaniczka 1-3m / Upwork | ✅ odc-by | ❌ 403 / no skills column | – | Not usable with these credentials |
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
