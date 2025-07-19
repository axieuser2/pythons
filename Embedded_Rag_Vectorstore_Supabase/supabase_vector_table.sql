-- Enable pgvector extension (run as superuser if not already enabled)
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the documents table for RAG
CREATE TABLE IF NOT EXISTS documents (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    content text NOT NULL,
    embedding vector(1536) NOT NULL,
    source text,
    metadata jsonb
);

-- Optional: Create an index for fast vector similarity search
CREATE INDEX IF NOT EXISTS idx_documents_embedding
ON documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);