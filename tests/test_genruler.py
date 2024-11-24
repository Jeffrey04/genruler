import pytest

import genruler as ruler
from genruler.modules import basic, boolean, condition, number, string


def test_parse():
    context = {"foo": "bar", "bar": ["foo", "bar"], "one": 1}

    rule = "(boolean.tautology)"
    expected = boolean.tautology()

    result = ruler.parse(rule)
    assert result(context) == expected(context)

    rule = "(boolean.and (boolean.tautology) (boolean.tautology))"
    expected = boolean.and_(boolean.tautology(), boolean.tautology())

    result = ruler.parse(rule)
    assert result(context) == expected(context)

    rule = """
    (boolean.and (boolean.tautology)
                (condition.equal (string.field "foo") "bar"))
    """

    expected = boolean.and_(
        boolean.tautology(),
        condition.equal(string.field("foo"), "bar"),
    )

    result = ruler.parse(rule)
    assert result(context) == expected(context)

    rule = '(condition.in "foo" ("foo" "bar"))'
    expected = condition.in_("foo", ["foo", "bar"])

    result = ruler.parse(rule)
    assert result(context) == expected(context)

    non_rule = '(and "foo" "bar")'

    with pytest.raises(AssertionError):
        result = ruler.parse(non_rule)

    rule = "(basic.value)"

    with pytest.raises(TypeError):
        result = ruler.parse(rule)

    rule = '(condition.in "foo" (basic.field "bar"))'
    expected = condition.in_("foo", basic.field("bar"))

    result = ruler.parse(rule)
    assert result(context) == expected(context)

    rule = '(number.add 1 (basic.field "one"))'
    expected = number.add(1, basic.field("one"))

    result = ruler.parse(rule)
    assert result(context) == expected(context)