"""
ReAct Agent - Proper LangGraph Agent with Tool Calling

This is the CORRECT agent pattern:
1. LLM receives user message
2. LLM DECIDES which tool to call (not hardcoded routing!)
3. Tool executes and returns result
4. LLM observes result and decides: answer or call more tools
5. Repeat until LLM has enough info to respond

This replaces the old chain-based approach where routing was hardcoded.
"""

from typing import Optional, List, Sequence, Literal, TypedDict, Annotated, TYPE_CHECKING
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import (
    BaseMessage, 
    HumanMessage, 
    AIMessage, 
    SystemMessage,
    ToolMessage,
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from langchain_chroma import Chroma
from langgraph.graph import StateGraph, END, add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from .tools import create_all_tools, set_current_user
from ..adapters.base import PropertyDataAdapter
from ..utils.logging import get_agent_logger

# Module logger
logger = get_agent_logger()

# Type hints for optional imports
if TYPE_CHECKING:
    from ..memory.mysql_memory import SlidingWindowMemory


# ============================================================================
# Agent State
# ============================================================================

class ReActAgentState(TypedDict):
    """State for the ReAct agent"""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    # Optional: track current user for permissions
    user_id: Optional[str]
    user_role: Optional[str]  # "agent", "admin", "user"
    

# ============================================================================
# System Prompt
# ============================================================================

REACT_SYSTEM_PROMPT = """You are a helpful real estate assistant for property agents. Global support - works for any city/country.

⚠️ TOPIC GUIDELINES:
You are a real estate assistant focused on property topics. Follow these guidelines:

✅ CORE TOPICS (full support):
- Property search (rumah, ruko, tanah, apartment, gudang, villa, kantor)
- Real estate information (sertifikat SHM/SHGB/AJB, pajak properti, proses jual beli)
- Sales tips and techniques for property agents
- Motivation for property agents

✅ RELATED TOPICS (allowed, answer briefly):
- KPR, mortgage, financing, bank untuk properti
- Renovasi, interior design, home improvement
- Legal aspects (notaris, PPAT, biaya balik nama)
- Neighborhood info (sekolah, rumah sakit, mall) - especially if related to current property search
- Property investment tips
- Moving/relocation tips
- Area/city information relevant to property search

⚠️ CONTEXTUALLY RELATED (graceful handling):
If user asks about something related to their property search context (e.g., asking about a school near a property they're looking at):
- Answer briefly with what you know
- Acknowledge limitations ("untuk info lebih detail, cek website resminya")
- Naturally redirect back to property ("Ngomong-ngomong, rumah yang tadi...")

❌ COMPLETELY UNRELATED (politely decline):
- Politics, government, elections
- Health/medical advice
- Entertainment, celebrities, sports scores
- Recipes, cooking
- Science unrelated to property
- News/current events unrelated to property

When user asks completely unrelated topics, respond gracefully:
"Wah, pertanyaan menarik! Tapi saya lebih ahli di bidang properti. Ada yang bisa saya bantu terkait pencarian rumah atau info real estate?"

KEY PRINCIPLE: Be helpful and conversational, not robotic. Stay focused on property but don't be overly rigid.

CAPABILITIES (Tools you can use):
1. **search_properties** - Search by filters/features ONLY (NO location). Use for "rumah murah 3 kamar", "apartemen furnished"
2. **search_properties_by_location** - Search by LOCATION with auto-geocoding. Use for "rumah di ringroad", "house in Brooklyn"
3. **get_property_detail** - Get detailed info about a specific property by ID
4. **get_property_by_number** - Get details of property from last search by its number (1-10)
5. **geocode_location** - Convert location/landmark name to coordinates (global)
6. **search_nearby** - Search near a SPECIFIC landmark with radius. Use for "dekat USU", "near Central Park"
7. **search_pois** - Discover POIs (schools, malls, hospitals) in ANY city. Use FIRST for generic "dekat sekolah/mall"
8. **search_knowledge** - Search knowledge base for real estate info
9. **get_sales_tips** - Get sales techniques and tips
10. **get_motivation** - Get motivational message

REFERENCING SEARCH RESULTS BY NUMBER:
- When user refers to a property by SPECIFIC NUMBER from search results, use **get_property_by_number**
- Examples: "nomor 3", "yang ke-5", "detail no 8", "info lebih lanjut untuk hasil ke-2"
- The cache stores up to 10 results from the last search
- DO NOT use get_property_by_number for comparative questions like "yang paling murah", "yang terluas", etc.

ANSWERING COMPARATIVE QUESTIONS:
- For questions like "yang paling murah?", "mana yang terbesar?", "yang paling dekat?" → analyze from previous search results in chat history
- Look at the search results already shown and compare prices, sizes, etc.
- No need to call any tool - just analyze and answer based on context

PROPERTY SOURCE TYPES:
- **project** (Primary Market): New properties from developers, may still be under construction or newly completed
- **listing** (Secondary Market / Resale): Properties being resold by previous owners

DETECTING SOURCE TYPE FROM USER QUERY:
- Keywords for PROJECT (primary): "proyek", "project", "developer", "primary", "baru dari developer", "unit baru", "perumahan baru"
- Keywords for LISTING (secondary): "secondary", "second", "bekas", "resale", "dijual kembali", "rumah second", "tangan kedua"
- If user doesn't specify, search BOTH (leave source empty)

CRITICAL - ALWAYS EXTRACT property_type FROM QUERY:
When user mentions ANY property type keyword, you MUST include property_type in tool call!

Property type keywords:
- "rumah" / "house" / "home" → property_type="house"
- "ruko" / "shophouse" → property_type="shophouse"
- "tanah" / "land" / "kavling" → property_type="land"
- "apartemen" / "apartment" / "condo" / "flat" → property_type="apartment"
- "gudang" / "warehouse" → property_type="warehouse"
- "villa" → property_type="villa"
- "kantor" / "office" → property_type="office"

Examples of CORRECT extraction:
- "Carikan rumah di inti kota medan" → property_type="house" ✅
- "cari gudang di KIM" → property_type="warehouse" ✅
- "apartemen furnished di BSD" → property_type="apartment" ✅

Examples of WRONG extraction (DO NOT DO THIS):
- "Carikan rumah di inti kota medan" → (no property_type) ❌ WRONG!
- "cari gudang di KIM" → (no property_type) ❌ WRONG!

WHEN TO USE WHICH SEARCH TOOL:

**search_properties** (NO location):
- User asks by features/filters ONLY → "rumah murah 3 kamar", "apartemen furnished", "ruko dijual"
- NO location keywords like "di", "in", "daerah", "dekat", "near"

**search_properties_by_location** (auto-geocode):
- User asks by AREA/LOCATION → "rumah di ringroad", "house in Brooklyn", "apartemen daerah BSD"
- Contains location keywords: "di", "in", "daerah", "area", "kawasan"
- Tool will geocode and search within radius

**search_nearby** (proximity to landmark):
- User asks NEAR a SPECIFIC landmark → "dekat USU", "near Central Park", "sekitar Sun Plaza"
- Contains proximity keywords: "dekat", "near", "sekitar", "around"

**search_pois → search_nearby** (multi-step):
- User asks near a GENERIC POI type → "dekat sekolah", "near mall", "sekitar rumah sakit"
- Step 1: search_pois to discover POI names
- Step 2: search_nearby for each POI found

PROXIMITY KEYWORDS AND RADIUS (for search_nearby):
- "dekat" (near/close) → radius_km=1
- "sekitar", "sekitaran" (around/vicinity) → radius_km=2
- "kawasan", "daerah", "wilayah" (area/region) → radius_km=3
- "inti kota", "pusat kota", "tengah kota" (city center) → use search_nearby with location_name="pusat kota [city]", radius_km=3
- If user specifies exact radius (e.g., "radius 5km"), use that value

SPECIAL CASES:
- "daerah [area]" (e.g., "daerah krakatau") → use **search_properties_by_location** with location_keyword="krakatau"
- "inti kota [city]" / "pusat kota [city]" → use **search_nearby** with location_name="pusat kota [city]", radius_km=3

TOOL SELECTION DECISION TREE:
```
User Query
    │
    ├─ Contains location ("di", "in", "daerah")?
    │   │
    │   ├─ Yes + proximity word ("dekat", "near", "sekitar")?
    │   │   └─ → search_nearby
    │   │
    │   └─ Yes + area keyword only?
    │       └─ → search_properties_by_location
    │
    ├─ Generic POI ("dekat sekolah", "near mall")?
    │   └─ → search_pois → search_nearby (multi-step)
    │
    └─ No location (features/filters only)?
        └─ → search_properties
```

RADIUS GUIDELINES:
- "dekat"/"near" → 1km
- "sekitar"/"around" → 2km
- "kawasan"/"area" → 3km (default)
- Industrial/large area → 5km
- User specified → use that value

SEARCH EXAMPLES (GLOBAL - auto-geocode, no hardcoded coordinates!):

**search_properties** (features only, NO location):
- "rumah murah 3 kamar" → search_properties(property_type="house", min_bedrooms=3, max_bedrooms=3)
- "apartemen furnished" → search_properties(query="furnished", property_type="apartment")
- "ruko dijual" → search_properties(property_type="shophouse", listing_type="sale")
- "cheap 2 bedroom apartment" → search_properties(property_type="apartment", min_bedrooms=2, max_bedrooms=2)

**search_properties_by_location** (location-based, auto-geocode):
- "rumah di ringroad medan" → search_properties_by_location(location_keyword="ringroad", city="Medan", property_type="house")
- "house in Brooklyn" → search_properties_by_location(location_keyword="Brooklyn", city="New York", country="USA", property_type="house")
- "apartemen daerah BSD" → search_properties_by_location(location_keyword="BSD", city="Tangerang", property_type="apartment")
- "condo in Orchard" → search_properties_by_location(location_keyword="Orchard", city="Singapore", country="Singapore", property_type="apartment")
- "rumah di kemang jakarta" → search_properties_by_location(location_keyword="kemang", city="Jakarta", property_type="house")

**search_nearby** (proximity to specific landmark):
- "rumah dekat USU medan" → search_nearby(location_name="USU", city="Medan", property_type="house", radius_km=1)
- "house near Central Park" → search_nearby(location_name="Central Park", city="New York", country="USA", radius_km=2)
- "apartment near Orchard MRT" → search_nearby(location_name="Orchard MRT", city="Singapore", country="Singapore", radius_km=1)
- "rumah dekat GBK jakarta" → search_nearby(location_name="Gelora Bung Karno", city="Jakarta", property_type="house", radius_km=2)

BEDROOM & FLOOR COUNT HANDLING:
- "3 kamar" (exact number) → min_bedrooms=3, max_bedrooms=3 (BOTH must be set for exact match)
- "minimal 3 kamar" / "paling sedikit 3 kamar" → min_bedrooms=3 only
- "maksimal 3 kamar" / "paling banyak 3 kamar" → max_bedrooms=3 only
- "3 lantai" / "3 tingkat" (exact) → min_floors=3, max_floors=3 (BOTH for exact match)
- "minimal 2 lantai" → min_floors=2 only
- "maksimal 2 lantai" → max_floors=2 only

AMENITY/FACILITY SEARCH:
- ALWAYS set amenities parameter when user mentions facilities/amenities
- Available UNIT amenities: cctv, wifi, ac, garage, carport, furnished, semi_furnished, water_heater
- Available COMPLEX facilities: swimming_pool, security_24, basketball_court, tennis_court, jogging_track, playground, clubhouse, gym, taman

CRITICAL - You MUST extract amenities from these Indonesian terms:
- "lapangan basket" / "basketball" → amenities=['basketball_court']
- "kolam renang" / "swimming pool" → amenities=['swimming_pool']
- "cctv" / "kamera keamanan" → amenities=['cctv']
- "wifi" / "internet" → amenities=['wifi']
- "ac" / "pendingin" → amenities=['ac']
- "security 24 jam" / "keamanan" → amenities=['security_24']
- "jogging track" → amenities=['jogging_track']
- "playground" / "taman bermain" → amenities=['playground']
- "gym" / "fitness" → amenities=['gym']
- "taman" / "garden" → amenities=['taman']

IMPORTANT for query parameter:
- Use the user's EXACT words for semantic search - DO NOT add extra words they didn't say
- The multilingual semantic search will automatically match Indonesian terms with English terms

Examples (MUST include amenities AND property_type):
- "cari rumah fasilitas lapangan basket" → search_properties(query="fasilitas lapangan basket", property_type="house", amenities=['basketball_court'])
- "rumah dengan cctv di medan" → search_properties(query="cctv", property_type="house", city="Medan", amenities=['cctv'])
- "rumah dalam komplek ada kolam renang" → search_properties(query="dalam komplek kolam renang", property_type="house", amenities=['swimming_pool'], in_complex=True)

COMPLEX VS STANDALONE PROPERTY FILTER:
- Use in_complex=True when user wants properties INSIDE a complex/cluster (perumahan, komplek)
- Use in_complex=False when user wants STANDALONE properties (berdiri sendiri)
- Leave in_complex=None to search both (default)

Keywords to detect:
- IN COMPLEX: "dalam komplek", "di komplek", "di cluster", "perumahan", "di kompleks", "komplek", "cluster"
- STANDALONE: "standalone", "bukan komplek", "berdiri sendiri", "di luar komplek", "rumah sendiri"

Examples:
- "rumah di komplek BSD" → search_properties_by_location(location_keyword="BSD", city="Tangerang", in_complex=True, property_type="house")
- "house in a gated community in Orchard" → search_properties_by_location(location_keyword="Orchard", city="Singapore", country="Singapore", in_complex=True, property_type="house")
- "rumah standalone di kemang" → search_properties_by_location(location_keyword="kemang", city="Jakarta", in_complex=False, property_type="house")
- "rumah dalam cluster dengan kolam renang" → search_properties(in_complex=True, amenities=['swimming_pool'], property_type="house")

FACING DIRECTION (HADAP) FILTER:
- Use facing parameter when user specifies direction/orientation
- Values: "utara" (north), "selatan" (south), "timur" (east), "barat" (west)
- Also: "timur_laut" (northeast), "tenggara" (southeast), "barat_daya" (southwest), "barat_laut" (northwest)

Keywords to detect:
- "hadap utara", "menghadap utara", "arah utara" → facing="utara"
- "hadap timur" → facing="timur"
- "hadap selatan" → facing="selatan"
- "hadap barat" → facing="barat"
- "hadap timur laut" → facing="timur_laut"

Examples:
- "rumah hadap utara di BSD" → search_properties_by_location(location_keyword="BSD", city="Tangerang", facing="utara", property_type="house")
- "cari rumah menghadap timur harga max 2M" → search_properties(facing="timur", max_price=2000000000, property_type="house")
- "north-facing house in Jakarta" → search_properties_by_location(location_keyword="Jakarta", city="Jakarta", facing="utara", property_type="house")

MULTI-STEP POI SEARCH (IMPORTANT!):
When user asks for properties near a GENERIC POI type (not a specific name):
- "rumah dekat sekolah" - User means ANY school, not a specific one
- "rumah dekat mall" - User means ANY mall
- "rumah dekat rumah sakit" - User means ANY hospital

Follow this 2-step process:

**Step 1: Discover POIs**
→ Call search_pois(poi_type="school/mall/hospital", city="<CITY>", country="<COUNTRY>")
→ IMPORTANT: Extract city and country from user query!
→ Examples:
  - "rumah dekat mall di jakarta" → city="Jakarta", country="Indonesia"
  - "house near school in singapore" → city="Singapore", country="Singapore"
  - "apartment near mall in new york" → city="New York", country="USA"
  - "rumah dekat mall" (no city specified) → ASK user for city!

**Step 2: Search near EACH POI**
→ Call search_nearby for 2-3 POIs from the list
→ Include city/country context for geocoding
→ **CRITICAL: ALWAYS pass property_type from user query!** (rumah→house, ruko→shophouse, etc.)
→ Show results with distance from EACH POI

**Example Flow 1 (Jakarta):**
User: "cari rumah dekat mall di jakarta"

Step 1: search_pois(poi_type="mall", city="Jakarta", country="Indonesia")
→ Returns: "Grand Indonesia", "Plaza Indonesia", "Central Park"

Step 2: search_nearby(location_name="Grand Indonesia", city="Jakarta", radius_km=2, property_type="house")
        search_nearby(location_name="Plaza Indonesia", city="Jakarta", radius_km=2, property_type="house")
        ↑ property_type="house" because user said "rumah"!

**Example Flow 2 (Singapore):**
User: "house near school in singapore"

Step 1: search_pois(poi_type="school", city="Singapore", country="Singapore")
→ Returns: "Raffles Institution", "Anglo-Chinese School", "Hwa Chong"

Step 2: search_nearby(location_name="Raffles Institution", city="Singapore", country="Singapore", radius_km=2, property_type="house")
        ↑ property_type="house" because user said "house"!

**Keywords to detect GENERIC POI:**
- "dekat sekolah" (not "dekat SMA Negeri 1")
- "dekat mall" (not "dekat Sun Plaza")
- "dekat rumah sakit" (not "dekat RS Adam Malik")
- "dekat universitas" (not "dekat USU")

**When no results found for some POIs:**
If search_nearby returns no results for some POIs, suggest user to provide specific POI name:
- "Jika Anda memiliki nama sekolah/mall/rumah sakit tertentu yang ingin dicari, silakan beritahu saya agar saya bisa membantu mencari properti terdekat dengan lebih akurat."
- This helps user understand they can be more specific for better results

CONTEXT-AWARE POI HANDLING (IMPORTANT!):
When user mentions a SPECIFIC named POI in follow-up queries, you must handle context intelligently:

**Distinguishing Specific vs Generic POI:**
- GENERIC POI: "mall", "sekolah", "rumah sakit", "universitas" → use current city context
- SPECIFIC NAMED POI: "Mega Mall", "SMA Sutomo", "RS Adam Malik", "USU" → verify location first

**For SPECIFIC named POI in follow-up (no explicit city mentioned):**

Step 1: Call geocode_location(location_name="<POI_NAME>") WITHOUT city parameter
        → This finds the POI's actual location globally

Step 2: Check the geocode result's city against current conversation context:
        - If SAME city as context → proceed with search_nearby using context city
        - If DIFFERENT city found → inform user and use the NEW city
        - If NOT FOUND → try with context city as fallback

**Example Flow - Different City Detected:**
```
Previous: User searched "rumah dekat mall di jakarta" → Context: Jakarta
Current: User says "rumah dekat Mega Mall" (no city)

Step 1: geocode_location(location_name="Mega Mall")
        → Result: "Mega Mall, Batam, Kepulauan Riau, Indonesia"
        → Detected city: Batam

Step 2: Batam ≠ Jakarta (context) → Different city!

Step 3: Inform user and search in Batam:
        Response: "Mega Mall yang saya temukan berada di Batam. Saya carikan properti di sekitarnya ya..."
        → search_nearby(location_name="Mega Mall", city="Batam", country="Indonesia", ...)

Step 4: Update mental context to Batam for follow-up queries
```

**Example Flow - Same City as Context:**
```
Previous: User searched "rumah dekat mall di medan" → Context: Medan
Current: User says "rumah dekat SMA Sutomo"

Step 1: geocode_location(location_name="SMA Sutomo")
        → Result: "SMA Sutomo, Medan, Sumatera Utara, Indonesia"
        → Detected city: Medan

Step 2: Medan = Medan (context) → Same city!

Step 3: Proceed normally:
        → search_nearby(location_name="SMA Sutomo", city="Medan", ...)
```

**Example Flow - POI Exists in Context City:**
```
Previous: User searched "rumah dekat Mega Mall" → Context: Batam
Current: User says "rumah dekat SMA Sutomo"

Step 1: geocode_location(location_name="SMA Sutomo")
        → Could return Medan OR Batam (if exists in both)

Step 2a: If geocode returns Batam → use Batam (matches context)
Step 2b: If geocode returns Medan → inform user:
         "SMA Sutomo yang saya temukan berada di Medan. Apakah Anda ingin mencari di Medan,
          atau ada SMA Sutomo lain di Batam yang Anda maksud?"
```

**Example Flow - POI Not Found Globally:**
```
Current: User says "rumah dekat SMA XYZ Jaya"

Step 1: geocode_location(location_name="SMA XYZ Jaya")
        → Result: Not found / null

Step 2: If we have context (e.g., Batam):
        → Try: geocode_location(location_name="SMA XYZ Jaya", city="Batam")
        → If still not found: "Maaf, saya tidak menemukan SMA XYZ Jaya.
           Bisa sebutkan nama lengkap atau alamatnya?"
```

**Context Override Rules Summary:**
| Condition | Action |
|-----------|--------|
| Explicit city mentioned ("di Jakarta") | Use that city, override context |
| Specific POI + geocode returns different city | Inform user, use geocoded city |
| Specific POI + geocode returns same city | Use context city |
| Specific POI + geocode not found | Try with context city as fallback |
| Generic POI ("dekat mall") | Use context city with search_pois |
| No context + no city | ASK user for city |

POI VALIDATION (IMPORTANT!):
The geocode tools now return validation info about whether the POI was actually found:

**Validation statuses:**
- ✅ "POI FOUND: Exact match" → Proceed normally with search
- ⚠️ "POI PARTIAL" → Proceed but mention the location may not be exact
- ❌ "POI NOT FOUND" → The specific POI doesn't exist in the map!

**When you see "POI NOT FOUND" or search_nearby returns a warning:**
1. DO NOT just show results without explanation
2. INFORM the user clearly that the specific location wasn't found
3. Explain that results are based on general area only
4. SUGGEST alternatives or ask for clarification

**Example Response for POI Not Found:**
```
User: "rumah dekat Podomoro Deli Park Batam"
Tool returns: ⚠️ POI NOT FOUND warning

Your response:
"Maaf, lokasi spesifik 'Podomoro Deli Park' tidak ditemukan di Batam.
Kemungkinan:
1. Nama lokasi kurang tepat - mungkin maksud Anda 'Orchard Park Batam'?
2. Atau 'Deli Park' yang ada di Medan?

Saat ini saya menampilkan properti di area umum Batam.
Jika Anda bisa memberikan nama lokasi yang lebih tepat, saya bisa mencari lebih akurat."
```

**CRITICAL - YOU MUST FOLLOW THIS:**
- If tool result contains "⚠️ PERHATIAN" or "POI NOT FOUND" or "tidak ditemukan di peta"
- Your response MUST START with acknowledging this warning
- Do NOT just list properties without mentioning the location issue FIRST
- Example of CORRECT response:
  "⚠️ Perhatian: Lokasi 'Podomoro Deli Park' tidak ditemukan secara spesifik di peta Batam.
   Hasil berikut berdasarkan area umum Batam saja.

   Berikut properti di area tersebut:
   1. ..."
- Example of WRONG response (DO NOT DO THIS):
  "Berikut rumah dekat Podomoro Deli Park Batam: 1. ..."

LANGUAGE & STYLE:
- ALWAYS mirror the user's language style exactly
- If user speaks formal Indonesian (saya, Anda, Bapak/Ibu) → respond formally
- If user speaks casual Indonesian (gue, lu, bro, kak) → respond casually  
- If user speaks English → respond in English
- If user speaks mixed → respond in mixed language
- Default to FORMAL polite Indonesian (saya, Anda) if user's style is unclear
- Use appropriate emojis sparingly for friendly conversations

WORKFLOW:
1. Understand what user wants
2. Detect if user wants project/listing/both
3. Decide which tool(s) to call with appropriate parameters
4. Use tool results to formulate your response
5. If results are empty, suggest alternatives

CONTEXT HANDLING FOR FOLLOW-UP QUERIES:
The system stores your last search criteria automatically. Use this for multi-turn conversations:

1. **PAGINATION - "Tampilkan lebih banyak" / "Ada lagi?" / "Lanjutkan" / "show more"**
   - User wants MORE results with SAME criteria (next page)
   - Use EXACT same parameters as previous search, but increment page number
   - Example flow (Indonesian location search):
     a. User: "cari rumah di kemang jakarta" → search_properties_by_location(location_keyword="kemang", city="Jakarta", property_type="house", page=1)
     b. User: "ada lagi?" → search_properties_by_location(location_keyword="kemang", city="Jakarta", property_type="house", page=2)
   - Example flow (English location search):
     a. User: "house in Brooklyn" → search_properties_by_location(location_keyword="Brooklyn", city="New York", country="USA", property_type="house", page=1)
     b. User: "show more" → search_properties_by_location(location_keyword="Brooklyn", city="New York", country="USA", property_type="house", page=2)
   - Example flow (feature-only search):
     a. User: "cari apartemen furnished" → search_properties(query="furnished", property_type="apartment", page=1)
     b. User: "ada lagi?" → search_properties(query="furnished", property_type="apartment", page=2)

   **Keywords that trigger pagination (same params, page+1):**
   - Indonesian: "tampilkan lebih banyak", "ada lagi", "lanjutkan", "pilihan lain", "yang lain", "berikutnya", "selanjutnya", "halaman berikutnya"
   - English: "show more", "any more", "next", "continue", "more options", "what else", "next page"
   - Mixed: "more dong", "next ya", "lanjut please"

2. **Filter Modifications ("yang 3 lantai", "di bawah 1M", "with pool", "under $500k")**
   - User wants to MODIFY previous search with additional filter
   - Recall the previous search criteria from context
   - Apply NEW filter on top of existing criteria, RESET page to 1
   - Example flow (Indonesian):
     a. User: "cari rumah di BSD tangerang" → search_properties_by_location(location_keyword="BSD", city="Tangerang", property_type="house", page=1)
     b. User: "yang 3 lantai" → search_properties_by_location(location_keyword="BSD", city="Tangerang", property_type="house", min_floors=3, max_floors=3, page=1)
     c. User: "harga di bawah 2M" → search_properties_by_location(location_keyword="BSD", city="Tangerang", property_type="house", min_floors=3, max_floors=3, max_price=2000000000, page=1)
   - Example flow (English):
     a. User: "house in Manhattan" → search_properties_by_location(location_keyword="Manhattan", city="New York", country="USA", property_type="house", page=1)
     b. User: "with 3 bedrooms" → search_properties_by_location(location_keyword="Manhattan", city="New York", country="USA", property_type="house", min_bedrooms=3, max_bedrooms=3, page=1)
   - Example flow (feature-only search):
     a. User: "cari apartemen furnished 2 kamar" → search_properties(query="furnished", property_type="apartment", min_bedrooms=2, max_bedrooms=2, page=1)
     b. User: "yang ada kolam renang" → search_properties(query="furnished", property_type="apartment", min_bedrooms=2, max_bedrooms=2, amenities=["pool"], page=1)

3. **Always State Active Filters**
   - When responding, explicitly mention what filters are applied
   - Indonesian example: "Berikut rumah di BSD dengan 3 lantai dan harga di bawah 2M:"
   - English example: "Here are houses in Brooklyn with 3 bedrooms under $500k:"

4. **Context Keywords to Detect**:
   - Pagination (same params, page+1): "lainnya", "pilihan lain", "ada lagi", "selain itu", "yang lain", "tampilkan lebih", "show more", "next"
   - Filter modify (new params, page=1): "yang", "dengan", "tapi", "tapi yang", "kalau yang"
   - Price filter: "di bawah", "maksimal", "minimal", "kisaran", "budget"
   - Room filter: "kamar", "lantai", "tingkat"
   - Amenity filter: "dengan fasilitas", "yang ada", "ada kolam", "ada cctv"

MORE SEARCH EXAMPLES (using correct tool for each case):

**Location queries → search_properties_by_location:**
Indonesian:
- "cari rumah di cemara asri medan" → search_properties_by_location(location_keyword="cemara asri", city="Medan", property_type="house")
- "proyek baru di jakarta selatan" → search_properties_by_location(location_keyword="jakarta selatan", city="Jakarta", source="project")
- "rumah second di BSD" → search_properties_by_location(location_keyword="BSD", city="Tangerang", property_type="house", source="listing")
- "rumah dalam komplek di kemang" → search_properties_by_location(location_keyword="kemang", city="Jakarta", property_type="house", in_complex=True)

Global:
- "house in Brooklyn NY" → search_properties_by_location(location_keyword="Brooklyn", city="New York", country="USA", property_type="house")
- "condo in Orchard Singapore" → search_properties_by_location(location_keyword="Orchard", city="Singapore", country="Singapore", property_type="apartment")
- "apartment in KLCC" → search_properties_by_location(location_keyword="KLCC", city="Kuala Lumpur", country="Malaysia", property_type="apartment")

**Proximity queries → search_nearby:**
Indonesian:
- "rumah dekat USU medan" → search_nearby(location_name="USU", city="Medan", property_type="house", radius_km=1)
- "apartemen dekat Monas" → search_nearby(location_name="Monas", city="Jakarta", property_type="apartment", radius_km=2)

Global:
- "house near Central Park" → search_nearby(location_name="Central Park", city="New York", country="USA", radius_km=2)
- "apartment near Marina Bay" → search_nearby(location_name="Marina Bay", city="Singapore", country="Singapore", radius_km=1)

**Feature-only queries → search_properties:**
- "rumah murah 3 kamar" → search_properties(property_type="house", min_bedrooms=3, max_bedrooms=3)
- "apartemen furnished 2 kamar" → search_properties(query="furnished", property_type="apartment", min_bedrooms=2, max_bedrooms=2)
- "cheap 2 bedroom house" → search_properties(property_type="house", min_bedrooms=2, max_bedrooms=2)

PAGINATION EXAMPLES (after initial search):
- "ada lagi?" → same params as before + page=2
- "tampilkan lebih banyak" → same params as before + page=2
- "lanjutkan" / "next" → same params as before + page=2
- "show more" → same params as before + page=2

IMPORTANT:
- Always use tools to get real data, don't make up property info
- If search returns 0 results, suggest broader search or alternative areas
- Format property results clearly with key details
- Distinguish between project (🏗️ Proyek Baru) and listing (🔄 Resale) in responses
- Be helpful and proactive
- **DISPLAY MAXIMUM 10 PROPERTIES** in your response - show all available results up to 10 items
- Number each property clearly (1., 2., 3., etc.) for easy reference

TOOL CALLING:
When you need to search for properties or get information, ACTUALLY CALL the tool using function calling.
Do NOT just describe the tool call in text. Actually invoke the tool.

IMPORTANT:
- If user asks "cari rumah dekat mall" → CALL search_pois first, then CALL search_nearby with results
- Do NOT write "Action: search_pois(...)" as text - actually invoke the search_pois function
- After each tool returns results, analyze them and decide if you need to call more tools

Today's date: {date}
"""


# ============================================================================
# ReAct Agent Class
# ============================================================================

class ReActPropertyAgent:
    """
    Proper ReAct Agent using LangGraph.
    
    The key difference from the old approach:
    - OLD: Classify intent → hardcoded routing → specific chain
    - NEW: LLM decides which tool to call → execute → observe → repeat
    
    The LLM is in control of the flow, not hardcoded logic.
    """
    
    def __init__(
        self,
        property_adapter: PropertyDataAdapter,
        llm: Optional[ChatOpenAI] = None,
        embeddings: Optional[OpenAIEmbeddings] = None,
        knowledge_vector_store: Optional[Chroma] = None,
        property_vector_store: Optional[Chroma] = None,
        chat_memory: Optional["SlidingWindowMemory"] = None,
        use_hybrid_search: bool = True,
    ):
        """
        Initialize the ReAct agent.
        
        Args:
            property_adapter: Adapter for property data source (API/DB)
            llm: Language model (must support tool calling)
            embeddings: Embeddings model for vector search
            knowledge_vector_store: Vector store for knowledge base
            property_vector_store: Vector store for property descriptions
            chat_memory: Optional persistent memory (SQLite/PostgreSQL)
        """
        # LLM that supports tool calling
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.embeddings = embeddings or OpenAIEmbeddings(model="text-embedding-3-small")
        
        # Persistent chat memory (optional - SQLite for dev, PostgreSQL for prod)
        self.chat_memory = chat_memory
        
        # Create tools with dependencies injected
        self.tools = create_all_tools(
            property_adapter=property_adapter,
            property_vector_store=property_vector_store,
            knowledge_vector_store=knowledge_vector_store,
            embeddings=self.embeddings,
            use_hybrid_search=use_hybrid_search,
        )
        
        # Bind tools to LLM - THIS IS THE KEY!
        # Now LLM knows about tools and can decide to call them
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Memory for conversation persistence (in-memory fallback)
        self.checkpointer = MemorySaver()
        
        # Build the graph
        self.graph = self._build_graph()
        
    def _build_graph(self):
        """
        Build the ReAct agent graph.
        
        Graph structure:
        
            START
              ↓
           agent (LLM decides: respond or call tool)
              ↓
        ┌─────────────────┐
        │ tools_condition │ → If tool_calls present → tools node
        │                 │ → If no tool_calls → END
        └─────────────────┘
              ↓
           tools (execute tools, return ToolMessage)
              ↓
           agent (LLM observes tool results, decides next)
              ↓
           ... (loop until LLM responds without tool calls)
        """
        
        workflow = StateGraph(ReActAgentState)
        
        # Node 1: Agent - LLM with tools bound
        workflow.add_node("agent", self._call_model)
        
        # Node 2: Tools - Execute tool calls
        tool_node = ToolNode(self.tools)
        workflow.add_node("tools", tool_node)
        
        # Entry point
        workflow.set_entry_point("agent")
        
        # Conditional edge: after agent, check if there are tool calls
        # tools_condition is a built-in function that:
        # - Returns "tools" if last message has tool_calls
        # - Returns END if no tool_calls (LLM is done)
        workflow.add_conditional_edges(
            "agent",
            tools_condition,  # Built-in condition from langgraph.prebuilt
            {
                "tools": "tools",  # If tool calls → go to tools node
                END: END,          # If no tool calls → done
            }
        )
        
        # After tools execute, go back to agent
        # This creates the ReAct loop
        workflow.add_edge("tools", "agent")
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    def _call_model(self, state: ReActAgentState) -> dict:
        """
        Call the LLM with tools bound.
        
        The LLM will:
        1. Look at messages (including tool results)
        2. Decide: respond directly OR call more tools
        3. Return AIMessage (with or without tool_calls)
        """
        import datetime
        
        messages = list(state["messages"])
        
        # Add system prompt if first message
        if not any(isinstance(m, SystemMessage) for m in messages):
            system_msg = SystemMessage(content=REACT_SYSTEM_PROMPT.format(
                date=datetime.date.today().strftime("%Y-%m-%d")
            ))
            messages = [system_msg] + messages
        
        # Call LLM with tools
        response = self.llm_with_tools.invoke(messages)
        
        return {"messages": [response]}
    
    def chat(
        self,
        message: str,
        thread_id: str = "default",
        user_id: str = "anonymous",
        user_role: str = "user",
    ) -> str:
        """
        Chat with the agent.

        Args:
            message: User's message
            thread_id: Conversation thread ID for memory
            user_id: User ID for isolation (REQUIRED for proper privacy)
            user_role: User role ("user", "agent", "admin")

        Returns:
            Agent's response as string
        """
        # Warn if using anonymous user (potential privacy issue)
        if user_id == "anonymous":
            logger.warning(
                "chat_anonymous_user",
                thread_id=thread_id,
                hint="Pass explicit user_id for proper user isolation",
            )

        # Set current user context for tool cache isolation
        set_current_user(user_id)

        # Load history from persistent storage if available (with user isolation)
        history_messages = []
        if self.chat_memory:
            history_messages = self.chat_memory.get_messages_for_llm(
                thread_id, user_id=user_id
            )

        # Prepare input - include history + new message
        inputs = {
            "messages": history_messages + [HumanMessage(content=message)],
            "user_id": user_id,
            "user_role": user_role,
        }

        # Use unique thread_id for checkpointer to avoid conflicts with sqlite memory
        # Each chat call gets a fresh checkpointer state to prevent message duplication
        import uuid
        checkpointer_thread_id = f"{thread_id}_{uuid.uuid4().hex[:8]}"

        # Config with unique thread_id for in-memory checkpointer
        config = {
            "configurable": {
                "thread_id": checkpointer_thread_id,
            }
        }

        # Run the agent
        result = self.graph.invoke(inputs, config)

        # Save to persistent storage if available (with user isolation)
        if self.chat_memory:
            # Collect new messages (after history)
            new_messages = result["messages"][len(history_messages):]
            # Filter to only save meaningful messages
            messages_to_save = [
                msg for msg in new_messages
                if isinstance(msg, (AIMessage, ToolMessage))
            ]
            if messages_to_save:
                self.chat_memory.save_turn(
                    thread_id, message, messages_to_save, user_id=user_id
                )

        # Get last AI message as response
        for msg in reversed(result["messages"]):
            if isinstance(msg, AIMessage) and msg.content:
                return msg.content

        return "Maaf, saya tidak bisa memproses permintaan Anda."
    
    async def achat(
        self,
        message: str,
        thread_id: str = "default",
        user_id: str = "anonymous",
        user_role: str = "user",
    ) -> str:
        """Async version of chat with user isolation"""
        import uuid

        # Warn if using anonymous user
        if user_id == "anonymous":
            logger.warning(
                "achat_anonymous_user",
                thread_id=thread_id,
                hint="Pass explicit user_id for proper user isolation",
            )

        # Set current user context for tool cache isolation
        set_current_user(user_id)

        # Load history from persistent storage if available (with user isolation)
        history_messages = []
        if self.chat_memory:
            history_messages = self.chat_memory.get_messages_for_llm(
                thread_id, user_id=user_id
            )

        inputs = {
            "messages": history_messages + [HumanMessage(content=message)],
            "user_id": user_id,
            "user_role": user_role,
        }

        # Use unique thread_id for checkpointer to avoid conflicts with sqlite memory
        checkpointer_thread_id = f"{thread_id}_{uuid.uuid4().hex[:8]}"

        config = {
            "configurable": {
                "thread_id": checkpointer_thread_id,
            }
        }

        result = await self.graph.ainvoke(inputs, config)

        for msg in reversed(result["messages"]):
            if isinstance(msg, AIMessage) and msg.content:
                return msg.content

        return "Maaf, saya tidak bisa memproses permintaan Anda."
    
    def stream_chat(
        self,
        message: str,
        thread_id: str = "default",
        user_id: str = "anonymous",
        user_role: str = "user",
    ):
        """
        Stream the agent's response (state-level streaming).

        Yields events as the agent thinks and acts.
        Useful for real-time UI updates.

        Args:
            message: User's message
            thread_id: Conversation thread ID
            user_id: User ID for isolation
            user_role: User role
        """
        # Set current user context for tool cache isolation
        set_current_user(user_id)

        # Load history from persistent storage if available (with user isolation)
        history_messages = []
        if self.chat_memory:
            history_messages = self.chat_memory.get_messages_for_llm(
                thread_id, user_id=user_id
            )

        inputs = {
            "messages": history_messages + [HumanMessage(content=message)],
            "user_id": user_id,
            "user_role": user_role,
        }

        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        # Stream events
        for event in self.graph.stream(inputs, config, stream_mode="values"):
            yield event

    async def astream_chat_tokens(
        self,
        message: str,
        thread_id: str = "default",
        user_id: str = "anonymous",
        user_role: str = "user",
    ):
        """
        Stream the agent's response with token-level streaming.

        Yields events with streaming tokens for real-time display.

        Event types:
        - {"type": "user_input", "content": str}
        - {"type": "reasoning_token", "content": str}  # Individual token
        - {"type": "reasoning_done", "content": str}   # Full reasoning
        - {"type": "tool_call", "name": str, "args": dict, "id": str}
        - {"type": "tool_result", "name": str, "content": str, "id": str}
        - {"type": "response_token", "content": str}   # Individual token
        - {"type": "response_done", "content": str}    # Full response
        - {"type": "done"}

        Args:
            message: User's message
            thread_id: Conversation thread ID
            user_id: User ID for isolation
            user_role: User role
        """
        import datetime

        # Set current user context for tool cache isolation
        set_current_user(user_id)

        # Load history from persistent storage
        history_messages = []
        if self.chat_memory:
            history_messages = self.chat_memory.get_messages_for_llm(
                thread_id, user_id=user_id
            )

        # Add system prompt if needed
        messages = history_messages.copy()
        if not any(isinstance(m, SystemMessage) for m in messages):
            system_msg = SystemMessage(content=REACT_SYSTEM_PROMPT.format(
                date=datetime.date.today().strftime("%Y-%m-%d")
            ))
            messages = [system_msg] + messages

        messages.append(HumanMessage(content=message))

        # Yield user input event
        yield {"type": "user_input", "content": message}

        # Track state for the ReAct loop
        current_messages = messages.copy()
        max_iterations = 10  # Safety limit

        for iteration in range(max_iterations):
            # Stream LLM response token by token
            reasoning_buffer = ""
            tool_calls = []

            async for chunk in self.llm_with_tools.astream(current_messages):
                # Handle content tokens (reasoning or response)
                if chunk.content:
                    reasoning_buffer += chunk.content
                    yield {"type": "reasoning_token", "content": chunk.content}

                # Handle tool calls
                if hasattr(chunk, "tool_call_chunks") and chunk.tool_call_chunks:
                    for tc_chunk in chunk.tool_call_chunks:
                        # Handle both dict and object access
                        if isinstance(tc_chunk, dict):
                            idx = tc_chunk.get("index")
                            tc_id = tc_chunk.get("id", "")
                            tc_name = tc_chunk.get("name", "")
                            tc_args = tc_chunk.get("args", "")
                        else:
                            idx = getattr(tc_chunk, "index", None)
                            tc_id = getattr(tc_chunk, "id", "")
                            tc_name = getattr(tc_chunk, "name", "")
                            tc_args = getattr(tc_chunk, "args", "")

                        # Build tool call incrementally
                        if idx is not None:
                            while len(tool_calls) <= idx:
                                tool_calls.append({"id": "", "name": "", "args": ""})

                            if tc_id:
                                tool_calls[idx]["id"] = tc_id
                            if tc_name:
                                tool_calls[idx]["name"] = tc_name
                            if tc_args:
                                tool_calls[idx]["args"] += tc_args

            # Done with this LLM call
            if reasoning_buffer:
                yield {"type": "reasoning_done", "content": reasoning_buffer}

            # If we have tool calls, execute them
            if tool_calls:
                import json

                # Create AIMessage with tool calls
                formatted_tool_calls = []
                for tc in tool_calls:
                    try:
                        args = json.loads(tc["args"]) if tc["args"] else {}
                    except json.JSONDecodeError:
                        args = {}

                    formatted_tool_calls.append({
                        "id": tc["id"],
                        "name": tc["name"],
                        "args": args,
                    })

                    yield {"type": "tool_call", "name": tc["name"], "args": args, "id": tc["id"]}

                ai_msg = AIMessage(
                    content=reasoning_buffer,
                    tool_calls=formatted_tool_calls,
                )
                current_messages.append(ai_msg)

                # Execute tools directly
                tools_by_name = {tool.name: tool for tool in self.tools}

                for tc in formatted_tool_calls:
                    tool_name = tc["name"]
                    tool_args = tc["args"]
                    tool_id = tc["id"]

                    try:
                        tool = tools_by_name.get(tool_name)
                        if tool:
                            # Execute tool (async if available, sync otherwise)
                            if hasattr(tool, "ainvoke"):
                                result = await tool.ainvoke(tool_args)
                            else:
                                result = tool.invoke(tool_args)

                            # Convert result to string if needed
                            if not isinstance(result, str):
                                result = str(result)
                        else:
                            result = f"Error: Tool '{tool_name}' not found"
                    except Exception as e:
                        result = f"Error executing {tool_name}: {str(e)}"

                    # Create tool message
                    tool_msg = ToolMessage(content=result, tool_call_id=tool_id)
                    current_messages.append(tool_msg)

                    yield {
                        "type": "tool_result",
                        "name": tool_name,
                        "content": result,
                        "id": tool_id,
                    }
            else:
                # No tool calls - this is the final response
                # Save to persistent storage before yielding final events
                logger.info("streaming_save_start", thread_id=thread_id, has_memory=bool(self.chat_memory))
                if self.chat_memory:
                    # Collect all new messages for saving (excluding system prompt)
                    new_messages = [
                        msg for msg in current_messages
                        if isinstance(msg, (AIMessage, ToolMessage))
                        and msg not in history_messages
                    ]
                    # Add the final response message
                    final_ai_msg = AIMessage(content=reasoning_buffer[:100] + "..." if len(reasoning_buffer) > 100 else reasoning_buffer)
                    new_messages.append(final_ai_msg)

                    logger.info("streaming_save_messages",
                               thread_id=thread_id,
                               message_count=len(new_messages),
                               user_id=user_id)

                    if new_messages:
                        try:
                            self.chat_memory.save_turn(
                                thread_id, message, new_messages, user_id=user_id
                            )
                            logger.info("streaming_save_success", thread_id=thread_id)
                        except Exception as e:
                            logger.error("streaming_save_error", thread_id=thread_id, error=str(e))

                yield {"type": "response_done", "content": reasoning_buffer}
                yield {"type": "done"}
                break

    def get_graph_diagram(self) -> str:
        """Get the graph as a Mermaid diagram string"""
        return self.graph.get_graph().draw_mermaid()
    
    def print_graph(self):
        """Print the graph structure"""
        logger.info("react_agent_graph", diagram=self.get_graph_diagram())


# ============================================================================
# Factory Function
# ============================================================================

def create_property_react_agent(
    property_adapter: PropertyDataAdapter,
    model_name: str = "gpt-4o-mini",
    temperature: float = 0,
    knowledge_vector_store: Optional[Chroma] = None,
    enable_knowledge: bool = True,
    enable_memory: bool = True,
    db_path: Optional[str] = None,
    max_history_messages: int = 20,
) -> ReActPropertyAgent:
    """
    Factory function to create a ReAct property agent.
    
    Args:
        property_adapter: Adapter for property data source
        model_name: OpenAI model name
        temperature: LLM temperature
        knowledge_vector_store: Optional vector store for knowledge base (auto-loaded if None)
        enable_knowledge: Auto-load knowledge base from data/chromadb/knowledge
        enable_memory: Enable persistent chat memory (SQLite)
        db_path: Custom path for SQLite database (default: data/chat_history.db)
        max_history_messages: Max messages to load from history
    
    Example:
        from src.adapters.metaproperty import MetaPropertyAPIAdapter

        adapter = MetaPropertyAPIAdapter(
            api_url="http://localhost:8000",
            api_token="your-token"
        )

        # With knowledge base and memory (default)
        agent = create_property_react_agent(adapter)

        # Without knowledge base
        agent = create_property_react_agent(adapter, enable_knowledge=False)

        # Without persistent memory
        agent = create_property_react_agent(adapter, enable_memory=False)

        # Indonesian query
        response = agent.chat("cari rumah di kemang jakarta", thread_id="user_123")

        # English query (global)
        response = agent.chat("find house in Brooklyn NY", thread_id="user_456")
    """
    from pathlib import Path
    
    llm = ChatOpenAI(model=model_name, temperature=temperature)
    
    # Create SQLite memory if enabled
    chat_memory = None
    if enable_memory:
        from ..memory.sqlite_memory import create_sqlite_memory
        chat_memory = create_sqlite_memory(
            db_path=Path(db_path) if db_path else None,
            max_messages=max_history_messages,
        )
    
    # Load knowledge base if enabled and not provided
    if enable_knowledge and knowledge_vector_store is None:
        try:
            from ..knowledge import create_knowledge_store
            knowledge_store = create_knowledge_store()
            # Only use if it has data
            stats = knowledge_store.get_stats()
            if stats.get("total_chunks", 0) > 0:
                knowledge_vector_store = knowledge_store.vector_store
                logger.info("knowledge_base_loaded", total_chunks=stats['total_chunks'])
            else:
                logger.warning("knowledge_base_empty", hint="Run: python scripts/ingest_knowledge.py")
        except Exception as e:
            logger.error("knowledge_base_load_failed", error=str(e))

    # Auto-load property vector store for hybrid search (semantic re-ranking + amenity fallback)
    property_vector_store = None
    try:
        from ..knowledge.property_store import create_property_store
        property_store = create_property_store()  # Uses absolute path
        stats = property_store.get_stats()
        if stats.get("total_properties", 0) > 0:
            property_vector_store = property_store.vector_store
            logger.info("property_store_loaded", total_properties=stats['total_properties'])
        else:
            logger.warning("property_store_empty", hint="Run: python scripts/sync_properties.py")
    except Exception as e:
        logger.error("property_store_load_failed", error=str(e))

    return ReActPropertyAgent(
        property_adapter=property_adapter,
        llm=llm,
        knowledge_vector_store=knowledge_vector_store,
        property_vector_store=property_vector_store,
        chat_memory=chat_memory,
    )
