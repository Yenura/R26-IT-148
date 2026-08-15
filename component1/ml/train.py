"""
Training Pipeline — Component 1: AI Resume Screening & IT Job Role Classification
IT22094872 | Dulnith K.D. | R26-IT-148

Trains two models for academic research comparison:
  1. PRIMARY MODEL  : Regex + Lexicon Feature Extraction → LogisticRegression (cv_classifier.pkl)
  2. BASELINE MODEL : TF-IDF Vectorizer → LogisticRegression (tfidf_baseline.pkl)

Evaluation Metrics Output to results/:
  - Accuracy, Macro F1, Weighted F1
  - Classification Report (TXT)
  - Confusion Matrix plot (PNG)
  - Metrics Summary (JSON)

Artifacts Saved to models/:
  - cv_classifier.pkl
  - label_encoder.pkl
  - feature_config.json
  - skill_lexicon.json
  - role_requirements.json
"""

import argparse
import csv
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.preprocessing import LabelEncoder

# Path setup
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from data.role_requirements import ALL_ROLES, REQUIRED_SKILLS, REQUIRED_YEARS
from ml.feature_engineering import FEATURE_NAMES, extract_cv_features
from ml.generate_data import generate_dataset
from ml.lexicon import SKILL_LEXICON

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("component1.train")

MODELS_DIR = ROOT / "models"
RESULTS_DIR = ROOT / "results"
DATA_DIR = ROOT / "data"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42
MAX_ITER = 1000


def load_data(path: Path) -> Tuple[List[str], List[str]]:
    """Loads texts and labels from CSV split file."""
    texts, labels = [], []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            texts.append(row["resume_text"])
            labels.append(row["job_role"])
    return texts, labels


def prepare_feature_dataset(texts: List[str]) -> np.ndarray:
    """Transforms raw text list into numerical feature matrix."""
    matrix = []
    for t in texts:
        feat_dict = extract_cv_features(t)
        matrix.append(feat_dict["feature_vector"])
    return np.array(matrix, dtype=np.float32)


def plot_confusion_matrix(cm: np.ndarray, classes: List[str], save_path: Path, title: str):
    """Plot and save confusion matrix heatmap."""
    fig, ax = plt.subplots(figsize=(14, 12))
    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)

    ax.set(
        xticks=np.arange(cm.shape[1]),
        yticks=np.arange(cm.shape[0]),
        xticklabels=classes,
        yticklabels=classes,
        title=title,
        ylabel='True Label',
        xlabel='Predicted Label'
    )

    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor", fontsize=9)
    plt.setp(ax.get_yticklabels(), fontsize=9)

    # Loop over data dimensions and create text annotations.
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], 'd'),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black", fontsize=8)

    fig.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def train_pipeline(n_per_role: int = 200):
    """Runs full training, baseline evaluation, and saves artifacts."""
    logger.info("Step 1: Preparing dataset...")
    train_path = DATA_DIR / "train.csv"
    val_path = DATA_DIR / "val.csv"
    test_path = DATA_DIR / "test.csv"

    if not train_path.exists():
        generate_dataset(n_per_role=n_per_role)

    train_texts, train_labels = load_data(train_path)
    val_texts, val_labels = load_data(val_path)
    test_texts, test_labels = load_data(test_path)

    # Combine train + val for final model training; test is held out for evaluation
    full_train_texts = train_texts + val_texts
    full_train_labels = train_labels + val_labels

    logger.info("Dataset size: Train=%d, Val=%d, Test=%d (Held-out)",
                len(train_texts), len(val_texts), len(test_texts))

    # Fit Label Encoder
    label_encoder = LabelEncoder()
    label_encoder.fit(ALL_ROLES)
    y_train = label_encoder.transform(full_train_labels)
    y_test = label_encoder.transform(test_labels)

    # ── PRIMARY MODEL: Feature Engineering + Logistic Regression ────────────
    logger.info("Step 2: Extracting feature vectors for Primary Model...")
    X_train_feat = prepare_feature_dataset(full_train_texts)
    X_test_feat = prepare_feature_dataset(test_texts)

    logger.info("Step 3: Training Primary Feature-Based Logistic Regression Classifier...")
    primary_clf = LogisticRegression(
        class_weight="balanced",
        max_iter=MAX_ITER,
        random_state=RANDOM_STATE,
        solver="lbfgs"
    )
    t0 = time.time()
    primary_clf.fit(X_train_feat, y_train)
    primary_train_time = time.time() - t0

    y_pred_primary = primary_clf.predict(X_test_feat)

    acc_primary = accuracy_score(y_test, y_pred_primary)
    macro_f1_primary = f1_score(y_test, y_pred_primary, average="macro")
    weighted_f1_primary = f1_score(y_test, y_pred_primary, average="weighted")

    logger.info("PRIMARY MODEL RESULTS -> Acc: %.4f | Macro F1: %.4f | Weighted F1: %.4f",
                acc_primary, macro_f1_primary, weighted_f1_primary)

    # ── BASELINE MODEL: TF-IDF + Logistic Regression ─────────────────────────
    logger.info("Step 4: Training Baseline TF-IDF + Logistic Regression Model...")
    tfidf_vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_train_tfidf = tfidf_vectorizer.fit_transform(full_train_texts)
    X_test_tfidf = tfidf_vectorizer.transform(test_texts)

    baseline_clf = LogisticRegression(
        class_weight="balanced",
        max_iter=MAX_ITER,
        random_state=RANDOM_STATE
    )
    t0 = time.time()
    baseline_clf.fit(X_train_tfidf, y_train)
    baseline_train_time = time.time() - t0

    y_pred_baseline = baseline_clf.predict(X_test_tfidf)

    acc_baseline = accuracy_score(y_test, y_pred_baseline)
    macro_f1_baseline = f1_score(y_test, y_pred_baseline, average="macro")
    weighted_f1_baseline = f1_score(y_test, y_pred_baseline, average="weighted")

    logger.info("BASELINE MODEL RESULTS -> Acc: %.4f | Macro F1: %.4f | Weighted F1: %.4f",
                acc_baseline, macro_f1_baseline, weighted_f1_baseline)

    # ── Step 5: Save Model Artifacts ──────────────────────────────────────────
    logger.info("Step 5: Saving Model Artifacts to models/...")
    
    joblib.dump(primary_clf, MODELS_DIR / "cv_classifier.pkl")
    joblib.dump(label_encoder, MODELS_DIR / "label_encoder.pkl")
    joblib.dump(baseline_clf, MODELS_DIR / "tfidf_baseline.pkl")
    joblib.dump(tfidf_vectorizer, MODELS_DIR / "tfidf_vectorizer.pkl")

    # Save feature_config.json
    feature_config = {
        "feature_names": FEATURE_NAMES,
        "n_features": len(FEATURE_NAMES),
        "target_roles": list(label_encoder.classes_),
        "model_type": "LogisticRegression(class_weight='balanced')",
        "random_state": RANDOM_STATE
    }
    with open(MODELS_DIR / "feature_config.json", "w", encoding="utf-8") as f:
        json.dump(feature_config, f, indent=2)

    # Save skill_lexicon.json
    with open(MODELS_DIR / "skill_lexicon.json", "w", encoding="utf-8") as f:
        json.dump(SKILL_LEXICON, f, indent=2)

    # Save role_requirements.json
    role_reqs_data = {
        "required_skills": REQUIRED_SKILLS,
        "required_years": REQUIRED_YEARS
    }
    with open(MODELS_DIR / "role_requirements.json", "w", encoding="utf-8") as f:
        json.dump(role_reqs_data, f, indent=2)

    # ── Step 6: Save Evaluation Metrics & Reports to results/ ────────────────
    logger.info("Step 6: Saving Evaluation Reports & Plots to results/...")

    target_names = [str(c) for c in label_encoder.classes_]
    report_primary = classification_report(y_test, y_pred_primary, target_names=target_names)
    report_baseline = classification_report(y_test, y_pred_baseline, target_names=target_names)

    report_text = f"""================================================================================
COMPONENT 1 — MODEL EVALUATION REPORT
================================================================================
Target Roles (20): {', '.join(target_names)}

1. PRIMARY MODEL: Feature Engineering + LogisticRegression (cv_classifier.pkl)
--------------------------------------------------------------------------------
Accuracy      : {acc_primary:.4f}
Macro F1      : {macro_f1_primary:.4f}
Weighted F1   : {weighted_f1_primary:.4f}
Training Time : {primary_train_time:.2f} seconds

Classification Report:
{report_primary}

2. BASELINE MODEL: TF-IDF + LogisticRegression (tfidf_baseline.pkl)
--------------------------------------------------------------------------------
Accuracy      : {acc_baseline:.4f}
Macro F1      : {macro_f1_baseline:.4f}
Weighted F1   : {weighted_f1_baseline:.4f}
Training Time : {baseline_train_time:.2f} seconds

Classification Report:
{report_baseline}
================================================================================
"""

    with open(RESULTS_DIR / "classification_report.txt", "w", encoding="utf-8") as f:
        f.write(report_text)

    # Save metrics JSON
    metrics_json = {
        "primary_model": {
            "model_file": "cv_classifier.pkl",
            "accuracy": float(acc_primary),
            "macro_f1": float(macro_f1_primary),
            "weighted_f1": float(weighted_f1_primary),
            "training_time_sec": float(primary_train_time)
        },
        "baseline_model": {
            "model_file": "tfidf_baseline.pkl",
            "accuracy": float(acc_baseline),
            "macro_f1": float(macro_f1_baseline),
            "weighted_f1": float(weighted_f1_baseline),
            "training_time_sec": float(baseline_train_time)
        },
        "num_test_samples": len(test_texts),
        "num_classes": len(target_names)
    }
    with open(RESULTS_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics_json, f, indent=2)

    # Confusion matrix plot
    cm_primary = confusion_matrix(y_test, y_pred_primary)
    plot_confusion_matrix(cm_primary, target_names, RESULTS_DIR / "confusion_matrix.png",
                          "Primary Feature-Based Logistic Regression Confusion Matrix")

    logger.info("Training and evaluation complete! All artifacts saved.")


if __name__ == "__main__":
    train_pipeline()
