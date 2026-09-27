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

## `size` counts spaCy tokens, not whitespace words

This is the part that surprises people. Measured:

```python
long_text = tr_text * 12
len(long_text.split())         # 360  ← whitespace "words"
len(tokenizer(long_text))      # 432  ← spaCy tokens
```

The ratio is 1.20; the difference is punctuation, which spaCy counts as
separate tokens. So:

```python
segments = tlf.segment_text(long_text, size=100, lang="tr")
len(segments)                             # 4
[len(s.split()) for s in segments]        # [83, 84, 84, 83]
```

432 tokens ÷ 100 = 4 full segments, and the remaining 32 tokens are
dropped. Each segment holds 100 **tokens** but 83–84 **words**.

??? note "Why spaCy tokens and not `\S+`"

    The first version of the plan used `re.finditer(r"\S+")`. It was
    measured and found not precise enough for research use: cutting at
    "exactly 1000 words" with `\S+` produced 40 segments that actually
    contained **1018–1562** spaCy tokens (the longest 53% longer than the
    shortest), and across that range TTR moved by **7.6%** in the same
    text.

    In other words, the length confusion that `min_fill` exists to prevent
    was entering through the counting method itself.

    The cost was measured and is negligible: 1.2 seconds per MB, about 1%
    of the `analyze()` calls that follow.

    Splitting on sentence boundaries was also tried and is worse: in text
    with broken punctuation a single "sentence" can be 2611 tokens, and
    segment size spreads over 385–2611.

## The last segment: `min_fill`

The default `min_fill=1.0` keeps only **full** segments. A short remainder
is discarded.

```python
tlf.segment_text(long_text, size=100, lang="tr")                  # 4
tlf.segment_text(long_text, size=100, min_fill=0.5, lang="tr")    # 4
```

Both give 4 here because the remainder is 32 tokens = 32%, below the `0.5`
threshold as well.

| `min_fill` | Meaning |
|---|---|
| `1.0` (default) | Full segments only. The cleanest comparison. |
| `0.5` | Also keep a last segment that is more than half full. |
| `0.0` | Keep whatever is left. **Breaks length comparability.** |

!!! warning "Discarded data is discarded silently"

    The library does not tell you how many segments it dropped. With
    `min_fill=1.0` and `size=1000`, a 1400-token file yields **one**
    segment and the remaining 400 tokens (punctuation included, ~330
    words) are gone. Short files in your
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

`unit="char"` counts raw characters; the tokenizer is not involved, so
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

`lang` must match the text. It defaults to `"tr"`; apostrophes and
abbreviations tokenize differently in the two languages, so splitting an
English text without `lang="en"` shifts the segment boundaries.

A segment's content is a **slice of the raw text**, not a re-joined token
list. Punctuation, whitespace and line breaks survive unchanged.
