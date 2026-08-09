"""Add reference answers and test cases to question bank."""
import json
import re
from pathlib import Path

BANK_PATH = Path(__file__).parent.parent / "models" / "question_bank.json"

# Reference answers for common descriptive topics
DESC_ANSWERS = {
    "clean code principles": "Clean code principles include meaningful naming, small focused functions, DRY (Don't Repeat Yourself), SOLID principles, proper error handling, and clear documentation. Code should be readable and maintainable.",
    "version control": "Version control systems like Git track changes to code over time, enable collaboration through branching and merging, provide history of changes, and support rollback to previous states.",
    "software architecture": "Software architecture defines the high-level structure of a system, including components, their relationships, and principles guiding design. Key patterns include MVC, microservices, event-driven, and layered architecture.",
    "data structures": "Data structures are ways of organizing and storing data for efficient access. Common types include arrays, linked lists, stacks, queues, trees, hash tables, and graphs. Choice depends on operation requirements.",
    "algorithms": "Algorithms are step-by-step procedures for solving problems. Key categories include sorting (quicksort, mergesort), searching (binary search), graph algorithms (BFS, DFS), and dynamic programming.",
    "design patterns": "Design patterns are reusable solutions to common software design problems. Creational patterns include Singleton and Factory. Structural patterns include Adapter and Decorator. Behavioral patterns include Observer and Strategy.",
    "testing": "Software testing verifies that code works as expected. Types include unit testing (individual functions), integration testing (component interaction), and end-to-end testing (full user workflows). Test-driven development writes tests before code.",
    "api design": "API design involves creating interfaces for software components. RESTful APIs use HTTP methods (GET, POST, PUT, DELETE) with resource-based URLs. Good APIs are consistent, well-documented, and handle errors gracefully.",
    "database design": "Database design involves organizing data efficiently. Key concepts include normalization (reducing redundancy), indexing (speeding queries), relationships (one-to-one, one-to-many, many-to-many), and ACID properties.",
    "security": "Software security involves protecting systems from threats. Key practices include input validation, authentication, authorization, encryption, secure communication (HTTPS), and regular security audits.",
    "performance optimization": "Performance optimization improves system speed and efficiency. Techniques include caching, lazy loading, database query optimization, code profiling, and minimizing network requests.",
    "agile methodology": "Agile is an iterative approach to software development. Key practices include sprints (time-boxed iterations), daily standups, retrospectives, continuous integration, and responding to change over following a plan.",
    "devops": "DevOps combines development and operations practices. Key concepts include continuous integration/continuous deployment (CI/CD), infrastructure as code, monitoring, and collaboration between teams.",
    "machine learning": "Machine learning enables systems to learn from data. Supervised learning uses labeled data, unsupervised learning finds patterns in unlabeled data, and reinforcement learning learns through trial and error.",
    "cloud computing": "Cloud computing provides on-demand computing resources. Key services include IaaS (infrastructure), PaaS (platform), and SaaS (software). Major providers are AWS, Azure, and Google Cloud.",
}

# Test cases for common coding topics
CODING_TESTS = {
    "reverse string": [{"input": {"s": "hello"}, "expected_output": "olleh"}],
    "fibonacci": [{"input": {"n": 5}, "expected_output": "5"}],
    "factorial": [{"input": {"n": 5}, "expected_output": "120"}],
    "palindrome": [{"input": {"s": "racecar"}, "expected_output": "True"}],
    "binary search": [{"input": {"arr": "[1,2,3,4,5]", "target": "3"}, "expected_output": "2"}],
    "merge sort": [{"input": {"arr": "[3,1,4,1,5]"}, "expected_output": "[1,1,3,4,5]"}],
    "linked list": [{"input": {"values": "[1,2,3]"}, "expected_output": "3"}],
    "tree traversal": [{"input": {"values": "[1,2,3]"}, "expected_output": "1 2 3"}],
    "hash table": [{"input": {"key": "name", "value": "Alice"}, "expected_output": "Alice"}],
    "stack": [{"input": {"operations": "push,push,pop"}, "expected_output": "1"}],
    "queue": [{"input": {"operations": "enqueue,enqueue,dequeue"}, "expected_output": "1"}],
    "graph": [{"input": {"edges": "0-1,1-2"}, "expected_output": "3"}],
    "dynamic programming": [{"input": {"n": "10"}, "expected_output": "55"}],
    "recursion": [{"input": {"n": "5"}, "expected_output": "120"}],
    "sorting": [{"input": {"arr": "[5,3,1,4,2]"}, "expected_output": "[1,2,3,4,5]"}],
}

def find_reference_answer(question_text, topic):
    """Find a reference answer based on question text and topic."""
    text_lower = question_text.lower()
    topic_lower = topic.lower() if topic else ""
    
    # Try exact topic match first
    for key, answer in DESC_ANSWERS.items():
        if key in topic_lower or key in text_lower:
            return answer
    
    # Generic fallback
    return f"This question covers {topic or 'software engineering'} concepts. A good answer should demonstrate understanding of the key principles, provide examples, and explain trade-offs."

def find_test_cases(question_text, topic):
    """Find test cases based on question text and topic."""
    text_lower = question_text.lower()
    topic_lower = topic.lower() if topic else ""
    
    for key, tests in CODING_TESTS.items():
        if key in text_lower or key in topic_lower:
            return tests
    
    # Default test case
    return [{"input": {"n": "5"}, "expected_output": "result"}]

def process_bank():
    with open(BANK_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)
    
    updated = 0
    for q in questions:
        qtype = q.get("question_type", "")
        topic = q.get("topic", "")
        text = q.get("question_text", "")
        
        if qtype == "Descriptive":
            if not q.get("answer_text") and not q.get("expected_answer"):
                q["answer_text"] = find_reference_answer(text, topic)
                updated += 1
        
        elif qtype == "Coding":
            if not q.get("test_cases"):
                q["test_cases"] = find_test_cases(text, topic)
                updated += 1
    
    with open(BANK_PATH, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    
    print(f"Updated {updated} questions out of {len(questions)} total")

if __name__ == "__main__":
    process_bank()
