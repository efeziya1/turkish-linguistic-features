# Concepts

## Feature

A **feature** is a single number extracted from a text. `ttr`,
`word_len_mean`, `atesman`: each is one feature. Names are lowercase, with words joined
by underscores.

By the kind of source they rest on, the 217 Turkish features fall into five types:

| Type | Count | What | Example |
|---|---:|---|---|
| **Literature measure** | 136 | A measure proposed in the literature; it has a citation | `mattr`, `mtld`, `atesman` |
| **Tag ratio** | 66 | The share of a tag that spaCy or Akana gives to words; the citation points at the scheme that defines the tag, not at a measure | `pos_noun_ratio` (Universal Dependencies), `akana_case_loc_ratio` (Akana) |
| **Plain definition** | 11 | Not based on a named measure in the literature; no citation | `question_sent_ratio`: the share of sentences ending in a question mark |
| **Tool-specific** | 2 | The formula comes from the literature; what it is applied to is this tool's decision | `sent_len_entropy`: Shannon entropy applied to sentence lengths |
| **Calibrated** | 2 | The threshold comes from this tool's corpus measurement | `short_sent_ratio`, `long_sent_ratio` |

Of 217 keys, 206 have a citation and 11 do not. The type also decides whether a feature
can be checked against a worked example its source published
([The verification system](verification.md)).

The tool does not give only the result of a readability formula; it also gives the measures
that go into the formula, such as mean sentence length and syllables per word, as separate
features. If you want to build a new formula, you can choose and test candidate variables
from these measures and the tool's other features.

## Key names

A name is built so that it says what the feature measures:

| Name | Meaning | Example |
|---|---|---|
| `…_ratio` | A share between 0 and 1 | `hapax_ratio`, `pos_noun_ratio` |
| `…_mean`, `…_median` | Mean, median | `sent_len_mean`, `sent_len_median` |
| `…_count` | A count | `word_count`, `sent_count`, `lemma_count` |
| The name in the literature | An established measure; no `_ratio` | `ttr`, `mattr`, `yule_k`, `posddev` |

The morphological features come from two analysers. Those from spaCy's Universal
Dependencies tags have no prefix (`case_loc_ratio`); those from Akana start with `akana_`
(`akana_case_loc_ratio`). The two do not give the same number:
`case_loc_ratio` is the locative's share among words that carry a case tag,
`akana_case_loc_ratio` its share among all analysed words. Akana also draws distinctions
the universal tags do not: the -DI past and the -mIş past are separate
(`akana_tense_past_def_ratio`, `akana_tense_past_nar_ratio`); in spaCy both are
`tense_past_ratio`.

The ten `punct_…_ratio` keys (`punct_comma_ratio`, `punct_dash_ratio` …) are each
mark type's share of all punctuation marks, so together they add up to 1. How much
punctuation a text has is `punct_char_ratio` (punctuation marks / characters).

## Group

Features are organised into 12 groups (13 with the `ngram_*` keys created when
you pass `custom_ngrams`). A group serves both to organise and to select: you can compute
only the groups you need.

```python
oz = tlf.analyze(text, lang="en", groups=["readability", "lexical"])
```

The groups, their contents and their sizes are listed in
[Analyse a single text](../how-to/single-text.md).

## Dynamic keys

Some keys are not written out one by one; they are generated from a
pattern:

- `char_*`: the letter-frequency vector, one key for each of the same 32 letters in both
  languages (the Turkish and English alphabets together: `char_a_ratio`, `char_ç_ratio` …
  `char_z_ratio`)
- `ngram_*`: counters for the word sequences (n-grams) you pass with `custom_ngrams`
  ([how](../how-to/single-text.md#count-your-own-phrases))

If you call `describe_feature("char_a_ratio")`, the `formula` and `requires`
fields are the **group-level** statement, not something specific to that
letter.

## Scale

Every feature has a scale:

| Scale | Meaning | Example |
|---|---|---|
| `ratio_0_1` | A share between 0 and 1 | `ttr`, `mattr` |
| `score` | A formula score with no fixed range | `atesman`, `yule_k`, `mtld` |
| `length` | A mean length in characters, words or sentences | `word_len_mean`, `sent_len_mean` |
| `nats` | Entropy in nats (natural logarithm; every logarithm in the tool is ln) | `entropy`, `punct_entropy` |
| `count` | A count | `lemma_count` |

## Word and sentence

A feature's value depends on how words, sentences and syllables are counted. Features count
words and sentences with the tool's own rules, not with the model's tokens. These are the
**default word** and the **default sentence**; other pages that use these names point here.

### Word

The text is split at whitespace. Punctuation at the edges of each piece is removed
(`. , ; : ! ? …`, quotes, brackets, dashes, `/`, `*`). What is left is a **word if it
contains at least one letter or digit**; otherwise it is not counted.

| Text | Words |
|---|---|
| `He read it.` | `He`, `read`, `it`: the full stop is not part of the word |
| `e-mail`, `it's`, `50%` | one word each: marks inside a word stay |
| `in 1999` | `in`, `1999`: a number is a word |
| `This — is a test ...` | `This`, `is`, `a`, `test`: `—` and `...` on their own are not words |
| `3. kat` · `Sonuç 3.` | Turkish only: `3.` is one word (an ordinal) when a word or a comma follows it; at the end of a sentence it is `3` |
| `came.Then` · `3.köprü` | When the space is left out, two words glued by punctuation are two words: `came`, `Then` · `3.`, `köprü`. Dotted initials (`G.Saray`), addresses (`site.net`), numbers (`1.5`) and a suffix after a quote or apostrophe (`“kampusu!”na`) are not split |

The ordinal rule is Turkish only because Turkish writes ordinals as a digit followed by a dot;
English writes `3rd`, so it needs no such rule.

When counting words, the tool removes punctuation by stripping the marks at the edges of the
word, not by looking at tags. Every feature except the `syntactic` group counts this word.

### Sentence

A sentence ends at:

- **`.` `?` `!` `…`**: always end a sentence. The ellipsis can also be written `...`.
- **Marks in a row** (`?!`, `!!!`) count as one sentence end.
- **`:`**: ends a sentence when a word starting with a capital, a quote, a dash or an
  opening bracket follows. When a lowercase word or a number follows (a list, an
  explanation, `10:30`), it does not.
- **the end of the text**, even without a mark.

In Turkish, the dot after an abbreviation:

- **in an abbreviation written with a capital** (`Dr.`, `Cad.`, `Ltd.`) does not end a
  sentence; these abbreviations lead into the name after them.
- **in an abbreviation written in lowercase** (`vb.`, `dk.`, `km.`) ends a sentence when a
  capital follows, and does not when a lowercase letter follows.
- **in `bkz.`** (*bakınız*, "see") does not end a sentence, even before a capital: the place
  referred to follows it (`bkz. Ek 2`).

In English, an abbreviation written as one unit, such as `Dr.`, does not end a sentence.

| Text | Sentences |
|---|---|
| `He came. He left!` | 2 |
| `What?! I don't know.` | 2 |
| `She said: We leave tomorrow.` | 2: a capital after `:` |
| `He bought three things: bread, milk and cheese.` | 1: lowercase after `:` |
| `The meeting began at 10:30.` | 1 |
| `Dr. Smith arrived.` | 1 |
| `Elma, armut vb. Sonra eve döndük.` | 2: a capital after `vb.` |
| `He came and went` | 1: no mark; the text ends |

The colon has this condition because a colon is not always a sentence boundary. In Turkish
newspaper columns (4,321 articles), the token after 93.9% of colons starts with a capital, a
quote, a dash or an opening bracket; in English columns (1,485 articles) the share is 62.4%.
The condition keeps a colon followed by a lowercase list or explanation from ending a
sentence. The rule is the same in both languages.

A sentence's length is the number of words in it. A sentence made only of a number is a
sentence too: `This is one. 1999! Done.` has 3 sentences. Every feature and `text_units`
count sentences the same way.

In Turkish, a dot after digits is the dot of an ordinal when a word follows it, and does not
end a sentence (`3. kat`). So `Yıl 1999. Bitti.` is one sentence: in writing, `1999. Bitti`
and `2. Dünya Savaşı` have the same form, and the rule cannot tell them apart.

Two kinds of feature do not use this rule:

- some **readability formulas** follow the counting their own source prescribes
  (table below);
- the **syntactic features** (`syntactic`) use spaCy's tokens and the sentences its
  parser finds.

### Counting in the readability formulas

For some readability formulas, the source itself says how words or sentences are counted.
In these formulas the tool follows the source's rule instead of the general one, so the
formula is computed the way its source computed it.

| Formula | Word | Sentence | Source |
|---|---|---|---|
| Çetinkaya-Uzun | Symbols standing alone (`%`, `$`, `+`) are words too | A colon always, and brackets, also end a sentence | Çetinkaya (2010) p.93 |
| Flesch, Flesch-Kincaid | Symbols standing alone are words too | A semicolon also ends a sentence | Kincaid et al. (1975) p.38 |
| ARI | Symbols standing alone are words too | General rule | Kincaid et al. (1975) p.33 |
| Kalyoncu's four formulas and their components | A number counts as the words of its reading: `1968`, "bin dokuz yüz altmış sekiz", is 5 words | General rule | Kalyoncu (2025) p.xiii |

The formulas not in the table (Ateşman, Bezirci-Yılmaz, SMOG, Coleman-Liau, LIX) use the
general rule. Syllables are counted by pronunciation in every formula: `1918`, "bin dokuz
yüz on sekiz", is 7 syllables; `%50` and `TBMM` are 4 each. Details:
[Limitations](limitations.md).

### A word's tags

spaCy splits text by its own rules, so one word can span several tokens: `Ankara-İstanbul`
becomes the tokens `Ankara`, `-` and `İstanbul`. The word is then counted once; its part of
speech, morphological tags and lemma come from the first token inside it that is not
punctuation. A double quote (`"` `“` `”` `«` `»`) is always punctuation here, whatever tag the
model gave it. Turkish lemmas are Akana's dictionary entry, English lemmas spaCy's.

In Turkish, proper nouns are found by Akana's named entity recogniser. Every word the
recogniser calls part of a person, place or organisation name counts as a proper noun
(`PROPN`), whatever tag spaCy gave it; so does every word of a multi-word name such as
`Mustafa Kemal`. The reason is that the spaCy Turkish model often does not tag words like
`Derya` or `Almanya'da` as `PROPN`. The
`syntactic` group reads spaCy's tokens for the dependency parse and is not affected.

### Counting unit of the diversity measures

In the lexical diversity measures, a type is the word's lowercased surface form, so a word
capitalised at the start of a sentence is not a separate type. Turkish is lowercased by the
Turkish rule (I → ı, İ → i); software's default conversion turns `IŞIK` into `işik`, so
this is handled separately.

Because the type rests on the surface form, inflected forms are separate types: `book` and
`books` are two types. This is the tool's design decision. The exceptions are the
lemma-based `*_variation` measures and `lemma_count`. Where the source counts in another unit (`brunet_w`, `herdan_c`,
`yule_k`), the citation says so.

### Content word

A content word is a word tagged `NOUN`, `PROPN`, `VERB`, `ADJ` or `ADV`: a noun, proper
noun, verb, adjective or adverb. Auxiliaries (`AUX`) do not count as verbs. This definition
is used by `lexical_density`, the part-of-speech variation measures, thematic concentration
and the frequency measures.

The definition is Lu's (2012), with one difference: Lu (2012, p.192) counts only the adverbs
derived from adjectives; the tool counts all adverbs, because the part-of-speech tagger does
not tell adverb types apart and that distinction would need a word list or a morpheme-based
rule. QUITA leaves the choice of content words to the researcher (Kubát et al. 2014,
pp.50–51).

`describe_feature(key)["definitions"]` names the rule each feature uses.

## The pipeline

When you call `analyze`, the text goes through four stages:

```text
raw text
   ↓  1. spaCy (tr_core_news_md / en_core_web_sm)
tokens · POS tags · morphological tags · dependency tree · English lemmas
   ↓  2. Akana (Turkish only)
morpheme analysis · Turkish lemmas · proper nouns
   ↓  3. the tool's own rules
word and sentence boundaries; each word takes its tags from its own token
   ↓  4. feature calculators
217 numbers (187 in English)
```

Akana is a Turkish morphological analyser: a port of Zemberek's rules, written in Rust and
called from Python. It needs no other environment such as Java. When a word has several
analyses, Akana's disambiguator picks one: it ranks the analyses by their frequency in
treebanks and corrects the ranking with a few rules that look at nearby words in the
sentence.

**The spaCy model and Akana are part of the result.** If either changes, the features that
depend on it change too. Of the 217 Turkish features, 105 depend on at least one of the two
analysers; the other 112 are computed with the tool's own rules alone. To reproduce a
result, report the versions of the spaCy model and Akana along with the tool's version.
Versions the tool was tested with: Python 3.12, spaCy 3.8.16, `tr_core_news_md` 1.0 (model
version 3.4.2), `en_core_web_sm` 3.8.0, Akana 0.12.0.

## `FeatureParams`

Window sizes, thresholds and sample counts live here. Details:
[Change the thresholds](../how-to/parameters.md).

The sentence thresholds (`short_sent_threshold`, `long_sent_threshold`) are
**measured separately for each language** (TR 4/17, EN 8/32).

## The registry

The registry holds, in one place, each feature's name, what it measures, its formula,
scale, parameters, the minimum data it needs, its citation and the tool's definitions of
the terms in the formula. `describe_feature`, the [reference section](../../reference/index.md)
and the [verification report](../../verification-report.md) read from it, so the
three always agree.

The registry is kept **in English**, so that no translation layer sits between the
definitions and formulas and the sources, most of which are in English.
