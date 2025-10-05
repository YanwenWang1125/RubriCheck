# RubriCheck Complete Pipeline Documentation

## Overview

RubriCheck is a comprehensive AI-powered essay grading system that combines three core modules to provide automated, rubric-based essay assessment. The system processes student essays, parses grading rubrics, and generates detailed feedback using OpenAI's language models.

## Architecture

The RubriCheck pipeline consists of three integrated modules:

1. **Essay Preprocessor** (`essay_preprocessor.py`) - Structures and analyzes student essays
2. **Rubric Parser** (`rubric_parser_prompt.py`) - Extracts and parses grading rubrics
3. **Grading Engine** (`grading_engine.py`) - Performs AI-powered essay grading
4. **Pipeline Integration** (`rubriCheck_pipeline.py`) - Orchestrates the complete workflow

---

## Module 1: Essay Preprocessor (`essay_preprocessor.py`)

### Purpose
The Essay Preprocessor prepares student essays for AI grading by performing language detection, text structuring, metadata extraction, and optional preprocessing tasks.

### Key Classes and Dataclasses

#### **Core Data Structures**

```python
@dataclass
class Section:
    """Represents a section of the essay with header and content."""
    header: str
    content: str
    start_char: int
    end_char: int

@dataclass  
class Paragraph:
    """Represents a paragraph with text and metadata."""
    text: str
    start_char: int
    end_char: int
    section_index: Optional[int] = None

@dataclass
class QuoteSpan:
    """Represents a quote within the essay."""
    text: str
    start_char: int
    end_char: int
    is_block_quote: bool = False

@dataclass
class Chunk:
    """Represents a chunk of text for processing."""
    paragraphs: List[Paragraph]
    start_char: int
    end_char: int

@dataclass
class Readability:
    """Readability metrics for the essay."""
    flesch_reading_ease: Optional[float] = None
    flesch_kincaid_grade: Optional[float] = None
    gunning_fog: Optional[float] = None
    automated_readability_index: Optional[float] = None
    coleman_liau_index: Optional[float] = None

@dataclass
class Metadata:
    """Comprehensive metadata about the processed essay."""
    language_detected: str
    translated: bool
    target_language: str
    word_count: int
    sentence_count: int
    char_count: int
    quote_char_ratio: float
    readability: Readability
    sections: List[Section]

@dataclass
class PIIItem:
    """Represents a PII item that was redacted."""
    kind: str
    original: str
    replacement: str
    char_start: int
    char_end: int

@dataclass
class ProcessedEssay:
    """Main output containing all processed essay data."""
    original_language: str
    language: str
    translated: bool
    pii_redacted: bool
    pii_map: List[PIIItem]
    metadata: Metadata
    paragraphs: List[Paragraph]
    chunks: List[Chunk]
    quotes: List[QuoteSpan]
    warnings: List[str]
```

#### **Core Classes**

```python
class LanguageDetector:
    """Detects the language of input text."""
    def detect(self, text: str) -> Optional[str]:
        """Detect language using multiple methods."""

class Translator:
    """Abstract base class for translation."""
    def translate(self, text: str, target_lang: str) -> Tuple[str, bool]:
        """Translate text to target language."""

class NoOpTranslator(Translator):
    """No-operation translator (default)."""

class PIIRedactor:
    """Redacts personally identifiable information."""
    def redact(self, text: str) -> Tuple[str, List[PIIItem]]:
        """Redact PII from text and return mapping."""

class StructureParser:
    """Parses essay structure into sections and paragraphs."""
    @staticmethod
    def split_paragraphs(text: str) -> List[Paragraph]:
        """Split text into paragraphs."""

class QuoteDetector:
    """Detects quotes within the essay."""
    @staticmethod
    def detect(text: str) -> List[QuoteSpan]:
        """Detect all quotes in the text."""

class Chunker:
    """Creates chunks for processing long essays."""
    def make_chunks(self, paragraphs: List[Paragraph]) -> List[Chunk]:
        """Create overlapping chunks from paragraphs."""

class MetadataExtractor:
    """Extracts comprehensive metadata from essays."""
    @staticmethod
    def word_count(text: str) -> int:
        """Count words in text."""
    
    @staticmethod
    def sentence_count(text: str) -> int:
        """Count sentences in text."""
    
    @staticmethod
    def readability(text: str) -> Readability:
        """Calculate readability metrics."""
    
    @staticmethod
    def sections(text: str) -> List[Section]:
        """Extract sections from text."""

class EssayPreprocessor:
    """Main preprocessor class that orchestrates all processing."""
    def __init__(self, translator: Optional[Translator] = None, pii_spacy: bool = True):
        """Initialize with optional translator and PII settings."""
    
    def run(self, text: str, opts: Optional[PreprocessOptions] = None) -> ProcessedEssay:
        """Main processing method that returns ProcessedEssay."""
```

### Workflow

1. **Language Detection**: Detects essay language using multiple methods
2. **Translation** (optional): Translates non-English essays to target language
3. **PII Redaction** (optional): Removes personally identifiable information
4. **Structure Parsing**: Identifies sections and paragraphs
5. **Quote Detection**: Finds and categorizes quotes
6. **Chunking**: Creates overlapping chunks for long essays
7. **Metadata Extraction**: Calculates word counts, readability, etc.
8. **Output Generation**: Returns structured `ProcessedEssay` object

### Features

- **Multi-language Support**: Automatic language detection and translation
- **PII Protection**: Optional redaction of personal information
- **Structure Analysis**: Section and paragraph identification
- **Quote Detection**: Inline and block quote identification
- **Readability Analysis**: Multiple readability metrics
- **Chunking**: Handles long essays with overlapping chunks
- **Metadata Extraction**: Comprehensive essay statistics

---

## Module 2: Rubric Parser (`rubric_parser_prompt.py`)

### Purpose
The Rubric Parser extracts and structures grading rubrics from various document formats using AI-powered parsing and validation.

### Key Classes and Dataclasses

#### **Core Data Structures**

```python
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
```

#### **Core Classes**

```python
class RubricParser:
    """Main rubric parser class with comprehensive parsing capabilities."""
    
    # JSON Schema for validation
    RUBRIC_JSON_SCHEMA: Dict[str, Any] = {
        # Comprehensive schema for rubric validation
    }
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """Initialize parser with OpenAI client."""
    
    def extract_text_from_file(self, path: str) -> Tuple[str, str]:
        """Extract text from supported file formats (TXT, DOCX)."""
    
    def _parse_rubric_with_llm(self, raw_text: str, method_hint: str = "narrative") -> Dict[str, Any]:
        """Parse rubric using OpenAI LLM with structured outputs."""
    
    def _validate_rubric(self, rubric: Dict[str, Any]) -> List[str]:
        """Validate rubric against JSON schema and perform semantic checks."""
    
    def parse_file(self, path: str) -> ParseResult:
        """Parse a rubric file and return structured result."""
    
    def parse_text(self, text: str, method_hint: str = "narrative") -> ParseResult:
        """Parse rubric from raw text."""
    
    def print_summary(self, result: ParseResult) -> None:
        """Print a formatted summary of the parsing result."""
    
    def get_criteria_count(self, result: ParseResult) -> int:
        """Get the number of criteria in the parsed rubric."""
    
    def get_scale_type(self, result: ParseResult) -> str:
        """Get the scale type of the parsed rubric."""
    
    def get_confidence(self, result: ParseResult) -> float:
        """Get the confidence score of the parsing result."""
    
    def is_successful(self, result: ParseResult) -> bool:
        """Check if parsing was successful."""
```

### Workflow

1. **File Reading**: Extracts text from DOCX and TXT files
2. **AI Parsing**: Uses OpenAI LLM to parse rubric structure
3. **Schema Validation**: Validates against comprehensive JSON schema
4. **Semantic Checks**: Performs additional validation rules
5. **Confidence Scoring**: Calculates parsing confidence
6. **Error Handling**: Provides detailed error messages and warnings
7. **Output Generation**: Returns structured rubric data

### Features

- **Multi-format Support**: DOCX, TXT file parsing
- **AI-Powered Parsing**: Uses OpenAI LLM for intelligent extraction
- **Schema Validation**: Comprehensive JSON schema validation
- **Confidence Scoring**: Parsing confidence assessment
- **Error Handling**: Detailed error reporting and warnings
- **Structured Output**: Standardized rubric format

### Supported Rubric Formats

- **Categorical Scales**: Excellent, Good, Fair, Poor
- **Numeric Scales**: Point-based scoring systems
- **Weighted Criteria**: Criteria with different importance weights
- **Multiple Descriptors**: Detailed level descriptions

---

## Module 3: Grading Engine (`grading_engine.py`)

### Purpose
The Grading Engine performs AI-powered essay grading using parsed rubrics and preprocessed essays, providing detailed feedback and scoring.

### Key Classes and Dataclasses

#### **Core Data Structures**

```python
@dataclass
class CriterionResult:
    """Result of grading a single criterion."""
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
    """Complete grading summary for an essay."""
    per_criterion: List[CriterionResult] = field(default_factory=list)
    numeric_score: Optional[float] = None
    letter: Optional[str] = None
    categorical_points: Optional[float] = None
    notes: Optional[str] = None
```

#### **Core Functions**

```python
def make_criterion_user_prompt(
    criterion: Dict[str, Any],
    processed_essay: ProcessedEssay,
    max_span_chars: int = 240
) -> str:
    """Create user prompt for grading a specific criterion."""

def evaluate_one_criterion(
    criterion: Dict[str, Any],
    processed_essay: ProcessedEssay,
    max_span_chars: int = 240
) -> CriterionResult:
    """Evaluate a single criterion against the essay."""

def grade_essay(
    rubric: Dict[str, Any],
    processed_essay: ProcessedEssay,
    max_span_chars: int = 240
) -> GradeSummary:
    """Main grading function that grades entire essay."""

def generate_essay_insights(processed_essay: ProcessedEssay) -> Dict[str, Any]:
    """Generate comprehensive insights about the essay."""

def convert_rubric_format(parsed_rubric: Dict[str, Any]) -> Dict[str, Any]:
    """Convert rubric from parser format to grading engine format."""

def parse_rubric_file(rubric_path: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
    """Parse a rubric file using the RubricParser."""

def grade_essay_with_rubric_file(
    rubric_path: str,
    processed_essay: ProcessedEssay,
    max_span_chars: int = 240,
    model: str = "gpt-4o-mini"
) -> GradeSummary:
    """Grade an essay using a rubric file."""

def complete_grading_workflow(
    rubric_path: str,
    essay_path: str,
    max_span_chars: int = 240,
    model: str = "gpt-4o-mini"
) -> Dict[str, Any]:
    """Complete grading workflow: parse rubric + preprocess essay + grade essay."""
```

### Workflow

1. **Rubric Processing**: Converts parsed rubric to grading format
2. **Criterion Evaluation**: Grades each criterion individually
3. **Evidence Extraction**: Identifies supporting evidence spans
4. **Consistency Checking**: Validates grading consistency
5. **Score Calculation**: Computes numeric and letter grades
6. **Insight Generation**: Creates comprehensive essay insights
7. **Result Compilation**: Assembles complete grading summary

### Features

- **AI-Powered Grading**: Uses OpenAI LLM for intelligent assessment
- **Evidence-Based**: Extracts specific evidence for each grade
- **Consistency Checking**: Validates grading consistency
- **Comprehensive Feedback**: Detailed justifications and suggestions
- **Multiple Scoring**: Numeric scores, letter grades, and categorical points
- **Essay Insights**: Additional analysis of essay quality

---

## Module 4: Pipeline Integration (`rubriCheck_pipeline.py`)

### Purpose
The Pipeline Integration module orchestrates the complete RubriCheck workflow, providing both command-line and programmatic interfaces.

### Key Classes

```python
class RubriCheckPipeline:
    """Main pipeline class that integrates all three modules."""
    
    def __init__(self, api_key_file: str = "../api.txt"):
        """Initialize pipeline with API key configuration."""
    
    def process_essay(self, essay_path: str, options: Optional[PreprocessOptions] = None) -> ProcessedEssay:
        """Process an essay file using the essay preprocessor."""
    
    def parse_rubric(self, rubric_path: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
        """Parse a rubric file using the rubric parser."""
    
    def grade_essay(self, rubric: Dict[str, Any], processed_essay: ProcessedEssay, max_span_chars: int = 240) -> GradeSummary:
        """Grade an essay using the grading engine."""
    
    def _convert_rubric_format(self, parsed_rubric: Dict[str, Any]) -> Dict[str, Any]:
        """Convert rubric format for grading engine."""
    
    def run_complete_pipeline(
        self,
        rubric_path: str,
        essay_path: str,
        essay_options: Optional[PreprocessOptions] = None,
        max_span_chars: int = 240,
        model: str = "gpt-4o-mini",
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run the complete pipeline from start to finish."""
```

### Workflow

1. **Essay Preprocessing**: Processes student essay
2. **Rubric Parsing**: Extracts and structures grading rubric
3. **AI Grading**: Performs comprehensive essay grading
4. **Result Compilation**: Assembles complete results
5. **Output Generation**: Saves results to file (optional)

### Features

- **Complete Integration**: Seamless workflow orchestration
- **Flexible Input**: Supports multiple file formats
- **Configurable Options**: Customizable preprocessing and grading
- **Result Export**: Optional JSON output saving
- **Error Handling**: Comprehensive error management
- **CLI Interface**: Command-line usage support

---

## Complete Workflow

### 1. Essay Preprocessing Phase

```
Raw Essay Text
    ↓
Language Detection
    ↓
Translation (optional)
    ↓
PII Redaction (optional)
    ↓
Structure Parsing (sections/paragraphs)
    ↓
Quote Detection
    ↓
Chunking (for long essays)
    ↓
Metadata Extraction
    ↓
ProcessedEssay Object
```

### 2. Rubric Parsing Phase

```
Rubric Document (DOCX/TXT)
    ↓
Text Extraction
    ↓
AI-Powered Parsing (OpenAI LLM)
    ↓
Schema Validation
    ↓
Semantic Validation
    ↓
Confidence Scoring
    ↓
Structured Rubric Data
```

### 3. Grading Phase

```
ProcessedEssay + Structured Rubric
    ↓
Criterion-by-Criterion Evaluation
    ↓
Evidence Extraction
    ↓
Consistency Checking
    ↓
Score Calculation
    ↓
Insight Generation
    ↓
GradeSummary Object
```

### 4. Integration Phase

```
All Results
    ↓
Result Compilation
    ↓
Metadata Assembly
    ↓
Output Formatting
    ↓
JSON Export (optional)
    ↓
Complete Results
```

---

## Usage Examples

### Command Line Interface

```bash
# Basic usage
python rubriCheck_pipeline.py --rubric rubric.docx --essay essay.txt

# With output file
python rubriCheck_pipeline.py --rubric rubric.pdf --essay essay.docx --output results.json

# Custom options
python rubriCheck_pipeline.py --rubric rubric.txt --essay essay.pdf --no-redact --chunk-size 4
```

### Programmatic Usage

```python
from rubriCheck_pipeline import RubriCheckPipeline, PreprocessOptions

# Initialize pipeline
pipeline = RubriCheckPipeline(api_key_file="../api.txt")

# Run complete workflow
results = pipeline.run_complete_pipeline(
    rubric_path="rubric.docx",
    essay_path="essay.txt",
    output_path="results.json"
)

# Access results
print(f"Score: {results['grading_results']['numeric_score']}")
print(f"Grade: {results['grading_results']['letter_grade']}")
```

### Step-by-Step Usage

```python
# Step 1: Process essay
processed_essay = pipeline.process_essay("essay.txt")

# Step 2: Parse rubric
rubric = pipeline.parse_rubric("rubric.docx")

# Step 3: Grade essay
grade_summary = pipeline.grade_essay(rubric, processed_essay)
```

---

## Output Format

The pipeline returns a comprehensive results dictionary:

```json
{
  "pipeline_info": {
    "rubric_file": "path/to/rubric.docx",
    "essay_file": "path/to/essay.txt",
    "timestamp": "2024-01-01T12:00:00",
    "version": "1.0"
  },
  "essay_metadata": {
    "word_count": 500,
    "sentence_count": 25,
    "language_detected": "en",
    "readability": {
      "flesch_reading_ease": 65.2,
      "flesch_kincaid_grade": 8.1
    },
    "quote_char_ratio": 0.15,
    "section_count": 3
  },
  "rubric_info": {
    "title": "Essay Writing Rubric",
    "scale_type": "categorical",
    "criteria_count": 6,
    "grading_config": {
      "numeric": true,
      "letter_bands": [...],
      "categorical_points_map": {...}
    }
  },
  "grading_results": {
    "per_criterion": [
      {
        "criterion_id": "thesis",
        "level": "Good",
        "justification": "Thesis is present but somewhat broad...",
        "evidence_spans": [
          {
            "text": "The main argument is that...",
            "start_char": 45,
            "end_char": 78
          }
        ],
        "actionable_suggestion": "Refine the thesis to be more specific...",
        "refuse": false
      }
    ],
    "numeric_score": 85.0,
    "letter_grade": "A",
    "categorical_points": 3.2
  },
  "essay_insights": {
    "length_assessment": {
      "level": "good",
      "message": "Essay has a good length for developing your arguments."
    },
    "readability_assessment": {
      "level": "standard",
      "message": "Essay has standard readability for academic writing."
    },
    "structure_assessment": {
      "level": "good",
      "message": "Essay shows good structural organization."
    },
    "quote_usage": {
      "level": "moderate",
      "message": "Essay has moderate quote usage. Good balance of original analysis and evidence."
    }
  },
  "flags": "Complete grading workflow finished successfully"
}
```

---

## Configuration Options

### Essay Preprocessing Options

```python
options = PreprocessOptions(
    target_language="en",           # Target language for translation
    translate_non_english=True,     # Enable/disable translation
    redact_pii=True,               # Enable/disable PII redaction
    chunk_max_paragraphs=6,        # Max paragraphs per chunk
    chunk_overlap_paragraphs=1     # Overlap between chunks
)
```

### Grading Options

- `max_span_chars`: Maximum characters for evidence spans (default: 240)
- `model`: OpenAI model to use (default: "gpt-4o-mini")

---

## Supported File Formats

### Rubric Files
- **DOCX**: Microsoft Word documents
- **TXT**: Plain text files
- **PDF**: Portable Document Format (limited support)

### Essay Files
- **TXT**: Plain text files
- **DOCX**: Microsoft Word documents
- **PDF**: Portable Document Format (limited support)

---

## Dependencies

### Required
```bash
pip install openai docx2txt jsonschema
```

### Optional (for enhanced functionality)
```bash
pip install langdetect fasttext textstat spacy
python -m spacy download en_core_web_sm
```

---

## Performance Considerations

### API Costs
- **Rubric Parsing**: ~1-2 API calls per rubric
- **Essay Grading**: ~2-3 calls per criterion
- **Consistency Checking**: ~1-2 additional calls
- **Total**: ~15-20 API calls per essay (6-criteria rubric)

### Processing Time
- **Essay Preprocessing**: 1-5 seconds (depending on length)
- **Rubric Parsing**: 2-10 seconds (depending on complexity)
- **Essay Grading**: 30-120 seconds (depending on criteria count)
- **Total**: 1-3 minutes per essay

### Memory Usage
- **Small Essays** (< 1000 words): ~50MB
- **Medium Essays** (1000-5000 words): ~100MB
- **Large Essays** (> 5000 words): ~200MB+

---

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all modules are in the same directory
2. **API Key Issues**: Verify API key in `../api.txt`
3. **File Format Issues**: Check supported formats
4. **Memory Issues**: Reduce chunk size for large essays
5. **Rate Limiting**: Implement delays between API calls

### Debug Mode

```bash
export RUBRICHECK_DEBUG=1
python rubriCheck_pipeline.py --rubric rubric.pdf --essay essay.txt
```

---

## License

This pipeline integrates the three RubriCheck modules. See individual module licenses for details.

---

## Author

RubriCheck - AI-Powered Essay Grading System