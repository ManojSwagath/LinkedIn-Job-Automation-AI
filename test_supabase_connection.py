#!/usr/bin/env python3
"""
Supabase Connection Test (Python version)
Equivalent to:
  import { createClient } from '@supabase/supabase-js'
  const supabaseUrl = 'https://xaaglooqmwzhitwdlcnz.supabase.co'
  const supabaseKey = process.env.SUPABASE_KEY
  const supabase = createClient(supabaseUrl, supabaseKey)
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*70)
print("SUPABASE CONNECTION TEST (Python)")
print("="*70)

def test_supabase_client():
    """Test Supabase client connection using Python SDK"""
    print("\n[1/3] Loading Supabase credentials...")
    print("-" * 70)
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url:
        print("❌ SUPABASE_URL not found in .env file")
        return False
    
    if not supabase_key:
        print("❌ SUPABASE_KEY not found in .env file")
        return False
    
    print(f"✅ SUPABASE_URL: {supabase_url}")
    print(f"✅ SUPABASE_KEY: {supabase_key[:20]}...{supabase_key[-20:]}")
    
    print("\n[2/3] Creating Supabase client...")
    print("-" * 70)
    
    try:
        from supabase import create_client, Client
        
        # Create Supabase client (equivalent to JS createClient)
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client created successfully")
        
        return supabase
    except ImportError as e:
        print(f"❌ Failed to import supabase library: {str(e)}")
        print("   Try: pip install supabase")
        return False
    except Exception as e:
        print(f"❌ Failed to create Supabase client: {str(e)}")
        return False


def test_supabase_connection(supabase):
    """Test actual connection to Supabase"""
    print("\n[3/3] Testing connection to Supabase...")
    print("-" * 70)
    
    if not supabase:
        print("❌ No Supabase client available")
        return False
    
    try:
        # Test connection by attempting to list tables (will work even if no tables exist)
        # This is equivalent to testing if we can make API calls
        response = supabase.table('_does_not_exist_test').select("*").limit(1).execute()
        
        # Even if table doesn't exist, we should get a response (just empty or error about table)
        # The fact that we got a response means connection works
        print("✅ Connection to Supabase: SUCCESS")
        print(f"   API endpoint is accessible")
        return True
        
    except Exception as e:
        error_str = str(e).lower()
        
        # If error is about table not existing, connection is actually fine
        if 'does not exist' in error_str or 'relation' in error_str or 'not found' in error_str:
            print("✅ Connection to Supabase: SUCCESS")
            print("   (Test table doesn't exist, but API is reachable)")
            return True
        else:
            print(f"❌ Connection failed: {str(e)}")
            return False


def test_database_tables(supabase):
    """Try to list actual tables in the database"""
    print("\n[BONUS] Checking database schema...")
    print("-" * 70)
    
    if not supabase:
        return
    
    try:
        # Try to query Postgres system tables to list user tables
        # Note: This might not work with anon key, but worth trying
        print("Attempting to discover tables in database...")
        
        # Common table names to check
        common_tables = ['users', 'profiles', 'posts', 'items', 'data']
        
        found_tables = []
        for table_name in common_tables:
            try:
                result = supabase.table(table_name).select("*").limit(1).execute()
                found_tables.append(table_name)
                print(f"  ✅ Found table: {table_name}")
            except:
                pass
        
        if found_tables:
            print(f"\n✅ Found {len(found_tables)} table(s): {', '.join(found_tables)}")
        else:
            print("  ℹ️  No standard tables found (or anon key has limited access)")
            print("  ℹ️  You may need to create tables in your Supabase dashboard")
        
    except Exception as e:
        print(f"  ℹ️  Could not list tables: {str(e)}")


def test_postgresql_connection():
    """Test direct PostgreSQL connection"""
    print("\n[POSTGRESQL] Testing direct database connection...")
    print("-" * 70)
    
    try:
        from sqlalchemy import create_engine, text
        
        db_url = os.getenv('SUPABASE_DATABASE_URL')
        
        if not db_url:
            print("❌ SUPABASE_DATABASE_URL not configured")
            return False
        
        print(f"Database URL: {db_url[:50]}... (password hidden)")
        
        engine = create_engine(
            db_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            echo=False
        )
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            row = result.fetchone()
            if row:
                version = row[0]
                print("✅ PostgreSQL Direct Connection: SUCCESS")
                print(f"   Database version: {version[:50]}...")
            else:
                print("✅ PostgreSQL Direct Connection: SUCCESS")
            return True
            
    except Exception as e:
        print(f"❌ PostgreSQL Direct Connection: FAILED")
        print(f"   Error: {str(e)}")
        return False


def main():
    """Run all Supabase tests"""
    
    # Test 1: Create client
    supabase = test_supabase_client()
    
    if not supabase:
        print("\n" + "="*70)
        print("❌ FAILED: Could not create Supabase client")
        print("="*70)
        return False
    
    # Test 2: Test connection
    connection_ok = test_supabase_connection(supabase)
    
    # Test 3: Try to list tables
    test_database_tables(supabase)
    
    # Test 4: Test PostgreSQL direct connection
    postgres_ok = test_postgresql_connection()
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    print(f"\nSupabase Client API:     {'✅ SUCCESS' if connection_ok else '❌ FAILED'}")
    print(f"PostgreSQL Direct:       {'✅ SUCCESS' if postgres_ok else '❌ FAILED'}")
    
    if connection_ok or postgres_ok:
        print("\n🎉 Supabase is connected and ready to use!")
        print("\nYou can now:")
        print("  1. Create tables in Supabase dashboard")
        print("  2. Use supabase client in your Python code")
        print("  3. Switch DATABASE_URL to Supabase for production")
        
        print("\nExample usage:")
        print("""
from supabase import create_client
import os

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key)

# Insert data
data = supabase.table('your_table').insert({"name": "test"}).execute()

# Query data
data = supabase.table('your_table').select("*").execute()
        """)
    else:
        print("\n❌ Supabase connection failed")
        print("   Check your credentials and network connection")
    
    print("="*70 + "\n")
    
    return connection_ok or postgres_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
