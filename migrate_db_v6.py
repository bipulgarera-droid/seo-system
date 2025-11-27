import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv('.env.local')
load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase: Client = create_client(url, key)

# SQL to add new columns for MoFu workflow
sql = """
ALTER TABLE pages 
ADD COLUMN IF NOT EXISTS content_description TEXT,
ADD COLUMN IF NOT EXISTS keywords TEXT,
ADD COLUMN IF NOT EXISTS research_data JSONB,
ADD COLUMN IF NOT EXISTS slug TEXT;
"""

try:
    # Execute the SQL directly using the REST API's rpc or just print it for manual execution if direct execution isn't supported easily via py library without a stored proc.
    # However, for this environment, we often simulate or use a direct postgres connection if available.
    # Since we are using the supabase-py client, we usually need a stored procedure to run raw SQL, OR we can just use the dashboard.
    # But for this agent, I'll assume we might have a 'exec_sql' function or similar, OR I will just print the instructions if I can't execute.
    
    # Actually, the previous migrations were just python scripts that *would* run if we had a way. 
    # Let's try to use the `postgres` connection if possible, but we only have supabase client.
    # I will create a function in Supabase via the dashboard usually, but here I can't.
    # I will just print the SQL and assume the user or a separate process applies it, 
    # OR I can try to use a "hack" if I had the connection string.
    
    # WAIT: The previous migrations in this session were just created but not explicitly "run" against a live DB in the chat logs I see?
    # Ah, I see `migrate_db_v4.py` in the file list.
    # I will stick to the pattern: Create the script.
    
    print("Migration SQL:")
    print(sql)
    
    # If we had a way to execute:
    # res = supabase.rpc('exec_sql', {'sql': sql}).execute()
    
except Exception as e:
    print(f"Error: {e}")
