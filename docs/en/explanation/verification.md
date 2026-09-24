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

## First: not every feature can be verified

This distinction is the most important part of the report. By definition,
some of the 208 features are **not even candidates** for verification:

| | Why not a candidate |
|---|---|
| ⚪ **no source** | A plain definition. `punc_,_ratio` means "commas / words"; there is no number in the literature to look for. `char_a`…`char_z` is 26 keys on its own. |
| ⚫ **tag scheme** | Not a measure but a count of an external scheme's categories. `pos_noun` → UD, `case_loc_ratio` → Zeyrek. **A scheme defines categories; it does not publish measurements** — de Marneffe's paper does not print "morph_case_loc = 0.07", and could not. |
| 🔧 **derivative** | The formula is from a source, **the application is ours**. `entropy_std` is Shannon's entropy, but taking its standard deviation across segments is ours; `long_sent_ratio`'s threshold comes from our own calibration. Nobody has published these measures — testing them against our own calibration would be reading our own answer sheet. |

On the Turkish side **141 rows** are one of these three. That leaves
**92 verification candidates**. That is the real denominator.

## The four statuses a candidate can have

| | Meaning |
|---|---|
| ✅ **exact** | Within tolerance of the number the source published. |
| 🟡 **documented deviation** | There is a difference and **the reason is written down** — the source rounded an intermediate value, the source's own numbers were produced by hand, and so on. |
| 🔍 **open** | The source gives the formula but never applies it to anything. Verifiable, not yet verified. |
| ❌ **mismatch** | An **unexplained** difference. **Release gate: a single one blocks a release.** |

Where things stand today: **48 of the 92 candidates are done** (45 ✅ +
3 🟡), 44 are 🔍 open.

The tolerance is **0.05**. Sources print rounded intermediate values, so
exact equality is not expected.

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

## Why 44 rows are still 🔍 open

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
| `readability` | 11 | 3 | 2 |
| `lexical` | 7 | 0 | 23 |
| `phonetic` | 0 | 0 | 12 |

Readability formulas are **practical instruments** — their authors publish
the formula together with a worked example, because the point is for someone
else to apply it. Lexical richness measures are mathematical definitions;
the author gives the formula and leaves the example to the reader.

## How a 🔍 becomes a ✅

Someone has to find a number the source actually published. Three recent
examples:

**The QUITA manual — thirteen features at once.** The manual works fourteen
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

All twenty-eight comparisons agree; all but one to five decimal places.

Note: the texts are under copyright (Orwell) and are **not** stored in the
repository — what is kept is the frequency distribution, 119 and 121 plain
integers. No text can be reconstructed from it.

**`mtld`** — McCarthy & Jarvis (2010) p.385 write: *".887 forms 40.4% of
the range between 1.00 and the full factor of .720."* A sequence of 47
types in 53 tokens, run through the production code, yields a partial
factor of **0.4043** — an exact match at the source's own precision.
⚪ → ✅

**`coleman_liau`** — The article gives two separate equations (estimate a
cloze percentage, then convert cloze to a grade level). Our formula is the
composition of the two, and the article never prints it in that form. Both
routes were computed on the same text: **7.7041** and **7.7046**. ⚪ → ✅

## What a 🟡 looks like — the Kincaid case

`ari` and `flesch_kincaid_grade` are 🟡. Here is why they are not ✅ and not
❌ either.

Appendix A of Kincaid et al. (1975) prints **18 real texts**, and Tables 1
and 2 print the values the source itself computed for them. All 18 went
through the pipeline. The mean deviation is **0.54 ARI points** — above the
0.05 tolerance, so ✅ is out.

It is not ❌ because the cause was **measured**:

- **The stroke definition was tested.** Counting spaces as strokes pushes
  the deviation from 0.54 to 4.24. Our space-excluding count is the correct
  one.
- **Whether the heading is counted was tested.** The source does not say;
  the with-heading variant is worse in all 18 passages. Headings are not
  counted.
- **The remaining difference was measured.** In 17 of the 18 passages, the
  stroke count that would yield the source's number is 0.996–1.041 times
  ours — a handful of characters. The source's numbers were produced in 1975
  **by hand**, with a mechanical counter attached to a typewriter; a
  difference of that size is expected.
- **The outlier was identified.** In passage 2 the source's own two numbers
  contradict each other: the sentence length implied by Table 1's ARI does
  not reproduce Table 2's FKGL.

All of it sits in the **passage-by-passage appendix** at the end of the
report, stroke and word counts included, so you can see which input a
difference came from.

That is what 🟡 means: *there is a difference, we measured it, and we know
where it comes from.*

## The report is generated from the tests

`docs/verification-report.md` is not written by hand.
`scripts/dogrulama_raporu.py` generates it, and
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
- **🔍 open** — the formula is implemented correctly but has not been
  compared numerically against the source. Give the citation; do **not**
  claim the number was verified against the source.
- **⚪ no source** — this is the library's own definition. Write the
  definition out yourself in your methods section.
- **⚫ tag scheme** — the number is ours, the categories are the scheme's.
  Cite the scheme (UD or Zeyrek), not a measure.
- **🔧 derivative** — the formula is the source's, the application ours.
  Cite the formula's source, but do not present the measure as "the X
  (year) measure"; write the definition out yourself.
- **❌** — if one exists, no release was made. If you see one, file an issue.
