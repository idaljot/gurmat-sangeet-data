# Extraction diagnosis — Guru Nanak Bani, Vol. I, 767pp

**Status: draft calibration notes (Phase A). No canonical data produced.**

## Headline finding — refutes prior diagnosis significantly

The prior diagnosis said books 3-4 are "text-based, content pages extract
fine; covers are images." The cover part is correct (page 1 has no
extractable text — genuinely an image). **The "content pages extract fine"
part is wrong.** A full per-page scan (via PyMuPDF, comparing Gurmukhi-vs-total
letter ratio across all 767 pages) found:

- **171 pages (22%)** are majority clean Unicode Gurmukhi text.
- **594 pages (77%)** are majority a **legacy WinAnsi font** that extracts as
  ASCII mojibake.
- 2 pages are blank/image-only.

That legacy-font majority splits into (at least) **two different, incompatible
schemes**, confirmed by font name + conversion testing:

1. **AnmolLipi/GurbaniLipi-family** (`FNTSBS+GurbaniLipi[Bold]`) — same
   "GurmukhiAkhar" ASCII scheme as book 1. Converts cleanly via
   `gurmukhi-utils` `toUnicode()` (verified — see `page-300.txt`, a notation
   table that converts perfectly, including correct sihari order).
2. **Asees-family** (`FNTSBS+Asees[Bold]` and, in the index pages, plain
   `Asees`/`Asees-Bold` Type1) — a **different** ASCII keying scheme.
   `gurmukhi-utils toUnicode()` was tested against it directly and produces
   wrong output (e.g. `nkg/ ;u[ Gkt? fs;[ ;u[Ò` → garbage, not real Gurmukhi
   words) — see `page-7.txt`. **No verified, citable, open-source mapping for
   Asees was found within this diagnosis's scope.** Marked unmapped.

Additionally — and this is the finding I'd flag as most important for
planning Phase B — **even the "good" (majority-clean-Unicode) pages are not
uniformly clean.** On the sampled page 16, most shabad first-lines are in the
clean CID font ("Akaash") and only need the by-now-familiar sipari reorder
fix (validated against `tesseract -l pan` OCR, which agreed word-for-word).
But **raag-header lines, and even scattered individual words inside otherwise
clean verse lines** (e.g. `ਕੂੜਿ ਵਿਗਾੜਿ`, `ਸੰਮ੍ਹਾਲੇ`, `ਦੇਹਿ ਪਿਆਰੋ` all fell back to
Asees on this one sampled page) are un-mappable Asees fragments **mixed in at
word granularity, not page granularity.** This means the true "how much of
this book is safely extractable" number is lower than the 22%/77% page-level
split suggests — some fraction of words on "good" pages are also
unrecoverable without OCR or manual work.

## Method per content type

| Content | Font | Method | Confidence |
|---|---|---|---|
| Cover (p.1) | — | none (image) | N/A — confirms prior diagnosis on this point only |
| Index / shabad-list pages (p.7) | Asees (WinAnsi) | `pdftotext -layout`; `gurmukhi-utils` attempted, failed | None — flagged unmapped |
| "Good" shabad-index page with raag headers (p.16) | Mixed: Akaash CID + Asees inline | `pdftotext` + regex sihari-reorder + NFC for CID runs; Asees runs left broken; cross-checked with `tesseract -l pan` OCR | High for CID runs (OCR-validated); none for Asees runs |
| Notation table, Siri Raag (p.20) | Asees (Type1 WinAnsi) | `pdftotext -layout`; OCR attempted as fallback | None for raw text; OCR unreliable for table cell alignment, rough aid only |
| Notation table, Gaudi (p.300) | GurbaniLipi (WinAnsi) | `pdftotext -layout` → `gurmukhi-utils toUnicode()` → NFC | High — output is fluent and correctly reordered |

## Text-accuracy estimate

- Clean-CID-font portions: ~90%+, based on the OCR cross-check on page 16.
- GurbaniLipi-legacy portions: high (same validated method as book 1).
- Asees-legacy portions (77% page-majority, plus scattered words elsewhere):
  **effectively 0% via current tooling** — needs either a dedicated Asees
  mapping (not found/verified in this pass) or OCR/manual transcription.
- Overall rough book-wide estimate, weighting by the page-level split: **very
  roughly 20-30% of the book is reliably machine-extractable today**; the
  rest needs either an Asees converter or OCR+review.

## Specific issues found

1. Prior diagnosis's "extracts fine" claim for this book is **not supported**
   — majority of pages are legacy-font-encoded, and even clean pages have
   embedded Asees fragments.
2. **Two distinct incompatible legacy ASCII schemes coexist in the same
   book** (GurbaniLipi/AnmolLipi-compatible vs. Asees-incompatible) — any
   extraction pipeline needs to detect font per run, not assume one scheme
   for the whole document.
3. Sipari reorder artifact **confirmed** on CID-font runs, consistent with
   the (correct part of the) prior diagnosis, and fixable with the same
   regex approach validated in book 1.
4. **Notation tables exist throughout this "Bani" volume**, not just in the
   dedicated "Sur Rachnavali" books — the prior diagnosis's implicit
   assumption that vol 1/2 are "just lyric text" is wrong; swara/taal grids
   appear at intervals (confirmed at pages 20, 300; likely many more).
5. Word-level (not just page-level) font mixing is a new complication not
   anticipated by the prior diagnosis or by my own initial per-page
   font-resource scan (which under-counted because it only checked page
   Resources, not which font actually rendered which run of text).

## Notation-fidelity verdict

**Mixed, skewing toward "needs manual transcription."** The one notation
table sampled in the fixable GurbaniLipi scheme (p.300) converted with high
apparent fidelity. The one sampled in Asees (p.20) is currently unusable via
automation — recommend either sourcing a verified Asees mapping before Phase
B, or planning for OCR + human transcription for the Asees-encoded notation
tables, which appear to be a large fraction of this book's total.

## Files in this sample
`page-1.png/txt` (cover, image-only), `page-7.png/txt` (index, Asees,
unmapped), `page-16.png/txt` (mixed CID+Asees index/header page, OCR
cross-checked), `page-20.png/txt` (notation table, Asees, unmapped),
`page-300.png/txt` (notation table, GurbaniLipi, converts cleanly).
