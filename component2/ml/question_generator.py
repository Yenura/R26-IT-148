"""
Component 2: Question Generation Model - Inference Module
Loads the trained TinyQGModel and generates interview questions.
Falls back to question bank if model is unavailable.
"""

import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch

logger = logging.getLogger(__name__)


def _load_model_and_tokenizer(model_dir: str):
    """Load the trained QG model and its tokenizer.

    Tries the retrained v2 artifacts (model_v2.pt / tokenizer_v2.json /
    config.json) first, then falls back to the v1 (model.pt / tokenizer.json).
    Returns (model, tokenizer) or (None, None).
    """
    ml_dir = os.path.join(os.path.dirname(model_dir), "..", "ml")
    ml_dir = os.path.abspath(ml_dir)
    if ml_dir not in sys.path:
        sys.path.insert(0, ml_dir)

    model_v2_path = os.path.join(model_dir, "model_v2.pt")
    tokenizer_v2_path = os.path.join(model_dir, "tokenizer_v2.json")
    config_path = os.path.join(model_dir, "config.json")
    if os.path.isfile(model_v2_path) and os.path.isfile(tokenizer_v2_path) and os.path.isfile(config_path):
        try:
            from train_qg_model_v2 import load_trained_model
            model, tokenizer = load_trained_model(model_dir, device="cpu")
            logger.info("QG v2 model loaded from %s (%s params)",
                        model_dir, sum(p.numel() for p in model.parameters()))
            return model, tokenizer
        except Exception as e:
            logger.warning("Failed to load QG v2 model: %s", e)

    model_path = os.path.join(model_dir, "model.pt")
    tokenizer_path = os.path.join(model_dir, "tokenizer.json")
    if not os.path.isfile(model_path) or not os.path.isfile(tokenizer_path):
        logger.warning("QG model files not found in %s", model_dir)
        return None, None

    try:
        from train_qg_model import TinyQGModel, CharTokenizer

        tokenizer = CharTokenizer.load(tokenizer_path)
        model = TinyQGModel(vocab_size=tokenizer.vocab_size())
        model.load_state_dict(torch.load(model_path, map_location="cpu"))
        model.eval()
        logger.info("QG model loaded (%s params)", sum(p.numel() for p in model.parameters()))
        return model, tokenizer
    except Exception as e:
        logger.warning("Failed to load QG model: %s", e)
        return None, None


def _parse_q(text: str) -> str:
    m = re.search(r"[Qq]:\s*(.+?)(?:\s*[AaKkOoLlCcTt]:|$)", text)
    return m.group(1).strip() if m else text.strip()


def _parse_a(text: str) -> str:
    m = re.search(r"[Aa]:\s*(.+?)(?:\s*[QqKkOoLlCcTt]:|$)", text)
    return m.group(1).strip() if m else ""


def _parse_k(text: str) -> List[str]:
    m = re.search(r"[Kk]:\s*(.+?)(?:\s*[QqAaOoLlCcTt]:|$)", text)
    if m:
        return [k.strip() for k in m.group(1).split(",") if k.strip()]
    return []


def _parse_o(text: str) -> Tuple[List[str], int]:
    o_match = re.search(r"[Oo]:\s*(.+?)(?:\s*[QqAaKkLlCcTt]:|$)", text)
    a_match = re.search(r"[Aa]:\s*(\d+)", text)
    options = []
    if o_match:
        options = [o.strip() for o in o_match.group(1).split("|") if o.strip()]
    answer_idx = int(a_match.group(1)) if a_match else 0
    return options, answer_idx


def _parse_l(text: str) -> str:
    m = re.search(r"[Ll]:\s*(.+?)(?:\s*[QqAaKkOoCcTt]:|$)", text)
    return m.group(1).strip() if m else "Python"


def _parse_t(text: str) -> List[Dict]:
    m = re.search(r"[Tt]:\s*(\[.*?\])", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except (json.JSONDecodeError, ValueError):
            pass
    return []


def _parse_c(text: str) -> str:
    m = re.search(r"[Cc]:\s*(.+?)$", text)
    return m.group(1).strip() if m else "O(n)"


class QuestionGenerator:
    """Generates interview questions using trained TinyQGModel."""

    def __init__(
        self,
        model_path: str,
        fallback_bank: Optional[List[Dict]] = None,
        max_length: int = 128,
        temperature: float = 0.8,
    ):
        self.model_path = model_path
        self.fallback_bank = fallback_bank or []
        self.max_length = max_length
        self.temperature = temperature
        self._model = None
        self._tokenizer = None

    def _load(self):
        if self._model is not None:
            return
        self._model, self._tokenizer = _load_model_and_tokenizer(self.model_path)

    @property
    def is_available(self) -> bool:
        self._load()
        return self._model is not None

    def _generate(self, input_text: str) -> str:
        self._load()
        if self._model is None:
            return ""
        src = self._tokenizer.encode(input_text, add_special=True)
        src_tensor = torch.tensor([src], dtype=torch.long)
        with torch.no_grad():
            output_ids = self._model.generate(
                src_tensor,
                self._tokenizer,
                max_len=self.max_length,
                temperature=self.temperature,
            )
        return self._tokenizer.decode(output_ids[0].tolist())

    def _make_mcq_from_qa(self, qtext: str, answer: str, diff: str, skills: List[str]) -> Dict:
        import random
        distractors = []
        topic = skills[0] if skills else "General"
        for q in self.fallback_bank:
            if q.get("question_type") == "MCQ" and q.get("topic") == topic:
                for o in q.get("options", []):
                    t = o.get("text", "")
                    if t and t != answer and t not in distractors:
                        distractors.append(t)
        if len(distractors) < 3:
            generic = ["None of the above", "All of the above", "Cannot be determined from the given information", "Not applicable in this context"]
            for g in generic:
                if g not in distractors and g != answer:
                    distractors.append(g)
        distractors = distractors[:3]
        options = [{"index": 0, "text": answer}] + [{"index": i + 1, "text": d} for i, d in enumerate(distractors)]
        random.shuffle(options)
        correct_idx = next(i for i, o in enumerate(options) if o["text"] == answer)
        for i, o in enumerate(options):
            o["index"] = i
        return {
            "id": f"QG_MCQ_{hash(qtext) % 100000}",
            "question_type": "MCQ",
            "difficulty": diff,
            "category": topic,
            "topic": topic,
            "question_text": qtext,
            "options": options,
            "correct_option": correct_idx,
            "keywords": skills[:3],
        }

    def generate_mcq(self, job_role: str, skills: List[str], count: int = 3) -> List[Dict]:
        questions = []
        difficulties = ["Easy", "Medium", "Hard"]
        skill_str = ", ".join(skills[:4])

        for i in range(count):
            diff = difficulties[i % len(difficulties)]
            out = self._generate(f"[MCQ] {job_role} | {skill_str} | {diff}")
            qtext = _parse_q(out)
            answer = _parse_a(out)
            options, answer_idx = _parse_o(out)

            if qtext and len(options) >= 2 and answer_idx < len(options):
                opts = [{"index": j, "text": options[j]} for j in range(len(options))]
                questions.append({
                    "id": f"QG_MCQ_{i+1:03d}",
                    "question_type": "MCQ",
                    "difficulty": diff,
                    "category": skills[0] if skills else "General",
                    "topic": skills[1] if len(skills) > 1 else diff,
                    "question_text": qtext,
                    "options": opts,
                    "correct_option": answer_idx,
                    "keywords": skills[:3],
                })
            elif qtext and answer:
                # Model generated Q&A format - convert to MCQ with distractors
                questions.append(self._make_mcq_from_qa(qtext, answer, diff, skills))

        return self._top_up(questions, "MCQ", count, skills, fix_options=True)

    def generate_descriptive(self, job_role: str, skills: List[str], count: int = 3) -> List[Dict]:
        questions = []
        difficulties = ["Easy", "Medium", "Hard"]
        skill_str = ", ".join(skills[:4])

        for i in range(count):
            diff = difficulties[i % len(difficulties)]
            out = self._generate(f"[Descriptive] {job_role} | {skill_str} | {diff}")
            qtext = _parse_q(out)
            answer = _parse_a(out)
            keywords = _parse_k(out) or skills[:3]

            if qtext and answer:
                questions.append({
                    "id": f"QG_DESC_{i+1:03d}",
                    "question_type": "Descriptive",
                    "difficulty": diff,
                    "category": skills[0] if skills else "General",
                    "topic": skills[1] if len(skills) > 1 else diff,
                    "question_text": qtext,
                    "answer_text": answer,
                    "keywords": keywords,
                })

        return self._top_up(questions, "Descriptive", count, skills)

    def _make_coding_from_qa(self, qtext: str, answer: str, diff: str, skills: List[str]) -> Dict:
        import random
        lang = "Python" if not skills or "Python" in str(skills).lower() else skills[0]
        test_cases = []
        answer_lower = answer.lower().strip()
        if any(kw in answer_lower for kw in ["return ", "output:", "result:", "prints"]):
            expected = answer.split(":")[-1].strip() if ":" in answer else answer.strip()
            expected = expected.replace("return ", "").strip()
            test_cases = [{"input": "sample_input", "expected_output": expected}]
        else:
            test_cases = [{"input": "sample_input", "expected_output": None}]
        topic = skills[0] if skills else "General"
        return {
            "id": f"QG_CODE_{hash(qtext) % 100000}",
            "question_type": "Coding",
            "difficulty": diff,
            "category": lang,
            "topic": topic,
            "question_text": f"Write a function to: {qtext.lower()}\n{answer}",
            "language": lang,
            "time_limit": 600,
            "test_cases": test_cases,
            "expected_complexity": "O(n)",
            "keywords": skills[:3],
        }

    def generate_coding(self, job_role: str, skills: List[str], count: int = 2) -> List[Dict]:
        questions = []
        difficulties = ["Easy", "Medium", "Hard"]
        skill_str = ", ".join(skills[:4])

        for i in range(count):
            diff = difficulties[i % len(difficulties)]
            out = self._generate(f"[Coding] {job_role} | {skill_str} | {diff}")
            qtext = _parse_q(out)
            lang = _parse_l(out)
            test_cases = _parse_t(out)
            complexity = _parse_c(out)
            answer = _parse_a(out)

            if qtext and test_cases:
                questions.append({
                    "id": f"QG_CODE_{i+1:03d}",
                    "question_type": "Coding",
                    "difficulty": diff,
                    "category": lang,
                    "topic": skills[1] if len(skills) > 1 else "General",
                    "question_text": qtext,
                    "language": lang,
                    "time_limit": 600,
                    "test_cases": test_cases,
                    "expected_complexity": complexity,
                    "keywords": skills[:3],
                })
            elif qtext and answer:
                # Model generated Q&A - convert to coding problem
                questions.append(self._make_coding_from_qa(qtext, answer, diff, skills))

        return self._top_up(questions, "Coding", count, skills)

    def generate_for_session(
        self, job_role: str, skills: List[str], num_mcq: int, num_desc: int, num_code: int
    ) -> List[Dict]:
        qs = []
        if num_mcq > 0:
            qs.extend(self.generate_mcq(job_role, skills, num_mcq))
        if num_desc > 0:
            qs.extend(self.generate_descriptive(job_role, skills, num_desc))
        if num_code > 0:
            qs.extend(self.generate_coding(job_role, skills, num_code))

        # Post-generation relevance filter: remove questions whose category/topic
        # has zero overlap with the role's required skills.
        if skills:
            skill_lower = {s.lower() for s in skills}
            filtered = []
            for q in qs:
                cat = q.get("category", "").lower()
                topic = q.get("topic", "").lower()
                text = q.get("question_text", "").lower()
                relevant = any(
                    sk in cat or sk in topic or sk in text
                    for sk in skill_lower
                )
                if relevant:
                    filtered.append(q)
            # Only use filtered set if it didn't strip everything
            if filtered:
                qs = filtered

        return qs

    def _filter_fallback(self, questions: List[Dict], skills: List[str]) -> List[Dict]:
        """Filter fallback questions to only include those relevant to the given skills."""
        if not skills:
            return questions
        skill_lower = {s.lower() for s in skills}
        filtered = []
        for q in questions:
            cat = q.get("category", "").lower()
            topic = q.get("topic", "").lower()
            text = q.get("question_text", "").lower()
            if any(sk in cat or sk in topic or sk in text for sk in skill_lower):
                filtered.append(q)
        return filtered

    def _get_relevant_from_bank(self, question_type: str, count: int, skills: List[str]) -> List[Dict]:
        """Pull questions from the fallback bank filtered by skill relevance."""
        if not skills:
            return [q for q in self.fallback_bank if q.get("question_type") == question_type][:count]
        skill_lower = {s.lower() for s in skills}
        relevant = []
        for q in self.fallback_bank:
            if q.get("question_type") != question_type:
                continue
            cat = q.get("category", "").lower()
            topic = q.get("topic", "").lower()
            text = q.get("question_text", "").lower()
            if any(sk in cat or sk in topic or sk in text for sk in skill_lower):
                relevant.append(q)
                if len(relevant) >= count:
                    break
        # If not enough relevant, top up from any typed questions
        if len(relevant) < count:
            for q in self.fallback_bank:
                if q.get("question_type") == question_type and q not in relevant:
                    relevant.append(q)
                    if len(relevant) >= count:
                        break
        return relevant[:count]

    def _top_up(self, questions: List[Dict], question_type: str, count: int,
                skills: List[str], fix_options: bool = False) -> List[Dict]:
        if len(questions) >= count:
            return questions[:count]
        needed = count - len(questions)
        extra = self._get_relevant_from_bank(question_type, needed, skills)
        seen_ids = {q.get("id") for q in questions}
        seen_texts = {q.get("question_text", "")[:80] for q in questions}
        for q in extra:
            if len(questions) >= count:
                break
            qid = q.get("id")
            qtext = q.get("question_text", "")[:80]
            if qid in seen_ids or qtext in seen_texts:
                continue
            if fix_options and q.get("options") and isinstance(q["options"][0], str):
                q["options"] = [{"index": i, "text": t} for i, t in enumerate(q["options"])]
            questions.append(q)
            seen_ids.add(qid)
            seen_texts.add(qtext)
        return questions[:count]
