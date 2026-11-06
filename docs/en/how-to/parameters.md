# Change the thresholds

Window sizes, thresholds and sample counts live in `FeatureParams`. These are the
parameters; the tool has 21, and you can change all of them.

## Usage

```python
import turkish_linguistic_features as tlf

# text: the three-sentence text from the Turkish tutorial (5, 13 and 7 words)
p = tlf.FeatureParams(short_sent_threshold=3, long_sent_threshold=12)
oz = tlf.analyze(text, lang="tr", params=p)
```

`FeatureParams` is a dataclass; fields you omit keep their defaults. For the
sentence thresholds that default is not a fixed number but the calibrated value
for the language — see [below](#the-sentence-thresholds-resolve-per-language).

Output (`short_sent_ratio`, `long_sent_ratio`):

```text
default (TR 4/17): short=0.0      long=0.0
manual (3/12)    : short=0.0      long=0.333333
```

Same text, different thresholds, different numbers. One of the three
sentences is over 12 words; none is over 17.

## Every field

| Field | Default | Affects |
|---|---|---|
| `mattr_window` | 50 | `mattr` |
| `mtld_threshold` | 0.72 | `mtld` |
| `mtld_min_tokens` | 100 | `mtld` |
| `hdd_sample_size` | 42 | `hdd` |
| `msttr_segment_size` | 100 | `msttr` |
| `vocd_sample_min` | 35 | `vocd_d` |
| `vocd_sample_max` | 50 | `vocd_d` |
| `vocd_num_samples` | 100 | `vocd_d` |
| `vocd_num_runs` | 3 | `vocd_d` |
| `vocd_min_tokens` | 50 | `vocd_d` |
| `vocd_random_seed` | 42 | `vocd_d` |
| `heaps_points` | 20 | `heaps_beta` |
| `brunet_w_a` | 0.172 | `brunet_w` |
| `brunet_w_b` | 20 | `brunet_w` |
| `verb_suffix_window` | 10 | `zeyrek_verb_suffix_diversity` |
| `verb_suffix_num_samples` | 100 | `zeyrek_verb_suffix_diversity` |
| `verb_suffix_random_seed` | 42 | `zeyrek_verb_suffix_diversity` |
| `kalyoncu_ttr_window` | 500 | `kalyoncu_ttr`, `kalyoncu_k1`–`kalyoncu_k3` |
| `short_sent_threshold` | TR **4** · EN **8** | `short_sent_ratio` |
| `long_sent_threshold` | TR **17** · EN **32** | `long_sent_ratio` |
| `max_parse_depth` | 20 | `parse_depth_mean` |

`zeyrek_verb_suffix_diversity` draws 100 random samples from the text's verbs; each sample
has 10 verbs, with no verb repeated within a sample. The result is the mean number of
distinct suffix types seen in the samples (Brezina & Pallotti 2019, pp.107-108: MC10). The
tool measures only the within-sample variety; MC10's between-sample component is left
out, so the measure is close to MC10a.

## Constants taken from sources were not tested on Turkish

Some values in the table are the source's own constants: MTLD's 0.72 threshold
(McCarthy & Jarvis 2010, p.385), HD-D's 42-word sample (p.383) and the 0.172 of Brunet's
measure (Brunet 1978, p.49). These numbers were set on English or French texts and have
not been tested on Turkish texts. It cannot be said that they do not carry over to Turkish,
but it has not been shown that they do.

For readability formulas, how this problem is handled is known: Ateşman (1997,
pp.73–74) kept the structure of the Flesch formula when applying it to Turkish and
recomputed its coefficients from Turkish texts. In this tool, the sentence thresholds were
likewise measured separately for each language (below). To try a constant on your own
corpus, change it with the fields above.

## The sentence thresholds resolve per language

These are the only two fields in the table without a single value. The reason
is typological: Turkish sentences are shorter than English ones, so one
threshold cannot serve both. The Turkish long-sentence threshold of 17 words counts 54% of
sentences in English columns as long; in its own language the share is 15%.

| Language | short | long |
|---|---|---|
| Turkish | **4** | **17** |
| English | **8** | **32** |

They were derived from the 15th and 85th percentiles of the sentence-length
distribution in newspaper columns, measured with the default sentence rule and
the default word (Turkish: 198,225 sentences; English: 52,745 sentences). Method:
[Threshold calibration](../../threshold-calibration.md).

## Which feature depends on which parameter

```python
tlf.describe_feature("mattr")["params"]
```

```text
('mattr_window',)
```

An empty tuple, `()`, means the feature depends on no parameter.

## Why `mattr_window` is 50

Covington & McFall (2010) recommend **500** for stylometric analysis. The
default here is 50 — a tenth of that, because the window size is also a **lower
bound**: `mattr` requires at least `2 × window` words. At 500, no text under 1000
words could produce a value at all.

The citation states this distinction openly. If you want 500:

```python
p = tlf.FeatureParams(mattr_window=500)
```
