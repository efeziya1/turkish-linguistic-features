# turkish-linguistic-features

A comprehensive toolkit for extracting quantitative linguistic features from
Turkish and English texts.

**Status: early development (0.1.0).** The eight public names are implemented
and tested; the package is not on PyPI yet — publishing is the last open task.
See `plan/from-scratch/`.

## What it does

Given a text, the library produces a flat `dict` of named numeric features:
lexical richness, phonetics, Turkish morphology (Zeyrek), syntax, readability and punctuation.

## Install

Not on PyPI yet. From a clone:

```bash
pip install -e .
```

Once published:

```bash
pip install turkish-linguistic-features
```

### Language models

Models are **not** installed automatically and the library will not install
them for you — a library that writes to your environment at import time is a
library you cannot trust in CI or in a read-only container. Install them
yourself, once:

```bash
# English
python -m spacy download en_core_web_sm          # 3.8.0

# Turkish — not in spaCy's registry, install the wheel directly
pip install https://huggingface.co/turkish-nlp-suite/tr_core_news_md/resolve/main/tr_core_news_md-1.0-py3-none-any.whl
```

Verified with spaCy 3.8.16, `en_core_web_sm` 3.8.0 and `tr_core_news_md` 1.0
(whose own metadata reports 3.4.2 — see below).

**Two things about the Turkish model that will look like bugs and are not.**

Its wheel disagrees with itself: the filename says version 1.0, the metadata
inside says 3.4.2. `pip` accepts this and installs it; stricter installers
refuse it as a malformed wheel.

Loading it prints a `W094` warning about an under-constrained spaCy version
requirement. That is the model's own `meta.json` talking, it is harmless, and
there is nothing to fix on either side.

The Turkish model is ~156 MB, the English one ~12 MB.

## Usage

```python
import turkish_linguistic_features as tlf

result = tlf.analyze("Bir metin.", lang="tr")          # 208 features (TR) / 182 (EN)
result = tlf.analyze(text, groups=["readability"])     # one group only
corpus = tlf.load_corpus("corpus/", segment_size=1000) # folder/CSV → records
chunks = tlf.segment_text(long_text, size=1000)        # split a single text
info   = tlf.describe_feature("mtld")                  # what a key measures, and its source
params = tlf.FeatureParams(mattr_window=100)           # metric constants

try:
    tlf.analyze(text)
except tlf.ModelNotFoundError as e:
    print(e)                       # the message includes the install command
except tlf.LinguisticFeaturesError:
    ...                            # the root of every error this library raises
```

`MissingDependencyWarning` is emitted when an optional package is missing. Turn
it into an error with `warnings.simplefilter("error", tlf.MissingDependencyWarning)`,
or silence it with `tlf.analyze(text, warn=False)`.

## License

MIT — see `LICENSE`.
