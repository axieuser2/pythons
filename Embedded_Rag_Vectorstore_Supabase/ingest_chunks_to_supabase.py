import os
import json
from openai import OpenAI
from supabase import create_client, Client

# Set your API keys and Supabase details here or via environment variables
OPENAI_API_KEY = "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"
SUPABASE_URL = "https://ompjkiiabyuegytncbwq.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9tcGpraWlhYnl1ZWd5dG5jYndxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Mjg0ODYyNiwiZXhwIjoyMDY4NDI0NjI2fQ.0DQ_g_h7vM4TVxgGFj2u38XXomdZ2YvwfNzJ0B3KfE4"

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def get_embedding(text):
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def main():
    with open("chunks_for_n8n.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            chunk = json.loads(line)
            content = chunk["content"]
            source = chunk.get("source")
            title = chunk.get("title")
            embedding = get_embedding(content)
            metadata = {"title": title} if title else None

            # Prepare data for insert (omit metadata if None)
            data = {
                "content": content,
                "embedding": embedding,
                "source": source
            }
            if metadata:
                data["metadata"] = metadata

            # Insert into Supabase and print response for debugging
            response = supabase.table("documents").insert(data).execute()
            print(f"Insert response: {response}")

if __name__ == "__main__":
    main()