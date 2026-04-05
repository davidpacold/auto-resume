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

# Strip dark mode and any UI-only elements before capture
PREPARE_PAGE = """
    document.documentElement.classList.remove('dark');
    document.querySelectorAll('.d-print-none, .dark-mode-switch')
        .forEach(function(el) { el.style.display = 'none'; });
"""


def render_pdf(browser, url, output_path, viewport_width=1440, screen_media=True):
    """Navigate to url and save a PDF to output_path."""
    page = browser.new_page(viewport={"width": viewport_width, "height": 900})
    if screen_media:
        page.emulate_media(media="screen")
    page.goto(url, wait_until="networkidle", timeout=60_000)
    page.wait_for_timeout(1500)  # Allow web fonts to finish rendering
    page.evaluate(PREPARE_PAGE)
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
            viewport_width=1440,
            screen_media=True,
        )

        # ATS PDF — plain single-column layout for HR / applicant tracking systems
        render_pdf(
            browser,
            f"{URL}ats/",
            Path("static_pdf") / "resume.ats.pdf",
            viewport_width=1200,
            screen_media=False,
        )

        browser.close()

    print("PDF generation complete.")
    print(f"  Visual : static_pdf/resume.letter.pdf")
    print(f"  ATS    : static_pdf/resume.ats.pdf")
