"""Evaluation script — Component 1
IT22094872 | Dulnith K.D. | R26-IT-148

Evaluates saved model artifacts against the held-out test set.

Usage (from inside component1/):
    python ml/evaluate.py [--model sbert|tfidf|both]
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
)

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from data.role_requirements import ALL_ROLES

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
        for row in csv.DictReader(f):
            texts.append(row["text"])
            labels.append(row["role"])
    return texts, labels


def evaluate_tfidf(test_texts, test_labels):
    clf_path = MODELS_DIR / "tfidf_classifier.joblib"
    vec_path = MODELS_DIR / "tfidf_vectorizer.joblib"
    if not clf_path.exists() or not vec_path.exists():
        print("TF-IDF artifacts not found. Run 'python ml/train.py' first.")
        return

    clf = joblib.load(clf_path)
    vec = joblib.load(vec_path)
    X   = vec.transform(test_texts)

    preds  = clf.predict(X)
    acc    = accuracy_score(test_labels, preds)
    macro  = f1_score(test_labels, preds, average="macro")
    report = classification_report(test_labels, preds, labels=ALL_ROLES, zero_division=0)
    cm     = confusion_matrix(test_labels, preds, labels=ALL_ROLES)

    print("\n" + "=" * 60)
    print("BASELINE: TF-IDF + LogisticRegression")
    print("=" * 60)
    print(f"Accuracy : {acc:.4f}")
    print(f"Macro-F1 : {macro:.4f}")
    print("\nPer-role classification report:")
    print(report)
    print("Confusion matrix saved (see train.py results/).")


def evaluate_sbert(test_texts, test_labels):
    clf_path = MODELS_DIR / "sbert_classifier.joblib"
    if not clf_path.exists():
        print("SBERT classifier artifact not found. Run 'python ml/train.py' first.")
        return

    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("sentence-transformers not installed — cannot evaluate SBERT model.")
        return

    clf   = joblib.load(clf_path)
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("\nEncoding test set with SBERT…")
    X = model.encode(test_texts, batch_size=64, show_progress_bar=True)

    preds  = clf.predict(X)
    acc    = accuracy_score(test_labels, preds)
    macro  = f1_score(test_labels, preds, average="macro")
    report = classification_report(test_labels, preds, labels=ALL_ROLES, zero_division=0)

    print("\n" + "=" * 60)
    print("PROPOSED: SBERT + LogisticRegression")
    print("=" * 60)
    print(f"Accuracy : {acc:.4f}")
    print(f"Macro-F1 : {macro:.4f}")
    print("\nPer-role classification report:")
    print(report)


def main():
    parser = argparse.ArgumentParser(description="Evaluate Component 1 classifiers")
    parser.add_argument("--model", choices=["sbert", "tfidf", "both"], default="both")
    args = parser.parse_args()

    test_texts, test_labels = _load_test()
    print(f"Test set: {len(test_texts)} samples, {len(set(test_labels))} roles")

    if args.model in ("tfidf", "both"):
        evaluate_tfidf(test_texts, test_labels)
    if args.model in ("sbert", "both"):
        evaluate_sbert(test_texts, test_labels)


if __name__ == "__main__":
    main()
