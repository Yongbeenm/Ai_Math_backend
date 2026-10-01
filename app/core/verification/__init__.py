"""
Enhanced verification module with problem-type-specific strategies.

This module provides deterministic verification of mathematical solutions
without relying on LLMs. Each problem type gets a specialized verification
strategy that checks the solution is actually correct.
"""

from app.core.verification.verifier import SolutionVerifier, VerificationResult

__all__ = ["SolutionVerifier", "VerificationResult"]
