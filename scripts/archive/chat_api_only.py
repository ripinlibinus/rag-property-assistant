"""
Interactive Chat - API ONLY (No ChromaDB)

Test chat dengan hanya menggunakan API search.
Tidak ada hybrid search, tidak ada semantic re-ranking.
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
    print("🔌 Property Assistant - API ONLY MODE")
    print("=" * 60)
    print("Mode: API search only (no ChromaDB, no hybrid)")
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

    # Create agent with hybrid search DISABLED
    agent = ReActPropertyAgent(
        property_adapter=adapter,
        llm=llm,
        use_hybrid_search=False,  # <-- API ONLY
    )

    print(f"✅ Agent ready (API only mode)")

    # Thread ID includes user_id for isolation
    thread_id = f"{user_id}_api_only"

    while True:
        try:
            print()
            user_input = input("You: ").strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            if user_input.lower() == "clear":
                thread_id = f"{user_id}_api_only_{os.urandom(4).hex()}"
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


if __name__ == "__main__":
    main()
