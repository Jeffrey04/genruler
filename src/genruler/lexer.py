import ast
from dataclasses import dataclass

from funcparserlib.lexer import Token, make_tokenizer
from funcparserlib.parser import NoParseError, Parser, forward_decl, many, some


@dataclass
class Symbol:
    """Represents a symbol in the S-expression."""

    name: str

    def __str__(self) -> str:
        return self.name


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


def safe_literal_eval(token: Token) -> str | int | float | Symbol:
    """Safely evaluate a token into a Python value.

    Args:
        token: The token to evaluate

    Returns:
        The evaluated value as the appropriate Python type:
        - NUMBER tokens become int or float
        - STRING tokens become str
        - SYMBOL tokens become Symbol objects
        - Other tokens return their value as is
    """
    match token.type:
        case "NUMBER" | "STRING":
            try:
                return ast.literal_eval(token.value)
            except (ValueError, SyntaxError):
                # For strings, return the value as is if literal_eval fails
                return token.value if token.type == "NUMBER" else token.value
        case "SYMBOL":
            return Symbol(token.value)
        case _:
            return token.value


def make_token_parser(token_type: str):
    """Create a parser for a specific token type.

    Args:
        token_type: The type of token to parse

    Returns:
        A parser that matches tokens of the specified type and returns their value
    """
    return some(lambda t: t.type == token_type) >> (lambda t: t.value)


def make_parser() -> Parser:
    """Create a parser for S-expressions.

    Returns:
        A parser that converts tokens into an AST
    """
    # Forward declaration for recursive definitions
    expr = forward_decl()

    # Basic parsers for each token type
    lparen = make_token_parser("LPAREN")
    rparen = make_token_parser("RPAREN")

    # Convert tokens to Python values
    number = some(lambda t: t.type == "NUMBER") >> safe_literal_eval
    string = some(lambda t: t.type == "STRING") >> safe_literal_eval
    symbol = some(lambda t: t.type == "SYMBOL") >> safe_literal_eval

    # Atom can be number, string, or symbol
    atom = number | string | symbol

    # List is a sequence of expressions in parentheses
    list_expr = (lparen + many(expr) + rparen) >> (
        lambda x: x[1]
    )  # Extract items between parentheses

    # Only allow list expressions at the top level
    expr.define(atom | list_expr)
    top_level = (lparen + many(expr) + rparen) >> (
        lambda x: x[1]
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
