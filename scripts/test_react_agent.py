"""
Test script for the NEW ReAct Agent

This demonstrates the PROPER agent pattern where:
- LLM decides which tools to call
- Not hardcoded routing
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()


def main():
    """Test the ReAct agent"""
    
    print("=" * 60)
    print("ReAct Property Agent Test")
    print("=" * 60)
    
    # Import agent components
    from src.adapters.metaproperty import MetaPropertyAPIAdapter
    from src.agents.react_agent import ReActPropertyAgent, create_property_react_agent
    
    # Get config
    api_url = os.getenv("METAPROPERTY_API_URL", "http://localhost:8000")
    api_token = os.getenv("METAPROPERTY_API_TOKEN", "")
    
    if not api_token:
        print("⚠️ METAPROPERTY_API_TOKEN not set!")
        print("Using sample data adapter instead...")
        # TODO: Fall back to sample data
    
    # Create adapter
    print(f"\n📡 Connecting to API: {api_url}")
    adapter = MetaPropertyAPIAdapter(
        api_url=api_url,
        api_token=api_token,
    )
    
    # Create ReAct agent
    print("🤖 Creating ReAct Agent...")
    agent = create_property_react_agent(
        property_adapter=adapter,
        model_name="gpt-4o-mini",
    )
    
    # Test queries
    test_queries = [
        "Halo!",
        "cari rumah di cemara asri",
        "ada ruko di daerah sunggal?",
        "tips untuk closing yang efektif",
        "kasih motivasi dong",
    ]
    
    print("\n🧪 Running Test Queries:")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}] User: {query}")
        print("-" * 40)
        
        try:
            # Chat with streaming to see the agent's thinking
            response = agent.chat(
                message=query,
                thread_id=f"test_{i}",
            )
            
            print(f"Agent: {response}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print("-" * 40)
    
    # Interactive mode
    print("\n" + "=" * 60)
    print("🎮 Interactive Mode (type 'quit' to exit)")
    print("=" * 60)
    
    thread_id = "interactive"
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye! 👋")
                break
            
            if not user_input:
                continue
            
            # Stream the response to see thinking
            print("\nAgent thinking...")
            
            response = agent.chat(
                message=user_input,
                thread_id=thread_id,
            )
            
            print(f"\nAgent: {response}")
            
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()


def test_stream():
    """Test streaming mode to see agent's thought process"""
    
    from src.adapters.metaproperty import MetaPropertyAPIAdapter
    from src.agents.react_agent import create_property_react_agent
    
    api_url = os.getenv("METAPROPERTY_API_URL", "http://localhost:8000")
    api_token = os.getenv("METAPROPERTY_API_TOKEN", "")
    
    adapter = MetaPropertyAPIAdapter(api_url=api_url, api_token=api_token)
    agent = create_property_react_agent(property_adapter=adapter)
    
    print("\n🔄 Streaming Mode Test")
    print("=" * 60)
    
    query = "cari rumah di cemara asri dengan 3 kamar tidur"
    print(f"Query: {query}\n")
    
    for event in agent.stream_chat(query, thread_id="stream_test"):
        messages = event.get("messages", [])
        if messages:
            last_msg = messages[-1]
            
            if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                for tc in last_msg.tool_calls:
                    print(f"🔧 Calling tool: {tc['name']}")
                    print(f"   Args: {tc['args']}")
            elif hasattr(last_msg, "content") and last_msg.content:
                if last_msg.type == "tool":
                    print(f"📤 Tool result: {last_msg.content[:200]}...")
                elif last_msg.type == "ai":
                    print(f"\n✅ Final response:\n{last_msg.content}")


def test_verbose():
    """Test with FULL verbose output showing complete thinking process"""
    
    from src.adapters.metaproperty import MetaPropertyAPIAdapter
    from src.agents.react_agent import create_property_react_agent
    from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
    
    api_url = os.getenv("METAPROPERTY_API_URL", "http://localhost:8000")
    api_token = os.getenv("METAPROPERTY_API_TOKEN", "")
    
    adapter = MetaPropertyAPIAdapter(api_url=api_url, api_token=api_token)
    agent = create_property_react_agent(property_adapter=adapter)
    
    print("\n" + "=" * 70)
    print("🧠 VERBOSE MODE - Full Agent Thinking Process")
    print("=" * 70)
    
    queries = [
        "cari rumah di cemara asri dengan 3 kamar tidur",
        # "tips untuk closing yang efektif",
    ]
    
    for query in queries:
        print(f"\n{'─' * 70}")
        print(f"📝 USER INPUT: {query}")
        print(f"{'─' * 70}\n")
        
        step = 0
        for event in agent.stream_chat(query, thread_id="verbose_test"):
            messages = event.get("messages", [])
            
            if not messages:
                continue
                
            last_msg = messages[-1]
            step += 1
            
            print(f"┌─ Step {step} ─────────────────────────────────────────────────")
            print(f"│ Message Type: {type(last_msg).__name__}")
            
            if isinstance(last_msg, SystemMessage):
                print(f"│ Role: SYSTEM")
                print(f"│ Content: [System prompt - {len(last_msg.content)} chars]")
                
            elif isinstance(last_msg, HumanMessage):
                print(f"│ Role: USER")
                print(f"│ Content: {last_msg.content}")
                
            elif isinstance(last_msg, AIMessage):
                print(f"│ Role: ASSISTANT (Agent)")
                
                # Check for tool calls
                if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                    print(f"│ ")
                    print(f"│ 🤔 THINKING: I need to use tools to answer this...")
                    print(f"│ ")
                    for i, tc in enumerate(last_msg.tool_calls, 1):
                        print(f"│ 🔧 Tool Call #{i}:")
                        print(f"│    Name: {tc['name']}")
                        print(f"│    Arguments:")
                        for key, val in tc['args'].items():
                            print(f"│      - {key}: {val}")
                        print(f"│    Tool Call ID: {tc['id']}")
                else:
                    # Final response (no tool calls)
                    print(f"│ ")
                    print(f"│ 💡 DECISION: I have enough info, responding directly")
                    print(f"│ ")
                    print(f"│ Content:")
                    # Print content with indentation
                    for line in last_msg.content.split('\n')[:15]:
                        print(f"│   {line}")
                    if last_msg.content.count('\n') > 15:
                        print(f"│   ... [{last_msg.content.count(chr(10)) - 15} more lines]")
                        
            elif isinstance(last_msg, ToolMessage):
                print(f"│ Role: TOOL RESULT")
                print(f"│ Tool Call ID: {last_msg.tool_call_id}")
                print(f"│ ")
                print(f"│ 📤 RESULT from tool:")
                # Print truncated result
                result_preview = last_msg.content[:500]
                for line in result_preview.split('\n')[:10]:
                    print(f"│   {line}")
                if len(last_msg.content) > 500:
                    print(f"│   ... [{len(last_msg.content) - 500} more chars]")
            
            print(f"└{'─' * 60}")
            print()
        
        print(f"\n{'═' * 70}")
        print(f"✅ Conversation complete ({step} steps)")
        print(f"{'═' * 70}\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test ReAct Agent")
    parser.add_argument("--stream", action="store_true", help="Test streaming mode")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show full thinking process")
    
    args = parser.parse_args()
    
    if args.verbose:
        test_verbose()
    elif args.stream:
        test_stream()
    else:
        main()
