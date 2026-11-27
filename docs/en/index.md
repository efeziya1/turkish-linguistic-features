# English documentation

This section has four parts. Which one you want depends on what you are trying to do.

| Purpose | Page |
|---|---|
| Using the tool for the first time, from start to finish | **[Tutorial](getting-started.md)** |
| Doing a specific job | **[How-to](how-to/index.md)** |
| Finding out what a feature is | **[Reference](../reference/index.md)** |
| Understanding why the tool works this way | **[Explanation](explanation/index.md)** |
| Starting from a working script | **[Example scripts](https://github.com/efeziya1/turkish-linguistic-features/tree/main/examples)** (ten scripts, each answering one question; comments in Turkish) |

If you are not sure, start with the tutorial: it takes you from installation to your first
table.

## At a glance

```python
import turkish_linguistic_features as tlf

oz = tlf.analyze("Colorless green ideas sleep furiously.", lang="en")
len(oz)               # 187
oz["word_len_mean"]   # 6.6
```

The library has **twelve** public names. That is all of them:

| Name | What it does |
|---|---|
| `analyze` | Extracts every feature from one text |
| `analyze_corpus` | Runs `analyze` on every text in a folder |
| `ngram_matches` | Shows what a given sequence of words, lemmas or POS tags (such as `["GO", "home"]` or `["ADJ", "NOUN"]`) matched in a text, with counts |
| `text_units` | Gives the words, lemmas, POS tags, syllable counts and sentences of a text as separate lists; these are the units the features count |
| `segment_text` | Splits a text into fixed-size segments |
| `save_csv` | Writes the resulting rows to CSV |
| `describe_feature` | Gives a feature's definition, formula, scale, the minimum data it needs, and its citation |
| `FeatureParams` | Holds settings such as thresholds and window sizes |
| `LinguisticFeaturesError` | The common type of the library's errors |
| `ModelNotFoundError` | Raised when required language data is missing: a spaCy model, or NLTK's `cmudict` for English syllable counts |
| `MissingDependencyWarning` | Warned when an optional package is missing |
| `ParagraphStructureWarning` | Warned when a text over 1000 words has no paragraph boundary |

Every feature, including the phrases counted with `custom_ngrams`, comes out
of `analyze`.

## Terms

The documentation uses fixed terminology; the glossary also gives each term's Turkish
equivalent as used in the Turkish pages. All terms in one place:
**[glossary](glossary.md)**.
