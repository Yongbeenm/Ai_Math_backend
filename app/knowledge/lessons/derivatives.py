"""
Derivatives Lessons and Chapter (Grade 12 Differential Calculus).
"""

from __future__ import annotations

from app.knowledge.explanation_templates.calculus import template_limit_direct_substitution
from app.knowledge.models import (
    Chapter,
    Concept,
    CurriculumExample,
    Lesson,
    Method,
    RuleFormula,
    SubjectDomain,
)

method_power_rule = Method(
    id="method_derivative_power_rule",
    rule_id="rule_derivative_power_rule",
    name_km="វិធានដេរីវេស្វ័យគុណ xⁿ",
    name_en="Power Rule for Differentiation",
    description_km="ដេរីវេនៃ xⁿ គឺ n * xⁿ⁻¹។",
    description_en="Derivative of xⁿ is n * xⁿ⁻¹.",
    applicability="Power functions xⁿ where n is a real number.",
    template=template_limit_direct_substitution,  # Fallback template
    examples=[
        CurriculumExample(
            id="ex_deriv_1",
            method_id="method_derivative_power_rule",
            problem_raw=r"\frac{d}{dx}(x^3)",
            problem_latex=r"\frac{d}{dx}(x^3)",
            solution_latex=r"3x^2",
            explanation_summary_km="ទម្លាក់ស្វ័យគុណ 3 មកមុខ រួចបន្ថយស្វ័យគុណ 1 បាន 3x²។",
        ),
    ],
)

rule_power_rule = RuleFormula(
    id="rule_derivative_power_rule",
    concept_id="concept_derivative_rules",
    name_km="រូបមន្តដេរីវេស្វ័យគុណ",
    name_en="Power Rule Identity",
    formula_latex=r"(x^n)' = n x^{n-1}",
    methods=[method_power_rule],
)

concept_derivative_rules = Concept(
    id="concept_derivative_rules",
    lesson_id="lesson_derivatives_computation",
    order=1,
    title_km="វិធានដេរីវេគ្រឹះ (Basic Differentiation Rules)",
    title_en="Basic Differentiation Rules",
    definition_km="វិធានសម្រាប់គណនាដេរីវេនៃអនុគមន៍ស្វ័យគុណ ផលបូក ផលគុណ និងផលចែក។",
    definition_en="Standard rules for computing derivatives of power, sum, product, and quotient functions.",
    rules=[rule_power_rule],
)

lesson_derivatives = Lesson(
    id="lesson_derivatives_computation",
    chapter_id="chapter_calculus_derivatives",
    order=1,
    title_km="ដេរីវេនៃអនុគមន៍ (Derivatives)",
    title_en="Derivatives of Functions",
    description_km="និយមន័យដេរីវេ រូបមន្តគ្រឹះ និងអនុវត្តន៍ដេរីវេ។",
    description_en="Derivative definitions, standard formulas, and calculus applications.",
    concepts=[concept_derivative_rules],
)

chapter_derivatives = Chapter(
    id="chapter_calculus_derivatives",
    domain=SubjectDomain.CALCULUS,
    order=4,
    title_km="ជំពូកទី៣ : ដេរីវេ និងអនុវត្តន៍ (Derivatives)",
    title_en="Chapter 3: Derivatives and Applications",
    grade_level=12,
    description_km="ដេរីវេនៃអនុគمន៍ និងការសិក្សាអថេរភាពនៃអនុគមន៍។",
    description_en="Derivatives and function behavior studies.",
    lessons=[lesson_derivatives],
)
