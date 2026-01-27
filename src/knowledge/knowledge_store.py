"""
Knowledge Base Manager

Manages ChromaDB vector store for knowledge base (sales techniques, 
real estate knowledge, motivational content).

Usage:
    from src.knowledge.knowledge_store import KnowledgeStore
    
    store = KnowledgeStore()
    store.ingest_directory("data/knowledge-base")
    results = store.search("cara closing", category="sales")
"""

import os
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


# Category mapping based on folder names
CATEGORY_MAP = {
    "sales-techniques": "sales",
    "real-estate-knowledge": "knowledge", 
    "motivational": "motivation",
}


class KnowledgeStore:
    """
    ChromaDB store for knowledge base (sales, real estate, motivation).
    
    Attributes:
        persist_dir: Directory to persist ChromaDB
        collection_name: Name of the collection
        embeddings: OpenAI embeddings model
    """
    
    def __init__(
        self,
        persist_dir: str = "data/chromadb/knowledge",
        collection_name: str = "knowledge_base",
        embedding_model: str = "text-embedding-3-small",
    ):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.embeddings = OpenAIEmbeddings(model=embedding_model)
        self._vector_store: Optional[Chroma] = None
        
        # Ensure directory exists
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
    
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
    
    def ingest_directory(
        self,
        docs_dir: str = "data/knowledge-base",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ) -> int:
        """
        Ingest all markdown files from the knowledge base directory.
        
        Args:
            docs_dir: Root directory containing knowledge base folders
            chunk_size: Size of text chunks for embedding
            chunk_overlap: Overlap between chunks
            
        Returns:
            Number of documents ingested
        """
        docs_path = Path(docs_dir)
        if not docs_path.exists():
            raise FileNotFoundError(f"Knowledge base directory not found: {docs_dir}")
        
        all_documents: List[Document] = []
        
        # Process each category folder
        for folder in docs_path.iterdir():
            if not folder.is_dir():
                continue
            
            category = CATEGORY_MAP.get(folder.name, folder.name)
            print(f"Processing category: {category} ({folder.name})")
            
            # Load markdown files from this category
            for md_file in folder.glob("*.md"):
                print(f"  Loading: {md_file.name}")
                
                try:
                    with open(md_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Create document with metadata
                    doc = Document(
                        page_content=content,
                        metadata={
                            "source": str(md_file.name),
                            "category": category,
                            "folder": folder.name,
                            "full_path": str(md_file),
                            "ingested_at": datetime.now().isoformat(),
                        }
                    )
                    all_documents.append(doc)
                    
                except Exception as e:
                    print(f"  Error loading {md_file}: {e}")
        
        if not all_documents:
            print("No documents found to ingest")
            return 0
        
        print(f"\nLoaded {len(all_documents)} documents")
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
        )
        
        chunks = text_splitter.split_documents(all_documents)
        print(f"Split into {len(chunks)} chunks")
        
        # Clear existing data and add new
        # Note: This is a full re-ingest strategy
        try:
            # Delete existing collection
            self.vector_store._client.delete_collection(self.collection_name)
            self._vector_store = None  # Reset to recreate
        except Exception:
            pass  # Collection might not exist
        
        # Add to vector store
        self.vector_store.add_documents(chunks)
        print(f"Ingested {len(chunks)} chunks to ChromaDB")
        
        return len(chunks)
    
    def search(
        self,
        query: str,
        category: Optional[str] = None,
        k: int = 5,
    ) -> List[Document]:
        """
        Search the knowledge base.
        
        Args:
            query: Search query
            category: Filter by category (sales, knowledge, motivation)
            k: Number of results
            
        Returns:
            List of matching documents
        """
        filter_dict = None
        if category:
            filter_dict = {"category": category}
        
        return self.vector_store.similarity_search(
            query=query,
            k=k,
            filter=filter_dict,
        )
    
    def search_with_scores(
        self,
        query: str,
        category: Optional[str] = None,
        k: int = 5,
    ) -> List[tuple[Document, float]]:
        """Search with similarity scores"""
        filter_dict = None
        if category:
            filter_dict = {"category": category}
        
        return self.vector_store.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter_dict,
        )
    
    def get_stats(self) -> dict:
        """Get collection statistics"""
        collection = self.vector_store._collection
        count = collection.count()
        
        # Count by category
        categories = {}
        if count > 0:
            results = collection.get(include=["metadatas"])
            for meta in results.get("metadatas", []):
                cat = meta.get("category", "unknown")
                categories[cat] = categories.get(cat, 0) + 1
        
        return {
            "total_chunks": count,
            "by_category": categories,
            "persist_dir": self.persist_dir,
        }
    
    def add_document(
        self,
        content: str,
        category: str,
        source: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ) -> int:
        """
        Add a single document to the knowledge base.
        
        Args:
            content: Document content
            category: Category (sales, knowledge, motivation)
            source: Source name/filename
            
        Returns:
            Number of chunks added
        """
        doc = Document(
            page_content=content,
            metadata={
                "source": source,
                "category": category,
                "ingested_at": datetime.now().isoformat(),
            }
        )
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        chunks = text_splitter.split_documents([doc])
        
        # Add to vector store
        self.vector_store.add_documents(chunks)
        
        return len(chunks)


# Project root for absolute paths
_PROJECT_ROOT = Path(__file__).parent.parent.parent


def create_knowledge_store(persist_dir: Optional[str] = None) -> KnowledgeStore:
    """
    Factory function to create KnowledgeStore.
    
    Args:
        persist_dir: Optional path. If None, uses data/chromadb/knowledge relative to project root.
    """
    if persist_dir is None:
        persist_dir = str(_PROJECT_ROOT / "data" / "chromadb" / "knowledge")
    return KnowledgeStore(persist_dir=persist_dir)
