# Public API

Ten names. Everything else in the package is private and may change
without notice.

Every function that takes `lang` defaults to `"tr"`. For English text,
pass `lang="en"` explicitly.

```python
import turkish_linguistic_features as tlf

tlf.__all__
```

```text
['analyze', 'analyze_corpus', 'FeatureParams', 'segment_text', 'save_csv',
 'describe_feature', 'LinguisticFeaturesError', 'ModelNotFoundError',
 'MissingDependencyWarning', 'ParagraphStructureWarning']
```

---

## `analyze`

```python
analyze(
    text: str,
    lang: str = "tr",
    model: str | None = None,
    groups: list[str] | None = None,
    params: FeatureParams | None = None,
    custom_ngrams: list[list[str]] | None = None,
    show_progress: bool = False,
    warn: bool = True,
) -> dict[str, float]
```

Extracts every feature from one text. Returns a flat `dict`; values are
`float`, and a value that could not be computed is `nan`.

| Parameter | Meaning |
|---|---|
| `text` | The text to analyse |
| `lang` | `"tr"` (default) or `"en"`. Anything else raises `ValueError`. Changes the feature set (208 vs 182) |
| `model` | spaCy model name. Defaults: `tr_core_news_md`, `en_core_web_sm` |
| `groups` | Restrict to these groups; `None` means all |
| `params` | Thresholds and window sizes. **`None` selects language-calibrated values** |
| `custom_ngrams` | Token sequences to count; each becomes an `ng_*` key |
| `show_progress` | Print progress to stdout |
| `warn` | `False` silences `MissingDependencyWarning` and `ParagraphStructureWarning`; does not change the result |

Raises `ModelNotFoundError` if the spaCy model is not installed, or — for
English, when `phonetic` or `readability` is requested — if NLTK's `cmudict`
corpus is not. The check runs before any model is loaded.

See: [TR](../tr/nasil/tek-metin.md) · [EN](../en/how-to/single-text.md)

---

## `analyze_corpus`

```python
analyze_corpus(
    path: str | Path,
    lang: str = "tr",
    segment_size: int | None = None,
    *,
    min_fill: float = 1.0,
    unit: str = "word",
    model: str | None = None,
    groups: list[str] | None = None,
    params: FeatureParams | None = None,
    custom_ngrams: list[list[str]] | None = None,
    show_progress: bool = False,
    warn: bool = True,
) -> list[dict[str, object]]
```

Runs `analyze` over every file in a one-level directory tree. Each row
carries `label` (folder name), `source` (file stem) and `segment_id`
alongside the features.

`segment_size` applies **per file**, not across the corpus. Leave it
`None` to analyse each file whole.

Files must be UTF-8 (a leading BOM is ignored). Otherwise
`LinguisticFeaturesError` is raised before any analysis, naming every file
that could not be decoded.

See: [TR](../tr/nasil/korpus.md) · [EN](../en/how-to/corpus.md)

---

## `segment_text`

```python
segment_text(
    text: str,
    size: int = 1000,
    min_fill: float = 1.0,
    unit: str = "word",
    lang: str = "tr",
) -> list[str]
```

Splits a text into fixed-size pieces. `size` counts **spaCy tokens**
(`unit="word"`) or raw characters (`unit="char"`). A trailing piece shorter
than `min_fill × size` is discarded.

Returned pieces are slices of the raw text, not re-joined tokens.

Pass the text's language: tokenization rules differ (apostrophes,
abbreviations), so the same English text gives different piece boundaries
with the default `lang="tr"`.

See: [TR](../tr/nasil/segmentleme.md) · [EN](../en/how-to/segmenting.md)

---

## `save_csv`

```python
save_csv(
    records: list[dict[str, object]],
    output_path: str | Path,
) -> None
```

Writes rows to CSV, UTF-8. The column order follows the first record's key
order, so `label`, `source` and `segment_id` come first.

---

## `describe_feature`

```python
describe_feature(key: str) -> dict
```

Returns everything known about one key:

```text
key · group · group_label · description · formula · scale ·
inputs · params · requires · citation · references
```

`citation` is the short pointer; `references` holds the full bibliographic
records to copy into a bibliography. `citation is None` means the key is
not a named measure from the literature.

Dynamic keys (`char_a`, `ng_*`) are accepted; for them `formula` and
`requires` are stated at the group level.

See: [TR](../tr/nasil/kunye.md) · [EN](../en/how-to/citations.md)

---

## `FeatureParams`

A frozen-style dataclass holding thresholds, window sizes and sample
counts. Nineteen fields; the full table is in
[TR](../tr/nasil/parametreler.md) · [EN](../en/how-to/parameters.md).

!!! warning

    Passing any `FeatureParams` switches off the language-specific
    calibration of `short_sent_threshold` and `long_sent_threshold`
    (TR 4/18, EN 7/39) and falls back to the dataclass defaults of 5/30.
    Carry the calibrated values over by hand if you need them.

---

## Exceptions and warnings

| Name | When |
|---|---|
| `LinguisticFeaturesError` | Base class for everything the library raises |
| `ModelNotFoundError` | Required language data is not installed: a spaCy model, or NLTK's `cmudict` for English syllable counts. The message contains the install command |
| `MissingDependencyWarning` | An optional package (`pandas`, `wordfreq`) is missing; the affected features return `nan` |
| `ParagraphStructureWarning` | A text over 1000 words has no blank-line paragraph boundary; `para_*` features describe the whole text as one paragraph |

Catching `LinguisticFeaturesError` catches every error the library raises
on purpose. It does not catch errors from spaCy or Zeyrek.
