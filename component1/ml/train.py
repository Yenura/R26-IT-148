"""Training pipeline — Component 1
IT22094872 | Dulnith K.D. | R26-IT-148

Trains two classifiers on the 20-role synthetic resume dataset:

  PROPOSED  : SBERT (all-MiniLM-L6-v2) → LogisticRegression
  BASELINE  : TF-IDF (unigrams+bigrams, max 10,000 features) → LogisticRegression

Metrics reported:
  - Accuracy, macro-F1, weighted-F1
  - Per-role precision / recall / F1 (classification_report)
  - Confusion matrix (saved as PNG chart)
  - Full evaluation report (txt) written to results/

Artifacts saved to models/:
  sbert_classifier.joblib
  tfidf_classifier.joblib
  tfidf_vectorizer.joblib
  label_classes.joblib

Usage (from inside component1/):
    python ml/train.py [--n-per-role N] [--skip-sbert]
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import sys
import time
from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.feature_extraction.text import TfidfVectorizer

# ── Path setup ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from ml.generate_data import generate
from data.role_requirements import ALL_ROLES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("component1.train")

MODELS_DIR  = ROOT / "models"
RESULTS_DIR = ROOT / "results"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42
MAX_ITER     = 1000


# ── Data loading ──────────────────────────────────────────────────────────────

def _load_csv(path: Path):
    texts, labels = [], []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            texts.append(row["text"])
            labels.append(row["role"])
    return texts, labels


def _load_or_generate(n_per_role: int):
    train_csv = ROOT / "data" / "train.csv"
    val_csv   = ROOT / "data" / "val.csv"
    test_csv  = ROOT / "data" / "test.csv"

    if not train_csv.exists():
        logger.info("Generating synthetic dataset (%d per role)…", n_per_role)
        generate(n_per_role=n_per_role)
    else:
        logger.info("Using existing dataset in data/")

    train_texts, train_labels = _load_csv(train_csv)
    val_texts,   val_labels   = _load_csv(val_csv)
    test_texts,  test_labels  = _load_csv(test_csv)

    # Combine train+val for final training; keep test strictly held out
    all_train_texts  = train_texts + val_texts
    all_train_labels = train_labels + val_labels

    return all_train_texts, all_train_labels, test_texts, test_labels


# ── TF-IDF baseline ───────────────────────────────────────────────────────────

def train_tfidf(train_texts, train_labels, test_texts, test_labels):
    logger.info("Training BASELINE: TF-IDF → LogisticRegression…")

    vectorizer = TfidfVectorizer(
        max_features=10_000,
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=2,
    )
    X_train = vectorizer.fit_transform(train_texts)
    X_test  = vectorizer.transform(test_texts)

    clf = LogisticRegression(
        max_iter=MAX_ITER,
        C=1.0,
        solver="lbfgs",
        multi_class="multinomial",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    clf.fit(X_train, train_labels)

    preds = clf.predict(X_test)
    acc   = accuracy_score(test_labels, preds)
    f1    = f1_score(test_labels, preds, average="macro")
    report = classification_report(test_labels, preds, labels=ALL_ROLES, zero_division=0)
    cm     = confusion_matrix(test_labels, preds, labels=ALL_ROLES)

    logger.info("BASELINE TF-IDF — Accuracy: %.4f | Macro-F1: %.4f", acc, f1)

    # Save
    joblib.dump(clf,        MODELS_DIR / "tfidf_classifier.joblib")
    joblib.dump(vectorizer, MODELS_DIR / "tfidf_vectorizer.joblib")
    joblib.dump(ALL_ROLES,  MODELS_DIR / "label_classes.joblib")

    return {"model": "TF-IDF + LogReg", "accuracy": acc, "macro_f1": f1,
            "report": report, "cm": cm, "preds": preds}


# ── SBERT proposed ────────────────────────────────────────────────────────────

def train_sbert(train_texts, train_labels, test_texts, test_labels):
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        logger.warning("sentence-transformers not installed — skipping SBERT training.")
        return None

    logger.info("Training PROPOSED: SBERT → LogisticRegression…")
    logger.info("Loading all-MiniLM-L6-v2 (downloads on first run)…")

    model = SentenceTransformer("all-MiniLM-L6-v2")

    t0 = time.time()
    logger.info("Encoding %d training texts…", len(train_texts))
    X_train = model.encode(train_texts, batch_size=64, show_progress_bar=True)
    logger.info("Encoding %d test texts…", len(test_texts))
    X_test  = model.encode(test_texts,  batch_size=64, show_progress_bar=True)
    logger.info("Encoding complete in %.1fs", time.time() - t0)

    clf = LogisticRegression(
        max_iter=MAX_ITER,
        C=1.0,
        solver="lbfgs",
        multi_class="multinomial",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    clf.fit(X_train, train_labels)

    preds  = clf.predict(X_test)
    acc    = accuracy_score(test_labels, preds)
    f1     = f1_score(test_labels, preds, average="macro")
    report = classification_report(test_labels, preds, labels=ALL_ROLES, zero_division=0)
    cm     = confusion_matrix(test_labels, preds, labels=ALL_ROLES)

    logger.info("PROPOSED SBERT — Accuracy: %.4f | Macro-F1: %.4f", acc, f1)

    # Save
    joblib.dump(clf,       MODELS_DIR / "sbert_classifier.joblib")
    joblib.dump(ALL_ROLES, MODELS_DIR / "label_classes.joblib")

    return {"model": "SBERT + LogReg", "accuracy": acc, "macro_f1": f1,
            "report": report, "cm": cm, "preds": preds}


# ── Evaluation report ─────────────────────────────────────────────────────────

def _save_report(results_list, test_labels):
    lines = [
        "=" * 70,
        "COMPONENT 1 — ROLE CLASSIFIER EVALUATION REPORT",
        "IT22094872 | Dulnith K.D. | R26-IT-148",
        "=" * 70,
        f"Test set size: {len(test_labels)} samples across {len(ALL_ROLES)} roles",
        "",
    ]
    for res in results_list:
        if res is None:
            continue
        lines += [
            "─" * 70,
            f"Model: {res['model']}",
            f"  Accuracy : {res['accuracy']:.4f}",
            f"  Macro-F1 : {res['macro_f1']:.4f}",
            "",
            "Per-role classification report:",
            res["report"],
        ]

    report_path = RESULTS_DIR / "evaluation_report.txt"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Evaluation report saved: %s", report_path)


def _save_confusion_matrix(res, suffix: str):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        cm = res["cm"]
        fig, ax = plt.subplots(figsize=(18, 16))
        im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
        plt.colorbar(im, ax=ax)
        ax.set_xticks(range(len(ALL_ROLES)))
        ax.set_yticks(range(len(ALL_ROLES)))
        short_labels = [r[:20] for r in ALL_ROLES]
        ax.set_xticklabels(short_labels, rotation=60, ha="right", fontsize=7)
        ax.set_yticklabels(short_labels, fontsize=7)
        ax.set_xlabel("Predicted", fontsize=11)
        ax.set_ylabel("True", fontsize=11)
        ax.set_title(f"Confusion Matrix — {res['model']}\n"
                     f"Acc={res['accuracy']:.3f} | Macro-F1={res['macro_f1']:.3f}", fontsize=12)

        # Annotate cells
        thresh = cm.max() / 2.0
        for i in range(len(ALL_ROLES)):
            for j in range(len(ALL_ROLES)):
                if cm[i, j] > 0:
                    ax.text(j, i, str(cm[i, j]),
                            ha="center", va="center",
                            color="white" if cm[i, j] > thresh else "black",
                            fontsize=6)

        plt.tight_layout()
        path = RESULTS_DIR / f"confusion_matrix_{suffix}.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        logger.info("Confusion matrix saved: %s", path)
    except Exception as exc:
        logger.warning("Could not save confusion matrix chart: %s", exc)


def _save_metrics_json(results_list):
    summary = {}
    for res in results_list:
        if res is None:
            continue
        key = res["model"].lower().replace(" ", "_").replace("+", "plus")
        summary[key] = {
            "accuracy": round(res["accuracy"], 4),
            "macro_f1": round(res["macro_f1"], 4),
        }
    path = RESULTS_DIR / "metrics_summary.json"
    path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    logger.info("Metrics JSON saved: %s", path)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Train Component 1 classifiers")
    parser.add_argument("--n-per-role", type=int, default=150,
                        help="Number of synthetic resumes per role (default: 150)")
    parser.add_argument("--skip-sbert", action="store_true",
                        help="Skip SBERT training (only train TF-IDF baseline)")
    args = parser.parse_args()

    train_texts, train_labels, test_texts, test_labels = _load_or_generate(args.n_per_role)
    logger.info("Dataset — Train: %d | Test: %d", len(train_texts), len(test_texts))

    tfidf_res = train_tfidf(train_texts, train_labels, test_texts, test_labels)
    sbert_res = None if args.skip_sbert else train_sbert(train_texts, train_labels, test_texts, test_labels)

    results_list = [tfidf_res, sbert_res]
    _save_report(results_list, test_labels)
    _save_confusion_matrix(tfidf_res, "tfidf_baseline")
    if sbert_res:
        _save_confusion_matrix(sbert_res, "sbert_proposed")
    _save_metrics_json(results_list)

    # Print summary
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE — SUMMARY")
    print("=" * 60)
    for res in results_list:
        if res:
            print(f"  {res['model']:30s}  Acc={res['accuracy']:.4f}  Macro-F1={res['macro_f1']:.4f}")
    print(f"\nArtifacts: {MODELS_DIR}")
    print(f"Results  : {RESULTS_DIR}")


if __name__ == "__main__":
    main()
