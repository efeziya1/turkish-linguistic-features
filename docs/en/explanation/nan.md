# What NaN means

## Short answer

`nan` means **"I cannot compute this number for this text."** It is not an
error; it is a missing-data marker.

The library does not invent a number from insufficient data. If it did, your
table would contain a column that looks real and means nothing, with no way
to tell.

## How often

In a three-word English text:

```python
short = tlf.analyze("A short sentence.", lang="en")
nans = [k for k, v in short.items() if isinstance(v, float) and v != v]
len(short), len(nans)
```

```text
(174, 33)
```

**33 of 174** features are `nan`. Examples:

```text
['aspect_imp_ratio', 'aspect_perf_ratio', 'aspect_prog_ratio',
 'case_abl_ratio', 'case_acc_ratio', 'case_dat_ratio', 'case_gen_ratio',
 'case_loc_ratio']
```

In the same text, `ttr` still returns a number:

```text
mattr  = nan   (needs at least 100 words)
ttr    = 1.0   (computable at any length)
```

## Why it happens

Three reasons.

### 1. The text is too short

Every feature has a minimum, and it is stated in the registry:

```python
tlf.describe_feature("mattr")["requires"]
```

```text
'at least 100 words (2 x mattr_window)'
```

A **word** here is the library's default word: a whitespace-separated unit
with edge punctuation stripped that contains a letter or digit (`e-posta`,
`%50` and numbers are one word each). Every feature except the dependency
features counts this word; `describe_feature(key)["definitions"]["word"]` says
which. `segment_text`'s `size` counts the same word, so a 100-word segment
meets a 100-word minimum.

Below the minimum you get `nan`. Some minimums come from the source
(`mtld`: "texts as short as 100 tokens can be used"), others from the
mathematics: with a single window, `mattr` collapses to plain TTR and stops
being a moving average — hence the `2 × window` threshold.

### 2. The required structure is absent

`zeyrek_derivational_suffix_ratio` has a zero denominator if the text contains no
derivational suffixes. `parse_depth_mean` cannot produce a value if no
sentence parses. `hapax_ratio` is meaningless in a one-word text.

### 3. An optional package is missing

Without `wordfreq`, `wordfreq_mean` and `wordfreq_rare_ratio` return `nan`
and the library raises a `MissingDependencyWarning`.

```python
oz = tlf.analyze(text, lang="en", warn=False)
```

`warn=False` silences the warning only; the feature is still `nan`. The same
flag also silences `ParagraphStructureWarning`.

## Not `nan`, but misleading: paragraphs

Paragraph boundaries are found from blank lines; a single line break does
not count. If your text has no blank lines, the whole text counts as one
paragraph and `para_len_mean` becomes the word count of the entire text: the
value is not `nan`, but it says nothing about paragraphs.

If a text longer than 1000 words yields no boundary at all, a
`ParagraphStructureWarning` is raised:

```python
import warnings
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    feats = tlf.analyze(book_text, lang="en")
print(caught[0].message)
```

```text
No paragraph boundary found: the text contains no blank line, so all 52521
words and 7347 sentences were counted as a single paragraph. ...
```

The message carries your own word and sentence counts, so you can tell at a
glance whether the text really is one paragraph.

This usually happens when the text lost its line breaks during extraction from
PDF or EPUB; [limitations §9](limitations.md) has the measurement.

## What to do in your table

**Do not fill `nan` with zero.** Zero is a measurement; `nan` is the
absence of one. `ttr = 0` says "no diversity at all"; `ttr = nan` says
"I could not measure it". Conflate them and your statistics break.

A sound approach:

```python
import pandas as pd
df = pd.DataFrame(tlf.analyze_corpus("corpus/", lang="en"))

# columns that were never measurable
never = df.columns[df.isna().all()]

# columns with partial gaps
partial = df.columns[df.isna().any() & ~df.isna().all()]
```

**Drop** the all-`nan` columns — that feature does not work on your corpus.
For the partial ones the decision is yours: drop the rows, or drop the
column.

## How to avoid `nan`

Keep texts long enough. The most practical way to clear the thresholds is
segmenting:

```python
rows = tlf.analyze_corpus("corpus/", lang="en", segment_size=1000)
```

1000-word segments feed nearly all 201 features. See
[Split a text into segments](../how-to/segmenting.md).

## Why `nan` and not `None`

`nan` is a `float`. That means every value in the returned dictionary has
the same type, and the table goes straight into `pandas`, `numpy`, R or
CSV. With `None`, the column dtype becomes `object`, arithmetic breaks, and
in a CSV an empty cell becomes hard to distinguish from a real zero.
