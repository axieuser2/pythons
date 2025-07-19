import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI
import tiktoken

# Load environment variables
load_dotenv()

# Set your OpenAI API key here or via environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Validate required environment variables
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY environment variable. Please check your .env file.")

# Files to process
FILES = [
    ("Axie Studio Extra Information!.txt", "extra_info"),
    ("Axie Studio Knowledge Base.txt", "knowledge_base"),
]

# Chunking parameters
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

def read_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def chunk_text(text, source):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", "!", "?", " "]
    )
    chunks = splitter.split_text(text)
    return [{"content": chunk, "source": source} for chunk in chunks]

def embed_chunks(chunks):
    client = OpenAI(api_key=OPENAI_API_KEY)
    embeddings = []
    for chunk in chunks:
        response = client.embeddings.create(
            input=chunk["content"],
            model="text-embedding-3-small"
        )
        chunk["embedding"] = response.data[0].embedding
        embeddings.append(chunk)
    return embeddings

def main():
    all_chunks = []
    for filepath, source in FILES:
        text = read_file(filepath)
        chunks = chunk_text(text, source)
        all_chunks.extend(chunks)
    print(f"Total chunks: {len(all_chunks)}")

    # Embed all chunks
    embedded_chunks = embed_chunks(all_chunks)
    print(f"Embedded {len(embedded_chunks)} chunks.")

    # Save to file for ingestion
    import json
    with open("embedded_chunks.json", "w", encoding="utf-8") as f:
        json.dump(embedded_chunks, f, ensure_ascii=False, indent=2)
    print("Saved embedded chunks to embedded_chunks.json")

if __name__ == "__main__":
    main()