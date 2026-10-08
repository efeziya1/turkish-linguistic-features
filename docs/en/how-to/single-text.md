# Analyse a single text

## The short version

```python
import turkish_linguistic_features as tlf

oz = tlf.analyze(text, lang="en")
```

What comes back is a flat `dict`: key is the feature name, value is a
number.

## The language changes the feature set

```python
tr = tlf.analyze(tr_text, lang="tr")
en = tlf.analyze(en_text, lang="en")

len(tr)   # 208
len(en)   # 181
```

The 27-feature difference breaks down as:

- **+23** Zeyrek suffix analysis: the `morphological_zeyrek` group (suffix
  chain, case markers, mood and tense; every key starts with `zeyrek_`) —
  Turkish only.
- **+2** vowel harmony (`harmony_fronting_ratio`, `harmony_rounding_ratio`) —
  a property of Turkish; not produced for English.
- **+3** letters: the Turkish alphabet has 29, English 26 (`ç ğ ı ö ş ü`
  only in Turkish, `q w x` only in English).
- **−1** readability: 3 Turkish-only features (the Ateşman, Çetinkaya-Uzun and
  Bezirci-Yılmaz formulas), 4 English-only features (the Flesch, Flesch-Kincaid
  and SMOG formulas and the polysyllabic word ratio); the shared ones exist in
  both.

The `phonetic` group has 14 features in Turkish and 12 in English.

`lang` accepts only `"tr"` and `"en"`. Anything else raises `ValueError`.

## Ask for specific groups

If you do not need all 208 features, pick groups; the output then carries
only those groups' keys:

```python
oz = tlf.analyze(text, lang="tr", groups=["readability", "lexical"])
len(oz)     # 45
```

Picking groups saves little time. Most of it goes to the spaCy and Zeyrek
preprocessing, which runs once whatever you ask for; groups only shorten the
calculation after it. On a 1000-word text all groups take about 1.2 seconds,
`readability` alone about 0.85 seconds.

The groups, with their Turkish feature counts:

| Group | Features | Contents |
|---|---|---|
| `lexical` | 38 | Lexical richness, frequency |
| `chars` | 29 | Letter frequency vector: one key per letter of the Turkish alphabet (26 in English; `q`, `w`, `x` only there) |
| `morphological_zeyrek` | 23 | Zeyrek suffix analysis (Turkish only) |
| `morphological` | 19 | UD morphological features |
| `punctuation` | 20 | Each mark type's share, punctuation density, capitalisation |
| `syntactic_dep` | 16 | Dependency parse |
| `phonetic` | 14 | Syllables, vowels, sound patterns |
| `frequency_structure` | 13 | Zipf, h-point, thematic concentration |
| `pos` | 12 | Part-of-speech shares |
| `syntactic` | 7 | Sentence structure |
| `sentence` | 7 | Sentence-length distribution |
| `readability` | 7 | Readability formulas |
| `paragraph` | 3 | Paragraph structure |

`describe_feature(key)["group"]` tells you where a given feature lives.

## Count your own phrases

If you are after a pattern the built-in features do not cover, pass it as
`custom_ngrams`:

```python
text = ("The old house was torn down. A new building went up, but the big garden "
        "stayed. Yet nobody forgot the old house.")
oz = tlf.analyze(text, lang="en", custom_ngrams=[["yet", "nobody"], ["ADJ", "NOUN"]])
oz["ngram_yet_nobody_count"]   # 1.0
oz["ngram_ADJ_NOUN_count"]     # 4.0
```

Each phrase becomes one key; its value is the number of matches in the text.

- Words are compared lowercased. The written form is matched, not the lemma:
  `old houses` would not match `old house`.
- An UPPERCASE UD part-of-speech tag (`NOUN`, `VERB`, `ADJ`…) matches any
  word carrying that tag. `["ADJ", "NOUN"]` means an adjective followed
  directly by a noun.
- A match never crosses a sentence boundary: `down. A` is not adjacent.
- The value is a plain count. To compare texts of different lengths, divide
  by `word_count` (`oz["ngram_ADJ_NOUN_count"] / oz["word_count"]`) or bring
  them to the same size first (`segment_size`).

The count answers "how often". To see **what** the phrase matched:

```python
tlf.ngram_matches(text, ["ADJ", "NOUN"], lang="en")
```

```text
{'old house': 2, 'new building': 1, 'big garden': 1}
```

The most frequent match comes first, and the counts add up to
`ngram_ADJ_NOUN_count`. Sentence and position are not returned. For several
texts, add the results up with `collections.Counter`. Working example:
[`examples/10_kelime_oruntuleri.py`](https://github.com/efeziya1/turkish-linguistic-features/blob/main/examples/10_kelime_oruntuleri.py).

## Progress output

For long texts:

```python
oz = tlf.analyze(text, lang="en", show_progress=True)
```

## Silence the warnings

If the optional `wordfreq` package is missing, the library raises
`MissingDependencyWarning` and leaves the two features that depend on it
(`wordfreq_*`) as `nan`. If you
are accepting that knowingly:

```python
oz = tlf.analyze(text, lang="en", warn=False)
```

`warn=False` **does not change the computation** — it only silences the
warning. The feature is still `nan`.

## Use a different spaCy model

```python
oz = tlf.analyze(text, lang="en", model="en_core_web_trf")
```

The defaults are `tr_core_news_md` and `en_core_web_sm`. If the model is
not installed you get `ModelNotFoundError`, and the message contains the
install command.

!!! warning "Changing the model changes the numbers"

    Tokenisation, part-of-speech tags, morphological tags and the
    dependency parse all come from the model. Do not compare a table produced with one model
    against a table produced with another. State which model you used in
    your methods section.

## Full signature

```python
analyze(
    text: str,
    lang: str = "tr",
    model: str | None = None,
    groups: list[str] | None = None,
    params: FeatureParams | None = None,
    custom_ngrams: list[list[str]] | None = None,
    show_progress: bool = False,
    warn: bool = True,
) -> dict[str, float]
```

For `params` see [Change the thresholds](parameters.md).
