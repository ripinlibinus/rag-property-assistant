"""
Metrics Collection for RAG-Tesis

Track search performance, tool execution, and other metrics for thesis analysis.
Outputs metrics to JSONL format for easy analysis with pandas.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import threading
import time

import structlog

logger = structlog.get_logger()


class SearchMethod(Enum):
    """Search method types for A/B testing"""
    API_ONLY = "api_only"
    CHROMADB_ONLY = "chromadb_only"
    HYBRID = "hybrid"
    HYBRID_60_40 = "hybrid_60_40"
    HYBRID_70_30 = "hybrid_70_30"
    HYBRID_80_20 = "hybrid_80_20"


@dataclass
class SearchMetrics:
    """Metrics for a single search operation"""
    
    # Identifiers
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    user_id: str = "anonymous"
    thread_id: str = ""
    query_id: str = ""
    
    # Query info
    query: str = ""
    query_tokens: int = 0
    
    # Search method
    method: str = "hybrid"  # api_only, chromadb_only, hybrid
    
    # API search results
    api_results_count: int = 0
    api_latency_ms: float = 0.0
    
    # ChromaDB search results  
    chromadb_results_count: int = 0
    chromadb_latency_ms: float = 0.0
    
    # Combined/final results
    final_results_count: int = 0
    total_latency_ms: float = 0.0
    
    # Re-ranking metrics
    reranking_applied: bool = False
    reranking_changes: int = 0  # How many positions changed
    reranking_latency_ms: float = 0.0
    
    # Token usage
    embedding_tokens: int = 0
    llm_input_tokens: int = 0
    llm_output_tokens: int = 0
    total_tokens: int = 0
    
    # Cache hits
    embedding_cache_hit: bool = False
    
    # Quality indicators (can be filled later via evaluation)
    relevance_score: Optional[float] = None
    user_feedback: Optional[str] = None  # thumbs_up, thumbs_down, none
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert None to null-friendly format
        return {k: v for k, v in data.items()}
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False)


@dataclass
class ToolMetrics:
    """Metrics for tool execution"""
    
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    user_id: str = "anonymous"
    thread_id: str = ""
    
    # Tool info
    tool_name: str = ""
    tool_args: Dict[str, Any] = field(default_factory=dict)
    
    # Execution
    success: bool = True
    error_message: str = ""
    latency_ms: float = 0.0
    
    # Results
    result_size_chars: int = 0
    result_count: int = 0  # For list results
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


@dataclass
class ConversationMetrics:
    """Metrics for conversation/session"""
    
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    user_id: str = "anonymous"
    thread_id: str = ""
    
    # Conversation stats
    message_count: int = 0
    total_turns: int = 0
    
    # Token totals
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_tokens: int = 0
    
    # Tool usage
    tools_used: List[str] = field(default_factory=list)
    tool_calls_count: int = 0
    
    # Duration
    session_duration_seconds: float = 0.0
    
    # Outcome
    completed_successfully: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


class MetricsCollector:
    """
    Collect and persist metrics for analysis.
    
    Thread-safe, writes to JSONL files.
    """
    
    def __init__(
        self,
        output_dir: str = "data/metrics",
        enabled: bool = True,
    ):
        """
        Initialize metrics collector.
        
        Args:
            output_dir: Directory to store metrics files
            enabled: Whether to actually write metrics (can disable for tests)
        """
        self.output_dir = Path(output_dir)
        self.enabled = enabled
        self._lock = threading.Lock()
        
        # Create output directory
        if self.enabled:
            self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, metric_type: str) -> Path:
        """Get output file path for a metric type with date-based rotation"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return self.output_dir / f"{metric_type}_{date_str}.jsonl"
    
    def _write_line(self, metric_type: str, data: str):
        """Thread-safe write of a metric line"""
        if not self.enabled:
            return
        
        file_path = self._get_file_path(metric_type)
        
        with self._lock:
            try:
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(data + "\n")
            except Exception as e:
                logger.error("metrics_write_error", error=str(e), metric_type=metric_type)
    
    def log_search(self, metrics: SearchMetrics):
        """Log search metrics"""
        self._write_line("search", metrics.to_json())
        
        logger.debug(
            "search_metrics_logged",
            query=metrics.query[:50],
            method=metrics.method,
            results=metrics.final_results_count,
            latency_ms=metrics.total_latency_ms,
        )
    
    def log_tool(self, metrics: ToolMetrics):
        """Log tool execution metrics"""
        self._write_line("tool", metrics.to_json())
        
        logger.debug(
            "tool_metrics_logged",
            tool=metrics.tool_name,
            success=metrics.success,
            latency_ms=metrics.latency_ms,
        )
    
    def log_conversation(self, metrics: ConversationMetrics):
        """Log conversation/session metrics"""
        self._write_line("conversation", metrics.to_json())
        
        logger.debug(
            "conversation_metrics_logged",
            thread_id=metrics.thread_id,
            turns=metrics.total_turns,
            tokens=metrics.total_tokens,
        )


class Timer:
    """Context manager for timing operations"""
    
    def __init__(self):
        self.start_time: float = 0
        self.end_time: float = 0
        self.elapsed_ms: float = 0
    
    def __enter__(self) -> "Timer":
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        self.end_time = time.perf_counter()
        self.elapsed_ms = (self.end_time - self.start_time) * 1000


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create global metrics collector"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def set_metrics_collector(collector: MetricsCollector):
    """Set custom metrics collector (for testing)"""
    global _metrics_collector
    _metrics_collector = collector
