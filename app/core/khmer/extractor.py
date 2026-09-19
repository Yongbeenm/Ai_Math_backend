"""
Pull the mathematical expression out of a sentence that mixes Khmer words
and math, e.g. "ដោះស្រាយសមីការនេះ 2x + 5 = 15" -> "2x+5=15".

This is intentionally simple (regex-based) for phase 1. It is called from
one place only (math_service.process_question), so it can be swapped for a
smarter extractor (e.g. a sequence-tagging model) later without touching
anything else in the pipeline.
"""
import re

# A run of characters that looks like math: digits, letters (variables),
# operators, parentheses, decimal points, '=', inequality signs, and whitespace.
_EXPRESSION_RUN = re.compile(r"[0-9a-zA-Z.\+\-\*/\^=()\s<>=≤≥]{3,}")

# Two-or-more consecutive Latin letters is an instructional *word* ("solve",
# "find", "the"...), not a variable. Real algebra variables are single
# letters (x, y, n, ...), so stripping whole words first stops English (or
# romanized) instruction text from being swallowed into the expression as
# spurious multiplied-together variables, e.g. "solve 2x+5=15" would
# otherwise parse as "s*o*l*v*e*2*x+5=15".
#
# NOTE: this is a deliberate phase-1 simplification. If/when function names
# like sin/cos/log are supported, this rule will need to allow-list those.
_MULTI_LETTER_WORD = re.compile(r"[a-zA-Z]{2,}")


def extract_expression(normalized_text: str) -> str | None:
    """Return the best-guess math substring from already Khmer-normalized
    text, or None if nothing looking like math was found."""
    text_without_words = _MULTI_LETTER_WORD.sub(" ", normalized_text)

    candidates = _EXPRESSION_RUN.findall(text_without_words)
    if not candidates:
        return None

    # Prefer candidates that contain at least one digit; plain prose can
    # otherwise match short runs of spaces/parentheses.
    with_digits = [c for c in candidates if re.search(r"\d", c)]
    pool = with_digits or candidates

    best = max(pool, key=len).strip()
    best = re.sub(r"\s+", "", best)  # spacing doesn't matter to the parser
    return best or None
