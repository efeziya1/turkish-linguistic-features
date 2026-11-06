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

len(tr)   # 214
len(en)   # 181
```

The 33-feature difference breaks down as:

- **+23** Zeyrek suffix analysis: the `morphological_zeyrek` group (suffix
  chain, case markers, mood and tense; every key starts with `zeyrek_`) —
  Turkish only.
- **+2** vowel harmony (`harmony_fronting_ratio`, `harmony_rounding_ratio`) —
  a property of Turkish; not produced for English.
- **+3** letters: the Turkish alphabet has 29, English 26 (`ç ğ ı ö ş ü`
  only in Turkish, `q w x` only in English).
- **+5** readability: 12 Turkish-only features (the Ateşman, Çetinkaya-Uzun and
  Bezirci-Yılmaz formulas; [Kalyoncu's](../explanation/kalyoncu.md) four formulas and five
  components), 7 English-only features (the Flesch, Flesch-Kincaid,
  SMOG, ARI, Coleman-Liau and LIX formulas and the polysyllabic word ratio); the
  shared `long_word_ratio` exists in both.

A readability formula is computed only in the language it was built for. A formula's
coefficients are set from texts in its own language; Ateşman (1997) likewise recomputed
the coefficients of the Flesch formula from Turkish texts when applying it to Turkish. So
Flesch is not given for Turkish text, nor Ateşman for English text.

The `phonological` group has 14 features in Turkish and 12 in English.

`lang` accepts only `"tr"` and `"en"`. Anything else raises `ValueError`.

## Ask for specific groups

If you do not need all 214 features, pick groups; the output then carries
only those groups' keys:

```python
oz = tlf.analyze(text, lang="tr", groups=["readability", "lexical"])
len(oz)     # 48
```

Picking groups saves little time. Most of it goes to the spaCy and Zeyrek
preprocessing, which runs once whatever you ask for; groups only shorten the
calculation after it. On a 1000-word text all groups take about 1.1 seconds,
`readability` alone about 0.95 seconds.

The groups, with their Turkish feature counts:

| Group | Name | Contents | Features |
|---|---|---|---|
| `lexical` | Lexical richness & frequency | lexical diversity, word frequency and lexical density | 35 |
| `chars` | Character frequencies | the share of each letter | 29 |
| `morphological_zeyrek` | Morphological features (Zeyrek) | ratios from morpheme analysis | 23 |
| `punctuation` | Punctuation & orthography | punctuation, capitals, digits | 20 |
| `morphological` | Morphological features (spaCy) | case, tense, person, aspect, voice | 19 |
| `frequency_structure` | Frequency structure | frequency-structure measures based on the h-point and Zipf's law | 17 |
| `pos` | Parts of speech | part-of-speech shares and variation | 17 |
| `syntactic` | Syntactic features | dependency distance, hierarchical distance, part of speech of the sentence-final word | 16 |
| `phonological` | Phonological features | vowel distribution, vowel harmony, syllable count | 14 |
| `readability` | Readability | readability formulas and their components | 13 |
| `sentence` | Sentence features | sentence count, length and question share | 8 |
| `paragraph` | Paragraph structure | paragraph count and length | 3 |

`chars` counts letters only: one key per letter of the Turkish alphabet (26 in English;
`q`, `w`, `x` only there). `morphological_zeyrek` is produced for Turkish only.

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
A phrase may also be a single item.

### What an item matches

Each item in a phrase is read in this order:

| Item | Matches | In the key |
|---|---|---|
| UD part-of-speech tag (`NOUN`, `VERB`, `ADJ`…) | Any word carrying that tag | uppercase (`NOUN`) |
| All uppercase, at least 2 letters (`HOUSE`, `GO`, `EV`) | Any word whose lemma it is | uppercase (`HOUSE`) |
| Anything else (`house`, `izmir`, `I`) | The lowercased written form | lowercase (`house`) |

**Written form.** A lowercase item matches the written form: `old houses` does not
match `old house`. It also catches capitalised spellings (`izmir` finds "Izmir" and
"IZMIR"), but not inflected forms.

**Lemma.** To catch inflected forms too, write the item in all capitals; it matches
every word carrying that lemma:

```python
tlf.ngram_matches("He went home. She goes home.", ["GO", "home"], lang="en")
# {'went home': 1, 'goes home': 1}
```

**Tag.** `["ADJ", "NOUN"]` means an adjective followed directly by a noun.

Details:

- Words, lemmas and tags can be mixed in one phrase: `["old", "HOUSE"]`, `["ADJ", "HOUSE"]`.
- The lemma comes from the same place as in the rest of the library: spaCy for English,
  Zeyrek's first analysis for Turkish.
- Verbs are written without an infinitive marker: `GO`, Turkish `GİT`.
- In Turkish, an uppercase item is lowercased by the Turkish rule: `İZMİR` → izmir,
  `IRMAK` → ırmak; dotless `IZMIR` becomes ızmır.
- A one-letter item is a word, never a lemma search (`I`, `O`).
- A lemma that is also a tag name is always read as the tag: the English lemma "part"
  cannot be searched as `PART`.
- A match never crosses a sentence boundary: `down. A` is not adjacent.

Other notes:
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
    against a table produced with another.

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
