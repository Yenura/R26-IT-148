"""
Employer Dashboard - Component 3
IT22027610 | Perera K.G.S.N | R26-IT-148

Full Streamlit dashboard for all 10 IT job roles.
Run: streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os, sys, warnings
warnings.filterwarnings("ignore")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from data.role_configs import (ROLES, ROLE_DISPLAY_NAMES, ROLE_ICONS,
                                ROLE_REQUIRED_SKILLS, ROLE_CV_WEIGHTS,
                                ROLE_INTERVIEW_WEIGHTS, ROLE_REQUIREMENTS,
                                REQUIRED_YEARS, EDU_LEVEL_NAMES)
from engine.css_engine import JobRequirementProfile, score_dataframe
from fairness.fairness_audit import run_audit, fair_reranking
from explainability.shap_explainer import (compute_shap, plot_waterfall,
                                            plot_summary, shortlist_table,
                                            FEATURE_NAMES)

DATASETS = os.path.join(ROOT, "datasets")
RESULTS  = os.path.join(ROOT, "results")

# ── Page config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Candidate Ranking | R26-IT-148",
    page_icon="🏆", layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.header-box {
  background: linear-gradient(135deg,#0f3460,#16213e,#1a1a2e);
  padding:22px 30px; border-radius:12px; margin-bottom:20px; color:white;
}
.metric-box {
  background:white; border-radius:10px; padding:14px;
  box-shadow:0 2px 8px rgba(0,0,0,0.08); border-left:4px solid #0f3460;
}
.badge-pass  {background:#27ae60;color:white;padding:2px 8px;border-radius:4px;font-size:12px;}
.badge-fail  {background:#c0392b;color:white;padding:2px 8px;border-radius:4px;font-size:12px;}
.badge-fair  {background:#27ae60;color:white;padding:4px 10px;border-radius:6px;font-weight:bold;}
.badge-unfair{background:#c0392b;color:white;padding:4px 10px;border-radius:6px;font-weight:bold;}
</style>
""", unsafe_allow_html=True)


# ── Cache data ───────────────────────────────────────────────────
@st.cache_data
def load_all():
    full  = pd.read_csv(f"{DATASETS}/candidates_full.csv")
    fair  = pd.read_csv(f"{DATASETS}/fairness_test_set.csv")
    jobs  = pd.read_csv(f"{DATASETS}/job_requirements.csv")
    abl   = pd.read_csv(f"{RESULTS}/ablation_study.csv")   if os.path.exists(f"{RESULTS}/ablation_study.csv")   else None
    sens  = pd.read_csv(f"{RESULTS}/weight_sensitivity.csv") if os.path.exists(f"{RESULTS}/weight_sensitivity.csv") else None
    fi    = pd.read_csv(f"{RESULTS}/feature_importance.csv") if os.path.exists(f"{RESULTS}/feature_importance.csv") else None
    return full, fair, jobs, abl, sens, fi


def css_color(v):
    return "#2ecc71" if v>=0.75 else ("#f39c12" if v>=0.55 else "#e74c3c")

def make_profile(role, min_edu, min_exp, w_edu, w_exp, w_mcq, w_desc, W_CV):
    w_skill = round(max(0.05, 1.0-w_edu-w_exp), 2)
    w_code  = round(max(0.05, 1.0-w_mcq-w_desc), 2)
    return JobRequirementProfile(
        job_id="CUSTOM", job_role=role,
        job_title=ROLE_DISPLAY_NAMES[role],
        min_edu=min_edu, min_exp_years=min_exp,
        min_skill_threshold=ROLE_REQUIREMENTS[role]["min_skill"],
        min_code_threshold=ROLE_REQUIREMENTS[role]["min_code"],
        w_edu=w_edu, w_exp=w_exp, w_skill=w_skill,
        w_mcq=w_mcq, w_desc=w_desc, w_code=w_code,
        W_CV=W_CV, W_INT=round(1.0-W_CV,2),
        required_years=REQUIRED_YEARS[role],
    )


# ── Sidebar ──────────────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.markdown("## 🏢 Employer Panel")
        st.markdown("---")

        role = st.selectbox(
            "Select Job Role",
            ROLES,
            format_func=lambda r: f"{ROLE_ICONS[r]}  {ROLE_DISPLAY_NAMES[r]}",
        )

        st.caption(f"**Required skills:** {ROLE_REQUIRED_SKILLS[role][:80]}...")

        st.markdown("#### 🔒 Hard Filter")
        min_edu = st.selectbox(
            "Min Education",
            [1,2,3,4], index=1,
            format_func=lambda x: EDU_LEVEL_NAMES[x],
        )
        min_exp = st.slider("Min Experience (yrs)", 0.0, 8.0,
                            float(ROLE_REQUIREMENTS[role]["min_exp"]), 0.5)

        st.markdown("#### 📄 CV Weights")
        dv = ROLE_CV_WEIGHTS[role]
        w_edu = st.slider("Education", 0.05, 0.60, dv["w_edu"], 0.05)
        w_exp = st.slider("Experience",0.05, 0.60, dv["w_exp"], 0.05)
        w_sk  = round(max(0.05,1.0-w_edu-w_exp),2)
        st.info(f"Skill Match weight = **{w_sk}** (auto)")

        st.markdown("#### 🎤 Interview Weights")
        di = ROLE_INTERVIEW_WEIGHTS[role]
        w_mcq  = st.slider("MCQ",        0.05, 0.60, di["w_mcq"],  0.05)
        w_desc = st.slider("Descriptive",0.05, 0.60, di["w_desc"], 0.05)
        w_co   = round(max(0.05,1.0-w_mcq-w_desc),2)
        st.info(f"Coding weight = **{w_co}** (auto)")

        st.markdown("#### ⚖️ Master Weights")
        W_CV  = st.slider("W_CV (CV weight)", 0.10, 0.90, 0.40, 0.05)
        W_INT = round(1.0-W_CV, 2)
        st.info(f"W_INT (Interview) = **{W_INT}**")

        top_n = st.slider("Shortlist top-N", 5, 50, 10)
        st.markdown("---")
        st.caption("R26-IT-148 | IT22027610")

    return role, min_edu, min_exp, w_edu, w_exp, w_mcq, w_desc, W_CV, top_n


# ── TAB 1: SHORTLIST ─────────────────────────────────────────────
def tab_shortlist(full_df, role, job, top_n):
    icon = ROLE_ICONS[role]
    dn   = ROLE_DISPLAY_NAMES[role]
    st.subheader(f"{icon} Ranked Shortlist — {dn}")

    role_df = full_df[full_df["job_role"]==role].copy()
    ranked  = score_dataframe(role_df, job)
    passed  = ranked[ranked["passed_hard_filter"]==1]
    failed  = ranked[ranked["passed_hard_filter"]==0]
    top     = passed.head(top_n)

    # KPI row
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Total Applicants",   len(role_df))
    c2.metric("Passed Filter",      len(passed))
    c3.metric("Filtered Out",       len(failed))
    c4.metric("Shortlisted",        len(top))
    c5.metric("Top CSS",            f"{passed['CSS'].max():.3f}" if len(passed) else "N/A")

    st.markdown("---")
    st.markdown(f"#### Top {top_n} Candidates — ranked by CSS score")

    for _, row in top.iterrows():
        rank  = int(row["rank"])
        cid   = row["candidate_id"]
        css   = float(row["CSS"])
        emoji = {1:"🥇",2:"🥈",3:"🥉"}.get(rank, f"**#{rank}**")

        with st.expander(f"{emoji}  {cid}  |  CSS = {css:.4f}", expanded=(rank<=3)):
            cols = st.columns(7)
            cols[0].metric("CSS",         f"{css:.3f}")
            cols[1].metric("S_cv",        f"{row['S_cv']:.3f}")
            cols[2].metric("S_int",       f"{row['S_int']:.3f}")
            cols[3].metric("S_edu",       f"{row['S_edu']:.3f}")
            cols[4].metric("S_exp",       f"{row['S_exp']:.3f}")
            cols[5].metric("S_skill",     f"{row['S_skill']:.3f}")
            cols[6].metric("Coding",      f"{row['P_code']:.3f}")

            # CSS bar
            fig,ax = plt.subplots(figsize=(7,0.5))
            ax.barh(0,1.0,color="#ecf0f1",height=0.4)
            ax.barh(0,css,color=css_color(css),height=0.4)
            ax.set_xlim(0,1); ax.axis("off")
            ax.text(css+0.01,0,f"{css:.3f}",va="center",fontsize=10,fontweight="bold")
            st.pyplot(fig,use_container_width=False); plt.close()

    if len(failed):
        with st.expander(f"❌ {len(failed)} candidates failed hard filter → forwarded to Skill Gap Module"):
            st.dataframe(
                failed[["candidate_id","filter_fail_reason"]].reset_index(drop=True),
                use_container_width=True)

    return passed


# ── TAB 2: SHAP ──────────────────────────────────────────────────
def tab_shap(full_df, role, job, top_n, passed):
    st.subheader("🔍 SHAP Explanations — Eq.11: CSS(c) = φ₀ + Σφᵢ")
    st.info("**Green** bars = feature pushes candidate above average. "
            "**Red** bars = feature pulls below average. "
            "φ₀ = mean CSS across all candidates in this role.")

    role_df = full_df[full_df["job_role"]==role].copy()
    if len(passed)==0:
        st.warning("No candidates passed the hard filter."); return

    merged = passed.merge(
        role_df[["candidate_id","S_edu","S_exp","S_skill","P_mcq","P_desc","P_code"]],
        on="candidate_id", how="left", suffixes=("","_r"))

    shap_df = compute_shap(merged,
                           w_edu=job.w_edu,w_exp=job.w_exp,w_skill=job.w_skill,
                           w_mcq=job.w_mcq,w_desc=job.w_desc,w_code=job.w_code,
                           W_CV=job.W_CV,W_INT=job.W_INT)

    # Summary chart
    st.markdown("#### Feature Importance (Mean |SHAP|)")
    fig = plot_summary(shap_df, title=f"SHAP Summary — {ROLE_DISPLAY_NAMES[role]}")
    st.pyplot(fig, use_container_width=False); plt.close()

    # Per-candidate waterfall
    st.markdown(f"#### Waterfall Charts — Top {min(top_n,5)}")
    top5 = merged.nlargest(min(top_n,5),"CSS")

    for _, row in top5.iterrows():
        cid = row["candidate_id"]; css = float(row["CSS"])
        sr  = shap_df[shap_df["candidate_id"]==cid]
        if not len(sr): continue
        with st.expander(f"#{int(row['rank'])} — {cid} | CSS={css:.4f}"):
            fig = plot_waterfall(sr.iloc[0], cid, css)
            st.pyplot(fig, use_container_width=False); plt.close()

            phi_cols = [c for c in shap_df.columns if c.startswith("phi_") and c!="phi_0"]
            phi_data = {FEATURE_NAMES.get(c.replace("phi_",""),c): round(sr.iloc[0][c],4)
                        for c in phi_cols}
            phi_df = pd.DataFrame([phi_data]).T.rename(columns={0:"SHAP φᵢ"})
            phi_df["Effect"] = phi_df["SHAP φᵢ"].apply(
                lambda x: "⬆ Helps" if x>0 else "⬇ Hurts")
            st.dataframe(phi_df, use_container_width=True)


# ── TAB 3: FAIRNESS ──────────────────────────────────────────────
def tab_fairness(fair_df, role):
    st.subheader("⚖️ Fairness Audit — Equations 9 & 10")
    col1,col2 = st.columns(2)
    with col1:
        st.markdown("**Eq.9 — Demographic Parity**")
        st.latex(r"|P(CSS\geq\tau|M)-P(CSS\geq\tau|F)|\leq 0.05")
    with col2:
        st.markdown("**Eq.10 — Equal Opportunity**")
        st.latex(r"P(\text{shortlisted}|\text{qualified},M)\approx P(\text{shortlisted}|\text{qualified},F)")

    rdf    = fair_df[fair_df["job_role"]==role].copy()
    report = run_audit(rdf, "CSS")
    dp     = report["dp"]; eo = report["eo"]

    if report["fair"]:
        st.markdown('<span class="badge-fair">✓ FAIR — All thresholds met</span>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge-unfair">⚠ UNFAIR — FA*IR re-ranking applied</span>',
                    unsafe_allow_html=True)
    st.markdown("---")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("DP Difference",  f"{dp['DP']:.4f}", delta="limit: 0.05",
              delta_color="inverse" if dp["violation"] else "normal")
    c2.metric("EOD",            f"{eo['EOD']:.4f}", delta="limit: 0.05",
              delta_color="inverse" if eo["violation"] else "normal")
    rates = dp.get("rates",{})
    if "M" in rates: c3.metric("Male shortlist rate",   f"{rates['M']:.1%}")
    if "F" in rates: c4.metric("Female shortlist rate", f"{rates['F']:.1%}")

    # Distribution plot
    fig,axes = plt.subplots(1,2,figsize=(11,4))
    for ax,gen,col in zip(axes,["M","F"],["#3498db","#e91e8c"]):
        gdf = rdf[rdf["gender"]==gen]["CSS"]
        ax.hist(gdf, bins=30, color=col, alpha=0.75, edgecolor="white")
        ax.axvline(gdf.mean(), color="red", linestyle="--", linewidth=2,
                   label=f"Mean={gdf.mean():.3f}")
        ax.set_title(f"{'Male' if gen=='M' else 'Female'} — {ROLE_DISPLAY_NAMES[role]} (n={len(gdf)})")
        ax.set_xlabel("CSS Score"); ax.legend(fontsize=9)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True); plt.close()

    # All roles summary table
    st.markdown("#### All Roles Fairness Summary")
    if os.path.exists(f"{RESULTS}/fairness_report.csv"):
        fr = pd.read_csv(f"{RESULTS}/fairness_report.csv")
        fr["Status"] = fr["Fair"].map({True:"✓ FAIR", False:"⚠ UNFAIR"})
        st.dataframe(fr[["Role","DP","EOD","Status"]], use_container_width=True)


# ── TAB 4: EVALUATION ────────────────────────────────────────────
def tab_evaluation(abl, sens, fi):
    st.subheader("📊 Model Evaluation — Ablation, Sensitivity, Feature Importance")

    if abl is not None:
        st.markdown("#### Ablation Study")
        st.caption("Compares 5 model configurations. CSS Proposed should outperform AHP/TOPSIS and single-source models.")
        fig,axes = plt.subplots(1,2,figsize=(13,4))
        colors = ["#e74c3c","#e67e22","#3498db","#2ecc71","#9b59b6"]
        for ax,metric in zip(axes,["NDCG@5","MAP"]):
            bars = ax.barh(abl["Config"], abl[metric], color=colors,
                           edgecolor="white", height=0.55)
            ax.set_xlabel(metric,fontsize=11)
            ax.set_title(f"{metric} — Ablation Study",fontsize=12,fontweight="bold")
            ax.set_xlim(0,1.05)
            for bar,v in zip(bars,abl[metric]):
                ax.text(bar.get_width()+0.01,bar.get_y()+bar.get_height()/2,
                        f"{v:.4f}",va="center",fontsize=9)
            ax.grid(axis="x",alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True); plt.close()
        st.dataframe(abl.set_index("Config"), use_container_width=True)

    if sens is not None:
        st.markdown("---")
        st.markdown("#### Weight Sensitivity Analysis (RQ3)")
        st.caption("Default config (CV=0.40, INT=0.60) validated against Schmidt & Hunter (1998) predictive validity r=0.51.")
        fig,ax = plt.subplots(figsize=(9,3.5))
        x = range(len(sens))
        ax.plot(x,sens["NDCG@5"],"o-",color="#2ecc71",lw=2,ms=8,label="NDCG@5")
        ax.plot(x,sens["Top3_Stability"],"s--",color="#e74c3c",lw=2,ms=8,label="Top-3 Stability")
        ax.set_xticks(list(x))
        ax.set_xticklabels(sens["Configuration"],rotation=12,ha="right",fontsize=9)
        ax.set_title("NDCG@5 and Top-3 Stability across Weight Configs",fontsize=12,fontweight="bold")
        ax.legend(); ax.grid(alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True); plt.close()
        st.dataframe(sens.set_index("Configuration"), use_container_width=True)

    if fi is not None:
        st.markdown("---")
        st.markdown("#### LambdaMART Feature Importance")
        fi_s = fi.sort_values("Importance", ascending=True)
        fig,ax = plt.subplots(figsize=(8,3.5))
        colors = plt.cm.Blues(np.linspace(0.4,0.9,len(fi_s)))
        ax.barh(fi_s["Feature"],fi_s["Importance"],color=colors,edgecolor="white")
        ax.set_xlabel("Gain Importance",fontsize=11)
        ax.set_title("LambdaMART — Feature Importance",fontsize=12,fontweight="bold")
        ax.grid(axis="x",alpha=0.3); plt.tight_layout()
        st.pyplot(fig, use_container_width=True); plt.close()


# ── TAB 5: DATASETS ──────────────────────────────────────────────
def tab_datasets(full_df, role):
    st.subheader("📂 Dataset Explorer")
    dn = ROLE_DISPLAY_NAMES[role]

    tabs = st.tabs(["All Roles", f"{dn} Only", "Job Requirements"])

    with tabs[0]:
        st.markdown(f"**Full dataset: {len(full_df):,} candidates across 10 roles**")
        role_counts = full_df["job_role"].value_counts().reset_index()
        role_counts.columns = ["job_role","count"]
        role_counts["Role"] = role_counts["job_role"].map(ROLE_DISPLAY_NAMES)
        fig,ax = plt.subplots(figsize=(10,4))
        ax.barh(role_counts["Role"], role_counts["count"],
                color=plt.cm.tab10(np.linspace(0,1,len(role_counts))),
                edgecolor="white")
        ax.set_xlabel("Candidates"); ax.set_title("Candidates per Role")
        ax.grid(axis="x",alpha=0.3); plt.tight_layout()
        st.pyplot(fig,use_container_width=True); plt.close()

        st.markdown("**Label distribution (0=Not Suitable → 3=Highly Suitable):**")
        ld = full_df["relevance_label"].value_counts().sort_index()
        st.bar_chart(ld)
        st.dataframe(full_df.head(50), use_container_width=True)

    with tabs[1]:
        rdf = full_df[full_df["job_role"]==role]
        st.markdown(f"**{dn}: {len(rdf)} candidates**")
        col1,col2 = st.columns(2)
        col1.markdown("**Relevance Labels:**")
        col1.bar_chart(rdf["relevance_label"].value_counts().sort_index())
        col2.markdown("**CSS Distribution:**")
        fig,ax = plt.subplots(figsize=(5,3))
        ax.hist(rdf["CSS"],bins=30,color="#3498db",edgecolor="white",alpha=0.8)
        ax.set_xlabel("CSS Score"); ax.set_ylabel("Count")
        ax.axvline(rdf["CSS"].mean(),color="red",linestyle="--",
                   label=f"Mean={rdf['CSS'].mean():.3f}")
        ax.legend(); plt.tight_layout()
        col2.pyplot(fig,use_container_width=True); plt.close()
        st.dataframe(rdf.head(100), use_container_width=True)

    with tabs[2]:
        jf = pd.read_csv(f"{DATASETS}/job_requirements.csv")
        st.dataframe(jf, use_container_width=True)


# ── MAIN ─────────────────────────────────────────────────────────
def main():
    st.markdown("""
    <div class="header-box">
      <h2 style="margin:0;">🏆 Interview-Driven Candidate Ranking System</h2>
      <p style="margin:4px 0 0 0;opacity:0.85;">
        Component 3 | Project R26-IT-148 | IT22027610 — Perera K.G.S.N.
      </p>
      <p style="margin:2px 0 0 0;opacity:0.70;font-size:13px;">
        10 IT Roles | CSS(c) = W_CV×S_cv + W_INT×S_int |
        Fairness: DP+EOD | Explainability: SHAP (Eq.11)
      </p>
    </div>
    """, unsafe_allow_html=True)

    full_df, fair_df, jobs_df, abl, sens, fi = load_all()

    (role, min_edu, min_exp, w_edu, w_exp,
     w_mcq, w_desc, W_CV, top_n) = sidebar()

    try:
        job = make_profile(role, min_edu, min_exp, w_edu, w_exp, w_mcq, w_desc, W_CV)
    except Exception as e:
        st.error(f"Weight error: {e}"); return

    tab1,tab2,tab3,tab4,tab5 = st.tabs([
        "🏆 Ranked Shortlist",
        "🔍 SHAP Explanations",
        "⚖️ Fairness Audit",
        "📊 Model Evaluation",
        "📂 Dataset Explorer",
    ])

    with tab1: passed = tab_shortlist(full_df, role, job, top_n)
    with tab2: tab_shap(full_df, role, job, top_n, passed)
    with tab3: tab_fairness(fair_df, role)
    with tab4: tab_evaluation(abl, sens, fi)
    with tab5: tab_datasets(full_df, role)


if __name__ == "__main__":
    main()
