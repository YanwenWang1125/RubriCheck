#!/usr/bin/env python3
"""
Test OpenAI API Key Validity
============================
Simple script to check if your OpenAI API key is valid and working.
"""

import os
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env file from the project root
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"[OK] Loaded environment variables from {env_path}")
    else:
        print(f"[ERROR] No .env file found at {env_path}")
        sys.exit(1)
except ImportError:
    print("[ERROR] python-dotenv not installed. Install it with: pip install python-dotenv")
    sys.exit(1)

def test_api_key():
    """Test if the OpenAI API key is valid."""
    print("\n[TEST] Testing OpenAI API Key...")
    print("=" * 50)
    
    # Check if API key exists
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("[ERROR] OPENAI_API_KEY not found in environment variables")
        return False
    
    # Check API key format
    if not api_key.startswith('sk-'):
        print("[ERROR] API key format is invalid (should start with 'sk-')")
        print(f"   Current key starts with: {api_key[:10]}...")
        return False
    
    print(f"[OK] API key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Test API key with OpenAI client
    try:
        from openai import OpenAI
        
        print("[TEST] Testing API key with OpenAI...")
        client = OpenAI(api_key=api_key)
        
        # Make a simple test request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello! This is a test message."}],
            max_tokens=10
        )
        
        print("[SUCCESS] API key is valid and working!")
        print(f"   Test response: {response.choices[0].message.content}")
        return True
        
    except ImportError:
        print("[ERROR] OpenAI library not installed. Install it with: pip install openai")
        return False
    except Exception as e:
        print(f"[ERROR] API key test failed: {e}")
        return False

def check_environment():
    """Check the environment setup."""
    print("[CHECK] Environment Check")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check required packages
    required_packages = ['openai', 'python-dotenv']
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"[OK] {package} is installed")
        except ImportError:
            print(f"[ERROR] {package} is not installed")
    
    # Check .env file
    env_file = Path('.env')
    if env_file.exists():
        print(f"[OK] .env file exists: {env_file.absolute()}")
        
        # Check if API key is in .env file
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'OPENAI_API_KEY=' in content:
                print("[OK] OPENAI_API_KEY found in .env file")
            else:
                print("[ERROR] OPENAI_API_KEY not found in .env file")
    else:
        print("[ERROR] .env file not found")

if __name__ == "__main__":
    print("[START] OpenAI API Key Validator")
    print("=" * 50)
    
    check_environment()
    
    if test_api_key():
        print("\n[SUCCESS] Your API key is valid and ready to use!")
        print("   You can now run the RubriCheck application.")
    else:
        print("\n[FAILED] API key validation failed.")
        print("   Please check your API key and try again.")
        print("\n[HELP] To fix this:")
        print("   1. Make sure you have a valid OpenAI API key")
        print("   2. Update the .env file with your actual API key")
        print("   3. Run this script again to verify")
