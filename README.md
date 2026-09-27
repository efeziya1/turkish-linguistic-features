# turkish-linguistic-features

Extracts **208 quantitative linguistic features** from Turkish text and 182
from English. Every feature is tied to a source in the literature, and the
[verification report](docs/verification-report.md) shows which ones match the
number that source published.

**Status: early development (0.1.0).** Not on PyPI yet.

```python
import turkish_linguistic_features as tlf

oz = tlf.analyze("Dil, insanın düşüncesini taşıyan en eski araçtır.", lang="tr")
oz["avg_word_length"]     # 5.8571
oz["atesman"]             # 77.2479  (Ateşman 1997 readability)
```

## Documentation

**→ [Full documentation](docs/index.md)** — tutorial, how-to guides, feature
reference and limitations, in **Turkish and English**.

Build and read it locally:

```bash
pip install mkdocs-material
mkdocs serve          # http://127.0.0.1:8000
```

Or build the static site and open `site/index.html`:

```bash
mkdocs build
```

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

### Language models

Models are **not** installed automatically — a library that writes to your
environment at import time is one you cannot trust in CI or in a read-only
container. Install them yourself, once:

```bash
# English — 12 MB
python -m spacy download en_core_web_sm

# Turkish — 156 MB, not in spaCy's registry, install the wheel directly
pip install https://huggingface.co/turkish-nlp-suite/tr_core_news_md/resolve/main/tr_core_news_md-1.0-py3-none-any.whl
```

Verified with spaCy 3.8.16, `en_core_web_sm` 3.8.0 and `tr_core_news_md` 1.0.

Two things about the Turkish model look like bugs and are not: its wheel
says `1.0` in the filename and `3.4.2` in the metadata, and loading it prints
a harmless `W094` warning. Details in the
[tutorial](docs/en/getting-started.md).

## The whole API

Ten public names:

```python
tlf.analyze(text, lang="tr")                     # 208 features (TR) / 182 (EN)
tlf.analyze(text, groups=["readability"])        # one group only
tlf.analyze_corpus("corpus/")                    # one row per file
tlf.analyze_corpus("corpus/", segment_size=1000) # or split into chunks
tlf.save_csv(rows, "features.csv")               # write them out
tlf.segment_text(long_text, size=1000)           # split a single text
tlf.describe_feature("mtld")                     # what a key measures, and its source
tlf.FeatureParams(mattr_window=100)              # metric constants

# tlf.LinguisticFeaturesError  tlf.ModelNotFoundError
# tlf.MissingDependencyWarning  tlf.ParagraphStructureWarning
```

Full signatures: [docs/reference/api.md](docs/reference/api.md).

## Development

```bash
pip install -r requirements.txt
pytest                          # 727 tests; pytest -m "" adds 1 slow one
ruff check .
python scripts/dogrulama_raporu.py   # regenerate the verification reports
python scripts/basvuru_uret.py       # regenerate the feature reference
```

## License

MIT — see `LICENSE`.
