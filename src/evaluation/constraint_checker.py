"""
Constraint checking logic for property evaluation.

Includes Haversine distance calculation and all constraint validators.
"""

import math
import re
from typing import Any, Optional

from .models import (
    ConstraintResult,
    Constraints,
    GoldQuestion,
    PropertyCheck,
    LocationConstraint,
    PriceConstraint,
    BedroomConstraint,
    FloorsConstraint,
)


class ConstraintChecker:
    """
    Check if properties meet gold standard constraints.
    """

    def __init__(self, default_price_tolerance: float = 0.0):
        """
        Initialize constraint checker.

        Args:
            default_price_tolerance: Default tolerance for price matching (0.0 = strict)
        """
        self.default_price_tolerance = default_price_tolerance

        # Property type mapping (Indonesian to normalized)
        self.property_type_map = {
            "rumah": "house",
            "house": "house",
            "apartment": "apartment",
            "apartemen": "apartment",
            "ruko": "ruko",
            "shophouse": "ruko",
            "tanah": "land",
            "land": "land",
            "gudang": "warehouse",
            "warehouse": "warehouse",
            "kantor": "office",
            "office": "office",
        }

        # Listing type mapping
        self.listing_type_map = {
            "dijual": "sale",
            "sale": "sale",
            "jual": "sale",
            "disewa": "rent",
            "rent": "rent",
            "sewa": "rent",
        }

    @staticmethod
    def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calculate the great circle distance between two points on earth.

        Args:
            lat1, lng1: Coordinates of first point (in degrees)
            lat2, lng2: Coordinates of second point (in degrees)

        Returns:
            Distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers

        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)

        # Haversine formula
        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def normalize_property_type(self, value: str) -> str:
        """Normalize property type to standard form."""
        if not value:
            return ""
        value_lower = value.lower().strip()
        return self.property_type_map.get(value_lower, value_lower)

    def normalize_listing_type(self, value: str) -> str:
        """Normalize listing type to standard form."""
        if not value:
            return ""
        value_lower = value.lower().strip()
        return self.listing_type_map.get(value_lower, value_lower)

    def check_property_type(
        self,
        actual: Optional[str],
        expected: Optional[str],
    ) -> ConstraintResult:
        """
        Check if property type matches expected.

        Args:
            actual: Actual property type from search result
            expected: Expected property type from gold standard

        Returns:
            ConstraintResult
        """
        if expected is None:
            return ConstraintResult.NA

        if actual is None:
            return ConstraintResult.MISSING

        actual_norm = self.normalize_property_type(actual)
        expected_norm = self.normalize_property_type(expected)

        if actual_norm == expected_norm:
            return ConstraintResult.PASS
        return ConstraintResult.FAIL

    def check_listing_type(
        self,
        actual: Optional[str],
        expected: Optional[str],
    ) -> ConstraintResult:
        """
        Check if listing type matches expected.

        Args:
            actual: Actual listing type from search result
            expected: Expected listing type from gold standard

        Returns:
            ConstraintResult
        """
        if expected is None:
            return ConstraintResult.NA

        if actual is None:
            return ConstraintResult.MISSING

        actual_norm = self.normalize_listing_type(actual)
        expected_norm = self.normalize_listing_type(expected)

        if actual_norm == expected_norm:
            return ConstraintResult.PASS
        return ConstraintResult.FAIL

    def check_location(
        self,
        prop_location: Optional[str],
        prop_lat: Optional[float],
        prop_lng: Optional[float],
        constraint: Optional[LocationConstraint],
        prop_name: Optional[str] = None,
        prop_address: Optional[str] = None,
    ) -> tuple[ConstraintResult, Optional[str], Optional[float], Optional[str]]:
        """
        Check if property location matches constraint.

        Uses keyword matching first (in location, name, address), then falls back to geo distance.

        Args:
            prop_location: Property location string (area/district)
            prop_lat: Property latitude
            prop_lng: Property longitude
            constraint: Location constraint from gold standard
            prop_name: Property name/title (also checked for keywords)
            prop_address: Property address (also checked for keywords)

        Returns:
            Tuple of (result, matched_keyword, distance_km, failure_reason)
        """
        if constraint is None:
            return ConstraintResult.NA, None, None, None

        # Combine all text fields for keyword search
        search_texts = []
        if prop_location:
            search_texts.append(prop_location.lower())
        if prop_name:
            search_texts.append(prop_name.lower())
        if prop_address:
            search_texts.append(prop_address.lower())
        combined_text = " ".join(search_texts)

        # First try keyword matching in combined text
        if combined_text and constraint.keywords:
            for keyword in constraint.keywords:
                if keyword.lower() in combined_text:
                    return ConstraintResult.PASS, keyword, None, None

        # Then try geo distance
        if (
            prop_lat is not None
            and prop_lng is not None
            and constraint.lat is not None
            and constraint.lng is not None
        ):
            distance = self.haversine_distance(
                prop_lat, prop_lng, constraint.lat, constraint.lng
            )
            if distance <= constraint.radius_km:
                return ConstraintResult.PASS, None, distance, None
            # FAIL with distance info
            reason = f"Geo distance {distance:.1f}km > radius {constraint.radius_km}km. Keywords {constraint.keywords} not found in: {prop_location or 'N/A'}"
            return ConstraintResult.FAIL, None, distance, reason

        # No keyword match and no geo data available
        if not combined_text and prop_lat is None:
            return ConstraintResult.MISSING, None, None, "No location data available"

        # FAIL - keywords not found, no geo fallback
        reason = f"Keywords {constraint.keywords} not found in location='{prop_location}'"
        if prop_lat is None or prop_lng is None:
            reason += ". Property has no coordinates for geo fallback"
        elif constraint.lat is None or constraint.lng is None:
            reason += ". Gold standard has no coordinates for geo fallback"
        return ConstraintResult.FAIL, None, None, reason

    def check_price(
        self,
        actual: Optional[int],
        constraint: Optional[PriceConstraint],
    ) -> ConstraintResult:
        """
        Check if price is within constraint range.

        Supports two modes:
        1. target mode: "harga X-an" → target ± tolerance (e.g., 1B ± 20% = 800M-1.2B)
        2. min/max mode: explicit min and/or max bounds

        Args:
            actual: Actual price
            constraint: Price constraint from gold standard

        Returns:
            ConstraintResult
        """
        if constraint is None:
            return ConstraintResult.NA

        # Check if any price constraint is specified
        if constraint.min is None and constraint.max is None and constraint.target is None:
            return ConstraintResult.NA

        if actual is None:
            return ConstraintResult.MISSING

        # Convert to int if string
        if isinstance(actual, str):
            try:
                actual = int(float(actual.replace(",", "").replace(".", "")))
            except ValueError:
                return ConstraintResult.MISSING

        # Use constraint tolerance if explicitly set (even if 0), else default
        tolerance = constraint.tolerance if constraint.tolerance is not None else self.default_price_tolerance

        # Target mode: "harga X-an" means around X with ± tolerance
        if constraint.target is not None:
            min_price = constraint.target * (1 - tolerance)
            max_price = constraint.target * (1 + tolerance)
            if min_price <= actual <= max_price:
                return ConstraintResult.PASS
            return ConstraintResult.FAIL

        # Min/Max mode: explicit bounds (tolerance applied to bounds)
        # Check min price
        if constraint.min is not None:
            min_with_tolerance = constraint.min * (1 - tolerance)
            if actual < min_with_tolerance:
                return ConstraintResult.FAIL

        # Check max price
        if constraint.max is not None:
            max_with_tolerance = constraint.max * (1 + tolerance)
            if actual > max_with_tolerance:
                return ConstraintResult.FAIL

        return ConstraintResult.PASS

    def check_bedrooms(
        self,
        actual: Optional[int],
        constraint: Optional[BedroomConstraint],
    ) -> ConstraintResult:
        """
        Check if bedroom count matches constraint.

        Args:
            actual: Actual bedroom count
            constraint: Bedroom constraint from gold standard

        Returns:
            ConstraintResult
        """
        if constraint is None:
            return ConstraintResult.NA

        if constraint.min is None and constraint.max is None and constraint.exact is None:
            return ConstraintResult.NA

        if actual is None:
            return ConstraintResult.MISSING

        # Convert to int if string
        if isinstance(actual, str):
            try:
                actual = int(actual)
            except ValueError:
                return ConstraintResult.MISSING

        # Check exact match
        if constraint.exact is not None:
            if actual == constraint.exact:
                return ConstraintResult.PASS
            return ConstraintResult.FAIL

        # Check min
        if constraint.min is not None and actual < constraint.min:
            return ConstraintResult.FAIL

        # Check max
        if constraint.max is not None and actual > constraint.max:
            return ConstraintResult.FAIL

        return ConstraintResult.PASS

    def check_floors(
        self,
        actual: Optional[int],
        constraint: Optional[FloorsConstraint],
    ) -> ConstraintResult:
        """
        Check if floor count matches constraint.

        Args:
            actual: Actual floor/story count
            constraint: Floors constraint from gold standard

        Returns:
            ConstraintResult
        """
        if constraint is None:
            return ConstraintResult.NA

        if constraint.min is None and constraint.max is None and constraint.exact is None:
            return ConstraintResult.NA

        if actual is None:
            return ConstraintResult.MISSING

        # Convert to int if string
        if isinstance(actual, str):
            try:
                actual = int(actual)
            except ValueError:
                return ConstraintResult.MISSING

        # Check exact match
        if constraint.exact is not None:
            if actual == constraint.exact:
                return ConstraintResult.PASS
            return ConstraintResult.FAIL

        # Check min
        if constraint.min is not None and actual < constraint.min:
            return ConstraintResult.FAIL

        # Check max
        if constraint.max is not None and actual > constraint.max:
            return ConstraintResult.FAIL

        return ConstraintResult.PASS

    def check_property(
        self,
        property_data: dict,
        gold_question: GoldQuestion,
    ) -> PropertyCheck:
        """
        Check all constraints for a single property.

        Args:
            property_data: Property data dictionary from search results
            gold_question: Gold standard question with constraints

        Returns:
            PropertyCheck with all constraint results
        """
        constraints = gold_question.constraints

        # Extract property data (handle various field names)
        prop_id = str(
            property_data.get("id")
            or property_data.get("property_id")
            or "unknown"
        )
        prop_name = (
            property_data.get("name")
            or property_data.get("title")
            or property_data.get("property_name")
            or "Unknown Property"
        )
        prop_type = (
            property_data.get("property_type")
            or property_data.get("type")
        )
        listing_type = (
            property_data.get("listing_type")
            or property_data.get("transaction_type")
        )
        prop_location = property_data.get("location") or property_data.get("area")
        prop_address = property_data.get("address") or property_data.get("display_address")
        prop_lat = property_data.get("latitude") or property_data.get("lat")
        prop_lng = property_data.get("longitude") or property_data.get("lng")
        prop_price = property_data.get("price")
        prop_bedrooms = property_data.get("bedrooms") or property_data.get("bedroom")
        prop_floors = property_data.get("floors") or property_data.get("floor") or property_data.get("stories")

        # Check each constraint
        property_type_result = self.check_property_type(prop_type, constraints.property_type)
        listing_type_result = self.check_listing_type(listing_type, constraints.listing_type)

        # Location check includes name and address for keyword matching
        location_result, keyword_match, distance, failure_reason = self.check_location(
            prop_location, prop_lat, prop_lng, constraints.location,
            prop_name=prop_name, prop_address=prop_address
        )

        price_result = self.check_price(prop_price, constraints.price)
        bedrooms_result = self.check_bedrooms(prop_bedrooms, constraints.bedrooms)
        floors_result = self.check_floors(prop_floors, constraints.floors)

        return PropertyCheck(
            property_id=prop_id,
            property_name=prop_name,
            property_type_result=property_type_result,
            listing_type_result=listing_type_result,
            location_result=location_result,
            price_result=price_result,
            bedrooms_result=bedrooms_result,
            floors_result=floors_result,
            location_keyword_match=keyword_match,
            location_distance_km=distance,
            location_failure_reason=failure_reason,
            actual_price=prop_price,
            actual_bedrooms=prop_bedrooms,
            actual_floors=prop_floors,
            actual_property_type=prop_type,
            actual_listing_type=listing_type,
        )

    def create_manual_property_check(
        self,
        property_data: dict,
    ) -> PropertyCheck:
        """
        Create a PropertyCheck for manual evaluation (no automatic constraint checking).

        Args:
            property_data: Property data dictionary from search results

        Returns:
            PropertyCheck with is_manual_evaluation=True and all results set to NA
        """
        # Extract property data
        prop_id = str(
            property_data.get("id")
            or property_data.get("property_id")
            or property_data.get("api_id")
            or "unknown"
        )
        prop_name = (
            property_data.get("name")
            or property_data.get("title")
            or property_data.get("property_name")
            or "Unknown Property"
        )
        prop_type = property_data.get("property_type") or property_data.get("type")
        listing_type = property_data.get("listing_type") or property_data.get("transaction_type")
        prop_price = property_data.get("price")
        prop_bedrooms = property_data.get("bedrooms") or property_data.get("bedroom")
        prop_floors = property_data.get("floors") or property_data.get("floor") or property_data.get("stories")

        return PropertyCheck(
            property_id=prop_id,
            property_name=prop_name,
            # All constraint results are NA for manual evaluation
            property_type_result=ConstraintResult.NA,
            listing_type_result=ConstraintResult.NA,
            location_result=ConstraintResult.NA,
            price_result=ConstraintResult.NA,
            bedrooms_result=ConstraintResult.NA,
            floors_result=ConstraintResult.NA,
            # Store actual values for display
            actual_price=prop_price,
            actual_bedrooms=prop_bedrooms,
            actual_floors=prop_floors,
            actual_property_type=prop_type,
            actual_listing_type=listing_type,
            # Mark as manual evaluation
            is_manual_evaluation=True,
            manual_result=None,  # Pending until evaluator marks it
            manual_comment="",
        )

    def check_all_properties(
        self,
        properties: list[dict],
        gold_question: GoldQuestion,
    ) -> list[PropertyCheck]:
        """
        Check all properties against gold standard constraints.

        Args:
            properties: List of property data dictionaries
            gold_question: Gold standard question with constraints

        Returns:
            List of PropertyCheck results
        """
        # For manual evaluation questions, create manual property checks
        if gold_question.is_manual_evaluation:
            return [self.create_manual_property_check(prop) for prop in properties]

        return [self.check_property(prop, gold_question) for prop in properties]
