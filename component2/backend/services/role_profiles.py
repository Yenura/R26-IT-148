"""
Single source of truth for job role -> coding language / coding profile.

Why this module exists
----------------------
The role metadata used to live in three places that drifted apart:

* ``frontend/src/pages/Interview.jsx``  (``ROLE_LANGUAGES`` / ``NON_CODING_ROLES``)
* ``backend/services/ml_engine.py``     (``_determine_coding_profile``)
* ``backend/services/qg_engine.py``     (ad-hoc scoring-config lookups)

The drift caused real, user-visible bugs:

* ``Blockchain Developer`` (coding weight 0.45) and ``Site Reliability
  Engineer`` (coding weight 0.25) were profiled as ``none`` even though the
  scoring config still weighted a coding section -- the candidate was scored
  on a section they were never meant to receive.
* ``QA/Test Automation Engineer`` was profiled as ``sql`` because its skill
  list happened to mention SQL, so its (Python/Java/JavaScript) coding
  questions were filtered through an SQL keyword gate.
* ``Network Engineer`` appeared in the frontend language map *and* in the
  frontend non-coding list at the same time.
* ``Mobile App Developer`` declared Kotlin/Swift/Dart but was detected as
  JavaScript because ``React Native`` matched an over-broad ``react`` rule.

Executable vs. declared vs. supported languages
-----------------------------------------------
The sandbox that runs candidate code (``routers/interview.py``) is
**Python-only**: it compiles with ``compile(code, "<string>", "exec")`` and
runs ``sys.executable`` inside a wrapper that blocks ``os`` / ``subprocess`` /
network imports.  Offering a language we cannot execute *and then executing it
anyway* means every candidate who actually writes in that language is graded
as a Python syntax error and scores 0 -- which is exactly what used to happen
for Java / Kotlin / Solidity.

There are therefore three sets:

* :func:`executable_languages` -- what the sandbox can run (Python).
* :func:`supported_languages` -- what we can *ask*, which also includes
  languages we can only assess with a non-executed format
  (:data:`NON_EXECUTED_FORMATS`): predict-the-output, find-the-bug and
  complete-the-function are graded by comparing text or picking an option, so
  they never need to run the candidate's code.
* :func:`declared_languages` -- the full, aspirational role list.

:func:`available_languages` is the role's declared list filtered to
``supported``, in declared order.  Python is **not** appended as a silent
default; a role whose declared languages are all unsupported offers nothing,
and its coding weight shifts to Descriptive.  Add a runtime here only together
with a hardened sandbox, or the guarantee is broken.
"""

from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Languages the sandbox can actually execute.
#
# Keep this in lock-step with the sandbox in ``routers/interview.py``.  Only
# Python has a hardened runner today, so this is intentionally a single entry.
# ---------------------------------------------------------------------------
EXECUTABLE_LANGUAGES: tuple = ("Python",)

# ---------------------------------------------------------------------------
# Languages the interview can ask WITHOUT executing code.
#
# A candidate's code cannot be *run* in these languages (there is no hardened
# runner), but it can still be assessed with the non-executed formats in
# ``NON_EXECUTED_FORMATS`` (predict-the-output / find-the-bug /
# complete-the-function), which are graded by comparing text or picking an
# option rather than by running the candidate's code.  Offering them is what
# makes Embedded / Frontend / Mobile / Blockchain questions role-appropriate
# instead of silently Python.
#
# Must stay in lock-step with ``models/coding_bank_nonexecuted.json``
# (enforced by tests).
# ---------------------------------------------------------------------------
NON_EXECUTED_LANGUAGES: tuple = ("Python", "Java", "C++", "JavaScript", "Go", "Rust")

# Question formats that are graded without running the candidate's code.
NON_EXECUTED_FORMATS: tuple = ("Predict Output", "Find the Bug", "Complete Function")

# The format stamped on ordinary, executed Coding questions.
EXECUTED_FORMAT = "Write Code"

# Coding languages a role's questions *would* use, ordered by preference.
# Only coding roles appear here (see ``NON_CODING_ROLES``).
ROLE_LANGUAGES: Dict[str, List[str]] = {
    "AI/NLP Engineer": ["Python"],
    "Backend Developer": ["Python", "Java", "C#", "Node.js", "Go", "JavaScript"],
    "Blockchain Developer": ["Solidity", "Rust", "Go", "Python"],
    "Data Engineer": ["Python", "SQL", "Scala"],
    "Data Scientist": ["Python", "R"],
    "Database Administrator": ["SQL", "Python"],
    "DevOps Engineer": ["Python", "Bash", "Go"],
    "Embedded Systems Engineer": ["C", "C++"],
    "Frontend Developer": ["JavaScript", "TypeScript"],
    "Full Stack Developer": ["JavaScript", "TypeScript", "Python", "Java"],
    "Machine Learning Engineer": ["Python"],
    "Mobile App Developer": ["Kotlin", "Swift", "Dart", "Java"],
    "QA/Test Automation Engineer": ["Python", "Java", "JavaScript"],
    "Site Reliability Engineer": ["Python", "Go", "Bash"],
    "Software Engineer": ["Python", "Java", "C#", "C++", "JavaScript", "Go"],
}

# Roles whose scoring config gives coding a weight of 0.0.  Must stay the
# exact complement of ``ROLE_LANGUAGES`` (enforced by tests).
NON_CODING_ROLES = {
    "Business/Systems Analyst",
    "Cloud Solutions Architect",
    "Cybersecurity Analyst",
    "Network Engineer",
    "UI/UX Designer",
}

# Roles that code, but not general-purpose software: SQL or shell/pipeline
# work.  Drives both the question filter and the per-type distribution.
ROLE_CODING_PROFILE: Dict[str, str] = {
    "Database Administrator": "sql",
    "DevOps Engineer": "scripting",
    "Site Reliability Engineer": "scripting",
}

# ---------------------------------------------------------------------------
# Skill -> language inference (used only for roles we don't know explicitly).
# ---------------------------------------------------------------------------
# Substring keywords: safe when the token is distinctive enough not to appear
# inside unrelated words.
_LANGUAGE_SUBSTRING_RULES = [
    (("solidity",), "Solidity"),
    (("kotlin",), "Kotlin"),
    (("swift",), "Swift"),
    (("dart", "flutter"), "Dart"),
    (("c#", "c sharp", ".net", "asp.net"), "C#"),
    (("c++", "c/c++", "c plus plus"), "C++"),
    (("rust",), "Rust"),
    (("scala",), "Scala"),
    (("typescript",), "TypeScript"),
    (("javascript", "node.js", "react", "vue", "angular"), "JavaScript"),
    (("bash", "shell script", "powershell"), "Bash"),
    (("golang",), "Go"),
]

# Exact-match keywords: tokens too short/ambiguous for substring matching
# (``go`` inside "MongoDB", ``r`` inside "Docker", ``c`` inside "CSS").
_LANGUAGE_EXACT_RULES = {
    "go": "Go",
    "r": "R",
    "c": "C",
    "java": "Java",
    "python": "Python",
    "sql": "SQL",
}

# Same map minus SQL: SQL is its own coding profile, not general-purpose code.
_LANGUAGE_EXACT_RULES_NO_SQL = {
    k: v for k, v in _LANGUAGE_EXACT_RULES.items() if v != "SQL"
}

# Skills that prove a role writes executable code even when they aren't a
# language name (test automation, ML frameworks, web platform work).
_CODING_SKILL_HINTS = (
    "selenium", "pytest", "jest", "cypress", "test automation", "api testing",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
    "react", "react native", "vue", "angular", "django", "flask", "fastapi",
    "spring", "node.js", "html", "css", "dom",
)

# Skills that imply shell/pipeline work rather than application code.
_SCRIPTING_SKILL_HINTS = (
    "docker", "kubernetes", "ci/cd", "terraform", "ansible", "pipeline",
    "infrastructure as code", "shell", "bash", "yaml", "git", "prometheus",
)


def _norm(skills: Optional[List[str]]) -> List[str]:
    return [str(s).strip().lower() for s in (skills or []) if str(s).strip()]


def is_coding_role(job_role: str) -> bool:
    """True if the role is expected to receive coding questions."""
    return job_role in ROLE_LANGUAGES


def declared_languages(job_role: str) -> List[str]:
    """Every language the role would use if the sandbox supported them all."""
    return list(ROLE_LANGUAGES.get(job_role, []))


def executable_languages() -> List[str]:
    """Languages the sandbox can genuinely run (see module docstring)."""
    return list(EXECUTABLE_LANGUAGES)


def supported_languages() -> List[str]:
    """Languages the interview may ask in at all.

    Executable languages first, then the languages we can only assess with a
    non-executed format.
    """
    langs = list(EXECUTABLE_LANGUAGES)
    for lang in NON_EXECUTED_LANGUAGES:
        if lang not in langs:
            langs.append(lang)
    return langs


def available_languages(job_role: str) -> List[str]:
    """Languages the interview may offer for this role, in declared order.

    The role's own declared languages, filtered to what we can actually ask
    (executable, or supported by a non-executed format).  Python is *not*
    silently appended: that used to give a Frontend Developer Python questions.
    It is used only for a role with no declared list at all (nothing to
    respect), and a role whose declared languages are all unsupported offers
    nothing, so its coding weight shifts to Descriptive instead.
    """
    if not is_coding_role(job_role):
        return []
    supported = {lang.lower(): lang for lang in supported_languages()}
    langs = [
        supported[lang.lower()]
        for lang in declared_languages(job_role)
        if lang.lower() in supported
    ]
    if langs:
        return langs
    return ["Python"] if not declared_languages(job_role) else []


def roles_with_language_fallback() -> Dict[str, List[str]]:
    """Roles offered a language they do not declare (a fallback was applied).

    Logged at startup: it means the interview would ask the candidate for a
    language the role never uses.
    """
    fallback = {}
    for role in ROLE_LANGUAGES:
        declared = {lang.lower() for lang in declared_languages(role)}
        offered = available_languages(role)
        if offered and offered[0].lower() not in declared:
            fallback[role] = offered
    return fallback


def roles_without_a_bank() -> List[str]:
    """Coding roles whose declared languages are all unsupported.

    These get no coding questions; their coding weight shifts to Descriptive.
    """
    return [role for role in ROLE_LANGUAGES if not available_languages(role)]


def log_language_coverage(logger) -> None:
    """Warn at startup about roles we cannot ask in their own language."""
    fallback = roles_with_language_fallback()
    if fallback:
        logger.warning(
            "⚠ Coding language fallback (offered language is not declared by the "
            "role): %s", fallback,
        )
    missing = roles_without_a_bank()
    if missing:
        logger.warning(
            "⚠ Coding roles with no bank for any declared language -- coding "
            "weight shifts to Descriptive: %s", missing,
        )


def default_language(job_role: str) -> Optional[str]:
    """First offerable language for the role, or None for non-coding roles."""
    langs = available_languages(job_role)
    return langs[0] if langs else None


def resolve_language(job_role: str, requested: Optional[str]) -> Optional[str]:
    """Map a requested language to one we can actually offer.

    Never returns an unsupported language: an unsupported choice is coerced to
    the role default rather than silently promised and graded as a syntax
    error.
    """
    if not is_coding_role(job_role):
        return None
    langs = available_languages(job_role)
    if requested:
        wanted = str(requested).strip()
        if wanted and wanted.lower() != "auto":
            for lang in langs:
                if lang.lower() == wanted.lower():
                    return lang
    return langs[0] if langs else None


def detect_language(job_role: str, skills: Optional[List[str]] = None) -> str:
    """Best-effort language for a role, used for question metadata.

    Prefers the role's own declared list, then falls back to skill keywords so
    unknown/employer-supplied roles still resolve sensibly.
    """
    declared = declared_languages(job_role)
    if declared:
        return declared[0]

    low = _norm(skills)
    joined = " ".join(low)
    for tokens, lang in _LANGUAGE_SUBSTRING_RULES:
        if any(tok in joined for tok in tokens):
            return lang
    for token in low:
        if token in _LANGUAGE_EXACT_RULES:
            return _LANGUAGE_EXACT_RULES[token]
    return "Python"


def _infer_profile_from_skills(skills: Optional[List[str]]) -> str:
    """Profile for a role we have no explicit entry for."""
    low = _norm(skills)
    joined = " ".join(low)

    if any(tok in joined for tok in _CODING_SKILL_HINTS):
        return "full"
    if any(tok in joined for tok in _SCRIPTING_SKILL_HINTS):
        return "scripting"

    has_language = any(
        any(tok in joined for tok in tokens) for tokens, _ in _LANGUAGE_SUBSTRING_RULES
    ) or any(
        tok in _LANGUAGE_EXACT_RULES_NO_SQL for tok in low
    )
    if has_language:
        return "full"
    if any("sql" in tok for tok in low):
        return "sql"
    return "none"


def determine_coding_profile(
    job_role: str,
    skills: Optional[List[str]] = None,
    coding_weight: Optional[float] = None,
) -> str:
    """Return ``full`` | ``sql`` | ``scripting`` | ``none`` for a role.

    The scoring config is authoritative: a coding weight of 0 (or a role in
    ``NON_CODING_ROLES``) always yields ``none`` no matter what the skill list
    contains.  Known coding roles use their explicit profile; unknown roles
    fall back to skill inference.
    """
    if coding_weight is not None and coding_weight <= 0:
        return "none"
    if job_role in NON_CODING_ROLES:
        return "none"
    if job_role in ROLE_LANGUAGES:
        return ROLE_CODING_PROFILE.get(job_role, "full")
    return _infer_profile_from_skills(skills)


def role_profile(job_role: str, coding_weight: Optional[float] = None) -> Dict:
    """Everything the frontend needs to render the coding controls for a role."""
    is_coding = is_coding_role(job_role) and (coding_weight is None or coding_weight > 0)
    return {
        "is_coding": is_coding,
        "coding_profile": determine_coding_profile(
            job_role, None, coding_weight=coding_weight
        ),
        "languages": available_languages(job_role) if is_coding else [],
        "declared_languages": declared_languages(job_role) if is_coding else [],
        "executable_languages": executable_languages(),
    }
