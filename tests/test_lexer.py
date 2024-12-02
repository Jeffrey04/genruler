from typing import Any

import pytest
from funcparserlib.lexer import Token
from funcparserlib.parser import Parser

from genruler import parse
from genruler.lexer import (
    Symbol,
    make_parser,
    make_sexp_tokenizer,
    read,
)


def test_symbol_class():
    """Test Symbol class functionality."""
    # Test basic properties
    sym = Symbol("test.symbol")
    assert sym.name == "test.symbol"
    assert str(sym) == "test.symbol"

    # Test equality
    assert Symbol("foo.bar") == Symbol("foo.bar")
    assert Symbol("foo.bar") != Symbol("bar.foo")
    assert Symbol("foo.bar") != "foo.bar"  # Test against string
    assert Symbol("foo.bar") != 42  # Test against other types


def test_make_sexp_tokenizer():
    """Test S-expression tokenizer creation and functionality."""
    tokenizer, useless = make_sexp_tokenizer()

    # Test basic tokenization
    tokens = [t for t in tokenizer('(foo.bar 42 "hello")') if t.type not in useless]
    assert [t.type for t in tokens] == [
        "LPAREN",
        "SYMBOL",
        "NUMBER",
        "STRING",
        "RPAREN",
    ]
    assert [t.value for t in tokens] == ["(", "foo.bar", "42", '"hello"', ")"]

    # Test number variations
    tokens = [t for t in tokenizer("42 3.14 -5 -2.718") if t.type not in useless]
    assert all(t.type == "NUMBER" for t in tokens)
    assert [t.value for t in tokens] == ["42", "3.14", "-5", "-2.718"]

    # Test string variations
    tokens = [t for t in tokenizer('"hello" "a.b.c" "123"') if t.type not in useless]
    assert all(t.type == "STRING" for t in tokens)
    assert [t.value for t in tokens] == ['"hello"', '"a.b.c"', '"123"']

    # Test symbol variations
    tokens = [t for t in tokenizer("foo.bar baz_123 +") if t.type not in useless]
    assert all(t.type == "SYMBOL" for t in tokens)
    assert [t.value for t in tokens] == ["foo.bar", "baz_123", "+"]

    # Test whitespace handling
    tokens = [t for t in tokenizer("  (  foo  123  )  ") if t.type not in useless]
    assert [t.type for t in tokens] == ["LPAREN", "SYMBOL", "NUMBER", "RPAREN"]
    assert [t.value for t in tokens] == ["(", "foo", "123", ")"]


def test_make_parser():
    """Test S-expression parser creation and functionality."""
    parser: Parser[Token, Any] = make_parser()

    # Test basic expression parsing
    tokens = [
        Token("LPAREN", "("),
        Token("SYMBOL", "foo.bar"),
        Token("NUMBER", "42"),
        Token("STRING", '"hello"'),
        Token("RPAREN", ")"),
    ]
    result = parser.parse(tokens)
    assert len(result) == 3
    assert isinstance(result[0], Symbol)
    assert result[0].name == "foo.bar"
    assert result[1] == 42
    assert result[2] == "hello"

    # Test nested expression parsing
    tokens = [
        Token("LPAREN", "("),
        Token("SYMBOL", "foo"),
        Token("LPAREN", "("),
        Token("SYMBOL", "bar"),
        Token("NUMBER", "42"),
        Token("RPAREN", ")"),
        Token("RPAREN", ")"),
    ]
    result = parser.parse(tokens)
    assert len(result) == 2
    assert isinstance(result[0], Symbol)
    assert result[0].name == "foo"
    assert isinstance(result[1], list)
    assert isinstance(result[1][0], Symbol)
    assert result[1][0].name == "bar"
    assert result[1][1] == 42


def test_read():
    """Test complete S-expression reading functionality."""
    # Test basic expression
    result = read('(foo.bar 42 "hello")')
    assert len(result) == 3
    assert isinstance(result[0], Symbol)
    assert result[0].name == "foo.bar"
    assert result[1] == 42
    assert result[2] == "hello"

    # Test nested expression
    result = read("(foo (bar 42))")
    assert len(result) == 2
    assert isinstance(result[0], Symbol)
    assert result[0].name == "foo"
    assert isinstance(result[1], list)
    assert isinstance(result[1][0], Symbol)
    assert result[1][0].name == "bar"
    assert result[1][1] == 42

    # Test error cases
    with pytest.raises(ValueError, match="Parse error"):
        read("foo.bar")  # Not wrapped in parentheses

    with pytest.raises(ValueError, match="Parse error"):
        read("(foo.bar")  # Unclosed parenthesis

    with pytest.raises(ValueError, match="Parse error"):
        read("foo.bar)")  # Extra closing parenthesis


def test_expression_evaluation():
    """Test evaluation of various S-expressions using parse function."""
    # Test simple expression
    result = parse("(boolean.tautology)")
    assert callable(result)
    assert result({}) is True

    # Test nested expression
    result = parse("(boolean.and (boolean.tautology) (boolean.tautology))")
    assert callable(result)
    assert result({}) is True

    # Test complex expression
    result = parse(
        "(boolean.or (boolean.and (boolean.tautology) (boolean.contradiction)) (boolean.tautology))"
    )
    assert callable(result)
    assert result({}) is True

    # Test invalid expressions
    with pytest.raises(ValueError, match="Parse error"):
        parse("boolean.tautology")  # Not wrapped in parentheses
