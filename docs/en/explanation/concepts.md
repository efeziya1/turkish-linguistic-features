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
the model's tokens:

- **Word** — a whitespace-separated piece with edge punctuation stripped,
  containing a letter or digit. `e-posta`, `%50` and numbers are one word
  each. Every feature except the dependency group counts this word.
- **Sentence** — `. ? ! …` end a sentence; `:` only when a new sentence
  follows. Abbreviations such as `Dr.` do not.
- **A word's tags** — the part of speech, morphological tags and lemma come
  from the first token inside the word. Turkish lemmas are Zeyrek's dictionary
  entry, English lemmas spaCy's.

`describe_feature(key)["definitions"]` names the rule a feature uses.

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
