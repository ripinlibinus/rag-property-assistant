"""
Interactive Chat - ChromaDB ONLY (Pure Semantic Search)

Test chat dengan hanya menggunakan ChromaDB semantic search.
Tidak ada API call, murni vector similarity search.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from src.knowledge import PropertyStore
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


SYSTEM_PROMPT = """Kamu adalah asisten properti yang membantu mencari rumah/properti.

Kamu akan diberikan hasil pencarian dari database vektor (ChromaDB) berdasarkan semantic similarity.
Gunakan informasi tersebut untuk menjawab pertanyaan user.

Format hasil: Judul properti, lokasi, dan skor relevansi.

Jika tidak ada hasil yang cocok, beritahu user dan sarankan kata kunci lain.
"""


def format_property_result(doc, score):
    """Format a single property result"""
    meta = doc.metadata
    title = meta.get("title", "N/A")
    location = meta.get("location", meta.get("city", "N/A"))
    price = meta.get("price", 0)
    bedrooms = meta.get("bedrooms", "-")
    
    price_str = f"Rp {price:,.0f}".replace(",", ".") if price else "Harga tidak tersedia"
    
    return f"• {title} - {location} | {price_str} | {bedrooms} KT [score: {score:.3f}]"


def search_chromadb(store: PropertyStore, query: str, k: int = 5):
    """Search ChromaDB with similarity scores"""
    results = store.vector_store.similarity_search_with_score(query=query, k=k)
    return results


def main():
    print("=" * 60)
    print("🧠 Property Assistant - ChromaDB ONLY MODE")
    print("=" * 60)
    print("Mode: Pure semantic search (ChromaDB vectors only)")
    print("Commands: 'quit' to exit, 'search <query>' to search directly")
    print("-" * 60)
    
    store = PropertyStore()
    count = len(store.vector_store.get()['ids'])
    print(f"✅ ChromaDB loaded: {count} properties")
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    
    while True:
        try:
            print()
            user_input = input("You: ").strip()
            
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            
            if user_input.lower() == "clear":
                messages = [SystemMessage(content=SYSTEM_PROMPT)]
                print("Conversation cleared")
                continue
            
            if not user_input:
                continue
            
            # Direct search mode
            if user_input.lower().startswith("search "):
                query = user_input[7:].strip()
                print(f"\n🔍 Searching: '{query}'")
                results = search_chromadb(store, query, k=10)
                print(f"\nFound {len(results)} results:\n")
                for i, (doc, score) in enumerate(results, 1):
                    print(f"{i}. {format_property_result(doc, score)}")
                continue
            
            # Chat mode - search and let LLM respond
            results = search_chromadb(store, user_input, k=5)
            
            if results:
                context = "Hasil pencarian ChromaDB (semantic search):\n\n"
                for i, (doc, score) in enumerate(results, 1):
                    meta = doc.metadata
                    context += f"{i}. {meta.get('title', 'N/A')}\n"
                    context += f"   Lokasi: {meta.get('location', meta.get('city', 'N/A'))}\n"
                    context += f"   Harga: Rp {meta.get('price', 0):,.0f}\n".replace(",", ".")
                    context += f"   Kamar: {meta.get('bedrooms', '-')} KT, {meta.get('bathrooms', '-')} KM\n"
                    context += f"   Luas: LT {meta.get('land_area', '-')}m², LB {meta.get('building_area', '-')}m²\n"
                    context += f"   Relevance Score: {score:.3f}\n\n"
            else:
                context = "Tidak ditemukan properti yang cocok di ChromaDB."
            
            # Add to conversation
            user_message = f"User bertanya: {user_input}\n\n{context}"
            messages.append(HumanMessage(content=user_message))
            
            # Get LLM response
            response = llm.invoke(messages)
            messages.append(response)
            
            print(f"\nAssistant: {response.content}")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
