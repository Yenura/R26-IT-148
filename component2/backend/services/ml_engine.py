"""
Component 2: Interview System - Service Layer
Handles business logic for interview generation, submission, and evaluation
"""

import json
import os
import sys
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path
import logging

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
        try:
            # Load question bank
            qb_path = os.path.join(self.models_dir, "question_bank.json")
            with open(qb_path, 'r') as f:
                self.question_bank = json.load(f)
            logger.info(f"✓ Loaded {len(self.question_bank)} questions")
            
            # Load job requirements
            jr_path = os.path.join(self.models_dir, "job_requirements.json")
            with open(jr_path, 'r') as f:
                self.job_requirements = json.load(f)
            logger.info(f"✓ Loaded job requirements for {len(self.job_requirements)} roles")
            
            # Load scoring configuration
            sc_path = os.path.join(self.models_dir, "interview_scoring_config.json")
            with open(sc_path, 'r') as f:
                self.interview_configs = json.load(f)
            logger.info("✓ Loaded interview scoring configuration")
            
        except Exception as e:
            logger.error(f"✗ Error loading resources: {e}")
            raise
    
    def get_available_jobs(self) -> List[str]:
        """Get list of available job roles"""
        return list(self.job_requirements.keys())
    
    def get_job_skills(self, job_role: str) -> List[str]:
        """Get required skills for a job role"""
        return self.job_requirements.get(job_role, [])
    
    def create_interview_session(self, candidate_id: str, job_role: str, 
                                num_questions: int = 10) -> Dict:
        """
        Create interview session with questions
        
        Args:
            candidate_id: Candidate ID
            job_role: Target job role
            num_questions: Number of questions to generate
            
        Returns:
            Interview session dictionary
        """
        if job_role not in self.job_requirements:
            raise ValueError(f"Invalid job role: {job_role}")
        
        # Get required skills
        required_skills = self.job_requirements[job_role]
        
        # Calculate question distribution
        num_mcq = round(num_questions * 0.30)
        num_desc = round(num_questions * 0.40)
        num_code = round(num_questions * 0.30)
        
        # Select questions by type
        mcq_questions = self._select_questions_by_type(
            "MCQ", num_mcq, required_skills
        )
        desc_questions = self._select_questions_by_type(
            "Descriptive", num_desc, required_skills
        )
        code_questions = self._select_questions_by_type(
            "Coding", num_code, required_skills
        )
        
        # Combine all questions
        all_questions = mcq_questions + desc_questions + code_questions
        
        # Create session
        session_id = f"INT_{datetime.now().strftime('%Y%m%d%H%M%S')}_{candidate_id[:4]}"
        
        session = {
            "session_id": session_id,
            "candidate_id": candidate_id,
            "job_role": job_role,
            "required_skills": required_skills,
            "questions": all_questions,
            "question_count": {
                "mcq": len(mcq_questions),
                "descriptive": len(desc_questions),
                "coding": len(code_questions)
            },
            "total_questions": len(all_questions),
            "created_at": datetime.utcnow().isoformat(),
            "status": "created"
        }
        
        logger.info(f"Created interview session {session_id} for {candidate_id}")
        
        return session
    
    def _select_questions_by_type(self, question_type: str, 
                                  count: int, 
                                  relevant_skills: List[str]) -> List[Dict]:
        """
        Select questions by type with relevance filtering
        
        Args:
            question_type: MCQ, Descriptive, or Coding
            count: Number of questions to select
            relevant_skills: Skills to filter by
            
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
        
        # Filter by relevance to skills
        relevant_questions = []
        for q in typed_questions:
            category = q.get("category", "").lower()
            topic = q.get("topic", "").lower()
            
            is_relevant = any(
                skill.lower() in category or skill.lower() in topic
                for skill in relevant_skills
            )
            
            if is_relevant or not relevant_questions:  # Always include if none found
                relevant_questions.append(q)
        
        # Return top 'count' questions
        return relevant_questions[:count]
    
    def evaluate_interview(self, session_id: str, interview_data: Dict) -> Dict:
        """
        Evaluate completed interview
        
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
        
        # Get weights for this job role
        weights = self.interview_configs.get("interview_weights", {}).get(
            job_role,
            {"mcq": 0.25, "descriptive": 0.35, "coding": 0.40}
        )
        
        # Calculate final interview score
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
            "weights_used": weights,
            "mcq_total": len(mcq_answers),
            "descriptive_total": len(desc_answers),
            "coding_total": len(code_answers),
            "weak_topics": weak_topics[:5],  # Top 5 weak areas
            "created_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Evaluated interview {session_id}: Score={interview_score}, Grade={grade}")
        
        return result
    
    def _evaluate_mcq_answers(self, answers: List[Dict]) -> float:
        """Evaluate MCQ answers"""
        if not answers:
            return 0
        
        correct_count = sum(
            1 for a in answers 
            if a.get("is_correct", False)
        )
        
        score = (correct_count / len(answers)) * 100
        return float(score)
    
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
    
    def _identify_weak_topics(self, mcq_answers: List, 
                             desc_answers: List,
                             code_answers: List,
                             mcq_score: float,
                             desc_score: float,
                             code_score: float) -> List[str]:
        """Identify weak topics based on performance"""
        weak_topics = []
        
        # If MCQ score is low, identify wrong topics
        if mcq_score < 70:
            wrong_mcqs = [
                a.get("topic", "Unknown") for a in mcq_answers
                if not a.get("is_correct", True)
            ]
            weak_topics.extend(wrong_mcqs)
        
        # If descriptive score is low, identify weak areas
        if desc_score < 70:
            weak_desc = [
                a.get("topic", "Unknown") for a in desc_answers
                if a.get("final_score", 100) < 60
            ]
            weak_topics.extend(weak_desc)
        
        # If coding score is low, identify complexity issues
        if code_score < 70:
            weak_topics.extend(["Algorithm Design", "Code Optimization"])
        
        # Remove duplicates and return unique topics
        return list(set(weak_topics))


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
            ml_dir = os.path.join(models_dir, "..", "..", "ml")
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
    
    def evaluate_descriptive(self, reference: str, 
                           candidate: str) -> Dict:
        """Evaluate descriptive answer"""
        if not self.desc_evaluator:
            return {"final_score": 50, "similarity": 0.5}
        
        result = self.desc_evaluator.evaluate_descriptive_answer(reference, candidate)
        return result
    
    def evaluate_coding(self, test_cases_passed: int,
                       total_test_cases: int) -> Dict:
        """Evaluate coding answer"""
        if not self.code_evaluator:
            return {"code_score": (test_cases_passed / total_test_cases * 100) if total_test_cases > 0 else 0}
        
        result = self.code_evaluator.evaluate_coding_answer(
            test_cases_passed, total_test_cases
        )
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
