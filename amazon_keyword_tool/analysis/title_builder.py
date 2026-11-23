# title_builder.py — Rule-based Amazon listing title suggestion

"""
Builds a suggested product title from a keyword report.

The title starts with the search keyword, then adds the report's top keywords
and competitor-gap keywords (alternating, so neither list crowds out the
other).

The keyword extractor returns overlapping n-grams of the same phrase
("water", "water resistant", "ipx5 water resistant", "water resistant touch"),
so the builder keeps phrases intact and in reading order:

  1. a keyword that is only a fragment of a longer keyword is dropped;
  2. keywords that overlap end-to-start are merged into one chain
     ("ipx5 water resistant" + "water resistant touch" becomes
     "ipx5 water resistant touch"), which rebuilds the word order real
     listings use;
  3. chains are added by priority, either whole (all words new) or as a
     continuation of the title's last words, with multi-word chains ahead of
     single words (a phrase says more than a lone word like "ear" or "use");
  4. a word never appears twice, and a chain that would push the title past
     the length limit falls back to its shorter phrases so they can still fit.

The title aims for a readable length (TARGET_TITLE_LENGTH) rather than
filling Amazon's full limit with a keyword list. The hard limit is never
exceeded.

This is a deterministic starting point for a seller to edit, not an AI rewrite.
"""

from itertools import zip_longest

# Amazon's maximum title length for most categories.
MAX_TITLE_LENGTH = 200

# Where the builder stops adding keywords. Long keyword lists read as spam, so
# the default aims well below the hard limit.
TARGET_TITLE_LENGTH = 120

# A chain: its words in order, and the original keywords it is made of.
Chain = tuple[list[str], list[str]]


def _title_case(text: str) -> str:
    return " ".join(w[:1].upper() + w[1:] for w in text.split())


def _interleave(top_keywords: list[str], gap_keywords: list[str]) -> list[str]:
    """top[0], gap[0], top[1], gap[1], ... (the longer list's tail follows)."""
    merged = []
    for top, gap in zip_longest(top_keywords, gap_keywords):
        if top:
            merged.append(top)
        if gap:
            merged.append(gap)
    return merged


def _cut_at_word_boundary(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    cut = text[:max_len]
    if text[max_len] != " " and " " in cut:  # cut landed mid-word: drop the partial word
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip()


def _is_fragment(words: list[str], other: list[str]) -> bool:
    """True if `words` appears contiguously inside the longer phrase `other`."""
    n = len(words)
    return len(other) > n and any(other[i:i + n] == words for i in range(len(other) - n + 1))


def _drop_fragments(keywords: list[str]) -> list[str]:
    """Remove duplicates and any keyword that is a fragment of a longer one."""
    split = {kw: kw.lower().split() for kw in keywords}
    kept, seen = [], set()
    for kw in keywords:
        if kw in seen or not split[kw]:
            continue
        seen.add(kw)
        if not any(_is_fragment(split[kw], other) for other in split.values()):
            kept.append(kw)
    return kept


def _overlap(first: list[str], second: list[str]) -> int:
    """How many leading words of `second` repeat the end of `first` (0 if none)."""
    for k in range(min(len(second) - 1, len(first)), 0, -1):
        if first[-k:] == second[:k]:
            return k
    return 0


def _merge_chains(keywords: list[str]) -> list[Chain]:
    """
    Merge keywords that overlap end-to-start into chains, longest overlap first.
    A merge that would repeat a word is not made. Each chain keeps the priority
    of its best-ranked member.
    """
    chains: list[Chain] = [(kw.lower().split(), [kw]) for kw in keywords]

    while True:
        best = None  # (overlap, i, j)
        for i, (a, _) in enumerate(chains):
            for j, (b, _) in enumerate(chains):
                if i == j:
                    continue
                k = _overlap(a, b)
                if k and not set(a) & set(b[k:]) and (best is None or k > best[0]):
                    best = (k, i, j)
        if best is None:
            return chains

        k, i, j = best
        (a, members_a), (b, members_b) = chains[i], chains[j]
        chains[min(i, j)] = (a + b[k:], members_a + members_b)
        del chains[max(i, j)]


def _words_to_add(title_words: list[str], phrase: list[str]) -> list[str]:
    """
    The words of `phrase` to append to the title, in order; [] means skip it
    (already covered, would split the phrase up, or would repeat a word).
    """
    present = set(title_words)
    if not phrase or all(w in present for w in phrase):
        return []
    if not any(w in present for w in phrase):
        return phrase
    k = _overlap(title_words, phrase)
    rest = phrase[k:]
    if k and not any(w in present for w in rest):
        return rest
    return []


def build_title(
    search_keyword: str,
    top_keywords: list[str],
    gap_keywords: list[str],
    max_len: int = MAX_TITLE_LENGTH,
    target_len: int = TARGET_TITLE_LENGTH,
) -> dict:
    """
    Suggest a listing title for ``search_keyword``.

    Args:
        search_keyword: The term that was researched; the title starts with it.
        top_keywords:   Keywords ranked by importance, best first.
        gap_keywords:   Competitor-gap keywords (used by top sellers, rare elsewhere).
        max_len:        Hard length limit for the title (never exceeded).
        target_len:     Length at which keywords stop being added (capped at max_len).

    Returns:
        {"title": str, "keywords_used": list[str], "length": int, "max_length": int}
    """
    title = _cut_at_word_boundary(_title_case(search_keyword), max_len)
    if not title:
        return {"title": "", "keywords_used": [], "length": 0, "max_length": max_len}

    title_words = title.lower().split()
    used: list[str] = []
    limit = min(max_len, target_len)

    def try_add(words: list[str], members: list[str]) -> bool:
        nonlocal title
        to_add = _words_to_add(title_words, words)
        if not to_add:
            return False
        candidate = f"{title} {_title_case(' '.join(to_add))}"
        if len(candidate) > limit:
            return False
        title = candidate
        title_words.extend(to_add)
        used.extend(members)
        return True

    chains = _merge_chains(_drop_fragments(_interleave(top_keywords, gap_keywords)))
    chains.sort(key=lambda chain: len(chain[0]) == 1)  # stable: phrases first, then single words
    for words, members in chains:
        if try_add(words, members) or len(members) == 1:
            continue
        # The chain didn't go in whole (too long, or it clashes with the title):
        # try its phrases one by one so shorter ones can still fit.
        for member in members:
            try_add(member.lower().split(), [member])

    return {
        "title": title,
        "keywords_used": used,
        "length": len(title),
        "max_length": max_len,
    }
