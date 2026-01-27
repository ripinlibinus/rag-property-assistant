"""
Token Counting Utilities

Accurate token counting using tiktoken for OpenAI models.
Replaces the inaccurate char/4 heuristic.
"""

from functools import lru_cache
from typing import List, Optional, Union

import tiktoken

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage,
)


# Model to encoding mapping
MODEL_ENCODINGS = {
    "gpt-4o": "o200k_base",
    "gpt-4o-mini": "o200k_base",
    "gpt-4-turbo": "cl100k_base",
    "gpt-4": "cl100k_base",
    "gpt-3.5-turbo": "cl100k_base",
}

# Default encoding for unknown models
DEFAULT_ENCODING = "cl100k_base"


@lru_cache(maxsize=10)
def get_encoding(model: str = "gpt-4o-mini") -> tiktoken.Encoding:
    """
    Get tiktoken encoding for a model.
    
    Uses LRU cache to avoid re-loading encodings.
    
    Args:
        model: Model name (default: gpt-4o-mini)
        
    Returns:
        tiktoken.Encoding instance
    """
    try:
        # Try to get encoding for model directly
        return tiktoken.encoding_for_model(model)
    except KeyError:
        # Fallback to known mapping
        encoding_name = MODEL_ENCODINGS.get(model, DEFAULT_ENCODING)
        return tiktoken.get_encoding(encoding_name)


def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """
    Count tokens in a text string.
    
    Args:
        text: Text to count tokens for
        model: Model to use for encoding (default: gpt-4o-mini)
        
    Returns:
        Number of tokens
    """
    if not text:
        return 0
    
    encoding = get_encoding(model)
    return len(encoding.encode(text))


def count_message_tokens(
    messages: List[BaseMessage],
    model: str = "gpt-4o-mini",
) -> int:
    """
    Count tokens for a list of LangChain messages.
    
    Accounts for message formatting overhead (role tokens, separators).
    
    Args:
        messages: List of LangChain messages
        model: Model to use for encoding
        
    Returns:
        Total token count
    """
    encoding = get_encoding(model)
    
    # Token overhead per message varies by model
    # For gpt-4o/gpt-4o-mini: ~4 tokens per message (role, separators)
    tokens_per_message = 4
    
    total = 0
    
    for msg in messages:
        # Base overhead for message structure
        total += tokens_per_message
        
        # Role token
        if isinstance(msg, SystemMessage):
            total += 1  # "system"
        elif isinstance(msg, HumanMessage):
            total += 1  # "user"
        elif isinstance(msg, AIMessage):
            total += 1  # "assistant"
        elif isinstance(msg, ToolMessage):
            total += 2  # "tool" + name
            
        # Content tokens
        if msg.content:
            total += len(encoding.encode(msg.content))
            
        # Tool calls in AIMessage
        if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                # Tool call structure overhead
                total += 10
                # Tool name and arguments
                total += len(encoding.encode(tc.get("name", "")))
                args = tc.get("args", {})
                if args:
                    import json
                    args_str = json.dumps(args)
                    total += len(encoding.encode(args_str))
    
    # Final overhead for message format
    total += 3  # Every reply is primed with <|start|>assistant<|message|>
    
    return total


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str = "gpt-4o-mini",
    usd_to_idr: float = 17000.0,
) -> dict:
    """
    Estimate cost based on token counts.
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: Model name
        usd_to_idr: USD to IDR exchange rate
        
    Returns:
        Dict with cost breakdown
    """
    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "gpt-4o-mini": {
            "input": 0.15,   # $0.15 per 1M input tokens
            "output": 0.60,  # $0.60 per 1M output tokens
        },
        "gpt-4o": {
            "input": 2.50,   # $2.50 per 1M input tokens
            "output": 10.00, # $10.00 per 1M output tokens
        },
        "gpt-4-turbo": {
            "input": 10.00,
            "output": 30.00,
        },
        "gpt-3.5-turbo": {
            "input": 0.50,
            "output": 1.50,
        },
    }
    
    pricing = PRICING.get(model, PRICING["gpt-4o-mini"])
    
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    total_usd = input_cost + output_cost
    total_idr = total_usd * usd_to_idr
    
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "input_cost_usd": input_cost,
        "output_cost_usd": output_cost,
        "total_usd": total_usd,
        "total_idr": total_idr,
        "model": model,
    }


def truncate_to_token_limit(
    text: str,
    max_tokens: int,
    model: str = "gpt-4o-mini",
) -> str:
    """
    Truncate text to fit within token limit.
    
    Args:
        text: Text to truncate
        max_tokens: Maximum tokens allowed
        model: Model for encoding
        
    Returns:
        Truncated text
    """
    if not text:
        return text
        
    encoding = get_encoding(model)
    tokens = encoding.encode(text)
    
    if len(tokens) <= max_tokens:
        return text
        
    truncated_tokens = tokens[:max_tokens]
    return encoding.decode(truncated_tokens)


def get_context_window_limit(model: str = "gpt-4o-mini") -> int:
    """
    Get context window limit for a model.
    
    Args:
        model: Model name
        
    Returns:
        Context window size in tokens
    """
    CONTEXT_LIMITS = {
        "gpt-4o": 128_000,
        "gpt-4o-mini": 128_000,
        "gpt-4-turbo": 128_000,
        "gpt-4": 8_192,
        "gpt-3.5-turbo": 16_385,
    }
    
    return CONTEXT_LIMITS.get(model, 8_192)
