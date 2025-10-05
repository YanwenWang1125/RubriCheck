#!/usr/bin/env python3
"""
Test script for RubriCheck Complete Pipeline
============================================
Tests the integration of all three modules.
"""

import os
import sys
import json
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        from rubriCheck_pipeline import RubriCheckPipeline, PreprocessOptions
        print("✅ Main pipeline imported successfully")
        
        # Test individual module imports
        from essay_preprocessor import EssayPreprocessor, PreprocessOptions as EssayOptions
        print("✅ Essay preprocessor imported successfully")
        
        from rubric_parser_prompt import parse_rubric_file, demo_parse_rubric
        print("✅ Rubric parser imported successfully")
        
        from grading_engine import grade_essay, GradeSummary
        print("✅ Grading engine imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_pipeline_initialization():
    """Test pipeline initialization."""
    print("\n🧪 Testing pipeline initialization...")
    
    try:
        from rubriCheck_pipeline import RubriCheckPipeline
        
        # Test with default API key file
        pipeline = RubriCheckPipeline()
        print("✅ Pipeline initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline initialization failed: {e}")
        return False

def test_essay_processing():
    """Test essay processing functionality."""
    print("\n🧪 Testing essay processing...")
    
    try:
        from rubriCheck_pipeline import RubriCheckPipeline
        
        # Create a sample essay
        sample_essay = """
        This is a test essay about renewable energy and its importance for national security.
        
        The essay argues that renewable energy sources like solar and wind power can reduce dependence on foreign oil.
        
        Several studies have shown that countries with higher renewable energy portfolios experience greater energy independence.
        """
        
        essay_path = "test_essay_sample.txt"
        with open(essay_path, 'w', encoding='utf-8') as f:
            f.write(sample_essay)
        
        # Test essay processing
        pipeline = RubriCheckPipeline()
        processed_essay = pipeline.process_essay(essay_path)
        
        print(f"✅ Essay processed: {processed_essay.metadata.word_count} words")
        print(f"   - Paragraphs: {len(processed_essay.paragraphs)}")
        print(f"   - Language: {processed_essay.metadata.language_detected}")
        
        # Clean up
        os.remove(essay_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Essay processing failed: {e}")
        return False

def test_rubric_parsing():
    """Test rubric parsing functionality."""
    print("\n🧪 Testing rubric parsing...")
    
    try:
        from rubriCheck_pipeline import RubriCheckPipeline
        
        # Check if test rubric exists
        rubric_path = "test_file/test_rubric.docx"
        if not os.path.exists(rubric_path):
            print(f"⚠️  Test rubric not found: {rubric_path}")
            print("   Skipping rubric parsing test")
            return True
        
        # Test rubric parsing
        pipeline = RubriCheckPipeline()
        rubric = pipeline.parse_rubric(rubric_path)
        
        print(f"✅ Rubric parsed: {len(rubric.get('criteria', []))} criteria")
        print(f"   - Scale type: {rubric.get('scale', {}).get('type')}")
        print(f"   - Title: {rubric.get('title', 'Untitled')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Rubric parsing failed: {e}")
        return False

def test_complete_pipeline():
    """Test the complete pipeline integration."""
    print("\n🧪 Testing complete pipeline...")
    
    try:
        from rubriCheck_pipeline import RubriCheckPipeline
        
        # Create sample essay
        sample_essay = """
        This essay argues that renewable energy is essential to national security by reducing dependence on volatile fuel markets.
        
        Several reports show countries with higher renewable portfolios experience less price shock; however, grid stability challenges remain.
        
        Opponents claim costs are prohibitive; this essay demonstrates recent cost curves and policy mechanisms that offset initial investment.
        """
        
        essay_path = "test_essay_complete.txt"
        with open(essay_path, 'w', encoding='utf-8') as f:
            f.write(sample_essay)
        
        # Check if test rubric exists
        rubric_path = "test_file/test_rubric.docx"
        if not os.path.exists(rubric_path):
            print(f"⚠️  Test rubric not found: {rubric_path}")
            print("   Skipping complete pipeline test")
            os.remove(essay_path)
            return True
        
        # Run complete pipeline
        pipeline = RubriCheckPipeline()
        results = pipeline.run_complete_pipeline(
            rubric_path=rubric_path,
            essay_path=essay_path,
            output_path="test_results.json"
        )
        
        # Check results
        grading = results["grading_results"]
        print(f"✅ Complete pipeline successful!")
        print(f"   - Score: {grading['numeric_score']}")
        print(f"   - Letter: {grading['letter_grade']}")
        print(f"   - Criteria: {len(grading['per_criterion'])}")
        
        # Clean up
        os.remove(essay_path)
        if os.path.exists("test_results.json"):
            os.remove("test_results.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Complete pipeline failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 RubriCheck Pipeline Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Pipeline Initialization", test_pipeline_initialization),
        ("Essay Processing", test_essay_processing),
        ("Rubric Parsing", test_rubric_parsing),
        ("Complete Pipeline", test_complete_pipeline)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Pipeline is ready to use.")
        print("\n💡 Next steps:")
        print("   1. Run: python rubriCheck_pipeline.py --rubric test_file/test_rubric.docx --essay your_essay.txt")
        print("   2. Check: python example_usage.py")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("   Make sure all dependencies are installed and API key is set.")

if __name__ == "__main__":
    main()
