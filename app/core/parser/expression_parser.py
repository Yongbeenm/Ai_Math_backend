"""
Turn a plain-text math expression (already Khmer-normalized and extracted,
e.g. "2x+5=15") into a SymPy expression or equation.

This is the boundary between "text" and "math": everything after this point
in the pipeline works with SymPy objects, never strings, until the very end
when we render steps back out.
"""
from __future__ import annotations

from dataclasses import dataclass

import sympy
from sympy import Eq, Symbol
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

_TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)


class ExpressionParseError(Exception):
    """Raised when the given text cannot be parsed as math at all."""


@dataclass
class ParsedMath:
    raw_text: str
    is_equation: bool
    sympy_expr: sympy.Expr | Eq
    symbols: list[Symbol]


def parse_math_text(raw_expression: str) -> ParsedMath:
    """
    Parse text such as '2x+5=15' or '3*(4+2)' into a SymPy Eq or Expr.

    Supports implicit multiplication ('2x' -> '2*x') and '^' as power
    ('x^2' -> 'x**2'), which is how most Khmer students actually write
    exponents.
    """
    text = raw_expression.strip()

    try:
        if "=" in text:
            lhs_text, rhs_text = text.split("=", 1)
            lhs = parse_expr(lhs_text, transformations=_TRANSFORMATIONS)
            rhs = parse_expr(rhs_text, transformations=_TRANSFORMATIONS)
            expr: sympy.Expr | Eq = Eq(lhs, rhs)
            is_equation = True
        else:
            expr = parse_expr(text, transformations=_TRANSFORMATIONS)
            is_equation = False
    except Exception as exc:  # sympy raises several different error types
        raise ExpressionParseError(
            f"Could not parse expression: {raw_expression!r}"
        ) from exc

    free_symbols = sorted(expr.free_symbols, key=lambda s: s.name)
    return ParsedMath(
        raw_text=raw_expression,
        is_equation=is_equation,
        sympy_expr=expr,
        symbols=free_symbols,
    )
