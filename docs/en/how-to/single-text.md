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
len(en)   # 182
```

The 26-feature difference breaks down as:

- **+24** Zeyrek suffix analysis (`morphological_zeyrek`: suffix chain,
  case markers, mood and tense) — Turkish only.
- **+3** letters: the Turkish alphabet has 29, English 26 (`ç ğ ı ö ş ü`
  only in Turkish, `q w x` only in English).
- **−1** readability: three formulas in Turkish (Ateşman, Çetinkaya-Uzun,
  Bezirci-Yılmaz), four in English (Flesch, Flesch-Kincaid, SMOG and the
  polysyllabic word ratio); the shared ones exist in both.

The vowel harmony features are produced in both languages.

`lang` accepts only `"tr"` and `"en"`. Anything else raises `ValueError`.

## Ask for specific groups

Computing all 208 features takes time. If you do not need them all:

```python
oz = tlf.analyze(text, lang="tr", groups=["readability", "lexical"])
len(oz)     # 39
```

The groups, with their Turkish feature counts:

| Group | Features | Contents |
|---|---|---|
| `lexical` | 32 | Lexical richness, frequency |
| `chars` | 29 | Letter frequency vector: one key per letter of the Turkish alphabet (26 in English; `q`, `w`, `x` only there) |
| `morphological_zeyrek` | 24 | Zeyrek suffix analysis (Turkish only) |
| `morphological` | 19 | UD morphological features |
| `punctuation` | 18 | Punctuation ratios |
| `syntactic_dep` | 16 | Dependency parse |
| `phonetic` | 15 | Syllables, vowels, sound patterns |
| `frequency_structure` | 13 | Zipf, h-point, thematic concentration |
| `pos` | 13 | Part-of-speech ratios |
| `syntactic` | 9 | Sentence structure |
| `sentence` | 8 | Sentence-length distribution |
| `readability` | 7 | Readability formulas |
| `paragraph` | 5 | Paragraph structure |

`describe_feature(key)["group"]` tells you where a given feature lives.

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

    Sentence splitting, part-of-speech tags and the dependency parse all
    come from the model. Do not compare a table produced with one model
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
