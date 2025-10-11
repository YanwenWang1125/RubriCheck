from __future__ import annotations
import os
import math
import statistics
import json
import re
from typing import Dict, List, Any, Optional, Tuple, Literal
from dataclasses import dataclass, field

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, skip loading .env file
    pass

# --------- OpenAI client ----------
# pip install openai>=1.0.0
from openai import OpenAI

# --------- Import essay preprocessor types ----------
try:
    from essay_preprocessor import ProcessedEssay, Paragraph, Metadata
except ImportError:
    # Fallback for when essay_preprocessor is not available
    ProcessedEssay = Any
    Paragraph = Any
    Metadata = Any

# --------- Import rubric parser ----------
try:
    from rubric_parser_prompt import RubricParser, ParseResult
except ImportError:
    # Fallback for when rubric parser is not available
    RubricParser = Any
    ParseResult = Any
OPENAI_MODEL = os.environ.get("RUBRICHECK_MODEL", "gpt-5")

# Import shared utilities
from utils import get_api_key_from_env, get_openai_client

# Import optimization modules
try:
    from optimization_config import get_optimization_config
    from cache_manager import get_cache_manager
    OPTIMIZATION_AVAILABLE = True
except ImportError:
    OPTIMIZATION_AVAILABLE = False
    print("⚠️  Optimization modules not available - using default settings")

# ===============================
# Data structures (expected inputs)
# ===============================

# Expected rubric structure (already parsed/normalized by your parser):
# {
#   "criteria": [
#     {
#       "id": "thesis",
#       "name": "Thesis & Focus",
#       "descriptors": {
#         "Excellent": "Clear, arguable thesis driving the essay...",
#         "Good": "Thesis present but may be somewhat broad...",
#         "Fair": "Thesis is unclear or only implied...",
#         "Poor": "No discernible thesis..."
#       },
#       "valid_levels": ["Excellent","Good","Fair","Poor"],
#       "weight": 0.25,  # optional; default = equal weights if missing
#       "level_scale_note": "Excellent > Good > Fair > Poor"
#     },
#     ...
#   ],
#   "grading": {
#       "numeric": True,                  # if True, weights are numeric; compute weighted avg
#       "letter_bands": [                 # optional; maps numeric to letters
#          {"min": 90, "max": 100, "letter": "A+"},
#          {"min": 85, "max": 89.99, "letter": "A"},
#          ...
#       ],
#       # If numeric=False or missing, we treat as categorical-only and map level->points:
#       "categorical_points_map": {"Excellent": 4, "Good": 3, "Fair": 2, "Poor": 1}
#   }
# }

# Expected input: ProcessedEssay from essay_preprocessor
# Contains rich metadata: paragraphs, sections, quotes, readability, language, etc.

# ===============================
# Prompt templates
# ===============================

SYSTEM_BASE = """You are RubriCheck, an AI grader that provides RICH, DETAILED analysis with comprehensive evidence spans. 
Rules:
- Only quote text present in the essay. Do not fabricate citations.
- For evidence, find MULTIPLE relevant excerpts (<= {max_span_chars} characters per excerpt) and include paragraph indices.
- Provide 2-4 evidence spans per criterion when possible, including both positive and negative evidence.
- Use complete sentences or meaningful phrases for evidence, not single words or fragments.
- Include context around key points to make evidence more meaningful.
- If the rubric content for this criterion is ambiguous or self-contradictory, REFUSE with {{"refuse": true, "reason": "..."}} using the exact JSON schema.
- Provide detailed, specific justifications that reference the evidence spans.
- Give concrete, actionable suggestions that directly address the evidence found.
- Output MUST be valid JSON with the exact keys specified—no extra keys, no prose outside JSON.
"""

# Strict JSON schema instructions (enforced by instruction + examples).
# We keep keys stable and visible in the user prompt.
CRITERION_OUTPUT_KEYS = [
    "criterion_id", "valid_levels", "level", "justification", "evidence_spans",
    "actionable_suggestion", "refuse", "reason"
]

def make_criterion_user_prompt(
    criterion: Dict[str, Any],
    processed_essay: ProcessedEssay,
    max_span_chars: int = 240
) -> str:
    # Extract paragraphs with rich metadata
    essay_paragraphs = [p.text for p in processed_essay.paragraphs if p.text.strip()]
    essay_block = "\n".join([f"[{i}] {p}" for i, p in enumerate(essay_paragraphs)])
    valid_levels_list = criterion["valid_levels"]
    descriptors = criterion["descriptors"]

    # Include essay metadata for better context
    metadata = processed_essay.metadata
    essay_context = f"""
ESSAY METADATA
- Word count: {metadata.word_count}
- Language: {metadata.language_detected}
- Readability: {metadata.readability.flesch_reading_ease:.1f} (Flesch Reading Ease)
- Quote ratio: {metadata.quote_char_ratio:.1%}
- Sections: {len(metadata.sections)}
"""

    return f"""
You will grade ONE criterion only.

CRITERION
- criterion_id: {criterion.get('id')}
- name: {criterion.get('name')}
- valid_levels (choose EXACTLY one): {valid_levels_list}
- level scale note: {criterion.get('level_scale_note', '')}

DESCRIPTORS (for this criterion only)
{descriptors}

{essay_context}

ESSAY (paragraph-indexed)
{essay_block}

REQUIREMENTS
1) Return STRICT JSON with EXACTLY these keys (no others):
{CRITERION_OUTPUT_KEYS}
2) "valid_levels": repeat a short list (the same list above) for transparency.
3) "level": MUST be one of valid_levels. If unsure/ambiguous, set "refuse"=true and fill "reason".
4) "justification": 1–3 sentences explaining why chosen level matches the descriptor.
5) "evidence_spans": array of objects, each with:
   - "paragraph_index" (integer)
   - "quote" (string, <= {max_span_chars} chars, must appear verbatim in that paragraph)
6) "actionable_suggestion": one concrete, specific improvement step for this criterion.
7) Safety: Never invent content; only quote from the essay paragraphs provided.
8) Consider essay metadata (word count, readability, language) in your evaluation.

Return ONLY the JSON object—no commentary.
"""

# Second pass self-check prompt (reads model's chosen level & justification)
def make_consistency_prompt(chosen: Dict[str, Any], criterion: Dict[str, Any]) -> str:
    return f"""
You are verifying rubric consistency for ONE criterion.

CRITERION DESCRIPTORS
{criterion["descriptors"]}

MODEL CHOICE
- level: {chosen.get("level")}
- justification: {chosen.get("justification")}
- evidence_spans: {chosen.get("evidence_spans")}

TASK
Explain why (or why not) the chosen level matches the descriptor language. 
If you find contradiction or weak alignment, say "low_confidence": true and explain briefly; else "low_confidence": false. 
Output JSON ONLY with keys: ["low_confidence", "explanation"].
"""

# Slightly perturbed prompts for agreement check
def make_agreement_variant_prompt(base_prompt: str, variant_tag: str) -> str:
    # Minimal perturbations: reorder rules, add harmless synonym, etc.
    return base_prompt + f"\n# variant_tag: {variant_tag}\n" \
                         f"Note: Verify factual quotes strictly; do not exceed span length.\n"

# ===============================
# Core LLM helpers
# ===============================

def llm_json(prompt: str, system: str, model: str = None) -> Dict[str, Any]:
    """
    Calls the OpenAI chat completion and attempts to parse JSON only.
    We ask the model to output ONLY JSON. If it fails, we rethrow with the raw text.
    """
    # Get optimization config
    config = get_optimization_config() if OPTIMIZATION_AVAILABLE else None
    
    model_to_use = model or (config.preferred_model if config else OPENAI_MODEL)
    temperature = config.temperature if config else 1.0
    max_tokens = config.max_tokens_per_request if config else None
    
    # Prepare request parameters
    request_params = {
        "model": model_to_use,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
    }
    
    # Add max_tokens if configured
    if max_tokens:
        request_params["max_tokens"] = max_tokens
    
    resp = get_openai_client().chat.completions.create(**request_params)
    txt = resp.choices[0].message.content.strip()
    # Simple JSON guard:
    # Extract first JSON object found:
    # Find the first { and try to parse from there
    start_idx = txt.find('{')
    if start_idx == -1:
        raise ValueError(f"Expected JSON but got:\n{txt}")
    
    # Try to parse JSON starting from the first {
    try:
        return json.loads(txt[start_idx:])
    except json.JSONDecodeError:
        # If that fails, try to find the end of the JSON object
        brace_count = 0
        end_idx = start_idx
        for i, char in enumerate(txt[start_idx:], start_idx):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i + 1
                    break
        
        try:
            return json.loads(txt[start_idx:end_idx])
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON returned:\n{txt}") from e

# ===============================
# Scoring + Aggregation
# ===============================

@dataclass
class CriterionResult:
    criterion_id: str
    valid_levels: List[str]
    level: Optional[str]
    justification: Optional[str]
    evidence_spans: List[Dict[str, Any]]
    actionable_suggestion: Optional[str]
    refuse: bool
    reason: Optional[str]
    low_confidence: bool = False
    consistency_explanation: Optional[str] = None
    agreement_flag: Literal["ok","needs_review","tie_break"] = "ok"
    tie_break_used: bool = False

@dataclass
class GradeSummary:
    per_criterion: List[CriterionResult] = field(default_factory=list)
    numeric_score: Optional[float] = None
    letter: Optional[str] = None
    categorical_points: Optional[float] = None
    notes: Dict[str, Any] = field(default_factory=dict)

def tie_break_choice(a: str, b: str, valid_levels: List[str]) -> str:
    # Prefer the higher of the two by scale order (left->right descending quality).
    # Assuming valid_levels is ordered from best to worst (as provided).
    # If order unknown, we keep 'a' by default.
    try:
        ia = valid_levels.index(a)
        ib = valid_levels.index(b)
        return a if ia < ib else b
    except:
        return a

def map_levels_to_points(levels: Dict[str, int], chosen_level: str) -> Optional[int]:
    return levels.get(chosen_level)

def compute_weighted_numeric(per: List[CriterionResult], rubric: Dict[str, Any]) -> Tuple[Optional[float], Optional[str]]:
    # Weighted mean of mapped numeric points if 'numeric' grading is configured.
    if not rubric.get("grading", {}).get("numeric", False):
        return None, None

    # If descriptors embed numeric thresholds, you'd parse them upstream.
    # Here, we map text levels onto provisional numeric anchors (Excellent=100, Good=85, Fair=70, Poor=55) as a fallback.
    fallback_map = {"Excellent": 100, "Good": 85, "Fair": 70, "Poor": 55}
    crits = rubric["criteria"]
    weights = []
    scores = []
    for c in per:
        crit_meta = next((x for x in crits if x["id"] == c.criterion_id), None)
        w = crit_meta.get("weight", None) if crit_meta else None
        if w is None:
            # equal weights later if any are missing
            pass
        weights.append(w)

    # Normalize weights: if any missing, treat all as equal
    if any(w is None for w in weights):
        weights = [1.0 for _ in per]
    total_w = sum(weights) or 1.0

    numeric_scores = []
    for c, w in zip(per, weights):
        if c.level is None:
            continue
        s = fallback_map.get(c.level)
        if s is not None:
            numeric_scores.append((s, w))

    if not numeric_scores:
        return None, None

    weighted = sum(s * w for s, w in numeric_scores) / total_w
    # Letter band mapping if provided
    letter = None
    bands = rubric.get("grading", {}).get("letter_bands", [])
    for band in bands:
        if band["min"] <= weighted <= band["max"]:
            letter = band["letter"]
            break
    return weighted, letter

def compute_categorical_aggregate(per: List[CriterionResult], rubric: Dict[str, Any]) -> Optional[float]:
    # Map levels->points then average (unweighted) unless you want weighted here as well.
    cmap = rubric.get("grading", {}).get("categorical_points_map", {"Excellent":4,"Good":3,"Fair":2,"Poor":1})
    vals = []
    for c in per:
        if c.level:
            pt = cmap.get(c.level)
            if pt is not None:
                vals.append(pt)
    if not vals:
        return None
    return statistics.mean(vals)

# ===============================
# Main per-criterion evaluation flow
# ===============================

def evaluate_one_criterion(
    criterion: Dict[str, Any],
    processed_essay: ProcessedEssay,
    max_span_chars: int = 240,
    model: str = None,
    fast_mode: bool = True
) -> CriterionResult:
    """
    Evaluate one criterion with optional fast mode for better performance.
    
    Args:
        criterion: The criterion to evaluate
        processed_essay: The processed essay data
        max_span_chars: Maximum characters for evidence spans
        model: OpenAI model to use
        fast_mode: If True, use single API call instead of agreement checking (faster)
    """
    system = SYSTEM_BASE.format(max_span_chars=max_span_chars)
    base_prompt = make_criterion_user_prompt(criterion, processed_essay, max_span_chars)

    if fast_mode:
        # Fast mode: Single API call (3-5x faster)
        final = llm_json(base_prompt, system, model)
        refused = final.get("refuse") is True
        agreement_flag = "ok"
        tie_break_used = False
        low_conf = False
        explanation = None
    else:
        # Full mode: Agreement checking (original behavior)
        # Agreement check: run two slightly perturbed versions
        out1 = llm_json(make_agreement_variant_prompt(base_prompt, "A"), system, model)
        out2 = llm_json(make_agreement_variant_prompt(base_prompt, "B"), system, model)

        # If either refused, mark refuse (you can decide a stricter policy)
        refused = (out1.get("refuse") is True) or (out2.get("refuse") is True)

        # Choose final level:
        lvl1 = out1.get("level")
        lvl2 = out2.get("level")
        final = out1
        agreement_flag = "ok"
        tie_break_used = False

        if not refused and lvl1 and lvl2 and lvl1 != lvl2:
            agreement_flag = "needs_review"
            # optional tie-break third pass:
            out3 = llm_json(make_agreement_variant_prompt(base_prompt, "TIE_BREAK"), system, model)
            lvl3 = out3.get("level")
            if lvl3 and (lvl3 == lvl1 or lvl3 == lvl2):
                final = out3
                agreement_flag = "ok"
                tie_break_used = True
            else:
                # If still no agreement, choose by scale order as a pragmatic default,
                # and keep the "needs_review" flag.
                final_level = tie_break_choice(lvl1, lvl2, criterion["valid_levels"])
                final = {**out1, "level": final_level}

        # Consistency self-check
        consistency = llm_json(
            make_consistency_prompt(final, criterion),
            system="You are a strict JSON validator.",
            model=model
        )
        low_conf = bool(consistency.get("low_confidence"))
        explanation = consistency.get("explanation")

    return CriterionResult(
        criterion_id=final.get("criterion_id", criterion.get("id")),
        valid_levels=final.get("valid_levels", criterion["valid_levels"]),
        level=final.get("level"),
        justification=final.get("justification"),
        evidence_spans=final.get("evidence_spans", []),
        actionable_suggestion=final.get("actionable_suggestion"),
        refuse=bool(final.get("refuse", False) or refused),
        reason=final.get("reason"),
        low_confidence=low_conf,
        consistency_explanation=explanation,
        agreement_flag="ok" if not refused and not low_conf and agreement_flag=="ok" else agreement_flag,
        tie_break_used=tie_break_used
    )


def evaluate_all_criteria_single_call(
    rubric: Dict[str, Any],
    processed_essay: ProcessedEssay,
    max_span_chars: int = 240,
    model: str = None
) -> List[CriterionResult]:
    """
    Evaluate all criteria in a single API call for maximum efficiency.
    
    Args:
        rubric: The rubric to use for grading
        processed_essay: The processed essay data
        max_span_chars: Maximum characters for evidence spans
        model: OpenAI model to use
        
    Returns:
        List of CriterionResult objects
    """
    system = SYSTEM_BASE.format(max_span_chars=max_span_chars)
    
    # Create combined prompt for all criteria
    combined_prompt = make_combined_criteria_prompt(rubric, processed_essay, max_span_chars)
    
    # Single API call
    result = llm_json(combined_prompt, system, model)
    
    # Parse the combined result
    return parse_combined_criteria_result(result, rubric)


def make_combined_criteria_prompt(
    rubric: Dict[str, Any],
    processed_essay: ProcessedEssay,
    max_span_chars: int = 240
) -> str:
    """Create a single prompt that evaluates all criteria at once."""
    # Extract paragraphs with rich metadata
    essay_paragraphs = [p.text for p in processed_essay.paragraphs if p.text.strip()]
    essay_block = "\n".join([f"[{i}] {p}" for i, p in enumerate(essay_paragraphs)])
    
    # Include essay metadata for better context
    metadata = processed_essay.metadata
    essay_context = f"""
ESSAY METADATA
- Word count: {metadata.word_count}
- Language: {metadata.language_detected}
- Readability: {metadata.readability.flesch_reading_ease:.1f} (Flesch Reading Ease)
- Quote ratio: {metadata.quote_char_ratio:.1%}
- Sections: {len(metadata.sections)}
"""

    # Build criteria section
    criteria_section = ""
    for i, criterion in enumerate(rubric["criteria"]):
        valid_levels_list = criterion["valid_levels"]
        descriptors = criterion["descriptors"]
        
        criteria_section += f"""
CRITERION {i+1}
- criterion_id: {criterion.get('id')}
- name: {criterion.get('name')}
- valid_levels (choose EXACTLY one): {valid_levels_list}
- level scale note: {criterion.get('level_scale_note', '')}

DESCRIPTORS (for this criterion only)
{descriptors}

"""
    
    return f"""
You will grade ALL criteria for this essay in a single response with RICH, DETAILED analysis.

{criteria_section}

{essay_context}

ESSAY (paragraph-indexed)
{essay_block}

REQUIREMENTS FOR RICH ANALYSIS:
1) Return STRICT JSON with an array called "criteria_results"
2) Each item in the array should have EXACTLY these keys:
   - "criterion_id" (string)
   - "valid_levels" (array of strings)
   - "level" (string, must be one of valid_levels)
   - "justification" (string, 2-4 detailed sentences explaining your reasoning)
   - "evidence_spans" (array of objects with "paragraph_index" and "quote")
   - "actionable_suggestion" (string, one concrete, specific improvement)

EVIDENCE SPAN REQUIREMENTS (CRITICAL):
3) "evidence_spans": 
   - Find MULTIPLE evidence spans per criterion (aim for 2-4 spans)
   - Each quote must be <= {max_span_chars} characters
   - Quotes must appear VERBATIM in the essay paragraphs
   - Include both POSITIVE evidence (what's done well) and NEGATIVE evidence (what needs improvement)
   - Prioritize the MOST RELEVANT and STRONGEST evidence
   - Include context around key points (don't just grab single words)
   - Use complete sentences or meaningful phrases, not fragments

ANALYSIS DEPTH:
4) Provide detailed justification that:
   - References specific evidence spans
   - Explains WHY the evidence supports the grade level
   - Considers the essay's overall quality and coherence
   - Acknowledges both strengths and weaknesses
5) Consider essay metadata (word count, readability, language) in your evaluation
6) Never invent content; only quote from the essay paragraphs provided

Return ONLY the JSON object with the "criteria_results" array—no commentary.
"""


def parse_combined_criteria_result(
    result: Dict[str, Any],
    rubric: Dict[str, Any]
) -> List[CriterionResult]:
    """Parse the combined criteria result into individual CriterionResult objects with enhanced evidence validation."""
    criteria_results = result.get("criteria_results", [])
    
    parsed_results = []
    for i, criterion_data in enumerate(criteria_results):
        # Get the original criterion for reference
        original_criterion = rubric["criteria"][i] if i < len(rubric["criteria"]) else {}
        
        # Validate and enhance evidence spans
        evidence_spans = criterion_data.get("evidence_spans", [])
        validated_spans = []
        
        for span in evidence_spans:
            if isinstance(span, dict) and "quote" in span and "paragraph_index" in span:
                # Ensure quote is not empty and has reasonable length
                quote = span.get("quote", "").strip()
                if quote and len(quote) > 10:  # Minimum meaningful length
                    validated_spans.append({
                        "quote": quote,
                        "paragraph_index": span.get("paragraph_index"),
                        "start": span.get("start", 0),
                        "end": span.get("end", len(quote))
                    })
        
        # If no valid evidence spans found, try to create a fallback
        if not validated_spans and criterion_data.get("justification"):
            # Create a minimal evidence span from the justification context
            justification = criterion_data.get("justification", "")
            if justification and len(justification) > 20:
                validated_spans.append({
                    "quote": justification[:200] + "..." if len(justification) > 200 else justification,
                    "paragraph_index": 0,
                    "start": 0,
                    "end": len(justification)
                })
        
        parsed_result = CriterionResult(
            criterion_id=criterion_data.get("criterion_id", original_criterion.get("id", f"criterion_{i}")),
            valid_levels=criterion_data.get("valid_levels", original_criterion.get("valid_levels", [])),
            level=criterion_data.get("level"),
            justification=criterion_data.get("justification"),
            evidence_spans=validated_spans,
            actionable_suggestion=criterion_data.get("actionable_suggestion"),
            refuse=bool(criterion_data.get("refuse", False)),
            reason=criterion_data.get("reason"),
            low_confidence=False,  # Single call doesn't have consistency checking
            consistency_explanation=None,
            agreement_flag="ok",
            tie_break_used=False
        )
        parsed_results.append(parsed_result)
    
    return parsed_results

def grade_essay(
    rubric: Dict[str, Any],
    processed_essay: ProcessedEssay,
    max_span_chars: int = 240,
    model: str = None,
    fast_mode: bool = True
) -> GradeSummary:
    """
    Grade an essay against a rubric with optional fast mode for better performance.
    
    Args:
        rubric: The rubric to use for grading
        processed_essay: The processed essay data
        max_span_chars: Maximum characters for evidence spans
        model: OpenAI model to use
        fast_mode: If True, use single API call for all criteria (much faster)
    """
    # Get optimization config
    config = get_optimization_config() if OPTIMIZATION_AVAILABLE else None
    
    # Apply optimization settings
    if config:
        # Use configured fast mode if not explicitly set
        if fast_mode is None:
            fast_mode = config.use_fast_mode_by_default
        
        # Limit essay length for processing
        if len(processed_essay.paragraphs) > config.max_essay_paragraphs:
            print(f"⚠️  Essay has {len(processed_essay.paragraphs)} paragraphs, limiting to {config.max_essay_paragraphs} for performance")
            processed_essay.paragraphs = processed_essay.paragraphs[:config.max_essay_paragraphs]
        
        # Use configured evidence span length
        max_span_chars = min(max_span_chars, config.max_evidence_span_chars)
    
    if fast_mode:
        # Single API call for all criteria (much faster and cheaper)
        results = evaluate_all_criteria_single_call(rubric, processed_essay, max_span_chars, model)
    else:
        # Multiple API calls (original approach for maximum accuracy)
        results: List[CriterionResult] = []
        for crit in rubric["criteria"]:
            res = evaluate_one_criterion(crit, processed_essay, max_span_chars=max_span_chars, model=model, fast_mode=False)
            results.append(res)

    # Aggregations
    numeric_score, letter = compute_weighted_numeric(results, rubric)
    categorical_points = None
    if not rubric.get("grading", {}).get("numeric", False):
        categorical_points = compute_categorical_aggregate(results, rubric)
        # if you ALSO want to show numeric (mapped) alongside categorical, you can compute both.

    # Notes about reliability/safety
    flags = {
        "any_refusals": any(r.refuse for r in results),
        "any_low_confidence": any(r.low_confidence for r in results),
        "any_needs_review": any(r.agreement_flag != "ok" for r in results),
    }
    
    # Add essay metadata insights
    metadata_insights = {
        "essay_length": processed_essay.metadata.word_count,
        "language": processed_essay.metadata.language_detected,
        "readability_score": processed_essay.metadata.readability.flesch_reading_ease,
        "quote_char_ratio": processed_essay.metadata.quote_char_ratio,
        "section_count": len(processed_essay.metadata.sections),
        "warnings": processed_essay.warnings
    }
    
    # Combine flags with metadata insights
    combined_notes = {**flags, "essay_metadata": metadata_insights}

    return GradeSummary(
        per_criterion=results,
        numeric_score=None if numeric_score is None else round(numeric_score, 2),
        letter=letter,
        categorical_points=None if categorical_points is None else round(categorical_points, 2),
        notes=combined_notes
    )


def convert_rubric_format(parsed_rubric: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert rubric from rubric_parser_prompt.py format to grading_engine.py format.
    
    Args:
        parsed_rubric: Rubric dictionary from RubricParser
        
    Returns:
        Converted rubric dictionary for grading engine
    """
    converted_criteria = []
    
    for criterion in parsed_rubric.get("criteria", []):
        # Convert descriptor_by_level to descriptors format
        descriptors = {}
        for level, description in criterion.get("descriptor_by_level", {}).items():
            descriptors[level] = description
        
        # Create converted criterion
        converted_criterion = {
            "id": criterion.get("name", "").lower().replace(" ", "_").replace("&", "and"),
            "name": criterion.get("name", ""),
            "descriptors": descriptors,
            "valid_levels": list(descriptors.keys()),
            "weight": criterion.get("weight", 1.0),
            "level_scale_note": f"{' > '.join(descriptors.keys())}"
        }
        converted_criteria.append(converted_criterion)
    
    # Determine scale type and create grading configuration
    scale_type = parsed_rubric.get("scale", {}).get("type", "categorical")
    levels = parsed_rubric.get("scale", {}).get("levels", [])
    
    if scale_type == "categorical" and levels:
        # Create categorical points mapping
        categorical_points_map = {}
        for i, level in enumerate(levels):
            categorical_points_map[level] = len(levels) - i
        
        converted_rubric = {
            "criteria": converted_criteria,
            "grading": {
                "numeric": True,
                "letter_bands": [
                    {"min": 90, "max": 100, "letter": "A+"},
                    {"min": 85, "max": 89.99, "letter": "A"},
                    {"min": 80, "max": 84.99, "letter": "A-"},
                    {"min": 70, "max": 79.99, "letter": "B"},
                    {"min": 60, "max": 69.99, "letter": "C"},
                    {"min": 0, "max": 59.99, "letter": "D or below"}
                ],
                "categorical_points_map": categorical_points_map
            }
        }
    else:
        # Numeric scale
        min_val = parsed_rubric.get("scale", {}).get("min", 0)
        max_val = parsed_rubric.get("scale", {}).get("max", 100)
        
        converted_rubric = {
            "criteria": converted_criteria,
            "grading": {
                "numeric": True,
                "letter_bands": [
                    {"min": 90, "max": 100, "letter": "A+"},
                    {"min": 85, "max": 89.99, "letter": "A"},
                    {"min": 80, "max": 84.99, "letter": "A-"},
                    {"min": 70, "max": 79.99, "letter": "B"},
                    {"min": 60, "max": 69.99, "letter": "C"},
                    {"min": 0, "max": 59.99, "letter": "D or below"}
                ]
            }
        }
    
    return converted_rubric


# Import parse_rubric_file from rubric_parser_prompt.py
from rubric_parser_prompt import parse_rubric_file as _parse_rubric_file

def parse_rubric_file(rubric_path: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
    """
    Parse a rubric file using the RubricParser and return the structured rubric.
    This is a wrapper that converts the rubric format for the grading engine.
    
    Args:
        rubric_path: Path to the rubric file (DOCX, TXT)
        model: OpenAI model to use for parsing
        
    Returns:
        Converted rubric dictionary for grading engine
        
    Raises:
        ValueError: If parsing fails
    """
    try:
        # Parse using the original function
        parsed_rubric = _parse_rubric_file(rubric_path, model)
        
        # Convert the rubric format for grading engine
        converted_rubric = convert_rubric_format(parsed_rubric)
        return converted_rubric
            
    except Exception as e:
        raise ValueError(f"Error parsing rubric file {rubric_path}: {str(e)}")


def grade_essay_with_rubric_file(
    rubric_path: str,
    processed_essay: ProcessedEssay,
    max_span_chars: int = 240,
    model: str = "gpt-4o-mini"
) -> GradeSummary:
    """
    Grade an essay using a rubric file (parses the rubric first, then grades).
    
    Args:
        rubric_path: Path to the rubric file
        processed_essay: Preprocessed essay data
        max_span_chars: Maximum characters for evidence spans
        model: OpenAI model to use for rubric parsing
        
    Returns:
        GradeSummary with grading results
    """
    # Parse and convert the rubric file
    rubric = parse_rubric_file(rubric_path, model)
    
    # Grade the essay using the converted rubric
    return grade_essay(rubric, processed_essay, max_span_chars)


def complete_grading_workflow(
    rubric_path: str,
    essay_path: str,
    max_span_chars: int = 240,
    model: str = "gpt-4o-mini"
) -> Dict[str, Any]:
    """
    Complete grading workflow: parse rubric + preprocess essay + grade essay.
    
    Args:
        rubric_path: Path to the rubric file (DOCX, TXT)
        essay_path: Path to the essay file
        max_span_chars: Maximum characters for evidence spans
        model: OpenAI model to use
        
    Returns:
        Complete grading results with rubric info, essay metadata, and grades
    """
    try:
        # Step 1: Parse the rubric
        print("🔍 Step 1: Parsing rubric...")
        rubric = parse_rubric_file(rubric_path, model)  # Already converted
        
        # Step 2: Preprocess the essay
        print("🔍 Step 2: Preprocessing essay...")
        from essay_preprocessor import EssayPreprocessor, PreprocessOptions
        
        # Read the essay file first
        with open(essay_path, 'r', encoding='utf-8', errors='ignore') as f:
            essay_text = f.read()
        
        preprocessor = EssayPreprocessor()
        options = PreprocessOptions()
        processed_essay = preprocessor.run(essay_text, options)
        
        print(f"✅ Essay preprocessed: {processed_essay.metadata.word_count} words, "
              f"{len(processed_essay.paragraphs)} paragraphs")
        
        # Step 3: Grade the essay
        print("🔍 Step 3: Grading essay...")
        grade_summary = grade_essay(rubric, processed_essay, max_span_chars)
        
        # Step 4: Generate insights
        print("🔍 Step 4: Generating insights...")
        essay_insights = generate_essay_insights(processed_essay)
        
        # Compile complete results
        results = {
            "rubric_info": {
                "title": "Parsed Rubric",  # Converted rubric doesn't have title
                "scale_type": "categorical",  # Converted to categorical
                "criteria_count": len(rubric.get("criteria", [])),
                "grading_config": rubric.get("grading", {})
            },
            "essay_metadata": {
                "word_count": processed_essay.metadata.word_count,
                "language": processed_essay.metadata.language_detected,
                "readability": processed_essay.metadata.readability.flesch_reading_ease,
                "quote_char_ratio": processed_essay.metadata.quote_char_ratio,
                "section_count": len(processed_essay.metadata.sections)
            },
            "grading_results": {
                "numeric_score": grade_summary.numeric_score,
                "letter_grade": grade_summary.letter,
                "categorical_points": grade_summary.categorical_points,
                "per_criterion": [
                    {
                        "criterion_id": result.criterion_id,
                        "level": result.level,
                        "justification": result.justification,
                        "evidence_spans": result.evidence_spans,
                        "actionable_suggestion": result.actionable_suggestion,
                        "refuse": result.refuse
                    }
                    for result in grade_summary.per_criterion
                ]
            },
            "essay_insights": essay_insights,
            "flags": grade_summary.notes
        }
        
        print("✅ Complete grading workflow finished!")
        return results
        
    except Exception as e:
        print(f"❌ Error in complete grading workflow: {e}")
        raise


def generate_essay_insights(processed_essay: ProcessedEssay) -> Dict[str, Any]:
    """Generate insights about the essay based on preprocessor metadata."""
    metadata = processed_essay.metadata
    
    insights = {
        "length_assessment": _assess_essay_length(metadata.word_count),
        "readability_assessment": _assess_readability(metadata.readability.flesch_reading_ease),
        "structure_assessment": _assess_structure(len(metadata.sections), len(processed_essay.paragraphs)),
        "quote_usage": _assess_quote_usage(metadata.quote_char_ratio),
        "language_notes": _assess_language(metadata.language_detected),
        "overall_quality_indicators": _assess_overall_quality(processed_essay)
    }
    
    return insights


def _assess_essay_length(word_count: int) -> Dict[str, Any]:
    """Assess essay length and provide feedback."""
    if word_count < 200:
        return {"level": "too_short", "message": "Essay is quite short. Consider expanding your arguments with more detail and examples."}
    elif word_count < 500:
        return {"level": "short", "message": "Essay is on the shorter side. You could develop your ideas further."}
    elif word_count < 1000:
        return {"level": "good", "message": "Essay has a good length for developing your arguments."}
    elif word_count < 2000:
        return {"level": "long", "message": "Essay is quite long. Consider tightening your arguments for clarity."}
    else:
        return {"level": "very_long", "message": "Essay is very long. Consider breaking into sections or tightening focus."}


def _assess_readability(flesch_score: Optional[float]) -> Dict[str, Any]:
    """Assess essay readability."""
    if flesch_score is None:
        return {"level": "unknown", "message": "Readability score not available."}
    elif flesch_score < 30:
        return {"level": "very_difficult", "message": "Essay is very difficult to read. Consider simplifying sentence structure."}
    elif flesch_score < 50:
        return {"level": "difficult", "message": "Essay is somewhat difficult to read. Consider using shorter sentences."}
    elif flesch_score < 70:
        return {"level": "standard", "message": "Essay has standard readability for academic writing."}
    elif flesch_score < 80:
        return {"level": "fairly_easy", "message": "Essay is fairly easy to read."}
    else:
        return {"level": "easy", "message": "Essay is very easy to read. Consider adding more sophisticated vocabulary."}


def _assess_structure(section_count: int, paragraph_count: int) -> Dict[str, Any]:
    """Assess essay structure."""
    if section_count == 0 and paragraph_count < 3:
        return {"level": "poor", "message": "Essay lacks clear structure. Consider adding an introduction, body paragraphs, and conclusion."}
    elif section_count == 0 and paragraph_count < 5:
        return {"level": "basic", "message": "Essay has basic structure but could benefit from more organization."}
    elif section_count > 0 or paragraph_count >= 5:
        return {"level": "good", "message": "Essay shows good structural organization."}
    else:
        return {"level": "excellent", "message": "Essay has excellent structural organization."}


def _assess_quote_usage(quote_char_ratio: float) -> Dict[str, Any]:
    """Assess quote usage in the essay."""
    if quote_char_ratio < 0.05:
        return {"level": "low", "message": "Essay uses few quotes. Consider incorporating more evidence to support your arguments."}
    elif quote_char_ratio < 0.15:
        return {"level": "moderate", "message": "Essay has moderate quote usage. Good balance of original analysis and evidence."}
    elif quote_char_ratio < 0.30:
        return {"level": "high", "message": "Essay uses many quotes. Consider adding more original analysis."}
    else:
        return {"level": "very_high", "message": "Essay relies heavily on quotes. Focus more on your own analysis and interpretation."}


def _assess_language(language: str) -> Dict[str, Any]:
    """Assess language usage."""
    if language != "en":
        return {"level": "non_english", "message": f"Essay is in {language}. Consider providing an English translation for better evaluation."}
    else:
        return {"level": "english", "message": "Essay is in English, which is appropriate for evaluation."}


def _assess_overall_quality(processed_essay: ProcessedEssay) -> Dict[str, Any]:
    """Assess overall essay quality indicators."""
    quality_indicators = []
    
    # Check for warnings
    if processed_essay.warnings:
        quality_indicators.append(f"Processing warnings: {len(processed_essay.warnings)}")
    
    # Check paragraph structure
    if len(processed_essay.paragraphs) < 3:
        quality_indicators.append("Very few paragraphs - may lack development")
    
    # Check for quotes
    if processed_essay.metadata.quote_char_ratio > 0:
        quality_indicators.append("Contains quoted material")
    
    return {
        "indicators": quality_indicators,
        "overall_assessment": "Good" if len(quality_indicators) < 2 else "Needs attention"
    }


# ===============================
# Example usage with RubricParser integration
# ===============================

def example_with_rubric_file():
    """Example showing how to use the grading engine with rubric files."""
    try:
        # Example usage with rubric file
        rubric_path = "test_file/test_rubric.docx"  # Your rubric file
        essay_path = "test_file/sample_essay.txt"    # Your essay file
        
        print("🚀 Running complete grading workflow...")
        results = complete_grading_workflow(rubric_path, essay_path)
        
        print("\n📊 Results Summary:")
        print(f"Rubric: {results['rubric_info']['title']}")
        print(f"Scale: {results['rubric_info']['scale_type']}")
        print(f"Criteria: {results['rubric_info']['criteria_count']}")
        print(f"Essay: {results['essay_metadata']['word_count']} words")
        print(f"Grade: {results['grading_results']['letter_grade']} ({results['grading_results']['numeric_score']})")
        
        return results
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        return None


def example_with_parsed_rubric():
    """Example showing how to use the grading engine with a parsed rubric."""
    try:
        # Parse a rubric file
        rubric_path = "test_file/test_rubric.docx"
        rubric = parse_rubric_file(rubric_path)  # Already converted
        
        # Create a sample essay (in practice, you'd load from file)
        sample_essay_text = """
        The impact of social media on modern communication has been profound. 
        While it has connected people across the globe, it has also created new challenges 
        in maintaining meaningful relationships. This essay will explore both the positive 
        and negative effects of social media on interpersonal communication.
        """
        
        # Preprocess the essay
        from essay_preprocessor import EssayPreprocessor, PreprocessOptions
        preprocessor = EssayPreprocessor()
        options = PreprocessOptions()
        processed_essay = preprocessor.run(sample_essay_text, options)
        
        # Grade the essay
        summary = grade_essay(rubric, processed_essay)
        
        print("📊 Grading Results:")
        print(f"  Numeric Score: {summary.numeric_score}")
        print(f"  Letter Grade: {summary.letter}")
        print(f"  Categorical Points: {summary.categorical_points}")
        
        print("\n📝 Per-Criterion Results:")
        for result in summary.per_criterion:
            print(f"  {result.criterion_id}: {result.level}")
            print(f"    Justification: {result.justification}")
            print(f"    Evidence: {len(result.evidence_spans)} spans")
            print(f"    Suggestion: {result.actionable_suggestion}")
            print()
        
        return summary
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        return None


# ===============================
# Main Example Usage
# ===============================

def run_grading_example():
    """Main function demonstrating complete grading workflow."""
    print("🚀 RubriCheck Grading Engine - Example Usage")
    print("=" * 60)
    
    try:
        # Example 1: Complete workflow with files
        print("\n📋 Example 1: Complete Grading Workflow")
        print("-" * 40)
        
        rubric_path = "test_file/test_rubric.docx"
        essay_path = "test_file/test_essay.txt"
        
        # Check if files exist
        if not os.path.exists(rubric_path):
            print(f"⚠️  Rubric file not found: {rubric_path}")
            print("💡 Please ensure you have a rubric file at this path")
            rubric_path = None
        
        if not os.path.exists(essay_path):
            print(f"⚠️  Essay file not found: {essay_path}")
            print("💡 Please ensure you have an essay file at this path")
            essay_path = None
        
        if rubric_path and essay_path:
            print(f"📄 Using rubric: {rubric_path}")
            print(f"📄 Using essay: {essay_path}")
            
            #Run complete workflow
            results = complete_grading_workflow(rubric_path, essay_path)
            
            print("\n📊 Final Results:")
            print(f"  Rubric: {results['rubric_info']['title']}")
            print(f"  Scale: {results['rubric_info']['scale_type']}")
            print(f"  Criteria: {results['rubric_info']['criteria_count']}")
            print(f"  Essay: {results['essay_metadata']['word_count']} words")
            print(f"  Grade: {results['grading_results']['letter_grade']} ({results['grading_results']['numeric_score']})")
            
            # Show per-criterion results
            print("\n📝 Per-Criterion Results:")
            for result in results['grading_results']['per_criterion']:
                print(f"  • {result['criterion_id']}: {result['level']}")
                print(f"    Justification: {result['justification'][:100]}...")
                print(f"    Evidence: {len(result['evidence_spans'])} spans")
                print(f"    Suggestion: {result['actionable_suggestion']}")
                print()
        
        # Example 2: Step-by-step workflow
        print("\n📋 Example 2: Step-by-Step Workflow")
        print("-" * 40)
        
        # Create sample rubric data
        sample_rubric = {
            "title": "Sample Essay Rubric",
            "scale": {
                "type": "categorical",
                "levels": ["Excellent", "Good", "Fair", "Poor"]
            },
            "criteria": [
                {
                    "id": "thesis",
                    "name": "Thesis & Focus",
                    "descriptor_by_level": {
                        "Excellent": "Clear, arguable thesis driving the essay",
                        "Good": "Thesis is present but somewhat broad",
                        "Fair": "Thesis is vague or inconsistently maintained",
                        "Poor": "No clear thesis or thesis is off-topic"
                    },
                    "weight": 3
                },
                {
                    "id": "evidence",
                    "name": "Evidence & Support",
                    "descriptor_by_level": {
                        "Excellent": "Strong, relevant evidence; well-integrated",
                        "Good": "Good evidence; mostly relevant",
                        "Fair": "Limited or somewhat irrelevant evidence",
                        "Poor": "Lacks evidence or off-topic"
                    },
                    "weight": 2
                }
            ],
            "source_parse": {
                "method": "narrative",
                "confidence": 1.0,
                "warnings": []
            }
        }
        
        # Create sample essay text
        sample_essay_text = """
        The impact of social media on modern communication has been profound and far-reaching. 
        While platforms like Facebook, Twitter, and Instagram have connected people across the globe, 
        they have also created new challenges in maintaining meaningful relationships and authentic 
        communication. This essay will explore both the positive and negative effects of social media 
        on interpersonal communication, examining how these platforms have transformed the way we 
        interact with one another.
        
        On the positive side, social media has democratized communication, allowing individuals 
        to share their thoughts and experiences with a global audience. It has enabled people to 
        maintain connections with friends and family members who live far away, and has provided 
        a platform for marginalized voices to be heard. However, the constant connectivity has 
        also led to issues such as information overload, decreased attention spans, and the 
        proliferation of misinformation.
        
        In conclusion, while social media has undoubtedly changed the landscape of communication, 
        it is up to individuals and society as a whole to navigate these changes responsibly and 
        ensure that these tools enhance rather than diminish our ability to connect meaningfully 
        with others.
        """
        
        print("📝 Using sample rubric and essay text...")
        
        # Preprocess the essay
        from essay_preprocessor import EssayPreprocessor, PreprocessOptions
        preprocessor = EssayPreprocessor()
        options = PreprocessOptions()
        processed_essay = preprocessor.run(sample_essay_text, options)
        
        print(f"✅ Essay preprocessed: {processed_essay.metadata.word_count} words, "
              f"{len(processed_essay.paragraphs)} paragraphs")
        
        # Convert the sample rubric to grading engine format
        converted_rubric = convert_rubric_format(sample_rubric)
        
        # Grade the essay
        summary = grade_essay(converted_rubric, processed_essay)
        
        print("\n📊 Grading Results:")
        print(f"  Numeric Score: {summary.numeric_score}")
        print(f"  Letter Grade: {summary.letter}")
        print(f"  Categorical Points: {summary.categorical_points}")
        
        print("\n📝 Per-Criterion Results:")
        for result in summary.per_criterion:
            print(f"  • {result.criterion_id}: {result.level}")
            print(f"    Justification: {result.justification}")
            print(f"    Evidence: {len(result.evidence_spans)} spans")
            print(f"    Suggestion: {result.actionable_suggestion}")
            print()
        
        # Generate insights
        insights = generate_essay_insights(processed_essay)
        print("🔍 Essay Insights:")
        print(f"  Length Assessment: {insights['length_assessment']['message']}")
        print(f"  Readability: {insights['readability_assessment']['message']}")
        print(f"  Structure: {insights['structure_assessment']['message']}")
        print(f"  Quote Usage: {insights['quote_usage']['message']}")
        
        print("\n✅ Example completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in main example: {e}")
        import traceback
        traceback.print_exc()
        return False


# if __name__ == "__main__":
#     success = run_grading_example()
#     if success:
#         print("\n🎉 All examples completed successfully!")
#     else:
#         print("\n❌ Some examples failed. Check the error messages above.")
