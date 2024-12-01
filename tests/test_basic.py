import unittest

from genruler.modules import basic


class BasicTest(unittest.TestCase):
    def test_coalesce(self):
        context = {}
        func = basic.coalesce(None, "hello world")
        expected = "hello world"

        result = func(context)
        self.assertEqual(result, expected)

        func = basic.coalesce("", "hello world")

        result = func(context)
        self.assertEqual(result, expected)

        func = basic.coalesce("", None)
        expected = None

        result = func(context)
        self.assertEqual(result, expected)

        func = basic.coalesce(None, "")
        expected = ""

        result = func(context)
        self.assertEqual(result, expected)

    def test_coalesce_with_callables(self):
        # Test with callable values
        context = {"status": "active"}
        func = basic.coalesce(
            lambda ctx: ctx.get("nonexistent"),
            lambda ctx: ctx["status"],
            "default"
        )
        self.assertEqual(func(context), "active")

        # Test with more than two arguments
        func = basic.coalesce(None, False, 0, "", [], {}, "found")
        self.assertEqual(func(context), "found")

        # Test with mixed types
        context = {"count": 0, "empty": "", "false": False}
        func = basic.coalesce(
            lambda ctx: ctx["count"],
            lambda ctx: ctx["empty"],
            lambda ctx: ctx["false"],
            "fallback"
        )
        self.assertEqual(func(context), "fallback")

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

    def test_context_nested(self):
        # Test nested contexts
        context = {
            "user": {
                "profile": {
                    "settings": {
                        "theme": "dark"
                    }
                }
            }
        }
        func = basic.context(
            basic.field("user"),
            basic.context(
                basic.field("profile"),
                basic.field("settings")
            )
        )
        self.assertEqual(func(context)["theme"], "dark")

        # Test with non-existent keys
        with self.assertRaises(KeyError):
            func = basic.context(
                basic.field("nonexistent"),
                basic.field("key")
            )
            func(context)

        # Test with different argument types
        context = {"data": {"value": 42}}
        func = basic.context(
            basic.field("data"),
            basic.value(123)  # Using value instead of field
        )
        self.assertEqual(func(context), 123)

    def test_coalesce_error_handling(self):
        # Test error propagation from context access
        context = {}
        func = basic.coalesce(
            lambda ctx: ctx["nonexistent"],  # This will raise KeyError
            "fallback"
        )
        # The error should propagate since it's an actual error, not a falsy value
        with self.assertRaises(KeyError):
            func(context)

        # Test with multiple falsy values followed by truthy
        context = {"items": [0, "", False, None, "found", "ignored"]}
        func = basic.coalesce(
            lambda ctx: ctx["items"][0],  # 0
            lambda ctx: ctx["items"][1],  # ""
            lambda ctx: ctx["items"][2],  # False
            lambda ctx: ctx["items"][3],  # None
            lambda ctx: ctx["items"][4],  # "found"
            lambda ctx: ctx["items"][5]   # "ignored"
        )
        self.assertEqual(func(context), "found")

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

        func = basic.field("lorem", None)
        expected = None

        result = func(context)
        self.assertEqual(result, expected)

        with self.assertRaises(KeyError):
            func = basic.field("lorem")

            result = func(context)

    def test_field_advanced_indexing(self):
        # Test with negative indices
        context = ["a", "b", "c"]
        func = basic.field(-1)
        self.assertEqual(func(context), "c")
        func = basic.field(-2)
        self.assertEqual(func(context), "b")

        # Test with computed negative indices
        func = basic.field(lambda ctx: -1)
        self.assertEqual(func(context), "c")

        # Test with invalid index type
        with self.assertRaises((TypeError, AttributeError)):
            context = ["a", "b", "c"]
            func = basic.field(object())  # object() can't be used as an index
            func(context)

    def test_field_computed_index(self):
        # Test with computed list indices
        context = ["a", "b", "c", "d"]
        func = basic.field(lambda ctx: 2)  # Access index 2
        self.assertEqual(func(context), "c")

        # Test with out of range computed index
        with self.assertRaises(IndexError):
            func = basic.field(lambda ctx: 10)
            func(context)

    def test_field_error_propagation(self):
        context = {"items": [1, 2, 3]}

        # Test error in callable key
        func = basic.field(lambda ctx: ctx["nonexistent"])  # This will raise KeyError
        with self.assertRaises(KeyError):
            func(context)

        # Test with non-string/non-int keys
        context = {("tuple", "key"): "value"}
        func = basic.field(("tuple", "key"))
        self.assertEqual(func(context), "value")

        # Test default value with error in callable
        context = {"items": [1, 2, 3]}
        func = basic.field(
            "missing",
            lambda ctx: 1/0  # This will raise ZeroDivisionError
        )
        with self.assertRaises(ZeroDivisionError):
            func(context)

    def test_field_list(self):
        context = ["lorem", "ipsum"]
        func = basic.field(0)
        expected = "lorem"

        result = func(context)
        self.assertEqual(result, expected)

        with self.assertRaises(IndexError):
            func = basic.field(3)

            result = func(context)

    def test_field_nested(self):
        # Test with nested dictionaries
        context = {
            "user": {
                "profile": {
                    "name": "John"
                }
            }
        }
        func = basic.field("user")
        result = func(context)
        self.assertEqual(result["profile"]["name"], "John")

        # Test with complex default values
        context = {"items": [1, 2, 3]}
        func = basic.field("count", lambda ctx: len(ctx["items"]))
        self.assertEqual(func(context), 3)

        # Test with different key types
        context = {42: "number-key", True: "bool-key"}
        func = basic.field(42)
        self.assertEqual(func(context), "number-key")
        func = basic.field(True)
        self.assertEqual(func(context), "bool-key")

    def test_value(self):
        context = {}

        # Test literal values
        func = basic.value(42)
        self.assertEqual(func(context), 42)

        func = basic.value("active")
        self.assertEqual(func(context), "active")

        # Test tuple values
        func = basic.value(("a", "b", "c"))
        self.assertEqual(func(context), ("a", "b", "c"))

        # Test invalid sub-rule
        with self.assertRaises(ValueError) as exc_info:
            basic.value(basic.field("status"))

        self.assertIn("basic.value cannot accept sub-rules", str(exc_info.exception))

    def test_value_complex(self):
        context = {}

        # Test with complex immutable types
        func = basic.value({"key": "value"})
        self.assertEqual(func(context), {"key": "value"})

        func = basic.value([1, 2, 3])
        self.assertEqual(func(context), [1, 2, 3])

        # Test with None value
        func = basic.value(None)
        self.assertIsNone(func(context))

        # Test with bool values
        func = basic.value(True)
        self.assertTrue(func(context))
        func = basic.value(False)
        self.assertFalse(func(context))
