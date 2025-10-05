#!/usr/bin/env python3
"""
RubriCheck Rubric Parser
========================
A comprehensive class for parsing rubric documents from supported formats
(DOCX, TXT) into structured JSON format using OpenAI's LLM.

Features:
- Multi-format support (DOCX, TXT)
- JSON Schema validation
- Structured OpenAI API integration
- Error handling and confidence scoring

Note: PDF and image processing removed to avoid fitz import conflicts.
For full functionality, use the notebook version with proper dependencies.

Author: RubriCheck
"""

import os
import io
import re
import json
import tempfile
import mimetypes
import math
from typing import Tuple, Dict, Any, Optional, List
from dataclasses import dataclass, field

# --- File extraction deps
# Note: PDF processing removed to avoid fitz import conflicts
# from pdf2image import convert_from_path
# import pytesseract
# import cv2
# import numpy as np
# from PIL import Image
import docx2txt

# --- OpenAI (Responses API with Structured Outputs)
from openai import OpenAI

# --- Validation
from jsonschema import Draft7Validator


@dataclass
class ParseResult:
    """Result of rubric parsing operation."""
    success: bool
    rubric: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    method: str = "unknown"
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "success": self.success,
            "rubric": self.rubric,
            "confidence": self.confidence,
            "method": self.method,
            "warnings": self.warnings,
            "errors": self.errors
        }


class RubricParser:
    """
    A comprehensive rubric parser that can handle supported file formats
    (DOCX, TXT) and extract structured rubric data using OpenAI's LLM.
    
    Note: PDF and image processing removed to avoid fitz import conflicts.
    """
    
    # JSON Schema for rubric validation
    RUBRIC_JSON_SCHEMA: Dict[str, Any] = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "RubricSchema",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "title": {"type": ["string", "null"], "maxLength": 200},
            "scale": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "type": {"type": "string", "enum": ["categorical", "numeric"]},
                    "levels": {
                        "type": ["array", "null"],
                        "items": {"type": "string", "minLength": 1},
                        "minItems": 1
                    },
                    "min": {"type": ["number", "null"]},
                    "max": {"type": ["number", "null"]},
                    "original_levels": {
                        "type": ["array", "null"],
                        "items": {"type": "string"}
                    },
                    "synonyms": {
                        "type": ["object", "null"],
                        "additionalProperties": {"type": "string"}
                    }
                },
                "required": ["type"]
            },
            "criteria": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "name": {"type": "string", "minLength": 1, "maxLength": 120},
                        "descriptor_by_level": {
                            "type": "object",
                            "additionalProperties": {"type": "string"}
                        },
                        "weight": {"type": "number", "exclusiveMinimum": 0},
                        "evidence_hint": {"type": ["string", "null"]},
                        "notes": {"type": ["string", "null"]}
                    },
                    "required": ["name", "descriptor_by_level"]
                }
            },
            "notes": {"type": ["string", "null"]},
            "source_parse": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "method": {"type": "string", "enum": ["table", "narrative", "hybrid", "ocr"]},
                    "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "warnings": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": []
                    }
                },
                "required": ["method", "confidence"]
            }
        },
        "required": ["scale", "criteria", "source_parse"]
    }
    
    # Supported file extensions (image processing removed)
    # IMG_EXT = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp"}  # Removed due to fitz conflicts
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize the RubricParser.
        
        Args:
            api_key: OpenAI API key (if None, will read from file)
            model: OpenAI model to use for parsing
        """
        self.model = model
        self.validator = Draft7Validator(self.RUBRIC_JSON_SCHEMA)
        
        # Use shared OpenAI client
        self.client = get_openai_client(api_key)
    
    # PDF and image processing methods removed to avoid fitz import conflicts
    
    def _extract_from_pdf(self, path: str) -> Tuple[str, str]:
        """PDF processing not available - fitz import conflicts removed."""
        print("⚠️  PDF processing not available - fitz import conflicts removed")
        return "", "error"
    
    def _extract_from_image(self, path: str) -> Tuple[str, str]:
        """Image processing not available - fitz import conflicts removed."""
        print("⚠️  Image processing not available - fitz import conflicts removed")
        return "", "error"
    
    def _extract_from_docx(self, path: str) -> Tuple[str, str]:
        """Extract text from DOCX file."""
        return docx2txt.process(path) or "", "narrative"
    
    def _extract_from_txt(self, path: str) -> Tuple[str, str]:
        """Extract text from TXT file."""
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(), "narrative"
    
    def extract_text_from_file(self, path: str) -> Tuple[str, str]:
        """
        Extract text from supported file formats (TXT, DOCX only).
        PDF and image processing removed to avoid fitz import conflicts.
        
        Args:
            path: Path to the file
            
        Returns:
            Tuple of (extracted_text, method_used)
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        
        ext = os.path.splitext(path)[1].lower()
        if ext == ".pdf":
            print("⚠️  PDF processing not available - fitz import conflicts removed")
            return "", "error"
        elif ext == ".docx":
            return self._extract_from_docx(path)
        elif ext in {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp"}:
            print("⚠️  Image processing not available - fitz import conflicts removed")
            return "", "error"
        else:
            return self._extract_from_txt(path)
    
    def _parse_rubric_with_llm(self, raw_text: str, method_hint: str = "narrative") -> Dict[str, Any]:
        """Parse rubric using OpenAI LLM with structured outputs."""
        # Build the system message with schema instructions
        system_message = (
            "You are a precise rubric parser. Convert the given rubric into strictly valid JSON that "
            "conforms to the provided JSON Schema. Do not fabricate content. If information is missing, "
            "omit it and write a warning. Preserve original level wording in descriptors; normalize level names.\n\n"
            "IMPORTANT: You must respond with valid JSON only. No additional text or explanations."
        )
        
        user_message = (
            "RAW_RUBRIC_TEXT:\n```\n" + raw_text.strip() + "\n```\n\n"
            "Instructions:\n"
            f"- The extraction method was '{method_hint}'. Set source_parse.method accordingly.\n"
            "- If levels like Excellent/Good/Fair/Poor are present, use them as categorical scale levels in best→worst order.\n"
            "- If a numeric points scale is present (e.g., 0–4), include scale.min/scale.max and set type='numeric'.\n"
            "- Parse weights when explicitly indicated (e.g., 'Clarity (30%)' → weight=0.30); otherwise default to 1.0.\n"
            "- If any descriptor is missing for a level, omit that key and add a warning.\n"
            "- If multiple rubrics are present, parse the first major rubric and add a warning.\n"
            "- Output only the JSON. No extra text.\n\n"
            "Required JSON structure:\n"
            "{\n"
            '  "title": "string or null",\n'
            '  "scale": {\n'
            '    "type": "categorical or numeric",\n'
            '    "levels": ["array of strings for categorical"],\n'
            '    "min": "number for numeric",\n'
            '    "max": "number for numeric"\n'
            '  },\n'
            '  "criteria": [\n'
            '    {\n'
            '      "name": "string",\n'
            '      "descriptor_by_level": {"level": "description"},\n'
            '      "weight": "number"\n'
            '    }\n'
            '  ],\n'
            '  "source_parse": {\n'
            '    "method": "table/narrative/hybrid/ocr",\n'
            '    "confidence": "number 0.0-1.0",\n'
            '    "warnings": ["array of strings"]\n'
            '  }\n'
            "}"
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"},
                max_tokens=2048,
                temperature=0.1
            )
            
            # Extract the JSON response
            json_text = response.choices[0].message.content
            parsed = json.loads(json_text)
            
            return parsed
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}")
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")
    
    def _validate_rubric(self, rubric: Dict[str, Any]) -> List[str]:
        """Validate rubric against JSON schema and perform semantic checks."""
        errors = []
        
        # JSON Schema validation
        for err in sorted(self.validator.iter_errors(rubric), key=lambda e: e.path):
            loc = "/".join([str(x) for x in err.path])
            errors.append(f"{loc}: {err.message}")
        
        # Additional semantic checks
        try:
            # 1) categorical: descriptor keys ⊆ levels
            if rubric["scale"]["type"] == "categorical":
                levels = set(rubric["scale"].get("levels") or [])
                for i, c in enumerate(rubric["criteria"]):
                    bad = [k for k in c["descriptor_by_level"].keys() if k not in levels]
                    if bad:
                        errors.append(f"criteria[{i}].descriptor_by_level has keys not in scale.levels: {bad}")
        except KeyError:
            pass
        
        # 2) numeric: min < max
        try:
            if rubric["scale"]["type"] == "numeric":
                mn = rubric["scale"].get("min")
                mx = rubric["scale"].get("max")
                if isinstance(mn, (int, float)) and isinstance(mx, (int, float)) and not (mn < mx):
                    errors.append("scale.min must be < scale.max")
        except KeyError:
            pass
        
        # 3) unique criterion names (case-insensitive)
        names = [c["name"].strip().lower() for c in rubric.get("criteria", [])]
        if len(set(names)) != len(names):
            errors.append("criteria names must be unique (case-insensitive)")
        
        return errors
    
    def parse_file(self, path: str) -> ParseResult:
        """
        Parse a rubric file and return structured result.
        
        Args:
            path: Path to the rubric file
            
        Returns:
            ParseResult object with success status and parsed data
        """
        try:
            # Extract text from file
            raw_text, method = self.extract_text_from_file(path)
            
            if not raw_text or len(raw_text.strip()) < 30:
                return ParseResult(
                    success=False,
                    errors=[f"Could not extract enough text from {path}"]
                )
            
            # Parse with LLM
            rubric = self._parse_rubric_with_llm(raw_text, method)
            
            # Validate the result
            validation_errors = self._validate_rubric(rubric)
            
            # Extract confidence and warnings from the parsed rubric
            source_parse = rubric.get("source_parse", {})
            confidence = source_parse.get("confidence", 0.5)
            warnings = source_parse.get("warnings", [])
            
            # Add validation errors as warnings
            if validation_errors:
                warnings.extend([f"validation: {e}" for e in validation_errors])
            
            # Update the rubric with validation warnings
            rubric.setdefault("source_parse", {})
            rubric["source_parse"]["warnings"] = warnings
            
            return ParseResult(
                success=True,
                rubric=rubric,
                confidence=confidence,
                method=method,
                warnings=warnings
            )
            
        except Exception as e:
            return ParseResult(
                success=False,
                errors=[f"Parsing failed: {str(e)}"]
            )
    
    def parse_text(self, text: str, method_hint: str = "narrative") -> ParseResult:
        """
        Parse rubric from raw text.
        
        Args:
            text: Raw rubric text
            method_hint: Hint about the text format
            
        Returns:
            ParseResult object with success status and parsed data
        """
        try:
            if not text or len(text.strip()) < 30:
                return ParseResult(
                    success=False,
                    errors=["Text is too short for parsing"]
                )
            
            # Parse with LLM
            rubric = self._parse_rubric_with_llm(text, method_hint)
            
            # Validate the result
            validation_errors = self._validate_rubric(rubric)
            
            # Extract confidence and warnings from the parsed rubric
            source_parse = rubric.get("source_parse", {})
            confidence = source_parse.get("confidence", 0.5)
            warnings = source_parse.get("warnings", [])
            
            # Add validation errors as warnings
            if validation_errors:
                warnings.extend([f"validation: {e}" for e in validation_errors])
            
            # Update the rubric with validation warnings
            rubric.setdefault("source_parse", {})
            rubric["source_parse"]["warnings"] = warnings
            
            return ParseResult(
                success=True,
                rubric=rubric,
                confidence=confidence,
                method=method_hint,
                warnings=warnings
            )
            
        except Exception as e:
            return ParseResult(
                success=False,
                errors=[f"Parsing failed: {str(e)}"]
            )
    
    def print_summary(self, result: ParseResult) -> None:
        """Print a formatted summary of the parsing result."""
        if not result.success:
            print("❌ Parsing failed!")
            for error in result.errors:
                print(f"  • {error}")
            return
        
        rubric = result.rubric
        print("=" * 50)
        print(f"📋 RUBRIC: {rubric.get('title', 'Untitled')}")
        print("=" * 50)
        
        # Scale info
        scale = rubric.get('scale', {})
        print(f"📏 Scale Type: {scale.get('type', 'unknown')}")
        if scale.get('type') == 'categorical':
            levels = scale.get('levels', [])
            print(f"📊 Levels: {' → '.join(levels) if levels else 'None'}")
        elif scale.get('type') == 'numeric':
            min_val = scale.get('min')
            max_val = scale.get('max')
            print(f"📊 Range: {min_val} - {max_val}")
        
        # Criteria
        criteria = rubric.get('criteria', [])
        print(f"\n📝 Criteria ({len(criteria)}):")
        for i, criterion in enumerate(criteria, 1):
            name = criterion.get('name', 'Unnamed')
            weight = criterion.get('weight', 1.0)
            print(f"  {i}. {name} (weight: {weight})")
        
        # Confidence and method
        print(f"\n🎯 Confidence: {result.confidence:.2f}" if result.confidence is not None else "\n🎯 Confidence: N/A")
        print(f"🔧 Method: {result.method}")
        
        # Warnings
        if result.warnings:
            print(f"\n⚠️  Warnings ({len(result.warnings)}):")
            for warning in result.warnings:
                print(f"  • {warning}")
        
        print("=" * 50)
    
    def get_criteria_count(self, result: ParseResult) -> int:
        """Get the number of criteria in the parsed rubric."""
        if not result.success:
            return 0
        return len(result.rubric.get('criteria', []))
    
    def get_scale_type(self, result: ParseResult) -> str:
        """Get the scale type of the parsed rubric."""
        if not result.success:
            return "unknown"
        return result.rubric.get('scale', {}).get('type', 'unknown')
    
    def get_confidence(self, result: ParseResult) -> float:
        """Get the confidence score of the parsing result."""
        return result.confidence
    
    def is_successful(self, result: ParseResult) -> bool:
        """Check if parsing was successful."""
        return result.success


# Convenience functions for backward compatibility
def parse_rubric_file(path: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
    """Parse a rubric file and return the rubric dictionary."""
    parser = RubricParser(model=model)
    result = parser.parse_file(path)
    
    if result.success:
        return result.rubric
    else:
        raise ValueError(f"Failed to parse rubric: {', '.join(result.errors)}")


def demo_parse_rubric(file_path: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
    """Demo function to parse a rubric file with console output."""
    parser = RubricParser(model=model)
    result = parser.parse_file(file_path)
    
    if result.success:
        print("✅ Rubric parsed successfully!")
        print(f"📊 Found {parser.get_criteria_count(result)} criteria")
        print(f"📏 Scale type: {parser.get_scale_type(result)}")
        parser.print_summary(result)
        return result.rubric
    else:
        print(f"❌ Error parsing rubric: {', '.join(result.errors)}")
        return {}


# Import shared utilities
from utils import get_api_key_from_file, get_openai_client

def run_parser_example():
    """Main function to parse a rubric file."""
    # Manual configuration - modify these values as needed
    file_path = "test_file/test_rubric.docx"  # Path to your rubric file
    model = "gpt-4o-mini"  # OpenAI model to use
    api_key = None  # Set to None to use environment variable, or provide your API key
    
    try:
        # Get API key from file if not provided
        if api_key is None:
            api_key = get_api_key_from_file()
        
        # Initialize parser
        rubric_parser = RubricParser(api_key=api_key, model=model)
        
        # Parse the file
        print(f"🔍 Parsing rubric file: {file_path}")
        result = rubric_parser.parse_file(file_path)
        
        if result.success:
            print("✅ Rubric parsed successfully!")
            print("📄 JSON Output:")
            print("=" * 50)
            print(json.dumps(result.rubric, indent=2, ensure_ascii=False))
            print("=" * 50)
        else:
            print(f"❌ Error parsing rubric: {', '.join(result.errors)}")
            return 1
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    return 0

def run_example():
    """Jupyter-safe function to run the example without CLI interference."""
    return run_parser_example()

# if __name__ == "__main__":
#    main()
