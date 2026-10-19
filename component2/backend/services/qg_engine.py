"""
Component 2: QG Engine Backend Wrapper
Replaces the RAG+LLM system with direct QG model + static bank fallback.
"""

import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Lazy-loaded singletons
_qg_generator = None
_question_bank = None


def _is_degenerate(text: str) -> bool:
    """True when the model has fallen into a repetition loop.

    Weak seq2seq models lock onto a phrase and repeat it --
    "senior senior senior", "a risk when a risk when a risk when ...".
    """
    words = re.findall(r"[a-z']+", text.lower())
    for i in range(len(words) - 2):
        if words[i] == words[i + 1] == words[i + 2]:
            return True
    if len(words) >= 10:
        grams = [tuple(words[i:i + 3]) for i in range(len(words) - 2)]
        if len(grams) != len(set(grams)):
            return True
    return False


def _is_good_question(q: Dict, job_role: str = "", skills: Optional[List[str]] = None) -> bool:
    """True if a generated question is usable.

    The tiny QG model can emit fragment/noise questions (``<unk>`` tokens,
    repeated filler, placeholder test cases, missing answer keys). Broken
    questions make scoring garbage no matter how good the scorer is.
    """
    text = json.dumps(q, ensure_ascii=False)
    if "<unk>" in text or "<pad>" in text:
        return False
    qtext = q.get("question_text") or ""
    if _is_degenerate(qtext):
        return False
    # The model loops inside answers and options too, not just the question:
    # "The ' class in Java is used to the ' in Java is used to the ' in Java ..."
    if _is_degenerate(q.get("answer_text") or ""):
        return False
    # Checked per option, NOT on the concatenation: legitimate distractor sets
    # ("All of the above" / "None of the above") share the 3-gram "of the
    # above", which made the joined string look like a repetition loop and
    # rejected perfectly good MCQs. A real loop still shows up inside a single
    # option ("CSS CSS CSS preprocessors").
    options = q.get("options") or []
    if any(
        _is_degenerate(str(o.get("text", "")))
        for o in options
        if isinstance(o, dict)
    ):
        return False
    # The corpus quotes identifiers -- "the 'synchronized' keyword in Java" -- and
    # the model frequently drops the identifier, leaving a bare quote: "the '
    # keyword in Java". A quote surrounded by whitespace is that failure; a real
    # quoted term ("the 'synchronized' keyword", "it's") is never shaped like it.
    if re.search(r"\s'\s", qtext):
        return False
    # Topical relevance. The generator fills category/topic straight from the
    # skill list, so testing those always "succeeds"; the question text itself
    # has to name the role, or share a meaningful word with one of its skills.
    # Word overlap rather than substring equality, because the corpus and
    # job_requirements phrase the same topic differently ("data pipelines" vs
    # "data pipeline design"). Applied to MCQ/Descriptive only -- the corpus
    # conditions those on the role, whereas coding prompts carry algorithm tags
    # instead, so a coding question legitimately never names a role skill.
    if skills and q.get("question_type") in ("MCQ", "Descriptive"):
        low = qtext.lower()
        skill_words = {w for s in skills if s for w in re.findall(r"[a-z0-9+#]{3,}", s.lower())}
        q_words = set(re.findall(r"[a-z0-9+#]{3,}", low))
        named = (bool(job_role) and job_role.lower() in low) or bool(q_words & skill_words)
        if not named:
            return False
    if len(qtext) < 20:
        return False
    t = q.get("question_type")
    if t == "MCQ":
        opts = q.get("options") or []
        return (
            isinstance(opts, list) and len(opts) >= 2
            and all(isinstance(o, dict) and o.get("text") for o in opts)
            and (q.get("correct_answer_index") is not None or q.get("correct_option") is not None)
        )
    if t == "Descriptive":
        answer = (q.get("answer_text") or "").strip()
        if len(answer) < 20:
            return False
        return bool(answer) and not answer.startswith("This question covers")
    if t == "Coding":
        qtext_lower = qtext.lower()
        for tc in q.get("test_cases") or []:
            expected = str(tc.get("expected_output", "")).strip().lower()
            if not expected or expected in ("see answer", "result"):
                continue
            inp = tc.get("input") or {}
            if isinstance(inp, dict) and inp:
                return True
        return False
    return False


def _get_qg_generator():
    """Lazy-load the QG model."""
    global _qg_generator
    if _qg_generator is not None:
        return _qg_generator

    models_dir = os.environ.get(
        "MODELS_DIR",
        str(Path(__file__).parent.parent.parent / "models"),
    )
    # Prefer T5 fine-tuned > retrained v2 > v1.
    t5_path = os.path.join(models_dir, "t5_qg")
    v2_path = os.path.join(models_dir, "qg_model_v2")
    v1_path = os.path.join(models_dir, "qg_model")
    if os.path.isdir(t5_path) and os.path.isfile(os.path.join(t5_path, "model.safetensors")):
        model_path = t5_path
    elif os.path.isdir(v2_path):
        model_path = v2_path
    else:
        model_path = v1_path

    if not os.path.isdir(model_path):
        logger.warning("QG model directory not found: %s", model_path)
        return None

    try:
        ml_dir = os.path.join(Path(__file__).parent.parent.parent, "ml")
        if os.path.exists(ml_dir):
            sys.path.insert(0, str(ml_dir))
        from question_generator import QuestionGenerator

        bank = _get_question_bank()
        _qg_generator = QuestionGenerator(model_path=model_path, fallback_bank=bank)
        if _qg_generator.is_available:
            backend = _qg_generator.backend
            logger.info(
                "QG model active: type=%s path=%s (requested %s)",
                backend["type"], backend["path"], model_path,
            )
            if backend["path"] and backend["path"] != model_path:
                logger.warning(
                    "Requested QG model %s could not load; using fallback %s",
                    model_path, backend["path"],
                )
            return _qg_generator
        logger.warning("QG model not available")
        _qg_generator = None
        return None
    except Exception as exc:
        logger.warning("Failed to load QG model: %s", exc)
        return None


def _get_question_bank() -> List[Dict]:
    """Load the static question bank."""
    global _question_bank
    if _question_bank is not None:
        return _question_bank

    models_dir = os.environ.get(
        "MODELS_DIR",
        str(Path(__file__).parent.parent.parent / "models"),
    )
    bank_path = os.path.join(models_dir, "question_bank.json")

    if os.path.exists(bank_path):
        try:
            with open(bank_path, encoding="utf-8") as f:
                _question_bank = json.load(f)
            logger.info("Loaded question bank: %d questions", len(_question_bank))
            return _question_bank
        except Exception as exc:
            logger.warning("Error loading question bank: %s", exc)

    _question_bank = []
    return _question_bank


def describe_qg_backend() -> Dict:
    """Report the configured vs. actually-active QG backend.

    Does NOT force a model load (which is slow); only reads file presence and,
    if a generator is already loaded, its real type/path.
    """
    models_dir = os.environ.get(
        "MODELS_DIR",
        str(Path(__file__).parent.parent.parent / "models"),
    )
    t5_path = os.path.join(models_dir, "t5_qg")
    v2_path = os.path.join(models_dir, "qg_model_v2")
    if os.path.isdir(t5_path) and os.path.isfile(os.path.join(t5_path, "model.safetensors")):
        configured = "t5_qg"
    elif os.path.isdir(v2_path):
        configured = "qg_model_v2"
    else:
        configured = "qg_model"

    info: Dict = {
        "configured": configured,
        "loaded": _qg_generator is not None,
        "active_type": None,
        "active_path": None,
    }
    if _qg_generator is not None:
        backend = _qg_generator.backend
        info["active_type"] = backend.get("type")
        info["active_path"] = backend.get("path")
        info["degraded"] = bool(backend.get("path")) and backend.get("path") != t5_path
    return info


def merge_skill_lists(role_defaults: List[str], employer_skills: Optional[List[str]]) -> List[str]:
    """Merge employer skills with role defaults, preserving order and deduplicating."""
    seen = set()
    out: List[str] = []
    for src in (employer_skills or []), role_defaults:
        for s in src:
            if not s or not str(s).strip():
                continue
            key = str(s).strip().lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(str(s).strip())
    return out


def generate_questions_qg(
    *,
    job_role: str,
    skills: List[str],
    num_mcq: int,
    num_desc: int,
    num_code: int,
    coding_profile: str,
    coding_language: Optional[str] = None,
) -> Optional[List[Dict]]:
    """
    Generate MCQ/Descriptive questions with the QG model.

    Returns the questions that pass the *per-question* quality gate -- possibly
    fewer than requested -- or ``None`` when the model is unavailable or
    produced nothing usable.  The caller keeps the passing questions and fills
    every shortfall from the curated static bank, so a partially-good batch is
    still useful instead of being discarded wholesale.

    Coding is deliberately never generated: the tiny model cannot emit runnable
    test cases (see models/t5_coding_diagnosis.md), so coding questions always
    come from the curated bank.  ``num_code`` is accepted for call-site
    compatibility and ignored.

    ``coding_language`` is the executable language the candidate selected; it is
    passed to the generator so any emitted question is labelled consistently.
    """
    _ = coding_profile  # coding is bank-sourced; the caller owns the profile
    if num_code:
        logger.info(
            "QG model: coding is bank-sourced; ignoring requested num_code=%d", num_code
        )
    generator = _get_qg_generator()
    if generator is None:
        return None

    try:
        from ml.question_generator import set_preferred_language
    except Exception:  # pragma: no cover - generator already imported it
        set_preferred_language = None
    if set_preferred_language is not None:
        set_preferred_language(coding_language)
    try:
        combined = generator.generate_for_session(
            job_role=job_role,
            skills=skills,
            num_mcq=num_mcq,
            num_desc=num_desc,
            num_code=0,
        )
        if not combined:
            logger.info("QG model returned no questions; using the static bank")
            return None

        # Per-question gate: keep every question that passes, drop the rest.
        # The caller tops each type back up from the bank, so a rejected slot
        # is filled individually instead of rejecting the whole role's batch.
        good = [q for q in combined if _is_good_question(q, job_role, skills)]
        if not good:
            logger.info(
                "QG gate rejected all %d generated questions; using the static bank",
                len(combined),
            )
            return None
        by_type: Dict[str, int] = {}
        for q in good:
            k = q.get("question_type") or "?"
            by_type[k] = by_type.get(k, 0) + 1
        logger.info(
            "QG gate: %d/%d generated questions passed (requested %d MCQ+Descriptive) %s",
            len(good), len(combined), num_mcq + num_desc, by_type,
        )
        return good
    except Exception as exc:
        logger.warning("QG model generation failed: %s", exc)
        return None
    finally:
        if set_preferred_language is not None:
            set_preferred_language(None)
