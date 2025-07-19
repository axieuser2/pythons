import os
import json
from supabase import create_client, Client

# Set your Supabase credentials here or via environment variables
SUPABASE_URL = "https://ompjkiiabyuegytncbwq.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9tcGpraWlhYnl1ZWd5dG5jYndxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Mjg0ODYyNiwiZXhwIjoyMDY4NDI0NjI2fQ.0DQ_g_h7vM4TVxgGFj2u38XXomdZ2YvwfNzJ0B3KfE4"

def main():
    # Load embedded chunks
    with open("embedded_chunks.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)

    # Connect to Supabase
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    # Insert each chunk into the documents table
    for i, chunk in enumerate(chunks, 1):
        data = {
            "content": chunk["content"],
            "embedding": chunk["embedding"],
            "source": chunk.get("source"),
            "metadata": None
        }
        res = supabase.table("documents").insert(data).execute()
        if getattr(res, "error", None):
            print(f"Chunk {i}: ERROR - {res.error}")
        else:
            print(f"Chunk {i}: Inserted successfully. Response: {res.data}")

    print("Ingestion complete. Please check the Supabase table again.")

if __name__ == "__main__":
    main()