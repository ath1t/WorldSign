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

## Deploy
1. Push this repository to GitHub, with the default branch named `main`.
2. Open **Settings → Pages** and choose **GitHub Actions**.
3. Push to `main`; the workflow validates the data and deploys the site.

## Add a sign
Add an entry to `data/signs/index.json` using `data/sign-template.json` as a starting point. Do not mark an entry `approved` until the language community review, source checks, media rights and signer consent are documented.

Validate:
```bash
python scripts/validate.py
```

## Data ethics
Sign languages are distinct natural languages and regional varieties must not be collapsed into a single universal system. Never invent a sign, infer meaning from a still image, or republish third-party media without permission. The website code licence does not grant rights to dictionary media or contributed linguistic content.
