# Gurmat Sangeet Notation Dataset — Vision

*A short note for Anmol. Written to explain the idea and, more importantly, to ask
for your guidance — on the data and on the direction.*

---

## The idea in one line

Take Bhai Jaspal Singh Ji's raag and notation work — which today lives in books,
classes, and memory — and turn it into a single, open, structured dataset that any
website, app, or study tool can use faithfully, with his name on it and with a clear
line between what he has approved and what is still unverified.

## Why bother

Right now, if three different people build kirtan-teaching tools, each re-enters the
same notation, makes its own mistakes, and none of them agree. If instead there is
**one trustworthy source** that everyone draws from, the tradition is represented
consistently everywhere, Ustaad ji is credited everywhere, and no one has to redo the
work. ShabadSwar.com would be the first tool to use it; kirtan.education could be the
second. The dataset is the foundation both sit on.

## The two things that make it trustworthy

1. **Provenance.** Every entry records where it came from.
2. **Authority.** Every entry is marked `approved` (Ustaad ji has confirmed it) or
   `draft` (compiled or student-entered, not yet verified). Tools must show the
   difference, so unverified notation can never quietly pass as his.

This is the heart of it: the value isn't that the data is *available*, it's that it's
*trustworthy*. That only works if the approval process is real — which is where you
and Ustaad ji come in.

## How it would grow (roadmap)

1. **Now — agree the shape.** Circulate the schema (the data structure) and this
   vision for review. Nothing is built on top yet.
2. **Get Ustaad ji's material.** The notation PDFs, transcribed carefully into the
   format — as `draft` until he confirms.
3. **Ustaad ji reviews.** Entries he confirms flip to `approved`.
4. **Publish + invite.** Release it openly under a license his family blesses, and
   invite other projects (starting with kirtan.education) to build on it.

There is no rush on any step. Getting it right matters more than getting it fast —
wrong notation is worse than no notation.

## Where I need your guidance

You know the tradition and the data far better than I do. The questions I'd most value
your thinking on:

- **Faithfulness.** Does structuring the work this way risk flattening anything
  important about how it's actually taught and sung?
- **Multiplicity.** A shabad can have more than one composition, and one dhun can
  cover a whole paath (like Sukhmani Sahib). Does the way I've modeled that match how
  Ustaad ji thinks about it?
- **The Ma convention.** Whether `m` means the shuddh or teevra madhyam has to be
  settled by ear with Ustaad ji — every notation depends on it. Can we sit with him on
  this?
- **Governance.** Who, besides Ustaad ji, should be able to mark something
  `approved`? This should be his call, stated clearly, not assumed.
- **Licensing.** I've proposed non-commercial + attribution (CC BY-NC), matching
  ShabadSwar. But it's his work and his name — the license is the family's decision.
  What would they be comfortable with?
- **Vision.** Am I aiming at the right thing? What would make this genuinely useful to
  teachers and students, versus just technically tidy?

## What's attached

- `SCHEMA.md` — the full data structure, with the reasoning behind each choice.
- `demo/index.html` — a small visual demo of how a tool would display the data.
  **Everything in it is placeholder sample data**, only there to show the shape and
  flow — none of it is Ustaad ji's real notation.

Thank you for looking at this. Your read on whether it honours the parampara matters
more than any technical detail.
