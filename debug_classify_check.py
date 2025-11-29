import os
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Get the most recent project or list them
projects = supabase.table('projects').select('id, domain').execute().data

if not projects:
    print("No projects found.")
    exit()

print("Projects:")
for i, p in enumerate(projects):
    print(f"{i}: {p['domain']} ({p['id']})")

# Just pick the first one or let me know which one to pick. 
# For automation, I'll pick the one that looks like 'nytarra' if it exists, else the first one.
target_project = next((p for p in projects if 'nytarra' in p['domain']), projects[0])
print(f"\nAnalyzing Project: {target_project['domain']}")

# Fetch pages
pages = supabase.table('pages').select('url, page_type').eq('project_id', target_project['id']).execute().data

print(f"Total Pages: {len(pages)}")
print("\nSample URLs and Types:")
for p in pages[:20]:
    print(f"URL: {p['url']} | Type: {p.get('page_type')}")

# Test Heuristics
print("\n--- Testing Heuristics ---")
matched = 0
for p in pages:
    url_lower = p['url'].lower()
    new_type = None
    if any(x in url_lower for x in ['/product/', '/products/', '/item/', '/p/', '/shop/']):
        new_type = 'Product'
    elif any(x in url_lower for x in ['/category/', '/categories/', '/c/', '/collection/', '/collections/']):
        new_type = 'Category'
    
    if new_type:
        # print(f"Match: {p['url']} -> {new_type}")
        matched += 1

print(f"\nPotential Matches with updated heuristics: {matched}")
