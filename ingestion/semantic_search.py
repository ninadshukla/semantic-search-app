import chromadb
from sentence_transformers import SentenceTransformer

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="ingestion/chroma_store")

collection = client.get_or_create_collection(name="website_chunks")

documents = [
    "Python is a programming language used for AI and web development.",
    "React is used to build interactive user interfaces.",
    "ChromaDB stores embeddings for semantic search.",
    "Firecrawl extracts clean website content for AI apps.",
    "The stock market fell after weak earnings reports."
]

ids = [f"doc_{i}" for i in range(len(documents))]

print("Creating embeddings...")
embeddings = model.encode(documents).tolist()

collection.add(
    documents=documents,
    embeddings=embeddings,
    ids=ids
)

query = "How do I store vectors for search?"

query_embedding = model.encode(query).tolist()

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)

print("\nSearch query:", query)
print("\nTop results:")

for doc in results["documents"][0]:
    print("-", doc)