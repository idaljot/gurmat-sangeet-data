# MANIFEST.md — block-clustering methodology and results

`books/extracted/manifest.json` turns Phase B's 749 raw notation "blocks" (extraction
units — a table-detection region or an inline notation line) into **302 real
transcription items**. A block is not a transcription unit: a single shabad's notation
often spans several detected blocks (multiple pages, or multiple sub-regions per page),
and a single raag-reference entry in *Raag Da Saroup Complete* is made of several
separate field-blocks (Sur, Aroh, Avroh, etc.). This file documents how blocks were
grouped into items, and — as important — where that grouping is uncertain.

**Status: draft compute output. No transcription has happened. Every item still routes
to manual transcription regardless of clustering confidence.**

## Headline: true per-book item counts

| Book | Raw blocks | Clustered items | Item type | Confidence (high/medium/low) |
|---|---|---|---|---|
| Guru Gobind Singh Ji Di Bani | 68 | 63 | 61 shabad-notation + 2 taal-reference | 63 / 0 / 0 |
| Asa Di Vaar | 167 | 120 | 120 notation-fragment | 0 / 16 / 104 |
| 2 Sampurn 55 Parhtala | 330 | 61 | 61 shabad-notation | 0 / 60 / 1 |
| Raag Da Saroup Complete | 184 | 58 | 58 raag-entry | 0 / 58 / 0 |
| **Total** | **749** | **302** | | |

Sanity check against Phase A's earlier rough estimates: Sampurn 55 Parhtala's 61 items
lines up well with Phase A's "~55 shabads" guess; Raag Da Saroup's 58 items is roughly
2x Phase A's "~30 raags" guess, which makes sense once you look at the actual pages —
several base raag names have 2-3 variant entries each (confirmed visually), so "~30 raag
*names*" and "~58 raag *entries*" are both correct, just counting different things.

**This changes the effort estimate's unit from "block" to "item" — use these counts, not
the 749 raw-block count, for planning manual transcription work.**

## Why book-specific clustering logic, not one rule

Direct inspection of each book's `notation-raw.json` (not assumption) showed the four
books have genuinely different structure:

- **Guru Gobind Singh Ji Di Bani** — blocks are already close to 1:1 with real
  shabad-notations (one notation table per page, mostly). Clustering here is just
  same-page grouping. The one real wrinkle, found by looking at the crop images
  directly (not inferable from the data fields): **pages 128-129 (7 blocks) are a
  taal-bol reference legend** (explaining Iktaal/Teentaal bol patterns for the reader),
  not shabad notation — hand-excluded from the shabad-notation count and tagged
  `taal-reference` instead.
- **2 Sampurn 55 Parhtala** — a raag heading appears once per composition; later pages
  of the same shabad's notation carry `raag: null` (continuation). Clustered by
  page-adjacency (gap ≤ 1) with the raag carried forward; a new non-null raag, or a
  page gap, starts a new item.
- **Raag Da Saroup Complete** — this book's raag-detail entries follow a fixed field
  order (Thaat, Jaati, Vaadi, Samvaadi, Sur, Varjit Sur, Samay, Aroh, Avroh, Mukh Ang).
  Multiple entries (raag variants) can share one page and one extracted raag label, so
  page/raag alone isn't enough — clustering detects entry boundaries by field order:
  a label whose position in that fixed order is not later than the last-seen label
  signals a new entry has started.
- **Asa Di Vaar** — a single continuous Vaar, one raag (Aasa) throughout, so raag
  carries no distinguishing signal at all here, and there's no shabad_id signal either
  (6/167 blocks matched). **Clustering is deliberately conservative: same-page grouping
  only.** No cross-page merge is attempted — there was no trustworthy signal to justify
  one. This is why 104 of 120 items are single-block, low-confidence: the true
  granularity of "one notation item" in this book needs a human's judgment, not an
  algorithm guessing across unrelated pages.

## Two real over-merges found and fixed by spot-checking (not left latent)

The task asked not to force merges that can't be justified. Two were found only by
opening the actual crop images, not by staring at the extracted fields:

1. **Sampurn 55 Parhtala, pages 219-224 (19 blocks) — a second taal-reference legend**
   near the end of the book got silently absorbed into the preceding raag's cluster,
   because there was no new raag heading or page-gap to signal the boundary (confirmed:
   `page-224-block-2.png` is a taal-bol legend table, X/2/0/3 markers and all — not
   shabad content). No reliable automated way was found to detect this in general
   (the OCR text on legend tables is too noisy to pattern-match), so instead: any
   cluster whose page span is a clear outlier versus the rest of that book's clusters
   is auto-flagged `cluster_confidence: "low"` with an explicit note. One cluster in
   this book was flagged this way (`sampurn-55-parhtala-0059`) — **do not treat it as
   one clean item without manual review; it likely needs splitting.**
2. **Raag Da Saroup Complete, page 23→24 boundary** — the first clustering pass (repeat
   detection only) spliced one entry's *tail* fields (Aroh, Avroh, Mukh Ang) onto the
   *next* entry's *head* fields (Sur, Varjit Sur), because those specific labels hadn't
   been seen yet in the current cluster. Fixed by switching to field-*order* detection
   (a label whose rank in the fixed field sequence goes backward or repeats signals a
   new entry) rather than simple repeat-detection. Verified fixed: the boundary now
   splits cleanly into two separate items.

Both are documented in `books/extracted/_lib/cluster_blocks.py`'s comments at the
exact point they're guarded against, so a future re-run doesn't reintroduce them
silently.

## `manifest.json` record shape

```jsonc
{
  "manifest_id": "sampurn-55-parhtala-0009",
  "book": "sampurn-55-parhtala",
  "item_type": "shabad-notation",       // shabad-notation | raag-entry | taal-reference | notation-fragment
  "cluster_confidence": "medium",       // high | medium | low -- how well-grounded the merge is, NOT transcription quality
  "cluster_basis": "...",               // human-readable explanation of why these blocks were grouped
  "page_range": [27, 31],
  "block_count": 8,
  "images": ["notation/page-027-block-1.png", "..."],
  "shabad_ids": [],                     // resolved BaniDB shabad_id(s), if any block in the cluster matched
  "raags": ["ਰਾਗ ਸਾਰੰਗ"],
  "taals": [],
  "status": "draft",
  "needs_manual_transcription": true    // unconditionally true for every item, regardless of confidence
}
```

`cluster_confidence` is about clustering, not content trust — even a `"high"` confidence
item (e.g. Guru Gobind Singh Ji Di Bani, which is mostly already 1:1) still needs full
manual transcription against its cropped image(s), per the unchanged Phase A/B notation
policy.

## Known limitations (be aware before relying on the counts for scheduling)

1. **Asa Di Vaar's 120 items are the least trustworthy grouping** — same-page-only
   clustering is conservative by design, but that means it may *under*-merge (leaving
   what's really one notation passage split across adjacent pages as separate items) as
   often as it avoids over-merging. Treat 120 as a rough upper bound on item count for
   this book, not a precise figure.
2. The two fixed over-merge bugs were found by spot-checking maybe a dozen clusters
   total, not all 302 — it's plausible similar cases exist elsewhere and weren't caught.
   The outlier-span safety net (bug #1's fix) only fires within a single book's own
   size distribution, so a similarly-shaped problem in a book where it *wouldn't* look
   like an outlier (e.g. if Asa Di Vaar had a legend page that happened to merge into a
   normal-sized cluster) would not be caught by that mechanism.
3. `raw_text`/`raw_sur_row` fields inside each block are still exactly as unreliable as
   documented in `EXTRACTION.md` — clustering doesn't improve their trustworthiness, it
   only groups them.

## Reproducing

`python3 books/extracted/_lib/cluster_blocks.py` (from repo root, with
`.venv-extraction` active) regenerates `manifest.json` from the existing
`notation-raw.json` files. Deterministic — no randomness, no external calls.
