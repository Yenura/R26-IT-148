"""
Component 2: Interview System - Data Loader & Preprocessor
Loads questions from multiple datasets and creates a unified question bank
"""

import pandas as pd
import numpy as np
import json
import os
import re
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

    def _dataset_questions_dir(self) -> str:
        """Folder where employer / course CSV question dumps live."""
        return os.path.join(self.data_dir, "DataSet for questions")

    @staticmethod
    def _normalize_df_columns(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.columns = [str(c).strip() for c in df.columns]
        return df

    @staticmethod
    def _safe_str(val) -> str:
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return ""
        return str(val).strip()

    def _file_tag(self, filename: str) -> str:
        stem = Path(filename).stem
        stem = re.sub(r"[^A-Za-z0-9]+", "_", stem).strip("_") or "DATA"
        return stem.upper()[:24]

    def load_java_questions(self) -> List[Dict]:
        """Backward-compatible: loads information-style Q&A (same as dataset folder scan)."""
        path = os.path.join(self._dataset_questions_dir(), "information.csv")
        if not os.path.isfile(path):
            return []
        return self._load_information_style_csv(path, self._file_tag("information.csv"))

    def load_software_questions(self) -> List[Dict]:
        """Load software engineering Q&A from Software Questions.csv if present."""
        file_path = os.path.join(self._dataset_questions_dir(), "Software Questions.csv")
        if not os.path.isfile(file_path):
            return []
        return self._load_software_style_csv(file_path, self._file_tag("Software Questions.csv"))

    def _load_information_style_csv(self, file_path: str, tag: str) -> List[Dict]:
        """Rows with Questions + Answers (+ optional language, level)."""
        try:
            df = self._normalize_df_columns(pd.read_csv(file_path, encoding="latin-1"))
            questions = []
            # tolerate column name variants
            qcol = "Questions" if "Questions" in df.columns else None
            acol = "Answers" if "Answers" in df.columns else None
            if not qcol or not acol:
                print(f"âœ— {file_path}: missing Questions/Answers columns (found: {list(df.columns)})")
                return []

            lang_col = "language" if "language" in df.columns else None
            level_col = None
            for c in df.columns:
                if c.strip().lower() == "level":
                    level_col = c
                    break

            for idx, row in df.iterrows():
                question_text = self._safe_str(row.get(qcol))
                answer_text = self._safe_str(row.get(acol))
                lang = self._safe_str(row.get(lang_col)) if lang_col else "General"
                diff_raw = "Easy"
                if level_col:
                    diff_raw = self._safe_str(row.get(level_col)) or "Easy"

                question = {
                    "id": f"Q_{tag}_{idx+1:05d}",
                    "question_text": question_text,
                    "answer_text": answer_text,
                    "language": lang or "General",
                    "difficulty": diff_raw or "Easy",
                    "question_type": "Descriptive",
                    "category": lang or "General",
                    "topic": lang or "General",
                    "keywords": self._extract_keywords(question_text),
                    "source_file": os.path.basename(file_path),
                }

                if question["question_text"] and question["answer_text"]:
                    questions.append(question)

            print(f"âœ“ Loaded {len(questions)} descriptive Q&A from {os.path.basename(file_path)}")
            return questions
        except Exception as e:
            print(f"âœ— Error loading {file_path}: {e}")
            return []

    def _load_software_style_csv(self, file_path: str, tag: str) -> List[Dict]:
        """Rows with Question + Answer + optional Category, Difficulty."""
        try:
            df = self._normalize_df_columns(pd.read_csv(file_path, encoding="latin-1"))
            if "Question" not in df.columns or "Answer" not in df.columns:
                print(f"âœ— {file_path}: expected Question and Answer columns (found: {list(df.columns)})")
                return []

            questions = []
            for idx, row in df.iterrows():
                qtext = self._safe_str(row.get("Question"))
                atext = self._safe_str(row.get("Answer"))
                cat = self._safe_str(row.get("Category")) or "General Programming"
                diff = self._safe_str(row.get("Difficulty")) or "Medium"
                question = {
                    "id": f"Q_{tag}_{idx+1:05d}",
                    "question_text": qtext,
                    "answer_text": atext,
                    "difficulty": diff,
                    "question_type": "Descriptive",
                    "category": cat,
                    "topic": cat,
                    "keywords": self._extract_keywords(qtext),
                    "source_file": os.path.basename(file_path),
                }
                if question["question_text"] and question["answer_text"]:
                    questions.append(question)

            print(f"âœ“ Loaded {len(questions)} descriptive Q&A from {os.path.basename(file_path)}")
            return questions
        except Exception as e:
            print(f"âœ— Error loading {file_path}: {e}")
            return []

    def _load_generic_qa_csv(self, file_path: str, tag: str) -> List[Dict]:
        """Best-effort: find question/answer-like columns by name."""
        try:
            df = self._normalize_df_columns(pd.read_csv(file_path, encoding="latin-1"))
            cols_lower = {c.lower(): c for c in df.columns}

            def pick(*candidates):
                for cand in candidates:
                    if cand.lower() in cols_lower:
                        return cols_lower[cand.lower()]
                return None

            qcol = pick("question", "questions", "prompt", "stem", "title")
            acol = pick("answer", "answers", "response", "solution", "explanation")
            if not qcol or not acol:
                print(f"âœ— {file_path}: could not infer question/answer columns: {list(df.columns)}")
                return []

            cat_col = pick("category", "topic", "subject", "tag")
            diff_col = pick("difficulty", "level")

            questions = []
            for idx, row in df.iterrows():
                qtext = self._safe_str(row.get(qcol))
                atext = self._safe_str(row.get(acol))
                cat = self._safe_str(row.get(cat_col)) if cat_col else "General"
                diff = self._safe_str(row.get(diff_col)) if diff_col else "Medium"
                question = {
                    "id": f"Q_{tag}_{idx+1:05d}",
                    "question_text": qtext,
                    "answer_text": atext,
                    "difficulty": diff or "Medium",
                    "question_type": "Descriptive",
                    "category": cat or "General",
                    "topic": cat or "General",
                    "keywords": self._extract_keywords(qtext),
                    "source_file": os.path.basename(file_path),
                }
                if question["question_text"] and question["answer_text"]:
                    questions.append(question)

            print(f"âœ“ Loaded {len(questions)} descriptive Q&A (generic schema) from {os.path.basename(file_path)}")
            return questions
        except Exception as e:
            print(f"âœ— Error loading {file_path}: {e}")
            return []

    def load_all_dataset_folder_csvs(self) -> List[Dict]:
        """
        Load every *.csv under Data_set/.../DataSet for questions into descriptive questions.
        Known schemas: information.csv (Questions/Answers), Software Questions.csv (Question/Answer).
        Other CSVs: generic question/answer column detection.
        """
        folder = self._dataset_questions_dir()
        if not os.path.isdir(folder):
            print(f"âœ— Dataset folder not found: {folder}")
            return []

        paths = sorted(
            p for p in Path(folder).glob("*.csv") if p.is_file()
        )
        if not paths:
            print(f"âœ— No CSV files found in {folder}")
            return []

        # Skip non-QA CSVs (e.g., leetcode_dataset which has different schema)
        skip_files = {"leetcode_dataset - lc.csv"}
        paths = [p for p in paths if p.name not in skip_files]

        combined: List[Dict] = []
        for p in paths:
            name = p.name
            tag = self._file_tag(name)
            try:
                df_head = self._normalize_df_columns(pd.read_csv(p, nrows=0, encoding="latin-1"))
            except Exception as e:
                print(f"[WARN] Skipping {p.name}: {e}")
                continue
            cols = set(df_head.columns)

            if "Questions" in cols and "Answers" in cols:
                combined.extend(self._load_information_style_csv(str(p), tag))
            elif "Question" in cols and "Answer" in cols:
                combined.extend(self._load_software_style_csv(str(p), tag))
            else:
                combined.extend(self._load_generic_qa_csv(str(p), tag))

        print(f"âœ“ Dataset folder total descriptive rows loaded: {len(combined)}")
        return combined
    
    def create_mcq_questions(self) -> List[Dict]:
        """Create MCQ questions from loaded descriptive questions"""
        mcq_templates = [
            {"id": "Q_MCQ_001", "question_text": "Which of the following is a key feature of Java?", "options": [{"index": 0, "text": "Platform independence"}, {"index": 1, "text": "Dynamic typing"}, {"index": 2, "text": "Functional programming only"}, {"index": 3, "text": "No OOP support"}], "correct_option": 0, "difficulty": "Easy", "question_type": "MCQ", "category": "Java", "topic": "Java Features", "keywords": ["java", "platform", "features"]},
            {"id": "Q_MCQ_002", "question_text": "What is the primary purpose of an abstract class?", "options": [{"index": 0, "text": "To define a contract that must be implemented"}, {"index": 1, "text": "To prevent instantiation while providing base behavior"}, {"index": 2, "text": "To make all methods private"}, {"index": 3, "text": "To allow multiple inheritance"}], "correct_option": 1, "difficulty": "Medium", "question_type": "MCQ", "category": "OOP", "topic": "Abstract Classes", "keywords": ["abstract", "class", "oop"]},
            {"id": "Q_MCQ_003", "question_text": "In machine learning, what does overfitting refer to?", "options": [{"index": 0, "text": "Model performs well on training but poorly on test data"}, {"index": 1, "text": "Model performs poorly on all data"}, {"index": 2, "text": "Using too few features"}, {"index": 3, "text": "Using linear models only"}], "correct_option": 0, "difficulty": "Medium", "question_type": "MCQ", "category": "Machine Learning", "topic": "Model Validation", "keywords": ["overfitting", "training", "ml"]},
            {"id": "Q_MCQ_004", "question_text": "What is the time complexity of binary search?", "options": [{"index": 0, "text": "O(n)"}, {"index": 1, "text": "O(log n)"}, {"index": 2, "text": "O(n^2)"}, {"index": 3, "text": "O(2^n)"}], "correct_option": 1, "difficulty": "Hard", "question_type": "MCQ", "category": "Data Structures", "topic": "Algorithms", "keywords": ["binary search", "complexity", "log"]},
            {"id": "Q_MCQ_005", "question_text": "Which of the following is NOT a type of NoSQL database?", "options": [{"index": 0, "text": "Document-based (MongoDB)"}, {"index": 1, "text": "Key-Value (Redis)"}, {"index": 2, "text": "Graph (Neo4j)"}, {"index": 3, "text": "Relational (PostgreSQL)"}], "correct_option": 3, "difficulty": "Easy", "question_type": "MCQ", "category": "Databases", "topic": "NoSQL", "keywords": ["nosql", "database", "mongodb"]},
            {"id": "Q_MCQ_006", "question_text": "What does CSS stand for?", "options": [{"index": 0, "text": "Cascading Style Sheets"}, {"index": 1, "text": "Computer Style Sheets"}, {"index": 2, "text": "Creative Style System"}, {"index": 3, "text": "Colorful Style Sheets"}], "correct_option": 0, "difficulty": "Easy", "question_type": "MCQ", "category": "Web Development", "topic": "CSS", "keywords": ["css", "style", "web"]},
            {"id": "Q_MCQ_007", "question_text": "Which data structure uses FIFO ordering?", "options": [{"index": 0, "text": "Stack"}, {"index": 1, "text": "Queue"}, {"index": 2, "text": "Tree"}, {"index": 3, "text": "Graph"}], "correct_option": 1, "difficulty": "Easy", "question_type": "MCQ", "category": "Data Structures", "topic": "Queue", "keywords": ["fifo", "queue", "data structure"]},
            {"id": "Q_MCQ_008", "question_text": "What is the purpose of a database index?", "options": [{"index": 0, "text": "To encrypt data"}, {"index": 1, "text": "To speed up query lookups"}, {"index": 2, "text": "To store backup data"}, {"index": 3, "text": "To enforce constraints"}], "correct_option": 1, "difficulty": "Easy", "question_type": "MCQ", "category": "Databases", "topic": "Indexing", "keywords": ["index", "database", "query"]},
            {"id": "Q_MCQ_009", "question_text": "In Python, which keyword is used to define a function?", "options": [{"index": 0, "text": "function"}, {"index": 1, "text": "def"}, {"index": 2, "text": "func"}, {"index": 3, "text": "define"}], "correct_option": 1, "difficulty": "Easy", "question_type": "MCQ", "category": "Python", "topic": "Functions", "keywords": ["python", "function", "def"]},
            {"id": "Q_MCQ_010", "question_text": "What is the time complexity of accessing an element in an array by index?", "options": [{"index": 0, "text": "O(n)"}, {"index": 1, "text": "O(log n)"}, {"index": 2, "text": "O(1)"}, {"index": 3, "text": "O(n^2)"}], "correct_option": 2, "difficulty": "Easy", "question_type": "MCQ", "category": "Data Structures", "topic": "Arrays", "keywords": ["array", "access", "complexity"]},
            {"id": "Q_MCQ_011", "question_text": "What is a closure in programming?", "options": [{"index": 0, "text": "A function with access to its outer scope variables"}, {"index": 1, "text": "A way to close a program"}, {"index": 2, "text": "A type of loop"}, {"index": 3, "text": "A method to end a thread"}], "correct_option": 0, "difficulty": "Medium", "question_type": "MCQ", "category": "Programming Concepts", "topic": "Closures", "keywords": ["closure", "scope", "function"]},
            {"id": "Q_MCQ_012", "question_text": "Which HTTP status code indicates a successful response?", "options": [{"index": 0, "text": "404"}, {"index": 1, "text": "500"}, {"index": 2, "text": "200"}, {"index": 3, "text": "301"}], "correct_option": 2, "difficulty": "Easy", "question_type": "MCQ", "category": "Web Development", "topic": "HTTP", "keywords": ["http", "status", "200"]},
            {"id": "Q_MCQ_013", "question_text": "What is the main advantage of using version control?", "options": [{"index": 0, "text": "Faster code execution"}, {"index": 1, "text": "Tracking changes and collaboration"}, {"index": 2, "text": "Reduced memory usage"}, {"index": 3, "text": "Automatic bug fixing"}], "correct_option": 1, "difficulty": "Easy", "question_type": "MCQ", "category": "Software Engineering", "topic": "Version Control", "keywords": ["git", "version", "control"]},
            {"id": "Q_MCQ_014", "question_text": "In OOP, what is polymorphism?", "options": [{"index": 0, "text": "Using multiple classes"}, {"index": 1, "text": "Objects of different classes treated through common interface"}, {"index": 2, "text": "Creating multiple instances"}, {"index": 3, "text": "Having many variables"}], "correct_option": 1, "difficulty": "Medium", "question_type": "MCQ", "category": "OOP", "topic": "Polymorphism", "keywords": ["polymorphism", "oop", "interface"]},
            {"id": "Q_MCQ_015", "question_text": "What is the purpose of a REST API?", "options": [{"index": 0, "text": "To run machine learning models"}, {"index": 1, "text": "To provide a standardized way for systems to communicate"}, {"index": 2, "text": "To store data permanently"}, {"index": 3, "text": "To compile source code"}], "correct_option": 1, "difficulty": "Medium", "question_type": "MCQ", "category": "Web Development", "topic": "REST API", "keywords": ["rest", "api", "communication"]},
            {"id": "Q_MCQ_016", "question_text": "What is the difference between a stack and a queue?", "options": [{"index": 0, "text": "Stack is FIFO, Queue is LIFO"}, {"index": 1, "text": "Stack is LIFO, Queue is FIFO"}, {"index": 2, "text": "Both are FIFO"}, {"index": 3, "text": "Both are LIFO"}], "correct_option": 1, "difficulty": "Easy", "question_type": "MCQ", "category": "Data Structures", "topic": "Stack vs Queue", "keywords": ["stack", "queue", "lifo", "fifo"]},
            {"id": "Q_MCQ_017", "question_text": "What is dependency injection?", "options": [{"index": 0, "text": "A design pattern where objects receive dependencies from external sources"}, {"index": 1, "text": "A way to inject bugs into code"}, {"index": 2, "text": "A testing methodology"}, {"index": 3, "text": "A type of database query"}], "correct_option": 0, "difficulty": "Medium", "question_type": "MCQ", "category": "Software Engineering", "topic": "Design Patterns", "keywords": ["dependency", "injection", "design"]},
            {"id": "Q_MCQ_018", "question_text": "What is the purpose of Docker?", "options": [{"index": 0, "text": "To manage databases"}, {"index": 1, "text": "To package applications in containers"}, {"index": 2, "text": "To write HTML"}, {"index": 3, "text": "To compile Java"}], "correct_option": 1, "difficulty": "Easy", "question_type": "MCQ", "category": "DevOps", "topic": "Containers", "keywords": ["docker", "container", "devops"]},
            {"id": "Q_MCQ_019", "question_text": "What is a primary key in a database?", "options": [{"index": 0, "text": "A key used for encryption"}, {"index": 1, "text": "A unique identifier for each record"}, {"index": 2, "text": "A password for login"}, {"index": 3, "text": "A foreign reference"}], "correct_option": 1, "difficulty": "Easy", "question_type": "MCQ", "category": "Databases", "topic": "SQL", "keywords": ["primary key", "database", "sql"]},
            {"id": "Q_MCQ_020", "question_text": "What is Big O notation used for?", "options": [{"index": 0, "text": "Describing code syntax"}, {"index": 1, "text": "Describing algorithm complexity"}, {"index": 2, "text": "Naming variables"}, {"index": 3, "text": "Formatting output"}], "correct_option": 1, "difficulty": "Medium", "question_type": "MCQ", "category": "Algorithms", "topic": "Complexity", "keywords": ["big o", "complexity", "algorithm"]},
            {"id": "Q_MCQ_021", "question_text": "What is the difference between HTTP and HTTPS?", "options": [{"index": 0, "text": "HTTP is faster"}, {"index": 1, "text": "HTTPS uses SSL/TLS encryption"}, {"index": 2, "text": "HTTPS is deprecated"}, {"index": 3, "text": "They are identical"}], "correct_option": 1, "difficulty": "Easy", "question_type": "MCQ", "category": "Web Development", "topic": "Security", "keywords": ["http", "https", "ssl"]},
            {"id": "Q_MCQ_022", "question_text": "What is a linked list?", "options": [{"index": 0, "text": "An array with links"}, {"index": 1, "text": "A sequence of nodes where each points to the next"}, {"index": 2, "text": "A type of tree"}, {"index": 3, "text": "A hash table"}], "correct_option": 1, "difficulty": "Easy", "question_type": "MCQ", "category": "Data Structures", "topic": "Linked Lists", "keywords": ["linked list", "node", "pointer"]},
            {"id": "Q_MCQ_023", "question_text": "What is the purpose of a load balancer?", "options": [{"index": 0, "text": "To encrypt traffic"}, {"index": 1, "text": "To distribute incoming requests across servers"}, {"index": 2, "text": "To store data"}, {"index": 3, "text": "To compile code"}], "correct_option": 1, "difficulty": "Medium", "question_type": "MCQ", "category": "DevOps", "topic": "Infrastructure", "keywords": ["load balancer", "server", "traffic"]},
            {"id": "Q_MCQ_024", "question_text": "What is recursion?", "options": [{"index": 0, "text": "A loop that runs forever"}, {"index": 1, "text": "A function that calls itself"}, {"index": 2, "text": "A type of variable"}, {"index": 3, "text": "A debugging technique"}], "correct_option": 1, "difficulty": "Easy", "question_type": "MCQ", "category": "Algorithms", "topic": "Recursion", "keywords": ["recursion", "function", "self"]},
            {"id": "Q_MCQ_025", "question_text": "What is the purpose of garbage collection?", "options": [{"index": 0, "text": "To delete files"}, {"index": 1, "text": "To automatically free unused memory"}, {"index": 2, "text": "To clean the screen"}, {"index": 3, "text": "To remove comments"}], "correct_option": 1, "difficulty": "Medium", "question_type": "MCQ", "category": "Programming Concepts", "topic": "Memory Management", "keywords": ["garbage", "memory", "collection"]},
            {"id": "Q_MCQ_026", "question_text": "What is a hash table?", "options": [{"index": 0, "text": "A sorted array"}, {"index": 1, "text": "A data structure mapping keys to values using hash function"}, {"index": 2, "text": "A type of linked list"}, {"index": 3, "text": "A tree structure"}], "correct_option": 1, "difficulty": "Medium", "question_type": "MCQ", "category": "Data Structures", "topic": "Hash Tables", "keywords": ["hash", "table", "key"]},
            {"id": "Q_MCQ_027", "question_text": "What is the difference between SQL and NoSQL?", "options": [{"index": 0, "text": "SQL is faster"}, {"index": 1, "text": "SQL is relational, NoSQL is non-relational"}, {"index": 2, "text": "NoSQL is older"}, {"index": 3, "text": "They are the same"}], "correct_option": 1, "difficulty": "Medium", "question_type": "MCQ", "category": "Databases", "topic": "SQL vs NoSQL", "keywords": ["sql", "nosql", "relational"]},
            {"id": "Q_MCQ_028", "question_text": "What is a microservices architecture?", "options": [{"index": 0, "text": "A single large application"}, {"index": 1, "text": "An app built as a collection of small, independent services"}, {"index": 2, "text": "A type of database"}, {"index": 3, "text": "A programming language"}], "correct_option": 1, "difficulty": "Medium", "question_type": "MCQ", "category": "Software Engineering", "topic": "Architecture", "keywords": ["microservices", "architecture", "service"]},
            {"id": "Q_MCQ_029", "question_text": "What is the purpose of CI/CD?", "options": [{"index": 0, "text": "Code Integration / Continuous Deployment"}, {"index": 1, "text": "Computer Intelligence / Central Database"}, {"index": 2, "text": "Creative Interface / Color Design"}, {"index": 3, "text": "None of the above"}], "correct_option": 0, "difficulty": "Medium", "question_type": "MCQ", "category": "DevOps", "topic": "CI/CD", "keywords": ["ci", "cd", "deployment"]},
            {"id": "Q_MCQ_030", "question_text": "What is the difference between TCP and UDP?", "options": [{"index": 0, "text": "TCP is faster, UDP is reliable"}, {"index": 1, "text": "TCP is reliable, UDP is faster"}, {"index": 2, "text": "Both are unreliable"}, {"index": 3, "text": "Both are slow"}], "correct_option": 1, "difficulty": "Medium", "question_type": "MCQ", "category": "Networking", "topic": "Protocols", "keywords": ["tcp", "udp", "protocol"]},
        ]
        print(f"[OK] Created {len(mcq_templates)} MCQ questions")
        return mcq_templates

    def create_coding_questions(self) -> List[Dict]:
        """Create coding questions with test cases"""
        coding_questions = [
            {"id": "Q_CODE_001", "question_text": "Write a function that finds the two numbers in an array that add up to a target sum.", "difficulty": "Easy", "question_type": "Coding", "category": "Algorithms", "topic": "Array", "language": "Python", "time_limit": 600, "test_cases": [{"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected_output": [0, 1]}, {"input": {"nums": [3, 2, 4], "target": 6}, "expected_output": [1, 2]}], "expected_complexity": "O(n)", "keywords": ["array", "hash", "two sum"]},
            {"id": "Q_CODE_002", "question_text": "Find the longest substring without repeating characters.", "difficulty": "Medium", "question_type": "Coding", "category": "Strings", "topic": "Sliding Window", "language": "Python", "time_limit": 900, "test_cases": [{"input": {"s": "abcabcbb"}, "expected_output": 3}, {"input": {"s": "bbbbb"}, "expected_output": 1}], "expected_complexity": "O(n)", "keywords": ["substring", "sliding window"]},
            {"id": "Q_CODE_003", "question_text": "Implement a function to reverse a linked list.", "difficulty": "Medium", "question_type": "Coding", "category": "Linked Lists", "topic": "Linked List", "language": "Python", "time_limit": 900, "test_cases": [{"input": {"head": [1, 2, 3, 4, 5]}, "expected_output": [5, 4, 3, 2, 1]}, {"input": {"head": [1, 2]}, "expected_output": [2, 1]}], "expected_complexity": "O(n)", "keywords": ["linked list", "reverse"]},
            {"id": "Q_CODE_004", "question_text": "Write a function to check if a string is a palindrome.", "difficulty": "Easy", "question_type": "Coding", "category": "Strings", "topic": "String Manipulation", "language": "Python", "time_limit": 600, "test_cases": [{"input": {"s": "racecar"}, "expected_output": True}, {"input": {"s": "hello"}, "expected_output": False}], "expected_complexity": "O(n)", "keywords": ["palindrome", "string"]},
            {"id": "Q_CODE_005", "question_text": "Implement binary search on a sorted array.", "difficulty": "Medium", "question_type": "Coding", "category": "Algorithms", "topic": "Search", "language": "Python", "time_limit": 600, "test_cases": [{"input": {"arr": [1, 2, 3, 4, 5], "target": 3}, "expected_output": 2}, {"input": {"arr": [1, 2, 3, 4, 5], "target": 6}, "expected_output": -1}], "expected_complexity": "O(log n)", "keywords": ["binary search", "sorted"]},
            {"id": "Q_CODE_006", "question_text": "Write a function to flatten a nested list.", "difficulty": "Medium", "question_type": "Coding", "category": "Data Structures", "topic": "Recursion", "language": "Python", "time_limit": 600, "test_cases": [{"input": {"nested": [1, [2, 3], [4, [5]]]}, "expected_output": [1, 2, 3, 4, 5]}], "expected_complexity": "O(n)", "keywords": ["flatten", "nested", "recursion"]},
            {"id": "Q_CODE_007", "question_text": "Implement a stack with push, pop, and getMin operations.", "difficulty": "Hard", "question_type": "Coding", "category": "Data Structures", "topic": "Stack", "language": "Python", "time_limit": 900, "test_cases": [{"input": {"operations": ["push", "push", "getMin", "pop", "getMin"], "values": [5, 3, None, None, None]}, "expected_output": [None, None, 3, 3, 5]}], "expected_complexity": "O(1)", "keywords": ["stack", "min", "push", "pop"]},
            {"id": "Q_CODE_008", "question_text": "Write a function to find the maximum subarray sum (Kadane's algorithm).", "difficulty": "Medium", "question_type": "Coding", "category": "Algorithms", "topic": "Dynamic Programming", "language": "Python", "time_limit": 900, "test_cases": [{"input": {"nums": [-2, 1, -3, 4, -1, 2, 1, -5, 4]}, "expected_output": 6}, {"input": {"nums": [1]}, "expected_output": 1}], "expected_complexity": "O(n)", "keywords": ["kadane", "subarray", "dynamic programming"]},
            {"id": "Q_CODE_009", "question_text": "Implement a queue using two stacks.", "difficulty": "Hard", "question_type": "Coding", "category": "Data Structures", "topic": "Queue", "language": "Python", "time_limit": 900, "test_cases": [{"input": {"operations": ["push", "push", "peek", "pop"], "values": [1, 2, None, None]}, "expected_output": [None, None, 1, 1]}], "expected_complexity": "O(1) amortized", "keywords": ["queue", "stack", "implementation"]},
            {"id": "Q_CODE_010", "question_text": "Write a function to count the frequency of elements in an array.", "difficulty": "Easy", "question_type": "Coding", "category": "Data Structures", "topic": "Hash Map", "language": "Python", "time_limit": 600, "test_cases": [{"input": {"arr": [1, 2, 2, 3, 3, 3]}, "expected_output": {1: 1, 2: 2, 3: 3}}], "expected_complexity": "O(n)", "keywords": ["frequency", "hash map", "count"]},
            {"id": "Q_CODE_011", "question_text": "Write a function to detect a cycle in a linked list.", "difficulty": "Medium", "question_type": "Coding", "category": "Linked Lists", "topic": "Two Pointers", "language": "Python", "time_limit": 600, "test_cases": [{"input": {"head": [3, 2, 0, -4], "pos": 1}, "expected_output": True}, {"input": {"head": [1, 2], "pos": -1}, "expected_output": False}], "expected_complexity": "O(n)", "keywords": ["cycle", "linked list", "floyd"]},
            {"id": "Q_CODE_012", "question_text": "Implement a function to merge two sorted arrays.", "difficulty": "Easy", "question_type": "Coding", "category": "Arrays", "topic": "Merge", "language": "Python", "time_limit": 600, "test_cases": [{"input": {"arr1": [1, 3, 5], "arr2": [2, 4, 6]}, "expected_output": [1, 2, 3, 4, 5, 6]}], "expected_complexity": "O(n+m)", "keywords": ["merge", "sorted", "array"]},
            {"id": "Q_CODE_013", "question_text": "Write a function to find the depth of a binary tree.", "difficulty": "Medium", "question_type": "Coding", "category": "Trees", "topic": "Binary Tree", "language": "Python", "time_limit": 600, "test_cases": [{"input": {"root": [3, 9, 20, None, None, 15, 7]}, "expected_output": 3}], "expected_complexity": "O(n)", "keywords": ["depth", "binary tree", "recursion"]},
            {"id": "Q_CODE_014", "question_text": "Write a SQL query to find the second highest salary.", "difficulty": "Medium", "question_type": "Coding", "category": "SQL", "topic": "Queries", "language": "SQL", "time_limit": 600, "test_cases": [{"input": {"table": "employees"}, "expected_output": "select"}], "expected_complexity": "O(n)", "keywords": ["sql", "salary", "second"]},
            {"id": "Q_CODE_015", "question_text": "Write a function to generate all permutations of a string.", "difficulty": "Hard", "question_type": "Coding", "category": "Algorithms", "topic": "Backtracking", "language": "Python", "time_limit": 900, "test_cases": [{"input": {"s": "abc"}, "expected_output": ["abc", "acb", "bac", "bca", "cab", "cba"]}], "expected_complexity": "O(n*n!)", "keywords": ["permutation", "backtracking"]},
        ]
        print(f"âœ“ Created {len(coding_questions)} coding questions")
        return coding_questions
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        if not isinstance(text, str):
            return []
        
        words = text.lower().split()
        keywords = [w for w in words if len(w) > 3]
        return keywords[:5]  # Return top 5 keywords
    
    def load_leetcode_dataset(self) -> List[Dict]:
        """Load LeetCode problems and convert to QG coding format."""
        leetcode_path = os.path.join(
            self._dataset_questions_dir(), "leetcode_dataset - lc.csv"
        )
        if not os.path.isfile(leetcode_path):
            print(f"âœ— LeetCode dataset not found: {leetcode_path}")
            return []

        try:
            df = self._normalize_df_columns(pd.read_csv(leetcode_path, encoding="latin-1"))
            questions = []
            for idx, row in df.iterrows():
                title = self._safe_str(row.get("title"))
                desc = self._safe_str(row.get("description"))
                difficulty_raw = self._safe_str(row.get("difficulty", "Medium"))
                topics = self._safe_str(row.get("related_topics", ""))

                if not title or not desc:
                    continue

                difficulty = difficulty_raw if difficulty_raw in ("Easy", "Medium", "Hard") else "Medium"
                skill_list = [t.strip() for t in topics.split(",") if t.strip()] or ["Algorithms"]
                skill_str = ", ".join(skill_list[:4])

                # Extract examples from description
                examples = self._extract_leetcode_examples(desc)

                question = {
                    "id": f"LC_{idx+1:05d}",
                    "question_text": f"{title}. {desc[:500]}",
                    "question_type": "Coding",
                    "difficulty": difficulty,
                    "category": skill_list[0] if skill_list else "Algorithms",
                    "topic": skill_str,
                    "language": "Python",
                    "time_limit": 900,
                    "test_cases": examples,
                    "expected_complexity": "O(n)",
                    "keywords": [s.lower() for s in skill_list[:5]],
                    "source_file": "leetcode_dataset.csv",
                }
                questions.append(question)

            print(f"âœ“ Loaded {len(questions)} coding questions from LeetCode dataset")
            return questions
        except Exception as e:
            print(f"âœ— Error loading LeetCode dataset: {e}")
            return []

    @staticmethod
    def _extract_leetcode_examples(description: str) -> List[Dict]:
        """Extract input/output examples from LeetCode problem description."""
        import re
        examples = []
        pattern = r"Example\s+\d+:\s*\n?\s*Input:\s*(.+?)\n?\s*Output:\s*(.+?)(?:\n|$)"
        matches = re.findall(pattern, description, re.DOTALL)
        for inp, out in matches[:3]:
            inp = inp.strip().rstrip(".")
            out = out.strip().rstrip(".")
            examples.append({"input": {"raw": inp}, "expected_output": out})
        if not examples:
            examples = [{"input": {}, "expected_output": "See description"}]
        return examples

    def load_job_requirements(self) -> Dict[str, List[str]]:
        """Load job requirements from dataset"""
        return self.job_skills_mapping
    
    def create_complete_question_bank(self) -> List[Dict]:
        """Create complete question bank from all sources"""
        all_questions = []
        
        # All CSVs under Data_set/.../DataSet for questions (information.csv, Software Questions.csv, etc.)
        all_questions.extend(self.load_all_dataset_folder_csvs())
        
        # Create MCQ and Coding questions
        all_questions.extend(self.create_mcq_questions())
        all_questions.extend(self.create_coding_questions())
        
        print(f"\nâœ“ Total questions in bank: {len(all_questions)}")
        
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
        print(f"âœ“ Question bank saved to {output_path}")
    
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

