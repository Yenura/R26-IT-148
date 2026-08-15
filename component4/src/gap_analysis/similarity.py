"""
Similarity Metrics — Component 4
Implements Jaccard Similarity and Weighted Skill Similarity.
"""

from typing import List, Set


def jaccard_similarity(skills_a: List[str], skills_b: List[str]) -> float:
    """
    Computes Jaccard Similarity J(A, B) = |A ∩ B| / |A ∪ B|.
    Returns float 0.0 - 1.0.
    """
    set_a = {s.strip().lower() for s in skills_a if s.strip()}
    set_b = {s.strip().lower() for s in skills_b if s.strip()}
    if not set_a or not set_b:
        return 0.0
    intersection = set_a.intersection(set_b)
    union = set_a.union(set_b)
    return round(len(intersection) / len(union), 4)


def weighted_skill_similarity(
    current_skills: List[str],
    required_skills: List[str],
    weights: dict = None
) -> float:
    """
    Computes weighted skill coverage relative to required skills.
    """
    set_curr = {s.strip().lower() for s in current_skills if s.strip()}
    set_req = [s.strip().lower() for s in required_skills if s.strip()]
    if not set_req:
        return 1.0

    matched_count = 0
    total_weight = 0.0
    matched_weight = 0.0

    for s in set_req:
        w = 1.0
        if weights and s in weights:
            w = weights[s]
        total_weight += w
        if s in set_curr:
            matched_weight += w
            matched_count += 1

    if total_weight == 0.0:
        return 0.0

    return round(matched_weight / total_weight, 4)
