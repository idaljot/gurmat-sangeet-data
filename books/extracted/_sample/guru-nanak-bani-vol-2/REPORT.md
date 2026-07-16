# Extraction diagnosis — Guru Nanak Bani, Vol. II, 780pp

**Status: draft calibration notes (Phase A). No canonical data produced.**

## Headline finding — refutes prior diagnosis even more strongly than Vol. I

The prior diagnosis ("text-based, content pages extract fine; covers are
images") is even further from correct here than for Vol. I. Full per-page
scan (PyMuPDF, Gurmukhi-vs-total-letters ratio across all 780 pages):

- **394 pages (50%)** majority clean Unicode Gurmukhi.
- **384 pages (49%)** majority legacy WinAnsi-font mojibake.
- 2 pages blank/image (covers).

Unlike Vol. I, **every legacy-encoded page sampled here uses the Asees font
family** (`FNTSBS+Asees`/`AseesBold`) — a document-wide font inventory scan
(sampling every 15th page) found **no GurbaniLipi or AnmolLipi fonts anywhere
in this volume**, only Asees (unmapped, see below) plus the CID Unicode fonts
(Akaash, Mangal-Regular, ArialUnicodeMS, Raavi). This means, unlike Vol. I
(which had a partially-fixable legacy scheme), **none of Vol. II's
legacy-font content is currently machine-convertible** with the tooling
available in this diagnosis.

As with Vol. I, `gurmukhi-utils toUnicode()` (the AnmolLipi/GurmukhiAkhar
ASCII scheme) was tested directly against Asees-encoded sample text and
confirmed to fail (produces non-words, see `page-26.txt`).

## Method per content type

| Content | Font | Method | Confidence |
|---|---|---|---|
| Cover (p.1) | — | none (image) | N/A — confirms prior diagnosis on this point only |
| Shabad-index page, no visible mixing (p.10) | CID Akaash/Mangal-Regular | `pdftotext` + regex sihari-reorder + NFC, cross-checked against `tesseract -l pan` OCR | High — OCR agrees almost word-for-word; one small gap found (see below) |
| Notation table, Raag Suhi #1 (p.26) | Asees (WinAnsi) | `pdftotext -layout`; `gurmukhi-utils` attempted, failed | None |
| Notation table, Raag Suhi #2 (p.60) | Asees (WinAnsi) | `pdftotext -layout` only | None for text; table grid structure visually plausible from genuine PDF table borders |

## Text-accuracy estimate

- Clean CID-font pages: high (~90-95%) after the reorder fix, validated
  against OCR on page 10. One real gap found even here: the CID extraction
  sometimes **drops the sub-joined rakar/nukta** in conjuncts (extracted
  `ਅੰਮਿਤ` where OCR — correctly — reads `ਅੰਮ੍ਰਿਤ`, "amrit"). This is a small
  but genuine accuracy gap in the "good" pages that should be tracked, not
  just the more obvious reorder/legacy-font issues.
- Asees-legacy pages/runs: 0% via current tooling, same conclusion as Vol. I.
- Overall rough estimate: since roughly half the book is Asees-majority and
  even the "good" half has small per-word gaps, **something like 40-50% of
  the book is reliably machine-extractable today** at this diagnosis's
  confidence level; the rest needs an Asees mapping or OCR/manual work.
- Did not detect the finer-grained word-level Asees mixing that Vol. I p.16
  showed on the one page sampled here (p.10) — but Vol. I's own "good" pages
  were not uniform either, so this should be checked on more pages before
  concluding Vol. II's "good" pages are cleaner than Vol. I's.

## Specific issues found

1. Prior diagnosis's "extracts fine" is **not supported** — essentially the
   same conclusion as Vol. I, and here the legacy content is *entirely*
   unmapped (no GurbaniLipi fallback like Vol. I had).
2. **Notation tables exist throughout this volume too** (confirmed at pages
   26 and 60, format matches Vol. I/book 1's grid layout) — again
   contradicting any assumption that these are lyric-only volumes.
3. Sipari reorder artifact present and fixable on CID-font pages, same
   method as books 1 and Vol. I.
4. New, smaller finding: **conjunct/nukta dropping** in CID-font extraction
   (rakar dropped from `ਅੰਮ੍ਰਿਤ`) — worth a systematic check in Phase B, this
   diagnosis only caught it because of the OCR cross-check.

## Notation-fidelity verdict

**Needs manual transcription / OCR fallback for the swara notation content
in this volume specifically** — both notation-table samples pulled were in
the unmapped Asees font, with 0% confidence text output. Table grid
structure is visually plausible (genuine bordered tables, as in books 1 and
Vol. I) so a human working directly from the page image should be able to
transcribe accurately, but do not attempt automated notation extraction for
this book without either a verified Asees→Unicode mapping or an OCR-based
pipeline validated specifically on tabular notation content (plain OCR was
not attempted on these table pages here — dense multi-column tables are a
known OCR weak point, see Vol. I's page-20 note).

## Files in this sample
`page-1.png/txt` (cover, image-only), `page-10.png/txt` (clean CID page, OCR
cross-checked), `page-26.png/txt` + `page-60.png/txt` (notation tables,
Asees, unmapped).
