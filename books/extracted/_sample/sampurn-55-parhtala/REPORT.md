# Sampurn 55 Parhtala — Phase A sampling notes

Source: `books/2 Sampurn 55 Parhtala  Shabad Sur Rachnavali Final with cover.pdf` (228pp,
not covered by the original prior diagnosis). Samples: pages 1, 3, 4, 5, 10, 32, 228
(front cover, English title/copyright page, foreword prose, intro-essay prose, a
16-column notation grid, a shabad-verse prose page, back cover/bio).

## Headline finding — this book is in noticeably better shape than the pre-diagnosis feared

The `pdffonts` signature (cryptic `TTxxxt00` subset names, `Custom` encoding, mostly
`uni=no`) matches the pattern typically associated with unrecoverable legacy fonts. In
practice, for **prose/commentary content** (the large majority of the book — 224 of 226
scanned pages produced Gurmukhi-range codepoints in a full-book scan with `pdftotext`),
extraction is either directly usable or one documented, mechanical transform away from
usable. Only the **sur/lyric notation grid tables** turned out to use a genuinely broken
font subset, matching the original worst-case prediction.

## Chosen method: OCR (`pdftoppm -r 150` + `tesseract -l pan`), spot-checked against renders

Three distinct extraction situations were found and confirmed by comparing `pdftotext`/
PyMuPDF text-layer output against the rendered page image for known content:

1. **Prose pages using the "reordering-bug" font family** (pages 5, 32, and the bulk of
   the book's shabad/commentary text): `pdftotext` extracts genuine Gurmukhi-block Unicode
   codepoints with the **correct letters but wrong internal order** — pre-base vowel signs
   (sihari `ਿ`) and halant `੍` appear in visual/typing order rather than Unicode logical
   order (e.g. rendered `ਵਿੱਚ` / `ਸ੍ਰੀ` extract as `ਿਵੱਚ` / `ਸਰ੍ੀ`). This is a well-documented,
   general class of Gurmukhi/Indic PDF-extraction bug, not specific to this book — see the
   Unicode Technical Note on Gurmukhi, gurbanifiles.net's "Issues Regarding the Use of
   Unicode Gurmukhi-Hindi fonts", and the same bug class reported for Devanagari in
   [PyMuPDF issue #4805](https://github.com/pymupdf/pymupdf/issues/4805). No ready-made,
   validated reordering script was found in this session, so **no fix was applied or
   invented** — flagging it as a solvable Phase B task instead.
2. **The foreword (page 4) specifically** uses a different font pair extracting to a
   legible **legacy ASCII-Gurmukhi transliteration scheme** (AnmolLipi/GurbaniAkhar-style
   phonetic Roman keyboard layout, e.g. `sRI gurU gRMQ swihb dI bwxI` = `ਸ੍ਰੀ ਗੁਰੂ ਗ੍ਰੰਥ ਸਾਹਿਬ
   ਦੀ ਬਾਣੀ`). Online converters for this class of scheme exist (e.g. toolsriver.com's and
   typingbits.com's Punjabi font converters) but were not applied/validated against this
   exact font here — flagged as a known, named scheme rather than random garbage.
3. **Notation grid tables** (page 10, and by extension the book's other sur/lyric grids):
   extract as fully garbled Latin ASCII gibberish from a font subset distinct from the
   surrounding prose — this matches the original diagnosis's worst-case prediction. The
   grid's own title line was garbled while the page *footer* (different, prose font)
   extracted correctly on the same page — confirming the break is isolated to the
   grid-specific font, not the whole page.

**For every sample page, `tesseract -l pan` OCR on a 150dpi render sidesteps all three
issues simultaneously** (it reads shaped glyphs directly, so reordering and transliteration
decoding are moot) and was used as the actual working text in this pass, spot-checked
word-by-word against the PNG.

## Text-accuracy estimate

- **Prose (foreword, essays, shabad text)** — pages 4, 5, 32, 228 body paragraph: **~95–97%**
  OCR accuracy by manual spot check, correct order throughout.
- **Italic-styled quoted Gurbani lines within prose** (found on page 4): OCR degrades
  sharply on italics specifically — worth flagging as a general risk wherever quotes are
  italicized in this book.
- **Notation grid table** (page 10, 16-column): **~60–75%** reliable cell recovery —
  moderate, not trustworthy as-is. Recurring errors: `S` (sustain marker) confused with
  digits `5`/`੦`; some cells merged; the numeric beat-header row partially garbled.
- **Cover pages** (1, 228): text is baked into the cover graphic, not real PDF text
  (`pdftotext` returns empty). OCR on the decorative front cover (page 1) is largely noise
  from the ornate border pattern, though the author's name was recovered correctly; OCR on
  the plainer back cover (page 228) is reliable for the bio paragraph but drops trailing
  digits in dense inline lists (e.g. "ਕਾਨੜਾ-6" → "ਕਾਨੜਾ-").

## Notation-fidelity verdict

**Not reliably automatable — same conclusion as Asa Di Vaar, via a different underlying
font-break mechanism.** Prose content in this book is in good shape (OCR-viable, ~95%+),
answering the task's central question: automated extraction **is** viable for most of the
book's *text* content. But the sur/lyric notation grids specifically are not — OCR on the
sampled grid (page 10) is only moderately reliable (~60–75%) and the underlying text layer
for grids is fully garbled. Recommend: capture notation grid pages as images and
hand-transcribe them directly against the rendered page, rather than trusting OCR or any
text-layer output for the actual swara/beat data. Prose surrounding the grids can
reasonably use OCR as a first-pass draft, still subject to human review per project policy
(all extracted content is `status: "draft"` regardless of confidence).

No Ma (madhyam) readings were transcribed as data in this pass — passing observation only.
