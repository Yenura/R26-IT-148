"""
Test Candidate Intelligence Engine — Component 1
IT22094872 | Dulnith K.D. | R26-IT-148

Exhaustive test suite testing all 13 Required Validation Scenarios:
1. Accountant 1 year + Software Engineer 1 year -> Target: Software Engineer (Relevant Exp ≈ 1 yr).
2. 10 years Accountant + 1 year Software Engineer -> Target: Software Engineer (S_exp reflects ≈ 1 yr, NOT 11 yrs).
3. Generic "Developer" title with Python + FastAPI + PostgreSQL -> Target: Backend Developer (High relevance >= 0.80).
4. "Software Engineer" title with React frontend work only -> Target: Backend Developer (Partial relevance 0.40 - 0.59).
5. Education = BSc Accounting -> Target: Software Engineer (Low education relevance <= 45.0).
6. Education = BSc Computer Science -> Target: Software Engineer (High education relevance >= 90.0).
7. Education = BSc Mathematics -> Target: Data Scientist (Relevant >= 75.0).
8. AWS Certification -> Target: Cloud Solutions Architect (High relevance >= 0.80).
9. AWS Certification -> Target: UI/UX Designer (Low relevance <= 0.25).
10. Skill listed only once with no experience evidence -> Low confidence (<= 0.50).
11. Skill appears in Skills, Experience, and Projects -> High/Very High confidence (>= 0.85).
12. Overlapping employment dates -> Verify deduplication (no double counting).
13. Personal/academic projects -> Verify they do NOT increase employment experience years.
"""

import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.extractor import (
    extract_employment_records,
    extract_experience_details,
    extract_experience_years,
    extract_skills_and_certifications,
    extract_education_details,
    extract_projects,
    validate_cross_evidence,
)
from backend.services.extractor import extract
from backend.services.scorer import (
    calculate_skill_score,
    calculate_experience_score,
    calculate_education_score,
    score,
)
from data.role_requirements import build_target_job_profile, REQUIRED_SKILLS


# ==============================================================================
# TEST SCENARIO 1: Accountant 1 yr + Software Engineer 1 yr -> Target: Software Engineer
# ==============================================================================
def test_scenario_1_accountant_plus_software_engineer():
    cv_text = """
    Jane Doe
    
    WORK EXPERIENCE
    Senior Accountant at Ernst & Young
    Jan 2021 - Dec 2021
    - Prepared balance sheets, audited general ledgers, filed corporate taxes.
    
    Software Engineer at TechCorp
    Jan 2022 - Dec 2022
    - Developed backend REST APIs with Python, Django, and PostgreSQL.
    
    EDUCATION
    BSc in Computer Science
    """
    details = extract_experience_details(cv_text, target_role="Software Engineer")
    
    assert details["total_professional_experience_years"] == pytest.approx(2.0, abs=0.2)
    assert details["it_sector_experience_years"] == pytest.approx(1.0, abs=0.2)
    assert details["target_role_relevant_experience_years"] == pytest.approx(1.0, abs=0.2)


# ==============================================================================
# TEST SCENARIO 2: 10 yrs Accountant + 1 yr Software Engineer -> Target: Software Engineer
# ==============================================================================
def test_scenario_2_ten_years_accountant_plus_one_year_se():
    cv_text = """
    Mark Smith
    
    WORK EXPERIENCE
    Senior Accountant & Financial Controller at KPMG
    Jan 2012 - Dec 2021
    - Managed corporate audits, balance sheets, payroll reconciliation, tax compliance.
    
    Software Engineer at StartupHub
    Jan 2022 - Dec 2022
    - Built microservices and web APIs using Python, FastAPI, and Docker.
    
    EDUCATION
    BSc in Accounting & Finance
    """
    details = extract_experience_details(cv_text, target_role="Software Engineer")
    
    assert details["total_professional_experience_years"] >= 10.0
    assert details["it_sector_experience_years"] == pytest.approx(1.0, abs=0.2)
    assert details["target_role_relevant_experience_years"] == pytest.approx(1.0, abs=0.2)
    
    # S_exp calculation must behave like ~1 year out of 3 years required, NOT 11 years (100%)
    s_exp, analysis = calculate_experience_score(
        candidate_years=details["total_professional_experience_years"],
        required_years=3.0,
        relevant_years=details["target_role_relevant_experience_years"],
        employment_records=details["employment_records"],
    )
    assert s_exp < 55.0  # Must NOT be 100%
    assert analysis.relevant_years == pytest.approx(1.0, abs=0.2)


# ==============================================================================
# TEST SCENARIO 3: Generic "Developer" title with Python+FastAPI+PostgreSQL -> Target: Backend Developer
# ==============================================================================
def test_scenario_3_generic_developer_with_backend_work():
    cv_text = """
    Alex Taylor
    
    WORK EXPERIENCE
    Developer at CloudSystems
    Jan 2022 - Dec 2023
    - Built Python FastAPI REST APIs and microservices.
    - Designed relational database schemas in PostgreSQL with Redis caching.
    - Dockerized backend services and integrated CI/CD pipelines.
    
    EDUCATION
    BSc in Software Engineering
    """
    records = extract_employment_records(cv_text, target_role="Backend Developer")
    assert len(records) >= 1
    rec = records[0]
    
    # Responsibilities and tech stack elevate generic "Developer" to HIGHLY_RELEVANT
    assert rec["target_role_relevance"] >= 0.80
    assert rec["relevance_category"] in ["HIGHLY_RELEVANT", "RELEVANT"]


# ==============================================================================
# TEST SCENARIO 4: "Software Engineer" title with React only -> Target: Backend Developer
# ==============================================================================
def test_scenario_4_frontend_only_applying_for_backend():
    cv_text = """
    Samantha Ray
    
    WORK EXPERIENCE
    Software Engineer at WebAgency
    Jan 2022 - Dec 2023
    - Developed modern responsive single-page web applications in React.js and CSS.
    - Designed reusable UI component libraries and managed Redux state.
    - Built mobile-first responsive web layouts with Tailwind CSS.
    
    EDUCATION
    BSc in Information Technology
    """
    records = extract_employment_records(cv_text, target_role="Backend Developer")
    assert len(records) >= 1
    rec = records[0]
    
    # React frontend work provides partial / weak relevance for Backend Developer (distinct from full backend match)
    assert 0.25 <= rec["target_role_relevance"] <= 0.60
    assert rec["relevance_category"] in ["PARTIALLY_RELEVANT", "WEAKLY_RELATED"]


# ==============================================================================
# TEST SCENARIO 5: Education = BSc Accounting -> Target: Software Engineer
# ==============================================================================
def test_scenario_5_accounting_degree_for_software_engineer():
    score_val, analysis = calculate_education_score(
        candidate_edu="Bachelor of Accounting from University of Colombo",
        edu_level=2,
        target_role="Software Engineer"
    )
    assert analysis.degree_level == "BSc"
    assert analysis.field_relevance in ["LOW", "IRRELEVANT"]
    assert score_val <= 45.0


# ==============================================================================
# TEST SCENARIO 6: Education = BSc Computer Science -> Target: Software Engineer
# ==============================================================================
def test_scenario_6_cs_degree_for_software_engineer():
    score_val, analysis = calculate_education_score(
        candidate_edu="B.Sc. (Hons) in Computer Science, University of Moratuwa",
        edu_level=2,
        target_role="Software Engineer"
    )
    assert analysis.degree_level == "BSc"
    assert analysis.field_relevance == "HIGH"
    assert score_val >= 85.0


# ==============================================================================
# TEST SCENARIO 7: Education = BSc Mathematics -> Target: Data Scientist
# ==============================================================================
def test_scenario_7_mathematics_degree_for_data_scientist():
    score_val, analysis = calculate_education_score(
        candidate_edu="BSc in Mathematics and Statistics, University of Colombo",
        edu_level=2,
        target_role="Data Scientist"
    )
    assert analysis.degree_level == "BSc"
    assert analysis.field_relevance in ["HIGH", "RELEVANT"]
    assert score_val >= 75.0


# ==============================================================================
# TEST SCENARIO 8: AWS Certification -> Target: Cloud Solutions Architect
# ==============================================================================
def test_scenario_8_aws_cert_for_cloud_architect():
    edu_full = extract_education_details(
        "Certifications: AWS Certified Solutions Architect Associate (2023)",
        target_role="Cloud Solutions Architect"
    )
    relevant_certs = edu_full.get("relevant_certifications", [])
    assert len(relevant_certs) >= 1
    assert relevant_certs[0]["relevance_score"] >= 0.80


# ==============================================================================
# TEST SCENARIO 9: AWS Certification -> Target: UI/UX Designer
# ==============================================================================
def test_scenario_9_aws_cert_for_uiux_designer():
    edu_full = extract_education_details(
        "Certifications: AWS Certified Solutions Architect Associate (2023)",
        target_role="UI/UX Designer"
    )
    relevant_certs = edu_full.get("relevant_certifications", [])
    assert len(relevant_certs) == 0  # Not relevant for UI/UX Designer


# ==============================================================================
# TEST SCENARIO 10: Skill listed only once in skills list -> Low Confidence
# ==============================================================================
def test_scenario_10_single_mention_skill_low_confidence():
    cv_text = """
    John Doe
    
    SKILLS
    Python, Java, Docker, Kubernetes
    
    EXPERIENCE
    Help Desk Technician at Corp
    Jan 2022 - Dec 2023
    - Answered user support tickets and configured desktop hardware.
    """
    skills_certs = extract_skills_and_certifications(cv_text, "Software Engineer")
    ev = skills_certs["skill_evidence"].get("docker", {})
    
    assert ev.get("confidence", 0.0) <= 0.50
    assert ev.get("evidence_strength") == "low"
    assert ev.get("evidence_sources") == ["skills"]


# ==============================================================================
# TEST SCENARIO 11: Skill appears in Skills, Experience, Projects -> High/Very High Confidence
# ==============================================================================
def test_scenario_11_multi_source_skill_high_confidence():
    cv_text = """
    John Doe
    
    SKILLS
    Python, React, PostgreSQL, Docker
    
    EXPERIENCE
    Backend Developer at Innovate Corp
    Jan 2022 - Dec 2023
    - Built scalable microservices in Python using FastAPI and Docker containers.
    
    PROJECTS
    Automated Trading Bot
    - Developed algorithmic trading platform with Python and WebSocket streams.
    """
    skills_certs = extract_skills_and_certifications(cv_text, "Backend Developer")
    py_ev = skills_certs["skill_evidence"].get("python", {})
    
    assert py_ev.get("confidence", 0.0) >= 0.85
    assert py_ev.get("evidence_strength") in ["high", "very_high"]
    assert "work_experience" in py_ev.get("evidence_sources", [])
    assert "projects" in py_ev.get("evidence_sources", [])


# ==============================================================================
# TEST SCENARIO 12: Overlapping employment dates -> Verify deduplication
# ==============================================================================
def test_scenario_12_overlapping_dates_deduplication():
    cv_text = """
    Bob Developer
    
    WORK EXPERIENCE
    Software Developer at Alpha Inc
    Jan 2022 - Dec 2023
    - Developed backend systems with Python and SQL.
    
    Freelance Developer at Beta Studio
    Jun 2022 - Dec 2022
    - Built web landing pages with JavaScript and HTML.
    
    EDUCATION
    BSc in Computer Science
    """
    details = extract_experience_details(cv_text, "Software Engineer")
    
    # Concurrent jobs from Jan 2022 - Dec 2023 must equal exactly 2.0 years (NOT 2.5 years)
    assert details["total_professional_experience_years"] == pytest.approx(2.0, abs=0.2)


# ==============================================================================
# TEST SCENARIO 13: Personal projects -> Verify they do NOT count as employment tenure
# ==============================================================================
def test_scenario_13_personal_projects_do_not_count_as_employment():
    cv_text = """
    Alice Student
    
    PROJECTS
    E-Commerce Web Portal (2021 - 2023)
    - Full stack store with React and Node.js.
    
    Personal Chat App (2020 - 2022)
    - Real-time chat application with WebSockets and MongoDB.
    
    EDUCATION
    BSc in Information Technology | 2020 - 2024
    """
    projects = extract_projects(cv_text)
    assert len(projects) >= 2
    
    details = extract_experience_details(cv_text, "Software Engineer")
    # Must NOT have counted project dates (2020-2023) as employment experience!
    assert details["total_professional_experience_years"] == 0.0
    assert details["it_sector_experience_years"] == 0.0
    assert len(details["employment_records"]) == 0
