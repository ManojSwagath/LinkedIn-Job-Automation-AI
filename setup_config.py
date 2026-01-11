#!/usr/bin/env python3
"""
Setup Configuration Script
Updates .env file with Qdrant and GitHub API keys
"""
import os
from pathlib import Path

def setup_configuration():
    """Setup all required API keys and configuration"""
    
    print("🔧 LinkedIn Job Automation - Configuration Setup")
    print("=" * 60)
    
    env_file = Path(__file__).parent / ".env"
    
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    
    # Read current .env
    with open(env_file, 'r') as f:
        env_content = f.read()
    
    print("\n📝 Current Configuration:")
    print("-" * 60)
    
    # Check Qdrant
    if 'QDRANT_URL=' in env_content and 'QDRANT_API_KEY=' in env_content:
        # Extract values
        for line in env_content.split('\n'):
            if line.startswith('QDRANT_URL='):
                qdrant_url = line.split('=', 1)[1].strip()
                if qdrant_url and not qdrant_url.startswith('http'):
                    print("⚠️  Qdrant URL: Not configured")
                else:
                    print(f"✅ Qdrant URL: {qdrant_url[:50]}...")
            elif line.startswith('QDRANT_API_KEY='):
                qdrant_key = line.split('=', 1)[1].strip()
                if qdrant_key and len(qdrant_key) > 10:
                    print(f"✅ Qdrant API Key: {qdrant_key[:20]}...")
                else:
                    print("⚠️  Qdrant API Key: Not configured")
    
    # Check GitHub API Key
    github_configured = False
    for line in env_content.split('\n'):
        if line.startswith('GITHUB_API_KEY='):
            github_key = line.split('=', 1)[1].strip()
            if github_key and len(github_key) > 10:
                print(f"✅ GitHub API Key: {github_key[:20]}...")
                github_configured = True
            else:
                print("⚠️  GitHub API Key: Not configured")
    
    # Check LinkedIn credentials
    linkedin_configured = False
    for line in env_content.split('\n'):
        if line.startswith('LINKEDIN_EMAIL='):
            email = line.split('=', 1)[1].strip()
            if email and '@' in email:
                print(f"✅ LinkedIn Email: {email}")
                linkedin_configured = True
            else:
                print("⚠️  LinkedIn Email: Not configured")
    
    # Check Gemini API
    for line in env_content.split('\n'):
        if line.startswith('GEMINI_API_KEY='):
            gemini_key = line.split('=', 1)[1].strip()
            if gemini_key and len(gemini_key) > 10:
                print(f"✅ Gemini API Key: {gemini_key[:20]}...")
            else:
                print("⚠️  Gemini API Key: Not configured")
    
    print("-" * 60)
    print("\n🎯 Configuration Status:")
    
    if linkedin_configured:
        print("✅ LinkedIn credentials configured")
    else:
        print("❌ LinkedIn credentials missing")
    
    if 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9' in env_content:
        print("✅ Qdrant vector database configured")
    else:
        print("⚠️  Qdrant needs configuration")
    
    if github_configured:
        print("✅ GitHub API for GPT-4o configured")
    else:
        print("⚠️  GitHub API key needs to be added")
    
    print("\n" + "=" * 60)
    
    # Offer to add GitHub API key if missing
    if not github_configured:
        print("\n💡 To add your GitHub API key:")
        print("   1. Get your GitHub token from: https://github.com/settings/tokens")
        print("   2. Add it to .env file: GITHUB_API_KEY=your_token_here")
        print("\nWould you like to add it now? (y/n): ", end="")
        
        try:
            response = input().strip().lower()
            if response == 'y':
                print("\nEnter your GitHub API key: ", end="")
                github_key = input().strip()
                
                if github_key:
                    # Update .env file
                    env_content = env_content.replace(
                        'GITHUB_API_KEY=',
                        f'GITHUB_API_KEY={github_key}'
                    )
                    
                    with open(env_file, 'w') as f:
                        f.write(env_content)
                    
                    print("✅ GitHub API key added successfully!")
                    return True
        except (KeyboardInterrupt, EOFError):
            print("\n\n⚠️  Setup cancelled")
            return False
    
    return True

if __name__ == "__main__":
    try:
        setup_configuration()
        print("\n✅ Configuration check complete!")
        print("\n🚀 Next steps:")
        print("   1. Make sure all API keys are configured in .env")
        print("   2. Run: python3 scripts/initialize_system.py")
        print("   3. Start servers: python3 scripts/start_all.py")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
