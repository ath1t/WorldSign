# WorldSign

An open-source, community-reviewed sign-language dictionary and learning website. Built as a static site for GitHub Pages.

## Features
- Language directory with Yangon and Mandalay sign-language research entries
- Search and language/category filters
- English and Burmese interface labels
- Accessible navigation, skip link, visible focus, reduced-motion support
- Contribution form that exports JSON locally
- Learning page that only uses approved entries
- JSON data model and Python validation
- GitHub Actions validation and Pages deployment

## Run locally
```bash
python3 -m http.server 8000
```
Open `http://localhost:8000`.

## Deploy to Vercel
1. Push this repository to GitHub, with the default branch named `main`.
2. In Vercel, choose **Add New → Project** and import the repository.
3. Set **Framework Preset** to **Other**.
4. Set **Root Directory** to `.` (repository root).
5. Leave **Build Command** empty; set **Output Directory** to `.`.
6. Deploy. Vercel will create Preview Deployments for branches/PRs and Production Deployments from `main`.

The repository includes `vercel.json` for clean URLs and basic response headers. GitHub Actions runs data validation; Vercel handles hosting and deployment.

## Add a sign
Add an entry to `data/signs/index.json` using `data/sign-template.json` as a starting point. Do not mark an entry `approved` until the language community review, source checks, media rights and signer consent are documented.

Validate:
```bash
python scripts/validate.py
```

## Data ethics
Sign languages are distinct natural languages and regional varieties must not be collapsed into a single universal system. Never invent a sign, infer meaning from a still image, or republish third-party media without permission. The website code licence does not grant rights to dictionary media or contributed linguistic content.
