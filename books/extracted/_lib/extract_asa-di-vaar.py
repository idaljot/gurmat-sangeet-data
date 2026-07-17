"""
Phase B full extraction driver for Asa Di Vaar (books/Asa Di Vaar.pdf, 217pp).

Method validated in Phase A (books/extracted/_sample/asa-di-vaar/REPORT.md):
text layer is a wrong-ToUnicode CID font (prose) mixed with a legacy-ASCII
WinAnsi font (grid tables) -- both unusable directly. `pdftoppm -r 150` +
`tesseract -l pan` OCR is used uniformly; prose and grid-table pages use the
same default/--psm 6-equivalent config (see extraction_common.ocr_page,
which is called once per page -- default tesseract PSM (3) is used, matching
Phase A's "prose pages used default PSM; grid/table pages used --psm 6"
finding that default PSM already handles both reasonably and --psm 6 was
specifically for grid pages; since we don't know a page's type before OCR'ing
it, and the shared pipeline crops to tables/lines separately from the raw
page OCR anyway, default PSM is used for the whole-page pass here).

Run from repo root:
    .venv-extraction/bin/python3 books/extracted/_lib/extract_asa-di-vaar.py
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from books.extracted._lib.extraction_common import run_extraction  # noqa: E402

if __name__ == "__main__":
    run_extraction(
        slug="asa-di-vaar",
        pdf_path=REPO_ROOT / "books" / "Asa Di Vaar.pdf",
        psm_config="",  # tesseract default PSM (3); see module docstring
        extraction_method_label="ocr-tesseract-pan(default-psm)",
        ocr_confidence_note=(
            "Prose ~95-97% char accuracy (Phase A estimate). Bordered grid "
            "tables: ~85-90% for sparse/12-col tables, ~50-65% for dense/16-col "
            "tables -- not trustworthy at high density. Inline Aroh/Avroh lines "
            "outside tables: inter-syllable spacing collapses, worse than table "
            "OCR. All notation flagged needs_manual_transcription regardless."
        ),
        force_notation_default=False,
    )
