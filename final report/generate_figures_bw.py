import os
import matplotlib.pyplot as plt
import numpy as np

# Output directory for dissertation figures
fig_dir = os.path.join(os.path.dirname(__file__), "figures")
os.makedirs(fig_dir, exist_ok=True)

# Set global styles - STRICT MONOCHROME / GRAYSCALE
plt.style.use('default')
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Times']
plt.rcParams['font.size'] = 10
plt.rcParams['text.color'] = '#000000'
plt.rcParams['axes.labelcolor'] = '#000000'
plt.rcParams['xtick.color'] = '#000000'
plt.rcParams['ytick.color'] = '#000000'
plt.rcParams['axes.edgecolor'] = '#000000'

# -------------------------------------------------------------
# Figure 1: Pipeline Latency Breakdown
# -------------------------------------------------------------
stages = [
    "Section\nSegmentation\n(0.06ms)",
    "Entity & Feature\nExtraction\n(76.23ms)",
    "Role\nClassification\n(41.67ms)",
    "JD Spec\nExtraction\n(30.53ms)",
    "SBERT Semantic\nMatching\n(2.75ms)",
    "3-Pillar\nScoring\n(0.09ms)"
]
latencies = [0.06, 76.23, 41.67, 30.53, 2.75, 0.09]
grays = ['#EAEAEA', '#404040', '#707070', '#959595', '#C0C0C0', '#D5D5D5']
hatches = ['', '///', '\\\\\\', '...', 'xxx', '']

fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=300)
bars = ax.bar(stages, latencies, color=grays, edgecolor='black', linewidth=1.0, width=0.6, hatch=hatches)
ax.set_ylabel("Processing Latency (Milliseconds)", fontsize=11, fontweight='bold')
ax.set_title("Component 1 End-to-End Processing Latency Breakdown (Total: 151.35 ms)", fontsize=12, fontweight='bold', pad=12)
ax.set_ylim(0, 90)
ax.grid(axis='y', linestyle='--', alpha=0.5, color='#888888')

for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2.0, yval + 1.8, f"{yval:.2f} ms", ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "fig1_latency_breakdown.png"))
plt.close()

# -------------------------------------------------------------
# Figure 2: Permutation Feature Importance & Pillar Weights
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 4.2), dpi=300)

labels_imp = ['Skills Pillar\n(85.9%)', 'Education Pillar\n(11.8%)', 'Experience Pillar\n(2.3%)']
sizes_imp = [85.9, 11.8, 2.3]
colors_imp = ['#505050', '#A0A0A0', '#E5E5E5']
hatches_imp = ['///', '...', 'xxx']
explode_imp = (0.05, 0.05, 0.05)

wedges1, texts1, autotexts1 = ax1.pie(sizes_imp, explode=explode_imp, labels=labels_imp, colors=colors_imp, autopct='%1.1f%%',
                                     startangle=140, textprops={'fontsize': 9.5, 'weight': 'bold'},
                                     wedgeprops={'edgecolor': 'black', 'linewidth': 1.0})
for w, h in zip(wedges1, hatches_imp):
    w.set_hatch(h)
for at in autotexts1:
    at.set_color('black')
ax1.set_title("(a) Permutation Feature Importance", fontsize=11, fontweight='bold', pad=10)

labels_w = ['Technical Skills\n(w = 0.50)', 'Experience Tenure\n(w = 0.30)', 'Education Level\n(w = 0.20)']
sizes_w = [50, 30, 20]
colors_w = ['#505050', '#909090', '#D0D0D0']
hatches_w = ['///', '\\\\\\', '...']
explode_w = (0.05, 0.05, 0.05)

wedges2, texts2, autotexts2 = ax2.pie(sizes_w, explode=explode_w, labels=labels_w, colors=colors_w, autopct='%1.0f%%',
                                     startangle=140, textprops={'fontsize': 9.5, 'weight': 'bold'},
                                     wedgeprops={'edgecolor': 'black', 'linewidth': 1.0})
for w, h in zip(wedges2, hatches_w):
    w.set_hatch(h)
for at in autotexts2:
    at.set_color('black')
ax2.set_title("(b) Deployed 3-Pillar Qualification Weights", fontsize=11, fontweight='bold', pad=10)

plt.suptitle("Empirical Feature Contribution vs. Deployed 3-Pillar Weights (S_cv)", fontsize=12, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "fig2_feature_importance_weights.png"))
plt.close()

# -------------------------------------------------------------
# Figure 3: Model Architecture Benchmark Comparison
# -------------------------------------------------------------
models = ['Multinomial\nNaive Bayes', 'Random Forest\n(100 Trees)', 'LinearSVC\n(L2 SVM)', 'DistilBERT\n(Fine-Tuned)', 'Balanced LogReg\n(Proposed)']
accuracies = [76.20, 78.40, 89.12, 91.80, 87.42]
latencies_model = [1.2, 18.5, 2.1, 142.0, 2.4]

x = np.arange(len(models))
width = 0.35

fig, ax1 = plt.subplots(figsize=(9, 4.5), dpi=300)

ax1.set_ylabel('Classification Accuracy (%)', fontsize=11, fontweight='bold')
bars1 = ax1.bar(x - width/2, accuracies, width, label='Accuracy (%)', color='#555555', edgecolor='black', linewidth=1.0)
ax1.tick_params(axis='y')
ax1.set_ylim(60, 100)
ax1.grid(axis='y', linestyle='--', alpha=0.4, color='#888888')

for bar in bars1:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 0.8, f"{yval:.1f}%", ha='center', va='bottom', fontsize=8.5, fontweight='bold')

ax2 = ax1.twinx()
ax2.set_ylabel('Inference Latency (ms)', fontsize=11, fontweight='bold')
bars2 = ax2.bar(x + width/2, latencies_model, width, label='Latency (ms)', color='#D0D0D0', edgecolor='black', linewidth=1.0, hatch='///')
ax2.tick_params(axis='y')
ax2.set_ylim(0, 160)

for bar in bars2:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 2.5, f"{yval:.1f}ms", ha='center', va='bottom', fontsize=8.5, fontweight='bold')

ax1.set_xticks(x)
ax1.set_xticklabels(models, fontsize=9.5, fontweight='bold')
ax1.set_title("Model Architecture Comparison: Classification Accuracy vs. Inference Latency", fontsize=12, fontweight='bold', pad=12)

# Combined legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True, edgecolor='black')

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "fig3_model_benchmark_comparison.png"))
plt.close()

# -------------------------------------------------------------
# Figure 4: Per-Role F1-Score Across 20 Canonical IT Roles
# -------------------------------------------------------------
roles = [
    'Mobile App Dev', 'QA/Test Eng', 'UI/UX Designer', 'AI/NLP Eng', 'Systems Analyst',
    'Cybersecurity', 'Data Engineer', 'Embedded Sys', 'Full Stack Dev', 'DevOps Eng',
    'Cloud Architect', 'Network Eng', 'Site Reliability', 'Database Admin', 'Backend Dev',
    'Blockchain Dev', 'Data Scientist', 'Frontend Dev', 'Software Eng', 'IT Support'
]
f1_scores = [
    1.00, 1.00, 1.00, 0.98, 0.98,
    0.98, 0.98, 0.98, 0.95, 0.93,
    0.94, 0.94, 0.92, 0.89, 0.91,
    0.97, 0.70, 0.80, 0.71, 0.97
]

sorted_indices = np.argsort(f1_scores)
roles_sorted = [roles[i] for i in sorted_indices]
f1_sorted = [f1_scores[i] for i in sorted_indices]

fig, ax = plt.subplots(figsize=(9, 6.5), dpi=300)
y_pos = np.arange(len(roles_sorted))
colors_f1 = ['#303030' if f >= 0.95 else '#757575' if f >= 0.85 else '#C0C0C0' for f in f1_sorted]
hatches_f1 = ['' if f >= 0.95 else '///' if f >= 0.85 else '...' for f in f1_sorted]

bars = ax.barh(y_pos, f1_sorted, color=colors_f1, edgecolor='black', linewidth=0.8, height=0.65)
for b, h in zip(bars, hatches_f1):
    b.set_hatch(h)

ax.set_yticks(y_pos)
ax.set_yticklabels(roles_sorted, fontsize=9, fontweight='bold')
ax.set_xlabel("Held-Out Test Set F1-Score (N = 819)", fontsize=11, fontweight='bold')
ax.set_title("Empirical Classification Performance Across 20 Canonical IT Roles", fontsize=12, fontweight='bold', pad=12)
ax.set_xlim(0.5, 1.08)
ax.grid(axis='x', linestyle='--', alpha=0.5, color='#888888')

for bar in bars:
    xval = bar.get_width()
    ax.text(xval + 0.01, bar.get_y() + bar.get_height()/2.0, f"{xval:.2f}", ha='left', va='center', fontsize=8.5, fontweight='bold')

ax.axvline(0.9247, color='black', linestyle='--', linewidth=1.5, label='Macro F1 Average (0.9247)')
ax.legend(loc='lower right', frameon=True, edgecolor='black', fontsize=9.5)

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "fig4_per_role_f1_scores.png"))
plt.close()

# -------------------------------------------------------------
# Figure 5: Synthetic Benchmark Leakage vs. Real Corpus
# -------------------------------------------------------------
categories = ['Accuracy', 'Macro Precision', 'Macro Recall', 'Macro F1']
synthetic_scores = [100.0, 100.0, 100.0, 100.0]
real_scores = [87.42, 91.35, 94.35, 92.47]

x = np.arange(len(categories))
width = 0.35

fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=300)
b1 = ax.bar(x - width/2, synthetic_scores, width, label='Synthetic Corpus (Template Memorization Leakage)', color='#D8D8D8', edgecolor='black', linewidth=1.0, hatch='///')
b2 = ax.bar(x + width/2, real_scores, width, label='Real Held-Out Corpus (Leakage-Free Train Split)', color='#404040', edgecolor='black', linewidth=1.0)

ax.set_ylabel("Score (%)", fontsize=11, fontweight='bold')
ax.set_title("Forensic Evaluation: Artificial Synthetic Leakage vs. Genuine Real-World Evaluation", fontsize=11.5, fontweight='bold', pad=12)
ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=10, fontweight='bold')
ax.set_ylim(70, 110)
ax.grid(axis='y', linestyle='--', alpha=0.5, color='#888888')
ax.legend(loc='upper right', frameon=True, edgecolor='black', fontsize=9.5)

for b in b1:
    y = b.get_height()
    ax.text(b.get_x() + b.get_width()/2, y + 1.2, f"{y:.1f}%", ha='center', va='bottom', fontsize=8.5, fontweight='bold')
for b in b2:
    y = b.get_height()
    ax.text(b.get_x() + b.get_width()/2, y + 1.2, f"{y:.2f}%", ha='center', va='bottom', fontsize=8.5, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "fig5_synthetic_leakage_audit.png"))
plt.close()

# -------------------------------------------------------------
# Figure 6: RecruitAI Macro Architecture
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5.2), dpi=300)
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.axis('off')

# Grayscale Boxes
c1_box = plt.Rectangle((0.5, 3.2), 4.0, 2.2, facecolor='#F5F5F5', edgecolor='black', linewidth=1.8, linestyle='solid')
c2_box = plt.Rectangle((5.5, 3.2), 4.0, 2.2, facecolor='#F5F5F5', edgecolor='black', linewidth=1.8, linestyle='solid')
c3_box = plt.Rectangle((0.5, 0.5), 4.0, 2.0, facecolor='#F5F5F5', edgecolor='black', linewidth=1.8, linestyle='solid')
c4_box = plt.Rectangle((5.5, 0.5), 4.0, 2.0, facecolor='#F5F5F5', edgecolor='black', linewidth=1.8, linestyle='solid')

ax.add_patch(c1_box)
ax.add_patch(c2_box)
ax.add_patch(c3_box)
ax.add_patch(c4_box)

ax.text(2.5, 5.0, "Component 1 (D. T. D. Perera - IT22089236)\nResume Screening & Role Classification\n(FastAPI Port 8001)", ha='center', va='center', fontsize=9.0, fontweight='bold', color='black')
ax.text(2.5, 3.9, "• Boundary-Guarded NER (400+ Skills)\n• Lebesgue Interval Union Algebra\n• Decoupled 2D Academic Matrix\n• Balanced 20-Role LogReg (83.0% Acc)", ha='center', va='center', fontsize=7.8, color='#333333')

ax.text(7.5, 5.0, "Component 2 (Yenura S. Karunanayaka - IT22306272)\nAutonomous Technical Interview Evaluation\n(FastAPI Port 8002)", ha='center', va='center', fontsize=9.0, fontweight='bold', color='black')
ax.text(7.5, 3.9, "• OpenAI Whisper STT (7.8% WER)\n• SBERT Dense Cosine Rubric Grading\n• Sandboxed AST Python Execution\n• Objective Multi-Modal Scoring", ha='center', va='center', fontsize=7.8, color='#333333')

ax.text(2.5, 1.8, "Component 3 (K. G. Savinda N. Perera - IT22027610)\nCandidate Suitability & Listwise Ranking\n(FastAPI Port 8003)", ha='center', va='center', fontsize=9.0, fontweight='bold', color='black')
ax.text(2.5, 1.0, "• Multi-Attribute Utility Theory (MAUT)\n• Non-Compensatory Prerequisite Gating\n• LambdaMART Learning-to-Rank (NDCG=0.892)\n• Adverse Impact Ratio Parity Audits", ha='center', va='center', fontsize=7.8, color='#333333')

ax.text(7.5, 1.8, "Component 4 (K. G. Savinda N. Perera - IT22027610)\nSkill Gap Diagnostics & Career Pathfinding\n(FastAPI Port 8004)", ha='center', va='center', fontsize=9.0, fontweight='bold', color='black')
ax.text(7.5, 1.0, "• 67-Feature GBDT Hireability Model\n• Dijkstra Shortest-Path DAG Lattice\n• Dynamic Paced Learning Roadmaps\n• Curated Curriculum Recommendations", ha='center', va='center', fontsize=7.8, color='#333333')

# Arrows in black
ax.annotate("", xy=(2.5, 2.5), xytext=(2.5, 3.2), arrowprops=dict(arrowstyle="->", lw=1.8, color='black'))
ax.text(2.6, 2.85, "Vector [S_skill, S_exp, S_edu]", fontsize=8, color='black', fontweight='bold')

ax.annotate("", xy=(6.5, 2.5), xytext=(6.5, 3.2), arrowprops=dict(arrowstyle="->", lw=1.8, color='black'))
ax.text(6.6, 2.85, "Interview Performance Scores", fontsize=8, color='black', fontweight='bold')

ax.annotate("", xy=(5.5, 1.5), xytext=(4.5, 1.5), arrowprops=dict(arrowstyle="<->", lw=1.8, color='black'))
ax.text(5.0, 1.65, "Sync", ha='center', fontsize=8, color='black', fontweight='bold')

ax.annotate("", xy=(5.5, 4.3), xytext=(4.5, 4.3), arrowprops=dict(arrowstyle="->", lw=1.8, color='black'))
ax.text(5.0, 4.45, "Extracted Profile", ha='center', fontsize=8, color='black', fontweight='bold')

plt.title("Figure 1.1: Multi-Microservice Architecture of the RecruitAI Ecosystem (R26-IT-148)", fontsize=11, fontweight='bold', pad=10)
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "fig6_macro_architecture.png"))
plt.close()

# -------------------------------------------------------------
# Figure 7: Temporal Algebra & Interval Merging
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 4.2), dpi=300)

y_naive = [3.2, 2.6]
labels_naive = ["Job A: Jan 2021 - Dec 2022 (24 mo)", "Job B: Jan 2022 - Dec 2022 (12 mo)"]
starts = [2021.0, 2022.0]
durations = [2.0, 1.0]
colors_bars = ['#888888', '#B0B0B0']
hatches_bars = ['///', '...']

for i in range(2):
    ax.barh(y_naive[i], durations[i], left=starts[i], height=0.4, color=colors_bars[i], edgecolor='black', linewidth=1.0, hatch=hatches_bars[i])
    ax.text(starts[i] + durations[i]/2, y_naive[i], labels_naive[i], ha='center', va='center', fontsize=8, color='black', fontweight='bold')

ax.text(2020.8, 3.7, "Candidate Concurrent Employment Records:", fontsize=9.5, fontweight='bold', color='black')
ax.text(2023.2, 2.9, "Naive Summation: 24 + 12 = 36 mo (3.0 yrs)\n[+50% Tenure Inflation Error]", fontsize=8.5, fontweight='bold', color='black')

# Dedup
y_dedup = 1.0
ax.barh(y_dedup, 2.0, left=2021.0, height=0.5, color='#444444', edgecolor='black', linewidth=1.5)
ax.text(2022.0, y_dedup, "Unified Deduplicated Interval: [Jan 2021, Dec 2022] = 24 Months (2.0 Years)", ha='center', va='center', fontsize=8.5, color='white', fontweight='bold')
ax.text(2020.8, 1.6, "Component 1 Temporal Interval Union Algebra:", fontsize=9.5, fontweight='bold', color='black')
ax.text(2023.2, 1.0, "True Commercial Tenure = 2.0 yrs\n[Zero Inflation Guaranteed]", fontsize=8.5, fontweight='bold', color='black')

ax.set_xlim(2020.5, 2024.2)
ax.set_ylim(0.4, 4.2)
ax.set_yticks([])
ax.set_xticks([2021.0, 2022.0, 2023.0])
ax.set_xticklabels(["Jan 2021", "Jan 2022", "Jan 2023"], fontsize=9.5, fontweight='bold')
ax.set_xlabel("Calendar Timeline", fontsize=10, fontweight='bold')
ax.set_title("Temporal Experience Disambiguation: Concurrent Employment Interval Merging", fontsize=11, fontweight='bold', pad=10)

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "fig7_temporal_algebra.png"))
plt.close()

# -------------------------------------------------------------
# Figure 8: Polysemy Shielding Mechanism
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 4.0), dpi=300)
ax.axis('off')

txt_input = 'Input Resume Sentence: "The candidate will go to the branch, rest after sprint reviews, and write high-grade C code."'
box_input = plt.Rectangle((0.02, 0.72), 0.96, 0.22, facecolor='#F5F5F5', edgecolor='black', linewidth=1.2)
ax.add_patch(box_input)
ax.text(0.04, 0.83, txt_input, fontsize=8.5, style='italic', color='black')

box_naive = plt.Rectangle((0.02, 0.38), 0.45, 0.28, facecolor='#EAEAEA', edgecolor='black', linewidth=1.2)
ax.add_patch(box_naive)
ax.text(0.245, 0.60, "Naive Substring Tokenizer", ha='center', fontsize=9, fontweight='bold', color='black')
ax.text(0.245, 0.48, "• 'go' -> Go Programming Language\n• 'rest' -> RESTful Web Services\n• 'C' -> C Systems Language\nFalse Positives: 3 Spurious Skills", ha='center', fontsize=7.8, color='#333333')

box_shield = plt.Rectangle((0.53, 0.38), 0.45, 0.28, facecolor='#FFFFFF', edgecolor='black', linewidth=1.5)
ax.add_patch(box_shield)
ax.text(0.755, 0.60, "Component 1 Context-Guarded Shield", ha='center', fontsize=9, fontweight='bold', color='black')
ax.text(0.755, 0.48, "• Look-around: `(?<=[\\s,;(])C(?=[\\s,;)/+])`\n• Negative assertions: `(?!to|ahead|for)`\n• Phrase guards: `\\b(RESTful|REST API)\\b`\nResult: 0 Spurious False Positives", ha='center', fontsize=7.8, color='#333333')

ax.text(0.5, 0.15, "Figure 3.1: Context-Guarded Regex Look-Around Shielding vs. Naive Substring Tokenizers", ha='center', fontsize=9.5, fontweight='bold', color='black')

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "fig8_polysemy_shield.png"))
plt.close()

# -------------------------------------------------------------
# Figure 9: Integrated Candidate Lifecycle Flow
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 4.8), dpi=300)
ax.axis('off')

stage_boxes = [
    ("Stage 1: Document Intake", "• PDF / DOCX Ingestion\n• Automated PII Blinding\n• Layout-Aware Line Slicing", "#FFFFFF", "black", 0.02),
    ("Stage 2: Semantic Screening", "• Boundary-Guarded NER\n• Temporal Interval Algebra\n• Decoupled 2D Education\n• Tri-Pillar: S_skill, S_exp, S_edu", "#F0F0F0", "black", 0.22),
    ("Stage 3: Multi-Modal Interview", "• RAIGS Dynamic Q-Bank\n• Whisper STT (7.2% WER)\n• SBERT Rubric (r=0.884)\n• AST Python Sandbox Code", "#E0E0E0", "black", 0.42),
    ("Stage 4: Suitability Ranking", "• Prerequisite Soft Gating\n• Linear CSS (0.4 CV + 0.6 Int)\n• LambdaMART Comparator\n• Demographic Parity Auditing", "#D0D0D0", "black", 0.62),
    ("Stage 5: Skill Gap & Roadmap", "• 67-Feature GBDT Ensemble\n• Paced Roadmap (2 skills/mo)\n• 47 Curated Courses\n• DAG Career Mobility Lattice", "#C0C0C0", "black", 0.82)
]

for title, body, bg, border, x in stage_boxes:
    rect = plt.Rectangle((x, 0.18), 0.16, 0.68, facecolor=bg, edgecolor=border, linewidth=1.5)
    ax.add_patch(rect)
    ax.text(x + 0.08, 0.78, title, ha='center', va='center', fontsize=8.2, fontweight='bold', color='black')
    ax.text(x + 0.08, 0.45, body, ha='center', va='center', fontsize=7.2, color='#222222')

for i in range(4):
    x_start = stage_boxes[i][4] + 0.16
    x_end = stage_boxes[i+1][4]
    ax.annotate('', xy=(x_end, 0.52), xytext=(x_start, 0.52),
                arrowprops=dict(arrowstyle="->", color="black", lw=1.8))

ax.text(0.70, 0.08, "Advancing: High Suitability -> Final Technical Offer", ha='center', fontsize=8.0, fontweight='bold', color='black')
ax.text(0.70, 0.03, "Unshortlisted / Gapped -> Diversion into Component 4 Remedial Roadmap", ha='center', fontsize=8.0, fontweight='bold', color='black')

ax.set_title("Figure 4.1: End-to-End RecruitAI Candidate Lifecycle and Analytical State Flow", fontsize=11, fontweight='bold', pad=12, color='black')

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "fig9_integrated_lifecycle_flow.png"))
plt.close()

# -------------------------------------------------------------
# Figure 10: Cross-Component Empirical Benchmark Overview
# -------------------------------------------------------------
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(10, 6.5), dpi=300)

models_c1 = ['Naive\nBayes', 'Random\nForest', 'Linear\nSVC', 'Proposed\nLogReg', 'DistilBERT']
accs_c1 = [76.20, 78.40, 89.12, 87.42, 91.80]
cols_c1 = ['#E0E0E0', '#D0D0D0', '#B0B0B0', '#404040', '#808080']
ax1.bar(models_c1, accs_c1, color=cols_c1, edgecolor='black', linewidth=1.0, width=0.55)
ax1.set_ylabel("Accuracy (%)", fontsize=8.5, fontweight='bold')
ax1.set_title("(a) Component 1: Role Classification Accuracy (N=819)", fontsize=9.5, fontweight='bold')
ax1.set_ylim(60, 100)
ax1.grid(axis='y', linestyle='--', alpha=0.4, color='#888888')
for i, v in enumerate(accs_c1):
    ax1.text(i, v + 0.8, f"{v:.1f}%", ha='center', fontsize=7.5, fontweight='bold')

models_c2 = ['TF-IDF\nCosine', 'Okapi\nBM25', 'USE\nEncoder', 'BERT\nBase', 'Proposed\nSBERT']
corr_c2 = [0.612, 0.635, 0.742, 0.789, 0.884]
cols_c2 = ['#E0E0E0', '#D0D0D0', '#B0B0B0', '#909090', '#404040']
ax2.bar(models_c2, corr_c2, color=cols_c2, edgecolor='black', linewidth=1.0, width=0.55)
ax2.set_ylabel("Human Correlation (r)", fontsize=8.5, fontweight='bold')
ax2.set_title("(b) Component 2: Answer Scoring vs Human Rubric", fontsize=9.5, fontweight='bold')
ax2.set_ylim(0.4, 1.0)
ax2.grid(axis='y', linestyle='--', alpha=0.4, color='#888888')
for i, v in enumerate(corr_c2):
    ax2.text(i, v + 0.015, f"{v:.3f}", ha='center', fontsize=7.5, fontweight='bold')

models_c3 = ['Single\nCV', 'Single\nInterview', 'AHP /\nTOPSIS', 'Proposed\nCSS', 'LambdaMART\nComparator']
ndcg_c3 = [0.812, 0.841, 0.879, 0.9437, 0.9473]
cols_c3 = ['#E0E0E0', '#D0D0D0', '#B0B0B0', '#404040', '#707070']
ax3.bar(models_c3, ndcg_c3, color=cols_c3, edgecolor='black', linewidth=1.0, width=0.55)
ax3.set_ylabel("NDCG@5 Metric", fontsize=8.5, fontweight='bold')
ax3.set_title("(c) Component 3: Candidate Listwise Ranking Fidelity", fontsize=9.5, fontweight='bold')
ax3.set_ylim(0.7, 1.0)
ax3.grid(axis='y', linestyle='--', alpha=0.4, color='#888888')
for i, v in enumerate(ndcg_c3):
    ax3.text(i, v + 0.007, f"{v:.3f}", ha='center', fontsize=7.5, fontweight='bold')

models_c4 = ['Logistic\nRegression', 'Random\nForest', 'Proposed\nGBDT 300T']
auc_c4 = [0.9245, 0.9512, 0.9763]
cols_c4 = ['#E0E0E0', '#B0B0B0', '#404040']
ax4.bar(models_c4, auc_c4, color=cols_c4, edgecolor='black', linewidth=1.0, width=0.45)
ax4.set_ylabel("ROC-AUC Score", fontsize=8.5, fontweight='bold')
ax4.set_title("(d) Component 4: Hireability Classification ROC-AUC", fontsize=9.5, fontweight='bold')
ax4.set_ylim(0.85, 1.0)
ax4.grid(axis='y', linestyle='--', alpha=0.4, color='#888888')
for i, v in enumerate(auc_c4):
    ax4.text(i, v + 0.003, f"{v:.4f}", ha='center', fontsize=7.5, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "fig10_cross_component_benchmarks.png"))
plt.close()

print("All black-and-white dissertation figures generated successfully.")
