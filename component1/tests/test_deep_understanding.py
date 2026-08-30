"""
Comprehensive Test Suite for Component 1 Deep CV Understanding & Accuracy Upgrades
Tests layout-aware parsing, lexicon expansion, employment decomposition,
role-relevant experience, multi-signal seniority, contextual skill evidence,
job requirement extraction, and independent Component 3 scoring contracts.
"""

import pytest
from backend.services.parser import normalize_extracted_text
from ml.lexicon import (
    SKILL_LEXICON,
    SKILL_ALIASES,
    CANONICAL_CERTIFICATIONS,
    RELATED_SKILLS_GRAPH,
)
from ml.extractor import (
    extract_sections,
    extract_employment_records,
    extract_experience_details,
    detect_seniority,
    extract_skills_and_certifications,
    extract_deep_cv_profile,
)
from backend.services.job_extractor import (
    extract_job_requirements,
    JobRequirements,
)
from backend.services.scorer import (
    score,
    calculate_skill_score,
    calculate_experience_score,
    calculate_education_score,
)


# ── 1. Document Parsing & Symbol Preservation Tests ───────────────────────────

class TestDocumentParsingSanitization:
    """Verifies text normalization while strictly preserving programming symbols."""

    def test_programming_symbols_preserved(self):
        raw = "Proficient in C++, C#, .NET Core, ASP.NET, Node.js, Next.js, and CI/CD pipelines."
        normalized = normalize_extracted_text(raw)
        assert "C++" in normalized
        assert "C#" in normalized
        assert ".NET" in normalized
        assert "ASP.NET" in normalized
        assert "Node.js" in normalized
        assert "Next.js" in normalized
        assert "CI/CD" in normalized

    def test_unicode_bullets_and_quotes_normalized(self):
        raw = "• Developed microservices – using \u201cFastAPI\u201d and \u2018Docker\u2019 \u00a0"
        normalized = normalize_extracted_text(raw)
        assert "•" in normalized or "-" in normalized
        assert '"FastAPI"' in normalized
        assert "'Docker'" in normalized
        assert "\u00a0" not in normalized


# ── 2. Lexicon & Taxonomy Expansion Tests ─────────────────────────────────────

class TestLexiconAndTaxonomy:
    """Verifies expanded lexicon, aliases, certifications, and graph."""

    def test_lexicon_size_and_categories(self):
        total_skills = sum(len(skills) for skills in SKILL_LEXICON.values())
        assert len(SKILL_LEXICON) >= 19
        assert total_skills >= 400

    def test_alias_resolution(self):
        assert SKILL_ALIASES.get("k8s") == "kubernetes"
        assert SKILL_ALIASES.get("reactjs") == "react"
        assert SKILL_ALIASES.get("ts") == "typescript"
        assert SKILL_ALIASES.get("postgres") == "postgresql"
        assert SKILL_ALIASES.get("tf") == "tensorflow"
        assert SKILL_ALIASES.get("amazon web services") == "aws"

    def test_canonical_certifications_coverage(self):
        cert_names = list(CANONICAL_CERTIFICATIONS.keys())
        assert any("aws certified solutions architect" in c for c in cert_names)
        assert any("certified kubernetes administrator" in c for c in cert_names)
        assert any("cissp" in c for c in cert_names)

    def test_related_skills_graph(self):
        assert "fastapi" in RELATED_SKILLS_GRAPH.get("python", [])
        assert "docker" in RELATED_SKILLS_GRAPH.get("kubernetes", [])
        assert "typescript" in RELATED_SKILLS_GRAPH.get("react", [])


# ── 3. Employment Decomposition & Role-Relevant Experience Tests ──────────────

class TestEmploymentDecomposition:
    """Verifies parsing of employment records and total vs relevant experience calculation."""

    SAMPLE_HYBRID_CV = """
    Jane Developer
    Email: jane@example.com
    SUMMARY
    Senior Backend Engineer with extensive distributed systems and cloud experience.
    
    EXPERIENCE
    Senior Backend Engineer at CloudTech Systems
    Jan 2022 - Present
    - Architected scalable microservices using Python, FastAPI, and PostgreSQL.
    - Containerized legacy applications using Docker and orchestrated deployments on Kubernetes.
    - Mentored 4 junior developers and led quarterly sprint planning.
    
    Data Analyst at RetailCorp
    Jun 2019 - Dec 2021
    - Built business intelligence dashboards with Power BI and wrote complex SQL queries.
    - Analyzed customer retention metrics using Excel and Tableau.
    
    EDUCATION
    B.Sc. in Computer Science - University of Moratuwa (2019)
    
    CERTIFICATIONS
    AWS Certified Solutions Architect - Associate
    """

    def test_employment_records_extracted(self):
        records = extract_employment_records(self.SAMPLE_HYBRID_CV, target_role="Backend Developer")
        assert len(records) >= 2
        titles = [r["job_title"].lower() for r in records]
        assert any("backend" in t for t in titles)
        assert any("analyst" in t for t in titles)

    def test_total_vs_role_relevant_experience(self):
        details = extract_experience_details(self.SAMPLE_HYBRID_CV, target_role="Backend Developer")
        total_years = details["total_experience_years"]
        relevant_years = details["role_relevant_experience_years"]

        assert total_years >= 5.0
        assert relevant_years > 0.0
        assert relevant_years <= total_years


# ── 4. Multi-Signal Seniority Detection Tests ──────────────────────────────────

class TestSeniorityDetection:
    """Verifies seniority detection across various candidate profiles."""

    def test_senior_level_detection(self):
        cv = """
        EXPERIENCE
        Senior Software Engineer at AlphaCorp
        2018 - Present
        - Led architectural refactoring and supervised a team of 6 engineers.
        """
        records = extract_employment_records(cv, "Software Engineer")
        sen_info = detect_seniority(records, relevant_years=7.0, text=cv)
        assert sen_info["seniority"] in ("Senior", "Lead")
        assert sen_info["confidence"] >= 0.70

    def test_lead_architect_detection(self):
        cv = """
        EXPERIENCE
        Lead Solutions Architect at Global Systems
        2014 - Present
        - Directed organizational cloud transformation and enterprise governance.
        """
        records = extract_employment_records(cv, "Cloud Solutions Architect")
        sen_info = detect_seniority(records, relevant_years=11.0, text=cv)
        assert sen_info["seniority"] in ("Lead", "Architect", "Principal")

    def test_junior_intern_detection(self):
        cv = """
        EXPERIENCE
        Software Engineering Intern at StartUpHub
        Jan 2025 - Jun 2025
        - Assisted with frontend bug fixes using HTML and JavaScript.
        """
        records = extract_employment_records(cv, "Software Engineer")
        sen_info = detect_seniority(records, relevant_years=0.5, text=cv)
        assert sen_info["seniority"] in ("Intern", "Junior")


# ── 5. Contextual Skill Evidence & Sniffing Tests ─────────────────────────────

class TestContextualSkillEvidence:
    """Verifies categorization into HIGH, MEDIUM, and LOW evidence levels."""

    def test_skill_evidence_levels(self):
        cv = """
        TECHNICAL SKILLS
        Python, Go, Java, Docker, Kubernetes, AWS
        
        WORK EXPERIENCE
        Backend Developer at Nexa
        2021 - 2024
        - Built asynchronous microservices in Python and FastAPI with PostgreSQL databases.
        - Deployed scalable clusters using Docker.
        """
        res = extract_skills_and_certifications(cv)
        skills = res["detected_skills"]
        evidence = res["skill_evidence"]

        assert "python" in skills
        assert "fastapi" in skills

        # Python and FastAPI mentioned in work experience bullets should have HIGH/VERY_HIGH evidence
        py_ev = evidence.get("python", {})
        assert py_ev.get("evidence_strength") in ["high", "very_high"]
        assert py_ev.get("evidence_level") in ["HIGH", "VERY_HIGH"]




# ── 6. Job Requirement Extraction Tests ───────────────────────────────────────

class TestJobRequirementExtractor:
    """Verifies parsing of raw JD text into structured JobRequirements."""

    SAMPLE_JD = """
    Job Title: Senior Backend Engineer
    Location: Remote / Colombo
    
    Requirements:
    - Minimum 5+ years of software engineering experience.
    - Strong proficiency in Python, FastAPI, PostgreSQL, and Docker.
    - Bachelor's degree in Computer Science, Software Engineering, or related IT discipline.
    
    Nice to have:
    - AWS Certified Solutions Architect.
    - Hands-on experience with Kubernetes, Kafka, and Redis.
    """

    def test_jd_extraction(self):
        reqs = extract_job_requirements(job_description=self.SAMPLE_JD)
        assert isinstance(reqs, JobRequirements)
        assert reqs.canonical_role in ("Backend Developer", "Software Engineer")
        assert reqs.required_experience_years >= 5.0
        assert reqs.required_seniority in ("Senior", "Lead")

        # Check required skills
        req_lower = [s.lower() for s in reqs.required_skills]
        assert "python" in req_lower
        assert "fastapi" in req_lower
        assert "postgresql" in req_lower

        # Check preferred skills
        pref_lower = [s.lower() for s in reqs.preferred_skills]
        assert any(k in pref_lower for k in ("kubernetes", "kafka", "redis"))


# ── 7. Component 3 Scoring Contract Tests ─────────────────────────────────────

class TestComponent3ScoringContract:
    """Verifies that S_skill, S_exp, and S_edu are strictly independent in [0, 100]."""

    def test_independent_score_bounds(self):
        result = score(
            role="Backend Developer",
            edu_level=3,
            experience_years=4.5,
            skills=["Python", "FastAPI", "PostgreSQL", "Docker", "Git"],
            role_relevant_experience_years=3.5,
            candidate_seniority="Mid",
            target_seniority="Mid",
            verified_certifications=[{"name": "AWS Certified Solutions Architect", "category": "Cloud"}],
        )

        assert 0.0 <= result.S_skill <= 100.0
        assert 0.0 <= result.S_exp <= 100.0
        assert 0.0 <= result.S_edu <= 100.0

        # Component 1 scores structure must match Component 3 contract
        assert hasattr(result.component_1_scores, "S_skill")
        assert hasattr(result.component_1_scores, "S_exp")
        assert hasattr(result.component_1_scores, "S_edu")

        # Independent score mutation verification: high edu with low exp
        low_exp_result = score(
            role="Backend Developer",
            edu_level=4, # PhD
            experience_years=0.0,
            skills=["Python", "FastAPI"],
        )
        assert low_exp_result.S_edu == 100.0
        assert low_exp_result.S_exp == 0.0
        assert 0.0 < low_exp_result.S_skill < 100.0
