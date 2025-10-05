from __future__ import annotations
import os
import math
import statistics
import json
import re
from typing import Dict, List, Any, Optional, Tuple, Literal
from dataclasses import dataclass, field

# --------- OpenAI client ----------
# pip install openai>=1.0.0
from openai import OpenAI
OPENAI_MODEL = os.environ.get("RUBRICHECK_MODEL", "gpt-4o-mini")

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
client = OpenAI(api_key=api_key)

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

# Essay paragraphs (privacy-processed, chunked upstream if needed):
# essay_paragraphs = ["Para 0 text...", "Para 1 text...", ...]

# ===============================
# Prompt templates
# ===============================

SYSTEM_BASE = """You are RubriCheck, an AI grader that outputs strict JSON for each criterion. 
Rules:
- Only quote text present in the essay. Do not fabricate citations.
- For evidence, quote short excerpts (<= {max_span_chars} characters per excerpt) and include paragraph indices.
- If the rubric content for this criterion is ambiguous or self-contradictory, REFUSE with {{"refuse": true, "reason": "..."}} using the exact JSON schema.
- No praise; provide one actionable suggestion per criterion.
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
    essay_paragraphs: List[str],
    max_span_chars: int = 240
) -> str:
    # Only pass relevant chunk: here we pass full paragraphs; upstream you may pass
    # paragraph indices likely relevant to this criterion. Keep it simple & auditable.
    essay_block = "\n".join([f"[{i}] {p}" for i, p in enumerate(essay_paragraphs)])
    valid_levels_list = criterion["valid_levels"]
    descriptors = criterion["descriptors"]

    return f"""
You will grade ONE criterion only.

CRITERION
- criterion_id: {criterion.get('id')}
- name: {criterion.get('name')}
- valid_levels (choose EXACTLY one): {valid_levels_list}
- level scale note: {criterion.get('level_scale_note', '')}

DESCRIPTORS (for this criterion only)
{descriptors}

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

def llm_json(prompt: str, system: str) -> Dict[str, Any]:
    """
    Calls the OpenAI chat completion and attempts to parse JSON only.
    We ask the model to output ONLY JSON. If it fails, we rethrow with the raw text.
    """
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
    )
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
    essay_paragraphs: List[str],
    max_span_chars: int = 240
) -> CriterionResult:
    system = SYSTEM_BASE.format(max_span_chars=max_span_chars)
    base_prompt = make_criterion_user_prompt(criterion, essay_paragraphs, max_span_chars)

    # Agreement check: run two slightly perturbed versions
    out1 = llm_json(make_agreement_variant_prompt(base_prompt, "A"), system)
    out2 = llm_json(make_agreement_variant_prompt(base_prompt, "B"), system)

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
        out3 = llm_json(make_agreement_variant_prompt(base_prompt, "TIE_BREAK"), system)
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
        system="You are a strict JSON validator."
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

def grade_essay(
    rubric: Dict[str, Any],
    essay_paragraphs: List[str],
    max_span_chars: int = 240
) -> GradeSummary:
    results: List[CriterionResult] = []
    for crit in rubric["criteria"]:
        res = evaluate_one_criterion(crit, essay_paragraphs, max_span_chars=max_span_chars)
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

    return GradeSummary(
        per_criterion=results,
        numeric_score=None if numeric_score is None else round(numeric_score, 2),
        letter=letter,
        categorical_points=None if categorical_points is None else round(categorical_points, 2),
        notes=flags
    )

# ===============================
# Example usage
# ===============================
if __name__ == "__main__":
    import json

    # Example rubric (minimal):
    rubric = {
        "criteria": [
            {
                "id": "thesis",
                "name": "Thesis & Focus",
                "descriptors": {
                    "Excellent": "Clear, arguable thesis driving the essay.",
                    "Good": "Thesis is present but somewhat broad or unevenly maintained.",
                    "Fair": "Thesis is unclear, implied, or inconsistently applied.",
                    "Poor": "No discernible thesis or focus."
                },
                "valid_levels": ["Excellent","Good","Fair","Poor"],
                "weight": 0.25,
                "level_scale_note": "Excellent > Good > Fair > Poor"
            },
            {
                "id": "evidence",
                "name": "Use of Evidence",
                "descriptors": {
                    "Excellent": "Integrates specific, well-chosen evidence; accurately cited; analysis is insightful.",
                    "Good": "Evidence is generally apt; some analysis; minor lapses.",
                    "Fair": "Evidence is limited, vague, or inconsistently analyzed.",
                    "Poor": "Little to no relevant evidence; analysis missing."
                },
                "valid_levels": ["Excellent","Good","Fair","Poor"],
                "weight": 0.25,
                "level_scale_note": "Excellent > Good > Fair > Poor"
            }
        ],
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

    essay_paragraphs = [
        "This essay argues that renewable energy is essential to national security by reducing dependence on volatile fuel markets.",
        "Several reports show countries with higher renewable portfolios experience less price shock; however, grid stability challenges remain.",
        "Opponents claim costs are prohibitive; this essay demonstrates recent cost curves and policy mechanisms that offset initial investment.",
    ]

    summary = grade_essay(rubric, essay_paragraphs, max_span_chars=180)
    print(json.dumps({
        "per_criterion": [r.__dict__ for r in summary.per_criterion],
        "numeric_score": summary.numeric_score,
        "letter": summary.letter,
        "categorical_points": summary.categorical_points,
        "notes": summary.notes
    }, indent=2, ensure_ascii=False))
