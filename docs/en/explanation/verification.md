# The verification system

## The problem

A library can say "I implement the Ateşman readability formula." How would
you check? By finding the source, reading the formula and inspecting the
code — that is, by doing enough work that you might as well not use the
library.

This library does something else: it takes **the number the source
published**, gives the same input to its own code, and prints the two side
by side.

The result: [verification report](../../verification-report.md)
([Turkish](../../dogrulama-raporu.md)).

## Two different things, kept apart

The rest of this page is about one of them: how many rows have been compared
against a number the source *published*. That is one layer. The layer beneath
it needs stating plainly too, because the report's "open" count is easy to
misread.

| Layer | What it guarantees | Coverage |
|---|---|---|
| **Formula equivalence** | The code implements the equation in the source. The citation gives page and equation number; tests exercise the formula and its edge cases. | The 190 features with a citation (Turkish; the other 11 are plain definitions with no source) |
| **Source-number verification** | A number the source *published* was found and compared against our output. | 48 of 144 candidate report rows (Turkish) |

The second layer is additional work, not a precondition for the first. A
feature marked "🔍 open" does **not** have a questionable formula; no published
number was found to compare against. Yule (1944) defines K but never prints
what K comes to in a novel — his not printing it does not make our K wrong.

Every feature has its formula written out. The 11 features without a citation
are plain definitions (the dash's share of punctuation marks or the number of
distinct lemmas, for example);
they rest on no source, so there is no source equation to match.

## First: not every feature can be verified

This distinction is the most important part of the report. By definition,
some of the 201 features are **not even candidates** for verification:

| | Why not a candidate |
|---|---|
| ⚪ **no source** | A plain definition. `punct_dash_ratio` means "dashes / all punctuation marks"; there is no number in the literature to look for. |
| ⚫ **tag scheme** | Not a measure but a count of an external scheme's categories. `pos_noun_ratio` → UD, `zeyrek_case_loc_ratio` → Zeyrek. **A scheme defines categories; it does not publish measurements** — de Marneffe's paper does not print "case_loc_ratio = 0.07", and could not. |
| 🔧 **derivative** | The formula is from a source, **the application is ours**. `sent_len_entropy` is Shannon's entropy, but applying it to sentence lengths is ours; `long_sent_ratio`'s threshold comes from our own calibration. Nobody has published these measures — testing them against our own calibration would be reading our own answer sheet. |

On the Turkish side **82 rows** are one of these three. That leaves
**144 verification candidates**. That is the real denominator.

## The four statuses a candidate can have

| | Meaning |
|---|---|
| ✅ **exact** | Within tolerance of the number the source published. If the cause of a small difference is known, it is noted under the row. |
| 🟡 **documented deviation** | The difference is **beyond the tolerance** and **the reason is written down** — the source rounded an intermediate value, the source's own numbers were produced by hand, and so on. |
| 🔍 **open** | The source gives the formula but never applies it to anything. Verifiable, not yet verified. |
| ❌ **mismatch** | An **unexplained** difference. **Release gate: a single one blocks a release.** |

Where things stand today: **48 of the 144 candidates are done** (46 ✅ +
2 🟡), 96 are 🔍 open.

The tolerance is **1% of the published value** (relative). Sources print
rounded intermediate values, so exact equality is not expected. A relative
tolerance means the same at every scale: the old fixed 0.05 was far too loose
for ratios between 0 and 1 (`ttr`) and far too tight for values in the
hundreds (`curve_length` ≈ 134).

**Exceeding the tolerance does not automatically make a row ❌.** What decides
is not the size of the difference but **whether its cause is known**. If the
cause has been measured and written down the row is 🟡; if it has not, the row
is ❌ and no release is made.

This is not an escape hatch. A reason cannot be a guess along the lines of
"it is probably rounding"; it has to be a measurement showing where the
difference came from. The Kincaid example below shows what that looks like.

## Two kinds of evidence

This distinction matters and has its own column in the report.

**End-to-end** pushes the source's **own text** through the pipeline, so
tokenisation, syllabification and sentence splitting are tested too. It is
the strongest evidence: if a number matches, not just the formula but every
step leading to it is correct.

**Formula** feeds the inputs to the function directly — for example
"syllables per word 2.2 and words per sentence 4". It verifies the formula
and its coefficients, not the pipeline. It is what is available when the
source published no text.

## Why 96 rows are still 🔍 open

The source published the formula but never applied it to a text and printed
the result. In quantitative linguistics this is **ordinary**. Yule (1944)
defines K; he does not print what K comes to for a particular novel. With no
such number there is nothing to compare against.

**This does not mean those rows are untested.** Their formulas and edge
cases are tested in their own test files. The report tracks only the
comparison *against the source's number*.

Which groups are verified follows from their genre, not from chance:

| Group | ✅ | 🟡 | 🔍 |
|---|---|---|---|
| `frequency_structure` | 22 | 0 | 2 |
| `readability` | 13 | 1 | 2 |
| `lexical` | 6 | 1 | 29 |
| `phonetic` | 0 | 0 | 11 |

Readability formulas are **practical instruments** — their authors publish
the formula together with a worked example, because the point is for someone
else to apply it. Lexical richness measures are mathematical definitions;
the author gives the formula and leaves the example to the reader.

## How a 🔍 becomes a ✅

Someone has to find a number the source actually published. Three
examples:

**The QUITA manual — fourteen features at once.** The manual works fourteen
indicators through two example texts from beginning to end and prints the
results, and it also **publishes those texts' frequency distributions**
(§15.3). Since the distribution is the only input these indicators take, the
comparison can be made directly:

| | QUITA | ours |
|---|---|---|
| `repeat_rate` Text 2 | 0.02147 | 0.02147 |
| `gini_coef` Text 1 | 0.3045 | 0.30449 |
| `curve_length` Text 2 | 134.2787 | 134.27870 |
| `entropy` Text 1 | 6.438043 | 6.438043 |

Twenty-seven of the twenty-eight comparisons fall within tolerance (the
largest relative difference is under 0.1%, and most deviate by zero). The
remaining one deviates by 0.009, which is 1.5% of the published value; it is
outside the 1% tolerance, so the row is 🟡, and the cause is plain: for `ttr`
on Text 2 the source printed 0.590, but dividing the numbers it
supplies itself gives 121 ÷ 202 = **0.599**. The published figure has a typo;
ours is the arithmetically correct value.

What the repository stores is two frequency distributions: 119 and 121 plain
integers. The texts themselves are under copyright (Orwell) and are not stored;
no text can be reconstructed from the numbers.

**`mtld`** — The measure sweeps the text and counts a "factor" each time TTR
drops below 0.72; the leftover stretch is added as a fractional factor.
McCarthy & Jarvis (2010) p.385 work through exactly that fraction: *".887 forms
40.4% of the range between 1.00 and the full factor of .720."* We ran the same
sequence through the production code and got a fractional factor of **0.4043** —
the same as the source's printed 40.4%.

**`coleman_liau`** — The article defines the measure in two steps: first
estimate the text's cloze percentage, then convert that percentage to a grade
level. In practice the two steps are combined into a single equation, and that
is the standard use in the literature. We measured that running the two steps
separately and using the single equation give the same result: **7.7041** and
**7.7046**. The 0.0005 between them comes from the source rounding an
intermediate value.

## What a 🟡 looks like — the Kincaid case

In the English report two readability features, `ari` and
`flesch_kincaid_grade`, sit at 🟡. `ari` is also in the Turkish schema and is
🟡 there on the same comparison; `flesch_kincaid_grade` is English-only. Three
questions explain it.

**What was compared?** The source for both measures is a 1975 US Navy technical
report. It does not only give the formulas: its appendix reprints **18 real
passages** taken from training material, and its tables give the ARI and FKGL
values the report itself computed for those 18 passages. So the source published
both the input and the answer — the best material verification can hope for. All
18 went through our pipeline.

**How large is the deviation?** The mean of the per-passage absolute
differences is **0.54 ARI points**. The −0.485 shown in the report is a
different number: the gap between the mean the source printed in Table 1
(12.3) and our mean over the 18 passages. Relative to the published
value that is about 3.9% (0.485 ÷ 12.3), far above the 1% tolerance, so ✅ is out.

**Why is it not ❌?** Because we did not guess where the deviation comes from, we
measured it. Both formulas take "strokes per word" (letters and digits) as an
input, and in 1975 that count was made by hand, with a mechanical counter
attached to a typewriter. We tested whether the difference sits there: how many
times our stroke count would the source's own number require? In 17 of the 18
passages the answer is **0.996–1.041 times** — a handful of characters per
passage. That is the size you expect from hand counting.

Two alternative explanations were tested and ruled out: counting spaces as
strokes pushes the deviation from 0.54 to 4.24 (so our space-excluding count is
the right one), and counting the passage headings makes the result worse in all
18 (so the source did not count them). One passage is also internally
inconsistent: in passage 2 the sentence length implied by the source's ARI does
not reproduce its own FKGL.

Every number per passage — stroke and word counts included — sits in the
appendix at the end of the report, so you can see which input a difference came
from.

That is what 🟡 means: *there is a difference, we measured it, and we know
where it comes from.*

## The report is generated from the tests

`docs/verification-report.md` is not written by hand.
`scripts/generate_verification_report.py` generates it, and
`tests/test_kaynak_esligi.py` reads **the same comparison table**. The
report and the tests cannot drift apart; if the report goes stale, a test
fails.

The coverage list comes from the registry, so a feature cannot be added
and quietly left out of the report.

## What to trust

Before you put a number in your work, look up its row:

- **✅** — the source's number matches. Use it.
- **🟡** — there is a difference but the reason is written down. Read the
  reason and decide whether it affects your use.
- **🔍 open** — the formula is matched to the equation in its source, but has
  not been compared against a number the source published. Give the citation;
  do not say "verified against the source's own number".
- **⚪ no source** — the library's own definition, because there is no number in
  the literature to look for (`punct_dash_ratio` = dashes / all punctuation marks).
- **⚫ tag scheme** — the number is ours, the categories are the scheme's.
  Cite the scheme (UD or Zeyrek), not a measure.
- **🔧 derivative** — the formula is the source's; the decision to apply that
  formula to this data is ours.
- **❌** — if one exists, no release was made. If you see one, file an issue.

### For ⚪ and 🔧 we supply the definition

In these two cases you do not have to write the measure's definition from
scratch for your methods section. The registry keeps a citable definition for
every feature:

```python
tlf.describe_feature("sent_len_entropy")["formula"]
```

```text
'Shannon entropy (nats) of the distribution of words per sentence'
```

Five examples:

| Feature | Definition | What belongs to the source |
|---|---|---|
| `punct_entropy` | Shannon entropy (nats) of the distribution over the ten mark types | the entropy formula — Shannon (1948) |
| `sent_len_entropy` | Shannon entropy (nats) of the distribution of words per sentence | the entropy formula — Shannon (1948) |
| `short_sent_ratio` | sentences with fewer than `short_sent_threshold` words / sentences | the threshold value — [threshold calibration](../../threshold-calibration.md) |
| `long_sent_ratio` | sentences with more than `long_sent_threshold` words / sentences | the threshold value — [threshold calibration](../../threshold-calibration.md) |
| `polysyllabic_word_ratio` | 3+ syllable words / syllabifiable words | the definition of polysyllabic — McLaughlin (1969) p.641 |

The one requirement is getting the attribution right: cite the source of the
formula, but do not attribute the measure itself to that source.

- ✗ "the Shannon (1948) `sent_len_entropy` measure"
- ✓ "Shannon (1948) entropy applied to the distribution of sentence lengths
  (as defined by turkish-linguistic-features)"

The first wording implies a measure the reader could look up in the source and
find. Shannon defined the entropy; he did not apply it to sentence lengths.
