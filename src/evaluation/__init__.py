"""
Evaluation Engine for RAG Property Search System.

This module provides constraint-based evaluation with confusion matrix metrics
as described in the thesis methodology.
"""

from .models import (
    ConstraintResult,
    GoldQuestion,
    PropertyCheck,
    QueryEvaluation,
    EvaluationMetrics,
    ConfusionMatrix,
)
from .constraint_checker import ConstraintChecker
from .evaluator import Evaluator
from .html_report import HTMLReportGenerator

__all__ = [
    "ConstraintResult",
    "GoldQuestion",
    "PropertyCheck",
    "QueryEvaluation",
    "EvaluationMetrics",
    "ConfusionMatrix",
    "ConstraintChecker",
    "Evaluator",
    "HTMLReportGenerator",
]
