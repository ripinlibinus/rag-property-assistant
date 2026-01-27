"""
Auto-Evaluation Script using LLM

Automatically evaluates search results relevance using LLM (GPT-4o-mini or Claude 3.5 Sonnet).
Generates evaluation reports compatible with HTML evaluation interface.

Usage:
    python scripts/auto_evaluate.py --evaluator gpt4o-mini
    python scripts/auto_evaluate.py --evaluator claude-sonnet
    python scripts/auto_evaluate.py --input data/evaluation/hybrid/20260124_140507/test_results_20260124_140507.json
    python scripts/auto_evaluate.py --compare
"""

import json
import re
import sys
import time
import argparse
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
import os
load_dotenv(project_root / '.env')


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class PropertyDetails:
    """Parsed property details from response."""
    num: str
    title: str
    url: Optional[str]
    price: str
    location: str
    specs: List[str]
    prop_type: str
    raw_content: str


@dataclass
class RelevanceJudgment:
    """LLM judgment for a single property."""
    relevant: bool
    confidence: float
    reasoning: str


@dataclass
class QueryEvaluation:
    """Evaluation results for a single query."""
    query_id: int
    question: str
    category: str
    results_count: int
    judgments: Dict[str, RelevanceJudgment]  # prop_num -> judgment
    quality_score: Optional[int] = None
    quality_reasoning: Optional[str] = None


# =============================================================================
# Property Parser (reused from generate_evaluation_html.py)
# =============================================================================

def parse_properties_from_response(response: str) -> List[PropertyDetails]:
    """
    Parse individual property results from agent response.
    Returns list of PropertyDetails.
    """
    properties = []

    # Split by numbered items (1., 2., **1.**, etc.)
    items = re.split(r'\n\s*(?:\*\*)?(\d+)\.(?:\*\*)?\s*', response)

    # First item is intro text, skip it
    for i in range(1, len(items), 2):
        if i + 1 < len(items):
            num = items[i]
            content = items[i + 1].strip()

            if not content:
                continue

            # Extract title (first line, usually in bold **)
            lines = content.split('\n')
            title_match = re.match(r'\*\*(.+?)\*\*', lines[0])
            title = title_match.group(1) if title_match else lines[0][:100]

            # Extract URL
            url_match = re.search(r'\[Lihat Detail\]\((https?://[^\)]+)\)', content)
            if not url_match:
                url_match = re.search(r'(https?://[^\s\)]+)', content)
            url = url_match.group(1) if url_match else None

            # Extract price
            price_match = re.search(r'Rp\s*([\d\.,]+)', content)
            price = f"Rp {price_match.group(1)}" if price_match else ""

            # Extract location
            location = ""
            for line in lines:
                if '📍' in line or 'lokasi' in line.lower():
                    location = re.sub(r'^[📍🏠💰🛏️🚿📐🔗\s]+', '', line).strip()
                    break

            # Extract specs
            specs = []

            bedroom_match = re.search(r'(\d+)\s*[Kk]amar\s*[Tt]idur', content)
            if bedroom_match:
                specs.append(f"{bedroom_match.group(1)} KT")

            bathroom_match = re.search(r'(\d+)\s*[Kk]amar\s*[Mm]andi', content)
            if bathroom_match:
                specs.append(f"{bathroom_match.group(1)} KM")

            lt_match = re.search(r'LT\s*[:\s]*(\d+)\s*m', content, re.IGNORECASE)
            if lt_match:
                specs.append(f"LT {lt_match.group(1)}m2")

            lb_match = re.search(r'LB\s*[:\s]*(\d+)\s*m', content, re.IGNORECASE)
            if lb_match:
                specs.append(f"LB {lb_match.group(1)}m2")

            floor_match = re.search(r'(\d+)\s*[Ll]antai', content)
            if floor_match:
                specs.append(f"{floor_match.group(1)} Lantai")

            # Property type
            if re.search(r'🏗️|Proyek Baru|\bProyek\b|\bproject\b', content, re.IGNORECASE):
                prop_type = 'Primary'
            elif re.search(r'\b(Sewa|Disewa|Disewakan)\b', content, re.IGNORECASE):
                prop_type = 'Rent'
            elif re.search(r'🔄|Resale|\b(Jual|Dijual)\b', content, re.IGNORECASE):
                prop_type = 'Secondary'
            else:
                prop_type = ""

            properties.append(PropertyDetails(
                num=num,
                title=title.strip(),
                url=url,
                price=price,
                location=location,
                specs=specs,
                prop_type=prop_type,
                raw_content=content[:500]
            ))

    return properties


# =============================================================================
# LLM Evaluator Base Class
# =============================================================================

def get_relevance_prompt(query: str, title: str, price: str, location: str,
                         specs: str, property_type: str, listing_type: str) -> str:
    """Generate relevance evaluation prompt."""
    return f"""You are evaluating search results for a real estate chatbot in Indonesia.

USER QUERY: {query}

PROPERTY DETAILS:
- Title: {title}
- Price: {price}
- Location: {location}
- Specs: {specs}
- Property Type: {property_type}
- Listing Type: {listing_type}

TASK: Determine if this property is RELEVANT to the user's query.

RELEVANCE CRITERIA:
1. Location Match: Does the property location match or is near the requested area?
2. Price Match: Is the price within the requested range (if specified)?
3. Property Type Match: Is it the right type (rumah, ruko, tanah, etc.)?
4. Specification Match: Does it meet bedroom/floor/size requirements?
5. Listing Type Match: Is it sale/rent as requested?
6. Feature Match: Does it have requested features/amenities?

IMPORTANT:
- A property is RELEVANT if it reasonably matches the main criteria
- Minor mismatches (e.g., 10% price difference) are acceptable
- If query is vague, be more lenient in judging relevance
- Focus on the MAIN intent of the query

Respond ONLY in valid JSON format. Example:
{{"relevant": true, "confidence": 0.85, "reasoning": "Brief explanation in Indonesian"}}
"""


def get_quality_prompt(query: str, total_count: int, relevant_count: int) -> str:
    """Generate quality evaluation prompt."""
    return f"""Rate the overall quality of this search response.

USER QUERY: {query}
TOTAL RESULTS: {total_count}
RELEVANT COUNT: {relevant_count}

Rate from 0-5:
5 = All results highly relevant (>90%)
4 = Most results relevant (70-90%)
3 = Half relevant (50-70%)
2 = Few relevant (30-50%)
1 = Almost no relevant results (<30%)
0 = No results or error

Respond ONLY in valid JSON format. Example:
{{"quality": 4, "reasoning": "Brief explanation"}}
"""


class LLMEvaluator(ABC):
    """Base class for LLM-based evaluation."""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.total_tokens = 0
        self.total_calls = 0

    @abstractmethod
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM and return response text."""
        pass

    def evaluate_relevance(self, query: str, prop: PropertyDetails) -> RelevanceJudgment:
        """Evaluate if a property is relevant to the query."""
        prompt = get_relevance_prompt(
            query=query,
            title=prop.title,
            price=prop.price,
            location=prop.location,
            specs=", ".join(prop.specs) if prop.specs else "N/A",
            property_type=prop.prop_type or "N/A",
            listing_type=prop.prop_type or "N/A"
        )

        response = self._call_llm_with_retry(prompt)
        return self._parse_relevance_response(response)

    def evaluate_quality(self, query: str, total_count: int, relevant_count: int) -> tuple:
        """Rate overall response quality (0-5)."""
        prompt = get_quality_prompt(
            query=query,
            total_count=total_count,
            relevant_count=relevant_count
        )

        response = self._call_llm_with_retry(prompt)
        return self._parse_quality_response(response)

    def _call_llm_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """Call LLM with exponential backoff retry."""
        delays = [1, 2, 4]
        last_error = None

        for attempt in range(max_retries):
            try:
                return self._call_llm(prompt)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    print(f"  Retry {attempt + 1}/{max_retries} after error: {e}")
                    time.sleep(delays[attempt])

        raise Exception(f"Max retries exceeded: {last_error}")

    def _parse_relevance_response(self, response: str) -> RelevanceJudgment:
        """Parse LLM response for relevance judgment."""
        try:
            data = self._extract_json(response)
            return RelevanceJudgment(
                relevant=bool(data.get('relevant', False)),
                confidence=float(data.get('confidence', 0.5)),
                reasoning=str(data.get('reasoning', 'No reasoning provided'))
            )
        except Exception as e:
            print(f"  Parse error: {e}, response: {response[:200]}")
            return RelevanceJudgment(
                relevant=False,
                confidence=0.0,
                reasoning=f"Parse error: {e}"
            )

    def _parse_quality_response(self, response: str) -> tuple:
        """Parse LLM response for quality rating."""
        try:
            data = self._extract_json(response)
            return (
                int(data.get('quality', 0)),
                str(data.get('reasoning', 'No reasoning provided'))
            )
        except Exception as e:
            return (0, f"Parse error: {e}")

    def _extract_json(self, response: str) -> dict:
        """Extract JSON from response, handling markdown code blocks."""
        # Try direct parse first
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            pass

        # Try to extract from markdown code block
        match = re.search(r'```(?:json)?\s*(.*?)\s*```', response, re.DOTALL)
        if match:
            return json.loads(match.group(1))

        # Try to find JSON object in response
        match = re.search(r'\{[^{}]*\}', response)
        if match:
            return json.loads(match.group(0))

        raise ValueError(f"Could not extract JSON from response")


# =============================================================================
# GPT-4o-mini Evaluator
# =============================================================================

class GPT4oMiniEvaluator(LLMEvaluator):
    """OpenAI GPT-4o-mini evaluator."""

    def __init__(self):
        super().__init__("gpt-4o-mini")
        from openai import OpenAI
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def _call_llm(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a real estate search relevance evaluator. Respond only in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=200
        )
        self.total_calls += 1
        if response.usage:
            self.total_tokens += response.usage.total_tokens
        return response.choices[0].message.content


# =============================================================================
# Claude 3.5 Sonnet Evaluator
# =============================================================================

class ClaudeSonnetEvaluator(LLMEvaluator):
    """Anthropic Claude Sonnet 4 evaluator."""

    def __init__(self):
        super().__init__("claude-sonnet-4-20250514")
        from anthropic import Anthropic
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

    def _call_llm(self, prompt: str) -> str:
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[
                {"role": "user", "content": prompt}
            ],
            system="You are a real estate search relevance evaluator. Respond only in JSON format."
        )
        self.total_calls += 1
        self.total_tokens += response.usage.input_tokens + response.usage.output_tokens
        return response.content[0].text


# =============================================================================
# Main Evaluation Functions
# =============================================================================

def evaluate_test_results(
    input_file: Path,
    evaluator: LLMEvaluator,
    output_dir: Path,
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Evaluate all test results using the specified LLM evaluator.
    Returns metrics dict with Precision@5, MRR, etc.
    """
    print(f"\n[INFO] Loading test results from: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = data.get('results', [])
    if limit:
        results = results[:limit]

    timestamp = data.get('timestamp', datetime.now().strftime('%Y%m%d_%H%M%S'))

    print(f"[INFO] Evaluating {len(results)} queries with {evaluator.model_name}")

    evaluations: List[QueryEvaluation] = []
    all_judgments = []

    for idx, result in enumerate(results):
        query_id = result.get('query_id', idx + 1)
        question = result.get('question', '')
        category = result.get('category', 'unknown')
        response = result.get('response', '')
        results_count = result.get('results_count', 0)

        print(f"\n[{idx + 1}/{len(results)}] Query #{query_id}: {question[:50]}...")

        # Parse properties from response
        properties = parse_properties_from_response(response)
        print(f"  Parsed {len(properties)} properties")

        # Evaluate each property
        judgments: Dict[str, RelevanceJudgment] = {}
        for prop in properties:
            print(f"    Evaluating property #{prop.num}: {prop.title[:40]}...", end=" ")
            judgment = evaluator.evaluate_relevance(question, prop)
            judgments[prop.num] = judgment
            print(f"{'RELEVANT' if judgment.relevant else 'NOT RELEVANT'} ({judgment.confidence:.2f})")

            # Store detailed judgment
            all_judgments.append({
                'query_id': query_id,
                'question': question,
                'property_num': prop.num,
                'property_title': prop.title,
                'property_price': prop.price,
                'property_location': prop.location,
                'relevant': judgment.relevant,
                'confidence': judgment.confidence,
                'reasoning': judgment.reasoning
            })

        # Calculate relevant count
        relevant_count = sum(1 for j in judgments.values() if j.relevant)

        # Evaluate overall quality
        quality_score, quality_reasoning = evaluator.evaluate_quality(
            question, results_count, relevant_count
        )

        evaluation = QueryEvaluation(
            query_id=query_id,
            question=question,
            category=category,
            results_count=results_count,
            judgments=judgments,
            quality_score=quality_score,
            quality_reasoning=quality_reasoning
        )
        evaluations.append(evaluation)

        print(f"  Quality: {quality_score}/5 | Relevant: {relevant_count}/{len(properties)}")

    # Calculate metrics
    metrics = calculate_metrics(evaluations)
    metrics['evaluator'] = evaluator.model_name
    metrics['total_tokens'] = evaluator.total_tokens
    metrics['total_api_calls'] = evaluator.total_calls
    metrics['timestamp'] = timestamp

    # Generate outputs
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save LLM judgments
    judgments_file = output_dir / 'llm_judgments.json'
    with open(judgments_file, 'w', encoding='utf-8') as f:
        json.dump(all_judgments, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] LLM judgments saved: {judgments_file}")

    # Generate rated CSV
    csv_file = output_dir / 'evaluation_rated.csv'
    generate_rated_csv(evaluations, csv_file)
    print(f"[OK] Rated CSV saved: {csv_file}")

    # Generate evaluation report JSON
    report_file = output_dir / 'evaluation_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    print(f"[OK] Evaluation report saved: {report_file}")

    # Generate markdown report
    md_file = output_dir / 'evaluation_report.md'
    generate_markdown_report(metrics, evaluations, md_file)
    print(f"[OK] Markdown report saved: {md_file}")

    return metrics


def calculate_metrics(evaluations: List[QueryEvaluation]) -> Dict[str, Any]:
    """Calculate evaluation metrics: Precision@5, Overall Precision, MRR, Success Rate."""

    total_queries = len(evaluations)
    total_precision_at_5 = 0
    total_overall_precision = 0
    total_mrr = 0
    total_success = 0

    precision_at_5_count = 0
    overall_precision_count = 0
    mrr_count = 0

    category_metrics: Dict[str, Dict] = {}

    for eval in evaluations:
        # Count relevant properties
        total_relevant = sum(1 for j in eval.judgments.values() if j.relevant)

        # Relevant in top 5
        relevant_in_top_5 = 0
        first_relevant_rank = 0

        for i in range(1, 11):
            num = str(i)
            if num in eval.judgments:
                if eval.judgments[num].relevant:
                    if first_relevant_rank == 0:
                        first_relevant_rank = i
                    if i <= 5:
                        relevant_in_top_5 += 1

        # Calculate Precision@5
        denominator = min(eval.results_count, 5)
        if denominator > 0:
            precision_at_5 = relevant_in_top_5 / denominator
            total_precision_at_5 += precision_at_5
            precision_at_5_count += 1
        else:
            precision_at_5 = 0

        # Calculate Overall Precision
        if eval.results_count > 0:
            overall_precision = total_relevant / eval.results_count
            total_overall_precision += overall_precision
            overall_precision_count += 1
        else:
            overall_precision = 0

        # Calculate MRR
        if eval.results_count > 0:
            if first_relevant_rank > 0:
                mrr = 1 / first_relevant_rank
                total_mrr += mrr
            mrr_count += 1
        else:
            mrr = 0

        # Calculate Success
        success = 1 if total_relevant >= 1 else 0
        total_success += success

        # Category breakdown
        cat = eval.category
        if cat not in category_metrics:
            category_metrics[cat] = {
                'count': 0,
                'precision_at_5': [],
                'overall_precision': [],
                'mrr': [],
                'success': []
            }

        category_metrics[cat]['count'] += 1
        if denominator > 0:
            category_metrics[cat]['precision_at_5'].append(precision_at_5)
        if eval.results_count > 0:
            category_metrics[cat]['overall_precision'].append(overall_precision)
            category_metrics[cat]['mrr'].append(mrr if first_relevant_rank > 0 else 0)
        category_metrics[cat]['success'].append(success)

    # Calculate averages
    avg_precision_at_5 = total_precision_at_5 / precision_at_5_count if precision_at_5_count > 0 else 0
    avg_overall_precision = total_overall_precision / overall_precision_count if overall_precision_count > 0 else 0
    avg_mrr = total_mrr / mrr_count if mrr_count > 0 else 0
    success_rate = total_success / total_queries if total_queries > 0 else 0

    # Category averages
    category_summary = {}
    for cat, data in category_metrics.items():
        category_summary[cat] = {
            'count': data['count'],
            'precision_at_5': sum(data['precision_at_5']) / len(data['precision_at_5']) if data['precision_at_5'] else 0,
            'overall_precision': sum(data['overall_precision']) / len(data['overall_precision']) if data['overall_precision'] else 0,
            'mrr': sum(data['mrr']) / len(data['mrr']) if data['mrr'] else 0,
            'success_rate': sum(data['success']) / len(data['success']) if data['success'] else 0
        }

    return {
        'total_queries': total_queries,
        'precision_at_5': round(avg_precision_at_5, 4),
        'overall_precision': round(avg_overall_precision, 4),
        'mrr': round(avg_mrr, 4),
        'success_rate': round(success_rate, 4),
        'category_breakdown': category_summary
    }


def generate_rated_csv(evaluations: List[QueryEvaluation], output_path: Path):
    """Generate CSV in the same format as manual evaluation."""

    headers = [
        'query_id', 'question', 'category', 'results_count',
        'relevant_count', 'relevant_in_top5', 'first_relevant_rank',
        'overall_precision', 'precision_at_5', 'mrr', 'success',
        'response_quality', 'notes'
    ]

    rows = []
    for eval in evaluations:
        # Count relevant
        total_relevant = sum(1 for j in eval.judgments.values() if j.relevant)
        relevant_in_top_5 = 0
        first_relevant_rank = 0

        for i in range(1, 11):
            num = str(i)
            if num in eval.judgments:
                if eval.judgments[num].relevant:
                    if first_relevant_rank == 0:
                        first_relevant_rank = i
                    if i <= 5:
                        relevant_in_top_5 += 1

        # Calculate metrics
        denominator = min(eval.results_count, 5)
        precision_at_5 = relevant_in_top_5 / denominator if denominator > 0 else 0
        overall_precision = total_relevant / eval.results_count if eval.results_count > 0 else 0
        mrr = 1 / first_relevant_rank if first_relevant_rank > 0 else 0
        success = 1 if total_relevant >= 1 else 0

        rows.append({
            'query_id': eval.query_id,
            'question': eval.question,
            'category': eval.category,
            'results_count': eval.results_count,
            'relevant_count': total_relevant,
            'relevant_in_top5': relevant_in_top_5,
            'first_relevant_rank': first_relevant_rank if first_relevant_rank > 0 else '',
            'overall_precision': round(overall_precision, 4),
            'precision_at_5': round(precision_at_5, 4),
            'mrr': round(mrr, 4),
            'success': success,
            'response_quality': eval.quality_score or '',
            'notes': f"Auto-evaluated. {eval.quality_reasoning or ''}"
        })

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def generate_markdown_report(metrics: Dict, evaluations: List[QueryEvaluation], output_path: Path):
    """Generate markdown evaluation report."""

    lines = [
        f"# Auto-Evaluation Report",
        f"",
        f"**Evaluator:** {metrics.get('evaluator', 'Unknown')}",
        f"**Timestamp:** {metrics.get('timestamp', 'N/A')}",
        f"**Total API Calls:** {metrics.get('total_api_calls', 0)}",
        f"**Total Tokens Used:** {metrics.get('total_tokens', 0)}",
        f"",
        f"---",
        f"",
        f"## Summary Metrics",
        f"",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total Queries | {metrics['total_queries']} |",
        f"| Precision@5 | {metrics['precision_at_5'] * 100:.1f}% |",
        f"| Overall Precision | {metrics['overall_precision'] * 100:.1f}% |",
        f"| MRR | {metrics['mrr']:.3f} |",
        f"| Success Rate | {metrics['success_rate'] * 100:.1f}% |",
        f"",
        f"---",
        f"",
        f"## Category Breakdown",
        f"",
        f"| Category | Count | P@5 | Overall P | MRR | Success |",
        f"|----------|-------|-----|-----------|-----|---------|"
    ]

    for cat, data in metrics.get('category_breakdown', {}).items():
        lines.append(
            f"| {cat} | {data['count']} | "
            f"{data['precision_at_5'] * 100:.1f}% | "
            f"{data['overall_precision'] * 100:.1f}% | "
            f"{data['mrr']:.3f} | "
            f"{data['success_rate'] * 100:.1f}% |"
        )

    lines.extend([
        f"",
        f"---",
        f"",
        f"## Detailed Results",
        f""
    ])

    for eval in evaluations:
        total_relevant = sum(1 for j in eval.judgments.values() if j.relevant)
        lines.append(f"### Query #{eval.query_id}")
        lines.append(f"**Question:** {eval.question}")
        lines.append(f"**Category:** {eval.category}")
        lines.append(f"**Relevant:** {total_relevant}/{eval.results_count}")
        lines.append(f"**Quality:** {eval.quality_score}/5")
        lines.append(f"")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def find_latest_test_results(method: str = 'hybrid') -> Optional[Path]:
    """Find the latest test results file for the given method."""

    base_dir = project_root / 'data' / 'evaluation' / method

    if not base_dir.exists():
        return None

    # Look for timestamped folders
    folders = sorted([f for f in base_dir.iterdir() if f.is_dir() and f.name.isdigit()], reverse=True)

    for folder in folders:
        # Look for test_results file
        for pattern in ['test_results*.json', 'test_results.json']:
            files = list(folder.glob(pattern))
            if files:
                return files[0]

    # Fallback: look for test_results_latest.json
    latest_file = base_dir / 'test_results_latest.json'
    if latest_file.exists():
        return latest_file

    return None


# =============================================================================
# Main CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='Auto-evaluate search results using LLM')
    parser.add_argument('--evaluator', type=str, default='gpt4o-mini',
                        choices=['gpt4o-mini', 'claude-sonnet'],
                        help='LLM evaluator to use')
    parser.add_argument('--input', type=str, default=None,
                        help='Input test results JSON file')
    parser.add_argument('--method', type=str, default='hybrid',
                        choices=['hybrid', 'api_only', 'vector_only'],
                        help='Search method (for finding latest results)')
    parser.add_argument('--limit', type=int, default=None,
                        help='Limit number of queries to evaluate (for testing)')
    parser.add_argument('--compare', action='store_true',
                        help='Run both evaluators and compare')

    args = parser.parse_args()

    # Find input file
    if args.input:
        input_file = Path(args.input)
    else:
        input_file = find_latest_test_results(args.method)

    if not input_file or not input_file.exists():
        print(f"[ERR] Input file not found. Run test first:")
        print(f"      python scripts/test_sequential_chat.py --method {args.method}")
        return

    print(f"\n{'='*60}")
    print(f"AUTO-EVALUATION")
    print(f"{'='*60}")
    print(f"Input: {input_file}")

    # Determine output directory
    # Get timestamp from input file's parent folder or filename
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    timestamp = data.get('timestamp', datetime.now().strftime('%Y%m%d_%H%M%S'))
    method = data.get('search_method', args.method)

    base_output_dir = project_root / 'data' / 'evaluation' / method / timestamp

    if args.compare:
        # Run both evaluators
        evaluators = [
            ('gpt4o-mini', GPT4oMiniEvaluator),
            ('claude-sonnet', ClaudeSonnetEvaluator)
        ]

        all_metrics = {}
        for name, EvaluatorClass in evaluators:
            print(f"\n{'='*60}")
            print(f"Running {name} evaluator...")
            print(f"{'='*60}")

            try:
                evaluator = EvaluatorClass()
                output_dir = base_output_dir / f'auto_{name.replace("-", "_")}'
                metrics = evaluate_test_results(input_file, evaluator, output_dir, args.limit)
                all_metrics[name] = metrics
            except Exception as e:
                print(f"[ERR] Failed to run {name}: {e}")

        # Generate comparison report
        if len(all_metrics) > 1:
            print(f"\n{'='*60}")
            print(f"COMPARISON REPORT")
            print(f"{'='*60}")
            print(f"\n{'Metric':<20} | {'GPT-4o-mini':<15} | {'Claude Sonnet':<15}")
            print(f"{'-'*20}-+-{'-'*15}-+-{'-'*15}")

            for metric in ['precision_at_5', 'overall_precision', 'mrr', 'success_rate']:
                gpt_val = all_metrics.get('gpt4o-mini', {}).get(metric, 0)
                claude_val = all_metrics.get('claude-sonnet', {}).get(metric, 0)

                if metric in ['precision_at_5', 'overall_precision', 'success_rate']:
                    print(f"{metric:<20} | {gpt_val*100:>13.1f}% | {claude_val*100:>13.1f}%")
                else:
                    print(f"{metric:<20} | {gpt_val:>14.3f} | {claude_val:>14.3f}")

    else:
        # Run single evaluator
        if args.evaluator == 'gpt4o-mini':
            evaluator = GPT4oMiniEvaluator()
        else:
            evaluator = ClaudeSonnetEvaluator()

        output_dir = base_output_dir / f'auto_{args.evaluator.replace("-", "_")}'
        metrics = evaluate_test_results(input_file, evaluator, output_dir, args.limit)

        print(f"\n{'='*60}")
        print(f"EVALUATION COMPLETE")
        print(f"{'='*60}")
        print(f"Precision@5:       {metrics['precision_at_5']*100:.1f}%")
        print(f"Overall Precision: {metrics['overall_precision']*100:.1f}%")
        print(f"MRR:               {metrics['mrr']:.3f}")
        print(f"Success Rate:      {metrics['success_rate']*100:.1f}%")
        print(f"\nOutput directory: {output_dir}")


if __name__ == '__main__':
    main()
