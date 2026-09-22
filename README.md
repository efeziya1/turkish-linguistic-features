# turkish-linguistic-features

A comprehensive toolkit for extracting quantitative linguistic features from
Turkish and English texts.

**Status: early development (0.1.0).** The public API is not usable yet — this
repository is currently being built up task by task. See `plan/from-scratch/`.

## What it does

Given a text, the library produces a flat `dict` of named numeric features:
lexical richness, phonetics, Turkish morphology (Zeyrek), syntax, readability and punctuation.

## Install

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

## Kullanım

```python
import turkish_linguistic_features as tlf

sonuc  = tlf.analyze("Bir metin.", lang="tr")          # 207 öznitelik (TR) / 181 (EN)
sonuc  = tlf.analyze(metin, groups=["readability"])    # yalnız bir grup
korpus = tlf.load_corpus("korpus/", segment_size=1000) # klasör/CSV → kayıtlar
parca  = tlf.segment_text(uzun_metin, size=1000)       # tek metni parçala
bilgi  = tlf.describe_feature("mtld")                  # anahtar ne ölçüyor, kaynağı ne
ayar   = tlf.FeatureParams(mattr_window=100)           # metrik sabitleri

try:
    tlf.analyze(metin)
except tlf.ModelNotFoundError as e:
    print(e)                       # mesaj kurulum komutunu içerir
except tlf.LinguisticFeaturesError:
    ...                            # kütüphanenin her hatasının kökü
```

`MissingDependencyWarning` opsiyonel bir paket eksik olduğunda verilir;
`warnings.simplefilter("error", tlf.MissingDependencyWarning)` ile hataya
çevrilebilir, `tlf.analyze(metin, warn=False)` ile susturulabilir.

## License

MIT — see `LICENSE`.
