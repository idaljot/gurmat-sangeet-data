# GURMAT-SANGEET-CONTEXT — project state & plan

Mutable project state, people, plan, and open decisions for the Gurmat Sangeet
Notation Dataset. `CLAUDE.md` holds the stable rules; `SCHEMA.md`/`SARGAM.md` are the
specs; `VISION.md` is the outward-facing why. **This file is the operational tracker** —
update it (and bump the date) whenever state changes.

_Last updated: 2026-07-17_

---

## Purpose (brief)

An open, structured dataset of raag reference data + kirtan sur notation from the
parampara of **Bhai Jaspal Singh Ji**. Reference implementation: ShabadSwar.com. See
`VISION.md` for the full rationale. Sacred content — **wrong notation is worse than none.**

## People

- **Daljot** — owner/builder.
- **Bhai Jaspal Singh Ji (Ustaad ji)** — musical authority. **Approves** data (draft →
  approved); does not type. Not tech-savvy → someone sits with him to review/confirm.
- **Anmol** — Ustaad ji's son; data analyst; kirtan. Provided the source PDFs. Owns
  vision/faithfulness questions + the Asees-font source ask + licensing (family).
- **Baljeet** — classmate, dev + kirtan. Technical schema review (gates canonical data).
- **Ranjit** — classmate, coding + kirtan. Potential helper (bandwidth-permitting),
  incl. sur transcription.

## Current state

- Repo live on Cloudflare Pages (landing `index.html`, `vision.html`, `demo/`).
- Committed to `main`: `SCHEMA.md`, `SARGAM.md`, `CLAUDE.md`, `README.md`, `LICENSE`
  (proposed CC BY-NC 4.0), stub `schema/*.json`, and the 7 source PDFs in `books/`.
  `data/raags.json` / `data/sources.json` now hold 2 explicitly-authorized **demo**
  entries from the raag-entry proof-of-concept (see below) — not a general go-ahead to
  populate real data; `data/notations.json` is still empty and stays that way until
  Baljeet's schema review.
- **Ma convention SETTLED (shuddha-set):** `M` = shuddh, `m` = teevra. Scripts: Roman +
  Gurmukhi only (Bhatkhande dropped).
- **Extraction Phase A (calibration) done**; see `books/extracted/_sample/PHASE_A_REPORT.md`.
- **Extraction Phase B (full run, 4 in-scope books) done and merged to `main`** (PR #2).
  See `books/extracted/EXTRACTION.md`. 607 pages, 749 notation blocks extracted (all
  `status: draft`, all flagged `needs_manual_transcription`).
- **Block-clustering done**: the 749 raw blocks are now clustered into **306 real
  transcription items** in `books/extracted/manifest.json` — see `books/extracted/MANIFEST.md`
  for the book-specific clustering logic, and six real over-merge bugs that were found by
  spot-checking crop images and fixed (not left latent). Per-book: Guru Gobind Singh Ji Di
  Bani 63, Asa Di Vaar 120 (least trustworthy grouping — conservative same-page-only),
  Sampurn 55 Parhtala 61, Raag Da Saroup Complete 62 (was 58 — see below). **Use these
  counts, not the 749 raw-block count, for effort planning.**
- **Shabad identification mechanism corrected**: the plan named "GurbaniNow" — that API
  is dead (deprecated upstream, confirmed non-functional: its own documented example
  query returns zero results). Using **BaniDB** instead (`banidb` PyPI package, same
  ecosystem, actively maintained) via `books/extracted/_lib/shabad_match.py`. Validated
  against a known SGGS line before use.
  - **`SCHEMA.md` reconciled** (done): replaced "GurbaniNow" naming and the `"JK3"`
    example with BaniDB's real integer `shabad_id` format, and noted the Shabad OS
    `sttm_id` equivalence.
  - **Offline source validated (GitHub issue #3):** the Shabad OS Database (same
    open-source family as `gurmukhi-utils`, already a dependency) ships a downloadable
    SQLite file. Its `sttm_id` column is the same scheme BaniDB exposes as `shabad_id`
    (confirmed: local `sttm_id=2779` returns the identical already-validated shabad), so
    every `shabad_id` stored in Phase B resolves against a local copy with zero rework.
    Decision (bundle offline vs. call BaniDB live) gated on the reference site's hosting;
    trade-offs + next step captured in issue #3.
- **Phase B completeness verified** against git history: all 4 books at exact page counts
  (131 / 217 / 228 / 31), no gaps or duplicates. The `notation/` subfolder only holds
  crops for `notation`-tagged pages (by design, not a shortfall). Open polish item: page 1's
  empty-text note is generic boilerplate rather than page-specific — pending decision.
- **Notation data-model gap found and filed (GitHub issue #4):** hand-encoded 2 real
  taal-grid crops into SARGAM strings to test the schema against reality. Confirmed
  (word-for-word, against a resolved `shabad_id`'s matched verse) that sur cells align
  1:1 with lyric syllables — but three concrete gaps exist: no per-beat lyric-alignment
  rule is ever stated, taal-bol (rhythm syllables) has no field anywhere in the schema,
  and (partially resolved) the bold "S" cells — **Daljot confirmed: "S" means hold the
  sur** (a sustain marker) — plus the non-linear beat usage seen in one example is now
  explained (a shabad line conventionally restarts at matra 9 of a 16-matra taal rather
  than continuing from the previous line's matra 9, ~99% of the time), not a random
  encoding gap. **Still gated**: the beat-alignment and taal-bol gaps remain, so the
  taal-grid transcription tool (Guru Gobind Singh Ji Di Bani, Sampurn 55 Parhtala) is
  still not built. **Raag Da Saroup Complete is a separate, unblocked path** (below) —
  its entries don't hit any of these three gaps.
- **Raag-entry proof-of-concept built** (`tools/raag-entry.html`): for each of the 62
  Raag Da Saroup Complete items, shows the crop image(s) + prefilled raw-OCR reference +
  a structured form (names, thaat, jati, vadi, samvadi, varjit, time, aroh, avroh, pakad,
  plus a passthrough field for the book's unmapped "Sur" field), with a live SARGAM
  render-back preview, saving to `localStorage` and exporting schema-shaped
  `data/raags.json` JSON. Verified working end-to-end in a real browser (not just read —
  actually driven with Puppeteer): sidebar navigation, image loading, live preview,
  save/export all confirmed. One real bug found by that testing and fixed: prefilled OCR
  fields didn't select-all on focus, so a normal click-and-type would append a
  correction after the stale OCR guess instead of replacing it.
  - **Schema gap found and filed (GitHub issue #6)**: this book's "Sur" field has no
    confirmed home in `raag.schema.json`/`SCHEMA.md` (values don't consistently match
    `komal`/`teevra`/`vadi`/`samvadi`); "Mukh Ang" plausibly maps to `pakad` but isn't
    confirmed. Not guessed at — captured verbatim in a flagged passthrough field instead.
    - **"Sur" field clarified (Daljot):** it lists which swaras of the raag are
      komal / teevra / shuddh — i.e. the raag's note-set (swar-vistaar), a distinct field,
      not `pakad`. Capture as its own field; do not collapse into an existing one.
    - **"Mukh Ang" researched (2026-07-16):** mainstream raag theory treats *Mukhya
      Ang / Mukh Ang* as **synonymous with Pakad** (both = the essential defining
      phrase/notes; "pakad is also known as mukhyaanga"), whereas *Chalan* is the broader
      full-movement grammar. So `Mukh Ang → pakad` is the conventional mapping (nuance:
      mukhya-ang may hold a small *set* of phrases, so long multi-phrase entries edge
      toward chalan). Recommend mapping to `pakad`, keeping raw text verbatim, Ustaad-ji to
      confirm. Sources: ragajunglism.org glossary, tanarang.com, Wikipedia Pakad/Chalan.
  - **2 demo entries wired up** (Siree Raag, Raag Gauri) in `data/raags.json`, via the
    real tool, `status: "draft"`. Deliberately conservative: only non-sur fields
    (thaat/jati/samvadi/varjit/time) were filled from reading the page text; **Aroh/
    Avroh/Pakad were left empty** rather than have AI assert a sur transcription — the
    raw OCR guess for those fields is preserved in `notes` only, clearly labeled
    unverified. The 60 remaining items are untouched, waiting on a human with the tool.
  - **Sub-raag hierarchy fixed (2026-07-16), item count 58 → 62 (confirmed by Daljot's
    manual count of the book):** root cause was `guess_raag()` in `extraction_common.py`
    only capturing the *first* raag heading per page and stamping it on every block that
    page, so sub-raag entries (e.g. Gauri's 3.1-3.11) all silently inherited the parent
    raag's name. Fixed with a new pass, `attach_raag_da_saroup_numbering()` in
    `cluster_blocks.py`, that reads each page's numbered heading ("1.", "2.1", down to 3
    levels deep — "4.1.1") and attaches `raag_number`/`parent_raag_number`/
    `raag_name_as_printed` to each item — nothing fabricated, numbers are either verbatim
    off the OCR'd page prose, or — where OCR dropped a heading line entirely (6 items:
    `3.6`, `3.8`, `3.10`, `15.1`, `16`, `28`) — **confirmed by rendering the actual source
    PDF page with `pdftoppm` and reading it directly**, not just inferred from sequence.
    Found and fixed 4 real over-merges this way (pages 10, 15, 16, 20 — each packed 2
    raags into 1 cluster). Initially misdiagnosed 3 of those (pages 15/16/20) as needing
    human review for suspected column-order OCR scrambling — rendering the actual pages
    showed they're clean and single-column; the scrambling was an artifact of full-page
    OCR text, not the real layout. Every item now has a confirmed number/parent/name, zero
    left unresolved. Full writeup: `books/extracted/MANIFEST.md`'s "Raag Da Saroup's
    numbering/hierarchy" section. Schema question filed as **issue #9** (no
    `parentRaag`/`raagNumber` field exists in `raag.schema.json` yet — Baljeet call);
    issue #10 (the column-scrambling theory) closed as a mis-diagnosis. Tool sidebar
    (`tools/raag-entry.html`) shows the numbering, indented by nesting depth.
  - **Cross-checked against the 60 canonical Gurbani raags (Daljot, 2026-07-16):** all 60
    matched a book item 1:1. The 62 vs 60 difference is **3 extras + 1 missing** (net +2),
    not a clean 2 extras — verified against the rendered source pages, not assumed:
    - Extras (real headings in this book, not among the 60 Gurbani raags): `6.1 ਰਾਗ
      ਦੇਵਗੰਧਾਰ` (Devgandhar), `16.2 ਰਾਗ ਬਿਲਾਵਲ ਮੰਗਲ` (Bilaval Mangal), `4.1.1 ਰਾਗ ਆਸਾਵਰੀ
      ਸੁਪੰਗ` (Asavari Supang — checked closely since it sits where the canonical list has
      "Asa Asavari"; rendered page 9 directly and confirmed the printed heading really
      says ਸੁਪੰਗ, not an OCR misread of ਆਸਾ).
    - Missing: **Asa Asavari** (canonical #20, SGGS p.409) — no entry anywhere in this
      book. The Asa family here goes 4 → 4.1 → 4.1.1 → 4.2 with no gap in the numbering,
      so this looks like the source book itself never covered this raag (an editorial
      scope difference — this book is a general raga reference, not specifically an SGGS
      raag index — not an extraction bug).
  - **Gurmukhi komal/teevra display bug fixed:** the Gurmukhi render map in both
    `tools/raag-entry.html` and `demo/index.html` collapsed komal (`r g d n`) and teevra
    (`m`) onto the same glyph as shuddh, making them visually indistinguishable — despite
    the canonical ASCII storage being correctly case-sensitive per SARGAM.md (display-only
    bug). Fixed with a CSS flexbox-wrapped mark (underline for komal, overline for teevra)
    — plain `text-decoration`/`border` on the span didn't render reliably given Gurmukhi
    font ascent metrics, confirmed via headless-Chrome screenshots before landing on the
    flex approach. SARGAM.md doesn't state an exact Gurmukhi marking convention, so this
    implements the standard one and flags it as **issue #8** for SARGAM.md to document.
  - **Entry-tool UX overhaul DONE (2026-07-17, commit `bb2163f`)**: rewrote
    `tools/raag-entry.html` around the real workflow of transcribing 60+ entries, after
    testing every interaction in a real browser (not just reading the code). Fixed a real
    data-loss bug — typing did nothing until an explicit "Save as draft" click, so
    navigating away first silently discarded it; now every field autosaves per keystroke.
    Also fixed a related correctness quirk where one full-form save made every OCR-
    prefilled field look "verified" even if a human never touched it. Added: a live
    warning when a sur field (Aroh/Avroh/Pakad) still contains Gurmukhi script (the single
    most likely real mistake — canonical SARGAM is Roman-only); click-to-zoom lightbox on
    crop images; a parent breadcrumb for sub-raags (e.g. 3.1 → 3) so Thaat/Vadi can be
    cross-checked against the base raag; Prev/Next navigation (buttons + arrow keys);
    sidebar search + filter chips (All/To do/Reviewed/Flagged) + a real progress bar; an
    explicit "Mark as reviewed" step separate from autosave, so progress reflects human
    confidence, not just "some field has a value"; the header now shows the raag's actual
    name, not just the manifest ID; and download/restore of a full local-progress JSON
    backup, so a contributor's work survives a cleared cache and can be handed off/merged
    — previously `localStorage` was a single point of failure with no way out. **The tool
    is ready for transcription to begin.** No data-model or export-shape changes.
  - **`plan.html` added** — a single-page live progress tracker (fetches `data/raags.json`
    client-side for transcribed/approved counts) alongside the roadmap, critical path, and
    parked items already tracked here. Companion view, not a replacement for this file.
- **Asees-font legacy mapping: partial breakthrough, not yet applied.** Contrary to Phase
  A's "0% confidence, unmapped" conclusion, bridging through a downloaded `.gmf` mapping
  table (`custom-font-mapping/mapping.sgphar.0.5`) before `gurmukhi-utils` recovers real
  Gurmukhi prose (verified against a rendered page: `ਗੁਰੂ ਨਾਨਕ ਦੇਵ` came out exactly right).
  Three known, bounded residual errors remain (a vowel-sign/consonant ambiguity on bare
  `h`, a ਨ/ਣ nasal mixup, one missing ਸ਼ rule) — see
  `books/extracted/_sample/PHASE_A_ASEES_REVALIDATION.md`. Not yet run across the full
  767/780-page Guru Nanak Bani volumes; still held.

## Extraction status (7 books)

- **4 in-scope — Phase B extraction DONE:** Guru Gobind Singh Ji Di Bani (131pp, 68
  notation blocks, 55 high-confidence shabad matches), Asa Di Vaar (217pp, 167 blocks,
  6 matches), 2 Sampurn 55 Parhtala (228pp, 330 blocks, 3 matches), Raag Da Saroup
  Complete (31pp, 184 blocks, 0 matches — raag-reference data, not shabad lyrics, so no
  matching applies). Per-book method/quirks: `books/extracted/EXTRACTION.md`.
- **3 held (font problems):** Guru Tegh Bahadur Ji (silent wrong-letter substitution in a
  CID font — fluent but incorrect), Guru Nanak Bani Vol. I & II (Asees legacy font — a
  partial machine-assisted fix now exists, see above, but not yet run at scale).
- **Notation is NOT auto-extracted as trustworthy data anywhere** — a deliberate safety
  choice, held through Phase B. All 749 notation blocks are cropped as page images and
  flagged `needs_manual_transcription: true` unconditionally, regardless of how clean the
  block's raw OCR/converted text looked. Automated sur text is a rough aid for the human
  transcriber only, never treated as data.
- **Bani text is not stored** by this dataset — shabads are referenced by `shabadId`
  (via BaniDB, see above). Books are used only to (a) identify the shabad (fuzzy-match,
  store the resolved `shabadId`, or leave `null` + flag for manual ID if no confident
  match) and (b) capture its notation/raag. Low match rates in the OCR books (Asa Di
  Vaar, Sampurn 55 Parhtala) mostly reflect blocks that aren't full identifiable
  first-lines to begin with (table fragments, raag/taal labels), not matching failures.

## Plan / roadmap

1. ~~Phase B extraction (4 in-scope books)~~ **DONE**, merged to `main`.
2. ~~Block-clustering (749 raw blocks → real transcription items)~~ **DONE.**
   `books/extracted/manifest.json` / `MANIFEST.md`.
3. **Transcription workflow — taal-grid tool (Guru Gobind Singh Ji Di Bani, Sampurn 55):
   still BLOCKED on issue #4.** Don't build that data-entry format until it's resolved.
   ~~Raag-entry tool (Raag Da Saroup Complete)~~ **DONE, including the UX overhaul
   (2026-07-17, commit `bb2163f`):** `tools/raag-entry.html` — cropped image(s) +
   prefilled raw OCR + structured form + live SARGAM render-back preview +
   `data/raags.json` export, now with autosave, a live Gurmukhi-in-sur-field warning,
   image zoom, parent breadcrumbs, prev/next nav, search/filter, an explicit reviewed
   marker, and backup/restore. Verified working end-to-end in a real browser. **Ready for
   human transcription to begin.** 2 of 62 items wired up as a demo (non-sur fields only —
   see Current State); 60 remain for a human with the tool. Schema gaps found along the
   way: issue #6 ("Sur" field / "Mukh Ang"→`pakad` mapping) and issue #9 (raag
   hierarchy/`parentRaag` field) — Baljeet's call, not blocking the tool.
4. **v0.1 target (reaffirmed core slice):** **Raag Da Saroup Complete (62 real raag-entry
   items) is the v0.1 core** — unblocked, data reconciled, tool built and ready. Sampurn 55
   Parhtala (61 real shabad-notation items) is a secondary v0.1-scope book but stays
   blocked on issue #4's taal-grid gaps, so it does not gate Raag Da Saroup starting.
   Publish Raag Da Saroup as `draft` first, then Ustaad-ji-approved.
   - **Sequencing note: Raag Da Saroup is NOT blocked by issue #4.** Its entries are
     raag-reference fields (Thaat/Jaati/Vaadi/Samvadi/Aroh/Avroh/Mukh Ang) — single-line
     Aroh/Avroh sur with no taal grid, no lyric syllables, and no bold-`S` cell, so all
     three issue-#4 gaps (beat↔syllable alignment, `S` semantics, taal-bol) are moot. It
     can therefore be the **first proof-of-concept slice** — the tool now exists;
     transcribe the remaining 60, get Ustaad-ji approval, publish the first `approved`
     records, wire into the reference site — all *while* the taal-grid books (Sampurn 55,
     Guru Gobind) wait on issue #4.
5. **Approval:** sit with Ustaad ji; he confirms entries; flip `draft` → `approved`.
6. **Full corpus:** incremental / community-fed (esp. the two large Guru Nanak volumes —
   the Asees partial-fix above may unblock these sooner than expected, pending the 3
   residual issues being resolved and a full-volume run).
7. **Consume from ShabadSwar** once schema is signed off + first approved data exists.

## Effort estimate (sharpened using `manifest.json`'s real item counts — see MANIFEST.md)

- Only real user-time sink is **manual sur transcription**; everything else (extraction,
  schema, site integration) is CVS/Baljeet time.
- ~20 min per shabad-notation, ~10 min per raag-entry (unchanged rates; now applied to
  real item counts, not raw block counts).
- **Full corpus solo: ~170–230 hrs — not the plan.**
- **v0.1 slice (Sampurn 55 [61 items] + Raag Da Saroup [62 items]): ~30 hrs** (61×20min +
  62×10min), splittable → ~10–15 hrs personal share with 1–2 helpers. Slightly higher
  than the earlier rough ~23hr guess, same order of magnitude.
- **Guru Gobind Singh Ji Di Bani (61 shabad-notations + 2 taal-reference legends):
  ~21 hrs.**
- **Asa Di Vaar (120 items): NOT confidently estimable yet.** This book's clustering is
  the least trustworthy (104/120 items are single-block, low-confidence — see
  MANIFEST.md) and mixes substantial bordered-table items (~20min each) with much
  shorter inline-notation-line items (~5min each) that the current item list doesn't
  distinguish by expected effort. Rough range: **15–40 hrs**, needs a human pass over
  `manifest.json` (or the transcription tool, once built) to narrow.
- **4 in-scope books, all together: roughly 65–90 hrs** (21 + 30 + 15-to-40) — **higher
  than the earlier pre-Phase-B ~50hr guess**, driven mostly by Asa Di Vaar's uncertainty
  and by the real item counts (302) landing a bit above the very rough original guesses.
- **Timeline:** revisit the "~6-8 weeks to v0.1" estimate — the v0.1 slice itself
  (Sampurn 55 + Raag Da Saroup, ~30hrs) still fits a similar timeline at ~5hrs/wk
  combined; the *4-book* timeline should be treated as loosely-held until Asa Di Vaar's
  range narrows.

## Open decisions / dependencies (human-gated)

- **Notation data-model gap (GitHub issue #4)** — hand-encoded real taal-grid crops into
  SARGAM strings; found 3 concrete gaps. **1 of 3 resolved (now with an external
  citation)**: "S" = elongate/sustain — Daljot's reading, corroborated by a standard
  Bhatkhande-based reference (raag-hindustani.com: "a symbol resembling a large 'S' ...
  elongated or sustained"); the matra-9 restart layout is documented in the same source
  (bandish beginning on the 9th Teentaal beat is notated from column 9, each line its own
  lyric+notation rows), so it's a standard convention, not a gap. **2 still open, both for
  Baljeet**: (a) state the beat↔syllable alignment rule explicitly (the reference confirms
  the "which syllable to which beat" model; our spec just never writes it down), and (b)
  add a `taalBol` field (the traditional system has a dedicated rhythm-marker row). Does
  not block Raag Da Saroup's tool (built, above) or anything already done.
- **Raag field-mapping gap (GitHub issue #6)** — **now largely answered, pending Baljeet
  sign-off.** "Sur" (Daljot): lists which swaras are komal/teevra/shuddh — the raag's
  note-set; keep as its own field, don't fold into `pakad`. "Mukh Ang" (researched
  2026-07-16): mainstream theory treats Mukh Ang / Mukhya Ang as synonymous with *pakad*
  (Chalan is the broader movement grammar), so `Mukh Ang → pakad` is the conventional
  mapping — recommend it, keep raw text verbatim, Ustaad ji to confirm. Doesn't block the
  tool (passthrough field).
- **Ustaad-ji confirmations (working rules, documented but not authority-confirmed)** —
  the matra-9 *universality* ("shabad lines ~always start at matra 9 in 16-matra taal") is
  Daljot's personal-experience rule: the *mechanism* is documented but the ~99% frequency
  is parampara-specific and Teentaal-16-specific (other taals have different sam/khali).
  Batch with the `Mukh Ang → pakad` confirmation for his review.
- **Reference-implementation domain not finalized** — docs say `ShabadSwar.com`; the live
  Gurbani-search site is currently pointed at `GurbaniSargam.com`. Not settled; don't
  mass-rename the docs until it is.
- **Offline shabad-ID source (issue #3)** — bundle the Shabad OS SQLite vs. call BaniDB
  live. Gated on the reference site's hosting setup. Not on the critical path.
- **Asees→Unicode mapping** — a partial machine-assisted path now exists (see above), but
  still ask Anmol whether the digitizer has a cleaner conversion table or the original
  word-processor source, which could resolve the 3 remaining residual error classes
  outright. Blocks the full Guru Nanak Vol. I & II run. Not on critical path.
- **Silent-substitution CID font** (Guru Tegh Bahadur, Asa Di Vaar) — no clean fix; use OCR
  + BaniDB cross-check; never let raw extracted text reach non-draft.
- **Asa Di Vaar's item count needs a human pass** — 120 clustered items, but 104 are
  single-block/low-confidence; effort estimate for this book is a 15-40hr range pending
  review. See MANIFEST.md.
- **Baljeet** — technical schema review (now has three concrete items queued: shabad-ID
  format already fixed for review, notation data-model gap in issue #4, raag field-mapping
  gap in issue #6); gates populating canonical `data/*.json`.
- **Anmol** — remaining vision/faithfulness questions (expected end of week), multiplicity
  framing, governance (who may approve).
- **Licensing** — CC BY-NC 4.0 proposed; needs the family's explicit blessing before publishing.
- **Repo visibility** — currently private; `books/` holds Ustaad ji's published works —
  confirm before making public.
