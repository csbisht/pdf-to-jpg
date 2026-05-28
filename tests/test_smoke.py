"""
Smoke tests for pdf-to-jpg.

Creates a minimal 1-page PDF using pypdfium2, converts it,
and asserts the expected output file(s) exist.
"""

import pytest
import pypdfium2 as pdfium
from pathlib import Path

from pdf_to_jpg import pdf_to_jpg, batch_convert


# ---------------------------------------------------------------------------
# Fixture — tiny 1-page PDF
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_pdf(tmp_path) -> Path:
    """Create a minimal valid 1-page PDF for testing."""
    pdf_path = tmp_path / "sample.pdf"
    doc = pdfium.PdfDocument.new()
    doc.new_page(width=72, height=72)   # 1-inch × 1-inch page
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_combined_mode(sample_pdf, tmp_path):
    """Default mode: all pages combined into one JPG."""
    out = tmp_path / "out"
    pdf_to_jpg(str(sample_pdf), str(out))
    assert (out / "sample.jpg").exists(), "Combined JPG not created"


def test_per_page_mode(sample_pdf, tmp_path):
    """Per-page mode: one JPG per page."""
    out = tmp_path / "out"
    pdf_to_jpg(str(sample_pdf), str(out), per_page=True)
    assert (out / "sample_1.jpg").exists(), "Per-page JPG not created"


def test_custom_name(sample_pdf, tmp_path):
    """Custom output name is respected."""
    out = tmp_path / "out"
    pdf_to_jpg(str(sample_pdf), str(out), output_name="invoice")
    assert (out / "invoice.jpg").exists(), "Custom-named JPG not created"


def test_missing_pdf_raises(tmp_path):
    """FileNotFoundError is raised for a non-existent PDF."""
    with pytest.raises(FileNotFoundError):
        pdf_to_jpg(str(tmp_path / "does_not_exist.pdf"), str(tmp_path / "out"))


def test_batch_mode(tmp_path):
    """Batch mode converts all PDFs in a folder."""
    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()
    for name in ("a.pdf", "b.pdf"):
        doc = pdfium.PdfDocument.new()
        doc.new_page(width=72, height=72)
        doc.save(str(pdf_dir / name))
        doc.close()

    out = tmp_path / "out"
    batch_convert(str(pdf_dir), str(out))

    assert (out / "a" / "a.jpg").exists(), "Batch: a.jpg not created"
    assert (out / "b" / "b.jpg").exists(), "Batch: b.jpg not created"
