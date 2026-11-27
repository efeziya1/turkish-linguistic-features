# Change the thresholds

Window sizes, thresholds and sample counts live in `FeatureParams`. These are the
parameters; the tool has 21, and you can change all of them.

## Usage

```python
import turkish_linguistic_features as tlf

metin = ("Kapı açıldı. Yaşlı adam yavaşça içeri girdi ve masaya oturdu. Herkes susmuş, "
         "onun ne söyleyeceğini merakla beklerken dışarıda yağmur bütün gece boyunca "
         "durmadan yağmaya devam etti ve sokaklar sular altında kaldı.")

p = tlf.FeatureParams(short_sent_threshold=10, long_sent_threshold=25)
oz = tlf.analyze(metin, lang="tr", params=p)
print(oz["short_sent_ratio"], oz["long_sent_ratio"])
```

```text
0.666667 0.0
```

The text's three sentences have 2, 8 and 21 words. With the default thresholds (4 and 17)
the result is `0.333333 0.333333`: one short and one long sentence. With thresholds of 10
and 25, two sentences are short and none is long.

Fields you leave out keep their default values. The default sentence thresholds were
measured separately for each language — [below](#the-sentence-thresholds-resolve-per-language).

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
| `verb_suffix_window` | 10 | `akana_verb_suffix_diversity` |
| `verb_suffix_num_samples` | 100 | `akana_verb_suffix_diversity` |
| `verb_suffix_random_seed` | 42 | `akana_verb_suffix_diversity` |
| `kalyoncu_ttr_window` | 500 | `kalyoncu_ttr`, `kalyoncu_k1`–`kalyoncu_k3` |
| `short_sent_threshold` | TR **4** · EN **8** | `short_sent_ratio` |
| `long_sent_threshold` | TR **17** · EN **32** | `long_sent_ratio` |
| `max_parse_depth` | 20 | `parse_depth_mean` |

`akana_verb_suffix_diversity` picks 10 verbs at random from the text, counts how many
different suffixes appear among them, and gives the mean over many such picks; the three
`verb_suffix_*` fields set the size of a pick, the number of picks and the random seed.

## The sentence thresholds resolve per language

These two fields have no single default; it depends on the language. The reason:
Turkish sentences are shorter than English ones, so one threshold cannot serve both. The Turkish long-sentence threshold of 17 words counts 54% of
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

An empty value, `()`, means the feature depends on no parameter.
