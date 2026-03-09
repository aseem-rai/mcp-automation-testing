"""Ensure test-data/dummy_resume.pdf exists; create minimal PDF if missing.
   Also provide a resume PDF with real text (name, email, title, etc.) for profile parsing."""

from __future__ import annotations

from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_TEST_DATA_DIR = _PROJECT_ROOT / "test-data"
_DUMMY_PDF = _TEST_DATA_DIR / "dummy_resume.pdf"
_RESUME_WITH_DETAILS_PDF = _TEST_DATA_DIR / "software_engineer_resume.pdf"

# Minimal valid PDF 1.4 (single empty page)
_MINIMAL_PDF_BYTES = (
    b"%PDF-1.4\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
    b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000052 00000 n \n0000000101 00000 n \n"
    b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF"
)


_DUMMY_JD_PDF = _TEST_DATA_DIR / "dummy_jd.pdf"


def ensure_dummy_resume_pdf() -> Path:
    """Return path to test-data/dummy_resume.pdf; create minimal PDF if missing."""
    _TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not _DUMMY_PDF.exists():
        _DUMMY_PDF.write_bytes(_MINIMAL_PDF_BYTES)
    return _DUMMY_PDF


def ensure_resume_with_details_pdf() -> Path:
    """Return path to a resume PDF with name, email, title, phone, location, summary
    so the app can parse it and show details on the profile page."""
    _TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
    if _RESUME_WITH_DETAILS_PDF.exists():
        return _RESUME_WITH_DETAILS_PDF
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ImportError:
        return ensure_dummy_resume_pdf()

    c = canvas.Canvas(str(_RESUME_WITH_DETAILS_PDF), pagesize=letter)
    _, height = letter
    y = height - 72
    line_height = 18

    def line(text: str) -> None:
        nonlocal y
        c.setFont("Helvetica", 12)
        c.drawString(72, y, text)
        y -= line_height

    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, y, "John Doe")
    y -= line_height * 1.2

    line("Software Engineer")
    line("Email: johndoe.example@email.com")
    line("Phone: +1 (555) 123-4567")
    line("Location: San Francisco, CA")
    y -= line_height
    line("Summary:")
    c.setFont("Helvetica", 11)
    c.drawString(72, y, "Experienced software engineer with 5+ years in full-stack development.")
    y -= line_height
    c.drawString(72, y, "Skilled in Python, JavaScript, and cloud platforms. Strong problem solver.")
    y -= line_height * 1.5
    c.setFont("Helvetica", 12)
    line("Experience: Senior Developer at Tech Corp (2020-Present)")
    line("Education: BS Computer Science, State University")

    c.save()
    return _RESUME_WITH_DETAILS_PDF


def ensure_dummy_jd_pdf() -> Path:
    """Return path to test-data/dummy_jd.pdf; create minimal PDF if missing."""
    _TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not _DUMMY_JD_PDF.exists():
        _DUMMY_JD_PDF.write_bytes(_MINIMAL_PDF_BYTES)
    return _DUMMY_JD_PDF
