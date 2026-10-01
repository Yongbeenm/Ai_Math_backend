"""
Base solver interface that all domain-specific solvers must implement.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import sympy

from app.parser.math_parser.expression_parser import ParsedMath
from app.solvers.base.types import SolveResult


class BaseSolver(ABC):
    """
    Abstract base class for all mathematical problem solvers.

    Each solver is responsible for:
    1. Determining if it can handle a given problem type
    2. Computing the solution using SymPy
    3. Verifying the solution is correct
    4. Generating step-by-step explanation (via step generators)

    Subclasses must implement:
    - can_solve(): Check if this solver handles the problem type
    - solve(): Compute and return the solution with steps
    """

    @abstractmethod
    def can_solve(self, problem_type: str) -> bool:
        """
        Determine if this solver can handle the given problem type.

        Args:
            problem_type: Problem type string from classifier
                         (e.g., "linear_equation", "quadratic_equation", "calculus_limit")

        Returns:
            True if this solver can handle this problem type
        """
        pass

    @abstractmethod
    def solve(self, parsed: ParsedMath, problem_type: str) -> SolveResult:
        """
        Solve the mathematical problem and generate steps.

        Args:
            parsed: Parsed mathematical expression/equation
            problem_type: Problem type string from classifier

        Returns:
            SolveResult containing answer, verification status, and steps

        Raises:
            ValueError: If the problem cannot be solved
        """
        pass

    def _verify_solution(
        self, equation: sympy.Eq, symbol: sympy.Symbol, solution: sympy.Expr
    ) -> bool:
        """
        Verify a solution by substituting it back into the equation.

        Args:
            equation: The original equation
            symbol: The variable being solved for
            solution: The proposed solution value

        Returns:
            True if the solution is correct (LHS ≈ RHS within tolerance)
        """
        # Use legacy verification function that returns boolean
        from app.core.engine.verification import verify_solution

        return verify_solution(equation, symbol, solution)

    def _get_step_generator(self, problem_type: str):
        """
        Get the step generator for this problem type, if available.

        Args:
            problem_type: Problem type string

        Returns:
            StepGenerator instance or None if no generator registered
        """
        from app.reasoning.steps.registry import get_step_generator

        return get_step_generator(problem_type)


class ExpressionEvaluator(BaseSolver):
    """
    Evaluates arithmetic and algebraic expressions (not equations).

    Handles:
    - Arithmetic: "2 + 3 * 4"
    - Fractions: "1/2 + 1/3"
    - Algebraic expressions: "2x + 3x" → "5x"
    - Simplification: "sqrt(16)" → "4"
    """

    def can_solve(self, problem_type: str) -> bool:
        return problem_type in (
            "arithmetic_expression",
            "algebraic_expression",
        )

    def solve(self, parsed: ParsedMath, problem_type: str) -> SolveResult:
        """Simplify and evaluate the expression."""
        from app.api.schemas.responses import SolutionStep

        expr = parsed.sympy_expr
        simplified = sympy.simplify(expr)

        # Detect operation type from raw text
        raw_text = parsed.raw_text.lower()
        is_fraction_operation = "/" in raw_text or "(" in raw_text

        if is_fraction_operation:
            description_km = "គណនាប្រភាគ៖"
            description_en = "Calculate the fraction:"
        else:
            description_km = "គណនាកន្សោម៖"
            description_en = "Evaluate the expression:"

        return SolveResult(
            answer=str(simplified),
            variable=None,
            is_verified=True,
            steps=[
                SolutionStep(
                    order=1,
                    description_km=description_km,
                    description_en=description_en,
                    expression=f"{expr} = {simplified}",
                )
            ],
        )


class StatementChecker(BaseSolver):
    """
    Checks truth value of numeric equations/inequalities without variables.

    Handles:
    - Numeric equations: "5 = 5" → True
    - Numeric inequalities: "3 < 5" → True
    """

    def can_solve(self, problem_type: str) -> bool:
        return problem_type in (
            "numeric_equation",
            "numeric_inequality",
        )

    def solve(self, parsed: ParsedMath, problem_type: str) -> SolveResult:
        """Check if the statement is true."""
        from app.api.schemas.responses import SolutionStep

        expr = parsed.sympy_expr

        # Determine truth value
        if isinstance(expr, sympy.Eq):
            # Numeric equation
            if isinstance(
                expr, (sympy.logic.boolalg.BooleanTrue, sympy.logic.boolalg.BooleanFalse)
            ):
                is_true = bool(expr)
            else:
                is_true = bool(sympy.simplify(expr.lhs - expr.rhs) == 0)

            description_km = "ត្រួតពិនិត្យសមភាព៖"
            description_en = "Check the equality:"
        else:
            # Numeric inequality
            is_true = bool(expr)
            description_km = "ត្រួតពិនិត្យអសមីការ៖"
            description_en = "Check the inequality:"

        return SolveResult(
            answer="true" if is_true else "false",
            variable=None,
            is_verified=is_true,
            steps=[
                SolutionStep(
                    order=1,
                    description_km=description_km,
                    description_en=description_en,
                    expression=str(parsed.raw_text),
                )
            ],
        )
