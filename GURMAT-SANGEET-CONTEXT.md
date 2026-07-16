# GURMAT-SANGEET-CONTEXT — project state & plan

Mutable project state, people, plan, and open decisions for the Gurmat Sangeet
Notation Dataset. `CLAUDE.md` holds the stable rules; `SCHEMA.md`/`SARGAM.md` are the
specs; `VISION.md` is the outward-facing why. **This file is the operational tracker** —
update it (and bump the date) whenever state changes.

_Last updated: 2026-07-15_

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
- **Extraction Phase A (calibration) done** on branch `feat-book-extraction`; see
  `books/extracted/_sample/PHASE_A_REPORT.md`. Awaiting Phase B.

## Extraction status (7 books)

- **4 in-scope (reliable prose):** Guru Gobind Singh Ji Di Bani, Asa Di Vaar,
  2 Sampurn 55 Parhtala, Raag Da Saroup Complete.
- **3 held (font problems):** Guru Tegh Bahadur Ji (silent wrong-letter substitution in a
  CID font — fluent but incorrect), Guru Nanak Bani Vol. I & II (unmapped "Asees" legacy
  font; ~half+ of content).
- **Notation is NOT auto-extracted anywhere** — a deliberate safety choice. Automated sur
  hits only ~60–90% (inline Aroh/Avroh lose spacing entirely), which is not safe for sacred
  notation. All sur → **manual transcription** against cropped page images.
- **Bani text is not stored** by this dataset — shabads are referenced by `shabadId`
  (GurbaniNow/SikhiToTheMax). Use the books only to (a) identify the shabad (fuzzy-match to
  GurbaniNow, store the resolved `shabadId`) and (b) capture its notation/raag. This
  sidesteps the substitution bug for bani lines; it only affects secondary non-notation prose.

## Plan / roadmap

1. **Phase B extraction (4 in-scope books)** — CVS. Auto-extract prose/structure into
   `books/extracted/<slug>/` (tagged sections, all `draft`); notation captured as flagged
   page-image references, not transcriptions. Also **output a count of notation blocks per
   book** to make the estimate exact. Held books wait on Asees mapping / substitution fix.
2. **Transcription workflow** — build a simple tool: cropped notation images + a structured
   entry form that outputs schema-ready JSON. Goal: make the manual step low-effort and
   splittable among classmates.
3. **v0.1 target (recommended scope):** Sampurn 55 Parhtala (~55 notations) + Raag Da
   Saroup (~30 raags). Publish as `draft`, then Ustaad-ji-approved.
4. **Approval:** sit with Ustaad ji; he confirms entries; flip `draft` → `approved`.
5. **Full corpus:** incremental / community-fed (esp. the two large Guru Nanak volumes).
   Open-ended by design.
6. **Consume from ShabadSwar** once schema is signed off + first approved data exists.

## Effort estimate (see conversation for detail)

- Only real user-time sink is **manual sur transcription**; everything else (extraction,
  schema, site integration) is CVS/Baljeet time.
- ~20 min per shabad-notation, ~10 min per raag.
- **Full corpus solo: ~170–230 hrs — not the plan.**
- **4 in-scope books: ~50 hrs.**
- **v0.1 slice (Sampurn 55 + Raag Da Saroup): ~23 hrs**, splittable → ~8–12 hrs personal
  share with 1–2 helpers.
- **Timeline:** ~6–8 weeks to an Ustaad-approved v0.1 at light (~5 hrs/wk combined) effort;
  a 10-entry proof-of-concept in ~4 hrs / under a week.
- Make exact via the per-book notation count from Phase B.

## Open decisions / dependencies (human-gated)

- **Asees→Unicode mapping** — ask Anmol whether the digitizer has a conversion table or the
  original word-processor source. Blocks Guru Nanak Vol. I & II. Not on critical path.
- **Silent-substitution CID font** (Guru Tegh Bahadur, Asa Di Vaar) — no clean fix; use OCR
  + GurbaniNow cross-check; never let raw extracted text reach non-draft.
- **Baljeet** — technical schema review; gates populating canonical `data/*.json`.
- **Anmol** — remaining vision/faithfulness questions (expected end of week), multiplicity
  framing, governance (who may approve).
- **Licensing** — CC BY-NC 4.0 proposed; needs the family's explicit blessing before publishing.
- **Repo visibility** — currently private; `books/` holds Ustaad ji's published works —
  confirm before making public.
