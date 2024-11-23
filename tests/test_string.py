import unittest

from genruler.modules import basic, string


class StringTest(unittest.TestCase):
    def test_concat(self):
        context = {"foo": "hello", "bar": "world"}
        rule = string.concat(" ", "hello", "world")
        expected = "hello world"

        result = rule(context)
        self.assertEqual(result, expected)

        rule = string.concat(basic.value(" "), string.field("foo"), "world")

        result = rule(context)
        self.assertEqual(result, expected)

        rule = string.concat(basic.value(" "), string.field("foo"), string.field("bar"))

        result = rule(context)
        self.assertEqual(result, expected)

    def test_concat_fields(self):
        context = {"foo": "hello", "bar": "world"}
        rule = string.concat_fields(" ", "foo", "bar")
        expected = "hello world"

        result = rule(context)
        self.assertEqual(result, expected)

        context = {"foo": "hello", "bar": "world"}
        rule = string.concat_fields(basic.value(" "), "foo", "bar")
        expected = "hello world"

        result = rule(context)
        self.assertEqual(result, expected)

    def test_field(self):
        context = {"foo": "bar"}
        rule = string.field("foo")
        expected = "bar"

        result = rule(context)
        self.assertEqual(result, expected)

        rule = string.field("bar", "baz")
        expected = "baz"

        result = rule(context)
        self.assertEqual(result, expected)

        with self.assertRaises(KeyError):
            rule = string.field("bar")

            result = rule(context)

    def test_lower(self):
        context = {"foo": "Hello from the OTHER side"}
        rule = string.lower("Hello from the OTHER side")
        expected = "hello from the other side"

        result = rule(context)
        self.assertEqual(result, expected)

        rule = string.lower(string.field("foo"))

        result = rule(context)
        self.assertEqual(result, expected)
