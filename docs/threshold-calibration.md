# Calibrating the sentence-length thresholds

`short_sent_threshold` and `long_sent_threshold` were not taken from a
published source; they were chosen by measurement on newspaper columns, with the default sentence rule.
This document records that measurement.

**Measured:** 2026-10-06 (current). The earlier measurement of 2026-07-28 is under "Earlier calibration" below.

## Result

| | `short_sent_threshold` | `long_sent_threshold` |
|---|---|---|
| **Turkish** | 4 | 18 |
| **English** | 9 | 33 |

The thresholds are resolved by language in the `analyze(lang=...)` call. If
you pass your own threshold through `FeatureParams`, yours wins; any field you
leave out keeps the value above ([details](en/how-to/parameters.md)).

## Method

| | Turkish | English |
|---|---|---|
| Source | KEMİK (YTÜ) column corpora | KEMİK `30Columnists` |
| Columnists | 162 | 30 |
| Articles | 4,321 | 1,485 |
| Words measured | 2,114,978 | 1,106,919 |
| **Sentences measured** | **197,990** | **52,745** |

The full corpora were used, with no sampling. The texts are not distributed; only the numbers are published.
Sentence boundaries were found with the library's default sentence rule (`. ? ! …`
always, `:` only when what follows starts like a new sentence; an abbreviation dot
does not end a sentence); length is the number of non-punctuation words, as in the
`sentence` group. Feature extraction was not run, since only the number of words per
sentence was needed.

The 15th and 85th percentiles were chosen as thresholds. A criterion such as
"mean of the outliers" was not used, because defining an outlier already
requires a threshold, and deriving the threshold from it would be circular.

### Raw percentile table

| Percentile | TR (n = 197,990) | EN (n = 52,745) |
|---|---|---|
| 5th | 2.0 | 5.0 |
| 10th | 3.0 | 7.0 |
| **15th** | **4.0** | **9.0** |
| 25th | 5.0 | 12.0 |
| 50th (median) | 9.0 | 19.0 |
| 75th | 14.0 | 28.0 |
| **85th** | **18.0** | **33.0** |
| 90th | 20.0 | 37.0 |
| 95th | 25.0 | 44.0 |

## Why a language-specific threshold

A single pair of thresholds for both languages, such as 5 and 30, sits in the
wrong place in both. In Turkish, 30 words is above even the 95th percentile
(25), so `long_sent_ratio` is practically always near zero. In English the same
number falls between the 75th (28) and 85th (33) percentiles.

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

## Earlier calibration (2026-07-28, superseded)

The thresholds were first measured on novel-heavy corpora with the spaCy parser's
sentences: TR 15 authors / 1,089,841 sentences, EN 10 authors / 341,892 sentences.
The result was TR 4/18, EN 7/39. On 2026-10-06 the `sentence` group moved to the
default sentence rule, and the thresholds were re-derived from newspaper columns
measured with that rule. The Turkish values (4/18) did not change; the English
ones moved from 7/39 to 9/33.

| Percentile | TR (n = 1,089,841) | EN (n = 341,892) |
|---|---|---|
| 5th | 3.0 | 4.0 |
| 10th | 4.0 | 6.0 |
| 15th | 4.0 | 7.0 |
| 25th | 6.0 | 10.0 |
| 50th (median) | 9.0 | 18.0 |
| 75th | 14.0 | 30.0 |
| 85th | 18.0 | 39.0 |
| 90th | 22.0 | 46.0 |
| 95th | 28.0 | 58.0 |

At that time the 15th/85th and 10th/90th candidates were compared by the proportion
of variance in `short_sent_ratio` and `long_sent_ratio` explained by author identity
(η²); 15th/85th was equally or more discriminating on all four measures (TR short
0.2745 / 0.2745; TR long 0.4021 / 0.4194; EN short 0.0893 / 0.1279; EN long 0.2701 /
0.2801). That comparison was **not repeated** on the new corpora; the choice of
15th/85th rests on the earlier result.

## Scope

**The thresholds were calibrated on newspaper columns.** A column is a single genre.

Novels give another distribution because dialogue lines produce very short
sentences: in Turkish novels under the default rule about 26.5% of sentences are
shorter than 4 words and 6.6% longer than 18 (12.1% and 13.0% in columns). There is
also **no guarantee** that the same thresholds suit technical writing, transcripts,
poetry, legal text or textbooks. If you work with those genres, compute the
percentiles of your own corpus and pass them through `FeatureParams`.

Also, `short_sent_ratio` and `long_sent_ratio` are **not comparable across the two
languages**: the same-named column is measured with a different threshold in each.
Before concluding that "Turkish texts have shorter sentences", keep in mind that what
you measure may be the threshold difference, not a language difference. If you want a
shared threshold, give **both fields** explicitly, e.g.
`FeatureParams(short_sent_threshold=5, long_sent_threshold=30)`, and pass the same
object for both languages. If you give only one, the other is still resolved by
language.
