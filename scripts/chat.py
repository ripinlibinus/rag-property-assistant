"""
Interactive Chat with ReAct Agent
Tree-style display with streaming
"""

import os
import sys

# Disable ChromaDB telemetry BEFORE any imports
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import io
import time
import asyncio
import argparse
import logging
from pathlib import Path

# Suppress ALL logs for clean CLI experience
logging.disable(logging.INFO)  # Disable INFO and below globally
logging.getLogger().setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("httpcore").setLevel(logging.ERROR)
logging.getLogger("chromadb").setLevel(logging.ERROR)
logging.getLogger("chromadb.telemetry").setLevel(logging.ERROR)
logging.getLogger("chromadb.config").setLevel(logging.ERROR)
logging.getLogger("rag.agent").setLevel(logging.ERROR)
logging.getLogger("src").setLevel(logging.ERROR)
logging.getLogger("openai").setLevel(logging.ERROR)
logging.getLogger("langchain").setLevel(logging.ERROR)

# Also suppress structlog if used
try:
    import structlog
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.CRITICAL),
        processors=[structlog.dev.ConsoleRenderer()],
        logger_factory=structlog.PrintLoggerFactory(file=io.StringIO()),
    )
except ImportError:
    pass

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
    console.print("[bold cyan]🏠 Property Assistant[/bold cyan] [dim]CLI v2.0[/dim]")
    console.print("[dim]'quit' to exit • 'clear' to reset[/dim]")
    console.print()


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


def print_user_input(query: str):
    """Print user input - skip, already shown in prompt"""
    pass


def print_reasoning(content: str, is_streaming: bool = False):
    """Print LLM reasoning in a nice box"""
    console.print()
    console.print("[dim]╭─ 🧠 Thinking ─────────────────────────────────────────────[/dim]")

    # Parse and display reasoning content
    lines = content.strip().split('\n')
    for line in lines:
        if line.strip():
            # Clean up markdown
            line = line.replace('**', '')
            # Truncate long lines
            if len(line) > 70:
                line = line[:67] + "..."
            console.print(f"[dim]│[/dim] [italic dim]{line}[/italic dim]")

    console.print("[dim]╰───────────────────────────────────────────────────────────[/dim]")


def print_tool_call(tool_name: str, args: dict):
    """Print tool call in a nice format"""
    # Format args nicely
    if args:
        args_parts = []
        for k, v in args.items():
            if isinstance(v, str) and len(v) > 30:
                v = v[:27] + "..."
            args_parts.append(f"[white]{k}[/white]=[cyan]{repr(v)}[/cyan]")
        args_str = ", ".join(args_parts)
    else:
        args_str = ""

    console.print()
    console.print(f"[bold blue]⚡ Tool:[/bold blue] [bold cyan]{tool_name}[/bold cyan]({args_str})")


def print_tool_result(content: str, lines_to_show: int = 5):
    """Print tool result summary"""
    import re

    lines = content.split('\n')
    total_lines = len(lines)

    # Count properties from result
    prop_count = 0
    prop_match = re.search(r'Ditemukan\s+(\d+)\s+properti', content)
    if not prop_match:
        prop_match = re.search(r'Found\s+(\d+)\s+propert', content)
    if prop_match:
        prop_count = int(prop_match.group(1))
    else:
        # Count numbered items
        prop_count = len(re.findall(r'^\d+\.', content, re.MULTILINE))

    # Show result summary
    if prop_count > 0:
        console.print(f"   [green]✓ Found {prop_count} properties[/green]")
    elif "tidak ditemukan" in content.lower() or "no properties" in content.lower():
        console.print(f"   [yellow]⚠ No properties found[/yellow]")
    else:
        console.print(f"   [dim]✓ Got result ({total_lines} lines)[/dim]")


def print_response_start():
    """Print response section start"""
    console.print()
    console.print("[bold green]💬 Assistant:[/bold green]")
    console.print("[dim]─────────────────────────────────────────────────────────────[/dim]")


def print_response(content: str, stream: bool = False):
    """Print the assistant response"""
    console.print(Markdown(content))
    console.print("[dim]─────────────────────────────────────────────────────────────[/dim]")


def print_token_summary(input_tokens: int, output_tokens: int):
    """Print token usage summary in one line"""
    usage = estimate_cost(input_tokens, output_tokens)
    console.print(
        f"[dim]📊 Tokens: {usage['total_tokens']:,} • "
        f"Cost: ${usage['total_usd']:.4f} (Rp {usage['total_idr']:,.0f})[/dim]"
    )


def print_session_summary(total_tokens: int, total_cost_usd: float):
    """Print session summary"""
    console.print()
    console.print("[dim]╭─ 📈 Session Summary ──────────────────────────────────────[/dim]")
    console.print(f"[dim]│[/dim]  Total tokens: [bold]{total_tokens:,}[/bold]")
    console.print(f"[dim]│[/dim]  Total cost: [yellow]${total_cost_usd:.6f}[/yellow] (Rp {total_cost_usd * USD_TO_IDR:,.0f})")
    console.print("[dim]╰───────────────────────────────────────────────────────────[/dim]")


# ============================================================================
# Async Streaming Chat Handler
# ============================================================================

async def process_streaming_chat(agent, user_input: str, thread_id: str, user_id: str):
    """Process chat with nice loading effects"""
    from rich.live import Live
    from rich.spinner import Spinner
    from rich.text import Text

    reasoning_buffer = ""
    response_buffer = ""
    input_tokens = 0
    output_tokens = 0

    # State tracking
    shown_reasoning = False
    current_spinner = None
    live_display = None

    input_tokens += count_tokens(user_input)

    # Start with thinking spinner
    console.print()
    live_display = Live(
        Spinner("dots", text="[cyan] Thinking...[/cyan]"),
        console=console,
        refresh_per_second=10
    )
    live_display.start()

    try:
        async for event in agent.astream_chat_tokens(user_input, thread_id=thread_id, user_id=user_id):
            event_type = event.get("type")

            # Skip user_input event
            if event_type == "user_input":
                continue

            # Reasoning token - buffer it
            elif event_type == "reasoning_token":
                reasoning_buffer += event["content"]
                output_tokens += 1
                # Update spinner text
                if live_display:
                    preview = reasoning_buffer[-50:].replace('\n', ' ').strip()
                    if len(preview) > 40:
                        preview = "..." + preview[-40:]
                    live_display.update(Spinner("dots", text=f"[cyan] Thinking: [dim]{preview}[/dim][/cyan]"))

            # Reasoning done - show it
            elif event_type == "reasoning_done":
                if live_display:
                    live_display.stop()
                    live_display = None
                if reasoning_buffer and not shown_reasoning:
                    print_reasoning(reasoning_buffer)
                    shown_reasoning = True

            # Tool call
            elif event_type == "tool_call":
                # Stop any spinner first
                if live_display:
                    live_display.stop()
                    live_display = None

                # Show reasoning if not yet shown
                if reasoning_buffer and not shown_reasoning:
                    print_reasoning(reasoning_buffer)
                    shown_reasoning = True
                    reasoning_buffer = ""

                # Show tool call
                print_tool_call(event["name"], event["args"])

                # Start spinner for tool execution
                live_display = Live(
                    Spinner("dots", text=f"[blue] Executing {event['name']}...[/blue]"),
                    console=console,
                    refresh_per_second=10
                )
                live_display.start()

            # Tool result
            elif event_type == "tool_result":
                if live_display:
                    live_display.stop()
                    live_display = None
                print_tool_result(event["content"])
                input_tokens += count_tokens(event["content"])
                reasoning_buffer = ""
                shown_reasoning = False  # Reset for next reasoning

                # Start thinking spinner again
                live_display = Live(
                    Spinner("dots", text="[cyan] Thinking...[/cyan]"),
                    console=console,
                    refresh_per_second=10
                )
                live_display.start()

            # Response done
            elif event_type == "response_done":
                if live_display:
                    live_display.stop()
                    live_display = None
                response_buffer = event["content"]
                output_tokens = count_tokens(response_buffer)

            # Done
            elif event_type == "done":
                if live_display:
                    live_display.stop()
                    live_display = None
                break

    except Exception as e:
        if live_display:
            live_display.stop()
        console.print(f"[red]Error: {e}[/red]")
        raise e
    finally:
        if live_display:
            live_display.stop()

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

    # Suppress ALL logging before imports
    import logging
    logging.disable(logging.CRITICAL)  # Disable all logging

    # Reconfigure structlog to be completely silent
    import structlog
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.CRITICAL),
        processors=[structlog.dev.ConsoleRenderer()],
        logger_factory=structlog.PrintLoggerFactory(file=io.StringIO()),
    )

    # Print header first
    print_header()

    # Show loading spinner while importing heavy modules
    with console.status("[cyan]Loading agent...[/cyan]", spinner="dots"):
        from src.adapters.metaproperty import MetaPropertyAPIAdapter
        from src.agents.react_agent import create_property_react_agent

    api_url = os.getenv("METAPROPERTY_API_URL", "http://localhost:8000")
    api_token = os.getenv("METAPROPERTY_API_TOKEN", "")

    # Create agent with loading spinner
    with console.status("[cyan]Initializing knowledge base...[/cyan]", spinner="dots"):
        adapter = MetaPropertyAPIAdapter(api_url=api_url, api_token=api_token)
        agent = create_property_react_agent(property_adapter=adapter)

    console.print("[green]✓[/green] Ready!")
    console.print()

    # Simple user session
    user_id = "user"

    thread_id = f"{user_id}_interactive"
    session_total_tokens = 0
    session_total_cost_usd = 0

    while True:
        try:
            user_input = console.input("\n[bold green]You:[/bold green] ").strip()

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
                # Verbose mode - show reasoning process
                result = asyncio.run(process_streaming_chat(
                    agent, user_input, thread_id, user_id
                ))

                # Show response
                print_response_start()
                print_response(result["response"])

                # Token summary
                usage = estimate_cost(result["input_tokens"], result["output_tokens"])
                print_token_summary(result["input_tokens"], result["output_tokens"])

                session_total_tokens += usage["total_tokens"]
                session_total_cost_usd += usage["total_usd"]

            else:
                # Simple mode - no reasoning display
                with console.status("[cyan]🤔 Thinking...[/cyan]", spinner="dots"):
                    response = agent.chat(
                        message=user_input,
                        thread_id=thread_id,
                        user_id=user_id,
                    )

                console.print()
                console.print("[bold green]💬 Assistant:[/bold green]")
                console.print("[dim]─────────────────────────────────────────────────────────────[/dim]")
                console.print(Markdown(response))
                console.print("[dim]─────────────────────────────────────────────────────────────[/dim]")

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
    parser.add_argument("-s", "--simple", action="store_true",
                        help="Simple mode without reasoning display")
    args = parser.parse_args()

    # Default: show reasoning (verbose). Use -s for simple mode
    main(verbose=not args.simple)
