import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(
    path="ingestion/chroma_store"
)

collection = client.get_collection(
    name="website_index"
)

model = SentenceTransformer("all-MiniLM-L6-v2")

query = input("Ask a question: ")

query_embedding = model.encode(query).tolist()

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)

print("\nTop Results:\n")

for doc in results["documents"][0]:
    print(doc)
    print("\n" + "-" * 80 + "\n")