"""Pure (DB-free) ranking tests using component3's CSS engine."""

from app.engine_link import CSSEngine, JobRequirementProfile, build_features


def _rank(candidates):
    engine = CSSEngine(JobRequirementProfile.from_role("Software_Engineer"))
    return engine.rank_pool(candidates)


def test_strong_candidate_ranks_first():
    results = _rank([
        build_features("weak", "Software_Engineer", 1.0, "B.Sc. Computer Science",
                       0.40, 0.5, 0.5, 0.3),
        build_features("strong", "Software_Engineer", 5.0, "M.Sc. Computer Science",
                       0.90, 0.8, 0.75, 0.95),
    ])
    ordered = [r.candidate_id for r in results]
    assert ordered.index("strong") < ordered.index("weak")
    strong = next(r for r in results if r.candidate_id == "strong")
    assert strong.passed_hard_filter and strong.CSS > 0.7
    assert strong.rank == 1


def test_hard_filter_rejects_low_education():
    results = _rank([
        build_features("c", "Software_Engineer", 6.0, "Diploma",
                       0.90, 0.8, 0.8, 0.9),
    ])
    s = results[0]
    assert not s.passed_hard_filter
    assert "Education" in s.filter_fail_reason
    assert s.CSS == 0.0


def test_hard_filter_rejects_insufficient_experience():
    results = _rank([
        build_features("c", "Software_Engineer", 0.5, "B.Sc. Computer Science",
                       0.90, 0.8, 0.8, 0.9),
    ])
    s = results[0]
    assert not s.passed_hard_filter
    assert "Experience" in s.filter_fail_reason


def test_hard_filter_rejects_low_skill():
    results = _rank([
        build_features("c", "Software_Engineer", 5.0, "B.Sc. Computer Science",
                       0.10, 0.8, 0.8, 0.9),
    ])
    s = results[0]
    assert not s.passed_hard_filter
    assert "Skill" in s.filter_fail_reason


def test_rank_assigns_position_to_passed_only():
    results = _rank([
        build_features("strong", "Software_Engineer", 5.0, "M.Sc. Computer Science",
                       0.90, 0.8, 0.75, 0.95),
        build_features("weak", "Software_Engineer", 1.0, "Diploma",
                       0.90, 0.8, 0.8, 0.9),
    ])
    strong = next(r for r in results if r.candidate_id == "strong")
    weak = next(r for r in results if r.candidate_id == "weak")
    assert strong.rank == 1
    assert weak.rank == 0
    assert results[-1].candidate_id == "weak"
