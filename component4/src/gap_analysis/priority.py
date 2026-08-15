"""
Priority Calculation Module — Component 4
Computes priority_score = role_importance * 0.50 + market_frequency * 0.30 + dependency_score * 0.20
using parameters from config/weights.json.
"""

import json
from pathlib import Path
from typing import Dict, Tuple

ROOT_DIR = Path(__file__).parent.parent.parent
WEIGHTS_FILE = ROOT_DIR / "config" / "weights.json"


def load_priority_weights() -> dict:
    if WEIGHTS_FILE.exists():
        with open(WEIGHTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "role_importance": 0.50,
        "market_frequency": 0.30,
        "dependency_score": 0.20,
        "thresholds": {"critical": 85.0, "high": 70.0, "medium": 50.0, "low": 0.0}
    }


def compute_priority_score(
    skill: str,
    importance_level: str = "high",
    market_freq_pct: float = 80.0,
    dependency_score_pct: float = 70.0
) -> Tuple[float, str]:
    """
    Computes priority_score (0 - 100) and categorizes into Critical, High, Medium, or Low.
    """
    weights_cfg = load_priority_weights()
    w_imp = weights_cfg.get("role_importance", 0.50)
    w_freq = weights_cfg.get("market_frequency", 0.30)
    w_dep = weights_cfg.get("dependency_score", 0.20)

    imp_numeric = 90.0 if importance_level.lower() == "high" else 65.0 if importance_level.lower() == "medium" else 40.0

    score = (imp_numeric * w_imp) + (market_freq_pct * w_freq) + (dependency_score_pct * w_dep)
    score = round(score, 1)

    thresholds = weights_cfg.get("thresholds", {"critical": 85.0, "high": 70.0, "medium": 50.0, "low": 0.0})

    if score >= thresholds.get("critical", 85.0):
        category = "Critical"
    elif score >= thresholds.get("high", 70.0):
        category = "High"
    elif score >= thresholds.get("medium", 50.0):
        category = "Medium"
    else:
        category = "Low"

    return score, category
