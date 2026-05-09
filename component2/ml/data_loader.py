"""
Component 2: Interview System - Data Loader & Preprocessor
Loads questions from multiple datasets and creates a unified question bank
"""

import pandas as pd
import numpy as np
import json
import os
from typing import List, Dict, Tuple
from pathlib import Path

class InterviewDataLoader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.questions_bank = []
        self.job_skills_mapping = {
            "AI Researcher": ["TensorFlow", "NLP", "Pytorch", "Deep Learning", "Machine Learning", "Python"],
            "Data Scientist": ["Python", "Machine Learning", "SQL", "Deep Learning", "Statistics", "TensorFlow"],
            "Cybersecurity Analyst": ["Cybersecurity", "Networking", "Linux", "Ethical Hacking"],
            "Software Engineer": ["Java", "SQL", "C++", "React", "Python", "REST APIs"]
        }
        
    def load_java_questions(self) -> List[Dict]:
        """Load Java Q&A from information.csv"""
        file_path = os.path.join(self.data_dir, "DataSet for questions/information.csv")
        
        try:
            df = pd.read_csv(file_path)
            questions = []
            
            for idx, row in df.iterrows():
                q_text = str(row.get("Questions") or "").strip()
                a_text = str(row.get("Answers")  or "").strip()
                lang   = str(row.get("language") or "Java").strip()
                level  = str(row.get(" level ")  or "Easy").strip()

                if not q_text or not a_text or q_text == "nan" or a_text == "nan":
                    continue

                question = {
                    "id": f"Q_JAVA_{idx+1:04d}",
                    "question_text": q_text,
                    "answer_text":   a_text,
                    "language":      lang,
                    "difficulty":    level if level in ("Easy", "Medium", "Hard") else "Easy",
                    "question_type": "Descriptive",
                    "category":      lang,
                    "topic":         lang,
                    "keywords":      self._extract_keywords(q_text)
                }
                questions.append(question)
            
            print(f"[OK] Loaded {len(questions)} Java questions from information.csv")
            return questions
            
        except Exception as e:
            print(f"[WARN] Error loading Java questions: {e}")
            return []

    
    def load_software_questions(self) -> List[Dict]:
        """Load software engineering Q&A from Software Questions.csv"""
        file_path = os.path.join(self.data_dir, "DataSet for questions/Software Questions.csv")
        
        try:
            df = pd.read_csv(file_path)
            questions = []
            
            for idx, row in df.iterrows():
                q_text = str(row.get("Question")  or "").strip()
                a_text = str(row.get("Answer")    or "").strip()
                diff   = str(row.get("Difficulty") or "Medium").strip()
                cat    = str(row.get("Category")   or "General Programming").strip()

                if not q_text or not a_text or q_text == "nan" or a_text == "nan":
                    continue

                question = {
                    "id":            f"Q_SW_{idx+1:04d}",
                    "question_text": q_text,
                    "answer_text":   a_text,
                    "difficulty":    diff if diff in ("Easy", "Medium", "Hard") else "Medium",
                    "question_type": "Descriptive",
                    "category":      cat,
                    "topic":         cat,
                    "keywords":      self._extract_keywords(q_text)
                }
                questions.append(question)
            
            print(f"[OK] Loaded {len(questions)} software engineering questions")
            return questions
            
        except Exception as e:
            print(f"[WARN] Error loading software questions: {e}")
            return []

    
    def create_mcq_questions(self) -> List[Dict]:
        """Create MCQ questions from loaded descriptive questions"""
        mcq_templates = [
            {
                "id": "Q_MCQ_001",
                "question_text": "Which of the following is a key feature of Java?",
                "options": ["Platform independence", "Dynamic typing", "Functional programming only", "No OOP support"],
                "correct_option": 0,
                "difficulty": "Easy",
                "question_type": "MCQ",
                "category": "Java",
                "topic": "Java Features",
                "keywords": ["Platform", "independence", "features"]
            },
            {
                "id": "Q_MCQ_002",
                "question_text": "What is the primary purpose of an abstract class?",
                "options": ["To define a contract that must be implemented", "To prevent instantiation while providing base behavior", "To make all methods private", "To allow multiple inheritance"],
                "correct_option": 1,
                "difficulty": "Medium",
                "question_type": "MCQ",
                "category": "OOP",
                "topic": "Abstract Classes",
                "keywords": ["abstract", "class", "instantiation"]
            },
            {
                "id": "Q_MCQ_003",
                "question_text": "In machine learning, what does overfitting refer to?",
                "options": ["Model performs well on training but poorly on test data", "Model performs poorly on all data", "Using too few features", "Using linear models only"],
                "correct_option": 0,
                "difficulty": "Medium",
                "question_type": "MCQ",
                "category": "Machine Learning",
                "topic": "Model Validation",
                "keywords": ["overfitting", "training", "test"]
            },
            {
                "id": "Q_MCQ_004",
                "question_text": "What is the time complexity of binary search?",
                "options": ["O(n)", "O(log n)", "O(n²)", "O(2^n)"],
                "correct_option": 1,
                "difficulty": "Hard",
                "question_type": "MCQ",
                "category": "Data Structures",
                "topic": "Algorithms",
                "keywords": ["binary search", "complexity", "O(log n)"]
            },
            {
                "id": "Q_MCQ_005",
                "question_text": "Which of the following is NOT a type of NoSQL database?",
                "options": ["Document-based (MongoDB)", "Key-Value (Redis)", "Graph (Neo4j)", "Relational (PostgreSQL)"],
                "correct_option": 3,
                "difficulty": "Easy",
                "question_type": "MCQ",
                "category": "Databases",
                "topic": "NoSQL",
                "keywords": ["NoSQL", "database", "types"]
            },
        ]
        
        print(f"✓ Created {len(mcq_templates)} MCQ questions")
        return mcq_templates
    
    def create_coding_questions(self) -> List[Dict]:
        """Create coding questions with test cases"""
        coding_questions = [
            {
                "id": "Q_CODE_001",
                "question_text": "Write a function that finds the two numbers in an array that add up to a target sum.",
                "difficulty": "Easy",
                "question_type": "Coding",
                "category": "Algorithms",
                "topic": "Array & Hash Table",
                "language": "Python",
                "time_limit": 600,  # seconds
                "test_cases": [
                    {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected_output": [0, 1]},
                    {"input": {"nums": [3, 2, 4], "target": 6}, "expected_output": [1, 2]},
                    {"input": {"nums": [3, 3], "target": 6}, "expected_output": [0, 1]},
                ],
                "expected_complexity": "O(n)",
                "keywords": ["array", "hash", "two pointer"]
            },
            {
                "id": "Q_CODE_002",
                "question_text": "Find the longest substring without repeating characters.",
                "difficulty": "Medium",
                "question_type": "Coding",
                "category": "Strings",
                "topic": "Sliding Window",
                "language": "Python",
                "time_limit": 900,
                "test_cases": [
                    {"input": {"s": "abcabcbb"}, "expected_output": 3},
                    {"input": {"s": "bbbbb"}, "expected_output": 1},
                    {"input": {"s": "pwwkew"}, "expected_output": 3},
                ],
                "expected_complexity": "O(n)",
                "keywords": ["substring", "sliding window", "hash"]
            },
            {
                "id": "Q_CODE_003",
                "question_text": "Implement a function to reverse a linked list.",
                "difficulty": "Medium",
                "question_type": "Coding",
                "category": "Linked Lists",
                "topic": "Linked List Operations",
                "language": "Python",
                "time_limit": 900,
                "test_cases": [
                    {"input": {"head": [1, 2, 3, 4, 5]}, "expected_output": [5, 4, 3, 2, 1]},
                    {"input": {"head": [1, 2]}, "expected_output": [2, 1]},
                    {"input": {"head": [1]}, "expected_output": [1]},
                ],
                "expected_complexity": "O(n)",
                "keywords": ["linked list", "reverse", "pointer"]
            },
        ]
        
        print(f"✓ Created {len(coding_questions)} coding questions")
        return coding_questions
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        if not isinstance(text, str):
            return []
        
        words = text.lower().split()
        keywords = [w for w in words if len(w) > 3]
        return keywords[:5]  # Return top 5 keywords
    
    def load_job_requirements(self) -> Dict[str, List[str]]:
        """Load job requirements from dataset"""
        return self.job_skills_mapping
    
    def create_complete_question_bank(self) -> List[Dict]:
        """Create complete question bank from all sources"""
        all_questions = []
        
        # Load from CSV files
        all_questions.extend(self.load_java_questions())
        all_questions.extend(self.load_software_questions())
        
        # Create MCQ and Coding questions
        all_questions.extend(self.create_mcq_questions())
        all_questions.extend(self.create_coding_questions())
        
        print(f"\n✓ Total questions in bank: {len(all_questions)}")
        
        # Break down by type
        mcq_count = sum(1 for q in all_questions if q.get("question_type") == "MCQ")
        desc_count = sum(1 for q in all_questions if q.get("question_type") == "Descriptive")
        code_count = sum(1 for q in all_questions if q.get("question_type") == "Coding")
        
        print(f"  - MCQ: {mcq_count}")
        print(f"  - Descriptive: {desc_count}")
        print(f"  - Coding: {code_count}\n")
        
        return all_questions
    
    def save_question_bank(self, questions: List[Dict], output_path: str):
        """Save question bank to JSON"""
        with open(output_path, 'w') as f:
            json.dump(questions, f, indent=2)
        print(f"✓ Question bank saved to {output_path}")
    
    def load_question_bank(self, input_path: str) -> List[Dict]:
        """Load question bank from JSON"""
        with open(input_path, 'r') as f:
            return json.load(f)


if __name__ == "__main__":
    # Test the loader
    data_dir = "c:/Users/ASUS/OneDrive/Documents/GitHub/R26-IT-148/Data_set"
    loader = InterviewDataLoader(data_dir)
    
    # Create and save question bank
    question_bank = loader.create_complete_question_bank()
    output_path = "c:/Users/ASUS/OneDrive/Documents/GitHub/R26-IT-148/component2/models/question_bank.json"
    loader.save_question_bank(question_bank, output_path)
    
    print("\n" + "="*60)
    print("Sample questions:")
    print("="*60)
    for q in question_bank[:3]:
        print(f"\nID: {q['id']}")
        print(f"Type: {q['question_type']}")
        print(f"Difficulty: {q['difficulty']}")
        print(f"Question: {q['question_text'][:80]}...")
