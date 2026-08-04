# backend/app/services/chunking.py
"""Medical-aware text chunking.

Splits clinical documents into semantically meaningful chunks by
detecting standard medical section headers (History, Assessment,
Plan, etc.) and falling back to paragraph-based splitting.
"""

import re
from typing import List, Optional, Tuple

# Common medical section headers (case-insensitive patterns)
_SECTION_PATTERNS = [
    r"^#{1,3}\s+",                          # Markdown headings
    r"^(chief complaint|cc)\s*[:.]",
    r"^(history of present illness|hpi)\s*[:.]",
    r"^(past medical history|pmh)\s*[:.]",
    r"^(medications?|current medications?)\s*[:.]",
    r"^(allergies)\s*[:.]",
    r"^(family history|fhx)\s*[:.]",
    r"^(social history|shx)\s*[:.]",
    r"^(review of systems|ros)\s*[:.]",
    r"^(physical exam(ination)?|pe)\s*[:.]",
    r"^(assessment( and plan)?|a/?p)\s*[:.]",
    r"^(plan)\s*[:.]",
    r"^(impression)\s*[:.]",
    r"^(diagnosis|diagnoses)\s*[:.]",
    r"^(lab(oratory)?\s*results?)\s*[:.]",
    r"^(imaging|radiology)\s*[:.]",
    r"^(procedure(s)?)\s*[:.]",
    r"^(discharge (summary|instructions?))\s*[:.]",
    r"^(follow[- ]?up)\s*[:.]",
    r"^(vital signs?|vitals)\s*[:.]",
]

_COMBINED_PATTERN = re.compile("|".join(f"({p})" for p in _SECTION_PATTERNS), re.IGNORECASE)

# Target chunk size in characters (roughly ~200 tokens)
MAX_CHUNK_CHARS = 1200
OVERLAP_CHARS = 150


def _detect_section_title(line: str) -> Optional[str]:
    """Return the section title if the line matches a medical header."""
    if _COMBINED_PATTERN.match(line.strip()):
        return line.strip().rstrip(":").strip()
    return None


def chunk_text(text: str) -> List[Tuple[str, Optional[str]]]:
    """Split text into (chunk_content, section_title) tuples.

    Strategy:
    1. Split on medical section headers first.
    2. If a section exceeds MAX_CHUNK_CHARS, sub-split by paragraphs.
    3. If a paragraph still exceeds, split by sentences with overlap.
    """
    if not text or not text.strip():
        return []

    lines = text.split("\n")
    sections: List[Tuple[Optional[str], List[str]]] = []
    current_title = None
    current_lines: List[str] = []

    for line in lines:
        title = _detect_section_title(line)
        if title:
            if current_lines:
                sections.append((current_title, current_lines))
            current_title = title
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_title, current_lines))

    # Now split sections that are too large
    chunks: List[Tuple[str, Optional[str]]] = []
    for title, sec_lines in sections:
        sec_text = "\n".join(sec_lines).strip()
        if not sec_text:
            continue
        if len(sec_text) <= MAX_CHUNK_CHARS:
            chunks.append((sec_text, title))
        else:
            # Sub-split by paragraphs
            paragraphs = re.split(r"\n\s*\n", sec_text)
            buffer = ""
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                if len(buffer) + len(para) + 2 <= MAX_CHUNK_CHARS:
                    buffer = f"{buffer}\n\n{para}" if buffer else para
                else:
                    if buffer:
                        chunks.append((buffer, title))
                    buffer = para
            if buffer:
                chunks.append((buffer, title))

    # Final pass: split any remaining oversized chunks by sentence
    final_chunks: List[Tuple[str, Optional[str]]] = []
    for content, title in chunks:
        if len(content) <= MAX_CHUNK_CHARS:
            final_chunks.append((content, title))
        else:
            sentences = re.split(r"(?<=[.!?])\s+", content)
            buf = ""
            for sent in sentences:
                if len(buf) + len(sent) + 1 <= MAX_CHUNK_CHARS:
                    buf = f"{buf} {sent}" if buf else sent
                else:
                    if buf:
                        final_chunks.append((buf.strip(), title))
                    buf = sent
            if buf:
                final_chunks.append((buf.strip(), title))

    return final_chunks
