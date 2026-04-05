# auto-resume

A Hugo-based resume/CV site for David Pacold, hosted on Cloudflare Pages with automated PDF generation via GitHub Actions.

**Live site:** https://resume.davidpacold.dev

## Architecture

- **Static site generator:** Hugo 0.154.5 (extended, for SCSS processing)
- **Hosting:** Cloudflare Pages
- **CI/CD:** GitHub Actions
- **PDF generation:** Playwright headless Chromium (`get_pdf.py`) — generates two PDFs from the deployed preview URL
- **Styling:** Bootstrap 5 + custom SCSS (`assets/scss/devresume.scss`)
- **Fonts:** IBM Plex Sans (all weights including 700 for the name heading)
- **Theme colors:** Primary `#291e95` (dark purple), Accent `#E8A000` (amber)

## Resume Content

All resume content lives in `config.toml` under `[params]`. Edit that file to update:
- Contact info, social links
- Summary, skills, experience, education, awards, talks, projects

Profile photo is at `static/assets/images/david-pacold-2.jpg`.

## PDF Outputs

Two PDFs are generated on every push and committed to `static/pdf/`:

| File | URL | Purpose |
|------|-----|---------|
| `resume.letter.pdf` | `/pdf/resume.letter.pdf` | Visual two-column layout for humans |
| `resume.ats.pdf` | `/pdf/resume.ats.pdf` | Plain single-column for ATS/HR tools |

The ATS PDF uses a separate Hugo template at `/ats/` (`layouts/ats/single.html`) — system fonts, no decorations, Skills before Experience.

## Workflows

### `preview_branch_action.yml`
Triggers on **push to any non-main branch** (and `workflow_dispatch`). Does NOT trigger on `pull_request` — prevents double-runs when pushing to a branch with an open PR.

Flow:
1. Builds the Hugo site
2. Waits for Cloudflare Pages to deploy the preview (polls CF API, 30 retries × 10s)
3. Generates both PDFs from the preview URL via Playwright (`get_pdf.py`)
4. Commits PDFs back to the branch (`static/pdf/*.pdf`)

When the PR is merged, the PDFs committed on the branch are included in the merge automatically.

### `regenerate-pdfs-main.yml`
Triggers on **push to main** (including PR merges) and `workflow_dispatch`.

Flow: same as above but uses the production URL `https://resume.davidpacold.dev`.

### Bot-commit loop prevention
Both workflows check `if: github.actor != 'github-actions[bot]'` to skip re-triggering when the bot commits PDFs back to the branch.

## Local Development

### Prerequisites
- Hugo extended 0.154.5+ **OR** Docker (preferred on Apple Silicon)
- Python 3.10+ with Playwright (for local PDF generation)

### Option A — Hugo installed locally
```bash
hugo server              # live reload at http://localhost:1313
hugo server -D           # include draft content
hugo --minify            # production build → public/
```

### Option B — Docker (Apple Silicon / no local Hugo)
Use `hugomods/hugo:exts` (multi-arch). **Do NOT use `klakegg/hugo`** — it is amd64-only and will crash on Apple Silicon.

```bash
# Live dev server with hot reload
docker run --rm -it \
  -v "$(pwd)":/src \
  -p 1313:1313 \
  hugomods/hugo:exts \
  hugo server --bind 0.0.0.0

# Then open: http://localhost:1313
```

```bash
# One-off production build (output in public/)
docker run --rm \
  -v "$(pwd)":/src \
  hugomods/hugo:exts \
  hugo --minify
```

### Previewing a branch locally
```bash
git checkout <branch-name>
git pull

# Then run either Hugo option above.
# The site reflects whatever is in config.toml and layouts/ on that branch.
```

### PDF generation locally
Requires Python 3.10+ and Playwright (one-time setup):
```bash
pip install playwright==1.51.0
playwright install chromium
```

Generate PDFs against the live prod site:
```bash
RESUME_URL=https://resume.davidpacold.dev python get_pdf.py
```

Generate PDFs against a local dev server (start `hugo server` first):
```bash
RESUME_URL=http://localhost:1313 python get_pdf.py
```

PDFs are written to `static_pdf/` (not `static/pdf/`). Copy them manually if you want to commit:
```bash
cp static_pdf/*.pdf static/pdf/
```

## Key Files

| File | Purpose |
|------|---------|
| `config.toml` | All resume content and site config |
| `assets/scss/devresume.scss` | All custom styles (dark mode, typography, layout) |
| `assets/js/darkmode.js` | Dark mode toggle with OS preference detection |
| `layouts/partials/` | Hugo partials (header, footer, sections) |
| `layouts/ats/single.html` | Standalone ATS-optimised resume template at `/ats/` |
| `get_pdf.py` | PDF generation script using Playwright |
| `static/assets/images/` | Profile photo and OG image |
| `static/pdf/` | Generated PDFs (committed by CI) |

## GitHub Actions Secrets Required

- `CLOUDFLARE_API_TOKEN` — for polling CF Pages deployment status
- `CLOUDFLARE_ACCOUNT_ID`

## Coding Standards

- Hugo templates: use `hugo.IsServer` (not `.Site.IsServer`, deprecated)
- Google Analytics: use `site.Config.Services.GoogleAnalytics.ID` block in config.toml (not `.Site.GoogleAnalytics`, removed in Hugo 0.125+)
- External links in templates: always include `rel="noopener noreferrer"`
- SCSS: all theme colors defined as variables at the top of `devresume.scss`
