import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Set your Supabase credentials here or via environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Validate required environment variables
if not all([SUPABASE_URL, SUPABASE_SERVICE_KEY]):
    raise ValueError("Missing required environment variables. Please check your .env file.")

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