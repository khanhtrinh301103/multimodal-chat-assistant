# backend/app/database/supabase_client.py
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL", "")
supabase_key = os.getenv("SUPABASE_KEY", "")

# Initialize Supabase client
supabase: Client = None

if supabase_url and supabase_key:
    try:
        supabase = create_client(supabase_url, supabase_key)
        print("✓ Supabase connected successfully")
    except Exception as e:
        print(f"⚠️ Supabase connection failed: {e}")
else:
    print("⚠️ Supabase credentials not configured")


def get_supabase() -> Client:
    """Get Supabase client instance"""
    if supabase is None:
        raise Exception("Supabase not initialized. Check .env configuration.")
    return supabase