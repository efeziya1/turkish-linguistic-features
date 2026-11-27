# Analyse a single text

## The short version

```python
import turkish_linguistic_features as tlf

oz = tlf.analyze(text, lang="en")
```

`analyze` returns a flat Python dictionary (`dict`): the keys are feature names, the
values are numbers.

## The language changes the feature set

```python
tr = tlf.analyze(tr_text, lang="tr")
en = tlf.analyze(en_text, lang="en")

len(tr)   # 217
len(en)   # 187
```

The 30 extra Turkish features come from:

- **+23** Akana suffix analysis: the `morphological_akana` group (suffix
  chain, case markers, mood and tense; every key starts with `akana_`) —
  Turkish only.
- **+2** vowel harmony (`harmony_fronting_ratio`, `harmony_rounding_ratio`) —
  a property of Turkish; not produced for English.
- **+5** readability: 12 Turkish-only features (the Ateşman, Çetinkaya-Uzun and
  Bezirci-Yılmaz formulas; Kalyoncu's four formulas and five
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

If you do not need all 217 features, pick groups; the output then carries
only those groups' keys:

```python
oz = tlf.analyze(text, lang="tr", groups=["readability", "lexical"])
len(oz)     # 48
```

Picking groups hardly changes the speed: most of the time goes to the spaCy and Akana
preprocessing, which runs once in any case (on a 1000-word text all groups take about 0.6
seconds, `readability` alone about 0.5 seconds). Picking groups is for narrowing the output
to the features you need.

The groups, with their Turkish feature counts:

| Group | Name | Contents | Features |
|---|---|---|---|
| `lexical` | Lexical richness & frequency | lexical diversity, word frequency and lexical density | 35 |
| `chars` | Character frequencies | the share of each letter | 32 |
| `morphological_akana` | Morphological features (Akana) | ratios from morpheme analysis | 23 |
| `punctuation` | Punctuation & orthography | punctuation, capitals, digits | 20 |
| `morphological` | Morphological features (spaCy) | case, tense, person, aspect, voice | 19 |
| `frequency_structure` | Frequency structure | frequency-structure measures based on the h-point and Zipf's law | 17 |
| `pos` | Parts of speech | part-of-speech shares and variation | 17 |
| `syntactic` | Syntactic features | dependency distance, hierarchical distance, part of speech of the sentence-final word | 16 |
| `phonological` | Phonological features | vowel distribution, vowel harmony, syllable count | 14 |
| `readability` | Readability | readability formulas and their components | 13 |
| `sentence` | Sentence features | sentence count, length and question share | 8 |
| `paragraph` | Paragraph structure | paragraph count and length | 3 |

`chars` counts letters only: one key for each of the same 32 letters in both languages (the
Turkish and English alphabets together). A `w` in a Turkish text or an `ş` in an English text
is counted too. `morphological_akana` is produced for Turkish only.

`describe_feature(key)["group"]` gives the group a feature belongs to.

## Count your own phrases

If you are after a pattern the built-in features do not cover, pass it as a word sequence
(*n-gram*) in `custom_ngrams`:

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
| Part-of-speech tag (`NOUN`, `VERB`, `ADJ`…; [list](#part-of-speech-tags)) | Any word carrying that tag | uppercase (`NOUN`) |
| All uppercase, at least 2 letters (`HOUSE`, `GO`, `EV`) | Any word whose lemma it is | uppercase (`HOUSE`) |
| Anything else (`house`, `izmir`, `I`) | The lowercased written form | lowercase (`house`) |

**Written form.** A lowercase item matches the written form: `old houses` does not
match `old house`. It also catches capitalised spellings (`izmir` finds "Izmir" and
"IZMIR"), but not inflected forms.

**Lemma.** To catch inflected forms too, write the item in all capitals; it then
matches every word carrying that lemma:

```python
tlf.ngram_matches("He went home. She goes home.", ["GO", "home"], lang="en")
# {'went home': 1, 'goes home': 1}
```

**Tag.** `["ADJ", "NOUN"]` means an adjective followed directly by a noun.

Details:

- Words, lemmas and tags can be used together in one phrase: `["old", "HOUSE"]`, `["ADJ", "HOUSE"]`.
- The lemma comes from the same place as in the rest of the library: spaCy for English,
  the analysis Akana chooses for Turkish.
- Verbs are written without an infinitive marker: `GO`, Turkish `GİT`.
- In Turkish, an uppercase item is lowercased by the Turkish rule: `İZMİR` → izmir,
  `IRMAK` → ırmak; dotless `IZMIR` becomes ızmır.
- A one-letter item is searched by its written form even in capitals: the `I` in
  `["I", "VERB"]` is the word "I", not a lemma.
- An all-capitals item that is also a tag name is searched as the tag: `PART` is the particle
  tag, not the English lemma *part*. To search for such a word, use its lowercase written form
  (`part`).
- A match never crosses a sentence boundary: `down. A` is not adjacent.

Other notes:
- The value is a plain count. To compare texts of different lengths, divide by
  `word_count` (`oz["ngram_ADJ_NOUN_count"] / oz["word_count"]`) or bring the texts to the
  same size first (`segment_size`).

The count answers "how often". To see **what** the phrase matched:

```python
tlf.ngram_matches(text, ["ADJ", "NOUN"], lang="en")
```

```text
{'old house': 2, 'new building': 1, 'big garden': 1}
```

The most frequent match comes first, and the counts add up to
`ngram_ADJ_NOUN_count`. Sentence and position are not returned. Working example:
[`examples/10_kelime_oruntuleri.py`](https://github.com/efeziya1/turkish-linguistic-features/blob/main/examples/10_kelime_oruntuleri.py).

### Part-of-speech tags

The tags come from the Universal Dependencies scheme and are the same in both languages:

| Tag | Part of speech | Example |
|---|---|---|
| `NOUN` | noun | `house`, `books` |
| `PROPN` | proper noun | `Anna`, `London` |
| `VERB` | verb | `bought`, `leaving` |
| `ADJ` | adjective | `old`, `big` |
| `ADV` | adverb | `quickly` |
| `PRON` | pronoun | `she`, `them` |
| `DET` | determiner | `the`, `every` |
| `NUM` | numeral | `two`, `three` |
| `ADP` | adposition | `in`, `at` |
| `AUX` | auxiliary | `will`, `is` |
| `CCONJ` | coordinating conjunction | `and`, `but` |
| `SCONJ` | subordinating conjunction | `because`, `if` |
| `PART` | particle | `not`, `to` |
| `INTJ` | interjection | `oh`, `wow` |
| `X` | other | foreign word, typo |

Punctuation (`PUNCT`) and symbols (`SYM`) are not words, so they never match in a phrase.
The tag comes from the spaCy model; the same word can get different tags in different
sentences.

## See the units that are counted

If you want to check which words a number came from, or make your own counts, you can see
the counted units directly. `text_units` gives the words the features count
([the word definition](../explanation/concepts.md#word)), the lemmas, POS tags, syllable
counts and sentences, as separate lists:

```python
u = tlf.text_units("Ali read the books. He will go home.", lang="en")
u["words"]      # ['Ali', 'read', 'the', 'books', 'He', 'will', 'go', 'home']
u["lemmas"]     # ['ali', 'read', 'the', 'book', 'he', 'will', 'go', 'home']
u["pos"]        # ['PROPN', 'VERB', 'DET', 'NOUN', 'PRON', 'AUX', 'VERB', 'ADV']
u["syllables"]  # [2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
u["sentences"]  # [['Ali', 'read', 'the', 'books'], ['He', 'will', 'go', 'home']]
```

The lemma, tag and syllable lists line up with the words: `u["lemmas"][3]` is the lemma of
`u["words"][3]`. The number of words equals `word_count`, the number of sentences
`sent_count` and the syllables add up to `syllable_count`, so you can see which units a
number came from. A word whose reading cannot be taken from the text (an e-mail or web
address) has `nan` syllables and stays out of the total.

`lemma_count` in `analyze` only gives how many *different* lemmas there are. To see how
often each lemma occurs, that is a frequency list, you can use Python's own `Counter` (it
does not come with the tool; it is part of Python):

```python
from collections import Counter
Counter(u["lemmas"]).most_common(10)   # the 10 most frequent lemmas and their counts
```

## Progress output

For long texts:

```python
oz = tlf.analyze(text, lang="en", show_progress=True)
```

## Silence the warnings

If the optional `wordfreq` package is missing, the library gives a
`MissingDependencyWarning` and leaves the two features that depend on it
(`wordfreq_*`) as `nan`. If you accept that knowingly, you can turn the warning off:

```python
oz = tlf.analyze(text, lang="en", warn=False)
```

`warn=False` **does not change the computation** — it only silences the
warning. The feature is still `nan`.

## Use a different spaCy model

```python
oz = tlf.analyze(text, lang="en", model="en_core_web_trf")
```

The defaults are `tr_core_news_md` and `en_core_web_sm`. If the model is not installed,
you get `ModelNotFoundError`; the message contains the install command.

!!! warning "Changing the model changes the numbers"

    Tokenisation, part-of-speech tags, morphological tags and the
    dependency parse all come from the model. Do not compare a table produced with one
    model against a table produced with another in the same study.

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
