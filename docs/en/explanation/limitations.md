# Limitations

This page has two parts. The first says where the tool is weak; the
second covers points that are not weaknesses of the tool but that you
need to know when interpreting the results.

## Limitations of the tool

### The sentence thresholds were calibrated on newspaper columns only

The `short_sent_ratio` and `long_sent_ratio` thresholds (TR 4/17, EN 8/32)
were derived from the 15th and 85th percentiles of the sentence-length
distribution in newspaper columns, measured with the default sentence rule
and the default word:

| Language | Columnists | Sentences |
|---|---:|---:|
| Turkish | 137 | 198,225 |
| English | 30 | 52,745 |

A column is a **single genre**. Sentence length also varies with genre, so the thresholds
may come out differently for novels, technical writing, transcripts, poetry or children's
books. Both corpora come from a limited number of writers; in the English corpus of only 30
columnists in particular, the thresholds may reflect those writers' style. The thresholds
show where a sentence falls in the distribution; they do not show whether readers actually
find such sentences short or long. Method:
[Threshold calibration](../../threshold-calibration.md).

### Constants taken from sources were not tested on Turkish

MTLD's 0.72 threshold, HD-D's 42-word sample and the 0.172 of Brunet's measure were taken
from their sources and have not been tested on Turkish texts. It cannot be said that they
do not carry over to Turkish, but it has not been shown that they do. Details:
[Change the thresholds](../how-to/parameters.md#constants-taken-from-sources-were-not-tested-on-turkish).

### Thirteen citations are secondary

**13** citations (12 in Turkish) carry `as cited in`: the primary source could not
be obtained and the formula was taken from the citing work. For example:

```text
Herdan (1960/1964), as cited in Tweedie & Baayen (1998) p.327, eq. (5)
```

Affected measures include `herdan_c`, `herdan_vm`, `honore_r`, `maas_a2`,
`dugast_u`, `simpson_d`, `heaps_beta`, `lix`, `cttr` and `summer_s`. The formulas were
verified, but not against the **primary source's own wording**.

### Accuracy of the language model

POS tags, morphological tags, English lemmas and the dependency features come from the
spaCy model. Change the model and those numbers change. Turkish lemmas come from Zeyrek
(below).

Altinok (2023, p.13747), who developed the Turkish model, reports that on their own test
data the model tags parts of speech correctly 90% of the time, falling to 63% for
dependencies when the relation label is included. The model was trained on formal written
sources; accuracy may differ on other kinds of text. Interpret the features that rest on
this information with care, especially the dependency measures (`syntactic`), where
accuracy is lowest.

Words and sentences are counted with the tool's own rules
([Concepts](concepts.md#word-and-sentence)).
`describe_feature(key)["definitions"]["word"]` names the word each feature uses.

Tested versions: spaCy 3.8.16, `en_core_web_sm` 3.8.0,
`tr_core_news_md` 1.0 (model version 3.4.2), Zeyrek 0.1.3.

### Split words

When spaCy splits a word into several tokens, the tool takes the word's part of speech and
morphological tags from the first token. For example, `sosyo-ekonomik` is an adjective but
is counted as a noun. This only affects the features that use these tags; it does not
touch the word, syllable and sentence counts or the readability formulas. In the newspaper
columns, 0.65% of Turkish words and 2.70% of English words are split into more than one
token.

### Turkish morphology depends on Zeyrek

The 23 features in the `morphological_zeyrek` group and the Turkish lemmas come from
Zeyrek. Zeyrek can return several analyses for a word; the tool takes the first without
looking at the context (in the Kalyoncu formulas, the one matching spaCy's part of
speech). To get the same numbers again, start Python with `PYTHONHASHSEED=0`.

### Two thirds of the candidates are still unverified

Of the **172 verification candidates, 61 are done** (61 ✅) and **111 are 🔍
open**: most sources publish a formula but never a worked numerical example.
Details: [The verification system](verification.md).

### Early development (0.x)

Until 1.0, key names and the public API may change; changes are announced in the release
notes.

## Things to know when using it

These are not shortcomings of the tool: they are how the measures
themselves behave, an input requirement, or an attribution rule. They still
affect your results.

### Tool-specific features

A few features are not literature measures but definitions
this tool made. Their citations say so plainly:

- `punct_entropy`, `sent_len_entropy`: Shannon's formula applied to the
  distribution of punctuation types and of sentence lengths. The formula is
  Shannon's; the decision to apply it there is ours.
- `polysyllabic_word_ratio`: the ratio form of SMOG's input. Not a measure
  McLaughlin defines.

There is nothing wrong with using them; cite the source of the formula, but do
not present the measure as that source's own.

### Paragraph features depend on how the input is formatted

The three `paragraph` features find paragraph boundaries from blank lines; a
single line break does not count. If the text has no blank lines, the whole
text counts as one paragraph; this is common in text extracted from PDF and
EPUB. If a text longer than 1000 words has no paragraph boundary at all, a
`ParagraphStructureWarning` is raised.

### What the syllable count reads aloud, and what it skips

The readability formulas and the syllable features follow Çetinkaya's (2010, p.93)
principle of counting syllables as they are read, so numbers, abbreviations and symbols are
counted **as they are read aloud**: `1918` → bin dokuz yüz on sekiz
(7 syllables), `cm` → santimetre, `%50` → yüzde elli, `3. kat` → üçüncü kat,
`10:30` → on otuz, `3kg` → üç kilogram, `TBMM` → te-be-me-me.

In Turkish, a dot after a number marks an ordinal when a word or a comma
follows it (`3. kat`); otherwise it ends the sentence (`Sonuç 3.` → üç).

Forms whose reading cannot be told from the text are not guessed; they are
**left out** of the syllable count: a unit letter on its own (`m` may be metre
or minute), symbols whose reading depends on context (`/`, `#`, `*`), and
unlisted lowercase abbreviations without vowels. In text dense with symbols
and abbreviations, the syllable count therefore comes out slightly lower than a
hand count.

### Phonological measures are computed from letters

The measures in the `phonological` group (vowel shares, vowel harmony) are computed from
the letters of the written text, not from phonemes; classes such as front and back vowels
are letter lists. They do not work with IPA transcription; that is left for later
versions.

### Heaps β is unreliable on short texts

`heaps_beta` is measured at 20 equally spaced points through the text (Tweedie & Baayen
1998, p.333), so every text is measured with the same number of points. There is no
minimum length; the value is computed for every text of 20 words or more, and a text
shorter than 20 words gives `nan`. The law fits large collections well and is not reliable
on short texts (Manning et al. 2008, p.81).

### The Kalyoncu formulas approximate hand counts

The `kalyoncu_*` keys reproduce Kalyoncu's (2025) hand counts approximately, with Zeyrek and
spaCy. Four of Kalyoncu's nine rules (common derivations, onomatopoeia, intensified forms, rare
senses) and Kalyoncu's meaning-based sentence definition are not applied. KL rests on expert
judgement (rules 3, 5, 8), so it is not expected to match the expert values exactly. Numbers
written in words count as in the list; a capitalised word not at the start of a sentence
counts as a proper noun; stems and verbals are counted from the Zeyrek analysis that matches
spaCy's class (these three rules apply in the `kalyoncu_*` keys only). Verbal suffixes Zeyrek
does not know and errors in the selected analysis change the result. Details:
[Kalyoncu formulas](kalyoncu.md).
