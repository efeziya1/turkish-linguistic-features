# Tutorial — from nothing to your first measurement

This page is a single path: it starts at installation and ends with a
readable table of numbers. No branching; the options live in
[How-to](how-to/index.md).

Time: about 15 minutes, most of it downloading models.

## 1. Install the library

The package is not on PyPI yet. Clone the repository and install it in
editable mode:

```bash
git clone https://github.com/efeziya1/turkish-linguistic-features.git
cd turkish-linguistic-features
pip install -e .
```

`-e` (editable) means the installed package tracks the repository, so
`git pull` is enough to update it.

## 2. Install the language data

`pip install` sets up the Python dependencies but not the language data.
Install the data for the language(s) you use, once:

```bash
# Turkish — 156 MB, not in spaCy's registry, install the wheel directly
pip install https://huggingface.co/turkish-nlp-suite/tr_core_news_md/resolve/main/tr_core_news_md-1.0-py3-none-any.whl

# English — two pieces: the spaCy model (12 MB) and the CMU pronouncing
# dictionary for syllable counts (1 MB)
python -m spacy download en_core_web_sm
python -m nltk.downloader cmudict
```

!!! note "Two things about the Turkish model that look like bugs"

    **The wheel disagrees with itself.** The filename says version `1.0`,
    the metadata inside says `3.4.2`. `pip` accepts it and installs it;
    stricter installers reject it as a malformed wheel.

    **Loading it prints a `W094` warning** about an under-constrained spaCy
    version requirement. That is the model's own `meta.json` talking. It is
    harmless and there is nothing to fix on either side.

Check the install:

```bash
python -c "import spacy; spacy.load('en_core_web_sm'); print('ok')"
```

## 3. Your first measurement

```python
import turkish_linguistic_features as tlf

text = (
    "Colorless green ideas sleep furiously. Chomsky built this sentence to "
    "show that a grammatical sentence can still be meaningless. This library, "
    "too, measures form, not meaning."
)

oz = tlf.analyze(text, lang="en")
print(len(oz))
```

```text
181
```

The first sentence is from Chomsky's *Syntactic Structures* (1957).

`lang` defaults to `"tr"`. Leave it out and English text is analysed with the
Turkish model and the Turkish feature set, so always pass `lang="en"`.

`analyze` returns a **flat dictionary**: keys are feature names, values are
numbers. No nesting, no classes, no `pandas` requirement.

## 4. Read the output

Looking at 181 numbers at once is pointless. Look at a few:

```python
for k in ("ttr", "word_len_mean", "flesch_reading_ease",
          "flesch_kincaid_grade", "ari", "coleman_liau"):
    print(f"{k:22s} {oz[k]}")
```

```text
ttr                    0.923077
word_len_mean          5.5385
flesch_reading_ease    51.6153
flesch_kincaid_grade   8.2131
ari                    10.0764
coleman_liau           13.3508
```

What these say:

| Key | Value | Reading |
|---|---|---|
| `ttr` | 0.923 | Type-token ratio. 24 of the 26 words are distinct; only `this` and `sentence` occur twice. A short text stays close to 1; the ratio falls as a text grows. |
| `word_len_mean` | 5.54 | 5.54 characters per word. |
| `flesch_reading_ease` | 51.6 | Ordinary prose falls between 0 and 100, but that is not a hard limit; 50–60 is "fairly difficult", roughly high-school level. |
| `flesch_kincaid_grade` | 8.21 | US grade level. |
| `ari` | 10.08 | Automated Readability Index, also a grade level. |
| `coleman_liau` | 13.35 | Another grade level, from letters and sentences per 100 words. |

!!! note "Three grade levels, three different numbers"

    8.21, 10.08 and 13.35 all claim to be a grade level for the same text.
    That is not a bug — readability formulas disagree by design, because
    they were fitted on different corpora with different criteria. Report
    which formula you used, and do not average them.

## 5. Why are some values `nan`?

```python
print(oz["mattr"])
```

```text
nan
```

The text has 26 words; `mattr` requires at least 100. The library does not
invent a number from insufficient data — it returns `nan`.

How much of the output is affected in a very short text:

```python
short = tlf.analyze("A short sentence.", lang="en")
nans = [k for k, v in short.items() if isinstance(v, float) and v != v]
print(len(short), len(nans))
```

```text
181 34
```

In a three-word text, **34 of 181** features return `nan`. That is honesty,
not failure. See **[What NaN means](explanation/nan.md)**.

## 6. See where a feature comes from

If you are going to put a number in your own work, you need to know its
source:

```python
d = tlf.describe_feature("mattr")
print(d["citation"])
print(d["references"][0])
```

```text
Covington & McFall (2010); default window 50 — C&M recommend a window of 500; 50 is used here so that texts of 100+ words can be measured (mattr needs 2 × window)
Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot: The moving-average type–token ratio (MATTR). Journal of Quantitative Linguistics, 17(2), 94–100. DOI 10.1080/09296171003643098
```

`references` is what you copy into your bibliography. `citation` is the
short pointer, and it **also tells you what we do not know** — in this case
it says outright that the default window size does not come from the source. The
dictionary's other fields (formula, scale, minimum data…): [Find a feature's
source](how-to/citations.md).

## 7. Turn a corpus into a table

One text is rarely enough. Lay your directory out like this:

```text
corpus/
  author_a/
    text1.txt
    text2.txt
  author_b/
    text3.txt
```

```python
rows = tlf.analyze_corpus("corpus/", lang="en")
tlf.save_csv(rows, "features.csv")
```

Each file becomes one row. The table has your features plus three identity
columns:

```text
label=author_a  source=text1     segment_id=0
label=author_a  source=text2     segment_id=0
label=author_b  source=text3     segment_id=0
```

`label` is the folder name (in most studies the author or the class),
`source` is the file name. The CSV opens directly in `pandas`, R or SPSS.

## Done — what next

You now have a working install and a feature table. From here:

- A specific job to do → **[How-to](how-to/index.md)**
- Texts of very different lengths →
  **[Split a text into segments](how-to/segmenting.md)**
- Wondering how far to trust the numbers →
  **[The verification system](explanation/verification.md)** and
  **[Limitations](explanation/limitations.md)**
