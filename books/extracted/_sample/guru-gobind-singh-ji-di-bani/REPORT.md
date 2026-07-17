# Extraction diagnosis — Guru Gobind Singh Ji Di Bani (Shabad Sur Rachnavali), 131pp

**Status: draft calibration notes (Phase A). No canonical data produced.**

## Headline finding — refutes prior diagnosis

The prior diagnosis said this book was "embedded Unicode Gurmukhi with a sipari
reorder artifact." Empirically that is true for only **~3 of 131 pages** (the
cover/title pages, 1/3/4). The other **~128 pages (98%)** — essentially the
entire book body — are set in a **legacy 8-bit ASCII-mapped Gurmukhi font**
(`FNTSBS+Raavi`/`FNTSBS+Akaash`/`FNTSBS+AnmolLipi`, WinAnsiEncoding, `uni=no`
per `pdffonts`) that naive `pdftotext`/`pdfplumber` extracts as nonsense Latin
mojibake (e.g. raw page 5: `s. jspwl isMG jI gurmiq sMgIq dy Kyqr...`).

**Good news:** this is not unrecoverable garbling. It is the well-documented
"GurmukhiAkhar" ASCII keying scheme used by the AnmolLipi font family, which
the open-source, actively-maintained npm package
[`gurmukhi-utils`](https://github.com/shabados/gurmukhi-utils) (Shabad OS /
SikhiToTheMax ecosystem) converts losslessly via its `toUnicode()` function —
verified directly, not assumed. Example:
`s. jspwl isMG jI` -> `ਸ. ਜਸਪਾਲ ਸਿੰਘ ਜੀ`, and critically
`gurU goibMd isMG jI` -> `ਗੁਰੂ ਗੋਬਿੰਦ ਸਿੰਘ ਜੀ` — the conversion **already produces
correct sihari order**, so the sipari artifact does not even arise for these
pages.

## Method per content type

| Content | Font found (pdffonts) | Method | Confidence |
|---|---|---|---|
| Cover/title (pp.1,3,4) | CID Identity-H, uni=yes | `pdftotext`, then regex sihari-reorder fix + NFC | Medium-high — reorder validated; one dropped character (sha in shabad) found, NOT recovered, flagged |
| Front matter / essays | `FNTSBS+*` WinAnsi, uni=no | `pdftotext -layout` -> `gurmukhi-utils toUnicode()` -> NFC | High (fluent, grammatical output) |
| Shabad lyrics + pad-arth glossary | same legacy font | same conversion | High for lyric lines; 2-column glossary layout collapses — not preserved |
| Swara/sur notation tables (e.g. pp.31, 126) | same legacy font + plain Latin in sur row | `pdftotext -layout` (genuine bordered PDF table) -> per-row `toUnicode()` | Row content high-confidence, validated by independent means (see below); exact per-cell boundaries not guaranteed |

## Text-accuracy estimate

- Front matter / lyric prose: **~95%+** after conversion, eyeballed against
  the rendered PNG for pages 5 and 30 — reads as fluent Punjabi with correct
  words. Not 100% because isolated dropped/garbled glyphs (e.g. the dropped
  sha case on page 1) are known to occur and a single random sample can't
  rule out more.
- Notation tables (pp.31, 126): **structure high-confidence, cell-precision
  medium**. Validated the taal-bol row of the Raag Sorath / Iktaal table
  (page 31) three independent ways: (1) `toUnicode()` conversion, (2) my own
  visual read of a 300dpi crop, (3) `tesseract -l pan` OCR of the same
  region — all three agree on "Dhin Dhin Dhage Tirkit Tu Na Kat Ta Dhage
  Tirkit Dhin Na" (Gurmukhi), which is the textbook Iktaal bol pattern. This
  cross-validation is strong evidence the conversion is trustworthy for this
  font on this book.

## Specific issues found

1. **Legacy-font mixing CONFIRMED, and far larger than the prior diagnosis
   assumed** — 128/131 pages, not a handful.
2. **Sipari reorder artifact CONFIRMED but only on the ~3 CID-Unicode
   pages**; does not affect the legacy-ASCII body pages because
   `gurmukhi-utils` handles reordering correctly during conversion.
3. **New issue not previously flagged: dropped glyph.** Page 1's subtitle
   ("Shabad Sur Rachnavali") extracts with its leading "sha" character
   silently absent from the raw text — not just reordered, actually missing.
   Left unfixed and flagged per instructions; do not guess the missing
   character even though it's obvious from context.
4. **Notation is genuinely tabular** (real PDF table borders, not just
   whitespace-aligned text), which is favorable — `pdftotext -layout`
   tracks real cell x-positions rather than guessing.
5. The **sur/swara syllable row inside notation tables is already written
   in plain Latin ASCII** (S R G M P D N, r g m d n) directly in the source
   PDF, matching this project's own SARGAM convention, and survives
   extraction untouched — it is the taal-bol and lyric rows (in Gurmukhi)
   that need the legacy-font conversion.
6. Ma readings observed only in passing on the two sampled notation tables
   (pp.31, 126): only shuddh `M` forms were seen (expected for Sorath/Kafi);
   no `m` (teevra) observed in this small sample. Not transcribed into
   canonical form — that is a later, reviewed step.

## Notation-fidelity verdict

**Mixed / cautiously trustworthy, with a required manual-review step.**
Row-by-row structure (which bols/swara go with which matra column) extracts
reliably given the genuine table borders and the validated conversion method.
However: (a) some cells contain combined lyric+sur glyphs whose internal
split is ambiguous from plain text alone (needs the PNG open side-by-side),
and (b) this diagnosis validated only 2 of the ~60 shabads' notation tables in
this book — do not assume uniform quality across all 60 without spot-checking
more before any bulk extraction. Recommend: extract via this method, but
require a human (ideally someone who reads swaralipi) to verify each
notation table against its rendered page image before marking `approved`.

## Files in this sample
`page-1.png/txt` (cover, sipari case), `page-5.png/txt` (foreword, legacy
ASCII), `page-30.png/txt` + `page-125.png/txt` (shabad lyrics + glossary,
legacy ASCII), `page-31.png/txt` + `page-126.png/txt` (notation tables).
