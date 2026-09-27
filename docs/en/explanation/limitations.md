# Limitations

This page says where the library is weak. Read it while writing your
methods section.

## 1. The sentence thresholds were calibrated on fiction only

The `short_sent_ratio` and `long_sent_ratio` thresholds (TR 4/18, EN 7/39)
were derived from the 15th and 85th percentiles of the sentence-length
distribution in novel corpora:

| Language | Authors | Sentences |
|---|---|---|
| Turkish | 15 | 1,089,841 |
| English | 10 | 341,892 |

Both sets are the **same genre**: novels/fiction. There is **no guarantee**
they generalise to technical writing, transcripts, poetry or children's
books. If you work in another genre, consider deriving the thresholds from
your own corpus — [the method is here](../../threshold-calibration.md).

## 2. Some features are this library's own derivations

A few features are not named measures from the literature but definitions
this library made. Their citations say so plainly:

- `entropy_std` — the **standard deviation of Shannon entropy across
  segments**. The entropy is Shannon's; the standard deviation is ours.
- `punct_entropy`, `sent_len_entropy` — Shannon's formula applied to the
  distribution of punctuation types and of sentence lengths. The formula is
  Shannon's; the decision to apply it there is ours.
- `polysyllabic_word_ratio` — the ratio form of SMOG's input. Not a measure
  McLaughlin himself defines.

There is nothing wrong with using them. The one requirement is getting the
attribution right: cite the source of the formula, but do not attribute the
measure itself to that source. In your methods section:

- ✗ "the Shannon (1948) `entropy_std` measure"
- ✓ "the standard deviation of Shannon (1948) entropy across segments
  (as defined by turkish-linguistic-features)"

The reason is simple: Shannon defined the entropy, not its standard deviation
across segments. The first wording implies a measure the reader could look up
in the source and find.

## 3. Eleven citations are secondary

**11 of 145** citations carry `as cited in` — the primary source could not
be obtained and the formula was taken from the citing work. For example:

```text
Herdan (1960/1964), as cited in Tweedie & Baayen (1998) p.327, eq. (5)
```

Affected measures include `herdan_c`, `brunet_w`, `dugast_u`, `yule_k`,
`simpson_d`, `heaps_beta` and `lix`. The formulas were verified, but not
against the **primary source's own wording**.

Carry the "as cited in" through into your own methods section. Do not
present it as though you read the primary.

## 4. The spaCy model is part of the result

Sentence splitting, POS tags and dependency features come from the model.
Change the model and the numbers change.

Verified combination: spaCy 3.8.16, `en_core_web_sm` 3.8.0,
`tr_core_news_md` 1.0.

Known oddities of the Turkish model:

- The wheel disagrees with itself: the filename says `1.0`, the internal
  metadata says `3.4.2`.
- Loading it prints a `W094` warning. The model's own `meta.json` is
  loosely written; this is harmless.

Neither is a bug, and neither has anything to fix.

## 5. Turkish morphology depends on Zeyrek

The 24 features in the `morphological_zeyrek` group come from Zeyrek, a
Python port of Zemberek's morphotactics. A word Zeyrek cannot analyse drops
out of those features.

Zeyrek is an **analyser, not a disambiguator**: it can return several
analyses for the same surface form and does not pick the right one from
context.

## 6. Sensitivity to text length

Most lexical richness measures change with length. `ttr` is the extreme
case: it always falls as a text grows.

If you compare texts of different lengths, either segment them to equal
size ([how](../how-to/segmenting.md)) or use measures designed to be
length-independent: `mattr`, `mtld`, `vocd_d`. Those also need at least
100 words.

## 7. Paragraph features depend on how the input is formatted

The five `para_*` features find paragraph boundaries from **blank lines**. A
single line break does not count as one — otherwise every line of a
hard-wrapped text would be a paragraph.

The consequence: if your text has no blank lines, the whole text counts as one
paragraph. `para_len_mean` becomes the word count of the entire text and both
CVs return NaN. The library cannot fix this — a boundary that was deleted
cannot be recovered.

This is **common** in text extracted from PDF and EPUB. Measured:
in one Turkish novel collection, **120 of 163** files contain no blank line at
all; one file is a single line of 191,806 characters and 7,347 sentences.

If a text longer than 1000 words yields no paragraph boundary at all, a
`ParagraphStructureWarning` is raised. If you see it you have two options:
re-extract the source text with paragraphs separated by blank lines, or leave
the `paragraph` group out via `groups`.

## 8. Half the candidates are still unverified

141 rows are not verification candidates at all (plain definitions, tag
schemes, or our own derivations). Of the remaining **92 candidates, 48 are done** (45 ✅ + 3 🟡)
and **44 are 🔍 open**.

The reason is in [The verification system](verification.md): most sources
publish a formula but never a worked numerical example. This is most
pronounced in the `lexical` group — 7 of its 30 candidates are verified.

This is not a quality problem but a **visibility** choice: the library makes
what has been verified, what has not, and what cannot be, distinguishable.

## 9. The package is not on PyPI yet

Version 0.1.0, early development. You install from a clone. Until 1.0, key
names and the public API may change; changes are announced in the release
notes.
