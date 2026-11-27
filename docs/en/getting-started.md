# Tutorial — from nothing to a first measurement

This page is a single path: it starts at installation and ends with a
readable table of numbers. No branching; the options live in
[How-to](how-to/index.md).

Time: about 15 minutes, most of it downloading models.

## 1. Install the library

```bash
pip install turkish-linguistic-features
```

## 2. Install the language data

`pip install` sets up the Python dependencies but not the language data.
Install the data for each language you use, once:

```bash
# Turkish — 156 MB, not in spaCy's registry, install the wheel directly
pip install https://huggingface.co/turkish-nlp-suite/tr_core_news_md/resolve/main/tr_core_news_md-1.0-py3-none-any.whl

# English — two pieces: the spaCy model (12 MB) and the CMU pronouncing
# dictionary for syllable counts (1 MB)
python -m spacy download en_core_web_sm
python -m nltk.downloader cmudict

# Optional — for the two wordfreq_* features
pip install "wordfreq>=3.0"
```

Akana (the Turkish morphological analyser) is installed automatically with the tool.

!!! note "The Turkish model"

    Loading the model shows a `W094` warning; it is harmless. The version in the package file's
    name (`1.0`) differs from the one inside it (`3.4.2`); `pip` does not mind.

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
187
```

The first sentence is from Chomsky's *Syntactic Structures* (1957).

`lang` defaults to `"tr"`. Leave it out and English text is analysed with the
Turkish model and the Turkish feature set, so always pass `lang="en"`.

`analyze` returns a **flat dictionary**: keys are feature names, values are
numbers. No nesting, no classes, no `pandas` requirement.

## 4. Read the output

You get a feature's value by its name:

```python
print(oz["ttr"])
print(oz["flesch_reading_ease"])
```

```text
0.923077
51.6153
```

What a few features say:

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
    they were fitted on different corpora with different criteria. Report which formula
    you used, and do not average them.

## 5. Why are some values `nan`?

```python
print(oz["mattr"])
```

```text
nan
```

The text has 26 words; `mattr` requires at least 100. The library does not
invent a number from insufficient data — it returns `nan`.

The shorter the text, the more `nan`: in a three-word text (`A short sentence.`) **35 of
187** features return `nan`. That is not an error. See **[What NaN means](explanation/nan.md)**.

## 6. See where a feature comes from

If you use a number in your own work, you need to know where it comes from:

```python
d = tlf.describe_feature("mattr")
print(d["citation"])
print(d["references"][0])
```

```text
Covington & McFall (2010); default window 50 — C&M recommend a window of 500 (p.97); 50 is used here so that texts of 100+ words can be measured (mattr needs 2 × window)
Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot: The moving-average type–token ratio (MATTR). Journal of Quantitative Linguistics, 17(2), 94–100. DOI 10.1080/09296171003643098
```

`references` is what you copy into your bibliography. `citation` is the short pointer,
and it **also says what is not known** — in this case
it says outright that the default window size does not come from the source. The
other fields `describe_feature` returns (formula, scale, minimum data…): [Find a feature's
source](how-to/citations.md).

## 7. Turn a corpus into a table

One text is rarely enough. Lay out your directory like this:

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

**Where is the file saved?** If you give only a file name (`"features.csv"`), the file is saved in
the folder you run Python from: the folder where you typed `python script.py` in the terminal,
or the notebook's folder in Jupyter. To save it elsewhere, give the full path:
`"C:/Users/yourname/Desktop/features.csv"`. A file with the same name is overwritten.
`"corpus/"` is looked up by the same rule.

Each file becomes one row: 3 rows, 190 columns, that is 187 features plus three identity
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
- Long texts to split →
  **[Split a text into segments](how-to/segmenting.md)**
- How far to trust the numbers →
  **[The verification system](explanation/verification.md)** and
  **[Limitations](explanation/limitations.md)**
