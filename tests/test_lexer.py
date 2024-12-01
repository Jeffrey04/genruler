from typing import Any

import pytest
from funcparserlib.lexer import Token
from funcparserlib.parser import Parser

from genruler import parse
from genruler.lexer import (
    Symbol,
    eval_numeric,
    eval_paren,
    eval_string,
    eval_symbol,
    make_parser,
    make_sexp_tokenizer,
    make_token_parser,
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


def test_eval_numeric():
    """Test numeric token evaluation."""
    # Test integers
    assert eval_numeric(Token("NUMBER", "42")) == 42
    assert eval_numeric(Token("NUMBER", "-17")) == -17
    assert eval_numeric(Token("NUMBER", "0")) == 0

    # Test floats
    assert eval_numeric(Token("NUMBER", "3.14")) == 3.14
    assert eval_numeric(Token("NUMBER", "-2.718")) == -2.718
    assert eval_numeric(Token("NUMBER", "0.0")) == 0.0

    # Test invalid numbers
    with pytest.raises(ValueError):
        eval_numeric(Token("NUMBER", "invalid"))
    with pytest.raises(SyntaxError):
        eval_numeric(Token("NUMBER", ""))
    with pytest.raises(SyntaxError):
        eval_numeric(Token("NUMBER", "12.34.56"))
    with pytest.raises(SyntaxError):
        eval_numeric(Token("NUMBER", "1e"))


def test_eval_string():
    """Test string token evaluation."""
    # Test basic strings
    assert eval_string(Token("STRING", '"hello"')) == "hello"
    assert eval_string(Token("STRING", '""')) == ""

    # Test strings with escapes
    assert eval_string(Token("STRING", '"hello\\nworld"')) == "hello\nworld"
    assert eval_string(Token("STRING", '"tab\\there"')) == "tab\there"
    assert eval_string(Token("STRING", '"quotes\\"here"')) == 'quotes"here'

    # Test strings with special characters
    assert (
        eval_string(Token("STRING", '"spaces and symbols: !@#$%^&*()"'))
        == "spaces and symbols: !@#$%^&*()"
    )


def test_eval_symbol():
    """Test symbol token evaluation."""
    # Test basic symbols
    symbol = eval_symbol(Token("SYMBOL", "test.symbol"))
    assert isinstance(symbol, Symbol)
    assert symbol.name == "test.symbol"

    # Test various symbol patterns
    patterns = ["a", "a.b", "a.b.c", "a_b", "a.b_c", "+", "-", "*", "/"]
    for pattern in patterns:
        symbol = eval_symbol(Token("SYMBOL", pattern))
        assert isinstance(symbol, Symbol)
        assert symbol.name == pattern


def test_eval_paren():
    """Test parenthesis token evaluation."""
    # Test valid parentheses
    assert eval_paren(Token("LPAREN", "(")) == "("
    assert eval_paren(Token("RPAREN", ")")) == ")"

    # Test invalid parentheses
    with pytest.raises(AssertionError):
        eval_paren(Token("LPAREN", "["))
    with pytest.raises(AssertionError):
        eval_paren(Token("RPAREN", "]"))


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


def test_make_token_parser():
    """Test token parser creation and functionality."""
    # Test basic token parsing
    number_parser: Parser[Token, Token] = make_token_parser("NUMBER")
    string_parser: Parser[Token, Token] = make_token_parser("STRING")
    symbol_parser: Parser[Token, Token] = make_token_parser("SYMBOL")

    # Test number parser
    result = number_parser.parse([Token("NUMBER", "42")])
    assert isinstance(result, Token)
    assert result.type == "NUMBER"
    assert result.value == "42"

    # Test string parser
    result = string_parser.parse([Token("STRING", '"hello"')])
    assert isinstance(result, Token)
    assert result.type == "STRING"
    assert result.value == '"hello"'

    # Test symbol parser
    result = symbol_parser.parse([Token("SYMBOL", "foo.bar")])
    assert isinstance(result, Token)
    assert result.type == "SYMBOL"
    assert result.value == "foo.bar"

    # Test parser rejection
    with pytest.raises(Exception):
        number_parser.parse([Token("STRING", '"not a number"')])


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
