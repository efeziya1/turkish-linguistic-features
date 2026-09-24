# Change the thresholds

Window sizes, thresholds and sample counts live in `FeatureParams`.

## Usage

```python
import turkish_linguistic_features as tlf
from turkish_linguistic_features import FeatureParams

p = FeatureParams(short_sent_threshold=3, long_sent_threshold=12)
oz = tlf.analyze(text, lang="tr", params=p)
```

`FeatureParams` is a dataclass; fields you omit keep their defaults.

Measured:

```text
default (TR 4/18): short=0.0      long=0.0
manual (3/12)    : short=0.0      long=0.333333
```

Same text, different thresholds, different numbers. One of the three
sentences is over 12 words; none is over 18.

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
| `ttr_slope_chunk_size` | 50 | `ttr_moving_slope` |
| `brunet_w_a` | 0.172 | `brunet_w` |
| `verb_suffix_window` | 50 | `verb_suffix_diversity` |
| `short_sent_threshold` | 5 | `short_sent_ratio` |
| `long_sent_threshold` | 30 | `long_sent_ratio` |
| `max_parse_depth` | 20 | `parse_depth_mean` |

## ⚠️ An important detail about the sentence thresholds

The table says `short_sent_threshold=5` and `long_sent_threshold=30`, **but
those values are not used.**

When you do not pass `params`, the library uses **language-specific**
calibrated values:

| Language | short | long |
|---|---|---|
| Turkish | **4** | **18** |
| English | **7** | **39** |

These were derived from the 15th and 85th percentiles of the
sentence-length distribution in novel corpora (Turkish: 15 authors /
1,089,841 sentences; English: 10 authors / 341,892 sentences). Method:
[Threshold calibration](../../esik-kalibrasyonu.md) (in Turkish).

The dataclass's own defaults of 5/30 are an **unreachable fallback** — they
would apply only for an unrecognised language, and `lang` already accepts
only `"tr"` and `"en"`.

!!! danger "Passing `params` loses the calibration"

    If you write `FeatureParams(mattr_window=100)`, then
    `short_sent_threshold` reverts to **5**, not 4. The language-specific
    resolution runs only when `params is None`.

    To change one field only, carry the calibrated values over by hand:

    ```python
    p = FeatureParams(mattr_window=100,
                      short_sent_threshold=4, long_sent_threshold=18)
    ```

## Which feature depends on which parameter

```python
tlf.describe_feature("mattr")["params"]
```

```text
['mattr_window']
```

An empty list means the feature depends on no parameter.

## Why `mattr_window` is 50

Covington & McFall (2010) recommend **500** for stylometric analysis. The
default here is 50 — a tenth of that. The reasons:

- 50 is the established value in the language-learning literature
  (in MSTTR and MTTRSS work `n` is usually 50).
- The window size is also a **lower bound**: `mattr` requires at least
  `2 × window` words. At 500, no text under 1000 words could produce a
  value at all.
- Measured on 15 Turkish novels: at w=50 the measure varies 0.52% with
  length, at w=500 it varies 1.26%. The discrimination signal-to-noise
  ratio is flat (~1.2) across window sizes.

The citation states this distinction openly. If you want 500:

```python
p = FeatureParams(mattr_window=500,
                  short_sent_threshold=4, long_sent_threshold=18)
```

and make sure your texts are at least 1000 words.
