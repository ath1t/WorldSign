# WorldSign

An open-source, community-reviewed sign-language dictionary and learning website. Built as a static site for Vercel.

## Features
- Language directory with Myanmar sign-language research targets and international language entries
- Public research catalogue documenting external datasets, reported sizes, licences and reuse restrictions
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

## Data sources and rights

`data/sources.json` contains source-level metadata and links for MSL4Emergency, Asian SignBank, ASL-LEX 2.0 and BSL SignBank. These are references, not imported dictionary entries. Reported source counts must not be presented as WorldSign entries. MSL4Emergency is listed as CC BY-NC-SA 4.0 (non-commercial, attribution and ShareAlike); Asian SignBank reuse requires separate permission; ASL-LEX is listed as CC BY-NC 4.0 in the dataset compendium, with media rights to be checked separately; BSL SignBank prohibits scraping and bulk redistribution.

The current approved sign dataset remains empty. Do not manufacture signs or copy third-party videos/images. Add only content with documented provenance, signer consent and compatible reuse rights.

## Add a sign
Add an entry to `data/signs/index.json` using `data/sign-template.json` as a starting point. Do not mark an entry `approved` until the language community review, source checks, media rights and signer consent are documented.

Validate:
```bash
python scripts/validate.py
```

## Data ethics
Sign languages are distinct natural languages and regional varieties must not be collapsed into a single universal system. Never invent a sign, infer meaning from a still image, or republish third-party media without permission. The website code licence does not grant rights to dictionary media or contributed linguistic content.


## Imported dictionary content

The current dictionary includes 15 phrase-level Myanmar Sign Language examples transcribed in the MSL4Emergency project README. Each record preserves the Burmese source phrase and the corpus sign-language transcription separately. These are source-documented examples, not verified isolated lexical signs, and remain pending review by Myanmar Deaf community reviewers. No video has been arbitrarily assigned to an individual phrase. The source corpus is licensed CC BY-NC-SA 4.0; respect its attribution, non-commercial and share-alike requirements.

Source: https://github.com/ye-kyaw-thu/MSL4Emergency
Sample video playlist: https://www.youtube.com/playlist?list=PLcEIKqU2ZkWKe0aGzGoKH5OtdjSHF3L_f


## Text-only dictionary data imports

WorldSign includes a text-only importer for public sign-language lexical resources. It does not download or mirror sign videos, images, ELAN/PFSX files, or other media.

Run locally:

```bash
python scripts/import_public_datasets.py
python scripts/validate.py
```

Or run **Actions → Import public sign dictionary text data → Run workflow** in GitHub. A monthly refresh is also configured. The importer currently targets:

- **MSL4Emergency:** 15 README phrase examples are included now; the importer fetches available text annotation files through the GitHub API. Only explicitly identified text files are downloaded. The corpus is not automatically classified as Yangon or Mandalay Sign Language. Source licence: CC BY-NC-SA 4.0.
- **EASIER Multilingual Sign Language Wordnet:** sign metadata, gloss tables, synset links, and definitions where present. Source licence: CC BY 4.0. Languages include BSL, NGT, LSF, DGS, GSL, DSGS, PJM, and STS.
- **ASL-LEX 2.0:** lexical/phonological database fields only; reference videos are excluded. The official download page states CC BY 4.0; verify the individual OSF file terms before redistributing a downloaded release.

Imported entries are marked `source-imported-needs-community-review`; imported glosses are not automatically treated as validated translations or visual sign instructions. Keep source attribution and licence notices with all derived data. MSL4Emergency is non-commercial and share-alike.

**Important:** the importer requires network access when it runs. A downloadable project archive does not itself contain the full upstream corpora until the importer workflow has completed successfully. Check the workflow summary and `data/signs/index.json` for actual imported counts.
