"""
Block-clustering: turn Phase B's 749 raw notation "blocks" (extraction units) into
real transcription items (shabad-notations, raag-entries, or flagged fragments).

Why book-specific logic, not one blind rule: empirical inspection of each book's
notation-raw.json showed genuinely different structure --

- guru-gobind-singh-ji-di-bani: blocks are already ~1:1 with real shabad-notations
  (68 blocks / 63 unique pages, mostly one block per page). The one exception found
  by spot-checking crops: pages 128-129 (7 blocks) are a TAAL-REFERENCE LEGEND
  (explaining Iktaal/Teentaal bol patterns), not shabad notation -- confirmed by
  viewing the crop images directly, not inferable from the raag/taal fields alone
  (which just show OCR noise there). Hard-excluded from shabad-notation clustering.
- sampurn-55-parhtala: raag heading appears once per composition, then blocks on
  following pages carry raag=None (continuation) until a new raag appears. Cluster by
  page-adjacency (gap<=1) with raag as a carry-forward signal; new raag or gap>1 starts
  a new cluster.
- raag-da-saroup-complete: multiple raag-entries (variants of a base raag family) can
  share one page and one extracted `raag` label -- confirmed by seeing repeated field
  labels (e.g. two "ਅਵਰੋਹ" blocks) within a single page's block sequence. Cluster by
  detecting when a field-type label repeats within the current raag group -- that
  repeat signals a new entry has started.
- asa-di-vaar: single continuous Vaar, all one raag (Aasa) throughout, so raag carries
  no distinguishing signal here. No cross-page signal is trustworthy, so clustering is
  deliberately conservative: only merge blocks on the exact same page. Cross-page
  merges are NOT attempted -- would be an unjustified guess.

Every block ends up in exactly one cluster. Nothing is discarded. Clusters get an
`item_type` (shabad-notation / raag-entry / taal-reference / notation-fragment) and a
`cluster_confidence` (high / medium / low) reflecting how strong the grounding for
that merge was -- NOT a claim about transcription quality (all clusters still route to
manual transcription regardless).
"""

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EXTRACTED = REPO_ROOT / "books" / "extracted"

# Pages visually confirmed (by viewing the crop images) to be a taal-reference legend,
# not shabad-notation content. See notes above -- not detectable from raag/taal fields.
GGSJDB_TAAL_LEGEND_PAGES = {128, 129}


def load_notation(slug):
    return json.load(open(EXTRACTED / slug / "notation-raw.json", encoding="utf-8"))


def field_label(raw_text):
    """Extract the leading label word/phrase from a raag-da-saroup raw_text block,
    e.g. 'ਵਰਜਿਤ ਸੁਰ _ : ਗੰਧਾਰ ਧੈਵਤ' -> 'ਵਰਜਿਤ ਸੁਰ'. Best-effort; returns None if no
    recognizable label prefix is found (block kept in the sequence, just untyped)."""
    if not raw_text:
        return None
    known_labels = [
        "ਵਰਜਿਤ ਸੁਰ", "ਸੁਰ", "ਆਰੋਹ", "ਅਵਰੋਹ", "ਮੁੱਖ ਅੰਗ",
        "ਥਾਟ", "ਜਾਤੀ", "ਵਾਦੀ", "ਸੰਵਾਦੀ", "ਸਮਾਂ",
    ]
    for label in sorted(known_labels, key=len, reverse=True):
        if raw_text.strip().startswith(label):
            return label
    return None


def cluster_guru_gobind_singh(blocks):
    clusters = []
    legend_blocks = [b for b in blocks if b["page"] in GGSJDB_TAAL_LEGEND_PAGES]
    real_blocks = [b for b in blocks if b["page"] not in GGSJDB_TAAL_LEGEND_PAGES]

    # legend blocks: one cluster per page (each page's 3-4 blocks together document
    # one set of taal patterns -- not further distinguishable without per-block visual
    # review of which specific taal each block shows)
    by_page = {}
    for b in legend_blocks:
        by_page.setdefault(b["page"], []).append(b)
    for page, page_blocks in sorted(by_page.items()):
        clusters.append({
            "item_type": "taal-reference",
            "cluster_confidence": "high",
            "cluster_basis": "visually confirmed taal-bol legend page (not shabad notation)",
            "blocks": page_blocks,
        })

    # real shabad-notation blocks: same-page grouping only (this book is already
    # near-1:1, no cross-page merge justified beyond what's on one page together)
    by_page = {}
    for b in real_blocks:
        by_page.setdefault(b["page"], []).append(b)
    for page, page_blocks in sorted(by_page.items()):
        clusters.append({
            "item_type": "shabad-notation",
            "cluster_confidence": "high",
            "cluster_basis": "same-page grouping (book is already ~1:1 blocks:pages)",
            "blocks": page_blocks,
        })
    return clusters


def cluster_sampurn_55(blocks):
    blocks_sorted = sorted(blocks, key=lambda b: (b["page"], b["image"]))
    clusters = []
    current = None
    current_raag = None
    last_page = None

    for b in blocks_sorted:
        raag = b.get("raag")
        page = b["page"]
        starts_new = (
            current is None
            or (last_page is not None and page - last_page > 1)
            or (raag and current_raag and raag != current_raag)
        )
        if starts_new:
            if current is not None:
                clusters.append(current)
            current = {
                "item_type": "shabad-notation",
                "cluster_confidence": "medium",
                "cluster_basis": "page-adjacency (gap<=1) + raag carry-forward",
                "blocks": [],
            }
            current_raag = raag
        elif raag:
            current_raag = raag  # update carried-forward raag if this block names one
        current["blocks"].append(b)
        last_page = page
    if current is not None:
        clusters.append(current)

    # Safety net: spot-checking found a real over-merge case (pages 219-224, 19
    # blocks) where a taal-reference legend appendix at the end of the book got
    # silently absorbed into the preceding raag's cluster because there was no new
    # raag heading or page-gap to signal a boundary. Visually confirmed via crop
    # (page-224-block-2.png is a taal-bol legend table, not shabad content). No
    # reliable text-based signal was found to auto-detect this in general, so flag
    # any similarly-shaped outlier (page span notably larger than the rest of this
    # book's clusters) as low-confidence needing review, rather than claim it's one
    # clean item.
    spans = [c["blocks"][-1]["page"] - c["blocks"][0]["page"] for c in clusters]
    normal_max_span = sorted(spans)[-2] if len(spans) > 1 else 0  # 2nd-largest, robust to one outlier
    for c in clusters:
        span = c["blocks"][-1]["page"] - c["blocks"][0]["page"]
        if span > normal_max_span and span >= 5:
            c["cluster_confidence"] = "low"
            c["cluster_basis"] += (
                " -- FLAGGED: page span far exceeds this book's other clusters; spot-"
                "checking found an analogous case is a taal-reference legend wrongly "
                "merged with adjacent shabad content, not one clean item. Needs human "
                "review before treating as a single transcription item -- may need "
                "manual splitting."
            )
    return clusters


# Fixed field order per Phase A's documented structure for this book. Used to detect
# entry boundaries: within one legitimate raag-entry, field labels appear in this
# order (not necessarily all present, but never backward/repeated). Seeing a label
# whose rank is <= the last-seen rank means we've wrapped into a new entry -- this
# catches both exact repeats AND the subtler case of a new entry's *early* fields
# (e.g. "ਸੁਰ") following the previous entry's *late* fields (e.g. "ਮੁੱਖ ਅੰਗ"), which a
# simple repeat-check misses. Found by spot-checking (page 23/24 boundary: a cluster
# wrongly spliced one entry's Aroh/Avroh/Mukh Ang tail onto the next entry's Sur/
# Varjit-Sur head).
FIELD_ORDER = ["ਥਾਟ", "ਜਾਤੀ", "ਵਾਦੀ", "ਸੰਵਾਦੀ", "ਸੁਰ", "ਵਰਜਿਤ ਸੁਰ", "ਸਮਾਂ", "ਆਰੋਹ", "ਅਵਰੋਹ", "ਮੁੱਖ ਅੰਗ"]
FIELD_RANK = {label: i for i, label in enumerate(FIELD_ORDER)}

# These pages packed 2 raag entries' blocks into 1 cluster because field-order detection
# never saw a recognizable early-order label after the boundary. Confirmed by rendering
# the actual source PDF pages (pdftoppm) and reading them directly -- every one of these
# is a clean, single-column, unambiguous page; the earlier suspicion of column-order OCR
# scrambling (filed as issue #10) was a mis-diagnosis caused by relying on the full-page
# tesseract text (which *does* garble reading order on some pages) instead of the actual
# rendered page image. Each split point below is grounded in matching a block's raw text
# against the correct raag's field values as read from the rendered page:
#   page 10: "5. ਰਾਗ ਗੁਜਰੀ" | "6. ਰਾਗ ਦੇਵਗੰਧਾਰੀ" -- block 3 ("ਗੰਧਾਰ, ਨਿਸ਼ਾਦ ਆਰੋਹ") is raag 6's
#     Varjit Sur value.
#   page 15: "13. ਰਾਗ ਬੈਰਾੜੀ" | "14. ਰਾਗ ਤਿਲੰਗ" -- block 3 ("ਠੀ ਸਗ ਮਪ,ਨੀ ਪ, ਗਮ ਗ,ਸ") matches
#     raag 14's Mukh Ang value.
#   page 16: "14.1 ਰਾਗ ਤਿਲੰਗ ਕਾਫੀ" | "15. ਰਾਗ ਸੂਹੀ" -- block 1 is 14.1's Mukh Ang value;
#     block 2 (bare "ਮੁੱਖ ਅੰਗ") is raag 15's own Mukh Ang label (value not captured).
#   page 20: "17.1 ਰਾਗ ਬਿਲਾਵਲ ਗੋਂਡ" | "18. ਰਾਗ ਰਾਮਕਲੀ" -- block 2 ("ਆਰੋਹ ਵਿਚ ਰਿਸ਼ਭ") matches
#     raag 18's Varjit Sur value.
RAAG_DA_SAROUP_MANUAL_SPLITS = {
    "notation/page-010-block-3.png",
    "notation/page-015-block-3.png",
    "notation/page-016-block-2.png",
    # page 20 block 1 (bare "ਮੁਖ ਅੰਗ") would otherwise get absorbed into the still-open
    # "17. ਰਾਗ ਗੋਂਡ" cluster carried over from page 19 (whose own Mukh Ang value is
    # already complete there) -- it's actually 17.1's label, so it needs its own split
    # too, not just a split before block 2.
    "notation/page-020-block-1.png",
    "notation/page-020-block-2.png",
}


def cluster_raag_da_saroup(blocks):
    blocks_sorted = sorted(blocks, key=lambda b: (b["page"], b["image"]))
    clusters = []
    current = None
    last_rank = -1
    current_raag = None

    for b in blocks_sorted:
        raag = b.get("raag")
        label = field_label(b.get("raw_text"))
        rank = FIELD_RANK.get(label) if label else None
        starts_new = (
            current is None
            or (raag and current_raag and raag != current_raag)
            or (rank is not None and rank <= last_rank)
            or b["image"] in RAAG_DA_SAROUP_MANUAL_SPLITS
        )
        if starts_new:
            if current is not None:
                clusters.append(current)
            current = {
                "item_type": "raag-entry",
                "cluster_confidence": "medium",
                "cluster_basis": "field-order-based entry-boundary detection within raag group",
                "blocks": [],
            }
            last_rank = -1
            current_raag = raag
        if rank is not None:
            last_rank = rank
        if raag:
            current_raag = raag
        current["blocks"].append(b)
    if current is not None:
        clusters.append(current)
    return clusters


# Raag Da Saroup Complete numbers its raags hierarchically in the printed book: "1.
# Raag A", "2. Raag B", "2.1 Raag B sub-raag", "2.1.1 ..." etc. That numbering isn't in
# notation-raw.json (block-level crops only capture field label:value pairs, not
# headings) -- it only survives in each page's full-page prose text
# (books/extracted/raag-da-saroup-complete/pages/page-NNN.json). This section attaches
# it to already-clustered raag-entry items as a best-effort, non-fabricating pass: every
# number attached is either read verbatim from a heading, or -- where OCR dropped a
# heading outright -- inferred ONLY when the surrounding sequence makes the missing
# ordinal unambiguous (never a guess about raag *content*, just which position an
# already-fully-clustered entry occupies).
RAAG_HEADING_RE = re.compile(r"^(\d+(?:\.\d+)*)\.?\s+(ਰਾਗ.*)$")


def extract_raag_headings(slug):
    """page_no -> ordered list of (number_str, name_str) parsed from that page's
    extracted prose. Best-effort regex match on numbered raag headings (e.g. '3.1
    ਰਾਗੁ ਗਉੜੀ ਗੁਆਰੇਰੀ'); returns exactly what's printed, nothing invented."""
    pages_dir = EXTRACTED / slug / "pages"
    headings = {}
    for page_path in sorted(pages_dir.glob("page-*.json")):
        page_no = int(re.search(r"page-(\d+)", page_path.stem).group(1))
        text = json.load(open(page_path, encoding="utf-8"))["text"]
        found = []
        for line in text.split("\n"):
            m = RAAG_HEADING_RE.match(line.strip())
            if m:
                found.append((m.group(1), m.group(2).strip()))
        headings[page_no] = found
    return headings


def parent_raag_number(number):
    if number is None or "." not in number:
        return None
    return number.rsplit(".", 1)[0]


# Numbers/names this book's OCR text layer dropped entirely (no heading line in
# notation-raw.json's page prose), even though the entry's own field content is present
# and complete on the page. Originally found by sequence (e.g. 3.5 then 3.7, nothing
# else between -- so 3.6 is the only possibility) and left nameless; **confirmed
# verbatim, name included, by rendering the actual source PDF page with `pdftoppm` and
# reading it directly** (`pdftoppm -r 200 -f N -l N -png "books/Raag Da Saroup
# Complete.pdf" out`) -- the printed heading is there, tesseract's text extraction just
# missed it on these specific pages.
RAAG_DA_SAROUP_GAP_NUMBERS = {
    5: ("3.6", "ਰਾਗੁ ਗਉੜੀ ਪੂਰਬੀ ਦੀਪਕੀ"),   # between 3.5 (page 4) and 3.7 (page 5)
    6: ("3.8", "ਰਾਗ ਗਉੜੀ ਮਾਝ"),           # between 3.7 (page 5) and 3.9 (page 6)
    7: ("3.10", "ਰਾਗ ਗਉੜੀ ਮਾਲਾ"),         # between 3.9 (page 6) and 3.11 (page 7)
    17: ("15.1", "ਰਾਗ ਸੂਹੀ ਕਾਫੀ"),        # between 15 (page 16) and 15.2 (page 17)
    18: ("16", "ਰਾਗ ਬਿਲਾਵਲੁ"),            # between 16.2/17 (page 19) and 16.1 (same page)
    28: ("28", "ਰਾਗ ਕਾਨੜਾ"),              # between 27 (page 27) and 29 (page 28)
}


def attach_raag_da_saroup_numbering(items):
    """Mutates raag-da-saroup-complete manifest items in place, adding raag_number /
    parent_raag_number / raag_name_as_printed (or an explicit review flag when the
    numbering can't be safely attached). See module docstring above."""
    headings_by_page = extract_raag_headings("raag-da-saroup-complete")
    items_by_start_page = {}
    for it in items:
        items_by_start_page.setdefault(it["page_range"][0], []).append(it)

    def blank(it, note, needs_review):
        it["raag_number"] = None
        it["raag_name_as_printed"] = None
        it["parent_raag_number"] = None
        it["raag_number_inferred"] = False
        it["needs_split_review"] = needs_review
        it["numbering_note"] = note

    for page_no, page_items in items_by_start_page.items():
        page_headings = headings_by_page.get(page_no, [])

        remaining = page_items
        if len(page_items) == len(page_headings) + 1 and page_no in RAAG_DA_SAROUP_GAP_NUMBERS:
            gap_number, gap_name = RAAG_DA_SAROUP_GAP_NUMBERS[page_no]
            gap_item = page_items[0]
            gap_item["raag_number"] = gap_number
            gap_item["raag_name_as_printed"] = gap_name
            gap_item["parent_raag_number"] = parent_raag_number(gap_number)
            gap_item["raag_number_inferred"] = True
            gap_item["needs_split_review"] = False
            gap_item["numbering_note"] = (
                "Heading dropped by tesseract's text extraction on this page; number "
                "and name confirmed by rendering the source PDF page directly (see "
                "RAAG_DA_SAROUP_GAP_NUMBERS comment) rather than the OCR text layer."
            )
            remaining = page_items[1:]

        for it, (num, name) in zip(remaining, page_headings):
            it["raag_number"] = num
            it["raag_name_as_printed"] = name
            it["parent_raag_number"] = parent_raag_number(num)
            it["raag_number_inferred"] = False
            it["needs_split_review"] = False
            it["numbering_note"] = None

        for it in remaining[len(page_headings):]:
            blank(
                it,
                "Unmatched against any heading found on this page's prose -- needs manual review.",
                needs_review=True,
            )


def cluster_asa_di_vaar(blocks):
    by_page = {}
    for b in blocks:
        by_page.setdefault(b["page"], []).append(b)
    clusters = []
    for page, page_blocks in sorted(by_page.items()):
        clusters.append({
            "item_type": "notation-fragment",
            "cluster_confidence": "low" if len(page_blocks) == 1 else "medium",
            "cluster_basis": (
                "same-page grouping only -- deliberately conservative: this book is a "
                "single continuous Vaar (one raag throughout), so no cross-page signal "
                "(raag/shabad_id) reliably distinguishes items. Each same-page group is "
                "presented as one item; true item boundaries need human judgment."
            ),
            "blocks": page_blocks,
        })
    return clusters


CLUSTERERS = {
    "guru-gobind-singh-ji-di-bani": cluster_guru_gobind_singh,
    "asa-di-vaar": cluster_asa_di_vaar,
    "sampurn-55-parhtala": cluster_sampurn_55,
    "raag-da-saroup-complete": cluster_raag_da_saroup,
}


def build_manifest():
    manifest = []
    stats = {}
    for slug, clusterer in CLUSTERERS.items():
        blocks = load_notation(slug)
        clusters = clusterer(blocks)
        stats[slug] = {
            "raw_blocks": len(blocks),
            "clustered_items": len(clusters),
            "by_item_type": {},
        }
        for i, c in enumerate(clusters):
            item_type = c["item_type"]
            stats[slug]["by_item_type"][item_type] = stats[slug]["by_item_type"].get(item_type, 0) + 1

            block_shabad_ids = sorted({
                b["shabad_match"]["shabad_id"]
                for b in c["blocks"]
                if b.get("shabad_match", {}).get("shabad_id") is not None
            })
            raags = sorted({b["raag"] for b in c["blocks"] if b.get("raag")})
            taals = sorted({b["taal"] for b in c["blocks"] if b.get("taal")})

            manifest.append({
                "manifest_id": f"{slug}-{i+1:04d}",
                "book": slug,
                "item_type": item_type,
                "cluster_confidence": c["cluster_confidence"],
                "cluster_basis": c["cluster_basis"],
                "page_range": [c["blocks"][0]["page"], c["blocks"][-1]["page"]],
                "block_count": len(c["blocks"]),
                "images": [b["image"] for b in c["blocks"]],
                "shabad_ids": block_shabad_ids,
                "raags": raags,
                "taals": taals,
                "status": "draft",
                "needs_manual_transcription": True,
            })

    attach_raag_da_saroup_numbering([x for x in manifest if x["book"] == "raag-da-saroup-complete"])
    return manifest, stats


if __name__ == "__main__":
    manifest, stats = build_manifest()
    out_path = EXTRACTED / "manifest.json"
    json.dump(manifest, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"wrote {len(manifest)} items to {out_path}")
    print()
    for slug, s in stats.items():
        print(f"{slug}: {s['raw_blocks']} raw blocks -> {s['clustered_items']} items  {s['by_item_type']}")
