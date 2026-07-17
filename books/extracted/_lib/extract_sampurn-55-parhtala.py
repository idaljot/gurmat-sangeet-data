"""
Phase B full extraction driver for Sampurn 55 Parhtala
(books/2 Sampurn 55 Parhtala  Shabad Sur Rachnavali Final with cover.pdf, 228pp).

Method validated in Phase A (books/extracted/_sample/sampurn-55-parhtala/REPORT.md):
prose uses a "reordering-bug" Gurmukhi font (letters correct, vowel-sign/halant
order wrong) -- OCR sidesteps this since it reads shaped glyphs, not codepoints.
Notation grid tables use a fully broken font subset (unusable text layer).
One page (the foreword, page 4 in the Phase A sample) uses a legible
AnmolLipi/GurbaniAkhar-style ASCII transliteration scheme; Phase A flagged
that OCR is an acceptable uniform fallback rather than special-casing that
page's detection, which is the choice made here (no gurmukhi-utils routing --
reliably detecting "is this THE AnmolLipi page" from OCR output alone was
judged more fragile than just OCR'ing it like everything else; it still goes
through the pipeline as prose/front-matter and is captured as draft text).

`pdftoppm -r 150` + `tesseract -l pan`, default PSM uniformly (see
extract_asa-di-vaar.py docstring for why default PSM is used for the
whole-page pass rather than switching PSM per page speculatively).

Run from repo root:
    .venv-extraction/bin/python3 books/extracted/_lib/extract_sampurn-55-parhtala.py
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from books.extracted._lib.extraction_common import run_extraction  # noqa: E402

if __name__ == "__main__":
    run_extraction(
        slug="sampurn-55-parhtala",
        pdf_path=REPO_ROOT / "books" / "2 Sampurn 55 Parhtala  Shabad Sur Rachnavali Final with cover.pdf",
        psm_config="",  # tesseract default PSM (3)
        extraction_method_label="ocr-tesseract-pan(default-psm)",
        ocr_confidence_note=(
            "Prose (foreword/essays/shabad text) ~95-97% accuracy (Phase A "
            "estimate), correct reading order via OCR despite the underlying "
            "reordering-bug font. Italic-styled quoted Gurbani lines degrade "
            "sharply. Notation grid tables: ~60-75% cell recovery, not "
            "trustworthy as-is. Foreword page's AnmolLipi-scheme text is "
            "OCR'd like any other page (not routed through gurmukhi-utils "
            "toUnicode in this pass). All notation flagged "
            "needs_manual_transcription regardless."
        ),
        force_notation_default=False,
    )
