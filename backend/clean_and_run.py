#!/usr/bin/env python3
"""
Clean and Run - Cleanup browser locks and run automation
This script ensures no stale browser processes are blocking execution
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def cleanup_browser():
    """Clean up browser processes and lock files"""
    print("="*70)
    print("🧹 CLEANUP - Removing stale browser processes and lock files")
    print("="*70)
    
    # 1. Kill any Chromium processes
    print("\n1. Killing Chromium processes...")
    try:
        result = subprocess.run(['pkill', '-f', 'chromium'], capture_output=True)
        if result.returncode == 0:
            print("   ✅ Killed Chromium processes")
        else:
            print("   ℹ️  No Chromium processes found")
    except Exception as e:
        print(f"   ⚠️  Could not kill processes: {e}")
    
    # 2. Kill any Playwright processes
    print("\n2. Killing Playwright processes...")
    try:
        result = subprocess.run(['pkill', '-f', 'playwright'], capture_output=True)
        if result.returncode == 0:
            print("   ✅ Killed Playwright processes")
        else:
            print("   ℹ️  No Playwright processes found")
    except Exception as e:
        print(f"   ⚠️  Could not kill processes: {e}")
    
    # 3. Remove browser profile lock files
    print("\n3. Removing browser profile lock files...")
    profile_dir = Path("browser_profile")
    
    if profile_dir.exists():
        lock_files = [
            profile_dir / "SingletonLock",
            profile_dir / "SingletonSocket",
            profile_dir / "SingletonCookie"
        ]
        
        removed_count = 0
        for lock_file in lock_files:
            if lock_file.exists():
                try:
                    lock_file.unlink()
                    print(f"   ✅ Removed: {lock_file.name}")
                    removed_count += 1
                except Exception as e:
                    print(f"   ⚠️  Could not remove {lock_file.name}: {e}")
        
        if removed_count == 0:
            print("   ℹ️  No lock files found")
    else:
        print("   ℹ️  No browser profile directory found")
    
    # 4. Optional: Remove entire browser profile (uncomment if needed)
    # print("\n4. Remove entire browser profile? (y/n)")
    # response = input("   > ").strip().lower()
    # if response == 'y':
    #     if profile_dir.exists():
    #         shutil.rmtree(profile_dir)
    #         print("   ✅ Removed entire browser profile")
    #     else:
    #         print("   ℹ️  No profile to remove")
    
    print("\n✅ Cleanup complete!")
    print("="*70)

def main():
    """Main execution"""
    print("\n" + "="*70)
    print("🚀 LINKEDIN AUTOMATION - CLEAN START")
    print("="*70)
    
    # Cleanup first
    cleanup_browser()
    
    # Ask which script to run
    print("\n📋 Which script do you want to run?")
    print("   1. Complete System Test (test_complete_system.py)")
    print("   2. Quick Login/Search Test (test_login_search.py)")
    print("   3. Full Automation (demo_automation.py)")
    print("   4. Exit (cleanup only)")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    scripts = {
        '1': 'test_complete_system.py',
        '2': 'test_login_search.py',
        '3': 'demo_automation.py'
    }
    
    if choice == '4':
        print("\n✅ Cleanup complete. Exiting.")
        return
    
    if choice not in scripts:
        print("\n❌ Invalid choice. Exiting.")
        return
    
    script = scripts[choice]
    
    print(f"\n🚀 Running: {script}")
    print("="*70)
    print()
    
    # Run the selected script
    try:
        subprocess.run(['python3', script])
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error running script: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
