from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
import requests
import os
import uuid
import time
import re

app = FastAPI()

# ---------------- PATHS ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PERSIST_DIR = os.path.join(BASE_DIR, "jarvis_memory_db")

# ---------------- EMBEDDINGS (CPU, OFFLINE, STABLE) ----------------
embed_model = SentenceTransformer(
    "all-MiniLM-L6-v2",
    local_files_only=True   # 🔥 prevents HF timeout
)

# ---------------- CHROMA ----------------
client = PersistentClient(path=PERSIST_DIR)
collection = client.get_or_create_collection(name="jarvis_memory")

# ---------------- CACHES ----------------
embedding_cache = {}
response_cache = {}

# ---------------- OLLAMA ----------------
def ask_ollama(prompt: str) -> str:
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "phi3",
        "prompt": prompt,
        "stream": False
    }

    try:
        r = requests.post(url, json=payload, timeout=60)
        return r.json().get("response", "").strip()
    except Exception as e:
        print("Ollama error:", e)
        return "⚠️ Brain connection issue."

# ---------------- OUTPUT CLEANER ----------------
def clean_answer(text: str) -> str:
    text = re.sub(r"[{}\[\]();<>]", "", text)
    text = re.sub(r"\b(map|Number|toArray|tableau)\b.*", "", text, flags=re.IGNORECASE)
    return text.strip()

# ---------------- QUESTION TYPE CHECK ----------------
def is_general_knowledge(text: str) -> bool:
    keywords = [
        "who is", "what is", "how many", "capital",
        "president", "prime minister", "won", "cups",
        "define", "explain"
    ]
    return any(k in text.lower() for k in keywords)

def is_personal_statement(text: str) -> bool:
    triggers = [
        "i am", "my name", "i live", "i study",
        "i work", "my goal", "my project", "remember"
    ]
    return any(t in text.lower() for t in triggers)

# ---------------- STORE MEMORY ----------------
def store_memory(text: str):
    if text in embedding_cache:
        embedding = embedding_cache[text]
    else:
        embedding = embed_model.encode(text).tolist()
        embedding_cache[text] = embedding

    collection.add(
        documents=[text],
        embeddings=[embedding],
        ids=[str(uuid.uuid4())],
        metadatas=[{"type": "personal"}]
    )

# ---------------- REQUEST MODEL ----------------
class ChatRequest(BaseModel):
    message: str

# ---------------- CHAT ENDPOINT ----------------
@app.post("/chat")
def chat(req: ChatRequest):
    start_time = time.time()
    user_input = req.message.strip()

    # ❌ Never cache general knowledge
    if user_input in response_cache and not is_general_knowledge(user_input):
        return {"answer": response_cache[user_input]}

    memory_context = ""

    # 🧠 Store ONLY personal info
    if is_personal_statement(user_input) and not user_input.endswith("?"):
        store_memory(user_input)

    # 🧠 Use memory ONLY for personal queries
    if is_personal_statement(user_input):
        if user_input in embedding_cache:
            query_embedding = embedding_cache[user_input]
        else:
            query_embedding = embed_model.encode(user_input).tolist()
            embedding_cache[user_input] = query_embedding

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )

        docs = results["documents"][0]
        if docs:
            memory_context = "\n".join(docs)

    # 🎯 PROMPT (terminal-like behavior)
    if memory_context:
        prompt = f"""
You are Jarvis.

Use the following PERSONAL MEMORY only if relevant:
{memory_context}

Question:
{user_input}

Answer confidently and correctly.
"""
    else:
        prompt = f"""
Answer the following question confidently using your best knowledge.
Do NOT guess. If unsure, say you are unsure.

Question:
{user_input}
"""

    answer = ask_ollama(prompt)
    answer = clean_answer(answer)

    # ⚡ Cache ONLY non-general answers
    if not is_general_knowledge(user_input):
        response_cache[user_input] = answer

    latency = round(time.time() - start_time, 2)
    print(f"⚡ Response time: {latency}s")

    return {"answer": answer}
