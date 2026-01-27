"""
Property Vector Store

Manages ChromaDB vector store for property semantic search.
Syncs with MetaProperty API using flag-based incremental sync.

Usage:
    from src.knowledge.property_store import PropertyStore
    
    store = PropertyStore()
    await store.sync_pending(adapter)  # Sync only need_ingest=true
    results = store.search("taman luas modern")
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document


class PropertyStore:
    """
    ChromaDB store for property semantic search.

    Stores property title + description for semantic matching,
    while structured data (price, bedrooms, etc.) stays in API.

    Sync Strategy:
        - MetaProperty has `need_ingest` flag on each listing
        - Scheduler calls sync_pending() periodically
        - After embedding, marks listings as ingested

    Multi-Model Support:
        - Set use_model_suffix=True to include model name in directory path
        - E.g., "data/chromadb/properties-text-embedding-3-small"
        - This allows storing embeddings from different models separately
    """

    def __init__(
        self,
        persist_dir: str = "data/chromadb/properties",
        collection_name: str = "properties",
        embedding_model: str = "text-embedding-3-small",
        use_model_suffix: bool = False,
    ):
        self.embedding_model = embedding_model

        # Optionally include model name in directory for multi-model comparison
        if use_model_suffix:
            model_suffix = embedding_model.replace("/", "-")
            self.persist_dir = f"{persist_dir}-{model_suffix}"
        else:
            self.persist_dir = persist_dir

        self.collection_name = collection_name
        self.embeddings = OpenAIEmbeddings(model=embedding_model)
        self._vector_store: Optional[Chroma] = None

        # Ensure directory exists
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
    
    @property
    def vector_store(self) -> Chroma:
        """Get or create the vector store"""
        if self._vector_store is None:
            self._vector_store = Chroma(
                persist_directory=self.persist_dir,
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
            )
        return self._vector_store
    
    def _create_document_text(self, listing: dict) -> str:
        """
        Create searchable text from listing data for semantic embedding.

        Optimized for property domain:
        - Rich text content (title, description, features) for semantic matching
        - Numeric fields (price, bedrooms) are in metadata for filtering, not embedded

        This reduces token usage while improving semantic relevance.
        """
        parts = []

        # 1. Title (high importance)
        if listing.get("title"):
            parts.append(listing["title"])

        # 2. Listing type context (dijual/disewa)
        listing_type = listing.get("listing_type", "")
        source_type = listing.get("source", "listing")
        if listing_type == "sale":
            parts.append("Properti dijual")
        elif listing_type == "rent":
            parts.append("Properti disewakan")

        # 3. Source type context (primary/secondary market)
        if source_type == "project":
            developer = listing.get("developer")
            if developer:
                parts.append(f"Proyek baru dari developer {developer}")
            else:
                parts.append("Proyek baru (primary market)")

            # 3b. Unit types info for projects (enables "proyek 3 kamar", "3 lantai" queries)
            unit_types = listing.get("unit_types") or []
            if unit_types:
                parts.append("Tipe unit tersedia: " + ", ".join(unit_types))

            # Bedrooms available in project
            bedrooms_avail = listing.get("bedrooms_available") or []
            if bedrooms_avail:
                if len(bedrooms_avail) == 1:
                    parts.append(f"Tersedia rumah {bedrooms_avail[0]} kamar tidur")
                else:
                    parts.append(f"Tersedia rumah {min(bedrooms_avail)}-{max(bedrooms_avail)} kamar tidur")

            # Floors available (handle string like "2.0")
            floors_avail = listing.get("floors_available") or []
            if floors_avail:
                # Convert to int, handling float strings like "2.0"
                floors_int = [int(float(f)) for f in floors_avail if f]
                if floors_int:
                    if len(floors_int) == 1:
                        parts.append(f"Bangunan {floors_int[0]} lantai")
                    else:
                        parts.append(f"Bangunan {min(floors_int)}-{max(floors_int)} lantai")

            # Building area range
            ba_min = listing.get("building_area_min")
            ba_max = listing.get("building_area_max")
            if ba_min and ba_max:
                if ba_min == ba_max:
                    parts.append(f"Luas bangunan {int(ba_min)}m²")
                else:
                    parts.append(f"Luas bangunan {int(ba_min)}-{int(ba_max)}m²")

            # Land area range
            la_min = listing.get("land_area_min")
            la_max = listing.get("land_area_max")
            if la_min and la_max:
                if la_min == la_max:
                    parts.append(f"Luas tanah {int(la_min)}m²")
                else:
                    parts.append(f"Luas tanah {int(la_min)}-{int(la_max)}m²")

        # 4. Description or additional_info (main content)
        description = listing.get("description")
        additional_info = listing.get("additional_info")

        if description:
            # Strip HTML tags if present
            import re
            clean_desc = re.sub(r'<[^>]+>', ' ', str(description))
            clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()
            if clean_desc:
                parts.append(clean_desc)

        if additional_info and additional_info != description:
            parts.append(additional_info)

        # 5. Location info (very important for property search)
        location_parts = []
        if listing.get("area_listing"):
            location_parts.append(listing["area_listing"])
        if listing.get("complex_name"):
            location_parts.append(f"Komplek {listing['complex_name']}")
        if listing.get("district"):
            location_parts.append(listing["district"])
        if listing.get("city"):
            location_parts.append(listing["city"])
        if listing.get("address") and listing["address"] not in location_parts:
            location_parts.append(listing["address"])
        if location_parts:
            parts.append("Lokasi: " + ", ".join(location_parts))

        # 6. Property type
        if listing.get("property_type"):
            type_map = {
                "house": "Rumah",
                "shophouse": "Ruko",
                "land": "Tanah",
                "apartment": "Apartemen",
                "warehouse": "Gudang",
                "office": "Kantor",
                "villa": "Villa",
                "perumahan": "Perumahan",
            }
            prop_type = listing["property_type"]
            parts.append(f"Tipe: {type_map.get(prop_type, prop_type)}")

        # 7. Certificate type (important for buyers)
        if listing.get("certificate_type"):
            cert_map = {
                "shm": "SHM (Sertifikat Hak Milik)",
                "shgb": "SHGB (Sertifikat Hak Guna Bangunan)",
                "hgb": "HGB",
                "girik": "Girik",
                "ppjb": "PPJB",
            }
            cert = listing["certificate_type"]
            parts.append(f"Sertifikat: {cert_map.get(cert.lower(), cert.upper())}")

        # 8. Amenities/Facilities (key differentiator for semantic search!)
        amenities = listing.get("amenities") or listing.get("facilities") or []
        if amenities and isinstance(amenities, list):
            # Map common amenity codes to Indonesian
            amenity_map = {
                "electricity": "listrik",
                "water": "air PDAM",
                "furnished": "full furnished",
                "semi_furnished": "semi furnished",
                "unfurnished": "unfurnished",
                "ceramic_floor": "lantai keramik",
                "marble_floor": "lantai marmer",
                "painted_walls": "dinding cat",
                "ac": "AC",
                "ac_installation": "instalasi AC",
                "water_heater": "water heater",
                "stair_railing": "railing tangga",
                "security_24": "security 24 jam",
                "swimming_pool": "kolam renang",
                "playground": "playground",
                "jogging_track": "jogging track",
                "clubhouse": "clubhouse",
                "garden": "taman",
                "garage": "garasi",
                "carport": "carport",
            }

            readable_amenities = []
            for a in amenities:
                if isinstance(a, str):
                    readable = amenity_map.get(a.lower(), a.replace("_", " "))
                    readable_amenities.append(readable)

            if readable_amenities:
                parts.append("Fasilitas: " + ", ".join(readable_amenities))

        return "\n\n".join(parts)
    
    def upsert_property(self, listing: dict) -> bool:
        """
        Add or update a single property in the vector store.
        
        Args:
            listing: Property data dict with id, title, description, etc.
            
        Returns:
            True if successful
        """
        property_id = str(listing.get("id") or listing.get("slug"))
        if not property_id:
            raise ValueError("Listing must have 'id' or 'slug'")
        
        # Create document text for embedding
        doc_text = self._create_document_text(listing)
        
        # Metadata for filtering (numeric/categorical fields)
        # These are NOT embedded but can be used for ChromaDB where clause
        source = listing.get("source", "listing")

        # For projects, use range data from unit types
        if source == "project":
            bedrooms_avail = listing.get("bedrooms_available") or []
            bathrooms_avail = listing.get("bathrooms_available") or []
            floors_avail = listing.get("floors_available") or []

            # Convert to int/float, handling string values like "2.0"
            bedrooms_avail = [int(float(x)) for x in bedrooms_avail if x] if bedrooms_avail else []
            bathrooms_avail = [int(float(x)) for x in bathrooms_avail if x] if bathrooms_avail else []
            floors_avail = [float(x) for x in floors_avail if x] if floors_avail else []

            bedrooms_min = min(bedrooms_avail) if bedrooms_avail else 0
            bedrooms_max = max(bedrooms_avail) if bedrooms_avail else 0
            bathrooms_min = min(bathrooms_avail) if bathrooms_avail else 0
            bathrooms_max = max(bathrooms_avail) if bathrooms_avail else 0
            floors_min = min(floors_avail) if floors_avail else 0
            floors_max = max(floors_avail) if floors_avail else 0

            land_area_min = float(listing.get("land_area_min", 0) or 0)
            land_area_max = float(listing.get("land_area_max", 0) or 0)
            building_area_min = float(listing.get("building_area_min", 0) or 0)
            building_area_max = float(listing.get("building_area_max", 0) or 0)
        else:
            # For listings, use single values
            bedrooms_min = bedrooms_max = int(listing.get("bedrooms", 0) or 0)
            bathrooms_min = bathrooms_max = int(listing.get("bathrooms", 0) or 0)
            floors_min = floors_max = float(listing.get("floors", 0) or 0)
            land_area_min = land_area_max = float(listing.get("land_area", 0) or 0)
            building_area_min = building_area_max = float(listing.get("building_area", 0) or 0)

        # Complex name (for in_complex filter)
        complex_name = listing.get("complex_name", "") or ""

        # Facing direction (hadap)
        facing = listing.get("facing", "") or listing.get("hadap", "") or ""

        # Get slug for URL construction
        slug = listing.get("slug", "")
        url_view = listing.get("url_view", "")

        # If no url_view but have slug, construct URL
        if not url_view and slug:
            listing_type = listing.get("listing_type", "sale")
            url_prefix = "dijual" if listing_type == "sale" else "disewa"
            url_view = f"https://metaproperty.id/{url_prefix}/{slug}"

        metadata = {
            "property_id": property_id,
            "slug": slug,
            "url_view": url_view,
            "title": listing.get("title", ""),
            "property_type": listing.get("property_type", ""),
            "listing_type": listing.get("listing_type", "sale"),
            "city": listing.get("city", ""),
            "district": listing.get("district", ""),
            "area_listing": listing.get("area_listing", ""),
            "price": float(listing.get("price", 0) or 0),
            "bedrooms": bedrooms_min,  # Min for range filtering
            "bedrooms_max": bedrooms_max,
            "bathrooms": bathrooms_min,
            "bathrooms_max": bathrooms_max,
            "land_area": land_area_min,
            "land_area_max": land_area_max,
            "building_area": building_area_min,
            "building_area_max": building_area_max,
            "floors": floors_min,
            "floors_max": floors_max,
            "certificate_type": listing.get("certificate_type", ""),
            "source": source,  # project or listing
            "status": listing.get("status", "active"),
            "complex_name": complex_name,  # For in_complex filter
            "in_complex": 1 if complex_name else 0,  # 1=in complex, 0=standalone (for filtering)
            "facing": facing.lower() if facing else "",  # Facing direction (utara, selatan, etc.)
            "synced_at": datetime.now().isoformat(),
        }
        
        # Remove existing document with same ID
        try:
            self.vector_store._collection.delete(ids=[property_id])
        except Exception:
            pass  # Document might not exist
        
        # Add new document
        doc = Document(page_content=doc_text, metadata=metadata)
        self.vector_store.add_documents([doc], ids=[property_id])
        
        return True
    
    def upsert_many(self, listings: List[dict]) -> int:
        """
        Bulk upsert multiple properties.
        
        Returns:
            Number of properties upserted
        """
        count = 0
        for listing in listings:
            try:
                self.upsert_property(listing)
                count += 1
            except Exception as e:
                print(f"Error upserting {listing.get('id')}: {e}")
        return count
    
    def delete_property(self, property_id: str) -> bool:
        """Delete a property from the vector store"""
        try:
            self.vector_store._collection.delete(ids=[str(property_id)])
            return True
        except Exception:
            return False
    
    def search(
        self,
        query: str,
        k: int = 20,
        property_type: Optional[str] = None,
        city: Optional[str] = None,
    ) -> List[str]:
        """
        Search properties semantically.
        
        Args:
            query: Semantic search query (e.g., "taman luas", "view bagus")
            k: Max number of results
            property_type: Optional filter
            city: Optional filter
            
        Returns:
            List of property IDs ranked by semantic relevance
        """
        # Build filter
        filter_dict = {}
        if property_type:
            filter_dict["property_type"] = property_type
        if city:
            filter_dict["city"] = city
        
        # Search
        results = self.vector_store.similarity_search(
            query=query,
            k=k,
            filter=filter_dict if filter_dict else None,
        )
        
        # Return property IDs in ranked order
        return [doc.metadata.get("property_id") for doc in results]
    
    def search_with_scores(
        self,
        query: str,
        k: int = 20,
    ) -> List[tuple[str, float]]:
        """
        Search with similarity scores.
        
        Returns:
            List of (property_id, score) tuples
        """
        results = self.vector_store.similarity_search_with_score(
            query=query,
            k=k,
        )
        
        return [
            (doc.metadata.get("property_id"), score)
            for doc, score in results
        ]
    
    def get_stats(self) -> dict:
        """Get collection statistics"""
        collection = self.vector_store._collection
        count = collection.count()

        return {
            "total_properties": count,
            "persist_dir": self.persist_dir,
            "embedding_model": self.embedding_model,
            "collection_name": self.collection_name,
        }

    def clear(self) -> bool:
        """Clear all properties from the vector store"""
        try:
            self.vector_store._client.delete_collection(self.collection_name)
            self._vector_store = None
            return True
        except Exception:
            return False


# Project root for absolute paths
_PROJECT_ROOT = Path(__file__).parent.parent.parent


def create_property_store(
    persist_dir: Optional[str] = None,
    embedding_model: str = "text-embedding-3-small",
    use_model_suffix: bool = False,
) -> PropertyStore:
    """
    Factory function to create PropertyStore.

    Args:
        persist_dir: Optional path. If None, uses data/chromadb/properties relative to project root.
        embedding_model: OpenAI embedding model name
        use_model_suffix: If True, appends model name to persist_dir

    Returns:
        PropertyStore instance
    """
    if persist_dir is None:
        persist_dir = str(_PROJECT_ROOT / "data" / "chromadb" / "properties")
    return PropertyStore(
        persist_dir=persist_dir,
        embedding_model=embedding_model,
        use_model_suffix=use_model_suffix,
    )


# Available embedding models for comparison
EMBEDDING_MODELS = [
    "text-embedding-3-small",   # Default, fastest, cheapest
    "text-embedding-3-large",   # Better quality, more expensive
    "text-embedding-ada-002",   # Legacy model
]
