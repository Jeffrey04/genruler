import unittest

from genruler import library


class LibraryTest(unittest.TestCase):
    def test_compute(self):
        context = {"foo": "bar"}
        arg = lambda context: context["foo"]
        expected = "bar"

        result = library.compute(arg, context)
        self.assertEqual(result, expected)

        arg = "meow"
        expected = "meow"

        result = library.compute(arg, context)
        self.assertEqual(result, expected)
