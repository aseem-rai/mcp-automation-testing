"""Generate minimal valid PDFs for Playwright upload testing. No external deps."""
from pathlib import Path


def _escape_pdf_string(s: str) -> str:
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def make_pdf(lines: list[str], out_path: Path) -> None:
    # Build content stream: show each line with Tj and move down.
    content = "BT /F1 12 Tf 72 720 Td\n"
    for i, line in enumerate(lines):
        if i:
            content += " 0 -14 Td\n"
        content += f" ({_escape_pdf_string(line)}) Tj\n"
    content += " ET"
    content_len = len(content)

    obj1 = "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    obj2 = "2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
    obj3 = (
        "3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        "/Contents 4 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>\nendobj\n"
    )
    obj4 = f"4 0 obj\n<< /Length {content_len} >>\nstream\n{content}\nendstream\nendobj\n"
    body = "%PDF-1.4\n" + obj1 + obj2 + obj3 + obj4
    offsets = [
        body.find("1 0 obj"),
        body.find("2 0 obj"),
        body.find("3 0 obj"),
        body.find("4 0 obj"),
    ]
    xref = "xref\n0 5\n0000000000 65535 f \n"
    for o in offsets:
        xref += f"{o:010d} 00000 n \n"
    xref_body = xref + "\n"
    trailer = f"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n{len(body) + len(xref_body)}\n%%EOF\n"
    pdf = body + xref_body + trailer
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(pdf.encode("latin-1"))


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    test_data = root / "test_data"
    test_data.mkdir(parents=True, exist_ok=True)

    make_pdf(
        [
            "Name: Test User",
            "Role: AI Engineer",
            "Skills: Python, NLP",
        ],
        test_data / "test_resume.pdf",
    )
    make_pdf(
        [
            "Role: AI Engineer",
            "Skills: Python, Machine Learning, NLP",
            "Experience: 1 year",
            "Location: Bangalore",
        ],
        test_data / "test_jd.pdf",
    )
    print("Created test_data/test_resume.pdf and test_data/test_jd.pdf")


if __name__ == "__main__":
    main()
