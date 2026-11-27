# Compare two versions

Measuring two states of the same text — before and after an edit, a
translation against its original, a draft against the final — is the most
direct use of this library. The comparison is fair because both states go
through the same pipeline with the same settings.

## Method

```python
import turkish_linguistic_features as tlf

before = tlf.analyze(before_text, lang="en")
after  = tlf.analyze(after_text,  lang="en")

print(before["flesch_reading_ease"], after["flesch_reading_ease"])
```

```text
10.7375 68.29
```

You take a feature's two values by name and set them side by side.

## A real example

An academic paragraph in its heavy form and its plain form:

=== "Before (53 words)"

    > The objective of the present investigation is the comparative
    > evaluation of the formulas utilised in the determination of the
    > readability levels of English texts, together with the establishment
    > of the degrees of concordance obtaining between those formulas. In
    > this connection, three distinct formulas in widespread use within the
    > relevant literature have been examined.

=== "After (24 words)"

    > This study compares English readability formulas. The aim is to show
    > how far they agree. We looked at three formulas that are widely used.

A few features in both states:

| Feature | Before | After |
|---|---:|---:|
| `sent_len_mean` | 26.50 | 8.00 |
| `word_len_mean` | 5.94 | 4.67 |
| `flesch_reading_ease` | 10.74 | 68.29 |
| `flesch_kincaid_grade` | 18.35 | 5.72 |
| `ari` | 20.17 | 5.14 |
| `coleman_liau` | 18.03 | 7.94 |
| `ttr` | 0.68 | 0.96 |
| `long_word_ratio` | 0.45 | 0.21 |

How to read it:

- **Mean sentence length 26.5 → 8 words.** This is the real change; two long
  sentences became three short ones.
- **Flesch Reading Ease 10.7 → 68.3.** On Flesch's bands, 10.7 is
  "very difficult" (postgraduate) and 68.3 is "standard". A 57-point jump.
- **All three grade-level formulas agree on the direction** and roughly on
  the size: FKGL −12.6, ARI −15.0, Coleman-Liau −10.1. Agreement in direction
  is reassuring, but not proof: all three rest on word and sentence length.
- **`long_word_ratio` 0.45 → 0.21.** "investigation", "concordance",
  "determination" are gone.
- **`ttr` 0.68 → 0.96, but this is not meaningful.** The second text is shorter,
  so TTR rose. That is length, not style.

## Many pairs at once

If you have many pairs, put the two states into two folders and give the two files of a pair
the same name:

```text
pairs/
  before/
    text1.txt
    text2.txt
  after/
    text1.txt
    text2.txt
```

```python
rows = tlf.analyze_corpus("pairs/", lang="en")
tlf.save_csv(rows, "before-after.csv")
```

In the table the `label` column is `before` or `after` and the `source` column is the file
name; two rows with the same `source` are a pair. Folder layout:
[Export a corpus to CSV](corpus.md).
