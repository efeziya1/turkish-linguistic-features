# Calibrating the sentence-length thresholds

`short_sent_threshold` and `long_sent_threshold` were not taken from a
published source; they were chosen by measurement on novel corpora. This
document records that measurement.

**Measured:** 2026-07-28

## Result

| | `short_sent_threshold` | `long_sent_threshold` |
|---|---|---|
| **Turkish** | 4 | 18 |
| **English** | 7 | 39 |

The thresholds are resolved by language in the `analyze(lang=...)` call. If
you pass your own threshold through `FeatureParams`, yours wins; any field you
leave out keeps the value above ([details](en/how-to/parameters.md)).

## Method

| | Turkish | English |
|---|---|---|
| Authors | 15 | 10 |
| Segments (1000 words) | 9,838 | 6,263 |
| **Sentences measured** | **1,089,841** | **341,892** |

Both sets are novels/fiction. The full corpora were used, with no sampling.
Sentence boundaries were found with the same spaCy model the library uses in
production; feature extraction was not run, since only the number of words per
sentence was needed.

The 15th and 85th percentiles were chosen as thresholds. A criterion such as
"mean of the outliers" was not used, because defining an outlier already
requires a threshold, and deriving the threshold from it would be circular.

### Raw percentile table

| Percentile | TR (n = 1,089,841) | EN (n = 341,892) |
|---|---|---|
| 5th | 3.0 | 4.0 |
| 10th | 4.0 | 6.0 |
| **15th** | **4.0** | **7.0** |
| 25th | 6.0 | 10.0 |
| 50th (median) | 9.0 | 18.0 |
| 75th | 14.0 | 30.0 |
| **85th** | **18.0** | **39.0** |
| 90th | 22.0 | 46.0 |
| 95th | 28.0 | 58.0 |

## Why a language-specific threshold

A single pair of thresholds for both languages, such as 5 and 30, sits in the
wrong place in both. In Turkish, 30 words is above even the 95th percentile
(28), so `long_sent_ratio` is practically always zero. In English the same
number falls exactly on the 75th percentile, so a quarter of the text is
flagged as "long".

The reason is typological: Turkish is agglutinative, and a single word can
carry what a subordinate clause carries in an analytic language. The surface
word count does not measure the same thing in the two languages.

## 15th/85th or 10th/90th

The two candidates were compared by the **proportion of variance in
`short_sent_ratio` and `long_sent_ratio` explained by author identity** (η²).

| | 10th/90th | 15th/85th |
|---|---|---|
| TR `short_ratio` | 0.2745 | 0.2745 |
| TR `long_ratio` | 0.4021 | **0.4194** |
| EN `short_ratio` | 0.0893 | **0.1279** |
| EN `long_ratio` | 0.2701 | **0.2801** |

15th/85th is equally or more discriminating on all four measures. TR
`short_ratio` is a tie because the 10th and 15th percentiles have the same
value (4.0) in Turkish.

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

**The thresholds were calibrated on novels/fiction only.**

There is **no guarantee** that the same thresholds suit technical writing,
transcripts, poetry, legal text or textbooks. If you work with those genres,
compute the percentiles of your own corpus and pass them through
`FeatureParams`.

Also, `short_sent_ratio` and `long_sent_ratio` are **not comparable across
the two languages**: the column with the same name is measured with a
different threshold in each. Keep this in mind before concluding something like
"Turkish texts have shorter sentences" — what you measure may be a difference
in thresholds, not in languages. If you want a common threshold, set **both**
fields explicitly, e.g. `FeatureParams(short_sent_threshold=5,
long_sent_threshold=30)`, and pass the same object for both languages. Set
only one and the other is still resolved by language.
