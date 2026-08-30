"""
Component 1: Batch Testing, Learning, and Validation Pipeline on Real IT Resumes Dataset
IT22089236 | D T D Perera | R26-IT-148

Iterates through all 251 real-world IT resume PDFs from:
C:\\Users\\thari\\Desktop\\000\\Resumes Datasets\\INFORMATION-TECHNOLOGY

Performs one-by-one breakdown testing:
1. PDF Text Extraction & Sanitization
2. Section Partitioning (Experience, Education, Skills, Projects, Certifications)
3. Skill & Alias Extraction Coverage
4. 3-Tier Experience Decomposition (Total Prof, IT Sector, Target Relevant)
5. Degree Level, Field Relevance, & Certification Recognition
6. Seniority Detection & Evidence Analysis
7. AI Job Role Classification & Alternative Probability Ranking
8. Full Scoring Engine ($S_{skill}, S_{exp}, S_{edu}$)
9. Anomaly & Edge-Case Detection
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Any, Dict, List

# Setup paths
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.services.parser import extract_text_from_path
from backend.services.extractor import extract
from backend.services.scorer import score
from backend.services.predictor import Predictor
from data.role_requirements import ALL_ROLES
from ml.extractor import (
    extract_deep_cv_profile,
    extract_sections,
    extract_skills_and_certifications,
    extract_experience_details,
    extract_education_details,
    clean_text,
    SKILL_LEXICON,
    SKILL_ALIASES,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("test_and_learn")

DATASET_DIR = Path(r"C:\Users\thari\Desktop\000\Resumes Datasets\INFORMATION-TECHNOLOGY")


def run_batch_evaluation():
    if not DATASET_DIR.exists():
        logger.error("Dataset directory does not exist: %s", DATASET_DIR)
        return

    pdf_files = sorted([f for f in DATASET_DIR.iterdir() if f.suffix.lower() == ".pdf"])
    total_files = len(pdf_files)
    logger.info("Found %d PDF resumes to process in %s", total_files, DATASET_DIR)

    predictor = Predictor()

    results = []
    failed_files = []
    zero_skills_files = []
    zero_exp_files = []
    zero_edu_files = []
    role_predictions_count = {}
    seniority_count = {}
    degree_levels_count = {}
    all_discovered_skills = set()

    start_time = time.time()

    for idx, pdf_path in enumerate(pdf_files, 1):
        filename = pdf_path.name
        file_res = {
            "index": idx,
            "filename": filename,
            "success": False,
            "text_length": 0,
            "word_count": 0,
            "skills_count": 0,
            "skills": [],
            "total_experience_years": 0.0,
            "it_experience_years": 0.0,
            "role_relevant_experience_years": 0.0,
            "employment_records_count": 0,
            "seniority": "Unknown",
            "degree_level": "None",
            "degree_field": "None",
            "predicted_role": "Unknown",
            "prediction_confidence": 0.0,
            "s_skill": 0.0,
            "s_exp": 0.0,
            "s_edu": 0.0,
            "errors": []
        }

        try:
            # 1. Parse Text
            raw_text = extract_text_from_path(str(pdf_path))
            if not raw_text or len(raw_text.strip()) < 20:
                file_res["errors"].append("Extracted text is empty or too short")
                failed_files.append((filename, "Empty text"))
                results.append(file_res)
                continue

            file_res["text_length"] = len(raw_text)
            file_res["word_count"] = len(raw_text.split())

            # 2. Extract Deep Profile & Features
            features = extract(raw_text, target_role="Software Engineer")
            
            file_res["skills_count"] = len(features.skills)
            file_res["skills"] = features.skills
            for s in features.skills:
                all_discovered_skills.add(s)

            if len(features.skills) == 0:
                zero_skills_files.append(filename)

            file_res["total_experience_years"] = features.total_professional_experience_years
            file_res["it_experience_years"] = features.it_sector_experience_years
            file_res["role_relevant_experience_years"] = features.role_relevant_experience_years
            file_res["employment_records_count"] = len(features.employment_records)
            file_res["seniority"] = features.seniority
            seniority_count[features.seniority] = seniority_count.get(features.seniority, 0) + 1

            if features.total_professional_experience_years == 0.0:
                zero_exp_files.append(filename)

            edu_det = features.education_details
            file_res["degree_level"] = edu_det.get("degree_level", "Unknown")
            file_res["degree_field"] = edu_det.get("degree_field", "Unknown")
            degree_levels_count[file_res["degree_level"]] = degree_levels_count.get(file_res["degree_level"], 0) + 1

            # 3. Model Role Prediction
            pred = predictor.predict(raw_text)
            file_res["predicted_role"] = pred.job_role
            file_res["prediction_confidence"] = pred.confidence
            role_predictions_count[pred.job_role] = role_predictions_count.get(pred.job_role, 0) + 1

            # 4. Scorer Evaluation against predicted role
            scores = score(
                role=pred.job_role if pred.job_role in ALL_ROLES else "Software Engineer",
                edu_level=features.edu_level,
                experience_years=features.experience_years,
                role_relevant_experience_years=features.role_relevant_experience_years,
                employment_records=features.employment_records,
                candidate_education=features.education,
                verified_certifications=features.verified_certifications,
            )
            file_res["s_skill"] = scores.S_skill
            file_res["s_exp"] = scores.S_exp
            file_res["s_edu"] = scores.S_edu
            file_res["success"] = True

        except Exception as exc:
            file_res["errors"].append(str(exc))
            failed_files.append((filename, str(exc)))
            logger.error("Error processing %s: %s", filename, exc, exc_info=True)

        results.append(file_res)

        if idx % 25 == 0 or idx == total_files:
            logger.info("Processed %d/%d resumes (%.1f%%)...", idx, total_files, (idx / total_files) * 100)

    elapsed = time.time() - start_time
    success_count = sum(1 for r in results if r["success"])

    logger.info("=" * 80)
    logger.info("BATCH TEST COMPLETED in %.2f seconds (%.2f ms/resume)", elapsed, (elapsed / total_files) * 1000)
    logger.info("Total Resumes Processed: %d", total_files)
    logger.info("Successful Breakdowns:   %d (%.2f%%)", success_count, (success_count / total_files) * 100)
    logger.info("Failed Breakdowns:       %d", len(failed_files))
    logger.info("Zero Skills Extracted:   %d (%.2f%%)", len(zero_skills_files), (len(zero_skills_files)/total_files)*100)
    logger.info("Zero Exp Extracted:      %d (%.2f%%)", len(zero_exp_files), (len(zero_exp_files)/total_files)*100)
    logger.info("Total Unique Skills:     %d", len(all_discovered_skills))
    logger.info("Seniority Breakdown:     %s", json.dumps(seniority_count, indent=2))
    logger.info("Degree Level Breakdown:  %s", json.dumps(degree_levels_count, indent=2))
    logger.info("Predicted Roles Top 10:  %s", json.dumps(dict(sorted(role_predictions_count.items(), key=lambda x: -x[1])[:10]), indent=2))
    logger.info("=" * 80)

    # Save detailed evaluation report
    report_file = ROOT / "results" / "dataset_evaluation_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump({
            "total_resumes": total_files,
            "success_count": success_count,
            "failed_count": len(failed_files),
            "failed_files": failed_files,
            "zero_skills_count": len(zero_skills_files),
            "zero_skills_files": zero_skills_files[:20],
            "zero_exp_count": len(zero_exp_files),
            "zero_exp_files": zero_exp_files[:20],
            "seniority_distribution": seniority_count,
            "degree_distribution": degree_levels_count,
            "role_distribution": role_predictions_count,
            "all_discovered_skills_count": len(all_discovered_skills),
            "sample_results": results[:10]
        }, f, indent=2)
    logger.info("Saved report to %s", report_file)


if __name__ == "__main__":
    run_batch_evaluation()
