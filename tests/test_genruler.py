import pytest

import genruler as ruler
from genruler.modules import basic, boolean, condition, number, string


def test_parse():
    context = {"foo": "bar", "bar": ["foo", "bar"], "one": 1}

    rule = "(boolean.tautology)"
    expected = boolean.tautology()

    result = ruler.parse(rule, use_hy=True)
    assert result(context) == expected(context)

    rule = "(boolean.and (boolean.tautology) (boolean.tautology))"
    expected = boolean.and_(boolean.tautology(), boolean.tautology())

    result = ruler.parse(rule, use_hy=True)
    assert result(context) == expected(context)

    rule = """
    (boolean.and (boolean.tautology)
                (condition.equal (string.field "foo") "bar"))
    """

    expected = boolean.and_(
        boolean.tautology(),
        condition.equal(string.field("foo"), "bar"),
    )

    result = ruler.parse(rule, use_hy=True)
    assert result(context) == expected(context)

    rule = '(condition.in "foo" ("foo" "bar"))'
    expected = condition.in_("foo", ["foo", "bar"])

    result = ruler.parse(rule, use_hy=True)
    assert result(context) == expected(context)

    non_rule = '(and "foo" "bar")'

    with pytest.raises(AssertionError):
        result = ruler.parse(non_rule, use_hy=True)

    rule = "(basic.value)"

    with pytest.raises(TypeError):
        result = ruler.parse(rule, use_hy=True)

    rule = '(condition.in "foo" (basic.field "bar"))'
    expected = condition.in_("foo", basic.field("bar"))

    result = ruler.parse(rule, use_hy=True)
    assert result(context) == expected(context)

    rule = '(number.add 1 (basic.field "one"))'
    expected = number.add(1, basic.field("one"))

    result = ruler.parse(rule, use_hy=True)
    assert result(context) == expected(context)


def test_parse2():
    context = {"foo": "bar", "bar": ["foo", "bar"]}

    # Test simple function call
    rule = "(boolean.tautology)"
    expected = boolean.tautology()

    result = ruler.parse(rule, use_hy=False)
    assert result(context) == expected(context)

    # Test nested function calls
    rule = "(boolean.and (boolean.tautology) (boolean.tautology))"
    expected = boolean.and_(boolean.tautology(), boolean.tautology())

    result = ruler.parse(rule, use_hy=False)
    assert result(context) == expected(context)

    # Test multi-line complex expression
    rule = """
    (boolean.and (boolean.tautology)
                (condition.equal (string.field "foo") "bar"))
    """

    expected = boolean.and_(
        boolean.tautology(),
        condition.equal(string.field("foo"), "bar"),
    )

    result = ruler.parse(rule, use_hy=False)
    assert result(context) == expected(context)

    # Test list arguments
    rule = '(condition.in "foo" ("foo" "bar"))'
    expected = condition.in_("foo", ["foo", "bar"])

    result = ruler.parse(rule, use_hy=False)
    assert result(context) == expected(context)

    # Test error cases
    non_rule = '(and "foo" "bar")'

    with pytest.raises(AssertionError):
        result = ruler.parse(non_rule, use_hy=False)

    rule = "(basic.value)"

    with pytest.raises(TypeError):
        result = ruler.parse(rule, use_hy=False)

    # Test nested field access
    rule = '(condition.in "foo" (basic.field "bar"))'
    expected = condition.in_("foo", basic.field("bar"))

    result = ruler.parse(rule, use_hy=False)
    assert result(context) == expected(context)
