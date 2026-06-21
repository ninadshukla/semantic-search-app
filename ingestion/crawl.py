import os
from dotenv import load_dotenv
from firecrawl import Firecrawl

print("Starting script...")

load_dotenv()

api_key = os.getenv("FIRECRAWL_API_KEY")

if not api_key:
    raise ValueError("Missing FIRECRAWL_API_KEY. Add it to your .env file.")

print("API key loaded.")

app = Firecrawl(api_key=api_key)

url = "https://news.ycombinator.com"

print("Scraping website...")

result = app.scrape(url, formats=["markdown"])

print("Scrape complete.")

print(result.markdown[:500])