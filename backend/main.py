from fastapi import FastAPI
from pydantic import BaseModel
import chromadb
from sentence_transformers import SentenceTransformer

app = FastAPI()

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(
    path="ingestion/chroma_store"
)

collection = client.get_collection(
    name="website_index"
)

class SearchRequest(BaseModel):
    query: str

@app.get("/")
def home():
    return {"message": "Semantic Search API is running"}

@app.post("/search")
def search(request: SearchRequest):
    query_embedding = model.encode(request.query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    return {
        "query": request.query,
        "results": results["documents"][0]
    }