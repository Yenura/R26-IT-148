"""Component 1 — TF-IDF CV↔job matching producing component3-compatible scores."""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from skills import (
    JOBS_DEFAULT, EDU_LEVEL_SCORES, EDU_LEVEL_NAMES,
    extract_skills, extract_experience_years, extract_education,
    education_relevance,
)


class SkillMatcher:
    def __init__(self, jobs=None, vectorizer=None):
        self.jobs = jobs or JOBS_DEFAULT
        self.vectorizer = vectorizer or TfidfVectorizer(
            lowercase=True, token_pattern=r"[A-Za-z0-9#+./]+"
        )
        self._tfidf = None

    def fit(self):
        corpus = [" ".join(spec["required_skills"]) for spec in self.jobs.values()]
        self._tfidf = self.vectorizer.fit_transform(corpus)
        return self

    def _sim(self, role, skills):
        if self._tfidf is None:
            return 0.0
        roles = list(self.jobs.keys())
        vec = self.vectorizer.transform([" ".join(skills)])
        return float(cosine_similarity(vec, self._tfidf)[0][roles.index(role)])

    def score(self, role, skills, years, edu_level, edu_rel):
        job = self.jobs[role]
        cand_low = {s.lower() for s in skills}
        covered = [r for r in job["required_skills"]
                   if any(r.lower() in c or c in r.lower() for c in cand_low)]
        coverage = len(covered) / len(job["required_skills"])
        sim = self._sim(role, skills)
        skill_raw = float(np.clip(0.75 * coverage + 0.25 * sim, 0.0, 1.0))

        s_edu = round(0.6 * EDU_LEVEL_SCORES.get(edu_level, 0.4) + 0.4 * edu_rel, 4)
        s_exp = round(min(years / job["required_years"], 1.0), 4)
        s_skill = round(skill_raw, 4)
        cv = round(job["w_edu"] * s_edu + job["w_exp"] * s_exp + job["w_skill"] * s_skill, 4)
        return {
            "S_edu": s_edu,
            "S_exp": s_exp,
            "S_skill": s_skill,
            "cv_matching_score": round(cv * 100, 2),
            "coverage": round(coverage, 4),
            "covered_skills": [r for r in covered],
            "missing_skills": [r for r in job["required_skills"] if r not in covered],
        }

    def analyze_cv(self, role, cv_text=None, skills=None, years=None,
                   education_text=None):
        text = cv_text or ""
        if skills is None:
            skills = extract_skills(text)
        if years is None:
            years = extract_experience_years(text)
        if education_text:
            edu_level, fields = extract_education(education_text)
        else:
            edu_level, fields = extract_education(text)
        edu_rel = education_relevance(edu_level, fields, role)
        res = self.score(role, skills, years, edu_level, edu_rel)
        return {
            "extracted_skills": skills,
            "experience_years": years,
            "edu_level": edu_level,
            "edu_level_name": EDU_LEVEL_NAMES.get(edu_level, "Diploma"),
            "edu_relevance": edu_rel,
            **res,
        }
