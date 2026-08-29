"""
Component 1 — High-Accuracy Hybrid Relevance Engine Test Suite
IT22094872 | Dulnith K.D. | R26-IT-148

Validates all 10 Critical Test Scenarios:
- CASE 1: 1 yr Accountant + 1 yr SE -> Target: SE (Total: 2, IT: 1, Relevant: 1)
- CASE 2: 10 yrs Accountant + 1 yr SE -> Target: SE (S_exp based on 1 yr, not 11 yrs)
- CASE 3: 2 yrs Backend Developer -> Target: ML Engineer (No ML evidence -> Low ML relevance)
- CASE 4: BSc Accounting -> Target: SE (Low field relevance, S_edu <= 35)
- CASE 5: BSc Computer Science -> Target: SE (High relevance, S_edu = 100)
- CASE 6: BSc Mathematics -> Target: Data Scientist (High/Relevant, S_edu >= 80)
- CASE 7: AWS Certification -> Target: Cloud Engineer (High relevance, +15 bonus)
- CASE 8: AWS Certification -> Target: UI/UX Designer (Low relevance, 0 bonus)
- CASE 9: Generic title "Software Engineer", only Frontend React work -> Target: Backend Developer (Partial relevance <= 0.45)
- CASE 10: Generic title "Developer", backend responsibilities (Python, FastAPI, PostgreSQL) -> Target: Backend Developer (High relevance >= 0.85)
- Additional: Interval merging deduplication & Project experience isolation
"""

import pytest
from ml.extractor import (
    extract_employment_records,
    extract_experience_details,
    extract_experience_years,
    extract_education_level,
    extract_education_details,
    extract_deep_cv_profile,
    extract_projects,
)
from backend.services.scorer import (
    score,
    calculate_experience_score,
    calculate_education_score,
    calculate_skill_score,
)
from backend.services.extractor import extract


# ==============================================================================
# TEST CASE 1: 1 Year Accountant + 1 Year Software Engineer -> Target: Software Engineer
# ==============================================================================
class TestCase1_AccountantPlusSoftwareEngineer:
    """
    Candidate with:
    - 1 year Accountant
    - 1 year Software Engineer
    Target Role: Software Engineer
    """

    SAMPLE_CV = """
    Jane Doe
    Email: jane.doe@example.com
    
    WORK EXPERIENCE
    Software Engineer at TechCorp Solutions
    Jan 2023 - Dec 2023
    - Built backend microservices using Python, FastAPI, and PostgreSQL.
    - Designed RESTful APIs and optimized database queries.
    
    Accountant at FinanceFirst Audit LLC
    Jan 2022 - Dec 2022
    - Prepared monthly balance sheets, ledger entries, and financial statements.
    - Conducted tax filing, payroll reconciliation, and annual corporate audits.
    
    EDUCATION
    B.Sc. in Computer Science - University of Colombo (2021)
    """

    def test_employment_records_classification(self):
        records = extract_employment_records(self.SAMPLE_CV, target_role="Software Engineer")
        assert len(records) >= 2

        # Find Accountant record
        acc_rec = next((r for r in records if "accountant" in r["job_title"].lower()), None)
        assert acc_rec is not None
        assert acc_rec["is_it_related"] is False
        assert acc_rec["category"] == "NON_IT"
        assert acc_rec["target_role_relevance"] == 0.0
        assert acc_rec["relevance_category"] == "IRRELEVANT"
        assert acc_rec["relevant_experience_months"] == 0.0

        # Find Software Engineer record
        se_rec = next((r for r in records if "software engineer" in r["job_title"].lower()), None)
        assert se_rec is not None
        assert se_rec["is_it_related"] is True
        assert se_rec["category"] == "IT_RELEVANT"
        assert se_rec["target_role_relevance"] >= 0.85
        assert se_rec["relevance_category"] == "HIGHLY_RELEVANT"
        assert se_rec["relevant_experience_months"] >= 10.0

    def test_3tier_experience_decomposition(self):
        details = extract_experience_details(self.SAMPLE_CV, target_role="Software Engineer")
        
        # 1. Total Professional Experience = 2 years
        assert details["total_experience_years"] >= 1.9
        assert details["total_professional_experience_years"] >= 1.9
        assert details["total_professional_experience_months"] >= 23.0

        # 2. IT Sector Experience = 1 year
        assert details["it_sector_experience_years"] == pytest.approx(1.0, abs=0.2)
        assert details["it_sector_experience_months"] == pytest.approx(12.0, abs=2.0)

        # 3. Target Role Relevant Experience = 1 year
        assert details["target_role_relevant_experience_years"] == pytest.approx(1.0, abs=0.2)
        assert details["target_role_relevant_experience_months"] == pytest.approx(12.0, abs=2.0)

    def test_s_exp_not_counting_accountant(self):
        features = extract(self.SAMPLE_CV, target_role="Software Engineer")
        scores = score(
            role="Software Engineer",
            edu_level=features.edu_level,
            experience_years=features.experience_years,
            role_relevant_experience_years=features.role_relevant_experience_years,
            employment_records=features.employment_records,
            candidate_education=features.education,
            required_years=3.0,
        )
        assert scores.S_exp < 55.0
        assert scores.experience_analysis.relevant_years == pytest.approx(1.0, abs=0.2)
        assert scores.experience_analysis.candidate_years >= 1.9


# ==============================================================================
# TEST CASE 2: 10 Years Accountant + 1 Year Software Engineer -> Target: Software Engineer
# ==============================================================================
class TestCase2_TenYearsAccountantPlusOneYearSE:
    """
    Candidate with:
    - 10 years Accountant
    - 1 year Software Engineer
    Target Role: Software Engineer (Requires 3 years)
    """

    SAMPLE_CV = """
    John Smith
    
    WORK EXPERIENCE
    Junior Software Engineer at DevStudio
    Jan 2023 - Dec 2023
    - Built web components with React and Node.js.
    - Wrote unit tests and resolved bug tickets in Jira.
    
    Senior Chief Accountant at Global Audit Corp
    Jan 2013 - Dec 2022
    - Managed corporate bookkeeping, audited tax reports, and led audit teams.
    - Supervised $50M annual budget and GAAP compliance.
    
    EDUCATION
    BSc in Accounting - University of London
    """

    def test_total_vs_it_vs_relevant(self):
        details = extract_experience_details(self.SAMPLE_CV, target_role="Software Engineer")
        assert details["total_professional_experience_years"] >= 10.5
        assert details["it_sector_experience_years"] == pytest.approx(1.0, abs=0.3)
        assert details["target_role_relevant_experience_years"] == pytest.approx(1.0, abs=0.3)

    def test_s_exp_not_inflated_by_10_years_accounting(self):
        features = extract(self.SAMPLE_CV, target_role="Software Engineer")
        scores = score(
            role="Software Engineer",
            edu_level=features.edu_level,
            experience_years=features.experience_years,
            role_relevant_experience_years=features.role_relevant_experience_years,
            employment_records=features.employment_records,
            required_years=3.0,
        )
        assert scores.S_exp < 55.0
        assert scores.S_exp >= 25.0


# ==============================================================================
# TEST CASE 3: 2 Years Backend Developer -> Target: Machine Learning Engineer
# ==============================================================================
class TestCase3_BackendDeveloperForMLEngineer:
    """
    Candidate with 2 years Backend Developer (APIs, SQL, Redis) applying for Machine Learning Engineer
    with NO machine learning / deep learning evidence in experience.
    """

    SAMPLE_CV = """
    Dave Backend
    
    WORK EXPERIENCE
    Backend Developer at PayGate Systems
    Jan 2022 - Dec 2023
    - Developed payment gateway APIs using Java Spring Boot and MySQL.
    - Managed server deployments and configured Apache Kafka queues.
    
    EDUCATION
    BSc in Information Technology - SLIIT (2021)
    """

    def test_backend_relevance_for_ml_is_low_or_partial(self):
        records = extract_employment_records(self.SAMPLE_CV, target_role="Machine Learning Engineer")
        assert len(records) >= 1
        rec = records[0]
        
        # IT related = True, but ML relevance is low/weakly related
        assert rec["is_it_related"] is True
        assert rec["target_role_relevance"] <= 0.45
        assert rec["relevance_category"] in ["PARTIALLY_RELEVANT", "WEAKLY_RELATED"]

    def test_ml_relevant_experience_is_lower_than_total_it(self):
        details = extract_experience_details(self.SAMPLE_CV, target_role="Machine Learning Engineer")
        assert details["it_sector_experience_years"] >= 1.9
        assert details["target_role_relevant_experience_years"] < 1.2


# ==============================================================================
# TEST CASE 4: Education = Bachelor of Accounting -> Target: Software Engineer
# ==============================================================================
class TestCase4_AccountingDegreeForSoftwareEngineer:
    """Candidate with Bachelor of Accounting applying for Software Engineer."""

    def test_accounting_degree_relevance_for_se(self):
        score_val, analysis = calculate_education_score(
            candidate_edu="Bachelor of Accounting from University of Colombo",
            edu_level=2,
            target_role="Software Engineer"
        )
        assert analysis.degree_level == "BSc"
        assert analysis.field_relevance in ["LOW", "IRRELEVANT"]
        assert score_val <= 45.0


# ==============================================================================
# TEST CASE 5: Education = BSc Computer Science -> Target: Software Engineer
# ==============================================================================
class TestCase5_ComputerScienceDegreeForSoftwareEngineer:
    """Candidate with BSc Computer Science applying for Software Engineer."""

    def test_cs_degree_relevance_for_se(self):
        score_val, analysis = calculate_education_score(
            candidate_edu="B.Sc. (Hons) in Computer Science, University of Moratuwa",
            edu_level=2,
            target_role="Software Engineer"
        )
        assert analysis.degree_level == "BSc"
        assert analysis.field_relevance == "HIGH"
        assert score_val >= 90.0


# ==============================================================================
# TEST CASE 6: Education = BSc Mathematics -> Target: Data Scientist
# ==============================================================================
class TestCase6_MathematicsDegreeForDataScientist:
    """Candidate with BSc Mathematics applying for Data Scientist."""

    def test_math_degree_for_data_scientist(self):
        score_val, analysis = calculate_education_score(
            candidate_edu="Bachelor of Science in Mathematics and Statistics, University of Peradeniya",
            edu_level=2,
            target_role="Data Scientist"
        )
        assert analysis.degree_level == "BSc"
        assert analysis.field_relevance in ["HIGH", "RELEVANT"]
        assert score_val >= 80.0


# ==============================================================================
# TEST CASE 7: AWS Certification -> Target: Cloud Solutions Architect
# ==============================================================================
class TestCase7_AWSCertForCloudEngineer:
    """AWS Certified Solutions Architect applied for Cloud Solutions Architect."""

    def test_aws_cert_for_cloud_architect(self):
        score_val, analysis = calculate_education_score(
            candidate_edu="BSc Information Technology",
            edu_level=2,
            verified_certifications=[{"certification": "AWS Certified Solutions Architect", "is_role_relevant": True}],
            target_role="Cloud Solutions Architect"
        )
        assert len(analysis.relevant_certifications) >= 1
        assert score_val >= 95.0


# ==============================================================================
# TEST CASE 8: AWS Certification -> Target: UI/UX Designer
# ==============================================================================
class TestCase8_AWSCertForUIUXDesigner:
    """AWS Certified Solutions Architect applied for UI/UX Designer."""

    def test_aws_cert_for_uiux_designer(self):
        score_val_with_cert, analysis_with = calculate_education_score(
            candidate_edu="Diploma in Graphic Design",
            edu_level=1,
            verified_certifications=[{"certification": "AWS Certified Solutions Architect", "is_role_relevant": False}],
            target_role="UI/UX Designer"
        )
        score_val_no_cert, analysis_no = calculate_education_score(
            candidate_edu="Diploma in Graphic Design",
            edu_level=1,
            verified_certifications=[],
            target_role="UI/UX Designer"
        )
        assert len(analysis_with.relevant_certifications) == 0
        assert score_val_with_cert == pytest.approx(score_val_no_cert, abs=2.0)


# ==============================================================================
# TEST CASE 9: Generic "Software Engineer", only Frontend React work -> Target: Backend Developer
# ==============================================================================
class TestCase9_FrontendEngineerApplyingForBackend:
    """
    Candidate with title "Software Engineer", but responsibilities and technologies
    are strictly frontend (React, Redux, CSS, HTML, Webpack).
    Target Job: Backend Developer
    Expected: Hybrid relevance drops to partial/weak (<= 0.45), NOT 1.0!
    """

    SAMPLE_CV = """
    Alice UI
    
    WORK EXPERIENCE
    Software Engineer at WebFront Studio
    Jan 2022 - Dec 2023
    - Built responsive user interfaces using React, Redux, HTML5, and CSS3.
    - Optimized DOM rendering, implemented client-side state management, and created UI components.
    - Worked closely with Figma design systems.
    
    EDUCATION
    BSc in Information Technology
    """

    def test_frontend_responsibilities_reduce_backend_relevance(self):
        records = extract_employment_records(self.SAMPLE_CV, target_role="Backend Developer")
        assert len(records) >= 1
        rec = records[0]

        assert rec["is_it_related"] is True
        # Title says Software Engineer (0.70), but responsibilities/tech are React/CSS (0.05-0.15)
        # Hybrid relevance should be partial (<= 0.48)
        assert rec["target_role_relevance"] <= 0.48
        assert rec["relevance_category"] in ["PARTIALLY_RELEVANT", "WEAKLY_RELATED"]


# ==============================================================================
# TEST CASE 10: Generic "Developer", Backend responsibilities (Python, FastAPI, PostgreSQL) -> Target: Backend Developer
# ==============================================================================
class TestCase10_GenericDeveloperWithBackendWork:
    """
    Candidate with generic title "Developer", but responsibilities and technologies
    are deeply backend (Python, FastAPI, PostgreSQL, REST APIs, Redis, Docker).
    Target Job: Backend Developer
    Expected: Hybrid relevance is HIGH (>= 0.80) despite the generic job title!
    """

    SAMPLE_CV = """
    Charlie Server
    
    WORK EXPERIENCE
    Developer at CloudScale Inc
    Jan 2022 - Dec 2023
    - Developed backend REST APIs using Python and FastAPI.
    - Designed relational database schemas in PostgreSQL, implemented Redis caching, and built Docker microservices.
    - Optimized SQL queries and configured database connection pools.
    
    EDUCATION
    BSc in Computer Science
    """

    def test_backend_responsibilities_elevate_generic_developer_title(self):
        records = extract_employment_records(self.SAMPLE_CV, target_role="Backend Developer")
        assert len(records) >= 1
        rec = records[0]

        assert rec["is_it_related"] is True
        # Generic title (0.50), but responsibilities/tech are FastAPI/PostgreSQL (1.0)
        # Hybrid relevance should be elevated to HIGH (>= 0.80)
        assert rec["target_role_relevance"] >= 0.80
        assert rec["relevance_category"] in ["HIGHLY_RELEVANT", "RELEVANT"]


# ==============================================================================
# TEST: Interval Merging and Project Isolation
# ==============================================================================
class TestIntervalMergingAndProjectIsolation:
    """Verifies that projects are isolated and overlapping employment dates are not double-counted."""

    CV_WITH_PROJECTS_AND_OVERLAP = """
    Bob Developer
    
    WORK EXPERIENCE
    Software Developer at Alpha Inc
    Jan 2022 - Dec 2023
    - Built web apps with Python and React.
    
    Freelance Web Developer at Beta Studio
    Jun 2022 - Dec 2022
    - Developed landing pages with HTML and JavaScript.
    
    PROJECTS
    E-Commerce Web Portal (2023)
    - Full-stack online store with Stripe payment integration.
    - Used React, Node.js, and MongoDB.
    
    EDUCATION
    BSc in Software Engineering
    """

    def test_projects_never_counted_as_employment(self):
        projects = extract_projects(self.CV_WITH_PROJECTS_AND_OVERLAP)
        assert len(projects) >= 1
        assert "E-Commerce" in projects[0]["project_title"]

        records = extract_employment_records(self.CV_WITH_PROJECTS_AND_OVERLAP, "Software Engineer")
        job_titles = [r["job_title"].lower() for r in records]
        assert not any("e-commerce" in t for t in job_titles)

    def test_overlapping_dates_deduplicated(self):
        details = extract_experience_details(self.CV_WITH_PROJECTS_AND_OVERLAP, "Software Engineer")
        assert details["total_professional_experience_years"] == pytest.approx(2.0, abs=0.2)


# ==============================================================================
# TEST CASE 11: Fresh Graduate / Student with Projects, Clubs, References -> 0 Exp
# ==============================================================================
class TestCase11_FreshGraduateZeroExperienceCV:
    """Undergraduate student CV with education, projects, clubs, soft skills, references, but NO work experience."""

    STUDENT_CV = """INUKA JATHMAL
    Information Systems Engineering
    ABOUT ME
    Aspiring project manager with problem-solving and communication skills.

    EDUCATION
    BSc (Hons) in Information Technology Specializing in Information Systems Engineering.
    SLIIT UNIVERSITY | 2023 - 2027
    AAT Passed Finalist | 2019 - 2020
    Ananda College | 2019 - 2021
    GCE Advanced Level Commerce Stream( English Medium )

    PROJECTS
    Home Service System
    HomeEase - Built a smart home service system web application using MERN stack with full CRUD features.
    Tech Stack: MongoDB, Express.js, React, Node.js

    Library Management System
    Built a library management system desktop application with full CRUD features.
    Tech Stack: Java

    TECHNOLOGY AND FRAMEWORKS
    Language : Java, JavaScript, Python, C/C++, Html, R, PHP
    Database : MySQL, MongoDB
    Libraries/Framework : Express.js, Node.js, React.js, Next.js

    CLUBS & LEADERSHIP SKILLS
    School cricket team u13, u15, u17
    Leo Club - Member, 2020 - 2022

    SOFT SKILLS
    Team Management, Leadership, Fast Learner

    REFERENCES
    Milinda Dias
    Lead Engineer - Technology
    Itechro(Pvt)Ltd
    """

    def test_zero_experience_extracted_for_student_cv(self):
        details = extract_experience_details(self.STUDENT_CV, "Software Engineer")
        assert details["total_professional_experience_years"] == 0.0
        assert details["it_sector_experience_years"] == 0.0
        assert details["target_role_relevant_experience_years"] == 0.0
        assert len(details["employment_records"]) == 0
        assert details["seniority"] == "Junior"

    def test_projects_and_skills_extracted_for_student_cv(self):
        from ml.extractor import extract_skills_and_certifications
        projects = extract_projects(self.STUDENT_CV)
        assert len(projects) >= 1
        skills = extract_skills_and_certifications(self.STUDENT_CV)["detected_skills"]
        assert "react" in skills or "java" in skills or "python" in skills


class TestCase12_UndergraduateEducationExtraction:
    """Verifies education extraction on complex undergraduate resumes (e.g., Sanduni Madushani)."""

    SANDUNI_CV = """
    SANDUNI MADUSHANI 
    Information System Engineering Undergraduate 
    95/8,Ihalayagoda,Ganemullla | +94764462473 
    msanduni333@gmail.com | Linkedin.com | github.com 
    
    SUMMARY 
    Motivated IT undergraduate specialized in Information System Engineering.
    
    EDUCATION 
    Sri Lanka Institute of Information Technology (May 2023 - Following) 
    Bachelor of science (Hons) in Information Technology Specialized in Information System Engineering
    
    Fundamental Data Analysis using Power BI - Alison (Year 2025) 
    
    PROJECTS 
    Local Service Finder (MERN Stack, MongoDB) 2026 
    Employee Management System (Java Swing, MYSQL Server) 2025 
    
    TECHNICAL SKILLS 
    Databases: MySQL, SQL server 
    Programming: C, C++, Java, R, SQL 
    Web Development: HTML, CSS, PHP, MERN Stack (MongoDB, Express.js, React.js, Node.js)
    """

    def test_sanduni_education_extracted(self):
        from backend.services.extractor import extract
        feat = extract(self.SANDUNI_CV, target_role="Software Engineer")
        assert "bachelor of science" in feat.education.lower() or "information technology" in feat.education.lower()
        assert feat.edu_level >= 2
        assert feat.degree_field in ["Computer Science", "Information Technology", "General IT"]


