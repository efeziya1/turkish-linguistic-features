# Split a text into segments

## Why it matters

Lexical richness features are **sensitive to text length**. TTR always
falls as a text gets longer, `hapax_ratio` falls, `yule_k` drifts. Put a
50 000-word novel and an 800-word column in the same table and what you
measure is not style, it is length. `mattr`, `mtld` and `vocd_d` are less
sensitive than TTR but not independent of length
([measured example](https://github.com/efeziya1/turkish-linguistic-features/blob/main/examples/09_uzunluk_duyarliligi.py)).

The fix is to bring everything to the same size.

```python
segments = tlf.segment_text(text, size=1000, lang="en")
```

## `size` counts words

`size` counts the word `analyze` counts: a whitespace-separated piece with
edge punctuation stripped, containing a letter or digit. Punctuation is not a
word. With the 30-word Turkish `metin` from the
[Turkish tutorial](../../tr/baslangic.md):

```python
long_text = " ".join([metin] * 12)             # 360 words
segments = tlf.segment_text(long_text, size=100, lang="tr")
len(segments)                                  # 3
[len(s.split()) for s in segments]             # [100, 100, 100]
```

360 words ÷ 100 = 3 full segments, and the remaining 60 words are dropped.
Each segment is exactly 100 words in `analyze`, enough for a measure such as
`mattr` that needs at least 100 words.

## The last segment: `min_fill`

The default `min_fill=1.0` keeps only **full** segments. A short remainder
is discarded.

```python
tlf.segment_text(long_text, size=100, lang="tr")                  # 3
tlf.segment_text(long_text, size=100, min_fill=0.5, lang="tr")    # 4
```

The remainder is 60 words, 60% of a segment: below the `1.0` threshold,
above `0.5`.

| `min_fill` | Meaning |
|---|---|
| `1.0` (default) | Full segments only. The cleanest comparison. |
| `0.5` | Also keep a last segment that is more than half full. |
| `0.0` | Keep whatever is left. **Breaks length comparability.** |

!!! warning "Discarded data is discarded silently"

    The library does not tell you how many segments it dropped. With
    `min_fill=1.0` and `size=1000`, a 1400-word file yields **one**
    segment and the remaining 400 words are gone. Short files in your
    corpus may produce no segments at all.

    Use it knowingly. If in doubt, count first:

    ```python
    for path in files:
        n = len(tlf.segment_text(path.read_text(encoding="utf-8"),
                                 size=1000, lang="en"))
        print(path.name, n)
    ```

## Splitting by characters

```python
tlf.segment_text(text, size=5000, unit="char", lang="en")
```

`unit="char"` counts raw characters; the word rule is not involved, so
`lang` becomes meaningless. It does not respect word boundaries — a
segment can end mid-word. Use it when a rough split is enough.

## Use it directly on a corpus

You do not have to split and call `analyze` yourself:

```python
rows = tlf.analyze_corpus("corpus/", lang="en", segment_size=1000)
```

`segment_size`, `min_fill` and `unit` mean the same thing and are applied
**to each file separately**.

## Full signature

```python
segment_text(
    text: str,
    size: int = 1000,
    min_fill: float = 1.0,
    unit: str = "word",
    lang: str = "tr",
) -> list[str]
```

`lang` must match the text. It defaults to `"tr"`. The word rule is nearly the
same in both languages; the difference is ordinals (in Turkish the `3.` of
`3. kat` is one word), so an English text rarely shifts its boundaries.

A segment's content is a **slice of the raw text**, not a re-joined word
list. Punctuation, whitespace and line breaks survive unchanged.
