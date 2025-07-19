import os
import json
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from openai import OpenAI
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Validate required environment variables
if not all([OPENAI_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_KEY]):
    raise ValueError("Missing required environment variables. Please check your .env file.")

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

class EnhancedQuerySystem:
    def __init__(self):
        self.client = openai_client
        self.supabase = supabase
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for query text"""
        response = self.client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding
    
    def search_documents(self, query: str, limit: int = 10, similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search documents using vector similarity"""
        query_embedding = self.get_embedding(query)
        
        # Use Supabase's vector similarity search
        response = supabase.rpc(
            'match_documents',
            {
                'query_embedding': query_embedding,
                'match_threshold': similarity_threshold,
                'match_count': limit
            }
        ).execute()
        
        return response.data if response.data else []
    
    def search_by_category(self, category: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search documents by specific category/chunk type"""
        response = supabase.table("documents").select("*").eq("metadata->>chunk_type", category).limit(limit).execute()
        return response.data if response.data else []
    
    def search_by_source(self, source: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search documents by source file"""
        response = supabase.table("documents").select("*").eq("source", source).limit(limit).execute()
        return response.data if response.data else []
    
    def comprehensive_search(self, query: str) -> Dict[str, Any]:
        """Perform comprehensive search across all document types"""
        results = {
            "semantic_search": self.search_documents(query, limit=5),
            "pricing_info": self.search_by_category("pricing", limit=3),
            "contact_info": self.search_by_category("contact", limit=3),
            "key_facts": self.search_by_category("key_fact", limit=5),
            "full_documents": self.search_by_category("full_document", limit=2)
        }
        
        return results
    
    def generate_answer(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """Generate comprehensive answer using retrieved context"""
        context = "\n\n".join([doc["content"] for doc in context_docs[:5]])
        
        prompt = f"""
Based on the following information about Axie Studio, please provide a comprehensive answer to the user's question.

Context Information:
{context}

User Question: {query}

Please provide a detailed, accurate answer based on the context provided. If the information is not available in the context, please say so.
"""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides accurate information about Axie Studio based on the provided context."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        return response.choices[0].message.content

def main():
    query_system = EnhancedQuerySystem()
    
    print("Enhanced Axie Studio Query System")
    print("=" * 40)
    
    while True:
        query = input("\nEnter your question (or 'quit' to exit): ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        if not query:
            continue
        
        print("\nSearching...")
        
        # Perform comprehensive search
        results = query_system.comprehensive_search(query)
        
        # Collect all relevant documents
        all_docs = []
        for category, docs in results.items():
            all_docs.extend(docs)
        
        if not all_docs:
            print("No relevant information found.")
            continue
        
        # Generate comprehensive answer
        answer = query_system.generate_answer(query, all_docs)
        
        print(f"\nAnswer:\n{answer}")
        
        # Show source information
        print(f"\nBased on {len(all_docs)} relevant documents:")
        for i, doc in enumerate(all_docs[:3], 1):
            title = doc.get("metadata", {}).get("title", "Unknown")
            chunk_type = doc.get("metadata", {}).get("chunk_type", "unknown")
            print(f"{i}. {title} ({chunk_type})")

if __name__ == "__main__":
    main()