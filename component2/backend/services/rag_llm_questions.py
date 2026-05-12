"""
RAG + general LLM question generation for Component 2.

Retrieves similar items from the local question bank (embedding or keyword fallback),
then asks an OpenAI-compatible Chat Completions API to adapt / compose questions
for the given job role and skill stack.

Enable with ENABLE_RAG_LLM_QUESTIONS=true and set LLM_API_KEY (+ optional LLM_BASE_URL, LLM_MODEL).
"""

from __future__ import annotations

import json
import logging
import os
import re
import uuid
from typing import Any, Dict, List, Optional, Tuple

import requests

logger = logging.getLogger(__name__)


def _env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name, str(default)).strip().lower()
    return v in ("1", "true", "yes", "on")


def merge_skill_lists(role_defaults: List[str], employer_skills: Optional[List[str]]) -> List[str]:
    """Employer order first, then role defaults; case-insensitive dedupe."""
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


def _question_text_for_match(q: Dict[str, Any]) -> str:
    parts = [
        str(q.get("question_text", "")),
        str(q.get("category", "")),
        str(q.get("topic", "")),
        " ".join(str(k) for k in (q.get("keywords") or []) if k),
    ]
    return " ".join(parts).lower()


def retrieve_relevant_questions(
    question_bank: List[Dict[str, Any]],
    job_role: str,
    skills: List[str],
    top_k: int = 15,
) -> List[Dict[str, Any]]:
    """RAG retrieval: prefer SBERT similarity; fallback to keyword overlap."""
    if not question_bank:
        return []

    query = f"{job_role}. Skills: {', '.join(skills)}".strip()
    top_k = max(3, min(top_k, 40))

    try:
        from sentence_transformers import SentenceTransformer, util

        model_name = os.getenv("SBERT_MODEL", "all-MiniLM-L6-v2")
        model = SentenceTransformer(model_name)
        q_emb = model.encode(query, convert_to_tensor=True)
        texts = [_question_text_for_match(q) for q in question_bank]
        corpus_emb = model.encode(texts, convert_to_tensor=True)
        scores = util.cos_sim(q_emb, corpus_emb)[0]
        idxs = scores.argsort(descending=True)[:top_k].tolist()
        return [question_bank[i] for i in idxs if 0 <= i < len(question_bank)]
    except Exception as exc:
        logger.warning("RAG embedding retrieval failed, using keyword fallback: %s", exc)
        skill_l = [s.lower() for s in skills if s]
        scored: List[Tuple[float, Dict[str, Any]]] = []
        for q in question_bank:
            blob = _question_text_for_match(q)
            score = sum(1 for s in skill_l if s and s in blob) + (job_role.lower() in blob)
            scored.append((float(score), q))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [q for _, q in scored[:top_k]]


def _strip_json_fence(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\s*", "", t, flags=re.IGNORECASE)
        t = re.sub(r"\s*```$", "", t)
    return t.strip()


def _chat_completions(
    messages: List[Dict[str, str]],
    *,
    api_key: str,
    base_url: str,
    model: str,
    timeout: int = 120,
) -> str:
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": float(os.getenv("LLM_TEMPERATURE", "0.35")),
    }
    # OpenAI-style JSON mode (many local providers reject this — retry without it)
    if os.getenv("LLM_JSON_MODE", "true").lower() in ("1", "true", "yes"):
        body["response_format"] = {"type": "json_object"}

    resp = requests.post(url, headers=headers, json=body, timeout=timeout)
    if resp.status_code >= 400 and "response_format" in body:
        body.pop("response_format", None)
        resp = requests.post(url, headers=headers, json=body, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def _validate_question(q: Dict[str, Any]) -> bool:
    if not q.get("question_text") or not q.get("question_type"):
        return False
    qtype = q.get("question_type")
    if qtype == "MCQ":
        opts = q.get("options") or []
        if len(opts) < 2:
            return False
        if q.get("correct_option") is None:
            return False
    elif qtype == "Descriptive":
        if not q.get("answer_text"):
            return False
    elif qtype == "Coding":
        if not (q.get("test_cases") or []):
            return False
    return True


def generate_questions_rag_llm(
    *,
    job_role: str,
    skills: List[str],
    question_bank: List[Dict[str, Any]],
    num_mcq: int,
    num_desc: int,
    num_code: int,
    coding_profile: str,
) -> Optional[List[Dict[str, Any]]]:
    """
    Returns a flat list of question dicts (MCQ + Descriptive + Coding) or None on failure/skip.
    """
    if not _env_bool("ENABLE_RAG_LLM_QUESTIONS", False):
        return None

    api_key = os.getenv("LLM_API_KEY", "").strip()
    if not api_key:
        logger.warning("ENABLE_RAG_LLM_QUESTIONS is set but LLM_API_KEY is empty; skipping LLM generation")
        return None

    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").strip()
    model = os.getenv("LLM_MODEL", "gpt-4o-mini").strip()
    top_k = int(os.getenv("RAG_TOP_K", "15"))

    rag_docs = retrieve_relevant_questions(question_bank, job_role, skills, top_k=top_k)
    rag_json = json.dumps(rag_docs, ensure_ascii=False, indent=2)[:24000]

    total = num_mcq + num_desc + num_code
    system = (
        "You are an expert technical interviewer. You output ONLY valid JSON (no markdown). "
        "Generate interview questions adapted to the employer's job role and skills. "
        "Use the RAG_CONTEXT as inspiration and style reference; do not copy IDs. "
        "Each question must be self-contained and technically accurate."
    )
    user = f"""Job role: {job_role}
Required skills (employer + defaults): {", ".join(skills)}
Coding profile for this session: {coding_profile}

Counts:
- MCQ: {num_mcq}
- Descriptive: {num_desc}
- Coding: {num_code}
Total questions: {total}

Return JSON with this exact shape:
{{
  "questions": [
    {{
      "question_type": "MCQ" | "Descriptive" | "Coding",
      "difficulty": "Easy" | "Medium" | "Hard",
      "category": string,
      "topic": string,
      "question_text": string,
      "keywords": string[],
      "options": [{{"index": 0, "text": "..."}}, ...]  // MCQ only, exactly 4 options, indices 0-3
      "correct_option": 0-3,  // MCQ only
      "answer_text": string,  // Descriptive only: reference answer for grading
      "language": string,     // Coding only, e.g. Python
      "test_cases": [{{"input": {{}}, "expected_output": any}}]  // Coding only, at least 2
    }}
  ]
}}

Rules:
- Provide exactly {total} questions: first {num_mcq} MCQ, next {num_desc} Descriptive, last {num_code} Coding (in that order).
- MCQ: one clearly correct option; distractors plausible.
- Descriptive: include a solid reference answer_text (5-12 sentences max).
- Coding: Python unless skills clearly imply another language; include runnable-style tests (simple inputs/outputs).
- Align topics with the listed skills (e.g. Django if Django is listed).

RAG_CONTEXT (example questions from bank — adapt, do not plagiarize):
{rag_json}
"""

    try:
        content = _chat_completions(
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            api_key=api_key,
            base_url=base_url,
            model=model,
        )
        payload = json.loads(_strip_json_fence(content))
        raw_list = payload.get("questions") or []
        out: List[Dict[str, Any]] = []
        for i, q in enumerate(raw_list):
            if not isinstance(q, dict):
                continue
            q = dict(q)
            q["id"] = q.get("id") or f"LLM_{uuid.uuid4().hex[:10].upper()}"
            if not _validate_question(q):
                logger.warning("LLM returned invalid question at index %s; skipping", i)
                continue
            out.append(q)
        if len(out) < total:
            logger.warning(
                "LLM returned %s valid questions, expected %s; falling back to bank selection",
                len(out),
                total,
            )
            return None
        return out[:total]
    except Exception as exc:
        logger.warning("RAG+LLM question generation failed: %s", exc, exc_info=True)
        return None
