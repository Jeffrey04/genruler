import pytest

import genruler
from genruler.exceptions import (
    InvalidFunctionNameError,
)


class TestQuickStart:
    def test_basic_condition(self):
        rule = genruler.parse('(condition.equal (basic.field "name") "John")')
        result = rule({"name": "John"})
        assert result is True


class TestBasicFunctions:
    def test_coalesce_simple(self):
        rule = genruler.parse('(basic.coalesce "" "value" "other")')
        result = rule({})
        assert result == "value"

    def test_coalesce_nested(self):
        rule = genruler.parse(
            '(basic.coalesce (basic.field "a") (basic.field "b") "default")'
        )
        result = rule({"b": "value", "a": None})
        assert result == "value"

    def test_context_nested_object(self):
        rule = genruler.parse(
            '(basic.context (basic.field "user") (basic.field "name"))'
        )
        result = rule({"user": {"name": "John"}})
        assert result == "John"

    def test_context_multiple_levels(self):
        rule = genruler.parse(
            '(basic.context (basic.field "data") (basic.context (basic.field "user") (basic.field "email")))'
        )
        result = rule({"data": {"user": {"email": "john@example.com"}}})
        assert result == "john@example.com"

    def test_field_dictionary_access(self):
        rule = genruler.parse('(basic.field "name")')
        result = rule({"name": "John"})
        assert result == "John"

    def test_field_with_default(self):
        rule = genruler.parse('(basic.field "age" 0)')
        result = rule({})
        assert result == 0

    def test_field_list_access(self):
        rule = genruler.parse("(basic.field 0)")
        result = rule(["first", "second"])
        assert result == "first"


class TestBasicValue:
    def test_literal_values(self):
        # Numbers
        rule = genruler.parse("(basic.value 42)")
        assert rule({}) == 42

        # Strings
        rule = genruler.parse('(basic.value "active")')
        assert rule({}) == "active"

        # Tuples (from list syntax)
        rule = genruler.parse('(basic.value ("a" "b" "c"))')
        assert rule({}) == ("a", "b", "c")

    def test_constant_comparison(self):
        rule = genruler.parse(
            '(condition.equal (basic.field "status") (basic.value "active"))'
        )
        assert rule({"status": "active"}) is True
        assert rule({"status": "inactive"}) is False

    def test_subrule_not_allowed(self):
        with pytest.raises(ValueError) as exc_info:
            rule = genruler.parse('(basic.value (basic.field "status"))')
        assert "basic.value cannot accept sub-rules" in str(exc_info.value)


class TestNumberFunctions:
    def test_add_simple(self):
        rule = genruler.parse("(number.add 1 2 3)")
        result = rule({})
        assert result == 6

    def test_add_fields(self):
        rule = genruler.parse('(number.add (basic.field "price") (basic.field "tax"))')
        result = rule({"price": 100, "tax": 20})
        assert result == 120

    def test_subtract(self):
        rule = genruler.parse("(number.subtract 10 3)")
        result = rule({})
        assert result == 7

    def test_multiply(self):
        rule = genruler.parse("(number.multiply 2 3 4)")
        result = rule({})
        assert result == 24

    def test_divide(self):
        rule = genruler.parse("(number.divide 10 2)")
        result = rule({})
        assert result == 5.0

    def test_modulo(self):
        rule = genruler.parse("(number.modulo 7 3)")
        result = rule({})
        assert result == 1


class TestBooleanFunctions:
    def test_and(self):
        rule = genruler.parse(
            '(boolean.and (condition.gt (basic.field "age") 18) (condition.equal (basic.field "verified") (boolean.tautology)))'
        )
        result = rule({"age": 21, "verified": True})
        assert result is True

    def test_or(self):
        rule = genruler.parse(
            '(boolean.or (condition.equal (basic.field "role") "admin") (condition.equal (basic.field "role") "moderator"))'
        )
        result = rule({"role": "admin"})
        assert result is True

    def test_not(self):
        rule = genruler.parse(
            '(boolean.not (condition.equal (basic.field "status") "blocked"))'
        )
        result = rule({"status": "active"})
        assert result is True

    def test_tautology(self):
        rule = genruler.parse("(boolean.tautology)")
        result = rule({})
        assert result is True

    def test_contradiction(self):
        rule = genruler.parse("(boolean.contradiction)")
        result = rule({})
        assert result is False

    def test_not_field(self):
        rule = genruler.parse('(boolean.not (basic.field "disabled"))')
        result = rule({"disabled": False})
        assert result is True

        result = rule({"disabled": True})
        assert result is False


class TestConditionFunctions:
    def test_equal(self):
        rule = genruler.parse('(condition.equal (basic.field "name") "John")')
        result = rule({"name": "John"})
        assert result is True

    def test_equal_fields(self):
        rule = genruler.parse(
            '(condition.equal (basic.field "password") (basic.field "confirm"))'
        )
        result = rule({"password": "secret", "confirm": "secret"})
        assert result is True

    def test_in_constant(self):
        rule = genruler.parse(
            '(condition.in (basic.value "apple") (basic.value ("apple" "banana" "orange")))'
        )
        result = rule({})
        assert result is True

    def test_in_fields(self):
        rule = genruler.parse(
            '(condition.in (basic.field "fruit") (basic.field "allowed"))'
        )
        result = rule({"fruit": "apple", "allowed": ["apple", "banana"]})
        assert result is True

    def test_is_none(self):
        rule = genruler.parse('(condition.is_none (basic.field "optional"))')
        result = rule({"optional": None})
        assert result is True

    def test_is_none_nested(self):
        rule = genruler.parse('(basic.context (basic.field "user") (condition.is_none (basic.field "email")))')
        result = rule({"user": {"email": None}})
        assert result is True

    def test_is_true(self):
        rule = genruler.parse('(condition.is_true (basic.field "active"))')
        result = rule({"active": True})
        assert result is True

    def test_is_true_truthy(self):
        rule = genruler.parse('(condition.is_true (basic.field "count"))')
        result = rule({"count": 1})
        assert result is False

    def test_greater_than(self):
        rule = genruler.parse('(condition.gt (basic.field "age") 18)')
        result = rule({"age": 21})
        assert result is True

    def test_greater_than_fields(self):
        rule = genruler.parse(
            '(condition.gt (basic.field "score") (basic.field "threshold"))'
        )
        result = rule({"score": 85, "threshold": 70})
        assert result is True

    def test_greater_equal(self):
        rule = genruler.parse('(condition.ge (basic.field "age") 18)')
        result = rule({"age": 18})
        assert result is True

    def test_greater_equal_fields(self):
        rule = genruler.parse(
            '(condition.ge (basic.field "score") (basic.field "passing"))'
        )
        result = rule({"score": 70, "passing": 70})
        assert result is True

    def test_less_than(self):
        rule = genruler.parse('(condition.lt (basic.field "age") 18)')
        result = rule({"age": 17})
        assert result is True

    def test_less_than_fields(self):
        rule = genruler.parse(
            '(condition.lt (basic.field "score") (basic.field "threshold"))'
        )
        result = rule({"score": 60, "threshold": 70})
        assert result is True

    def test_less_equal(self):
        rule = genruler.parse('(condition.le (basic.field "age") 18)')
        result = rule({"age": 18})
        assert result is True

    def test_less_equal_fields(self):
        rule = genruler.parse(
            '(condition.le (basic.field "score") (basic.field "passing"))'
        )
        result = rule({"score": 70, "passing": 70})
        assert result is True


class TestStringFunctions:
    def test_concat(self):
        rule = genruler.parse('(string.concat "," "a" "b" "c")')
        result = rule({})
        assert result == "a,b,c"

    def test_concat_with_fields(self):
        rule = genruler.parse(
            '(string.concat " " (basic.field "first") (basic.field "last"))'
        )
        result = rule({"first": "John", "last": "Doe"})
        assert result == "John Doe"

    def test_concat_fields(self):
        rule = genruler.parse('(string.concat_fields "," "first" "last")')
        result = rule({"first": "John", "last": "Doe"})
        assert result == "John,Doe"

    def test_concat_fields_multiple(self):
        rule = genruler.parse('(string.concat_fields " - " "city" "state" "country")')
        result = rule({"city": "San Francisco", "state": "CA", "country": "USA"})
        assert result == "San Francisco - CA - USA"

    def test_string_field(self):
        rule = genruler.parse('(string.field "name")')
        result = rule({"name": "John"})
        assert result == "John"

    def test_string_field_number(self):
        rule = genruler.parse('(string.field "age")')
        result = rule({"age": 25})
        assert result == "25"

    def test_string_field_default(self):
        rule = genruler.parse('(string.field "missing" "N/A")')
        result = rule({})
        assert result == "N/A"

    def test_lower(self):
        rule = genruler.parse('(string.lower "HELLO")')
        result = rule({})
        assert result == "hello"

    def test_lower_field(self):
        rule = genruler.parse('(string.lower (basic.field "name"))')
        result = rule({"name": "JOHN"})
        assert result == "john"


class TestListFunctions:
    def test_length_direct(self):
        rule = genruler.parse('(list.length (basic.value ("a" "b" "c")))')
        result = rule({})
        assert result == 3

    def test_length_field(self):
        rule = genruler.parse('(list.length (basic.field "items"))')
        result = rule({"items": [1, 2, 3, 4]})
        assert result == 4

    def test_length_empty(self):
        rule = genruler.parse('(list.length (basic.field "empty"))')
        result = rule({"empty": []})
        assert result == 0


class TestExtendingGenRuler:
    def test_custom_greeting(self):
        from genruler.library import compute
        from genruler.modules import basic

        class CustomModule:
            @staticmethod
            def greet():
                return lambda ctx: f"Hello, {compute(basic.field('name', 'World'), ctx)}!"

        rule = genruler.parse("(greet)", env=CustomModule)
        result = rule({"name": "Alice"})
        assert result == "Hello, Alice!"

        result = rule({})
        assert result == "Hello, World!"


class TestErrorHandling:
    def test_invalid_function_name(self):
        with pytest.raises(InvalidFunctionNameError) as exc_info:
            rule = genruler.parse('(invalid_fn "value")')
        assert "Invalid function name 'invalid_fn'" in str(exc_info.value)

    def test_parse_error(self):
        with pytest.raises(ValueError) as exc_info:
            rule = genruler.parse('(basic.field "name"')  # Missing closing parenthesis
        assert "Parse error" in str(exc_info.value)

    def test_missing_field(self):
        rule = genruler.parse('(basic.field "age")')
        with pytest.raises(KeyError) as exc_info:
            rule({})  # Empty context
        assert "'age'" in str(exc_info.value)

    def test_invalid_subrule(self):
        with pytest.raises(ValueError) as exc_info:
            rule = genruler.parse('(basic.value (basic.field "status"))')
        assert "basic.value cannot accept sub-rules" in str(exc_info.value)
