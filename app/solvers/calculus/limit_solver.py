"""
Calculus limit solver.
"""

from __future__ import annotations

import sympy
from sympy import Eq, Limit

from app.api.schemas.responses import SolutionStep
from app.parser.math_parser.expression_parser import ParsedMath
from app.solvers.base import BaseSolver, SolveResult


class LimitSolver(BaseSolver):
    """
    Solves calculus limit problems.

    Handles:
    - Standard limits: lim_{x→a} f(x)
    - One-sided limits: lim_{x→a⁺} f(x), lim_{x→a⁻} f(x)
    - Limits at infinity: lim_{x→∞} f(x)
    - Limits with equations: f(x) = lim_{x→a} g(x)

    Uses SymPy's limit evaluation with step-by-step explanation generation.
    """

    SUPPORTED_TYPES = {
        "calculus_limit",
    }

    def can_solve(self, problem_type: str) -> bool:
        return problem_type in self.SUPPORTED_TYPES

    def solve(self, parsed: ParsedMath, problem_type: str) -> SolveResult:
        """
        Evaluate a limit and generate steps.

        Process:
        1. Extract the Limit object from the expression
        2. Evaluate using SymPy's .doit() method
        3. Generate steps using the limit step generator
        4. Return formatted result
        """
        expr = parsed.sympy_expr

        # Extract limit object and variable name
        limit_obj, variable_name = self._extract_limit(expr)

        if limit_obj is None:
            return SolveResult(
                answer=None,
                variable=None,
                is_verified=False,
                steps=[
                    SolutionStep(
                        order=1,
                        description_km="កន្សោមមិនមែនជាលីមីតទេ",
                        description_en="Expression is not a limit",
                        expression=str(expr),
                    )
                ],
            )

        # Evaluate the limit
        try:
            ans_val = limit_obj.doit()
            ans_str = str(ans_val)
        except Exception as e:
            return SolveResult(
                answer=None,
                variable=variable_name,
                is_verified=False,
                steps=[
                    SolutionStep(
                        order=1,
                        description_km=f"មិនអាចគណនាលីមីតបាន៖ {str(e)}",
                        description_en=f"Unable to evaluate limit: {str(e)}",
                        expression=str(limit_obj),
                    )
                ],
            )

        # Generate steps using step generator if available
        generator = self._get_step_generator("calculus_limit")
        if generator is not None:
            steps = generator.generate(limit_obj)
        else:
            # Fallback generic step
            steps = [
                SolutionStep(
                    order=1,
                    description_km="គណនាលីមីត៖",
                    description_en="Evaluate the limit:",
                    expression=f"{expr} = {ans_str}",
                )
            ]

        return SolveResult(
            answer=ans_str,
            variable=variable_name,
            is_verified=True,  # Limits are trusted from SymPy
            steps=steps,
            metadata={
                "limit_expression": str(limit_obj.args[0]) if limit_obj.args else None,
                "limit_point": str(limit_obj.args[2]) if len(limit_obj.args) > 2 else None,
                "limit_variable": variable_name,
            },
        )

    def _extract_limit(self, expr: sympy.Expr) -> tuple[Limit | None, str | None]:
        """
        Extract the Limit object and variable name from the expression.

        Handles two cases:
        1. Direct Limit: lim_{x→a} f(x)
        2. Equation with Limit: y = lim_{x→a} f(x)

        Returns:
            Tuple of (Limit object, variable name string) or (None, None) if not a limit
        """
        # Case 1: Direct limit
        if isinstance(expr, Limit):
            limit_obj = expr
            variable_name = str(limit_obj.args[1]) if len(limit_obj.args) > 1 else None
            return limit_obj, variable_name

        # Case 2: Equation with limit (y = lim_{x→a} f(x))
        if isinstance(expr, Eq):
            # Check if RHS is a limit
            if isinstance(expr.rhs, Limit):
                limit_obj = expr.rhs
                variable_name = str(expr.lhs)  # Use LHS as the variable name
                return limit_obj, variable_name

            # Check if LHS is a limit
            if isinstance(expr.lhs, Limit):
                limit_obj = expr.lhs
                variable_name = str(expr.rhs)
                return limit_obj, variable_name

        # Not a limit expression
        return None, None
