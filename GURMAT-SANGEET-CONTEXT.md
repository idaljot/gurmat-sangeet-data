# GURMAT-SANGEET-CONTEXT — project state & plan

Mutable project state, people, plan, and open decisions for the Gurmat Sangeet
Notation Dataset. `CLAUDE.md` holds the stable rules; `SCHEMA.md`/`SARGAM.md` are the
specs; `VISION.md` is the outward-facing why. **This file is the operational tracker** —
update it (and bump the date) whenever state changes.

_Last updated: 2026-07-16_

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
- **Extraction Phase B (full run, 4 in-scope books) done** on branch `feat-book-extraction`;
  see `books/extracted/EXTRACTION.md`. 607 pages, 749 notation blocks extracted (all
  `status: draft`, all flagged `needs_manual_transcription`). Not yet merged/PR'd for
  review as of this update.
- **Shabad identification mechanism corrected**: the plan named "GurbaniNow" — that API
  is dead (deprecated upstream, confirmed non-functional: its own documented example
  query returns zero results). Using **BaniDB** instead (`banidb` PyPI package, same
  ecosystem, actively maintained) via `books/extracted/_lib/shabad_match.py`. Validated
  against a known SGGS line before use.
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

1. ~~Phase B extraction (4 in-scope books)~~ **DONE.** `books/extracted/<slug>/` per book:
   tagged-section page text, `notation-raw.json`, cropped notation images. PR not yet
   opened for review — next step.
2. **Transcription workflow** — build a simple tool: cropped notation images + a structured
   entry form that outputs schema-ready JSON. Goal: make the manual step low-effort and
   splittable among classmates. Now unblocked by real per-book notation counts (below).
3. **v0.1 target (recommended scope):** Sampurn 55 Parhtala (~55 notations, 330 raw
   blocks — several blocks per shabad, needs clustering) + Raag Da Saroup (~30 raags, 184
   raw blocks). Publish as `draft`, then Ustaad-ji-approved.
4. **Approval:** sit with Ustaad ji; he confirms entries; flip `draft` → `approved`.
5. **Full corpus:** incremental / community-fed (esp. the two large Guru Nanak volumes —
   the Asees partial-fix above may unblock these sooner than expected, pending the 3
   residual issues being resolved and a full-volume run).
6. **Consume from ShabadSwar** once schema is signed off + first approved data exists.

## Effort estimate (see conversation for detail)

- Only real user-time sink is **manual sur transcription**; everything else (extraction,
  schema, site integration) is CVS/Baljeet time.
- ~20 min per shabad-notation, ~10 min per raag.
- **Full corpus solo: ~170–230 hrs — not the plan.**
- **4 in-scope books: ~50 hrs** (rough, pre-Phase-B estimate — see caveat below).
- **v0.1 slice (Sampurn 55 + Raag Da Saroup): ~23 hrs**, splittable → ~8–12 hrs personal
  share with 1–2 helpers.
- **Timeline:** ~6–8 weeks to an Ustaad-approved v0.1 at light (~5 hrs/wk combined) effort;
  a 10-entry proof-of-concept in ~4 hrs / under a week.
- **Phase B produced real notation-block counts (749 total: 68 / 167 / 330 / 184 across
  the 4 books) — but a "block" is a raw extraction unit, not a transcription unit.** E.g.
  Sampurn 55 Parhtala has ~55 actual shabads but 330 detected blocks (~6 blocks/shabad on
  average — a table often spans multiple detected regions). Before the ~20-min/~10-min
  per-item estimate above can be sharpened, blocks need clustering into actual
  shabad-notations/raag-entries — a small follow-up task, not done yet. Treat the ~50hr /
  ~23hr figures as still-rough until that clustering happens.

## Open decisions / dependencies (human-gated)

- **Asees→Unicode mapping** — a partial machine-assisted path now exists (see above), but
  still ask Anmol whether the digitizer has a cleaner conversion table or the original
  word-processor source, which could resolve the 3 remaining residual error classes
  outright. Blocks the full Guru Nanak Vol. I & II run. Not on critical path.
- **Silent-substitution CID font** (Guru Tegh Bahadur, Asa Di Vaar) — no clean fix; use OCR
  + BaniDB cross-check; never let raw extracted text reach non-draft.
- **Notation-block → transcription-item clustering** — needed to turn the 749 raw blocks
  from Phase B into an accurate count of actual shabad-notations/raag-entries for the
  effort estimate and the transcription-tool backlog. Small task, not yet done.
- **Baljeet** — technical schema review; gates populating canonical `data/*.json`.
- **Anmol** — remaining vision/faithfulness questions (expected end of week), multiplicity
  framing, governance (who may approve).
- **Licensing** — CC BY-NC 4.0 proposed; needs the family's explicit blessing before publishing.
- **Repo visibility** — currently private; `books/` holds Ustaad ji's published works —
  confirm before making public.
