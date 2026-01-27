"""Utils module - Shared utilities and helpers"""

from .logging import (
    configure_logging,
    get_logger,
    get_search_logger,
    get_agent_logger,
    get_api_logger,
)

from .geocoding import (
    geocode_location_async,
    geocode_location_sync,
    get_cached_geocode,
    set_geocode_cache,
    get_geocode_cache_stats,
    clear_geocode_cache,
    KNOWN_LOCATIONS,
)

__all__ = [
    "configure_logging",
    "get_logger",
    "get_search_logger",
    "get_agent_logger",
    "get_api_logger",
    # Geocoding
    "geocode_location_async",
    "geocode_location_sync",
    "get_cached_geocode",
    "set_geocode_cache",
    "get_geocode_cache_stats",
    "clear_geocode_cache",
    "KNOWN_LOCATIONS",
]
