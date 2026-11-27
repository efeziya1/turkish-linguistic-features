# The verification system

## The problem

A library can say "I implement the Ateşman readability formula." How would you check? You
would have to find the source, read the formula and inspect the code. That is more work than a user
should have to do.

This library does something else: it takes **the number the source
published**, gives the same input to its own code, and prints the two side
by side.

The result: [verification report](../../verification-report.md)
([Turkish](../../dogrulama-raporu.md)).

## The two layers of verification

### 1. Formula equivalence

The formula of every feature with a citation was checked against its
source; the source is mostly primary, secondary in 12 Turkish citations (`as cited in`). Each
citation shows the page and number of the formula in the source (e.g.
`p.327, eq. (5)`). Tests exercise the formula and its edge cases. The 11 features without a citation are plain definitions; there is no
source to check them against.

### 2. Source-number verification

An extra check on top of the first layer: the result a source published for a text or an
input is found and compared with the tool's result. 22 of the 136 candidate features are
verified in this layer.
The rest of this page is about this layer.

The second layer is not a precondition for the first. A feature marked 🔍 open does
not have a questionable formula; only no published example was found to compare against.

## First: not every feature can be verified

By definition, some of the 217 features are **not even candidates** for verification:

| | Why not a candidate |
|---|---|
| ⚪ **plain definition** | No source. `punct_dash_ratio` means "dashes / all punctuation marks"; there is no number in the literature to look for. |
| ⚫ **tag ratio** | Not a measure but a count of an external scheme's categories. `pos_noun_ratio` → UD, `akana_case_loc_ratio` → Akana. **A scheme defines categories; it does not publish measurements** — de Marneffe's paper does not print "case_loc_ratio = 0.07", and could not. |
| 🔧 **tool-specific** | The formula is from a source, **what it is applied to is the tool's**. `sent_len_entropy` is Shannon's entropy, but applying it to sentence lengths is the tool's decision. Nobody has published this measure. |
| 📐 **calibrated** | The threshold comes from the tool's own calibration: `long_sent_ratio`. Testing the tool against its own calibration would be reading its own answer sheet. |

In Turkish, **81 features** are one of these four; the remaining **136 features** are
verification candidates. Where possible, a feature was tested against more than one
published example.

## The four statuses a candidate can have

| | Meaning |
|---|---|
| ✅ **match** | Within tolerance of the number the source published. If the cause of a small difference is known, it is noted under the row. |
| 🟡 **documented deviation** | The difference is **beyond the tolerance** and **the reason is written down** — the source rounded an intermediate value, the source's own numbers were produced by hand, and so on. |
| 🔍 **open** | The source gives the formula but no example of applying it to a text; it can be verified once a published example is found. |
| ❌ **mismatch** | An **unexplained** difference. **Release gate: a single one blocks a release.** |

Where things stand today: **22 of the 136 candidate features are verified** (✅),
114 are 🔍 open. Turkish has no 🟡; in English two features are 🟡: `ari` deviates from the
source by 4.4% (0.54 points), `flesch_kincaid_grade` by 3.5% (0.37 points). For both, the
reason is that the source counted characters by hand in 1975; the passage-by-passage numbers
are in the appendix of the [verification report](../../verification-report.md).

The tolerance is **1% of the published value** (relative). Sources print
rounded intermediate values, so exact equality is not expected.

**Exceeding the tolerance does not automatically make a row ❌.** What decides
is not the size of the difference but **whether its cause is known**. If the
cause has been measured and written down the row is 🟡; if it has not, the row
is ❌ and no release is made.

**Exception: the source's own calculation.** When a source publishes both the inputs and the
result, the result can be recomputed from those inputs. If the published result does not
agree with that calculation (for instance, the source truncated 121 ÷ 202 = 0.599 to 0.59
instead of rounding it) and the tool's value equals the calculation from the source's own
inputs, the comparison counts as ✅; the case is written under the comparison. The exception
applies only where the source's own numbers allow the check, and today it applies in one
place: `ttr` on QUITA's Text 2.

For a difference beyond the tolerance to count as 🟡, the reason cannot be a guess either
("it is probably rounding"); it has to be a measurement showing where the difference came
from. The two English 🟡 above are an example.

## Two kinds of evidence

This distinction matters and has its own column in the report.

**End-to-end** pushes the source's **own text** through the pipeline, so
tokenisation, syllabification and sentence splitting are tested too. It is
the strongest evidence: if a number matches, not just the formula but every
step leading to it is correct.

**Formula** feeds the inputs to the function directly — for example
"syllables per word 2.2 and words per sentence 4". It verifies the formula
and its coefficients, not the pipeline. Of the 22 verified Turkish features, 19 were tested
this way; the end-to-end ones are the Ateşman, Çetinkaya-Uzun and Bezirci-Yılmaz formulas.

## Why 114 features are still 🔍 open

The source published the formula but never applied it to a text and printed
the result. In quantitative linguistics this is **ordinary**. With no such
number there is nothing to compare against.

`yule_k` is a different case. Yule (1944) prints K values, but computes them on the lemmas of
a single word class, mostly nouns. The tool counts the surface forms of all words, so the two
cannot be compared on the same input.

**This does not mean those rows are untested.** Their formulas and edge
cases are tested in their own test files. The report tracks only the
comparison *against the source's number*.

Which groups are verified follows from their genre, not from chance:

| Group | ✅ | 🔍 |
|---|---:|---:|
| `frequency_structure` | 11 | 6 |
| `lexical` | 5 | 29 |
| `readability` | 3 | 10 |
| `syntactic` | 2 | 0 |
| `pos` | 1 | 4 |

Readability formulas are **practical instruments**: their authors publish the formula
together with a worked example, because the point is for someone else to apply it. That is
why the Ateşman, Çetinkaya-Uzun and Bezirci-Yılmaz formulas could be verified; the open ones
are the formulas' components and Kalyoncu's formulas. Lexical richness measures are
mathematical definitions; the author gives the formula and leaves the example to the reader.

## How a 🔍 becomes a ✅

Someone has to find a number the source actually published. An example:

**The QUITA manual — fourteen features at once.** The manual works fourteen
indicators through two example texts from beginning to end and prints the
results, and it also **publishes those texts' frequency distributions**
(§15.3). Since the distribution is the only input these indicators take, the
comparison can be made directly:

| | QUITA | tool |
|---|---|---|
| `repeat_rate` Text 2 | 0.02147 | 0.02147 |
| `gini_coef` Text 1 | 0.3045 | 0.30449 |
| `curve_length` Text 2 | 134.2787 | 134.27870 |
| `entropy` Text 1 | 6.438043 bits = 4.462511 nats | 4.462512 |

QUITA is the manual of a piece of software: for the formulas it is a secondary source (each
formula's original source is in the citation), while the numbers compared are the manual's own
calculations. QUITA gives entropy in bits; the tool uses natural logarithms, so the value is
converted to nats for the comparison.

All fourteen features match the source on both texts (the largest relative difference is
under 0.1%, and most deviate by zero). Only `ttr` on Text 2 deviates by 0.009, which is 1.5%
of the published value: the source printed 0.59, but dividing the numbers it supplies itself
gives 121 ÷ 202 = **0.599**. The source truncated the result instead of rounding
it (rounded to two decimals it is 0.60). The tool's value is arithmetically correct, so this
comparison is ✅ too (the exception for the source's own calculation, above).

## In short: how much could be checked

Only 22 of the 136 Turkish literature measures could be compared with a worked example
their source published, and all of them match the source. Only three of these features could be tested end to end, that is, together with
word, syllable and sentence counting. Most sources define a measure by its formula but do
not apply it to a text and publish the result.

Outside the report, a test dataset with expert values was also used: the 57 texts
published for the TOMA program (Kalyoncu et al. 2026). On this dataset the tool's word and
syllable counts agree with the expert values almost completely, and its sentence counts and
Turkish readability formulas agree on most texts. For variables that rest on human
judgement (Kalyoncu's KL and KCO) the tool does not reproduce the expert values.

## For ⚪, 🔧 and 📐 the tool gives the definition

These features have no source in the literature, so if you use them in a study you have to
define them yourself. The tool gives a ready-made definition for every feature, which you
can take for your methods section:

```python
tlf.describe_feature("sent_len_entropy")["formula"]
```

```text
'Shannon entropy (nats) of the distribution of words per sentence'
```

Five examples:

| Feature | Definition | What belongs to the source |
|---|---|---|
| ⚪ `lemma_count` | number of different lemmas in the text | — (no source) |
| ⚪ `sent_syllable_mean` | mean syllables per sentence | — (no source) |
| 🔧 `sent_len_entropy` | Shannon entropy (nats) of the distribution of sentence lengths | the entropy formula — Shannon (1948) |
| 📐 `short_sent_ratio` | sentences shorter than 4 words / sentences (8 in English) | the threshold value — [threshold calibration](../../threshold-calibration.md) |
| 📐 `long_sent_ratio` | sentences longer than 17 words / sentences (32 in English) | the threshold value — [threshold calibration](../../threshold-calibration.md) |

Cite the source of the formula, but do not present the measure as that source's own.

- ✗ "the Shannon (1948) `sent_len_entropy` measure"
- ✓ "Shannon (1948) entropy applied to the distribution of sentence lengths
  (turkish-linguistic-features, doi:10.5281/zenodo.23009540)"

The first wording implies a measure the reader could look up in the source and
find. Shannon defined the entropy; he did not apply it to sentence lengths.
