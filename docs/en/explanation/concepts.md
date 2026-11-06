# Concepts

## Feature

A **feature** is a single number extracted from a text. `ttr`,
`word_len_mean`, `atesman`: each is one feature. Names are `snake_case`.

By the kind of source they rest on, the 214 Turkish features fall into five types:

| Type | Count | What | Example |
|---|---:|---|---|
| **Literature measure** | 133 | A measure proposed in the literature; it has a citation | `mattr`, `mtld`, `atesman` |
| **Tag ratio** | 66 | The share of a tag that spaCy or Zeyrek gives to words; the citation points at the scheme that defines the tag, not at a measure | `pos_noun_ratio` (Universal Dependencies), `zeyrek_case_loc_ratio` (Zeyrek) |
| **Plain definition** | 11 | Not based on a named measure in the literature; no citation | `question_sent_ratio`: the share of sentences ending in a question mark |
| **Tool-specific** | 2 | The formula comes from the literature; what it is applied to is this tool's decision | `sent_len_entropy`: Shannon entropy applied to sentence lengths |
| **Calibrated** | 2 | The threshold comes from this tool's corpus measurement | `short_sent_ratio`, `long_sent_ratio` |

Of 214 keys, 203 have a citation and 11 do not. The type also decides whether a feature
can be checked against a number its source published
([The verification system](verification.md)).

The tool does not give only the result of a readability formula; it also gives the measures
that go into the formula, such as mean sentence length and syllables per word, as separate
features. If you want to build a new formula for Turkish, you can choose and test candidate
variables from these measures and the tool's other features.

## Key names

A name is built so that it says what the feature measures:

| Name | Meaning | Example |
|---|---|---|
| `…_ratio` | A share between 0 and 1 | `hapax_ratio`, `pos_noun_ratio` |
| `…_mean`, `…_median` | Mean, median | `sent_len_mean`, `sent_len_median` |
| `…_count` | A count | `word_count`, `sent_count`, `lemma_count` |
| The name in the literature | An established measure; no `_ratio` | `ttr`, `mattr`, `yule_k`, `posddev` |

The morphological features come from two analysers. Those from spaCy's Universal
Dependencies tags have no prefix (`case_loc_ratio`); those from Zeyrek start with `zeyrek_`
(`zeyrek_case_loc_ratio`). The two do not give the same number:
`case_loc_ratio` is the locative's share among words that carry a case tag,
`zeyrek_case_loc_ratio` its share among all analysed words. Zeyrek also draws distinctions
the universal tags do not: the -DI past and the -mIş past are separate
(`zeyrek_tense_past_def_ratio`, `zeyrek_tense_past_nar_ratio`); in spaCy both are
`tense_past_ratio`.

The ten `punct_…_ratio` keys (`punct_comma_ratio`, `punct_dash_ratio` …) are each
mark type's share of all punctuation marks, so together they add up to 1. How much
punctuation a text has is `punct_char_ratio` (punctuation marks / characters).

## Group

Features are organised into 12 groups (13 with the `ngram_*` keys created when
you pass `custom_ngrams`). A group serves both to organise and to select: you can compute
only the groups you need.

```python
oz = tlf.analyze(text, lang="en", groups=["readability", "lexical"])
```

The groups, their contents and their sizes are listed in
[Analyse a single text](../how-to/single-text.md).

## Dynamic keys

Some keys are not written out one by one; they are generated from a
pattern:

- `char_*`: the letter-frequency vector, one key per letter of the alphabet
  (Turkish 29: `char_a_ratio`, `char_ç_ratio` … `char_z_ratio`; English 26)
- `ngram_*`: counters for the word sequences (n-grams) you pass with `custom_ngrams`
  ([how](../how-to/single-text.md#count-your-own-phrases))

If you call `describe_feature("char_a_ratio")`, the `formula` and `requires`
fields are the **group-level** statement, not something specific to that
letter.

## Scale

Every feature has a scale:

| Scale | Meaning | Example |
|---|---|---|
| `ratio_0_1` | A share between 0 and 1 | `ttr`, `mattr` |
| `score` | A formula score with no fixed range | `atesman`, `yule_k`, `mtld` |
| `length` | A mean length in characters, words or sentences | `word_len_mean`, `sent_len_mean` |
| `nats` | Entropy in nats (natural logarithm; every logarithm in the tool is ln) | `entropy`, `punct_entropy` |
| `count` | A count | `lemma_count` |

## Word and sentence

A feature's value depends on how words, sentences and syllables are counted. Features count
words and sentences with the tool's own rules, not with the model's tokens. These are the
**default word** and the **default sentence**; other pages that use these names point here.

### Word

The text is split at whitespace. Punctuation at the edges of each piece is removed
(`. , ; : ! ? …`, quotes, brackets, dashes, `/`, `*`). What is left is a **word if it
contains at least one letter or digit**; otherwise it is not counted.

| Text | Words |
|---|---|
| `He read it.` | `He`, `read`, `it`: the full stop is not part of the word |
| `e-mail`, `it's`, `50%` | one word each: marks inside a word stay |
| `in 1999` | `in`, `1999`: a number is a word |
| `This — is a test ...` | `This`, `is`, `a`, `test`: `—` and `...` on their own are not words |
| `3. kat` · `Sonuç 3.` | Turkish only: `3.` is one word (an ordinal) when a word or a comma follows it; at the end of a sentence it is `3` |

The ordinal rule is Turkish only because Turkish writes ordinals as a digit followed by a dot;
English writes `3rd`, so it needs no such rule.

Part-of-speech based analyses remove punctuation and symbols by looking at their tags; this
tool does the same job by stripping the marks at the edges of the word. Every feature except
the `syntactic` group counts this word.

### Sentence

A sentence ends at:

- **`.` `?` `!` `…`**: always. `...` and `…` are the same mark. Marks in a row
  such as `?!` end one sentence.
- **`:`**: only when what follows starts like a new sentence: a capital letter, a
  quote, a dash or an opening bracket. A colon followed by a lowercase word or a number
  (a list, an explanation, `10:30`) does not end a sentence.
- **the end of the text**, even without a mark.

A full stop after an abbreviation does **not** end a sentence: `Dr.` is one unit. In
Turkish, the dot after a listed abbreviation such as `bkz.` ends a sentence only when the
next word starts with a capital.

| Text | Sentences |
|---|---|
| `He came. He left!` | 2 |
| `What?! I don't know.` | 2 |
| `She said: We leave tomorrow.` | 2: a capital after `:` |
| `He bought three things: bread, milk and cheese.` | 1: lowercase after `:` |
| `The meeting began at 10:30.` | 1 |
| `Dr. Smith arrived.` | 1 |
| `He came and went` | 1: no mark; the text ends |

The colon has this condition because a colon is not always a sentence boundary. In Turkish
newspaper columns (4,321 articles), the token after 93.9% of colons starts with a capital, a
quote, a dash or an opening bracket; in English columns (1,485 articles) the share is 62.4%.
The condition keeps a colon followed by a lowercase list or explanation from ending a
sentence. The rule is the same in both languages.

A sentence's length is the number of words in it. The sentence-length features and
`sent_count` do not count a sentence with no letter in it, so that it does not pull the
mean down: `This is one. 1999. Done.` has 2 sentences, and all 5 of its words, `1999`
included, are counted.

Two kinds of feature do not use this rule:

- some **readability formulas** follow the counting their own source prescribes
  (table below);
- the **syntactic features** (`syntactic`) use spaCy's tokens and the sentences its
  parser finds.

### Counting in the readability formulas

For some readability formulas, the source itself says how words or sentences are counted.
In these formulas the tool follows the source's rule instead of the general one, so the
formula is computed the way its source computed it.

| Formula | Word | Sentence | Source |
|---|---|---|---|
| Çetinkaya-Uzun | Symbols standing alone (`%`, `$`, `+`) are words too | A colon always, and brackets, also end a sentence | Çetinkaya (2010) p.93 |
| Flesch, Flesch-Kincaid | Symbols standing alone are words too | A semicolon also ends a sentence | Kincaid et al. (1975) p.38 |
| ARI | Symbols standing alone are words too | General rule | Kincaid et al. (1975) p.33 |
| Kalyoncu's four formulas and their components | A number counts as the words of its reading: `1968`, "bin dokuz yüz altmış sekiz", is 5 words | General rule | Kalyoncu (2025) p.xiii |

The formulas not in the table (Ateşman, Bezirci-Yılmaz, SMOG, Coleman-Liau, LIX) use the
general rule. Syllables are counted by pronunciation in every formula: `1918`, "bin dokuz
yüz on sekiz", is 7 syllables; `%50` and `TBMM` are 4 each. Details:
[Limitations](limitations.md).

### A word's tags

spaCy splits text by its own rules, so one word can span several tokens: `Ankara-İstanbul`
becomes the tokens `Ankara`, `-` and `İstanbul`. The word is then counted once; its part of
speech, morphological tags and lemma come from the first token inside it that is not
punctuation. A double quote (`"` `“` `”` `«` `»`) is always punctuation here, whatever tag the
model gave it. Turkish lemmas are Zeyrek's dictionary entry, English lemmas spaCy's.

### Counting unit of the diversity measures

In the lexical diversity measures, a type is the word's lowercased surface form, so a word
capitalised at the start of a sentence is not a separate type. Turkish is lowercased by the
Turkish rule (I → ı, İ → i); software's default conversion turns `IŞIK` into `işik`, so
this is handled separately.

Because the type rests on the surface form, inflected forms are separate types: `book` and
`books` are two types. This is the tool's design decision. The exceptions are `*_variation`
and `lemma_count`. Where the source counts in another unit (`brunet_w`, `herdan_c`,
`yule_k`), the citation says so.

### Content word

A content word is a word tagged `NOUN`, `PROPN`, `VERB`, `ADJ` or `ADV`: a noun, proper
noun, verb, adjective or adverb. Auxiliaries (`AUX`) do not count as verbs. This definition
is used by `lexical_density`, the part-of-speech variation measures, thematic concentration
and the frequency measures.

The definition is Lu's (2012), with one difference: Lu (2012, p.192) counts only the adverbs
derived from adjectives; the tool counts all adverbs, because the part-of-speech tagger does
not tell adverb types apart and that distinction would need a word list or a morpheme-based
rule. QUITA leaves the choice of content words to the researcher (Kubát et al. 2014,
pp.50–51).

`describe_feature(key)["definitions"]` names the rule each feature uses.

## The pipeline

When you call `analyze`, the text goes through four stages:

```text
raw text
   ↓  1. spaCy (tr_core_news_md / en_core_web_sm)
tokens · POS tags · morphological tags · dependency tree · English lemmas
   ↓  2. Zeyrek (Turkish only)
morpheme analysis · Turkish lemmas
   ↓  3. the tool's own rules
word and sentence boundaries; each word takes its tags from its own token
   ↓  4. feature calculators
214 numbers (181 in English)
```

Zeyrek was chosen so that the tool runs entirely inside Python, without installing another
environment such as Java.

**The spaCy model and Zeyrek are part of the result.** If either changes, the features that
depend on it change too. Of the 214 Turkish features, 105 depend on at least one of the two
analysers; the other 109 are computed with the tool's own rules alone. To reproduce a
result, report the versions of the spaCy model and Zeyrek along with the tool's version.
Versions the tool was tested with: Python 3.12, spaCy 3.8.16, `tr_core_news_md` 1.0 (model
version 3.4.2), `en_core_web_sm` 3.8.0, Zeyrek 0.1.3.

## `FeatureParams`

Window sizes, thresholds and sample counts live here. Details:
[Change the thresholds](../how-to/parameters.md).

The sentence thresholds (`short_sent_threshold`, `long_sent_threshold`) are
**calibrated per language** (TR 4/17, EN 8/32).

## The registry

The registry holds, in one place, each feature's name, what it measures, its formula,
scale, parameters, the minimum data it needs, its citation and the tool's definitions of
the terms in the formula. `describe_feature`, the [reference section](../../reference/index.md)
and the [verification report](../../verification-report.md) read from it, so the
three always agree.

The registry is kept **in English**, so that no translation layer sits between the
definitions and formulas and the sources, most of which are in English.
