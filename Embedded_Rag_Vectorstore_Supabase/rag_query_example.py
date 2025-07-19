import os
from dotenv import load_dotenv
from openai import OpenAI
import psycopg2
import numpy as np

# Load environment variables
load_dotenv()

# Set your credentials
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_DB_HOST = os.getenv("SUPABASE_DB_HOST")
SUPABASE_DB_PORT = int(os.getenv("SUPABASE_DB_PORT", 5432))
SUPABASE_DB_NAME = os.getenv("SUPABASE_DB_NAME")
SUPABASE_DB_USER = os.getenv("SUPABASE_DB_USER")
SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")

# Validate required environment variables
required_vars = [OPENAI_API_KEY, SUPABASE_DB_HOST, SUPABASE_DB_NAME, SUPABASE_DB_USER, SUPABASE_DB_PASSWORD]
if not all(required_vars):
    raise ValueError("Missing required environment variables. Please check your .env file.")

def embed_query(query):
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.embeddings.create(
        input=query,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def query_supabase(query_embedding, top_k=1):
    # Connect to Supabase Postgres
    conn = psycopg2.connect(
        host=SUPABASE_DB_HOST,
        port=SUPABASE_DB_PORT,
        dbname=SUPABASE_DB_NAME,
        user=SUPABASE_DB_USER,
        password=SUPABASE_DB_PASSWORD
    )
    cur = conn.cursor()
    # Prepare the embedding as a Postgres array
    emb_str = "[" + ",".join([str(x) for x in query_embedding]) + "]"
    sql = f"""
        SELECT content, source, embedding <#> %s AS distance
        FROM documents
        ORDER BY embedding <#> %s
        LIMIT {top_k};
    """
    cur.execute(sql, (emb_str, emb_str))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def main():
    user_query = input("Enter your question: ")
    query_embedding = embed_query(user_query)
    results = query_supabase(query_embedding, top_k=3)
    for idx, (content, source, distance) in enumerate(results, 1):
        print(f"\nResult {idx} (source: {source}, distance: {distance:.4f}):\n{content}\n")

if __name__ == "__main__":
    main()