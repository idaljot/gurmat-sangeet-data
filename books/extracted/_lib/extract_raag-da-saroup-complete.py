"""
Phase B full extraction driver for Raag Da Saroup Complete
(books/Raag Da Saroup Complete.pdf, 31pp).

Method validated in Phase A (books/extracted/_sample/raag-da-saroup-complete/REPORT.md):
this book mixes legacy-ASCII, wrong-ToUnicode CID, and legible-AnmolLipi-scheme
fonts, sometimes within a single page/field -- all three unusable directly.
`pdftoppm -r 150` + `tesseract -l pan --psm 4` is the validated method
(--psm 4, NOT --psm 6: Phase A confirmed --psm 6 silently drops entire
label:value rows on this book's list-style layout).

The book is almost entirely raag-reference label:value entries (Thaat/Jaati/
Vaadi/Samvaadi/Sur/Varjit Sur/Samay/Aroh/Avroh/Mukh Ang per raag), so
force_notation_default=True biases the page classifier toward `notation`
for any page with at least one recognizable raag-entry label -- matching
the book's actual structure (see classify_section in extraction_common.py).

Run from repo root:
    .venv-extraction/bin/python3 books/extracted/_lib/extract_raag-da-saroup-complete.py
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from books.extracted._lib.extraction_common import run_extraction  # noqa: E402

if __name__ == "__main__":
    run_extraction(
        slug="raag-da-saroup-complete",
        pdf_path=REPO_ROOT / "books" / "Raag Da Saroup Complete.pdf",
        psm_config="--psm 4",
        extraction_method_label="ocr-tesseract-pan(--psm4)",
        ocr_confidence_note=(
            "Labels and short values (Thaat/Jaati/Vaadi/Samvaadi/Sur/Varjit "
            "Sur/Samay) ~95%+ accurate with --psm 4 (Phase A estimate). "
            "Aroh/Avroh/Mukh Ang lines -- the actual sur data -- are "
            "unreliable: OCR collapses or partially collapses inter-syllable "
            "spacing on nearly every entry, the worst failure mode of any "
            "content type across all 3 books. All notation flagged "
            "needs_manual_transcription regardless."
        ),
        force_notation_default=True,
    )
