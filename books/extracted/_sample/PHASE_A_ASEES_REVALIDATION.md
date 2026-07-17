# Asees legacy-font re-validation (Part 2 checkpoint)

**Status: calibration finding, not yet applied to any extraction. Checkpoint per task
instructions — reporting before running full 767/780-page extraction on Guru Nanak Bani
Vol. I/II.**

## Headline: Phase A's "Asees is unmapped, 0% confidence" conclusion is too pessimistic

Phase A tested `gurmukhi-utils toUnicode()` directly against raw Asees-encoded text and
it failed (confirmed again here — see baseline test below). But that's the wrong test:
Asees isn't the same ASCII scheme as AnmolLipi/GurbaniLipi, so feeding it straight to a
tool built for that scheme was never going to work. It doesn't mean Asees is unmappable.

Using the `.gmf` mapping tables now in `custom-font-mapping/` as a **bridge** — convert
Asees's raw extracted characters to the AnmolLipi ASCII convention first, *then* run
`gurmukhi-utils toUnicode()` — recovers real, correct Punjabi/Gurmukhi words. Tested
empirically, not assumed:

**Baseline (confirms Phase A was right to flag this as broken on its own):**
```
IN:  r[o{ BkBe d/t ih dh ;zg{oD pkDh L Ppd ;[o ouBktbh
gurmukhi-utils direct: ਰ।ੋ{ ਭਕਭੲ ਦ/ਟ ਹਿ ਦਹ ;ਜ਼ਗ{ੋਧ ਪਕਧਹ ਲ਼ ਫਪਦ ;।ੋ ੋੁਭਕਟਬਹ   [garbage]
```

**Bridged via `custom-font-mapping/mapping.sgphar.0.5/SGPHar to Unicode.gmf` (166 rules)
then `gurmukhi-utils`:**
```
IN:     r[o{ BkBe d/t ih dh ;zg{oD pkDh L Ppd ;[o ouBktbh
BRIDGE: gurU nwnk dyv jh dh sMpUrx bwxh : >bd sur rcnwvlh
OUT:    ਗੁਰੂ ਨਾਨਕ ਦੇਵ ਜਹ ਦਹ ਸੰਪੂਰਣ ਬਾਣਹ : >ਬਦ ਸੁਰ ਰਚਨਾਵਲਹ
TRUE (read off the rendered page-400 footer): ਗੁਰੂ ਨਾਨਕ ਦੇਵ ਜੀ ਦੀ ਸੰਪੂਰਨ ਬਾਣੀ : ਸ਼ਬਦ ਸੁਰ ਰਚਨਾਵਲੀ
```

Verified against the actual rendered page (`Guru Nanak Bani Vol. II`, p.400/Ang 1127,
footer line, and the raag heading): consonant skeleton and most vowels are **correct**
(`ਗੁਰੂ ਨਾਨਕ ਦੇਵ` matches exactly; `ਰਾਗੁ ਭੈਰਉ` — tested separately — matches exactly).

## What's still wrong, precisely

Three recurring, systematic (not random) residual errors, all confirmed against the
rendered page:

1. **Bare `h` is ambiguous.** This book's "Asees" font uses the same extracted character
   for both ਹ (consonant "ha") and, in some positions, the vowel sign ੀ (bihari/long-ee) —
   e.g. `ਜੀ`→`ਜਹ`, `ਦੀ`→`ਦਹ`, `ਬਾਣੀ`→`ਬਾਣਹ`. Confirmed this is not a missing rule: SGPHar's
   own table has an *explicit* `h`→`h` identity rule, meaning the table's author assumed
   `h` always means ਹ. It doesn't, for this specific font. This needs either a smarter
   context rule or a different/corrected mapping table — not yet solved.
2. **Nasal confusion**: `ਸੰਪੂਰਨ` (Sampooran) came out as `ਸੰਪੂਰਣ` (wrong nasal, ਨ vs ਣ) —
   single-character mapping gap.
3. **Missing rule for `ਸ਼`**: the "sha" character (rendered as `>` after the bridge step)
   has no rule in SGPHar's table, so it passes through as literal `>`.

**Notation/sur rows do not benefit from this fix.** Tested on Vol. I p.20 (the "Asees"
sur-notation row of a Sorath-family table) — the bridged output is not coherent Gurmukhi
words (as expected: sur rows aren't prose, they're syllable-per-cell notation, sometimes
mixing plain Gurmukhi consonants used as sur symbols with dashes/spacing that this
character-level bridge isn't designed to handle). **This does not change Phase A's
notation-fidelity conclusion — sur content still needs manual transcription regardless of
font.** It only changes the outlook for *prose*.

## Where this leaves the "held books" call

- **Guru Nanak Bani Vol. I & II prose**: was "~20-30%/40-50% reliably extractable, Asees
  portion effectively 0%." Revised: Asees prose now has a working (if imperfect —
  3 known systematic error classes above) automated bridge. Rough accuracy on the tested
  passages, eyeballed against the page image: high-80s to low-90s% at the character level,
  concentrated errors in vowel-length/nasal distinctions rather than wrong consonants.
- **Guru Tegh Bahadur Ji's silent-substitution CID font bug**: untouched by this finding —
  different book, different failure mode (not a legacy ASCII font at all). Still needs
  OCR/GurbaniNow cross-check as before.
- I have **not** run this bridge across the full 767/780 pages, and have not attempted to
  fix the three residual error classes — that's real, scoped follow-up work, not
  something to greenlight sight-unseen for two ~800-page books. Per the checkpoint
  instruction, holding here rather than proceeding to full-volume extraction.

## Recommendation

Worth pursuing as a near-term follow-up (likely fixable — the `h` ambiguity in particular
may resolve by testing whether context [preceding character] disambiguates it, or by
checking whether a different one of the 7 downloaded mapping tables handles this book's
specific font better), but **not done yet**, and I'm not running the full-volume
extraction until it is. The 4 in-scope books for tonight's Phase B (Guru Gobind Singh Ji
Di Bani, Asa Di Vaar, 2 Sampurn 55 Parhtala, Raag Da Saroup Complete) are unaffected by
this and don't depend on it.
