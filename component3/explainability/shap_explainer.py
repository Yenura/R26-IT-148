"""
SHAP Explainability - Component 3
IT22027610 | Perera K.G.S.N | R26-IT-148
Equation 11: CSS(c) = phi_0 + sum(phi_i)
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.role_configs import ROLE_DISPLAY_NAMES

FEATURE_COLS  = ["S_edu", "S_exp", "S_skill", "P_mcq", "P_desc", "P_code"]
FEATURE_NAMES = {
    "S_edu":   "Education Score",
    "S_exp":   "Experience Score",
    "S_skill": "Skill Match",
    "P_mcq":   "MCQ Performance",
    "P_desc":  "Descriptive Score",
    "P_code":  "Coding Score",
}
COLORS = {"pos":"#2ecc71","neg":"#e74c3c","bg":"#f8f9fa","line":"#2c3e50"}


def compute_shap(df, w_edu=0.20,w_exp=0.30,w_skill=0.50,
                 w_mcq=0.20,w_desc=0.30,w_code=0.50,
                 W_CV=0.40,W_INT=0.60):
    """
    Equation 11 — analytical SHAP for linear CSS model.
    phi_i = eff_weight_i * (feature_i - mean_feature_i)
    phi_0 = mean CSS
    """
    eff = {"S_edu":W_CV*w_edu,"S_exp":W_CV*w_exp,"S_skill":W_CV*w_skill,
           "P_mcq":W_INT*w_mcq,"P_desc":W_INT*w_desc,"P_code":W_INT*w_code}
    out = pd.DataFrame()
    out["candidate_id"] = df["candidate_id"]
    out["CSS"]  = df["CSS"]
    out["phi_0"]= df["CSS"].mean().round(4)
    for f, w in eff.items():
        out[f"phi_{f}"] = (w*(df[f]-df[f].mean())).round(4)
    return out


def plot_waterfall(row, cid, css, save_path=None):
    phi_0   = row["phi_0"]
    feats   = list(FEATURE_NAMES.keys())
    vals    = [row[f"phi_{f}"] for f in feats]
    labels  = [FEATURE_NAMES[f] for f in feats]
    idx     = np.argsort(np.abs(vals))[::-1]
    svals   = [vals[i] for i in idx]
    slbls   = [labels[i] for i in idx]

    fig, ax = plt.subplots(figsize=(9,5))
    fig.patch.set_facecolor(COLORS["bg"]); ax.set_facecolor(COLORS["bg"])
    run = phi_0; bots, hts, cols = [], [], []
    for v in svals:
        bots.append(run); hts.append(v)
        cols.append(COLORS["pos"] if v>=0 else COLORS["neg"]); run += v
    ax.barh(range(len(svals)), hts, left=bots, color=cols, height=0.55, edgecolor="white")
    for i,(b,h,v) in enumerate(zip(bots,hts,svals)):
        sign = "+" if v>=0 else ""
        ax.text(b+h+(0.003 if h>=0 else -0.003), i, f"{sign}{v:.3f}",
                va="center", ha="left" if h>=0 else "right",
                fontsize=9, fontweight="bold",
                color=COLORS["pos"] if h>=0 else COLORS["neg"])
    ax.axvline(phi_0, color="#7f8c8d", linestyle="--", linewidth=1.5,
               label=f"Base (φ₀) = {phi_0:.3f}")
    ax.axvline(css,   color=COLORS["line"], linestyle="-", linewidth=2.5,
               label=f"CSS = {css:.3f}")
    ax.set_yticks(range(len(slbls))); ax.set_yticklabels(slbls, fontsize=10)
    ax.set_xlabel("SHAP Contribution (φ)", fontsize=11)
    ax.set_title(f"Candidate {cid}  |  CSS(c) = φ₀ + Σφᵢ  =  {phi_0:.3f} + "
                 f"{sum(svals):.3f}  =  {css:.3f}",
                 fontsize=11, fontweight="bold")
    ax.legend(fontsize=8); ax.grid(axis="x", alpha=0.3)
    pos_p = mpatches.Patch(color=COLORS["pos"], label="Increases CSS")
    neg_p = mpatches.Patch(color=COLORS["neg"], label="Decreases CSS")
    ax.legend(handles=[pos_p,neg_p]+ax.get_legend_handles_labels()[0],
              loc="lower right", fontsize=8)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=130, bbox_inches="tight", facecolor=COLORS["bg"])
        plt.close(); return None
    return fig


def plot_summary(shap_df, title="SHAP Feature Importance", save_path=None):
    phi_cols = [c for c in shap_df.columns if c.startswith("phi_") and c!="phi_0"]
    names  = [FEATURE_NAMES.get(c.replace("phi_",""),c) for c in phi_cols]
    means  = shap_df[phi_cols].abs().mean().values
    idx    = np.argsort(means)
    fig, ax = plt.subplots(figsize=(8,4))
    fig.patch.set_facecolor(COLORS["bg"]); ax.set_facecolor(COLORS["bg"])
    colors  = plt.cm.Blues(np.linspace(0.4,0.9,len(idx)))
    bars = ax.barh([names[i] for i in idx],[means[i] for i in idx],
                   color=colors,edgecolor="white",height=0.6)
    for bar,v in zip(bars,[means[i] for i in idx]):
        ax.text(bar.get_width()+0.001, bar.get_y()+bar.get_height()/2,
                f"{v:.4f}", va="center", ha="left", fontsize=9)
    ax.set_xlabel("Mean |SHAP Value|",fontsize=11)
    ax.set_title(title,fontsize=12,fontweight="bold")
    ax.grid(axis="x",alpha=0.3); plt.tight_layout()
    if save_path:
        plt.savefig(save_path,dpi=130,bbox_inches="tight",facecolor=COLORS["bg"])
        plt.close(); return None
    return fig


def shortlist_table(df, shap_df, top_n=10):
    merged = df.merge(shap_df, on="candidate_id", suffixes=("","_s"))
    top    = merged.nlargest(top_n,"CSS").copy()
    top["rank"] = range(1,len(top)+1)
    phi_cols = [c for c in shap_df.columns if c.startswith("phi_") and c!="phi_0"]
    top["strongest"] = top.apply(
        lambda r: FEATURE_NAMES.get(max(phi_cols,key=lambda c:r[c]).replace("phi_",""),""), axis=1)
    top["weakest"]   = top.apply(
        lambda r: FEATURE_NAMES.get(min(phi_cols,key=lambda c:r[c]).replace("phi_",""),""), axis=1)
    return top[["rank","candidate_id","CSS","S_cv","S_int",
                "phi_0","strongest","weakest"]+phi_cols].reset_index(drop=True)


if __name__ == "__main__":
    BASE    = os.path.join(os.path.dirname(os.path.dirname(__file__)),"datasets")
    RESULTS = os.path.join(os.path.dirname(os.path.dirname(__file__)),"results")
    CHARTS  = os.path.join(RESULTS,"charts")
    os.makedirs(CHARTS, exist_ok=True)

    test_df = pd.read_csv(f"{BASE}/test_set.csv")
    print("=" * 60)
    print("  SHAP EXPLAINABILITY — All 20 Roles")
    print("=" * 60)

    for role in test_df["job_role"].unique():
        rdf = test_df[test_df["job_role"]==role].copy()
        rdf = rdf.sort_values("CSS", ascending=False).head(30)
        shap_df = compute_shap(rdf)
        phi_cols = [c for c in shap_df.columns if c.startswith("phi_") and c!="phi_0"]

        # Verify equation
        recon = shap_df["phi_0"] + shap_df[phi_cols].sum(axis=1)
        err   = (recon - shap_df["CSS"]).abs().max()
        dn    = ROLE_DISPLAY_NAMES.get(role, role)
        print(f"  {dn:<35} φ₀={shap_df['phi_0'].iloc[0]:.4f}  err={err:.2e}")

        # Summary chart per role
        plot_summary(shap_df, title=f"SHAP Importance — {dn}",
                     save_path=f"{CHARTS}/shap_summary_{role}.png")

        # Waterfall for top 1
        top1 = rdf.nlargest(1,"CSS").iloc[0]
        sr   = shap_df[shap_df["candidate_id"]==top1["candidate_id"]]
        if len(sr):
            plot_waterfall(sr.iloc[0], top1["candidate_id"], top1["CSS"],
                           save_path=f"{CHARTS}/waterfall_top1_{role}.png")

        shap_df.to_csv(f"{RESULTS}/shap_{role}.csv", index=False)

    print(f"\n  Charts → {CHARTS}")
    print("=" * 60)
