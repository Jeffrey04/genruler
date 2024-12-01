import ast
from dataclasses import dataclass
from operator import itemgetter
from typing import Any

from funcparserlib.lexer import Token, make_tokenizer
from funcparserlib.parser import NoParseError, Parser, forward_decl, many, some


@dataclass
class Symbol:
    """Represents a symbol in the S-expression."""

    name: str

    def __str__(self) -> str:
        return self.name

def eval_numeric(token: Token) -> int | float:
    return ast.literal_eval(token.value)


def eval_string(token: Token) -> str:
    return ast.literal_eval(token.value)


def eval_symbol(token: Token) -> Symbol:
    return Symbol(token.value)


def eval_paren(token: Token) -> str:
    assert token.value in ("(", ")")

    return token.value


def make_sexp_tokenizer():
    """Create a tokenizer for S-expressions.

    Returns:
        A tuple of (tokenizer function, set of useless token types)
    """
    specs = [
        ("SPACE", (r"[ \t\r\n]+",)),
        ("LPAREN", (r"\(",)),
        ("RPAREN", (r"\)",)),
        ("STRING", (r'"[^"]*"',)),
        ("NUMBER", (r"-?\d+\.\d+|-?\d+",)),
        (
            "SYMBOL",
            (r'[^\s\(\)"]+',),
        ),  # Matches any non-space, non-paren, non-quote characters
    ]
    useless = ["SPACE"]
    return make_tokenizer(specs), set(useless)


def make_token_parser(token_type: str) -> Parser[Token, Token]:
    """Create a parser for matching tokens of a specific type.

    Uses funcparserlib's 'some' combinator to create a parser that matches tokens
    based on their type. The parser will only match tokens that have the exact
    type specified.

    Args:
        token_type (str): The type of token to match (e.g. 'NUMBER', 'STRING', 'SYMBOL')

    Returns:
        Parser: A parser that matches tokens of the specified type and returns the token
    """

    def pred(t: Token) -> bool:
        return t.type == token_type

    return some(pred)


def make_parser() -> Parser[Token, Any]:
    """Create a parser for S-expressions.

    Returns:
        A parser that converts tokens into an AST
    """
    # Forward declaration for recursive definitions
    expr = forward_decl()

    # Basic parsers for each token type
    lparen = make_token_parser("LPAREN") >> eval_paren
    rparen = make_token_parser("RPAREN") >> eval_paren

    # Convert tokens to Python values
    number = make_token_parser("NUMBER") >> eval_numeric
    string = make_token_parser("STRING") >> eval_string
    symbol = make_token_parser("SYMBOL") >> eval_symbol

    # Atom can be number, string, or symbol
    atom = number | string | symbol

    # List is a sequence of expressions in parentheses
    list_expr = (lparen + many(expr) + rparen) >> (
        itemgetter(1)
    )  # Extract items between parentheses

    # Only allow list expressions at the top level
    expr.define(atom | list_expr)
    top_level = (lparen + many(expr) + rparen) >> (
        itemgetter(1)
    )  # Extract items between parentheses

    return top_level


def read(input: str) -> list:
    """Read an S-expression string into an AST.

    Args:
        input: The S-expression string to parse

    Returns:
        The parsed AST

    Raises:
        ValueError: If the input cannot be parsed
    """
    tokenizer, useless = make_sexp_tokenizer()
    try:
        # Tokenize input
        tokens = [
            Token(t.type, t.value) for t in tokenizer(input) if t.type not in useless
        ]

        # Parse tokens into AST
        parser = make_parser()
        return parser.parse(tokens)

    except NoParseError as e:
        raise ValueError(f"Parse error: {e}")
