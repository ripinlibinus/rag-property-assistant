"""
Interactive Chat with ReAct Agent
Tree-style display with streaming
"""

import os
import sys

# Disable ChromaDB telemetry BEFORE any imports
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import time
import asyncio
import argparse
import logging
from pathlib import Path

# Suppress noisy logs early
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.ERROR)
logging.getLogger("chromadb.telemetry").setLevel(logging.ERROR)
logging.getLogger("chromadb.config").setLevel(logging.ERROR)

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

# Rich imports
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.tree import Tree
from rich.rule import Rule

# Fix Windows encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Initialize Rich console
console = Console(force_terminal=True)

# Import token utilities
from src.utils.tokens import count_tokens, estimate_cost

# Exchange rate
USD_TO_IDR = 17000.0

# Tree characters
TREE = {
    "branch": "├─",
    "last": "└─",
    "pipe": "│ ",
    "space": "  ",
}


# ============================================================================
# Tree-Style Display Helpers
# ============================================================================

def print_header():
    """Print minimal header"""
    console.print()
    console.print("[bold cyan]Property Assistant[/bold cyan] [dim]v2.0[/dim]")
    console.print("[dim]Type 'quit' to exit, 'clear' to reset[/dim]")
    console.rule(style="dim")


def print_tree_item(prefix: str, label: str, content: str = "", style: str = "white", is_last: bool = False):
    """Print a tree item with proper indentation"""
    branch = TREE["last"] if is_last else TREE["branch"]
    console.print(f"{prefix}{branch} [bold {style}]{label}[/bold {style}]", end="")
    if content:
        console.print(f" [dim]{content}[/dim]")
    else:
        console.print()


def print_tree_content(prefix: str, content: str, style: str = "white", is_last: bool = False):
    """Print content under a tree branch"""
    indent = TREE["space"] if is_last else TREE["pipe"]
    lines = content.split('\n')
    for line in lines:
        if line.strip():
            console.print(f"{prefix}{indent}  [{style}]{line}[/{style}]")


def print_processing_start():
    """Print processing header"""
    console.print()
    console.print("[bold magenta]┌ Processing...[/bold magenta]")


def print_user_input(query: str):
    """Print user input in tree format"""
    console.print(f"[magenta]{TREE['branch']}[/magenta] [bold green]Input:[/bold green] [white]\"{query}\"[/white]")


def print_reasoning(content: str, is_streaming: bool = False):
    """Print LLM reasoning in tree format"""
    console.print(f"[magenta]{TREE['branch']}[/magenta] [bold yellow]Thinking:[/bold yellow]")

    # Parse and display reasoning content
    lines = content.strip().split('\n')
    for i, line in enumerate(lines):
        is_last_line = (i == len(lines) - 1)
        branch = TREE["space"]

        if line.strip():
            # Highlight **bold** text
            if '**' in line:
                line = line.replace('**Thinking**:', '[cyan]Thinking:[/cyan]')
                line = line.replace('**Strategy**:', '[cyan]Strategy:[/cyan]')
                line = line.replace('**Action**:', '[cyan]Action:[/cyan]')
                line = line.replace('**', '')
            console.print(f"[magenta]{TREE['pipe']}[/magenta]   [dim]{line}[/dim]")


def print_tool_call(tool_name: str, args: dict):
    """Print tool call in tree format"""
    args_str = ", ".join([f"{k}={repr(v)}" for k, v in args.items()])
    console.print(f"[magenta]{TREE['branch']}[/magenta] [bold blue]Tool:[/bold blue] [cyan]{tool_name}[/cyan]({args_str})")


def print_tool_result(content: str, lines_to_show: int = 8):
    """Print tool result with detail"""
    import re

    lines = content.split('\n')
    total_lines = len(lines)

    # Count properties from result
    prop_count = 0
    prop_match = re.search(r'Ditemukan\s+(\d+)\s+properti', content)
    if prop_match:
        prop_count = int(prop_match.group(1))
    else:
        # Count numbered items
        prop_count = len(re.findall(r'^\d+\.', content, re.MULTILINE))

    # Header with count
    if prop_count > 0:
        console.print(f"[magenta]{TREE['pipe']}[/magenta]   [bold green]✓ Found {prop_count} properties[/bold green]")
    else:
        console.print(f"[magenta]{TREE['pipe']}[/magenta]   [dim]Result: {total_lines} lines[/dim]")

    # Show preview of results
    for i, line in enumerate(lines[:lines_to_show]):
        if line.strip():
            # Highlight property numbers
            if re.match(r'^\d+\.', line):
                console.print(f"[magenta]{TREE['pipe']}[/magenta]   [yellow]{line}[/yellow]")
            else:
                console.print(f"[magenta]{TREE['pipe']}[/magenta]   [dim]{line}[/dim]")

    if total_lines > lines_to_show:
        remaining = total_lines - lines_to_show
        console.print(f"[magenta]{TREE['pipe']}[/magenta]   [dim]... +{remaining} more lines[/dim]")


def print_response_start():
    """Print response section start"""
    console.print(f"[magenta]{TREE['last']}[/magenta] [bold green]Response:[/bold green]")


def print_response(content: str, stream: bool = False):
    """Print the assistant response (no streaming to avoid duplication issues)"""
    console.print()
    # Direct Markdown render - no streaming animation to avoid Windows terminal issues
    console.print(Markdown(content))


def print_token_summary(input_tokens: int, output_tokens: int):
    """Print token usage summary in one line"""
    usage = estimate_cost(input_tokens, output_tokens)
    console.print()
    console.print(
        f"[dim]Tokens: {usage['total_tokens']:,} | "
        f"Cost: ${usage['total_usd']:.4f} (Rp {usage['total_idr']:,.0f})[/dim]"
    )


def print_session_summary(total_tokens: int, total_cost_usd: float):
    """Print session summary"""
    console.print()
    console.rule("[cyan]Session Summary[/cyan]", style="cyan")
    console.print(f"  Total tokens: [bold]{total_tokens:,}[/bold]")
    console.print(f"  Total cost: [yellow]${total_cost_usd:.6f}[/yellow] (Rp {total_cost_usd * USD_TO_IDR:,.0f})")
    console.rule(style="cyan")


# ============================================================================
# Async Streaming Chat Handler
# ============================================================================

async def process_streaming_chat(agent, user_input: str, thread_id: str, user_id: str):
    """Process chat with tree-style display"""

    reasoning_buffer = ""
    response_buffer = ""
    input_tokens = 0
    output_tokens = 0

    # State tracking
    has_tool_calls = False
    after_tool_result = False
    shown_reasoning = False

    # Start processing
    print_processing_start()
    print_user_input(user_input)
    input_tokens += count_tokens(user_input)

    try:
        async for event in agent.astream_chat_tokens(user_input, thread_id=thread_id, user_id=user_id):
            event_type = event.get("type")

            # Skip user_input event (already shown)
            if event_type == "user_input":
                continue

            # Reasoning token - buffer it
            elif event_type == "reasoning_token":
                reasoning_buffer += event["content"]
                output_tokens += 1

            # Reasoning done
            elif event_type == "reasoning_done":
                pass  # Wait to see if tool_call follows

            # Tool call - show reasoning then tool
            elif event_type == "tool_call":
                has_tool_calls = True

                # Show reasoning if we have it
                if reasoning_buffer and not shown_reasoning:
                    print_reasoning(reasoning_buffer)
                    shown_reasoning = True

                # Show tool call
                print_tool_call(event["name"], event["args"])
                reasoning_buffer = ""

            # Tool result
            elif event_type == "tool_result":
                print_tool_result(event["content"])
                input_tokens += count_tokens(event["content"])
                after_tool_result = True
                reasoning_buffer = ""

            # Response done
            elif event_type == "response_done":
                response_buffer = event["content"]
                output_tokens = count_tokens(response_buffer)

            # Done
            elif event_type == "done":
                break

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise e

    return {
        "response": response_buffer,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }


# ============================================================================
# Main Chat Function
# ============================================================================

def main(verbose=False):
    """Start interactive chat"""

    from src.adapters.metaproperty import MetaPropertyAPIAdapter
    from src.agents.react_agent import create_property_react_agent

    api_url = os.getenv("METAPROPERTY_API_URL", "http://localhost:8000")
    api_token = os.getenv("METAPROPERTY_API_TOKEN", "")

    # Print header
    print_header()

    # Get user ID
    console.print()
    user_id = console.input("[dim]User ID (enter for guest):[/dim] ").strip() or "guest"
    console.print(f"[dim]Logged in as: {user_id}[/dim]")

    # Create agent
    adapter = MetaPropertyAPIAdapter(api_url=api_url, api_token=api_token)
    agent = create_property_react_agent(property_adapter=adapter)

    thread_id = f"{user_id}_interactive"
    session_total_tokens = 0
    session_total_cost_usd = 0

    while True:
        try:
            console.print()
            user_input = console.input("[bold green]You:[/bold green] ").strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                print_session_summary(session_total_tokens, session_total_cost_usd)
                console.print("[cyan]Goodbye![/cyan]")
                break

            if user_input.lower() == "clear":
                thread_id = f"{user_id}_interactive_{os.urandom(4).hex()}"
                console.print("[green]Session cleared.[/green]")
                continue

            if not user_input:
                continue

            if verbose:
                # Verbose mode with tree display
                result = asyncio.run(process_streaming_chat(
                    agent, user_input, thread_id, user_id
                ))

                # Show response
                print_response_start()
                print_response(result["response"])

                # Count properties in response
                import re
                response_props = len(re.findall(r'(?:^|\n)\s*(?:\*\*)?(\d+)\.', result["response"]))
                if response_props > 0:
                    console.print(f"\n[dim]Response contains {response_props} numbered items[/dim]")

                # Token summary
                usage = estimate_cost(result["input_tokens"], result["output_tokens"])
                print_token_summary(result["input_tokens"], result["output_tokens"])

                session_total_tokens += usage["total_tokens"]
                session_total_cost_usd += usage["total_usd"]

            else:
                # Simple mode
                with console.status("[cyan]Thinking...[/cyan]", spinner="dots"):
                    response = agent.chat(
                        message=user_input,
                        thread_id=thread_id,
                        user_id=user_id,
                    )

                console.print()
                console.print(Markdown(response))

                # Estimate tokens
                input_tokens = count_tokens(user_input) + 500
                output_tokens = count_tokens(response)
                usage = estimate_cost(input_tokens, output_tokens)

                session_total_tokens += usage["total_tokens"]
                session_total_cost_usd += usage["total_usd"]

                console.print(f"\n[dim]~{usage['total_tokens']:,} tokens | ${usage['total_usd']:.4f}[/dim]")

        except KeyboardInterrupt:
            console.print("\n[cyan]Goodbye![/cyan]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interactive Property Chat")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Show detailed processing with tree display")
    args = parser.parse_args()

    main(verbose=args.verbose)
