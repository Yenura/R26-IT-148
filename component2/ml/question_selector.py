"""
Component 2: Interview System - Question Generation & Selection
Implements question selection algorithm based on relevance scoring
"""

import json
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from sentence_transformers import SentenceTransformer, util
from collections import defaultdict
import random


class QuestionSelector:
    """
    Selects interview questions based on job role and relevance scoring
    
    Selection formula:
    SelectionScore(q) = α × RelevanceScore(q, role)
                      + β × (1 - RecentlyUsed(q))
                      + γ × DifficultyMatch(q, target)
    where α + β + γ = 1 (default: 0.6, 0.2, 0.2)
    """
    
    def __init__(self, question_bank: List[Dict], 
                 model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize question selector
        
        Args:
            question_bank: List of question dictionaries
            model_name: SBERT model name for relevance scoring
        """
        self.question_bank = question_bank
        self.sbert_model = SentenceTransformer(model_name)
        self.question_usage_count = defaultdict(int)
        self.question_last_used = defaultdict(lambda: None)
        
        # Selection weights
        self.alpha = 0.6    # Relevance weight
        self.beta = 0.2     # Recency weight
        self.gamma = 0.2    # Difficulty match weight
        
        print(f"✓ Question selector initialized with {len(question_bank)} questions")
    
    def encode_job_skills(self, job_role: str, required_skills: List[str]) -> np.ndarray:
        """
        Encode job role and required skills
        
        Args:
            job_role: Job title/role
            required_skills: List of required skills
            
        Returns:
            Combined embedding for job requirements
        """
        text = f"{job_role} requires {' '.join(required_skills)}"
        embedding = self.sbert_model.encode(text, convert_to_tensor=False)
        return embedding
    
    def calculate_relevance_score(self, question: Dict, 
                                 job_role_embedding: np.ndarray) -> float:
        """
        Calculate RelevanceScore using cosine similarity
        
        Formula: RelevanceScore(q, role) = CosineSimilarity(SBERT(q.topic), SBERT(role.skills))
        
        Args:
            question: Question dictionary
            job_role_embedding: Embedding of job role + skills
            
        Returns:
            Relevance score in [0, 1]
        """
        question_text = f"{question.get('category', '')} {question.get('topic', '')}"
        question_embedding = self.sbert_model.encode(question_text, convert_to_tensor=False)
        
        # Normalize and compute cosine similarity
        q_norm = question_embedding / (np.linalg.norm(question_embedding) + 1e-8)
        j_norm = job_role_embedding / (np.linalg.norm(job_role_embedding) + 1e-8)
        
        similarity = float(np.dot(q_norm, j_norm))
        return np.clip(similarity, 0, 1)
    
    def calculate_recency_score(self, question_id: str) -> float:
        """
        Calculate recency score (lower usage = higher score)
        
        Formula: RecencyScore = 1 - RecentlyUsed(q)
        
        Args:
            question_id: Question identifier
            
        Returns:
            Recency score in [0, 1]
        """
        # Simple approach: penalize based on usage count
        usage_count = self.question_usage_count[question_id]
        
        # Normalize: assuming max reasonable reuse is 10
        recency = 1.0 - min(usage_count / 10.0, 1.0)
        
        return float(recency)
    
    def calculate_difficulty_match(self, question_difficulty: str, 
                                  target_difficulty: str) -> float:
        """
        Calculate difficulty match score
        
        Formula: DifficultyMatch = 1 if difficulties match, 0 otherwise
        
        Args:
            question_difficulty: Question's difficulty level
            target_difficulty: Target difficulty for interview
            
        Returns:
            Match score (0 or 1)
        """
        match = 1.0 if question_difficulty == target_difficulty else 0.0
        return match
    
    def calculate_selection_score(self, question: Dict,
                                 job_role_embedding: np.ndarray,
                                 target_difficulty: str) -> float:
        """
        Calculate overall selection score
        
        Formula: SelectionScore(q) = α × RelevanceScore + β × RecencyScore + γ × DifficultyMatch
        
        Args:
            question: Question dictionary
            job_role_embedding: Job role embedding
            target_difficulty: Target difficulty level
            
        Returns:
            Overall selection score in [0, 1]
        """
        relevance = self.calculate_relevance_score(question, job_role_embedding)
        recency = self.calculate_recency_score(question['id'])
        difficulty = self.calculate_difficulty_match(
            question['difficulty'], target_difficulty
        )
        
        score = (self.alpha * relevance + 
                self.beta * recency + 
                self.gamma * difficulty)
        
        return float(score)
    
    def select_questions_by_type(self, job_role: str, 
                               required_skills: List[str],
                               num_total: int = 10) -> Dict[str, List[Dict]]:
        """
        Select questions by type (MCQ, Descriptive, Coding)
        
        Distribution:
        - Easy: 30%
        - Medium: 50%
        - Hard: 20%
        
        Args:
            job_role: Job role
            required_skills: Required skills
            num_total: Total number of questions to select
            
        Returns:
            Dictionary with questions grouped by type and difficulty
        """
        # Default distribution by question type
        num_mcq = round(num_total * 0.30)
        num_desc = round(num_total * 0.40)
        num_code = round(num_total * 0.30)
        
        # Difficulty distribution
        num_easy = round(num_total * 0.30)
        num_medium = round(num_total * 0.50)
        num_hard = round(num_total * 0.20)
        
        # Encode job role and skills
        job_embedding = self.encode_job_skills(job_role, required_skills)
        
        # Group questions by type
        questions_by_type = defaultdict(list)
        for q in self.question_bank:
            qtype = q.get('question_type', 'Descriptive')
            questions_by_type[qtype].append(q)
        
        selected_questions = {
            "MCQ": [],
            "Descriptive": [],
            "Coding": []
        }
        
        # Select MCQ questions
        selected_questions["MCQ"] = self._select_questions_from_type(
            questions_by_type.get("MCQ", []),
            job_embedding,
            num_mcq
        )
        
        # Select Descriptive questions
        selected_questions["Descriptive"] = self._select_questions_from_type(
            questions_by_type.get("Descriptive", []),
            job_embedding,
            num_desc
        )
        
        # Select Coding questions
        selected_questions["Coding"] = self._select_questions_from_type(
            questions_by_type.get("Coding", []),
            job_embedding,
            num_code
        )
        
        return selected_questions
    
    def _select_questions_from_type(self, questions: List[Dict],
                                   job_embedding: np.ndarray,
                                   count: int) -> List[Dict]:
        """
        Select specific number of questions from a type
        
        Args:
            questions: Questions of a specific type
            job_embedding: Job role embedding
            count: Number to select
            
        Returns:
            Selected questions
        """
        if not questions:
            return []
        
        # Score all questions
        scored_questions = []
        for q in questions:
            # Vary difficulty target
            difficulties = ['Easy', 'Medium', 'Hard']
            
            # Get difficulty distribution
            if len(scored_questions) < len(questions) * 0.3:
                target_diff = 'Easy'
            elif len(scored_questions) < len(questions) * 0.8:
                target_diff = 'Medium'
            else:
                target_diff = 'Hard'
            
            score = self.calculate_selection_score(q, job_embedding, target_diff)
            scored_questions.append((q, score))
        
        # Sort by score (descending) and select top
        scored_questions.sort(key=lambda x: x[1], reverse=True)
        selected = [q for q, score in scored_questions[:count]]
        
        # Update usage counts
        for q in selected:
            self.question_usage_count[q['id']] += 1
            self.question_last_used[q['id']] = datetime.now()
        
        return selected
    
    def create_interview_session(self, job_role: str,
                               required_skills: List[str],
                               num_questions: int = 10) -> Dict:
        """
        Create a complete interview session with questions
        
        Args:
            job_role: Target job role
            required_skills: Required skills for the role
            num_questions: Total number of questions
            
        Returns:
            Interview session dictionary
        """
        # Select questions
        questions_by_type = self.select_questions_by_type(
            job_role, required_skills, num_questions
        )
        
        # Create session
        session = {
            "session_id": f"INT_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "job_role": job_role,
            "required_skills": required_skills,
            "created_at": datetime.now().isoformat(),
            "questions": [],
            "question_count": {
                "mcq": len(questions_by_type.get("MCQ", [])),
                "descriptive": len(questions_by_type.get("Descriptive", [])),
                "coding": len(questions_by_type.get("Coding", []))
            }
        }
        
        # Add all questions to session in random order
        all_questions = []
        for qtype, questions in questions_by_type.items():
            for idx, q in enumerate(questions):
                q_copy = q.copy()
                q_copy['sequence'] = len(all_questions) + 1
                q_copy['type_category'] = qtype
                all_questions.append(q_copy)
        
        # Shuffle questions
        random.shuffle(all_questions)
        
        session["questions"] = all_questions
        session["total_questions"] = len(all_questions)
        
        return session


def load_and_prepare_questions(question_bank_path: str) -> List[Dict]:
    """Load question bank from JSON"""
    with open(question_bank_path, 'r') as f:
        return json.load(f)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("Testing Question Selection")
    print("="*70)
    
    # Load question bank
    try:
        question_bank = load_and_prepare_questions(
            "c:/Users/ASUS/OneDrive/Documents/GitHub/R26-IT-148/component2/models/question_bank.json"
        )
        print(f"✓ Loaded {len(question_bank)} questions from bank")
    except:
        print("⚠ Could not load question bank, creating sample")
        question_bank = [
            {
                "id": "Q_001",
                "question_text": "What is polymorphism?",
                "question_type": "Descriptive",
                "difficulty": "Easy",
                "category": "OOP",
                "topic": "Inheritance"
            }
        ]
    
    # Initialize selector
    selector = QuestionSelector(question_bank)
    
    # Create interview
    job_role = "AI Researcher"
    skills = ["Python", "Machine Learning", "TensorFlow"]
    
    session = selector.create_interview_session(job_role, skills, num_questions=6)
    
    print(f"\nInterview Session Created:")
    print(f"  Session ID: {session['session_id']}")
    print(f"  Job Role: {session['job_role']}")
    print(f"  Total Questions: {session['total_questions']}")
    print(f"  MCQ: {session['question_count']['mcq']}")
    print(f"  Descriptive: {session['question_count']['descriptive']}")
    print(f"  Coding: {session['question_count']['coding']}")
    
    print(f"\nFirst 3 Questions:")
    for q in session['questions'][:3]:
        print(f"  {q['sequence']}. [{q['question_type']}] {q['question_text'][:60]}...")
