"""
Registry mapping problem_type -> StepGenerator.

To add support for a new topic later (quadratic, systems of equations,
calculus, ...): write a class implementing StepGenerator in its own file,
then add one line here. No other file needs to change.
"""

from __future__ import annotations

from app.reasoning.steps.base import StepGenerator
from app.reasoning.steps.calculus_limit import LimitStepGenerator
from app.reasoning.steps.inequality import LinearInequalityStepGenerator
from app.reasoning.steps.linear import LinearStepGenerator
from app.reasoning.steps.polynomial import PolynomialStepGenerator
from app.reasoning.steps.quadratic import QuadraticStepGenerator
from app.reasoning.steps.system import SystemStepGenerator

_GENERATORS: dict[str, StepGenerator] = {
    generator.problem_type: generator
    for generator in [
        LinearStepGenerator(),
        QuadraticStepGenerator(),
        PolynomialStepGenerator(),
        SystemStepGenerator(),
        LinearInequalityStepGenerator(),
        LimitStepGenerator(),
    ]
}


def get_step_generator(problem_type: str) -> StepGenerator | None:
    """Returns None when no dedicated generator is registered yet for this
    problem_type (e.g. quadratic_equation) — callers should fall back to a
    generic, still-verified-but-not-narrated answer in that case."""
    return _GENERATORS.get(problem_type)
