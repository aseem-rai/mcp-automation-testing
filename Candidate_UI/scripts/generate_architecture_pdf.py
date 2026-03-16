from __future__ import annotations

from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "reports" / "cursor_mcp_playwright_test_architecture.pdf"


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="SmallMuted",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#555555"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            spaceBefore=8,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            spaceAfter=4,
        )
    )
    return styles


def bullet(text: str, styles) -> Paragraph:
    return Paragraph(f"• {text}", styles["Body"])


def build_pdf() -> Path:
    styles = make_styles()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=A4,
        rightMargin=1.6 * cm,
        leftMargin=1.6 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.6 * cm,
        title="Cursor MCP + Playwright Architecture",
    )

    story = []
    story.append(Paragraph("Cursor MCP + Playwright Test Architecture", styles["Title"]))
    story.append(
        Paragraph(
            "Project: D:/playwright-mcp<br/>"
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles["SmallMuted"],
        )
    )
    story.append(Spacer(1, 8))

    story.append(Paragraph("1) High-Level Architecture", styles["SectionTitle"]))
    story.append(bullet("User works in Cursor IDE and triggers test actions.", styles))
    story.append(
        bullet(
            "Cursor can use MCP tool servers. In this workspace the key servers are "
            "<b>user-playwright</b> and <b>cursor-ide-browser</b>.",
            styles,
        )
    )
    story.append(bullet("This repository executes UI tests using Playwright + pytest.", styles))
    story.append(
        bullet("Test artifacts are produced under <b>test-results/</b> (report, logs, screenshots).", styles)
    )

    story.append(Spacer(1, 6))
    story.append(Paragraph("2) Playwright Framework Architecture", styles["SectionTitle"]))
    story.append(bullet("Primary config and lifecycle hooks are in <b>conftest.py</b>.", styles))
    story.append(
        bullet(
            "Fixture hierarchy: session-scoped <b>playwright_instance</b>/<b>browser</b>, then per-test "
            "<b>context</b> and <b>page</b>.",
            styles,
        )
    )
    story.append(
        bullet(
            "Autouse fixture <b>ensure_google_sign_in</b> validates login via saved auth state and redirects to dashboard when needed.",
            styles,
        )
    )
    story.append(
        bullet("Page Object Model under <b>framework/pages</b> encapsulates selectors and actions.", styles)
    )
    story.append(
        bullet("Run options: base URL, browser, headed/headless, slowmo, mocks, auth toggles.", styles)
    )

    story.append(Spacer(1, 6))
    story.append(Paragraph("3) Test Case Coverage (Current)", styles["SectionTitle"]))
    module_rows = [
        ["Module", "File", "Cases"],
        ["Login", "tests/test_login.py", "1"],
        ["Dashboard", "tests/test_dashboard.py", "14"],
        ["Jobs", "tests/test_jobs.py", "12"],
        ["Resume", "tests/test_resume.py", "7"],
        ["Profile", "tests/test_profile.py", "4"],
        ["Preps", "tests/test_preps.py", "5"],
        ["Prep JD Flow", "tests/preps/test_create_prep_jd.py", "1"],
        ["Total", "-", "44"],
    ]
    module_table = Table(module_rows, colWidths=[4.2 * cm, 8.8 * cm, 2.4 * cm])
    module_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e78")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (2, 1), (2, -1), "CENTER"),
                ("BACKGROUND", (0, 1), (-1, -2), colors.HexColor("#f7f9fc")),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#d9ead3")),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ]
        )
    )
    story.append(module_table)

    story.append(Spacer(1, 8))
    marker_rows = [
        ["Marker", "Purpose"],
        ["smoke", "Quick stability checks"],
        ["regression", "Wider regression coverage"],
        ["dashboard/jobs/resume/profile/prep/login", "Module-specific execution"],
        ["sanity/negative/upload", "Specialized execution groups"],
    ]
    marker_table = Table(marker_rows, colWidths=[4.5 * cm, 10.9 * cm])
    marker_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3d85c6")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f7f9fc")),
            ]
        )
    )
    story.append(marker_table)

    story.append(Spacer(1, 6))
    story.append(Paragraph("4) How Test Execution Runs", styles["SectionTitle"]))
    flow = [
        "1. Command starts (example: pytest tests/test_dashboard.py -q).",
        "2. Pytest loads options from pytest.ini and custom options from conftest.py.",
        "3. Session fixtures start Playwright and launch browser.",
        "4. For each test: create context/page, navigate to base URL, run login guard if enabled.",
        "5. Test calls Page Object methods to perform UI actions and assertions.",
        "6. Hooks capture logs, screenshots, and metadata into HTML report details.",
        "7. Context closes after each test; browser closes at session end.",
    ]
    for step in flow:
        story.append(Paragraph(step, styles["Body"]))

    story.append(Spacer(1, 6))
    story.append(Paragraph("5) Common Run Commands", styles["SectionTitle"]))
    story.append(Paragraph("• pytest", styles["Body"]))
    story.append(Paragraph("• pytest -m smoke", styles["Body"]))
    story.append(Paragraph("• pytest tests/test_dashboard.py -q", styles["Body"]))
    story.append(Paragraph("• pytest --headed --browser=chromium --base-url=https://example.com", styles["Body"]))
    story.append(Paragraph("• python run_tests.py --suite all", styles["Body"]))

    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            "Notes: Content is generated from this repository structure and current pytest/playwright configuration.",
            styles["SmallMuted"],
        )
    )

    doc.build(story)
    return OUTPUT_PATH


if __name__ == "__main__":
    path = build_pdf()
    print(f"PDF generated: {path}")
