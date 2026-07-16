# Extraction diagnosis — Guru Tegh Bahadur Ji (Shabad Sur Rachnavali), 135pp

**Status: draft calibration notes (Phase A). No canonical data produced.**

## Headline finding — refutes prior diagnosis, in the opposite direction from book 1

The prior diagnosis grouped this book with book 1 as having "the sipari
reorder artifact." Empirically: **134 of 135 pages extract as majority clean
Unicode Gurmukhi** (page 135 is blank/image-only) — there is **no** widespread
legacy-ASCII-font mojibake here (unlike book 1, which was ~98% legacy-encoded).
So the prior diagnosis's premise ("same issue as book 1") is wrong.

**However, the actual problem is worse in a different way, and this is the
most important finding for this book.** The embedded CID Gurmukhi font
(`ABCDEE+Raavi` / `ABCDEE+Raavi,Bold`, Identity-H, `uni=yes` per `pdffonts` —
i.e. it *looks* trustworthy from font metadata alone) has a **corrupted or
misaligned `ToUnicode` CMap**. Naive extraction does not just reorder
characters (the book-1-style sipari artifact) — it **substitutes wrong
Gurmukhi letters for correct ones**, silently. This was independently
confirmed on page 80 (Ang 727, a well-known, verifiable shabad):

- Rendered/true text (confirmed via 300dpi visual read AND `tesseract -l pan`
  OCR, both agree): **ਹਰਿ ਜਸੁ ਰੇ ਮਨਾ ਗਾਇ ਲੈ ਜੋ ਸੰਗੀ ਹੈ ਤੇਰੋ ॥**
- Raw `pdftotext` extraction of the exact same line: **ਹਤਰ ਜਸੁ ਰੇ ਮਨਾ ਗਾਇ ਲੈ
  ਜੋ ਸੰ ਗੀ ਹੈ ਿੇਰੋ ॥**

`ਹਿਰ` came out as `ਹਤਰ` and `ਤੇਰੋ` came out as `ਿੇਰੋ` — i.e. sihari (ਿ) and
`ਤ` (ta) are cross-substituted. On page 1 a *different* wrong-substitution
pattern shows up in the same font family (e.g. `ਮਾਹਿਰਾਂ` extracts as
`ਮਾਵਹਰਾਂ` — ਿ dropped, spurious ਵ appears). This is consistent with a
systematically shifted/misaligned CMap table rather than one simple
two-character swap rule — **do not attempt a global find-and-replace fix**;
the exact substitution appears to depend on which specific glyph slot in the
subsetted font is hit, which varies.

## Method per content type

| Content | Method | Confidence |
|---|---|---|
| Front matter (pp.1-2) | `pdftotext -layout`, raw; cross-checked against `tesseract -l pan` OCR of the same page | Low-medium — legible enough to gist, not safe to quote verbatim |
| Shabad lyrics (pp.20, 80) | Same | Low-medium; page 80 specifically validated wrong at word level (see above) |
| Notation table (p.21) | Same — table is CID Unicode this time (not legacy-ASCII like book 1's tables), genuine bordered PDF table | Structure believable; individual syllables NOT verified reliable given the confirmed substitution bug in this exact font |

No legacy-ASCII (`uni=no`) font pages were found in this sample (unlike book
1). `pdffonts` still lists `FNTSBS+*`/`AnmolLipi`/`GurbaniLipi` `uni=no`
variants as *embedded* in this PDF, but they did not appear in use on any of
the 5 sampled pages — worth re-checking on a wider sample before assuming
they're unused throughout.

## Text-accuracy estimate

Rough eyeball against OCR + rendered PNGs: **~85-90% of characters correct,
but the wrong ~10-15% are not random noise — they are plausible-looking
Gurmukhi letters in the wrong place**, which is more dangerous for a sacred
text than obvious mojibake (garbled AnmolLipi-style text is at least
obviously wrong and won't be mistaken for real Gurbani; this substitution bug
produces fluent-looking but factually wrong Gurmukhi that a fast reviewer
could miss). Treat this as a strong caution flag, not a percentage to
casually accept.

## Specific issues found

1. **New finding, not in prior diagnosis**: corrupted/misaligned ToUnicode
   CMap in the embedded Raavi CID font causing silent letter substitution
   (confirmed, see above) — more severe than simple reordering.
2. **Prior diagnosis's "book 1 = book 2, same sipari issue" claim is not
   supported** — book 2 is not legacy-ASCII-encoded like book 1's body text;
   its problem is different and, if anything, harder to detect automatically
   because output still looks like plausible Gurmukhi.
3. Mid-word extraneous space characters appear (e.g. `ਸੰ ਗੀਤ` instead of
   `ਸੰਗੀਤ`) — a separate, more common and more benign justification-related
   PDF extraction artifact; simple whitespace collapsing would likely fix
   this but was not applied to the samples (kept raw for diagnostic honesty).
4. Sargam row in the notation table (p.21) again includes plain Latin `S`
   mixed with Gurmukhi cells (same pattern as book 1) — consistent with the
   author's convention of writing sur directly in Latin sargam letters.
5. OCR (`tesseract -l pan`) was measurably more accurate than raw text
   extraction on every page tested, though not perfect itself (introduces
   its own errors, e.g. `ਗੁਏਵਾਨਾਂ` for what should likely be `ਗੁਣਵਾਨਾਂ`) —
   OCR should be treated as a second opinion, not ground truth.

## Notation-fidelity verdict

**Needs manual transcription / human verification, more so than book 1.**
Given the confirmed silent-substitution bug in this exact font, I do not
recommend trusting extracted sargam-table text for this book without a
human directly reading the rendered page image. The Latin sargam row is
probably safe (matches book 1's pattern), but the Gurmukhi taal-bol and
lyric context around it cannot currently be automatically verified as
correct — the corruption is real and specific, not hypothetical.

## Files in this sample
`page-1.png/txt`, `page-2.png/txt` (front matter), `page-20.png/txt`
(lyrics), `page-21.png/txt` (notation table), `page-80.png/txt` (lyrics,
the validated Ang-727 corruption case). Each `.txt` includes both the raw
`pdftotext` output and a `tesseract -l pan` OCR pass for comparison.
