# RubriCheck Grading Engine - Complete Features Guide

## 🎯 Overview
The `grading_engine.py` is the core AI grading engine that takes a parsed rubric and preprocessed essay to generate detailed grading results with AI-powered analysis.

## 📊 Data Structures

### Core Classes

#### `CriterionResult`
```python
@dataclass
class CriterionResult:
    criterion_id: str                    # ID of the criterion
    valid_levels: List[str]              # Available grade levels
    level: Optional[str]                  # Chosen grade level
    justification: Optional[str]          # AI explanation for the grade
    evidence_spans: List[Dict[str, Any]]  # Text evidence with paragraph indices
    actionable_suggestion: Optional[str]  # Improvement suggestion
    refuse: bool                         # Whether AI refused to grade
    reason: Optional[str]                # Reason for refusal
    low_confidence: bool = False         # AI confidence flag
    consistency_explanation: Optional[str] = None  # Consistency check result
    agreement_flag: Literal["ok","needs_review","tie_break"] = "ok"
    tie_break_used: bool = False
```

#### `GradeSummary`
```python
@dataclass
class GradeSummary:
    per_criterion: List[CriterionResult]  # Results for each criterion
    numeric_score: Optional[float]       # Final numeric score
    letter: Optional[str]               # Letter grade (A, B, C, etc.)
    categorical_points: Optional[float] # Categorical scoring
    notes: Dict[str, Any]              # Metadata and flags
```

## 🔧 Core Functions

### 1. **Main Grading Functions**

#### `grade_essay(rubric, processed_essay, max_span_chars=240)`
**Purpose**: Grade an essay using a rubric and preprocessed essay data.

**Parameters**:
- `rubric` (Dict): Parsed rubric dictionary
- `processed_essay` (ProcessedEssay): Preprocessed essay from essay_preprocessor
- `max_span_chars` (int): Maximum characters for evidence quotes

**Returns**: `GradeSummary` object

**Usage**:
```python
from grading_engine import grade_essay
from essay_preprocessor import EssayPreprocessor

# Preprocess essay
preprocessor = EssayPreprocessor()
processed_essay = preprocessor.run(essay_text)

# Grade essay
summary = grade_essay(rubric, processed_essay)
print(f"Grade: {summary.letter} ({summary.numeric_score})")
```

#### `evaluate_one_criterion(criterion, processed_essay, max_span_chars=240)`
**Purpose**: Grade a single criterion of an essay.

**Parameters**:
- `criterion` (Dict): Single criterion from rubric
- `processed_essay` (ProcessedEssay): Preprocessed essay
- `max_span_chars` (int): Maximum characters for evidence

**Returns**: `CriterionResult` object

**Usage**:
```python
# Grade single criterion
criterion = rubric["criteria"][0]  # First criterion
result = evaluate_one_criterion(criterion, processed_essay)
print(f"Criterion: {result.criterion_id}")
print(f"Level: {result.level}")
print(f"Justification: {result.justification}")
```

### 2. **Rubric File Integration**

#### `parse_rubric_file(rubric_path, model="gpt-4o-mini")`
**Purpose**: Parse a rubric file and convert it for the grading engine.

**Parameters**:
- `rubric_path` (str): Path to rubric file (DOCX, TXT)
- `model` (str): OpenAI model for parsing

**Returns**: Converted rubric dictionary

**Usage**:
```python
# Parse rubric file
rubric = parse_rubric_file("test_file/test_rubric.docx")
print(f"Found {len(rubric['criteria'])} criteria")
```

#### `grade_essay_with_rubric_file(rubric_path, processed_essay, max_span_chars=240, model="gpt-4o-mini")`
**Purpose**: Complete workflow: parse rubric file + grade essay.

**Parameters**:
- `rubric_path` (str): Path to rubric file
- `processed_essay` (ProcessedEssay): Preprocessed essay
- `max_span_chars` (int): Maximum characters for evidence
- `model` (str): OpenAI model for parsing

**Returns**: `GradeSummary` object

**Usage**:
```python
# Complete workflow with rubric file
summary = grade_essay_with_rubric_file(
    "test_file/test_rubric.docx", 
    processed_essay
)
```

### 3. **Complete Workflow Functions**

#### `complete_grading_workflow(rubric_path, essay_path, max_span_chars=240, model="gpt-4o-mini")`
**Purpose**: End-to-end grading: parse rubric + preprocess essay + grade + generate insights.

**Parameters**:
- `rubric_path` (str): Path to rubric file
- `essay_path` (str): Path to essay file
- `max_span_chars` (int): Maximum characters for evidence
- `model` (str): OpenAI model

**Returns**: Complete results dictionary

**Usage**:
```python
# Complete end-to-end grading
results = complete_grading_workflow(
    "test_file/test_rubric.docx",
    "test_file/essay.txt"
)

print(f"Final Grade: {results['grading_results']['letter_grade']}")
print(f"Essay Word Count: {results['essay_metadata']['word_count']}")
```

### 4. **Essay Insights Functions**

#### `generate_essay_insights(processed_essay)`
**Purpose**: Generate detailed insights about essay quality based on metadata.

**Parameters**:
- `processed_essay` (ProcessedEssay): Preprocessed essay data

**Returns**: Dictionary with assessment insights

**Usage**:
```python
# Generate essay insights
insights = generate_essay_insights(processed_essay)

print("Essay Insights:")
print(f"Length: {insights['length_assessment']['message']}")
print(f"Readability: {insights['readability_assessment']['message']}")
print(f"Structure: {insights['structure_assessment']['message']}")
```

#### Individual Assessment Functions:
- `_assess_essay_length(word_count)`: Assess essay length
- `_assess_readability(flesch_score)`: Assess readability
- `_assess_structure(section_count, paragraph_count)`: Assess structure
- `_assess_quote_usage(quote_char_ratio)`: Assess quote usage
- `_assess_language(language)`: Assess language
- `_assess_overall_quality(processed_essay)`: Overall quality indicators

### 5. **Utility Functions**

#### `convert_rubric_format(parsed_rubric)`
**Purpose**: Convert rubric from rubric_parser_prompt.py format to grading_engine.py format.

**Parameters**:
- `parsed_rubric` (Dict): Rubric from RubricParser

**Returns**: Converted rubric dictionary

**Usage**:
```python
# Convert rubric format
converted_rubric = convert_rubric_format(parsed_rubric)
```

#### `llm_json(prompt, system)`
**Purpose**: Call OpenAI API and parse JSON response.

**Parameters**:
- `prompt` (str): User prompt
- `system` (str): System prompt

**Returns**: Parsed JSON dictionary

### 6. **Scoring Functions**

#### `compute_weighted_numeric(per_criterion, rubric)`
**Purpose**: Compute weighted numeric score from criterion results.

**Parameters**:
- `per_criterion` (List[CriterionResult]): Criterion results
- `rubric` (Dict): Rubric configuration

**Returns**: Tuple of (numeric_score, letter_grade)

#### `compute_categorical_aggregate(per_criterion, rubric)`
**Purpose**: Compute categorical points aggregate.

**Parameters**:
- `per_criterion` (List[CriterionResult]): Criterion results
- `rubric` (Dict): Rubric configuration

**Returns**: Categorical points average

### 7. **Example Functions**

#### `run_grading_example()`
**Purpose**: Run comprehensive examples demonstrating all features.

**Returns**: Boolean success status

**Usage**:
```python
# Run all examples
success = run_grading_example()
```

#### `example_with_rubric_file()`
**Purpose**: Example using rubric file.

#### `example_with_parsed_rubric()`
**Purpose**: Example using pre-parsed rubric.

## 🎯 Key Features

### 1. **AI-Powered Grading**
- Uses OpenAI GPT models for intelligent grading
- Provides detailed justifications for each grade
- Includes evidence spans with exact text quotes
- Offers actionable improvement suggestions

### 2. **Multi-Level Consistency Checks**
- **Agreement Check**: Runs multiple AI evaluations for consistency
- **Tie-Breaking**: Resolves disagreements with third evaluation
- **Self-Consistency**: AI reviews its own decisions
- **Confidence Flags**: Identifies low-confidence decisions

### 3. **Rich Metadata Integration**
- Uses essay preprocessor metadata (word count, readability, language)
- Includes essay structure analysis (sections, paragraphs)
- Analyzes quote usage and evidence integration
- Provides comprehensive essay insights

### 4. **Flexible Scoring Systems**
- **Numeric Scoring**: Weighted averages with letter grade mapping
- **Categorical Scoring**: Point-based systems
- **Custom Weighting**: Supports criterion weights
- **Letter Bands**: Configurable grade boundaries

### 5. **Safety and Reliability**
- **Refusal Mechanism**: AI can refuse to grade ambiguous criteria
- **Error Handling**: Graceful handling of parsing errors
- **Validation**: JSON schema validation for responses
- **Warning Flags**: Identifies potential issues

## 📝 Usage Examples

### Basic Grading
```python
from grading_engine import grade_essay
from essay_preprocessor import EssayPreprocessor

# Setup
preprocessor = EssayPreprocessor()
processed_essay = preprocessor.run(essay_text)

# Grade
summary = grade_essay(rubric, processed_essay)

# Results
print(f"Grade: {summary.letter} ({summary.numeric_score})")
for result in summary.per_criterion:
    print(f"{result.criterion_id}: {result.level}")
    print(f"  Justification: {result.justification}")
    print(f"  Evidence: {len(result.evidence_spans)} spans")
```

### Complete Workflow
```python
from grading_engine import complete_grading_workflow

# End-to-end grading
results = complete_grading_workflow(
    "rubric.docx",
    "essay.txt"
)

# Access results
print(f"Final Grade: {results['grading_results']['letter_grade']}")
print(f"Essay Insights: {results['essay_insights']}")
```

### Single Criterion Grading
```python
from grading_engine import evaluate_one_criterion

# Grade one criterion
criterion = rubric["criteria"][0]
result = evaluate_one_criterion(criterion, processed_essay)

print(f"Level: {result.level}")
print(f"Justification: {result.justification}")
print(f"Evidence: {result.evidence_spans}")
```

### Essay Insights
```python
from grading_engine import generate_essay_insights

# Generate insights
insights = generate_essay_insights(processed_essay)

# Access insights
print(f"Length Assessment: {insights['length_assessment']['message']}")
print(f"Readability: {insights['readability_assessment']['message']}")
print(f"Structure: {insights['structure_assessment']['message']}")
```

## 🔧 Configuration

### Environment Variables
- `RUBRICHECK_MODEL`: OpenAI model to use (default: "gpt-4o-mini")
- `OPENAI_API_KEY`: OpenAI API key (or use utils.py for file-based loading)

### Rubric Format Requirements
The grading engine expects rubrics in this format:
```python
{
    "criteria": [
        {
            "id": "thesis",
            "name": "Thesis & Focus",
            "descriptors": {
                "Excellent": "Clear, arguable thesis...",
                "Good": "Thesis present but...",
                "Fair": "Thesis is unclear...",
                "Poor": "No discernible thesis..."
            },
            "valid_levels": ["Excellent", "Good", "Fair", "Poor"],
            "weight": 1.0,
            "level_scale_note": "Excellent > Good > Fair > Poor"
        }
    ],
    "grading": {
        "numeric": True,
        "letter_bands": [
            {"min": 90, "max": 100, "letter": "A+"},
            {"min": 85, "max": 89.99, "letter": "A"}
        ]
    }
}
```

## 🚀 Getting Started

1. **Install Dependencies**:
   ```bash
   pip install openai>=1.0.0
   ```

2. **Set API Key**:
   ```python
   # Option 1: Environment variable
   os.environ["OPENAI_API_KEY"] = "your-api-key"
   
   # Option 2: Use utils.py (recommended)
   from utils import get_api_key_from_env
   ```

3. **Run Example**:
   ```python
   from grading_engine import run_grading_example
   run_grading_example()
   ```

## 📊 Output Format

### GradeSummary Output
```python
{
    "per_criterion": [
        {
            "criterion_id": "thesis",
            "level": "Good",
            "justification": "The essay presents a clear thesis...",
            "evidence_spans": [
                {
                    "paragraph_index": 0,
                    "quote": "The impact of social media..."
                }
            ],
            "actionable_suggestion": "Consider strengthening your thesis...",
            "refuse": False,
            "low_confidence": False
        }
    ],
    "numeric_score": 85.5,
    "letter": "A",
    "categorical_points": 3.2,
    "notes": {
        "any_refusals": False,
        "any_low_confidence": False,
        "essay_metadata": {
            "word_count": 450,
            "language": "en",
            "readability_score": 65.2
        }
    }
}
```

This comprehensive guide covers all available features and methods in the `grading_engine.py` module! 🎉
