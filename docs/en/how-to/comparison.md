# Compare two versions

Measuring two states of the same text — before and after an edit, a
translation against its original, a draft against the final — is the most
direct use of this library. The comparison is fair because **the same
text** goes through the same pipeline twice.

## Method

```python
import turkish_linguistic_features as tlf

before = tlf.analyze(before_text, lang="en")
after  = tlf.analyze(after_text,  lang="en")

print(f"{'key':22s} {'before':>10} {'after':>10} {'diff':>10}")
for k in ("sent_len_mean", "word_len_mean", "flesch_reading_ease",
          "flesch_kincaid_grade", "ari", "coleman_liau", "ttr", "long_word_ratio"):
    print(f"{k:22s} {before[k]:10.4f} {after[k]:10.4f} {after[k]-before[k]:+10.4f}")
```

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

Output:

```text
key                        before      after       diff
sent_len_mean             26.5000     8.0000   -18.5000
word_len_mean              5.9434     4.6667    -1.2767
flesch_reading_ease       10.7375    68.2900   +57.5525
flesch_kincaid_grade      18.3450     5.7217   -12.6233
ari                       20.1689     5.1387   -15.0302
coleman_liau              18.0302     7.9400   -10.0902
ttr                        0.6792     0.9583    +0.2791
long_word_ratio            0.4528     0.2083    -0.2445
```

How to read it:

- **Sentence length 26.5 → 8 words.** This is the real change; two long
  sentences became three short ones.
- **Flesch Reading Ease 10.7 → 68.3.** On the 0–100 scale, 10.7 is
  "very difficult" (postgraduate) and 68.3 is "standard". A 57-point jump.
- **All three grade-level formulas agree on the direction** and roughly on
  the size: FKGL −12.6, ARI −15.0, Coleman-Liau −10.1. Agreement in direction
  is reassuring, but not proof: all three rest on word and sentence length.
- **`long_word_ratio` 0.45 → 0.21.** "investigation", "concordance",
  "determination" are gone.
- **`ttr` 0.68 → 0.96 but this means nothing.** The second text is shorter,
  so TTR rose. That is length, not style. This is exactly why TTR should
  not be read on its own.

## What to watch for

!!! warning "If the length changed, do not read lexical richness"

    When an edit shortens a text, `ttr`, `hapax_ratio` and `yule_k` change
    **because of length**. For a real comparison on those measures, bring
    both texts to the same size. That only works when both texts are at
    least `size` tokens long; it does not suit the short examples on this
    page (`segment_text` returns an empty list).

    ```python
    p1 = tlf.segment_text(before_text, size=500, lang="en")
    p2 = tlf.segment_text(after_text,  size=500, lang="en")
    if p1 and p2:                      # both ≥ 500 tokens
        before, after = tlf.analyze(p1[0], lang="en"), tlf.analyze(p2[0], lang="en")
    ```

    `mattr`, `mtld` and `vocd_d` are **less** sensitive to length than TTR,
    but **not independent** of it; `mtld` and `vocd_d` drift noticeably in
    Turkish ([measured example](https://github.com/efeziya1/turkish-linguistic-features/blob/main/examples/09_uzunluk_duyarliligi.py)). They
    also need at least 100 words. When comparing texts of different lengths,
    bring them to the same size with `segment_size` first.

Sentence length, syllable mean, word length and the readability formulas
are relatively insensitive to length, but noisy in short texts: a change to
a few sentences moves them noticeably. SMOG needs at least 30 sentences and
returns `nan` below that.

## Many pairs at once

If you have a set of pairs, build a table:

```python
import turkish_linguistic_features as tlf

rows = []
for name, before_text, after_text in pairs:
    for label, text in (("before", before_text), ("after", after_text)):
        rows.append({"label": label, "source": name, "segment_id": 0,
                     **tlf.analyze(text, lang="en")})

tlf.save_csv(rows, "before-after.csv")
```

Because `label` holds `before`/`after`, the CSV feeds straight into a
paired analysis.
