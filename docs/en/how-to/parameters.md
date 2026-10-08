# Change the thresholds

Window sizes, thresholds and sample counts live in `FeatureParams`.

## Usage

```python
import turkish_linguistic_features as tlf
from turkish_linguistic_features import FeatureParams

# metin: the three-sentence Turkish text from the tutorial (7, 7 and 16 words)
p = FeatureParams(short_sent_threshold=3, long_sent_threshold=12)
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
| `heaps_min_tokens` | 300 | `heaps_beta` |
| `heaps_step` | 50 | `heaps_beta` |
| `brunet_w_a` | 0.172 | `brunet_w` |
| `verb_suffix_window` | 50 | `zeyrek_verb_suffix_diversity` |
| `short_sent_threshold` | TR **4** · EN **8** | `short_sent_ratio` |
| `long_sent_threshold` | TR **17** · EN **32** | `long_sent_ratio` |
| `max_parse_depth` | 20 | `parse_depth_mean` |

## The sentence thresholds resolve per language

These are the only two fields in the table without a single value. The reason
is typological: Turkish sentences are shorter than English ones, so one
threshold cannot serve both.

| Language | short | long |
|---|---|---|
| Turkish | **4** | **17** |
| English | **8** | **32** |

They were derived from the 15th and 85th percentiles of the sentence-length
distribution in newspaper columns, measured with the default sentence rule and
the default word (Turkish: 162 columnists / 197,990 sentences; English: 30
columnists / 52,745 sentences). Method:
[Threshold calibration](../../threshold-calibration.md).

**Resolution is per field.** A field you set uses your number; a field you
leave out keeps the calibrated value for the language. Changing an unrelated
field therefore does not disturb the thresholds:

```python
text = ("Kapı açıldı. Sabah erkenden yola çıktık. Köyün girişindeki "
        "yaşlı çınarın altında oturan adam, uzun yıllar önce bu yollardan "
        "geçen kervanları, pazar günlerini ve kaybolan komşularını anlattı.")
p = FeatureParams(mattr_window=100)            # thresholds untouched
feats = tlf.analyze(text, lang="tr", params=p)  # still TR 4/17
```

Output — sentences of 2, 4 and 20 words:

```text
params=None                       short=0.333333   long=0.333333
FeatureParams(mattr_window=100)   short=0.333333   long=0.333333
```

The two rows match, because `mattr_window` has nothing to do with sentence
thresholds.

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
default here is 50 — a tenth of that. The reasons:

- The window size is also a **lower bound**: `mattr` requires at least
  `2 × window` words. At 500, no text under 1000 words could produce a
  value at all.

The citation states this distinction openly. If you want 500:

```python
p = FeatureParams(mattr_window=500)
```

and make sure your texts are at least 1000 words. You do not need to carry the
sentence thresholds over by hand; they stay at their calibrated values.
