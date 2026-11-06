# Calibrating the sentence-length thresholds

`short_sent_threshold` and `long_sent_threshold` were not taken from a
published source; they were chosen by measurement on newspaper columns, with the default sentence rule
and the default word.
This document records that measurement.

**Measured:** 2026-10-06; re-measured with version 0.3.0 (2026-11-04). The thresholds did not change.

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
| Columnists | 137 | 30 |
| Articles | 4,321 | 1,485 |
| Words measured | 2,108,415 | 1,078,588 |
| **Sentences measured** | **198,225** | **52,745** |

The Turkish columnists were counted after merging case, Turkish letters and spacing in the
corpora's author folder names; the same author can be spelled differently across corpora
(`canDundar` / `candundar`), and the raw names give 162.

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

| Percentile | TR (n = 198,225) | EN (n = 52,745) |
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

In Turkish the 85th percentile sits on the boundary: at 17, 14.9% of sentences count as long; at 18, 12.9%.

### Short and long sentences

A **short sentence** is shorter than the threshold (fewer words than `short_sent_threshold`); a
**long sentence** is longer than the threshold (more words than `long_sent_threshold`). A
sentence whose length equals the threshold is in neither count.

Why: sentence lengths are whole numbers, so whether the threshold itself is included changes
the share noticeably. In Turkish, including it would count 19.2% of sentences as short and
17.3% as long; excluding it gives 12.2% short and 14.9% long. The second pair is closer to
15%.

## Why a language-specific threshold

A single pair of thresholds for both languages, such as 5 and 30, sits in the
wrong place in both. In Turkish, 30 words is above even the 95th percentile
(25), so `long_sent_ratio` is practically always near zero. In English the same
number falls between the 75th (27) and 85th (32) percentiles.

The reason is typological: Turkish is agglutinative, and a single word can
carry what a subordinate clause carries in an analytic language. The surface
word count does not measure the same thing in the two languages.

## Comparison with Ateşman (1997)

Ateşman (1997, p.73) gives 9–10 words as the mean sentence length of Turkish; the
corpus median (9.0) agrees with it, and the mean is 10.64 words. In English columns the mean
is 20.45 words. That is longer than the 14–15 words Ateşman gives for English, following
Flesch, but inside the 8–29-word range Flesch (1948, p.230) gives across genres; the
difference most likely comes from genre.

## Where each threshold falls in the other language

Applied to the other language's columns, a threshold separates a very different share of
sentences:

| Threshold | In its own language | In the other language |
|---|---:|---:|
| Turkish short (under 4 words) | 12.2% | English 3.0% |
| Turkish long (over 17 words) | 14.9% | English 54.2% |
| English short (under 8 words) | 12.4% | Turkish 40.9% |
| English long (over 32 words) | 14.7% | Turkish 1.7% |

No threshold falls on the same percentile in the other language. So a feature with the
same name does not measure the same thing in both languages under a shared threshold.

## Scope

**The thresholds were calibrated on newspaper columns.** A column is a single genre.

There is **no guarantee** that the same thresholds suit novels, technical
writing, transcripts, poetry, legal text or textbooks.

Also, `short_sent_ratio` and `long_sent_ratio` are **not comparable across the two
languages**: the same-named column is measured with a different threshold in each.
If you want a shared threshold, give **both fields** explicitly, e.g.
`FeatureParams(short_sent_threshold=5, long_sent_threshold=30)`, and pass the same
object for both languages. If you give only one, the other is still resolved by
language.
