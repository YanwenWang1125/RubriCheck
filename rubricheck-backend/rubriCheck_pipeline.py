#!/usr/bin/env python3
"""
RubriCheck Complete Pipeline
============================
Integrates all three modules:
1. Essay Preprocessor (essay_preprocessor.py)
2. Rubric Parser (rubric_parser_prompt.py) 
3. Grading Engine (grading_engine.py)

Usage:
    python rubriCheck_pipeline.py --rubric path/to/rubric.pdf --essay path/to/essay.txt
    python rubriCheck_pipeline.py --rubric path/to/rubric.docx --essay path/to/essay.pdf --output results.json
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import asdict

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, skip loading .env file
    pass

# Add current directory to path for imports
current_dir = os.getcwd()
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import all three modules
try:
    # Import from essay_preprocessor.py
    from essay_preprocessor import EssayPreprocessor, PreprocessOptions, ProcessedEssay
    
    # Import from rubric_parser_prompt.py  
    from rubric_parser_prompt import parse_rubric_file, demo_parse_rubric
    
    # Import from grading_engine.py
    from grading_engine import grade_essay, GradeSummary, generate_essay_insights, run_grading_example
    
    print("All modules imported successfully!")
    
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all three Python modules are in the same directory")
    print("Available files:")
    for f in os.listdir('.'):
        if f.endswith('.py'):
            print(f"  - {f}")
    sys.exit(1)


class RubriCheckPipeline:
    """
    Complete pipeline that integrates all three RubriCheck modules.
    """
    
    def __init__(self, api_key: str = None):
        """Initialize the pipeline with API key configuration."""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            print("Warning: No OpenAI API key provided. Set OPENAI_API_KEY environment variable.")
        else:
            os.environ["OPENAI_API_KEY"] = self.api_key
            print("API key configured successfully")
    
    def process_essay(self, essay_path: str, options: Optional[PreprocessOptions] = None) -> ProcessedEssay:
        """Step 1: Process essay using essay_preprocessor module."""
        print(f"Processing essay: {essay_path}")
        
        if not os.path.exists(essay_path):
            raise FileNotFoundError(f"Essay file not found: {essay_path}")
            
        with open(essay_path, 'r', encoding='utf-8', errors='ignore') as f:
            essay_text = f.read()
        
        preprocessor = EssayPreprocessor()
        options = options or PreprocessOptions()
        processed_essay = preprocessor.run(essay_text, options)
        
        print(f"Essay processed: {len(processed_essay.paragraphs)} paragraphs, {processed_essay.metadata.word_count} words")
        return processed_essay
    
    def parse_rubric(self, rubric_path: str) -> Dict[str, Any]:
        """Step 2: Parse rubric using rubric_parser_prompt module."""
        print(f"Parsing rubric: {rubric_path}")
        
        if not os.path.exists(rubric_path):
            raise FileNotFoundError(f"Rubric file not found: {rubric_path}")
        
        rubric = demo_parse_rubric(rubric_path)
        
        if not rubric:
            raise ValueError("Failed to parse rubric")
            
        print(f"Rubric parsed: {len(rubric.get('criteria', []))} criteria")
        return rubric
    
    def grade_essay(self, rubric: Dict[str, Any], processed_essay: ProcessedEssay, 
                  max_span_chars: int = 240) -> GradeSummary:
        """Step 3: Grade essay using grading_engine module."""
        print("Grading essay with AI...")
        
        # Pass the full ProcessedEssay object to utilize rich metadata
        converted_rubric = self._convert_rubric_format(rubric)
        summary = grade_essay(converted_rubric, processed_essay, max_span_chars)
        
        print(f"Grading complete: {summary.numeric_score} ({summary.letter})")
        return summary
    
    def _convert_rubric_format(self, rubric: Dict[str, Any]) -> Dict[str, Any]:
        """Convert rubric from parser format to grader format."""
        converted = {
            "criteria": [],
            "grading": {
                "numeric": True,
                "letter_bands": [
                    {"min": 90, "max": 100, "letter": "A+"},
                    {"min": 85, "max": 89.99, "letter": "A"},
                    {"min": 80, "max": 84.99, "letter": "A-"},
                    {"min": 0, "max": 79.99, "letter": "B or below"}
                ],
                "categorical_points_map": {"Excellent": 4, "Good": 3, "Fair": 2, "Poor": 1}
            }
        }
        
        for i, criterion in enumerate(rubric.get('criteria', [])):
            converted_criterion = {
                "id": f"criterion_{i}",
                "name": criterion.get('name', f'Criterion {i+1}'),
                "descriptors": criterion.get('descriptor_by_level', {}),
                "valid_levels": rubric.get('scale', {}).get('levels', ['Excellent', 'Good', 'Fair', 'Poor']),
                "weight": criterion.get('weight', 1.0) / sum(c.get('weight', 1.0) for c in rubric.get('criteria', [])),
                "level_scale_note": " → ".join(rubric.get('scale', {}).get('levels', []))
            }
            converted["criteria"].append(converted_criterion)
        
        return converted
    
    def run_complete_pipeline(self, rubric_path: str, essay_path: str, 
                            output_path: Optional[str] = None,
                            essay_options: Optional[PreprocessOptions] = None) -> Dict[str, Any]:
        """Run the complete pipeline: essay preprocessing → rubric parsing → AI grading."""
        print("Starting RubriCheck Complete Pipeline")
        print("=" * 50)
        
        try:
            # Step 1: Process essay
            processed_essay = self.process_essay(essay_path, essay_options)
            
            # Step 2: Parse rubric
            rubric = self.parse_rubric(rubric_path)
            
            # Step 3: Grade essay
            grade_summary = self.grade_essay(rubric, processed_essay)
            
            # Generate essay insights using preprocessor metadata
            essay_insights = generate_essay_insights(processed_essay)
            
            # Compile results
            results = {
                "pipeline_info": {
                    "rubric_file": rubric_path,
                    "essay_file": essay_path,
                    "timestamp": str(Path().cwd()),
                    "version": "1.0"
                },
                "essay_metadata": asdict(processed_essay.metadata),
                "essay_insights": essay_insights,
                "rubric_info": {
                    "title": rubric.get('title'),
                    "scale_type": rubric.get('scale', {}).get('type'),
                    "criteria_count": len(rubric.get('criteria', [])),
                    "source_parse": rubric.get('source_parse', {})
                },
                "grading_results": {
                    "per_criterion": [asdict(r) for r in grade_summary.per_criterion],
                    "numeric_score": grade_summary.numeric_score,
                    "letter_grade": grade_summary.letter,
                    "categorical_points": grade_summary.categorical_points,
                    "reliability_flags": grade_summary.notes
                },
                "warnings": processed_essay.warnings + rubric.get('source_parse', {}).get('warnings', [])
            }
            
            # Save results if output path provided
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                print(f"Results saved to: {output_path}")
            
            print("\nPipeline completed successfully!")
            return results
            
        except Exception as e:
            print(f"Pipeline failed: {e}")
            raise


# def example_basic_usage():
#     """Basic example of using the pipeline."""
#     print("🔬 Example: Basic Pipeline Usage")
#     print("=" * 40)
    
#     # Initialize pipeline
#     pipeline = RubriCheckPipeline()
    
#     # Example file paths (adjust these to your actual files)
#     rubric_path = "test_file/test_rubric.docx"
#     essay_path = "test_essay.txt"  # You'll need to create this
    
#     # Create a sample essay if it doesn't exist
#     if not os.path.exists(essay_path):
#         sample_essay = """
#         This essay argues that renewable energy is essential to national security by reducing dependence on volatile fuel markets.
        
#         Several reports show countries with higher renewable portfolios experience less price shock; however, grid stability challenges remain.
        
#         Opponents claim costs are prohibitive; this essay demonstrates recent cost curves and policy mechanisms that offset initial investment.
#         """
#         with open(essay_path, 'w', encoding='utf-8') as f:
#             f.write(sample_essay)
#         print(f"📝 Created sample essay: {essay_path}")
    
#     try:
#         # Run complete pipeline
#         results = pipeline.run_complete_pipeline(
#             rubric_path=rubric_path,
#             essay_path=essay_path,
#             output_path="example_results.json"
#         )
        
#         # Print results
#         print("\n📊 Results:")
#         grading = results["grading_results"]
#         print(f"Score: {grading['numeric_score']} ({grading['letter_grade']})")
        
#         return results
        
#     except Exception as e:
#         print(f"❌ Error: {e}")
#         return None


# def example_step_by_step():
#     """Example showing step-by-step pipeline execution."""
#     print("🔍 Example: Step-by-Step Execution")
#     print("=" * 35)
    
#     pipeline = RubriCheckPipeline()
    
#     try:
#         # Step 1: Process essay
#         print("Step 1: Processing essay...")
#         processed_essay = pipeline.process_essay("test_essay.txt")
#         print(f"   - {len(processed_essay.paragraphs)} paragraphs")
#         print(f"   - {processed_essay.metadata.word_count} words")
#         print(f"   - Language: {processed_essay.metadata.language_detected}")
        
#         # Step 2: Parse rubric
#         print("\nStep 2: Parsing rubric...")
#         rubric = pipeline.parse_rubric("test_file/test_rubric.docx")
#         print(f"   - {len(rubric.get('criteria', []))} criteria")
#         print(f"   - Scale type: {rubric.get('scale', {}).get('type')}")
        
#         # Step 3: Grade essay
#         print("\nStep 3: Grading essay...")
#         grade_summary = pipeline.grade_essay(rubric, processed_essay)
#         print(f"   - Score: {grade_summary.numeric_score}")
#         print(f"   - Letter: {grade_summary.letter}")
#         print(f"   - Criteria evaluated: {len(grade_summary.per_criterion)}")
        
#         # Show detailed results
#         print("\n📋 Detailed Results:")
#         for i, criterion in enumerate(grade_summary.per_criterion, 1):
#             print(f"   {i}. {criterion.criterion_id}: {criterion.level}")
#             if criterion.justification:
#                 print(f"      Justification: {criterion.justification[:80]}...")
        
#     except Exception as e:
#         print(f"❌ Error: {e}")


# def main():
#     """Command line interface for the complete pipeline."""
#     parser = argparse.ArgumentParser(
#         description="RubriCheck Complete Pipeline - AI-powered essay grading",
#         formatter_class=argparse.RawDescriptionHelpFormatter,
#         epilog="""
# Examples:
#   python rubriCheck_pipeline.py --rubric rubric.pdf --essay essay.txt
#   python rubriCheck_pipeline.py --rubric rubric.docx --essay essay.pdf --output results.json
#   python rubriCheck_pipeline.py --rubric rubric.txt --essay essay.docx --no-redact
#         """
#     )
    
#     parser.add_argument("--rubric", required=True, help="Path to rubric file (pdf, docx, txt, image)")
#     parser.add_argument("--essay", required=True, help="Path to essay file (txt, docx, pdf, image)")
#     parser.add_argument("--output", help="Path to save results JSON file")
#     parser.add_argument("--api-key-file", default=r"C:\Users\Leo\AI projects\_api.txt", help="Path to API key file")
    
#     # Essay preprocessing options
#     parser.add_argument("--no-redact", action="store_true", help="Disable PII redaction")
#     parser.add_argument("--no-translate", action="store_true", help="Disable translation")
#     parser.add_argument("--target-language", default="en", help="Target language for translation")
#     parser.add_argument("--chunk-size", type=int, default=6, help="Maximum paragraphs per chunk")
    
#     # Grading options
#     parser.add_argument("--max-span-chars", type=int, default=240, help="Maximum characters for evidence spans")
    
#     args = parser.parse_args()
    
#     # Create essay preprocessing options
#     essay_options = PreprocessOptions(
#         target_language=args.target_language,
#         translate_non_english=not args.no_translate,
#         redact_pii=not args.no_redact,
#         chunk_max_paragraphs=args.chunk_size
#     )
    
#     # Initialize and run pipeline
#     pipeline = RubriCheckPipeline(api_key_file=args.api_key_file)
    
#     try:
#         results = pipeline.run_complete_pipeline(
#             rubric_path=args.rubric,
#             essay_path=args.essay,
#             output_path=args.output,
#             essay_options=essay_options
#         )
        
#         # Print summary
#         print("\n📊 GRADING SUMMARY")
#         print("=" * 30)
#         grading = results["grading_results"]
#         print(f"Overall Score: {grading['numeric_score']} ({grading['letter_grade']})")
#         print(f"Criteria Evaluated: {len(grading['per_criterion'])}")
        
#         print("\n📝 CRITERION BREAKDOWN")
#         print("-" * 30)
#         for i, criterion in enumerate(grading['per_criterion'], 1):
#             print(f"{i}. {criterion['criterion_id']}: {criterion['level']}")
#             if criterion.get('justification'):
#                 print(f"   Justification: {criterion['justification'][:100]}...")
#             if criterion.get('actionable_suggestion'):
#                 print(f"   Suggestion: {criterion['actionable_suggestion']}")
#             print()
        
#         if results.get('warnings'):
#             print("⚠️  WARNINGS")
#             print("-" * 20)
#             for warning in results['warnings']:
#                 print(f"• {warning}")
        
#     except Exception as e:
#         print(f"❌ Pipeline execution failed: {e}")
#         sys.exit(1)


def example_basic_usage():
    """Basic example of using the pipeline."""
    print("🔬 Example: Basic Pipeline Usage")
    print("=" * 40)
    
    # Initialize pipeline
    pipeline = RubriCheckPipeline()
    
    # Example file paths (adjust these to your actual files)
    rubric_path = "test_file/test_rubric.docx"
    essay_path = "test_essay.txt"  # You'll need to create this
    
    # Create a sample essay if it doesn't exist
    if not os.path.exists(essay_path):
        sample_essay = """
        This essay argues that renewable energy is essential to national security by reducing dependence on volatile fuel markets.
        
        Several reports show countries with higher renewable portfolios experience less price shock; however, grid stability challenges remain.
        
        Opponents claim costs are prohibitive; this essay demonstrates recent cost curves and policy mechanisms that offset initial investment.
        """
        with open(essay_path, 'w', encoding='utf-8') as f:
            f.write(sample_essay)
        print(f"📝 Created sample essay: {essay_path}")
    
    try:
        # Run complete pipeline
        results = pipeline.run_complete_pipeline(
            rubric_path=rubric_path,
            essay_path=essay_path,
            output_path="example_results.json"
        )
        
        # Print results
        print("\n📊 Results:")
        grading = results["grading_results"]
        print(f"Score: {grading['numeric_score']} ({grading['letter_grade']})")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def example_step_by_step():
    """Example showing step-by-step pipeline execution."""
    print("🔍 Example: Step-by-Step Execution")
    print("=" * 35)
    
    pipeline = RubriCheckPipeline()
    
    try:
        # Step 1: Process essay
        print("Step 1: Processing essay...")
        processed_essay = pipeline.process_essay("test_essay.txt")
        print(f"   - {len(processed_essay.paragraphs)} paragraphs")
        print(f"   - {processed_essay.metadata.word_count} words")
        print(f"   - Language: {processed_essay.metadata.language_detected}")
        
        # Step 2: Parse rubric
        print("\nStep 2: Parsing rubric...")
        rubric = pipeline.parse_rubric("test_file/test_rubric.docx")
        print(f"   - {len(rubric.get('criteria', []))} criteria")
        print(f"   - Scale type: {rubric.get('scale', {}).get('type')}")
        
        # Step 3: Grade essay
        print("\nStep 3: Grading essay...")
        grade_summary = pipeline.grade_essay(rubric, processed_essay)
        print(f"   - Score: {grade_summary.numeric_score}")
        print(f"   - Letter: {grade_summary.letter}")
        print(f"   - Criteria evaluated: {len(grade_summary.per_criterion)}")
        
        # Show detailed results
        print("\n📋 Detailed Results:")
        for i, criterion in enumerate(grade_summary.per_criterion, 1):
            print(f"   {i}. {criterion.criterion_id}: {criterion.level}")
            if criterion.justification:
                print(f"      Justification: {criterion.justification[:80]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Manual configuration - modify these parameters as needed
    run_basic_example = True      # Set to True to run basic usage example
    run_step_by_step = True       # Set to True to run step-by-step example
    run_custom_pipeline = False   # Set to True to run custom pipeline
    
    # Custom pipeline parameters (used if run_custom_pipeline = True)
    custom_rubric_path = "test_file/test_rubric.docx"  # Path to your rubric file
    custom_essay_path = "test_essay.txt"               # Path to your essay file
    custom_output_path = "custom_results.json"         # Output file for results
    custom_api_key = None                              # Set to your API key or None to use env var
    
    # Essay preprocessing options
    essay_options = PreprocessOptions(
        target_language="en",           # Target language for translation
        translate_non_english=True,     # Enable/disable translation
        redact_pii=True,               # Enable/disable PII redaction
        chunk_max_paragraphs=6,        # Max paragraphs per chunk
        chunk_overlap_paragraphs=1     # Overlap between chunks
    )
    
    print("🚀 RubriCheck Pipeline Examples")
    print("=" * 50)
    print(f"Configuration:")
    print(f"  - Basic Example: {'Enabled' if run_basic_example else 'Disabled'}")
    print(f"  - Step-by-Step Example: {'Enabled' if run_step_by_step else 'Disabled'}")
    print(f"  - Custom Pipeline: {'Enabled' if run_custom_pipeline else 'Disabled'}")
    print()
    
    # Run Basic Usage Example
    if run_basic_example:
        print("Running basic usage example...")
        print("-" * 30)
        example_basic_usage()
        print()
    
    # Run Step-by-Step Example
    if run_step_by_step:
        print("Running step-by-step example...")
        print("-" * 30)
        example_step_by_step()
        print()
    
    # Run Custom Pipeline
    if run_custom_pipeline:
        print("Running custom pipeline...")
        print("-" * 30)
        
        try:
            # Initialize pipeline with custom API key
            pipeline = RubriCheckPipeline(api_key=custom_api_key)
            
            # Run complete pipeline with custom parameters
            results = pipeline.run_complete_pipeline(
                rubric_path=custom_rubric_path,
                essay_path=custom_essay_path,
                output_path=custom_output_path,
                essay_options=essay_options
            )
            
            # Print custom results
            print("\n📊 Custom Pipeline Results:")
            grading = results["grading_results"]
            print(f"Overall Score: {grading['numeric_score']} ({grading['letter_grade']})")
            print(f"Criteria Evaluated: {len(grading['per_criterion'])}")
            
            print("\n📝 Criterion Breakdown:")
            for i, criterion in enumerate(grading['per_criterion'], 1):
                print(f"{i}. {criterion['criterion_id']}: {criterion['level']}")
                if criterion.get('justification'):
                    print(f"   Justification: {criterion['justification'][:100]}...")
                if criterion.get('actionable_suggestion'):
                    print(f"   Suggestion: {criterion['actionable_suggestion']}")
                print()
            
            if results.get('warnings'):
                print("⚠️  Warnings:")
                for warning in results['warnings']:
                    print(f"• {warning}")
            
        except Exception as e:
            print(f"❌ Custom pipeline failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n🎉 All examples completed!")
