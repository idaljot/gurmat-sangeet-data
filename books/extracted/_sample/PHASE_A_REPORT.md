# Phase A — extraction calibration report

**Status: draft calibration notes. No canonical data produced. Awaiting sign-off before Phase B.**

Samples, rendered page images, and full per-book detail live in `books/extracted/_sample/<slug>/REPORT.md`.
This file is the cross-book synthesis.

## Headline: the pre-existing per-book diagnosis needed real revision

Every book's actual font situation differs from the prior diagnosis, in most cases by a lot.
Two new failure modes turned up that the original diagnosis didn't anticipate:

1. **Silent wrong-letter substitution** (not just reordering) in a "looks Unicode, `pdffonts`
   says `uni=yes`" CID font — confirmed in *Guru Tegh Bahadur Ji* and *Asa Di Vaar* by
   comparing extracted text against known Gurbani (SGGS Ang 727: rendered `ਹਰਿ ... ਤੇਰੋ`,
   `pdftotext` extracts `ਹਤਰ ... ਿੇਰੋ`). This is more dangerous than obvious mojibake because
   it produces fluent-looking, plausible Gurmukhi that a fast reviewer could mistake for correct.
2. **Word-level font mixing inside "clean" pages** — in *Guru Nanak Bani Vol. I*, individual
   words fall back to an unmapped legacy font in the middle of otherwise-clean lines, so
   page-level "this page is fine" checks aren't sufficient.

## Per-book summary

| Book | Prior diagnosis said | What's actually true | Best method found | Prose accuracy | Notation verdict |
|---|---|---|---|---|---|
| Guru Gobind Singh Ji Di Bani (131pp) | Unicode + sipari fix | 98% of pages are legacy AnmolLipi/GurbaniLipi ASCII, not a few pages | `gurmukhi-utils toUnicode()` (open-source, Shabad OS) → NFC | ~95%+ | Structurally reliable (real table borders), needs human verification per table |
| Guru Tegh Bahadur Ji (135pp) | Same issue as book above | Mostly clean-looking CID Unicode, but confirmed **silent letter-substitution bug** in the embedded font | None reliable — OCR as second opinion only | ~85-90% but wrong subset is misleading, not random | **Do not trust without human read of the page image** |
| Guru Nanak Bani Vol. I (767pp) | "Text-based, extracts fine" | 77% legacy-encoded, split across 2 incompatible schemes (1 fixable, 1 not); even "good" pages have word-level fallback | `gurmukhi-utils` for GurbaniLipi runs; Asees runs unmapped | ~20-30% reliably extractable today | Mixed; Asees-font tables need OCR/manual |
| Guru Nanak Bani Vol. II (780pp) | "Text-based, extracts fine" | 49% legacy-encoded, **entirely** unmapped Asees font (no fixable fallback) | Sihari-reorder+NFC for CID runs only | ~40-50% reliably extractable today | Asees-font tables: 0% confidence, needs OCR/manual |
| Asa Di Vaar (217pp) | Legacy ASCII font + some images | Confirmed, but the "Unicode-looking" font also has the silent-substitution bug — both paths need OCR, not the text layer | `pdftoppm` + `tesseract -l pan` (OCR) | ~95-97% | Grid tables 50-90% (density-dependent); inline Aroh/Avroh **collapses spacing**, needs manual transcription |
| 2 Sampurn 55 Parhtala (228pp, not in original list) | — | Scary font signature, but prose is in better shape than feared | OCR | ~95-97% | Notation grids badly broken (~60-75%, text layer fully garbled) — manual transcription |
| Raag Da Saroup Complete (31pp, not in original list) | — | Almost entirely raag-reference label:value data — the highest notation-density book | OCR (`--psm 4`, not `--psm 6`) | Labels ~95%+ | **Aroh/Avroh/Mukh Ang lines unreliable** — OCR collapses inter-syllable spacing on nearly every entry |

## Cross-cutting pattern worth designing around

**Bordered grid tables tolerate OCR much better than inline space-separated swara lists.**
Every book shows the same split: a real PDF table with cell borders (e.g. taal-bol grids)
extracts with recoverable structure, while a swara sequence written as plain
space-separated text in running prose or a label:value field (Aroh/Avroh lines) has its
inter-syllable spacing collapsed by OCR almost every time. This means notation risk isn't
just "which book" — it's "which layout shape," and Phase B should treat inline notation
lines as needing manual transcription by default, independent of which book they're in.

## Two open problems before Phase B can hit good numbers

1. **No verified Asees-font mapping was found or derived.** This blocks ~half of Guru
   Nanak Bani Vol. I and all of Vol. II's legacy content. Options: source a mapping (ask
   Anmol/the family if the digitizer has one), fall back to OCR for Asees runs, or leave
   that content flagged for manual transcription in Phase B.
2. **The silent-substitution CID font bug** (Guru Tegh Bahadur Ji, Asa Di Vaar) has no
   known fix — it's not a clean cipher. OCR is the only cross-check found so far, and OCR
   has its own error rate (~3-5% on clean prose, worse on notation).

## Recommendation

Text extraction is viable and can likely hit high accuracy for **prose/commentary** using a
per-run method dispatch (gurmukhi-utils for AnmolLipi/GurbaniLipi legacy runs, sihari-reorder+NFC
for genuine clean CID runs, OCR for wrong-ToUnicode CID runs and for books where the text layer
is untrustworthy end-to-end). **Notation/swara content should not be auto-extracted as data in
any book** — capture it as a page image and route it to manual transcription, per the "wrong
notation is worse than no notation" rule. This matches the task's original framing (~99% target
applies to text, notation stays draft) but the manual-transcription share of notation is larger
than the original diagnosis assumed, especially for inline (non-tabular) swara lines.
