# Component 1 — AI Resume Screening & IT Job Role Classification
**Research Paper & Ecosystem Component 1 — R26-IT-148 (SLIIT Final Year Project)**  
**Author:** Dulnith K.D. (IT22094872)

---

## 1. System Overview & Research Purpose

Component 1 delivers an explainable, academic-grade AI system for automated resume screening and **20 IT Job Role Classification**. 

The core pipeline processes raw CVs in **PDF, DOCX, or TXT** formats, cleans text (anonymizing sensitive PII), extracts key information (experience, education, skills, certifications), builds engineered feature vectors ($S_{edu}, S_{exp}, S_{skill}$ + 20-role skill overlap dimensions), and predicts target job roles with confidence probabilities and transparent screening scores.

---

## 2. Model Architecture

```text
CV (PDF / DOCX / TXT)
       │
       ▼
Text Extraction (PyMuPDF / python-docx / UTF-8)
       │
       ▼
Text Preprocessing & Anonymization (Strip PII: email/phone/URL/address, preserve technical terms C++, Node.js, REST API)
       │
       ▼
Regex + Lexicon Based Information Extraction
       ├── Experience Parser (Regex for year ranges & explicitly stated experience)
       ├── Education Parser (Degree level: PhD/MSc/BSc/Diploma + major field classification)
       └── Skill & Certification Extractor (20-Role Comprehensive IT Skill Lexicon)
       │
       ▼
Feature Engineering
       ├── S_skill (Normalized Skill Match Score: 0.0 – 1.0)
       ├── S_exp   (Normalized Experience Match Score: 0.0 – 1.0)
       ├── S_edu   (Normalized Education Match Score: 0.0 – 1.0)
       ├── Per-Role Skill Overlap Vector (20 feature dimensions)
       └── Quantitative Meta Features (skill_count, cert_count, project_count)
       │
       ▼
Feature-Based Logistic Regression Classifier (cv_classifier.pkl)
       │
       ▼
20 IT Job Role Classification + Prediction Probabilities
       │
       ▼
Screening Score Engine: screening_score = (S_skill * 0.50 + S_exp * 0.30 + S_edu * 0.20) * 100
```

---

## 3. Canonical 20 IT Job Roles

The system strictly classifies CVs into exactly these **20 IT Job Roles**:

1. Software Engineer
2. Data Scientist
3. Machine Learning Engineer
4. DevOps Engineer
5. Cloud Solutions Architect
6. Database Administrator
7. Frontend Developer
8. Backend Developer
9. Mobile App Developer
10. Full Stack Developer
11. QA/Test Automation Engineer
12. Data Engineer
13. Site Reliability Engineer
14. Cybersecurity Analyst
15. UI/UX Designer
16. Network Engineer
17. Business/Systems Analyst
18. AI/NLP Engineer
19. Blockchain Developer
20. Embedded Systems Engineer

---

## 4. Feature Engineering & Core Equations

### 4.1 Skill Score ($S_{skill}$)
$$S_{skill} = \frac{|\text{Detected Skills} \cap \text{Required Role Skills}|}{|\text{Required Role Skills}|}$$

### 4.2 Experience Score ($S_{exp}$)
$$S_{exp} = \min\left(1.0, \frac{\text{Extracted Experience Years}}{\text{Required Role Experience Years}}\right)$$

### 4.3 Education Score ($S_{edu}$)
$$S_{edu} = \text{Education Level Score} \times \text{Major Relevance Factor}$$
- Degree Level: PhD ($1.0$), MSc ($0.80$), BSc ($0.60$), Diploma ($0.40$), None ($0.20$).
- Major Relevance: CS/IT/SE/DS ($1.0$), General/Other ($0.80$).

### 4.4 Screening Score (0–100)
$$\text{Screening Score} = (0.50 \times S_{skill} + 0.30 \times S_{exp} + 0.20 \times S_{edu}) \times 100$$

---

## 5. Model Evaluation & Research Results

Evaluation conducted on a held-out test split ($15\%$ test set across all 20 canonical roles):

| Model Architecture | Accuracy | Macro F1 | Weighted F1 | Model File |
| :--- | :---: | :---: | :---: | :--- |
| **Primary Model**: Feature Engineering + LogisticRegression | **98.57%** | **0.9857** | **0.9857** | `cv_classifier.pkl` |
| **Baseline Model**: TF-IDF + LogisticRegression | **98.33%** | **0.9833** | **0.9833** | `tfidf_baseline.pkl` |

*Evaluation metrics, classification report (`results/classification_report.txt`), and confusion matrix plot (`results/confusion_matrix.png`) are saved in `results/`.*

---

## 6. Model Artifacts (`models/`)

- `cv_classifier.pkl`: Feature-based `LogisticRegression` model.
- `label_encoder.pkl`: Scikit-Learn `LabelEncoder` for 20 role labels.
- `feature_config.json`: Feature list configuration and vector dimension mapping.
- `skill_lexicon.json`: Categorized IT skill dictionary.
- `role_requirements.json`: Required skills and experience thresholds per role.

---

## 7. API Endpoints

### 7.1 `POST /api/v1/screen-resume`
Screen an uploaded CV file (`multipart/form-data`) and return role prediction, confidence, screening score, and feature breakdowns.

#### Example Request:
```bash
curl -X POST "http://localhost:8001/api/v1/screen-resume" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_resume.pdf"
```

#### Example Response:
```json
{
  "predicted_role": "Backend Developer",
  "confidence": 0.9856,
  "screening_score": 88.33,
  "scores": {
    "S_skill": 0.90,
    "S_exp": 1.00,
    "S_edu": 0.60
  },
  "detected_skills": [
    "django",
    "docker",
    "fastapi",
    "postgresql",
    "python",
    "redis"
  ],
  "detected_certs": [
    "AWS Certified Solutions Architect"
  ],
  "experience_years": 4.0,
  "education": [
    "Computer Science"
  ],
  "top_roles": [
    {
      "role": "Backend Developer",
      "probability": 0.9856
    },
    {
      "role": "Software Engineer",
      "probability": 0.0112
    }
  ]
}
```

### 7.2 `GET /health`
Health check endpoint returning system status and model loading state.

---

## 8. Unit Testing & Verification

Run the unit test suite inside `component1/`:
```bash
python -m pytest tests/test_component1.py
```
*All 7 unit tests covering text cleaning, PII removal, experience extraction, education extraction, skill matching, feature calculation, model prediction, and FastAPI endpoints pass with 100% success rate.*
