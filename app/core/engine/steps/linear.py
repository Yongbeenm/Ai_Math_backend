"""
Step-by-step derivation for linear equations (ax + b = cx + d).

The algorithm:
  1. Show the original equation.
  2. If the variable appears on both sides, collect it on the left.
  3. Move the remaining constant off the variable's side (add/subtract).
  4. Clear the coefficient (divide, or multiply by the reciprocal when the
     coefficient is itself a fraction — the way a textbook would phrase it).
  5. State the answer.

Every arithmetic operation is done by SymPy, and the final value is
substituted back and checked by verification.verify_solution before it is
ever returned to the API layer — the steps shown here are a *description*
of a computation SymPy already did, not a separate, potentially-wrong,
free-form explanation.
"""
from __future__ import annotations

import sympy
from sympy import Eq, Symbol, expand, nsimplify

from app.core.engine.steps.base import StepGenerator
from app.models.schemas import SolutionStep


def _format_number(value: sympy.Expr) -> str:
    """Render a number the way a textbook would: no '.0', fractions kept as
    fractions rather than decimals."""
    if value == sympy.floor(value):
        try:
            return str(int(value))
        except TypeError:
            pass
    return str(value)


class LinearStepGenerator(StepGenerator):
    problem_type = "linear_equation"

    def generate(self, eq: Eq, symbol: Symbol) -> list[SolutionStep]:
        steps: list[SolutionStep] = []
        order = 1

        lhs = expand(eq.lhs)
        rhs = expand(eq.rhs)

        steps.append(
            SolutionStep(
                order=order,
                description_km="សមីការដើម៖",
                description_en="Original equation:",
                expression=f"{lhs} = {rhs}",
            )
        )
        order += 1

        lhs_coeff = lhs.coeff(symbol, 1)
        lhs_const = lhs - lhs_coeff * symbol
        rhs_coeff = rhs.coeff(symbol, 1)
        rhs_const = rhs - rhs_coeff * symbol

        # Step: collect all variable terms on the left, if needed.
        if rhs_coeff != 0:
            new_lhs_coeff = lhs_coeff - rhs_coeff
            new_lhs_expr = new_lhs_coeff * symbol + lhs_const
            new_rhs = rhs_const
            steps.append(
                SolutionStep(
                    order=order,
                    description_km=f"ផ្លាស់ទី {symbol} ទាំងអស់មកខាងឆ្វេង៖",
                    description_en=f"Move all {symbol} terms to the left side:",
                    expression=f"{new_lhs_expr} = {new_rhs}",
                )
            )
            order += 1
            lhs_coeff = new_lhs_coeff
            rhs = new_rhs
        else:
            rhs = rhs_const

        # Step: move the remaining constant off the variable's side.
        if lhs_const != 0:
            new_rhs = rhs - lhs_const
            if lhs_const > 0:
                description_km = f"ដក {_format_number(lhs_const)} ពីភាគីទាំងពីរ៖"
                description_en = f"Subtract {_format_number(lhs_const)} from both sides:"
            else:
                description_km = f"បូក {_format_number(-lhs_const)} ទៅភាគីទាំងពីរ៖"
                description_en = f"Add {_format_number(-lhs_const)} to both sides:"
            steps.append(
                SolutionStep(
                    order=order,
                    description_km=description_km,
                    description_en=description_en,
                    expression=f"{lhs_coeff * symbol} = {new_rhs}",
                )
            )
            order += 1
            rhs = new_rhs

        # Step: clear the coefficient of the variable.
        if lhs_coeff != 1:
            is_proper_fraction = lhs_coeff.is_Rational and lhs_coeff.q != 1
            if is_proper_fraction:
                reciprocal = nsimplify(1 / lhs_coeff)
                final_value = nsimplify(rhs * reciprocal)
                description_km = f"គុណភាគីទាំងពីរដោយ {_format_number(reciprocal)}៖"
                description_en = f"Multiply both sides by {_format_number(reciprocal)}:"
            else:
                final_value = nsimplify(rhs / lhs_coeff)
                description_km = f"ចែកភាគីទាំងពីរដោយ {_format_number(lhs_coeff)}៖"
                description_en = f"Divide both sides by {_format_number(lhs_coeff)}:"
            steps.append(
                SolutionStep(
                    order=order,
                    description_km=description_km,
                    description_en=description_en,
                    expression=f"{symbol} = {final_value}",
                )
            )
            order += 1
        else:
            final_value = rhs

        steps.append(
            SolutionStep(
                order=order,
                description_km=f"ចម្លើយ៖ {symbol} = {_format_number(final_value)}",
                description_en=f"Answer: {symbol} = {_format_number(final_value)}",
                expression=f"{symbol} = {_format_number(final_value)}",
            )
        )
        return steps
