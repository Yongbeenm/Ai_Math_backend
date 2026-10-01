"""
Knowledge Base Module for Lesson-Aware Mathematics Instruction.
"""

from app.knowledge.models import (
    Chapter,
    Concept,
    CurriculumExample,
    ExplanationStepTemplate,
    ExplanationTemplate,
    Lesson,
    LessonMetadata,
    Method,
    RuleFormula,
    SubjectDomain,
)
from app.knowledge.registry import KnowledgeBaseRegistry, get_knowledge_registry

__all__ = [
    "Chapter",
    "Concept",
    "CurriculumExample",
    "ExplanationStepTemplate",
    "ExplanationTemplate",
    "KnowledgeBaseRegistry",
    "Lesson",
    "LessonMetadata",
    "Method",
    "RuleFormula",
    "SubjectDomain",
    "get_knowledge_registry",
]
