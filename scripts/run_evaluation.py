"""
Run Evaluation Tests
Evaluates the agent against predefined test cases

Run: python scripts/run_evaluation.py
"""
import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from src.agents.orchestrator import OrchestratorAgent
from src.agents.property_agent import PropertyAgent
from src.agents.coach_agent import CoachAgent
from src.adapters.metaproperty import MetaPropertyAPIAdapter
from tests.evaluation import EvaluationFramework


async def main():
    print("=" * 60)
    print("🧪 RAG Property Agent - Evaluation Tests")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not set in .env")
        return
    
    print("\n📋 Initializing components...")
    
    # Initialize data adapter
    api_url = os.getenv("METAPROPERTY_API_URL", "http://localhost:8000")
    api_token = os.getenv("METAPROPERTY_API_TOKEN", "")
    
    data_adapter = MetaPropertyAPIAdapter(
        api_url=api_url,
        api_token=api_token,
    )
    
    # Initialize agents
    property_agent = PropertyAgent(data_adapter=data_adapter)
    coach_agent = CoachAgent()
    
    print("  - Indexing knowledge base...")
    await coach_agent.initialize()
    
    orchestrator = OrchestratorAgent(
        property_agent=property_agent,
        coach_agent=coach_agent,
    )
    
    print("  ✅ Agents ready")
    
    # Initialize evaluation framework
    print("\n📊 Loading test cases...")
    evaluator = EvaluationFramework()
    
    try:
        test_cases = evaluator.load_test_cases()
        print(f"  ✅ Loaded {len(test_cases)} test cases")
    except FileNotFoundError:
        print("  ❌ Test cases file not found at data/test_cases/test_cases.json")
        return
    except Exception as e:
        print(f"  ❌ Error loading test cases: {e}")
        return
    
    # Show test case summary
    print("\n📋 Test Case Categories:")
    categories = {}
    for tc in test_cases:
        categories[tc.category] = categories.get(tc.category, 0) + 1
    for cat, count in categories.items():
        print(f"  - {cat}: {count} tests")
    
    # Run evaluation
    print("\n🚀 Running evaluation...")
    print("-" * 60)
    
    report = await evaluator.run_all_tests(orchestrator)
    
    # Display results
    print("\n" + "=" * 60)
    print("📊 EVALUATION RESULTS")
    print("=" * 60)
    
    print(f"\n✅ Passed: {report.passed_tests}/{report.total_tests}")
    print(f"❌ Failed: {report.failed_tests}/{report.total_tests}")
    print(f"🎯 Intent Accuracy: {report.intent_accuracy:.1%}")
    print(f"📈 Overall Accuracy: {report.overall_accuracy:.1%}")
    
    print("\n📂 Category Breakdown:")
    for cat, results in report.category_results.items():
        status = "✅" if results["passed"] == results["total"] else "⚠️"
        print(f"  {status} {cat}: {results['passed']}/{results['total']} ({results['intent_accuracy']:.1%} intent)")
    
    print("\n⏱️ Performance:")
    print(f"  Avg Latency: {report.avg_latency_ms:.0f}ms")
    print(f"  P95 Latency: {report.p95_latency_ms:.0f}ms")
    print(f"  P99 Latency: {report.p99_latency_ms:.0f}ms")
    
    print(f"\n💰 Cost (estimated):")
    print(f"  Total: ${report.total_cost_usd:.4f}")
    print(f"  Avg/Query: ${report.avg_cost_per_query:.6f}")
    
    # Show failed tests
    failed_tests = [r for r in evaluator.results if not r.passed]
    if failed_tests:
        print("\n❌ Failed Tests Details:")
        print("-" * 60)
        for result in failed_tests[:10]:  # Show first 10
            tc = next((t for t in test_cases if t.id == result.test_case_id), None)
            print(f"\n  ID: {result.test_case_id}")
            if tc:
                print(f"  Input: {tc.input[:60]}...")
            print(f"  Expected: {result.actual_intent}")
            print(f"  Got: {result.predicted_intent} (intent_correct: {result.intent_correct})")
            print(f"  Relevance: {result.relevance_score:.1f}/5")
            if result.key_points_missing:
                print(f"  Missing: {result.key_points_missing[:3]}")
            if result.error:
                print(f"  Error: {result.error}")
    
    # Save report
    output_path = "data/evaluation_report.json"
    evaluator.save_report(report, output_path)
    print(f"\n💾 Report saved to: {output_path}")
    
    print("\n" + "=" * 60)
    print("✨ Evaluation Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
