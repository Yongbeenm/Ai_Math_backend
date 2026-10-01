"""
Integrals Lessons and Chapter (Grade 12 Integral Calculus).
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

method_integral_power_rule = Method(
    id="method_integral_power_rule",
    rule_id="rule_integral_power_rule",
    name_km="រូបមន្តអាំងតេក្រាលស្វ័យគុណ",
    name_en="Power Rule for Integration",
    description_km="អាំងតេក្រាលនៃ xⁿ dx គឺ (xⁿ⁺¹)/(n+1) + C (ចំពោះ n ≠ -1)។",
    description_en="Integral of xⁿ dx is (xⁿ⁺¹)/(n+1) + C for n != -1.",
    applicability="Integrals of power expressions xⁿ.",
    template=template_limit_direct_substitution,
    examples=[
        CurriculumExample(
            id="ex_integ_1",
            method_id="method_integral_power_rule",
            problem_raw=r"\int x^2 \, dx",
            problem_latex=r"\int x^2 \, dx",
            solution_latex=r"\frac{x^3}{3} + C",
            explanation_summary_km="បន្ថែមស្វ័យគុណ 1 រួចចែកនឹងស្វ័យគុណថ្មី ទទួលបាន x³/3 + C។",
        ),
    ],
)

rule_integral_power = RuleFormula(
    id="rule_integral_power_rule",
    concept_id="concept_indefinite_integral",
    name_km="រូបមន្តព្រីមីទីវស្វ័យគុណ",
    name_en="Indefinite Integral Power Rule",
    formula_latex=r"\int x^n \, dx = \frac{x^{n+1}}{n+1} + C",
    methods=[method_integral_power_rule],
)

concept_integral_basics = Concept(
    id="concept_indefinite_integral",
    lesson_id="lesson_integrals_evaluation",
    order=1,
    title_km="ព្រីមីទីវ និងអាំងតេក្រាលមិនកំណត់ (Indefinite Integrals)",
    title_en="Primitives and Indefinite Integrals",
    definition_km="ព្រីមីទីវនៃអនុគមន៍ f គឺជាអនុគមន៍ F ដែល F'(x) = f(x)។",
    definition_en="Antiderivative F of function f satisfying F'(x) = f(x).",
    rules=[rule_integral_power],
)

lesson_integrals = Lesson(
    id="lesson_integrals_evaluation",
    chapter_id="chapter_calculus_integrals",
    order=1,
    title_km="អាំងតេក្រាលមិនកំណត់ និងកំណត់ (Integrals)",
    title_en="Indefinite and Definite Integrals",
    description_km="ការគណនាព្រីមីទីវ អាំងតេក្រាលកំណត់ និងការគណនាក្រឡាផ្ទៃ។",
    description_en="Computing primitives, definite integrals, and area calculations.",
    concepts=[concept_integral_basics],
)

chapter_integrals = Chapter(
    id="chapter_calculus_integrals",
    domain=SubjectDomain.CALCULUS,
    order=5,
    title_km="ជំពូកទី៤ : អាំងតេក្រាល (Integrals)",
    title_en="Chapter 4: Integrals",
    grade_level=12,
    description_km="អាំងតេក្រាលមិនកំណត់ អាំងតេក្រាលកំណត់ និងអនុវត្តន៍។",
    description_en="Indefinite, definite integrals, and geometric applications.",
    lessons=[lesson_integrals],
)
