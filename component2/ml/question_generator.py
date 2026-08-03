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
    """Load the trained TinyQGModel and its tokenizer."""
    model_path = os.path.join(model_dir, "model.pt")
    tokenizer_path = os.path.join(model_dir, "tokenizer.json")
    if not os.path.isfile(model_path) or not os.path.isfile(tokenizer_path):
        logger.warning("QG model files not found in %s", model_dir)
        return None, None

    try:
        # Import from the ml module directly
        ml_dir = os.path.join(os.path.dirname(model_dir), "..", "ml")
        ml_dir = os.path.abspath(ml_dir)
        if ml_dir not in sys.path:
            sys.path.insert(0, ml_dir)

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
        """Convert Q&A into MCQ by generating distractors based on keywords."""
        import random
        # Try to get distractors from fallback bank
        distractors = []
        for q in self.fallback_bank:
            if q.get("question_type") == "MCQ":
                for o in q.get("options", []):
                    t = o.get("text", "")
                    if t and t != answer and t not in distractors:
                        distractors.append(t)
        # Add generic distractors if not enough
        generic = ["None of the above", "All of the above", "It depends on the context"]
        for g in generic:
            if g not in distractors and g != answer:
                distractors.append(g)
        random.shuffle(distractors)
        distractors = distractors[:3]
        options = [{"index": 0, "text": answer}, {"index": 1, "text": distractors[0]},
                   {"index": 2, "text": distractors[1] if len(distractors) > 1 else "None of the above"},
                   {"index": 3, "text": distractors[2] if len(distractors) > 2 else "All of the above"}]
        return {
            "id": f"QG_MCQ_{random.randint(100,999):03d}",
            "question_type": "MCQ",
            "difficulty": diff,
            "category": skills[0] if skills else "General",
            "topic": skills[1] if len(skills) > 1 else diff,
            "question_text": qtext,
            "options": options,
            "correct_option": 0,
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

        if not questions:
            fallback = [q for q in self.fallback_bank if q.get("question_type") == "MCQ"][:count]
            # Ensure options are in correct format: [{"index": 0, "text": "..."}]
            for q in fallback:
                if q.get("options") and isinstance(q["options"][0], str):
                    q["options"] = [{"index": i, "text": t} for i, t in enumerate(q["options"])]
            return fallback
        return questions[:count]

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

        if not questions:
            return [q for q in self.fallback_bank if q.get("question_type") == "Descriptive"][:count]
        return questions[:count]

    def _make_coding_from_qa(self, qtext: str, answer: str, diff: str, skills: List[str]) -> Dict:
        """Convert Q&A into a coding problem stub."""
        import random
        lang = "Python" if not skills or "Python" in str(skills).lower() else skills[0]
        return {
            "id": f"QG_CODE_{random.randint(100,999):03d}",
            "question_type": "Coding",
            "difficulty": diff,
            "category": lang,
            "topic": skills[1] if len(skills) > 1 else "General",
            "question_text": f"Write a function to: {qtext.lower()}\n{answer}",
            "language": lang,
            "time_limit": 600,
            "test_cases": [{"input": {}, "expected_output": "See answer"}],
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

        if not questions:
            return [q for q in self.fallback_bank if q.get("question_type") == "Coding"][:count]
        return questions[:count]

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
        return qs
