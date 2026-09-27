# English documentation

This section has four parts. Which one you want depends on what you are
trying to do right now.

| What you want | Where to go |
|---|---|
| I have never used this, walk me through it | **[Tutorial](getting-started.md)** |
| I need to get a specific job done | **[How-to](how-to/index.md)** |
| I am looking up what a feature is | **[Reference](../reference/index.md)** |
| I want to understand why it works this way | **[Explanation](explanation/index.md)** |

If you are not sure, start with the tutorial: it takes you from installation
to your first table.

## At a glance

```python
import turkish_linguistic_features as tlf

oz = tlf.analyze("Language is the oldest instrument that carries thought.",
                 lang="en")
len(oz)                   # 182
oz["avg_word_length"]     # 5.875
```

The library has **ten** public names. That is all of them:

| Name | What it does |
|---|---|
| `analyze` | Extracts every feature from one text |
| `analyze_corpus` | Runs `analyze` on every text in a folder |
| `segment_text` | Splits a text into fixed-size segments |
| `save_csv` | Writes the resulting rows to CSV |
| `describe_feature` | Gives a feature's definition and source |
| `FeatureParams` | The settings object holding thresholds and windows |
| `LinguisticFeaturesError` | Base class for every error the library raises |
| `ModelNotFoundError` | Raised when a spaCy model is missing |
| `MissingDependencyWarning` | Warned when an optional package is missing |
| `ParagraphStructureWarning` | Warned when a text over 1000 words has no paragraph boundary |

Ten names, 182 features for English (208 for Turkish). You never need to learn a new function to get
more features — they all come out of `analyze`.

## Terms

The documentation uses fixed terminology. If a word is unclear:
**[glossary](glossary.md)**.
