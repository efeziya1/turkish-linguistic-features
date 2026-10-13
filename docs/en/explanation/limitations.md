# Limitations

This page has two parts. The first says where the library is weak; the
second covers points that are not weaknesses of the library but that you
need to know when interpreting the results.

## Limitations of the library

### 1. The sentence thresholds were calibrated on newspaper columns only

The `short_sent_ratio` and `long_sent_ratio` thresholds (TR 4/17, EN 8/32)
were derived from the 15th and 85th percentiles of the sentence-length
distribution in newspaper columns, measured with the default sentence rule
and the default word:

| Language | Sentences |
|---|---|
| Turkish | 197,990 |
| English | 52,745 |

A column is a **single genre**. There is **no guarantee** the thresholds suit
novels, technical writing, transcripts, poetry or children's books. Method:
[Threshold calibration](../../threshold-calibration.md).

### 2. Fifteen citations are secondary

**15** citations carry `as cited in` — the primary source could not
be obtained and the formula was taken from the citing work. For example:

```text
Herdan (1960/1964), as cited in Tweedie & Baayen (1998) p.327, eq. (5)
```

Affected measures include `herdan_c`, `herdan_vm`, `honore_r`, `maas_a2`, `brunet_w`,
`dugast_u`, `simpson_d`, `heaps_beta`, `lix`, `cttr` and `summer_s`. The formulas were verified, but not
against the **primary source's own wording**.

### 3. The spaCy model is part of the result

POS tags, morphological tags, English lemmas and the dependency features
(with the parser's own sentences) come from the model. Change the model and
those numbers change. Turkish lemmas come from Zeyrek (§4).

Words and sentences are counted with the library's own rules
([Concepts](concepts.md#word-and-sentence)).
`describe_feature(key)["definitions"]["word"]` names the word each feature uses.

Tested versions: spaCy 3.8.16, `en_core_web_sm` 3.8.0,
`tr_core_news_md` 1.0.

### 4. Turkish morphology depends on Zeyrek

The 23 features in the `morphological_zeyrek` group and the Turkish lemmas come
from Zeyrek. Zeyrek can return several analyses for a word; the library takes the
first, without looking at the context. Which one comes first can differ slightly
each time Python runs; for reproducible numbers, start Python with
`PYTHONHASHSEED=0`.

### 5. Two thirds of the candidates are still unverified

Of the **151 verification candidates, 48 are done** (46 ✅ + 2 🟡) and **103 are 🔍
open**: most sources publish a formula but never a worked numerical example.
Details: [The verification system](verification.md).

### 6. Early development (0.x)

Until 1.0, key names and the public API may change; changes are announced in the release
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

There is nothing wrong with using them; cite the source of the formula, but do
not present the measure as that source's own.

### 8. Paragraph features depend on how the input is formatted

The three `paragraph` features find paragraph boundaries from blank lines; a
single line break does not count. If the text has no blank lines, the whole
text counts as one paragraph; this is common in text extracted from PDF and
EPUB. If a text longer than 1000 words has no paragraph boundary at all, a
`ParagraphStructureWarning` is raised.

### 9. What the syllable count reads aloud, and what it skips

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
