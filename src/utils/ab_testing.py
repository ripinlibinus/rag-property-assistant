"""
A/B Testing Framework for RAG-Tesis

Compare different search methods for thesis analysis:
- API only
- ChromaDB only  
- Hybrid with various weight configurations

Supports:
- Random assignment with configurable weights
- Consistent assignment per user (hash-based)
- Manual override for testing
"""

import hashlib
import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List

import structlog

logger = structlog.get_logger()


class SearchMethod(Enum):
    """Available search methods for A/B testing"""
    API_ONLY = "api_only"
    CHROMADB_ONLY = "chromadb_only"
    HYBRID = "hybrid"  # Default 60/40 weight
    HYBRID_50_50 = "hybrid_50_50"
    HYBRID_60_40 = "hybrid_60_40"
    HYBRID_70_30 = "hybrid_70_30"
    HYBRID_80_20 = "hybrid_80_20"
    
    @property
    def semantic_weight(self) -> float:
        """Get semantic weight for this method"""
        weights = {
            SearchMethod.API_ONLY: 0.0,
            SearchMethod.CHROMADB_ONLY: 1.0,
            SearchMethod.HYBRID: 0.6,
            SearchMethod.HYBRID_50_50: 0.5,
            SearchMethod.HYBRID_60_40: 0.6,
            SearchMethod.HYBRID_70_30: 0.7,
            SearchMethod.HYBRID_80_20: 0.8,
        }
        return weights.get(self, 0.6)
    
    @property
    def use_semantic_rerank(self) -> bool:
        """Whether to use semantic re-ranking"""
        return self != SearchMethod.API_ONLY
    
    @property
    def use_api_search(self) -> bool:
        """Whether to use API search"""
        return self != SearchMethod.CHROMADB_ONLY


@dataclass
class ABTestConfig:
    """Configuration for A/B test"""
    name: str
    description: str
    start_date: str
    end_date: Optional[str] = None
    
    # Method weights for random assignment (must sum to 1.0)
    method_weights: Dict[SearchMethod, float] = field(default_factory=lambda: {
        SearchMethod.HYBRID_60_40: 1.0,  # Default: 100% hybrid
    })
    
    # Whether to use consistent assignment per user
    consistent_per_user: bool = True
    
    # Enabled flag
    enabled: bool = True


class ABTestManager:
    """
    Manage A/B testing for search methods.
    
    Usage:
        ab_manager = ABTestManager()
        
        # Get method for a user
        method = ab_manager.get_method(user_id="user123")
        
        # Use in search
        result = await hybrid_service.search(
            ...,
            use_semantic_rerank=method.use_semantic_rerank,
            semantic_weight=method.semantic_weight,
        )
    """
    
    def __init__(
        self,
        config: Optional[ABTestConfig] = None,
        default_method: SearchMethod = SearchMethod.HYBRID_60_40,
    ):
        """
        Initialize A/B test manager.
        
        Args:
            config: A/B test configuration
            default_method: Default method when no config or test disabled
        """
        self.config = config
        self.default_method = default_method
        self._override_method: Optional[SearchMethod] = None
    
    def set_override(self, method: Optional[SearchMethod]):
        """
        Set manual override for testing.
        
        Args:
            method: Method to use, or None to clear override
        """
        self._override_method = method
        logger.info("ab_test_override_set", method=method.value if method else None)
    
    def clear_override(self):
        """Clear manual override"""
        self._override_method = None
    
    def get_method(self, user_id: Optional[str] = None) -> SearchMethod:
        """
        Get search method for a request.
        
        Args:
            user_id: User ID for consistent assignment
            
        Returns:
            SearchMethod to use for this request
        """
        # Check for manual override
        if self._override_method is not None:
            return self._override_method
        
        # Check if config exists and is enabled
        if not self.config or not self.config.enabled:
            return self.default_method
        
        # Check date range
        now = datetime.now().strftime("%Y-%m-%d")
        if self.config.start_date > now:
            return self.default_method
        if self.config.end_date and self.config.end_date < now:
            return self.default_method
        
        # Get method based on assignment strategy
        if self.config.consistent_per_user and user_id:
            return self._get_consistent_method(user_id)
        else:
            return self._get_random_method()
    
    def _get_consistent_method(self, user_id: str) -> SearchMethod:
        """
        Get consistent method based on user ID hash.
        
        Same user always gets same method during the test.
        """
        # Create hash of user_id
        hash_bytes = hashlib.md5(user_id.encode()).digest()
        hash_val = int.from_bytes(hash_bytes[:4], 'big') % 1000
        
        # Assign based on cumulative weights
        cumulative = 0.0
        threshold = hash_val / 1000.0
        
        for method, weight in self.config.method_weights.items():
            cumulative += weight
            if threshold < cumulative:
                logger.debug(
                    "ab_test_assignment",
                    user_id=user_id,
                    method=method.value,
                    hash_val=hash_val,
                    assignment_type="consistent",
                )
                return method
        
        # Fallback to first method
        return list(self.config.method_weights.keys())[0]
    
    def _get_random_method(self) -> SearchMethod:
        """Get random method based on weights."""
        methods = list(self.config.method_weights.keys())
        weights = list(self.config.method_weights.values())
        
        selected = random.choices(methods, weights=weights, k=1)[0]
        
        logger.debug(
            "ab_test_assignment",
            method=selected.value,
            assignment_type="random",
        )
        
        return selected
    
    def get_stats(self) -> Dict:
        """Get current A/B test status."""
        return {
            "config_name": self.config.name if self.config else None,
            "enabled": self.config.enabled if self.config else False,
            "override": self._override_method.value if self._override_method else None,
            "default_method": self.default_method.value,
            "method_weights": {
                m.value: w 
                for m, w in self.config.method_weights.items()
            } if self.config else {},
        }


# =============================================================================
# Preset Configurations
# =============================================================================

def create_baseline_test() -> ABTestConfig:
    """Create baseline A/B test: 100% hybrid (for collecting baseline metrics)"""
    return ABTestConfig(
        name="baseline",
        description="Baseline metrics collection - 100% hybrid search",
        start_date="2026-01-01",
        method_weights={
            SearchMethod.HYBRID_60_40: 1.0,
        },
        consistent_per_user=False,
        enabled=True,
    )


def create_comparison_test() -> ABTestConfig:
    """Create comparison A/B test: Compare API vs Hybrid vs ChromaDB"""
    return ABTestConfig(
        name="method_comparison",
        description="Compare all search methods equally",
        start_date="2026-01-01",
        method_weights={
            SearchMethod.API_ONLY: 0.33,
            SearchMethod.HYBRID_60_40: 0.34,
            SearchMethod.CHROMADB_ONLY: 0.33,
        },
        consistent_per_user=True,
        enabled=True,
    )


def create_hybrid_weight_test() -> ABTestConfig:
    """Create A/B test comparing different hybrid weights"""
    return ABTestConfig(
        name="hybrid_weight_comparison",
        description="Compare hybrid search with different semantic weights",
        start_date="2026-01-01",
        method_weights={
            SearchMethod.HYBRID_50_50: 0.25,
            SearchMethod.HYBRID_60_40: 0.25,
            SearchMethod.HYBRID_70_30: 0.25,
            SearchMethod.HYBRID_80_20: 0.25,
        },
        consistent_per_user=True,
        enabled=True,
    )


# =============================================================================
# Global A/B Test Manager Instance
# =============================================================================

_ab_manager: Optional[ABTestManager] = None


def get_ab_manager() -> ABTestManager:
    """Get or create global A/B test manager"""
    global _ab_manager
    if _ab_manager is None:
        # Default: baseline test (100% hybrid)
        _ab_manager = ABTestManager(
            config=create_baseline_test(),
            default_method=SearchMethod.HYBRID_60_40,
        )
    return _ab_manager


def set_ab_manager(manager: ABTestManager):
    """Set custom A/B test manager"""
    global _ab_manager
    _ab_manager = manager


def configure_ab_test(test_type: str = "baseline") -> ABTestManager:
    """
    Configure A/B testing with a preset.
    
    Args:
        test_type: One of "baseline", "comparison", "hybrid_weights"
        
    Returns:
        Configured ABTestManager
    """
    configs = {
        "baseline": create_baseline_test,
        "comparison": create_comparison_test,
        "hybrid_weights": create_hybrid_weight_test,
    }
    
    config_factory = configs.get(test_type, create_baseline_test)
    manager = ABTestManager(config=config_factory())
    set_ab_manager(manager)
    
    logger.info("ab_test_configured", test_type=test_type, config=manager.get_stats())
    
    return manager
