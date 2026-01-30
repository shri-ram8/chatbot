from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
import os

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PERSIST_DIR = os.path.join(BASE_DIR, "jarvis_memory_db")

# Ensure the directory exists
os.makedirs(PERSIST_DIR, exist_ok=True)

print(f"💾 Persistent storage location: {PERSIST_DIR}")

# Create persistent client (this saves to disk automatically)
client = PersistentClient(path=PERSIST_DIR)

# Delete and recreate collection for clean slate
try:
    client.delete_collection(name="jarvis_memory")
    print("🗑️ Old collection deleted")
except:
    print("📂 No existing collection found")

# Create new collection
collection = client.get_or_create_collection(
    name="jarvis_memory",
    metadata={"description": "Jarvis long-term memory storage"}
)

# Load embedding model
print("🧠 Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Read knowledge file
knowledge_file = os.path.join(BASE_DIR, "knowledge", "test.txt")
print(f"📖 Reading knowledge from: {knowledge_file}")

with open(knowledge_file, "r", encoding="utf-8") as f:
    text = f.read()

print(f"📝 Text length: {len(text)} characters")

# Generate embedding
print("🔢 Generating embedding...")
embedding = model.encode(text).tolist()

# Add to persistent collection
collection.add(
    documents=[text],
    embeddings=[embedding],
    ids=["doc1"],
    metadatas=[{"source": "test.txt", "type": "knowledge"}]
)

print(f"\n✅ SUCCESS!")
print(f"📊 Documents in memory: {collection.count()}")
print(f"💾 Memory saved permanently to: {PERSIST_DIR}")
print(f"📁 Files created: chroma.sqlite3, and ChromaDB internal files")