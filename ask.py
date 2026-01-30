from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
import requests
import os
import uuid

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PERSIST_DIR = os.path.join(BASE_DIR, "jarvis_memory_db")

print("🧠 Loading embedding model...")
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

print("🔌 Connecting to Jarvis memory...")
client = PersistentClient(path=PERSIST_DIR)
collection = client.get_or_create_collection(name="jarvis_memory")

print(f"✅ Connected! Memory contains {collection.count()} documents")

# Ollama call
def ask_ollama(prompt):
    url = "http://localhost:11434/api/generate"
    data = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(url, json=data)
    return response.json()["response"].strip()

# Step 4.1 – Memory classifier
def is_memory_worthy(text):
    prompt = f"""
Decide if this sentence contains important personal information
or useful factual knowledge worth storing in long-term memory.
Answer only YES or NO.

Sentence: {text}
"""
    result = ask_ollama(prompt)
    return result.upper().startswith("YES")

# Step 4.2 – Store into Chroma
def store_memory(text):
    embedding = embed_model.encode(text).tolist()
    doc_id = str(uuid.uuid4())

    collection.add(
        documents=[text],
        embeddings=[embedding],
        ids=[doc_id],
        metadatas=[{"type": "auto_memory"}]
    )

    print("💾 (Memory Stored)")

print("\n" + "="*60)
print("🤖 JARVIS – Autonomous Memory + Brain (Ollama)")
print("="*60)

while True:
    query = input("\nYou: ")
    if query.lower() == "exit":
        print("👋 Goodbye, Tony Stark!")
        break

    # STEP 4: Auto memory detection
    if is_memory_worthy(query):
        store_memory(query)

    # Embed query for recall
    query_embedding = embed_model.encode(query).tolist()

    # Search memory
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )

    documents = results["documents"][0]

    if len(documents) == 0:
        context = "No relevant memory found."
        memory_note = "No memory found. Answer using your general knowledge."
    else:
        context = "\n".join(documents)
        memory_note = "Use the following long-term memory to answer."

    # Final RAG prompt
    prompt = f"""
You are Jarvis, an intelligent personal AI assistant.

{memory_note}

LONG-TERM MEMORY:
{context}

QUESTION:
{query}

Give a clear, simple, human-like answer.
"""

    print("\n🧠 Thinking...")
    answer = ask_ollama(prompt)

    print("\n🤖 Jarvis:", answer)
