import PyPDF2
import re

reader = PyPDF2.PdfReader("final report/IT22089236_DRAFT.pdf")

items = [
    ("Figure 1.1", "Multi-Microservice Architecture"),
    ("Figure 3.4", "Context-Guarded Regex Look-Around Shielding"),
    ("Figure 3.2", "Temporal Experience Disambiguation"),
    ("Figure 5.5", "Forensic Evaluation: Artificial Synthetic Leakage"),
    ("Figure 5.4", "Empirical Classification Performance Across 20 Canonical IT Roles"),
    ("Figure 5.3", "Model Architecture Comparison: Classification Accuracy"),
    ("Figure 5.2", "Empirical Feature Importance Contributions"),
    ("Figure 5.1", "Pipeline Processing Latency Breakdown Across All Six Stages"),
    ("Table 1.1", "Enterprise Technical Recruitment Funnel Drop-Off Metrics"),
    ("Table 2.1", "Comprehensive Survey of Commercial and Open-Source Resume Screening"),
    ("Table 2.2", "International Academic Degree Framework Harmonization Matrix"),
    ("Table 3.1", "Academic Degree Tier Level and Disciplinary Field Relevance"),
    ("Table 3.2", "Dense 67-Dimensional Feature Vector Specification"),
    ("Table 3.3", "Canonical IT Job Role Benchmark Competencies"),
    ("Table 4.1", "Component 1 Microservice RESTful API Specification"),
    ("Table 4.2", "Automated Pytest Verification Suite Breakdown"),
    ("Table 5.0", "5-Fold Stratified Cross-Validation Convergence"),
    ("Table 5.0b", "Hyperparameter Grid Search Optimization"),
    ("Table 5.1", "Primary Classification Performance Metrics on Held-Out Test"),
    ("Table 5.2", "Per-Class Precision, Recall, and F1-Score Across 20"),
    ("Table 5.3", "Comparative Benchmark Against Alternative Machine Learning"),
    ("Table 5.4", "Feature Subset Extraction Ablation Study"),
    ("Table 5.5", "Stage-by-Stage Latency Benchmarking Over 50 Iterations"),
    ("Table 5.6", "Comparative Case Study Predictions, Tri-Pillar Scoring"),
    ("Table 5.7", "Primary Off-Diagonal Error Clusters in 20x20 Classification Matrix"),
    ("Table 6.0", "Representative Closed-Form Feature Attribution Log-Odds Weights"),
    ("Table 6.1", "Global AI Regulatory Compliance Mapping")
]

print("--- FIGURES AND TABLES EXACT PAGES ---")
for num, title in items:
    found_pages = []
    for idx in range(8, len(reader.pages)): # Skip front matter
        txt = reader.pages[idx].extract_text() or ""
        if num.lower() in txt.lower():
            found_pages.append(idx + 1)
    print(f"{num}: {found_pages}")
