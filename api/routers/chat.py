"""
Chat Router - Main chat endpoint for property search
"""
import re
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse

from ..schemas import ChatRequest, ChatResponse, PropertySummary, SearchMetadata
from ..dependencies import get_agent
from src.utils.ab_testing import SearchMethod

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = logging.getLogger(__name__)


def format_price(price: int) -> str:
    """Format price to Indonesian format (M for million, T for trillion)"""
    if price >= 1_000_000_000_000:
        return f"Rp {price / 1_000_000_000_000:.1f} T"
    elif price >= 1_000_000_000:
        return f"Rp {price / 1_000_000_000:.1f} M"
    elif price >= 1_000_000:
        return f"Rp {price / 1_000_000:.0f} Jt"
    else:
        return f"Rp {price:,}".replace(",", ".")


def extract_properties_from_response(response: str) -> list:
    """
    Extract property IDs mentioned in the response.
    This is a simple extraction - in production you might want
    to parse the actual tool results.
    """
    # This is a placeholder - actual implementation would
    # track properties from tool calls during agent execution
    return []


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, agent=Depends(get_agent)):
    """
    Main chat endpoint for property search assistant.

    The assistant uses a ReAct agent to:
    1. Understand user intent
    2. Search properties using appropriate tools
    3. Generate natural language response

    Supports multiple search methods:
    - hybrid: API filtering + semantic re-ranking (recommended)
    - api_only: Only API filtering
    - vector_only: Only ChromaDB semantic search
    """
    try:
        # Map method string to SearchMethod enum for A/B testing
        method_map = {
            "hybrid": SearchMethod.HYBRID,
            "api_only": SearchMethod.API_ONLY,
            "vector_only": SearchMethod.CHROMADB_ONLY,
        }
        ab_method = method_map.get(request.method, SearchMethod.HYBRID)

        # Set the method for this request
        from src.utils.ab_testing import get_ab_manager
        ab_manager = get_ab_manager()

        # Set override to use the requested method
        ab_manager.set_override(ab_method)

        try:
            # Call the agent
            response = agent.chat(
                message=request.message,
                thread_id=request.session_id,
                user_id=request.user_id,
            )
        finally:
            # Clear override after request
            ab_manager.clear_override()

        # For now, we return the response without parsing properties
        # In a more sophisticated implementation, we would track
        # tool results during execution
        return ChatResponse(
            response=response,
            properties=[],  # TODO: Extract from tool results
            session_id=request.session_id,
            metadata=SearchMetadata(
                total_found=0,
                returned=0,
                method_used=request.method,
                has_more=False,
            ),
        )

    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat request: {str(e)}",
        )


@router.post("/stream")
async def chat_stream(request: ChatRequest, agent=Depends(get_agent)):
    """
    Streaming chat endpoint for real-time responses.

    Returns Server-Sent Events (SSE) with:
    - user_input: Echo of user message
    - reasoning_token: Tokens as agent thinks
    - tool_call: When agent calls a tool
    - tool_result: Result from tool execution
    - response_token: Final response tokens
    - done: Stream complete
    """
    import json
    from src.utils.ab_testing import get_ab_manager

    # Map method string to SearchMethod enum
    method_map = {
        "hybrid": SearchMethod.HYBRID,
        "api_only": SearchMethod.API_ONLY,
        "vector_only": SearchMethod.CHROMADB_ONLY,
    }
    ab_method = method_map.get(request.method, SearchMethod.HYBRID)

    # Set override for this request
    ab_manager = get_ab_manager()
    ab_manager.set_override(ab_method)

    async def generate():
        try:
            async for event in agent.astream_chat_tokens(
                message=request.message,
                thread_id=request.session_id,
                user_id=request.user_id,
            ):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            logger.error(f"Stream error: {str(e)}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        finally:
            # Clear override after streaming completes
            ab_manager.clear_override()

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
