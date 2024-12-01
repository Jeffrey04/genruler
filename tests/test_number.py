import unittest

from genruler.modules import number


class NumberTest(unittest.TestCase):
    def test_add(self):
        # Test with direct numbers
        func = number.add(2, 3)
        self.assertEqual(func({}), 5)

        # Test with multiple numbers
        func = number.add(1, 2, 3, 4)
        self.assertEqual(func({}), 10)

        # Test with callable arguments
        func = number.add(lambda x: 5, lambda x: 3)
        self.assertEqual(func({}), 8)

        # Test with context values
        func = number.add(lambda ctx: ctx["a"], lambda ctx: ctx["b"])
        self.assertEqual(func({"a": 10, "b": 20}), 30)

    def test_subtract(self):
        # Test with direct numbers
        func = number.subtract(10, 3)
        self.assertEqual(func({}), 7)

        # Test with multiple numbers (left-to-right subtraction)
        func = number.subtract(20, 5, 3)
        self.assertEqual(func({}), 12)  # 20 - 5 - 3 = 12

        # Test with callable arguments
        func = number.subtract(lambda x: 10, lambda x: 4)
        self.assertEqual(func({}), 6)

        # Test with context values
        func = number.subtract(lambda ctx: ctx["total"], lambda ctx: ctx["deduction"])
        self.assertEqual(func({"total": 100, "deduction": 25}), 75)

    def test_multiply(self):
        # Test with direct numbers
        func = number.multiply(4, 3)
        self.assertEqual(func({}), 12)

        # Test with multiple numbers
        func = number.multiply(2, 3, 4)
        self.assertEqual(func({}), 24)

        # Test with callable arguments
        func = number.multiply(lambda x: 5, lambda x: 6)
        self.assertEqual(func({}), 30)

        # Test with context values
        func = number.multiply(lambda ctx: ctx["quantity"], lambda ctx: ctx["price"])
        self.assertEqual(func({"quantity": 5, "price": 10}), 50)

    def test_divide(self):
        # Test with direct numbers
        func = number.divide(12, 3)
        self.assertEqual(func({}), 4.0)

        # Test with multiple numbers (left-to-right division)
        func = number.divide(100, 2, 5)
        self.assertEqual(func({}), 10.0)  # 100 / 2 / 5 = 10

        # Test with callable arguments
        func = number.divide(lambda x: 15, lambda x: 3)
        self.assertEqual(func({}), 5.0)

        # Test with context values
        func = number.divide(lambda ctx: ctx["total"], lambda ctx: ctx["parts"])
        self.assertEqual(func({"total": 100, "parts": 4}), 25.0)

        # Test division by zero
        func = number.divide(10, 0)
        with self.assertRaises(ZeroDivisionError):
            func({})

    def test_modulo(self):
        # Test with direct numbers
        func = number.modulo(17, 5)
        self.assertEqual(func({}), 2)

        # Test with multiple numbers (left-to-right modulo)
        func = number.modulo(100, 30, 7)
        self.assertEqual(func({}), 3)  # (100 % 30) % 7 = 3

        # Test with callable arguments
        func = number.modulo(lambda x: 23, lambda x: 7)
        self.assertEqual(func({}), 2)

        # Test with context values
        func = number.modulo(lambda ctx: ctx["items"], lambda ctx: ctx["per_page"])
        self.assertEqual(func({"items": 47, "per_page": 10}), 7)

        # Test modulo by zero
        func = number.modulo(10, 0)
        with self.assertRaises(ZeroDivisionError):
            func({})
