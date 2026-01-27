"""
Coach Agent - Full Implementation with RAG-based Knowledge Retrieval

This agent handles coaching-related queries:
- Sales tips and techniques
- Real estate knowledge (certificates, taxes, processes)
- Motivation and mindset
"""

import os
from pathlib import Path
from typing import Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .state import AgentState


# System prompt for coach agent
COACH_SYSTEM_PROMPT = """You are a helpful real estate coach and mentor for property agents in Indonesia.

Your responsibilities:
1. Provide practical sales tips and techniques
2. Answer questions about real estate knowledge (certificates, taxes, legal processes)
3. Offer motivation and encouragement

LANGUAGE & STYLE RULES:
- Detected user language: {language_instruction}
- ALWAYS respond in the user's language
- Mirror the user's speaking style and tone:
  * If user is formal → respond formally
  * If user is casual ("gue", "gimana", "bro") → respond casually
  * If user mixes languages → you may mix appropriately
- Be warm, supportive, and encouraging
- Use emojis appropriately for friendly tone

CONTENT RULES:
- Give specific, actionable advice
- If you don't know something, say so honestly
- Use the provided context for accurate information

CONTEXT FROM KNOWLEDGE BASE:
{context}

USER QUERY:
{query}

Provide a helpful, friendly response:"""


class CoachAgent:
    """
    Agent for coaching and knowledge-related tasks:
    - Sales techniques (closing, follow-up, objection handling)
    - Real estate knowledge (certificates, taxes, legal)
    - Motivation and mindset
    """
    
    def __init__(
        self,
        llm: Optional[ChatOpenAI] = None,
        embeddings: Optional[OpenAIEmbeddings] = None,
        knowledge_path: str = "data/knowledge-base",
        chroma_path: str = "data/chroma",
    ):
        """
        Initialize CoachAgent.
        
        Args:
            llm: Language model for responses
            embeddings: Embeddings model for knowledge retrieval
            knowledge_path: Path to knowledge base documents
            chroma_path: Path to ChromaDB storage
        """
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        self.embeddings = embeddings or OpenAIEmbeddings(model="text-embedding-3-small")
        self.knowledge_path = Path(knowledge_path)
        self.chroma_path = Path(chroma_path)
        
        # Vector store for knowledge retrieval
        self.vectorstore: Optional[Chroma] = None
        self._knowledge_indexed = False
    
    async def initialize(self):
        """Initialize the agent (index knowledge if needed)"""
        if not self._knowledge_indexed:
            await self.index_knowledge()
    
    async def index_knowledge(self):
        """Index all knowledge base documents into ChromaDB"""
        if not self.knowledge_path.exists():
            print(f"Warning: Knowledge path {self.knowledge_path} not found")
            return
        
        documents = []
        
        # Load all markdown files from knowledge base
        for md_file in self.knowledge_path.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Determine category from path
                relative_path = md_file.relative_to(self.knowledge_path)
                category = relative_path.parts[0] if len(relative_path.parts) > 1 else "general"
                
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": str(md_file),
                        "category": category,
                        "filename": md_file.name,
                    }
                )
                documents.append(doc)
                
            except Exception as e:
                print(f"Error loading {md_file}: {e}")
        
        if not documents:
            print("No knowledge documents found to index")
            return
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n## ", "\n### ", "\n\n", "\n", " "]
        )
        chunks = text_splitter.split_documents(documents)
        
        # Create vector store
        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            collection_name="knowledge",
            persist_directory=str(self.chroma_path),
        )
        
        self._knowledge_indexed = True
        print(f"Indexed {len(chunks)} knowledge chunks from {len(documents)} documents")
    
    async def _retrieve_context(
        self, 
        query: str, 
        category: Optional[str] = None,
        k: int = 3
    ) -> str:
        """Retrieve relevant context from knowledge base"""
        
        if not self.vectorstore:
            # Try to load existing vectorstore
            try:
                self.vectorstore = Chroma(
                    collection_name="knowledge",
                    embedding_function=self.embeddings,
                    persist_directory=str(self.chroma_path),
                )
            except:
                return "No knowledge base available."
        
        # Build filter if category specified
        filter_dict = None
        if category:
            filter_dict = {"category": category}
        
        # Retrieve relevant documents
        try:
            docs = self.vectorstore.similarity_search(
                query, 
                k=k,
                filter=filter_dict,
            )
            
            if not docs:
                return "No relevant information found in knowledge base."
            
            # Combine context
            context_parts = []
            for doc in docs:
                source = doc.metadata.get("filename", "unknown")
                context_parts.append(f"[Source: {source}]\n{doc.page_content}")
            
            return "\n\n---\n\n".join(context_parts)
            
        except Exception as e:
            print(f"Retrieval error: {e}")
            return "Error retrieving from knowledge base."
    
    async def process(self, state: AgentState) -> dict:
        """
        Process a coaching query.
        
        Determines the type of query and retrieves relevant knowledge.
        """
        query = state.get("current_input", "")
        intent = state.get("intent", "")
        
        # Get language from state (detected by orchestrator)
        user_lang = state.get("language", "id")
        if user_lang == "en":
            language_instruction = "English - user wrote in English"
        else:
            language_instruction = "Indonesian - user wrote in Bahasa Indonesia"
        
        # Determine category based on intent
        category = None
        if intent == "coaching_sales":
            category = "sales-techniques"
        elif intent == "coaching_knowledge":
            category = "real-estate-knowledge"
        elif intent == "coaching_motivation":
            category = "motivational"
        
        # Retrieve relevant context
        context = await self._retrieve_context(query, category)
        
        # Generate response with language instructions
        prompt = COACH_SYSTEM_PROMPT.format(
            context=context,
            query=query,
            language_instruction=language_instruction
        )
        
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        
        return {
            "response": response.content,
            "coaching_response": {
                "category": category,
                "context_retrieved": len(context) > 50,
            }
        }
    
    async def get_sales_tips(self, state: AgentState) -> dict:
        """Get sales tips - specific handler for sales queries"""
        state["intent"] = "coaching_sales"
        return await self.process(state)
    
    async def get_knowledge(self, state: AgentState) -> dict:
        """Get real estate knowledge - specific handler for knowledge queries"""
        state["intent"] = "coaching_knowledge"
        return await self.process(state)
    
    async def get_motivation(self, state: AgentState) -> dict:
        """Get motivation - specific handler for motivational queries"""
        state["intent"] = "coaching_motivation"
        return await self.process(state)
    
    # Synchronous version for testing
    def process_sync(self, query: str, intent: str = "coaching_knowledge", language: str = "id") -> dict:
        """Synchronous version for testing"""
        import asyncio
        
        state = AgentState(
            messages=[],
            current_input=query,
            session_id="test",
            client_phone="test",
            intent=intent,
            confidence=1.0,
            routed_to="coach_agent",
            language=language,
            extracted_info={},
            client_profile=None,
            conversation_context=None,
            retrieved_properties=None,
            property_action_result=None,
            coaching_response=None,
            response=None,
            start_time=0,
            metrics={},
        )
        
        return asyncio.run(self.process(state))
