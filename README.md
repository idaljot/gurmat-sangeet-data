# Gurmat Sangeet Notation Dataset

> ⚠️ **DRAFT FOR REVIEW — not yet published as canonical.**
> This repository is being circulated for review by Bhai Jaspal Singh Ji's family
> and for technical review before it is published. The schema, licensing, and data
> are all provisional. Please do not treat any data here as authoritative yet.

An open, structured dataset of **raag reference data** and **kirtan swar (sur)
notation** from the parampara of **Bhai Jaspal Singh Ji**.

This is a **data** repository, not an application — any project can consume it. The
first consumer and reference implementation is [ShabadSwar.com](https://shabadswar.com).

## Why this exists

Ustaad ji's raag and notation work is a teaching treasure that currently lives in
books, classes, and individual memory. This dataset makes it **structured, machine-
readable, and reusable** so that any website, app, or study tool can present it
faithfully — with clear attribution and a built-in distinction between what Ustaad ji
has personally approved and what is still unverified.

## What's here

| File | What it is |
|------|------------|
| [`SCHEMA.md`](SCHEMA.md) | The data contract — the authoritative description of every field. **Start here.** |
| [`SARGAM.md`](SARGAM.md) | How to read a notation string (the sur/taal spec). |
| [`data/raags.json`](data/raags.json) | Raag reference data (scales, character, resources). |
| [`data/notations.json`](data/notations.json) | Kirtan compositions (sur + taal) for shabads. |
| [`data/sources.json`](data/sources.json) | Provenance registry (books, classes, contributors). |
| [`schema/`](schema/) | JSON Schemas for validating the data files. |

The `data/` files are currently **empty containers** — real data is added only after
the schema is approved and Ustaad ji's material is available.

## How to use it (once published)

1. Fetch the JSON file(s) you need directly from this repo (raw URLs or a release tag).
2. Read `SCHEMA.md` for the field meanings and `SARGAM.md` to interpret notation strings.
3. **Filter by `status`.** Show `approved` records as authoritative; visibly mark
   `draft` records as unverified. Never let unverified data masquerade as Ustaad ji's
   confirmed work.
4. Notation is stored once as a canonical ASCII string; render it in whatever script
   (Roman / Bhatkhande / Gurmukhi) your users need.

## Data integrity

Every record carries `status` (`approved` | `draft`), and approved records also carry
`reviewedBy` and `reviewedOn`. This provenance backbone is what makes the dataset
*trustworthy*, not merely *available*. See `SCHEMA.md` → "Review status."

## License (proposed — pending the family's blessing)

Proposed: **CC BY-NC 4.0** — free to use and adapt for **non-commercial** purposes
with **attribution to Bhai Jaspal Singh Ji**. This matches the license on ShabadSwar.com.

This is *proposed*, not settled. Because this is Ustaad ji's work and his name, the
license is his family's decision. An alternative under consideration is CC BY-SA 4.0
(wider reach — permits commercial use but keeps derivatives open). See `SCHEMA.md` →
"Licensing" for the tradeoffs. The Gurbani text itself is public domain; this license
would cover only the notation, raag data, and compilation.

## Status & how to help review

This is a **request for review**, not a finished release. Open questions are listed at
the bottom of `SCHEMA.md` (multiplicity framing, the Ma convention, `verseId`,
governance, taal data, license). Feedback especially welcome on:

- **Technical:** does the schema parse cleanly? Anything over- or under-designed?
- **Tradition & authority:** does the structure represent the parampara faithfully?
  Who governs `approved` status? Is the licensing right?

Open an issue or send notes directly. Thank you for helping get the foundation right.
