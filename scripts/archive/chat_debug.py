"""
DEBUG Chat - Shows detailed processing steps
Run: python scripts/chat_debug.py
"""
import asyncio
import os
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from src.agents.orchestrator import OrchestratorAgent
from src.agents.property_agent import PropertyAgent
from src.agents.coach_agent import CoachAgent
from src.adapters.metaproperty import MetaPropertyAPIAdapter
from src.adapters.base import SearchCriteria


def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


async def debug_search(query: str):
    """Debug a single search query step by step"""
    
    print_section("🔍 DEBUG: Property Search Flow")
    print(f"\nQuery: '{query}'")
    
    # Get config
    api_url = os.getenv("METAPROPERTY_API_URL", "http://localhost:8000")
    api_token = os.getenv("METAPROPERTY_API_TOKEN", "")
    
    print(f"\n📡 API Config:")
    print(f"   URL: {api_url}")
    print(f"   Token: {'✓ Set' if api_token else '✗ Missing'}")
    
    # Step 1: Initialize adapter
    print_section("STEP 1: Initialize Data Adapter")
    adapter = MetaPropertyAPIAdapter(api_url=api_url, api_token=api_token)
    print(f"   Adapter: MetaPropertyAPIAdapter")
    print(f"   API URL: {adapter.api_url}")
    
    # Step 2: Test direct API call
    print_section("STEP 2: Test Direct API Call (No Filters)")
    try:
        # Search with no filters first
        empty_criteria = SearchCriteria()
        result = await adapter.search(empty_criteria)
        print(f"   ✓ API responds!")
        print(f"   Total properties in DB: {result.total}")
        print(f"   Returned: {len(result.properties)} properties")
        if result.properties:
            print(f"\n   Sample properties:")
            for i, prop in enumerate(result.properties[:3], 1):
                print(f"   {i}. {prop.title}")
                print(f"      Location: {prop.location}, {prop.city}")
                print(f"      Price: Rp {prop.price:,.0f}")
    except Exception as e:
        print(f"   ✗ API Error: {e}")
        return
    
    # Step 3: Initialize Property Agent
    print_section("STEP 3: Initialize Property Agent")
    property_agent = PropertyAgent(data_adapter=adapter)
    print(f"   ✓ Property Agent initialized")
    print(f"   Vector search enabled: {property_agent.enable_vector_search}")
    
    # Step 4: Parse the query
    print_section("STEP 4: Parse Natural Language Query")
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage
    
    # Use the same parsing prompt
    from src.agents.property_agent import SEARCH_PARSER_PROMPT
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    parse_prompt = SEARCH_PARSER_PROMPT.format(query=query, context="None")
    
    print(f"\n   Sending to LLM for parsing...")
    response = await llm.ainvoke([HumanMessage(content=parse_prompt)])
    
    print(f"\n   LLM Raw Response:")
    print(f"   {response.content[:500]}")
    
    # Extract JSON
    try:
        content = response.content
        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            parsed = json.loads(content[start:end])
            print(f"\n   ✓ Parsed JSON:")
            print(f"   {json.dumps(parsed, indent=4)}")
        else:
            parsed = {}
            print(f"   ✗ No JSON found in response")
    except json.JSONDecodeError as e:
        print(f"   ✗ JSON Parse Error: {e}")
        parsed = {}
    
    # Step 5: Build SearchCriteria
    print_section("STEP 5: Build Search Criteria")
    
    from src.adapters.base import PropertyType, ListingType
    
    # Use search_keywords for clean search
    search_keywords = parsed.get("search_keywords") or parsed.get("location") or parsed.get("landmark")
    
    criteria = SearchCriteria(
        query=search_keywords,  # Clean keywords for API search
        location=parsed.get("location"),
        city=parsed.get("city"),
        min_price=parsed.get("min_price"),
        max_price=parsed.get("max_price"),
        min_bedrooms=parsed.get("min_bedrooms"),
    )
    
    # Parse property type
    if parsed.get("property_type"):
        try:
            criteria.property_type = PropertyType(parsed["property_type"])
        except ValueError:
            print(f"   ⚠ Invalid property_type: {parsed['property_type']}")
    
    print(f"\n   SearchCriteria object:")
    print(f"   - query: {criteria.query}")
    print(f"   - location: {criteria.location}")
    print(f"   - city: {criteria.city}")
    print(f"   - property_type: {criteria.property_type}")
    print(f"   - min_price: {criteria.min_price}")
    print(f"   - max_price: {criteria.max_price}")
    print(f"   - min_bedrooms: {criteria.min_bedrooms}")
    
    # Step 6: Execute API Search with criteria
    print_section("STEP 6: Execute API Search with Criteria")
    
    result = await adapter.search(criteria)
    
    print(f"\n   Results: {len(result.properties)} / {result.total} total")
    
    if result.properties:
        print(f"\n   Found properties:")
        for i, prop in enumerate(result.properties[:5], 1):
            print(f"   {i}. {prop.title}")
            print(f"      Location: {prop.location}, {prop.city}")
            print(f"      Type: {prop.property_type.value if prop.property_type else 'N/A'}")
            print(f"      Price: Rp {prop.price:,.0f}")
            print()
    else:
        print(f"\n   ✗ NO PROPERTIES FOUND!")
        print(f"\n   Possible issues:")
        print(f"   1. Location '{criteria.location}' might not match DB exactly")
        print(f"   2. API filter is case-sensitive?")
        print(f"   3. Check what locations exist in database")
    
    # Step 7: Debug - What locations exist?
    print_section("STEP 7: Available Locations in Database")
    
    # Fetch all without filter
    all_criteria = SearchCriteria(limit=100)
    all_result = await adapter.search(all_criteria)
    
    locations = set()
    cities = set()
    for prop in all_result.properties:
        if prop.location:
            locations.add(prop.location.lower())
        if prop.city:
            cities.add(prop.city.lower())
    
    print(f"\n   Unique locations: {sorted(locations)}")
    print(f"\n   Unique cities: {sorted(cities)}")
    
    # Check if user's location is in there
    user_loc = (criteria.location or "").lower()
    if user_loc:
        matching = [loc for loc in locations if user_loc in loc or loc in user_loc]
        print(f"\n   Locations matching '{user_loc}': {matching if matching else 'NONE!'}")


async def main():
    print("=" * 60)
    print("🔍 DEBUG MODE - Property Search Flow")
    print("=" * 60)
    print("\nThis shows step-by-step how a search query is processed.")
    
    while True:
        print("\n" + "-" * 60)
        query = input("Enter search query (or 'quit'): ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        if not query:
            query = "cari rumah di daerah cemara asri"
            print(f"Using default: '{query}'")
        
        await debug_search(query)


if __name__ == "__main__":
    asyncio.run(main())
