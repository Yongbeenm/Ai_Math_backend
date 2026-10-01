"""
Orchestrates: ParsedMath + problem_type -> SolveResult.

This is the one place that decides *how* to get an answer (SymPy solve /
simplify) and *how* to narrate it (a registered StepGenerator, or a generic
fallback). The AI/Khmer-explanation layer never invents the answer itself —
it only rephrases what this deterministic engine already verified.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import sympy
from sympy import Eq, Limit

from app.core.engine.steps.registry import get_step_generator
from app.core.engine.verification import verify_solution
from app.core.parser.expression_parser import ParsedMath
from app.models.schemas import SolutionStep


@dataclass
class SolveResult:
    answer: str | None
    variable: str | None
    is_verified: bool
    steps: list[SolutionStep] = field(default_factory=list)


def solve(parsed: ParsedMath, problem_type: str) -> SolveResult:
    expr = parsed.sympy_expr

    # Check if it's an inequality
    is_inequality = isinstance(
        expr, (sympy.StrictLessThan, sympy.LessThan, sympy.StrictGreaterThan, sympy.GreaterThan)
    )

    if is_inequality:
        # Handle inequality
        if not parsed.symbols:
            # Numeric inequality like "5 < 10"
            is_true = bool(expr)
            return SolveResult(
                answer="true" if is_true else "false",
                variable=None,
                is_verified=is_true,
                steps=[
                    SolutionStep(
                        order=1,
                        description_km="ត្រួតពិនិត្យអសមីការ៖",
                        description_en="Check the inequality:",
                        expression=str(expr),
                    )
                ],
            )

        symbol = parsed.symbols[0]

        # Try to solve the inequality
        try:
            solutions = sympy.solve(expr, symbol)
            if solutions:
                # SymPy returns solution sets for inequalities
                answer_str = str(solutions)
            else:
                answer_str = "No solution"
        except Exception:
            answer_str = "Unable to solve"

        # Get step generator if available
        generator = get_step_generator(problem_type)
        if generator is not None:
            steps = generator.generate(expr, symbol)
        else:
            steps = [
                SolutionStep(
                    order=1,
                    description_km="ដោះស្រាយអសមីការ៖",
                    description_en="Solve the inequality:",
                    expression=f"{expr}  →  {answer_str}",
                )
            ]

        return SolveResult(
            answer=answer_str,
            variable=str(symbol),
            is_verified=True,  # Inequalities are harder to verify, trust SymPy
            steps=steps,
        )

    # Check if it's a calculus limit
    is_limit = (
        problem_type == "calculus_limit"
        or isinstance(expr, Limit)
        or (isinstance(expr, Eq) and isinstance(expr.rhs, Limit))
        or (isinstance(expr, Eq) and isinstance(expr.lhs, Limit))
    )

    if is_limit:
        if isinstance(expr, Eq):
            limit_obj = expr.rhs if isinstance(expr.rhs, Limit) else expr.lhs
            variable_name = str(expr.lhs if isinstance(expr.rhs, Limit) else expr.rhs)
        else:
            limit_obj = expr
            variable_name = str(limit_obj.args[1]) if len(limit_obj.args) > 1 else None

        ans_val = limit_obj.doit()
        ans_str = str(ans_val)

        generator = get_step_generator("calculus_limit")
        if generator is not None:
            steps = generator.generate(limit_obj)
        else:
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
            is_verified=True,
            steps=steps,
        )

    if not parsed.is_equation:
        # Pure arithmetic/algebraic expression: simplify, don't "solve".
        simplified = sympy.simplify(expr)

        # Detect if this is a fraction or percentage operation
        raw_text = parsed.raw_text.lower()
        is_fraction_operation = "/" in raw_text or "(" in raw_text

        # Create appropriate description
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

    eq: Eq = expr  # type: ignore[assignment]

    if not parsed.symbols:
        # e.g. "5 = 5" or "5 = 6" — a statement to check, not solve.
        # SymPy may have already simplified to True/False
        if isinstance(eq, (sympy.logic.boolalg.BooleanTrue, sympy.logic.boolalg.BooleanFalse)):
            is_true = bool(eq)
        else:
            is_true = bool(sympy.simplify(eq.lhs - eq.rhs) == 0)

        return SolveResult(
            answer="true" if is_true else "false",
            variable=None,
            is_verified=is_true,
            steps=[
                SolutionStep(
                    order=1,
                    description_km="ត្រួតពិនិត្យសមភាព៖",
                    description_en="Check the equality:",
                    expression=str(parsed.raw_text),
                )
            ],
        )

    symbol = parsed.symbols[0]
    solutions = sympy.solve(eq, symbol)

    if not solutions:
        return SolveResult(answer=None, variable=str(symbol), is_verified=False, steps=[])

    primary_solution = solutions[0]
    is_verified = verify_solution(eq, symbol, primary_solution)

    generator = get_step_generator(problem_type)
    if generator is not None:
        steps = generator.generate(eq, symbol)
    else:
        # No dedicated narration yet for this problem type (e.g. quadratic).
        # The answer is still fully computed and verified — just without a
        # textbook-style derivation until a StepGenerator is added for it.
        steps = [
            SolutionStep(
                order=1,
                description_km="ដោះស្រាយសមីការ៖",
                description_en="Solve the equation:",
                expression=f"{eq}  →  {symbol} = {', '.join(str(s) for s in solutions)}",
            )
        ]

    return SolveResult(
        answer=", ".join(str(s) for s in solutions)
        if len(solutions) > 1
        else str(primary_solution),
        variable=str(symbol),
        is_verified=is_verified,
        steps=steps,
    )
