from backend.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
import chromadb
from sentence_transformers import SentenceTransformer
import re

app = FastAPI()
app.include_router(auth_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(
    path="ingestion/chroma_store"
)

collection = client.get_collection(
    name="website_index"
)

class SearchRequest(BaseModel):
    query: str
    
class InsightRequest(BaseModel):
    query: str
    snippets: list[str]

@app.get("/")
def home():
    return {"message": "Semantic Search API is running"}

@app.post("/search")
def search(request: SearchRequest):
    query_embedding = model.encode(request.query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5,
        include=["documents", "distances"]
    )

    cleaned_results = []

    for i, doc in enumerate(results["documents"][0]):
        distance = results["distances"][0][i]

        if distance > 1.2:
            continue

        text = doc.replace("\n", " ").replace("\\", " ")
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        text = re.sub(r"https?://\S+", "", text)
        text = re.sub(r"[#_*`|>\[\]\(\)]", " ", text)
        text = " ".join(text.split())

        relevance_score = max(
            0,
            round((1.2 - distance) / 1.2 * 100, 2)
        )

        cleaned_results.append({
            "id": i + 1,
            "title": f"Result #{i + 1}",
            "snippet": text[:400],
            "score": relevance_score
        })

    return {
        "query": request.query,
        "results": cleaned_results
    }
@app.post("/insights")
def get_insights(request: InsightRequest):
    query = request.query.lower()
    text = " ".join(request.snippets).lower()

    if "python" in query and "loop" in query:
        insight = (
            "The top results explain Python loops, including for-loops, "
            "while-loops, break, continue, and else clauses used with loops."
        )
    elif "python" in query:
        insight = (
            "The top results explain Python programming concepts related to your search."
        )
    else:
        insight = (
            f"The top results are related to '{request.query}'. Review the result cards below for details."
        )

    return {"insight": insight}