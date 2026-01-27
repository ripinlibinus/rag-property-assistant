"""
Evaluation Framework for Thesis Analysis
Automated testing and metrics collection
"""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.memory.models import AgentMetrics


@dataclass
class TestCase:
    """Represents a single test case"""
    id: str
    category: str
    subcategory: str
    input: str
    expected_intent: str
    expected_response_type: str
    expected_key_points: list[str]
    expected_property_filters: Optional[dict] = None
    expected_action: Optional[dict] = None
    expected_accuracy: Optional[str] = None
    expected_behavior: Optional[str] = None
    context_required: bool = False
    conversation: Optional[list[dict]] = None


@dataclass
class TestResult:
    """Result of running a single test case"""
    test_case_id: str
    passed: bool
    
    # Intent Classification
    predicted_intent: str
    actual_intent: str
    intent_correct: bool
    
    # Response Quality
    response: str
    relevance_score: float  # 0-5
    key_points_covered: list[str]
    key_points_missing: list[str]
    
    # Performance
    latency_ms: int
    tokens_used: int
    estimated_cost_usd: float
    
    # Error info
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "test_case_id": self.test_case_id,
            "passed": self.passed,
            "intent_correct": self.intent_correct,
            "predicted_intent": self.predicted_intent,
            "actual_intent": self.actual_intent,
            "relevance_score": self.relevance_score,
            "latency_ms": self.latency_ms,
            "tokens_used": self.tokens_used,
            "estimated_cost_usd": self.estimated_cost_usd,
            "error": self.error,
        }


@dataclass
class EvaluationReport:
    """Aggregated evaluation results"""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    
    # Accuracy Metrics
    intent_accuracy: float = 0.0
    overall_accuracy: float = 0.0
    
    # Per-category metrics
    category_results: dict = field(default_factory=dict)
    
    # Performance Metrics
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    
    # Cost Metrics
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    avg_cost_per_query: float = 0.0
    
    # Detailed results
    test_results: list[dict] = field(default_factory=list)


class EvaluationFramework:
    """
    Framework for running automated evaluations
    """
    
    def __init__(self, test_cases_path: str = "data/test_cases/test_cases.json"):
        self.test_cases_path = Path(test_cases_path)
        self.test_cases: list[TestCase] = []
        self.results: list[TestResult] = []
        
    def load_test_cases(self) -> list[TestCase]:
        """Load test cases from JSON file"""
        with open(self.test_cases_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.test_cases = []
        for item in data:
            # Handle multi-turn conversations separately
            if item.get("conversation"):
                test_case = TestCase(
                    id=item["id"],
                    category=item["category"],
                    subcategory=item["subcategory"],
                    input=item["conversation"][-1]["content"],
                    expected_intent=item["expected_intent"],
                    expected_response_type=item["expected_response_type"],
                    expected_key_points=item.get("expected_key_points", []),
                    expected_behavior=item.get("expected_behavior"),
                    conversation=item["conversation"],
                )
            else:
                test_case = TestCase(
                    id=item["id"],
                    category=item["category"],
                    subcategory=item["subcategory"],
                    input=item["input"],
                    expected_intent=item["expected_intent"],
                    expected_response_type=item["expected_response_type"],
                    expected_key_points=item.get("expected_key_points", []),
                    expected_property_filters=item.get("expected_property_filters"),
                    expected_action=item.get("expected_action"),
                    expected_accuracy=item.get("expected_accuracy"),
                    expected_behavior=item.get("expected_behavior"),
                    context_required=item.get("context_required", False),
                )
            self.test_cases.append(test_case)
        
        return self.test_cases
    
    async def run_test(self, test_case: TestCase, agent) -> TestResult:
        """Run a single test case against the agent"""
        start_time = time.time()
        
        try:
            # Call agent
            result = await agent.process(
                message=test_case.input,
                session_id=f"test_{test_case.id}",
                client_phone="test_phone"
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Check intent classification
            predicted_intent = result.get("intent", "unknown")
            intent_correct = predicted_intent == test_case.expected_intent
            
            # Score response (basic implementation - can use LLM for better scoring)
            relevance_score = self._score_relevance(
                result.get("response", ""),
                test_case.expected_key_points
            )
            
            key_points_covered, key_points_missing = self._check_key_points(
                result.get("response", ""),
                test_case.expected_key_points
            )
            
            # Determine if test passed (intent correct + relevance >= 3)
            passed = intent_correct and relevance_score >= 3.0
            
            return TestResult(
                test_case_id=test_case.id,
                passed=passed,
                predicted_intent=predicted_intent,
                actual_intent=test_case.expected_intent,
                intent_correct=intent_correct,
                response=result.get("response", ""),
                relevance_score=relevance_score,
                key_points_covered=key_points_covered,
                key_points_missing=key_points_missing,
                latency_ms=latency_ms,
                tokens_used=result.get("metrics", {}).get("total_tokens", 0),
                estimated_cost_usd=self._estimate_cost(result.get("metrics", {})),
            )
            
        except Exception as e:
            return TestResult(
                test_case_id=test_case.id,
                passed=False,
                predicted_intent="error",
                actual_intent=test_case.expected_intent,
                intent_correct=False,
                response="",
                relevance_score=0.0,
                key_points_covered=[],
                key_points_missing=test_case.expected_key_points,
                latency_ms=int((time.time() - start_time) * 1000),
                tokens_used=0,
                estimated_cost_usd=0.0,
                error=str(e),
            )
    
    async def run_all_tests(self, agent) -> EvaluationReport:
        """Run all test cases and generate report"""
        if not self.test_cases:
            self.load_test_cases()
        
        self.results = []
        for test_case in self.test_cases:
            result = await self.run_test(test_case, agent)
            self.results.append(result)
        
        return self._generate_report()
    
    def _score_relevance(self, response: str, expected_key_points: list[str]) -> float:
        """Score response relevance (0-5)"""
        if not response:
            return 0.0
        
        if not expected_key_points:
            return 3.0  # Default middle score if no key points
        
        # Flexible keyword matching with synonyms
        response_lower = response.lower()
        matches = 0
        
        # Synonym mappings for common terms
        synonyms = {
            "hasil pencarian": ["ditemukan", "found", "properti", "properties", "hasil", "🏠"],
            "lokasi": ["di", "at", "location", "📍"],
            "daftar properti": ["properti", "listing", "pilihan", "options"],
            "range harga": ["harga", "price", "rp", "budget", "💰"],
            "luas tanah": ["lt:", "tanah", "land", "m²", "sqm"],
            "tipe": ["rumah", "ruko", "tanah", "apartment", "house", "land"],
            "3 kt": ["3kt", "3 kamar", "3 bedroom", "bedrooms"],
            "budget 1m": ["1m", "1 milyar", "miliar", "1,000,000,000"],
            "minta klarifikasi": ["apa", "what", "?", "kriteria", "butuh"],
            "alternatif": ["lain", "other", "pilihan", "options"],
            # Greeting synonyms
            "sapaan": ["halo", "hai", "hello", "hi", "selamat", "👋"],
            "sapaan pagi": ["pagi", "morning", "☀️"],
            "tawarkan bantuan": ["bantu", "help", "bisa", "butuh", "?"],
            "sama-sama": ["sama-sama", "welcome", "senang", "😊"],
            # Out of scope synonyms
            "tidak bisa jawab": ["maaf", "sorry", "tidak", "bukan", "🤔"],
            "redirect ke topik properti": ["properti", "real estate", "rumah", "🏠"],
            # Coaching synonyms
            "definisi": ["adalah", "merupakan", "pengertian", "artinya"],
            "pentingnya": ["penting", "fungsi", "gunanya", "untuk"],
            "handling objections": ["objection", "keberatan", "menangani", "handle"],
            "praktis": ["tips", "cara", "langkah", "strategi"],
            "value justification": ["value", "nilai", "worth", "keuntungan"],
            "highlight fitur": ["fitur", "feature", "keunggulan", "kelebihan"],
            "call to action": ["hubungi", "contact", "segera", "tunggu"],
        }
        
        for kp in expected_key_points:
            kp_lower = kp.lower()
            # Direct match
            if kp_lower in response_lower:
                matches += 1
                continue
            
            # Check synonyms
            for key, syns in synonyms.items():
                if key in kp_lower:
                    if any(syn in response_lower for syn in syns):
                        matches += 1
                        break
            else:
                # Check partial word match
                words = kp_lower.split()
                if any(word in response_lower for word in words if len(word) > 3):
                    matches += 0.5
        
        score = (matches / len(expected_key_points)) * 5
        return min(5.0, score)
    
    def _check_key_points(
        self, response: str, expected_key_points: list[str]
    ) -> tuple[list[str], list[str]]:
        """Check which key points are covered in response"""
        response_lower = response.lower()
        covered = []
        missing = []
        
        # Synonym mappings
        synonyms = {
            "hasil pencarian": ["ditemukan", "found", "properti"],
            "lokasi": ["di", "📍", "location"],
            "daftar properti": ["properti", "listing"],
            "sapaan": ["halo", "hai", "hello", "hi", "selamat", "👋"],
            "tawarkan bantuan": ["bantu", "help", "bisa", "butuh"],
            "sama-sama": ["sama-sama", "welcome", "senang"],
            "tidak bisa jawab": ["maaf", "sorry", "tidak", "bukan"],
            "redirect ke topik properti": ["properti", "real estate", "rumah"],
        }
        
        for kp in expected_key_points:
            kp_lower = kp.lower()
            
            # Direct match
            if kp_lower in response_lower:
                covered.append(kp)
                continue
            
            # Check synonyms
            matched = False
            for key, syns in synonyms.items():
                if key in kp_lower:
                    if any(syn in response_lower for syn in syns):
                        covered.append(kp)
                        matched = True
                        break
            
            # Partial word match
            if not matched:
                words = kp_lower.split()
                if any(word in response_lower for word in words if len(word) > 3):
                    covered.append(kp)
                else:
                    missing.append(kp)
        
        return covered, missing
    
    def _estimate_cost(self, metrics: dict) -> float:
        """Estimate cost in USD based on token usage"""
        # GPT-4o-mini pricing (as of 2024)
        INPUT_COST_PER_1K = 0.00015
        OUTPUT_COST_PER_1K = 0.0006
        
        input_tokens = metrics.get("input_tokens", 0)
        output_tokens = metrics.get("output_tokens", 0)
        
        cost = (input_tokens / 1000 * INPUT_COST_PER_1K) + (output_tokens / 1000 * OUTPUT_COST_PER_1K)
        return round(cost, 6)
    
    def _generate_report(self) -> EvaluationReport:
        """Generate aggregated evaluation report"""
        report = EvaluationReport()
        report.total_tests = len(self.results)
        report.passed_tests = sum(1 for r in self.results if r.passed)
        report.failed_tests = report.total_tests - report.passed_tests
        
        # Intent accuracy
        intent_correct = sum(1 for r in self.results if r.intent_correct)
        report.intent_accuracy = intent_correct / report.total_tests if report.total_tests > 0 else 0.0
        
        # Overall accuracy
        report.overall_accuracy = report.passed_tests / report.total_tests if report.total_tests > 0 else 0.0
        
        # Per-category results
        categories = set(tc.category for tc in self.test_cases)
        for category in categories:
            cat_results = [r for r, tc in zip(self.results, self.test_cases) if tc.category == category]
            report.category_results[category] = {
                "total": len(cat_results),
                "passed": sum(1 for r in cat_results if r.passed),
                "intent_accuracy": sum(1 for r in cat_results if r.intent_correct) / len(cat_results) if cat_results else 0,
            }
        
        # Latency metrics
        latencies = [r.latency_ms for r in self.results]
        if latencies:
            latencies_sorted = sorted(latencies)
            report.avg_latency_ms = sum(latencies) / len(latencies)
            report.p95_latency_ms = latencies_sorted[int(len(latencies) * 0.95)]
            report.p99_latency_ms = latencies_sorted[int(len(latencies) * 0.99)]
        
        # Cost metrics
        report.total_tokens = sum(r.tokens_used for r in self.results)
        report.total_cost_usd = sum(r.estimated_cost_usd for r in self.results)
        report.avg_cost_per_query = report.total_cost_usd / report.total_tests if report.total_tests > 0 else 0.0
        
        # Add detailed results
        report.test_results = [r.to_dict() for r in self.results]
        
        return report
    
    def save_report(self, report: EvaluationReport, output_path: str = "data/evaluation_report.json"):
        """Save evaluation report to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": report.timestamp,
                "summary": {
                    "total_tests": report.total_tests,
                    "passed_tests": report.passed_tests,
                    "failed_tests": report.failed_tests,
                    "intent_accuracy": report.intent_accuracy,
                    "overall_accuracy": report.overall_accuracy,
                },
                "performance": {
                    "avg_latency_ms": report.avg_latency_ms,
                    "p95_latency_ms": report.p95_latency_ms,
                    "p99_latency_ms": report.p99_latency_ms,
                },
                "cost": {
                    "total_tokens": report.total_tokens,
                    "total_cost_usd": report.total_cost_usd,
                    "avg_cost_per_query": report.avg_cost_per_query,
                },
                "category_results": report.category_results,
                "test_results": report.test_results,
            }, f, indent=2, ensure_ascii=False)
