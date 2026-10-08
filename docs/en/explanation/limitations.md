# Limitations

This page has two parts. The first says where the library is weak; the
second covers points that are not weaknesses of the library but that you
need to know when interpreting the results. Read both while writing your
methods section.

## Limitations of the library

### 1. The sentence thresholds were calibrated on newspaper columns only

The `short_sent_ratio` and `long_sent_ratio` thresholds (TR 4/17, EN 8/32)
were derived from the 15th and 85th percentiles of the sentence-length
distribution in newspaper columns, measured with the default sentence rule
and the default word:

| Language | Columnists | Sentences |
|---|---|---|
| Turkish | 162 | 197,990 |
| English | 30 | 52,745 |

A column is a **single genre**. There is **no guarantee** the thresholds suit
novels, technical writing, transcripts, poetry or children's books. If you work
in another genre, consider deriving the thresholds from your own corpus —
[the method is here](../../threshold-calibration.md).

### 2. Fourteen citations are secondary

**14 of 163** citations carry `as cited in` — the primary source could not
be obtained and the formula was taken from the citing work. For example:

```text
Herdan (1960/1964), as cited in Tweedie & Baayen (1998) p.327, eq. (5)
```

Affected measures include `herdan_c`, `herdan_vm`, `maas_a2`, `brunet_w`,
`dugast_u`, `simpson_d`, `heaps_beta`, `lix`, `cttr` and `summer_s`. The formulas were verified, but not
against the **primary source's own wording**.

Carry the "as cited in" through into your own methods section. Do not
present it as though you read the primary.

### 3. The spaCy model is part of the result

POS tags, morphological tags, English lemmas and the dependency features
(with the parser's own sentences) come from the model. Change the model and
those numbers change. Turkish lemmas come from Zeyrek (§4).

Word and sentence counts do not use the model's labels. The default word is a
whitespace-separated unit with edge punctuation stripped; the default sentence
rule reads sentence-ending marks from the model's tokenizer. Every feature
except the dependency features counts this word. Features that need a label
per word (POS, lemma, morphology) take it from the first word token inside the
word: the model splits `Türk-Amerikan` or English `it's` into several tokens,
and the word carries the first part's label (`Türk`, `it`). This happens to
0.3% of the words in Turkish newspaper columns and 2.7% in English ones. The
dependency features count the model's tokens.
`describe_feature(key)["definitions"]["word"]` names the word each feature uses.

Verified combination: spaCy 3.8.16, `en_core_web_sm` 3.8.0,
`tr_core_news_md` 1.0.

The Turkish model has two oddities that look like bugs (a version-number
mismatch and a `W094` warning); both are explained in the
[tutorial](../getting-started.md#2-install-the-language-data) and both are
harmless.

### 4. Turkish morphology depends on Zeyrek

The 23 features in the `morphological_zeyrek` group and the Turkish lemmas
come from Zeyrek, a Python port of Zemberek's morphotactics. A word Zeyrek
cannot analyse drops out of the Zeyrek features; its lemma is the part before
its apostrophe (`Pittsburgh'tan` → `pittsburgh`).

Zeyrek is an **analyser, not a disambiguator**: it can return several
analyses for the same surface form and does not pick the right one from
context. The library takes the **first** analysis, with no context.

Zeyrek orders the analyses by the number of suffix transitions, fewest first;
ties keep the iteration order of an internal Python set, which depends on
`PYTHONHASHSEED`. On the TOMA set (57 texts, 8,215 distinct words) 58.2% of
the words have more than one analysis, and for **200 words (2.4%)** the first
analysis changed across hash seeds 0–3. The Zeyrek features of the same text
can therefore differ slightly between Python processes. For reproducible
numbers, fix the seed before Python starts, e.g. `PYTHONHASHSEED=0`.

### 5. Half the candidates are still unverified

82 rows are not verification candidates at all (plain definitions, tag
schemes, or our own derivations). Of the remaining **142 candidates, 48 are done** (46 ✅ + 2 🟡)
and **94 are 🔍 open**.

The reason is in [The verification system](verification.md): most sources
publish a formula but never a worked numerical example. This is most
pronounced in the `lexical` group — 7 of its 36 candidates are verified.

### 6. The package is not on PyPI yet

Early development (0.x). You install from a clone. Until 1.0, key
names and the public API may change; changes are announced in the release
notes.

## Things to know when using it

These are not shortcomings of the library: they are how the measures
themselves behave, an input requirement, or an attribution rule. They still
affect your results.

### 7. Some features are this library's own derivations

A few features are not named measures from the literature but definitions
this library made. Their citations say so plainly:

- `punct_entropy`, `sent_len_entropy` — Shannon's formula applied to the
  distribution of punctuation types and of sentence lengths. The formula is
  Shannon's; the decision to apply it there is ours.
- `polysyllabic_word_ratio` — the ratio form of SMOG's input. Not a measure
  McLaughlin himself defines.

There is nothing wrong with using them. The one requirement is getting the
attribution right: cite the source of the formula, but do not attribute the
measure itself to that source. In your methods section:

- ✗ "the Shannon (1948) `sent_len_entropy` measure"
- ✓ "Shannon (1948) entropy applied to the distribution of sentence lengths
  (as defined by turkish-linguistic-features)"

The reason is simple: Shannon defined the entropy; he did not apply it to
sentence lengths. The first wording implies a measure the reader could look up
in the source and find.

### 8. Sensitivity to text length

Most lexical richness measures change with length. `ttr` is the extreme
case: it always falls as a text grows.

`mattr`, `mtld` and `vocd_d` are less sensitive to length than TTR but not
independent of it; `mtld` and `vocd_d` drift noticeably in Turkish
([measured example](https://github.com/efeziya1/turkish-linguistic-features/blob/main/examples/09_uzunluk_duyarliligi.py)). They also
need at least 100 words. If you compare texts of different lengths, bring
them to the same size with `segment_size` first
([how](../how-to/segmenting.md)).

### 9. Paragraph features depend on how the input is formatted

The two `para_*` features find paragraph boundaries from **blank lines**. A
single line break does not count as one — otherwise every line of a
hard-wrapped text would be a paragraph.

The consequence: if your text has no blank lines, the whole text counts as one
paragraph. `para_len_mean` becomes the word count of the entire text. The
library cannot fix this — a boundary that was deleted
cannot be recovered.

This is **common** in text extracted from PDF and EPUB: blank lines between
paragraphs are lost during extraction. The value is not `nan`, so the numbers
will not show it; the warning below does.

If a text longer than 1000 words yields no paragraph boundary at all, a
`ParagraphStructureWarning` is raised. If you see it you have two options:
re-extract the source text with paragraphs separated by blank lines, or leave
the `paragraph` group out via `groups`.

### 10. What the syllable count reads aloud, and what it skips

The readability formulas and the syllable features count numbers,
abbreviations and symbols **as they are read aloud**, following the
Çetinkaya-Uzun (2010) counting protocol: `1918` → bin dokuz yüz on sekiz
(7 syllables), `cm` → santimetre, `%50` → yüzde elli, `3. kat` → üçüncü kat,
`10:30` → on otuz, `3kg` → üç kilogram, `TBMM` → te-be-me-me.

In Turkish, a dot after a number marks an ordinal when a word or a comma
follows it (`3. kat`); otherwise it ends the sentence (`Sonuç 3.` → üç).

Forms whose reading cannot be told from the text are not guessed; they are
**left out** of the syllable count: a unit letter on its own (`m` may be metre
or minute), symbols whose reading depends on context (`/`, `#`, `*`), and
unlisted lowercase abbreviations without vowels. In text dense with symbols
and abbreviations, the syllable count therefore comes out slightly lower than a
hand count following the protocol.
