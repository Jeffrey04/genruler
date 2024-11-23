import unittest

from genruler.modules import basic, boolean


class BooleanTest(unittest.TestCase):
    def test_and(self):
        context = {}
        rule = boolean.and_(True, True)

        result = rule(context)
        self.assertTrue(result)

        rule = boolean.and_(True, False)

        result = rule(context)
        self.assertFalse(result)

        rule = boolean.and_(False, True)

        result = rule(context)
        self.assertFalse(result)

        rule = boolean.and_(False, False)

        result = rule(context)
        self.assertFalse(result)

        rule = boolean.and_(True, True, False)

        result = rule(context)
        self.assertFalse(result)

        rule = boolean.and_(True, True, True)

        result = rule(context)
        self.assertTrue(result)

        rule = boolean.and_(True, basic.value(True), True)

        result = rule(context)
        self.assertTrue(result)

    def test_contradiction(self):
        context = {}
        rule = boolean.contradiction()

        result = rule(context)
        self.assertFalse(result)

    def test_not(self):
        context = {}
        rule = boolean.not_(True)

        result = rule(context)
        self.assertFalse(result)

        rule = boolean.not_(basic.value(True))

        result = rule(context)
        self.assertFalse(result)

    def test_or(self):
        context = {}
        rule = boolean.or_(True, True)

        result = rule(context)
        self.assertTrue(result)

        rule = boolean.or_(True, False)

        result = rule(context)
        self.assertTrue(result)

        rule = boolean.or_(False, True)

        result = rule(context)
        self.assertTrue(result)

        rule = boolean.or_(False, False)

        result = rule(context)
        self.assertFalse(result)

        rule = boolean.or_(True, True, False)

        result = rule(context)
        self.assertTrue(result)

        rule = boolean.or_(True, True, True)

        result = rule(context)
        self.assertTrue(result)

        rule = boolean.or_(True, basic.value(True), True)

        result = rule(context)
        self.assertTrue(result)

    def test_tautology(self):
        context = {}
        rule = boolean.tautology()

        result = rule(context)
        self.assertTrue(result)
