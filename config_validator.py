#!/usr/bin/env python3
"""
Configuration Validator
Validates that all required environment variables are properly set
"""

import os
from dotenv import load_dotenv

def validate_config():
    """Validate all required environment variables"""
    load_dotenv()
    
    required_vars = {
        "OPENAI_API_KEY": "OpenAI API key for embeddings and chat",
        "SUPABASE_URL": "Supabase project URL",
        "SUPABASE_SERVICE_KEY": "Supabase service role key",
        "SUPABASE_DB_HOST": "Supabase database host (optional for direct DB access)",
        "SUPABASE_DB_PASSWORD": "Supabase database password (optional for direct DB access)"
    }
    
    missing_vars = []
    present_vars = []
    
    print("🔍 Validating Configuration...")
    print("=" * 50)
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive values for display
            if "KEY" in var or "PASSWORD" in var:
                display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
            present_vars.append(var)
        else:
            print(f"❌ {var}: Missing - {description}")
            missing_vars.append(var)
    
    print("\n" + "=" * 50)
    
    if missing_vars:
        print(f"❌ Configuration incomplete!")
        print(f"Missing variables: {', '.join(missing_vars)}")
        print(f"Please update your .env file with the missing values.")
        return False
    else:
        print(f"✅ Configuration complete!")
        print(f"All {len(present_vars)} required variables are set.")
        return True

def main():
    if validate_config():
        print(f"\n🚀 Ready to run RAG processing!")
    else:
        print(f"\n⚠️  Please fix configuration before proceeding.")

if __name__ == "__main__":
    main()