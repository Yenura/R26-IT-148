import os
import matplotlib.pyplot as plt
import numpy as np

# Output directory for dissertation figures
fig_dir = os.path.join(os.path.dirname(__file__), "figures")
os.makedirs(fig_dir, exist_ok=True)

# Set global styles
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10

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
colors = ['#2b5c8f', '#1f77b4', '#3895d3', '#58b4f5', '#8ed2ff', '#2ca02c']

fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=300)
bars = ax.bar(stages, latencies, color=colors, edgecolor='black', linewidth=0.8, width=0.6)
ax.set_ylabel("Processing Latency (Milliseconds)", fontsize=11, fontweight='bold')
ax.set_title("Component 1 End-to-End Processing Latency Breakdown (Total: 151.35 ms)", fontsize=12, fontweight='bold', pad=12)
ax.set_ylim(0, 90)

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

# Feature Importance
labels_imp = ['Skills Pillar\n(85.9%)', 'Education Pillar\n(11.8%)', 'Experience Pillar\n(2.3%)']
sizes_imp = [85.9, 11.8, 2.3]
colors_imp = ['#1f77b4', '#ff7f0e', '#2ca02c']
explode_imp = (0.05, 0.05, 0.05)

ax1.pie(sizes_imp, explode=explode_imp, labels=labels_imp, colors=colors_imp, autopct='%1.1f%%',
        shadow=True, startangle=140, textprops={'fontsize': 10, 'weight': 'bold'})
ax1.set_title("(a) Permutation Feature Importance", fontsize=11, fontweight='bold', pad=10)

# Deployed 3-Pillar Scoring Weights
labels_w = ['Technical Skills\n(w = 0.50)', 'Experience Tenure\n(w = 0.30)', 'Education Level\n(w = 0.20)']
sizes_w = [50, 30, 20]
colors_w = ['#1f77b4', '#2ca02c', '#ff7f0e']
explode_w = (0.05, 0.05, 0.05)

ax2.pie(sizes_w, explode=explode_w, labels=labels_w, colors=colors_w, autopct='%1.0f%%',
        shadow=True, startangle=140, textprops={'fontsize': 10, 'weight': 'bold'})
ax2.set_title("(b) Deployed 3-Pillar Qualification Weights", fontsize=11, fontweight='bold', pad=10)

plt.suptitle("Empirical Feature Contribution vs. Deployed 3-Pillar Weights ($S_{cv}$)", fontsize=13, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "fig2_feature_importance_weights.png"))
plt.close()

# -------------------------------------------------------------
# Figure 3: Model Architecture Benchmark Comparison
# -------------------------------------------------------------
models = ['Multinomial\nNaive Bayes', 'Random Forest\n(100 Trees)', 'LinearSVC\n(L2 SVM)', 'DistilBERT\n(Fine-Tuned)', 'Balanced LogReg\n(Proposed)']
accuracies = [76.20, 78.40, 89.12, 91.80, 90.49]
latencies_model = [1.2, 18.5, 2.1, 142.0, 2.4]

x = np.arange(len(models))
width = 0.35

fig, ax1 = plt.subplots(figsize=(9, 4.5), dpi=300)

color = '#1f77b4'
ax1.set_ylabel('Classification Accuracy (%)', color=color, fontsize=11, fontweight='bold')
bars1 = ax1.bar(x - width/2, accuracies, width, label='Accuracy (%)', color=color, edgecolor='black', linewidth=0.8)
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_ylim(60, 100)

for bar in bars1:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 0.8, f"{yval:.1f}%", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color=color)

ax2 = ax1.twinx()
color = '#d62728'
ax2.set_ylabel('Inference Latency (ms)', color=color, fontsize=11, fontweight='bold')
bars2 = ax2.bar(x + width/2, latencies_model, width, label='Latency (ms)', color=color, edgecolor='black', linewidth=0.8, alpha=0.85)
ax2.tick_params(axis='y', labelcolor=color)
ax2.set_ylim(0, 160)

for bar in bars2:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 2.5, f"{yval:.1f}ms", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color=color)

ax1.set_xticks(x)
ax1.set_xticklabels(models, fontsize=9.5, fontweight='bold')
ax1.set_title("Model Architecture Comparison: Classification Accuracy vs. Inference Latency", fontsize=12, fontweight='bold', pad=12)

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

# Sort by F1
sorted_indices = np.argsort(f1_scores)
roles_sorted = [roles[i] for i in sorted_indices]
f1_sorted = [f1_scores[i] for i in sorted_indices]

fig, ax = plt.subplots(figsize=(9, 6.5), dpi=300)
y_pos = np.arange(len(roles_sorted))
colors_f1 = ['#2ca02c' if f >= 0.95 else '#1f77b4' if f >= 0.85 else '#ff7f0e' for f in f1_sorted]

bars = ax.barh(y_pos, f1_sorted, color=colors_f1, edgecolor='black', linewidth=0.6, height=0.65)
ax.set_yticks(y_pos)
ax.set_yticklabels(roles_sorted, fontsize=9, fontweight='bold')
ax.set_xlabel("Held-Out Test Set $F_1$-Score ($N=819$)", fontsize=11, fontweight='bold')
ax.set_title("Empirical Classification Performance Across 20 Canonical IT Roles", fontsize=12, fontweight='bold', pad=12)
ax.set_xlim(0.5, 1.05)

for bar in bars:
    xval = bar.get_width()
    ax.text(xval + 0.01, bar.get_y() + bar.get_height()/2.0, f"{xval:.2f}", ha='left', va='center', fontsize=8.5, fontweight='bold')

ax.axvline(0.9156, color='red', linestyle='--', linewidth=1.2, label='Macro F1 Average (0.9156)')
ax.legend(loc='lower right', frameon=True, fontsize=10)

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
b1 = ax.bar(x - width/2, synthetic_scores, width, label='Synthetic Corpus (Template Memorization Leakage)', color='#d62728', edgecolor='black', linewidth=0.8, alpha=0.8)
b2 = ax.bar(x + width/2, real_scores, width, label='Real Held-Out Corpus (Leakage-Free Train Split)', color='#2ca02c', edgecolor='black', linewidth=0.8)

ax.set_ylabel("Score (%)", fontsize=11, fontweight='bold')
ax.set_title("Forensic Evaluation: Artificial Synthetic Leakage vs. Genuine Real-World Evaluation", fontsize=11.5, fontweight='bold', pad=12)
ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=10, fontweight='bold')
ax.set_ylim(70, 108)
ax.legend(loc='upper right', frameon=True, fontsize=9.5)

for b in b1:
    y = b.get_height()
    ax.text(b.get_x() + b.get_width()/2, y + 1.2, f"{y:.1f}%", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#a01e1e')
for b in b2:
    y = b.get_height()
    ax.text(b.get_x() + b.get_width()/2, y + 1.2, f"{y:.2f}%", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#1e7e1e')

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

# Boxes
c1_box = plt.Rectangle((0.5, 3.2), 4.0, 2.2, facecolor='#ebf8ff', edgecolor='#2b6cb0', linewidth=2, linestyle='solid')
c2_box = plt.Rectangle((5.5, 3.2), 4.0, 2.2, facecolor='#f0fff4', edgecolor='#2f855a', linewidth=2, linestyle='solid')
c3_box = plt.Rectangle((0.5, 0.5), 4.0, 2.0, facecolor='#fffaf0', edgecolor='#c05621', linewidth=2, linestyle='solid')
c4_box = plt.Rectangle((5.5, 0.5), 4.0, 2.0, facecolor='#faf5ff', edgecolor='#6b46c1', linewidth=2, linestyle='solid')

ax.add_patch(c1_box)
ax.add_patch(c2_box)
ax.add_patch(c3_box)
ax.add_patch(c4_box)

# Texts
ax.text(2.5, 5.0, "Component 1 (D. T. D. Perera - IT22089236)\nResume Screening & Role Classification\n(FastAPI Port 8001)", ha='center', va='center', fontsize=9.0, fontweight='bold', color='#1a365d')
ax.text(2.5, 3.9, "• Boundary-Guarded NER (400+ Skills)\n• Lebesgue Interval Union Algebra\n• Decoupled 2D Academic Matrix\n• Balanced 20-Role LogReg (83.0% Acc)", ha='center', va='center', fontsize=7.8, color='#2d3748')

ax.text(7.5, 5.0, "Component 2 (Yenura S. Karunanayaka - IT22306272)\nAutonomous Technical Interview Evaluation\n(FastAPI Port 8002)", ha='center', va='center', fontsize=9.0, fontweight='bold', color='#22543d')
ax.text(7.5, 3.9, "• OpenAI Whisper STT (7.8% WER)\n• SBERT Dense Cosine Rubric Grading\n• Sandboxed AST Python Execution\n• Objective Multi-Modal Scoring", ha='center', va='center', fontsize=7.8, color='#2d3748')

ax.text(2.5, 1.8, "Component 3 (K. G. Savinda N. Perera - IT22027610)\nCandidate Suitability & Listwise Ranking\n(FastAPI Port 8003)", ha='center', va='center', fontsize=9.0, fontweight='bold', color='#7b341e')
ax.text(2.5, 1.0, "• Multi-Attribute Utility Theory (MAUT)\n• Non-Compensatory Prerequisite Gating\n• LambdaMART Learning-to-Rank (NDCG=0.892)\n• Adverse Impact Ratio Parity Audits", ha='center', va='center', fontsize=7.8, color='#2d3748')

ax.text(7.5, 1.8, "Component 4 (K. G. Savinda N. Perera - IT22027610)\nSkill Gap Diagnostics & Career Pathfinding\n(FastAPI Port 8004)", ha='center', va='center', fontsize=9.0, fontweight='bold', color='#44337a')
ax.text(7.5, 1.0, "• 67-Feature GBDT Hireability Model\n• Dijkstra Shortest-Path DAG Lattice\n• Dynamic Paced Learning Roadmaps\n• Curated Curriculum Recommendations", ha='center', va='center', fontsize=7.8, color='#2d3748')

# Arrows
ax.annotate("", xy=(2.5, 2.5), xytext=(2.5, 3.2), arrowprops=dict(arrowstyle="->", lw=2, color='#2b6cb0'))
ax.text(2.6, 2.85, "Vector [S_skill, S_exp, S_edu]", fontsize=8, color='#2b6cb0', fontweight='bold')

ax.annotate("", xy=(6.5, 2.5), xytext=(6.5, 3.2), arrowprops=dict(arrowstyle="->", lw=2, color='#2f855a'))
ax.text(6.6, 2.85, "Interview Performance Scores", fontsize=8, color='#2f855a', fontweight='bold')

ax.annotate("", xy=(5.5, 1.5), xytext=(4.5, 1.5), arrowprops=dict(arrowstyle="<->", lw=2, color='#4a5568'))
ax.text(5.0, 1.65, "Sync", ha='center', fontsize=8, color='#4a5568', fontweight='bold')

ax.annotate("", xy=(5.5, 4.3), xytext=(4.5, 4.3), arrowprops=dict(arrowstyle="->", lw=2, color='#2b6cb0'))
ax.text(5.0, 4.45, "Extracted Profile", ha='center', fontsize=8, color='#2b6cb0', fontweight='bold')

plt.title("Figure 3.1: High-Level Microservice Architecture of the RecruitAI Ecosystem (R26-IT-148)", fontsize=11, fontweight='bold', pad=10)
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "fig6_macro_architecture.png"))
plt.close()

# -------------------------------------------------------------
# Figure 7: Temporal Algebra & Interval Merging
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 4.2), dpi=300)

y_naive = [3.2, 2.6]
labels_naive = ["Job A: Jan 2021 – Dec 2022 (24 mo)", "Job B: Jan 2022 – Dec 2022 (12 mo)"]
starts = [2021.0, 2022.0]
durations = [2.0, 1.0]
colors_bars = ['#3182ce', '#63b3ed']

for i in range(2):
    ax.barh(y_naive[i], durations[i], left=starts[i], height=0.4, color=colors_bars[i], edgecolor='black', linewidth=0.8)
    ax.text(starts[i] + durations[i]/2, y_naive[i], labels_naive[i], ha='center', va='center', fontsize=8, color='white', fontweight='bold')

ax.text(2020.8, 3.7, "Candidate Concurrent Employment Records:", fontsize=9.5, fontweight='bold', color='#2d3748')
ax.text(2023.2, 2.9, "Naive Summation: 24 + 12 = 36 mo (3.0 yrs)\n[+50% Tenure Inflation Error]", fontsize=8.5, fontweight='bold', color='#c53030')

# Dedup
y_dedup = 1.0
ax.barh(y_dedup, 2.0, left=2021.0, height=0.5, color='#38a169', edgecolor='black', linewidth=1.2)
ax.text(2022.0, y_dedup, "Unified Deduplicated Interval: [Jan 2021, Dec 2022] = 24 Months (2.0 Years)", ha='center', va='center', fontsize=8.5, color='white', fontweight='bold')
ax.text(2020.8, 1.6, "Component 1 Temporal Interval Union Algebra:", fontsize=9.5, fontweight='bold', color='#22543d')
ax.text(2023.2, 1.0, "True Commercial Tenure = 2.0 yrs\n[Zero Inflation Guaranteed]", fontsize=8.5, fontweight='bold', color='#22543d')

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

# Text box illustration
txt_input = 'Input Resume Sentence: "The candidate will go to the branch, rest after sprint reviews, and write high-grade C code."'
box_input = plt.Rectangle((0.02, 0.72), 0.96, 0.22, facecolor='#edf2f7', edgecolor='#4a5568', linewidth=1.2)
ax.add_patch(box_input)
ax.text(0.04, 0.83, txt_input, fontsize=8.5, style='italic', color='#1a202c')

# Naive extraction box
box_naive = plt.Rectangle((0.02, 0.38), 0.45, 0.28, facecolor='#fff5f5', edgecolor='#e53e3e', linewidth=1.2)
ax.add_patch(box_naive)
ax.text(0.245, 0.60, "Naive Substring Tokenizer", ha='center', fontsize=9, fontweight='bold', color='#c53030')
ax.text(0.245, 0.48, "• 'go' -> Go Programming Language\n• 'rest' -> RESTful Web Services\n• 'C' -> C Systems Language\nFalse Positives: 3 Spurious Skills", ha='center', fontsize=7.8, color='#742a2a')

# Shielded extraction box
box_shield = plt.Rectangle((0.53, 0.38), 0.45, 0.28, facecolor='#f0fff4', edgecolor='#38a169', linewidth=1.2)
ax.add_patch(box_shield)
ax.text(0.755, 0.60, "Component 1 Context-Guarded Shield", ha='center', fontsize=9, fontweight='bold', color='#22543d')
ax.text(0.755, 0.48, "• Look-around: `(?<=[\\s,;(])C(?=[\\s,;)/+])`\n• Negative assertions: `(?!to|ahead|for)`\n• Phrase guards: `\\b(RESTful|REST API)\\b`\nResult: 0 Spurious False Positives", ha='center', fontsize=7.8, color='#22543d')

# Footer
ax.text(0.5, 0.15, "Figure 3.4: Context-Guarded Regex Look-Around Shielding vs. Naive Substring Tokenizers", ha='center', fontsize=9.5, fontweight='bold', color='#1a365d')

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "fig8_polysemy_shield.png"))
plt.close()

# -------------------------------------------------------------
# Figure 9: Integrated Candidate Lifecycle Flow
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 4.8), dpi=300)
ax.axis('off')

# Stages
stage_boxes = [
    ("Stage 1: Document Intake", "• PDF / DOCX Ingestion\n• Automated PII Blinding\n• Layout-Aware Line Slicing", "#ebf8ff", "#2b6cb0", 0.02),
    ("Stage 2: Semantic Screening", "• Boundary-Guarded NER\n• Temporal Interval Algebra\n• Decoupled 2D Education\n• Tri-Pillar: S_skill, S_exp, S_edu", "#e6fffa", "#234e52", 0.22),
    ("Stage 3: Multi-Modal Interview", "• RAIGS Dynamic Q-Bank\n• Whisper STT (7.2% WER)\n• SBERT Rubric (r=0.884)\n• AST Python Sandbox Code", "#faf5ff", "#553c9e", 0.42),
    ("Stage 4: Suitability Ranking", "• Prerequisite Soft Gating\n• Linear CSS (0.4 CV + 0.6 Int)\n• LambdaMART Comparator\n• Demographic Parity Auditing", "#fffaf0", "#7b341e", 0.62),
    ("Stage 5: Skill Gap & Roadmap", "• 67-Feature GBDT Ensemble\n• Paced Roadmap (2 skills/mo)\n• 47 Curated Courses\n• DAG Career Mobility Lattice", "#f0fff4", "#22543d", 0.82)
]

for title, body, bg, border, x in stage_boxes:
    rect = plt.Rectangle((x, 0.18), 0.16, 0.68, facecolor=bg, edgecolor=border, linewidth=1.5)
    ax.add_patch(rect)
    ax.text(x + 0.08, 0.78, title, ha='center', va='center', fontsize=8.2, fontweight='bold', color=border)
    ax.text(x + 0.08, 0.45, body, ha='center', va='center', fontsize=7.2, color='#2d3748')

# Arrows between stages
for i in range(4):
    x_start = stage_boxes[i][4] + 0.16
    x_end = stage_boxes[i+1][4]
    ax.annotate('', xy=(x_end, 0.52), xytext=(x_start, 0.52),
                arrowprops=dict(arrowstyle="->", color="#4a5568", lw=2.0))

# Decision branch from Stage 4
ax.text(0.70, 0.08, "Advancing: High Suitability -> Final Technical Offer", ha='center', fontsize=8.0, fontweight='bold', color='#2b6cb0')
ax.text(0.70, 0.03, "Unshortlisted / Gapped -> Seamless Diversion into Component 4 Remedial Roadmap", ha='center', fontsize=8.0, fontweight='bold', color='#c53030')

ax.set_title("Figure 1.2: End-to-End RecruitAI Candidate Lifecycle and Analytical State Flow", fontsize=11, fontweight='bold', pad=12, color='#1a365d')

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "fig9_integrated_lifecycle_flow.png"))
plt.close()

# -------------------------------------------------------------
# Figure 10: Cross-Component Empirical Benchmark Overview
# -------------------------------------------------------------
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(10, 6.5), dpi=300)

# (a) C1 Classification
models_c1 = ['Naive\nBayes', 'Random\nForest', 'Linear\nSVC', 'Proposed\nLogReg', 'DistilBERT']
accs_c1 = [76.20, 78.40, 89.12, 87.42, 91.80]
cols_c1 = ['#cbd5e0', '#cbd5e0', '#a0aec0', '#2b6cb0', '#718096']
ax1.bar(models_c1, accs_c1, color=cols_c1, edgecolor='black', linewidth=0.8, width=0.55)
ax1.set_ylabel("Accuracy (%)", fontsize=8.5, fontweight='bold')
ax1.set_title("(a) Component 1: Role Classification Accuracy (N=819)", fontsize=9.5, fontweight='bold')
ax1.set_ylim(60, 100)
for i, v in enumerate(accs_c1):
    ax1.text(i, v + 0.8, f"{v:.1f}%", ha='center', fontsize=7.5, fontweight='bold')

# (b) C2 Multi-Modal Interview
models_c2 = ['TF-IDF\nCosine', 'Okapi\nBM25', 'USE\nEncoder', 'BERT\nBase', 'Proposed\nSBERT']
corr_c2 = [0.612, 0.635, 0.742, 0.789, 0.884]
cols_c2 = ['#cbd5e0', '#cbd5e0', '#a0aec0', '#a0aec0', '#553c9e']
ax2.bar(models_c2, corr_c2, color=cols_c2, edgecolor='black', linewidth=0.8, width=0.55)
ax2.set_ylabel("Human Correlation (r)", fontsize=8.5, fontweight='bold')
ax2.set_title("(b) Component 2: Answer Scoring vs Human Rubric", fontsize=9.5, fontweight='bold')
ax2.set_ylim(0.4, 1.0)
for i, v in enumerate(corr_c2):
    ax2.text(i, v + 0.015, f"{v:.3f}", ha='center', fontsize=7.5, fontweight='bold')

# (c) C3 Listwise Ranking
models_c3 = ['Single\nCV', 'Single\nInterview', 'AHP /\nTOPSIS', 'Proposed\nCSS', 'LambdaMART\nComparator']
ndcg_c3 = [0.812, 0.841, 0.879, 0.9437, 0.9473]
cols_c3 = ['#cbd5e0', '#cbd5e0', '#a0aec0', '#c53030', '#718096']
ax3.bar(models_c3, ndcg_c3, color=cols_c3, edgecolor='black', linewidth=0.8, width=0.55)
ax3.set_ylabel("NDCG@5 Metric", fontsize=8.5, fontweight='bold')
ax3.set_title("(c) Component 3: Candidate Listwise Ranking Fidelity", fontsize=9.5, fontweight='bold')
ax3.set_ylim(0.7, 1.0)
for i, v in enumerate(ndcg_c3):
    ax3.text(i, v + 0.007, f"{v:.3f}", ha='center', fontsize=7.5, fontweight='bold')

# (d) C4 Skill Gap Hireability
models_c4 = ['Logistic\nRegression', 'Random\nForest', 'Proposed\nGBDT 300T']
auc_c4 = [0.9245, 0.9512, 0.9763]
cols_c4 = ['#cbd5e0', '#a0aec0', '#22543d']
ax4.bar(models_c4, auc_c4, color=cols_c4, edgecolor='black', linewidth=0.8, width=0.45)
ax4.set_ylabel("ROC-AUC Score", fontsize=8.5, fontweight='bold')
ax4.set_title("(d) Component 4: Hireability Classification ROC-AUC", fontsize=9.5, fontweight='bold')
ax4.set_ylim(0.85, 1.0)
for i, v in enumerate(auc_c4):
    ax4.text(i, v + 0.003, f"{v:.4f}", ha='center', fontsize=7.5, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "fig10_cross_component_benchmarks.png"))
plt.close()

print("All dissertation figures generated successfully.")

