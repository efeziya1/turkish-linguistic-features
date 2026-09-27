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
  "citation": "Covington & McFall (2010); default window 50 — C&M's own recommendation is 500, 50 was settled on after measurement",
  "references": [
    "Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot: The moving-average type–token ratio (MATTR). Journal of Quantitative Linguistics, 17(2), 94–100. DOI 10.1080/09296171003643098"
  ]
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

## The citation also tells you what we do not know

In the example above the citation says:

> default window 50 — C&M's own recommendation is 500, 50 was settled on
> after measurement

That is: the method is Covington & McFall's, **but the default window size
is not theirs.** Being able to read that distinction off the citation is
deliberate. Presenting a number as if it rested on a source, when it does
not, is worse than giving no source at all.

Other forms of the same pattern:

- `"Herdan (1960/1964), as cited in Tweedie & Baayen (1998) p.327, eq. (5)"`
  — **the primary source could not be obtained**; the formula was taken
  from the citing work. **11 of 145** citations are like this, and all of
  them carry `as cited in`.
- `"McLaughlin (1969) p.641; polysyllabic = 3+ syllables — the ratio form
  of SMOG's input, not the source's own measure"` — derived from the
  source, but not a measure the source itself defines.

There is one more mechanism: if a constant in a formula could not be
verified, `[unverified constant]` is appended to the citation. **No feature
currently carries it** (the list is empty); the mechanism is there in case
it is needed.

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

**67 of the 208** Turkish keys have no citation: 29 are the letter-frequency
vector (one key per letter of the Turkish alphabet), 17 are punctuation
ratios, and 21 are other plain definitions such as lengths and spreads.

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
all 45 works.

## Does the number actually match?

The citation tells you the source; it does not tell you the number
**agrees**. There is a separate document for that:

- **[Verification report](../../verification-report.md)** — for each
  feature, a comparison against the number its source published.
- How to read it: **[The verification system](../explanation/verification.md)**.
