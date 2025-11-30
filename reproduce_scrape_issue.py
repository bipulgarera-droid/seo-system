
import sys
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv('.env.local')

# Add current dir to path to import api
sys.path.append(os.getcwd())

from api.index import scrape_page_content, fetch_with_curl

url = "https://www.nytarra.in/products/divine-spark-candle"

print(f"Testing scraping for: {url}")

print("\n--- Testing fetch_with_curl ---")
content, latency = fetch_with_curl(url)
print(f"Latency: {latency}s")
if content:
    print(f"Content length: {len(content)}")
    print(f"Preview: {content[:200]}...")
else:
    print("fetch_with_curl returned None or empty content")

print("\n--- Testing scrape_page_content ---")
data = scrape_page_content(url)
if data:
    print("Scrape Successful!")
    print(f"Title: {data.get('title')}")
    print(f"Body Content Length: {len(data.get('body_content', ''))}")
else:
    print("scrape_page_content returned None")
