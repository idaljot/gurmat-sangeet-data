"""
Shared Phase B (full) extraction pipeline for OCR-based book extraction.

Used by extract_asa-di-vaar.py, extract_sampurn-55-parhtala.py,
extract_raag-da-saroup-complete.py (see books/extracted/_lib/). Every book's
text layer was confirmed unusable in Phase A (wrong-ToUnicode CID fonts /
legacy-ASCII fonts / mixed) -- see books/extracted/_sample/<slug>/REPORT.md
for the full per-book diagnosis. OCR (`pdftoppm` render + `tesseract -l pan`)
is the validated method for all three books; this module implements that
pipeline once so each book script only supplies book-specific parameters.

Design notes / heuristics (documented per project instructions -- simple,
not claimed to be perfect, every notation block is unconditionally flagged
needs_manual_transcription regardless of how it's classified):

1. Page render: `pdftoppm -r 150 -png -f N -l N` (matches the DPI validated
   in Phase A for all three books).

2. OCR: `pytesseract.image_to_data()` (not just image_to_string) so we get
   per-line bounding boxes in pixel space alongside text -- needed to crop
   notation blocks precisely. PSM is book-specific (caller supplies it):
   default/--psm 6 for Asa Di Vaar & Sampurn 55, --psm 4 for Raag Da Saroup
   (Phase A found --psm 6 silently drops rows on that book's list layout).

3. Bordered-table detection: `pdfplumber.find_tables()` on the *original PDF*
   page. This works off vector line-drawing operators, not the (broken)
   text layer, so it is font-bug-independent -- validated in this session on
   Asa Di Vaar page 3 (known 12-col grid) and page 5 (known grid), both
   detected correctly. Tables with fewer than MIN_TABLE_COLS columns are
   discarded as likely false positives (e.g. paragraph-column artifacts).
   bbox is in PDF points; converted to pixel space via the render DPI/72
   scale factor to crop the rendered PNG.

4. Inline-notation-line detection: works on the OCR'd line data (since the
   PDF text layer is untrustworthy for exactly the same content). A line is
   flagged as an inline swara/notation line if EITHER:
     a. it begins with (fuzzy-matches) a known notation-bearing label --
        Aroh/Avroh/Mukh Ang/Sur/Varjit Sur, Gurmukhi or Roman spelling
        (label OCR is ~95%+ reliable per Phase A, so this is the strong
        signal, esp. for Raag Da Saroup's label:value entries), OR
     b. it is a "short-token cluster": >=MIN_TOKENS whitespace-separated
        tokens, with >=SHORT_TOKEN_FRACTION of them at or below
        SHORT_TOKEN_MAXLEN characters -- catches free-floating Aroh/Avroh
        lines embedded in running prose (Asa Di Vaar p.2 pattern) that
        aren't preceded by a recognizable label.
   Lines already inside a detected bordered-table bbox are skipped (already
   counted as part of that table). Adjacent qualifying lines (small vertical
   gap) are merged into a single block.

5. Section tagging is page-level, first-match-wins:
     notation   -- page has any bordered table OR any raag-entry label
                   (>=2 of Thaat/Jaati/Vaadi/Samvaadi/Sur/Samay/Aroh/Avroh/
                   Mukh Ang) OR any inline-notation-line block
     front-matter -- low text density / cover-page keyword match (©, ISBN,
                   www., or explicit first/last-page-of-book position)
     index      -- ਤਤਕਰਾ / ਸੂਚੀ / "index" / "contents" keyword
     biography  -- ਜੀਵਨੀ / ਜਨਮ ਮਿਤੀ / "biography" keyword
     essay      -- prose fallback (word count over threshold)
     other      -- anything else (near-empty OCR, decorative pages, etc.)
   This is intentionally simple per the task brief ("simple, documented
   heuristics are fine") -- it is a sorting aid for human review, not a
   claim of ground truth.

Nothing here invents or "fixes" notation. All OCR text is raw tesseract
output, labeled as such. Every notation block gets
needs_manual_transcription: true unconditionally.
"""

import json
import re
import subprocess
import tempfile
from pathlib import Path

import pdfplumber
import pytesseract
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[3]
RENDER_DPI = 150
PDF_POINTS_DPI = 72.0
SCALE = RENDER_DPI / PDF_POINTS_DPI

MIN_TABLE_COLS = 3  # discard find_tables() hits narrower than this (false positives)

# Inline-notation-line heuristics. Real swara sequences observed in Phase A
# (e.g. "ਸ ਰੇ ਮ ਪ ਧ ਸਂ", "ਸ ਰੇ ਮੇ, ਪ ਨੀ ਸਂ") are runs of *very* short tokens
# (single consonant +/- one vowel-sign/octave-marker, <=2 chars each), unlike
# ordinary short Gurmukhi words (ਆਸਾ, ਦੀ, ਵਾਰ, ਮਹਲਾ = 2-4 chars). Tuned tighter
# than a first pass after that first pass caught recurring page headers like
# "2: ਆਸਾ ਦੀ ਵਾਰ" and shabad attribution lines ("ਆਸਾ ਮਹਲਾ ੪ ਛੰਤ ਘਰੁ ੪") as
# false positives -- still a simple heuristic, not a claim of precision; every
# resulting block is needs_manual_transcription regardless.
MIN_TOKENS = 5
SHORT_TOKEN_MAXLEN = 2
SHORT_TOKEN_FRACTION = 0.75
LINE_MERGE_GAP_PX = 12  # vertical gap under which adjacent flagged lines merge into one block

# Common shabad/section-attribution words that are short enough to trip the
# short-token-cluster test but are not swara data -- if these dominate a
# line's short tokens, don't treat it as inline notation via that path.
_HEADER_STOPWORDS = {
    "ਆਸਾ", "ਦੀ", "ਵਾਰ", "ਮਹਲਾ", "ਛੰਤ", "ਘਰੁ", "ਘਰ", "ਰਾਗੁ", "ਪਉੜੀ",
    "ਸਲੋਕ", "ਮਃ", "ਨਾਨਕ", "ਪਦ", "ਅਰਥ",
}
_PAGE_HEADER_RE = re.compile(r"^\s*[0-9੦-੯]+\s*[:.]")

# Notation-bearing labels (Gurmukhi + Roman spellings seen in Phase A OCR output).
# Only these carry actual swara/sur sequences -- Thaat/Jaati/Vaadi/Samvaadi/Samay
# are raag metadata, tagged for page-level `notation` section but not cropped as
# their own inline-line blocks.
NOTATION_LABELS = [
    "ਆਰੋਹ", "ਅਵਰੋਹ", "ਮੁੱਖ ਅੰਗ", "ਮੁਖ ਅੰਗ", "ਸੁਰ", "ਵਰਜਿਤ ਸੁਰ",
    "aroh", "avroh", "avrohi", "arohi", "mukh ang", "sur",
]
RAAG_ENTRY_LABELS = [
    "ਥਾਟ", "ਜਾਤੀ", "ਵਾਦੀ", "ਸੰਵਾਦੀ", "ਸੁਰ", "ਵਰਜਿਤ", "ਸਮਾਂ", "ਆਰੋਹ", "ਅਵਰੋਹ", "ਮੁੱਖ",
]
INDEX_KEYWORDS = ["ਤਤਕਰਾ", "ਸੂਚੀ", "index", "contents", "table of content"]
BIO_KEYWORDS = ["ਜੀਵਨੀ", "ਜਨਮ ਮਿਤੀ", "ਜਨਮ ਤਾਰੀਖ", "biography", "life sketch"]
FRONT_MATTER_KEYWORDS = ["isbn", "©", "all rights reserved", "copyright", "www.", "first edition"]

_GURMUKHI_RE = re.compile(r"[਀-੿]")


def gurmukhi_ratio(text):
    if not text:
        return 0.0
    return len(_GURMUKHI_RE.findall(text)) / max(len(text), 1)


def render_page_png(pdf_path, page_num, out_path, dpi=RENDER_DPI):
    """Render one 1-indexed page of pdf_path to out_path (PNG) via pdftoppm."""
    prefix = str(out_path.with_suffix(""))
    subprocess.run(
        [
            "pdftoppm", "-r", str(dpi), "-png",
            "-f", str(page_num), "-l", str(page_num),
            "-singlefile", str(pdf_path), prefix,
        ],
        check=True, capture_output=True,
    )
    if not out_path.exists():
        raise RuntimeError(f"pdftoppm did not produce {out_path}")


def ocr_page(image_path, psm_config):
    """Run tesseract -l pan over the rendered page image. Returns
    (full_text, lines) where lines is a list of
    {"text", "bbox": (x0,y0,x1,y1) in pixel space, "conf"} grouped from
    pytesseract.image_to_data word boxes."""
    img = Image.open(image_path)
    full_text = pytesseract.image_to_string(img, lang="pan", config=psm_config)

    data = pytesseract.image_to_data(
        img, lang="pan", config=psm_config, output_type=pytesseract.Output.DICT
    )
    lines = {}
    n = len(data["text"])
    for i in range(n):
        word = data["text"][i].strip()
        if not word:
            continue
        key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        x0, y0 = data["left"][i], data["top"][i]
        x1, y1 = x0 + data["width"][i], y0 + data["height"][i]
        conf = data["conf"][i]
        if key not in lines:
            lines[key] = {"words": [], "bbox": [x0, y0, x1, y1], "confs": []}
        entry = lines[key]
        entry["words"].append(word)
        entry["bbox"][0] = min(entry["bbox"][0], x0)
        entry["bbox"][1] = min(entry["bbox"][1], y0)
        entry["bbox"][2] = max(entry["bbox"][2], x1)
        entry["bbox"][3] = max(entry["bbox"][3], y1)
        try:
            c = float(conf)
            if c >= 0:
                entry["confs"].append(c)
        except (TypeError, ValueError):
            pass

    out_lines = []
    for key in sorted(lines.keys()):
        e = lines[key]
        avg_conf = sum(e["confs"]) / len(e["confs"]) if e["confs"] else None
        out_lines.append({
            "text": " ".join(e["words"]),
            "bbox": tuple(e["bbox"]),
            "conf": avg_conf,
        })
    # sort top-to-bottom
    out_lines.sort(key=lambda l: l["bbox"][1])
    return full_text, out_lines


def detect_bordered_tables(pdf_page):
    """Return list of {"bbox_px": (x0,y0,x1,y1)} for plausible grid tables on
    this pdfplumber page, using vector line detection (font-independent)."""
    out = []
    try:
        tables = pdf_page.find_tables()
    except Exception:
        return out
    for t in tables:
        rows = t.rows
        ncols = len(rows[0].cells) if rows else 0
        if ncols < MIN_TABLE_COLS:
            continue
        x0, y0, x1, y1 = t.bbox
        out.append({
            "bbox_px": (x0 * SCALE, y0 * SCALE, x1 * SCALE, y1 * SCALE),
            "rows": len(rows),
            "cols": ncols,
        })
    return out


def _bbox_overlaps(a, b):
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return not (ax1 < bx0 or bx1 < ax0 or ay1 < by0 or by1 < ay0)


def _line_is_labeled_notation(text):
    # Require the label to appear near the START of the line (label:value
    # structure), not merely anywhere in it -- an earlier pass matched
    # running book-title headers that happen to contain "ਸੁਰ" mid-sentence
    # (e.g. "... ਸ਼ਬਦ ਸੁਰ ਰਚਨਾਵਲੀ" repeated on every Sampurn 55 page) as false
    # positives. Checking only the leading tokens fixes that while still
    # catching real label:value lines ("ਆਰੋਹ : ਸਰੇ,ਮਪ,ਨੀਸੰ", "ਸੁਰ $ ਸ਼ੜਜ...").
    tokens = text.strip().split()
    lead = " ".join(tokens[:3]).lower()
    lead_raw = " ".join(tokens[:3])
    for label in NOTATION_LABELS:
        if label.lower() in lead or label in lead_raw:
            return True
    return False


def _line_is_short_token_cluster(text):
    if _PAGE_HEADER_RE.match(text.strip()):
        return False
    tokens = [t for t in re.split(r"[\s,]+", text.strip()) if t]
    if len(tokens) < MIN_TOKENS:
        return False
    short_tokens = [t for t in tokens if len(t) <= SHORT_TOKEN_MAXLEN]
    if (len(short_tokens) / len(tokens)) < SHORT_TOKEN_FRACTION:
        return False
    stopword_hits = sum(1 for t in short_tokens if t in _HEADER_STOPWORDS)
    if short_tokens and (stopword_hits / len(short_tokens)) > 0.4:
        return False
    return True


def detect_inline_notation_lines(ocr_lines, table_bboxes_px):
    """From OCR line data, pick out lines that look like inline swara
    sequences (label-anchored or short-token-cluster), skip anything inside
    an already-detected bordered table, and merge vertically-adjacent hits
    into single blocks."""
    candidates = []
    for line in ocr_lines:
        if not line["text"].strip():
            continue
        if any(_bbox_overlaps(line["bbox"], tb) for tb in table_bboxes_px):
            continue
        labeled = _line_is_labeled_notation(line["text"])
        clustered = _line_is_short_token_cluster(line["text"])
        if labeled or clustered:
            candidates.append({**line, "labeled": labeled, "clustered": clustered})

    if not candidates:
        return []

    candidates.sort(key=lambda l: l["bbox"][1])
    merged = [candidates[0]]
    for c in candidates[1:]:
        prev = merged[-1]
        gap = c["bbox"][1] - prev["bbox"][3]
        if gap <= LINE_MERGE_GAP_PX:
            nb = (
                min(prev["bbox"][0], c["bbox"][0]),
                min(prev["bbox"][1], c["bbox"][1]),
                max(prev["bbox"][2], c["bbox"][2]),
                max(prev["bbox"][3], c["bbox"][3]),
            )
            prev["bbox"] = nb
            prev["text"] = prev["text"] + " / " + c["text"]
            prev["labeled"] = prev["labeled"] or c["labeled"]
            prev["clustered"] = prev["clustered"] or c["clustered"]
        else:
            merged.append(c)
    return merged


def classify_section(full_text, page_num, total_pages, has_table, has_inline_notation,
                      force_notation_default=False):
    """Page-level section tag. See module docstring for the heuristic order.
    force_notation_default: book-specific override (Raag Da Saroup is almost
    entirely raag-entry notation content by structure)."""
    text = full_text or ""
    low = text.lower()
    word_count = len(text.split())
    raag_label_hits = sum(1 for lbl in RAAG_ENTRY_LABELS if lbl in text)

    if has_table or has_inline_notation or raag_label_hits >= 2:
        return "notation"
    if force_notation_default and raag_label_hits >= 1:
        return "notation"
    if any(k in low or k in text for k in INDEX_KEYWORDS):
        return "index"
    if any(k in low or k in text for k in BIO_KEYWORDS):
        return "biography"
    if (page_num <= 2 or page_num >= total_pages - 1) and word_count < 40:
        return "front-matter"
    if any(k in low for k in FRONT_MATTER_KEYWORDS):
        return "front-matter"
    if word_count >= 40:
        return "essay"
    if force_notation_default:
        return "notation"
    return "other"


def find_shabad_candidate_line(ocr_lines, min_gurmukhi_ratio=0.6, min_words=4):
    """Best-effort pick of a single OCR line on this page that looks like a
    shabad first line (mool panktee), to hand to match_shabad(). Never
    guesses which shabad -- only picks which *line* to try matching.
    Returns None if nothing plausible found."""
    best = None
    for line in ocr_lines:
        t = line["text"].strip()
        if len(t.split()) < min_words:
            continue
        if gurmukhi_ratio(t) < min_gurmukhi_ratio:
            continue
        if _line_is_labeled_notation(t) or _line_is_short_token_cluster(t):
            continue
        best = t
        break
    return best


def crop_and_save(image_path, bbox_px, out_path, pad=6):
    img = Image.open(image_path)
    w, h = img.size
    x0, y0, x1, y1 = bbox_px
    x0 = max(0, int(x0) - pad)
    y0 = max(0, int(y0) - pad)
    x1 = min(w, int(x1) + pad)
    y1 = min(h, int(y1) + pad)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.crop((x0, y0, x1, y1)).save(out_path)


def guess_raag(text):
    m = re.search(r"ਰਾਗ[ੁ]?\s*[:：]?\s*([਀-੿]{2,20})", text)
    if m:
        return m.group(0).strip()
    return None


def guess_taal(text):
    m = re.search(r"ਤਾਲ[ ]?\s*[:：]?\s*([਀-੿]{2,20})", text)
    if m:
        return m.group(0).strip()
    return None


class NotationRawWriter:
    """Append-only writer for notation-raw.json (one JSON array per book)."""

    def __init__(self, path):
        self.path = path
        self.records = []
        if path.exists():
            try:
                self.records = json.loads(path.read_text())
            except Exception:
                self.records = []

    def add(self, record):
        self.records.append(record)

    def flush(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.records, ensure_ascii=False, indent=2))


def run_extraction(*, slug, pdf_path, psm_config, extraction_method_label,
                    ocr_confidence_note, force_notation_default=False,
                    shabad_match_fn=None, page_range=None, log_every=10):
    """Drives the full per-page pipeline for one book. shabad_match_fn is
    injected (defaults to books.extracted._lib.shabad_match.match_shabad)
    so this module has no hard import-time dependency on network access."""
    if shabad_match_fn is None:
        from books.extracted._lib.shabad_match import match_shabad as shabad_match_fn

    book_dir = REPO_ROOT / "books" / "extracted" / slug
    pages_dir = book_dir / "pages"
    notation_dir = book_dir / "notation"
    pages_dir.mkdir(parents=True, exist_ok=True)
    notation_dir.mkdir(parents=True, exist_ok=True)

    raw_writer = NotationRawWriter(book_dir / "notation-raw.json")

    with pdfplumber.open(str(pdf_path)) as pdf:
        total_pages = len(pdf.pages)
        pages = page_range or range(1, total_pages + 1)

        stats = {
            "pages_processed": 0,
            "section_counts": {},
            "blocks_bordered_table": 0,
            "blocks_inline_line": 0,
            "shabad_match_high": 0,
            "shabad_match_medium": 0,
            "shabad_match_none": 0,
            "shabad_match_attempts": 0,
        }

        with tempfile.TemporaryDirectory(prefix=f"{slug}-render-") as tmpdir:
            tmpdir = Path(tmpdir)
            for page_num in pages:
                png_path = tmpdir / f"page-{page_num:03d}.png"
                render_page_png(pdf_path, page_num, png_path)

                full_text, ocr_lines = ocr_page(png_path, psm_config)

                pdf_page = pdf.pages[page_num - 1]
                tables = detect_bordered_tables(pdf_page)
                table_bboxes = [t["bbox_px"] for t in tables]
                inline_blocks = detect_inline_notation_lines(ocr_lines, table_bboxes)

                section = classify_section(
                    full_text, page_num, total_pages,
                    has_table=bool(tables),
                    has_inline_notation=bool(inline_blocks),
                    force_notation_default=force_notation_default,
                )
                stats["section_counts"][section] = stats["section_counts"].get(section, 0) + 1

                page_record = {
                    "page": page_num,
                    "section": section,
                    "text": full_text,
                    "status": "draft",
                    "extraction_method": extraction_method_label,
                    "ocr_confidence_note": ocr_confidence_note,
                }
                (pages_dir / f"page-{page_num:03d}.json").write_text(
                    json.dumps(page_record, ensure_ascii=False, indent=2)
                )

                if section == "notation" and (tables or inline_blocks):
                    shabad_line = find_shabad_candidate_line(ocr_lines)
                    shabad_result = None
                    if shabad_line:
                        stats["shabad_match_attempts"] += 1
                        try:
                            shabad_result = shabad_match_fn(shabad_line)
                        except Exception as e:
                            shabad_result = {"shabad_id": None, "confidence": "none",
                                              "method": f"error: {e}", "matched_verse": None}
                        conf = shabad_result.get("confidence", "none")
                        stats[f"shabad_match_{conf}"] = stats.get(f"shabad_match_{conf}", 0) + 1

                    block_idx = 0
                    for t in tables:
                        block_idx += 1
                        img_name = f"page-{page_num:03d}-block-{block_idx}.png"
                        crop_and_save(png_path, t["bbox_px"], notation_dir / img_name)
                        raw_writer.add({
                            "book": slug,
                            "page": page_num,
                            "image": f"notation/{img_name}",
                            "layout": "bordered-table",
                            "raw_text": None,  # cell text not reliably OCR'able as structured
                                                 # data per Phase A; image is source of truth
                            "table_shape": {"rows": t["rows"], "cols": t["cols"]},
                            "raag": guess_raag(full_text),
                            "taal": guess_taal(full_text),
                            "shabad_match": shabad_result,
                            "status": "draft",
                            "needs_manual_transcription": True,
                        })
                        stats["blocks_bordered_table"] += 1

                    for blk in inline_blocks:
                        block_idx += 1
                        img_name = f"page-{page_num:03d}-block-{block_idx}.png"
                        crop_and_save(png_path, blk["bbox"], notation_dir / img_name)
                        raw_writer.add({
                            "book": slug,
                            "page": page_num,
                            "image": f"notation/{img_name}",
                            "layout": "inline-line",
                            "raw_text": blk["text"],
                            "raw_text_flag": "low-confidence-ocr: inter-syllable spacing "
                                             "likely collapsed, do not parse as tokenized data",
                            "raag": guess_raag(full_text),
                            "taal": guess_taal(full_text),
                            "shabad_match": shabad_result,
                            "status": "draft",
                            "needs_manual_transcription": True,
                        })
                        stats["blocks_inline_line"] += 1

                stats["pages_processed"] += 1
                if page_num % log_every == 0 or page_num == (pages[-1] if hasattr(pages, "__getitem__") else page_num):
                    print(f"[{slug}] page {page_num}/{total_pages} section={section} "
                          f"tables={len(tables)} inline={len(inline_blocks)}")

    raw_writer.flush()
    stats_path = book_dir / "_extraction_stats.json"
    stats_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2))
    print(f"[{slug}] DONE. stats: {json.dumps(stats, ensure_ascii=False)}")
    return stats
