import os
import chromadb
from bs4 import BeautifulSoup
import re
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

url = "https://docs.python.org/3/tutorial/controlflow.html"

print("Scraping website...")
result = firecrawl.scrape(url, formats=["markdown"])

markdown = result.markdown 
soup = BeautifulSoup(markdown, "html.parser")
clean_text = soup.get_text(separator=" ")

clean_text = re.sub(r'http\S+', '', clean_text)
clean_text = re.sub(r'\s+', ' ', clean_text).strip()

print("Splitting content into chunks...")

chunks = [] 

chunk_size = 500

for i in range(0, len(clean_text), chunk_size):
    chunks.append(clean_text[i:i + chunk_size])

print(f"Created {len(chunks)} chunks")

client = chromadb.PersistentClient(
    path="ingestion/chroma_store"
)

collection = client.get_or_create_collection(
    name="website_index"
)

client.delete_collection(name="website_index")
collection = client.get_or_create_collection(name="website_index")

print("Creating embeddings...")

embeddings = model.encode(chunks).tolist()

collection.add(
    documents=chunks,
    embeddings=embeddings,
    ids=[f"chunk_{i}" for i in range(len(chunks))]
)

print("Website successfully indexed!")