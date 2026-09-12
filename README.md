# turkish-linguistic-features

A comprehensive toolkit for extracting quantitative linguistic features from
Turkish and English text.

**Status: early development (0.1.0).** The public API is not usable yet — this
repository is currently being built up task by task. See `plan/from-scratch/`.

## What it does

Given a text, the library produces a flat `dict` of named numeric features:
lexical richness, phonetics, Turkish morphology (Zeyrek), syntax (spaCy),
readability and punctuation.

## What it does not do

It **measures**; it does not decide. No classifiers, no predictions, no
authorship attribution, no accuracy reporting. Full scope boundary:
`plan/from-scratch/00-ANA-PLAN.md` §0.

## Install

```bash
pip install turkish-linguistic-features
```

Language models are not installed automatically (~50 MB each) and are fetched
on first use.

## License

MIT — see `LICENSE`.
