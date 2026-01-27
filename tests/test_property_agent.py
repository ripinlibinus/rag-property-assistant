"""
Test script for Property Agent with MetaProperty adapter
Run: python -m tests.test_property_agent
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def test_search():
    """Test property search"""
    from src.agents import create_property_agent
    
    api_url = os.getenv("METAPROPERTY_API_URL", "http://localhost:8000")
    
    print(f"🔗 Connecting to MetaProperty API: {api_url}")
    
    agent = create_property_agent(
        api_url=api_url,
        enable_vector_search=False,  # Disable for initial test
    )
    
    # Simulate search state
    state = {
        "current_input": "Cari rumah 3 kamar di Sunggal budget 1M",
        "session_id": "test-session",
        "client_phone": "08123456789",
        "messages": [],
        "metrics": {},
    }
    
    print("\n📝 Query: Cari rumah 3 kamar di Sunggal budget 1M")
    print("-" * 50)
    
    try:
        result = await agent.search(state)
        print("\n✅ Response:")
        print(result.get("response", "No response"))
        
        properties = result.get("retrieved_properties", [])
        print(f"\n📊 Retrieved {len(properties)} properties")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure MetaProperty API is running and METAPROPERTY_API_URL is set correctly")


async def test_orchestrator():
    """Test full orchestrator flow"""
    from src.agents import create_orchestrator_from_env
    
    print("\n🤖 Testing Orchestrator Agent")
    print("=" * 50)
    
    try:
        orchestrator = create_orchestrator_from_env()
        
        test_messages = [
            "Halo",
            "Cari rumah 3KT di Sunggal budget 1M",
            "Apa itu SHM?",
            "Tips closing buyer yang ragu",
        ]
        
        for msg in test_messages:
            print(f"\n👤 User: {msg}")
            result = await orchestrator.process(
                message=msg,
                session_id="test-session",
                client_phone="08123456789",
            )
            print(f"🤖 Bot: {result['response'][:200]}...")
            print(f"   Intent: {result['intent']} (confidence: {result['confidence']:.2f})")
            print("-" * 50)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    print("=" * 60)
    print("  RAG Property Agent - Integration Test")
    print("=" * 60)
    
    # Check OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️ OPENAI_API_KEY not set. Please set it in .env file.")
        return
    
    # Test property agent
    await test_search()
    
    # Test orchestrator
    await test_orchestrator()
    
    print("\n✅ Tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
