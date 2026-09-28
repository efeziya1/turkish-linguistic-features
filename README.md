# turkish-linguistic-features

[![CI](https://github.com/efeziya1/turkish-linguistic-features/actions/workflows/ci.yml/badge.svg)](https://github.com/efeziya1/turkish-linguistic-features/actions/workflows/ci.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23009540.svg)](https://doi.org/10.5281/zenodo.23009540)

Extracts **208 quantitative linguistic features** from Turkish text and 180
from English. Every feature has its formula written out; 141 of the Turkish
features cite a source in the literature, the rest are plain definitions
(such as a letter's share of the text). The
[verification report](docs/verification-report.md) shows which ones have been
checked against a number their source published.

**Status: early development (0.x).** Not on PyPI yet. Changes: [CHANGELOG](CHANGELOG.md).

```python
import turkish_linguistic_features as tlf

oz = tlf.analyze("Dil, insanın düşüncesini taşıyan en eski araçtır.", lang="tr")
oz["avg_word_length"]     # 5.8571
oz["atesman"]             # 77.2479  (Ateşman 1997 readability)
```

## Documentation

**→ [Full documentation](docs/index.md)** — tutorial, how-to guides, feature
reference and limitations, in **Turkish and English**.

| | |
|---|---|
| Türkçe | [docs/tr/](docs/tr/index.md) |
| English | [docs/en/](docs/en/index.md) |
| Feature reference | [docs/reference/features.md](docs/reference/features.md) |
| Verification report | [TR](docs/dogrulama-raporu.md) · [EN](docs/verification-report.md) |

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

Ten public names:

```python
tlf.analyze(text, lang="tr")                     # 208 features (TR) / 180 (EN)
tlf.analyze(text, groups=["readability"])        # one group only
tlf.analyze_corpus("corpus/")                    # one row per file
tlf.analyze_corpus("corpus/", segment_size=1000) # or split into chunks
tlf.save_csv(rows, "features.csv")               # write them out
tlf.segment_text(text, size=1000, lang="tr")     # split a single text
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
python scripts/dogrulama_raporu.py   # regenerate the verification reports
python scripts/basvuru_uret.py       # regenerate the feature reference
mkdocs serve                         # preview the docs site at http://127.0.0.1:8000
```

## License

MIT — see `LICENSE`.
