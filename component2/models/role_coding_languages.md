# Job Roles & Coding Languages

Source of truth: `component2/backend/services/role_profiles.py`
Served to the frontend by `GET /api/v1/interview/jobs` (keys `role_profiles`
and `executable_languages`), and driven from the scoring config
`component2/models/interview_scoring_config.json`.

## The 20 positions

`code` = coding weight from `interview_weights`. A weight of `0.0` means the
role never receives coding questions.

| # | Role | Profile | Declared languages | Offered language | Graded by | mcq | desc | code |
|---|------|---------|--------------------|------------------|-----------|-----|------|------|
| 1 | AI/NLP Engineer | full | Python | Python | executed | 0.25 | 0.35 | 0.40 |
| 2 | Backend Developer | full | Python, Java, C#, Node.js, Go, JavaScript | Python | executed | 0.20 | 0.30 | 0.50 |
| 3 | Blockchain Developer | full | Solidity, Rust, Go, Python | Rust | non-executed | 0.25 | 0.30 | 0.45 |
| 4 | Business/Systems Analyst | none | – | – | – | 0.35 | 0.65 | 0.00 |
| 5 | Cloud Solutions Architect | none | – | – | – | 0.45 | 0.55 | 0.00 |
| 6 | Cybersecurity Analyst | none | – | – | – | 0.45 | 0.55 | 0.00 |
| 7 | Data Engineer | full | Python, SQL, Scala | Python | executed | 0.25 | 0.30 | 0.45 |
| 8 | Data Scientist | full | Python, R | Python | executed | 0.30 | 0.30 | 0.40 |
| 9 | Database Administrator | sql | SQL, Python | Python | executed | 0.30 | 0.40 | 0.30 |
| 10 | DevOps Engineer | scripting | Python, Bash, Go | Python | executed | 0.40 | 0.40 | 0.20 |
| 11 | Embedded Systems Engineer | full | C, C++ | C++ | non-executed | 0.25 | 0.35 | 0.40 |
| 12 | Frontend Developer | full | JavaScript, TypeScript | JavaScript | non-executed | 0.25 | 0.35 | 0.40 |
| 13 | Full Stack Developer | full | JavaScript, TypeScript, Python, Java | JavaScript | non-executed | 0.20 | 0.35 | 0.45 |
| 14 | Machine Learning Engineer | full | Python | Python | executed | 0.25 | 0.30 | 0.45 |
| 15 | Mobile App Developer | full | Kotlin, Swift, Dart, Java | Java | non-executed | 0.25 | 0.35 | 0.40 |
| 16 | Network Engineer | none | – | – | – | 0.45 | 0.55 | 0.00 |
| 17 | QA/Test Automation Engineer | full | Python, Java, JavaScript | Python | executed | 0.25 | 0.35 | 0.40 |
| 18 | Site Reliability Engineer | scripting | Python, Go, Bash | Python | executed | 0.35 | 0.40 | 0.25 |
| 19 | Software Engineer | full | Python, Java, C#, C++, JavaScript, Go | Python | executed | 0.20 | 0.30 | 0.50 |
| 20 | UI/UX Designer | none | – | – | – | 0.30 | 0.70 | 0.00 |

Totals: **15 coding roles, 5 non-coding roles, 20 positions.** Of the 15, 10
are graded by *executing* Python and 5 (Embedded, Frontend, Full Stack, Mobile,
Blockchain) by a *non-executed* format in their own language.

## Declared vs. executable vs. supported languages

* **Declared** is the language stack the role would *naturally* use.
* **Executable** (`EXECUTABLE_LANGUAGES`) is what the sandbox can actually run.
  The code runner in `backend/routers/interview.py` compiles with
  `compile(code, "<string>", "exec")` and runs `sys.executable` inside a wrapper
  that blocks `os`/`subprocess`/network imports. That sandbox is
  **Python-only**.
* **Supported** (`supported_languages()`) is executable **plus** the languages
  we can assess with a non-executed format (`NON_EXECUTED_FORMATS`):
  predict-the-output, find-the-bug and complete-the-function. Those formats are
  graded by comparing text against an answer key, or by picking an option —
  so they never need to run the candidate's code.

`available_languages(role)` is `declared ∩ supported`, **in declared order**.
Python is *not* appended as a silent default: that is what used to hand a
Frontend Developer Python questions. A coding role whose declared languages are
all unsupported offers nothing; its coding weight shifts to Descriptive, and
`role_profiles.log_language_coverage()` warns about it at startup.

Extending `EXECUTABLE_LANGUAGES` still requires a hardened sandbox and matching
test cases for the new language. Extending `NON_EXECUTED_LANGUAGES` requires
questions in `component2/models/coding_bank_nonexecuted.json`; a test
(`tests/test_coding_nonexecuted.py`) fails if the constant promises a language
the bank does not have.

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
10. **The served session mix did not match the requested mix.** A single
    whole-bank top-up padded the *total* rather than each type, so a role that
    asked for `4/3/3` could be served `1/8/11`, and a **non-coding role could
    receive a coding question** it was never scored on. Top-up is now
    per-type (`_top_up_by_type`), so every session contains exactly its
    advertised counts and a non-coding role can never leak a coding question.
11. **Python was the silent default language for every role.** A Frontend
    Developer, an Embedded Systems Engineer and a Mobile App Developer were all
    handed Python coding questions, graded as Python. Language selection now
    uses the role's *first declared* language that is either executable or has
    a non-executed format — JavaScript, C++ and Java respectively — and Python
    is only ever offered to a role that declares it (or to a role we know
    nothing about).
12. **A language filter that matched nothing silently served another
    language.** Both the coding profile filter and the per-type top-up widened
    back to the whole cross-language pool when they found nothing, so a Rust or
    JavaScript candidate could still be served a Python question. Both now stop
    at the resolved language; when the pool is genuinely empty the coding share
    moves to Descriptive and the session stops advertising a coding section.

## Invariants (enforced by `backend/tests/test_role_profiles.py` and
## `backend/tests/test_coding_nonexecuted.py`)

* `coding weight > 0` ⟺ role is in `ROLE_LANGUAGES` ⟺ profile ≠ `none`
* `coding weight = 0` ⟺ role is in `NON_CODING_ROLES` ⟺ profile = `none`
* offered languages ⊆ `supported_languages()`
* a role with a declared language list is never offered a language outside it
  (no silent Python)
* `resolve_language` never returns a language outside `supported_languages()`
* every language in `NON_EXECUTED_LANGUAGES` has questions in
  `coding_bank_nonexecuted.json`, and every coding role's resolved language has
  enough questions to fill a session
* the answer key (`accepted_answers` / `correct_answer_index`) is not part of
  the `InterviewQuestion` response model, so it is never sent to a candidate
* the per-type distribution sums to the requested count and gives 0 coding
  questions to non-coding roles
* a served session contains exactly its advertised per-type counts, and a
  non-coding session contains zero coding questions
