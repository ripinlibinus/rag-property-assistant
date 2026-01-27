"""
Main evaluation engine for constraint-based evaluation.
"""

import json
from collections import defaultdict
from pathlib import Path
from typing import Optional

from .models import (
    ConstraintResult,
    GoldQuestion,
    PropertyCheck,
    QueryEvaluation,
    EvaluationMetrics,
    ConfusionMatrix,
    PerConstraintAccuracy,
)
from .constraint_checker import ConstraintChecker


class Evaluator:
    """
    Main evaluation engine that orchestrates constraint checking
    and metrics calculation.
    """

    def __init__(
        self,
        threshold_t: float = 0.6,
        price_tolerance: float = 0.0,
    ):
        """
        Initialize evaluator.

        Args:
            threshold_t: CPR threshold for query success (default 0.6)
            price_tolerance: Default price tolerance (default 0.0 = strict)
        """
        self.threshold_t = threshold_t
        self.price_tolerance = price_tolerance
        self.checker = ConstraintChecker(default_price_tolerance=price_tolerance)

    def load_gold_standard(self, path: str | Path) -> list[GoldQuestion]:
        """
        Load gold standard questions from JSON file.

        Args:
            path: Path to gold standard JSON file

        Returns:
            List of GoldQuestion objects
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Update threshold from gold file if specified
        if "threshold_t" in data:
            self.threshold_t = data["threshold_t"]
        if "price_tolerance" in data:
            self.price_tolerance = data["price_tolerance"]
            self.checker = ConstraintChecker(default_price_tolerance=self.price_tolerance)

        questions = []
        for q_data in data.get("questions", []):
            questions.append(GoldQuestion.from_dict(q_data))

        return questions

    def load_test_results(self, path: str | Path) -> dict:
        """
        Load test results from JSON file.

        Args:
            path: Path to test results JSON file

        Returns:
            Test results dictionary
        """
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def extract_properties_from_response(self, response: str) -> list[dict]:
        """
        Extract property data from agent response.

        This is a best-effort extraction. The response format may vary.

        Args:
            response: Agent response text

        Returns:
            List of property dictionaries (may be empty)
        """
        # For now, return empty - this should be implemented based on
        # the actual response format or by using structured output
        # from the test runner
        return []

    def evaluate_query(
        self,
        gold_question: GoldQuestion,
        response: str,
        properties: Optional[list[dict]] = None,
    ) -> QueryEvaluation:
        """
        Evaluate a single query against gold standard.

        Args:
            gold_question: Gold standard question
            response: Agent response text
            properties: Pre-extracted property data (optional)

        Returns:
            QueryEvaluation with constraint results
        """
        # If properties not provided, try to extract from response
        if properties is None:
            properties = self.extract_properties_from_response(response)

        has_results = len(properties) > 0

        # Check constraints for each property
        property_checks = self.checker.check_all_properties(properties, gold_question)

        return QueryEvaluation(
            query_id=gold_question.id,
            question=gold_question.question,
            category=gold_question.category,
            expected_result=gold_question.expected_result,
            has_results=has_results,
            property_checks=property_checks,
            is_manual_evaluation=gold_question.is_manual_evaluation,
        )

    def calculate_pca(
        self,
        evaluations: list[QueryEvaluation],
    ) -> PerConstraintAccuracy:
        """
        Calculate Per-Constraint Accuracy (PCA).

        PCA[constraint] = passed[constraint] / total[constraint]

        Args:
            evaluations: List of query evaluations

        Returns:
            PerConstraintAccuracy with metrics for each constraint
        """
        # Count pass/total for each constraint
        counts = {
            "property_type": {"pass": 0, "total": 0},
            "listing_type": {"pass": 0, "total": 0},
            "location": {"pass": 0, "total": 0},
            "price": {"pass": 0, "total": 0},
            "bedrooms": {"pass": 0, "total": 0},
            "floors": {"pass": 0, "total": 0},
        }

        for eval_result in evaluations:
            for prop_check in eval_result.property_checks:
                # Property type
                if prop_check.property_type_result != ConstraintResult.NA:
                    counts["property_type"]["total"] += 1
                    if prop_check.property_type_result == ConstraintResult.PASS:
                        counts["property_type"]["pass"] += 1

                # Listing type
                if prop_check.listing_type_result != ConstraintResult.NA:
                    counts["listing_type"]["total"] += 1
                    if prop_check.listing_type_result == ConstraintResult.PASS:
                        counts["listing_type"]["pass"] += 1

                # Location
                if prop_check.location_result != ConstraintResult.NA:
                    counts["location"]["total"] += 1
                    if prop_check.location_result == ConstraintResult.PASS:
                        counts["location"]["pass"] += 1

                # Price
                if prop_check.price_result != ConstraintResult.NA:
                    counts["price"]["total"] += 1
                    if prop_check.price_result == ConstraintResult.PASS:
                        counts["price"]["pass"] += 1

                # Bedrooms
                if prop_check.bedrooms_result != ConstraintResult.NA:
                    counts["bedrooms"]["total"] += 1
                    if prop_check.bedrooms_result == ConstraintResult.PASS:
                        counts["bedrooms"]["pass"] += 1

                # Floors
                if prop_check.floors_result != ConstraintResult.NA:
                    counts["floors"]["total"] += 1
                    if prop_check.floors_result == ConstraintResult.PASS:
                        counts["floors"]["pass"] += 1

        # Calculate accuracy
        def safe_accuracy(c: dict) -> Optional[float]:
            if c["total"] == 0:
                return None
            return round(c["pass"] / c["total"], 4)

        return PerConstraintAccuracy(
            property_type=safe_accuracy(counts["property_type"]),
            listing_type=safe_accuracy(counts["listing_type"]),
            location=safe_accuracy(counts["location"]),
            price=safe_accuracy(counts["price"]),
            bedrooms=safe_accuracy(counts["bedrooms"]),
            floors=safe_accuracy(counts["floors"]),
        )

    def calculate_confusion_matrix(
        self,
        evaluations: list[QueryEvaluation],
    ) -> ConfusionMatrix:
        """
        Calculate confusion matrix from query evaluations.

        Args:
            evaluations: List of query evaluations

        Returns:
            ConfusionMatrix
        """
        cm = ConfusionMatrix()

        for eval_result in evaluations:
            category = eval_result.get_confusion_category(self.threshold_t)
            if category == "TP":
                cm.tp += 1
            elif category == "FP":
                cm.fp += 1
            elif category == "TN":
                cm.tn += 1
            elif category == "FN":
                cm.fn += 1

        return cm

    def calculate_category_metrics(
        self,
        evaluations: list[QueryEvaluation],
    ) -> dict[str, dict]:
        """
        Calculate metrics broken down by category.

        Args:
            evaluations: List of query evaluations

        Returns:
            Dictionary of category -> metrics
        """
        category_evals = defaultdict(list)
        for eval_result in evaluations:
            category_evals[eval_result.category].append(eval_result)

        metrics = {}
        for category, evals in category_evals.items():
            successful = sum(1 for e in evals if e.is_success(self.threshold_t))
            total_props = sum(e.num_properties for e in evals)
            mean_cpr = (
                sum(e.mean_cpr * e.num_properties for e in evals) / total_props
                if total_props > 0
                else 0.0
            )

            metrics[category] = {
                "total_queries": len(evals),
                "successful_queries": successful,
                "success_rate": round(successful / len(evals), 4) if evals else 0.0,
                "total_properties": total_props,
                "mean_cpr": round(mean_cpr, 4),
            }

        return metrics

    def calculate_metrics(
        self,
        evaluations: list[QueryEvaluation],
    ) -> EvaluationMetrics:
        """
        Calculate all evaluation metrics.

        Args:
            evaluations: List of query evaluations

        Returns:
            EvaluationMetrics with all calculated metrics
        """
        total_queries = len(evaluations)
        total_properties = sum(e.num_properties for e in evaluations)

        # PCA
        pca = self.calculate_pca(evaluations)

        # Mean CPR (weighted by number of properties)
        if total_properties > 0:
            mean_cpr = sum(
                e.mean_cpr * e.num_properties for e in evaluations
            ) / total_properties
        else:
            mean_cpr = 0.0

        # Strict success ratio
        total_strict = sum(e.strict_success_count for e in evaluations)
        strict_ratio = total_strict / total_properties if total_properties > 0 else 0.0

        # Query success rate
        successful = sum(1 for e in evaluations if e.is_success(self.threshold_t))
        query_success_rate = successful / total_queries if total_queries > 0 else 0.0

        # Confusion matrix
        cm = self.calculate_confusion_matrix(evaluations)

        # Category metrics
        category_metrics = self.calculate_category_metrics(evaluations)

        return EvaluationMetrics(
            total_queries=total_queries,
            total_properties=total_properties,
            threshold_t=self.threshold_t,
            pca=pca,
            mean_cpr=mean_cpr,
            strict_success_ratio=strict_ratio,
            query_success_rate=query_success_rate,
            confusion_matrix=cm,
            category_metrics=category_metrics,
        )

    def run_evaluation(
        self,
        gold_questions: list[GoldQuestion],
        test_results: list[dict],
    ) -> tuple[list[QueryEvaluation], EvaluationMetrics]:
        """
        Run full evaluation.

        Args:
            gold_questions: List of gold standard questions
            test_results: List of test result dictionaries

        Returns:
            Tuple of (evaluations, metrics)
        """
        # Create mapping of question ID to test result
        result_map = {}
        for result in test_results:
            query_id = result.get("query_id")
            if query_id is not None:
                result_map[query_id] = result

        evaluations = []
        for gold in gold_questions:
            result = result_map.get(gold.id)
            if result is None:
                # No test result for this question - mark as failed
                eval_result = QueryEvaluation(
                    query_id=gold.id,
                    question=gold.question,
                    category=gold.category,
                    expected_result=gold.expected_result,
                    has_results=False,
                    property_checks=[],
                )
            else:
                response = result.get("response", "")
                properties = result.get("properties", [])

                # Use api_data for verified properties (more accurate)
                merged_properties = []
                for prop in properties:
                    if prop.get("verified") and prop.get("api_data"):
                        # Merge api_data into property, api_data takes priority
                        merged = {**prop, **prop["api_data"]}
                        # Ensure lat/lng are available for geo check
                        merged["latitude"] = prop["api_data"].get("latitude")
                        merged["longitude"] = prop["api_data"].get("longitude")
                        merged_properties.append(merged)
                    else:
                        merged_properties.append(prop)

                eval_result = self.evaluate_query(
                    gold_question=gold,
                    response=response,
                    properties=merged_properties,
                )

            evaluations.append(eval_result)

        metrics = self.calculate_metrics(evaluations)
        return evaluations, metrics

    def merge_evaluations(
        self,
        existing: list[QueryEvaluation],
        new: list[QueryEvaluation],
    ) -> list[QueryEvaluation]:
        """
        Merge new evaluations into existing ones (for incremental evaluation).

        Args:
            existing: Existing evaluations
            new: New evaluations to merge

        Returns:
            Merged list with new results replacing existing ones by query_id
        """
        # Create map of existing by query_id
        eval_map = {e.query_id: e for e in existing}

        # Update with new evaluations
        for new_eval in new:
            eval_map[new_eval.query_id] = new_eval

        # Return sorted by query_id
        return sorted(eval_map.values(), key=lambda e: e.query_id)
