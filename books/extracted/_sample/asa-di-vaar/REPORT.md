# Asa Di Vaar — Phase A sampling notes

Source: `books/Asa Di Vaar.pdf` (217pp). Samples: pages 1, 2, 3, 4, 5, 100, 101 (cover,
verse+inline-notation, 12-col grid, essay/commentary, second grid style, verse ~mid-book,
16-col grid ~mid-book).

## Chosen method

Two genuinely different embedded-font situations exist in this book, confirmed via
`pdffonts` + PyMuPDF per-page font listing and visually cross-checked page by page — this
is **not** a case of "half the book is legacy, half is clean," it is finer-grained than
that:

1. **CID Type0 `Identity-H` `Raavi`/`Raavi,Bold` (`uni=yes`)** — used for verse/shabad text
   and essay/commentary prose (pages 2, 4, 100, and similar). `pdffonts` reports these as
   Unicode-mapped, and the extracted codepoints do fall in the Gurmukhi block (U+0A00–
   U+0A7F) — but **the ToUnicode mapping is wrong**. Confirmed by comparing extracted text
   against the rendered page image for well-known Gurbani lines: rendered page 2 clearly
   shows `ੴ ਸਤਿਗੁਰ ਪ੍ਰਸਾਦਿ ॥`, but `pdftotext`/PyMuPDF both extract `ੴ ਸਤਤਗੁਯ ਩ਰਸਾਤਦ ॥`. This
   is a known class of bug (Indic-script Identity-H CID fonts storing glyphs in
   visual/shaped order rather than logical order — the same class of issue reported for
   Devanagari in [PyMuPDF issue #4805](https://github.com/pymupdf/pymupdf/issues/4805) and
   for Sinhala/Tamil in PDFBox/OpenPDF trackers). No fixed character-substitution table was
   found or safely derivable — it is not a clean 1:1 cipher — so **no mapping was invented**;
   OCR was used instead.
2. **Plain TrueType `WinAnsiEncoding` `Raavi`/`Asees` (`uni=no`)** — used for the sur/lyric
   grid tables (pages 3, 5, 101). This is the legacy ASCII-mapped path described in the
   prior diagnosis; text layer is garbled Latin (`okr[ nk;k` = "vaar aasa", matching the
   prior fingerprint exactly). Confirmed unusable directly.

**Method actually used for all sampled pages: `pdftoppm -r 150` render + `tesseract -l pan`
OCR**, spot-checked word-by-word against the rendered PNG. `pdftotext -layout` output is
kept in each `page-N.txt` only as a labeled "GARBLED — reference only" artifact, not as
usable data. Prose pages used default PSM; grid/table pages used `--psm 6`.

## Text-accuracy estimate

- **Prose (shabad text, word-meanings, essays)** — pages 2, 4, 100: **~95–97%** OCR
  character accuracy, estimated by manual word-for-word comparison against the rendered
  image. Main recurring error: the ੴ (Ik Onkar) ligature is OCR'd as three separate
  characters; occasional single vowel-sign slips (e.g. ਪ੍ਰੇਮਿ → ਪ੍ਰੋਮਿ).
- **Sparse/simple grid tables (12-column, page 3)**: **~85–90%** cell-level accuracy.
  Structure and sur↔lyric alignment survive well. Dominant error: the `S` (sustain/hold)
  marker is frequently misread as digit `5`.
- **Denser grid tables (16-column, page 101)**: **~50–65%** reliable cell recovery. Column
  density is inversely correlated with OCR grid fidelity in this book — cells get merged,
  boundaries drop, stray punctuation appears. The one line of prose footnote on that same
  page OCR'd cleanly by contrast.
- **Cover (page 1)**: image-only; title is a stylized WordArt graphic, not real text.
  Not notation-bearing — no OCR attempted, noted as image-only.

## Issues found, page by page

- p.1 — image-only cover (photo + WordArt title). No text layer of consequence.
- p.2 — clean render, wrong-ToUnicode CID font; prose + word-meanings OCR well; the
  inline Aroh/Avroh notation line (`ਸ ਰੇ ਮ ਪ ਧ ਸਂ`) had its inter-syllable spacing
  **collapsed by OCR** into `ਸਰੇਮਪਧਸਂ` — this is a distinct failure mode from the grid
  tables and is untrustworthy without manual respacing.
- p.3 — legacy WinAnsi font, 12-column Ektaal grid; OCR with `--psm 6` preserved row/column
  structure well; good candidate for OCR-assisted (not automated) transcription.
- p.4 — wrong-ToUnicode CID font, pure prose essay (Mool Mantar explanation); OCR reliable.
- p.5 — legacy WinAnsi font, unnumbered grid table; noisier than p.3 (more digit/dash
  confusion), lower confidence.
- p.100 — wrong-ToUnicode CID font, prose Salok; confirms the pattern holds ~100 pages in.
- p.101 — legacy WinAnsi font, 16-column grid (denser); OCR degraded significantly, not
  trustworthy for direct use.

Overall the book alternates, roughly but not strictly by page parity, between these two
font regimes throughout its 217 pages (spot-checked at pp. 1–5, 100–101, 150–151, 215–217);
both regimes require OCR rather than the PDF text layer.

## Notation-fidelity verdict

**Mixed — not automatable end-to-end; every notation page needs human verification before
entering data.**

- Inline notation lists (Aroh/Avroh embedded in running prose, e.g. p.2): OCR collapses
  spacing between syllables — **needs manual transcription**, not raw OCR.
- Simple/sparse grid tables (e.g. p.3, ~12 columns): OCR is a usable **first-pass draft**
  with a known, correctable failure mode (S/5 confusion) — still requires cell-by-cell
  verification against the rendered image before treating as data.
- Dense grid tables (e.g. p.101, 16 columns): OCR is **not trustworthy** — recommend
  capturing these as page images and hand-transcribing directly from the image rather than
  post-editing OCR output, per the "never guess or invent notation" rule.

No Ma (madhyam) readings were transcribed as data in this pass — passing observation only,
per instructions; a later reviewed step should confirm shuddh/teevra readings directly
against page images, not against OCR output.
