"""
Calculus Explanation Templates (Grade 12 BacII Focus).

Curriculum-aligned step templates for limits:
1. Direct Substitution (Continuous functions: lim_{x->c} f(x) = f(c))
2. Indeterminate Form [0/0] via Conjugate Rationalization
3. Indeterminate Form [0/0] via Polynomial Factorization & Cancellation
"""

from __future__ import annotations

from app.knowledge.models import ExplanationStepTemplate, ExplanationTemplate

# --- Template 1: Direct Substitution (Continuous Functions) ---
template_limit_direct_substitution = ExplanationTemplate(
    id="tmpl_limit_direct_substitution",
    method_id="method_limit_direct_substitution",
    name_km="គណនាលីមីតដោយជំនួសតម្លៃផ្ទាល់ (អនុគមន៍ជាប់)",
    name_en="Direct Substitution for Continuous Functions",
    verification_strategy="none",
    pedagogical_notes_km="ប្រសិនបើអនុគមន៍ f កំណត់ និងជាប់ត្រង់ c នោះលីមីតស្មើនឹងតម្លៃអនុគមន៍ត្រង់ c ពោលគឺ lim_{x->c} f(x) = f(c)។",
    pedagogical_notes_en="If f is defined and continuous at c, the limit equals the function value f(c) by direct substitution.",
    steps=[
        ExplanationStepTemplate(
            order=1,
            action_type="identify_limit_expression",
            title_km="កំណត់កន្សោមលីមីត និងចំណុចខិតជិត",
            title_en="Identify Limit Expression & Target Value",
            rationale_template_km="កត់សម្គាល់អនុគមន៍ f(x) និងចំណុចដែលអថេរខិតជិត x -> c។",
            rationale_template_en="Identify the function f(x) and approach point x -> c.",
        ),
        ExplanationStepTemplate(
            order=2,
            action_type="check_continuity_and_substitute",
            title_km="ពិនិត្យភាពជាប់ និងជំនួសតម្លៃផ្ទាល់",
            title_en="Verify Continuity & Apply Direct Substitution",
            rationale_template_km="អនុគមន៍កំណត់ និងជាប់ត្រង់ចំណុចខិតជិត ដូច្នេះអាចអនុវត្តលក្ខណៈជំនួសផ្ទាល់ lim_{x->c} f(x) = f(c)។",
            rationale_template_en="The function is defined and continuous at the target point, so apply direct substitution lim_{x->c} f(x) = f(c).",
            rule_reference="\\lim_{x \\to c} f(x) = f(c)",
        ),
        ExplanationStepTemplate(
            order=3,
            action_type="compute_limit_value",
            title_km="គណនាតម្លៃលេខចុងក្រោយ",
            title_en="Compute Final Limit Value",
            rationale_template_km="គណនាតម្លៃលេខដែលទទួលបានពីការជំនួស ដើម្បីបានចម្លើយពិតប្រាកដ។",
            rationale_template_en="Evaluate the arithmetic expression obtained from substitution to determine the exact limit value.",
        ),
    ],
)

# --- Template 2: Indeterminate [0/0] via Conjugate Rationalization ---
template_limit_conjugate = ExplanationTemplate(
    id="tmpl_limit_conjugate",
    method_id="method_limit_conjugate",
    name_km="គណនាលីមីតរាង [0/0] ដោយគុណកន្សោមឆ្លាស់",
    name_en="Indeterminate Limit [0/0] via Conjugate Rationalization",
    verification_strategy="none",
    pedagogical_notes_km="គុណភាគយកនិងភាគបែងនឹងកន្សោមឆ្លាស់ ដើម្បីលុបរ៉ាឌីកាល់ និងសម្រួលកត្តាសូន្យ។",
    pedagogical_notes_en="Multiply numerator and denominator by conjugate to eliminate radicals and cancel indeterminate zero factors.",
    steps=[
        ExplanationStepTemplate(
            order=1,
            action_type="check_indeterminate_form",
            title_km="ជំនួសផ្ទាល់ និងកំណត់រាងមិនកំណត់ [0/0]",
            title_en="Direct Substitution & Identify Indeterminate Form [0/0]",
            rationale_template_km="ជំនួសតម្លៃ x -> c ផ្ទាល់ដើម្បីដឹងថាកន្សោមមានរាងមិនកំណត់ 0/0 ដែលត្រូវលុបបំបាត់។",
            rationale_template_en="Substitute x -> c to verify the indeterminate form [0/0].",
        ),
        ExplanationStepTemplate(
            order=2,
            action_type="multiply_conjugate",
            title_km="គុណភាគយក និងភាគបែងនឹងកន្សោមឆ្លាស់",
            title_en="Multiply Numerator & Denominator by Conjugate",
            rationale_template_km="ប្រើរូបមន្ត (√A - B)(√A + B) = A - B² ដើម្បីបំបាត់រ៉ាឌីកាល់។",
            rationale_template_en="Use (√A - B)(√A + B) = A - B² to eliminate square roots.",
            rule_reference="(\\sqrt{A} - B)(\\sqrt{A} + B) = A - B^2",
        ),
        ExplanationStepTemplate(
            order=3,
            action_type="cancel_zero_factor",
            title_km="សម្រួលកត្តារួម (x − c) ដែលនាំឱ្យស្មើសូន្យ",
            title_en="Cancel Indeterminate Factor (x − c)",
            rationale_template_km="លុបកត្តាដែលធ្វើឱ្យភាគយកនិងភាគបែងស្មើសូន្យចោល។",
            rationale_template_en="Cancel common factor responsible for numerator and denominator vanishing.",
            rule_reference="\\frac{(x - c)P(x)}{(x - c)Q(x)} = \\frac{P(x)}{Q(x)}",
        ),
        ExplanationStepTemplate(
            order=4,
            action_type="evaluate_reduced_limit",
            title_km="គណនាលីមីតនៃកន្សោមសម្រួលរួច",
            title_en="Evaluate Limit of Reduced Expression",
            rationale_template_km="ជំនួស x -> c ចូលក្នុងកន្សោមថ្មីដើម្បីទទួលបានតម្លៃលីមីតពិតប្រាកដ។",
            rationale_template_en="Substitute x -> c into the simplified expression to determine the final limit value.",
        ),
    ],
)

# --- Template 3: Indeterminate [0/0] via Factorization ---
template_limit_factor_cancel = ExplanationTemplate(
    id="tmpl_limit_factor_cancel",
    method_id="method_limit_factor_cancel",
    name_km="គណនាលីមីតរាង [0/0] ដោយដាក់ជាផលគុណកត្តា",
    name_en="Indeterminate Limit [0/0] via Factorization",
    verification_strategy="none",
    pedagogical_notes_km="ដាក់ភាគយកនិងភាគបែងជាផលគុណកត្តា រួចសម្រួលកត្តាសូន្យ (x - c)។",
    pedagogical_notes_en="Factor numerator and denominator, then cancel common indeterminate factor (x - c).",
    steps=[
        ExplanationStepTemplate(
            order=1,
            action_type="check_indeterminate_form",
            title_km="ជំនួសផ្ទាល់ និងកំណត់រាងមិនកំណត់ [0/0]",
            title_en="Direct Substitution & Identify Indeterminate Form [0/0]",
            rationale_template_km="ជំនួស x -> c ដើម្បីដឹងថាកន្សោមមានរាងមិនកំណត់ 0/0។",
            rationale_template_en="Substitute x -> c to verify the indeterminate form 0/0.",
        ),
        ExplanationStepTemplate(
            order=2,
            action_type="factor_polynomials",
            title_km="ដាក់ភាគយក និងភាគបែងជាផលគុណកត្តា",
            title_en="Factor Numerator & Denominator",
            rationale_template_km="បំបែកពហុធាភាគយក និងភាគបែងដើម្បីទាញកត្តា (x - c) ចេញ។",
            rationale_template_en="Factor numerator and denominator polynomials to isolate the (x - c) zero factor.",
        ),
        ExplanationStepTemplate(
            order=3,
            action_type="cancel_zero_factor",
            title_km="សម្រួលកត្តារួម (x − c)",
            title_en="Cancel Common Factor (x − c)",
            rationale_template_km="សម្រួលកត្តាដែលធ្វើឱ្យស្មើសូន្យចោល។",
            rationale_template_en="Cancel the common factor (x - c) that causes the 0/0 indeterminate form.",
        ),
        ExplanationStepTemplate(
            order=4,
            action_type="evaluate_reduced_limit",
            title_km="គណនាលីមីតចុងក្រោយ",
            title_en="Evaluate Final Limit",
            rationale_template_km="ជំនួស x -> c ចូលក្នុងកន្សោមសាមញ្ញដើម្បីទទួលបានលទ្ធផលចុងក្រោយ។",
            rationale_template_en="Substitute x -> c into the simplified fraction to find the final answer.",
        ),
    ],
)
