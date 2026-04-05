# auto-resume

An automated resume site that generates a PDF on every change.

Built with Hugo, deployed on Cloudflare Pages, with PDF generation via PDF.co and GitHub Actions.

## Live site

[resume.davidpacold.dev](https://resume.davidpacold.dev)

## How it works

1. Edit `config.toml` with your resume content
2. Push to a branch — GitHub Actions builds the site, waits for Cloudflare Pages to deploy a preview, generates a PDF, and commits it back to the branch
3. Merge to `main` — Cloudflare Pages deploys to production, GitHub Actions regenerates the PDF against the live URL and commits it

## Setup requirements

- [Cloudflare Pages](https://pages.cloudflare.com) account (free)
- [PDF.co](https://pdf.co) account (free credits available)
- A custom domain (optional)

## GitHub Actions secrets required

| Secret | Description |
|--------|-------------|
| `PDFCO_KEY` | PDF.co API key |
| `CLOUDFLARE_API_TOKEN` | Cloudflare API token with Pages edit permissions |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare account ID |

## Cloudflare Pages environment variables

Set `HUGO_VERSION` to match the version in the workflow files (currently `0.154.5`).

## Credits

- [Xiaoying Riley](https://themes.3rdwavemedia.com) for the DevResume Bootstrap theme
- [Cowboysmall](https://github.com/cowboysmall-tools/hugo-devresume-theme) for the Hugo port
- [Bas Steins](https://bas.codes/posts/github-actions-resume) for the original automation concept
- [Hugo](https://github.com/gohugoio/hugo) for static site generation
- [PDF.co](https://pdf.co) for PDF generation
- [GitHub Actions](https://github.com/features/actions) for CI/CD
