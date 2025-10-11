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
    from langdetect import detect as _ld_detect  # type: ignore
except Exception:
    _ld_detect = None

try:
    import fasttext  # type: ignore
    _FASTTEXT_MODEL = None
except Exception:
    fasttext = None
    _FASTTEXT_MODEL = None

try:
    import textstat  # type: ignore
except Exception:
    textstat = None

try:
    import spacy  # type: ignore
    _SPACY_NLP = None
except Exception:
    spacy = None
    _SPACY_NLP = None

# ------------------------------
# Data Models
# ------------------------------
@dataclass
class Section:
    title: str
    char_start: int
    char_end: int

@dataclass
class Paragraph:
    id: int
    char_start: int
    char_end: int
    text: str

@dataclass
class QuoteSpan:
    kind: str  # "inline" or "block"
    char_start: int
    char_end: int
    text: str

@dataclass
class Chunk:
    id: int
    paragraph_ids: List[int]
    char_start: int
    char_end: int
    text: str

@dataclass
class Readability:
    flesch_reading_ease: Optional[float] = None
    flesch_kincaid_grade: Optional[float] = None
    gunning_fog: Optional[float] = None
    automated_readability_index: Optional[float] = None
    coleman_liau_index: Optional[float] = None

@dataclass
class Metadata:
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
    kind: str
    original: str
    replacement: str
    char_start: int
    char_end: int

@dataclass
class ProcessedEssay:
    original_language: str
    language: str
    translated: bool
    pii_redacted: bool
    pii_map: List[PIIItem]
    metadata: Metadata
    paragraphs: List[Paragraph]
    chunks: List[Chunk]
    quotes: List[QuoteSpan]
    warnings: List[str] = field(default_factory=list)

    def to_json(self, indent: int = 2) -> str:
        def encode(obj: Any):
            if hasattr(obj, "__dict__"):
                return asdict(obj)
            if isinstance(obj, (set,)):
                return list(obj)
            raise TypeError(f"Type not serializable: {type(obj)}")
        return json.dumps(asdict(self), indent=indent, ensure_ascii=False)

# ------------------------------
# Utilities
# ------------------------------
_WORD_RE = re.compile(r"\b\w+\b", re.UNICODE)
_SENT_RE = re.compile(r"(?<!\w\.[a-z])(?<![A-Z][a-z]\.)(?<=\.|\?|!|\n)\s+")
# We will do a simpler sentence split to avoid heavy deps
_SIMPLE_SENT_RE = re.compile(r"[^.!?\n]+[.!?]?\n?", re.MULTILINE)

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}")
_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)

_INLINE_QUOTES_RE = re.compile(
    r"(\".*?\"|\"[^\"]{3,}?\"|\'.*?\'|\'[^\']{3,}?\')",
    re.DOTALL,
)
_BLOCKQUOTE_LINE_RE = re.compile(r"^\s{0,3}>\s?.+", re.MULTILINE)

_HEADER_PATTERNS = [
    re.compile(r"^\s*#{1,6}\s*(.+)$", re.MULTILINE),  # Markdown
    re.compile(r"^\s*(\d+(?:\.\d+)*)\s+(.{2,80})$", re.MULTILINE),  # 1. Intro
    re.compile(r"^\s*([A-Z][A-Z\s]{3,})$", re.MULTILINE),  # ALL CAPS LINES
]
_KNOWN_HEADERS = {
    "abstract", "introduction", "background", "literature review",
    "methods", "methodology", "results", "analysis", "discussion",
    "conclusion", "limitations", "future work", "references",
    "works cited", "acknowledgments",
}


def _simple_words(text: str) -> List[str]:
    return re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ']+", text)


def _count_sentences(text: str) -> int:
    sentences = [s.strip() for s in _SIMPLE_SENT_RE.findall(text) if s.strip()]
    return max(1, len(sentences))


def _count_syllables(word: str) -> int:
    # Very rough heuristic syllable counter for fallback readability
    word = word.lower()
    if not word:
        return 0
    vowels = "aeiouyà-öø-ÿ"
    count = 0
    prev_is_vowel = False
    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev_is_vowel:
            count += 1
        prev_is_vowel = is_vowel
    if word.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


def _safe_div(a: float, b: float) -> float:
    return a / b if b else 0.0

# ------------------------------
# Language Detection & Translation
# ------------------------------
class LanguageDetector:
    def __init__(self):
        self.fasttext_model = None
        if fasttext is not None:
            try:
                # You may load a lid.176.ftz model here if available.
                # self.fasttext_model = fasttext.load_model("lid.176.ftz")
                self.fasttext_model = None
            except Exception:
                self.fasttext_model = None

    def detect(self, text: str) -> str:
        # Prioritize langdetect if available as zero-setup
        if _ld_detect is not None:
            try:
                return _ld_detect(text)
            except Exception:
                pass
        # Fallback crude heuristic: assume English if mostly ASCII
        ascii_ratio = _safe_div(sum(1 for c in text if ord(c) < 128), max(1, len(text)))
        return "en" if ascii_ratio > 0.9 else "unknown"


class Translator:
    def translate(self, text: str, target_language: str) -> Tuple[str, bool]:
        """Return (translated_text, changed?). Override in subclasses."""
        return text, False


class NoOpTranslator(Translator):
    pass


class OpenAITranslator(Translator):
    """Stub for OpenAI translation—implement with your API client externally."""
    def __init__(self, client=None, model: str = "gpt-4o-mini"):
        self.client = client
        self.model = model

    def translate(self, text: str, target_language: str) -> Tuple[str, bool]:
        # Pseudocode:
        # resp = self.client.chat.completions.create(
        #     model=self.model,
        #     messages=[{"role":"system","content":f"Translate to {target_language}."},
        #               {"role":"user","content":text}],
        #     temperature=0
        # )
        # t = resp.choices[0].message.content
        # return t, (t.strip() != text.strip())
        return text, False

# ------------------------------
# PII Minimization
# ------------------------------
class PIIRedactor:
    def __init__(self, enable_spacy: bool = True):
        self.use_spacy = enable_spacy and (spacy is not None)
        self._nlp = None
        if self.use_spacy:
            global _SPACY_NLP
            if _SPACY_NLP is None:
                try:
                    _SPACY_NLP = spacy.load("en_core_web_sm")
                except Exception:
                    _SPACY_NLP = None
            self._nlp = _SPACY_NLP

    def _spacy_entities(self, text: str) -> List[Tuple[str, int, int, str]]:
        ents: List[Tuple[str, int, int, str]] = []
        if not self._nlp:
            return ents
        try:
            doc = self._nlp(text)
            for ent in doc.ents:
                if ent.label_ in {"PERSON", "ORG"}:
                    ents.append((ent.text, ent.start_char, ent.end_char, ent.label_))
        except Exception:
            pass
        return ents

    def redact(self, text: str) -> Tuple[str, List[PIIItem]]:
        mappings: List[PIIItem] = []
        # First pass: regex-based (emails, phones, URLs)
        def replace_with(tag: str):
            counter = {"n": 0}
            def _repl(m: re.Match) -> str:
                counter["n"] += 1
                placeholder = f"[REDACTED_{tag}_{counter['n']}]"
                mappings.append(PIIItem(tag.lower(), m.group(0), placeholder, m.start(), m.end()))
                return placeholder
            return _repl

        text = _EMAIL_RE.sub(replace_with("EMAIL"), text)
        text = _PHONE_RE.sub(replace_with("PHONE"), text)
        text = _URL_RE.sub(replace_with("URL"), text)

        # Second pass: spaCy named entities (PERSON/ORG) if available
        if self._nlp is not None:
            # We must map spans carefully after prior replacements; recompute indices by scanning
            ents = self._spacy_entities(text)
            # Replace from end to start to keep offsets valid
            ents_sorted = sorted(ents, key=lambda x: x[1], reverse=True)
            idx = 0
            for original, start, end, label in ents_sorted:
                idx += 1
                placeholder = f"[REDACTED_{label}_{idx}]"
                mappings.append(PIIItem(label.lower(), original, placeholder, start, end))
                text = text[:start] + placeholder + text[end:]
        return text, mappings

# ------------------------------
# Section & Paragraph Parsing
# ------------------------------
class StructureParser:
    @staticmethod
    def find_sections(text: str) -> List[Section]:
        found: List[Section] = []
        # Pattern-based headers
        for pat in _HEADER_PATTERNS:
            for m in pat.finditer(text):
                title = m.group(1).strip() if m.lastindex else m.group(0).strip()
                start = m.start()
                # Section end is unknown here; consumer can infer by next start
                found.append(Section(title=title, char_start=start, char_end=m.end()))
        # Known headings (case-insensitive) as standalone lines
        lines = text.splitlines(keepends=True)
        offset = 0
        for line in lines:
            clean = line.strip().lower()
            if clean in _KNOWN_HEADERS:
                found.append(Section(title=line.strip(), char_start=offset, char_end=offset + len(line)))
            offset += len(line)
        # Deduplicate by (start,end)
        uniq = {(s.char_start, s.char_end): s for s in found}
        return sorted(uniq.values(), key=lambda s: s.char_start)

    @staticmethod
    def split_paragraphs(text: str) -> List[Paragraph]:
        paras: List[Paragraph] = []
        # Split on blank lines (>=2 newlines) while preserving char spans
        parts = re.split(r"\n\s*\n+", text)
        cursor = 0
        pid = 0
        for part in parts:
            # Find this part in the original text starting at cursor
            idx = text.find(part, cursor)
            if idx == -1:
                idx = cursor
            para_text = part.strip("\n")
            char_start = idx
            char_end = idx + len(part)
            paras.append(Paragraph(id=pid, char_start=char_start, char_end=char_end, text=para_text))
            pid += 1
            cursor = char_end
        return paras

# ------------------------------
# Quote Detection
# ------------------------------
class QuoteDetector:
    @staticmethod
    def detect(text: str) -> List[QuoteSpan]:
        quotes: List[QuoteSpan] = []
        # Inline quotes
        for m in _INLINE_QUOTES_RE.finditer(text):
            quotes.append(QuoteSpan(kind="inline", char_start=m.start(), char_end=m.end(), text=m.group(0)))
        # Blockquotes (markdown-style)
        for m in _BLOCKQUOTE_LINE_RE.finditer(text):
            start = m.start()
            # Extend contiguous blockquote lines
            end = m.end()
            quotes.append(QuoteSpan(kind="block", char_start=start, char_end=end, text=m.group(0)))
        # Merge overlapping spans
        quotes = QuoteDetector._merge_overlaps(quotes)
        return quotes

    @staticmethod
    def _merge_overlaps(spans: List[QuoteSpan]) -> List[QuoteSpan]:
        if not spans:
            return spans
        spans = sorted(spans, key=lambda s: s.char_start)
        merged: List[QuoteSpan] = []
        cur = spans[0]
        for s in spans[1:]:
            if s.char_start <= cur.char_end:
                cur.char_end = max(cur.char_end, s.char_end)
                cur.text = ""  # omit merged text to save memory
                cur.kind = cur.kind if cur.kind == s.kind else "block"
            else:
                merged.append(cur)
                cur = s
        merged.append(cur)
        return merged

# ------------------------------
# Chunking
# ------------------------------
@dataclass
class ChunkingConfig:
    max_paragraphs: int = 6
    overlap_paragraphs: int = 1


class Chunker:
    def __init__(self, cfg: ChunkingConfig):
        self.cfg = cfg

    def make_chunks(self, paragraphs: List[Paragraph]) -> List[Chunk]:
        chunks: List[Chunk] = []
        if not paragraphs:
            return chunks
        i = 0
        cid = 0
        while i < len(paragraphs):
            start_i = i
            end_i = min(len(paragraphs), i + self.cfg.max_paragraphs)
            para_slice = paragraphs[start_i:end_i]
            text = "\n\n".join(p.text for p in para_slice)
            char_start = para_slice[0].char_start
            char_end = para_slice[-1].char_end
            chunks.append(
                Chunk(
                    id=cid,
                    paragraph_ids=[p.id for p in para_slice],
                    char_start=char_start,
                    char_end=char_end,
                    text=text,
                )
            )
            cid += 1
            if end_i >= len(paragraphs):
                break
            # Overlap by N paragraphs
            i = end_i - self.cfg.overlap_paragraphs
            if i <= start_i:  # ensure progress
                i = end_i
        return chunks

# ------------------------------
# Metadata Extraction
# ------------------------------
class MetadataExtractor:
    @staticmethod
    def word_count(text: str) -> int:
        return len(_simple_words(text))

    @staticmethod
    def sentence_count(text: str) -> int:
        return _count_sentences(text)

    @staticmethod
    def readability(text: str) -> Readability:
        if textstat is not None:
            try:
                return Readability(
                    flesch_reading_ease=textstat.flesch_reading_ease(text),
                    flesch_kincaid_grade=textstat.flesch_kincaid_grade(text),
                    gunning_fog=textstat.gunning_fog(text),
                    automated_readability_index=textstat.automated_readability_index(text),
                    coleman_liau_index=textstat.coleman_liau_index(text),
                )
            except Exception:
                pass
        # Fallbacks
        words = _simple_words(text)
        sentences = MetadataExtractor.sentence_count(text)
        chars = sum(len(w) for w in words)
        syllables = sum(_count_syllables(w) for w in words)
        # Basic formulas
        fre = 206.835 - 1.015 * _safe_div(len(words), sentences) - 84.6 * _safe_div(syllables, len(words))
        fk = 0.39 * _safe_div(len(words), sentences) + 11.8 * _safe_div(syllables, len(words)) - 15.59
        ari = 4.71 * _safe_div(chars, len(words)) + 0.5 * _safe_div(len(words), sentences) - 21.43
        cli = 0.0588 * (100 * _safe_div(chars, len(words))) - 0.296 * (100 * _safe_div(sentences, len(words))) - 15.8
        # Gunning Fog fallback
        complex_words = sum(1 for w in words if _count_syllables(w) >= 3)
        gf = 0.4 * (_safe_div(len(words), sentences) + 100 * _safe_div(complex_words, len(words)))
        return Readability(
            flesch_reading_ease=fre,
            flesch_kincaid_grade=fk,
            gunning_fog=gf,
            automated_readability_index=ari,
            coleman_liau_index=cli,
        )

    @staticmethod
    def sections(text: str) -> List[Section]:
        return StructureParser.find_sections(text)

    @staticmethod
    def quote_ratio(text: str, quotes: List[QuoteSpan]) -> float:
        if not text:
            return 0.0
        quoted_chars = sum(q.char_end - q.char_start for q in quotes)
        return _safe_div(quoted_chars, len(text))

# ------------------------------
# Options & Orchestrator
# ------------------------------
@dataclass
class PreprocessOptions:
    target_language: str = "en"
    translate_non_english: bool = True
    redact_pii: bool = True
    chunk_max_paragraphs: int = 6
    chunk_overlap_paragraphs: int = 1


class EssayPreprocessor:
    def __init__(self, translator: Optional[Translator] = None, pii_spacy: bool = True):
        self.lang_detector = LanguageDetector()
        self.translator = translator or NoOpTranslator()
        self.pii = PIIRedactor(enable_spacy=pii_spacy)

    def run(self, text: str, opts: Optional[PreprocessOptions] = None) -> ProcessedEssay:
        opts = opts or PreprocessOptions()
        warnings: List[str] = []

        # Language detection
        detected_lang = self.lang_detector.detect(text)
        working_text = text
        did_translate = False
        if opts.translate_non_english and detected_lang and detected_lang != opts.target_language and detected_lang != "unknown":
            try:
                working_text, did_translate = self.translator.translate(working_text, opts.target_language)
            except Exception as e:
                warnings.append(f"Translation failed: {e}")

        # PII Minimization (student-facing)
        pii_map: List[PIIItem] = []
        if opts.redact_pii:
            try:
                working_text, pii_map = self.pii.redact(working_text)
            except Exception as e:
                warnings.append(f"PII redaction failed: {e}")

        # Structure: sections + paragraphs
        sections = MetadataExtractor.sections(working_text)
        paragraphs = StructureParser.split_paragraphs(working_text)

        # Quote detection
        quotes = QuoteDetector.detect(working_text)

        # Chunking
        chunker = Chunker(ChunkingConfig(
            max_paragraphs=opts.chunk_max_paragraphs,
            overlap_paragraphs=opts.chunk_overlap_paragraphs,
        ))
        chunks = chunker.make_chunks(paragraphs)

        # Metadata
        wc = MetadataExtractor.word_count(working_text)
        sc = MetadataExtractor.sentence_count(working_text)
        cc = len(working_text)
        quote_ratio = MetadataExtractor.quote_ratio(working_text, quotes)
        readability = MetadataExtractor.readability(working_text)

        meta = Metadata(
            language_detected=detected_lang or "unknown",
            translated=did_translate,
            target_language=opts.target_language,
            word_count=wc,
            sentence_count=sc,
            char_count=cc,
            quote_char_ratio=quote_ratio,
            readability=readability,
            sections=sections,
        )

        processed = ProcessedEssay(
            original_language=detected_lang or "unknown",
            language=opts.target_language if did_translate else detected_lang or "unknown",
            translated=did_translate,
            pii_redacted=opts.redact_pii,
            pii_map=pii_map,
            metadata=meta,
            paragraphs=paragraphs,
            chunks=chunks,
            quotes=quotes,
            warnings=warnings,
        )
        return processed


# ------------------------------
# CLI / Demo
# ------------------------------

def _print_summary(proc: ProcessedEssay) -> None:
    print("== Metadata ==")
    print(f"Detected language: {proc.metadata.language_detected}")
    print(f"Translated: {proc.metadata.translated}")
    print(f"Word count: {proc.metadata.word_count}")
    print(f"Sentences: {proc.metadata.sentence_count}")
    print(f"Chars: {proc.metadata.char_count}")
    print(f"Quote ratio: {proc.metadata.quote_char_ratio:.3f}")
    print("Readability:")
    print(f"  Flesch Reading Ease: {proc.metadata.readability.flesch_reading_ease}")
    print(f"  Flesch-Kincaid Grade: {proc.metadata.readability.flesch_kincaid_grade}")

    print("\n== Sections ==")
    for s in proc.metadata.sections:
        print(f" - {s.title} [{s.char_start}:{s.char_end}]")

    print("\n== Paragraphs ==")
    for p in proc.paragraphs:
        print(f" #{p.id} [{p.char_start}:{p.char_end}] -> {p.text[:60]!r}")

    print("\n== Chunks ==")
    for c in proc.chunks:
        print(f" * Chunk {c.id} paras={c.paragraph_ids} [{c.char_start}:{c.char_end}] len={len(c.text)}")

    print("\n== Quotes ==")
    for q in proc.quotes:
        print(f" - {q.kind} [{q.char_start}:{q.char_end}] -> {q.text[:60]!r}")

    if proc.pii_redacted and proc.pii_map:
        print("\n== PII Map ==")
        for item in proc.pii_map[:10]:
            print(f" - {item.kind}: {item.original!r} -> {item.replacement}")

    if proc.warnings:
        print("\n== Warnings ==")
        for w in proc.warnings:
            print(" -", w)


# if __name__ == "__main__":
#     # Manual configuration - modify these parameters as needed
#     essay_file_path = None  # Set to file path if you want to load from file, otherwise None
#     enable_pii_redaction = True  # Set to False to disable PII redaction
#     enable_translation = True  # Set to False to disable translation
#     output_json = False  # Set to True to output JSON instead of summary
    
#     # Sample essay text for demonstration
#     DEMO_TEXT = """

# Moss, Howard (1922-1987)   Howard Moss was an important practitioner of formal verse in the mid-twentieth century. He also had an uncanny ability to envision—and thereby in his poems to transform—nature into the environment created by humanity, bringing it into the realm of civilization; he strove to formalize nature, in keeping with his view of what poetry should be. He once remarked, "What my poems are really about […] is the experience of hovering between the forms of nature and the forms of art" (Leiter 29). Moss set an example for his generation among poets who believed in explicit order, and for later poets who have identified themselves with NEW FORMALISM. He was also the poetry editor at The New Yorker magazine from 1950 until shortly before his death, a position that allowed him to orchestrate much of mainstream American writing.

# Moss was born and raised in New York City. In 1942, he won Poetry magazine's Janet Sewall David Award for his own poetry. His first book was published in 1946. He was inducted into the American Academy and Institute of Arts and Letters in 1968, and won the National Book Award for poetry for his Selected Poems in 1971. His New Selected Poems (1984) was awarded the Lenore Marshall / Nation Poetry Prize in 1986, a year when he received a fellowship from the Academy of American Poets.

# All of Moss's work possesses a subtle finish. His early and middle poems are end-rhymed and metered, his later work freer—but all of it has a striking regularity of meter and tone. The prevalent themes in Moss's work involve fundamental issues such as change in life, human relationships, loss, and death. He writes ably of "the difficulty of love, the decay of the body, the passing of time, and the inevitability of death," all set against "the inexhaustible beauty of the natural world," as Dana Gioia has observed (102). He is, in fact, a great elegist who can portray attachment and loss with stunning acuity through graphic simplicity and bitter irony.

# In "Elegy for My Sister" (1980) he painstakingly details his sister's fatal disease and her struggle to cope with it. Trying to rise from her bed, her leg breaks "simply by standing up"; her bones have been "[m]elted into a kind of eggshell sawdust" by chemotherapy. His metaphors go beyond physical distress to show the plight of the soul. And in "Elegy for My Father" (1954) intense pain, dying and separation are made vivid through paradox. His father, for example, is freed from life by his pain, a "double-dealing enemy."

# Moss's finely crafted verse is matched by his willingness to account for the peripatetic and otherwise insignificant details of living, making them at times monumental. In his work the truth peeks out through artifice.
# """

#     # Load text from file or use demo text
#     if essay_file_path:
#         print(f"Loading essay from file: {essay_file_path}")
#         try:
#             with open(essay_file_path, "r", encoding="utf-8") as f:
#                 text = f.read()
#         except FileNotFoundError:
#             print(f"Error: File '{essay_file_path}' not found. Using demo text instead.")
#             text = DEMO_TEXT
#         except Exception as e:
#             print(f"Error reading file: {e}. Using demo text instead.")
#             text = DEMO_TEXT
#     else:
#         print("Using demo text for processing...")
#         text = DEMO_TEXT

#     # Initialize preprocessor with NoOp translator (no actual translation)
#     preprocessor = EssayPreprocessor(translator=NoOpTranslator())
    
#     # Configure processing options
#     options = PreprocessOptions(
#         target_language="en",
#         translate_non_english=enable_translation,
#         redact_pii=enable_pii_redaction,
#         chunk_max_paragraphs=6,
#         chunk_overlap_paragraphs=1
#     )
    
#     print(f"Processing options:")
#     print(f"  - PII Redaction: {'Enabled' if enable_pii_redaction else 'Disabled'}")
#     print(f"  - Translation: {'Enabled' if enable_translation else 'Disabled'}")
#     print(f"  - Target Language: {options.target_language}")
#     print(f"  - Chunk Max Paragraphs: {options.chunk_max_paragraphs}")
#     print(f"  - Chunk Overlap: {options.chunk_overlap_paragraphs}")
#     print()

#     # Process the essay
#     try:
#         processed_essay = preprocessor.run(text, options)
        
#         # Output results
#         if output_json:
#             print("=== JSON OUTPUT ===")
#             print(processed_essay.to_json())
#         else:
#             print("=== PROCESSING SUMMARY ===")
#             _print_summary(processed_essay)
            
#     except Exception as e:
#         print(f"Error during processing: {e}")
#         import traceback
#         traceback.print_exc()