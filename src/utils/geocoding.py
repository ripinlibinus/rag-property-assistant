"""
Geocoding Service with Caching

Provides geocoding functionality with:
- TTL cache for API results (24 hours)
- Pre-populated known locations for Medan area
- Google Maps API with Nominatim fallback
"""

import os
from typing import Optional, Tuple, Dict
from cachetools import TTLCache
import httpx

from .logging import get_agent_logger

logger = get_agent_logger()

# Cache geocoding results for 24 hours, max 500 locations
_geocode_cache: TTLCache = TTLCache(maxsize=500, ttl=86400)

# Pre-populated cache for common Medan locations
# These are locations that may not match text search but are commonly searched
KNOWN_LOCATIONS: Dict[str, Tuple[float, float]] = {
    # Industrial areas
    "kim": (3.6693658, 98.6904473),
    "kawasan industri medan": (3.6693658, 98.6904473),
    "kawasan industri": (3.6693658, 98.6904473),
    "mabar": (3.6847, 98.6833),

    # Universities
    "usu": (3.5656, 98.6565),
    "universitas sumatera utara": (3.5656, 98.6565),
    "kampus usu": (3.5656, 98.6565),
    "unimed": (3.6089, 98.6833),
    "universitas negeri medan": (3.6089, 98.6833),
    "uinsu": (3.6167, 98.6833),
    "uin sumatera utara": (3.6167, 98.6833),
    "umsu": (3.5833, 98.6667),
    "unika": (3.5656, 98.6333),
    "universitas katolik": (3.5656, 98.6333),
    "unpri": (3.5833, 98.6500),
    "mikroskil": (3.5833, 98.6667),

    # Malls
    "sun plaza": (3.5833, 98.6667),
    "sunplaza": (3.5833, 98.6667),
    "centre point": (3.5833, 98.6833),
    "centerpoint": (3.5833, 98.6833),
    "delipark": (3.5939, 98.6742),
    "deli park": (3.5939, 98.6742),
    "podomoro city deli": (3.5939, 98.6742),
    "cambridge": (3.6847, 98.6453),
    "manhattan": (3.5833, 98.6500),
    "plaza medan fair": (3.5833, 98.6500),
    "medan fair": (3.5833, 98.6500),
    "grand palladium": (3.5667, 98.6833),
    "focal point": (3.5667, 98.6833),
    "lippo plaza": (3.5656, 98.6333),
    "hermes palace": (3.5833, 98.6667),

    # Hospitals
    "rs adam malik": (3.5833, 98.6500),
    "adam malik": (3.5833, 98.6500),
    "rs columbia asia": (3.5833, 98.6667),
    "columbia asia": (3.5833, 98.6667),
    "rs elisabeth": (3.5833, 98.6833),
    "elisabeth": (3.5833, 98.6833),
    "rs murni teguh": (3.5656, 98.6167),
    "murni teguh": (3.5656, 98.6167),
    "rs royal prima": (3.6847, 98.6453),
    "royal prima": (3.6847, 98.6453),
    "rs pirngadi": (3.5833, 98.6667),
    "pirngadi": (3.5833, 98.6667),
    "rs hermina": (3.5656, 98.6565),
    "hermina": (3.5656, 98.6565),
    "rs siloam": (3.5833, 98.6667),
    "siloam": (3.5833, 98.6667),

    # Schools
    "sutomo": (3.5833, 98.6833),
    "sekolah sutomo": (3.5833, 98.6833),
    "methodist": (3.5833, 98.6667),
    "al azhar": (3.6167, 98.6500),
    "binus school": (3.5656, 98.6333),

    # City centers
    "pusat kota medan": (3.5952, 98.6722),
    "inti kota medan": (3.5952, 98.6722),
    "pusat kota": (3.5952, 98.6722),
    "inti kota": (3.5952, 98.6722),

    # Transport hubs
    "bandara kualanamu": (3.6422, 98.8853),
    "kualanamu": (3.6422, 98.8853),
    "stasiun medan": (3.5833, 98.6667),
    "terminal amplas": (3.5500, 98.6833),
    "terminal pinang baris": (3.5656, 98.6167),

    # Residential areas that might not be in DB exactly
    "cemara asri": (3.6289, 98.6960),
    "givency one": (3.6089, 98.6171),
    "givency": (3.6089, 98.6171),
    "citraland bagya city": (3.6130, 98.7291),
    "citraland": (3.6130, 98.7291),
    "bagya city": (3.6130, 98.7291),
}


def get_cached_geocode(location: str) -> Optional[Tuple[float, float]]:
    """
    Get geocode from cache or known locations.

    Args:
        location: Location name to look up

    Returns:
        Tuple of (latitude, longitude) or None if not found
    """
    location_lower = location.lower().strip()

    # Check known locations first
    if location_lower in KNOWN_LOCATIONS:
        return KNOWN_LOCATIONS[location_lower]

    # Check runtime cache
    if location_lower in _geocode_cache:
        return _geocode_cache[location_lower]

    return None


def set_geocode_cache(location: str, lat: float, lng: float) -> None:
    """
    Store geocode result in runtime cache.

    Args:
        location: Location name
        lat: Latitude
        lng: Longitude
    """
    _geocode_cache[location.lower().strip()] = (lat, lng)


async def geocode_location_async(
    location: str,
    default_city: str = "Medan"
) -> Optional[Tuple[float, float]]:
    """
    Geocode a location name to coordinates (async version).

    Tries in order:
    1. Known locations cache
    2. Runtime cache
    3. Google Maps API
    4. Nominatim (OpenStreetMap)

    Args:
        location: Location name to geocode
        default_city: Default city to append if not in location

    Returns:
        Tuple of (latitude, longitude) or None if not found
    """
    # Check cache first
    cached = get_cached_geocode(location)
    if cached:
        logger.debug("geocode_cache_hit", location=location)
        return cached

    # Build search query with city context
    search_query = location
    location_lower = location.lower()
    if default_city.lower() not in location_lower and "indonesia" not in location_lower:
        search_query = f"{location}, {default_city}, Indonesia"

    # Try Google Maps API first
    google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    if google_api_key:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    "https://maps.googleapis.com/maps/api/geocode/json",
                    params={
                        "address": search_query,
                        "key": google_api_key,
                        "language": "id",
                        "region": "id",
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "OK" and data.get("results"):
                        loc = data["results"][0]["geometry"]["location"]
                        result = (loc["lat"], loc["lng"])
                        set_geocode_cache(location, *result)
                        logger.info(
                            "geocode_google_success",
                            location=location,
                            lat=result[0],
                            lng=result[1]
                        )
                        return result
                    elif data.get("status") == "ZERO_RESULTS":
                        logger.debug("geocode_google_no_results", location=location)
        except Exception as e:
            logger.warning("geocode_google_error", location=location, error=str(e))

    # Fallback to Nominatim (free, no API key)
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": search_query,
                    "format": "json",
                    "limit": 1,
                },
                headers={"User-Agent": "MetaPropertyBot/1.0 (property search assistant)"}
            )
            if response.status_code == 200:
                data = response.json()
                if data:
                    result = (float(data[0]["lat"]), float(data[0]["lon"]))
                    set_geocode_cache(location, *result)
                    logger.info(
                        "geocode_nominatim_success",
                        location=location,
                        lat=result[0],
                        lng=result[1]
                    )
                    return result
    except Exception as e:
        logger.warning("geocode_nominatim_error", location=location, error=str(e))

    logger.warning("geocode_failed", location=location)
    return None


def geocode_location_sync(
    location: str,
    default_city: str = "Medan"
) -> Optional[Tuple[float, float]]:
    """
    Geocode a location name to coordinates (sync version).

    Uses httpx sync client. For async contexts, use geocode_location_async.

    Args:
        location: Location name to geocode
        default_city: Default city to append if not in location

    Returns:
        Tuple of (latitude, longitude) or None if not found
    """
    # Check cache first
    cached = get_cached_geocode(location)
    if cached:
        return cached

    # Build search query with city context
    search_query = location
    location_lower = location.lower()
    if default_city.lower() not in location_lower and "indonesia" not in location_lower:
        search_query = f"{location}, {default_city}, Indonesia"

    # Try Google Maps API first
    google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    if google_api_key:
        try:
            with httpx.Client(timeout=10) as client:
                response = client.get(
                    "https://maps.googleapis.com/maps/api/geocode/json",
                    params={
                        "address": search_query,
                        "key": google_api_key,
                        "language": "id",
                        "region": "id",
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "OK" and data.get("results"):
                        loc = data["results"][0]["geometry"]["location"]
                        result = (loc["lat"], loc["lng"])
                        set_geocode_cache(location, *result)
                        return result
        except Exception:
            pass

    # Fallback to Nominatim
    try:
        with httpx.Client(timeout=10) as client:
            response = client.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": search_query,
                    "format": "json",
                    "limit": 1,
                },
                headers={"User-Agent": "MetaPropertyBot/1.0"}
            )
            if response.status_code == 200:
                data = response.json()
                if data:
                    result = (float(data[0]["lat"]), float(data[0]["lon"]))
                    set_geocode_cache(location, *result)
                    return result
    except Exception:
        pass

    return None


def get_geocode_cache_stats() -> dict:
    """
    Get cache statistics for monitoring.

    Returns:
        Dictionary with cache stats
    """
    return {
        "runtime_cache_size": len(_geocode_cache),
        "known_locations_count": len(KNOWN_LOCATIONS),
        "cache_maxsize": _geocode_cache.maxsize,
        "cache_ttl_seconds": _geocode_cache.ttl,
    }


def clear_geocode_cache() -> None:
    """Clear the runtime geocode cache (not known locations)."""
    _geocode_cache.clear()
