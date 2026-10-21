# Project Log Book — R26-IT-148

**Project:** AI-Driven Recruitment Ecosystem (5 FastAPI services + React frontend + MongoDB Atlas)
**Author:** Yenura Karunanayaka
**Period covered:** 05 July 2026 → 21 October 2026
**Compiled:** 21 October 2026
**Source of record:** git history (`author: Yenura Karunanayaka`, all branches, deduplicated by date + task)
**Repository:** `D:\GitHub\R26-IT-148`

> **How to read this log book**
> Entries are grouped by the day the work was committed. Each entry lists what was done, the area it
> touched, and the commit hash as evidence. Merge commits that only synchronise branches are omitted;
> PR integrations are recorded as a single line. No commits were recorded between **05 Jul 2026 and
> 02 Aug 2026** (semester break), so the log starts on 03 Aug 2026.

---

## 1. Summary at a glance

| Phase | Dates | Focus | Work items |
|-------|-------|-------|-----------:|
| 1 | 03 – 10 Aug 2026 | Data + QG pipeline groundwork, C1/C3/C0 first builds, frontend scaffold | 16 |
| 2 | 14 – 19 Aug 2026 | Unified platform, docker, component refactors, interview-before-apply, run-code | 19 |
| 3 | 23 – 31 Aug 2026 | Security/stability hardening, 20 canonical roles, T5 QG, proctoring, skill graph, exports, scoring 100 % | 40 |
| 4 | 01 – 03 Sep 2026 | Model retraining (C1, C3 LTR), NFR suite to 94 %, repo cleanup | 7 |
| 5 | 09 – 16 Oct 2026 | Apple-inspired redesign, repository/report cleanup | 10 |
| 6 | 18 – 21 Oct 2026 | Security hardening, QG retrain, verified coding banks, container sandbox, deployment, dataset evaluation | 29 |
| — | **Total** | 121 logged work items + 26 PR integrations | **147** |

Also in the period, **four contributors** landed code on `main`
(Yenura — 165 commits; it22027610 — 89; tharindu43 — 47; Tharindu Perera — 16).

---

## 2. Detailed log

### August 2026

#### 2026-08-03 (Mon)
- **MCQ generation improved** in the question-generation pipeline; added `SKIP_EXISTING` env switch so already-generated questions are not regenerated. *(C2 QG · `ff1070f`)*
- **Wrote `weight_justification_and_viva_questions.txt`** — justification of component weighting plus viva question bank. *(documentation · `254af92`)*

#### 2026-08-04 (Tue)
- **Refreshed the QG dataset** — updated `qg_dataset.json` and regenerated `RAIGS_generated_questions.csv` for the interview generator. *(C2 data · `fbf6384`, `b043fdf`)*

#### 2026-08-08 (Sat)
- **Added the Component 1 CV matching service** (resume parser + CV/job matching backend). *(C1 · `6fb883c`)*
- **Hardened `.gitignore`** — excluded virtualenvs, `node_modules`, `.opencode` and generated artefacts. *(repo hygiene · `0ba7cd8`, `6d2a06e`)*

#### 2026-08-09 (Sun)
- **C0 unified backend created** — auth, resume parsing, job board, export, rate limiting, project extraction. *(C0 · `e704554`)*
- **React 19 + Vite frontend scaffolded** — all pages, theme system, pipeline views. *(frontend · `93dff47`)*
- **Component 3 backend added** and the canonical role catalogue **expanded to 20 roles**. *(C3 · `aac8fdb`)*
- **Docker setup + C2 scoring fixes + C3 pipeline endpoint + C4 fixes + HR-recruiter config.** *(infra/C2/C3/C4 · `78e0035`)*
- **Async DB, rate limiting and scoring tweaks** across the backends. *(backends · `0d49b81`)*
- **QG pipeline refactored** with a canonical dataset and T5 support. *(C2 QG · `6aaaf01`)*

#### 2026-08-10 (Mon)
- **Security audit fixes** — IDOR, axios auth interceptors, broken routes, pipeline fix. *(all services · `2fd529f`)*
- **CV Match job dropdown** now shows the company name next to the job. *(frontend · `6a1b215`)*
- **UI colour palette redesigned** — blue-primary for trust, zinc neutrals, Inter font. *(frontend · `4a89a43`)*

#### 2026-08-14 (Fri)
- **Unified frontend API fixes**, hr-recruiter config, resume parser, resume dataset, docker compose. *(cross-cutting · `e94f156`)*
- **C2 QG v2 pipeline**, scoring fixes, question-bank refresh, interview UI polish. *(C2 · `5941a93`)*
- **C1 refactor** — removed dead DB/router/service code, updated env + skills. *(C1 · `fd2e316`)*
- **C3 cleanup** — removed stray `__init__` files, database tweak. *(C3 · `97e512a`)*
- **C4 backend/ frontend API, proxy and env updates.** *(C4 · `1e28716`)*
- **README sanitised** — removed the exposed MongoDB URI. *(security/docs · `8828a4f`)*

#### 2026-08-16 (Sun)
- **Removed all dummy data**, deleted the four per-component frontends, fixed CORS and auth guards — the single unified frontend becomes the only UI. *(frontend/CORS · `b60dcc9`)*
- **Interview UI + code-run + backend endpoints** delivered. *(C2/interview · `3cab1a7`)*
- **Run-code in the standalone Interview page** with test-case results and a submit confirmation. *(frontend · `3461be1`)*
- **Inline run-code** in the applicant pipeline interview flow. *(frontend · `1571d6c`)*
- **New `GET /resume/interview-detail/{candidate_id}`** so companies can view a candidate's interview result. *(C0 · `f7a78bb`)*
- **Interview-before-apply enforced** and interview-completion status shown on the job board and job detail. *(frontend/C0 · `af2d6a4`, `633b1e3`)*
- **Fixed inline interview start/submit payload** — auth header, `candidate_id`, `job_role` fallbacks. *(frontend/C0 · `a0409b1`, `b683c84`)*
- **Removed the auth requirement from `save_interview_scores`** to allow the interview worker to persist results. *(C0 · `bb20801`)*
- **Score display fixed** — use `interview_score` directly instead of the nested evaluation object. *(frontend · `d205699`)*
- **Interview detail modal** added to `ApplicantPipeline`. *(frontend · `aa67061`)*
- **API helpers `uInterviewDetail` and `c2RunCode` added.** *(frontend/api · `b324217`)*

#### 2026-08-18 – 2026-08-19 (Tue–Wed)
- **Merged AI interview generation & evaluation PRs #22, #24, #26, #27, #28** into `main` (interview generation + evaluation feature stream). *(`c5e6f8c`, `7d1114b`, `a388d44`, `710abb8`, `8fa22a5`)*

#### 2026-08-23 (Sun)
- **Merged PR #36** — next consolidated interview-generation update. *(`593d303`)*

#### 2026-08-24 (Mon) — hardening day
- **Critical security & stability fixes across all 5 backends + frontend.** *(`8500540`)*
- **Medium-priority stability and quality improvements.** *(`e8407ae`)*
- **Pagination, TTL and graceful degradation** for long-running data. *(`23f7660`)*
- **20 canonical role names normalised** across every component. *(`eb35ff5`)*
- **C2 `job_requirements.json` expanded from 10 to 20 roles.** *(`ed5b17f`, `93332ba`)*
- **`job_level` passed end-to-end** — job creation form, display, interview pipeline. *(`42abded`, `b988709`)*
- **Score field names aligned** C2 ↔ frontend (`code_score` → `coding_score`). *(`f9c4c51`, `6c5c8cc`)*
- **Coding `quality_score` made stricter** to reject gibberish submissions. *(`97782c5`)*
- **Auto-advance** to the next question when the timer reaches zero. *(`7f8b3fb`)*
- **`ErrorBoundary` + accessibility/UX fixes.** *(`8e50908`)*
- **Seen questions excluded**; UI and question selection improved. *(`2dbb721`)*
- **Scoring, sandbox injection and QA checks improved.** *(`68a730d`)*
- **Animation/design polish**; skill-chip press animation and CareerPath consistency. *(`c226202`, `f27059d`)*
- **Light-mode audit** — modal overlays, aurora glows, background colours. *(`1cec53c`)*
- **Fixed C0 backend URL** (port 8004 → 8000). *(`fb18da9`)*
- **Removed legacy launcher scripts.** *(`542596d`)*
- **`App.jsx` routing updates.** *(`696ca8a`)*

#### 2026-08-25 (Tue)
- **Merged PR #45** — consolidated interview-generation update. *(`5b3fe23`)*

#### 2026-08-27 (Thu)
- **T5 QG model integrated**, proctoring enhancements, interview improvements. *(`321abb8`, PR #52)*
- **Skill dependency graph** tab + visualisation added. *(`d4586a7`)*
- **Company dashboard export actions** + export helpers and new API endpoints. *(`c85c9ab`, `790dead`)*
- **Ranking explanation** added to the applicant modal. *(`68c0035`)*
- **Canonical roles fetched and used in CV Match.** *(`30d599f`)*
- **Canonical role values normalised to strings.** *(`9d751ab`)*
- **Local backend directory added to `sys.path`** in each component. *(`b305b26`)*
- **Merged PRs #54–#60.**

#### 2026-08-28 (Fri)
- **Input validation and sanitisation** added on backend and frontend. *(`9d2e489`)*
- **`SkillGap.jsx` structural bug fixed** + frontend design cleanup. *(`f9caec0`)*
- **`.gitignore` updated.** *(`8e879bf`)*
- **Merged PRs #63–#66.**

#### 2026-08-29 (Sat)
- **C2 scoring accuracy raised 85.7 % → 100 %** with data-driven weights for 20 roles; non-coding roles handled, QG tuned, duplicate list keys and modals fixed. *(`bbf7c87`)*
- **Non-coding role set expanded to 5** — UI/UX Designer, Business/Systems Analyst, Network Engineer plus the existing two — these roles now receive **0 coding questions**. *(`3c61d9a`)*

#### 2026-08-30 (Sun)
- **Skill-driven coding-language selection**, auto-fill fix, performance tuning (1.28 s interview start, 1.72 s submit). *(`789d8d2`)*
- **Registration error messages parsed properly.** *(`7b38de2`)*
- **Removed the demo auto-login fallback**, relaxed password validation for the demo build. *(`32c1e50`)*
- **`interview_scoring_config.json` backed up.** *(`89d8643`)*
- **Merged PR #74.**

#### 2026-08-31 (Mon)
- **Username truncation + dropdown styling** fixed in the navbar. *(`969531b`)*
- **CV Match theme tokens updated**, stale docs removed. *(`32d3a3a`)*
- **Merged PR #81.**

### September 2026

#### 2026-09-01 (Tue)
- **Scoring accuracy improvements + frontend fixes.** *(`b0f9066`)*
- **LambdaMART learning-to-rank retrained** with the 12-feature format and an `ensure_features()` guard for ablation runs. *(`1fd9c29`)*
- **NFR suite improved 91 % → 94 %** — lazy-loaded recharts, C1 rate limiting, CORS test fix, NFR test URL fixes. *(`1b195f8`)*
- **NFR report recorded: 50 PASS / 7 WARN / 0 FAIL (94 %).** *(`8ff41a0`)*

#### 2026-09-02 (Wed)
- **T5 continuation script logging improved** (`continue_t5_to_90.py`) so the 90 % training target can be monitored. *(`6c76dbb`)*

#### 2026-09-03 (Thu)
- **C1 models retrained** — primary model 87.3 % → **98.5 %**, TF-IDF baseline **100 %**, `multi_class` deprecation fixed for scikit-learn 1.9. *(`ecd6028`)*
- **Repository cleaned** — untracked `.venv312`, 14 `.pkl`, `.bak`, `.mp4`, `.pt` files, removed log folders; `.gitignore` updated. *(`97b6469`)*

### October 2026

#### 2026-10-09 (Fri)
- **Merged PR #86** — interview generation & evaluation consolidation. *(`2b53002`)*

#### 2026-10-16 (Fri)
- **Apple-inspired frontend design system adopted** (tokens, surfaces, motion). *(`22fdb35`)*
- **Removed large documentation/report trees from git** — `docs/`, `papers/`, `paper/`, `poster/`, `overleaf_reports/`, `final report/`, component accuracy report. *(`c37c1cd`, `6f2f94f`, `2535393`, `270ddef`, `a266f9f`, `9e7a0b9`, `100d4ea`)*
- **`.gitignore` updated** for build artefacts and checkpoints. *(`653916a`, `c0d922c`, `88f72b8`)*
- **Merged PRs #88 and #89.**

#### 2026-10-18 (Sun) — security hardening
- **Auth hardened and recruiter data scoped** to the owning company. *(`4911a9a`)*
- **Candidate access and scoring pipelines hardened.** *(`d46a3ec`)*
- **Candidate data access hardened; models refreshed.** *(`880d947`)*
- **Interview access hardened; question generation improved.** *(`8108916`)*
- **Frontend UX refreshed; auth flows hardened.** *(`bc7715b`)*
- **Merged PR #92.**

#### 2026-10-19 (Mon) — model quality, coding bank, deployment
- **QG model retrained properly** and its output made usable. *(`6cc16ea`)*
- **Two out-of-distribution bugs fixed** that made the QG model look broken. *(`bd93f32`)*
- **Batch-level impact reported**; resumed-run throughput logging fixed. *(`7b2445e`)*
- **QG gate now judges relevance**, not just structure. *(`74def8b`)*
- **Per-question gate + type routing added**; coding collapse diagnosed. *(`08af75b`)*
- **Interview composition matches the requested mix**; coding-question leaks stopped. *(`cd4d181`)*
- **Role/coding-language drift fixed**; no languages promised that the sandbox cannot run. *(`9089f44`)*
- **Role skills matched by word overlap** instead of substring equality. *(`4a9a8d2`)*
- **Evaluated checkpoint report + 20-role gate measurement** added. *(`6c5d053`)*
- **External interview datasets fetched and evaluated** (schema, licence, fit). *(`51ac5be`)*
- **Verified Python coding bank** built from humaneval-x + lbpp. *(`273c964`)*
- **Role-appropriate coding questions** in every declared language. *(`334e3ba`)*
- **Coding answer spellings normalised**; find-the-bug keys proven. *(`82b39d3`)*
- **Database Administrator role served SQL** instead of the Python fallback. *(`911611d`)*
- **Candidate code now runs in a hardened container** rather than a subprocess. *(`ae0cd10`)*
- **Per-role skills measured against real job postings.** *(`3c60292`)*
- **Frontend hosted on Cloudflare Pages**, backends exposed through a Tunnel. *(`16e4767`)*
- **Shared Atlas credentials removed from the launchers.** *(`e908612`)*
- **Database credentials removed from `.env.example`.** *(`1fb98ef`)*
- **Unclosed JSX expression fixed** — it had broken every build. *(`cf40e0f`)*
- **Ownership enforced on C4 analytics and skill simulation.** *(`633cbe1`)*
- **C0 score-sync task kept alive.** *(`86733a4`)*
- **Merged PR #93.**

#### 2026-10-21 (Wed)
- **C3 endpoint renamed** `/rank/jobs` → `/rank/roles` to match the role-based ranking model. *(`69099bf`)*
- **Component 2 slide-style overview README** added. *(`7d077cd`)*
- **Log book created and `LESSONS.md` restored** after it was dropped by a branch merge. *(this session)*

---

## 3. Verified results recorded in this period

| Item | Result | Evidence |
|------|--------|----------|
| C1 resume/role models | primary **98.5 %**, TF-IDF baseline **100 %** | `ecd6028` |
| C2 interview scoring | **100 %** agreement with the data-driven rubric (20 roles) | `bbf7c87` |
| C3 LambdaMART ranker | **NDCG@5 = 0.9473** | `1fd9c29` |
| T5 question generator | **87.93 %** at epoch 12/15 (90 % target) | `component2/models/t5_qg/history.json` |
| NFR suite | **94 %** — 50 PASS / 7 WARN / 0 FAIL | `8ff41a0`, `nfr_test_report.json` |
| Role coverage | **20 canonical roles**, 5 of them non-coding (0 coding questions) | `eb35ff5`, `3c61d9a` |
| API wiring | **72 endpoints audited**, all reachable from the frontend | frontend `src/api.js` |
| Security | IDOR, ownership, credential and CORS issues closed | `2fd529f`, `4911a9a`, `633cbe1`, `e908612` |

---

## 4. Open items carried forward

1. **T5 QG training** — continue from epoch 12/15 (87.93 %) to the 90 % target; monitor via `continue_t5_to_90.py`.
2. **Light-mode sweep** — re-verify every page with a hard refresh; check remaining panels that still carry hardcoded colours.
3. **NFR warnings** — 7 WARN items remain in the NFR suite.
4. **Dataset licensing** — record the licence decision for the external interview datasets evaluated on 19 Oct.

---

## 5. Appendix — team contributions merged into `main`

| Contributor | Commits (05 Jul – 21 Oct 2026) | Active window |
|-------------|-------------------------------:|---------------|
| Yenura Karunanayaka | 165 | 03 Aug – 21 Oct 2026 |
| it22027610 | 89 | 14 Aug – 15 Oct 2026 |
| tharindu43 | 47 | 05 Aug – 16 Oct 2026 |
| Tharindu Perera | 16 | 22 Aug – 31 Aug 2026 |

*(Counts exclude merge commits; this log book itemises only the author's own work. Team work is visible in `git log --author=<name>`.)*

---

*Maintained alongside `LESSONS.md`: this file records **what was done and when**; `LESSONS.md` records **what was learned**.*
