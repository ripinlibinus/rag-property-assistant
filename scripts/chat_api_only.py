"""
Chat with API Only - Testing API search without ChromaDB re-ranking

Usage:
    python scripts/chat_api_only.py
    python scripts/chat_api_only.py -v  # verbose mode

This script tests API search directly without ChromaDB semantic re-ranking.
Useful for verifying that API filters work correctly.
"""

import os
import sys

# Disable ChromaDB telemetry BEFORE any imports
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import asyncio
import argparse
import logging
from pathlib import Path

# Suppress noisy logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.ERROR)

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

# Fix Windows encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

from rich.console import Console
from rich.markdown import Markdown

console = Console(force_terminal=True)


def main(verbose=False):
    """Start interactive chat with API-only search"""

    from src.adapters.metaproperty import MetaPropertyAPIAdapter
    from src.agents.react_agent import create_property_react_agent
    from src.utils.ab_testing import configure_ab_test, get_ab_manager, SearchMethod

    api_url = os.getenv("METAPROPERTY_API_URL", "http://localhost:8000")
    api_token = os.getenv("METAPROPERTY_API_TOKEN", "")

    # Configure API-only mode (no ChromaDB re-ranking)
    configure_ab_test("baseline")
    ab_manager = get_ab_manager()
    ab_manager.set_override(SearchMethod.API_ONLY)

    console.print()
    console.print("[bold cyan]Property Assistant[/bold cyan] [bold yellow](API-Only Mode)[/bold yellow]")
    console.print("[dim]ChromaDB re-ranking disabled - pure API search[/dim]")
    console.print("[dim]Type 'quit' to exit, 'clear' to reset session[/dim]")
    console.rule(style="dim")

    # Get user ID
    console.print()
    user_id = console.input("[dim]User ID (enter for guest):[/dim] ").strip() or "guest"
    console.print(f"[dim]Logged in as: {user_id}[/dim]")

    # Create agent
    adapter = MetaPropertyAPIAdapter(api_url=api_url, api_token=api_token)
    agent = create_property_react_agent(property_adapter=adapter)

    thread_id = f"{user_id}_api_only"

    while True:
        try:
            console.print()
            user_input = console.input("[bold green]You:[/bold green] ").strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                console.print("[cyan]Goodbye![/cyan]")
                break

            if user_input.lower() == "clear":
                thread_id = f"{user_id}_api_only_{os.urandom(4).hex()}"
                console.print("[green]Session cleared.[/green]")
                continue

            if not user_input:
                continue

            # Process chat
            if verbose:
                # Verbose mode - show tool calls
                console.print("\n[magenta]Processing...[/magenta]")

                async def run_verbose():
                    tool_calls_shown = []
                    async for event in agent.astream_chat_tokens(user_input, thread_id=thread_id, user_id=user_id):
                        event_type = event.get("type")

                        if event_type == "tool_call":
                            tool_name = event["name"]
                            args = event["args"]
                            args_str = ", ".join([f"{k}={repr(v)[:50]}" for k, v in args.items()])
                            console.print(f"  [blue]Tool:[/blue] [cyan]{tool_name}[/cyan]({args_str})")
                            tool_calls_shown.append(tool_name)

                        elif event_type == "tool_result":
                            content = event["content"]
                            # Count properties in result
                            import re
                            prop_match = re.search(r'Ditemukan\s+(\d+)\s+properti', content)
                            if prop_match:
                                console.print(f"  [green]Result: {prop_match.group(1)} properties found[/green]")
                            else:
                                lines = len(content.split('\n'))
                                console.print(f"  [dim]Result: {lines} lines[/dim]")

                        elif event_type == "response_done":
                            return event["content"]

                    return ""

                response = asyncio.run(run_verbose())
            else:
                with console.status("[cyan]Searching via API...[/cyan]", spinner="dots"):
                    response = agent.chat(
                        message=user_input,
                        thread_id=thread_id,
                        user_id=user_id,
                    )

            console.print()
            console.print(Markdown(response))

            # Count properties in response
            import re
            prop_count = len(re.findall(r'(?:^|\n)\s*(?:\*\*)?(\d+)\.', response))
            if prop_count > 0:
                console.print(f"\n[dim]Found {prop_count} properties in response[/dim]")

        except KeyboardInterrupt:
            console.print("\n[cyan]Goodbye![/cyan]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interactive Property Chat (API-Only)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Show detailed processing")
    args = parser.parse_args()

    main(verbose=args.verbose)
