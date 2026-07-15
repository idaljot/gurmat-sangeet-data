# Gurmat Sangeet Notation Dataset — Schema (DRAFT v0.1)

An open, structured dataset of raag reference data and kirtan swar (sur) notation
from the parampara of **Bhai Jaspal Singh Ji**.

This is a **data** repository, not an application. Any project may consume it.
The reference implementation is [ShabadSwar.com](https://shabadswar.com).

> **STATUS: DRAFT FOR REVIEW.** Not yet published as canonical. Pending review by
> Bhai Jaspal Singh Ji's family and technical review.

---

## Design principles

1. **JSON, and boringly simple.** A developer should be able to parse and use this
   in ten minutes. Simplicity drives adoption; complexity kills it.
2. **Data separate from display.** Notation is stored as one canonical ASCII string
   (see `SARGAM.md`). How it is *rendered* (Roman / Bhatkhande / Gurmukhi) is the
   consumer's concern, not the data's.
3. **Provenance and authority are first-class.** Every record carries where it came
   from and whether Bhai Jaspal Singh Ji has reviewed it. Consumers MUST be able to
   filter to only-approved data. Unverified data must never masquerade as authoritative.
4. **Additive, versioned, stable.** Once published, fields are not removed or
   repurposed. New fields may be added. Consumers should ignore unknown fields.
5. **Many-to-many by default.** The link between shabads and notations runs both
   ways: a shabad may have several notations, **and** one notation may serve several
   shabads (e.g. a single dhun sung across every pada of Sukhmani Sahib). The schema
   models this as a many-to-many relationship from day one, even where only
   one-to-one exists today.

---

## Repository layout

```
/
├── README.md              What this is, how to use it, license
├── SCHEMA.md              This file — the data contract
├── SARGAM.md              The notation string spec (how to read a notation string)
├── LICENSE                CC BY-NC 4.0 (proposed — see Licensing)
├── data/
│   ├── raags.json         Raag reference data
│   ├── notations.json     Kirtan compositions (sur + taal) for shabads
│   └── sources.json       Provenance registry (books, classes, contributors)
└── schema/
    ├── raag.schema.json       JSON Schema for validation
    └── notation.schema.json   JSON Schema for validation
```

Separate files (rather than one blob) so consumers can fetch only what they need,
and so a change to notation doesn't churn the raag file.

---

## Shared conventions

### Review status — the integrity backbone

Every record carries:

```jsonc
{
  "status": "approved",       // "approved" | "draft"
  "reviewedBy": "Bhai Jaspal Singh Ji",   // present only when status = approved
  "reviewedOn": "2026-07-12",             // ISO date, present only when approved
  "sourceRef": "book:gurmat-sangeet-vol1",// key into sources.json
  "sourceNote": "Compiled from public sources"  // free text, optional
}
```

- `approved` = Bhai Jaspal Singh Ji (or an authority he designates) has confirmed it.
- `draft` = compiled from other sources, submitted by a student, or otherwise
  unverified. **Consumers should visibly mark draft data as unverified.**

This distinction is the reason the dataset can be trusted. Do not drop it.

### Identifiers

- **`shabadIds`** — an **array** of shabad identifiers as used by the GurbaniNow /
  SikhiToTheMax ecosystem (e.g. `["JK3"]`). One notation may apply to several shabads
  (see "many-to-many" below), so this is **always an array** — a single-shabad
  notation is simply an array of one. Each ID is alphanumeric, case-sensitive, and
  globally unique across sources (Guru Granth Sahib Ji, Sri Dasam Granth, Vaaran Bhai
  Gurdas Ji, Bhai Nand Lal Ji).
- **`verseId`** — OPTIONAL. Identifies a specific line (pankti) within a shabad,
  used to point at the exact sthayi line rather than inferring it (e.g. from rahaao).
  Same ecosystem's line identifier. Meaningful only for a single-shabad record; leave
  `null` when a notation spans multiple shabads.
- **`notationId`** — this dataset's own stable ID for a notation record
  (e.g. `"n-0001"`). Required because a shabad may have several notations, and
  consumers need a stable handle for each.

### Text encoding rules (load-bearing)

- Plain UTF-8.
- Notation strings are **case-sensitive** — case carries komal/shuddh/teevra meaning.
  Never case-fold, lowercase, or `text-transform` notation. Doing so destroys meaning.
- Do not put notation in URL path segments without escaping.

---

## `data/raags.json`

A map of raag name → raag record.

```jsonc
{
  "Siree Raag": {
    "names": {
      "roman": "Siree Raag",
      "gurmukhi": "ਸਿਰੀਰਾਗੁ",
      "alternates": ["Sri Raag", "Sri"]        // spellings seen elsewhere
    },

    // --- Musical structure (the authoritative core) ---
    "thaat": "",                    // e.g. "Bilawal"
    "jati": "",                     // e.g. "Sampurna" (7 notes)
    "aroh": "",                     // ascending, as a SARGAM string: "S G m D N S."
    "avroh": "",                    // descending
    "pakad": "",                    // characteristic phrase, SARGAM string
    "vadi": "",                     // most prominent swar, e.g. "Ma"
    "samvadi": "",                  // second most prominent
    "komal": [],                    // e.g. ["Re", "Dha"]
    "teevra": [],                   // e.g. ["Ma"]
    "varjit": [],                   // omitted swars, e.g. ["Pa"]

    // --- Character (accessible, teaching-facing) ---
    "time": "",                     // traditional association, NOT a rule (see note)
    "season": "",                   // for seasonal raags, e.g. "Spring" (Basant)
    "mood": "",                     // rasa / character
    "notes": "",                    // teaching notes

    // --- Resources ---
    "resources": [
      {
        "type": "youtube-playlist",
        "url": "https://www.youtube.com/playlist?list=...",
        "label": "Bhai Jaspal Singh Ji — Raag Siree"
      }
    ],

    // --- Provenance ---
    "status": "draft",
    "sourceNote": "Compiled from public sources",
    "reviewedBy": null,
    "reviewedOn": null
  }
}
```

**Note on `time`:** In Gurmat Sangeet, raags express *mood* and are traditionally
**not** restricted to clock times the way Hindustani classical prescribes. The `time`
field records the traditional association only. Consumers should present it as such,
not as a rule.

**Note on scales:** `aroh`, `avroh`, and `pakad` are stored as SARGAM strings
(see `SARGAM.md`), not free text — so they are machine-readable and renderable in
any script (Roman / Bhatkhande / Gurmukhi), like any other notation.

---

## `data/notations.json`

An **array** of notation records. An array (not a map keyed by shabad) *because the
shabad ↔ notation relationship is many-to-many* — several notations may exist for one
shabad, and one notation may serve several shabads. See below.

```jsonc
[
  {
    "notationId": "n-0001",              // stable, unique within this dataset
    "shabadIds": ["JK3"],                // one OR MORE shabads this notation applies to
    "verseId": null,                     // OPTIONAL: exact sthayi line (single-shabad only)
    "appliesToNote": "",                 // OPTIONAL: human context when spanning many shabads

    "title": "Gur Arjan Vito Kurbani",   // human label for this composition
    "raag": "Soohi",                     // must match a key in raags.json
    "composer": "Bhai Jaspal Singh Ji",  // whose composition this is

    // --- Rhythm ---
    "taal": "Deepchandi",                // taal name
    "tempo": 170,                        // BPM, integer, nullable
    "key": "C#",                         // Sa pitch, nullable (e.g. "C#", "D")

    // --- The notation itself (SARGAM strings — see SARGAM.md) ---
    "sections": [
      { "label": "alaap",  "notation": "P D N S.  ..." },
      { "label": "sthayi", "notation": "G P D P D P M G R S" },
      { "label": "antara", "notation": "S. S. S. S. n n D D ..." },
      { "label": "antara", "notation": "..." }      // a 2nd antara is just another section
    ],

    // --- Resources ---
    "resources": [
      {
        "type": "youtube-video",
        "url": "https://www.youtube.com/watch?v=...",
        "label": "Bhai Jaspal Singh Ji"
      }
    ],

    // --- Provenance ---
    "status": "draft",
    "sourceRef": "book:gurmat-sangeet-vol1",  // key into sources.json, nullable
    "sourceNote": "",
    "contributor": "",                        // who entered it (optional, may be a handle)
    "reviewedBy": null,
    "reviewedOn": null,
    "addedOn": "2026-07-12"                   // ISO date
  }
]
```

A notation that spans a whole paath is one record with many `shabadIds`:

```jsonc
{
  "notationId": "n-0042",
  "shabadIds": ["SKM1", "SKM2", "SKM3", "…"],   // every pada it applies to
  "appliesToNote": "Standard Sukhmani Sahib paath dhun — same for every pada",
  "title": "Sukhmani Sahib",
  "raag": "Gauri",
  "sections": [ { "label": "sthayi", "notation": "…" } ],
  "status": "draft"
  // …provenance fields as above
}
```

### Why `sections` is an array, not fixed `sthayi`/`antara` fields

Real teaching material has: an alaap, a sthayi, one or more antaras, sometimes a
tukda or a variation. Fixed fields (`sthayi`, `antara`) cannot express *two* antaras
or an alternate version. An ordered array of `{label, notation}` expresses all of it,
and new section types can appear without a schema change.

Recognised labels (consumers should handle unknown labels gracefully):
`alaap`, `sthayi`, `antara`, `tukda`, `variation`, `other`.

### Why the shabad ↔ notation link is many-to-many

The relationship runs in both directions, so the schema supports both:

- **Many notations per shabad** — the same shabad may have several compositions
  (different raags, teachers, or arrangements). These are several records that each
  list that shabad in their `shabadIds`, distinguished by `notationId`, raag,
  composer, and title.
- **Many shabads per notation** — one notation may be reused across many shabads.
  The classic case is a paath like **Sukhmani Sahib**, where a single dhun is sung for
  every pada of every ashtapadi. That is **one** record whose `shabadIds` array lists
  all the shabads it applies to (with `appliesToNote` giving the human context).

Consumers building a "compositions for this shabad" view group notation records by
membership in `shabadIds` — i.e. find every record whose `shabadIds` contains the
shabad in question.

*(Note: the exact framing is pending Bhai Jaspal Singh Ji's input. The schema is
permissive — N records per shabad and N shabads per record — so it accommodates
whatever framing he uses.)*

---

## `data/sources.json`

Provenance registry, so `sourceRef` values resolve to something meaningful.

```jsonc
{
  "book:gurmat-sangeet-vol1": {
    "type": "book",
    "title": "…",
    "author": "Bhai Jaspal Singh Ji",
    "year": null,
    "note": "Notation transcribed from the printed book"
  },
  "class:2026": {
    "type": "class",
    "title": "Kirtan class notation, 2026",
    "note": "Entered by students, pending review"
  }
}
```

---

## Licensing (proposed)

**CC BY-NC 4.0** — free to use and adapt for **non-commercial** purposes,
**attribution to Bhai Jaspal Singh Ji required**.

Rationale: attribution honours the ustaad and his parampara; the non-commercial
restriction protects his sacred work from being absorbed into a paid product. This
matches the license already used on the ShabadSwar.com reference implementation
(CC BY-NC).

**Tradeoff to weigh in review:** NonCommercial is the more protective choice, but it
also *limits adoption* — any consumer that is even mildly commercial (an ad-supported
app, a paid teaching platform) cannot use the data. If maximum reach with openness is
preferred over the commercial restriction, the alternative is **CC BY-SA 4.0**
(attribution + share-alike: permits commercial use but forces derivatives to stay
open under the same terms). CC BY (attribution only) is the maximally permissive option.

**Gurbani text itself is in the public domain.** This license covers the *notation,
raag data, and compilation* — the scholarly and musical work — not the shabads.

> **Requires Bhai Jaspal Singh Ji's family's explicit blessing before publishing.**
> It is his data and his name; the license is his call, not ours. The BY-NC proposal
> above is a starting point for that conversation, not a settled decision.

---

## Versioning

Semantic versioning on the dataset (`v0.1.0` → `v1.0.0` at first authoritative
release). Tagged releases so consumers can pin a version. Additive changes bump
minor; a breaking schema change bumps major (and should be rare — see principle 4).

---

## Open questions (for review)

1. **Multiplicity framing** — pending Bhai Jaspal Singh Ji's input on how he thinks
   about multiple notations of one shabad. The schema is permissive; his framing may
   suggest which fields distinguish them (raag? composer? title?).
2. **Ma convention — SETTLED (shuddha-set).** `SARGAM.md` uses `M` = shuddh madhyam,
   `m` = teevra madhyam (uppercase = shuddh, lowercase = altered). Notation scripts are
   Roman/Latin and Gurmukhi only (Bhatkhande dropped). Still confirm each *book's* ma
   readings against the source when transcribing — the convention is fixed, but reading a
   given ma as shuddh vs teevra in Ustaad ji's notation still takes care.
3. **`verseId` adoption** — is pointing at the exact sthayi line worth the extra
   entry effort, vs. inferring from rahaao? Depends on how often they diverge.
4. **Governance** — who may mark a record `approved`? Presumably Bhai Jaspal Singh Ji
   or someone he designates. Needs to be stated, not assumed.
5. **Taal data** — should the dataset also carry taal definitions (thekas)? Currently
   consumers each define their own. Including them would help, but taal thekas are
   more standardised and less "his" than the raag/notation data.
6. **License** — BY-NC (proposed, matches ShabadSwar) vs BY-SA (wider reach). The
   family decides; see Licensing.
7. **Representing large regular structures** — for a long paath like Sukhmani Sahib,
   listing every pada's id in `shabadIds` may be verbose. Is an enumerated array
   sufficient, or should the schema also support a compact range/pattern form (e.g.
   "all padas of Bani X")? Enumerate for now; a range form can be added additively
   (principle 4) if entry proves painful.
