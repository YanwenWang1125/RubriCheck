#!/usr/bin/env python3
"""
Test script for essay file parsing functionality.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

def test_essay_parsing():
    """Test the essay parsing functionality."""
    print("🧪 Testing Essay File Parsing")
    print("=" * 50)
    
    # Import the function
    try:
        from app import extract_essay_text
        print("✅ Successfully imported extract_essay_text function")
    except ImportError as e:
        print(f"❌ Failed to import: {e}")
        return False
    
    # Test with a simple text file
    test_text = "This is a test essay about renewable energy. It discusses the benefits of solar and wind power."
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_text)
        temp_path = f.name
    
    try:
        result = extract_essay_text(temp_path)
        if result == test_text:
            print("✅ TXT file parsing works correctly")
        else:
            print(f"❌ TXT file parsing failed. Expected: {test_text}, Got: {result}")
            return False
    except Exception as e:
        print(f"❌ TXT file parsing error: {e}")
        return False
    finally:
        os.unlink(temp_path)
    
    # Test error handling
    try:
        result = extract_essay_text("nonexistent_file.txt")
        if "Error extracting text" in result:
            print("✅ Error handling works correctly")
        else:
            print(f"❌ Error handling failed. Got: {result}")
            return False
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False
    
    print("\n🎉 All tests passed!")
    return True

if __name__ == "__main__":
    success = test_essay_parsing()
    sys.exit(0 if success else 1)
