# genruler

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

A rule DSL language parser in Python that allows you to write and evaluate rules using a LISP-inspired syntax.

## Table of Contents
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Requirements](#requirements)
- [Ruler DSL](#ruler-dsl)
  - [Syntax & Structure](#syntax--structure)
- [API Reference](#ruler-api-overview)
  - [Array Functions](#array-functions)
  - [Basic Functions](#basic-functions)
  - [Boolean Operators](#boolean-operators)
  - [Condition Rules](#condition-rules)
- [Error Handling](#error-handling)
- [Contributing](#contributing)
- [License](#license)

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

## Requirements

- Python 3.12 or higher (less than 3.14)

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

## Parsing and computing result

In order to parse the rule, just call `genruler.parse`. The result is a function where you can put in a context object in order for it to compute a result.

```python
import genruler

rule = genruler.parse('(condition.Equal (basic.Field "fieldA") "X")')
context = {"fieldA": "X"}
rule(context) // should return true
```

## Ruler API overview

### Array functions

Some array related functions.

#### array.length

```
(array.length $argument)
```

Returns the length of a given array `$argument`. For example,

```python
import genruler

rule = genruler.parse('(array.length (basic.Field "fieldA"))')
context = {"fieldA": [1, 2, 3]}
rule(context) // should return 3
```

### Basic functions

Some random functions that don't fit anywhere else goes here

#### basic.context

```
(basic.context $context_sub, $rule)
```

Temporarily change the context to `$context_sub`, and perform `$rule` with `$context_sub` as the new `context`

- `$context_sub` _(required)_: A struct, or a rule to extract a new struct w.r.t. the original `context`
- `$rule` _(required)_: the rule to be applied w.r.t. `$context_sub`

An example:

```python
rule = ruler.parse('(basic.Context (basic.field, 'sub')
                                   (basic.field, 'foo'))')

context = {"sub": {"foo": "bar"}}
rule(context) # returns context['sub']['foo'], which is 'bar'
```

#### Basic.field

```
(basic.field $key $default)
```

Returns a field value from `context` when called.

- `$key` _(required)_: is a `key` in the `context`.
- `$default` _(optional)_: is a default value to be returned when `context[key]` does not exist.

#### basic.value

```
(basic.value $value)
```

Returns a value, regardless what is in the `context`

- `$value` _(required)_: a value to return. **MAY NOT** be a sub-rule

### Boolean operators

Usually used to chain condition rules (see next section) together

#### boolean.and

```
(boolean.and $argument1 $argument2 ...)
```

Returns `True` if all arguments returns `True`, or `False` otherwise.

#### boolean.contradiction

```
(boolean.contradiction)
```

Always returns a `False`, a shorthand for

```
(basic.Value false)
```

#### boolean.not

```
(boolean.not $argument)
```

Returns the result of negation done to `$argument`.

#### boolean.or

```
(boolean.or $argument2 $argument2)
```

Returns `True` if any of the arguments is `True`, or `False` otherwise.

#### boolean.tautology

```
(boolean.tautology)
```

Returns `True` regardless

### Condition rules

Usually returns either true or false

#### condition.equal

```
(condition.equal $alpha $beta)
```

Returns `True` if and only if `$alpha` is equivalent to `$beta`.

#### condition.gt

```
(condition.gt $alpha $beta)
```

Returns `True` if and only if `$alpha` is greater than `$beta`.

#### condition.ge

```
(condition.ge $alpha $beta)
```

Returns `True` if and only if `$alpha` is greater than or equal to `$beta`.

#### condition.in

```
(condition.in $alpha $values)
```

Returns `True` if `$alpha` is in `$values`

#### condition.is_none

```
(condition.is_none $alpha)
```

Returns `True` if `$alpha` is `None`

#### condition.is_true

```
(condition.Is_True $alpha)
```

Returns `True` if `$alpha` is `True`

#### condition.lt

```
(condition.less_than $alpha $beta)
```

Returns `True` if and only if `$alpha` is less than `$beta`.

#### condition.le

```
["condition.Less_Than_Equal", $alpha, $beta]
```

Returns `True` if and only if `$alpha` is less than or equal to `$beta`.

### String operations

Some basic string operations

#### string.concat

```
(string.Concat $link $argument1 $argument2 ...)
```

Concatenate arguments by `$link`

#### string.concat_fields

```
(string.concat_fields $link $key1 $key2 ...)
```

A short hand for

```
(string.concat $link (string.Field $key1) (string.field $key2) ...)
```

Note: `$key1`, `$key2` etc.

#### string.lower

```
(string.lower $value)
```

Change `$value` to lowercase

## Error Handling

When using ruler, you might encounter these common errors:

1. Syntax Errors: Occur when the rule string is not properly formatted
2. Context Key Errors: When accessing non-existent fields in the context
3. Type Errors: When comparing incompatible types

Example of handling errors:

```python
try:
    rule = genruler.parse('(condition.equal (basic.field "age") 25)')
    result = rule({})  # Empty context
except KeyError:
    print("Field not found in context")
except Exception as e:
    print(f"An error occurred: {str(e)}")
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
