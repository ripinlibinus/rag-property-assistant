#!/usr/bin/env python
"""
Evaluation V2 - Constraint-Based Evaluation with Confusion Matrix

This script runs constraint-based evaluation for the RAG property search system.
It compares search results against gold standard constraints and calculates
metrics including PCA (Per-Constraint Accuracy), CPR (Constraint Pass Ratio),
and Confusion Matrix (TP, FP, TN, FN, Precision, Recall, F1).

Usage:
    # Run evaluation with 5 questions (first 5)
    python scripts/evaluate_v2.py --gold data/gold/questions_v2.json --limit 5

    # Run full evaluation
    python scripts/evaluate_v2.py --gold data/gold/questions_v2.json

    # With specific search method and LLM
    python scripts/evaluate_v2.py --method hybrid --llm openai

    # Incremental evaluation - run specific question range
    python scripts/evaluate_v2.py --from 4 --to 8

    # Re-run single question
    python scripts/evaluate_v2.py --from 4 --to 4

    # Resume from question 15
    python scripts/evaluate_v2.py --from 15

    # Use existing test results (skip running agent)
    python scripts/evaluate_v2.py --results data/evaluation/v2/hybrid_openai_20260125/results.json
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Fix Windows console encoding for Unicode/emoji support
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from dotenv import load_dotenv
load_dotenv()

from src.evaluation import (
    Evaluator,
    HTMLReportGenerator,
    GoldQuestion,
    QueryEvaluation,
)
from src.evaluation.models import ConstraintResult


def apply_manual_input(
    evaluations: list[QueryEvaluation],
    manual_input_path: str,
    verbose: bool = False,
) -> list[QueryEvaluation]:
    """
    Apply manual input (constraint overrides and manual evaluations) to evaluations.

    Args:
        evaluations: List of QueryEvaluation from automatic evaluation
        manual_input_path: Path to manual_input.json file
        verbose: Print verbose output

    Returns:
        Updated evaluations with manual overrides applied
    """
    with open(manual_input_path, "r", encoding="utf-8") as f:
        manual_data = json.load(f)

    constraint_overrides = manual_data.get("constraint_overrides", {})
    manual_evaluations = manual_data.get("manual_evaluations", {})

    override_count = 0
    manual_count = 0

    # Map result strings to ConstraintResult enum
    result_map = {
        "pass": ConstraintResult.PASS,
        "fail": ConstraintResult.FAIL,
        "na": ConstraintResult.NA,
    }

    for eval_result in evaluations:
        query_id = str(eval_result.query_id)

        # Apply constraint overrides (for Q1-Q21)
        if query_id in constraint_overrides:
            query_overrides = constraint_overrides[query_id]
            for prop_idx_str, prop_overrides in query_overrides.items():
                prop_idx = int(prop_idx_str)
                if prop_idx < len(eval_result.property_checks):
                    prop_check = eval_result.property_checks[prop_idx]

                    for constraint, new_value in prop_overrides.items():
                        if new_value in result_map:
                            new_result = result_map[new_value]
                            attr_name = f"{constraint}_result"
                            if hasattr(prop_check, attr_name):
                                old_value = getattr(prop_check, attr_name)
                                setattr(prop_check, attr_name, new_result)
                                override_count += 1
                                if verbose:
                                    print(f"    Override Q{query_id} P{prop_idx} {constraint}: {old_value.value} -> {new_value}")

        # Apply manual evaluations (for Q22-Q30)
        if query_id in manual_evaluations:
            query_manuals = manual_evaluations[query_id]
            for prop_idx_str, manual_data_item in query_manuals.items():
                prop_idx = int(prop_idx_str)
                if prop_idx < len(eval_result.property_checks):
                    prop_check = eval_result.property_checks[prop_idx]

                    result = manual_data_item.get("result")
                    comment = manual_data_item.get("comment", "")

                    if result:
                        prop_check.manual_result = result
                        prop_check.manual_comment = comment
                        prop_check.is_manual_evaluation = True
                        manual_count += 1
                        if verbose:
                            print(f"    Manual Q{query_id} P{prop_idx}: {result}")

    print(f"[*] Applied manual input: {override_count} constraint overrides, {manual_count} manual evaluations")

    return evaluations


def fetch_property_from_api(
    slug: str,
    api_url: str,
    api_token: str,
    source: str = "listing",
) -> dict | None:
    """
    Fetch property data from API using slug (exact match).

    Args:
        slug: Property slug from URL (unique identifier)
        api_url: API base URL
        api_token: API token
        source: "listing" or "project"

    Returns property dict with actual data from database.
    """
    import requests

    try:
        # Use direct slug endpoint for exact match (no duplicates)
        if source == "listing":
            endpoint = f"{api_url}/api/v1/listings/{slug}"
        else:
            endpoint = f"{api_url}/api/v1/projects/{slug}"

        resp = requests.get(
            endpoint,
            headers={"Authorization": f"Bearer {api_token}"},
            timeout=10,
        )

        if resp.status_code != 200:
            return None

        data = resp.json()
        if not data.get("success") or not data.get("data"):
            return None

        prop = data["data"]

        # Build URL for viewing property
        slug = prop.get("slug", "")
        if source == "listing":
            url_view = f"https://2026-website.metaproperty.co.id/properti/{slug}" if slug else ""
        else:
            url_view = f"https://2026-website.metaproperty.co.id/proyek/{slug}" if slug else ""

        return {
            "api_id": prop.get("id"),
            "uuid": prop.get("uuid"),
            "name": prop.get("title") or prop.get("name"),
            "slug": slug,
            "url_view": url_view,
            "price": prop.get("price"),
            "bedrooms": prop.get("bedrooms"),
            "bathrooms": prop.get("bathrooms"),
            "floors": int(float(prop.get("floors"))) if prop.get("floors") else None,
            "land_size": prop.get("land_area"),  # Renamed for consistency
            "building_size": prop.get("building_area"),  # Renamed for consistency
            "land_area": prop.get("land_area"),  # Keep original name too
            "building_area": prop.get("building_area"),  # Keep original name too
            "property_type": prop.get("property_type"),
            "listing_type": prop.get("listing_type"),
            "location": prop.get("display_address") or prop.get("area_listing"),
            "address": prop.get("address") or prop.get("display_address") or "",
            "description": prop.get("description") or prop.get("additional_info") or "",
            "additional_info": prop.get("additional_info") or "",
            "latitude": float(prop.get("latitude")) if prop.get("latitude") else None,
            "longitude": float(prop.get("longitude")) if prop.get("longitude") else None,
            "district": prop.get("district"),
            "city": prop.get("city"),
            # Additional fields for manual evaluation
            "features": prop.get("features") or [],
            "facilities": prop.get("facilities") or [],
            "images": prop.get("images") or [],
        }
    except Exception as e:
        print(f"    [WARN] API fetch failed for {slug}: {e}")
        return None


def verify_properties_with_api(
    test_results: list[dict],
    api_url: str,
    api_token: str,
    verbose: bool = False,
) -> list[dict]:
    """
    Verify extracted properties against API data.

    Updates properties with actual data from API and adds verification status.
    """
    print("[*] Verifying properties against API...")

    for result in test_results:
        properties = result.get("properties", [])
        verified_count = 0

        for prop in properties:
            slug = prop.get("slug")
            if not slug:
                prop["verified"] = False
                prop["verify_error"] = "no_slug"
                continue

            source = prop.get("source", "listing")
            api_data = fetch_property_from_api(slug, api_url, api_token, source=source)
            if api_data:
                prop["verified"] = True
                prop["api_id"] = api_data.get("api_id")
                prop["api_data"] = api_data

                # Compare extracted vs API data - detect actual mismatches
                mismatches = []
                extracted_price = prop.get("price")
                api_price = api_data.get("price")
                if extracted_price and api_price and int(extracted_price) != int(api_price):
                    mismatches.append(f"price: extracted {int(extracted_price):,} vs api {int(api_price):,}")

                extracted_beds = prop.get("bedrooms")
                api_beds = api_data.get("bedrooms")
                if extracted_beds and api_beds and extracted_beds != api_beds:
                    mismatches.append(f"bedrooms: extracted {extracted_beds} vs api {api_beds}")

                extracted_baths = prop.get("bathrooms")
                api_baths = api_data.get("bathrooms")
                if extracted_baths and api_baths and extracted_baths != api_baths:
                    mismatches.append(f"bathrooms: extracted {extracted_baths} vs api {api_baths}")

                prop["mismatches"] = mismatches
                prop["extraction_accurate"] = len(mismatches) == 0
                verified_count += 1
            else:
                prop["verified"] = False
                prop["verify_error"] = "not_found"

        if verbose:
            print(f"    Q{result.get('query_id')}: {verified_count}/{len(properties)} verified")

    return test_results


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run constraint-based evaluation for RAG property search"
    )
    parser.add_argument(
        "--gold",
        type=str,
        default="data/gold/questions_v2.json",
        help="Path to gold standard JSON file",
    )
    parser.add_argument(
        "--method",
        type=str,
        default="hybrid",
        choices=["hybrid", "api_only", "vector_only"],
        help="Search method to use",
    )
    parser.add_argument(
        "--llm",
        type=str,
        default="openai",
        choices=["openai", "anthropic", "google"],
        help="LLM provider to use",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit to first N questions",
    )
    parser.add_argument(
        "--from",
        dest="from_q",
        type=int,
        default=1,
        help="Start from question N (1-indexed)",
    )
    parser.add_argument(
        "--to",
        dest="to_q",
        type=int,
        default=None,
        help="End at question N (1-indexed)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory (for incremental evaluation)",
    )
    parser.add_argument(
        "--results",
        type=str,
        default=None,
        help="Use existing test results JSON (skip running agent)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="Override CPR threshold (default from gold file)",
    )
    parser.add_argument(
        "--skip-run",
        action="store_true",
        help="Skip running agent, only recalculate from existing results",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--reparse",
        action="store_true",
        help="Re-parse properties from response text (use with --results)",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify extracted properties against API (fetch actual data)",
    )
    parser.add_argument(
        "--manual-input",
        type=str,
        default=None,
        help="Path to manual_input.json with constraint overrides and manual evaluations",
    )
    return parser.parse_args()


def load_gold_questions(gold_path: str) -> tuple[list[GoldQuestion], dict, list[dict]]:
    """Load gold standard questions from JSON file."""
    with open(gold_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    raw_questions = data.get("questions", [])
    questions = [GoldQuestion.from_dict(q) for q in raw_questions]
    config = {
        "threshold_t": data.get("threshold_t", 0.6),
        "price_tolerance": data.get("price_tolerance", 0.10),
    }
    return questions, config, raw_questions


def extract_properties_from_response(response: str) -> list[dict]:
    """
    Extract property data from agent response text.

    Handles the markdown format used by the agent:
    1. **[Property Name](URL)**
       - 🔄 Resale
       - 📍 Address
       - 💰 Rp X
       - 🏠 X KT, X KM, LT Xm², LB Xm²

    Also handles format without links:
    1. **Property Name**
       - ...
    """
    properties = []

    # Try to find JSON blocks in response first
    json_pattern = r'\{[^{}]*"(?:id|property_id)"[^{}]*\}'
    matches = re.findall(json_pattern, response, re.DOTALL)
    for match in matches:
        try:
            prop = json.loads(match)
            properties.append(prop)
        except json.JSONDecodeError:
            pass

    # If no JSON found, parse markdown format
    if not properties:
        # Split by numbered items (1. **[Name]**, 2. **Name**, etc.)
        # Pattern matches lines starting with "N. **" where N is a number
        property_blocks = re.split(r'\n(?=\d+\.\s+\*\*)', response)

        for block in property_blocks:
            if not block.strip():
                continue

            prop = {}
            first_line = block.split('\n')[0]

            # Try to extract name with URL: "1. **[Property Name](URL)**"
            name_url_match = re.match(
                r'^\d+\.\s+\*\*\[(.+?)\]\(([^)]+)\)\*\*',
                first_line
            )
            if name_url_match:
                prop["name"] = name_url_match.group(1).strip()
                url = name_url_match.group(2)
                # Extract slug from URL
                slug_match = re.search(r'properti/([a-z0-9-]+)', url)
                if slug_match:
                    prop["slug"] = slug_match.group(1)
                    prop["source"] = "listing"
                project_match = re.search(r'project/([a-z0-9-]+)', url)
                if project_match:
                    prop["slug"] = project_match.group(1)
                    prop["source"] = "project"
            else:
                # Try format without URL: "1. **Property Name**"
                name_match = re.match(r'^\d+\.\s+\*\*(.+?)\*\*', first_line)
                if name_match:
                    prop["name"] = name_match.group(1).strip()
                else:
                    continue  # Skip if no name found

            # Extract location (📍 or "Lokasi:")
            loc_match = re.search(r'📍\s*(.+?)(?:\n|$)', block)
            if loc_match:
                prop["location"] = loc_match.group(1).strip()
            else:
                loc_match = re.search(r'(?:lokasi|alamat|address)[:\s]*(.+?)(?:\n|$)', block, re.I)
                if loc_match:
                    prop["location"] = loc_match.group(1).strip()

            # Extract price (💰 Rp X or "Harga:")
            price_match = re.search(r'💰\s*Rp\.?\s*([0-9.,]+)', block)
            if not price_match:
                price_match = re.search(r'(?:harga|price)[:\s]*Rp\.?\s*([0-9.,]+)', block, re.I)
            if price_match:
                price_str = price_match.group(1).replace('.', '').replace(',', '')
                try:
                    prop["price"] = int(price_str)
                except ValueError:
                    pass

            # Extract bedrooms (🏠 X Kamar Tidur or "X KT")
            bed_match = re.search(r'(\d+)\s*[Kk]amar\s*[Tt]idur', block)
            if not bed_match:
                bed_match = re.search(r'(\d+)\s*(?:KT|BR|bedroom)', block, re.I)
            if bed_match:
                prop["bedrooms"] = int(bed_match.group(1))

            # Extract bathrooms
            bath_match = re.search(r'(\d+)\s*[Kk]amar\s*[Mm]andi', block)
            if bath_match:
                prop["bathrooms"] = int(bath_match.group(1))

            # Extract land area (LT)
            lt_match = re.search(r'LT\s*(\d+)\s*m', block)
            if lt_match:
                prop["land_area"] = int(lt_match.group(1))

            # Extract building area (LB)
            lb_match = re.search(r'LB\s*(\d+)\s*m', block)
            if lb_match:
                prop["building_area"] = int(lb_match.group(1))

            # Extract slug from URL if not already extracted from name line
            # Format: https://2026-website.metaproperty.co.id/properti/property-name-XXXXXXXX
            if not prop.get("slug"):
                url_match = re.search(r'metaproperty\.co\.id/properti/([a-z0-9-]+)', block)
                if url_match:
                    prop["slug"] = url_match.group(1)
                    prop["source"] = "listing"

                # Check if from project (different URL pattern)
                project_match = re.search(r'metaproperty\.co\.id/project/([a-z0-9-]+)', block)
                if project_match:
                    prop["slug"] = project_match.group(1)
                    prop["source"] = "project"

            # Extract property type from context
            name_lower = prop.get("name", "").lower()
            if "rumah" in name_lower or "house" in name_lower:
                prop["property_type"] = "house"
            elif "ruko" in name_lower or "shophouse" in name_lower:
                prop["property_type"] = "ruko"
            elif "apartemen" in name_lower or "apartment" in name_lower:
                prop["property_type"] = "apartment"
            elif "tanah" in name_lower or "land" in name_lower:
                prop["property_type"] = "land"
            elif "gudang" in name_lower or "warehouse" in name_lower:
                prop["property_type"] = "warehouse"
            elif "villa" in name_lower:
                prop["property_type"] = "house"  # Villa = house
            elif "townhouse" in name_lower:
                prop["property_type"] = "house"  # Townhouse = house

            # Infer listing type from response context
            if "disewa" in response.lower() or "sewa" in response.lower():
                if "dijual" not in block.lower():
                    prop["listing_type"] = "rent"
            if "dijual" in response.lower() or "jual" in response.lower():
                if "disewa" not in block.lower():
                    prop["listing_type"] = "sale"

            # Only add if we have at least name
            if prop.get("name"):
                properties.append(prop)

    return properties


def run_agent_evaluation(
    questions: list[GoldQuestion],
    method: str = "hybrid",
    llm: str = "openai",
    verbose: bool = False,
) -> list[dict]:
    """
    Run agent for each question and collect results.

    Returns list of result dicts with query_id, question, response, properties.
    """
    from src.adapters.metaproperty import MetaPropertyAPIAdapter
    from src.agents.react_agent import create_property_react_agent
    from src.utils.ab_testing import configure_ab_test, get_ab_manager, SearchMethod

    api_url = os.getenv("METAPROPERTY_API_URL", "http://localhost:8000")
    api_token = os.getenv("METAPROPERTY_API_TOKEN", "")

    # Map method string to SearchMethod enum
    method_map = {
        "hybrid": SearchMethod.HYBRID_60_40,
        "api_only": SearchMethod.API_ONLY,
        "vector_only": SearchMethod.CHROMADB_ONLY,
    }

    search_method = method_map.get(method, SearchMethod.HYBRID_60_40)

    print(f"[*] Initializing agent with {method} search method")

    # Configure search method
    configure_ab_test("baseline")
    ab_manager = get_ab_manager()
    ab_manager.set_override(search_method)

    # Initialize agent
    adapter = MetaPropertyAPIAdapter(api_url=api_url, api_token=api_token)
    agent = create_property_react_agent(property_adapter=adapter)

    user_id = "eval_v2"
    thread_id = f"{user_id}_{method}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    results = []
    total = len(questions)

    for i, gold in enumerate(questions, 1):
        print(f"\n[{i:02d}/{total}] Q{gold.id}: {gold.question}")

        try:
            response = agent.chat(
                message=gold.question,
                thread_id=thread_id,
                user_id=user_id,
            )

            # Extract properties from response
            properties = extract_properties_from_response(response)

            if verbose:
                try:
                    # Handle encoding issues with emojis on Windows console
                    preview = response[:200].replace('\n', ' ')
                    print(f"    Response: {preview}...")
                except UnicodeEncodeError:
                    print(f"    Response: (contains special chars, {len(response)} chars)")
                print(f"    Properties found: {len(properties)}")

            results.append({
                "query_id": gold.id,
                "question": gold.question,
                "category": gold.category,
                "response": response,
                "properties": properties,
                "properties_count": len(properties),
            })

        except Exception as e:
            print(f"    [ERROR] {e}")
            results.append({
                "query_id": gold.id,
                "question": gold.question,
                "category": gold.category,
                "response": "",
                "properties": [],
                "properties_count": 0,
                "error": str(e),
            })

    return results


def main():
    args = parse_args()

    print("=" * 70)
    print("EVALUATION V2 - Constraint-Based with Confusion Matrix")
    print("=" * 70)

    # Load gold standard
    gold_path = project_root / args.gold
    print(f"\n[*] Loading gold standard: {gold_path}")
    questions, config, gold_questions_raw = load_gold_questions(gold_path)
    print(f"    Questions: {len(questions)}")
    print(f"    Threshold T: {config['threshold_t']}")

    # Apply filters
    if args.limit:
        questions = questions[:args.limit]
        print(f"    Limited to: {len(questions)}")

    if args.from_q or args.to_q:
        from_idx = args.from_q - 1 if args.from_q else 0
        to_idx = args.to_q if args.to_q else len(questions)
        questions = [q for q in questions if from_idx < q.id <= to_idx]
        print(f"    Filtered to Q{args.from_q or 1}-Q{args.to_q or 'end'}: {len(questions)}")

    # Override threshold if specified
    threshold = args.threshold if args.threshold else config["threshold_t"]

    # Setup output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = project_root / "data" / "evaluation" / "v2" / f"{args.method}_{args.llm}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n[*] Output directory: {output_dir}")

    # Get or run test results
    if args.results:
        print(f"\n[*] Loading existing results: {args.results}")
        with open(args.results, "r", encoding="utf-8") as f:
            data = json.load(f)
        test_results = data.get("results", data) if isinstance(data, dict) else data

        # Re-parse properties from response if requested
        if args.reparse:
            print("[*] Re-parsing properties from responses...")
            for result in test_results:
                response = result.get("response", "")
                properties = extract_properties_from_response(response)
                result["properties"] = properties
                result["properties_count"] = len(properties)
                print(f"    Q{result.get('query_id')}: {len(properties)} properties extracted")

    # Verify against API if requested (only if we have results from --results)
    if args.verify and args.results:
        api_url = os.getenv("METAPROPERTY_API_URL", "http://localhost:8000")
        api_token = os.getenv("METAPROPERTY_API_TOKEN", "")
        test_results = verify_properties_with_api(
            test_results, api_url, api_token, verbose=args.verbose
        )

    # Save results (if reparsed or verified from existing results)
    if args.results and (args.reparse or args.verify):
        results_file = output_dir / "results.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": timestamp,
                "method": args.method,
                "llm": args.llm,
                "threshold_t": threshold,
                "total_questions": len(questions),
                "reparsed": args.reparse,
                "verified": args.verify,
                "source_file": args.results if args.results else None,
                "results": test_results,
            }, f, ensure_ascii=False, indent=2)
        print(f"[*] Results saved: {results_file}")
    elif args.results:
        # Results already loaded above, just skip agent run
        print(f"    Using {len(test_results)} results from file")
    elif args.skip_run:
        # Try to load existing results from output dir
        existing_results = output_dir / "results.json"
        if existing_results.exists():
            print(f"\n[*] Loading existing results: {existing_results}")
            with open(existing_results, "r", encoding="utf-8") as f:
                data = json.load(f)
            test_results = data.get("results", [])
        else:
            print("[ERROR] No existing results found and --skip-run specified")
            return
    else:
        print(f"\n[*] Running agent evaluation...")
        print(f"    Method: {args.method}")
        print(f"    LLM: {args.llm}")
        test_results = run_agent_evaluation(
            questions,
            method=args.method,
            llm=args.llm,
            verbose=args.verbose,
        )

        # Verify against API if requested
        if args.verify:
            api_url = os.getenv("METAPROPERTY_API_URL", "http://localhost:8000")
            api_token = os.getenv("METAPROPERTY_API_TOKEN", "")
            print("[*] Verifying properties against API...")
            test_results = verify_properties_with_api(
                test_results, api_url, api_token, verbose=args.verbose
            )

        # Save results (with merge for incremental evaluation)
        results_file = output_dir / "results.json"

        # Merge with existing results if doing incremental evaluation
        if results_file.exists() and (args.from_q or args.to_q):
            print("[*] Merging with existing results...")
            with open(results_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
            existing_results = existing_data.get("results", [])

            # Create map by query_id
            results_map = {r.get("query_id"): r for r in existing_results}

            # Update with new results
            for new_result in test_results:
                results_map[new_result.get("query_id")] = new_result

            # Sort by query_id
            test_results = sorted(results_map.values(), key=lambda r: r.get("query_id", 0))
            print(f"    Merged: {len(test_results)} total results")

        with open(results_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": timestamp,
                "method": args.method,
                "llm": args.llm,
                "threshold_t": threshold,
                "total_questions": len(test_results),
                "verified": args.verify,
                "results": test_results,
            }, f, ensure_ascii=False, indent=2)
        print(f"\n[*] Results saved: {results_file}")

    # Run evaluation
    print("\n[*] Running constraint evaluation...")
    evaluator = Evaluator(
        threshold_t=threshold,
        price_tolerance=config["price_tolerance"],
    )

    evaluations, metrics = evaluator.run_evaluation(questions, test_results)

    # For incremental evaluation, recalculate with ALL gold questions
    # since test_results has been merged above
    if args.from_q or args.to_q:
        print("[*] Recalculating evaluations for all merged results...")
        all_gold, _, _ = load_gold_questions(gold_path)
        evaluations, metrics = evaluator.run_evaluation(all_gold, test_results)
        print(f"    Total evaluations: {len(evaluations)}")

    # Apply manual input if provided
    if args.manual_input:
        print(f"\n[*] Applying manual input: {args.manual_input}")
        evaluations = apply_manual_input(
            evaluations,
            args.manual_input,
            verbose=args.verbose,
        )
        # Recalculate metrics after applying manual overrides
        print("[*] Recalculating metrics with manual input...")
        metrics = evaluator.calculate_metrics(evaluations)

    # Save evaluation results
    eval_data = {
        "timestamp": timestamp,
        "method": args.method,
        "llm": args.llm,
        "threshold_t": threshold,
        "metrics": metrics.to_dict(),
        "evaluations": [
            {
                "query_id": e.query_id,
                "question": e.question,
                "category": e.category,
                "expected_result": e.expected_result,
                "has_results": e.has_results,
                "num_properties": e.num_properties,
                "mean_cpr": e.mean_cpr,
                "strict_success": e.strict_success_count,
                "is_success": e.is_success(threshold),
                "confusion_category": e.get_confusion_category(threshold),
            }
            for e in evaluations
        ],
    }

    # Save metrics
    metrics_file = output_dir / "metrics.json"
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(eval_data, f, ensure_ascii=False, indent=2)
    print(f"[*] Metrics saved: {metrics_file}")

    # Generate HTML report
    print("\n[*] Generating HTML report...")
    report_gen = HTMLReportGenerator()
    html_file = output_dir / "evaluation.html"
    report_gen.generate_report(
        evaluations=evaluations,
        metrics=metrics,
        output_path=html_file,
        title=f"Evaluation V2 - {args.method.upper()} / {args.llm.upper()}",
        timestamp=timestamp,
        raw_results=test_results,
        gold_questions=gold_questions_raw,
    )
    print(f"[*] HTML report: {html_file}")

    # Log run info
    run_log_file = output_dir / "run_log.json"
    run_log = []
    if run_log_file.exists():
        with open(run_log_file, "r", encoding="utf-8") as f:
            run_log = json.load(f)
    run_log.append({
        "timestamp": timestamp,
        "from_q": args.from_q,
        "to_q": args.to_q,
        "limit": args.limit,
        "questions_evaluated": len(questions),
    })
    with open(run_log_file, "w", encoding="utf-8") as f:
        json.dump(run_log, f, ensure_ascii=False, indent=2)

    # Print summary
    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Total Queries:       {metrics.total_queries}")
    print(f"Total Properties:    {metrics.total_properties}")
    print(f"Threshold T:         {threshold}")
    print("-" * 40)
    print(f"Mean CPR:            {metrics.mean_cpr:.2%}")
    print(f"Strict Success:      {metrics.strict_success_ratio:.2%}")
    print(f"Query Success Rate:  {metrics.query_success_rate:.2%}")
    print("-" * 40)
    cm = metrics.confusion_matrix
    print(f"Confusion Matrix:")
    print(f"  TP: {cm.tp}  FP: {cm.fp}")
    print(f"  FN: {cm.fn}  TN: {cm.tn}")
    print("-" * 40)
    print(f"Precision:           {cm.precision:.2%}")
    print(f"Recall:              {cm.recall:.2%}")
    print(f"F1 Score:            {cm.f1_score:.2%}")
    print(f"Accuracy:            {cm.accuracy:.2%}")
    print("=" * 70)

    print(f"\nOpen report: {html_file}")


if __name__ == "__main__":
    main()
