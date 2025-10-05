#!/usr/bin/env python3
"""
RubriCheck Complete Pipeline
============================
Integrates all three modules:
1. Essay Preprocessor (essay_preprocessor.ipynb)
2. Rubric Parser (rubric_parser_prompt.ipynb) 
3. Grading Engine (grading_engine.ipynb)

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

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import all three modules
try:
    # Import from essay_preprocessor.ipynb
    from essay_preprocessor import EssayPreprocessor, PreprocessOptions, ProcessedEssay
    
    # Import from rubric_parser_prompt.ipynb  
    from rubric_parser_prompt import parse_rubric_file, demo_parse_rubric
    
    # Import from grading_engine.ipynb (formerly rubriCheck.ipynb)
    from grading_engine import grade_essay, GradeSummary
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all three notebook modules are in the same directory")
    sys.exit(1)


class RubriCheckPipeline:
    """
    Complete pipeline that integrates all three RubriCheck modules.
    """
    
    def __init__(self, api_key_file: str = "../api.txt"):
        """Initialize the pipeline with API key configuration."""
        self.api_key_file = api_key_file
        self._setup_api_key()
        
    def _setup_api_key(self):
        """Set up API key from file."""
        try:
            with open(self.api_key_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith('rubriCheck:'):
                        api_key = line.strip().split(':', 1)[1].strip()
                        os.environ["OPENAI_API_KEY"] = api_key
                        print("✅ API key loaded successfully")
                        return
            raise ValueError("rubriCheck API key not found in file")
        except FileNotFoundError:
            print(f"❌ API file not found at {self.api_key_file}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error loading API key: {e}")
            sys.exit(1)
    
    def process_essay(self, essay_path: str, options: Optional[PreprocessOptions] = None) -> ProcessedEssay:
        """
        Step 1: Process essay using essay_preprocessor module.
        
        Args:
            essay_path: Path to essay file (txt, docx, pdf, image)
            options: Preprocessing options
            
        Returns:
            ProcessedEssay object with structured data
        """
        print(f"📝 Processing essay: {essay_path}")
        
        # Read essay file
        if not os.path.exists(essay_path):
            raise FileNotFoundError(f"Essay file not found: {essay_path}")
            
        with open(essay_path, 'r', encoding='utf-8', errors='ignore') as f:
            essay_text = f.read()
        
        # Process essay
        preprocessor = EssayPreprocessor()
        options = options or PreprocessOptions()
        processed_essay = preprocessor.run(essay_text, options)
        
        print(f"✅ Essay processed: {len(processed_essay.paragraphs)} paragraphs, {processed_essay.metadata.word_count} words")
        return processed_essay
    
    def parse_rubric(self, rubric_path: str) -> Dict[str, Any]:
        """
        Step 2: Parse rubric using rubric_parser_prompt module.
        
        Args:
            rubric_path: Path to rubric file (pdf, docx, txt, image)
            
        Returns:
            Parsed rubric dictionary
        """
        print(f"📋 Parsing rubric: {rubric_path}")
        
        if not os.path.exists(rubric_path):
            raise FileNotFoundError(f"Rubric file not found: {rubric_path}")
        
        # Parse rubric
        rubric = demo_parse_rubric(rubric_path)
        
        if not rubric:
            raise ValueError("Failed to parse rubric")
            
        print(f"✅ Rubric parsed: {len(rubric.get('criteria', []))} criteria")
        return rubric
    
    def grade_essay(self, rubric: Dict[str, Any], processed_essay: ProcessedEssay, 
                  max_span_chars: int = 240) -> GradeSummary:
        """
        Step 3: Grade essay using rubriCheck module.
        
        Args:
            rubric: Parsed rubric dictionary
            processed_essay: Processed essay object
            max_span_chars: Maximum characters for evidence spans
            
        Returns:
            GradeSummary with results
        """
        print("🤖 Grading essay with AI...")
        
        # Convert processed essay to format expected by grader
        essay_paragraphs = [p.text for p in processed_essay.paragraphs if p.text.strip()]
        
        # Convert rubric to expected format
        converted_rubric = self._convert_rubric_format(rubric)
        
        # Grade the essay
        summary = grade_essay(converted_rubric, essay_paragraphs, max_span_chars)
        
        print(f"✅ Grading complete: {summary.numeric_score} ({summary.letter})")
        return summary
    
    def _convert_rubric_format(self, rubric: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert rubric from parser format to grader format.
        
        Args:
            rubric: Rubric from parser
            
        Returns:
            Converted rubric for grader
        """
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
        
        # Convert criteria
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
        """
        Run the complete pipeline: essay preprocessing → rubric parsing → AI grading.
        
        Args:
            rubric_path: Path to rubric file
            essay_path: Path to essay file  
            output_path: Optional path to save results JSON
            essay_options: Optional essay preprocessing options
            
        Returns:
            Complete results dictionary
        """
        print("🚀 Starting RubriCheck Complete Pipeline")
        print("=" * 50)
        
        try:
            # Step 1: Process essay
            processed_essay = self.process_essay(essay_path, essay_options)
            
            # Step 2: Parse rubric
            rubric = self.parse_rubric(rubric_path)
            
            # Step 3: Grade essay
            grade_summary = self.grade_essay(rubric, processed_essay)
            
            # Compile results
            results = {
                "pipeline_info": {
                    "rubric_file": rubric_path,
                    "essay_file": essay_path,
                    "timestamp": str(Path().cwd()),
                    "version": "1.0"
                },
                "essay_metadata": asdict(processed_essay.metadata),
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
                print(f"💾 Results saved to: {output_path}")
            
            print("\n🎉 Pipeline completed successfully!")
            return results
            
        except Exception as e:
            print(f"❌ Pipeline failed: {e}")
            raise


def main():
    """Command line interface for the complete pipeline."""
    parser = argparse.ArgumentParser(
        description="RubriCheck Complete Pipeline - AI-powered essay grading",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python rubriCheck_pipeline.py --rubric rubric.pdf --essay essay.txt
  python rubriCheck_pipeline.py --rubric rubric.docx --essay essay.pdf --output results.json
  python rubriCheck_pipeline.py --rubric rubric.txt --essay essay.docx --no-redact
        """
    )
    
    parser.add_argument("--rubric", required=True, help="Path to rubric file (pdf, docx, txt, image)")
    parser.add_argument("--essay", required=True, help="Path to essay file (txt, docx, pdf, image)")
    parser.add_argument("--output", help="Path to save results JSON file")
    parser.add_argument("--api-key-file", default="../api.txt", help="Path to API key file")
    
    # Essay preprocessing options
    parser.add_argument("--no-redact", action="store_true", help="Disable PII redaction")
    parser.add_argument("--no-translate", action="store_true", help="Disable translation")
    parser.add_argument("--target-language", default="en", help="Target language for translation")
    parser.add_argument("--chunk-size", type=int, default=6, help="Maximum paragraphs per chunk")
    
    # Grading options
    parser.add_argument("--max-span-chars", type=int, default=240, help="Maximum characters for evidence spans")
    
    args = parser.parse_args()
    
    # Create essay preprocessing options
    essay_options = PreprocessOptions(
        target_language=args.target_language,
        translate_non_english=not args.no_translate,
        redact_pii=not args.no_redact,
        chunk_max_paragraphs=args.chunk_size
    )
    
    # Initialize and run pipeline
    pipeline = RubriCheckPipeline(api_key_file=args.api_key_file)
    
    try:
        results = pipeline.run_complete_pipeline(
            rubric_path=args.rubric,
            essay_path=args.essay,
            output_path=args.output,
            essay_options=essay_options
        )
        
        # Print summary
        print("\n📊 GRADING SUMMARY")
        print("=" * 30)
        grading = results["grading_results"]
        print(f"Overall Score: {grading['numeric_score']} ({grading['letter_grade']})")
        print(f"Criteria Evaluated: {len(grading['per_criterion'])}")
        
        print("\n📝 CRITERION BREAKDOWN")
        print("-" * 30)
        for i, criterion in enumerate(grading['per_criterion'], 1):
            print(f"{i}. {criterion['criterion_id']}: {criterion['level']}")
            if criterion.get('justification'):
                print(f"   Justification: {criterion['justification'][:100]}...")
            if criterion.get('actionable_suggestion'):
                print(f"   Suggestion: {criterion['actionable_suggestion']}")
            print()
        
        if results.get('warnings'):
            print("⚠️  WARNINGS")
            print("-" * 20)
            for warning in results['warnings']:
                print(f"• {warning}")
        
    except Exception as e:
        print(f"❌ Pipeline execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
