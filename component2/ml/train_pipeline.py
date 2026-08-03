"""
Component 2: Interview System - Main ML Training Script
Orchestrates data loading, model training, and evaluation
"""

import os
import json
import pickle
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from data_loader import InterviewDataLoader
from answer_evaluator import DescriptiveAnswerEvaluator, MCQEvaluator, CodingEvaluator
from question_selector import QuestionSelector, load_and_prepare_questions


def main():
    print("\n" + "="*70)
    print("COMPONENT 2: AI INTERVIEW SYSTEM - ML PIPELINE")
    print("="*70)
    
    # Configuration — resolve paths relative to this script
    _root = Path(__file__).resolve().parent.parent.parent
    data_dir   = str(_root / "Data_set")
    output_dir = str(Path(__file__).resolve().parent.parent / "backend" / "trained_models")
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # ====================================================================
    # STEP 1: Load and prepare data
    # ====================================================================
    print("\n[STEP 1] Loading and Preparing Data")
    print("-" * 70)
    
    loader = InterviewDataLoader(data_dir)
    question_bank = loader.create_complete_question_bank()
    job_requirements = loader.load_job_requirements()
    
    # Save question bank
    question_bank_path = os.path.join(output_dir, "question_bank.json")
    loader.save_question_bank(question_bank, question_bank_path)
    
    # Save job requirements
    job_req_path = os.path.join(output_dir, "job_requirements.json")
    with open(job_req_path, 'w') as f:
        json.dump(job_requirements, f, indent=2)
    print(f"✓ Saved job requirements to {job_req_path}")
    
    # ====================================================================
    # STEP 2: Initialize and save evaluators
    # ====================================================================
    print("\n[STEP 2] Initializing Answer Evaluators")
    print("-" * 70)
    
    # Descriptive answer evaluator (SBERT-based)
    print("Initializing SBERT model for semantic similarity...")
    desc_evaluator = DescriptiveAnswerEvaluator(model_name="all-MiniLM-L6-v2")
    
    # Save SBERT model config
    sbert_config_path = os.path.join(output_dir, "sbert_config.json")
    with open(sbert_config_path, 'w') as f:
        json.dump({
            "model_name": "all-MiniLM-L6-v2",
            "alpha": desc_evaluator.alpha,
            "beta": desc_evaluator.beta,
            "description": "Semantic similarity scoring for descriptive answers"
        }, f, indent=2)
    print(f"✓ SBERT config saved to {sbert_config_path}")
    
    # MCQ Evaluator
    mcq_evaluator = MCQEvaluator(penalty_for_wrong=0.25)
    mcq_config_path = os.path.join(output_dir, "mcq_config.json")
    with open(mcq_config_path, 'w') as f:
        json.dump({
            "penalty_for_wrong": mcq_evaluator.penalty,
            "description": "MCQ evaluation with negative marking"
        }, f, indent=2)
    print(f"✓ MCQ config saved to {mcq_config_path}")
    
    # Coding Evaluator
    code_evaluator = CodingEvaluator(test_pass_weight=0.7)
    code_config_path = os.path.join(output_dir, "coding_config.json")
    with open(code_config_path, 'w') as f:
        json.dump({
            "test_pass_weight": code_evaluator.test_weight,
            "quality_weight": code_evaluator.quality_weight,
            "description": "Coding answer evaluation based on test cases and quality"
        }, f, indent=2)
    print(f"✓ Coding config saved to {code_config_path}")
    
    # ====================================================================
    # STEP 3: Initialize and test question selector
    # ====================================================================
    print("\n[STEP 3] Initializing Question Selector")
    print("-" * 70)
    
    selector = QuestionSelector(question_bank, model_name="all-MiniLM-L6-v2")
    
    # Save selector config
    selector_config_path = os.path.join(output_dir, "selector_config.json")
    with open(selector_config_path, 'w') as f:
        json.dump({
            "alpha": selector.alpha,
            "beta": selector.beta,
            "gamma": selector.gamma,
            "description": "Question selection weights: relevance, recency, difficulty"
        }, f, indent=2)
    print(f"✓ Selector config saved to {selector_config_path}")
    
    # ====================================================================
    # STEP 4: Test interview generation for each job role
    # ====================================================================
    print("\n[STEP 4] Testing Interview Generation")
    print("-" * 70)
    
    test_sessions = {}
    for job_role, skills in job_requirements.items():
        session = selector.create_interview_session(job_role, skills, num_questions=8)
        test_sessions[job_role] = session
        
        print(f"\n  {job_role}:")
<<<<<<< HEAD
        print(f'    - Total: {session["total_questions"]} questions')
        print(f'    - MCQ: {session["question_count"]["mcq"]}')
        print(f'    - Descriptive: {session["question_count"]["descriptive"]}')
        print(f'    - Coding: {session["question_count"]["coding"]}')
=======
        print(f"    - Total: {session['total_questions']} questions")
        print(f"    - MCQ: {session['question_count']['mcq']}")
        print(f"    - Descriptive: {session['question_count']['descriptive']}")
        print(f"    - Coding: {session['question_count']['coding']}")
>>>>>>> 89262470df6a5ccaf42b2e5b1cdae708ecc31de6
    
    # Save sample sessions
    sample_sessions_path = os.path.join(output_dir, "sample_interview_sessions.json")
    with open(sample_sessions_path, 'w') as f:
        json.dump(test_sessions, f, indent=2, default=str)
    print(f"\n✓ Sample sessions saved to {sample_sessions_path}")
    
    # ====================================================================
    # STEP 5: Test evaluators with sample answers
    # ====================================================================
    print("\n[STEP 5] Testing Answer Evaluators")
    print("-" * 70)
    
    # Test Descriptive Evaluator
    print("\n  Testing Descriptive Answer Evaluator:")
    ref_answer = "Polymorphism allows objects of different classes to be treated uniformly through a common interface."
    cand_answer = "Polymorphism enables different objects to be treated as the same type using inheritance."
    
    desc_result = desc_evaluator.evaluate_descriptive_answer(ref_answer, cand_answer)
    print(f"    Reference: {ref_answer[:60]}...")
    print(f"    Candidate: {cand_answer[:60]}...")
    print(f"    → Score: {desc_result['final_score']}/100")
    print(f"    → Similarity: {desc_result['cosine_similarity']}")
    print(f"    → Keyword Match: {desc_result['keyword_coverage']}")
    
    # Test MCQ Evaluator
    print("\n  Testing MCQ Evaluator:")
    correct = [0, 1, 2, 3, 0, 2]
    candidate = [0, 1, 0, 3, 0, 2]  # 5/6 correct
    
    mcq_result = mcq_evaluator.evaluate_batch_mcq(correct, candidate)
    print(f"    Correct: {correct}")
    print(f"    Candidate: {candidate}")
<<<<<<< HEAD
    print(f'    → Score: {mcq_result["mcq_score"]}/100')
    print(f'    → Accuracy: {mcq_result["accuracy"]}%')
=======
    print(f"    → Score: {mcq_result['mcq_score']}/100")
    print(f"    → Accuracy: {mcq_result['accuracy']}%")
>>>>>>> 89262470df6a5ccaf42b2e5b1cdae708ecc31de6
    
    # Test Coding Evaluator
    print("\n  Testing Coding Evaluator:")
    code_result = code_evaluator.evaluate_coding_answer(
        test_cases_passed=3,
        total_test_cases=4,
        has_syntax_error=False,
        complexity_order=0,
        code_length=30,
        comments_ratio=0.12
    )
    print(f"    Test Cases: {code_result['tests_passed']}/{code_result['total_tests']}")
    print(f"    Syntax Valid: {code_result['syntax_valid']}")
<<<<<<< HEAD
    print(f'    → Score: {code_result["code_score"]}/100')
=======
    print(f"    → Score: {code_result['code_score']}/100")
>>>>>>> 89262470df6a5ccaf42b2e5b1cdae708ecc31de6
    
    # Save evaluation configs
    eval_config_path = os.path.join(output_dir, "evaluation_config.json")
    with open(eval_config_path, 'w') as f:
        json.dump({
            "descriptive_test": {
                "reference": ref_answer,
                "candidate": cand_answer,
                "result": desc_result
            },
            "mcq_test": {
                "correct": correct,
                "candidate": candidate,
                "result": mcq_result
            },
            "coding_test": {
                "tests_passed": 3,
                "total_tests": 4,
                "result": code_result
            }
        }, f, indent=2)
    print(f"\n✓ Evaluation configs saved to {eval_config_path}")
    
    # ====================================================================
    # STEP 6: Create interview scoring configuration
    # ====================================================================
    print("\n[STEP 6] Creating Interview Scoring Configuration")
    print("-" * 70)
    
    # Default weights by role
    interview_weights = {
        "Software Engineer": {"mcq": 0.20, "descriptive": 0.30, "coding": 0.50},
        "Data Scientist": {"mcq": 0.25, "descriptive": 0.45, "coding": 0.30},
        "AI Researcher": {"mcq": 0.20, "descriptive": 0.40, "coding": 0.40},
        "Cybersecurity Analyst": {"mcq": 0.40, "descriptive": 0.35, "coding": 0.25},
    }
    
    # Grade bands
    grade_bands = {
        "Excellent": {"min": 85, "description": "Outstanding performance"},
        "Good": {"min": 70, "description": "Strong performance"},
        "Average": {"min": 55, "description": "Acceptable performance"},
        "Below Average": {"min": 40, "description": "Needs improvement"},
        "Poor": {"min": 0, "description": "Insufficient performance"}
    }
    
    scoring_config = {
        "interview_weights": interview_weights,
        "grade_bands": grade_bands,
        "time_penalty": {
            "enabled": True,
            "lambda": 0.1,
            "description": "Penalty for exceeding time limit"
        }
    }
    
    scoring_config_path = os.path.join(output_dir, "interview_scoring_config.json")
    with open(scoring_config_path, 'w') as f:
        json.dump(scoring_config, f, indent=2)
    print(f"✓ Scoring config saved to {scoring_config_path}")
    
    print("\n  Weight Configurations:")
    for role, weights in interview_weights.items():
        print(f"    {role}: MCQ={weights['mcq']}, Desc={weights['descriptive']}, Code={weights['coding']}")
    
    # ====================================================================
    # STEP 7: Create model metadata
    # ====================================================================
    print("\n[STEP 7] Creating Model Metadata")
    print("-" * 70)
    
    metadata = {
        "component": "Component 2: AI Interview Generation & Evaluation",
        "version": "1.0.0",
        "created_at": "2024",
        "models": {
            "question_bank": {
                "path": question_bank_path,
                "description": "Complete question bank with MCQ, Descriptive, and Coding questions",
                "total_questions": len(question_bank),
                "breakdown": {
                    "mcq": sum(1 for q in question_bank if q.get('question_type') == 'MCQ'),
                    "descriptive": sum(1 for q in question_bank if q.get('question_type') == 'Descriptive'),
                    "coding": sum(1 for q in question_bank if q.get('question_type') == 'Coding')
                }
            },
            "sbert_model": {
                "path": sbert_config_path,
                "description": "Sentence-BERT for semantic similarity",
                "model_name": "all-MiniLM-L6-v2"
            },
            "evaluators": {
                "mcq": {"path": mcq_config_path},
                "descriptive": {"path": sbert_config_path},
                "coding": {"path": code_config_path}
            },
            "selector": {
                "path": selector_config_path,
                "description": "Question selection algorithm based on relevance and recency"
            }
        },
        "api_endpoints": {
            "start_interview": "POST /api/v1/interview/start",
            "submit_answers": "POST /api/v1/interview/submit",
            "get_results": "GET /api/v1/interview/result/{id}",
            "question_bank": "GET /api/v1/interview/questions/{role}"
        }
    }
    
    metadata_path = os.path.join(output_dir, "metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Metadata saved to {metadata_path}")
    
    # ====================================================================
    # FINAL SUMMARY
    # ====================================================================
    print("\n" + "="*70)
    print("ML PIPELINE COMPLETE")
    print("="*70)
    print(f"\nOutput Directory: {output_dir}\n")
    
    files_created = {
        "question_bank.json": "Question bank with all questions",
        "job_requirements.json": "Job role to skills mapping",
        "sbert_config.json": "SBERT configuration",
        "mcq_config.json": "MCQ evaluation config",
        "coding_config.json": "Coding evaluation config",
        "selector_config.json": "Question selector config",
        "interview_scoring_config.json": "Interview scoring weights and grades",
        "sample_interview_sessions.json": "Sample interview sessions",
        "evaluation_config.json": "Evaluation test results",
        "metadata.json": "Model metadata and documentation"
    }
    
    print("Created Files:")
    for filename, description in files_created.items():
        filepath = os.path.join(output_dir, filename)
        size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
        print(f"  ✓ {filename:40s} ({size:,} bytes)")
        print(f"      └─ {description}")
    
    print("\n✓ Component 2 ML Pipeline Ready for Backend Integration")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
