"""
Interactive Chat - HYBRID MODE (API + ChromaDB Re-ranking)

Test chat dengan hybrid search:
1. API filter untuk structured criteria (price, bedrooms, location)
2. ChromaDB semantic re-ranking untuk relevance
3. Fallback ke pure semantic jika API return 0
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from src.adapters.metaproperty import MetaPropertyAPIAdapter
from src.agents.react_agent import ReActPropertyAgent
from langchain_openai import ChatOpenAI


def main():
    print("=" * 60)
    print("🔀 Property Assistant - HYBRID MODE")
    print("=" * 60)
    print("Mode: API filtering + ChromaDB semantic re-ranking")
    print("-" * 60)

    # Get user ID for proper isolation
    print("Enter your user ID (or press Enter for 'guest'):")
    user_id = input("> ").strip() or "guest"
    print(f"User ID: {user_id}")
    print("-" * 60)
    print("Commands: 'quit' to exit, 'clear' to reset")
    print("-" * 60)

    api_url = os.getenv("METAPROPERTY_API_URL", "http://localhost:8000")
    api_token = os.getenv("METAPROPERTY_API_TOKEN", "")

    adapter = MetaPropertyAPIAdapter(api_url=api_url, api_token=api_token)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Create agent with hybrid search ENABLED
    agent = ReActPropertyAgent(
        property_adapter=adapter,
        llm=llm,
        use_hybrid_search=True,  # <-- HYBRID MODE
    )

    print(f"✅ Agent ready (Hybrid mode)")

    # Thread ID includes user_id for isolation
    thread_id = f"{user_id}_hybrid"

    while True:
        try:
            print()
            user_input = input("You: ").strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            if user_input.lower() == "clear":
                thread_id = f"{user_id}_hybrid_{os.urandom(4).hex()}"
                print("Conversation cleared (new session)")
                continue

            if not user_input:
                continue

            # Run agent with user_id for isolation
            response = agent.chat(user_input, thread_id=thread_id, user_id=user_id)
            print(f"\nAssistant: {response}")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
