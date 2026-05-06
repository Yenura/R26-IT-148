"""
Fairness Audit - Component 3
IT22027610 | Perera K.G.S.N | R26-IT-148
Equations 9 & 10 — per role + overall
"""

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
import os, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.role_configs import ROLES, ROLE_DISPLAY_NAMES

THRESHOLD   = 0.55
DP_EPSILON  = 0.05
EO_EPSILON  = 0.05
PROTECTED   = "gender"
PRIV        = "M"


def demographic_parity(df, score_col="CSS"):
    df = df.copy(); df["sl"] = (df[score_col] >= THRESHOLD).astype(int)
    rates = {g: df[df[PROTECTED]==g]["sl"].mean() for g in df[PROTECTED].unique()}
    vals  = list(rates.values())
    diff  = abs(vals[0]-vals[1]) if len(vals)>=2 else 0.0
    return {"DP": round(diff,4), "rates":{g:round(r,4) for g,r in rates.items()},
            "violation": diff > DP_EPSILON}


def equal_opportunity(df, score_col="CSS", label_col="relevance_label"):
    df = df.copy(); df["sl"] = (df[score_col] >= THRESHOLD).astype(int)
    qdf = df[df[label_col] >= 2]
    if len(qdf) == 0: return {"EOD":0.0,"violation":False}
    tpr = {g: qdf[qdf[PROTECTED]==g]["sl"].mean() for g in qdf[PROTECTED].unique()}
    vals = list(tpr.values())
    diff = abs(vals[0]-vals[1]) if len(vals)>=2 else 0.0
    return {"EOD":round(diff,4),"rates":{g:round(r,4) for g,r in tpr.items()},
            "violation": diff > EO_EPSILON, "n_qualified":len(qdf)}


def chi2_test(df, score_col="CSS"):
    df = df.copy(); df["sl"] = (df[score_col] >= THRESHOLD).astype(int)
    ct = pd.crosstab(df[PROTECTED], df["sl"])
    if ct.shape == (2,2):
        chi2, p, _, _ = chi2_contingency(ct)
        return {"chi2":round(chi2,4),"p_value":round(p,4),"significant":p<0.05}
    return {"chi2":0,"p_value":1.0,"significant":False}


def fair_reranking(df, score_col="CSS", top_k=20, min_prop=0.40):
    df = df.copy().sort_values(score_col, ascending=False).reset_index(drop=True)
    priv_pool = df[df[PROTECTED]==PRIV].sort_values(score_col,ascending=False).reset_index(drop=True)
    unpr_pool = df[df[PROTECTED]!=PRIV].sort_values(score_col,ascending=False).reset_index(drop=True)
    ranked = []; p_i = u_i = 0
    for pos in range(1, top_k+1):
        cur_u = sum(1 for r in ranked if r[PROTECTED]!=PRIV)
        need_u = int(np.ceil(pos*min_prop))
        remain = top_k - pos + 1
        if need_u - cur_u >= remain and u_i < len(unpr_pool):
            ranked.append(unpr_pool.iloc[u_i]); u_i += 1
        else:
            ps = priv_pool.iloc[p_i][score_col] if p_i < len(priv_pool) else -1
            us = unpr_pool.iloc[u_i][score_col] if u_i < len(unpr_pool) else -1
            if p_i < len(priv_pool) and ps >= us:
                ranked.append(priv_pool.iloc[p_i]); p_i += 1
            elif u_i < len(unpr_pool):
                ranked.append(unpr_pool.iloc[u_i]); u_i += 1
            elif p_i < len(priv_pool):
                ranked.append(priv_pool.iloc[p_i]); p_i += 1
            else: break
    out = pd.DataFrame(ranked).reset_index(drop=True)
    out["rank_after_fair"] = range(1, len(out)+1)
    return out


def run_audit(df, score_col="CSS"):
    dp  = demographic_parity(df, score_col)
    eo  = equal_opportunity(df, score_col)
    st  = chi2_test(df, score_col)
    violation = dp["violation"] or eo["violation"]
    report = {"dp":dp,"eo":eo,"stat":st,"fair": not violation}
    if violation:
        reranked = fair_reranking(df, score_col)
        dp_a = demographic_parity(reranked, score_col)
        eo_a = equal_opportunity(reranked, score_col)
        report["reranked_dp"] = dp_a
        report["reranked_eo"] = eo_a
    return report


def run_per_role_audit(df, score_col="CSS"):
    results = {}
    for role in df["job_role"].unique():
        rdf = df[df["job_role"]==role]
        results[role] = run_audit(rdf, score_col)
    return results


def print_audit(report, role_name="Overall"):
    dp = report["dp"]; eo = report["eo"]
    status = "✓ FAIR" if report["fair"] else "⚠ UNFAIR"
    print(f"  {role_name:<32} DP={dp['DP']:.4f} EOD={eo['EOD']:.4f}  {status}")


if __name__ == "__main__":
    BASE    = os.path.join(os.path.dirname(os.path.dirname(__file__)), "datasets")
    RESULTS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
    os.makedirs(RESULTS, exist_ok=True)

    df = pd.read_csv(f"{BASE}/fairness_test_set.csv")
    print("=" * 65)
    print("  FAIRNESS AUDIT — 10 IT Roles | Component 3")
    print("=" * 65)
    print(f"  Total: {len(df)} | Gender: {df['gender'].value_counts().to_dict()}")
    print(f"\n  {'Role':<32} {'DP':>8} {'EOD':>8}  Status")
    print("  " + "─"*60)

    per_role = run_per_role_audit(df)
    rows = []
    for role, rpt in per_role.items():
        print_audit(rpt, ROLE_DISPLAY_NAMES.get(role, role))
        rows.append({
            "Role": ROLE_DISPLAY_NAMES.get(role, role),
            "DP":   rpt["dp"]["DP"],
            "EOD":  rpt["eo"]["EOD"],
            "Fair": rpt["fair"],
            "DP_rates": str(rpt["dp"]["rates"]),
        })

    overall = run_audit(df)
    print("  " + "─"*60)
    print_audit(overall, "OVERALL")

    rows.append({
        "Role":"OVERALL","DP":overall["dp"]["DP"],
        "EOD":overall["eo"]["EOD"],"Fair":overall["fair"],
        "DP_rates":str(overall["dp"]["rates"])
    })
    pd.DataFrame(rows).to_csv(f"{RESULTS}/fairness_report.csv", index=False)
    print(f"\n  Report saved → {RESULTS}/fairness_report.csv")
    print("=" * 65)
