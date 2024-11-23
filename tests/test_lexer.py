import pytest

from genruler import parse


def test_simple_expression():
    result = parse("(boolean.tautology)", use_hy=False)
    assert callable(result), "Result should be callable"
    assert result({}) is True, "boolean.tautology should return True"


def test_nested_expression():
    result = parse(
        "(boolean.and (boolean.tautology) (boolean.tautology))", use_hy=False
    )
    assert callable(result), "Result should be callable"
    assert result({}) is True, "Nested AND of two True values should be True"


def test_complex_expression():
    result = parse(
        "(boolean.or (boolean.and (boolean.tautology) (boolean.contradiction)) (boolean.tautology))",
        use_hy=False,
    )
    assert callable(result), "Result should be callable"
    assert result({}) is True, "Complex boolean expression should evaluate correctly"


def test_reject_atom():
    with pytest.raises(ValueError, match="Parse error"):
        parse(
            "boolean.tautology", use_hy=False
        )  # Should fail - not wrapped in parentheses
