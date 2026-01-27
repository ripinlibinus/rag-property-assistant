"""
Property Agent - Full Implementation with Hybrid Search (Adapter + Vector)

This agent handles all property-related operations:
- Search properties using hybrid approach (API filter + semantic ranking)
- CRUD operations via chat with permission checks
- Generate marketing descriptions
"""

import json
from pathlib import Path
from typing import Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.documents import Document
from langchain_chroma import Chroma

from .state import AgentState
from ..adapters.base import (
    PropertyDataAdapter, 
    Property, 
    PropertyUpdate,
    PropertyCreate,
    SearchCriteria,
    SearchResult,
    PropertyType,
    ListingType,
)


# System prompt for the property agent
PROPERTY_AGENT_SYSTEM_PROMPT = """You are a property search assistant for a real estate agency.
Your job is to help users find, manage, and get information about properties.

LANGUAGE & STYLE RULES:
- ALWAYS match user's language (Indonesian/English/mixed)
- Adapt your tone and speaking style to mirror the user:
  * Formal user → formal response
  * Casual user ("gue", "lu", "bro") → casual response  
  * Professional user → professional response
- Use appropriate emojis for friendly conversations
- Keep responses natural and conversational

RESPONSE GUIDELINES:
- Be helpful and provide detailed property information
- Format search results clearly with key details
- Always include: price, location, bedrooms, area
- For nearby/area searches, mention the landmark context

When user asks to update or modify a listing:
1. First identify which property they're referring to
2. Ask for confirmation before making changes
3. Only update if you have explicit permission
"""

SEARCH_PARSER_PROMPT = """Analyze the user's property search query and extract search criteria.

Query: {query}
Previous context: {context}

Extract the following in JSON format:
{{
  "property_type": "house" | "shophouse" | "land" | "apartment" | null,
  "listing_type": "sale" | "rent" | null,
  "source": "listing" | "project" | null,
  "min_price": number in IDR | null,
  "max_price": number in IDR | null,
  "location": "location/district name" | null,
  "city": "city name" | null,
  "min_bedrooms": number | null,
  "min_land_area": number in sqm | null,
  "min_building_area": number in sqm | null,
  "features": ["feature1", "feature2"] | null,
  "search_keywords": "CLEAN keywords for database search" | null,
  "nearby_search": true | false,
  "landmark": "landmark name if searching near a place" | null
}}

SOURCE DETECTION (primary vs secondary market):
- "project" (primary market): Keywords like "proyek", "project", "developer", "primary", "baru", "perumahan baru", "cluster baru", "new development"
- "listing" (secondary market): Keywords like "secondary", "bekas", "listing", "resale", "second", "rumah second"
- null: No specific preference, search both

CRITICAL for search_keywords:
- Extract ONLY the location/area/landmark name
- Remove filler words: "cari", "carikan", "ada", "yang", "di", "daerah", "sekitar"
- Examples:
  * "cari rumah di daerah cemara asri" -> search_keywords: "cemara asri"
  * "ada ruko di krakatau?" -> search_keywords: "krakatau"
  * "rumah di jalan setia budi" -> search_keywords: "setia budi"
  * "Find house near USU" -> search_keywords: "USU"

IMPORTANT for Location/Area Searches:
- If user says "near/dekat/sekitar/sekitaran/daerah [PLACE]", set nearby_search=true and landmark=[PLACE]
- Common landmarks to recognize (Medan area):
  * USU/Universitas Sumatera Utara -> Padang Bulan, Dr. Mansyur, Medan Baru
  * Bandara Kualanamu -> Beringin, Tanjung Morawa
  * Sun Plaza -> Medan Kota, Simpang Limun
  * Centre Point -> Medan Maimun
- Preserve Indonesian location names (e.g., "Sunggal", "Helvetia")

Notes:
- Convert "1M" or "1 milyar" to 1000000000
- Convert "500jt" to 500000000
- "3KT" = 3 bedrooms
- "2KM" = 2 bathrooms
"""

DESCRIPTION_GENERATOR_PROMPT = """Create a compelling marketing description for this property:

{property_details}

Requirements:
1. Write in Indonesian (Bahasa Indonesia)
2. Be persuasive and highlight key features
3. Suitable for listing/advertisement
4. Around 100-150 words
5. Use natural, engaging language

Output: Just the description text, no headers or formatting.
"""


class PropertyAgent:
    """
    Agent for property-related tasks:
    - Search properties (adapter + vector hybrid)
    - Update/create listing information
    - Generate marketing descriptions
    """
    
    def __init__(
        self, 
        data_adapter: PropertyDataAdapter,
        llm: Optional[ChatOpenAI] = None,
        embeddings: Optional[OpenAIEmbeddings] = None,
        chroma_path: str = "data/chroma",
        enable_vector_search: bool = True,
    ):
        """
        Initialize PropertyAgent.
        
        Args:
            data_adapter: Adapter for property data source
            llm: Language model for parsing and generation
            embeddings: Embeddings model for vector search
            chroma_path: Path to ChromaDB storage
            enable_vector_search: Whether to use vector search for ranking
        """
        self.adapter = data_adapter
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.embeddings = embeddings or OpenAIEmbeddings(model="text-embedding-3-small")
        self.chroma_path = Path(chroma_path)
        self.enable_vector_search = enable_vector_search
        
        # Vector store for semantic search
        self.vectorstore: Optional[Chroma] = None
        if enable_vector_search:
            self._init_vectorstore()
    
    def _init_vectorstore(self):
        """Initialize or load ChromaDB vector store"""
        try:
            self.vectorstore = Chroma(
                collection_name="properties",
                embedding_function=self.embeddings,
                persist_directory=str(self.chroma_path),
            )
        except Exception as e:
            print(f"Warning: Could not initialize vector store: {e}")
            self.vectorstore = None
    
    async def index_properties(self, properties: list[Property]):
        """
        Index properties in vector store for semantic search.
        Call this periodically to sync data from adapter.
        """
        if not self.vectorstore:
            return
        
        documents = []
        ids = []
        
        for prop in properties:
            doc = Document(
                page_content=prop.to_embedding_text(),
                metadata={
                    "id": prop.id,
                    "source": prop.source,
                    "property_type": prop.property_type.value,
                    "price": prop.price,
                    "location": prop.location,
                    "city": prop.city,
                }
            )
            documents.append(doc)
            ids.append(f"{prop.source}_{prop.id}")
        
        # Upsert documents
        self.vectorstore.add_documents(documents, ids=ids)
    
    async def search(self, state: AgentState) -> dict:
        """
        Search properties using hybrid approach.
        
        1. Parse user query to extract criteria
        2. Fetch from adapter with filters
        3. Optionally re-rank using vector similarity
        4. Format response
        """
        query = state.get("current_input", "")
        context = state.get("conversation_context", {})
        
        # Use language from state (detected by orchestrator) or fallback to detection
        user_lang = state.get("language") or self._detect_language(query)
        
        # Get extracted info from orchestrator if available
        extracted_info = state.get("extracted_info", {})
        
        # Parse search criteria from natural language
        criteria, parsed_data = await self._parse_search_query(query, context)
        
        # Handle nearby/landmark search
        if parsed_data.get("nearby_search") or extracted_info.get("nearby"):
            landmark = parsed_data.get("landmark") or extracted_info.get("landmark")
            if landmark:
                # Expand search to nearby areas
                criteria = self._expand_nearby_search(criteria, landmark)
        
        # Fetch from data adapter
        result = await self.adapter.search(criteria)
        
        # Apply vector ranking if enabled and we have results
        if self.enable_vector_search and result.properties and criteria.query:
            result = await self._apply_vector_ranking(result, criteria.query)
        
        # Format response with landmark context if applicable
        landmark_context = parsed_data.get("landmark") or extracted_info.get("landmark")
        response = self._format_search_results(result, criteria, user_lang, landmark_context)
        
        return {
            "response": response,
            "retrieved_properties": [p.to_dict() for p in result.properties[:5]],
        }
    
    async def _parse_search_query(
        self, 
        query: str, 
        context: dict
    ) -> tuple[SearchCriteria, dict]:
        """Parse natural language query into structured criteria.
        
        Returns:
            tuple: (SearchCriteria, parsed_data dict with all extracted fields)
        """
        
        prompt = SEARCH_PARSER_PROMPT.format(
            query=query,
            context=json.dumps(context) if context else "None"
        )
        
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        
        try:
            # Extract JSON from response
            content = response.content
            # Find JSON in response
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                parsed = json.loads(content[start:end])
            else:
                parsed = {}
        except json.JSONDecodeError:
            parsed = {}
        
        # Build criteria - use search_keywords for API search
        search_keywords = parsed.get("search_keywords") or parsed.get("location") or parsed.get("landmark")

        criteria = SearchCriteria(
            query=search_keywords,  # This will be sent as 'search' to API
            location=parsed.get("location"),
            city=parsed.get("city"),
            min_price=parsed.get("min_price"),
            max_price=parsed.get("max_price"),
            min_bedrooms=parsed.get("min_bedrooms"),
            min_land_area=parsed.get("min_land_area"),
            min_building_area=parsed.get("min_building_area"),
            source=parsed.get("source"),  # "listing", "project", or None (both)
        )
        
        # Parse property type
        if parsed.get("property_type"):
            try:
                criteria.property_type = PropertyType(parsed["property_type"])
            except ValueError:
                pass
        
        # Parse listing type
        if parsed.get("listing_type"):
            try:
                criteria.listing_type = ListingType(parsed["listing_type"])
            except ValueError:
                pass
        
        return criteria, parsed
    
    def _expand_nearby_search(
        self, 
        criteria: SearchCriteria, 
        landmark: str
    ) -> SearchCriteria:
        """
        Expand search criteria for nearby/area-based searches.
        Maps landmarks to known nearby areas.
        """
        # Mapping of landmarks to nearby areas (Medan specific)
        LANDMARK_AREAS = {
            "usu": ["Padang Bulan", "Dr. Mansyur", "Medan Baru", "Simpang Limun"],
            "universitas sumatera utara": ["Padang Bulan", "Dr. Mansyur", "Medan Baru"],
            "kualanamu": ["Beringin", "Tanjung Morawa", "Batang Kuis"],
            "bandara kualanamu": ["Beringin", "Tanjung Morawa", "Batang Kuis"],
            "sun plaza": ["Medan Kota", "Simpang Limun", "Thamrin"],
            "centre point": ["Medan Maimun", "Kesawan", "Medan Kota"],
            "uisu": ["Teladan", "Medan Kota", "Sukaramai"],
            "masjid raya": ["Medan Area", "Kesawan", "Petisah"],
            "setia budi": ["Tanjung Sari", "Simpang Selayang", "Medan Selayang"],
            "plaza medan fair": ["Petisah", "Sei Sikambing", "Medan Petisah"],
            "cambridge": ["Medan Johor", "Pangkalan Masyhur"],
            "ringroad": ["Medan Johor", "Medan Tuntungan", "Setia Budi"],
            "medan johor": ["Medan Johor", "Pangkalan Masyhur", "Gedung Johor"],
            "krakatau": ["Medan Timur", "Glugur Darat", "Pulo Brayan"],
        }
        
        # Normalize landmark for lookup
        landmark_lower = landmark.lower().strip()
        
        nearby_areas = []
        for key, areas in LANDMARK_AREAS.items():
            if key in landmark_lower or landmark_lower in key:
                nearby_areas = areas
                break
        
        if nearby_areas:
            # Add areas to query for semantic matching
            areas_text = ", ".join(nearby_areas)
            if criteria.query:
                criteria.query = f"{criteria.query} {areas_text}"
            else:
                criteria.query = areas_text
            
            # If no specific location set, use first nearby area
            if not criteria.location:
                criteria.location = nearby_areas[0]
        else:
            # Landmark not in mapping, use it as location directly
            if not criteria.location:
                criteria.location = landmark
            if criteria.query:
                criteria.query = f"{criteria.query} {landmark}"
            else:
                criteria.query = landmark
        
        return criteria
    
    async def _apply_vector_ranking(
        self, 
        result: SearchResult, 
        query: str
    ) -> SearchResult:
        """Re-rank search results using vector similarity"""
        
        if not self.vectorstore or not result.properties:
            return result
        
        # Get vector similarity scores
        try:
            docs_with_scores = self.vectorstore.similarity_search_with_score(
                query, 
                k=len(result.properties) * 2
            )
            
            # Build score map
            score_map = {}
            for doc, score in docs_with_scores:
                prop_id = doc.metadata.get("id")
                if prop_id:
                    score_map[prop_id] = 1 - score  # Convert distance to similarity
            
            # Apply scores to properties
            for prop in result.properties:
                if prop.id in score_map:
                    prop.relevance_score = score_map[prop.id]
                else:
                    prop.relevance_score = 0.5  # Default score
            
            # Re-sort by relevance
            result.properties.sort(
                key=lambda p: p.relevance_score or 0, 
                reverse=True
            )
            
        except Exception as e:
            print(f"Vector ranking error: {e}")
        
        return result
    
    def _format_search_results(
        self, 
        result: SearchResult, 
        criteria: SearchCriteria,
        lang: str = "id",
        landmark_context: Optional[str] = None
    ) -> str:
        """Format search results for chat response"""
        
        if not result.properties:
            if lang == "id":
                response = "🔍 Maaf, tidak ditemukan properti"
                if landmark_context:
                    response += f" di sekitar {landmark_context}"
                response += " yang sesuai dengan kriteria:\n"
                if criteria.property_type:
                    response += f"- Tipe: {criteria.property_type.value}\n"
                if criteria.location:
                    response += f"- Lokasi: {criteria.location}\n"
                if criteria.max_price:
                    response += f"- Budget maksimal: Rp {criteria.max_price:,.0f}\n"
                response += "\nCoba perluas kriteria pencarian Anda."
            else:
                response = "🔍 Sorry, no properties found"
                if landmark_context:
                    response += f" near {landmark_context}"
                response += " matching your criteria.\n"
                response += "Try broadening your search."
            return response
        
        # Build response
        count = len(result.properties)
        if lang == "id":
            if landmark_context:
                response = f"🏠 Ditemukan {count} properti di sekitar **{landmark_context}**:\n\n"
            else:
                response = f"🏠 Ditemukan {count} properti yang cocok:\n\n"
        else:
            if landmark_context:
                response = f"🏠 Found {count} properties near **{landmark_context}**:\n\n"
            else:
                response = f"🏠 Found {count} matching properties:\n\n"
        
        for i, prop in enumerate(result.properties[:5], 1):
            response += f"**{i}. {prop.title}**\n"
            response += f"   📍 {prop.location}, {prop.city}\n"
            response += f"   💰 Rp {prop.price:,.0f}\n"

            # Show source type (primary/secondary) and developer if applicable
            source_label = "🏗️ Primary" if prop.source_type == "project" else "🏠 Secondary"
            if prop.developer_name:
                response += f"   {source_label} | Developer: {prop.developer_name}\n"
            elif prop.source_type == "project":
                response += f"   {source_label}\n"

            specs = []
            if prop.bedrooms:
                specs.append(f"{prop.bedrooms}KT")
            if prop.bathrooms:
                specs.append(f"{prop.bathrooms}KM")
            if prop.land_area:
                specs.append(f"LT:{prop.land_area}m²")
            if prop.building_area:
                specs.append(f"LB:{prop.building_area}m²")

            if specs:
                response += f"   📐 {' | '.join(specs)}\n"

            if prop.features:
                response += f"   ✨ {', '.join(prop.features[:3])}\n"

            response += "\n"
        
        if result.has_more:
            if lang == "id":
                response += f"_...dan {result.total - count} properti lainnya._\n\n"
            else:
                response += f"_...and {result.total - count} more properties._\n\n"
        
        if lang == "id":
            response += "Ketik nomor untuk melihat detail, atau sebutkan kriteria lain."
        else:
            response += "Type a number for details, or specify other criteria."
        
        return response
    
    async def update_listing(self, state: AgentState) -> dict:
        """Update property listing via chat"""
        
        query = state.get("current_input", "")
        # TODO: Parse update request and execute via adapter
        
        response = "✅ Untuk update listing, saya butuh informasi:\n"
        response += "1. ID atau nama properti yang akan diupdate\n"
        response += "2. Field yang ingin diubah (harga/status/deskripsi)\n"
        response += "3. Nilai baru\n\n"
        response += "Contoh: \"Update harga rumah ID abc123 jadi 1.5M\""
        
        return {
            "response": response,
            "property_action_result": {"status": "awaiting_details"},
        }
    
    async def generate_description(self, state: AgentState) -> dict:
        """Generate marketing description for a property"""
        
        extracted = state.get("metrics", {}).get("extracted_info", {})
        property_id = extracted.get("property_id")
        
        if property_id:
            prop = await self.adapter.get_by_id(property_id)
        else:
            # Get first property as example
            result = await self.adapter.search(SearchCriteria(limit=1))
            prop = result.properties[0] if result.properties else None
        
        if not prop:
            return {
                "response": "Tidak ada properti yang tersedia untuk dibuatkan deskripsi.",
            }
        
        property_details = f"""
        Nama: {prop.title}
        Tipe: {prop.property_type.value}
        Lokasi: {prop.location}, {prop.city}
        Harga: Rp {prop.price:,}
        Kamar Tidur: {prop.bedrooms or '-'}
        Kamar Mandi: {prop.bathrooms or '-'}
        Luas Tanah: {prop.land_area or '-'} m²
        Luas Bangunan: {prop.building_area or '-'} m²
        Fitur: {', '.join(prop.features) if prop.features else '-'}
        """
        
        prompt = DESCRIPTION_GENERATOR_PROMPT.format(property_details=property_details)
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        
        result = f"📝 **Deskripsi Marketing untuk {prop.title}:**\n\n"
        result += response.content
        result += "\n\n_Deskripsi ini bisa Anda copy dan gunakan untuk listing._"
        
        return {"response": result}
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection (Indonesian vs English)"""
        id_words = ["cari", "rumah", "harga", "kamar", "dengan", "di", "yang", "untuk"]
        text_lower = text.lower()
        id_count = sum(1 for word in id_words if word in text_lower)
        return "id" if id_count >= 2 else "en"
    
    async def get_property_detail(self, property_id: str) -> Optional[dict]:
        """Get detailed property information by ID"""
        prop = await self.adapter.get_by_id(property_id)
        if prop:
            return prop.to_dict()
        return None
