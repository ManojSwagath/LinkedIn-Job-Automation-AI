#!/usr/bin/env python3
"""
Comprehensive Database Connection Status Report
Tests all configured databases and provides detailed status
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*80)
print("🔌 DATABASE CONNECTION STATUS REPORT")
print("="*80)

def test_sqlite():
    """Test SQLite Connection"""
    print("\n[1/4] Testing SQLite Connection...")
    print("-" * 80)
    
    try:
        from sqlalchemy import create_engine, text
        
        db_url = os.getenv('DATABASE_URL', 'sqlite:///./data/autoagenthire.db')
        print(f"Database: {db_url}")
        
        engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False}
        )
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ SQLite Connection: SUCCESS")
            print(f"   Status: Database is operational")
            return True
            
    except Exception as e:
        print(f"❌ SQLite Connection: FAILED")
        print(f"   Error: {str(e)}")
        return False


def test_models():
    """Test Database Models"""
    print("\n[2/4] Testing Database Models...")
    print("-" * 80)
    
    try:
        from backend.database.models_complete import Base
        
        tables = list(Base.metadata.tables.keys())
        print(f"✅ Models Loaded: SUCCESS")
        print(f"   Tables defined: {len(tables)}")
        for table in sorted(tables):
            print(f"     - {table}")
        return True
        
    except Exception as e:
        print(f"❌ Models: FAILED")
        print(f"   Error: {str(e)}")
        return False


def test_supabase_postgresql():
    """Test Supabase PostgreSQL Connection"""
    print("\n[3/4] Testing Supabase PostgreSQL Connection...")
    print("-" * 80)
    
    try:
        from sqlalchemy import create_engine, text
        
        db_url = os.getenv('SUPABASE_DATABASE_URL')
        
        if not db_url:
            print("❌ SUPABASE_DATABASE_URL not configured")
            return False
        
        # Parse and display masked URL
        parts = db_url.split('@')
        if len(parts) == 2:
            host_part = parts[1]
            print(f"Host: {host_part}")
        
        engine = create_engine(
            db_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True
        )
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Supabase PostgreSQL: SUCCESS")
            print(f"   Status: Database is connected")
            return True
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Supabase PostgreSQL: FAILED")
        
        # Provide helpful feedback based on error type
        if "Tenant or user not found" in error_msg:
            print(f"   Error: Tenant or user not found")
            print(f"   Cause: Username or connection string format incorrect")
            print(f"   Action: Verify credentials from Supabase dashboard")
        elif "could not translate host name" in error_msg:
            print(f"   Error: DNS resolution failed")
            print(f"   Cause: Cannot reach the database server")
            print(f"   Action: Check network connectivity")
        else:
            print(f"   Error: {error_msg[:100]}")
        
        return False


def test_supabase_api():
    """Test Supabase REST API Credentials"""
    print("\n[4/4] Testing Supabase REST API Configuration...")
    print("-" * 80)
    
    try:
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url:
            print("❌ SUPABASE_URL not configured")
            return False
        
        if not supabase_key:
            print("❌ SUPABASE_KEY not configured")
            return False
        
        print(f"✅ Supabase REST API: CONFIGURED")
        print(f"   URL: {supabase_url}")
        print(f"   Key: {supabase_key[:30]}...{supabase_key[-10:]}")
        return True
        
    except Exception as e:
        print(f"❌ Supabase API: FAILED")
        print(f"   Error: {str(e)}")
        return False


def main():
    """Run all tests and provide summary"""
    
    results = {
        "SQLite": test_sqlite(),
        "Models": test_models(),
        "Supabase PostgreSQL": test_supabase_postgresql(),
        "Supabase API": test_supabase_api(),
    }
    
    # Summary
    print("\n" + "="*80)
    print("📊 CONNECTION STATUS SUMMARY")
    print("="*80)
    
    print("\n| Database Component | Status |")
    print("|-------------------|--------|")
    for name, status in results.items():
        symbol = "✅" if status else "❌"
        print(f"| {name:<17} | {symbol} {'PASS' if status else 'FAIL':<5} |")
    
    sqlite_ok = results["SQLite"] and results["Models"]
    supabase_ok = results["Supabase PostgreSQL"]
    api_ok = results["Supabase API"]
    
    print("\n" + "="*80)
    print("🎯 APPLICATION STATUS")
    print("="*80)
    
    if sqlite_ok:
        print("\n✅ **YOUR APP IS READY TO RUN!**")
        print("   - SQLite database is working")
        print("   - All database models are loaded")
        print("   - You can start using your application immediately")
        print("\n   To start your app:")
        print("   ```bash")
        print("   python start_system.py")
        print("   ```")
    else:
        print("\n⚠️  SQLite database issue detected")
    
    if supabase_ok:
        print("\n✅ Supabase PostgreSQL database is connected!")
        print("   You can switch to this for production")
    else:
        print("\n⚠️  Supabase PostgreSQL not connected (Optional)")
        print("   You can still use SQLite for now")
    
    if api_ok:
        print("\n✅ Supabase REST API credentials are configured")
        print("   Ready for API operations")
    
    print("\n" + "="*80)
    print("💡 RECOMMENDATIONS")
    print("="*80)
    
    if sqlite_ok:
        print("\n✅ For Development:")
        print("   - Continue with SQLite (already working)")
        print("   - Your app is fully functional")
    
    if not supabase_ok and api_ok:
        print("\n⚠️  For Supabase PostgreSQL:")
        print("   - Get the correct connection string from:")
        print("     https://app.supabase.com")
        print("   - Settings → Database → Connection String")
        print("   - Update SUPABASE_DATABASE_URL in .env")
        print("   - Run this test again to verify")
    
    if sqlite_ok:
        print("\n🚀 FOR PRODUCTION:")
        print("   1. Setup complete Supabase PostgreSQL connection")
        print("   2. Change DATABASE_URL to point to Supabase")
        print("   3. Run migrations to create production tables")
        print("   4. Deploy with confidence!")
    
    print("\n" + "="*80 + "\n")
    
    return sqlite_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
