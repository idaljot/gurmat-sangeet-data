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
  (proposed CC BY-NC 4.0), empty `data/*.json`, stub `schema/*.json`, and the 7 source
  PDFs in `books/`.
- **Ma convention SETTLED (shuddha-set):** `M` = shuddh, `m` = teevra. Scripts: Roman +
  Gurmukhi only (Bhatkhande dropped).
- **Extraction Phase A (calibration) done**; see `books/extracted/_sample/PHASE_A_REPORT.md`.
- **Extraction Phase B (full run, 4 in-scope books) done and merged to `main`** (PR #2).
  See `books/extracted/EXTRACTION.md`. 607 pages, 749 notation blocks extracted (all
  `status: draft`, all flagged `needs_manual_transcription`).
- **Block-clustering done**: the 749 raw blocks are now clustered into **302 real
  transcription items** in `books/extracted/manifest.json` — see `books/extracted/MANIFEST.md`
  for the book-specific clustering logic, and two real over-merge bugs that were found by
  spot-checking crop images and fixed (not left latent). Per-book: Guru Gobind Singh Ji Di
  Bani 63, Asa Di Vaar 120 (least trustworthy grouping — conservative same-page-only),
  Sampurn 55 Parhtala 61, Raag Da Saroup Complete 58. **Use these counts, not the 749
  raw-block count, for effort planning.**
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
  rule is ever stated, the bold "S" cells' meaning (sustain? literal Sa-as-syllable?) is
  genuinely ambiguous from the source alone, and taal-bol (rhythm syllables) has no field
  anywhere in the schema. **Do not build the transcription tool's data-entry format until
  this gets a look from Baljeet** (and, for the musical-semantics question, Ustaad ji) —
  everything else (extraction, clustering) is unaffected and can proceed.
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
3. **Transcription workflow** — build a simple tool: cropped notation images + a structured
   entry form that outputs schema-ready JSON. Goal: make the manual step low-effort and
   splittable among classmates. **Blocked on issue #4** (notation data-model gap) — don't
   build the data-entry format until that's resolved, to avoid redoing entered data.
4. **v0.1 target (recommended scope):** Sampurn 55 Parhtala (61 real shabad-notation
   items, per `manifest.json`) + Raag Da Saroup (58 real raag-entry items). Publish as
   `draft`, then Ustaad-ji-approved.
   - **Sequencing note: Raag Da Saroup is NOT blocked by issue #4.** Its entries are
     raag-reference fields (Thaat/Jaati/Vaadi/Samvadi/Aroh/Avroh/Mukh Ang) — single-line
     Aroh/Avroh sur with no taal grid, no lyric syllables, and no bold-`S` cell, so all
     three issue-#4 gaps (beat↔syllable alignment, `S` semantics, taal-bol) are moot. It
     can therefore be the **first proof-of-concept slice** — build the raag-entry tool,
     transcribe, get Ustaad-ji approval, publish the first `approved` records, wire into
     the reference site — all *while* the taal-grid books (Sampurn 55, Guru Gobind) wait on
     issue #4. Only remaining gate for it is a light confirmation of `raag.schema.json`'s
     fields (Baljeet), which is far smaller than the notation-model question.
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
- **v0.1 slice (Sampurn 55 [61 items] + Raag Da Saroup [58 items]): ~30 hrs** (61×20min +
  58×10min), splittable → ~10–15 hrs personal share with 1–2 helpers. Slightly higher
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
  SARGAM strings; found 3 concrete gaps (no stated lyric-alignment rule, ambiguous `S`-cell
  semantics needing a musical answer, no field for taal-bol). **Blocks the transcription
  tool's data-entry format** — doesn't block anything already done (extraction,
  clustering). Needs Baljeet (schema) and ideally Ustaad ji (the `S`-cell semantics
  question specifically).
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
- **Baljeet** — technical schema review (now has two concrete items queued: shabad-ID
  format already fixed for review, notation data-model gap in issue #4); gates populating
  canonical `data/*.json`.
- **Anmol** — remaining vision/faithfulness questions (expected end of week), multiplicity
  framing, governance (who may approve).
- **Licensing** — CC BY-NC 4.0 proposed; needs the family's explicit blessing before publishing.
- **Repo visibility** — currently private; `books/` holds Ustaad ji's published works —
  confirm before making public.
