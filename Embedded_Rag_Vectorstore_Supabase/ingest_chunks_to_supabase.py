import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Set your API keys and Supabase details here or via environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Validate required environment variables
if not all([OPENAI_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_KEY]):
    raise ValueError("Missing required environment variables. Please check your .env file.")

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