# Limitations

This page has two parts. The first says where the tool is weak; the
second covers points that are not weaknesses of the tool but that you need to know when
interpreting the results.

## Limitations of the tool

### The sentence thresholds were measured on newspaper columns only

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

MTLD's 0.72 threshold (McCarthy & Jarvis 2010, p.385), HD-D's 42-word sample (p.383) and the
0.172 of Brunet's measure (Brunet 1978, p.49) were set on English or French texts and have not
been tested on Turkish texts. It cannot be said that they do not carry over to Turkish, but it
has not been shown that they do. To try a constant on your own corpus:
[Change the thresholds](../how-to/parameters.md).

### Thirteen citations are secondary

**13** citations (12 in Turkish) carry `as cited in`: the primary source could not
be obtained and the formula was taken from the citing work. For example:

```text
Herdan (1960/1964), as cited in Tweedie & Baayen (1998) p.327, eq. (5)
```

Affected measures include `herdan_c`, `herdan_vm`, `honore_r`, `maas_a2`,
`dugast_u`, `simpson_d`, `heaps_beta`, `lix`, `cttr` and `summer_s`. The formulas were
checked against the citing source, but could not be checked against the **primary source
itself**.

### Accuracy of the language model

POS tags, morphological tags and the dependency features come from the spaCy model in both
languages; Turkish lemmas and proper nouns come from Akana (below). If the model changes,
these numbers change.

As reported by Altinok (2023, p.13747), the Turkish spaCy model (`tr_core_news_md`) gets the
part of speech right for 90% of words. In dependency parsing the share is 63%; here both the
word a word attaches to and the type of the relation must be right. The model was trained on
formal written texts, so accuracy may differ on other kinds of text. Interpret the dependency
measures (`syntactic`) with particular care.

Words and sentences are counted with the tool's own rules
([Concepts](concepts.md#word-and-sentence)).
`describe_feature(key)["definitions"]["word"]` names the word each feature uses.

Tested versions: spaCy 3.8.16, `en_core_web_sm` 3.8.0,
`tr_core_news_md` 1.0 (model version 3.4.2), Akana 0.12.0.

### Split words

When spaCy splits a word into several tokens, the tool takes the word's part of speech and
morphological tags from the first token. For example, `sosyo-ekonomik` is an adjective but
is counted as a noun. This only affects the features that use these tags; it does not
touch the word, syllable and sentence counts or the readability formulas. In the newspaper
columns, 0.65% of Turkish words and 2.70% of English words are split into more than one
token.

### Turkish morphology depends on Akana

The 23 features in the `morphological_akana` group, the Turkish lemmas and proper nouns come
from Akana. When a word has several analyses, Akana picks one by looking at the sentence; the
choice is sometimes wrong: in *Bakan dün geldi* 'the minister came yesterday' `bakan` counts
as a verbal (bak-an). The named entity recogniser that finds proper nouns also misses some
names that are ordinary words too: in *Kitabı Sevgi bana verdi* 'Sevgi gave me the book'
`Sevgi` counts as a noun (`NOUN`).

### Most features have no published example

Of the **136 candidate features, 22 were compared with a published example and all matched** (✅). For **114**, no
published example was found in the sources (🔍 open): most sources publish a formula but
no example of applying it to a text.
Details: [The verification system](verification.md).

### Early development (0.x)

Until 1.0, key names and the public API may change; changes are announced in the release
notes.

## Things to know when using it

These are not shortcomings of the tool: they are how the measures themselves behave, an input
requirement, or an attribution rule. They still affect your results.

### Tool-specific features

A few features are not literature measures but definitions
this tool made. Their citations say so plainly:

- `punct_entropy`, `sent_len_entropy`: Shannon's formula applied to the
  distribution of punctuation types and of sentence lengths. The formula is
  Shannon's; where it is applied is the tool's decision.
- `polysyllabic_word_ratio`: the ratio form of SMOG's input. Not a measure
  McLaughlin defines.

There is nothing wrong with using them; cite the source of the formula, but do not present
the measure as that source's own.

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

A dot inside a number: with an hour of 0–24 before the dot and two digits of 00–59 after it,
the number is read as a time (`8.15` → sekiz on beş, `12.30` → on iki otuz); otherwise it is
a decimal, read with "nokta" (`1.5` → bir nokta beş, `1.60`, `25.30` → yirmi beş nokta otuz).
A single `0` is not taken as an hour (`0.25` → sıfır nokta yirmi beş; midnight is written
`00.25`). Three digits after the dot make a thousands group (`2.850` → iki bin sekiz yüz
elli). Decimals that look like times (`4.50` lira) are read as times and come out two
syllables short.

More examples:

| Form | Reading | Syllables |
|---|---|---:|
| `ve/veya`, `4+4+4` (joined by a symbol) | ve veya · dört artı dört artı dört | 3 · 7 |
| `1/2` (fraction) | bir bölü iki | 5 |
| `12/05/2020`, `13.3.2008` (date) | on iki sıfır beş iki bin yirmi · on üç üç iki bin sekiz | 11 · 8 |
| `4x4` (`x` between numbers) | dört çarpı dört | 4 |
| `F1`, `A2'den` (letters + number) | fe bir · a iki den | 2 · 4 |
| `5N1K` | beş ne bir ke | 4 |
| `Dersim'38` (shortened year) | dersim otuz sekiz | 6 |
| `tv` (vowelless abbreviation) | te ve | 2 |

Forms whose reading cannot be told from the text are not guessed; they are **left out** of
the syllable count: a single lowercase consonant on its own, e-mail and web addresses. In the
newspaper columns, 0.03% of words are left out this way.

### Phonological measures are computed from letters

The measures in the `phonological` group (vowel shares, vowel harmony) are computed from
the letters of the written text, not from phonemes; classes such as front and back vowels
are letter lists. They do not work with IPA transcription; that is left for later
versions.

### Heaps β is unreliable on short texts

`heaps_beta` is measured at 20 equally spaced points through the text (Tweedie & Baayen
1998, p.333), so every text is measured with the same number of points. The value is
computed for every text of 20 words or more; a shorter text gives `nan`. The law fits large collections well and is not reliable
on short texts (Manning et al. 2008, p.81).

### Measures that need human judgement are computed approximately

The sources of some measures did the counting by hand, with expert judgement: an expert
decides whether a word counts as being in a list, or where a sentence ends in meaning. The
tool makes these decisions with rules, so the result is close to the expert count but not
the same. The features in this situation are Kalyoncu's (2025) formulas and their components
(`kalyoncu_*`).
