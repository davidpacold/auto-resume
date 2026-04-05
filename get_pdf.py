import os
from pathlib import Path

from playwright.sync_api import sync_playwright

# Fetch and normalise the base URL
URL = os.environ.get("RESUME_URL", "")
if not URL:
    raise ValueError("Environment variable 'RESUME_URL' is not set.")
if URL.startswith("http://"):
    URL = URL.replace("http://", "https://", 1)
elif not URL.startswith("https://"):
    URL = f"https://{URL}"
URL = URL.rstrip("/") + "/"

PDF_MARGIN = {"top": "10mm", "right": "10mm", "bottom": "10mm", "left": "10mm"}

# Injected before visual PDF capture:
# - Forces light mode
# - Hides UI-only elements using setProperty('important') to beat Bootstrap's !important
# - Forces two-column layout via targeted CSS — Playwright PDF renderer ignores
#   viewport width and renders at paper width (~816px), so Bootstrap's lg breakpoints
#   never fire; we override .resume-main / .resume-aside directly instead
PREPARE_VISUAL = """
    document.documentElement.classList.remove('dark');

    ['dark-mode-switch', 'd-print-none'].forEach(function(cls) {
        document.querySelectorAll('.' + cls).forEach(function(el) {
            el.style.setProperty('display', 'none', 'important');
        });
    });
    document.querySelectorAll('footer').forEach(function(el) {
        el.style.setProperty('display', 'none', 'important');
    });

    var style = document.createElement('style');
    style.textContent = [
        '.resume-main  { flex: 0 0 66.666% !important; max-width: 66.666% !important; width: 66.666% !important; }',
        '.resume-aside { flex: 0 0 33.333% !important; max-width: 33.333% !important; width: 33.333% !important; }',
        '.resume-title   { flex: 0 0 66.666% !important; max-width: 66.666% !important; }',
        '.resume-contact { flex: 0 0 33.333% !important; max-width: 33.333% !important; border-left: 1px solid rgba(0,0,0,0.08) !important; }',
        '.row { flex-wrap: nowrap !important; }',
    ].join('\\n');
    document.head.appendChild(style);
"""

# ATS capture — just light mode; the ATS template has no UI chrome to hide
PREPARE_ATS = """
    document.documentElement.classList.remove('dark');
"""


def render_pdf(browser, url, output_path, prepare_script, viewport_width=1440, screen_media=True):
    """Navigate to url and save a PDF to output_path."""
    page = browser.new_page(viewport={"width": viewport_width, "height": 900})
    if screen_media:
        page.emulate_media(media="screen")
    page.goto(url, wait_until="networkidle", timeout=60_000)
    page.wait_for_timeout(1500)  # Allow web fonts to finish rendering
    page.evaluate(prepare_script)
    page.pdf(
        path=str(output_path),
        format="Letter",
        margin=PDF_MARGIN,
        print_background=True,
    )
    page.close()
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    os.makedirs("static_pdf", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()

        # Visual PDF — desktop two-column layout at 1440 px
        render_pdf(
            browser,
            URL,
            Path("static_pdf") / "resume.letter.pdf",
            prepare_script=PREPARE_VISUAL,
            viewport_width=1440,
            screen_media=True,
        )

        # ATS PDF — plain single-column layout for HR / applicant tracking systems
        render_pdf(
            browser,
            f"{URL}ats/",
            Path("static_pdf") / "resume.ats.pdf",
            prepare_script=PREPARE_ATS,
            viewport_width=1200,
            screen_media=False,
        )

        browser.close()

    print("PDF generation complete.")
    print(f"  Visual : static_pdf/resume.letter.pdf")
    print(f"  ATS    : static_pdf/resume.ats.pdf")
