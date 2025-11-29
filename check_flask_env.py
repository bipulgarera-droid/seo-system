#!/usr/bin/env python3
import sys
import os

# Add the directory to path
sys.path.insert(0, '/Users/bipul/Downloads/seo-saas-brain')

# Import after modifying path
from dotenv import load_dotenv

# Load exactly like Flask does
load_dotenv('.env.local')
load_dotenv()

print("Environment variables Flask would see:")
print(f"  PERPLEXITY_API_KEY: {os.environ.get('PERPLEXITY_API_KEY', 'NOT FOUND')}")
print(f"  DATAFORSEO_LOGIN: {os.environ.get('DATAFORSEO_LOGIN', 'NOT FOUND')}")
print(f"  SUPABASE_URL: {os.environ.get('SUPABASE_URL', 'NOT FOUND')[:30]}...")

print("\nChecking .env file content:")
try:
    with open('.env', 'r') as f:
        for line in f:
            if 'PERPLEXITY' in line:
                print(f"  Found in .env: {line.strip()[:60]}...")
except Exception as e:
    print(f"  Error reading .env: {e}")

print("\nCurrent working directory:", os.getcwd())
