# Export a corpus to CSV

## Directory layout

`analyze_corpus` recognises three layouts on its own. Every row carries a
`label` and a `source`.

**1. Subfolders — the folder name is the label:**

```text
corpus/
  author_a/
    text1.txt       → label "author_a", source "text1"
    text2.txt
  author_b/
    text3.txt
```

**2. `Label_Title.txt` at the root — everything up to the first underscore
is the label:**

```text
corpus/
  Novel_Barren.txt    → label "Novel", source "Barren"
  notes.txt           → label "" (no underscore), source "notes"
```

Note: in a name like `text_1.txt` the first part also becomes the label (label `"text"`,
source `"1"`). The two layouts can coexist in one folder.

**3. A single CSV or TSV file** — `analyze_corpus("corpus.csv")`. Each row is one text. The
column headers are `text`, `label` and `source`; the Turkish ones are accepted too
(`metin`, `etiket`, `kaynak`). Only the text column is required; without a source column the
file name is used. A `.tsv` file is read as tab-separated.

??? note "All accepted headers"

    | Field | Headers (the first match is used) |
    |---|---|
    | text | `text`, `Text`, `metin`, `Metin`, `METIN`, `content` |
    | label | `label`, `Label`, `etiket`, `Etiket`, `ETIKET`, `author`, `Author`, `yazar`, `Yazar`, `kategori`, `category` |
    | source | `source`, `Source`, `kaynak`, `Kaynak`, `başlık`, `title`, `book`, `file` |

The label does not have to be an author: period, genre, grade level, experimental arm,
whatever you are measuring.

Files must be **UTF-8**; if any is not, you get a list of all of them before the analysis
starts. If an error occurs while a text is analysed, the run stops and the message says
which file it stopped at.

## Two calls

```python
import turkish_linguistic_features as tlf

rows = tlf.analyze_corpus("corpus/", lang="tr")
tlf.save_csv(rows, "features.csv")
```

Where the file is saved: [Tutorial, step 7](../getting-started.md#7-turn-a-corpus-into-a-table).

## What comes out

One row per file: 3 rows, 220 columns. 220 columns = 217 features plus three identity
columns:

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
label,source,segment_id,lemma_count,word_count,word_len_mean,entropy,yu...
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

For example, in a folder `one_file/` holding a single 648-word file:

```python
whole    = tlf.analyze_corpus("one_file/", lang="tr")
segments = tlf.analyze_corpus("one_file/", lang="tr", segment_size=200)
print(len(whole), len(segments))
```

Output:

```text
1 3
```

648 ÷ 200 = 3 full segments; the remaining 48 words are dropped under the
default `min_fill=1.0`.

A working example that compares sentence-length distributions across labels:
[`examples/05_cumle_ritmi.py`](https://github.com/efeziya1/turkish-linguistic-features/blob/main/examples/05_cumle_ritmi.py).

!!! note "Segmenting is per file, not across the corpus"

    `segment_size=1000` splits **each file separately** into 1000-word
    chunks. It does not concatenate the corpus and cut every 1000 words.
    So every file leaves a remainder shorter than `segment_size`, and with the
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

`groups`, `params`, `model`, `custom_ngrams` and `warn` mean the same as in
`analyze` and apply to every segment. `custom_ngrams` counts are per segment.
