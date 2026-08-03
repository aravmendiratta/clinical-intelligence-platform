# backend/tests/test_chunking.py
"""Tests for the medical-aware text chunking service."""

from app.services.chunking import chunk_text


def test_empty_text():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_short_text_single_chunk():
    text = "Patient presented with mild headache."
    chunks = chunk_text(text)
    assert len(chunks) == 1
    assert "headache" in chunks[0][0]


def test_medical_section_splitting():
    text = """Chief Complaint: Chest pain for 2 days.

History of Present Illness: Patient is a 55-year-old male who presents with
substernal chest pain radiating to the left arm. Pain started 2 days ago.

Medications: Aspirin 81mg daily, Lisinopril 10mg daily.

Assessment and Plan: Rule out acute coronary syndrome.
Order troponin, EKG, chest X-ray. Start heparin drip.
"""
    chunks = chunk_text(text)
    assert len(chunks) >= 3  # Should split on section headers
    # Check that section titles are detected
    titles = [title for _, title in chunks if title]
    assert any("Chief Complaint" in t for t in titles)


def test_large_text_gets_split():
    # Create a text larger than MAX_CHUNK_CHARS
    large_text = "This is a test sentence. " * 200
    chunks = chunk_text(large_text)
    assert len(chunks) > 1
    for content, _ in chunks:
        assert len(content) <= 1500  # some tolerance
