import pytest

import genruler as ruler
from genruler.exceptions import InvalidFunctionNameError, NonCallableResultError
from genruler.modules import basic, boolean, condition, number, string


def test_parse_simple_expression():
    """Test parsing a simple S-expression with no context needed."""
    rule = "(number.add 1 2)"
    result = ruler.parse(rule)
    assert result({}) == 3


def test_parse_with_context():
    """Test parsing expressions that use context values."""
    context = {"foo": "bar", "bar": ["foo", "bar"], "one": 1}

    # Test with field access
    rule = '(number.add 1 (basic.field "one"))'
    result = ruler.parse(rule)
    assert result(context) == 2

    # Test with nested field access
    rule = '(condition.in "foo" (basic.field "bar"))'
    result = ruler.parse(rule)
    assert result(context) is True


def test_parse_with_env():
    """Test parsing with a custom environment module."""
    class TestModule:
        @staticmethod
        def custom_func():
            return lambda ctx: "success"
    
    rule = "(custom_func)"
    result = ruler.parse(rule, env=TestModule)
    assert result({}) == "success"


def test_parse_complex_boolean():
    """Test parsing complex boolean expressions."""
    context = {"foo": "bar"}
    
    # Test nested boolean operations
    rule = "(boolean.and (boolean.tautology) (boolean.tautology))"
    result = ruler.parse(rule)
    assert result(context) is True

    # Test with condition
    rule = """
    (boolean.and (boolean.tautology)
                (condition.equal (string.field "foo") "bar"))
    """
    result = ruler.parse(rule)
    assert result(context) is True


def test_parse_errors():
    """Test various error conditions in parsing."""
    # Test invalid function name
    with pytest.raises(InvalidFunctionNameError) as excinfo:
        ruler.parse('(and "foo" "bar")')
    assert "must be in format 'module.function'" in str(excinfo.value)

    # Test non-callable result with a list of numbers
    with pytest.raises(NonCallableResultError) as excinfo:
        ruler.parse("(1 2 3 4)")
    assert "Parse result must be callable" in str(excinfo.value)