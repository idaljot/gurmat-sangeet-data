# EXTRACTION.md — book extraction methodology (Phase B)

Documents how each in-scope book was extracted, so this is reproducible. Companion to
`books/extracted/_sample/PHASE_A_REPORT.md` (calibration) and
`books/extracted/_sample/PHASE_A_ASEES_REVALIDATION.md` (legacy-font follow-up).
**Everything produced by this pass is `status: "draft"`.** Nothing here is canonical —
see `GURMAT-SANGEET-CONTEXT.md` for the approval workflow.

## Scope

4 of 7 source books, per the Phase A sign-off (the other 3 — Guru Tegh Bahadur Ji, Guru
Nanak Bani Vol. I & II — are held on font problems; see
`books/extracted/_sample/PHASE_A_ASEES_REVALIDATION.md` for a partial update on that).

## Shared tooling

- **Shabad identification**: `books/extracted/_lib/shabad_match.py`. The task originally
  named "GurbaniNow" for this — that API (`api.gurbaninow.com`) is explicitly deprecated
  upstream and confirmed non-functional this session (its own documented example query
  returns zero results). Used **BaniDB** instead (same broad ecosystem/ownership,
  actively maintained) via the `banidb` PyPI package. Validated end-to-end: searching the
  exact text of SGGS Ang 727 returns the correct `shabad_id` with matching ang/raag/writer.
  Tiered fuzzy strategy: exact-line search first, then progressively shorter leading
  substrings (8, 5, 3 words) to tolerate OCR/extraction noise, similarity-scored against
  the returned verse. **Never fabricates a match** — returns `confidence: "none"` and
  `shabad_id: null` when nothing is found, which callers must leave for manual
  identification rather than guess.
- **Legacy Gurmukhi ASCII font decoding**: `gurmukhi-utils` (npm, Shabad OS ecosystem),
  `toUnicode()`. Validated in Phase A against known text.
- **Section tagging**: `front-matter` / `essay` / `biography` / `notation` / `index` /
  `other`, per page, via simple documented heuristics in each extraction script — draft
  tags, not authoritative.
- **Notation policy (unchanged from Phase A)**: no book's sur/swara content is trusted as
  extracted text. Every notation block gets `needs_manual_transcription: true`
  unconditionally, plus a cropped page image, regardless of how structurally clean the
  block looked. Extracted "raw" notation text is a rough aid for the human transcriber,
  never a substitute.
- **Bani text policy**: shabad lyric text is never stored as canonical content. Only a
  first-line is kept (labeled "extracted, not canonical") as a matching aid, plus the
  resolved `shabad_id` when found. Front-matter/essay/biography/index prose IS kept as
  extracted draft text (that rule is specifically about not treating book-rendered lyric
  text as a source of truth for bani, not about withholding non-lyric prose).

## Results overview

| Book | Pages | Notation blocks | Shabad match (high/medium/none) |
|---|---|---|---|
| Guru Gobind Singh Ji Di Bani | 131 | 68 | 55 / 0 / 13 |
| Asa Di Vaar | 217 | 167 (48 table, 119 inline-line) | 6 / 0 / 161 |
| 2 Sampurn 55 Parhtala | 228 | 330 (318 table, 12 inline-line) | 1 / 2 / 327 |
| Raag Da Saroup Complete | 31 | 184 (all inline-line) | 0 / 0 / 184 |
| **Total** | **607** | **749** | **62 / 2 / 685** |

Low match rates for the OCR books are expected, not a pipeline defect: most detected
notation blocks are table fragments, raag/taal labels, or Aroh/Avroh lines — not full,
identifiable Gurbani first-lines — so there's often no valid candidate to search on in the
first place (Raag Da Saroup Complete has 0/184 because it's raag-reference data, not
shabad lyrics, by design). The matcher's job is to never claim a match it can't back up,
not to force a high hit rate.

## Per-book detail

### Guru Gobind Singh Ji Di Bani (131pp) → `guru-gobind-singh-ji-di-bani/`

- **Method**: font-run-aware extraction (`pymupdf` per-span font detection) — legacy
  WinAnsi runs (`FNTSBS+Raavi`, `FNTSBS+Akaash`, `FNTSBS+AnmolLipi`, 128/131 pages) piped
  through `gurmukhi-utils toUnicode()`; the ~3 genuine CID-Unicode pages (cover/title) get
  NFC + sihari-reorder fix.
- **Notation**: genuine bordered PDF tables (12-column taal grids). Cropped as page
  images. **Table structure is more complex than a flat "one sur row" model** — visually
  confirmed (page 9) that cells interleave up to ~8 stacked sub-rows (sur written as
  Gurmukhi consonants, e.g. `ਸਂ ਧੁ ਪ`, alternating with taal-bol/lyric fragments, plus an
  occasional bold Latin `S` sustain marker) — not the uniform "plain Latin sargam row"
  Phase A's sampling assumed for this book. `raw_sur_row` in `notation-raw.json` is a
  best-effort single-row extraction and is explicitly flagged as unable to represent the
  full grid; treat it as a rough aid only.
- **Known gap**: page 1's subtitle drops a "sha" character on extraction (not reordered —
  actually missing). Left unfixed and flagged, per "never guess" policy.
- **Fix applied post-run**: the extraction script initially left `raag`/`taal`/
  `raw_sur_row` in raw un-converted AnmolLipi ASCII in `notation-raw.json` even though
  page text and `extracted_first_line` were correctly converted. Patched afterward
  (same `gurmukhi-utils` bridge) across all 68 records and verified against the page-9
  crop — the shabad-match (`ang 455`, similarity 0.99) confirms the corrected
  `raw_sur_row` now reads consistently with the matched verse.
- **Shabad match**: 55/68 high confidence (81%) — much better than the other 3 books,
  because this book's font-bridge method produces cleaner text than OCR.

### Asa Di Vaar (217pp) → `asa-di-vaar/`

- **Method**: `pdftoppm -r 150` + `tesseract -l pan`, default PSM for prose,
  `--psm 6` where a bordered table was detected.
- **Notation**: two distinct layouts, tagged separately — `bordered-table` (48 blocks,
  moderate OCR reliability, density-dependent per Phase A) and `inline-line` (119 blocks,
  Aroh/Avroh-style running text where OCR collapses inter-syllable spacing — the least
  trustworthy content type). Every block cropped as an image regardless.
- **Shabad match**: low hit rate (6/167) expected — most blocks are table fragments or
  inline notation lines, not full first-lines; where a first-line was extractable,
  matching worked as designed.

### 2 Sampurn 55 Parhtala (228pp) → `sampurn-55-parhtala/`

- **Method**: same OCR approach as Asa Di Vaar. One page (the foreword) is in a
  legible AnmolLipi/GurbaniAkhar ASCII scheme distinct from the rest of the book; it was
  left on the uniform OCR path rather than special-cased (documented in Phase A as an
  acceptable simplification).
- **Notation**: dominated by `bordered-table` blocks (318 of 330) — matches this book's
  structure as mostly full sur/taal grids per shabad (Phase A estimated ~55 shabads'
  worth of notation; 318 detected blocks reflects that grids often span multiple
  table-detection regions per shabad, not 318 distinct shabads).
- **Shabad match**: 3/330 (1 high, 2 medium) — very low, consistent with most blocks being
  table interior fragments without an adjacent clean first-line to search on.

### Raag Da Saroup Complete (31pp) → `raag-da-saroup-complete/`

- **Method**: `tesseract -l pan --psm 4` (not `--psm 6` — confirmed in Phase A that `--psm
  6` silently drops rows on this book's label:value layout).
- **Notation**: 184 blocks, all `inline-line` (Aroh/Avroh/Mukh Ang entries per raag) — by
  far the least trustworthy layout type per the cross-book pattern (inline lines lose
  syllable spacing under OCR). Labels (Thaat/Jaati/Vaadi/etc.) are comparatively reliable
  per Phase A (~95%+) but aren't shabad-lyric content, so they don't go through
  shabad-matching at all.
- **Shabad match**: 0/184 by design — this book is raag reference data, not shabad
  lyrics; there's nothing to match against.

## Known limitations / follow-ups

1. Section-tagging heuristics are simple and unverified at scale — spot-check before
   relying on `section` counts for anything beyond routing.
2. Table-region cropping (`pdfplumber.find_tables()` / bounding-box heuristics) was not
   individually verified on every one of the 749 notation blocks — spot-checked a sample
   per book. A full visual audit is part of the human-review workflow, not this pass.
3. `raw_text` / `raw_sur_row` fields are consistently, deliberately unreliable by design —
   they exist to give a human transcriber a head start, not to be parsed as data.
4. The Asees-legacy-font bridge validated in
   `books/extracted/_sample/PHASE_A_ASEES_REVALIDATION.md` (for Guru Nanak Bani Vol. I/II)
   is not yet applied anywhere — those 2 books remain held, unrelated to this pass.
