"""
Real CV PDF Ingestion & Training Pipeline — Component 1
IT22094872 | Dulnith K.D. | R26-IT-148

Ingests real PDF (and DOCX/TXT) resumes from a local folder, extracts text,
cleans PII, masks target role title leakage, incorporates them into the training corpus,
and triggers model retraining and validation.

Directory Layout Supported:
  1. Role Subfolders (Recommended):
     component1/data/raw_pdf_resumes/
       ├── Software Engineer/
       │     ├── candidate_1.pdf
       │     └── candidate_2.pdf
       ├── Data Scientist/
       │     └── candidate_3.pdf
       └── ...

  2. Single Folder with Manifest CSV:
     component1/data/raw_pdf_resumes/
       ├── manifest.csv  (columns: filename, job_role)
       ├── cv_01.pdf
       └── cv_02.pdf

  3. Direct CLI Path:
     python ml/ingest_pdf_resumes.py --input-dir "C:/path/to/my/cvs" --retrain
"""

import argparse
import csv
import json
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from backend.services.parser import extract_text_from_path
from data.role_requirements import ALL_ROLES
from ml.extractor import clean_text
from ml.generate_data import mask_role_leakage
from ml.train import run_training_and_evaluation

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("component1.pdf_ingest")

DATA_DIR = ROOT / "data"
PDF_DIR = DATA_DIR / "raw_pdf_resumes"
PDF_DIR.mkdir(parents=True, exist_ok=True)


def scan_and_extract_pdfs(input_dir: Path) -> List[Dict[str, str]]:
    """
    Recursively scans the given directory for PDF, DOCX, and TXT CVs,
    extracts plain text, applies PII sanitization, and returns structured records.
    """
    records = []
    supported_exts = {".pdf", ".docx", ".txt"}

    logger.info("Scanning directory for CV files: %s", input_dir)

    # Check for optional manifest.csv in the directory
    manifest_file = input_dir / "manifest.csv"
    manifest_map: Dict[str, str] = {}
    if manifest_file.exists():
        try:
            with open(manifest_file, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    fname = row.get("filename", "").strip()
                    role = row.get("job_role", "").strip()
                    if fname and role:
                        manifest_map[fname] = role
            logger.info("Loaded role mapping from manifest.csv (%d entries)", len(manifest_map))
        except Exception as e:
            logger.warning("Could not parse manifest.csv: %s", e)

    count = 0
    for root, _, files in os.walk(input_dir):
        rel_dir = Path(root).relative_to(input_dir)
        folder_role = rel_dir.parts[0] if rel_dir.parts else None

        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() not in supported_exts:
                continue

            # Determine Job Role
            role = None
            if file in manifest_map:
                role = manifest_map[file]
            elif folder_role and folder_role in ALL_ROLES:
                role = folder_role
            elif folder_role:
                # Fuzzy match folder name to canonical roles
                for r in ALL_ROLES:
                    if r.lower() == folder_role.lower():
                        role = r
                        break

            if not role:
                logger.warning("Skipping '%s': Cannot determine target IT role. Place in a role subfolder (e.g., 'Software Engineer/') or add to manifest.csv", file_path.name)
                continue

            # Extract Text
            try:
                raw_text = extract_text_from_path(file_path)
                if not raw_text or len(raw_text.strip()) < 30:
                    logger.warning("Skipping '%s': Extracted text is too short or unreadable.", file_path.name)
                    continue

                # Clean PII and apply label leakage masking
                cleaned = clean_text(raw_text)
                sanitized = mask_role_leakage(cleaned, role)

                record_id = f"PDF-CV-{count + 1:04d}"
                records.append({
                    "resume_id": record_id,
                    "resume_text": sanitized,
                    "job_role": role,
                    "education": "Extracted from PDF",
                    "experience_years": "Extracted from PDF",
                    "skills": "Extracted from PDF",
                    "source": f"Real_PDF_{file_path.name}"
                })
                count += 1
                logger.info("  [+] Ingested [%s] -> Role: %s (%d chars)", file_path.name, role, len(sanitized))
            except Exception as e:
                logger.error("Error processing '%s': %s", file_path.name, e)

    logger.info("Total real PDF/DOCX resumes extracted: %d", len(records))
    return records


def merge_and_save_dataset(new_records: List[Dict[str, str]], retrain: bool = True):
    """
    Merges ingested PDF resume records into data/train.csv, data/val.csv, data/test.csv
    and triggers model retraining.
    """
    if not new_records:
        logger.warning("No records to merge.")
        return

    normalized_csv = DATA_DIR / "normalized_resumes.csv"
    train_csv = DATA_DIR / "train.csv"
    val_csv = DATA_DIR / "val.csv"
    test_csv = DATA_DIR / "test.csv"

    # Load existing or initialize
    if normalized_csv.exists():
        df_existing = pd.read_csv(normalized_csv)
    else:
        df_existing = pd.DataFrame()

    df_new = pd.DataFrame(new_records)
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    df_combined = df_combined.drop_duplicates(subset=["resume_text"]).reset_index(drop=True)

    logger.info("Combined dataset count: %d records (added %d new PDF resumes)", len(df_combined), len(df_new))

    # Stratified Split (70% Train, 15% Val, 15% Test)
    train_df, temp_df = train_test_split(
        df_combined,
        test_size=0.30,
        random_state=42,
        stratify=df_combined["job_role"]
    )
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=42,
        stratify=temp_df["job_role"]
    )

    df_combined.to_csv(normalized_csv, index=False, encoding="utf-8")
    train_df.to_csv(train_csv, index=False, encoding="utf-8")
    val_df.to_csv(val_csv, index=False, encoding="utf-8")
    test_df.to_csv(test_csv, index=False, encoding="utf-8")

    logger.info("Saved updated dataset splits -> Train: %d, Val: %d, Test: %d", len(train_df), len(val_df), len(test_df))

    # Update manifest
    manifest_path = DATA_DIR / "dataset_manifest.json"
    manifest = {
        "dataset_name": "Component 1 Real PDF & IT Resume Corpus",
        "version": "c1_real_pdf_v2",
        "total_records": len(df_combined),
        "real_pdf_records_added": len(df_new),
        "splits": {
            "train": len(train_df),
            "val": len(val_df),
            "test": len(test_df)
        },
        "leakage_prevention": {
            "target_role_label_masked": True,
            "mask_replacement_token": "Technical Professional",
            "deduplication_performed": True,
            "preprocessing_fit_strategy": "Fitted strictly on train.csv split only"
        }
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    logger.info("Dataset manifest updated at %s", manifest_path)

    if retrain:
        logger.info("\n" + "=" * 70)
        logger.info("LAUNCHING MODEL RETRAINING WITH NEW REAL PDF RESUMES...")
        logger.info("=" * 70)
        run_training_and_evaluation()


def main():
    parser = argparse.ArgumentParser(description="Ingest real CV PDF files into Component 1 Training")
    parser.add_argument(
        "--input-dir",
        type=str,
        default=str(PDF_DIR),
        help="Directory containing PDF/DOCX resumes (default: component1/data/raw_pdf_resumes)"
    )
    parser.add_argument(
        "--no-retrain",
        action="store_true",
        help="Do not trigger model retraining after ingestion"
    )
    args = parser.parse_args()

    input_path = Path(args.input_dir)
    if not input_path.exists():
        logger.error("Input directory does not exist: %s", input_path)
        sys.exit(1)

    records = scan_and_extract_pdfs(input_path)
    if records:
        merge_and_save_dataset(records, retrain=not args.no_retrain)
    else:
        logger.info("No PDF records found to ingest. Place PDF files in %s organized by role name subfolders.", input_path)


if __name__ == "__main__":
    main()
