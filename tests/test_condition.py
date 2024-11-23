import unittest

from genruler.modules import basic, condition, string


class ConditionTest(unittest.TestCase):
    def test_equal(self):
        context = {"foo": "bar", "bar": "baz", "baz": "bar"}
        rule = condition.equal("bar", "bar")

        result = rule(context)
        self.assertTrue(result)

        rule = condition.equal(string.field("foo"), "bar")

        result = rule(context)
        self.assertTrue(result)

        rule = condition.equal(string.field("foo"), string.field("baz"))
        result = rule(context)
        self.assertTrue(result)

        rule = condition.equal(string.field(string.field("foo")), string.field("baz"))
        result = rule(context)
        self.assertFalse(result)

    def test_in(self):
        context = {"foo": "lorem"}
        rule = condition.in_(string.field("foo"), ["lorem", "ipsum", "dolor", "sit"])

        result = rule(context)
        self.assertTrue(result)

        rule = condition.in_(string.field("foo"), ["hello", "ipsum", "dolor", "sit"])

        result = rule(context)
        self.assertFalse(result)

        rule = condition.in_("amit", ["lorem", "ipsum", "dolor", "sit"])

        result = rule(context)
        self.assertFalse(result)

    def test_is_none(self):
        context = {"foo": None}
        rule = condition.is_none(None)

        result = rule(context)
        self.assertTrue(result)

        rule = condition.is_none(basic.field("foo"))

        result = rule(context)
        self.assertTrue(context)

        rule = condition.is_none("")

        result = rule(context)
        self.assertFalse(result)

    def test_is_true(self):
        context = {"foo": True}
        rule = condition.is_true(True)

        result = rule(context)
        self.assertTrue(result)

        rule = condition.is_true(basic.field("foo"))

        result = rule(context)
        self.assertTrue(context)

        rule = condition.is_true(1)

        result = rule(context)
        self.assertFalse(result)
