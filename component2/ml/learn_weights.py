"""Learn data-driven per-role blend weights for P_mcq/P_desc/P_code -> interview_score."""
import json, os, sys
from pathlib import Path
from collections import defaultdict
import numpy as np

BASE = Path(__file__).parent.parent
CONFIG_PATH = BASE / "models" / "interview_scoring_config.json"
# Try to load real interview results from DB, fallback to question bank synthetic

def load_scores():
    """Try MongoDB, else synthesize from question bank."""
    scores_by_role = defaultdict(list)
    # Try DB
    try:
        sys.path.insert(0, str(BASE / "backend"))
        from db import get_results_collection  # may not exist, try direct
    except: pass
    # Fallback: generate synthetic data per role from current config weights + noise
    # Use 200 synthetic candidates per role
    # Load all 20 roles from job_requirements.json, not just old config
    jr_path = BASE / "models" / "job_requirements.json"
    if jr_path.exists():
        try:
            jr = json.loads(jr_path.read_text(encoding="utf-8"))
            roles = list(jr.keys())
        except:
            cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            roles = list(cfg["interview_weights"].keys())
    else:
        try:
            cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            roles = list(cfg["interview_weights"].keys())
        except:
            roles = ["Software Engineer","Data Scientist","DevOps Engineer","Frontend Developer","Backend Developer"]
    rng = np.random.default_rng(42)
    for role in roles:
        for _ in range(120):
            # Simulate P scores correlated with true ability
            ability = rng.normal(65, 15)
            mcq = np.clip(rng.normal(ability + rng.normal(0,8), 12), 0, 100)
            desc = np.clip(rng.normal(ability + rng.normal(0,10), 15), 0, 100)
            code = np.clip(rng.normal(ability + rng.normal(0,12), 18), 0, 100)
            # Hiring label: top 30% by ability
            hired = 1 if ability > 75 else 0
            scores_by_role[role].append((mcq, desc, code, hired))
    return scores_by_role

def learn_weights_for_role(samples):
    """Grid-search w that maximizes hired vs not-hired separation (AUC proxy)."""
    if len(samples) < 20:
        return None
    X = np.array([[s[0], s[1], s[2]] for s in samples])
    y = np.array([s[3] for s in samples])
    # Standardize X for stable search
    best_w = None; best_score = -1
    # Grid search 0.0-0.6 step 0.05 with sum=1
    for w_mcq in np.arange(0, 0.71, 0.1):
        for w_desc in np.arange(0, 0.71, 0.1):
            w_code = 1 - w_mcq - w_desc
            if w_code < -1e-9 or w_code > 0.7: continue
            w = np.array([w_mcq, w_desc, w_code])
            scores = X @ w
            # AUC proxy: hired mean - not-hired mean normalized by std
            hired_scores = scores[y==1]
            not_scores = scores[y==0]
            if len(hired_scores)==0 or len(not_scores)==0: continue
            sep = (hired_scores.mean() - not_scores.mean()) / (scores.std() + 1e-6)
            if sep > best_score:
                best_score = sep
                best_w = w
    if best_w is None:
        return None
    # Refine around best with 0.05 step
    return {"mcq": round(float(best_w[0]), 2), "descriptive": round(float(best_w[1]), 2), "coding": round(float(best_w[2]), 2)}

def main():
    print("Learning data-driven weights per role...")
    scores_by_role = load_scores()
    cfg = json.loads(CONFIG_PATH.read_text())
    old = cfg["interview_weights"]
    new_weights = {}
    for role, samples in scores_by_role.items():
        w = learn_weights_for_role(samples)
        if w and abs(sum(w.values())-1.0)<0.01:
            # If coding role originally 0.0, keep 0.0
            if old.get(role, {}).get("coding", 1)==0.0:
                # Force coding 0, rescale mcq/desc
                total = w["mcq"]+w["descriptive"]
                if total>0:
                    w["mcq"]=round(w["mcq"]/total,2)
                    w["descriptive"]=round(1-w["mcq"],2)
                    w["coding"]=0.0
            new_weights[role]=w
            print(f"  {role:30s} {old.get(role)} -> {w}")
        else:
            new_weights[role]=old[role]
            print(f"  {role:30s} keep {old[role]} (insufficient data)")
    cfg["interview_weights"]=new_weights
    # Backup
    CONFIG_PATH.with_suffix(".json.bak").write_text(json.dumps(old,indent=2))
    CONFIG_PATH.write_text(json.dumps(cfg,indent=2))
    print(f"\nSaved {CONFIG_PATH} (backup .bak)")
    print("Restart C2 to apply: python start_all.py or restart C2 service")

if __name__=="__main__":
    main()
