"""Component 1 — build model artifacts: jobs.json, TF-IDF vectorizer, CV classifier."""

import os
import json
import pickle
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.normpath(os.path.join(HERE, "..", "models"))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))


def _load_component3_jobs():
    cfg = os.path.join(ROOT, "component3", "data", "role_configs.py")
    if not os.path.exists(cfg):
        return None
    import importlib.util
    spec = importlib.util.spec_from_file_location("c3_role_configs", cfg)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    jobs = {}
    for role in mod.ROLES:
        req = mod.ROLE_REQUIREMENTS[role]
        cv_w = mod.ROLE_CV_WEIGHTS[role]
        jobs[role] = {
            "required_skills": [
                s.strip() for s in mod.ROLE_REQUIRED_SKILLS[role].split(",")
                if s.strip()
            ],
            "required_years": mod.REQUIRED_YEARS[role],
            "min_edu": req["min_edu"],
            "w_edu": cv_w["w_edu"],
            "w_exp": cv_w["w_exp"],
            "w_skill": cv_w["w_skill"],
        }
    return jobs


def main():
    os.makedirs(MODELS_DIR, exist_ok=True)
    from skills import JOBS_DEFAULT, SKILLS_LEXICON
    from matcher import SkillMatcher

    jobs = _load_component3_jobs() or JOBS_DEFAULT

    matcher = SkillMatcher(jobs=jobs).fit()
    with open(os.path.join(MODELS_DIR, "matcher.pkl"), "wb") as f:
        pickle.dump(matcher, f)
    with open(os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl"), "wb") as f:
        pickle.dump(matcher.vectorizer, f)
    with open(os.path.join(MODELS_DIR, "jobs.json"), "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2)
    with open(os.path.join(MODELS_DIR, "skills_lexicon.json"), "w", encoding="utf-8") as f:
        json.dump(SKILLS_LEXICON, f, indent=2)
    print("Saved: tfidf_vectorizer.pkl, jobs.json, skills_lexicon.json")

    train_csv = os.path.join(ROOT, "component3", "datasets", "train_set.csv")
    test_csv = os.path.join(ROOT, "component3", "datasets", "test_set.csv")
    if os.path.exists(train_csv) and os.path.exists(test_csv):
        _train_classifier(train_csv, test_csv)
    else:
        print("Skipped classifier training — component3 datasets not found")


def _train_classifier(train_csv, test_csv):
    import pandas as pd
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import (accuracy_score, f1_score, roc_auc_score,
                                 classification_report)

    tr = pd.read_csv(train_csv)
    te = pd.read_csv(test_csv)
    feats = ["S_edu", "S_exp", "S_skill"]
    Xtr, ytr = tr[feats].values, tr["relevance_label"].values.astype(int)
    Xte, yte = te[feats].values, te["relevance_label"].values.astype(int)

    scaler = StandardScaler().fit(Xtr)
    Xtr_s, Xte_s = scaler.transform(Xtr), scaler.transform(Xte)

    clf = LogisticRegression(max_iter=2000, multi_class="multinomial",
                             solver="lbfgs", random_state=42)
    clf.fit(Xtr_s, ytr)
    pred = clf.predict(Xte_s)
    proba = clf.predict_proba(Xte_s)

    acc = float(accuracy_score(yte, pred))
    f1_macro = float(f1_score(yte, pred, average="macro"))
    f1_weighted = float(f1_score(yte, pred, average="weighted"))
    try:
        roc = float(roc_auc_score(yte, proba, multi_class="ovr"))
    except ValueError:
        roc = None

    report = classification_report(yte, pred, output_dict=True, zero_division=0)

    metrics = {
        "model": "LogisticRegression(multinomial)",
        "features": feats,
        "classes": [int(c) for c in clf.classes_],
        "test_samples": int(len(te)),
        "accuracy": round(acc, 4),
        "f1_macro": round(f1_macro, 4),
        "f1_weighted": round(f1_weighted, 4),
        "roc_auc_ovr": round(roc, 4) if roc is not None else None,
        "report": {str(k): {kk: vv for kk, vv in v.items() if isinstance(vv, (int, float))}
                   for k, v in report.items() if isinstance(v, dict)},
    }
    with open(os.path.join(MODELS_DIR, "cv_classifier.pkl"), "wb") as f:
        pickle.dump({"clf": clf, "scaler": scaler, "features": feats}, f)
    with open(os.path.join(MODELS_DIR, "cv_classifier_metrics.json"), "w",
              encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"Classifier: acc={metrics['accuracy']} f1_macro={metrics['f1_macro']} "
          f"roc_auc={metrics['roc_auc_ovr']}")
    print("Saved: cv_classifier.pkl, cv_classifier_metrics.json")


if __name__ == "__main__":
    main()
