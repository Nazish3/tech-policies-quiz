import pytest
from quiz.utils import normalise_name, is_valid_name, score_percentage


def test_normalise_name_trims_and_collapses_spaces():
    assert normalise_name("  Nazish   Jujara ") == "Nazish Jujara"


@pytest.mark.parametrize("name,expected", [
    ("Nazish", True),
    ("Nazish Jujara", True),
    ("N", False),
    ("", False),
    ("Nazish123", False),
    ("O'Connor", True),
    ("Mary-Jane", True),
])
def test_is_valid_name(name, expected):
    assert is_valid_name(name) == expected


def test_score_percentage():
    assert score_percentage(3, 4) == 75


def test_score_percentage_raises_on_invalid_total():
    with pytest.raises(ValueError):
        score_percentage(1, 0)


def test_score_percentage_raises_on_invalid_score():
    with pytest.raises(ValueError):
        score_percentage(10, 4)