"""
Enhanced Orchestrator Agent - Full LangGraph Implementation
Routes requests to appropriate agents with memory context
"""

import json
import time
from typing import Literal, Optional, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import AgentState

# System prompt for intent classification
INTENT_CLASSIFIER_PROMPT = """You are an intent classifier for an Indonesian real estate property assistant.

LANGUAGE DETECTION:
Detect the user's language and speaking style:
- language: "en" if user writes in English, "id" if Indonesian
- Also note if user is casual (uses "gue", "lu", "bro", informal) or formal

Analyze the message and classify into one of these categories:

PROPERTY INTENTS:
- property_search: User looking for property. Examples: "Cari rumah di Sunggal", "Find house near USU", "Ada ruko budget 1M?"
- property_update: Agent wants to update listing. Examples: "Update harga jadi 1.5M", "Mark as sold"
- property_description: Request marketing description. Examples: "Buatkan deskripsi", "Write description"

COACHING INTENTS:
- coaching_sales: Sales tips and techniques. Examples: "How to close a deal?", "Tips follow up client"
- coaching_knowledge: Property knowledge questions. Examples: "What is SHM?", "Bedanya SHM dan SHGB?"
- coaching_motivation: Motivation/support needed. Examples: "I need motivation", "Kasih motivasi dong"

OTHER INTENTS:
- greeting: Greetings, thanks. Examples: "Hello", "Halo", "Thank you"
- general: General property-related but not specific
- out_of_scope: Not related to real estate

CONTEXTUAL QUERY HANDLING:
If the message is short and refers to previous context (e.g., "Yang lebih murah?", "Ada yang bagus?", "Yang lain?"):
- Look at CONTEXT to determine if it relates to property search
- If previous context mentions property/rumah/search, classify as property_search
- Words like "lebih", "lain", "bagus", "murah", "besar" usually mean refinement of previous search

LOCATION HANDLING:
For property_search, extract location intelligently:
- Direct areas: "Sunggal", "Helvetia", "Medan Selayang"
- Landmarks/places: "dekat USU" -> location: "USU", nearby: true
- Relative: "sekitar kampus" -> location: "kampus", nearby: true

CONTEXT:
{context}

USER MESSAGE:
{message}

Output JSON ONLY (no markdown):
{{"intent": "<intent>", "confidence": <0.0-1.0>, "language": "id" | "en", "extracted_info": {{}}, "reason": "brief reason"}}

For property_search, extracted_info must include:
- property_type: "rumah" | "ruko" | "tanah" | "apartment" | null
- location: location/area/landmark mentioned | null
- nearby: true if user wants "near/dekat/sekitar" a place | false
- min_price: minimum price in IDR | null
- max_price: maximum price in IDR | null  
- bedrooms: number of bedrooms | null
- features: list of features mentioned
- refinement: "cheaper" | "bigger" | "other" | null (if refining previous search)
"""


class OrchestratorAgent:
    """
    Main orchestrator that routes requests to specialized agents
    Uses LangGraph for state management and flow control
    """
    
    def __init__(
        self, 
        llm: ChatOpenAI | None = None,
        property_agent = None,
        coach_agent = None,
    ):
        """Initialize the orchestrator with specialized agents"""
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.property_agent = property_agent
        self.coach_agent = coach_agent
        
        # Memory for checkpointing
        self.memory = MemorySaver()
        
        # Build and compile the graph
        self.graph = self._build_graph()
        
    def _build_graph(self) -> Any:
        """Build the LangGraph workflow"""
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("classify_intent", self._classify_intent)
        workflow.add_node("load_context", self._load_context)
        workflow.add_node("route_to_agent", self._route_to_agent)
        workflow.add_node("property_agent", self._call_property_agent)
        workflow.add_node("coach_agent", self._call_coach_agent)
        workflow.add_node("handle_greeting", self._handle_greeting)
        workflow.add_node("handle_out_of_scope", self._handle_out_of_scope)
        workflow.add_node("format_response", self._format_response)
        workflow.add_node("save_metrics", self._save_metrics)
        
        # Set entry point
        workflow.set_entry_point("classify_intent")
        
        # Add edges - linear flow first
        workflow.add_edge("classify_intent", "load_context")
        workflow.add_edge("load_context", "route_to_agent")
        
        # Conditional routing based on intent
        workflow.add_conditional_edges(
            "route_to_agent",
            self._get_route,
            {
                "property": "property_agent",
                "coaching": "coach_agent",
                "greeting": "handle_greeting",
                "out_of_scope": "handle_out_of_scope",
            }
        )
        
        # All paths lead to format_response then save_metrics
        workflow.add_edge("property_agent", "format_response")
        workflow.add_edge("coach_agent", "format_response")
        workflow.add_edge("handle_greeting", "format_response")
        workflow.add_edge("handle_out_of_scope", "format_response")
        workflow.add_edge("format_response", "save_metrics")
        workflow.add_edge("save_metrics", END)
        
        return workflow.compile(checkpointer=self.memory)
    
    def _classify_intent(self, state: AgentState) -> dict:
        """Classify the user's intent using LLM"""
        
        # Get context from recent messages
        context = "Tidak ada konteks sebelumnya"
        if state.get("messages") and len(state["messages"]) > 1:
            recent = state["messages"][-4:-1]  # Exclude current message
            context_parts = []
            for m in recent:
                if hasattr(m, 'content'):
                    role = "User" if isinstance(m, HumanMessage) else "Assistant"
                    context_parts.append(f"{role}: {m.content[:150]}")
            if context_parts:
                context = " | ".join(context_parts)
        
        # Call LLM for classification
        prompt = INTENT_CLASSIFIER_PROMPT.format(
            message=state["current_input"],
            context=context
        )
        
        start_time = time.time()
        response = self.llm.invoke([HumanMessage(content=prompt)])
        llm_time = (time.time() - start_time) * 1000
        
        # Parse response
        try:
            # Clean up response - remove markdown code blocks if present
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip()
            
            result = json.loads(content)
            extracted_info = result.get("extracted_info", {})
            
            return {
                "intent": result.get("intent", "general"),
                "confidence": result.get("confidence", 0.8),
                "language": result.get("language", "id"),  # Store detected language
                "extracted_info": extracted_info,  # Store for property/coach agents
                "metrics": {
                    **state.get("metrics", {}),
                    "llm_latency_ms": int(llm_time),
                    "extracted_info": extracted_info,
                }
            }
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback to general if parsing fails
            return {
                "intent": "general",
                "confidence": 0.5,
                "language": "id",  # Default to Indonesian
                "extracted_info": {},
                "metrics": {
                    **state.get("metrics", {}),
                    "llm_latency_ms": int(llm_time),
                    "parse_error": str(e),
                }
            }
    
    def _load_context(self, state: AgentState) -> dict:
        """Load client profile and conversation context from memory"""
        # TODO: Implement actual memory loading from Redis/PostgreSQL
        
        # For now, return placeholder
        return {
            "client_profile": {
                "phone": state.get("client_phone"),
                "name": None,
                "preferred_locations": [],
                "budget_range": None,
            },
            "conversation_context": None,
        }
    
    def _route_to_agent(self, state: AgentState) -> dict:
        """Determine which agent should handle the request"""
        intent = state.get("intent", "general")
        
        if intent in ["property_search", "property_update", "property_description"]:
            routed_to = "property_agent"
        elif intent in ["coaching_sales", "coaching_knowledge", "coaching_motivation"]:
            routed_to = "coach_agent"
        elif intent == "greeting":
            routed_to = "greeting_handler"
        elif intent == "out_of_scope":
            routed_to = "out_of_scope_handler"
        else:
            routed_to = "coach_agent"  # Default to coach for general
            
        return {"routed_to": routed_to}
    
    def _get_route(self, state: AgentState) -> str:
        """Get the route name for conditional edge"""
        routed_to = state.get("routed_to", "coaching")
        
        if routed_to == "property_agent":
            return "property"
        elif routed_to == "coach_agent":
            return "coaching"
        elif routed_to == "greeting_handler":
            return "greeting"
        else:
            return "out_of_scope"
    
    async def _call_property_agent(self, state: AgentState) -> dict:
        """Call the property agent"""
        intent = state.get("intent")
        
        # Use actual property agent if available
        if self.property_agent:
            try:
                if intent == "property_search":
                    result = await self.property_agent.search(state)
                    return result
                elif intent == "property_update":
                    result = await self.property_agent.update_listing(state)
                    return result
                elif intent == "property_description":
                    result = await self.property_agent.generate_description(state)
                    return result
            except Exception as e:
                return {"response": f"⚠️ Error: {str(e)}"}
        
        # Placeholder response if no property agent
        extracted = state.get("metrics", {}).get("extracted_info", {})
        
        if intent == "property_search":
            location = extracted.get("location", "")
            prop_type = extracted.get("property_type", "properti")
            
            response = f"🏠 Mencari {prop_type}"
            if location:
                response += f" di {location}"
            response += "...\n\n"
            response += "Berikut beberapa pilihan untuk Anda:\n"
            response += "1. Rumah 3KT di Sunggal - Rp 1.5M\n"
            response += "2. Rumah Minimalis Medan Selayang - Rp 850jt\n"
            response += "3. Rumah Hook Medan Johor - Rp 980jt\n\n"
            response += "Mau lihat detail yang mana?"
            
        elif intent == "property_update":
            response = "✅ Untuk update listing, tolong berikan:\n"
            response += "1. ID atau nama properti\n"
            response += "2. Data yang ingin diupdate\n"
            
        elif intent == "property_description":
            response = "📝 Saya siap membuatkan deskripsi marketing!\n"
            response += "Tolong berikan detail properti atau ID listing yang ingin dibuatkan deskripsi."
        else:
            response = "🏠 Ada yang bisa saya bantu terkait properti?"
            
        return {"response": response}
    
    async def _call_coach_agent(self, state: AgentState) -> dict:
        """Call the coach agent"""
        intent = state.get("intent")
        
        # Use actual coach agent if available
        if self.coach_agent:
            try:
                result = await self.coach_agent.process(state)
                return result
            except Exception as e:
                print(f"Coach agent error: {e}")
                # Fall through to placeholder
        
        # Placeholder response based on intent
        query = state.get("current_input", "").lower()
        
        if intent == "coaching_sales":
            if "closing" in query or "ragu" in query:
                response = "💡 **Tips Closing Buyer yang Ragu:**\n\n"
                response += "1. **Dengarkan keberatannya** - Jangan langsung counter, pahami dulu\n"
                response += "2. **Tanya alasan spesifik** - \"Apa yang membuat Bapak masih mempertimbangkan?\"\n"
                response += "3. **Berikan jaminan** - Tekankan value dan keuntungan jangka panjang\n"
                response += "4. **Ciptakan urgency** - \"Properti ini banyak diminati\"\n"
                response += "5. **Tawarkan opsi** - Berikan pilihan, bukan yes/no\n\n"
                response += "Mau tips lebih spesifik?"
            elif "follow up" in query:
                response = "📱 **Tips Follow Up yang Efektif:**\n\n"
                response += "1. **Timing tepat** - 24-48 jam setelah viewing\n"
                response += "2. **Berikan value** - Jangan hanya tanya \"gimana?\"\n"
                response += "3. **Multi-channel** - WA, telepon, email\n"
                response += "4. **Personal touch** - Sebut detail percakapan sebelumnya"
            else:
                response = "💼 Saya siap membantu dengan tips penjualan!\n\n"
                response += "Topik apa yang ingin dibahas?\n"
                response += "- Teknik closing\n- Follow up client\n- Handling objection"
                
        elif intent == "coaching_knowledge":
            if "shm" in query or "shgb" in query or "sertifikat" in query:
                response = "📋 **Perbedaan SHM dan SHGB:**\n\n"
                response += "**SHM (Sertifikat Hak Milik):**\n"
                response += "- Hak kepemilikan tertinggi\n- Tidak ada batas waktu\n- Hanya untuk WNI\n\n"
                response += "**SHGB:**\n- Masa berlaku 30+20 tahun\n- Bisa untuk badan hukum\n\n"
                response += "💡 SHM lebih disarankan untuk investasi jangka panjang."
            elif "ajb" in query:
                response = "📜 **AJB (Akta Jual Beli)**\n\n"
                response += "Akta autentik dari PPAT sebagai bukti peralihan hak.\n\n"
                response += "**Fungsi:** Bukti peralihan hak, syarat balik nama\n"
                response += "**Biaya:** ~1% dari nilai transaksi"
            else:
                response = "📚 Saya siap menjawab pertanyaan tentang:\n"
                response += "- Sertifikat (SHM, SHGB)\n- Proses jual beli\n- Pajak properti\n- KPR"
                
        elif intent == "coaching_motivation":
            import random
            motivations = [
                "💪 **Semangat!** Setiap agent sukses pernah merasakan masa sulit. Yang membedakan adalah mereka tidak menyerah!",
                "🌟 **Anda Bisa!** Konsistensi adalah kunci. Keep going! 💪",
                "🔥 **Tetap Semangat!** Setiap 'tidak' membawa Anda lebih dekat ke 'ya' yang besar!",
            ]
            response = random.choice(motivations)
        else:
            response = "Saya siap membantu dengan tips penjualan, pengetahuan properti, atau motivasi!"
            
        return {"response": response}
    
    def _handle_greeting(self, state: AgentState) -> dict:
        """Handle greeting messages with language awareness"""
        import random
        
        query = state.get("current_input", "").lower()
        # Get detected language from state (set by classify_intent)
        lang = state.get("language", "id")
        
        # Also check query for language hints as fallback
        english_words = ["hello", "hi", "thanks", "thank you", "good morning", "good evening"]
        if any(word in query for word in english_words):
            lang = "en"
        
        if lang == "en":
            # English responses
            if "thank" in query:
                responses = [
                    "You're welcome! 😊 Anything else I can help with?",
                    "Happy to help! Feel free to ask anytime 🏠",
                ]
            elif "morning" in query:
                responses = [
                    "Good morning! ☀️ Ready to help you find your dream property!",
                ]
            elif "evening" in query or "night" in query:
                responses = [
                    "Good evening! 🌙 How can I assist you with property today?",
                ]
            else:
                responses = [
                    "Hello! 👋 I'm your property assistant. How can I help you?",
                    "Hi there! 🏠 I can help you with:\n"
                    "- Finding properties\n- Sales tips\n- Real estate knowledge\n\n"
                    "What do you need?",
                ]
        else:
            # Indonesian responses
            if "terima kasih" in query or "makasih" in query:
                responses = [
                    "Sama-sama! 😊 Ada lagi yang bisa saya bantu?",
                    "Senang bisa membantu! Jangan ragu untuk bertanya lagi ya 🏠",
                ]
            elif "pagi" in query:
                responses = [
                    "Selamat pagi! ☀️ Semangat untuk hari ini! Ada yang bisa saya bantu terkait properti?",
                ]
            elif "siang" in query:
                responses = [
                    "Selamat siang! 🌤️ Ada properti yang sedang Anda cari?",
                ]
            elif "malam" in query:
                responses = [
                    "Selamat malam! 🌙 Masih semangat kerja ya! Ada yang bisa dibantu?",
                ]
            else:
                responses = [
                    "Halo! 👋 Saya asisten properti Anda. Ada yang bisa saya bantu?",
                    "Hai! Selamat datang! 🏠 Saya siap membantu Anda dengan:\n"
                    "- Mencari properti\n- Tips penjualan\n- Pengetahuan real estate\n\n"
                    "Apa yang Anda butuhkan?",
                ]
        
        return {"response": random.choice(responses)}
    
    def _handle_out_of_scope(self, state: AgentState) -> dict:
        """Handle out-of-scope requests"""
        response = (
            "🤔 Maaf, saya adalah asisten khusus untuk properti real estate.\n\n"
            "Saya bisa membantu Anda dengan:\n"
            "🏠 Mencari properti (rumah, ruko, tanah, apartment)\n"
            "💼 Tips dan teknik penjualan\n"
            "📚 Pengetahuan real estate (sertifikat, pajak, proses)\n"
            "💪 Motivasi untuk agent\n\n"
            "Ada yang bisa saya bantu terkait properti?"
        )
        return {"response": response}
    
    def _format_response(self, state: AgentState) -> dict:
        """Format the final response and add to messages"""
        # Calculate total metrics
        metrics = state.get("metrics", {})
        if state.get("start_time"):
            elapsed = (time.time() - state["start_time"]) * 1000
            metrics["total_latency_ms"] = int(elapsed)
        
        # Add response to messages
        new_messages = []
        if state.get("response"):
            new_messages = [AIMessage(content=state["response"])]
            
        return {
            "messages": new_messages,
            "metrics": metrics,
        }
    
    def _save_metrics(self, state: AgentState) -> dict:
        """Save metrics to database for thesis analysis"""
        # TODO: Implement actual saving to AgentMetrics table
        
        metrics = state.get("metrics", {})
        metrics["saved"] = True
        metrics["timestamp"] = time.time()
        
        return {"metrics": metrics}
    
    async def process(
        self, 
        message: str, 
        session_id: str, 
        client_phone: str,
        thread_id: str | None = None,
    ) -> dict:
        """
        Process a message through the agent graph
        
        Args:
            message: User message
            session_id: Current session ID
            client_phone: Client's phone number
            thread_id: Thread ID for conversation memory
            
        Returns:
            Response dictionary with message and metadata
        """
        # Initialize state
        initial_state: AgentState = {
            "messages": [HumanMessage(content=message)],
            "current_input": message,
            "session_id": session_id,
            "client_phone": client_phone,
            "intent": None,
            "confidence": 0.0,
            "routed_to": None,
            "language": None,  # Will be detected by classify_intent
            "extracted_info": {},  # Will be populated by classify_intent
            "client_profile": None,
            "conversation_context": None,
            "retrieved_properties": None,
            "property_action_result": None,
            "coaching_response": None,
            "response": None,
            "start_time": time.time(),
            "metrics": {},
        }
        
        # Config for checkpointing
        config = {"configurable": {"thread_id": thread_id or session_id}}
        
        # Run the graph
        result = await self.graph.ainvoke(initial_state, config)
        
        return {
            "response": result.get("response", "Maaf, terjadi kesalahan."),
            "intent": result.get("intent"),
            "confidence": result.get("confidence"),
            "routed_to": result.get("routed_to"),
            "metrics": result.get("metrics", {}),
        }
    
    def process_sync(
        self, 
        message: str, 
        session_id: str, 
        client_phone: str,
        thread_id: str | None = None,
    ) -> dict:
        """Synchronous version of process for testing"""
        import asyncio
        return asyncio.run(self.process(message, session_id, client_phone, thread_id))
