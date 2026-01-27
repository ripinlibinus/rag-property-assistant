"""
Simple Interactive Chat for Manual Testing
Run: python scripts/chat_test.py
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
from src.agents.state import AgentState
from src.adapters.metaproperty import MetaPropertyAPIAdapter


async def main():
    print("=" * 60)
    print("🏠 RAG Property Agent - Manual Testing")
    print("=" * 60)
    print("\nInitializing agents...")
    
    # Get config from env
    api_url = os.getenv("METAPROPERTY_API_URL", "http://localhost:8000")
    api_token = os.getenv("METAPROPERTY_API_TOKEN", "")
    
    # Initialize data adapter
    data_adapter = MetaPropertyAPIAdapter(
        api_url=api_url,
        api_token=api_token,
    )
    
    # Initialize agents
    property_agent = PropertyAgent(data_adapter=data_adapter)
    coach_agent = CoachAgent()
    
    # Initialize coach agent (index knowledge base)
    print("  - Indexing knowledge base...")
    await coach_agent.initialize()
    
    # Initialize orchestrator with agents
    orchestrator = OrchestratorAgent(
        property_agent=property_agent,
        coach_agent=coach_agent,
    )
    
    print("✅ Ready! Type your message (or 'quit' to exit)\n")
    print("Example queries:")
    print("  - Cari rumah di Medan harga 1 miliar")
    print("  - Apa itu SHM dan SHGB?")
    print("  - Tips closing yang efektif")
    print("  - Halo")
    print("-" * 60)
    
    session_id = "test-session-001"
    client_phone = "08123456789"
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            # Process through orchestrator (uses message, session_id, client_phone)
            print("\n⏳ Processing...")
            result = await orchestrator.process(
                message=user_input,
                session_id=session_id,
                client_phone=client_phone,
            )
            
            # Display result
            response = result.get("response", "No response generated")
            intent = result.get("intent", "unknown")
            routed_to = result.get("routed_to", "unknown")
            
            print(f"\n🤖 Agent ({routed_to} | intent: {intent}):")
            print(f"   {response}")
            
            # Show properties if any
            if result.get("retrieved_properties"):
                props = result["retrieved_properties"]
                print(f"\n   📋 Found {len(props)} properties:")
                for i, prop in enumerate(props[:3], 1):
                    title = prop.get("title", prop.get("name", "N/A"))
                    price = prop.get("price", 0)
                    city = prop.get("city", "")
                    print(f"      {i}. {title} - Rp {price:,.0f} ({city})")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
