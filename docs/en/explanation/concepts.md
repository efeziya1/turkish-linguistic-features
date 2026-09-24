# Concepts

## Feature

A **feature** is a single number extracted from a text. `ttr`,
`avg_word_length`, `atesman` — each is one feature. Names are `snake_case`
and they do not change; version upgrades never rename a key.

A feature is one of three things:

1. **A named measure from the literature** — `mattr`, `yule_k`,
   `flesch_reading_ease`. These have citations.
2. **A category of an external tag scheme** — `pos_noun` (UD),
   `case_loc_ratio` (Zeyrek). The citation points at the scheme, not at the
   measure.
3. **A plain definition** — `punc_,_ratio` ("commas / words"). No citation,
   because there is nothing to attribute.

Of 208 keys, 141 have a citation and 67 do not.

## Group

Features are organised into 13 groups. A group is both an organising device
and a selection device:

```python
oz = tlf.analyze(text, lang="en", groups=["readability", "lexical"])
```

The groups and their sizes are listed in
[Analyse a single text](../how-to/single-text.md).

## Dynamic keys

Some keys are not written out one by one; they are generated from a
pattern:

- `char_a` … `char_z` — the letter-frequency vector
- `punc_,_ratio`, `punc_._ratio` … — punctuation ratios
- `ng_*` — n-gram counters created when you pass `custom_ngrams`

If you call `describe_feature("char_a")`, the `formula` and `requires`
fields are the **group-level** statement, not something specific to that
letter.

## Scale

Every feature has a scale, and it matters when you plot:

| Scale | Meaning | Example |
|---|---|---|
| `ratio_0_1` | A ratio between 0 and 1 | `ttr`, `mattr` |
| `score` | A formula score with no bound | `atesman`, `ari` |
| `count` | A count | `n_lemma_count` |
| `chars` / `words` | A mean whose unit is characters or words | `avg_word_length` |

Two `ratio_0_1` features can share an axis; putting a `score` next to them
misleads.

## The pipeline

When you call `analyze`, this happens in order:

```text
raw text
   ↓  spaCy (tr_core_news_md / en_core_web_sm)
surface tokens · lemmas · POS tags · dependency tree · sentence boundaries
   ↓  Zeyrek (Turkish only)
suffix analysis
   ↓  feature extractors
208 numbers
```

Two consequences:

1. **The spaCy model is part of the result.** Change the model and
   sentence splitting, POS tags and dependency features change with it.
   State which model you used in your methods section.
2. **Preprocessing runs once.** All 208 features draw on the same analysis,
   so asking for fewer `groups` does not speed up preprocessing — it only
   shortens the extraction step.

## `FeatureParams`

Window sizes, thresholds and sample counts live here. Details:
[Change the thresholds](../how-to/parameters.md).

The critical point: when you leave `params=None`, the library uses
**language-specific calibrated** values (TR 4/18, EN 7/39). The moment you
pass a `FeatureParams()`, that calibration is switched off.

## The registry

Feature names, descriptions, formulas, requirements and citations all live
in one place: `features/_registry_texts.py`. `describe_feature` reads from
it, the [reference section](../../reference/index.md) is generated from it,
and the [verification report](../../verification-report.md) takes its
coverage list from it.

This is deliberate: add a feature without registering it and the tests
fail. No feature can escape the documentation.
