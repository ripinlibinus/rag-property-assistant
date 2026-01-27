"""
Test suite for Coach Agent with RAG Knowledge Retrieval

Tests:
- Knowledge base indexing
- Context retrieval for different categories
- Response generation
- Error handling
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.agents.coach_agent import CoachAgent
from src.agents.state import AgentState


# Test fixtures
@pytest.fixture
def knowledge_path():
    """Path to test knowledge base"""
    return Path(__file__).parent.parent / "data" / "knowledge-base"


@pytest.fixture
def chroma_test_path(tmp_path):
    """Temporary path for test ChromaDB"""
    return tmp_path / "chroma_test"


@pytest.fixture
def sample_state():
    """Sample agent state for testing"""
    return AgentState(
        messages=[],
        current_input="",
        session_id="test-session",
        client_phone="08123456789",
        intent="coaching_knowledge",
        confidence=0.9,
        routed_to="coach_agent",
        language="id",  # Default Indonesian
        extracted_info={},  # Empty extracted info
        client_profile=None,
        conversation_context=None,
        retrieved_properties=None,
        property_action_result=None,
        coaching_response=None,
        response=None,
        start_time=0,
        metrics={},
    )


class TestCoachAgentIndexing:
    """Test knowledge base indexing functionality"""
    
    def test_knowledge_path_exists(self, knowledge_path):
        """Verify knowledge base directory exists"""
        assert knowledge_path.exists(), f"Knowledge path {knowledge_path} not found"
        
        # Check subdirectories
        assert (knowledge_path / "sales-techniques").exists()
        assert (knowledge_path / "real-estate-knowledge").exists()
        assert (knowledge_path / "motivational").exists()
    
    def test_knowledge_files_exist(self, knowledge_path):
        """Verify knowledge files are present"""
        md_files = list(knowledge_path.rglob("*.md"))
        assert len(md_files) >= 4, f"Expected at least 4 markdown files, found {len(md_files)}"
        
        # Check specific files mentioned in progress report
        expected_files = [
            "sales-techniques/closing-strategies.md",
            "real-estate-knowledge/sertifikat-types.md",
            "real-estate-knowledge/proses-jual-beli.md",
            "motivational/mindset-tips.md",
        ]
        for expected in expected_files:
            file_path = knowledge_path / expected
            assert file_path.exists(), f"Expected file {expected} not found"
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, knowledge_path, chroma_test_path):
        """Test agent can be initialized"""
        # Mock LLM and embeddings to avoid API key requirement
        mock_llm = Mock()
        mock_embeddings = Mock()
        mock_embeddings.embed_query = Mock(return_value=[0.1] * 1536)
        mock_embeddings.embed_documents = Mock(return_value=[[0.1] * 1536])
        
        agent = CoachAgent(
            llm=mock_llm,
            embeddings=mock_embeddings,
            knowledge_path=str(knowledge_path),
            chroma_path=str(chroma_test_path),
        )
        
        assert agent is not None
        assert agent.vectorstore is None  # Not indexed yet
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_knowledge_indexing(self, knowledge_path, chroma_test_path):
        """Test knowledge base can be indexed - requires OPENAI_API_KEY"""
        import os
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
            
        agent = CoachAgent(
            knowledge_path=str(knowledge_path),
            chroma_path=str(chroma_test_path),
        )
        
        await agent.index_knowledge()
        
        assert agent.vectorstore is not None
        assert agent._knowledge_indexed is True


class TestCoachAgentRetrieval:
    """Test knowledge retrieval functionality - Requires OPENAI_API_KEY for embeddings"""
    
    @pytest.fixture
    async def indexed_agent(self, knowledge_path, chroma_test_path):
        """Get an agent with indexed knowledge"""
        import os
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        agent = CoachAgent(
            knowledge_path=str(knowledge_path),
            chroma_path=str(chroma_test_path),
        )
        await agent.index_knowledge()
        return agent
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_retrieve_sales_knowledge(self, indexed_agent):
        """Test retrieving sales techniques knowledge"""
        agent = await indexed_agent
        
        context = await agent._retrieve_context(
            "Bagaimana cara closing yang efektif?",
            category="sales-techniques"
        )
        
        assert context is not None
        assert len(context) > 50  # Has meaningful content
        # Check content relates to closing
        assert any(word in context.lower() for word in ["closing", "strategi", "teknik", "deal"])
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_retrieve_real_estate_knowledge(self, indexed_agent):
        """Test retrieving real estate knowledge"""
        agent = await indexed_agent
        
        context = await agent._retrieve_context(
            "Apa perbedaan SHM dan SHGB?",
            category="real-estate-knowledge"
        )
        
        assert context is not None
        assert len(context) > 50
        # Check content relates to certificates
        assert any(word in context.lower() for word in ["shm", "shgb", "sertifikat", "hak"])
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_retrieve_motivation(self, indexed_agent):
        """Test retrieving motivational content"""
        agent = await indexed_agent
        
        context = await agent._retrieve_context(
            "Saya butuh motivasi untuk tetap semangat",
            category="motivational"
        )
        
        assert context is not None
        assert len(context) > 50
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_retrieve_without_category(self, indexed_agent):
        """Test retrieval without category filter"""
        agent = await indexed_agent
        
        context = await agent._retrieve_context(
            "Tips menjual properti",
            category=None
        )
        
        assert context is not None
        assert len(context) > 50
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_retrieve_no_match(self, indexed_agent):
        """Test retrieval with unlikely query"""
        agent = await indexed_agent
        
        context = await agent._retrieve_context(
            "XYZABC12345 gibberish query",
            category="sales-techniques"
        )
        
        # Should still return something (similarity search returns closest matches)
        assert context is not None


class TestCoachAgentProcess:
    """Test the main process method - Requires OPENAI_API_KEY"""
    
    @pytest.fixture
    async def mock_llm_agent(self, knowledge_path, chroma_test_path):
        """Get agent with mocked LLM for faster tests"""
        import os
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set for embeddings")
        
        agent = CoachAgent(
            knowledge_path=str(knowledge_path),
            chroma_path=str(chroma_test_path),
        )
        await agent.index_knowledge()
        
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = "Ini adalah tips penjualan yang berguna untuk Anda."
        agent.llm = AsyncMock()
        agent.llm.ainvoke = AsyncMock(return_value=mock_response)
        
        return agent
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_process_sales_intent(self, mock_llm_agent, sample_state):
        """Test processing sales coaching query"""
        agent = await mock_llm_agent
        
        sample_state["current_input"] = "Bagaimana cara handle objection harga terlalu mahal?"
        sample_state["intent"] = "coaching_sales"
        
        result = await agent.process(sample_state)
        
        assert "response" in result
        assert result["response"] is not None
        assert "coaching_response" in result
        assert result["coaching_response"]["category"] == "sales-techniques"
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_process_knowledge_intent(self, mock_llm_agent, sample_state):
        """Test processing knowledge query"""
        agent = await mock_llm_agent
        
        sample_state["current_input"] = "Jelaskan tentang pajak BPHTB"
        sample_state["intent"] = "coaching_knowledge"
        
        result = await agent.process(sample_state)
        
        assert "response" in result
        assert result["coaching_response"]["category"] == "real-estate-knowledge"
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_process_motivation_intent(self, mock_llm_agent, sample_state):
        """Test processing motivation query"""
        agent = await mock_llm_agent
        
        sample_state["current_input"] = "Saya merasa tidak termotivasi hari ini"
        sample_state["intent"] = "coaching_motivation"
        
        result = await agent.process(sample_state)
        
        assert "response" in result
        assert result["coaching_response"]["category"] == "motivational"


class TestCoachAgentIntegration:
    """Integration tests with real LLM (requires API key)"""
    
    @pytest.fixture
    def has_api_key(self):
        """Check if OpenAI API key is available"""
        import os
        return bool(os.getenv("OPENAI_API_KEY"))
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_response_generation(self, knowledge_path, chroma_test_path, has_api_key, sample_state):
        """Test full response generation with real LLM"""
        if not has_api_key:
            pytest.skip("OPENAI_API_KEY not set")
        
        agent = CoachAgent(
            knowledge_path=str(knowledge_path),
            chroma_path=str(chroma_test_path),
        )
        await agent.initialize()
        
        sample_state["current_input"] = "Apa itu SHM dan SHGB?"
        sample_state["intent"] = "coaching_knowledge"
        
        result = await agent.process(sample_state)
        
        assert "response" in result
        response = result["response"]
        
        # Response should mention SHM or SHGB
        assert any(word in response.upper() for word in ["SHM", "SHGB", "SERTIFIKAT"])
        
        # Response should be substantial
        assert len(response) > 100
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_indonesian_response(self, knowledge_path, chroma_test_path, has_api_key, sample_state):
        """Test that response is in Indonesian when query is in Indonesian"""
        if not has_api_key:
            pytest.skip("OPENAI_API_KEY not set")
        
        agent = CoachAgent(
            knowledge_path=str(knowledge_path),
            chroma_path=str(chroma_test_path),
        )
        await agent.initialize()
        
        sample_state["current_input"] = "Berikan tips closing yang efektif"
        sample_state["intent"] = "coaching_sales"
        
        result = await agent.process(sample_state)
        response = result["response"]
        
        # Check for Indonesian words in response
        indonesian_words = ["dan", "yang", "untuk", "dengan", "adalah", "ini", "itu"]
        has_indonesian = any(word in response.lower() for word in indonesian_words)
        assert has_indonesian, "Response should be in Indonesian"


# Helper for running tests
if __name__ == "__main__":
    # Run with: python -m pytest tests/test_coach_agent.py -v
    pytest.main([__file__, "-v", "-m", "not integration"])
