"""
Data models for constraint-based evaluation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class ConstraintResult(Enum):
    """Result of a single constraint check."""
    PASS = "pass"
    FAIL = "fail"
    NA = "na"        # Constraint not applicable (not specified in gold)
    MISSING = "missing"  # Property data missing for this constraint


@dataclass
class LocationConstraint:
    """Location constraint from gold standard."""
    keywords: list[str] = field(default_factory=list)
    lat: Optional[float] = None
    lng: Optional[float] = None
    radius_km: float = 2.0


@dataclass
class PriceConstraint:
    """Price constraint from gold standard."""
    min: Optional[int] = None
    max: Optional[int] = None
    target: Optional[int] = None  # For "harga X-an" (around X) queries
    currency: str = "IDR"
    tolerance: float = 0.0  # No tolerance by default - strict matching


@dataclass
class BedroomConstraint:
    """Bedroom constraint from gold standard."""
    min: Optional[int] = None
    max: Optional[int] = None
    exact: Optional[int] = None


@dataclass
class FloorsConstraint:
    """Floors/stories constraint from gold standard."""
    min: Optional[int] = None
    max: Optional[int] = None
    exact: Optional[int] = None


@dataclass
class Constraints:
    """All constraints for a gold question."""
    property_type: Optional[str] = None
    listing_type: Optional[str] = None
    location: Optional[LocationConstraint] = None
    price: Optional[PriceConstraint] = None
    bedrooms: Optional[BedroomConstraint] = None
    floors: Optional[FloorsConstraint] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Constraints":
        """Create Constraints from dictionary."""
        location = None
        if "location" in data:
            loc_data = data["location"]
            location = LocationConstraint(
                keywords=loc_data.get("keywords", []),
                lat=loc_data.get("lat"),
                lng=loc_data.get("lng"),
                radius_km=loc_data.get("radius_km", 2.0),
            )

        price = None
        if "price" in data:
            price_data = data["price"]
            price = PriceConstraint(
                min=price_data.get("min"),
                max=price_data.get("max"),
                target=price_data.get("target"),
                currency=price_data.get("currency", "IDR"),
                tolerance=price_data.get("tolerance", 0.0),
            )

        bedrooms = None
        if "bedrooms" in data:
            bed_data = data["bedrooms"]
            bedrooms = BedroomConstraint(
                min=bed_data.get("min"),
                max=bed_data.get("max"),
                exact=bed_data.get("exact"),
            )

        floors = None
        if "floors" in data:
            floor_data = data["floors"]
            floors = FloorsConstraint(
                min=floor_data.get("min"),
                max=floor_data.get("max"),
                exact=floor_data.get("exact"),
            )

        return cls(
            property_type=data.get("property_type"),
            listing_type=data.get("listing_type"),
            location=location,
            price=price,
            bedrooms=bedrooms,
            floors=floors,
        )


@dataclass
class GoldQuestion:
    """Gold standard question with constraints."""
    id: int
    question: str
    category: str
    expected_result: str  # "has_data" or "no_data"
    constraints: Constraints
    notes: str = ""
    evaluation_mode: str = "auto"  # "auto" or "manual"

    @classmethod
    def from_dict(cls, data: dict) -> "GoldQuestion":
        """Create GoldQuestion from dictionary."""
        return cls(
            id=data["id"],
            question=data["question"],
            category=data["category"],
            expected_result=data["expected_result"],
            constraints=Constraints.from_dict(data.get("constraints", {})),
            notes=data.get("notes", ""),
            evaluation_mode=data.get("evaluation_mode", "auto"),
        )

    @property
    def is_manual_evaluation(self) -> bool:
        """Check if this question requires manual evaluation."""
        return self.evaluation_mode == "manual"


@dataclass
class PropertyCheck:
    """Constraint check results for a single property."""
    property_id: str
    property_name: str
    property_type_result: ConstraintResult = ConstraintResult.NA
    listing_type_result: ConstraintResult = ConstraintResult.NA
    location_result: ConstraintResult = ConstraintResult.NA
    price_result: ConstraintResult = ConstraintResult.NA
    bedrooms_result: ConstraintResult = ConstraintResult.NA
    floors_result: ConstraintResult = ConstraintResult.NA

    # Additional info for debugging
    location_keyword_match: Optional[str] = None
    location_distance_km: Optional[float] = None
    location_failure_reason: Optional[str] = None  # Explains why location check failed
    actual_price: Optional[int] = None
    actual_bedrooms: Optional[int] = None
    actual_floors: Optional[int] = None
    actual_property_type: Optional[str] = None
    actual_listing_type: Optional[str] = None

    # Manual evaluation fields
    is_manual_evaluation: bool = False
    manual_result: Optional[str] = None  # "pass", "fail", or None (pending)
    manual_comment: str = ""

    @property
    def all_results(self) -> list[ConstraintResult]:
        """Get all constraint results."""
        return [
            self.property_type_result,
            self.listing_type_result,
            self.location_result,
            self.price_result,
            self.bedrooms_result,
            self.floors_result,
        ]

    @property
    def applicable_results(self) -> list[ConstraintResult]:
        """Get only applicable (non-NA) constraint results."""
        return [r for r in self.all_results if r != ConstraintResult.NA]

    @property
    def strict_pass(self) -> bool:
        """Check if all applicable constraints pass."""
        # For manual evaluation, check manual_result
        if self.is_manual_evaluation:
            return self.manual_result == "pass"
        applicable = self.applicable_results
        if not applicable:
            return True  # No constraints = pass
        return all(r == ConstraintResult.PASS for r in applicable)

    @property
    def cpr(self) -> float:
        """Calculate Constraint Pass Ratio for this property."""
        # For manual evaluation, return 1.0 if pass, 0.0 if fail, 0.0 if pending
        if self.is_manual_evaluation:
            if self.manual_result == "pass":
                return 1.0
            elif self.manual_result == "fail":
                return 0.0
            else:
                return 0.0  # Pending - treated as fail until evaluated

        applicable = self.applicable_results
        if not applicable:
            return 1.0
        passed = sum(1 for r in applicable if r == ConstraintResult.PASS)
        return passed / len(applicable)

    @property
    def is_pending_manual(self) -> bool:
        """Check if this is a pending manual evaluation."""
        return self.is_manual_evaluation and self.manual_result is None


@dataclass
class QueryEvaluation:
    """Evaluation results for a single query."""
    query_id: int
    question: str
    category: str
    expected_result: str
    has_results: bool
    property_checks: list[PropertyCheck] = field(default_factory=list)

    # Override fields (for manual review)
    override_success: Optional[bool] = None
    override_notes: str = ""

    # Manual evaluation mode
    is_manual_evaluation: bool = False

    @property
    def num_properties(self) -> int:
        """Number of properties returned."""
        return len(self.property_checks)

    @property
    def mean_cpr(self) -> float:
        """Mean CPR across all properties."""
        if not self.property_checks:
            return 0.0
        return sum(p.cpr for p in self.property_checks) / len(self.property_checks)

    @property
    def strict_success_count(self) -> int:
        """Count of properties that pass all constraints."""
        return sum(1 for p in self.property_checks if p.strict_pass)

    @property
    def strict_success_ratio(self) -> float:
        """Ratio of properties that pass all constraints."""
        if not self.property_checks:
            return 0.0
        return self.strict_success_count / len(self.property_checks)

    @property
    def has_pending_manual(self) -> bool:
        """Check if this query has any pending manual evaluations."""
        return any(p.is_pending_manual for p in self.property_checks)

    def is_success(self, threshold: float = 0.6) -> bool:
        """
        Determine if query is successful based on threshold.

        For 'has_data' queries: Success if has results AND mean_cpr >= threshold
        For 'no_data' queries: Success if no results
        For manual evaluation with pending: Returns False until evaluated
        """
        if self.override_success is not None:
            return self.override_success

        # For manual evaluation, if any property is pending, return False
        if self.is_manual_evaluation and self.has_pending_manual:
            return False

        if self.expected_result == "no_data":
            return not self.has_results

        # expected_result == "has_data"
        return self.has_results and self.mean_cpr >= threshold

    def get_confusion_category(self, threshold: float = 0.6) -> str:
        """
        Determine confusion matrix category.

        Returns: 'TP', 'FP', 'TN', 'FN'
        """
        gt_positive = self.expected_result == "has_data"
        pred_positive = self.has_results and (
            not self.property_checks or self.mean_cpr >= threshold
        )

        if gt_positive and pred_positive:
            return "TP"
        elif not gt_positive and pred_positive:
            return "FP"
        elif not gt_positive and not pred_positive:
            return "TN"
        else:  # gt_positive and not pred_positive
            return "FN"


@dataclass
class ConfusionMatrix:
    """Confusion matrix for query-level evaluation."""
    tp: int = 0
    fp: int = 0
    tn: int = 0
    fn: int = 0

    @property
    def total(self) -> int:
        return self.tp + self.fp + self.tn + self.fn

    @property
    def precision(self) -> float:
        """Precision = TP / (TP + FP)"""
        if self.tp + self.fp == 0:
            return 0.0
        return self.tp / (self.tp + self.fp)

    @property
    def recall(self) -> float:
        """Recall = TP / (TP + FN)"""
        if self.tp + self.fn == 0:
            return 0.0
        return self.tp / (self.tp + self.fn)

    @property
    def f1_score(self) -> float:
        """F1 = 2 * P * R / (P + R)"""
        p, r = self.precision, self.recall
        if p + r == 0:
            return 0.0
        return 2 * p * r / (p + r)

    @property
    def accuracy(self) -> float:
        """Accuracy = (TP + TN) / Total"""
        if self.total == 0:
            return 0.0
        return (self.tp + self.tn) / self.total

    def to_dict(self) -> dict:
        return {
            "tp": self.tp,
            "fp": self.fp,
            "tn": self.tn,
            "fn": self.fn,
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1_score": round(self.f1_score, 4),
            "accuracy": round(self.accuracy, 4),
        }


@dataclass
class PerConstraintAccuracy:
    """Per-Constraint Accuracy (PCA) metrics."""
    property_type: Optional[float] = None
    listing_type: Optional[float] = None
    location: Optional[float] = None
    price: Optional[float] = None
    bedrooms: Optional[float] = None
    floors: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "property_type": self.property_type,
            "listing_type": self.listing_type,
            "location": self.location,
            "price": self.price,
            "bedrooms": self.bedrooms,
            "floors": self.floors,
        }


@dataclass
class EvaluationMetrics:
    """Aggregated evaluation metrics."""
    total_queries: int
    total_properties: int
    threshold_t: float

    # Per-Constraint Accuracy
    pca: PerConstraintAccuracy

    # Aggregated metrics
    mean_cpr: float
    strict_success_ratio: float

    # Query-level success
    query_success_rate: float

    # Confusion matrix
    confusion_matrix: ConfusionMatrix

    # Category breakdown
    category_metrics: dict[str, dict] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "total_queries": self.total_queries,
            "total_properties": self.total_properties,
            "threshold_t": self.threshold_t,
            "pca": self.pca.to_dict(),
            "mean_cpr": round(self.mean_cpr, 4),
            "strict_success_ratio": round(self.strict_success_ratio, 4),
            "query_success_rate": round(self.query_success_rate, 4),
            "confusion_matrix": self.confusion_matrix.to_dict(),
            "category_metrics": self.category_metrics,
        }
