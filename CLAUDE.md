# CLAUDE.md — Gurmat Sangeet Notation Dataset

Operating instructions for AI sessions in this repo. Keep this file lean and stable.

## What this is

An open, structured **data** repository (not an application) of raag reference data and
kirtan swar (sur) notation from the parampara of **Bhai Jaspal Singh Ji**, built as a
*seva* project. Any project may consume it; the reference implementation is
[ShabadSwar.com](https://shabadswar.com). **Draft for review — not yet canonical.**

Sacred musical content — **wrong notation is worse than no notation.**

## Read first

- **`SCHEMA.md`** — the data contract (every field, and why). The authority.
- **`SARGAM.md`** — the notation string spec (how to read/write sur, taal, octaves).
- **`VISION.md`** — purpose, roadmap, open questions for the community.
- `README.md` / `index.html` — the front door.

## Notation rules (do not violate)

- **Never guess or "fix" notation.** If a reading is uncertain, leave it flagged, don't invent.
- **All entered/extracted data is `status: "draft"`** until Bhai Jaspal Singh Ji (or an
  authority he designates) confirms it. Only he flips a record to `approved`.
- **Ma convention — SETTLED (shuddha-set):** `M` = shuddh madhyam, `m` = teevra madhyam.
  Uniform rule: **uppercase = shuddh (natural), lowercase = the altered note** (`r g d n`
  komal, `m` teevra). Uppercase `S R G M P D N` = the natural Bilaval scale.
- **Notation scripts: Roman/Latin and Gurmukhi only** (Bhatkhande dropped). Notation is
  stored once as canonical ASCII (SARGAM); scripts are a display layer.
- **Case is meaning.** Never case-fold, lowercase, or `text-transform` notation, and keep
  storage/search case-sensitive — case carries komal/shuddh/teevra.

## Data model

- Shabad ↔ notation is **many-to-many**: notation records carry a `shabadIds` **array**
  (one notation may serve many shabads, e.g. a single Sukhmani Sahib dhun; a shabad may
  have many notations).
- **Provenance is first-class:** every record carries `status` and where it came from.
  Consumers must be able to filter to approved-only and visibly mark drafts as unverified.

## Book extraction

- Source PDFs live in `books/`. Extracted content goes in `books/extracted/<book-slug>/`,
  keeping **all** content (notation, raag, plus non-notation: front matter, essays, bios,
  indexes) as `draft`.
- Extract with scripts that write to disk; never load whole PDFs into model context.
- Capture notation **as found**; canonical SARGAM encoding is a later, reviewed step.

## Workflow

- Branch off `main` → review → merge. `main` auto-deploys to Cloudflare Pages
  (**`main` = production**), no-build static site served from repo root.
- **User-facing changes** (landing/demo/schema-as-published, data): open a PR and verify
  the Cloudflare preview before merging. **Docs-only, already eyeballed:** fast-forward is fine.
- Do **not** populate `data/*.json` with real notation until the schema is reviewed
  (Baljeet) and book readings are confirmed.

## Pending (human-gated)

- Baljeet: technical schema review. Anmol: faithfulness/vision + remaining questions.
- Licensing (proposed CC BY-NC 4.0) needs the family's explicit blessing before publishing.
- If the repo is made public, note that `books/` contains Ustaad ji's published works —
  confirm that's intended before flipping visibility.

## Maintenance

When a change alters project state, update the relevant doc (`SCHEMA.md`, `SARGAM.md`,
`VISION.md`) **in the same commit** as the change.
