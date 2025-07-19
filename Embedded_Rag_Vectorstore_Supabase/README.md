# Axie Studio RAG Vector Store Setup

This project enables you to embed your `.txt` knowledge files into a Supabase vector store for use with AI chatbots and semantic search.

---

## 📦 1. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 📄 2. Prepare Your Knowledge Files

- Place your `.txt` files (e.g., `Axie Studio Extra Information!.txt`, `Axie Studio Knowledge Base.txt`) in the project directory.
- You can update or replace these files at any time to re-embed new knowledge.

---

## 🧩 3. Chunk and Embed the Files

This step splits your text into chunks and generates embeddings using OpenAI.

```bash
python prepare_rag_chunks.py
```

- Output: `embedded_chunks.json` (contains all chunks and their embeddings).

---

## 🚀 4. Ingest Embeddings into Supabase

This uploads all chunks and embeddings to your Supabase vector table.

```bash
python ingest_to_supabase.py
```

- Each chunk is stored in the `documents` table in Supabase.

---

## 🔍 5. Query the Vector Store (Test)

You can test semantic search with:

```bash
python rag_query_example.py
```

- Enter a question when prompted.
- The script will return the most relevant chunk(s) from your knowledge base.

---

## ♻️ To Re-Embed After Updating Files

1. Replace or update your `.txt` files.
2. Run:

   ```bash
   python prepare_rag_chunks.py
   python ingest_to_supabase.py
   ```

3. Your Supabase vector store will be updated with the new knowledge.

---

## 🛠️ Configuration

- **OpenAI API Key:** Hardcoded in `prepare_rag_chunks.py` (update if needed).
- **Supabase URL & Service Key:** Hardcoded in `ingest_to_supabase.py` (update if needed).
- **Table Schema:** See `supabase_vector_table.sql` for the required table structure.

---

## 🧠 Integrate with Your Chatbot

Use the logic in `rag_query_example.py` as a template for your chatbot backend to perform semantic search and retrieval-augmented generation (RAG) using your Supabase vector store.

---

## ❓ Troubleshooting

- If you do not see data in Supabase, check the output of `ingest_to_supabase.py` for errors.
- Ensure your table schema matches `supabase_vector_table.sql`.
- For further issues, check your API keys and Supabase permissions.

---

**All your knowledge is now ready for AI-powered search and chat!**