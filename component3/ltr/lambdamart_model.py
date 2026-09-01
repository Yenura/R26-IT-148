"""
LambdaMART LTR Model - Component 3
IT22027610 | Perera K.G.S.N | R26-IT-148

Trains global and per-role LambdaMART models across all 20 IT job roles.
Includes Ablation study (Configs A-E), Weight sensitivity analysis,
and NDCG@5, NDCG@10, MAP, Spearman rank correlation evaluation.
"""

import numpy as np
import pandas as pd
import lightgbm as lgb
from scipy.stats import spearmanr
import warnings, os, sys, pickle
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.role_configs import ROLES, ROLE_DISPLAY_NAMES

FEATURE_COLS = ["S_edu", "S_exp", "S_skill", "P_mcq", "P_desc", "P_code",
                "S_cv", "S_int", "CSS", "skill_x_mcq", "skill_x_code", "exp_x_code"]
LABEL_COL    = "relevance_label"
GROUP_COL    = "job_role"


# ── Metrics ──────────────────────────────────────────────────────

def dcg_at_k(rels, k):
    rels = np.array(rels[:k], dtype=float)
    if not len(rels):
        return 0.0
    return float(np.sum((2**rels - 1) / np.log2(np.arange(2, len(rels) + 2))))

def ndcg_at_k(rels, k):
    d = dcg_at_k(rels, k)
    i = dcg_at_k(sorted(rels, reverse=True), k)
    return d / i if i > 0 else 0.0

def avg_precision(rels):
    hits, s = 0, 0.0
    for i, r in enumerate(rels):
        if r > 0:
            hits += 1
            s += hits / (i + 1)
    return s / hits if hits else 0.0

def evaluate(df, score_col, k5=5, k10=10):
    all5, all10, allap, allsp = [], [], [], []
    per_role = {}
    for role in df[GROUP_COL].unique():
        g = df[df[GROUP_COL] == role].sort_values(score_col, ascending=False)
        rels = g[LABEL_COL].tolist()
        n5  = ndcg_at_k(rels, k5)
        n10 = ndcg_at_k(rels, k10)
        ap  = avg_precision(rels)
        sp, _ = spearmanr(g[score_col].rank(ascending=False),
                          g[LABEL_COL].rank(ascending=False))
        if np.isnan(sp):
            sp = 0.0
        per_role[role] = {
            "NDCG@5": round(n5, 4),
            "NDCG@10": round(n10, 4),
            "MAP": round(ap, 4),
            "Spearman": round(sp, 4),
            "n": len(g)
        }
        all5.append(n5)
        all10.append(n10)
        allap.append(ap)
        allsp.append(sp)
    per_role["OVERALL"] = {
        "NDCG@5": round(float(np.mean(all5)), 4),
        "NDCG@10": round(float(np.mean(all10)), 4),
        "MAP": round(float(np.mean(allap)), 4),
        "Spearman": round(float(np.mean(allsp)), 4),
        "n": len(df)
    }
    return per_role

def print_metrics(m, title=""):
    print(f"\n{'-'*65}")
    if title:
        print(f"  {title}")
        print(f"{'-'*65}")
    print(f"  {'Role':<32} {'NDCG@5':>7} {'NDCG@10':>8} {'MAP':>7} {'Spearman':>9}")
    print("-" * 65)
    for k, v in m.items():
        dn = ROLE_DISPLAY_NAMES.get(k, k)
        print(f"  {dn:<32} {v['NDCG@5']:>7.4f} {v['NDCG@10']:>8.4f} "
              f"{v['MAP']:>7.4f} {v['Spearman']:>9.4f}")
    print("-" * 65)


# ── AHP/TOPSIS baseline ──────────────────────────────────────────

def topsis_score(df):
    F = df[FEATURE_COLS].copy().values.astype(float)
    norms = np.sqrt((F**2).sum(axis=0)) + 1e-10
    N = F / norms
    W = np.ones(len(FEATURE_COLS)) / len(FEATURE_COLS)
    WN = N * W
    ip = WN.max(axis=0)
    in_ = WN.min(axis=0)
    dp = np.sqrt(((WN - ip)**2).sum(axis=1))
    dn = np.sqrt(((WN - in_)**2).sum(axis=1))
    return dn / (dp + dn + 1e-10)


# ── LambdaMART Ranker ────────────────────────────────────────────

class LambdaMARTRanker:
    def __init__(self):
        self.model = None
        self.params = {
            "objective": "lambdarank",
            "metric": "ndcg",
            "ndcg_eval_at": [5, 10],
            "label_gain": [0, 1, 3, 7],
            "num_leaves": 31,
            "max_depth": 6,
            "min_child_samples": 15,
            "n_estimators": 800,
            "learning_rate": 0.05,
            "feature_fraction": 0.85,
            "bagging_fraction": 0.85,
            "bagging_freq": 5,
            "reg_alpha": 0.1,
            "reg_lambda": 0.1,
            "verbose": -1,
            "random_state": 42,
        }

    def _prepare_grouped(self, df):
        # Sort by group to ensure contiguous group blocks for LightGBM
        df_sorted = df.sort_values(GROUP_COL).reset_index(drop=True)
        groups = df_sorted.groupby(GROUP_COL, sort=False).size().tolist()
        return df_sorted, groups

    def _engineer_features(self, df):
        """Add interaction features to improve ranking accuracy."""
        df = df.copy()
        df["S_cv"] = 0.40 * df["S_edu"] + 0.30 * df["S_exp"] + 0.50 * df["S_skill"]
        df["S_int"] = 0.20 * df["P_mcq"] + 0.30 * df["P_desc"] + 0.50 * df["P_code"]
        df["CSS"] = 0.40 * df["S_cv"] + 0.60 * df["S_int"]
        df["skill_x_mcq"] = df["S_skill"] * df["P_mcq"]
        df["skill_x_code"] = df["S_skill"] * df["P_code"]
        df["exp_x_code"] = df["S_exp"] * df["P_code"]
        return df

    def _standardize_fit(self, df):
        """Fit standardization parameters from training data."""
        from sklearn.preprocessing import StandardScaler
        self.scaler = StandardScaler()
        self.scaler.fit(df[FEATURE_COLS].values)

    def _standardize_transform(self, df):
        """Apply standardization to features."""
        scaler = getattr(self, 'scaler', None)
        if scaler is not None:
            df[FEATURE_COLS] = scaler.transform(df[FEATURE_COLS].values)
        return df

    def train(self, tr, va):
        tr = self._engineer_features(tr)
        va = self._engineer_features(va)
        self._standardize_fit(tr)
        tr = self._standardize_transform(tr)
        va = self._standardize_transform(va)
        tr_sorted, tr_groups = self._prepare_grouped(tr)
        va_sorted, va_groups = self._prepare_grouped(va)

        Xtr = tr_sorted[FEATURE_COLS].values
        ytr = tr_sorted[LABEL_COL].values.astype(int)
        Xva = va_sorted[FEATURE_COLS].values
        yva = va_sorted[LABEL_COL].values.astype(int)

        td = lgb.Dataset(Xtr, label=ytr, group=tr_groups)
        vd = lgb.Dataset(Xva, label=yva, group=va_groups, reference=td)
        cbs = [lgb.early_stopping(stopping_rounds=50, verbose=False), lgb.log_evaluation(-1)]
        self.model = lgb.train(self.params, td, valid_sets=[vd], callbacks=cbs)

    def predict(self, df):
        if isinstance(df, pd.DataFrame):
            df = self._engineer_features(df)
            df = self._standardize_transform(df)
            X = df[FEATURE_COLS].values
        else:
            X = df
        return self.model.predict(X)

    def save(self, path):
        with open(path, "wb") as f:
            pickle.dump({"model": self.model, "scaler": self.scaler}, f)
        print(f"  Model saved -> {path}")

    def feature_importance(self):
        imp = self.model.feature_importance(importance_type="gain")
        return pd.DataFrame({"Feature": FEATURE_COLS, "Importance": imp})\
                 .sort_values("Importance", ascending=False)


# ── Ablation study ───────────────────────────────────────────────

def ablation_study(tr, va, te):
    results = []
    configs = [
        ("A - CV Only",             lambda d: 0.20*d.S_edu + 0.30*d.S_exp + 0.50*d.S_skill),
        ("B - Interview Only",      lambda d: 0.20*d.P_mcq + 0.30*d.P_desc + 0.50*d.P_code),
        ("C - AHP/TOPSIS Baseline", lambda d: pd.Series(topsis_score(d), index=d.index)),
        ("D - CSS Proposed",        lambda d: 0.40*d.S_cv + 0.60*d.S_int),
    ]
    for name, fn in configs:
        df = te.copy()
        df["_score"] = fn(df)
        m = evaluate(df, "_score")["OVERALL"]
        results.append({
            "Config": name,
            **{k: m[k] for k in ["NDCG@5", "NDCG@10", "MAP", "Spearman"]}
        })

    # LambdaMART LTR
    rk = LambdaMARTRanker()
    rk.train(tr, va)
    df = te.copy()
    df["_score"] = rk.predict(df)
    m = evaluate(df, "_score")["OVERALL"]
    results.append({
        "Config": "E - LambdaMART LTR",
        **{k: m[k] for k in ["NDCG@5", "NDCG@10", "MAP", "Spearman"]}
    })
    return pd.DataFrame(results), rk


# ── Weight sensitivity ───────────────────────────────────────────

def weight_sensitivity(te):
    configs = [
        (0.40, 0.60, "Default (CV=0.40, INT=0.60)"),
        (0.50, 0.50, "Balanced (CV=0.50, INT=0.50)"),
        (0.60, 0.40, "CV-heavy (CV=0.60, INT=0.40)"),
        (0.25, 0.75, "INT-heavy (CV=0.25, INT=0.75)"),
    ]
    rows, top3_ref = [], None
    for wcv, wint, label in configs:
        df = te.copy()
        df["_score"] = wcv * df["S_cv"] + wint * df["S_int"]
        m = evaluate(df, "_score")["OVERALL"]

        top3 = {}
        for role in df[GROUP_COL].unique():
            top3[role] = set(df[df[GROUP_COL] == role].nlargest(3, "_score")["candidate_id"])
        if top3_ref is None:
            top3_ref = top3

        stab = np.mean([len(top3_ref[r] & top3[r]) / 3.0 for r in top3_ref if r in top3])
        rows.append({
            "Configuration": label,
            "W_CV": wcv,
            "W_INT": wint,
            **{k: m[k] for k in ["NDCG@5", "NDCG@10", "MAP", "Spearman"]},
            "Top3_Stability": round(float(stab), 4)
        })
    return pd.DataFrame(rows)


# ── Main ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    BASE    = os.path.join(os.path.dirname(os.path.dirname(__file__)), "datasets")
    RESULTS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
    MODELS  = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
    for p in [RESULTS, MODELS]:
        os.makedirs(p, exist_ok=True)

    tr = pd.read_csv(f"{BASE}/train_set.csv")
    va = pd.read_csv(f"{BASE}/val_set.csv")
    te = pd.read_csv(f"{BASE}/test_set.csv")
    print(f"Train={len(tr)} | Val={len(va)} | Test={len(te)}")

    # CSS baseline evaluation across all 20 roles
    te["CSS_pred"] = 0.40 * te["S_cv"] + 0.60 * te["S_int"]
    m = evaluate(te, "CSS_pred")
    print_metrics(m, "CSS Weighted Average - All 20 Roles")

    # Ablation
    print("\nRunning ablation study across all 20 roles...")
    abl, rk = ablation_study(tr, va, te)
    print(abl.to_string(index=False))
    abl.to_csv(f"{RESULTS}/ablation_study.csv", index=False)

    # Sensitivity
    print("\nRunning weight sensitivity...")
    sens = weight_sensitivity(te)
    print(sens.to_string(index=False))
    sens.to_csv(f"{RESULTS}/weight_sensitivity.csv", index=False)

    # Feature importance
    fi = rk.feature_importance()
    fi.to_csv(f"{RESULTS}/feature_importance.csv", index=False)
    print(f"\nFeature Importance:\n{fi.to_string(index=False)}")

    rk.save(f"{MODELS}/lambdamart_model.pkl")
    print("\nDone training and evaluating LambdaMART on all 20 roles.")
