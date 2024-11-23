import unittest

from genruler.modules import basic


class BasicTest(unittest.TestCase):
    def test_context(self):
        context = {"sub": {"foo": "bar"}}
        func = basic.context(basic.field("sub"), basic.field("foo"))
        expected = "bar"

        result = func(context)
        self.assertEqual(result, expected)

        context_sub = {"foo": "bar"}
        func = basic.context(context_sub, basic.field("foo"))
        expected = "bar"

        result = func(context)
        self.assertEqual(result, expected)

    def test_field(self):
        context = {"foo": "bar", "baz": "foo"}
        func = basic.field("foo")
        expected = "bar"

        result = func(context)
        self.assertEqual(result, expected)

        func = basic.field("lorem", "meow")
        expected = "meow"

        result = func(context)
        self.assertEqual(result, expected)

        try:
            func = basic.field("lorem", None)
            expected = None

            result = func(context)
            self.assertEqual(result, expected)
        except KeyError:
            self.fail("rule triggered keyError")

        with self.assertRaises(KeyError):
            func = basic.field("lorem")

            result = func(context)

    def test_field_list(self):
        context = ["lorem", "ipsum"]
        func = basic.field(0)
        expected = "lorem"

        result = func(context)
        self.assertEqual(result, expected)

        with self.assertRaises(IndexError):
            func = basic.field(3)

            result = func(context)

    def test_value(self):
        context = {}
        func = basic.value("Foo")
        expected = "Foo"

        result = func(context)
        self.assertEqual(result, expected)
