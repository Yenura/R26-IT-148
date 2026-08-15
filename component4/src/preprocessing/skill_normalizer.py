"""
Skill Normalizer Module — Component 4
Loads data/skill_aliases.json and maps skill strings to canonical skill names.
"""

import json
from pathlib import Path
from typing import List, Set

ROOT_DIR = Path(__file__).parent.parent.parent
ALIASES_FILE = ROOT_DIR / "data" / "skill_aliases.json"

_ALIASES_CACHE = None


def load_skill_aliases() -> dict:
    global _ALIASES_CACHE
    if _ALIASES_CACHE is not None:
        return _ALIASES_CACHE

    if ALIASES_FILE.exists():
        with open(ALIASES_FILE, "r", encoding="utf-8") as f:
            _ALIASES_CACHE = json.load(f)
    else:
        _ALIASES_CACHE = {
            "js": "JavaScript",
            "javascript": "JavaScript",
            "py": "Python",
            "python programming": "Python",
            "reactjs": "React",
            "react.js": "React"
        }
    return _ALIASES_CACHE


def normalize_skill(skill: str) -> str:
    """Normalize a single skill string using skill_aliases.json."""
    if not skill or not skill.strip():
        return ""
    clean = skill.strip().lower()
    aliases = load_skill_aliases()
    if clean in aliases:
        return aliases[clean]
    # Check lowercase alias mapping keys
    for alias_key, canonical in aliases.items():
        if alias_key.lower() == clean:
            return canonical
    return skill.strip().title()


def normalize_skills(skills: List[str]) -> List[str]:
    """Normalize a list of skill strings and remove duplicates preserving order."""
    seen: Set[str] = set()
    normalized = []
    for s in skills:
        norm = normalize_skill(s)
        if norm and norm.lower() not in seen:
            seen.add(norm.lower())
            normalized.append(norm)
    return normalized
