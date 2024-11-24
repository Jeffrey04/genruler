import pytest
from funcparserlib.lexer import Token

from genruler import parse
from genruler.lexer import (
    Symbol,
    make_parser,
    make_sexp_tokenizer,
    read,
    safe_literal_eval,
)


def test_safe_literal_eval():
    """Test safe_literal_eval function."""
    # Test numbers
    assert safe_literal_eval(Token("NUMBER", "42")) == 42
    assert safe_literal_eval(Token("NUMBER", "3.14")) == 3.14
    assert safe_literal_eval(Token("NUMBER", "-5")) == -5
    assert safe_literal_eval(Token("NUMBER", "-2.718")) == -2.718
    assert safe_literal_eval(Token("NUMBER", "invalid")) == "invalid"  # Fallback

    # Test strings
    assert safe_literal_eval(Token("STRING", '"hello"')) == "hello"
    assert safe_literal_eval(Token("STRING", '"hello\\nworld"')) == "hello\nworld"
    assert safe_literal_eval(Token("STRING", '"123"')) == "123"
    assert safe_literal_eval(Token("STRING", "invalid")) == "invalid"  # Fallback without quotes

    # Test symbols
    sym = safe_literal_eval(Token("SYMBOL", "foo.bar"))
    assert isinstance(sym, Symbol)
    assert sym.name == "foo.bar"

    # Test other tokens
    assert safe_literal_eval(Token("OTHER", "value")) == "value"


def test_simple_expression():
    result = parse("(boolean.tautology)")
    assert callable(result), "Result should be callable"
    assert result({}) is True, "boolean.tautology should return True"


def test_nested_expression():
    result = parse("(boolean.and (boolean.tautology) (boolean.tautology))")
    assert callable(result), "Result should be callable"
    assert result({}) is True, "Nested AND of two True values should be True"


def test_complex_expression():
    result = parse(
        "(boolean.or (boolean.and (boolean.tautology) (boolean.contradiction)) (boolean.tautology))"
    )
    assert callable(result), "Result should be callable"
    assert result({}) is True, "Complex boolean expression should evaluate correctly"


def test_reject_atom():
    with pytest.raises(ValueError, match="Parse error"):
        parse("boolean.tautology")  # Should fail - not wrapped in parentheses


def test_make_sexp_tokenizer():
    """Test the S-expression tokenizer."""
    tokenizer, useless = make_sexp_tokenizer()

    # Test basic tokenization
    tokens = [t for t in tokenizer('(foo.bar 123 "hello")') if t.type not in useless]
    assert [t.type for t in tokens] == [
        "LPAREN",
        "SYMBOL",
        "NUMBER",
        "STRING",
        "RPAREN",
    ]
    assert [t.value for t in tokens] == ["(", "foo.bar", "123", '"hello"', ")"]

    # Test number formats
    tokens = [t for t in tokenizer("42 3.14 -5 -2.718") if t.type not in useless]
    assert all(t.type == "NUMBER" for t in tokens)
    assert [t.value for t in tokens] == ["42", "3.14", "-5", "-2.718"]

    # Test string with spaces and special chars
    tokens = [
        t for t in tokenizer('"hello world" "a.b.c" "123"') if t.type not in useless
    ]
    assert all(t.type == "STRING" for t in tokens)
    assert [t.value for t in tokens] == ['"hello world"', '"a.b.c"', '"123"']

    # Test symbols
    tokens = [t for t in tokenizer("foo.bar baz_123 +") if t.type not in useless]
    assert all(t.type == "SYMBOL" for t in tokens)
    assert [t.value for t in tokens] == ["foo.bar", "baz_123", "+"]

    # Test whitespace handling
    tokens = [t for t in tokenizer("  (  foo  123  )  ") if t.type not in useless]
    assert [t.type for t in tokens] == ["LPAREN", "SYMBOL", "NUMBER", "RPAREN"]


def test_make_parser():
    """Test the S-expression parser."""
    parser = make_parser()

    # Test basic parsing
    tokens = [
        Token("LPAREN", "("),
        Token("SYMBOL", "foo.bar"),
        Token("NUMBER", "123"),
        Token("STRING", '"hello"'),
        Token("RPAREN", ")"),
    ]
    result = parser.parse(tokens)
    assert len(result) == 3
    assert isinstance(result[0], Symbol)
    assert result[0].name == "foo.bar"
    assert result[1] == 123
    assert result[2] == "hello"

    # Test nested expressions
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

    # Test literal parsing
    tokens = [
        Token("LPAREN", "("),
        Token("SYMBOL", "test"),
        Token("NUMBER", "3.14"),
        Token("NUMBER", "-42"),
        Token("STRING", '"hello\\nworld"'),  # Test string with escape sequence
        Token("RPAREN", ")"),
    ]
    result = parser.parse(tokens)
    assert len(result) == 4
    assert isinstance(result[0], Symbol)
    assert result[0].name == "test"
    assert result[1] == 3.14
    assert result[2] == -42
    assert result[3] == "hello\nworld"  # Verify escape sequence is handled


def test_make_token_parser():
    """Test make_token_parser function."""
    from funcparserlib.parser import NoParseError

    from genruler.lexer import make_token_parser

    # Create parsers for different token types
    lparen_parser = make_token_parser("LPAREN")
    number_parser = make_token_parser("NUMBER")
    string_parser = make_token_parser("STRING")
    symbol_parser = make_token_parser("SYMBOL")

    # Test LPAREN parser
    assert lparen_parser.parse([Token("LPAREN", "(")]) == "("
    with pytest.raises(NoParseError):
        lparen_parser.parse([Token("RPAREN", ")")])

    # Test NUMBER parser
    assert number_parser.parse([Token("NUMBER", "42")]) == "42"
    assert number_parser.parse([Token("NUMBER", "-3.14")]) == "-3.14"
    with pytest.raises(NoParseError):
        number_parser.parse([Token("STRING", '"42"')])

    # Test STRING parser
    assert string_parser.parse([Token("STRING", '"hello"')]) == '"hello"'
    assert string_parser.parse([Token("STRING", '"hello world"')]) == '"hello world"'
    with pytest.raises(NoParseError):
        string_parser.parse([Token("NUMBER", "42")])

    # Test SYMBOL parser
    assert symbol_parser.parse([Token("SYMBOL", "foo.bar")]) == "foo.bar"
    assert symbol_parser.parse([Token("SYMBOL", "baz_123")]) == "baz_123"
    with pytest.raises(NoParseError):
        symbol_parser.parse([Token("NUMBER", "42")])

    # Test empty input
    with pytest.raises(NoParseError):
        lparen_parser.parse([])

    # Test multiple tokens (should parse first token)
    result = lparen_parser.parse([Token("LPAREN", "("), Token("LPAREN", "(")])
    assert result == "("


def test_read():
    """Test the read function that combines tokenization and parsing."""
    # Test basic expression
    result = read('(foo.bar 123 "hello")')
    assert len(result) == 3
    assert isinstance(result[0], Symbol)
    assert result[0].name == "foo.bar"
    assert result[1] == 123
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


def test_symbol():
    """Test Symbol class functionality."""
    sym = Symbol("foo.bar")
    assert sym.name == "foo.bar"
    assert str(sym) == "foo.bar"
    assert Symbol("foo.bar") == Symbol("foo.bar")
    assert Symbol("foo.bar") != Symbol("bar.foo")
