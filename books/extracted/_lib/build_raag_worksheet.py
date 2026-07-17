"""
Builds a per-item worksheet for the Raag Da Saroup Complete proof-of-concept entry tool
(tools/raag-entry.html). Joins manifest.json (the clustered items) with notation-raw.json
(per-block raw OCR text) and the page-level extracted text (for the surrounding prose --
Thaat/Jaati/Vadi/Samvadi/Samay are prose labels, not separately-cropped notation blocks).

This is a convenience join only -- it doesn't invent or correct anything. Every field
value is either "as extracted" (and clearly labeled low-confidence OCR) or left for a
human to fill in via the tool.

Output: books/extracted/raag-da-saroup-complete/worksheet.json
"""

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
BOOK_DIR = REPO_ROOT / "books" / "extracted" / "raag-da-saroup-complete"

# Recognized field labels, per Phase A's documented structure for this book -- used to
# split a block's raw_text into a (label, value) pair for prefill, same list used by
# cluster_blocks.py's field_label().
KNOWN_LABELS = [
    "ਵਰਜਿਤ ਸੁਰ", "ਸੁਰ", "ਆਰੋਹ", "ਅਵਰੋਹ", "ਮੁੱਖ ਅੰਗ",
    "ਥਾਟ", "ਜਾਤੀ", "ਵਾਦੀ", "ਸੰਵਾਦੀ", "ਸਮਾਂ",
]


def split_label(raw_text):
    if not raw_text:
        return None, raw_text
    stripped = raw_text.strip()
    for label in sorted(KNOWN_LABELS, key=len, reverse=True):
        if stripped.startswith(label):
            value = stripped[len(label):].lstrip(" :।_-,")
            return label, value
    return None, raw_text


def main():
    manifest = json.load(open(REPO_ROOT / "books" / "extracted" / "manifest.json", encoding="utf-8"))
    notation_raw = json.load(open(BOOK_DIR / "notation-raw.json", encoding="utf-8"))
    notation_by_image = {r["image"]: r for r in notation_raw}

    items = [x for x in manifest if x["book"] == "raag-da-saroup-complete"]

    # cache page text (front-matter/prose the block-level notation extraction doesn't cover)
    page_text_cache = {}

    def page_text(page_no):
        if page_no not in page_text_cache:
            path = BOOK_DIR / "pages" / f"page-{page_no:03d}.json"
            page_text_cache[page_no] = json.load(open(path, encoding="utf-8"))["text"] if path.exists() else ""
        return page_text_cache[page_no]

    worksheet = []
    for item in items:
        ocr_fields = {}
        for image in item["images"]:
            rec = notation_by_image.get(image)
            if not rec:
                continue
            label, value = split_label(rec.get("raw_text"))
            if label:
                # if a label appears more than once in one item (shouldn't, given
                # clustering already guards this, but be defensive), keep the first
                ocr_fields.setdefault(label, value)

        # surrounding page prose, for Thaat/Jaati/Vaadi/Samvaadi/Samay context that
        # isn't in a separately-cropped notation block
        start_page, end_page = item["page_range"]
        prose = "\n---\n".join(page_text(p) for p in range(start_page, end_page + 1))

        worksheet.append({
            "manifest_id": item["manifest_id"],
            "page_range": item["page_range"],
            "cluster_confidence": item["cluster_confidence"],
            "raag_gurmukhi_guess": (item["raags"][0] if item["raags"] else None),
            "images": item["images"],
            "ocr_fields": ocr_fields,
            "page_prose": prose,
        })

    out_path = BOOK_DIR / "worksheet.json"
    json.dump(worksheet, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"wrote {len(worksheet)} worksheet entries to {out_path}")


if __name__ == "__main__":
    main()
