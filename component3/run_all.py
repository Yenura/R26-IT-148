"""
run_all.py - Master Pipeline Script
Component 3 | IT22027610 | Perera K.G.S.N | R26-IT-148

Executes the full end-to-end pipeline across all 20 IT job roles:
  1. Data Ingestion & Generation (20 Roles x 600 = 12,000 candidates)
  2. CSS Engine Validation (Equations 1-8)
  3. LambdaMART LTR Training + Ablation Study (Configs A-E)
  4. Weight Sensitivity Analysis (RQ3) & Feature Importance
  5. Fairness Audit (Equations 9 & 10) for all 20 roles + Overall
  6. SHAP Explainability (Equation 11) for all 20 roles

Usage:
  python run_all.py                # full pipeline
  streamlit run dashboard/app.py   # launch dashboard
"""

import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd

ROOT    = os.path.dirname(os.path.abspath(__file__))
DATASETS= os.path.join(ROOT, "datasets")
RESULTS = os.path.join(ROOT, "results")
MODELS  = os.path.join(ROOT, "models")
CHARTS  = os.path.join(RESULTS, "charts")
for p in [DATASETS, RESULTS, MODELS, CHARTS]:
    os.makedirs(p, exist_ok=True)

def step(n, t):
    print(f"\n{'='*65}")
    print(f"  STEP {n}: {t}")
    print(f"{'='*65}")


if __name__ == "__main__":
    print("=" * 65)
    print("  COMPONENT 3 - FULL PIPELINE")
    print("  Interview-Driven Candidate Ranking | 20 IT Roles")
    print("  IT22027610 | Perera K.G.S.N | R26-IT-148")
    print("=" * 65)
    t0 = time.time()

    # ── STEP 1: Data Ingestion & Generation ───────────────────────
    step(1, "Dataset Ingestion & Generation (20 Roles x 600 = 12,000)")
    from data.generate_data import (
        load_or_generate_all_roles, generate_fairness_dataset,
        generate_job_requirements, RECORDS_PER_ROLE
    )
    from data.role_configs import ROLES, ROLE_DISPLAY_NAMES

    role_dfs = load_or_generate_all_roles(DATASETS)
    for role, df in role_dfs.items():
        safe = role.replace(" ", "_")
        df.to_csv(f"{DATASETS}/role_{safe}.csv", index=False)

    full_df = pd.concat(list(role_dfs.values()), ignore_index=True)

    # Train/Val/Test split (60/15/25) per role
    tr_l, va_l, te_l = [], [], []
    for role in ROLES:
        rdf = full_df[full_df["job_role"] == role].sample(frac=1, random_state=42)
        n = len(rdf)
        t1, t2 = int(n * 0.60), int(n * 0.75)
        tr_l.append(rdf.iloc[:t1])
        va_l.append(rdf.iloc[t1:t2])
        te_l.append(rdf.iloc[t2:])

    train_df = pd.concat(tr_l, ignore_index=True)
    val_df   = pd.concat(va_l, ignore_index=True)
    test_df  = pd.concat(te_l, ignore_index=True)
    fair_df  = generate_fairness_dataset(250)
    jobs_df  = generate_job_requirements()

    full_df.to_csv(f"{DATASETS}/candidates_full.csv",    index=False)
    train_df.to_csv(f"{DATASETS}/train_set.csv",          index=False)
    val_df.to_csv(f"{DATASETS}/val_set.csv",              index=False)
    test_df.to_csv(f"{DATASETS}/test_set.csv",            index=False)
    fair_df.to_csv(f"{DATASETS}/fairness_test_set.csv",   index=False)
    jobs_df.to_csv(f"{DATASETS}/job_requirements.csv",    index=False)

    print(f"  [OK] Full: {len(full_df):,} | Train: {len(train_df):,} | "
          f"Val: {len(val_df):,} | Test: {len(test_df):,} | Fairness: {len(fair_df):,}")

    # ── STEP 2: CSS Engine Validation ─────────────────────────────
    step(2, "CSS Engine Validation (Equations 1-8)")
    from engine.css_engine import JobRequirementProfile, CandidateFeatures, CSSEngine
    job = JobRequirementProfile.from_role("Software_Engineer")
    eng = CSSEngine(job)
    f   = CandidateFeatures("TEST", "Software_Engineer", 3, 0.90, 5.0, 0.85, 0.80, 0.75, 0.90)
    s   = eng.score_one(f)
    print(f"  [OK] Test candidate: CSS={s.CSS} | Passed={s.passed_hard_filter}")

    # ── STEP 3: LambdaMART + Ablation ─────────────────────────────
    step(3, "LambdaMART Training + Ablation Study (All 20 Roles)")
    from ltr.lambdamart_model import (LambdaMARTRanker, ablation_study,
                                       weight_sensitivity, evaluate, print_metrics)
    test_df["CSS_pred"] = 0.40 * test_df["S_cv"] + 0.60 * test_df["S_int"]
    m = evaluate(test_df, "CSS_pred")
    print_metrics(m, "CSS Weighted Average - All 20 Roles")

    abl, rk = ablation_study(train_df, val_df, test_df)
    print("\nAblation Study Results:\n" + abl.to_string(index=False))
    abl.to_csv(f"{RESULTS}/ablation_study.csv", index=False)
    rk.save(f"{MODELS}/lambdamart_model.pkl")

    # ── STEP 4: Weight Sensitivity ────────────────────────────────
    step(4, "Weight Sensitivity Analysis (RQ3)")
    sens = weight_sensitivity(test_df)
    print(sens.to_string(index=False))
    sens.to_csv(f"{RESULTS}/weight_sensitivity.csv", index=False)
    fi = rk.feature_importance()
    fi.to_csv(f"{RESULTS}/feature_importance.csv", index=False)
    print(f"\nFeature Importance:\n{fi.to_string(index=False)}")

    # ── STEP 5: Fairness ──────────────────────────────────────────
    step(5, "Fairness Audit (Equations 9 & 10) - All 20 Roles")
    from fairness.fairness_audit import run_audit, run_per_role_audit, print_audit
    per_role_rep = run_per_role_audit(fair_df)
    rows_f = []
    print(f"  {'Role':<32} {'DP':>8}  {'EOD':>8}  Status")
    print("  " + "-" * 58)
    for role, rpt in per_role_rep.items():
        print_audit(rpt, ROLE_DISPLAY_NAMES.get(role, role))
        rows_f.append({
            "Role": ROLE_DISPLAY_NAMES.get(role, role),
            "DP": rpt["dp"]["DP"],
            "EOD": rpt["eo"]["EOD"],
            "Fair": rpt["fair"]
        })
    overall_rpt = run_audit(fair_df)
    print("  " + "-" * 58)
    print_audit(overall_rpt, "OVERALL")
    rows_f.append({
        "Role": "OVERALL",
        "DP": overall_rpt["dp"]["DP"],
        "EOD": overall_rpt["eo"]["EOD"],
        "Fair": overall_rpt["fair"]
    })
    pd.DataFrame(rows_f).to_csv(f"{RESULTS}/fairness_report.csv", index=False)

    # ── STEP 6: SHAP ──────────────────────────────────────────────
    step(6, "SHAP Explainability (Equation 11) - All 20 Roles")
    from explainability.shap_explainer import (compute_shap, plot_waterfall,
                                                plot_summary)
    from data.role_configs import ROLE_CV_WEIGHTS, ROLE_INTERVIEW_WEIGHTS
    for role in ROLES:
        rdf = test_df[test_df["job_role"] == role].copy()
        rdf = rdf.sort_values("CSS_pred", ascending=False).head(30)
        cv_w = ROLE_CV_WEIGHTS[role]
        int_w = ROLE_INTERVIEW_WEIGHTS[role]
        shap_df = compute_shap(rdf,
                               w_edu=cv_w["w_edu"], w_exp=cv_w["w_exp"],
                               w_skill=cv_w["w_skill"], w_mcq=int_w["w_mcq"],
                               w_desc=int_w["w_desc"], w_code=int_w["w_code"])
        shap_df.to_csv(f"{RESULTS}/shap_{role}.csv", index=False)
        plot_summary(shap_df, f"SHAP - {ROLE_DISPLAY_NAMES[role]}",
                     f"{CHARTS}/shap_summary_{role}.png")
        top1 = rdf.nlargest(1, "CSS_pred").iloc[0]
        sr   = shap_df[shap_df["candidate_id"] == top1["candidate_id"]]
        if len(sr):
            plot_waterfall(sr.iloc[0], top1["candidate_id"], float(top1["CSS_pred"]),
                           save_path=f"{CHARTS}/waterfall_top1_{role}.png")
        print(f"  [OK] SHAP charts -> {ROLE_DISPLAY_NAMES[role]}")

    # ── Summary ───────────────────────────────────────────────────
    elapsed = time.time() - t0
    ov = m["OVERALL"]
    best_abl  = abl[abl["Config"] == "D - CSS Proposed"].iloc[0]
    ltr_abl   = abl[abl["Config"] == "E - LambdaMART LTR"].iloc[0]

    print(f"""
{'='*65}
  RESULTS SUMMARY
{'='*65}
  Dataset       : {len(full_df):,} candidates | 20 IT roles
  Train/Val/Test: {len(train_df):,} / {len(val_df):,} / {len(test_df):,}
  Fairness set  : {len(fair_df):,} (5,000M + 5,000F)
{'-'*65}
  CSS Model NDCG@5   : {ov['NDCG@5']:.4f}
  CSS Model MAP      : {ov['MAP']:.4f}
  CSS Model Spearman : {ov['Spearman']:.4f}
{'-'*65}
  Ablation - CSS Proposed : NDCG@5 = {best_abl['NDCG@5']:.4f}
  Ablation - LambdaMART   : NDCG@5 = {ltr_abl['NDCG@5']:.4f}
{'-'*65}
  Fairness DP  : {overall_rpt['dp']['DP']:.4f}  (limit 0.05) {'[PASS]' if not overall_rpt['dp']['violation'] else '[FAIL]'}
  Fairness EOD : {overall_rpt['eo']['EOD']:.4f}  (limit 0.05) {'[PASS]' if not overall_rpt['eo']['violation'] else '[FAIL]'}
{'-'*65}
  Weight Sensitivity Top-3 Stability: {sens['Top3_Stability'].max():.2f}
  Time elapsed  : {elapsed:.1f}s
{'-'*65}
  Results  -> ./results/
  Charts   -> ./results/charts/
  Datasets -> ./datasets/
{'='*65}

  Launch dashboard:
    streamlit run dashboard/app.py
""")
