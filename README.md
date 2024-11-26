# genruler

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

## Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [Installation](#installation)
  - [Requirements](#requirements)
- [Ruler DSL](#ruler-dsl)
  - [Syntax & Structure](#syntax--structure)
  - [Parsing and Evaluation](#parsing-and-evaluation)
- [API Reference](#api-reference)
  - [Basic Functions](#basic-functions)
  - [Number Functions](#number-functions)
  - [Boolean Operators](#boolean-operators)
  - [String Functions](#string-functions)
  - [Condition Rules](#condition-rules)
  - [List Functions](#list-functions)
- [Extending GenRuler](#extending-genruler)
- [Error Handling](#error-handling)
- [Contributing](#contributing)
- [License](#license)

## Overview

A rule DSL language parser in Python that allows you to write and evaluate rules using a LISP-inspired syntax.

## Quick Start

```python
import genruler

# Parse a simple rule
rule = genruler.parse('(condition.equal (basic.field "name") "John")')

# Apply the rule to a context
context = {"name": "John"}
result = rule(context)  # Returns True
```

## Installation

You can install genruler directly from PyPI:

```bash
pip install genruler
```

Alternatively, you can install from source:

```bash
git clone https://github.com/jeffrey04/genruler.git
cd genruler
pip install -e .
```

### Requirements

- Python 3.12 or higher
- funcparserlib >= 1.0.1

## Ruler DSL

This mini-language is partially inspired by LISP. A rule is represented by a an s-expression.

### Syntax & Structure

```
(namespace.function_name "some_arguments" "more_arguments_if_applicable")
```

A rule is usually consist of a function name, and a list of (sometimes optional) arguments. Function names are often namespaced (e.g. `"boolean.and"`, `"condition.equal"` etc.) and usually only recognized if placed in the first elemnt.

Unless otherwise specified, **a rule can be inserted as an argument to another rule**, for example a `boolean.and` rule.

```
(boolean.and (condition.equal (basic.field "fieldA") "X"),
              condition.equal (basic.field "fieldB") "Y")
```

### Parsing and Evaluation

In order to parse the rule, just call `genruler.parse`. The result is a function where you can put in a context object in order for it to compute a result.

```python
import genruler

rule = genruler.parse('(condition.Equal (basic.Field "fieldA") "X")')
context = {"fieldA": "X"}
rule(context) // should return true
```

## API Reference

### Basic Functions

Functions for basic operations like field access and value handling.

#### basic.coalesce

```
(basic.coalesce $value $arg1 $arg2 ...)
```

Returns the first non-empty (truthy) value from a sequence of values. Similar to SQL's COALESCE function. Arguments are evaluated in order until a truthy value is found.

Examples:
```python
# Returns "value" since it's the first truthy value
rule = genruler.parse('(basic.coalesce "" "value" "other")')
context = {}
result = rule(context)  # Returns "value"

# Works with nested expressions
rule = genruler.parse('(basic.coalesce (basic.field "a") (basic.field "b") "default")')
context = {"b": "value", "a": None}
result = rule(context)  # Returns "value"
```

#### basic.context

```
(basic.context $context_sub $argument)
```

Access nested context values by evaluating a sub-context expression and then evaluating an argument within that sub-context.

Examples:
```python
# Access nested object
rule = genruler.parse('(basic.context (basic.field "user") (basic.field "name"))')
context = {"user": {"name": "John"}}
result = rule(context)  # Returns "John"

# Multiple levels of nesting
rule = genruler.parse('(basic.context (basic.field "data") (basic.context (basic.field "user") (basic.field "email")))')
context = {"data": {"user": {"email": "john@example.com"}}}
result = rule(context)  # Returns "john@example.com"
```

#### basic.field

```
(basic.field $key [$default])
```

Access field values from a dictionary or list context. For dictionaries, supports optional default values for missing keys. For lists, uses direct index access.

Examples:
```python
# Dictionary access
rule = genruler.parse('(basic.field "name")')
context = {"name": "John"}
result = rule(context)  # Returns "John"

# With default value
rule = genruler.parse('(basic.field "age" 0)')
context = {}
result = rule(context)  # Returns 0

# List access
rule = genruler.parse('(basic.field 0)')
context = ["first", "second"]
result = rule(context)  # Returns "first"
```

#### basic.value

Creates a constant value that is returned as-is, ignoring the context. Useful for comparing fields against fixed values:
- Only accepts literal values (numbers, strings)
- List syntax produces tuples: `("a" "b")` -> `("a", "b")`
- Cannot contain sub-rules (will raise an error)

Examples:
```python
# Simple constant values
rule = genruler.parse('(basic.value 42)')
result = rule({})  # Returns 42

rule = genruler.parse('(basic.value "active")')
result = rule({})  # Returns "active"

rule = genruler.parse('(basic.value ("a" "b" "c"))')
result = rule({})  # Returns ("a", "b", "c")

# Sub-rules are not allowed
rule = genruler.parse('(basic.value (basic.field "status"))')  # ValueError: basic.value cannot accept sub-rules

# Use basic.value for constant comparisons
rule = genruler.parse('(condition.equal (basic.field "status") (basic.value "active"))')
result = rule({"status": "active"})  # Returns True
```

### Number Functions

Functions for numeric operations.

#### number.add

```
(number.add $value1 $value2 ...)
```

Adds multiple numbers together. Values are evaluated in the context before addition.

Examples:
```python
# Simple addition
rule = genruler.parse('(number.add 1 2 3)')
context = {}
result = rule(context)  # Returns 6

# With field values
rule = genruler.parse('(number.add (basic.field "price") (basic.field "tax"))')
context = {"price": 100, "tax": 20}
result = rule(context)  # Returns 120
```

#### number.subtract

```
(number.subtract $value1 $value2)
```

Subtracts the second value from the first value. Values are evaluated in the context before subtraction.

Examples:
```python
# Simple subtraction
rule = genruler.parse('(number.subtract 10 3)')
context = {}
result = rule(context)  # Returns 7

# With field values
rule = genruler.parse('(number.subtract (basic.field "total") (basic.field "discount"))')
context = {"total": 100, "discount": 20}
result = rule(context)  # Returns 80
```

#### number.multiply

```
(number.multiply $value1 $value2 ...)
```

Multiplies multiple numbers together. Values are evaluated in the context before multiplication.

Examples:
```python
# Simple multiplication
rule = genruler.parse('(number.multiply 2 3 4)')
context = {}
result = rule(context)  # Returns 24

# With field values
rule = genruler.parse('(number.multiply (basic.field "quantity") (basic.field "price"))')
context = {"quantity": 5, "price": 10}
result = rule(context)  # Returns 50
```

#### number.divide

```
(number.divide $value1 $value2)
```

Divides the first value by the second value. Values are evaluated in the context before division.

Examples:
```python
# Simple division
rule = genruler.parse('(number.divide 10 2)')
context = {}
result = rule(context)  # Returns 5.0

# With field values
rule = genruler.parse('(number.divide (basic.field "total") (basic.field "parts"))')
context = {"total": 100, "parts": 4}
result = rule(context)  # Returns 25.0
```

#### number.modulo

```
(number.modulo $value1 $value2)
```

Computes the remainder when dividing the first value by the second value. Values are evaluated in the context before the modulo operation.

Examples:
```python
# Simple modulo
rule = genruler.parse('(number.modulo 7 3)')
context = {}
result = rule(context)  # Returns 1

# With field values
rule = genruler.parse('(number.modulo (basic.field "items") (basic.field "per_page"))')
context = {"items": 17, "per_page": 5}
result = rule(context)  # Returns 2
```

### Boolean Operators

Functions for logical operations.

#### boolean.and

```
(boolean.and $value1 $value2 ...)
```

Performs a logical AND operation on all values. Values are evaluated in the context before the operation. Returns True only if all values are True.

Examples:
```python
# Simple AND operation
rule = genruler.parse('(boolean.and (condition.gt (basic.field "age") 18) (condition.equal (basic.field "verified") (boolean.tautology)))')
context = {"age": 21, "verified": True}
result = rule(context)  # Returns True

# Multiple conditions
rule = genruler.parse('(boolean.and (basic.field "active") (basic.field "paid") (basic.field "verified"))')
context = {"active": True, "paid": True, "verified": True}
result = rule(context)  # Returns True
```

#### boolean.or

```
(boolean.or $value1 $value2 ...)
```

Performs a logical OR operation on all values. Values are evaluated in the context before the operation. Returns True if any value is True.

Examples:
```python
# Check multiple conditions
rule = genruler.parse('(boolean.or (condition.equal (basic.field "role") "admin") (condition.equal (basic.field "role") "moderator"))')
context = {"role": "admin"}
result = rule(context)  # Returns True

# With field values
rule = genruler.parse('(boolean.or (basic.field "premium") (basic.field "trial"))')
context = {"premium": False, "trial": True}
result = rule(context)  # Returns True
```

#### boolean.not

```
(boolean.not $value)
```

Performs a logical NOT operation on the value. The value is evaluated in the context before the operation.

Examples:
```python
# Negate a condition
rule = genruler.parse('(boolean.not (condition.equal (basic.field "status") "blocked"))')
context = {"status": "active"}
result = rule(context)  # Returns True

# Negate a field value
rule = genruler.parse('(boolean.not (basic.field "disabled"))')
context = {"disabled": False}
result = rule(context)  # Returns True
```

#### boolean.tautology

```
(boolean.tautology)
```

Always returns True, regardless of the context. Useful as a default condition or in complex logical expressions.

Examples:
```python
# Simple tautology
rule = genruler.parse('(boolean.tautology)')
context = {}
result = rule(context)  # Returns True

# In combination with AND
rule = genruler.parse('(boolean.and (boolean.tautology) (condition.equal (basic.field "valid") true))')
context = {"valid": true}
result = rule(context)  # Same as just checking valid=true
```

#### boolean.contradiction

```
(boolean.contradiction)
```

Always returns False, regardless of the context. Useful as a default condition or in complex logical expressions.

Examples:
```python
# Simple contradiction
rule = genruler.parse('(boolean.contradiction)')
context = {}
result = rule(context)  # Returns False

# In combination with OR
rule = genruler.parse('(boolean.or (boolean.contradiction) (condition.equal (basic.field "valid") true))')
context = {"valid": true}
result = rule(context)  # Same as just checking valid=true
```

### String Functions

Functions for string manipulation and field access.

#### string.concat

```
(string.concat $separator $value1 $value2 ...)
```

Joins multiple values into a single string using the specified separator. Each value is evaluated in the context and converted to a string before joining.

Examples:
```python
# Join with comma separator
rule = genruler.parse('(string.concat "," "a" "b" "c")')
context = {}
result = rule(context)  # Returns "a,b,c"

# Join with space, using field values
rule = genruler.parse('(string.concat " " (basic.field "first") (basic.field "last"))')
context = {"first": "John", "last": "Doe"}
result = rule(context)  # Returns "John Doe"
```

#### string.concat_fields

```
(string.concat_fields $separator $field1 $field2 ...)
```

Similar to `string.concat` but specifically for joining field values. Automatically retrieves and joins the values of specified fields from the context.

Examples:
```python
# Join field values with comma
rule = genruler.parse('(string.concat_fields "," "first" "last")')
context = {"first": "John", "last": "Doe"}
result = rule(context)  # Returns "John,Doe"

# Join multiple fields with custom separator
rule = genruler.parse('(string.concat_fields " - " "city" "state" "country")')
context = {"city": "San Francisco", "state": "CA", "country": "USA"}
result = rule(context)  # Returns "San Francisco - CA - USA"
```

#### string.field

```
(string.field $key [$default])
```

Retrieves a field value from the context and converts it to a string. Similar to `basic.field` but ensures the result is a string. Optionally accepts a default value if the field doesn't exist.

Examples:
```python
# Basic string field access
rule = genruler.parse('(string.field "name")')
context = {"name": "John"}
result = rule(context)  # Returns "John"

# Numbers are converted to strings
rule = genruler.parse('(string.field "age")')
context = {"age": 25}
result = rule(context)  # Returns "25"

# With default value
rule = genruler.parse('(string.field "missing" "N/A")')
context = {}
result = rule(context)  # Returns "N/A"
```

#### string.lower

```
(string.lower $value)
```

Converts a value to lowercase. The value is first evaluated in the context and then converted to lowercase.

Examples:
```python
# Simple lowercase conversion
rule = genruler.parse('(string.lower "HELLO")')
context = {}
result = rule(context)  # Returns "hello"

# Lowercase field value
rule = genruler.parse('(string.lower (basic.field "name"))')
context = {"name": "JOHN"}
result = rule(context)  # Returns "john"
```

### Condition Rules

Functions for comparing values and checking conditions.

#### condition.equal

```
(condition.equal $value1 $value2)
```

Compares two values for equality. Values are evaluated in the context before comparison.

Examples:
```python
# Compare field with constant
rule = genruler.parse('(condition.equal (basic.field "name") "John")')
context = {"name": "John"}
result = rule(context)  # Returns True

# Compare two fields
rule = genruler.parse('(condition.equal (basic.field "password") (basic.field "confirm"))')
context = {"password": "secret", "confirm": "secret"}
result = rule(context)  # Returns True
```

#### condition.in

```
(condition.in $value $list)
```

Checks if a value is contained in a list. The value and list are evaluated in the context before checking.

Examples:
```python
# Check against constant list
rule = genruler.parse('(condition.in (basic.value "apple") (basic.value ("apple" "banana" "orange")))')
context = {}
result = rule(context)  # Returns True

# Check field value against list field
rule = genruler.parse('(condition.in (basic.field "fruit") (basic.field "allowed"))')
context = {"fruit": "apple", "allowed": ["apple", "banana"]}
result = rule(context)  # Returns True
```

#### condition.is_none

```
(condition.is_none $value)
```

Checks if a value is None. The value is evaluated in the context before checking.

Examples:
```python
# Check if field is None
rule = genruler.parse('(condition.is_none (basic.field "optional"))')
context = {"optional": None}
result = rule(context)  # Returns True

# Check with nested expression
rule = genruler.parse('(basic.context (basic.field "user") (condition.is_none (basic.field "email")))')
context = {"user": {"email": None}}
result = rule(context)  # Returns True
```

#### condition.is_true

```
(condition.is_true $value)
```

Checks if a value is exactly True (not just truthy). The value is evaluated in the context before checking.

Examples:
```python
# Check boolean field
rule = genruler.parse('(condition.is_true (basic.field "active"))')
context = {"active": True}
result = rule(context)  # Returns True

# Non-True values return False
rule = genruler.parse('(condition.is_true (basic.field "count"))')
context = {"count": 1}  # Even though 1 is truthy, it's not True
result = rule(context)  # Returns False
```

#### condition.gt (Greater Than)

```
(condition.gt $value1 $value2)
```

Checks if the first value is greater than the second value. Values are evaluated in the context before comparison.

Examples:
```python
# Compare numbers
rule = genruler.parse('(condition.gt (basic.field "age") 18)')
context = {"age": 21}
result = rule(context)  # Returns True

# Compare field values
rule = genruler.parse('(condition.gt (basic.field "score") (basic.field "threshold"))')
context = {"score": 85, "threshold": 70}
result = rule(context)  # Returns True
```

#### condition.ge (Greater Than or Equal)

```
(condition.ge $value1 $value2)
```

Checks if the first value is greater than or equal to the second value. Values are evaluated in the context before comparison.

Examples:
```python
# Compare numbers
rule = genruler.parse('(condition.ge (basic.field "age") 18)')
context = {"age": 18}
result = rule(context)  # Returns True

# Compare field values
rule = genruler.parse('(condition.ge (basic.field "score") (basic.field "passing"))')
context = {"score": 70, "passing": 70}
result = rule(context)  # Returns True
```

#### condition.lt (Less Than)

```
(condition.lt $value1 $value2)
```

Checks if the first value is less than the second value. Values are evaluated in the context before comparison.

Examples:
```python
# Compare numbers
rule = genruler.parse('(condition.lt (basic.field "age") 18)')
context = {"age": 17}
result = rule(context)  # Returns True

# Compare field values
rule = genruler.parse('(condition.lt (basic.field "score") (basic.field "threshold"))')
context = {"score": 60, "threshold": 70}
result = rule(context)  # Returns True
```

#### condition.le (Less Than or Equal)

```
(condition.le $value1 $value2)
```

Checks if the first value is less than or equal to the second value. Values are evaluated in the context before comparison.

Examples:
```python
# Compare numbers
rule = genruler.parse('(condition.le (basic.field "age") 18)')
context = {"age": 18}
result = rule(context)  # Returns True

# Compare field values
rule = genruler.parse('(condition.le (basic.field "score") (basic.field "passing"))')
context = {"score": 70, "passing": 70}
result = rule(context)  # Returns True
```

### List Functions

Functions for working with lists and sequences.

#### list.length

```
(list.length $list)
```

Returns the length of a list. The list argument is evaluated in the context before calculating the length.

Examples:
```python
# Direct list length
rule = genruler.parse('(list.length ["a", "b", "c"])')
context = {}
result = rule(context)  # Returns 3

# Field list length
rule = genruler.parse('(list.length (basic.field "items"))')
context = {"items": [1, 2, 3, 4]}
result = rule(context)  # Returns 4

# Empty list
rule = genruler.parse('(list.length (basic.field "empty"))')
context = {"empty": []}
result = rule(context)  # Returns 0
```

## Extending GenRuler

GenRuler can be extended with custom functions through the `env` parameter in the `parse` function. This allows you to add domain-specific functionality without modifying the core library.

```python
from genruler.library import compute
from genruler.modules import basic

class CustomModule:
    @staticmethod
    def greet():
        return lambda ctx: f"Hello, {compute(basic.field('name', 'World'))}!"

# Use custom functions in rules
rule = genruler.parse("(greet)", env=CustomModule)
result = rule({"name": "Alice"})  # Returns "Hello, Alice!"
```

Custom functions should:
- Return a callable that takes a context parameter
- Use `genruler.library.compute` for evaluating arguments that might be rules
- Keep functions pure - only depend on arguments and context
- Follow the same error handling patterns as built-in functions

## Error Handling

The library provides clear error messages for common issues:

```python
# Invalid function name
rule = genruler.parse('(invalid_fn "value")')
# InvalidFunctionNameError: Invalid function name 'invalid_fn'

# Missing closing parenthesis
rule = genruler.parse('(basic.field "name"')
# ValueError: Parse error at position 20

# Missing field in context
rule = genruler.parse('(basic.field "age")')
rule({})  # KeyError: 'age'

# Invalid sub-rule in basic.value
rule = genruler.parse('(basic.value (basic.field "status"))')
# ValueError: basic.value cannot accept sub-rules
```

## Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Run the tests (`python -m pytest`)
5. Commit your changes (`git commit -am 'Add new feature'`)
6. Push to the branch (`git push origin feature/improvement`)
7. Create a Pull Request

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.
