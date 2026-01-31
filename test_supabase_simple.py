#!/usr/bin/env python3
"""
Simple Supabase PostgreSQL Connection Test
Tests the database connection without using the Supabase SDK
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*70)
print("SUPABASE DATABASE CONNECTION TEST")
print("="*70)

def test_postgresql_connection():
    """Test direct PostgreSQL connection to Supabase"""
    print("\n[1/2] Testing PostgreSQL Connection...")
    print("-" * 70)
    
    try:
        from sqlalchemy import create_engine, text, inspect
        
        db_url = os.getenv('SUPABASE_DATABASE_URL')
        
        if not db_url:
            print("❌ SUPABASE_DATABASE_URL not configured in .env")
            return False
        
        print(f"Database URL: postgresql://postgres:***@{db_url.split('@')[1] if '@' in db_url else 'unknown'}")
        
        print("\nConnecting to Supabase PostgreSQL...")
        engine = create_engine(
            db_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            echo=False,
            connect_args={'connect_timeout': 10}
        )
        
        with engine.connect() as connection:
            # Test 1: Basic query
            result = connection.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print("✅ Basic query: SUCCESS")
            
            # Test 2: Get database version
            result = connection.execute(text("SELECT version()"))
            row = result.fetchone()
            if row:
                version = row[0]
                print(f"✅ Database version: {version[:60]}...")
            
            # Test 3: Get current database name
            result = connection.execute(text("SELECT current_database()"))
            row = result.fetchone()
            if row:
                db_name = row[0]
                print(f"✅ Connected to database: {db_name}")
            
            # Test 4: List schemas
            result = connection.execute(text("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name NOT IN ('pg_catalog', 'information_schema')
                ORDER BY schema_name
            """))
            schemas = [row[0] for row in result.fetchall()]
            print(f"✅ Available schemas: {', '.join(schemas) if schemas else 'None (default: public)'}")
            
            return True
            
    except Exception as e:
        print(f"❌ PostgreSQL Connection FAILED")
        print(f"   Error: {str(e)}")
        return False


def test_tables():
    """List tables in the database"""
    print("\n[2/2] Checking Database Schema...")
    print("-" * 70)
    
    try:
        from sqlalchemy import create_engine, text
        
        db_url = os.getenv('SUPABASE_DATABASE_URL')
        if not db_url:
            print("❌ SUPABASE_DATABASE_URL not configured")
            return False
            
        engine = create_engine(db_url, pool_pre_ping=True)
        
        with engine.connect() as connection:
            # List tables in public schema
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result.fetchall()]
            
            if tables:
                print(f"✅ Found {len(tables)} table(s) in database:")
                for table in tables:
                    print(f"   - {table}")
            else:
                print("ℹ️  No tables found in 'public' schema")
                print("   This is normal for a new database")
                print("   You can create tables using:")
                print("     1. Supabase Dashboard (https://app.supabase.com)")
                print("     2. Python SQLAlchemy migrations")
                print("     3. SQL commands")
            
            return True
            
    except Exception as e:
        print(f"⚠️  Could not list tables: {str(e)}")
        return False


def test_supabase_api():
    """Test Supabase REST API access"""
    print("\n[BONUS] Testing Supabase REST API...")
    print("-" * 70)
    
    try:
        import requests
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("⚠️  Supabase API credentials not configured")
            return False
        
        # Test health endpoint
        health_url = f"{supabase_url}/rest/v1/"
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}"
        }
        
        response = requests.get(health_url, headers=headers, timeout=10)
        
        if response.status_code in [200, 404]:  # 404 is OK, means API is accessible
            print(f"✅ Supabase REST API: Accessible")
            print(f"   Base URL: {supabase_url}")
            return True
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠️  Could not test API: {str(e)}")
        return False


def main():
    """Run all tests"""
    
    postgres_ok = test_postgresql_connection()
    
    if postgres_ok:
        test_tables()
        test_supabase_api()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    if postgres_ok:
        print("\n🎉 SUCCESS! Supabase PostgreSQL is connected!")
        print("\nYour Supabase database is ready to use!")
        print("\nNext Steps:")
        print("  1. Create tables in Supabase Dashboard or via migrations")
        print("  2. Update DATABASE_URL to use Supabase in production:")
        print("     DATABASE_URL=postgresql://postgres:***@db.xaaglooqmwzhitwdlcnz...")
        print("  3. Use SQLAlchemy to interact with the database")
        
        print("\nExample Python Code:")
        print("""
from sqlalchemy import create_engine
import os

db_url = os.getenv('SUPABASE_DATABASE_URL')
engine = create_engine(db_url)

with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM your_table"))
    for row in result:
        print(row)
        """)
    else:
        print("\n❌ Supabase connection failed")
        print("   Check:")
        print("   - Network connectivity")
        print("   - Database URL and password in .env")
        print("   - Supabase project is active")
    
    print("="*70 + "\n")
    
    return postgres_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
