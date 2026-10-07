# Find a feature's source

If you are going to use a number in your own work, you have to say where it
came from. The library hands you that.

## `describe_feature`

```python
import json
import turkish_linguistic_features as tlf

print(json.dumps(tlf.describe_feature("mattr"), indent=2))
```

```json
{
  "key": "mattr",
  "group": "lexical",
  "group_label": "Lexical richness & frequency",
  "description": "moving-average TTR",
  "formula": "mean TTR of every sliding window of mattr_window words",
  "scale": "ratio_0_1",
  "inputs": ["surface_tokens", "lemma_tokens", "pos_data"],
  "params": ["mattr_window"],
  "requires": "at least 100 words (2 x mattr_window)",
  "citation": "Covington & McFall (2010); default window 50 — C&M recommend a window of 500; 50 is used here so that texts of 100+ words can be measured (mattr needs 2 × window)",
  "references": [
    "Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot: The moving-average type–token ratio (MATTR). Journal of Quantitative Linguistics, 17(2), 94–100. DOI 10.1080/09296171003643098"
  ],
  "definitions": {
    "word": {"name": "space_unit", "source": "tlf", "description": "Whitespace-separated piece of the raw text with edge punctuation stripped, containing a letter or digit; the library's default word."},
    "type": {"name": "lowercase_surface", "source": "tlf", "description": "The word string lowercased by language (Turkish I→ı, İ→i); inflected forms are separate types."}
  }
}
```

## What each field is for

| Field | Use |
|---|---|
| `description` | One-sentence definition |
| `formula` | The computation itself, in words |
| `scale` | `ratio_0_1`, `score`, `count`… — set your plot axis by this |
| `inputs` | Which preprocessing step it needs |
| `params` | Which `FeatureParams` field affects it |
| `requires` | The minimum data needed to produce a number; below it, `nan` |
| `citation` | **Short pointer** — the parenthetical in your methods section |
| `references` | **Full bibliographic record** — what goes in your bibliography |
| `definitions` | What the terms in `formula` mean and where the definition comes from: for each term `{"name", "source" (who defines the rule: tlf, spacy, zeyrek, textstat, wordfreq), "description" (one sentence: how it is counted)}`; only the terms that formula uses; `describe_feature(key, lang="tr")` picks the language for terms that differ by language (`syllable`) |

## The citation also tells you what we do not know

In the example above the citation says:

> default window 50 — C&M recommend a window of 500; 50 is used here so
> that texts of 100+ words can be measured (mattr needs 2 × window)

That is: the method is Covington & McFall's, **but the default window size
is not theirs.** Being able to read that distinction off the citation is
deliberate. Presenting a number as if it rested on a source, when it does
not, is worse than giving no source at all.

Other forms of the same pattern:

- `"Herdan (1960/1964), as cited in Tweedie & Baayen (1998) p.327, eq. (5)"`
  — **the primary source could not be obtained**; the formula was taken
  from the citing work. **14 of 148** citations are like this, and all of
  them carry `as cited in`.
- `"McLaughlin (1969) p.641; polysyllabic = 3+ syllables — the ratio form
  of SMOG's input, not the source's own measure"` — derived from the
  source, but not a measure the source itself defines.

## Features without a source

```python
tlf.describe_feature("punc_,_ratio")
```

```json
{
  "key": "punc_,_ratio",
  "group": "punctuation",
  "description": "comma marks per word",
  "formula": "marks / words",
  "citation": null,
  "references": []
}
```

A `citation` of `None` means the key is **not a named measure from the
literature**; it is a plain definition: `punc_,_ratio` ("commas / words"),
`char_a` ("share of the letter a"), `avg_sent_len_word` ("words per
sentence"). Keys that count the categories of an external tag scheme do
have a citation, pointing at the scheme (`morph_case_loc` → UD;
`case_loc_ratio` → Zeyrek).

**43 of the 205** Turkish keys have no citation: 29 are the letter-frequency
vector (one key per letter of the Turkish alphabet), 8 are punctuation and
capitalisation ratios, and 6 are other plain definitions such as the lemma
count or sentence-length skewness.

## Building a bibliography for your methods section

```python
used = ["mattr", "flesch_reading_ease", "avg_sent_len_word"]

refs = set()
for k in used:
    refs.update(tlf.describe_feature(k)["references"])

for r in sorted(refs):
    print(r)
```

This gives you the bibliography for the features **you actually used**, not
all 56 works.

## Does the number actually match?

The citation tells you the source; it does not tell you the number
**agrees**. There is a separate document for that:

- **[Verification report](../../verification-report.md)** — for each
  feature, a comparison against the number its source published.
- How to read it: **[The verification system](../explanation/verification.md)**.
