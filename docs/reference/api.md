# Public API

Eleven names. Everything else in the package is private and may change
without notice.

Every function that takes `lang` defaults to `"tr"`. For English text,
pass `lang="en"` explicitly.

```python
import turkish_linguistic_features as tlf

tlf.__all__
```

```text
['analyze', 'analyze_corpus', 'ngram_matches', 'FeatureParams', 'segment_text',
 'save_csv', 'describe_feature', 'LinguisticFeaturesError', 'ModelNotFoundError',
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
| `lang` | `"tr"` (default) or `"en"`. Anything else raises `ValueError`. Changes the feature set (208 vs 181) |
| `model` | spaCy model name. Defaults: `tr_core_news_md`, `en_core_web_sm` |
| `groups` | Restrict to these groups; `None` means all |
| `params` | Thresholds and window sizes. **`None` selects language-calibrated values** |
| `custom_ngrams` | Word sequences to count, one key `ngram_{...}_count` each. An UPPERCASE UD tag (`NOUN`, `VERB` …) in a phrase matches any word with that tag; matches stay inside a sentence. See `ngram_matches` for what matched |
| `show_progress` | Print progress to stdout |
| `warn` | `False` silences `MissingDependencyWarning` and `ParagraphStructureWarning`; does not change the result |

Raises `ModelNotFoundError` if the spaCy model is not installed, or — for
English, when `phonetic` or `readability` is requested — if NLTK's `cmudict`
corpus is not. The check runs before any model is loaded.

See: [TR](../tr/nasil/tek-metin.md) · [EN](../en/how-to/single-text.md)

---

## `ngram_matches`

```python
ngram_matches(
    text: str,
    phrase: list[str],
    lang: str = "tr",
    model: str | None = None,
) -> dict[str, int]
```

What one `custom_ngrams` phrase matched in a text, most frequent first. The
matching is the same as in `analyze`, so the values add up to the phrase's
`ngram_{...}_count`.

```python
tlf.ngram_matches("Kadın geldi. Kadın güldü ve kadın oturdu.", ["kadın", "VERB"])
```

```text
{'kadın geldi': 1, 'kadın güldü': 1, 'kadın oturdu': 1}
```

Sentence and position are not returned. For several texts, add the results up
(`collections.Counter`). The text goes through the spaCy pipeline, as in
`analyze`.

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

Runs `analyze` over every text in a corpus. Three layouts are recognised:
subfolders (`corpus/label/file.txt`), `Label_Title.txt` files at the root
(the part before the first underscore is the label), or a single CSV/TSV
file with a text column. Each row carries `label`, `source` and
`segment_id` alongside the features. Details and accepted CSV headers:
[TR](../tr/nasil/korpus.md) · [EN](../en/how-to/corpus.md).

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

Splits a text into fixed-size pieces. `size` counts **words** — the word
`analyze` counts (`unit="word"`) — or raw characters (`unit="char"`). A trailing piece shorter
than `min_fill × size` is discarded.

Returned pieces are slices of the raw text, not re-joined words.

Pass the text's language; the word rule differs slightly (Turkish ordinals
such as `3.` are one word).

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
describe_feature(key: str, lang: str | None = None) -> dict
```

Returns everything known about one key:

```text
key · group · group_label · description · formula · scale ·
inputs · params · requires · citation · references · definitions
```

`citation` is the short pointer; `references` holds the full bibliographic
records to copy into a bibliography. `citation is None` means the key is
not a named measure from the literature.

`definitions` explains the terms the `formula` uses (`sentence`, `word`, `syllable`,
`letter`, `type`…): for each, `{"name": ..., "source": ..., "description": ...}` — the
rule tlf counts it with, who defines that rule (`tlf`, `spacy`, `zeyrek`,
`textstat`, `wordfreq`) and, in one sentence, how it is counted. A term the formula does not use is absent.
Where the definition differs by language (`syllable`), `describe_feature(key, lang="tr")` returns
that language's entry; without `lang` you get `{"tr": ..., "en": ...}`.

Dynamic keys (`char_a_ratio`, `ngram_*_count`) are accepted; for them `formula` and
`requires` are stated at the group level.

See: [TR](../tr/nasil/kunye.md) · [EN](../en/how-to/citations.md)

---

## `FeatureParams`

A frozen dataclass (`frozen=True`) holding thresholds, window sizes and
sample counts. Eighteen fields; the full table is in
[TR](../tr/nasil/parametreler.md) · [EN](../en/how-to/parameters.md).

!!! note

    `short_sent_threshold` and `long_sent_threshold` default to `None`,
    which means "use the calibrated value for `lang`" (TR 4/17, EN 8/32).
    They are resolved field by field: a field you set wins, a field you leave
    out stays calibrated. Setting an unrelated field such as `mattr_window`
    does not touch the sentence thresholds.

---

## Exceptions and warnings

| Name | When |
|---|---|
| `LinguisticFeaturesError` | Base class for everything the library raises |
| `ModelNotFoundError` | Required language data is not installed: a spaCy model, or NLTK's `cmudict` for English syllable counts. The message contains the install command |
| `MissingDependencyWarning` | The optional `wordfreq` package is missing; the two `wordfreq_*` features return `nan` |
| `ParagraphStructureWarning` | A text over 1000 words has no blank-line paragraph boundary; the two `para_*` features describe the whole text as one paragraph |

Catching `LinguisticFeaturesError` catches every error the library raises
on purpose. It does not catch errors from spaCy or Zeyrek.
