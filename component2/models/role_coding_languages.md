# Job Roles & Coding Languages

Source of truth: `component2/backend/services/role_profiles.py`
Served to the frontend by `GET /api/v1/interview/jobs` (keys `role_profiles`
and `executable_languages`), and driven from the scoring config
`component2/models/interview_scoring_config.json`.

## The 20 positions

`code` = coding weight from `interview_weights`. A weight of `0.0` means the
role never receives coding questions.

| # | Role | Profile | Declared languages | Offerable (runnable) | mcq | desc | code |
|---|------|---------|--------------------|----------------------|-----|------|------|
| 1 | AI/NLP Engineer | full | Python | Python | 0.25 | 0.35 | 0.40 |
| 2 | Backend Developer | full | Python, Java, C#, Node.js, Go, JavaScript | Python | 0.20 | 0.30 | 0.50 |
| 3 | Blockchain Developer | full | Solidity, Rust, Go, Python | Python | 0.25 | 0.30 | 0.45 |
| 4 | Business/Systems Analyst | none | – | – | 0.35 | 0.65 | 0.00 |
| 5 | Cloud Solutions Architect | none | – | – | 0.45 | 0.55 | 0.00 |
| 6 | Cybersecurity Analyst | none | – | – | 0.45 | 0.55 | 0.00 |
| 7 | Data Engineer | full | Python, SQL, Scala | Python | 0.25 | 0.30 | 0.45 |
| 8 | Data Scientist | full | Python, R | Python | 0.30 | 0.30 | 0.40 |
| 9 | Database Administrator | sql | SQL, Python | Python | 0.30 | 0.40 | 0.30 |
| 10 | DevOps Engineer | scripting | Python, Bash, Go | Python | 0.40 | 0.40 | 0.20 |
| 11 | Embedded Systems Engineer | full | C, C++ | Python | 0.25 | 0.35 | 0.40 |
| 12 | Frontend Developer | full | JavaScript, TypeScript | Python | 0.25 | 0.35 | 0.40 |
| 13 | Full Stack Developer | full | JavaScript, TypeScript, Python, Java | Python | 0.20 | 0.35 | 0.45 |
| 14 | Machine Learning Engineer | full | Python | Python | 0.25 | 0.30 | 0.45 |
| 15 | Mobile App Developer | full | Kotlin, Swift, Dart, Java | Python | 0.25 | 0.35 | 0.40 |
| 16 | Network Engineer | none | – | – | 0.45 | 0.55 | 0.00 |
| 17 | QA/Test Automation Engineer | full | Python, Java, JavaScript | Python | 0.25 | 0.35 | 0.40 |
| 18 | Site Reliability Engineer | scripting | Python, Go, Bash | Python | 0.35 | 0.40 | 0.25 |
| 19 | Software Engineer | full | Python, Java, C#, C++, JavaScript, Go | Python | 0.20 | 0.30 | 0.50 |
| 20 | UI/UX Designer | none | – | – | 0.30 | 0.70 | 0.00 |

Totals: **15 coding roles, 5 non-coding roles, 20 positions.**

## Declared vs. offerable languages

* **Declared** is the language stack the role would *naturally* use. It is
  reporting metadata and a wish-list for future runtimes.
* **Offerable** is what the interview actually lets a candidate pick, i.e.
  `declared ∩ executable`. The code runner in
  `backend/routers/interview.py` compiles with `compile(code, "<string>",
  "exec")` and runs `sys.executable` inside a wrapper that blocks
  `os`/`subprocess`/network imports. That sandbox is **Python-only**.

Today only Python is executable, so every coding role is offered Python
(Python is also the language of all 1,307 bank coding questions). The Python
fallback is appended for roles whose declared list has no executable entry
(Frontend, Mobile, Embedded, Blockchain), so those roles are still offered a
language the sandbox can actually run rather than a promise it cannot keep.

`EXECUTABLE_LANGUAGES` may only be extended together with a hardened sandbox
and matching test cases for the new language.

## Bugs this mapping fixes

1. **Blockchain Developer** had a coding weight of `0.45` but a `none` coding
   profile. It now receives coding questions.
2. **Site Reliability Engineer** had a coding weight of `0.25` but a `none`
   profile. It is now `scripting` (like DevOps).
3. **QA/Test Automation Engineer** was profiled as `sql` because its skill list
   mentioned SQL, so its Python/Java/JavaScript coding questions were pushed
   through an SQL keyword gate. It is now `full`.
4. **Mobile App Developer** was detected as JavaScript because `React Native`
   matched an over-broad `react` rule. Detection now checks Kotlin/Swift/Dart
   first.
5. **Network Engineer** appeared in both the frontend language map and the
   frontend non-coding list. The frontend maps are now the exact complement
   and the backend is the authority.
6. **`coding_language` was ignored end-to-end.** The UI promised "Coding
   questions will be generated in *Kotlin*", the backend dropped the field, the
   question was Python and the candidate's Kotlin was compiled as Python →
   `SyntaxError` → score `0`. The field is now threaded through the start
   request, validated against the executable set, stored on the session and on
   every coding question, and sent to `/code/run`.
7. **`/code/run` and submit graded any language as Python.** Both now refuse an
   unsupported language instead of silently scoring it.
8. **The per-type question mix disagreed with the scoring weights** (e.g.
   Frontend Developer mixed `0.20/0.30/0.50` while being graded
   `0.25/0.35/0.40`; 8 roles fell through to a generic default).
   `_get_question_distribution` now derives the mix from the same
   `interview_weights` used for grading.
9. **`_filter_coding_questions_by_profile` ignored language**, and the
   off-topic fallback compared the *algorithm topic* (`category`) against
   language names, so it never matched anything. Filtering is now by the
   `language` field first, then by profile keywords.

## Invariants (enforced by `backend/tests/test_role_profiles.py`)

* `coding weight > 0` ⟺ role is in `ROLE_LANGUAGES` ⟺ profile ≠ `none`
* `coding weight = 0` ⟺ role is in `NON_CODING_ROLES` ⟺ profile = `none`
* offered languages ⊆ `EXECUTABLE_LANGUAGES`
* `resolve_language` never returns a declared-but-unexecutable language
* the per-type distribution sums to the requested count and gives 0 coding
  questions to non-coding roles
