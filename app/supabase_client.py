from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

def get_supabase() -> Client:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
    return create_client(supabase_url, supabase_key)