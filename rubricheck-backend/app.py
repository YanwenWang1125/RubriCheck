#!/usr/bin/env python3
"""
RubriCheck Backend API Server
=============================
Flask API server that provides the /evaluate endpoint for the frontend.
Integrates with the existing RubriCheck pipeline modules.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import asdict

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import Flask and related modules
try:
    from flask import Flask, request, jsonify, Response
    from flask_cors import CORS
    from dotenv import load_dotenv
except ImportError:
    print("Flask not installed. Installing Flask and Flask-CORS...")
    os.system("pip install flask flask-cors python-dotenv")
    from flask import Flask, request, jsonify, Response
    from flask_cors import CORS
    from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Import RubriCheck modules
try:
    from essay_preprocessor import EssayPreprocessor, PreprocessOptions, ProcessedEssay
    from rubric_parser_prompt import parse_rubric_file, demo_parse_rubric
    from grading_engine import grade_essay, GradeSummary, generate_essay_insights
    print("All RubriCheck modules imported successfully!")
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all RubriCheck modules are in the same directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

class RubriCheckAPI:
    """API wrapper for RubriCheck pipeline."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the API with OpenAI API key."""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.warning("No OpenAI API key provided. Set OPENAI_API_KEY environment variable.")
        else:
            os.environ["OPENAI_API_KEY"] = self.api_key
            logger.info("OpenAI API key configured")
        
        # Initialize preprocessor
        self.preprocessor = EssayPreprocessor()
    
    def convert_frontend_rubric_to_backend(self, frontend_rubric: Dict[str, Any]) -> Dict[str, Any]:
        """Convert frontend rubric format to backend format."""
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
                "categorical_points_map": {}
            }
        }
        
        # Extract levels and create points mapping
        all_levels = set()
        for criterion in frontend_rubric.get('criteria', []):
            for level in criterion.get('levels', []):
                all_levels.add(level.get('name', ''))
        
        # Create points mapping (assuming 4-level scale)
        level_names = sorted(list(all_levels))
        if len(level_names) == 4:
            points_map = {level_names[0]: 4, level_names[1]: 3, level_names[2]: 2, level_names[3]: 1}
        else:
            # Default mapping
            points_map = {"Excellent": 4, "Good": 3, "Fair": 2, "Poor": 1}
        
        converted["grading"]["categorical_points_map"] = points_map
        
        # Convert criteria
        total_weight = sum(c.get('weight', 1.0) for c in frontend_rubric.get('criteria', []))
        
        for i, criterion in enumerate(frontend_rubric.get('criteria', [])):
            converted_criterion = {
                "id": criterion.get('id', f"criterion_{i}"),
                "name": criterion.get('name', f'Criterion {i+1}'),
                "descriptors": {},
                "valid_levels": [level.get('name', '') for level in criterion.get('levels', [])],
                "weight": (criterion.get('weight', 1.0) / total_weight) if total_weight > 0 else 1.0,
                "level_scale_note": " → ".join([level.get('name', '') for level in criterion.get('levels', [])])
            }
            
            # Convert levels to descriptors
            for level in criterion.get('levels', []):
                level_name = level.get('name', '')
                level_desc = level.get('description', '')
                converted_criterion["descriptors"][level_name] = level_desc
            
            converted["criteria"].append(converted_criterion)
        
        return converted
    
    def convert_backend_result_to_frontend(self, grade_summary: GradeSummary) -> Dict[str, Any]:
        """Convert backend grading result to frontend format."""
        frontend_result = {
            "overall": {
                "numeric": grade_summary.numeric_score,
                "letter": grade_summary.letter,
                "confidence": 0.85  # Default confidence
            },
            "items": [],
            "meta": {
                "categorical_points": grade_summary.categorical_points,
                "notes": grade_summary.notes
            }
        }
        
        # Convert per-criterion results
        for criterion_result in grade_summary.per_criterion:
            # Convert evidence spans format
            evidence_spans = []
            if criterion_result.evidence_spans:
                for span in criterion_result.evidence_spans:
                    evidence_spans.append({
                        "text": span.get("quote", ""),
                        "paraIndex": span.get("paragraph_index")
                    })
            
            frontend_item = {
                "criterionId": criterion_result.criterion_id,
                "level": criterion_result.level,
                "justification": criterion_result.justification or "",
                "evidenceSpans": evidence_spans,
                "suggestion": criterion_result.actionable_suggestion or "",
                "confidence": 0.8  # Default confidence
            }
            frontend_result["items"].append(frontend_item)
        
        return frontend_result
    
    def evaluate_essay(self, rubric: Dict[str, Any], essay_text: str, model: str = 'gpt-5-mini') -> Dict[str, Any]:
        """Evaluate an essay against a rubric."""
        try:
            logger.info("Starting essay evaluation...")
            
            # Step 1: Process essay
            logger.info("Processing essay...")
            options = PreprocessOptions(
                target_language="en",
                translate_non_english=True,
                redact_pii=True,
                chunk_max_paragraphs=6
            )
            processed_essay = self.preprocessor.run(essay_text, options)
            logger.info(f"Essay processed: {len(processed_essay.paragraphs)} paragraphs, {processed_essay.metadata.word_count} words")
            
            # Step 2: Convert rubric format
            logger.info("Converting rubric format...")
            backend_rubric = self.convert_frontend_rubric_to_backend(rubric)
            
            # Step 3: Grade essay
            logger.info(f"Grading essay with AI using model: {model}")
            grade_summary = grade_essay(backend_rubric, processed_essay, max_span_chars=240, model=model)
            logger.info(f"Grading complete: {grade_summary.numeric_score} ({grade_summary.letter})")
            
            # Step 4: Convert result to frontend format
            logger.info("Converting result to frontend format...")
            frontend_result = self.convert_backend_result_to_frontend(grade_summary)
            
            # Add essay insights
            essay_insights = generate_essay_insights(processed_essay)
            frontend_result["meta"]["essay_insights"] = essay_insights
            frontend_result["meta"]["essay_metadata"] = asdict(processed_essay.metadata)
            
            logger.info("Essay evaluation completed successfully")
            return frontend_result
            
        except Exception as e:
            logger.error(f"Error during essay evaluation: {e}")
            raise

# Initialize API
api_handler = RubriCheckAPI()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "message": "RubriCheck API is running",
        "version": "1.0.0"
    })

@app.route('/evaluate', methods=['POST'])
def evaluate():
    """Main evaluation endpoint."""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        rubric = data.get('rubric')
        essay_text = data.get('essayText')
        model = data.get('model', 'gpt-5-mini')  # Default to gpt-5-mini
        
        if not rubric:
            return jsonify({"error": "No rubric provided"}), 400
        
        if not essay_text:
            return jsonify({"error": "No essay text provided"}), 400
        
        logger.info(f"Received evaluation request: rubric '{rubric.get('title', 'Unknown')}', essay length: {len(essay_text)} chars, model: {model}")
        
        # Evaluate essay
        result = api_handler.evaluate_essay(rubric, essay_text, model)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in /evaluate endpoint: {e}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/rubric/parse', methods=['POST'])
def parse_rubric():
    """Parse rubric from uploaded file."""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ['.json', '.docx', '.txt']:
            return jsonify({"error": f"Unsupported file type: {file_ext}. Supported: .json, .docx, .txt"}), 400
        
        # Save uploaded file temporarily with proper extension
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Parse rubric
            rubric = demo_parse_rubric(temp_path)
            if not rubric:
                return jsonify({"error": "Failed to parse rubric. Please check the file format and content."}), 400
            
            # Convert to frontend format
            frontend_rubric = {
                "id": rubric.get('id', 'parsed_rubric'),
                "title": rubric.get('title', 'Parsed Rubric'),
                "criteria": []
            }
            
            for i, criterion in enumerate(rubric.get('criteria', [])):
                frontend_criterion = {
                    "id": f"criterion_{i}",
                    "name": criterion.get('name', f'Criterion {i+1}'),
                    "weight": criterion.get('weight', 1.0),
                    "levels": []
                }
                
                # Convert levels
                for level_name, description in criterion.get('descriptor_by_level', {}).items():
                    frontend_criterion["levels"].append({
                        "name": level_name,
                        "description": description
                    })
                
                frontend_rubric["criteria"].append(frontend_criterion)
            
            return jsonify(frontend_rubric)
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
    except Exception as e:
        logger.error(f"Error in /rubric/parse endpoint: {e}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Get configuration from environment
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 8000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting RubriCheck API server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug)
