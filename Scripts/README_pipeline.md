# RubriCheck Complete Pipeline

This is an integrated Python pipeline that combines all three RubriCheck modules:

1. **Essay Preprocessor** (`essay_preprocessor.ipynb`) - Processes and structures student essays
2. **Rubric Parser** (`rubric_parser_prompt.ipynb`) - Extracts and parses rubric documents  
3. **Grading Engine** (`grading_engine.ipynb`) - Grades essays using AI against rubrics

## Files

- `rubriCheck_pipeline.py` - Main integrated pipeline
- `example_usage.py` - Example usage demonstrations
- `README_pipeline.md` - This documentation

## Prerequisites

Make sure you have all dependencies installed:

```bash
pip install openai fitz pdf2image pytesseract opencv-python pillow docx2txt jsonschema
```

## Setup

1. **API Key**: Place your OpenAI API key in `../api.txt`:
   ```
   rubriCheck: sk-your-api-key-here
   ```

2. **File Structure**: Ensure your files are organized as:
   ```
   Scripts/
   ├── rubriCheck_pipeline.py
   ├── example_usage.py
   ├── test_file/
   │   └── test_rubric.docx
   └── ../api.txt
   ```

## Usage

### Command Line Interface

```bash
# Basic usage
python rubriCheck_pipeline.py --rubric rubric.pdf --essay essay.txt

# Save results to file
python rubriCheck_pipeline.py --rubric rubric.docx --essay essay.pdf --output results.json

# Custom options
python rubriCheck_pipeline.py --rubric rubric.txt --essay essay.docx --no-redact --chunk-size 4
```

### Programmatic Usage

```python
from rubriCheck_pipeline import RubriCheckPipeline, PreprocessOptions

# Initialize pipeline
pipeline = RubriCheckPipeline(api_key_file="../api.txt")

# Run complete pipeline
results = pipeline.run_complete_pipeline(
    rubric_path="rubric.pdf",
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
rubric = pipeline.parse_rubric("rubric.pdf")

# Step 3: Grade essay
grade_summary = pipeline.grade_essay(rubric, processed_essay)
```

## Supported File Formats

### Rubric Files
- PDF (.pdf)
- Word documents (.docx)
- Text files (.txt)
- Images (.png, .jpg, .jpeg, .webp, .tif, .tiff, .bmp)

### Essay Files
- Text files (.txt)
- Word documents (.docx)
- PDF files (.pdf)
- Images (.png, .jpg, .jpeg, .webp, .tif, .tiff, .bmp)

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

- `max_span_chars`: Maximum characters for evidence quotes (default: 240)

## Output Format

The pipeline returns a comprehensive results dictionary:

```json
{
  "pipeline_info": {
    "rubric_file": "path/to/rubric.pdf",
    "essay_file": "path/to/essay.txt",
    "timestamp": "2024-01-01T12:00:00",
    "version": "1.0"
  },
  "essay_metadata": {
    "word_count": 500,
    "sentence_count": 25,
    "language_detected": "en",
    "readability": {...}
  },
  "rubric_info": {
    "title": "Essay Writing Rubric",
    "scale_type": "categorical",
    "criteria_count": 6
  },
  "grading_results": {
    "per_criterion": [
      {
        "criterion_id": "thesis",
        "level": "Good",
        "justification": "Thesis is present but...",
        "evidence_spans": [...],
        "actionable_suggestion": "Refine the thesis to..."
      }
    ],
    "numeric_score": 85.0,
    "letter_grade": "A",
    "reliability_flags": {...}
  },
  "warnings": []
}
```

## Examples

### Example 1: Basic Usage
```python
from rubriCheck_pipeline import RubriCheckPipeline

pipeline = RubriCheckPipeline()
results = pipeline.run_complete_pipeline(
    rubric_path="my_rubric.pdf",
    essay_path="student_essay.txt"
)
```

### Example 2: Custom Options
```python
from rubriCheck_pipeline import RubriCheckPipeline, PreprocessOptions

# Custom preprocessing
options = PreprocessOptions(
    redact_pii=False,  # Don't redact PII
    chunk_max_paragraphs=4  # Smaller chunks
)

pipeline = RubriCheckPipeline()
results = pipeline.run_complete_pipeline(
    rubric_path="rubric.docx",
    essay_path="essay.pdf",
    essay_options=options,
    output_path="detailed_results.json"
)
```

### Example 3: Step-by-Step Processing
```python
pipeline = RubriCheckPipeline()

# Process essay
essay = pipeline.process_essay("essay.txt")
print(f"Processed {essay.metadata.word_count} words")

# Parse rubric
rubric = pipeline.parse_rubric("rubric.pdf")
print(f"Found {len(rubric['criteria'])} criteria")

# Grade essay
grade = pipeline.grade_essay(rubric, essay)
print(f"Score: {grade.numeric_score} ({grade.letter})")
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all three notebook modules are in the same directory
2. **API Key Issues**: Check that your API key is correctly set in `../api.txt`
3. **File Not Found**: Verify file paths are correct and files exist
4. **Memory Issues**: For large essays, reduce `chunk_max_paragraphs`

### Debug Mode

Enable detailed logging by setting environment variable:
```bash
export RUBRICHECK_DEBUG=1
python rubriCheck_pipeline.py --rubric rubric.pdf --essay essay.txt
```

## Performance Tips

1. **Large Essays**: Use smaller chunk sizes for very long essays
2. **Multiple Essays**: Process essays in batches to manage API costs
3. **Caching**: Save processed essays to avoid reprocessing
4. **Parallel Processing**: Use multiprocessing for multiple essays

## API Costs

The pipeline makes multiple OpenAI API calls:
- 2-3 calls per criterion for grading
- 1 call for rubric parsing
- Additional calls for consistency checking

For a 6-criteria rubric, expect ~15-20 API calls per essay.

## License

This pipeline integrates the three RubriCheck modules. See individual module licenses for details.
