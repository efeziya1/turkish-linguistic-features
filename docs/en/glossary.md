# Glossary

These terms are used consistently throughout the documentation. The point is
not to be exhaustive but to avoid calling the same thing two names on two
pages.

## Library concepts

| Term | Meaning |
|---|---|
| **feature** | A single number extracted from a text (`ttr`, `atesman`) |
| **key** | A feature's name; the `dict` key in the returned mapping |
| **group** | One of the 13 sets features belong to (`lexical`, `readability`…; 14 with `custom_ngrams`) |
| **citation** | The short source pointer — the parenthetical in a methods section |
| **reference** | The full bibliographic record — what goes in a bibliography |
| **registry** | The single place all feature metadata lives |
| **pipeline** | The chain of steps from raw text to numbers |
| **scale** | The kind of value: `ratio_0_1`, `score`, `count`… |
| **segment** | A slice of text produced by `segment_text` |
| **label** | The folder name in a corpus; author, class or experimental arm |

## Measurement terms

| Term | Meaning |
|---|---|
| **word** | A whitespace-separated piece with edge punctuation stripped, containing a letter or digit; the word the library counts |
| **sentence** | A unit ending in `. ? ! …`; `:` only when a new sentence follows |
| **spaCy token** | The unit the model splits text into; punctuation is a token of its own. `segment_text` counts these |
| **lemma** | A word's dictionary form; from Zeyrek for Turkish, from spaCy for English |
| **POS tag** | One of the 17 UD part-of-speech tags (`NOUN`, `VERB`, `ADJ`…) |
| **n-gram** | A sequence of consecutive words; counted with `custom_ngrams` |
| **type** | One of the distinct words in a text |
| **token** | In the type-token ratio: one of the word instances in a text |
| **type-token ratio (TTR)** | Number of types ÷ number of tokens |
| **hapax legomenon** | A word occurring exactly once in the text |
| **stroke** | Every non-space character — the input to ARI |
| **window** | The number of words examined at a time in a rolling computation |
| **threshold** | The boundary value that triggers a classification |
| **percentile** | The value below which n% of the distribution falls |
| **calibration** | Deriving a threshold from data rather than picking it |

## Verification terms

| Term | Meaning |
|---|---|
| **exact** | Within tolerance of the source's number (✅) |
| **documented deviation** | A difference whose reason is written down (🟡) |
| **mismatch** | An unexplained difference (❌) |
| **end-to-end** | Tested by pushing the source's own text through the pipeline |
| **formula** | Tested by feeding inputs directly to the function |
| **as cited in** | The primary source could not be obtained; taken from a secondary |
| **release gate** | A condition that blocks a release if unmet |

## On "stroke"

ARI's input is the number of **strokes**, which is Kincaid's own term: it
comes from a typewriter with a keystroke counter attached. Appendix B of
the 1975 report says:

> Letters, symbols, and punctuation marks are included in the count of
> strokes.

So a stroke is every non-space character. In modern presentations of the
formula this is usually called "characters". Some implementations count
only letters and drop punctuation; this one does not, because the source
says otherwise.
