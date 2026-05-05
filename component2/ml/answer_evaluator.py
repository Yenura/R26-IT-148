"""
Component 2: Interview System - SBERT Semantic Similarity Model
Trains and evaluates semantic similarity for descriptive answers
"""

import pickle
import json
import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path


class DescriptiveAnswerEvaluator:
    """
    Evaluates descriptive answers using SBERT (Sentence-BERT) semantic similarity
    
    Scoring formula:
    Desc_Score(i) = min(100, α × Raw_Desc_Score(i) + β × KeywordBonus(i) × 100)
    where α = 0.7, β = 0.3
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize SBERT model
        
        Args:
            model_name: Pre-trained SBERT model name
        """
        self.model = SentenceTransformer(model_name)
        self.alpha = 0.7  # Weight for semantic similarity
        self.beta = 0.3   # Weight for keyword coverage
        print(f"✓ Loaded SBERT model: {model_name}")
    
    def encode_text(self, text: str) -> np.ndarray:
        """
        Encode text to embedding vector
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector (d-dimensional)
        """
        return self.model.encode(text, convert_to_tensor=False)
    
    def compute_cosine_similarity(self, embedding1: np.ndarray, 
                                 embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Formula: CosineSim = (e1 · e2) / (‖e1‖ · ‖e2‖)
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score in [0, 1]
        """
        # Normalize vectors
        e1_norm = embedding1 / (np.linalg.norm(embedding1) + 1e-8)
        e2_norm = embedding2 / (np.linalg.norm(embedding2) + 1e-8)
        
        # Cosine similarity
        similarity = np.dot(e1_norm, e2_norm)
        
        # Clip to [0, 1] range
        return float(np.clip(similarity, 0, 1))
    
    def extract_keywords(self, text: str) -> set:
        """
        Extract keywords from text (simple approach: split and filter)
        
        Args:
            text: Input text
            
        Returns:
            Set of keywords
        """
        if not isinstance(text, str):
            return set()
        
        # Remove common words and split
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'is', 'are', 'was', 'were',
            'is', 'it', 'to', 'of', 'for', 'in', 'by', 'with', 'from',
            'as', 'be', 'that', 'this', 'which', 'what', 'when', 'where',
            'how', 'why', 'all', 'each', 'both', 'any', 'some', 'such'
        }
        
        words = text.lower().split()
        keywords = {w.strip('.,!?;:') for w in words 
                   if w.lower() not in stop_words and len(w) > 2}
        
        return keywords
    
    def calculate_keyword_bonus(self, reference_text: str, 
                               candidate_text: str) -> float:
        """
        Calculate keyword coverage bonus
        
        Formula: KeywordBonus = |{k ∈ Keywords(ref) : k in candidate}| / |Keywords(ref)|
        
        Args:
            reference_text: Reference answer
            candidate_text: Candidate's answer
            
        Returns:
            Bonus score in [0, 1]
        """
        ref_keywords = self.extract_keywords(reference_text)
        cand_text_lower = candidate_text.lower()
        
        if not ref_keywords:
            return 0.5
        
        matches = sum(1 for kw in ref_keywords if kw in cand_text_lower)
        bonus = matches / len(ref_keywords)
        
        return float(bonus)
    
    def evaluate_descriptive_answer(self, reference_answer: str, 
                                   candidate_answer: str) -> Dict:
        """
        Evaluate a descriptive answer against reference
        
        Args:
            reference_answer: Expected/reference answer
            candidate_answer: Candidate's provided answer
            
        Returns:
            Dictionary with detailed scoring metrics
        """
        # Step 1: Encode both texts
        e_ref = self.encode_text(reference_answer)
        e_candidate = self.encode_text(candidate_answer)
        
        # Step 2: Compute cosine similarity
        cosine_sim = self.compute_cosine_similarity(e_ref, e_candidate)
        raw_score = cosine_sim * 100  # Scale to 0-100
        
        # Step 3: Calculate keyword bonus
        keyword_bonus = self.calculate_keyword_bonus(reference_answer, candidate_answer)
        
        # Step 4: Combine with formula
        final_score = min(100, self.alpha * raw_score + self.beta * keyword_bonus * 100)
        
        return {
            "cosine_similarity": round(cosine_sim, 4),
            "raw_score": round(raw_score, 2),
            "keyword_bonus": round(keyword_bonus, 4),
            "keyword_coverage": f"{int(keyword_bonus * 100)}%",
            "final_score": round(final_score, 2),
            "embedding_dim": len(e_ref),
            "alpha": self.alpha,
            "beta": self.beta
        }
    
    def batch_evaluate(self, reference_answers: List[str], 
                      candidate_answers: List[str]) -> Dict:
        """
        Evaluate multiple descriptive answers
        
        Args:
            reference_answers: List of reference answers
            candidate_answers: List of candidate answers
            
        Returns:
            Dictionary with aggregate metrics
        """
        if len(reference_answers) != len(candidate_answers):
            raise ValueError("Reference and candidate answer lists must have same length")
        
        scores = []
        details = []
        
        for ref, cand in zip(reference_answers, candidate_answers):
            detail = self.evaluate_descriptive_answer(ref, cand)
            scores.append(detail['final_score'])
            details.append(detail)
        
        # Aggregate score
        descriptive_score = float(np.mean(scores)) if scores else 0
        
        return {
            "descriptive_score": round(descriptive_score, 2),
            "average_similarity": round(np.mean([d['cosine_similarity'] for d in details]), 4),
            "min_score": round(np.min(scores), 2) if scores else 0,
            "max_score": round(np.max(scores), 2) if scores else 0,
            "total_questions": len(scores),
            "per_question_details": details
        }
    
    def save_model(self, output_path: str):
        """Save model to disk"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            pickle.dump(self.model, f)
        print(f"✓ Model saved to {output_path}")
    
    def load_model(self, input_path: str):
        """Load model from disk"""
        with open(input_path, 'rb') as f:
            self.model = pickle.load(f)
        print(f"✓ Model loaded from {input_path}")


class MCQEvaluator:
    """
    Evaluates MCQ answers with optional negative marking
    
    Scoring formula:
    Score_MCQ(i) = +1 if correct
                   -p if wrong (p = 0.25)
                   0 if skipped
    
    MCQ_Score = max(0, Σ Score_MCQ(i)) / N_mcq × 100
    """
    
    def __init__(self, penalty_for_wrong: float = 0.25):
        """
        Initialize MCQ evaluator
        
        Args:
            penalty_for_wrong: Penalty multiplier for wrong answers (0-1)
        """
        self.penalty = penalty_for_wrong
    
    def evaluate_single_mcq(self, correct_option: int, 
                           candidate_option: int, 
                           skipped: bool = False) -> float:
        """
        Evaluate a single MCQ answer
        
        Args:
            correct_option: Index of correct option
            candidate_option: Index of candidate's chosen option
            skipped: Whether question was skipped
            
        Returns:
            Score (+1, -penalty, or 0)
        """
        if skipped:
            return 0.0
        
        if candidate_option == correct_option:
            return 1.0
        else:
            return -self.penalty
    
    def evaluate_batch_mcq(self, correct_answers: List[int], 
                          candidate_answers: List[int],
                          skipped_flags: List[bool] = None) -> Dict:
        """
        Evaluate batch of MCQ answers
        
        Args:
            correct_answers: List of correct option indices
            candidate_answers: List of candidate's chosen options
            skipped_flags: List of boolean flags for skipped questions
            
        Returns:
            Dictionary with scoring details
        """
        if len(correct_answers) != len(candidate_answers):
            raise ValueError("Lists must have same length")
        
        if skipped_flags is None:
            skipped_flags = [False] * len(correct_answers)
        
        individual_scores = []
        correct_count = 0
        wrong_count = 0
        skipped_count = 0
        
        for i, (correct, candidate, skipped) in enumerate(
            zip(correct_answers, candidate_answers, skipped_flags)):
            
            score = self.evaluate_single_mcq(correct, candidate, skipped)
            individual_scores.append(score)
            
            if skipped:
                skipped_count += 1
            elif candidate == correct:
                correct_count += 1
            else:
                wrong_count += 1
        
        # Aggregate score
        total_score = max(0, sum(individual_scores))  # No negative aggregate
        mcq_score = (total_score / len(correct_answers) * 100) if correct_answers else 0
        
        return {
            "mcq_score": round(mcq_score, 2),
            "total_questions": len(correct_answers),
            "correct": correct_count,
            "wrong": wrong_count,
            "skipped": skipped_count,
            "accuracy": round(correct_count / len(correct_answers) * 100, 2),
            "penalty_applied": self.penalty,
            "individual_scores": individual_scores
        }


class CodingEvaluator:
    """
    Evaluates coding answers based on test case execution and quality
    
    Scoring formula:
    Code_Score(i) = γ × Score_Code(i) × 100 + (1-γ) × Quality_Score(i) × 100
    where γ = 0.7 (test pass weight)
    """
    
    def __init__(self, test_pass_weight: float = 0.7):
        """
        Initialize coding evaluator
        
        Args:
            test_pass_weight: Weight for test case pass rate (0-1)
        """
        self.test_weight = test_pass_weight
        self.quality_weight = 1 - test_pass_weight
    
    def evaluate_test_cases(self, test_cases_passed: int, 
                           total_test_cases: int) -> float:
        """
        Calculate test case pass rate
        
        Args:
            test_cases_passed: Number of passing test cases
            total_test_cases: Total number of test cases
            
        Returns:
            Pass rate in [0, 1]
        """
        if total_test_cases == 0:
            return 0.0
        
        return float(test_cases_passed) / total_test_cases
    
    def evaluate_code_quality(self, has_syntax_error: bool = False,
                            complexity_order: int = 0,  # 0=optimal, 1=one worse, 2+=two worse
                            code_length: int = 0,
                            comments_ratio: float = 0.0) -> float:
        """
        Calculate code quality score (simple heuristic)
        
        Formula:
        Quality = w1 × SyntaxValid + w2 × ComplexityScore + w3 × ReadabilityScore
        
        Args:
            has_syntax_error: Whether code has syntax errors
            complexity_order: How many orders of complexity worse than expected
            code_length: Number of lines of code
            comments_ratio: Ratio of comment lines to total lines
            
        Returns:
            Quality score in [0, 1]
        """
        w1, w2, w3 = 0.5, 0.3, 0.2
        
        # Syntax validity
        syntax_score = 0.0 if has_syntax_error else 1.0
        
        # Complexity score
        if complexity_order == 0:
            complexity_score = 1.0
        elif complexity_order == 1:
            complexity_score = 0.5
        else:
            complexity_score = 0.0
        
        # Readability score (based on comments ratio, prefer 0.1-0.2)
        if comments_ratio == 0:
            readability_score = 0.5
        elif 0.1 <= comments_ratio <= 0.2:
            readability_score = 1.0
        else:
            readability_score = 0.5
        
        quality = w1 * syntax_score + w2 * complexity_score + w3 * readability_score
        return float(quality)
    
    def evaluate_coding_answer(self, test_cases_passed: int,
                              total_test_cases: int,
                              has_syntax_error: bool = False,
                              complexity_order: int = 0,
                              code_length: int = 0,
                              comments_ratio: float = 0.0) -> Dict:
        """
        Evaluate a coding answer comprehensively
        
        Args:
            test_cases_passed: Number of passing test cases
            total_test_cases: Total test cases
            has_syntax_error: Whether code has syntax errors
            complexity_order: Complexity order difference
            code_length: Lines of code
            comments_ratio: Comment to code ratio
            
        Returns:
            Dictionary with detailed metrics
        """
        # Test case pass rate
        pass_rate = self.evaluate_test_cases(test_cases_passed, total_test_cases)
        test_score = pass_rate * 100
        
        # Quality score
        quality = self.evaluate_code_quality(
            has_syntax_error, complexity_order, code_length, comments_ratio
        )
        quality_score = quality * 100
        
        # Combined score
        code_score = (self.test_weight * test_score + 
                     self.quality_weight * quality_score)
        
        return {
            "code_score": round(code_score, 2),
            "test_pass_rate": round(pass_rate, 4),
            "test_score": round(test_score, 2),
            "tests_passed": test_cases_passed,
            "total_tests": total_test_cases,
            "syntax_valid": not has_syntax_error,
            "complexity_order": complexity_order,
            "code_length": code_length,
            "comments_ratio": round(comments_ratio, 4),
            "quality_score": round(quality_score, 2),
            "test_weight": self.test_weight,
            "quality_weight": self.quality_weight
        }


if __name__ == "__main__":
    print("\n" + "="*70)
    print("Testing Descriptive Answer Evaluator")
    print("="*70)
    
    desc_evaluator = DescriptiveAnswerEvaluator()
    
    reference = "Polymorphism allows objects of different classes to be treated as objects of a common superclass."
    candidate = "Polymorphism lets different objects be treated as the same type using inheritance and method overriding."
    
    result = desc_evaluator.evaluate_descriptive_answer(reference, candidate)
    print(json.dumps(result, indent=2))
    
    print("\n" + "="*70)
    print("Testing MCQ Evaluator")
    print("="*70)
    
    mcq_evaluator = MCQEvaluator()
    
    correct = [0, 1, 2, 3, 0]
    candidate = [0, 1, 0, 3, 1]  # One wrong
    
    result = mcq_evaluator.evaluate_batch_mcq(correct, candidate)
    print(json.dumps(result, indent=2))
    
    print("\n" + "="*70)
    print("Testing Coding Evaluator")
    print("="*70)
    
    code_evaluator = CodingEvaluator()
    
    result = code_evaluator.evaluate_coding_answer(
        test_cases_passed=3,
        total_test_cases=4,
        has_syntax_error=False,
        complexity_order=0,
        code_length=25,
        comments_ratio=0.15
    )
    print(json.dumps(result, indent=2))
