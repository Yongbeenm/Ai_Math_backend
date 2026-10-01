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

    SUPPORTED_TYPES = (
        "arithmetic_expression",
        "algebraic_expression",
        "factored_expression",
        "expression_factorization",
        "polynomial_factorization",
        "expression_simplification",
        "fraction_simplification",
        "radical_simplification",
        "expression_expansion",
        "polynomial_expansion",
    )

    def can_solve(self, problem_type: str) -> bool:
        return problem_type in self.SUPPORTED_TYPES

    def solve(self, parsed: ParsedMath, problem_type: str) -> SolveResult:
        """Evaluate, simplify, expand, or factor the expression."""
        from app.api.schemas.responses import SolutionStep

        expr = parsed.sympy_expr

        variable = None
        if parsed.raw_text and "=" in parsed.raw_text:
            parts = parsed.raw_text.split("=", 1)
            pot_var = parts[0].strip()
            if len(pot_var) <= 2 and pot_var.replace("(", "").replace(")", "").isalpha():
                variable = pot_var
        if isinstance(expr, sympy.Eq) and isinstance(expr.lhs, sympy.Symbol):
            if variable is None:
                variable = str(expr.lhs)
            expr = expr.rhs

        lesson_info = None

        if problem_type in ("factored_expression", "expression_expansion", "polynomial_expansion"):
            evaluated = sympy.expand(expr)
            from app.explanation.engine import get_explanation_engine

            engine = get_explanation_engine()
            steps, lesson_info = engine.generate_explanation(
                expr, problem_type=problem_type, raw_text=parsed.raw_text, symbol=None
            )
            if not steps:
                generator = self._get_step_generator(problem_type)
                if generator is not None and hasattr(generator, "generate"):
                    steps = generator.generate(expr, symbol=None, raw_text=parsed.raw_text)
                else:
                    steps = [
                        SolutionStep(
                            order=1,
                            description_km="គណនាផលគុណ និងពន្លាតកន្សោម៖",
                            description_en="Calculate product and expand the expression:",
                            expression=f"{sympy.latex(expr)} = {sympy.latex(evaluated)}",
                        )
                    ]
        elif problem_type in ("expression_factorization", "polynomial_factorization"):
            evaluated = sympy.factor(expr)
            from app.explanation.engine import get_explanation_engine

            engine = get_explanation_engine()
            steps, lesson_info = engine.generate_explanation(
                expr, problem_type=problem_type, raw_text=parsed.raw_text, symbol=None
            )
            if not steps:
                steps = [
                    SolutionStep(
                        order=1,
                        description_km="កន្សោមដើម៖",
                        description_en="Original expression:",
                        expression=sympy.latex(expr),
                    ),
                    SolutionStep(
                        order=2,
                        description_km="ដាក់ជាផលគុណកត្តា (បំបែកកត្តារួម ឬប្រើរូបមន្តស្មើភាព)៖",
                        description_en="Factor into product (factoring out common terms or identities):",
                        expression=f"= {sympy.latex(evaluated)}",
                    ),
                ]
        elif problem_type in ("radical_simplification",):
            evaluated = sympy.simplify(expr)
            steps = [
                SolutionStep(
                    order=1,
                    description_km="កន្សោមដើម៖",
                    description_en="Original expression:",
                    expression=sympy.latex(expr),
                ),
                SolutionStep(
                    order=2,
                    description_km="សម្រួលរ៉ាឌីកាល់ (ទាញកត្តាការេពេញចេញក្រៅ)៖",
                    description_en="Simplify radical (extract perfect square factors):",
                    expression=f"= {sympy.latex(evaluated)}",
                ),
            ]
        else:
            evaluated = sympy.simplify(expr)
            raw_text = parsed.raw_text.lower()
            is_fraction_operation = "/" in raw_text
            if is_fraction_operation:
                description_km = "គណនាប្រភាគ និងសម្រួល៖"
                description_en = "Calculate and simplify the fraction:"
            else:
                description_km = "គណនាកន្សោម៖"
                description_en = "Evaluate the expression:"

            steps = [
                SolutionStep(
                    order=1,
                    description_km=description_km,
                    description_en=description_en,
                    expression=f"{sympy.latex(expr)} = {sympy.latex(evaluated)}",
                )
            ]

        return SolveResult(
            answer=str(evaluated),
            variable=variable,
            is_verified=True,
            steps=steps,
            lesson_info=lesson_info,
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
