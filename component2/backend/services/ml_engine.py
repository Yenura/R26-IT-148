"""
Component 2: Interview System - Service Layer
Handles business logic for interview generation, submission, and evaluation
"""

import json
import os
import re
import sys
import uuid
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path
import logging

from services.qg_engine import generate_questions_qg, merge_skill_lists

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InterviewService:
    """
    Manages interview sessions, question generation, and answer evaluation
    """
    
    def __init__(self, models_dir: str):
        """
        Initialize interview service
        
        Args:
            models_dir: Directory containing trained models and configs
        """
        self.models_dir = models_dir
        self.question_bank = None
        self.job_requirements = None
        self.interview_configs = {}
        
        self._load_resources()
    
    def _load_resources(self):
        """Load all required resources"""
        # Load question bank
        qb_path = os.path.join(self.models_dir, "question_bank.json")
        if os.path.exists(qb_path):
            try:
                with open(qb_path, 'r', encoding="utf-8") as f:
                    self.question_bank = json.load(f)
                logger.info(f"✓ Loaded {len(self.question_bank)} questions")
            except Exception as e:
                logger.warning(f"⚠ Error loading question bank: {e}")
                self.question_bank = []
        else:
            logger.warning(f"⚠ Question bank not found: {qb_path}")
            self.question_bank = []

        if not self.question_bank:
            self.question_bank = self._default_question_bank()
            logger.warning("⚠ Using built-in fallback question bank (%d questions)", len(self.question_bank))
        
        # Load job requirements
        jr_path = os.path.join(self.models_dir, "job_requirements.json")
        if os.path.exists(jr_path):
            try:
                with open(jr_path, 'r', encoding="utf-8") as f:
                    self.job_requirements = json.load(f)
                logger.info(f"✓ Loaded job requirements for {len(self.job_requirements)} roles")
            except Exception as e:
                logger.warning(f"⚠ Error loading job requirements: {e}")
                self.job_requirements = self._default_job_requirements()
        else:
            logger.warning(f"⚠ Job requirements not found: {jr_path}")
            self.job_requirements = self._default_job_requirements()
        
        # Load scoring configuration
        sc_path = os.path.join(self.models_dir, "interview_scoring_config.json")
        if os.path.exists(sc_path):
            try:
                with open(sc_path, 'r', encoding="utf-8") as f:
                    self.interview_configs = json.load(f)
                logger.info("✓ Loaded interview scoring configuration")
            except Exception as e:
                logger.warning(f"⚠ Error loading scoring config: {e}")
                self.interview_configs = self._default_scoring_config()
        else:
            logger.warning(f"⚠ Scoring config not found: {sc_path}")
            self.interview_configs = self._default_scoring_config()
    
    def _default_job_requirements(self) -> Dict[str, List[str]]:
        """Return default job requirements when config file is missing"""
        return {
            "Software Engineer": ["Java", "Python", "C++", "SQL", "React", "REST APIs", "OOP", "Design Patterns"],
            "Data Scientist": ["Python", "Machine Learning", "SQL", "Statistics", "Deep Learning", "Data Analysis", "Pandas", "NumPy"],
            "Machine Learning Engineer": ["Python", "TensorFlow", "PyTorch", "MLOps", "Model Training", "Data Pipeline", "Scikit-learn"],
            "DevOps Engineer": ["Docker", "Kubernetes", "CI/CD", "AWS", "Linux", "Git", "Infrastructure as Code", "Monitoring"],
            "Cybersecurity Analyst": ["Cybersecurity", "Networking", "Linux", "Ethical Hacking", "SIEM", "Threat Detection", "Encryption", "Vulnerability Assessment"],
            "Cloud Solutions Architect": ["AWS", "GCP", "Azure", "Cloud Architecture", "Scalability", "Security", "Microservices", "Load Balancing"],
            "Database Administrator": ["SQL", "NoSQL", "Database Optimization", "Backup and Recovery", "Indexing", "Replication", "MongoDB", "PostgreSQL"],
            "Frontend Developer": ["React", "JavaScript", "CSS", "HTML", "Vue", "TypeScript", "UI/UX", "Accessibility", "DOM", "Responsive Design"],
            "Backend Developer": ["Python", "Java", "Node.js", "APIs", "Microservices", "SQL", "Database Design", "Server-side Logic", "Authentication"],
            "Mobile App Developer": ["React Native", "Flutter", "iOS", "Android", "Kotlin", "Swift", "Mobile UI", "Performance Optimization"]
        }

    def _default_question_bank(self) -> List[Dict]:
        """Return a small but usable fallback question bank for local runs."""
        return [
            {
                "id": "FB_MCQ_001",
                "question_text": "What is the primary purpose of an index in SQL databases?",
                "question_type": "MCQ",
                "difficulty": "Easy",
                "category": "SQL",
                "topic": "Database Optimization",
                "options": [
                    {"index": 0, "text": "To increase table size"},
                    {"index": 1, "text": "To speed up query lookups"},
                    {"index": 2, "text": "To encrypt all records"},
                    {"index": 3, "text": "To replace primary keys"},
                ],
                "correct_option": 1,
                "keywords": ["sql", "index", "query"],
            },
            {
                "id": "FB_MCQ_002",
                "question_text": "Which HTTP method is commonly used to partially update a resource?",
                "question_type": "MCQ",
                "difficulty": "Easy",
                "category": "REST APIs",
                "topic": "HTTP Methods",
                "options": [
                    {"index": 0, "text": "GET"},
                    {"index": 1, "text": "PATCH"},
                    {"index": 2, "text": "DELETE"},
                    {"index": 3, "text": "HEAD"},
                ],
                "correct_option": 1,
                "keywords": ["http", "rest", "patch"],
            },
            {
                "id": "FB_MCQ_003",
                "question_text": "Which React feature is used for component state in function components?",
                "question_type": "MCQ",
                "difficulty": "Easy",
                "category": "React",
                "topic": "Hooks",
                "options": [
                    {"index": 0, "text": "useState"},
                    {"index": 1, "text": "useMemo"},
                    {"index": 2, "text": "useRef"},
                    {"index": 3, "text": "useId"},
                ],
                "correct_option": 0,
                "keywords": ["react", "hooks", "state"],
            },
            {
                "id": "FB_DESC_001",
                "question_text": "Explain polymorphism in object-oriented programming with an example.",
                "answer_text": "Polymorphism allows objects of different classes to be treated through a common interface, often via method overriding.",
                "question_type": "Descriptive",
                "difficulty": "Medium",
                "category": "OOP",
                "topic": "Design Patterns",
                "keywords": ["polymorphism", "oop", "overriding"],
            },
            {
                "id": "FB_DESC_002",
                "question_text": "How would you design a scalable REST API for high traffic?",
                "answer_text": "A scalable REST API typically uses stateless services, caching, pagination, load balancing, and database indexing.",
                "question_type": "Descriptive",
                "difficulty": "Hard",
                "category": "Backend",
                "topic": "REST APIs",
                "keywords": ["api", "scaling", "caching", "load balancing"],
            },
            {
                "id": "FB_DESC_003",
                "question_text": "What is overfitting in machine learning and how can it be reduced?",
                "answer_text": "Overfitting happens when a model learns training noise; reduce it using regularization, cross-validation, dropout, and more data.",
                "question_type": "Descriptive",
                "difficulty": "Medium",
                "category": "Machine Learning",
                "topic": "Model Validation",
                "keywords": ["overfitting", "regularization", "cross-validation"],
            },
            {
                "id": "FB_DESC_004",
                "question_text": "Why is CI/CD important for DevOps teams?",
                "answer_text": "CI/CD automates build, test, and release workflows to reduce risk and speed up delivery.",
                "question_type": "Descriptive",
                "difficulty": "Easy",
                "category": "DevOps",
                "topic": "CI/CD",
                "keywords": ["devops", "automation", "pipeline"],
            },
            {
                "id": "FB_CODE_001",
                "question_text": "Write a function that returns the sum of two integers.",
                "question_type": "Coding",
                "difficulty": "Easy",
                "category": "Python",
                "topic": "Functions",
                "language": "Python",
                "time_limit": 600,
                "test_cases": [
                    {"input": {"a": 2, "b": 3}, "expected_output": 5},
                    {"input": {"a": -1, "b": 1}, "expected_output": 0},
                ],
                "expected_complexity": "O(1)",
                "keywords": ["python", "function"],
            },
            {
                "id": "FB_CODE_002",
                "question_text": "Write a function to reverse a string.",
                "question_type": "Coding",
                "difficulty": "Easy",
                "category": "Python",
                "topic": "Strings",
                "language": "Python",
                "time_limit": 600,
                "test_cases": [
                    {"input": {"s": "abc"}, "expected_output": "cba"},
                    {"input": {"s": "level"}, "expected_output": "level"},
                ],
                "expected_complexity": "O(n)",
                "keywords": ["python", "string"],
            },
            {
                "id": "FB_CODE_003",
                "question_text": "Write an SQL query to return all employees with salary greater than 50000.",
                "question_type": "Coding",
                "difficulty": "Medium",
                "category": "SQL",
                "topic": "Query Writing",
                "language": "SQL",
                "time_limit": 600,
                "test_cases": [
                    {"input": {"table": "employees"}, "expected_output": "select"},
                ],
                "expected_complexity": "O(n)",
                "keywords": ["sql", "query", "select"],
            },
            {
                "id": "FB_CODE_004",
                "question_text": "Given an array of integers, return indices of two numbers that add up to target.",
                "question_type": "Coding",
                "difficulty": "Medium",
                "category": "Algorithms",
                "topic": "Array",
                "language": "Python",
                "time_limit": 900,
                "test_cases": [
                    {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected_output": [0, 1]},
                    {"input": {"nums": [3, 2, 4], "target": 6}, "expected_output": [1, 2]},
                ],
                "expected_complexity": "O(n)",
                "keywords": ["array", "hash map"],
            },
            {
                "id": "FB_CODE_005",
                "question_text": "Write a Dockerfile for a basic Python web app and explain each layer.",
                "question_type": "Coding",
                "difficulty": "Medium",
                "category": "DevOps",
                "topic": "Docker",
                "language": "Text",
                "time_limit": 900,
                "test_cases": [
                    {"input": {"artifact": "dockerfile"}, "expected_output": "from"},
                ],
                "expected_complexity": "O(1)",
                "keywords": ["docker", "dockerfile", "devops"],
            },
        ]
    
    def _determine_coding_profile(self, job_role: str, required_skills: List[str]) -> str:
        """Determine the coding profile based on job role and skill keywords."""
        trigger_keywords = {
            "Python", "Java", "JavaScript", "C++", "C#", "SQL", "Kotlin", "Swift",
            "TypeScript", "React", "Vue", "Node.js", "Flutter", "React Native",
            "TensorFlow", "PyTorch", "HTML", "CSS"
        }
        skill_text = " ".join(required_skills).lower()

        # Role-specific overrides for known edge cases
        if job_role == "DevOps Engineer":
            return "scripting"
        if job_role in {"Cybersecurity Analyst", "Cloud Solutions Architect"}:
            return "none"

        has_language = any(keyword.lower() in skill_text for keyword in trigger_keywords if keyword != "SQL")
        has_sql = any("sql" in skill.lower() for skill in required_skills)

        if has_language:
            return "full"
        if has_sql:
            return "sql"
        return "none"

    def _get_question_distribution(self, job_role: str, coding_profile: str, num_questions: int) -> Tuple[int, int, int]:
        """Return MCQ/Descriptive/Coding question counts for the role."""
        distribution = {
            "Software Engineer": (0.20, 0.30, 0.50),
            "Data Scientist": (0.25, 0.35, 0.40),
            "Machine Learning Engineer": (0.20, 0.30, 0.50),
            "DevOps Engineer": (0.40, 0.40, 0.20),
            "Cybersecurity Analyst": (0.45, 0.55, 0.00),
            "Cloud Solutions Architect": (0.45, 0.55, 0.00),
            "Database Administrator": (0.30, 0.40, 0.30),
            "Frontend Developer": (0.20, 0.30, 0.50),
            "Backend Developer": (0.20, 0.30, 0.50),
            "Mobile App Developer": (0.20, 0.30, 0.50)
        }
        mcq_pct, desc_pct, code_pct = distribution.get(job_role, (0.30, 0.40, 0.30))

        if coding_profile == "none":
            code_pct = 0.0
        if coding_profile == "scripting":
            mcq_pct, desc_pct, code_pct = 0.40, 0.40, 0.20
        if coding_profile == "sql" and job_role == "Database Administrator":
            mcq_pct, desc_pct, code_pct = 0.30, 0.40, 0.30

        mcq_count = int(num_questions * mcq_pct)
        desc_count = int(num_questions * desc_pct)
        code_count = int(num_questions * code_pct)

        remainder = num_questions - (mcq_count + desc_count + code_count)
        for idx in range(remainder):
            if code_pct >= desc_pct and code_pct >= mcq_pct:
                code_count += 1
            elif desc_pct >= mcq_pct:
                desc_count += 1
            else:
                mcq_count += 1

        return mcq_count, desc_count, code_count

    def _default_scoring_config(self) -> Dict:
        """Return default scoring configuration when config file is missing"""
        return {
            "interview_weights": {
                "Software Engineer": {"mcq": 0.20, "descriptive": 0.30, "coding": 0.50},
                "Data Scientist": {"mcq": 0.25, "descriptive": 0.35, "coding": 0.40},
                "Machine Learning Engineer": {"mcq": 0.20, "descriptive": 0.30, "coding": 0.50},
                "DevOps Engineer": {"mcq": 0.40, "descriptive": 0.40, "coding": 0.20},
                "Cybersecurity Analyst": {"mcq": 0.45, "descriptive": 0.55, "coding": 0.00},
                "Cloud Solutions Architect": {"mcq": 0.45, "descriptive": 0.55, "coding": 0.00},
                "Database Administrator": {"mcq": 0.30, "descriptive": 0.40, "coding": 0.30},
                "Frontend Developer": {"mcq": 0.20, "descriptive": 0.30, "coding": 0.50},
                "Backend Developer": {"mcq": 0.20, "descriptive": 0.30, "coding": 0.50},
                "Mobile App Developer": {"mcq": 0.20, "descriptive": 0.30, "coding": 0.50}
            },
            "grade_bands": {
                "Excellent": {"min": 85},
                "Good": {"min": 70},
                "Average": {"min": 55},
                "Below Average": {"min": 40},
                "Poor": {"min": 0}
            }
        }
    
    def get_available_jobs(self) -> List[str]:
        """Get list of available job roles"""
        return list(self.job_requirements.keys())
    
    def get_job_skills(self, job_role: str) -> List[str]:
        """Get required skills for a job role"""
        return self.job_requirements.get(job_role, [])
    
    def create_interview_session(
        self,
        candidate_id: str,
        job_role: str,
        num_questions: int = 10,
        employer_skills: Optional[List[str]] = None,
    ) -> Dict:
        """
        Create interview session with questions
        
        Args:
            candidate_id: Candidate ID
            job_role: Target job role
            num_questions: Number of questions to generate
            employer_skills: Optional skills from employer posting (merged with role defaults)

        Returns:
            Interview session dictionary
        """
        if job_role not in self.job_requirements:
            raise ValueError(f"Invalid job role: {job_role}")
        
        # Merge employer-posted skills with role defaults (employer order preserved)
        required_skills = merge_skill_lists(self.job_requirements[job_role], employer_skills)
        coding_profile = self._determine_coding_profile(job_role, required_skills)
        num_mcq, num_desc, num_code = self._get_question_distribution(
            job_role, coding_profile, num_questions
        )

        qg_questions = generate_questions_qg(
            job_role=job_role,
            skills=required_skills,
            num_mcq=num_mcq,
            num_desc=num_desc,
            num_code=num_code,
            coding_profile=coding_profile,
        )

        if qg_questions:
            all_questions = qg_questions
            mcq_questions = [q for q in all_questions if q.get("question_type") == "MCQ"]
            desc_questions = [q for q in all_questions if q.get("question_type") == "Descriptive"]
            code_questions = [q for q in all_questions if q.get("question_type") == "Coding"]
            logger.info("Interview session using QG model generated questions (%s items)", len(all_questions))
        else:
            # Select questions by type from bank
            mcq_questions = self._select_questions_by_type(
                "MCQ", num_mcq, required_skills
            )
            desc_questions = self._select_questions_by_type(
                "Descriptive", num_desc, required_skills
            )
            code_questions = self._select_questions_by_type(
                "Coding", num_code, required_skills,
                coding_profile=coding_profile
            )

            # Combine all questions and top up if bank is smaller than requested count.
            all_questions = mcq_questions + desc_questions + code_questions
            if len(all_questions) < num_questions:
                all_questions = self._top_up_questions(all_questions, num_questions, coding_profile=coding_profile)
        
        # Create session with high-entropy ID to avoid collisions.
        candidate_prefix = re.sub(r"[^A-Za-z0-9]", "", candidate_id or "CAND")[:4].upper() or "CAND"
        session_id = f"INT_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{candidate_prefix}_{uuid.uuid4().hex[:6].upper()}"
        
        # Log warning if any question type is missing
        missing_types = []
        if not mcq_questions:
            missing_types.append("MCQ")
        if not desc_questions:
            missing_types.append("Descriptive")
        if not code_questions:
            missing_types.append("Coding")
        
        session = {
            "session_id": session_id,
            "candidate_id": candidate_id,
            "job_role": job_role,
            "required_skills": required_skills,
            "coding_profile": coding_profile,
            "questions": all_questions,
            "question_count": {
                "mcq": sum(1 for q in all_questions if q.get("question_type") == "MCQ"),
                "descriptive": sum(1 for q in all_questions if q.get("question_type") == "Descriptive"),
                "coding": sum(1 for q in all_questions if q.get("question_type") == "Coding"),
            },
            "total_questions": len(all_questions),
            "created_at": datetime.utcnow().isoformat(),
            "status": "created"
        }
        
        if missing_types:
            logger.warning(f"⚠ Created interview session {session_id} with missing question types: {', '.join(missing_types)}. Weights will be redistributed during evaluation.")
        else:
            logger.info(f"Created interview session {session_id} for {candidate_id}")
        
        return session

    def _top_up_questions(self, selected_questions: List[Dict], target_count: int, coding_profile: str = "full") -> List[Dict]:
        """Top up with unused unique questions first; only repeat as last resort."""
        if not selected_questions:
            return []

        topped_up = list(selected_questions)
        existing_ids = {q.get("id") for q in topped_up if q.get("id")}
        existing_texts = {q.get("question_text", "").strip().lower() for q in topped_up if q.get("question_text")}

        # 1) Fill from remaining bank with unseen question text.
        for candidate in self.question_bank:
            if len(topped_up) >= target_count:
                break
            cid = candidate.get("id")
            ctext = candidate.get("question_text", "").strip().lower()
            if not ctext or cid in existing_ids or ctext in existing_texts:
                continue
            if candidate.get("question_type") == "Coding" and coding_profile in {"sql", "scripting"}:
                if not self._filter_coding_questions_by_profile([candidate], coding_profile):
                    continue
            topped_up.append(candidate)
            if cid:
                existing_ids.add(cid)
            existing_texts.add(ctext)

        # 2) If still short, repeat selected pool with unique IDs.
        idx = 1
        while len(topped_up) < target_count and selected_questions:
            source = selected_questions[(idx - 1) % len(selected_questions)].copy()
            source["id"] = f"{source.get('id', 'Q')}_R{idx}"
            topped_up.append(source)
            idx += 1
        return topped_up
    
    def _select_questions_by_type(self, question_type: str, 
                                  count: int, 
                                  relevant_skills: List[str],
                                  coding_profile: str = "full") -> List[Dict]:
        """
        Select questions by type with relevance filtering
        
        Args:
            question_type: MCQ, Descriptive, or Coding
            count: Number of questions to select
            relevant_skills: Skills to filter by
            coding_profile: Coding profile for Coding questions
            
        Returns:
            List of selected questions
        """
        # Filter by type
        typed_questions = [
            q for q in self.question_bank 
            if q.get("question_type") == question_type
        ]
        
        if not typed_questions:
            logger.warning(f"No {question_type} questions found")
            return []

        if question_type == "Coding":
            typed_questions = self._filter_coding_questions_by_profile(
                typed_questions, coding_profile
            )
            if not typed_questions:
                logger.warning(f"No coding questions found for profile: {coding_profile}. Falling back to generic coding questions.")
                typed_questions = [
                    q for q in self.question_bank 
                    if q.get("question_type") == "Coding"
                ]
        
        # Filter by relevance to skills; if none match, fall back to generic typed questions.
        relevant_questions = []
        for q in typed_questions:
            category = q.get("category", "").lower()
            topic = q.get("topic", "").lower()
            question_text = q.get("question_text", "").lower()

            is_relevant = any(
                skill.lower() in category
                or skill.lower() in topic
                or skill.lower() in question_text
                for skill in relevant_skills
            )
            if is_relevant:
                relevant_questions.append(q)

        if relevant_questions:
            return relevant_questions[:count]

        # No relevant questions found; fall back to typed pool but skip
        # obviously-off-topic categories (e.g. Java for Data Scientist).
        off_topic_cats = {"java", "javascript", "typescript", "ruby", "php", "swift", "kotlin", "go", "rust", "c++", "c#", "scala"}
        safe = [q for q in typed_questions if q.get("category", "").lower() not in off_topic_cats]
        logger.warning("FALLBACK: typed=%d, relevant=%d, safe=%d (off_topic_cats=%s, skill_cats=%s, categories=%s)",
                       len(typed_questions), len(relevant_questions), len(safe), off_topic_cats,
                       [s.lower() for s in relevant_skills],
                       [q.get("category", "") for q in typed_questions[:5]])
        return (safe if safe else typed_questions)[:count]
    
    def _filter_coding_questions_by_profile(self, coding_questions: List[Dict], profile: str) -> List[Dict]:
        """Filter coding questions based on SQL, scripting, or full coding profiles."""
        if profile == "sql":
            keywords = ["sql", "query", "database", "schema", "index", "join", "select"]
        elif profile == "scripting":
            keywords = ["docker", "kubernetes", "ci/cd", "pipeline", "yaml", "shell", "git", "terraform", "dockerfile", "github actions", "bash"]
        else:
            return coding_questions

        filtered = []
        for q in coding_questions:
            text = " ".join([
                str(q.get("category", "")),
                str(q.get("topic", "")),
                str(q.get("question_text", ""))
            ]).lower()
            if any(keyword in text for keyword in keywords):
                filtered.append(q)

        return filtered
    
    def evaluate_interview(self, session_id: str, interview_data: Dict) -> Dict:
        """
        Evaluate completed interview with fair weight redistribution
        
        Args:
            session_id: Interview session ID
            interview_data: Interview data with answers
            
        Returns:
            Score result dictionary
        """
        candidate_id = interview_data.get("candidate_id")
        job_role = interview_data.get("job_role")
        answers = interview_data.get("answers", [])
        
        # Separate answers by type
        mcq_answers = [a for a in answers if a.get("question_type") == "MCQ"]
        desc_answers = [a for a in answers if a.get("question_type") == "Descriptive"]
        code_answers = [a for a in answers if a.get("question_type") == "Coding"]
        
        # Evaluate each type
        mcq_score = self._evaluate_mcq_answers(mcq_answers)
        desc_score = self._evaluate_descriptive_answers(desc_answers)
        code_score = self._evaluate_coding_answers(code_answers)
        
        # Get original weights for this job role
        original_weights = self.interview_configs.get("interview_weights", {}).get(
            job_role,
            {"mcq": 0.25, "descriptive": 0.35, "coding": 0.40}
        )
        
        # Determine which question types have answers (are available)
        has_mcq = len(mcq_answers) > 0
        has_descriptive = len(desc_answers) > 0
        has_coding = len(code_answers) > 0
        
        # Normalize weights based on available question types
        weights, weight_adjustment_applied = self._normalize_weights(
            original_weights, has_mcq, has_descriptive, has_coding
        )
        
        # Calculate final interview score with normalized weights
        interview_score = (
            weights.get("mcq", 0.25) * mcq_score +
            weights.get("descriptive", 0.35) * desc_score +
            weights.get("coding", 0.40) * code_score
        )
        
        # Determine grade
        grade_bands = self.interview_configs.get("grade_bands", {})
        grade = self._get_grade(interview_score, grade_bands)
        
        # Identify weak topics
        weak_topics = self._identify_weak_topics(
            mcq_answers, desc_answers, code_answers,
            mcq_score, desc_score, code_score
        )
        
        mcq_correct = sum(1 for a in mcq_answers if a.get("is_correct", False))
        coding_tests_passed = sum(a.get("tests_passed", 0) for a in code_answers)
        
        result = {
            "interview_id": f"RES_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "session_id": session_id,
            "candidate_id": candidate_id,
            "job_role": job_role,
            "mcq_score": round(mcq_score, 2),
            "descriptive_score": round(desc_score, 2),
            "coding_score": round(code_score, 2),
            "interview_score": round(interview_score, 2),
            "grade": grade,
            "original_weights": original_weights,
            "weights_used": weights,
            "weight_adjustment_applied": weight_adjustment_applied,
            "mcq_total": len(mcq_answers),
            "mcq_correct": mcq_correct,
            "descriptive_total": len(desc_answers),
            "coding_total": len(code_answers),
            "coding_tests_passed": coding_tests_passed,
            "weak_topics": weak_topics[:5],  # Top 5 weak areas
            "created_at": datetime.utcnow().isoformat()
        }
        
        if weight_adjustment_applied:
            logger.info(f"Evaluated interview {session_id}: Score={interview_score}, Grade={grade} (weights redistributed due to missing question types)")
        else:
            logger.info(f"Evaluated interview {session_id}: Score={interview_score}, Grade={grade}")
        
        return result
    
    def _evaluate_mcq_answers(self, answers: List[Dict]) -> float:
        if not answers:
            return 0
        correct_count = sum(1 for a in answers if a.get("is_correct", False))
        return round(correct_count / len(answers) * 100, 2)
    
    def _evaluate_descriptive_answers(self, answers: List[Dict]) -> float:
        """Evaluate descriptive answers"""
        if not answers:
            return 0
        
        # Average of individual scores
        scores = [
            a.get("final_score", 0) for a in answers
        ]
        
        score = sum(scores) / len(scores) if scores else 0
        return float(score)
    
    def _evaluate_coding_answers(self, answers: List[Dict]) -> float:
        """Evaluate coding answers"""
        if not answers:
            return 0
        
        # Average of individual scores
        scores = [
            a.get("code_score", 0) for a in answers
        ]
        
        score = sum(scores) / len(scores) if scores else 0
        return float(score)
    
    def _get_grade(self, score: float, grade_bands: Dict) -> str:
        """Get grade based on score"""
        for grade_name in ["Excellent", "Good", "Average", "Below Average", "Poor"]:
            band = grade_bands.get(grade_name, {})
            if score >= band.get("min", 0):
                return grade_name
        
        return "Poor"
    
    def _normalize_weights(self, original_weights: Dict[str, float],
                           has_mcq: bool, has_descriptive: bool,
                           has_coding: bool) -> Tuple[Dict[str, float], bool]:
        if has_mcq and has_descriptive and has_coding:
            return original_weights, False
        weights = original_weights.copy()
        adjustment_applied = False
        missing_weight = 0
        if not has_mcq:
            missing_weight += weights.get("mcq", 0.25)
            weights["mcq"] = 0
            adjustment_applied = True
        if not has_descriptive:
            missing_weight += weights.get("descriptive", 0.35)
            weights["descriptive"] = 0
            adjustment_applied = True
        if not has_coding:
            missing_weight += weights.get("coding", 0.40)
            weights["coding"] = 0
            adjustment_applied = True
        if adjustment_applied and missing_weight > 0:
            available = {k: v for k, v in weights.items() if v > 0}
            total_available = sum(available.values())
            if total_available > 0:
                for k in available:
                    weights[k] += missing_weight * (weights[k] / total_available)
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}
        return weights, adjustment_applied
    
    def _identify_weak_topics(self, mcq_answers: List, 
                             desc_answers: List,
                             code_answers: List,
                             mcq_score: float,
                             desc_score: float,
                             code_score: float) -> List[str]:
        weak_topics = []
        if mcq_score < 70:
            for a in mcq_answers:
                if not a.get("is_correct", False):
                    topic = a.get("topic", "")
                    if topic:
                        weak_topics.append(topic)
        if desc_score < 70:
            for a in desc_answers:
                if a.get("final_score", 100) < 60:
                    topic = a.get("topic", "")
                    if topic:
                        weak_topics.append(topic)
        if code_score < 70:
            for a in code_answers:
                topic = a.get("topic", "")
                if topic:
                    weak_topics.append(topic)
                else:
                    weak_topics.append("Coding")
        seen = set()
        unique = []
        for t in weak_topics:
            if t not in seen:
                seen.add(t)
                unique.append(t)
        return unique[:5]


class AnswerEvaluationService:
    """
    Evaluates individual answers using ML models
    """
    
    def __init__(self, models_dir: str):
        """
        Initialize evaluation service
        
        Args:
            models_dir: Directory containing trained models
        """
        self.models_dir = models_dir
        
        # Import ML evaluators
        try:
            # Add ML directory to path
            ml_dir = os.path.join(models_dir, "..", "ml")
            if os.path.exists(ml_dir):
                sys.path.insert(0, ml_dir)
            
            from answer_evaluator import (
                DescriptiveAnswerEvaluator,
                MCQEvaluator,
                CodingEvaluator
            )
            
            self.desc_evaluator = DescriptiveAnswerEvaluator()
            self.mcq_evaluator = MCQEvaluator()
            self.code_evaluator = CodingEvaluator()
            
            logger.info("✓ Evaluation models initialized")
            
        except Exception as e:
            logger.warning(f"Could not load ML models: {e}")
            self.desc_evaluator = None
            self.mcq_evaluator = None
            self.code_evaluator = None
    
    def evaluate_mcq(self, correct_option: int, 
                    candidate_option: int) -> Dict:
        """Evaluate MCQ answer"""
        if not self.mcq_evaluator:
            is_correct = correct_option == candidate_option
            return {"is_correct": is_correct, "score": 100 if is_correct else 0}
        
        score = self.mcq_evaluator.evaluate_single_mcq(correct_option, candidate_option)
        return {
            "is_correct": score > 0,
            "score": (score + 1) * 50  # Normalize to 0-100
        }
    
    def evaluate_descriptive(self, reference: str, candidate: str) -> Dict:
        """Evaluate descriptive answer"""
        if not self.desc_evaluator:
            reference_tokens = set(re.findall(r"\w+", (reference or "").lower()))
            candidate_tokens = set(re.findall(r"\w+", (candidate or "").lower()))
            if not candidate_tokens:
                return {"final_score": 0.0, "similarity": 0.0, "keyword_coverage": 0.0}

            intersection = reference_tokens.intersection(candidate_tokens)
            similarity = len(intersection) / max(len(reference_tokens), 1)

            keywords = reference_tokens
            matched_keywords = len([t for t in keywords if t in candidate_tokens])
            keyword_coverage = matched_keywords / max(len(keywords), 1)

            final_score = round((similarity * 0.7 + keyword_coverage * 0.3) * 100, 2)
            return {
                "final_score": final_score,
                "similarity": round(similarity, 2),
                "keyword_coverage": round(keyword_coverage, 2)
            }

        result = self.desc_evaluator.evaluate_descriptive_answer(reference, candidate)
        return result

    def evaluate_coding(self, code_text: str, test_cases: List[Dict]) -> Dict:
        """Evaluate coding answer"""
        if not self.code_evaluator:
            syntax_valid = False
            tests_passed = 0
            total_tests = len(test_cases or [])
            code_text = code_text or ""

            if code_text:
                try:
                    compile(code_text, "<submitted_code>", "exec")
                    syntax_valid = True
                except SyntaxError:
                    syntax_valid = False

                if syntax_valid and total_tests > 0:
                    lowered = code_text.lower()
                    for tc in test_cases:
                        expected = str(tc.get("expected_output", "")).lower()
                        if expected and expected in lowered:
                            tests_passed += 1

            test_pass_rate = round((tests_passed / total_tests * 100) if total_tests else (100 if syntax_valid else 0), 2)
            base_score = 70 if syntax_valid else (40 if code_text else 0)
            quality_score = min(1.0, len(code_text) / 800)
            code_score = round(min(100.0, base_score + test_pass_rate * 0.15 + quality_score * 10), 2)

            return {
                "code_score": code_score,
                "syntax_valid": syntax_valid,
                "test_pass_rate": test_pass_rate,
                "tests_passed": tests_passed,
                "total_tests": total_tests,
                "quality_score": round(quality_score, 2)
            }

        result = self.code_evaluator.evaluate_coding_answer(code_text, test_cases)
        return result


# Singleton instances
_interview_service = None
_evaluation_service = None


def get_interview_service(models_dir: str) -> InterviewService:
    """Get or create interview service"""
    global _interview_service
    if _interview_service is None:
        _interview_service = InterviewService(models_dir)
    return _interview_service


def get_evaluation_service(models_dir: str) -> AnswerEvaluationService:
    """Get or create evaluation service"""
    global _evaluation_service
    if _evaluation_service is None:
        _evaluation_service = AnswerEvaluationService(models_dir)
    return _evaluation_service
