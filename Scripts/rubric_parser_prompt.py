import os, io, re, json, tempfile, mimetypes, math
from typing import Tuple, Dict, Any, Optional, List

# --- File extraction deps
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract
import cv2
import numpy as np
from PIL import Image
import docx2txt

# --- OpenAI (Responses API with Structured Outputs)
from openai import OpenAI

# --- Validation
from jsonschema import Draft7Validator

# Read API key from api.txt file
def get_api_key_from_file(file_path: str = r"C:\Users\Leo\AI projects\_api.txt", keyname: str = "RubricParserPrompt") -> str:
    """Read API key from api.txt file for rubriCheck project."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith(f'{keyname}:'):
                    return line.strip().split(':', 1)[1].strip()
        raise ValueError("rubriCheck API key not found in file")
    except FileNotFoundError:
        raise FileNotFoundError(f"API file not found at {file_path}")

# Set the API key from file
api_file = r"C:\Users\Leo\AI projects\_api.txt"
keyname = "RubricParserPrompt"
api_key = get_api_key_from_file()
os.environ["OPENAI_API_KEY"] = api_key

# Verify the API key is set
try:
    api_key = os.environ["OPENAI_API_KEY"]
    if api_key == "your-api-key-here":
        print("⚠️  Please replace 'your-api-key-here' with your actual OpenAI API key!")
    else:
        print("✅ API key is set and ready to use!")
        print(f"🔑 Key starts with: {api_key[:8]}...")
except KeyError:
    print("❌ API key not found in environment variables")

# =========================
# JSON SCHEMA (Structured)
# =========================

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

# Pre-compile validator for speed
RUBRIC_VALIDATOR = Draft7Validator(RUBRIC_JSON_SCHEMA)

# =========================
# File → text extraction
# =========================

IMG_EXT = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp"}

def _deskew_and_binarize(pil_img: Image.Image) -> Image.Image:
    """Basic deskew + binarization to improve OCR."""
    img = np.array(pil_img.convert("L"))  # grayscale
    # threshold
    _, th = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # deskew
    coords = np.column_stack(np.where(th == 0))
    angle = 0.0
    if coords.size > 0:
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
    (h, w) = th.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    rotated = cv2.warpAffine(th, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return Image.fromarray(rotated)

def _ocr_pil_image(pil_img: Image.Image, lang: str = "eng") -> str:
    proc = _deskew_and_binarize(pil_img)
    return pytesseract.image_to_string(proc, lang=lang)

def _extract_from_pdf(path: str) -> Tuple[str, str]:
    """Return (text, method). Try native text first; fallback to OCR if text looks empty."""
    doc = fitz.open(path)
    texts = []
    for p in doc:
        txt = p.get_text("text")
        if txt:
            texts.append(txt)
    native_text = "\n".join(texts).strip()
    if len(native_text) >= 400 or (len(native_text) > 40 and len(texts) >= 1):
        return native_text, "table" if " | " in native_text or re.search(r"\bPoints?\b", native_text, re.I) else "narrative"

    # Fallback to OCR
    pages = convert_from_path(path, dpi=300)
    ocr_texts = []
    for pil in pages:
        ocr_texts.append(_ocr_pil_image(pil))
    return "\n".join(ocr_texts).strip(), "ocr"

def _extract_from_image(path: str) -> Tuple[str, str]:
    pil = Image.open(path)
    return _ocr_pil_image(pil), "ocr"

def _extract_from_docx(path: str) -> Tuple[str, str]:
    return docx2txt.process(path) or "", "narrative"

def _extract_from_txt(path: str) -> Tuple[str, str]:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read(), "narrative"

def extract_text_from_file(path: str) -> Tuple[str, str]:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return _extract_from_pdf(path)
    if ext == ".docx":
        return _extract_from_docx(path)
    if ext in IMG_EXT:
        return _extract_from_image(path)
    return _extract_from_txt(path)

# =========================
# OpenAI call (Structured Outputs)
# =========================

def _openai_client() -> OpenAI:
    return OpenAI()  # reads OPENAI_API_KEY

def parse_rubric_with_llm(raw_text: str, method_hint: str = "narrative", model: str = "gpt-4o-mini") -> Dict[str, Any]:
    """
    Calls the OpenAI Chat Completions API with JSON mode to get a strictly valid rubric JSON.
    """
    client = _openai_client()

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
        response = client.chat.completions.create(
            model=model,
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
        print(f"❌ Failed to parse JSON response: {e}")
        print(f"Raw response: {json_text}")
        raise
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        raise

# =========================
# Validation & post-checks
# =========================

def validate_rubric(rubric: Dict[str, Any]) -> List[str]:
    errors = []
    for err in sorted(RUBRIC_VALIDATOR.iter_errors(rubric), key=lambda e: e.path):
        loc = "/".join([str(x) for x in err.path])
        errors.append(f"{loc}: {err.message}")
    # Additional semantic checks:
    # 1) categorical: descriptor keys ⊆ levels
    try:
        if rubric["scale"]["type"] == "categorical":
            levels = set(rubric["scale"].get("levels") or [])
            for i, c in enumerate(rubric["criteria"]):
                bad = [k for k in c["descriptor_by_level"].keys() if k not in levels]
                if bad:
                    errors.append(f"criteria[{i}].descriptor_by_level has keys not in scale.levels: {bad}")
    except KeyError:
        pass
    # 2) numeric: min < max (jsonschema also checks types)
    if rubric["scale"]["type"] == "numeric":
        mn = rubric["scale"].get("min"); mx = rubric["scale"].get("max")
        if isinstance(mn, (int,float)) and isinstance(mx, (int,float)) and not (mn < mx):
            errors.append("scale.min must be < scale.max")
    # 3) unique criterion names (case-insensitive)
    names = [c["name"].strip().lower() for c in rubric.get("criteria", [])]
    if len(set(names)) != len(names):
        errors.append("criteria names must be unique (case-insensitive)")
    return errors

# =========================
# Public entry point
# =========================

def parse_rubric_file(path: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
    raw_text, parse_hint_method = extract_text_from_file(path)
    if not raw_text or len(raw_text.strip()) < 30:
        raise ValueError("Could not extract enough text from the file for parsing.")

    rubric = parse_rubric_with_llm(raw_text, parse_hint_method, model=model)
    problems = validate_rubric(rubric)
    if problems:
        # attach validator findings as warnings
        rubric.setdefault("source_parse", {}).setdefault("warnings", [])
        rubric["source_parse"]["warnings"].extend([f"validation: {p}" for p in problems])
    return rubric

# =========================
# Demo and testing functions
# =========================

def demo_parse_rubric(file_path: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
    """
    Demo function to parse a rubric file and return the result.
    Use this in Jupyter notebooks instead of command line execution.
    """
    try:
        result = parse_rubric_file(file_path, model=model)
        print("✅ Rubric parsed successfully!")
        print(f"📊 Found {len(result.get('criteria', []))} criteria")
        print(f"📏 Scale type: {result.get('scale', {}).get('type', 'unknown')}")
        return result
    except Exception as e:
        print(f"❌ Error parsing rubric: {e}")
        return {}

def print_rubric_summary(rubric: Dict[str, Any]):
    """Print a formatted summary of the parsed rubric."""
    if not rubric:
        print("No rubric data to display")
        return
    
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
    
    # Warnings
    warnings = rubric.get('source_parse', {}).get('warnings', [])
    if warnings:
        print(f"\n⚠️  Warnings ({len(warnings)}):")
        for warning in warnings:
            print(f"  • {warning}")
    
    print("=" * 50)

# CLI functionality (only runs when script is executed directly, not in notebook)
if __name__ == "__main__" and not hasattr(__builtins__, '__IPYTHON__'):
    import argparse, pprint
    ap = argparse.ArgumentParser(description="Parse a rubric file into canonical JSON.")
    ap.add_argument("file", help="Path to rubric: .txt .docx .pdf .png .jpg")
    ap.add_argument("--model", default="gpt-4.1-mini", help="OpenAI model (supports Structured Outputs).")
    args = ap.parse_args()

    result = parse_rubric_file(args.file, model=args.model)
    print(json.dumps(result, indent=2, ensure_ascii=False))
