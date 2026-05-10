"""
HR Recruitment Dashboard - Component 3
TalentRank — Smart Recruitment Platform
IT22027610 | Perera K.G.S.N | R26-IT-148
Run: streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os, sys, warnings
warnings.filterwarnings("ignore")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from data.role_configs import (
    ROLES, ROLE_DISPLAY_NAMES, ROLE_ICONS,
    ROLE_REQUIRED_SKILLS, ROLE_CV_WEIGHTS,
    ROLE_INTERVIEW_WEIGHTS, ROLE_REQUIREMENTS, REQUIRED_YEARS
)
from engine.css_engine import JobRequirementProfile, score_dataframe

DATASETS = os.path.join(ROOT, "datasets")

st.set_page_config(
    page_title="TalentRank — Smart Recruitment",
    page_icon="🎯", layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.main { background-color: #f5f7fa; }
.top-header {
  background: linear-gradient(135deg,#1e3a5f 0%,#2d6a9f 100%);
  padding:28px 36px; border-radius:14px;
  margin-bottom:28px; color:white;
}
.top-header h1 { margin:0; font-size:28px; font-weight:700; }
.top-header p  { margin:6px 0 0 0; opacity:0.85; font-size:15px; }
.kpi-card {
  background:white; border-radius:12px; padding:20px;
  text-align:center; box-shadow:0 2px 8px rgba(0,0,0,0.06);
}
.kpi-number { font-size:36px; font-weight:700; color:#1e3a5f; }
.kpi-label  { font-size:13px; color:#666; margin-top:4px; }
.section-header {
  font-size:18px; font-weight:600; color:#1e3a5f;
  margin:24px 0 16px 0; padding-bottom:8px;
  border-bottom:2px solid #e0e7ef;
}
.badge-excellent { background:#e8f5e9; color:#2e7d32; padding:4px 12px; border-radius:20px; font-weight:600; font-size:13px; border:1px solid #a5d6a7; }
.badge-good      { background:#e3f2fd; color:#1565c0; padding:4px 12px; border-radius:20px; font-weight:600; font-size:13px; border:1px solid #90caf9; }
.badge-average   { background:#fff8e1; color:#f57f17; padding:4px 12px; border-radius:20px; font-weight:600; font-size:13px; border:1px solid #ffe082; }
.badge-weak      { background:#fce4ec; color:#c62828; padding:4px 12px; border-radius:20px; font-weight:600; font-size:13px; border:1px solid #ef9a9a; }
.strength-pill   { background:#e8f5e9; color:#2e7d32; padding:5px 14px; border-radius:20px; font-size:13px; font-weight:500; display:inline-block; margin:3px; }
.weakness-pill   { background:#fce4ec; color:#c62828; padding:5px 14px; border-radius:20px; font-size:13px; font-weight:500; display:inline-block; margin:3px; }
.neutral-pill    { background:#f3f4f6; color:#374151; padding:5px 14px; border-radius:20px; font-size:13px; font-weight:500; display:inline-block; margin:3px; }
section[data-testid="stSidebar"] { background:#1e3a5f; }
#MainMenu { visibility:hidden; } footer { visibility:hidden; } header { visibility:hidden; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────────
@st.cache_data
def load_data():
    return pd.read_csv(f"{DATASETS}/candidates_full.csv")

def pct(v):   return int(round(float(v) * 100))
def stars(v): s=round(float(v)*5); return "⭐"*s+"☆"*(5-s)

def match_badge(v):
    if v>=0.80: return '<span class="badge-excellent">Excellent</span>'
    elif v>=0.65: return '<span class="badge-good">Good</span>'
    elif v>=0.50: return '<span class="badge-average">Average</span>'
    else: return '<span class="badge-weak">Needs Improvement</span>'

def match_color(v):
    if v>=0.80: return "#2e7d32"
    elif v>=0.65: return "#1565c0"
    elif v>=0.50: return "#f57f17"
    else: return "#c62828"

def match_bg(v):
    if v>=0.80: return "#e8f5e9"
    elif v>=0.65: return "#e3f2fd"
    elif v>=0.50: return "#fff8e1"
    else: return "#fce4ec"

def verdict(css):
    if css>=0.82: return "🟢 Strongly Recommended"
    elif css>=0.68: return "🔵 Recommended"
    elif css>=0.55: return "🟡 Consider with Caution"
    else: return "🔴 Not Recommended"

def edu_label(lv):
    return {1:"Diploma",2:"Bachelor's Degree",
            3:"Master's Degree",4:"PhD"}.get(int(lv),"Unknown")

def make_profile(role, min_edu, min_exp):
    cv_w=ROLE_CV_WEIGHTS[role]; int_w=ROLE_INTERVIEW_WEIGHTS[role]
    req=ROLE_REQUIREMENTS[role]
    return JobRequirementProfile(
        job_id="HR_JOB", job_role=role,
        job_title=ROLE_DISPLAY_NAMES[role],
        min_edu=min_edu, min_exp_years=min_exp,
        min_skill_threshold=req["min_skill"],
        min_code_threshold=req["min_code"],
        w_edu=cv_w["w_edu"], w_exp=cv_w["w_exp"],
        w_skill=cv_w["w_skill"], w_mcq=int_w["w_mcq"],
        w_desc=int_w["w_desc"], w_code=int_w["w_code"],
        W_CV=0.40, W_INT=0.60,
        required_years=REQUIRED_YEARS[role],
    )

def sw_analysis(row):
    areas={
        "Education":        float(row.get("S_edu",0)),
        "Work Experience":  float(row.get("S_exp",0)),
        "Technical Skills": float(row.get("S_skill",0)),
        "Knowledge Test":   float(row.get("P_mcq",0)),
        "Problem Solving":  float(row.get("P_desc",0)),
        "Practical Coding": float(row.get("P_code",0)),
    }
    return {
        "strengths":  [k for k,v in areas.items() if v>=0.75],
        "good":       [k for k,v in areas.items() if 0.60<=v<0.75],
        "weaknesses": [k for k,v in areas.items() if v<0.50],
        "all": areas
    }

def draw_radar(areas):
    labels=list(areas.keys()); vals=[pct(v) for v in areas.values()]
    vals+=vals[:1]
    angles=np.linspace(0,2*np.pi,len(labels),endpoint=False).tolist()
    angles+=angles[:1]
    fig,ax=plt.subplots(figsize=(4,4),subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("white")
    ax.plot(angles,vals,"o-",lw=2,color="#2d6a9f")
    ax.fill(angles,vals,alpha=0.25,color="#2d6a9f")
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels,size=8)
    ax.set_ylim(0,100)
    ax.set_yticks([25,50,75,100])
    ax.set_yticklabels(["25%","50%","75%","100%"],size=7)
    ax.grid(True,alpha=0.3); plt.tight_layout()
    return fig


# ── Sidebar ──────────────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='padding:16px 0 8px 0;'>
          <div style='color:white;font-size:22px;font-weight:700;'>🎯 TalentRank</div>
          <div style='color:#90caf9;font-size:13px;margin-top:4px;'>Smart Recruitment Platform</div>
        </div>
        <hr style='border-color:#2d6a9f;margin:12px 0;'>
        """, unsafe_allow_html=True)

        st.markdown("<p style='color:#90caf9;font-size:12px;text-transform:uppercase;letter-spacing:1px;'>Job Position</p>", unsafe_allow_html=True)
        role = st.selectbox("pos", ROLES,
            format_func=lambda r: f"{ROLE_ICONS[r]}  {ROLE_DISPLAY_NAMES[r]}",
            label_visibility="collapsed")

        st.markdown(f"<div style='background:#16325a;border-radius:8px;padding:10px 14px;margin:10px 0;'><div style='color:#90caf9;font-size:11px;margin-bottom:4px;'>REQUIRED SKILLS</div><div style='color:white;font-size:12px;'>{ROLE_REQUIRED_SKILLS[role]}</div></div>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color:#2d6a9f;margin:16px 0;'>", unsafe_allow_html=True)

        st.markdown("<p style='color:#90caf9;font-size:12px;text-transform:uppercase;'>Minimum Requirements</p>", unsafe_allow_html=True)
        min_edu = st.selectbox("Min Education Level",[1,2,3,4],index=1,
            format_func=edu_label)
        min_exp = st.slider("Min Work Experience (years)",0.0,10.0,
            float(ROLE_REQUIREMENTS[role]["min_exp"]),0.5)

        st.markdown("<hr style='border-color:#2d6a9f;margin:16px 0;'>", unsafe_allow_html=True)
        top_n = st.slider("Candidates to Shortlist",5,50,15)
        st.markdown("<hr style='border-color:#2d6a9f;margin:16px 0;'>", unsafe_allow_html=True)
        st.markdown("<p style='color:#90caf9;font-size:11px;'>Powered by AI Ranking Engine<br>R26-IT-148 | SLIIT</p>", unsafe_allow_html=True)
    return role, min_edu, min_exp, top_n


# ── TAB 1: SHORTLIST ─────────────────────────────────────────────
def tab_shortlist(full_df, role, job, top_n):
    dn = ROLE_DISPLAY_NAMES[role]; icon = ROLE_ICONS[role]
    role_df = full_df[full_df["job_role"]==role].copy()
    ranked  = score_dataframe(role_df, job)
    passed  = ranked[ranked["passed_hard_filter"]==1]
    failed  = ranked[ranked["passed_hard_filter"]==0]
    top     = passed.head(top_n).copy()

    st.markdown(f"<div class='section-header'>{icon} Candidate Shortlist — {dn}</div>", unsafe_allow_html=True)

    k1,k2,k3,k4 = st.columns(4)
    k1.markdown(f"<div class='kpi-card'><div class='kpi-number'>{len(role_df)}</div><div class='kpi-label'>Total Applications</div></div>", unsafe_allow_html=True)
    k2.markdown(f"<div class='kpi-card'><div class='kpi-number' style='color:#2e7d32;'>{len(passed)}</div><div class='kpi-label'>Qualified Candidates</div></div>", unsafe_allow_html=True)
    k3.markdown(f"<div class='kpi-card'><div class='kpi-number' style='color:#c62828;'>{len(failed)}</div><div class='kpi-label'>Did Not Meet Requirements</div></div>", unsafe_allow_html=True)
    top_s = pct(passed["CSS"].max()) if len(passed) else 0
    k4.markdown(f"<div class='kpi-card'><div class='kpi-number' style='color:#1565c0;'>{top_s}%</div><div class='kpi-label'>Top Match Score</div></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Bar chart
    if len(top)>0:
        st.markdown("<div class='section-header'>Overall Match Score — Top Candidates</div>", unsafe_allow_html=True)
        show_n = min(15, len(top))
        cd = top.head(show_n).copy()
        cd["disp"] = [f"#{i+1} — {c}" for i,c in enumerate(cd["candidate_id"])]
        cd["sp"]   = (cd["CSS"]*100).round(0)
        cd["col"]  = cd["CSS"].apply(match_color)

        fig,ax = plt.subplots(figsize=(10, show_n*0.52+0.8))
        fig.patch.set_facecolor("white"); ax.set_facecolor("#f8f9fa")
        bars = ax.barh(cd["disp"][::-1], cd["sp"][::-1],
                       color=cd["col"][::-1].tolist(),
                       height=0.6, edgecolor="white", linewidth=0.5)
        for bar,score in zip(bars, cd["sp"][::-1]):
            ax.text(bar.get_width()+0.8, bar.get_y()+bar.get_height()/2,
                    f"{int(score)}%", va="center", ha="left",
                    fontsize=10, fontweight="bold", color="#333")
        ax.set_xlim(0,115)
        ax.set_xlabel("Overall Match Score (%)", fontsize=11, color="#555")
        ax.set_title(f"Candidate Rankings — {dn}", fontsize=13,
                     fontweight="bold", color="#1e3a5f", pad=12)
        ax.axvline(80,color="#2e7d32",linestyle="--",alpha=0.4,linewidth=1.5,label="Excellent (80%+)")
        ax.axvline(65,color="#1565c0",linestyle="--",alpha=0.4,linewidth=1.5,label="Good (65%+)")
        ax.legend(fontsize=9, loc="lower right")
        ax.grid(axis="x",alpha=0.3)
        ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True); plt.close()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-header'>Top {top_n} Candidates — Detailed Profiles</div>", unsafe_allow_html=True)

    medals = {1:"🥇",2:"🥈",3:"🥉"}
    for _, row in top.iterrows():
        rank=int(row["rank"]); cid=row["candidate_id"]
        css=float(row["CSS"]); sw=sw_analysis(row); vd=verdict(css)
        ric=medals.get(rank,f"#{rank}")

        orig = role_df[role_df["candidate_id"]==cid]
        if len(orig):
            edu_txt = edu_label(int(orig.iloc[0]["edu_level"]))
            yrs = float(orig.iloc[0]["years_experience"])
            exp_txt = f"{yrs:.1f} years" if yrs>=1 else f"{int(yrs*12)} months"
        else:
            edu_txt=exp_txt="—"

        score_items=[
            ("Education",        float(row.get("S_edu",0))),
            ("Work Experience",  float(row.get("S_exp",0))),
            ("Technical Skills", float(row.get("S_skill",0))),
            ("Knowledge Test",   float(row.get("P_mcq",0))),
            ("Problem Solving",  float(row.get("P_desc",0))),
            ("Practical Coding", float(row.get("P_code",0))),
        ]

        with st.expander(f"{ric}  Candidate {cid}   |   Match Score: {pct(css)}%   |   {vd}", expanded=(rank<=3)):
            left, right = st.columns([3,2])
            with left:
                st.markdown(f"**Education:** {edu_txt} &nbsp;&nbsp; **Experience:** {exp_txt}")
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**Performance Breakdown**")

                for label, score in score_items:
                    c1,c2,c3 = st.columns([2,4,2])
                    c1.markdown(f"<div style='font-size:13px;padding-top:6px;color:#444;'>{label}</div>", unsafe_allow_html=True)
                    # Simple progress bar using st.progress
                    c2.progress(int(pct(score)))
                    c3.markdown(f"<div style='padding-top:4px;'>{match_badge(score)}</div>", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**Key Strengths**")
                if sw["strengths"]:
                    st.markdown(" ".join([f'<span class="strength-pill">✓ {s}</span>' for s in sw["strengths"]]), unsafe_allow_html=True)
                else:
                    st.markdown('<span class="neutral-pill">No standout strengths identified</span>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**Areas for Improvement**")
                if sw["weaknesses"]:
                    st.markdown(" ".join([f'<span class="weakness-pill">⚠ {w}</span>' for w in sw["weaknesses"]]), unsafe_allow_html=True)
                else:
                    st.markdown('<span class="strength-pill">No significant weaknesses</span>', unsafe_allow_html=True)

            with right:
                areas={"Education":float(row.get("S_edu",0)),"Experience":float(row.get("S_exp",0)),"Skills":float(row.get("S_skill",0)),"Knowledge":float(row.get("P_mcq",0)),"Problem\nSolving":float(row.get("P_desc",0)),"Coding":float(row.get("P_code",0))}
                st.pyplot(draw_radar(areas), use_container_width=True); plt.close()

                vc=match_color(css); vbg=match_bg(css)
                st.markdown(f"<div style='background:{vbg};border:1px solid {vc};border-radius:10px;padding:14px;text-align:center;margin-top:12px;'><div style='font-size:13px;color:#666;margin-bottom:4px;'>Overall Assessment</div><div style='font-size:28px;font-weight:700;color:{vc};'>{pct(css)}%</div><div style='font-size:13px;font-weight:600;color:{vc};margin-top:4px;'>{vd}</div><div style='font-size:13px;margin-top:6px;'>{stars(css)}</div></div>", unsafe_allow_html=True)

    if len(failed)>0:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander(f"⛔  {len(failed)} candidates did not meet the minimum requirements"):
            st.markdown("These candidates were screened out as they did not meet one or more minimum requirements. They will receive guidance on how to improve their profile.")
            for _, row in failed.head(20).iterrows():
                r = row.get("filter_fail_reason","").replace("edu_level","education level").replace("min_edu","minimum required").replace("S_skill","skill level").replace("P_code","coding ability").replace("threshold","minimum")
                st.markdown(f"• **{row['candidate_id']}** — {r}")

    return passed, role_df


# ── TAB 2: INSIGHTS ──────────────────────────────────────────────
def tab_insights(full_df, role, job, top_n, passed, role_df):
    dn=ROLE_DISPLAY_NAMES[role]; icon=ROLE_ICONS[role]
    st.markdown(f"<div class='section-header'>{icon} Candidate Insights — {dn}</div>", unsafe_allow_html=True)
    st.markdown("This section explains **why** each candidate received their score. Use this to prepare targeted interview questions or to give feedback.")

    if len(passed)==0:
        st.warning("No qualified candidates found."); return

    top = passed.head(top_n).copy()

    # What matters most for this role
    st.markdown("<div class='section-header'>What Matters Most for This Role</div>", unsafe_allow_html=True)
    cv_w=ROLE_CV_WEIGHTS[role]; int_w=ROLE_INTERVIEW_WEIGHTS[role]
    importance={"Technical Skills":cv_w["w_skill"]*0.40,"Practical Coding":int_w["w_code"]*0.60,"Problem Solving":int_w["w_desc"]*0.60,"Knowledge Test":int_w["w_mcq"]*0.60,"Work Experience":cv_w["w_exp"]*0.40,"Education":cv_w["w_edu"]*0.40}
    importance=dict(sorted(importance.items(),key=lambda x:x[1],reverse=True))

    fig,ax=plt.subplots(figsize=(9,3.5))
    fig.patch.set_facecolor("white"); ax.set_facecolor("#f8f9fa")
    lbls=list(importance.keys()); vals=[v*100 for v in importance.values()]
    colors=["#1e3a5f" if i==0 else "#2d6a9f" if i==1 else "#5b9bd5" for i in range(len(lbls))]
    bars=ax.barh(lbls[::-1],vals[::-1],color=colors[::-1],height=0.55,edgecolor="white")
    for bar,val in zip(bars,vals[::-1]):
        ax.text(bar.get_width()+0.3,bar.get_y()+bar.get_height()/2,f"{val:.0f}%",va="center",ha="left",fontsize=10,fontweight="bold",color="#333")
    ax.set_xlabel("Importance in Ranking (%)",fontsize=11,color="#555")
    ax.set_title(f"What Drives Rankings — {dn}",fontsize=13,fontweight="bold",color="#1e3a5f",pad=10)
    ax.set_xlim(0,40); ax.grid(axis="x",alpha=0.3)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True); plt.close()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>Why Each Candidate Was Ranked Here</div>", unsafe_allow_html=True)

    base={
        "Education":passed["S_edu"].mean(),"Work Experience":passed["S_exp"].mean(),
        "Technical Skills":passed["S_skill"].mean(),"Knowledge Test":passed["P_mcq"].mean(),
        "Problem Solving":passed["P_desc"].mean(),"Practical Coding":passed["P_code"].mean()
    }
    avg_css=passed["CSS"].mean()

    for _,row in top.iterrows():
        rank=int(row["rank"]); cid=row["candidate_id"]; css=float(row["CSS"]); vd=verdict(css)
        cscores={"Education":float(row.get("S_edu",0)),"Work Experience":float(row.get("S_exp",0)),"Technical Skills":float(row.get("S_skill",0)),"Knowledge Test":float(row.get("P_mcq",0)),"Problem Solving":float(row.get("P_desc",0)),"Practical Coding":float(row.get("P_code",0))}
        above=[(k,v) for k,v in cscores.items() if v>base[k]+0.05]; above.sort(key=lambda x:x[1],reverse=True)
        below=[(k,v) for k,v in cscores.items() if v<base[k]-0.05]; below.sort(key=lambda x:x[1])
        diff=pct(css)-pct(avg_css)
        diff_txt=f"{diff}% above average" if diff>=0 else f"{abs(diff)}% below average"

        with st.expander(f"#{rank} — {cid} | {pct(css)}% Match | {vd}"):
            st.markdown(f"**Overall Score: {pct(css)}%** ({diff_txt} for this role)")
            st.markdown("<br>", unsafe_allow_html=True)
            ca,cb=st.columns(2)
            with ca:
                st.markdown("##### 💪 Why This Candidate Scored Well")
                if above:
                    for area,val in above[:3]:
                        ab=pct(val)-pct(base[area])
                        st.markdown(f'<span class="strength-pill">✓ {area}: {pct(val)}% (+{ab}% vs average)</span>', unsafe_allow_html=True)
                else:
                    st.markdown("*Scored near average across all areas.*")
            with cb:
                st.markdown("##### ⚠ Areas That Held Them Back")
                if below:
                    for area,val in below[:3]:
                        bel=pct(base[area])-pct(val)
                        st.markdown(f'<span class="weakness-pill">⚠ {area}: {pct(val)}% (-{bel}% vs average)</span>', unsafe_allow_html=True)
                else:
                    st.markdown("*No significant weaknesses.*")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("##### How This Candidate Compares to the Average Applicant")
            al=list(cscores.keys()); cv=[pct(cscores[a]) for a in al]; av=[pct(base[a]) for a in al]
            x=np.arange(len(al)); fig,ax=plt.subplots(figsize=(9,3.2))
            fig.patch.set_facecolor("white"); ax.set_facecolor("#f8f9fa")
            b1=ax.bar(x-0.175,cv,0.35,label="This Candidate",color="#1e3a5f",alpha=0.85,edgecolor="white")
            b2=ax.bar(x+0.175,av,0.35,label="Average Applicant",color="#90caf9",alpha=0.85,edgecolor="white")
            ax.set_xticks(x); ax.set_xticklabels([a.replace(" ","\n") for a in al],fontsize=9)
            ax.set_ylabel("Score (%)",fontsize=10); ax.set_ylim(0,115)
            ax.legend(fontsize=9); ax.grid(axis="y",alpha=0.3)
            ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
            for bar in b1:
                ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+1,f"{int(bar.get_height())}%",ha="center",va="bottom",fontsize=8,color="#1e3a5f",fontweight="bold")
            plt.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close()

            st.markdown("##### 📋 Suggested Interview Focus Areas")
            tips={"Practical Coding":"Include a live coding exercise to verify programming ability.","Problem Solving":"Ask scenario-based questions to assess how they approach complex problems.","Knowledge Test":"Ask technical theory questions to verify domain knowledge.","Technical Skills":"Discuss specific technologies on the job description in depth.","Work Experience":"Ask them to describe past projects in detail.","Education":"Ask how their academic background relates to this role."}
            if below:
                for area,_ in below[:2]:
                    st.markdown(f"- **{area}:** {tips.get(area,'Probe this area further.')}")
            else:
                st.markdown("- This candidate is strong across all areas. Focus the interview on cultural fit and specific project experience.")


# ── TAB 3: COMPARISON ────────────────────────────────────────────
def tab_comparison(full_df, role, job, top_n, passed, role_df):
    dn=ROLE_DISPLAY_NAMES[role]; icon=ROLE_ICONS[role]
    st.markdown(f"<div class='section-header'>{icon} Side-by-Side Comparison — {dn}</div>", unsafe_allow_html=True)
    st.markdown("Compare all shortlisted candidates at a glance. All scores shown as percentages.")

    if len(passed)==0:
        st.warning("No qualified candidates to compare."); return

    top=passed.head(top_n).copy()
    merged=top.merge(role_df[["candidate_id","edu_level","years_experience"]],on="candidate_id",how="left")

    rows=[]
    for _,row in merged.iterrows():
        css=float(row["CSS"])
        rows.append({
            "Rank":f"#{int(row['rank'])}",
            "Candidate ID":row["candidate_id"],
            "Overall Match":f"{pct(css)}%",
            "Recommendation":verdict(css),
            "Education":edu_label(int(row["edu_level"])),
            "Experience":f"{float(row['years_experience']):.1f} yrs",
            "Tech Skills":f"{pct(float(row['S_skill']))}%",
            "Knowledge":f"{pct(float(row['P_mcq']))}%",
            "Problem Solving":f"{pct(float(row['P_desc']))}%",
            "Coding Ability":f"{pct(float(row['P_code']))}%",
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=min(600,50+len(rows)*38))
    st.markdown("<br>", unsafe_allow_html=True)

    # Heatmap
    st.markdown("<div class='section-header'>Score Heatmap — All Candidates at a Glance</div>", unsafe_allow_html=True)
    st.caption("🟢 Dark green = Excellent  |  🟡 Yellow = Average  |  🔴 Red = Needs Improvement")

    sc={"Overall\nMatch":"CSS","Tech\nSkills":"S_skill","Knowledge\nTest":"P_mcq","Problem\nSolving":"P_desc","Coding\nAbility":"P_code","Education":"S_edu","Experience":"S_exp"}
    hdata=[]; clbls=[]
    for _,row in top.head(20).iterrows():
        hdata.append([pct(float(row[v])) for v in sc.values()])
        clbls.append(f"#{int(row['rank'])} {row['candidate_id']}")
    hm=np.array(hdata,dtype=float)

    fig,ax=plt.subplots(figsize=(11,max(4,len(clbls)*0.45+1.2)))
    fig.patch.set_facecolor("white")
    im=ax.imshow(hm,cmap="RdYlGn",vmin=0,vmax=100,aspect="auto")
    ax.set_xticks(range(len(sc))); ax.set_xticklabels(list(sc.keys()),fontsize=10,fontweight="bold")
    ax.set_yticks(range(len(clbls))); ax.set_yticklabels(clbls,fontsize=9)
    for i in range(len(clbls)):
        for j in range(len(sc)):
            val=hm[i,j]; tc="white" if val<40 or val>75 else "black"
            ax.text(j,i,f"{int(val)}%",ha="center",va="center",fontsize=9,color=tc,fontweight="bold")
    plt.colorbar(im,ax=ax,label="Score (%)",shrink=0.8)
    ax.set_title(f"Candidate Comparison Heatmap — {dn}",fontsize=13,fontweight="bold",color="#1e3a5f",pad=12)
    plt.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close()

    # Top 3 summary
    st.markdown("<div class='section-header'>Recruitment Summary</div>", unsafe_allow_html=True)
    top3=passed.head(3); medals=["🥇 Top Pick","🥈 Second Choice","🥉 Third Choice"]
    if len(top3)>0:
        cols=st.columns(min(3,len(top3)))
        for i,(_,row) in enumerate(top3.iterrows()):
            css=float(row["CSS"]); vc=match_color(css); vbg=match_bg(css)
            with cols[i]:
                st.markdown(f"<div style='background:{vbg};border:1px solid {vc};border-radius:12px;padding:18px;text-align:center;'><div style='font-size:15px;font-weight:700;color:{vc};margin-bottom:8px;'>{medals[i]}</div><div style='font-size:20px;font-weight:700;color:#1e3a5f;'>{row['candidate_id']}</div><div style='font-size:28px;font-weight:700;color:{vc};margin:8px 0;'>{pct(css)}%</div><div style='font-size:13px;color:{vc};'>{verdict(css)}</div><div style='font-size:14px;margin-top:6px;'>{stars(css)}</div></div>", unsafe_allow_html=True)


# ── Main ─────────────────────────────────────────────────────────
def main():
    full_df=load_data()
    role,min_edu,min_exp,top_n=sidebar()
    job=make_profile(role,min_edu,min_exp)

    st.markdown("""
    <div class='top-header'>
      <h1>🎯 TalentRank — Smart Recruitment Platform</h1>
      <p>AI-powered candidate ranking for smarter, faster, and fairer hiring decisions.</p>
    </div>""", unsafe_allow_html=True)

    t1,t2,t3=st.tabs(["📋  Candidate Shortlist","💡  Candidate Insights","📊  Compare Candidates"])

    with t1:
        passed,role_df=tab_shortlist(full_df,role,job,top_n)
    with t2:
        tab_insights(full_df,role,job,top_n,passed,role_df)
    with t3:
        tab_comparison(full_df,role,job,top_n,passed,role_df)

if __name__=="__main__":
    main()