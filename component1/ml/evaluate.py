"""Evaluation script — Component 1
IT22089236 | D T D Perera | R26-IT-148

Evaluates saved model artifacts against the held-out independent test set.

Usage (from inside component1/):
    python ml/evaluate.py [--model primary|tfidf|both]
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import joblib
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from data.role_requirements import ALL_ROLES
from ml.feature_engineering import extract_cv_features

MODELS_DIR = ROOT / "models"
DATA_DIR   = ROOT / "data"


def _load_test():
    test_csv = DATA_DIR / "test.csv"
    if not test_csv.exists():
        raise FileNotFoundError(
            "data/test.csv not found. Run 'python ml/train.py' first to generate data."
        )
    texts, labels = [], []
    with open(test_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            t = row.get("resume_text") or row.get("text", "")
            r = row.get("job_role") or row.get("role", "")
            if t and r:
                texts.append(t)
                labels.append(r)
    return texts, labels


def evaluate_primary(test_texts, test_labels):
    clf_path = MODELS_DIR / "cv_classifier.pkl"
    enc_path = MODELS_DIR / "label_encoder.pkl"
    if not clf_path.exists() or not enc_path.exists():
        print("Primary model artifacts not found. Run 'python ml/train.py' first.")
        return

    clf = joblib.load(clf_path)
    enc = joblib.load(enc_path)

    # Extract feature matrix
    matrix = [extract_cv_features(t)["feature_vector"] for t in test_texts]
    X = np.array(matrix, dtype=np.float32)
    y_true = enc.transform(test_labels)

    preds = clf.predict(X)
    acc = accuracy_score(y_true, preds)
    prec = precision_score(y_true, preds, average="macro", zero_division=0)
    rec = recall_score(y_true, preds, average="macro", zero_division=0)
    macro = f1_score(y_true, preds, average="macro", zero_division=0)
    weighted = f1_score(y_true, preds, average="weighted", zero_division=0)
    report = classification_report(y_true, preds, target_names=[str(c) for c in enc.classes_], zero_division=0)

    print("\n" + "=" * 70)
    print("PRIMARY MODEL: NLP Entity Features + Balanced LogisticRegression")
    print("=" * 70)
    print(f"Accuracy    : {acc:.4f} ({acc*100:.2f}%)")
    print(f"Precision   : {prec:.4f} ({prec*100:.2f}%)")
    print(f"Recall      : {rec:.4f} ({rec*100:.2f}%)")
    print(f"Macro F1    : {macro:.4f} ({macro*100:.2f}%)")
    print(f"Weighted F1 : {weighted:.4f} ({weighted*100:.2f}%)")
    print("\nPer-role classification report:")
    print(report)


def evaluate_tfidf(test_texts, test_labels):
    clf_path = MODELS_DIR / "tfidf_baseline.pkl"
    vec_path = MODELS_DIR / "tfidf_vectorizer.pkl"
    enc_path = MODELS_DIR / "label_encoder.pkl"
    if not clf_path.exists() or not vec_path.exists() or not enc_path.exists():
        print("TF-IDF artifacts not found. Run 'python ml/train.py' first.")
        return

    clf = joblib.load(clf_path)
    vec = joblib.load(vec_path)
    enc = joblib.load(enc_path)

    X = vec.transform(test_texts)
    y_true = enc.transform(test_labels)

    preds = clf.predict(X)
    acc = accuracy_score(y_true, preds)
    prec = precision_score(y_true, preds, average="macro", zero_division=0)
    rec = recall_score(y_true, preds, average="macro", zero_division=0)
    macro = f1_score(y_true, preds, average="macro", zero_division=0)
    weighted = f1_score(y_true, preds, average="weighted", zero_division=0)
    report = classification_report(y_true, preds, target_names=[str(c) for c in enc.classes_], zero_division=0)

    print("\n" + "=" * 70)
    print("BASELINE MODEL: TF-IDF (1-2 N-grams) + LogisticRegression")
    print("=" * 70)
    print(f"Accuracy    : {acc:.4f} ({acc*100:.2f}%)")
    print(f"Precision   : {prec:.4f} ({prec*100:.2f}%)")
    print(f"Recall      : {rec:.4f} ({rec*100:.2f}%)")
    print(f"Macro F1    : {macro:.4f} ({macro*100:.2f}%)")
    print(f"Weighted F1 : {weighted:.4f} ({weighted*100:.2f}%)")
    print("\nPer-role classification report:")
    print(report)


def main():
    parser = argparse.ArgumentParser(description="Evaluate Component 1 classifiers")
    parser.add_argument("--model", choices=["primary", "tfidf", "both"], default="both")
    args = parser.parse_args()

    test_texts, test_labels = _load_test()
    print(f"Held-out test set loaded: {len(test_texts)} samples across {len(set(test_labels))} roles.")

    if args.model in ("primary", "both"):
        evaluate_primary(test_texts, test_labels)
    if args.model in ("tfidf", "both"):
        evaluate_tfidf(test_texts, test_labels)


if __name__ == "__main__":
    main()
