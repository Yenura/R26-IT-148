from app.engine_link import (
    build_features,
    edu_to_css,
    normalise_role,
    role_display_name,
)


def test_normalise_role_title_case():
    assert normalise_role("Software Engineer") == "Software_Engineer"
    assert normalise_role("Data Scientist") == "Data_Scientist"


def test_normalise_role_snake_case():
    assert normalise_role("Software_Engineer") == "Software_Engineer"
    assert normalise_role("data_scientist") == "Data_Scientist"


def test_normalise_role_insensitive():
    assert normalise_role("DEVOPS ENGINEER") == "DevOps_Engineer"


def test_normalise_role_unknown():
    import pytest

    with pytest.raises(ValueError):
        normalise_role("Astronaut")


def test_role_display_name():
    assert role_display_name("Software_Engineer") == "Software Engineer"


def test_edu_to_css_levels():
    assert edu_to_css("Ph.D. Artificial Intelligence") == 4
    assert edu_to_css("PhD") == 4
    assert edu_to_css("M.Sc. Data Science") == 3
    assert edu_to_css("MBA") == 3
    assert edu_to_css("B.Sc. Computer Science") == 2
    assert edu_to_css("Diploma") == 1
    assert edu_to_css("Bootcamp + Self-Taught") == 1
    assert edu_to_css(None) == 1
    assert edu_to_css("") == 1


def test_build_features_clamps_ranges():
    f = build_features(
        candidate_id="c1",
        role_key="Software_Engineer",
        experience_years=9,
        education="B.Sc. Computer Science",
        skill_score_raw=2.0,
        p_mcq=-0.2,
        p_desc=0.5,
        p_code=1.5,
        edu_relevance=2.0,
    )
    assert f.years_experience == 9.0
    assert f.skill_score_raw == 1.0
    assert f.P_mcq == 0.0
    assert f.P_code == 1.0
    assert f.edu_relevance == 1.0
    assert f.edu_level == 2
