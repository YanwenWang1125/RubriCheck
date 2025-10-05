from __future__ import annotations

import json
import math
import re
import sys
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

#!/usr/bin/env python3
"""
RubriCheck Essay Preprocessor
---------------------------------
A modular Python pipeline to prepare student essays for rubric-based grading.

Features
- Language detection (with optional auto-translation hook)
- Optional PII minimization (redaction + reversible mapping)
- Section/paragraph parsing with stable indices
- Chunking with paragraph-level overlap for long essays
- Quote detection (inline & block) and quote ratio
- Metadata extraction (word/sentence counts, readability, section headers)
- Structured JSON-like output via dataclasses

Optional dependencies (auto-detected if installed):
    pip install langdetect fasttext textstat spacy
    python -m spacy download en_core_web_sm

Notes
- Translation is implemented via pluggable interface; default is NoOp.
- Readability prefers textstat when available; otherwise uses fallbacks.
- PII redaction uses regex for emails/phones and spaCy for PERSON/ORG when available.

Author: RubriCheck
"""

# ------------------------------
# Optional Dependency Detection
# ------------------------------
try:
    import langdetect
    HAS_LANGDETECT = True
except ImportError:
    HAS_LANGDETECT = False

try:
    import textstat
    HAS_TEXTSTAT = True
except ImportError:
    HAS_TEXTSTAT = False

try:
    import spacy
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False

# ------------------------------
# Data Classes
# ------------------------------

@dataclass
class Section:
    """A section of the essay with metadata."""
    title: str
    start_idx: int
    end_idx: int
    paragraphs: List[int]  # paragraph indices in this section

@dataclass
class Paragraph:
    """A paragraph with metadata."""
    text: str
    start_idx: int
    end_idx: int
    section_idx: int
    is_quote: bool = False
    quote_type: Optional[str] = None  # 'inline' or 'block'

@dataclass
class Quote:
    """A detected quote."""
    text: str
    start_idx: int
    end_idx: int
    quote_type: str  # 'inline' or 'block'
    paragraph_idx: int

@dataclass
class Chunk:
    """A chunk of text for processing."""
    text: str
    paragraph_indices: List[int]
    start_idx: int
    end_idx: int

@dataclass
class Readability:
    """Readability metrics."""
    flesch_reading_ease: Optional[float] = None
    flesch_kincaid_grade: Optional[float] = None
    gunning_fog: Optional[float] = None
    ari: Optional[float] = None
    coleman_liau: Optional[float] = None

@dataclass
class Metadata:
    """Essay metadata."""
    word_count: int
    sentence_count: int
    paragraph_count: int
    character_count: int
    language_detected: str
    readability: Readability
    quote_ratio: float
    section_count: int
    chunk_count: int

@dataclass
class PIIItem:
    """A PII item that was redacted."""
    original: str
    redacted: str
    pii_type: str
    start_idx: int
    end_idx: int

@dataclass
class ProcessedEssay:
    """The complete processed essay."""
    original_text: str
    processed_text: str
    sections: List[Section]
    paragraphs: List[Paragraph]
    quotes: List[Quote]
    chunks: List[Chunk]
    metadata: Metadata
    pii_items: List[PIIItem]
    warnings: List[str] = field(default_factory=list)

# ------------------------------
# Configuration Classes
# ------------------------------

@dataclass
class PreprocessOptions:
    """Options for essay preprocessing."""
    target_language: str = "en"
    translate_non_english: bool = True
    redact_pii: bool = True
    chunk_max_paragraphs: int = 6
    chunk_overlap_paragraphs: int = 1
    min_paragraph_length: int = 50
    max_paragraph_length: int = 2000

# ------------------------------
# Main Preprocessor Class
# ------------------------------

class EssayPreprocessor:
    """Main essay preprocessor class."""
    
    def __init__(self):
        self.nlp = None
        self._load_spacy_model()
    
    def _load_spacy_model(self):
        """Load spaCy model if available."""
        if HAS_SPACY:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("Warning: spaCy model 'en_core_web_sm' not found. PII detection will be limited.")
                self.nlp = None
    
    def run(self, text: str, options: PreprocessOptions) -> ProcessedEssay:
        """Run the complete preprocessing pipeline."""
        warnings = []
        
        # Step 1: Language detection
        language = self._detect_language(text)
        if language != options.target_language and options.translate_non_english:
            warnings.append(f"Essay is in {language}, translation not implemented yet")
        
        # Step 2: PII redaction
        if options.redact_pii:
            processed_text, pii_items = self._redact_pii(text)
        else:
            processed_text, pii_items = text, []
        
        # Step 3: Parse sections and paragraphs
        sections, paragraphs = self._parse_structure(processed_text)
        
        # Step 4: Detect quotes
        quotes = self._detect_quotes(paragraphs)
        
        # Step 5: Create chunks
        chunks = self._create_chunks(paragraphs, options)
        
        # Step 6: Calculate metadata
        metadata = self._calculate_metadata(
            processed_text, sections, paragraphs, quotes, chunks, language
        )
        
        return ProcessedEssay(
            original_text=text,
            processed_text=processed_text,
            sections=sections,
            paragraphs=paragraphs,
            quotes=quotes,
            chunks=chunks,
            metadata=metadata,
            pii_items=pii_items,
            warnings=warnings
        )
    
    def _detect_language(self, text: str) -> str:
        """Detect the language of the text."""
        if HAS_LANGDETECT:
            try:
                return langdetect.detect(text)
            except:
                pass
        
        # Fallback: simple heuristic
        if re.search(r'[а-яё]', text, re.IGNORECASE):
            return 'ru'
        elif re.search(r'[一-龯]', text):
            return 'zh'
        else:
            return 'en'
    
    def _redact_pii(self, text: str) -> Tuple[str, List[PIIItem]]:
        """Redact PII from text."""
        pii_items = []
        processed_text = text
        
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(email_pattern, text):
            original = match.group()
            redacted = f"[EMAIL_{len(pii_items)}]"
            pii_items.append(PIIItem(
                original=original,
                redacted=redacted,
                pii_type="email",
                start_idx=match.start(),
                end_idx=match.end()
            ))
            processed_text = processed_text.replace(original, redacted)
        
        # Phone numbers
        phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
        for match in re.finditer(phone_pattern, text):
            original = match.group()
            redacted = f"[PHONE_{len(pii_items)}]"
            pii_items.append(PIIItem(
                original=original,
                redacted=redacted,
                pii_type="phone",
                start_idx=match.start(),
                end_idx=match.end()
            ))
            processed_text = processed_text.replace(original, redacted)
        
        # Names using spaCy if available
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ["PERSON", "ORG"]:
                    original = ent.text
                    redacted = f"[{ent.label_}_{len(pii_items)}]"
                    pii_items.append(PIIItem(
                        original=original,
                        redacted=redacted,
                        pii_type=ent.label_.lower(),
                        start_idx=ent.start_char,
                        end_idx=ent.end_char
                    ))
                    processed_text = processed_text.replace(original, redacted)
        
        return processed_text, pii_items
    
    def _parse_structure(self, text: str) -> Tuple[List[Section], List[Paragraph]]:
        """Parse text into sections and paragraphs."""
        sections = []
        paragraphs = []
        
        # Simple section detection (lines that are all caps or start with numbers)
        lines = text.split('\n')
        current_section = None
        current_paragraph = ""
        paragraph_start = 0
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                if current_paragraph:
                    # End current paragraph
                    paragraphs.append(Paragraph(
                        text=current_paragraph.strip(),
                        start_idx=paragraph_start,
                        end_idx=paragraph_start + len(current_paragraph),
                        section_idx=len(sections) - 1 if sections else 0
                    ))
                    current_paragraph = ""
                continue
            
            # Check if this is a section header
            if (line.isupper() or 
                re.match(r'^\d+\.?\s+[A-Z]', line) or
                re.match(r'^[A-Z][a-z]+:', line)):
                
                # Save current section if exists
                if current_section:
                    sections.append(current_section)
                
                # Start new section
                current_section = Section(
                    title=line,
                    start_idx=text.find(line),
                    end_idx=text.find(line) + len(line),
                    paragraphs=[]
                )
                paragraph_start = text.find(line) + len(line)
            else:
                # Add to current paragraph
                if current_paragraph:
                    current_paragraph += " " + line
                else:
                    current_paragraph = line
                    paragraph_start = text.find(line)
        
        # Add final paragraph and section
        if current_paragraph:
            paragraphs.append(Paragraph(
                text=current_paragraph.strip(),
                start_idx=paragraph_start,
                end_idx=paragraph_start + len(current_paragraph),
                section_idx=len(sections) - 1 if sections else 0
            ))
        
        if current_section:
            sections.append(current_section)
        
        # Update section paragraph indices
        for i, paragraph in enumerate(paragraphs):
            if paragraph.section_idx < len(sections):
                sections[paragraph.section_idx].paragraphs.append(i)
        
        return sections, paragraphs
    
    def _detect_quotes(self, paragraphs: List[Paragraph]) -> List[Quote]:
        """Detect quotes in paragraphs."""
        quotes = []
        
        for i, paragraph in enumerate(paragraphs):
            text = paragraph.text
            
            # Block quotes (indented or starting with >)
            if text.startswith('>') or text.startswith('    '):
                quotes.append(Quote(
                    text=text,
                    start_idx=paragraph.start_idx,
                    end_idx=paragraph.end_idx,
                    quote_type="block",
                    paragraph_idx=i
                ))
                paragraph.is_quote = True
                paragraph.quote_type = "block"
            
            # Inline quotes (text within quotes)
            elif '"' in text:
                quote_pattern = r'"([^"]+)"'
                for match in re.finditer(quote_pattern, text):
                    quotes.append(Quote(
                        text=match.group(1),
                        start_idx=paragraph.start_idx + match.start(),
                        end_idx=paragraph.start_idx + match.end(),
                        quote_type="inline",
                        paragraph_idx=i
                    ))
        
        return quotes
    
    def _create_chunks(self, paragraphs: List[Paragraph], options: PreprocessOptions) -> List[Chunk]:
        """Create chunks from paragraphs."""
        chunks = []
        
        for i in range(0, len(paragraphs), options.chunk_max_paragraphs - options.chunk_overlap_paragraphs):
            chunk_paragraphs = paragraphs[i:i + options.chunk_max_paragraphs]
            if not chunk_paragraphs:
                break
            
            chunk_text = " ".join(p.text for p in chunk_paragraphs)
            chunks.append(Chunk(
                text=chunk_text,
                paragraph_indices=list(range(i, i + len(chunk_paragraphs))),
                start_idx=chunk_paragraphs[0].start_idx,
                end_idx=chunk_paragraphs[-1].end_idx
            ))
        
        return chunks
    
    def _calculate_metadata(self, text: str, sections: List[Section], 
                          paragraphs: List[Paragraph], quotes: List[Quote], 
                          chunks: List[Chunk], language: str) -> Metadata:
        """Calculate essay metadata."""
        # Basic counts
        word_count = len(text.split())
        sentence_count = len(re.findall(r'[.!?]+', text))
        paragraph_count = len(paragraphs)
        character_count = len(text)
        
        # Quote ratio
        quote_text_length = sum(len(q.text) for q in quotes)
        quote_ratio = quote_text_length / character_count if character_count > 0 else 0
        
        # Readability
        readability = self._calculate_readability(text)
        
        return Metadata(
            word_count=word_count,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            character_count=character_count,
            language_detected=language,
            readability=readability,
            quote_ratio=quote_ratio,
            section_count=len(sections),
            chunk_count=len(chunks)
        )
    
    def _calculate_readability(self, text: str) -> Readability:
        """Calculate readability metrics."""
        if HAS_TEXTSTAT:
            return Readability(
                flesch_reading_ease=textstat.flesch_reading_ease(text),
                flesch_kincaid_grade=textstat.flesch_kincaid_grade(text),
                gunning_fog=textstat.gunning_fog(text),
                ari=textstat.automated_readability_index(text),
                coleman_liau=textstat.coleman_liau_index(text)
            )
        else:
            # Simple fallback calculations
            sentences = len(re.findall(r'[.!?]+', text))
            words = len(text.split())
            syllables = sum(self._count_syllables(word) for word in text.split())
            
            if sentences > 0 and words > 0:
                avg_sentence_length = words / sentences
                avg_syllables_per_word = syllables / words
                
                # Simple Flesch Reading Ease
                flesch = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
                
                return Readability(
                    flesch_reading_ease=flesch,
                    flesch_kincaid_grade=0.39 * avg_sentence_length + 11.8 * avg_syllables_per_word - 15.59
                )
            else:
                return Readability()
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simple heuristic)."""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            if char in vowels:
                if not prev_was_vowel:
                    syllable_count += 1
                prev_was_vowel = True
            else:
                prev_was_vowel = False
        
        # Handle silent e
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)

# ------------------------------
# Example Usage
# ------------------------------

if __name__ == "__main__":
    # Example usage
    preprocessor = EssayPreprocessor()
    options = PreprocessOptions()
    
    sample_text = """
    Introduction
    
    This essay discusses the importance of renewable energy in modern society.
    
    "The future of energy lies in sustainable sources," according to recent studies.
    
    The main arguments are:
    1. Environmental benefits
    2. Economic advantages
    3. Energy independence
    
    Conclusion
    
    In conclusion, renewable energy is essential for a sustainable future.
    """
    
    result = preprocessor.run(sample_text, options)
    print(f"Processed essay with {len(result.paragraphs)} paragraphs")
    print(f"Word count: {result.metadata.word_count}")
    print(f"Language: {result.metadata.language_detected}")
