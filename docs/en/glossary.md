# Glossary

These terms are used consistently throughout the documentation, so that the same thing
never gets two names on two pages. The Turkish column gives the term used in the Turkish
documentation and in the thesis that describes the tool.

## The tool's concepts

| Term | Turkish | Meaning |
|---|---|---|
| **feature** | öznitelik | A single number extracted from a text (`ttr`, `atesman`) |
| **key** | anahtar | A feature's name; the `dict` key in the returned mapping |
| **group** | grup | One of the 12 sets features belong to (`lexical`, `readability`…; 13 with `custom_ngrams`) |
| **citation** | künye | The short source pointer; the parenthetical in a methods section |
| **reference** | kaynakça kaydı | The full bibliographic record; what goes in a bibliography |
| **registry** | öznitelik dizini | The single place each feature's definition, formula and citation live |
| **pipeline** | çözümleme hattı | The steps from raw text to numbers: spaCy, Zeyrek and the tool's own rules |
| **scale** | ölçek | The kind of value: `ratio_0_1`, `score`, `count`… |
| **segment** | parça | A slice of text produced by `segment_text` |
| **label** | etiket | The folder name in a corpus; author, class or experimental arm |
| **parameter** | parametre | A window size, threshold or sample count you can change (`FeatureParams`) |
| **constant** | sabit | A number fixed in a formula: MTLD's 0.72, Brunet's 0.172, the coefficients of a readability formula |
| **n-gram** | sözcük dizisi | A sequence of words, lemmas or part-of-speech tags you give; counted with `custom_ngrams` |

## Language processing

| Term | Turkish | Meaning |
|---|---|---|
| **token** | türce | The smallest unit spaCy splits text into; punctuation is a token of its own. In the type-token ratio, each word instance in a text |
| **type** | tür | One of the distinct words in a text; `house` occurring three times is one type |
| **type-token ratio (TTR)** | tür/türce oranı | Number of types ÷ number of tokens |
| **lemma** | sözlükbirim | A word's dictionary form; from Zeyrek for Turkish, from spaCy for English |
| **morpheme** | biçimbirim | A root or suffix in Zeyrek's analysis |
| **part of speech** | sözcük türü | Noun, verb, adjective… |
| **POS tag** | sözcük türü etiketi | One of the 17 Universal Dependencies part-of-speech tags (`NOUN`, `VERB`, `ADJ`…) |
| **dependency** | bağımlılık | The link the parser draws between two words of a sentence |
| **parser** | ayrıştırıcı | The component that derives a sentence's dependency structure (spaCy) |
| **analyzer** | çözümleyici | The component that splits a word into morphemes; Zeyrek in this tool |
| **tagger** | etiketleyici | The component that gives words their part-of-speech tags (spaCy) |
| **tokenizer** | türceleyici | The component that splits text into tokens |
| **disambiguation** | belirsizlik giderme | Choosing, from several analyses of a word, the one that fits the context; Zeyrek does not do this |
| **hash seed** | karma tohumu | Python's internal number that changes on every run; fixed with `PYTHONHASHSEED=0` |
| **sentence boundary** | tümce sınırı | Where a sentence ends; found with the tool's own rule |
| **content word** | içeriksel sözcük | A noun, proper noun, verb, adjective or adverb |
| **phoneme** | sesbirim | A sound unit that distinguishes meaning; the tool works with letters, not phonemes |
| **syllable** | seslem | The unit counted by the readability formulas and the syllable features |
| **transcription** | çevriyazı | Writing sounds down in a script such as IPA |

## Measurement

| Term | Turkish | Meaning |
|---|---|---|
| **word** | sözcük | A whitespace-separated piece with edge punctuation stripped, containing a letter or digit; the word the tool counts |
| **sentence** | tümce | A unit ending in `. ? ! …`; `:` only when a new sentence follows |
| **corpus** | derlem | Texts analysed together |
| **measure** | ölçü | A calculation proposed in the literature (MTLD, the Ateşman formula) |
| **lexical diversity** | sözcüksel çeşitlilik | How many different words a text uses (TTR, MATTR, MTLD) |
| **lexical richness** | sözcüksel zenginlik | The breadth of the vocabulary; covers the diversity and frequency measures |
| **lexical density** | sözcüksel yoğunluk | The share of content words among all words |
| **syntactic complexity** | sözdizimsel karmaşıklık | How complex sentence structure is |
| **dependency distance** | bağımlılık uzaklığı | The difference between the positions of two linked words |
| **hierarchical distance** | hiyerarşik uzaklık | A word's distance from the root of the dependency tree |
| **readability** | okunabilirlik | How easy or hard a text is to read |
| **readability formula** | okunabilirlik formülü | A formula that estimates readability from word and sentence properties |
| **h-point** | h-noktası | The point in the rank–frequency distribution where rank equals frequency |
| **rank–frequency** | sıra–sıklık | The distribution of words ordered by frequency rank |
| **thematic concentration** | tematik yoğunlaşma | How much a text concentrates on a few content words |
| **hapax legomenon** | hapax | A word occurring exactly once in the text |
| **stroke** | vuruş | Every non-space character (the input to ARI) |
| **window** | pencere | A run of consecutive words measured at a time |
| **threshold** | eşik | The boundary value that triggers a classification |
| **percentile** | yüzdelik | nth percentile: n% of the values are equal to it or smaller |
| **median** | ortanca | The middle value of ordered values (the 50th percentile) |
| **calibration** | kalibrasyon | Setting a threshold by measuring it in a corpus |
| **not a number (NaN)** | sayı değil | "This number cannot be computed for this text" |

## Verification

| Term | Turkish | Meaning |
|---|---|---|
| **literature** | alanyazın | The body of publications on a subject |
| **literature measure** | alanyazın ölçüsü | A measure with a name in the literature; it has a citation |
| **tag ratio** | etiket oranı | The share of one category of an external tag scheme |
| **plain definition** | yalın tanım | A definition without a source |
| **tool-specific** | araca özgü | Formula from a source; what it is applied to, from this tool |
| **calibrated** | kalibre edilmiş | Threshold from this tool's own calibration |
| **primary source** | birincil kaynak | The publication that proposed the measure |
| **secondary source** | ikincil kaynak | A source that reports the measure from another publication |
| **as cited in** | aktaran (akt.) | The primary source could not be obtained; taken from a secondary one |
| **comparison** | karşılaştırma | In the report, pairing a feature with a number its source published |
| **match** | örtüşen | Within tolerance of the source's number (✅) |
| **documented deviation** | belgelenmiş sapma | A difference whose reason is written down (🟡) |
| **open** | açık | No number published by the source has been found yet (🔍) |
| **mismatch** | uyuşmazlık | An unexplained difference (❌) |
| **relative tolerance** | göreli tolerans | The allowed difference as a share of the published value (1%) |
| **end-to-end comparison** | uçtan uca karşılaştırma | Tested by pushing the source's own text through the pipeline |
| **formula comparison** | formül karşılaştırması | Tested by feeding inputs directly to the formula |
| **test dataset** | sınama veri seti | Texts with known values, prepared to test software (the TOMA dataset) |
| **release gate** | yayın kapısı | A condition that blocks a release if unmet |
