import os
import re
import chromadb

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from firecrawl import Firecrawl
from sentence_transformers import SentenceTransformer

print("Loading environment variables...")
load_dotenv()

api_key = os.getenv("FIRECRAWL_API_KEY")

if not api_key:
    raise ValueError("FIRECRAWL_API_KEY missing!")

print("Initializing Firecrawl...")
firecrawl = Firecrawl(api_key=api_key)

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

sources = [
    {
        "title": "Python Documentation",
        "url": "https://docs.python.org/3/tutorial/controlflow.html",
    },
    {
        "title": "FastAPI Documentation",
        "url": "https://fastapi.tiangolo.com/tutorial/",
    },
    {
        "title": "React Documentation",
        "url": "https://react.dev/learn",
    },
    {
        "title": "Wikipedia Clothing",
        "url": "https://en.wikipedia.org/wiki/Clothing",
    },
    {
        "title": "Wikipedia Food",
        "url": "https://en.wikipedia.org/wiki/Food",
    },
    {
        "title": "Wikipedia Consumer Goods",
        "url": "https://en.wikipedia.org/wiki/Consumer_good",
    },
    {
        "title": "Wikipedia Household Goods",
        "url": "https://en.wikipedia.org/wiki/Household_good",
    },
    {
        "title": "Wikipedia Personal Care",
        "url": "https://en.wikipedia.org/wiki/Personal_care",
    },
]

all_chunks = []
all_metadatas = []
all_ids = []

chunk_size = 500

for source in sources:
    title = source["title"]
    url = source["url"]

    print(f"Scraping {title}...")

    result = firecrawl.scrape(url, formats=["markdown"])
    markdown = result.markdown

    soup = BeautifulSoup(markdown, "html.parser")
    clean_text = soup.get_text(separator=" ")

    clean_text = re.sub(r"http\S+", "", clean_text)
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    print(f"Splitting {title} into chunks...")

    for i in range(0, len(clean_text), chunk_size):
        chunk = clean_text[i:i + chunk_size]

        if len(chunk.strip()) < 50:
            continue

        chunk_id = f"{title.lower().replace(' ', '_')}_{i}"

        all_chunks.append(chunk)

        all_metadatas.append({
            "source": url,
            "title": title,
            "chunk_number": i
        })

        all_ids.append(chunk_id)

print(f"Created {len(all_chunks)} total chunks")

client = chromadb.PersistentClient(
    path="ingestion/chroma_store"
)

try:
    client.delete_collection(name="website_index")
except Exception:
    pass

collection = client.get_or_create_collection(
    name="website_index"
)

print("Creating embeddings...")
embeddings = model.encode(all_chunks).tolist()

collection.add(
    documents=all_chunks,
    embeddings=embeddings,
    ids=all_ids,
    metadatas=all_metadatas
)

print("Multiple websites successfully indexed!")