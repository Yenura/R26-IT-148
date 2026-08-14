"""
Component 2: QG Engine Backend Wrapper
Replaces the RAG+LLM system with direct QG model + static bank fallback.
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Lazy-loaded singletons
_qg_generator = None
_question_bank = None


def _is_good_question(q: Dict) -> bool:
    """True if a generated question is usable.

    The tiny QG model can emit fragment/noise questions (``<unk>`` tokens,
    placeholder test cases, missing answer keys). Broken questions make
    scoring garbage no matter how good the scorer is.
    """
    text = json.dumps(q, ensure_ascii=False)
    if "<unk>" in text or "<pad>" in text:
        return False
    qtext = q.get("question_text") or ""
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
        return bool((q.get("answer_text") or "").strip().lower()) \
            and not q.get("answer_text", "").startswith("This question covers")
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
    # Prefer the retrained v2 model (canonical dataset); fall back to v1.
    v2_path = os.path.join(models_dir, "qg_model_v2")
    v1_path = os.path.join(models_dir, "qg_model")
    model_path = v2_path if os.path.isdir(v2_path) else v1_path

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
            logger.info("QG model loaded from %s", model_path)
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
) -> Optional[List[Dict]]:
    """
    Generate questions using QG model. Returns None if model unavailable.
    Caller falls back to static question bank.
    When coding_profile is 'none', num_code is 0 and no coding questions are requested.
    """
    generator = _get_qg_generator()
    if generator is None:
        return None

    try:
        combined = generator.generate_for_session(
            job_role=job_role,
            skills=skills,
            num_mcq=num_mcq,
            num_desc=num_desc,
            num_code=num_code,
        )
        total = num_mcq + num_desc + num_code
        if combined and len(combined) == total:
            good = [q for q in combined if _is_good_question(q)]
            if len(good) == total:
                logger.info("QG model generated %d valid questions", len(good))
                return good
            logger.warning(
                "QG model: %d/%d questions failed quality gate; falling back to static bank",
                total - len(good), total,
            )
            return None
        if combined and len(combined) > 0:
            good = [q for q in combined if _is_good_question(q)]
            if good and len(good) >= len(combined) // 2:
                logger.info(
                    "QG model generated %d/%d valid questions; using partial results",
                    len(good), total,
                )
                return good[:total]
            logger.warning(
                "QG model: only %d/%d questions passed quality gate; falling back to static bank",
                len(good), total,
            )
            return None
        else:
            logger.info("QG model returned no questions; falling through")
        return None
    except Exception as exc:
        logger.warning("QG model generation failed: %s", exc)
        return None
