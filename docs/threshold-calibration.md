# Calibrating the sentence-length thresholds

`short_sent_threshold` and `long_sent_threshold` were not taken from a
published source; they were chosen by measurement on newspaper columns, with the default sentence rule
and the default word.
This document records that measurement.

**Measured:** 2026-10-06.

## Result

| | `short_sent_threshold` | `long_sent_threshold` |
|---|---|---|
| **Turkish** | 4 | 17 |
| **English** | 8 | 32 |

The thresholds are resolved by language in the `analyze(lang=...)` call. If
you pass your own threshold through `FeatureParams`, yours wins; any field you
leave out keeps the value above ([details](en/how-to/parameters.md)).

## Method

| | Turkish | English |
|---|---|---|
| Source | KEMİK (YTÜ) column corpora | KEMİK `30Columnists` |
| Columnists | 162 | 30 |
| Articles | 4,321 | 1,485 |
| Words measured | 2,108,415 | 1,078,588 |
| **Sentences measured** | **197,990** | **52,745** |

The full corpora were used, with no sampling. The texts are not distributed; only the numbers are published.
Sentences and words were counted exactly as the `sentence` group counts them, with the
library's default sentence rule and default word; both are defined, with examples, in
[Concepts](en/explanation/concepts.md#word-and-sentence). A sentence's length is the number
of words in it, and a sentence with no letter in it is not counted. Only these lengths were
needed, so no other feature was computed.

The 15th and 85th percentiles were chosen as thresholds. A criterion such as
"mean of the outliers" was not used, because defining an outlier already
requires a threshold, and deriving the threshold from it would be circular.

### Raw percentile table

| Percentile | TR (n = 197,990) | EN (n = 52,745) |
|---|---|---|
| 5th | 2.0 | 5.0 |
| 10th | 3.0 | 7.0 |
| **15th** | **4.0** | **8.0** |
| 25th | 5.0 | 11.0 |
| 50th (median) | 9.0 | 19.0 |
| 75th | 14.0 | 27.0 |
| **85th** | **17.0** | **32.0** |
| 90th | 20.0 | 36.0 |
| 95th | 25.0 | 43.0 |

In Turkish the 85th percentile sits on the boundary: at 17, 15.0% of sentences count as long; at 18, 12.9%.

## Why a language-specific threshold

A single pair of thresholds for both languages, such as 5 and 30, sits in the
wrong place in both. In Turkish, 30 words is above even the 95th percentile
(25), so `long_sent_ratio` is practically always near zero. In English the same
number falls between the 75th (27) and 85th (32) percentiles.

The reason is typological: Turkish is agglutinative, and a single word can
carry what a subordinate clause carries in an analytic language. The surface
word count does not measure the same thing in the two languages.

## Comparison with Ateşman (1997)

Ateşman (1997), p.74, gives the calibration endpoints of the formula: the
easiest text has a mean sentence length of **4** words, the hardest **30**.

The Turkish `short_sent_threshold=4` comes from the calibration. That it
coincides with Ateşman's "easiest text" value is only a note: that number is
the mean of a text, not a threshold, so it is not cited as the source — the
same reasoning that applies to 30.
Ateşman's Turkish norm on p.73 (mean sentence length of 9–10 words) also agrees
with the corpus median (9.0).

Ateşman's 30 was **not used** for `long`: it is the mean of the hardest text,
not a threshold for calling a single sentence long. Used as a threshold, it
lies above the 95th percentile in Turkish.

## Scope

**The thresholds were calibrated on newspaper columns.** A column is a single genre.

There is **no guarantee** that the same thresholds suit novels, technical
writing, transcripts, poetry, legal text or textbooks. If you work with those genres, compute the
percentiles of your own corpus and pass them through `FeatureParams`.

Also, `short_sent_ratio` and `long_sent_ratio` are **not comparable across the two
languages**: the same-named column is measured with a different threshold in each.
Before concluding that "Turkish texts have shorter sentences", keep in mind that what
you measure may be the threshold difference, not a language difference. If you want a
shared threshold, give **both fields** explicitly, e.g.
`FeatureParams(short_sent_threshold=5, long_sent_threshold=30)`, and pass the same
object for both languages. If you give only one, the other is still resolved by
language.
