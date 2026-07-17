#!/usr/bin/env python3
"""
Phase B extraction pipeline — "Guru Gobind Singh Ji Di Bani" (Shabad Sur Rachnavali), 131pp.
Slug: guru-gobind-singh-ji-di-bani

Everything this script writes is DRAFT data (status: "draft"). Nothing here is
authoritative; sacred notation content is never guessed or "fixed" — ambiguous or
missing characters are left exactly as extracted and flagged.

------------------------------------------------------------------------------------
WHAT THIS BOOK LOOKS LIKE (confirmed empirically before writing this script; see the
Phase A sample report at books/extracted/_sample/guru-gobind-singh-ji-di-bani/REPORT.md
for the original calibration, and EXTRACTION.md next to this book's output for what
changed on the full 131-page run):

  - Pages 1, 3, 4: genuine CID/Identity-H Unicode Gurmukhi text. Poppler/PyMuPDF already
    extract real Gurmukhi codepoints, but a pre-base vowel sign (sihari, ਿ) comes out
    BEFORE its base consonant in the text stream instead of after (e.g. raw "ਗੋਿਬੰਦ"
    should read "ਗੋਬਿੰਦ"). Fix: a regex that moves ਿ to just after the next Gurmukhi
    consonant, then NFC normalize. Page 1's subtitle also silently drops the leading
    "ਸ਼" (sha) of "ਸ਼ਬਦ" (Shabad) in the raw extraction — a dropped character, not just
    reordered. NOT reconstructed here; left as extracted and flagged.
  - Page 2: plain English (copyright/ISBN page). No Gurmukhi at all — passed through
    untouched.
  - Pages 5-131 (127 pages): Gurmukhi typed in a legacy 8-bit ASCII-keyed font
    (AnmolLipi/GurbaniLipi convention — e.g. "gurU goibMd isMG jI" -> "ਗੁਰੂ ਗੋਬਿੰਦ ਸਿੰਘ
    ਜੀ"). IMPORTANT, non-obvious finding from re-checking Phase A on this full run:
    the embedded font *names* for the body text (pages 6-131) are "Asees" and
    "AmrLipiHeavy", NOT "AnmolLipi"/"Raavi" as pages 3-5 use. In a *different* book
    (Guru Nanak Bani), a font named "Asees" uses a genuinely different, harder-to-map
    ASCII scheme (see PHASE_A_ASEES_REVALIDATION.md) where gurmukhi-utils fails
    outright. That is NOT what's happening here: this PDF's "Asees"/"AmrLipiHeavy"
    fonts, despite the name, key text using the *same* AnmolLipi-style scheme as the
    rest of the book. This was verified directly (not assumed) before trusting the
    pipeline: raw page-31/126-style text run through gurmukhi-utils toUnicode()
    produces fluent, grammatical Gurmukhi ("jY jY rUp AryK Apwr ]" ->
    "ਜੈ ਜੈ ਰੂਪ ਅਰੇਖ ਅਪਾਰ ॥"), matching Phase A's conclusion for this book. Lesson:
    embedded font *names* are not a reliable signal across different PDFs/books —
    the actual character mapping must be spot-checked per book regardless of what a
    font calls itself. Because of this, dispatch below is content-based (does a span's
    extracted text already contain Gurmukhi Unicode codepoints, or is it Latin ASCII
    text sitting in a font we know is used for Gurmukhi body copy on this book) rather
    than a hardcoded font-name-to-method table.
  - Notation is genuine bordered PDF tables (pdfplumber find_tables()), but with a
    near-full-page decorative border/frame present on almost every page that also
    registers as a "table" — that frame is excluded (area >85% of the page) before
    treating anything as a real content table.
  - Inside a real notation table: a numeric matra-header row, a sparse taal-sign row,
    one Gurmukhi taal-bol row, then ALTERNATING short "sur-like" rows and longer
    "lyric-like" rows repeating down the sthai/antara block (one sur+lyric pair per
    line of the verse set against the fixed taal cycle) — confirmed by reconstructing
    the lyric-row tokens and matching them word-for-word against the shabad text on
    the preceding page. The sur-row cell content is captured as-extracted (Latin/mixed
    ASCII tokens, NOT run through gurmukhi-utils, matching Phase A's finding that this
    row already survives extraction untouched) — this script does not attempt to
    interpret what those tokens mean in the project's own SARGAM.md convention. That
    interpretation is exactly the "needs a human who reads swaralipi" step, which is
    why every notation block is unconditionally flagged needs_manual_transcription.
  - Some notation-adjacent pages (raag-characteristics blocks: Aroh/Avroh/Pakad/Thaat/
    etc., and two appendix sections — a taal-bol reference table pp.128-129, and a
    raag-characteristics reference table pp.130-131) do NOT have a bordered inner table
    at all; they're plain label:value lines in the legacy Gurmukhi font. These are still
    tagged section="notation" (they are raag/taal reference *data*, this project's core
    subject matter) but fall back to a full-page crop since there's no precise table
    bbox to crop to.

DISPATCH SUMMARY (method used per page, decided from PyMuPDF span content+font, not
guessed page-by-page):
  - "cid-reorder"    : page has spans with real Gurmukhi Unicode codepoints (pp.1,3,4).
  - "gurmukhi-utils"  : page has spans in a known Gurmukhi-body font family, containing
                        Latin ASCII text in the legacy keying scheme (pp.5-131 except 2).
  - "none"            : no Gurmukhi signal at all — pure Latin/English page (p.2).
  - "mixed"           : BOTH signals present on the same page. Does not occur anywhere
                        in this book (verified: every page has at most one of the two
                        signals), but implemented defensively: falls back to running
                        gurmukhi-utils over the whole page (the dominant case if it ever
                        happens) and flags the page's "notes" for manual double-check,
                        since true span-by-span interleaving is not implemented.

SECTION CLASSIFICATION — simple, explainable, DRAFT heuristics (see classify_section()
docstring below for the exact priority order and triggers). Not meant to be perfect;
meant to be auditable.

SETUP / HOW TO RE-RUN:
  1. Poppler CLI (`pdftotext`) and Node/npm must be on PATH.
  2. Python venv: /Users/daljotsingh/gurmat-sangeet-data/.venv-extraction/bin/python3
     (has pymupdf, pdfplumber, pypdf, banidb).
  3. gurmukhi-utils is NOT vendored into the repo (per project convention — it's a
     scratch/tooling dependency, not book content). This script bootstraps it on first
     run into ~/.cache/gurmat-sangeet-extraction/gurmukhi-utils/ via `npm install`
     (override with the GURMUKHI_UTILS_DIR env var). Safe to delete and re-run.
  4. Run from the repo root:
       .venv-extraction/bin/python3 books/extracted/_lib/extract_guru_gobind_singh.py
------------------------------------------------------------------------------------
"""

import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

import fitz  # pymupdf
import pdfplumber

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from books.extracted._lib.shabad_match import match_shabad  # noqa: E402

SLUG = "guru-gobind-singh-ji-di-bani"
BOOK_PDF = REPO_ROOT / "books" / "Guru Gobind Singh Ji Di Bani (131 page).pdf"
OUT_DIR = REPO_ROOT / "books" / "extracted" / SLUG
PAGES_DIR = OUT_DIR / "pages"
NOTATION_DIR = OUT_DIR / "notation"
NOTATION_RAW_JSON = OUT_DIR / "notation-raw.json"
TOTAL_PAGES = 131

# ---------------------------------------------------------------------------
# gurmukhi-utils bridge (Node subprocess, batched — one process for the whole book
# rather than one per page/span).
# ---------------------------------------------------------------------------

GMU_DIR = Path(os.environ.get(
    "GURMUKHI_UTILS_DIR",
    str(Path.home() / ".cache" / "gurmat-sangeet-extraction" / "gurmukhi-utils"),
))

_BRIDGE_JS = """
// Reads a JSON array of strings from stdin, writes a JSON array of
// gurmukhi-utils toUnicode()-converted strings to stdout. Batched to avoid
// paying Node startup cost once per page/span.
const { toUnicode } = require("gurmukhi-utils");
let input = "";
process.stdin.on("data", (d) => (input += d));
process.stdin.on("end", () => {
  const arr = JSON.parse(input);
  const out = arr.map((s) => (s === null ? null : toUnicode(s)));
  process.stdout.write(JSON.stringify(out));
});
"""


def ensure_gurmukhi_utils():
    GMU_DIR.mkdir(parents=True, exist_ok=True)
    if not (GMU_DIR / "node_modules" / "gurmukhi-utils").exists():
        print(f"[setup] npm install gurmukhi-utils in {GMU_DIR} ...", file=sys.stderr)
        subprocess.run(["npm", "install", "gurmukhi-utils", "--silent"],
                        cwd=GMU_DIR, check=True)
    bridge = GMU_DIR / "toUnicode_batch.js"
    bridge.write_text(_BRIDGE_JS)
    return bridge


def gurmukhi_utils_batch(strings):
    """Convert a list of legacy-ASCII-keyed strings to Unicode Gurmukhi in one
    Node subprocess call. None entries pass through as None."""
    if not strings:
        return []
    bridge = ensure_gurmukhi_utils()
    proc = subprocess.run(
        ["node", str(bridge)],
        input=json.dumps(strings), capture_output=True, text=True, check=True,
    )
    return json.loads(proc.stdout)


# ---------------------------------------------------------------------------
# CID-Unicode sihari-reorder + NFC fix (pages 1, 3, 4)
# ---------------------------------------------------------------------------

SIHARI = "ਿ"  # ਿ
# Gurmukhi consonants (incl. nukta-formed ones) that sihari can attach to.
_CONSONANT_CLASS = "ਕ-ਹਖ਼-ੜਫ਼"
_SIHARI_REORDER_RE = re.compile(f"{SIHARI}([{_CONSONANT_CLASS}])")


def fix_sihari_reorder(text):
    """Move a pre-base sihari that extracted BEFORE its base consonant to just
    after it (correct Unicode logical order). Validated against the Phase A
    sample (page 1: "ਗੋਿਬੰਦ" -> "ਗੋਬਿੰਦ", "ਿਸੰਘ" -> "ਸਿੰਘ", etc.)."""
    return _SIHARI_REORDER_RE.sub(lambda m: m.group(1) + SIHARI, text)


def cid_unicode_fix(text):
    return unicodedata.normalize("NFC", fix_sihari_reorder(text))


# ---------------------------------------------------------------------------
# Per-page method dispatch, decided from PyMuPDF span content + font.
# ---------------------------------------------------------------------------

GURMUKHI_BODY_FONT_SUBSTRINGS = (
    "akaash", "anmollipi", "raavi", "asees", "amrlipiheavy", "mangal",
)


def _has_gurmukhi_unicode(text):
    return any(0x0A00 <= ord(c) <= 0x0A7F for c in text)


def page_method_signals(fitz_page):
    """Inspect every text span on the page. Returns (any_unicode, any_legacy)."""
    any_unicode = False
    any_legacy = False
    d = fitz_page.get_text("dict")
    for block in d.get("blocks", []):
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span.get("text", "")
                if not text.strip():
                    continue
                if _has_gurmukhi_unicode(text):
                    any_unicode = True
                    continue
                fontname = span.get("font", "").lower()
                if re.search(r"[A-Za-z]", text) and any(
                    sub in fontname for sub in GURMUKHI_BODY_FONT_SUBSTRINGS
                ):
                    any_legacy = True
    return any_unicode, any_legacy


def page_raw_layout_text(page_num):
    """pdftotext -layout for a single page — validated in Phase A as the method
    that best preserves the notation grid's column alignment."""
    proc = subprocess.run(
        ["pdftotext", "-f", str(page_num), "-l", str(page_num), "-layout",
         str(BOOK_PDF), "-"],
        capture_output=True, text=True, check=True,
    )
    return proc.stdout


# ---------------------------------------------------------------------------
# Section classification — simple, explainable, DRAFT heuristics.
# ---------------------------------------------------------------------------

_FRONT_MATTER_RE = re.compile(
    r"ISBN|Copyright|First Edition|Price\s*:|True Sparrow Publishers", re.I)
_INDEX_HEADING_RE = re.compile(r"\bqqkrw\b")
_TOC_ROW_RE = re.compile(r"^\s*\d{1,2}\s+\S.+\s\d{1,3}\s*$", re.M)
_MATRA_HEADER_RE = re.compile(r"^\s*1\s+2\s+3\b")
# Line-anchored + colon-required so this doesn't false-positive on prose that merely
# *mentions* Aroh/Avroh in passing (e.g. the foreword describing the book's contents) --
# only matches an actual "Aroh :" / "Avroh :" field-label line.
_AROH_LABEL_RE = re.compile(r"^\s*A[wW]?roh\s*:", re.M)
_AVROH_LABEL_RE = re.compile(r"^\s*Avroh\s*:", re.M)
_TAAL_APPENDIX_RE = re.compile(r"qwl\s+mwqrw|qwl\s+bol|qwl\s+icMn")
_RAAG_APPENDIX_RE = re.compile(r"rwgW\s+dw\s+srUp")
_PD_ARTH_RE = re.compile(r"pd\s*-\s*ArQ")
_BIO_RE = re.compile(r"jIvn\s*bwrY|jnm\s*asQwn|jIvn\s*ibvrx|jIvnI", re.I)


def _has_matra_header(raw_text):
    return any(_MATRA_HEADER_RE.match(line) for line in raw_text.splitlines())


def classify_section(page_num, raw_text, has_inner_table):
    """
    Priority order (first match wins). Draft tag only — human review authoritative.

      1. front-matter : page <= 2, or ISBN/Copyright/Edition/Price/Publisher keywords.
      2. index        : the Gurmukhi-ASCII heading "qqkrw" (ਤਤਕਰਾ = table of contents),
                         or >=3 lines matching a "serial# ... trailing#" TOC-row shape.
      3. notation      : an inner bordered table (beyond the near-full-page frame) plus
                         a numeric matra-header row ("1 2 3 ...") -> the bordered
                         sur/taal-bol grid (e.g. pp.9, 125, 127).
      4. other        : shabad lyric + pad-arth glossary pages ("pd - ArQ" heading) —
                         checked BEFORE the raag-info rule below because, empirically,
                         every page in this book carrying a "pd - ArQ" glossary also
                         carries an "Aroh :"/"Avroh :" raag-characteristics footer
                         directly under it (e.g. pp.8, 10, 126) — the page is still
                         primarily lyrics + word-glosses, so it's tagged "other", not
                         "notation" (its raag-info footer text is preserved in the
                         page's "text" field regardless, just not double-counted as a
                         separate notation block).
      5. notation      : STANDALONE raag/taal reference content with no lyrics/glossary
                         on the page: (a) an "Aroh :" + "Avroh :" field-label pair with
                         no pd-arth heading present; OR (b) the taal-bol reference
                         appendix ("qwl mwqrw"/"qwl bol"/"qwl icMn", pp.128-129); OR
                         (c) the raag-characteristics reference appendix ("rwgW dw
                         srUp", pp.130-131).
      6. biography    : biography-style keywords (jIvnI / jnm asQwn / ...). Included
                         for completeness; not expected to fire in this book (no
                         standalone author-bio page was found in the source text).
      7. essay        : remaining substantial-prose pages (foreword, chhand/meter
                         definitions) — the residual discursive-text bucket.
      8. other        : default fallback.
    """
    if page_num <= 2 or _FRONT_MATTER_RE.search(raw_text):
        return "front-matter", "page<=2 or ISBN/Copyright/Edition/Price keyword"

    if _INDEX_HEADING_RE.search(raw_text) or len(_TOC_ROW_RE.findall(raw_text)) >= 3:
        return "index", "qqkrw heading or >=3 TOC-row-shaped lines"

    if has_inner_table and _has_matra_header(raw_text):
        return "notation", "inner bordered table + numeric matra header row"

    if _PD_ARTH_RE.search(raw_text):
        return "other", "shabad lyric + pad-arth glossary page (pd - ArQ heading)"

    if _AROH_LABEL_RE.search(raw_text) and _AVROH_LABEL_RE.search(raw_text):
        return "notation", "standalone Aroh:/Avroh: raag-info block, no pd-arth on page"
    if _TAAL_APPENDIX_RE.search(raw_text):
        return "notation", "taal-bol reference appendix (qwl mwqrw/bol/icMn)"
    if _RAAG_APPENDIX_RE.search(raw_text):
        return "notation", "raag-characteristics reference appendix (rwgW dw srUp)"

    if _BIO_RE.search(raw_text):
        return "biography", "biography keyword match"

    # Residual prose heuristic: page has a meaningful amount of alphabetic text but
    # none of the structural markers above -> treat as discursive/essay content.
    letters = len(re.findall(r"[A-Za-z਀-੿]", raw_text))
    if letters > 400:
        return "essay", "substantial prose, no structural marker matched (fallback)"

    return "other", "no heuristic matched (fallback)"


# ---------------------------------------------------------------------------
# Notation table detection + cropping + raw sur-row heuristic.
# ---------------------------------------------------------------------------

FRAME_AREA_RATIO = 0.85  # tables covering more of the page than this are the page's
                          # decorative border, not real content, on nearly every page.


def inner_tables(plumber_page):
    page_area = plumber_page.width * plumber_page.height
    out = []
    for t in plumber_page.find_tables():
        x0, y0, x1, y1 = t.bbox
        area = (x1 - x0) * (y1 - y0)
        if page_area and area / page_area < FRAME_AREA_RATIO:
            out.append(t)
    return out


_SUR_LIKE_TOKEN_RE = re.compile(r"^[A-Za-z.\-]{1,3}$")
_ALL_DIGITS_OR_SIGN_RE = re.compile(r"^[\dxX.\-]+$")


def sur_row_candidates(cropped_text):
    """Heuristically pick out the short-token 'sur-like' rows from a notation
    table's cropped text (see module docstring: sur-rows and lyric-rows alternate
    down the block). Returns the candidate lines as extracted, unconverted, exactly
    as found -- this is the 'raw_sur_row' content; no interpretation attempted."""
    candidates = []
    for line in cropped_text.splitlines():
        tokens = line.split()
        if len(tokens) < 4:
            continue
        if all(_ALL_DIGITS_OR_SIGN_RE.match(t) for t in tokens):
            continue  # numeric matra header / taal-sign row
        avg_len = sum(len(t) for t in tokens) / len(tokens)
        sur_like_frac = sum(1 for t in tokens if _SUR_LIKE_TOKEN_RE.match(t)) / len(tokens)
        if avg_len <= 2.4 and sur_like_frac >= 0.6:
            candidates.append(line.strip())
    return candidates


_RAAG_HEADING_RE = re.compile(r"rwg\s+(\S+)")
_TAAL_HEADING_RE = re.compile(r"qwl\s*:?\s*(\S+)")


def raag_taal_heading(raw_text):
    raag = _RAAG_HEADING_RE.search(raw_text)
    taal = _TAAL_HEADING_RE.search(raw_text)
    return (raag.group(1) if raag else None), (taal.group(1) if taal else None)


def first_lyric_line(prev_page_converted_text):
    """Best-effort shabad opening line from the PRECEDING page's converted text
    (notation pages follow their shabad's lyrics+pad-arth page in this book's
    layout). Skips blank lines, a bare verse-serial heading ('12.' / '੧੨.'), short
    bani-genre-label lines (e.g. 'ਬਿਸਨਪਦ ॥' -- a form label, not the shabad text,
    identified by having <=3 whitespace-separated tokens), and stops before the
    'pd - ArQ' / 'ਪਦ - ਅਰਥ' glossary heading."""
    if not prev_page_converted_text:
        return None
    for line in prev_page_converted_text.splitlines():
        s = line.strip()
        if not s:
            continue
        if re.fullmatch(r"[\d੦-੯]{1,3}\.?", s):
            continue
        if re.search(r"ਪਦ\s*-\s*ਅਰਥ|pd\s*-\s*ArQ", s, re.I):
            break
        if not _has_gurmukhi_unicode(s):
            continue
        if len(s.split()) <= 3:
            continue  # likely a bani-genre label line, not the actual verse
        if s.count("॥") > 1:
            continue  # compound genre/raag/invocation header line, not a verse
        return s
    return None


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main():
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    NOTATION_DIR.mkdir(parents=True, exist_ok=True)

    fitz_doc = fitz.open(str(BOOK_PDF))
    plumber_doc = pdfplumber.open(str(BOOK_PDF))

    # --- Pass 1: per-page raw text + method decision ---
    page_info = []  # list of dicts, 1 per page
    legacy_batch_indices = []
    legacy_batch_strings = []

    for i in range(TOTAL_PAGES):
        page_num = i + 1
        raw_text = page_raw_layout_text(page_num)
        any_unicode, any_legacy = page_method_signals(fitz_doc[i])

        note = ""
        if any_unicode and any_legacy:
            method = "mixed"
            note = ("Page has BOTH Gurmukhi-Unicode and legacy-ASCII-Gurmukhi span "
                     "signals; span-level interleaving not implemented, fell back to "
                     "gurmukhi-utils over the whole page. Needs manual double-check.")
        elif any_unicode:
            method = "cid-reorder"
        elif any_legacy:
            method = "gurmukhi-utils"
        else:
            method = "none"

        info = {"page": page_num, "raw_text": raw_text, "method": method, "note": note}
        page_info.append(info)

        if method in ("gurmukhi-utils", "mixed"):
            legacy_batch_indices.append(i)
            legacy_batch_strings.append(raw_text)

    # --- Pass 2: batch gurmukhi-utils conversion (one Node process for the book) ---
    print(f"[gurmukhi-utils] converting {len(legacy_batch_strings)} pages in one batch...",
          file=sys.stderr)
    converted_batch = gurmukhi_utils_batch(legacy_batch_strings)
    for idx, converted in zip(legacy_batch_indices, converted_batch):
        page_info[idx]["converted_text"] = converted

    for info in page_info:
        if info["method"] == "cid-reorder":
            info["converted_text"] = cid_unicode_fix(info["raw_text"])
        elif info["method"] == "none":
            info["converted_text"] = info["raw_text"]
        # "gurmukhi-utils" / "mixed" already set above

    # Known, deliberately-not-fixed residual issue (documented in EXTRACTION.md).
    page_info[0]["note"] = (page_info[0]["note"] + " " if page_info[0]["note"] else "") + (
        "Known residual: subtitle's leading 'ਸ਼' (sha, in 'ਸ਼ਬਦ'/Shabad) is silently "
        "dropped in the raw PDF text layer -- NOT reconstructed, left as extracted."
    )

    # --- Pass 3: section classification, notation detection/cropping, shabad match ---
    notation_records = []
    notation_block_count = 0
    match_tally = {"high": 0, "medium": 0, "none": 0}

    for i, info in enumerate(page_info):
        page_num = info["page"]
        plumber_page = plumber_doc.pages[i]
        tables = inner_tables(plumber_page)
        section, why = classify_section(page_num, info["raw_text"], bool(tables))

        page_record = {
            "page": page_num,
            "section": section,
            "text": info["converted_text"],
            "status": "draft",
            "extraction_method": info["method"],
            "notes": (f"section heuristic: {why}. " + info["note"]).strip(),
        }
        (PAGES_DIR / f"page-{page_num:03d}.json").write_text(
            json.dumps(page_record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

        if section != "notation":
            continue

        raag, taal = raag_taal_heading(info["raw_text"])
        prev_converted = page_info[i - 1]["converted_text"] if i > 0 else None
        candidate_line = first_lyric_line(prev_converted)
        if candidate_line:
            # source="D" (Dasam Bani / ਦਸਮ ਬਾਣੀ), NOT shabad_match's default "G" (Sri
            # Guru Granth Sahib Ji) -- this whole book is Dasam Granth compositions (the
            # foreword says so explicitly: "ਦਸਮ ਗ੍ਰੰਥ ਬਾਣੀ ਵਿਚ..."). Verified against
            # banidb.sources(): source_id 'D' = 'ਦਸਮ ਬਾਣੀ' / 'Dasam Bani'. Confirmed this
            # matters empirically: the default source="G" returned "none"/weak "medium"
            # mismatches against unrelated SGGS verses for every shabad tried in this
            # book; source="D" returns high-confidence, correct-writer
            # ("Guru Gobind Singh Ji") matches for the same lines.
            shabad_match = match_shabad(candidate_line, source="D")
        else:
            shabad_match = {"shabad_id": None, "confidence": "none",
                             "method": "no-candidate-line-found", "matched_verse": None}
        match_tally[shabad_match.get("confidence", "none")] = (
            match_tally.get(shabad_match.get("confidence", "none"), 0) + 1
        )

        fitz_page = fitz_doc[i]
        blocks_this_page = [t for t in tables if _has_matra_header_table(t)]
        if not blocks_this_page and tables:
            # Has inner tables but none matched the matra-header check closely enough
            # (e.g. odd layouts) -- still use them rather than falling back blind.
            blocks_this_page = tables

        if blocks_this_page:
            for k, table in enumerate(blocks_this_page, start=1):
                notation_block_count += 1
                rect = fitz.Rect(*table.bbox)
                pix = fitz_page.get_pixmap(clip=rect, dpi=150)
                img_name = f"page-{page_num:03d}-block-{k}.png"
                pix.save(str(NOTATION_DIR / img_name))

                cropped_text = plumber_page.crop(table.bbox).extract_text(layout=True) or ""
                sur_lines = sur_row_candidates(cropped_text)

                notation_records.append({
                    "book": SLUG,
                    "page": page_num,
                    "image": f"notation/{img_name}",
                    "raw_sur_row": "\n".join(sur_lines) if sur_lines else None,
                    "raag": raag,
                    "taal": taal,
                    "shabad_match": shabad_match,
                    "extracted_first_line": candidate_line,
                    "status": "draft",
                    "needs_manual_transcription": True,
                    "notes": (
                        "raw_sur_row heuristically identified as the short-token rows "
                        "alternating with lyric rows below the taal-bol row (see script "
                        "docstring); NOT verified against SARGAM.md conventions -- do not "
                        "treat as canonical notation without human review against the "
                        "cropped image."
                    ),
                })
        else:
            # No bordered inner table on this notation-tagged page (raag-info block or
            # appendix table without clean borders) -- fall back to a full-page crop.
            notation_block_count += 1
            rect = fitz_page.rect
            pix = fitz_page.get_pixmap(clip=rect, dpi=150)
            img_name = f"page-{page_num:03d}-block-1.png"
            pix.save(str(NOTATION_DIR / img_name))
            notation_records.append({
                "book": SLUG,
                "page": page_num,
                "image": f"notation/{img_name}",
                "raw_sur_row": None,
                "raag": raag,
                "taal": taal,
                "shabad_match": shabad_match,
                "extracted_first_line": candidate_line,
                "status": "draft",
                "needs_manual_transcription": True,
                "notes": (
                    "No bordered inner table detected on this page (raag-characteristics "
                    "block or appendix content) -- cropped the FULL PAGE as a fallback "
                    "per the task's allowance; cropping is not precise here."
                ),
            })

    NOTATION_RAW_JSON.write_text(
        json.dumps(notation_records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Pages processed: {TOTAL_PAGES}")
    print(f"Notation blocks: {notation_block_count}")
    print(f"Shabad match tally: {match_tally}")


def _has_matra_header_table(table):
    """Does this specific inner table's own text contain the numeric matra header
    row? Used to prefer the real sur/taal-bol grid tables over incidental other
    bordered boxes pdfplumber may detect on the same page."""
    text = table.page.crop(table.bbox).extract_text(layout=True) or ""
    return _has_matra_header(text)


if __name__ == "__main__":
    main()
