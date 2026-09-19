"""
Classify a ParsedMath object into a problem_type string. This string drives
both which step generator is used and what the API reports back in
`problem_type`, so keep the set of values stable — the mobile app may
eventually branch on it (e.g. to show a different icon per problem type).
"""
from __future__ import annotations

import sympy
from sympy import Eq, Limit, Poly

from app.core.parser.expression_parser import ParsedMath


def classify_problem(parsed: ParsedMath) -> str:
    expr = parsed.sympy_expr
    
    # Check if it's an inequality (relational expression) - do this FIRST
    # before checking is_equation, since inequalities have is_equation=False
    if isinstance(expr, (sympy.StrictLessThan, sympy.LessThan, 
                        sympy.StrictGreaterThan, sympy.GreaterThan)):
        if len(parsed.symbols) == 0:
            return "numeric_inequality"
        if len(parsed.symbols) > 1:
            return "multivariate_inequality"
        # Determine if it's linear or higher degree
        try:
            symbol = parsed.symbols[0]
            difference = sympy.expand(expr.lhs - expr.rhs)
            degree = Poly(difference, symbol).degree()
            if degree == 1:
                return "linear_inequality"
            elif degree == 2:
                return "quadratic_inequality"
            else:
                return "polynomial_inequality"
        except Exception:
            return "unknown_inequality"
    
    # Check if it's a calculus limit
    if isinstance(expr, Limit):
        return "calculus_limit"
    if isinstance(expr, Eq) and (isinstance(expr.rhs, Limit) or isinstance(expr.lhs, Limit)):
        return "calculus_limit"

    # Now check equations
    if not parsed.is_equation:
        return "algebraic_expression" if parsed.symbols else "arithmetic_expression"

    eq = parsed.sympy_expr  # a sympy.Eq

    if len(parsed.symbols) == 0:
        return "numeric_equation"  # e.g. "5 = 5" — a statement, not a solve

    if len(parsed.symbols) > 1:
        return "multivariate_equation"  # e.g. two-variable systems — future work

    symbol = parsed.symbols[0]
    try:
        difference = sympy.expand(eq.lhs - eq.rhs)
        degree = Poly(difference, symbol).degree()
    except Exception:
        return "unknown_equation"

    if degree == 1:
        return "linear_equation"
    if degree == 2:
        return "quadratic_equation"
    if degree > 2:
        return "polynomial_equation"
    return "unknown_equation"
