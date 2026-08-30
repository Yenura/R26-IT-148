"""
Tests for International and Non-Standard Degree Qualifications Recognition
Component 1 — AI Resume Screening & IT Job Role Classification
IT22094872 | Dulnith K.D. | R26-IT-148
"""

import pytest
from ml.extractor import extract_education_level, extract_education_details


class TestInternationalDegreeQualifications:
    """Verifies that non-standard international qualifications correctly map to academic levels."""

    @pytest.mark.parametrize("text,expected_level_name,expected_min_score", [
        # Doctoral Level (Level 4 - score 1.0)
        ("Doctor of Engineering (Dr.-Ing.) in Artificial Intelligence", "PhD", 1.0),
        ("Dr. rer. nat. in Computer Science from TU Munich", "PhD", 1.0),
        ("Doctor of Philosophy (DPhil) in Computing", "PhD", 1.0),
        ("Doctor of Science (D.Sc.) in Information Systems", "PhD", 1.0),
        ("Docteur en Informatique, Université de Paris", "PhD", 1.0),
        ("Doktor der Ingenieurwissenschaften (Dr.-Ing.)", "PhD", 1.0),
        
        # Master's / 2nd Cycle Bologna Level (Level 3 - score 0.8)
        ("Diplom-Informatiker (Dipl.-Inf.) in Computer Science", "MSc", 0.8),
        ("Diplom-Ingenieur (Dipl.-Ing.) in Software Systems", "MSc", 0.8),
        ("Diplome d'Ingenieur in Computer Science, INSA Lyon", "MSc", 0.8),
        ("Laurea Magistrale in Ingegneria Informatica, Politecnico di Milano", "MSc", 0.8),
        ("Master of Philosophy (MPhil) in Machine Learning", "MSc", 0.8),
        ("Master of Computer Applications (MCA)", "MSc", 0.8),
        ("Magister en Ciencias de la Computacion", "MSc", 0.8),
        ("Maitrise en Informatique", "MSc", 0.8),
        ("Postgraduate Diploma (PGDip) in Software Engineering", "MSc", 0.8),

        # Bachelor's / 1st Cycle Bologna Level (Level 2 - score 0.6)
        ("Licenciatura en Ciencias de la Computacion, Universidad de Buenos Aires", "BSc", 0.6),
        ("Grado en Ingenieria Informatica, Universidad Politecnica de Madrid", "BSc", 0.6),
        ("Laurea Triennale in Informatica, Universita di Roma", "BSc", 0.6),
        ("Diplom-Ingenieur (FH) in Information Technology", "BSc", 0.6),
        ("Bachelor of Applied Science (BAppSc) in Software Development", "BSc", 0.6),
        ("Bachelor of Computer Applications (BCA)", "BSc", 0.6),
        ("Bachelor of Information Technology (BIT)", "BSc", 0.6),

        # Diploma / Vocational Level (Level 1 - score 0.4)
        ("Higher National Diploma (HND) in Computing & Systems Development", "Diploma", 0.4),
        ("Brevet de Technicien Superieur (BTS) Services Informatiques aux Organisations", "Diploma", 0.4),
        ("Diplome Universitaire de Technologie (DUT) Informatique", "Diploma", 0.4),
        ("Associate of Applied Science (AAS) in Network Administration", "Diploma", 0.4),
        ("Foundation Degree in Computing (FdSc)", "Diploma", 0.4),
    ])
    def test_international_degree_level_classification(self, text, expected_level_name, expected_min_score):
        res = extract_education_level(text)
        assert res["level_score"] >= expected_min_score, f"Failed for {text}: got {res['level_score']} expected >= {expected_min_score}"
        assert res["level_name"] == expected_level_name, f"Failed for {text}: got {res['level_name']} expected {expected_level_name}"
