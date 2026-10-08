# Concepts

## Feature

A **feature** is a single number extracted from a text. `ttr`,
`word_len_mean`, `atesman` — each is one feature. Names are `snake_case`.
Until version 1.0 a key may be renamed; renamed keys are announced in the
release notes.

A feature is one of three things:

1. **A named measure from the literature** — `mattr`, `yule_k`,
   `flesch_reading_ease`. These have citations.
2. **A category of an external tag scheme** — `pos_noun_ratio` (UD),
   `zeyrek_case_loc_ratio` (Zeyrek). The citation points at the scheme, not at the
   measure.
3. **A plain definition** — `punct_dash_ratio` ("dashes / all punctuation marks"). No citation,
   because it is not a named measure that could be attributed.

Of 208 keys, 197 have a citation and 11 do not.

## Key names

A name is built so that it says what the feature measures:

| Name | Meaning | Example |
|---|---|---|
| `…_ratio` | A share between 0 and 1 | `hapax_ratio`, `pos_noun_ratio` |
| `…_mean`, `…_median` | Mean, median | `sent_len_mean`, `sent_len_median` |
| `…_count` | A count | `word_count`, `sent_count`, `lemma_count` |
| The name in the literature | An established measure; no `_ratio` | `ttr`, `mattr`, `yule_k`, `posddev` |

The morphological features come from two analysers. Those from spaCy's UD
tags have no prefix (`case_loc_ratio`); those from Zeyrek start with `zeyrek_`
(`zeyrek_case_loc_ratio`). The two do not give the same number:
`case_loc_ratio` is the locative's share among words that carry a case tag,
`zeyrek_case_loc_ratio` its share among all analysed words. Zeyrek also tells
the -DI past from the -mIş past (`zeyrek_tense_past_def_ratio`,
`zeyrek_tense_past_nar_ratio`); in spaCy both are `tense_past_ratio`.

## Group

Features are organised into 13 groups (14 with the `ngram_*` keys created when
you pass `custom_ngrams`). A group is both an organising device
and a selection device:

```python
oz = tlf.analyze(text, lang="en", groups=["readability", "lexical"])
```

The groups and their sizes are listed in
[Analyse a single text](../how-to/single-text.md).

## Dynamic keys

Some keys are not written out one by one; they are generated from a
pattern:

- `char_*` — the letter-frequency vector, one key per letter of the alphabet
  (Turkish 29: `char_a_ratio`, `char_ç_ratio` … `char_z_ratio`; English 26)
- `ngram_*` — n-gram counters created when you pass `custom_ngrams`
  ([how](../how-to/single-text.md#count-your-own-phrases))

If you call `describe_feature("char_a_ratio")`, the `formula` and `requires`
fields are the **group-level** statement, not something specific to that
letter.

## Scale

Every feature has a scale, and it matters when you plot:

| Scale | Meaning | Example |
|---|---|---|
| `ratio_0_1` | A share between 0 and 1 | `ttr`, `mattr` |
| `score` | A formula score with no fixed range | `atesman`, `yule_k`, `mtld` |
| `length` | A mean length in characters, words or sentences | `word_len_mean`, `sent_len_mean` |
| `nats` | Entropy in nats (natural logarithm; every logarithm in the library is ln) | `entropy`, `punct_entropy` |
| `count` | A count | `lemma_count` |

Two `ratio_0_1` features can share an axis; putting a `score` next to them
misleads.

## Word and sentence

Features count words and sentences with the library's own rules, not with
the model's tokens. These are the **default word** and the **default sentence**;
other pages that use these names point here.

### Word

The text is split at whitespace. Punctuation at the edges of each piece is removed
(`. , ; : ! ? …`, quotes, brackets, dashes, `/`, `*`). What is left is a **word if it
contains at least one letter or digit**; otherwise it is not counted.

| Text | Words |
|---|---|
| `He read it.` | `He`, `read`, `it` — the full stop is not part of the word |
| `e-mail`, `it's`, `50%` | one word each — marks inside a word stay |
| `in 1999` | `in`, `1999` — a number is a word |
| `This — is a test ...` | `This`, `is`, `a`, `test` — `—` and `...` on their own are not words |
| `3. kat` · `Sonuç 3.` | Turkish only: `3.` is one word (an ordinal) when a word or a comma follows it; at the end of a sentence it is `3` |

Every feature except the dependency group counts this word.

### Sentence

A sentence ends at:

- **`.` `?` `!` `…`** — always. `...` and `…` are the same mark. Marks in a row
  (`?!`, `."`) end one sentence, not two.
- **`:`** — only when what follows starts like a new sentence: a capital letter, a
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
| `She said: We leave tomorrow.` | 2 — a capital after `:` |
| `He bought three things: bread, milk and cheese.` | 1 — lowercase after `:` |
| `The meeting began at 10:30.` | 1 |
| `Dr. Smith arrived.` | 1 |
| `He came and went` | 1 — no mark; the text ends |

A sentence's length is the number of words in it. The sentence-length features and
`sent_count` do not count a sentence with no letter in it, so that it does not pull the
mean down: `This is one. 1999. Done.` has 2 sentences, and all 5 of its words, `1999`
included, are counted.

Two kinds of feature do not use this rule:

- some **readability formulas** follow the counting their own source prescribes:
  Çetinkaya-Uzun also ends a sentence at `:` and at brackets, the Flesch formulas at `;`;
- the **dependency group** (`syntactic_dep`) uses spaCy's tokens and its parser's
  sentences.

### A word's tags

The part of speech, morphological tags and lemma come from the first token inside the
word. Turkish lemmas are Zeyrek's dictionary entry, English lemmas spaCy's.

`describe_feature(key)["definitions"]` names the rule each feature uses.

## The pipeline

When you call `analyze`, this happens in order:

```text
raw text
   ↓  spaCy (tr_core_news_md / en_core_web_sm)
tokens · POS tags · morphological tags · dependency tree · English lemmas
   ↓  Zeyrek (Turkish only)
suffix analysis · Turkish lemmas
   ↓  the library's own rules
word and sentence boundaries; each word takes its tags from its own token
   ↓  feature extractors
208 numbers
```

Two consequences:

1. **The spaCy model is part of the result.** Change the model and the
   tokens, POS, morphological and dependency features change with it.
   State which model you used in your methods section.
2. **Preprocessing runs once.** All 208 features draw on the same analysis,
   so asking for fewer `groups` does not speed up preprocessing — it only
   shortens the extraction step.

## `FeatureParams`

Window sizes, thresholds and sample counts live here. Details:
[Change the thresholds](../how-to/parameters.md).

The sentence thresholds (`short_sent_threshold`, `long_sent_threshold`) are
**calibrated per language** (TR 4/17, EN 8/32) and resolved field by field:
a field you set wins, a field you leave out stays calibrated. So
`FeatureParams(mattr_window=100)` does not change the sentence thresholds.

## The registry

Feature names, descriptions, formulas, requirements and citations all live
in one place. `describe_feature`, the [reference section](../../reference/index.md)
and the [verification report](../../verification-report.md) read from it, so the
three always agree.
