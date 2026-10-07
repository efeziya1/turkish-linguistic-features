"""One word definition for the whole library (2026-10-07, Efe).

Every group except ``syntactic_dep`` counts the default word (``kelime_birimleri``:
whitespace unit, edge punctuation stripped). Groups that need a tag per word (POS,
morphology, lemma, Zeyrek morphemes) take it from the model token the word holds:
the first token inside the word's whitespace chunk that is not punctuation or a
symbol. A word split into several tokens (TR ``Türk-Amerikan``, ``4-5``; EN ``it's``,
``don't``) therefore gets its first part's tag. Measured: 0.31 % of Turkish and
2.66 % of English words are split (300 columns each).

Pure computation on ready-made lists (K3). Tokens that cannot be found in the raw
text in order mean the inputs are not aligned: preprocessing error → ``ValueError`` (K4).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..alfabe import _kucuk_harf
from ..vocab import NON_WORD_POS
from .readability import word_units

__all__ = ["WordView", "word_token_indices", "word_view"]

_UNANALYSED = "Unk"


def word_token_indices(raw_text: str, surface_tokens: list[str],
                       pos_data: list[tuple[str, str]], lang: str) -> list[int | None]:
    """For each default word, the index of its tag-bearing token in ``surface_tokens``.

    ``None`` when every token inside the word is punctuation or a symbol (rare: a
    word made of digits the model tagged ``SYM``, for instance).
    """
    if len(surface_tokens) != len(pos_data):
        raise ValueError(
            f"surface_tokens ({len(surface_tokens)}) is not aligned with pos_data "
            f"({len(pos_data)}) — preprocessing error"
        )
    starts: list[int] = []
    cursor = 0
    for tok in surface_tokens:
        at = raw_text.find(tok, cursor)
        if at < 0:
            raise ValueError(f"token {tok!r} not found in raw_text — preprocessing error")
        starts.append(at)
        cursor = at + len(tok)

    out: list[int | None] = []
    t = 0
    for _, is_word, chunk_start, chunk_end in word_units(raw_text, lang):
        while t < len(starts) and starts[t] < chunk_start:
            t += 1
        if not is_word:
            continue
        found = None
        k = t
        while k < len(starts) and starts[k] < chunk_end:
            if found is None and pos_data[k][1] not in NON_WORD_POS:
                found = k
            k += 1
        out.append(found)
    return out


@dataclass(frozen=True)
class WordView:
    """Tag-level inputs re-expressed per default word (all lists aligned with ``words``)."""

    words: list[str]
    pos: list[tuple[str, str]]
    lemmas: list[str]
    morph: list[tuple[str, str]] | None
    morphemes: list[Any] | None
    sentences: list[list[str]]


def word_view(raw_text: str, words: list[str], surface_tokens: list[str],
              pos_data: list[tuple[str, str]], lemma_tokens: list[str],
              morph_tags: list[tuple[str, str]] | None, morpheme_lists: list[Any] | None,
              sentences: list[list[str]], lang: str) -> WordView:
    """Per-word POS, lemma, morphology and Zeyrek morphemes, plus words per rule sentence.

    ``lemma_tokens`` is aligned with the word tokens of ``pos_data`` (punctuation and
    symbols left out, T21). ``sentences`` is ``kural_cumleleri``'s output (token lists
    that concatenate to ``surface_tokens``); a word belongs to the sentence of its
    tag-bearing token. A word without such a token gets ``X``, its lowercased form as
    lemma and an unanalysed morpheme entry.
    """
    idx = word_token_indices(raw_text, surface_tokens, pos_data, lang)
    if len(idx) != len(words):
        raise ValueError(f"default words ({len(words)}) do not match word units ({len(idx)})")

    for name, lst in (("morph_tags", morph_tags), ("morpheme_lists", morpheme_lists)):
        # An empty morpheme_lists is English (no Zeyrek), not a misalignment.
        if lst is not None and len(lst) and len(lst) != len(pos_data):
            raise ValueError(
                f"{name} ({len(lst)}) is not aligned with pos_data ({len(pos_data)})"
                f" — preprocessing error"
            )
    word_tokens = [i for i, (_, p) in enumerate(pos_data) if p not in NON_WORD_POS]
    if len(word_tokens) != len(lemma_tokens):
        raise ValueError(
            f"lemma_tokens ({len(lemma_tokens)}) is not aligned with the word tokens of "
            f"pos_data ({len(word_tokens)}) — preprocessing error"
        )
    lemma_of = dict(zip(word_tokens, lemma_tokens, strict=True))

    sent_of: list[int] = []
    for s, cumle in enumerate(sentences):
        sent_of += [s] * len(cumle)

    pos: list[tuple[str, str]] = []
    lemmas: list[str] = []
    morph: list[tuple[str, str]] = []
    morphemes: list[Any] = []
    groups: dict[int, list[str]] = {}
    last_sent = 0
    for w, i in zip(words, idx, strict=True):
        if i is None:
            pos.append((w, "X"))
            lemmas.append(_kucuk_harf(w, lang))
            morph.append((w, ""))
            morphemes.append(((_UNANALYSED, w, False),))
        else:
            pos.append((w, pos_data[i][1]))
            lemmas.append(lemma_of[i])
            if morph_tags is not None:
                morph.append((w, morph_tags[i][1]))
            if morpheme_lists:
                morphemes.append(morpheme_lists[i])
            if i < len(sent_of):
                last_sent = sent_of[i]
        groups.setdefault(last_sent, []).append(w)

    return WordView(
        words=list(words),
        pos=pos,
        lemmas=lemmas,
        morph=morph if morph_tags is not None else None,
        # Empty lists on an empty text still mean "measured" (all NaN, K4); empty lists
        # next to tokens mean English, which has no Zeyrek morphemes.
        morphemes=morphemes if morpheme_lists is not None and (morpheme_lists or not pos_data)
        else None,
        sentences=[groups[s] for s in sorted(groups)],
    )
