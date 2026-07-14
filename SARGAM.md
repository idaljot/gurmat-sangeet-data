# SARGAM — Canonical Notation Spec

A deterministic, web-safe notation for Hindustani / Gurmat Sangeet swara and tal.
This is the single source of truth for how notation is **stored**. Pretty rendering
(Bhatkhande dots/dashes, or Gurmukhi script) is a **display layer** generated from this
form — never the other way around. The reference parser lives in `src/lib/sargam.js`.

Synthesized and corrected from G.S. Mansukhani, *Indian Classical Music and Sikh Kirtan*,
and sharda.org's "Notation & Taal Systems". Both keep an ASCII fallback alongside their
diacritic form; this spec makes that fallback consistent and complete.

> There is no single traditional standard either: the diacritic notation itself splits into
> two lineages — the **Bhatkhande** and **Paluskar (Vishnu Digambar)** paddhatis — and the
> Roman single-letter form has no agreed convention at all (see §1). That's the whole reason
> for this document: store **one** canonical form, and render any tradition on top of it.

---

## 0. Design decisions (read this first)

- **Case carries meaning.** Uppercase / lowercase distinguishes the two chromatic variants
  of a swara. This is the standard sargam-text convention (sharda, and common music
  software), so notation copies in and out of the wider ecosystem without translation.
  We considered a case-free suffix scheme (`R_`, `M^`) and rejected it: it's non-standard,
  more verbose, and the risks it guards against are cheaply mitigated (see §6).
- **The rule for case is uniform:** *lowercase = the lower of the two chromatic pitches* —
  no exception, including Ma. Be clear-eyed that there is **no industry-wide standard** for
  single-letter Hindustani notation (§1 documents the competing convention). The value of
  this spec isn't that it found the "right" answer — it's that it makes one explicit,
  documented choice and applies it consistently.
- **`.` is reserved exclusively for octave.** Never a rest, never sentence punctuation
  inside a token.
- **Data stays plain ASCII.** Every token is typable on any keyboard and survives
  copy-paste, search, CSV/JSON, RSS, forms, and screen readers unchanged.

---

## 1. Swara (note) encoding

| Swara | Komal (lower) | Shuddh / natural | Teevra (higher) |
|-------|---------------|------------------|-----------------|
| Sa    | —             | `S`              | —               |
| Re    | `r`           | `R`              | —               |
| Ga    | `g`           | `G`              | —               |
| Ma    | —             | `m`              | `M`             |
| Pa    | —             | `P`              | —               |
| Dha   | `d`           | `D`              | —               |
| Ni    | `n`           | `N`              | —               |

**Rule:** lowercase is always the **lower-pitched** member of a pair.

For Re/Ga/Dha/Ni the lower member is the *komal* (flat) note, so `r g d n` = komal.
For **Ma**, the two variants are shuddh Ma and the *higher* teevra Ma — so the lower one,
shuddh Ma, is lowercase `m`, and teevra Ma is uppercase `M`.

> ⚠️ **Ma is contested — there is no standard, so read this.** Single-letter Hindustani
> notation splits into two principled camps that disagree only on Ma:
>
> - **Pitch-height convention (this spec):** lowercase = the lower semitone of every pair,
>   uniformly. So `m` = **shuddh** Ma, `M` = **teevra** Ma. Layout: `S r R g G m M P d D n N`.
> - **Shuddha-set convention (Rajan Parrikar and others):** all seven shuddh notes are
>   uppercase and *every* alteration — komal **and** teevra — is lowercase. So `M` = shuddh
>   Ma, `m` = teevra Ma. Layout: `S r R g G M m P d D n N`. Its appeal is that uppercase
>   `SRGMPDN` then spells exactly the natural (Bilaval) scale.
>
> Both rules are internally consistent; they partition the octave on different principles
> (pitch height vs. primary-vs-altered). We default to the **pitch-height** convention
> because it appears to be the majority usage and is what most software emits — best for
> interop. **But this is the single most likely point of disagreement with an outside
> source.** If your teachers, community, or source material use the shuddha-set convention,
> flip it: swap the `variant` values on `m` and `M` in `sargam.js` (one line each). Nothing
> else in the system depends on the choice.

`S` and `P` have only one form and are always uppercase. Lowercase `s` / `p` are **invalid**.

---

## 2. Octave (saptak)

| Octave | Mark | Example |
|--------|------|---------|
| Ati-mandra (2 below) | two leading dots | `..N` |
| Mandra (1 below)     | one leading dot  | `.N`  |
| Madhya (middle, default) | none         | `N`   |
| Tar (1 above)        | one trailing dot | `N.`  |
| Ati-tar (2 above)    | two trailing dots| `N..` |

A token may have leading **or** trailing dots, never both. `.` means octave and nothing
else, so it never collides with a sentence period (and §6 keeps notation in `<code>` anyway).

---

## 3. Beats, duration, and grouping

A notation line is a sequence of whitespace-separated **beat tokens** (matras).

| Element | Token | Meaning |
|---------|-------|---------|
| One swara = one beat | `S` | the default |
| Multiple swaras in one beat | `(S R)` | wrap 2+ swaras in parentheses; the whole group occupies one beat (faster subdivision) |
| Sustain / hold | `-` | a standalone beat that extends the previous swara by one more beat |
| Rest / silence | `_` | a standalone silent beat |

Examples:

```
S  -  G  -          Sa held two beats, then Ga held two beats
(S R) (g m) P        beat 1 = Sa+Re, beat 2 = komal-Ga + shuddh-Ma, beat 3 = Pa
S  _  S  _           Sa, silence, Sa, silence
```

Parentheses replace the source documents' hyphen-grouping so that `-` can carry its more
standard sargam meaning (sustain). Grouping is unambiguous and nests one level only.

---

## 3a. Vocal interjections (labels)

Kirtan notation sometimes has a spoken/sung interjection between phrases of swara — most
commonly **"Waheguru"** written inline rather than set to notes. Any bare alphabetic token
that (a) is 3+ characters and (b) is made up mostly of letters outside the swara alphabet
(`S r R g G m M P d D n N`) is parsed as a **label** event and passed through verbatim —
it isn't translated into any script, it just displays as-is in all three notation hands:

```
P D N S. | Waheguru | S. N D P
```

parses to a `section`, three notes, a `{type:'label', text:'Waheguru'}`, another
`section`, and three more notes.

This is deliberately narrow: a short token that's mostly-valid swara letters (e.g. a typo
like `Sx`) is **not** treated as a label — it still raises a parse error, because it's more
likely a mistake that should be caught by validation (§6/build pipeline) than a real word.

---

## 4. Structural separators

| Separator | Meaning | Timing effect |
|-----------|---------|---------------|
| space | beat (matra) boundary | advances one beat |
| `,` (comma) | phrase / sub-phrase boundary | none — readability only |
| `|` (pipe) | section / vibhaag boundary | aligns to tal claps; none on its own |

Section labels (written in full, they're rare per line): `Asthai`, `Antra`, `Sanchari`,
`Abhog`, `Rahau`.

---

## 5. Tal (rhythm cycle)

| Element | Mark |
|---------|------|
| Sam (first beat / arrival) | `X` |
| Tali (clap) | the ordinal of the clap: `2`, `3`, `4`, … |
| Khali (empty / wave) | `0` |

`X` is used for sam rather than `+`, because a literal `+` decodes to a space inside URL
query strings and would corrupt in any link, slug, or form field. `X` / `0` / digits have
no reserved meaning in HTML, URLs, CSV, or regex.

**Teentaal (16 beats, 4 vibhaags):**

| Beat | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|------|---|---|---|---|---|---|---|---|---|----|----|----|----|----|----|----|
| Mark | X |   |   |   | 2 |   |   |   | 0 |    |    |    | 3  |    |    |    |

---

## 6. Site / storage rules

The case-based encoding is robust **as long as case is preserved end to end.** The two
things that can quietly fold case are both cheap config fixes, not reasons to change the
encoding:

1. **Inputs.** On any field where users type notation, disable mobile auto-capitalization
   and autocorrect:
   ```html
   <input class="sargam" autocapitalize="off" autocorrect="off" spellcheck="false">
   ```
   (Auto-capitalize only ever fires at the start of a field / after sentence punctuation,
   and only *raises* case — so this one attribute closes the only realistic input hazard.)

2. **Storage & search must be case-sensitive.**
   - Use a case-sensitive DB collation for notation columns (e.g. MySQL
     `utf8mb4_0900_as_cs` or `utf8mb4_bin`; Postgres is case-sensitive by default). A
     case-folding collation makes `Sr` and `SR` collide in unique indexes and lookups.
   - Do **not** lowercase URL slugs derived from notation.
   - If you expose search-by-notation, build that index case-sensitively, or komal and
     shuddh become indistinguishable.

Additional display/storage hygiene:

- Wrap every notation string in `<code>` (or a `.sargam` element) so a sentence-final
  period is never read as a tar-octave dot, and prose styling can't bleed in.
- **Never** apply CSS `text-transform: uppercase/lowercase` to notation. It's display-only
  and won't corrupt stored data, but it will visually turn komal into shuddh for the reader.
  Scope such rules away from notation classes.
- Store as plain UTF-8 text with no rich-text dependency, so it exports cleanly to CSV/JSON,
  print, and assistive tech.
- Avoid `+` and `#` in any token that can reach a URL (`#` is the fragment delimiter). This
  spec already does.

**Plan B (only for uncontrolled inputs you can't set attributes on):** fall back to
case-insensitive suffix accidentals — `Rt Gt Dt Nt`? no — use a letter suffix so it stays
URL-safe: komal `Rb Gb Db Nb`, teevra `Mt`. Document it as a separate mode; do not mix it
into the primary system.

---

## 7. Worked example — Siri Raag (illustrative)

> **Unverified data.** The raga attributes below are illustrative and reconstructed; confirm
> them against the source book before publishing. Note also that **Siri Raag** as the opening
> raga of the Guru Granth Sahib is not simply identical to Hindustani **Raga Shree** — treat
> the Gurmat Sangeet form on its own terms rather than assuming the Hindustani mapping.

| | Traditional (as printed) | Canonical |
|---|---|---|
| Aroha    | S r r P, m P N Ṡ                     | `S r r P , m P N S.` |
| Avaroha  | Ṡ N d P, m D m G R, R R P R G G R S | `S. N d P , m D m G R , R R P R G G R S` |
| Pakad    | S, r, r, P, m G r, G R S            | `S , r , r , P , m G r , G R S` |

---

## 8. Migrating pre-spec notation

The class's earliest hand-entered notation (before this spec existed) used a different
octave mark and ran multiple swaras together with no separator. The merge step in
`scripts/fetch-notation.mjs` normalizes it automatically on every fetch (see
`normalizeLegacyNotation()` there) — nothing needs to change in the Google Sheet. Known
translations:

| Legacy | Canonical | Note |
|--------|-----------|------|
| `S'` | `S.` | trailing apostrophe → trailing dot (tar) |
| `S"` | `S..` | trailing double-quote → double trailing dot (ati-tar) |
| `.N` | `.N` | leading dot already meant mandra — unchanged |
| `GGGG` | `G G G G` | legacy notation ran same-beat letters together with no space; audited against each shabad's known taal (word-lengths cleanly matching the taal's vibhag structure) to confirm one letter = one beat |
| `(mG)` | `(m G)` | groups already used parens; just needed the internal space |
| `*` | *(stripped)* | undocumented marker found only in two legacy shabads; meaning unconfirmed, flagged for manual follow-up rather than guessed at |

---

## 9. Quick reference (footer / contributor card)

```
Shuddh:   S  R  G  m  P  D  N          (Ma natural = lowercase m)
Komal:    r  g  d  n                    (Re Ga Dha Ni only)
Teevra:   M                             (Ma only; uppercase = sharp)
Octave:   .N mandra   N tar   ..N/N.. ati-
Beat:     (space)   In-beat group: (S R)   Hold: -   Rest: _
Phrase: ,     Section: |     Label (spoken interjection): bare word, e.g. Waheguru
Tal:      Sam X   Tali 2/3/4…   Khali 0
```
