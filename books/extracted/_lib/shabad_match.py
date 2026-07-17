"""
Shabad identification helper for book extraction (Phase B).

Uses the `banidb` PyPI package (KhalisFoundation/BaniDB), the actively-maintained
successor in the SikhiToTheMax/GurbaniNow lineage. NOTE: the task originally named
"GurbaniNow" -- that API (api.gurbaninow.com) is explicitly marked deprecated upstream
and was confirmed non-functional in this session (its own documented example query
returns zero results). BaniDB is the same broad ecosystem/ownership (KhalisFoundation)
and was validated end-to-end here: searching the exact known text of SGGS Ang 727
("ਹਰਿ ਜਸੁ ਰੇ ਮਨਾ ਗਾਇ ਲੈ ਜੋ ਸੰਗੀ ਹੈ ਤੇਰੋ ॥") returns shabad_id 2779 with the correct
ang/raag/writer -- exact match, not a guess.

This module never invents a shabadId. If nothing matches with reasonable confidence,
it returns confidence "none" and the caller must leave shabadId unset / flag for
manual identification -- do not guess a shabad for sacred content.

Usage:
    from shabad_match import match_shabad
    result = match_shabad("ਹਰਿ ਜਸੁ ਰੇ ਮਨਾ ਗਾਇ ਲੈ")
    # result = {"shabad_id": 2779, "confidence": "high", "method": "exact-line",
    #           "matched_verse": "...", "ang": 727, "raag": "...", "writer": "..."}
"""

import difflib
import re

import banidb

_GURMUKHI_RE = re.compile(r"[਀-੿]")


def _gurmukhi_ratio(text):
    if not text:
        return 0.0
    letters = len(text)
    gurmukhi = len(_GURMUKHI_RE.findall(text))
    return gurmukhi / letters


def _normalize(s):
    return re.sub(r"\s+", " ", s).strip()


def _similarity(a, b):
    return difflib.SequenceMatcher(None, _normalize(a), _normalize(b)).ratio()


def match_shabad(candidate_line, source="G", min_gurmukhi_ratio=0.5):
    """
    Try to identify a shabad from an extracted line of text (first line / mool
    panktee of a shabad, however noisy). Returns a dict with confidence
    "high" | "medium" | "none". Never fabricates a match.

    Tiered strategy, most to least strict:
      1. Exact-line search (searchtype=2) on the raw candidate text.
      2. If that fails, try the same search on progressively shorter leading
         substrings (helps when OCR/extraction garbled the tail of the line).
      3. If nothing found, return confidence "none" -- caller must flag for
         manual identification, not guess.

    Any hit is scored by string similarity between the candidate and the
    returned verse; below 0.6 similarity is downgraded to "medium" even on an
    exact-search hit, since the search can return a *different* verse if the
    candidate matched a common phrase inside it.
    """
    candidate = _normalize(candidate_line)
    if not candidate or _gurmukhi_ratio(candidate) < min_gurmukhi_ratio:
        return {"shabad_id": None, "confidence": "none", "method": "not-gurmukhi",
                "matched_verse": None}

    tried = []
    for cutoff_words in (None, 8, 5, 3):
        query = candidate
        if cutoff_words is not None:
            words = candidate.split(" ")
            if len(words) <= cutoff_words or cutoff_words in tried:
                continue
            query = " ".join(words[:cutoff_words])
        tried.append(cutoff_words)

        try:
            r = banidb.search(query, searchtype=2, source=source)
        except Exception as e:
            return {"shabad_id": None, "confidence": "none", "method": f"error: {e}",
                    "matched_verse": None}

        if r.get("total_results", 0) < 1:
            continue

        top = r["pages_data"]["page_1"][0]
        verse = top["verse"]
        sim = _similarity(candidate, verse)
        confidence = "high" if sim >= 0.6 else "medium"
        return {
            "shabad_id": top["shabad_id"],
            "confidence": confidence,
            "method": f"exact-line-search(words={cutoff_words or 'all'})",
            "similarity": round(sim, 3),
            "matched_verse": verse,
            "ang": top.get("source", {}).get("ang"),
            "raag": top.get("source", {}).get("raagpu"),
            "writer": top.get("source", {}).get("writer"),
        }

    return {"shabad_id": None, "confidence": "none", "method": "no-match-any-tier",
            "matched_verse": None}


if __name__ == "__main__":
    # self-test against the known-good Ang 727 line
    r = match_shabad("ਹਰਿ ਜਸੁ ਰੇ ਮਨਾ ਗਾਇ ਲੈ ਜੋ ਸੰਗੀ ਹੈ ਤੇਰੋ ॥")
    assert r["shabad_id"] == 2779, f"self-test failed: {r}"
    assert r["confidence"] == "high", f"self-test failed: {r}"
    print("self-test OK:", r)
