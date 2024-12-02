import unittest

from genruler import library
from genruler.lexer import Symbol


class LibraryTest(unittest.TestCase):
    def test_compute(self):
        context = {"foo": "bar"}
        expected = "bar"

        result = library.compute(lambda context: context["foo"], context)
        self.assertEqual(result, expected)

        arg = "meow"
        expected = "meow"

        result = library.compute(arg, context)
        self.assertEqual(result, expected)

    def test_compute_with_method(self):
        class TestClass:
            def test_method(self, x):
                return x * 2

        obj = TestClass()
        result = library.compute(obj.test_method, 5)
        self.assertEqual(result, 10)

    def test_compute_with_different_contexts(self):
        # Test with different context types
        def fn(x):
            return str(x)

        self.assertEqual(library.compute(fn, 123), "123")
        self.assertEqual(library.compute(fn, [1, 2, 3]), "[1, 2, 3]")
        self.assertEqual(library.compute(fn, {"a": 1}), "{'a': 1}")

    def test_evaluate_basic(self):
        # Test basic value sequence
        sequence = [1, 2, 3]
        result = library.evaluate(sequence, None)
        self.assertEqual(result, (1, 2, 3))

    def test_evaluate_with_function(self):
        # Test with a custom function since genruler functions return callables
        class CustomEnv:
            def add(self, x, y):
                return x + y

        env = CustomEnv()
        sequence = [Symbol("add"), 1, 2]
        result = library.evaluate(sequence, env)
        self.assertEqual(result, 3)

    def test_evaluate_nested(self):
        # Test nested expression with custom function
        class CustomEnv:
            def add(self, x, y):
                return x + y

        env = CustomEnv()
        sequence = [Symbol("add"), [Symbol("add"), 1, 2], 3]
        result = library.evaluate(sequence, env)
        self.assertEqual(result, 6)

    def test_evaluate_with_custom_env(self):
        class CustomEnv:
            def custom_func(self, x):
                return x * 2

        env = CustomEnv()
        sequence = [Symbol("custom_func"), 5]
        result = library.evaluate(sequence, env)
        self.assertEqual(result, 10)

    def test_evaluate_errors(self):
        # Test invalid sequence type
        with self.assertRaises(TypeError):
            library.evaluate("not a list", None)  # type: ignore

        # Test invalid function name
        with self.assertRaises(library.InvalidFunctionNameError):
            library.evaluate([Symbol("nonexistent_function"), 1], None)

    def test_get_function(self):
        class TestEnv:
            def test_func(self):
                return "test"

        env = TestEnv()
        # Test successful function retrieval
        func = library.get_function("test_func", env)
        self.assertEqual(func(), "test")

        # Test function not found
        with self.assertRaises(library.InvalidFunctionNameError):
            library.get_function("nonexistent", env)

        # Test None environment
        with self.assertRaises(library.InvalidFunctionNameError):
            library.get_function("any_func", None)

    def test_get_genruler_function(self):
        # Test getting a valid function
        func = library.get_genruler_function("number", "add")
        self.assertTrue(callable(func))

        # Test function with underscore
        func = library.get_genruler_function("number", "subtract")
        self.assertTrue(callable(func))

        # Test invalid module
        with self.assertRaises(ImportError):
            library.get_genruler_function("nonexistent_module", "func")

        # Test invalid function
        with self.assertRaises(AttributeError):
            library.get_genruler_function("number", "nonexistent_function")
