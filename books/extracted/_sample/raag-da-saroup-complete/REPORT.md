# Raag Da Saroup Complete — Phase A sampling notes

Source: `books/Raag Da Saroup Complete.pdf` (31pp, not in the original prior diagnosis —
turned up in the folder). Given its short length, sampled exhaustively by scouting every
page's rendered thumbnail; picked 7 representative pages: 1, 2, 3, 6, 11, 20, 31
(spanning the start, several interior sections, and the last page).

## Structure of the book

Every one of the 31 pages follows the same format: 1–3 short "raag-detail" entries per
page, each a label:value list — ਥਾਟ (Thaat), ਜਾਤੀ (Jaati), ਵਾਦੀ (Vaadi), ਸੰਵਾਦੀ (Samvaadi),
ਸੁਰ (Sur), ਵਰਜਿਤ ਸੁਰ (Varjit Sur), ਸਮਾਂ (Samay), ਆਰੋਹ (Aroh), ਅਵਰੋਹ (Avroh), ਮੁੱਖ ਅੰਗ (Mukh
Ang) — i.e. almost purely structured raag-reference data closely matching what
`SCHEMA.md`'s raag records need, with the last three fields being inline swara/notation
strings rather than prose. This makes the notation-fidelity question the dominant concern
for the whole book, not just isolated pages.

## Chosen method

`pdffonts` per-page inspection (via PyMuPDF) confirms the task brief's prediction: this
book mixes, often **within a single page**, the two font problems separately diagnosed in
Asa Di Vaar:

1. Legacy WinAnsi visual-shape ASCII font (same family as Asa Di Vaar's Raavi/Asees
   legacy path) — garbles to nonsense Latin (`okr f;ohrkr`).
2. CID Identity-H font with the same wrong-ToUnicode bug documented for Asa Di Vaar — the
   telltale wrong character `਩` reappears here (e.g. `ਜਾਤੀ : ਸੰ ਩ੂਯਣ`), confirming this is
   the same underlying font-family bug, not a new one.
3. A third pattern also appears on some pages/fields: a legible AnmolLipi/GurbaniAkhar-style
   ASCII transliteration scheme (`rwgu gauVI` = `ਰਾਗੁ ਗਉੜੀ`), same class as Sampurn 55
   Parhtala's page 4.

All three text-layer paths are unusable directly. **Method used: `pdftoppm -r 150` render +
`tesseract -l pan --psm 4`**, spot-checked against the PNG for every sampled page.
`--psm 4` (single column of variable-sized text) was chosen after testing — `--psm 6`
(uniform block, used successfully for Asa Di Vaar/Parhtala's true grid tables) silently
**dropped entire label:value rows** on this book's list-style layout (e.g. lost the ਥਾਟ,
ਵਾਦੀ, and ਸਮਾਂ rows on page 1 test); `--psm 4` recovered all rows correctly.

## Text-accuracy estimate

- **Labels and short values** (ਥਾਟ, ਜਾਤੀ, ਵਾਦੀ, ਸੰਵਾਦੀ, ਸੁਰ, ਵਰਜਿਤ ਸੁਰ, ਸਮਾਂ): **~95%+**
  accuracy with `--psm 4`, spot-checked across all 7 sampled pages.
- **ਆਰੋਹ / ਅਵਰੋਹ / ਮੁੱਖ ਅੰਗ (Aroh/Avroh/Mukh Ang) notation lines — the actual sur data**:
  unreliable. OCR **collapses or partially collapses the spacing between swara syllables**
  on nearly every sampled entry, e.g. rendered `ਸ ਰੇ ਮੇ, ਪ ਨੀ ਸਂ` comes back as `ਸਰੇ ਮੇ,ਪਨੀਸਂ`.
  This is the identical failure mode found for Asa Di Vaar's inline Aroh/Avroh line (page
  2) — confirms it's a general OCR limitation for space-separated swara sequences (as
  opposed to true grid/table notation, which OCR handles comparatively better), not
  specific to one book or font.

## Issues found

- Font breakage is finer-grained here than in the other two books — it can switch
  mid-page, even mid-field, between the legacy-ASCII and wrong-CID paths. Not worth trying
  to special-case by font; OCR-on-render sidesteps all of it uniformly.
- No image-only or scanned pages found in this short book; no OCR fallback for
  cover/scans was needed (unlike the other two books' covers).
- No dense multi-column grid tables in this book (unlike Asa Di Vaar/Parhtala) — the
  notation here is always inline label:value lines, which is a *different* and, per the
  evidence above, *harder* case for OCR fidelity than the grid tables in the other books.

## Notation-fidelity verdict

**Not trustworthy for direct ingestion — needs manual transcription or careful
respacing/verification of every Aroh/Avroh/Mukh Ang line.** This book is almost entirely
composed of exactly the notation-bearing content this project cares most about (raag
reference data with aroh/avroh), and it is also the pattern OCR handles worst in this
sampling pass (worse than the grid tables in the other two books). Recommend treating
every Aroh/Avroh/Mukh Ang line as needing hand verification against the page image, not
as OCR output to lightly edit — collapsed spacing is easy to mis-parse silently (e.g.
telling where one swara syllable ends and the next begins), which is precisely the kind
of error this project's "wrong notation is worse than no notation" rule is meant to catch.
The label fields (Thaat/Jaati/Vaadi/etc.) are comparatively low-risk and can use OCR as a
draft starting point with lighter review.

No Ma (madhyam) readings were transcribed as data in this pass — passing observation only.
