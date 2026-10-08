# turkish-linguistic-features

[![CI](https://github.com/efeziya1/turkish-linguistic-features/actions/workflows/ci.yml/badge.svg)](https://github.com/efeziya1/turkish-linguistic-features/actions/workflows/ci.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23009540.svg)](https://doi.org/10.5281/zenodo.23009540)

Extracts 208 quantitative linguistic features from Turkish text and 181 from
English. Every feature has its formula written out; 197 of the Turkish features
and 170 of the English ones cite a source in the literature, and the rest are
plain definitions (such as the dash's share of punctuation marks). The
[verification report](docs/verification-report.md) shows which ones have been
checked against a number their source published. Documentation:
https://efeziya1.github.io/turkish-linguistic-features/

**Status: early development (0.x).** Not on PyPI yet. Changes: [CHANGELOG](CHANGELOG.md).

```python
import turkish_linguistic_features as tlf

oz = tlf.analyze("Dil, insanın düşüncesini taşıyan en eski araçtır.", lang="tr")
oz["word_len_mean"]   # 5.8571
oz["atesman"]         # 77.2479  (Ateşman 1997 readability)
```

## Documentation

**→ [Full documentation](https://efeziya1.github.io/turkish-linguistic-features/)** — tutorial, how-to
guides, feature reference and limitations, in **Turkish and English**.

| | |
|---|---|
| Türkçe | [tr/](https://efeziya1.github.io/turkish-linguistic-features/tr/) |
| English | [en/](https://efeziya1.github.io/turkish-linguistic-features/en/) |
| Feature reference | [reference/features/](https://efeziya1.github.io/turkish-linguistic-features/reference/features/) |
| Verification report | [TR](https://efeziya1.github.io/turkish-linguistic-features/dogrulama-raporu/) · [EN](https://efeziya1.github.io/turkish-linguistic-features/verification-report/) |

## Install

From a clone:

```bash
git clone https://github.com/efeziya1/turkish-linguistic-features.git
cd turkish-linguistic-features
pip install -e .
```

### Language data

`pip install` sets up the Python dependencies but not the language data.
Install the data for the language(s) you use, once:

```bash
# Turkish — 156 MB. The model is by turkish-nlp-suite and is not in spaCy's
# registry, so install the wheel directly:
pip install https://huggingface.co/turkish-nlp-suite/tr_core_news_md/resolve/main/tr_core_news_md-1.0-py3-none-any.whl

# English — the spaCy model (12 MB) and the CMU Pronouncing Dictionary for
# syllable counts (1 MB):
python -m spacy download en_core_web_sm
python -m nltk.downloader cmudict
```

If something is missing, `analyze()` stops with an error that shows the
command to run.

Verified with spaCy 3.8.16, `en_core_web_sm` 3.8.0 and `tr_core_news_md` 1.0.
The Turkish wheel says `1.0` in its filename but `3.4.2` in its metadata, and
loading it prints a `W094` warning; both are harmless
([details](docs/en/getting-started.md)).

## The whole API

Eleven public names:

```python
tlf.analyze(text, lang="tr")                     # 208 features (TR) / 181 (EN)
tlf.analyze(text, groups=["readability"])        # one group only
tlf.analyze_corpus("corpus/")                    # one row per file
tlf.analyze_corpus("corpus/", segment_size=1000) # or split into chunks
tlf.save_csv(rows, "features.csv")               # write them out
tlf.segment_text(text, segment_size=1000, lang="tr")  # split a single text
tlf.analyze(text, custom_ngrams=[["ADJ", "NOUN"]])  # count your own phrases
tlf.ngram_matches(text, ["ADJ", "NOUN"])         # ...and see what they matched
tlf.describe_feature("mtld")                     # what a key measures, and its source
tlf.FeatureParams(mattr_window=100)              # metric constants

# tlf.LinguisticFeaturesError  tlf.ModelNotFoundError
# tlf.MissingDependencyWarning  tlf.ParagraphStructureWarning
```

Full signatures: [docs/reference/api.md](docs/reference/api.md).

## Development

```bash
pip install -r requirements.txt
pytest                          # pytest -m "" also runs the slow test
ruff check .
python scripts/generate_verification_report.py  # regenerate the verification reports
python scripts/generate_feature_reference.py    # regenerate the feature reference
```

## License

MIT — see `LICENSE`.
