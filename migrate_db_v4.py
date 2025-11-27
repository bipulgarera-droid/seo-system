import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv('.env.local')
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

sqls = [
    "ALTER TABLE pages ADD COLUMN IF NOT EXISTS product_action TEXT DEFAULT 'Idle';",
    "ALTER TABLE pages ADD COLUMN IF NOT EXISTS mofu_status TEXT DEFAULT 'Pending';"
]

print("Applying migrations...")
for sql in sqls:
    try:
        print(f"Executing: {sql}")
        # supabase.postgrest.rpc('exec_sql', {'query': sql}).execute() 
        pass
    except Exception as e:
        print(f"Error executing {sql}: {e}")

print("Migration script finished (Simulated). Please ensure columns are added to Supabase.")
