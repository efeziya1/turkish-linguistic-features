# Export a corpus to CSV

## Directory layout

`analyze_corpus` expects **one level of folders**. The folder name becomes
the label:

```text
corpus/
  author_a/
    text1.txt
    text2.txt
  author_b/
    text3.txt
```

The label does not have to be an author — period, genre, grade level,
experimental arm, whatever you are measuring.

## Two calls

```python
import turkish_linguistic_features as tlf

rows = tlf.analyze_corpus("corpus/", lang="tr")
tlf.save_csv(rows, "features.csv")
```

That is the whole chain.

## What comes out

```text
row count:    3
column count: 211
```

One row per file. 211 columns = 208 features plus three identity columns:

```text
label=author_a  source=text1     segment_id=0  ttr=1.0
label=author_a  source=text2     segment_id=0  ttr=1.0
label=author_b  source=text3     segment_id=0  ttr=1.0
```

| Column | Meaning |
|---|---|
| `label` | Folder name |
| `source` | File name, without the extension |
| `segment_id` | Segment number; always `0` unless you pass `segment_size` |

The CSV header:

```text
label,source,segment_id,n_lemma_count,avg_word_length,word_length_cv,entropy,yule_k,simpso...
```

## Watch progress

For a large corpus:

```python
rows = tlf.analyze_corpus("corpus/", lang="tr", show_progress=True)
```

```text
  [1/3] text1 #0
  [2/3] text2 #0
  [3/3] text3 #0
```

## Split files into segments

```python
rows = tlf.analyze_corpus("corpus/", lang="tr", segment_size=1000)
```

Measured:

```text
without segment_size : 1 row  (one row per file)
segment_size=200     : 3 rows
segment_id values    : [0, 1, 2]
```

!!! danger "Segmenting is per file, not across the corpus"

    `segment_size=1000` splits **each file separately** into 1000-token
    chunks. It does not concatenate the corpus and cut every 1000 tokens.
    So every file leaves a remainder shorter than `size`, and with the
    default `min_fill=1.0` that remainder is **discarded**.

    Why and when to segment →
    [Split a text into segments](segmenting.md).

## Full signature

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

`groups`, `params`, `model` and `warn` mean the same as in `analyze` and
apply to every segment.

## A DataFrame instead of a CSV

`save_csv` writes to disk. To stay in memory, the returned list is already
`pandas`-ready:

```python
import pandas as pd
df = pd.DataFrame(tlf.analyze_corpus("corpus/", lang="tr"))
```

`pandas` is not a required dependency; you install it yourself.
