"""
Learning Path Recommendation Engine — Component 4
Generates a structured, dependency-ordered learning sequence and recommends learning resources.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from src.preprocessing.skill_normalizer import normalize_skills
from src.gap_analysis.skill_gap import analyze_skill_gap

ROOT_DIR = Path(__file__).parent.parent.parent
MODELS_DIR = ROOT_DIR / "models"
RESOURCES_FILE = MODELS_DIR / "learning_resources.json"

# Canonical skill dependencies graph
SKILL_DEPENDENCY_GRAPH = {
    "Python": [],
    "SQL": [],
    "HTML": [],
    "CSS": [],
    "Git": [],
    "Linux": [],
    "C++": [],
    "Java": [],
    "JavaScript": [],
    "Pandas": ["Python"],
    "NumPy": ["Python"],
    "Statistics": ["Python"],
    "FastAPI": ["Python"],
    "Django": ["Python"],
    "Machine Learning": ["Python", "Pandas", "Statistics"],
    "Scikit-Learn": ["Machine Learning"],
    "Deep Learning": ["Machine Learning"],
    "PyTorch": ["Deep Learning"],
    "TensorFlow": ["Deep Learning"],
    "MLOps": ["Machine Learning", "Docker"],
    "Docker": ["Linux"],
    "Kubernetes": ["Docker"],
    "CI/CD": ["Git", "Docker"],
    "Terraform": ["AWS"],
    "AWS": ["Linux", "Networking"],
    "Azure": ["Linux", "Networking"],
    "React": ["JavaScript", "HTML", "CSS"],
    "Node.js": ["JavaScript"],
    "PostgreSQL": ["SQL"],
    "MySQL": ["SQL"],
    "MongoDB": ["SQL"]
}


def load_resources() -> dict:
    if RESOURCES_FILE.exists():
        with open(RESOURCES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def generate_learning_path(current_skills: List[str], target_role: str) -> Dict[str, Any]:
    """
    Generates a step-by-step learning path ordered by skill dependencies.
    Attach resources (course title, type, level, provider/url) for each missing skill.
    """
    gap_result = analyze_skill_gap(current_skills, target_role)
    missing_info = gap_result.get("missing_skills", [])
    resource_catalog = load_resources()

    # Sort missing skills by dependency order first, then priority_score
    missing_skill_names = [m["skill"] for m in missing_info]

    def dependency_level(skill: str) -> int:
        deps = SKILL_DEPENDENCY_GRAPH.get(skill, [])
        if not deps:
            return 0
        return 1 + max(dependency_level(d) for d in deps)

    ordered_missing = sorted(
        missing_info,
        key=lambda x: (dependency_level(x["skill"]), -x["priority_score"])
    )

    learning_steps = []
    for step_idx, item in enumerate(ordered_missing, start=1):
        sk = item["skill"]
        p_cat = item["priority"]
        p_score = item["priority_score"]

        res_info = resource_catalog.get(sk)
        if not res_info:
            for rk, rv in resource_catalog.items():
                if rk.lower() in sk.lower() or sk.lower() in rk.lower():
                    res_info = rv
                    break

        if res_info:
            res_obj = {
                "title": res_info.get("course", f"{sk} Course"),
                "type": "course",
                "level": res_info.get("level", "Beginner").lower(),
                "provider": res_info.get("provider", "Coursera"),
                "url": res_info.get("url", f"https://www.coursera.org/search?query={sk.replace(' ', '+')}")
            }
        else:
            res_obj = {
                "title": f"Verified {sk} Learning Course",
                "type": "course",
                "level": "intermediate",
                "provider": "Online Education",
                "url": f"https://www.coursera.org/search?query={sk.replace(' ', '+')}"
            }

        learning_steps.append({
            "step": step_idx,
            "skill": sk,
            "priority": p_cat,
            "priority_score": p_score,
            "resources": [res_obj]
        })

    return {
        "target_role": target_role,
        "total_steps": len(learning_steps),
        "learning_path": learning_steps
    }
