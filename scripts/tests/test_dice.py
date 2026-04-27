import sys
import os
import re
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dice import roll, parse_notation, DiceResult


def test_single_die_returns_value_in_range():
    result = roll("1d6")
    assert 1 <= result.total <= 6


def test_multiple_dice_returns_value_in_range():
    result = roll("3d6")
    assert 3 <= result.total <= 18
    assert len(result.rolls) == 3


def test_modifier_added_correctly():
    result = roll("1d1+5")
    assert result.total == 6
    assert result.rolls == [1]
    assert result.modifier == 5


def test_negative_modifier():
    result = roll("1d1-3")
    assert result.total == -2


def test_advantage_returns_higher_of_two():
    # With 1d1 both rolls are 1, so advantage total == 1
    result = roll("2d1 advantage")
    assert result.total == 1
    assert len(result.rolls) == 2
    assert result.kept == [1]


def test_disadvantage_returns_lower_of_two():
    result = roll("2d1 disadvantage")
    assert result.total == 1
    assert len(result.rolls) == 2


def test_keep_highest(monkeypatch):
    # Mock random to return predictable values
    import dice as dice_module
    call_count = [0]
    values = [3, 5, 1, 6]
    def mock_randint(a, b):
        val = values[call_count[0] % len(values)]
        call_count[0] += 1
        return val
    monkeypatch.setattr(dice_module.random, "randint", mock_randint)
    result = roll("4d6kh3")
    assert result.kept == sorted([3, 5, 1, 6], reverse=True)[:3]
    assert result.total == sum(sorted([3, 5, 1, 6], reverse=True)[:3])


def test_invalid_notation_raises():
    with pytest.raises(ValueError, match="Invalid dice notation"):
        roll("banana")


def test_result_has_breakdown_string():
    result = roll("1d1+2")
    assert "1" in result.breakdown
    assert "2" in result.breakdown
    assert "3" in result.breakdown


def test_d20_range():
    for _ in range(20):
        result = roll("1d20")
        assert 1 <= result.total <= 20


def test_parse_notation_basic():
    count, sides, modifier, mode, keep = parse_notation("3d8+2")
    assert count == 3
    assert sides == 8
    assert modifier == 2
    assert mode is None


def test_parse_notation_advantage():
    count, sides, modifier, mode, keep = parse_notation("2d20 advantage")
    assert mode == "advantage"


def test_parse_notation_keep_highest():
    count, sides, modifier, mode, keep = parse_notation("4d6kh3")
    assert keep == ("highest", 3)
