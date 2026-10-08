# Changelog

## [Unreleased]

This release renames and removes feature keys; tables built with 0.1.0 will not line up
column for column. Keys: Turkish 208 (the same number, not the same keys), English 180 → 181. Cited features: Turkish
141 → 197, English 116 → 170; 11 keys in each language are plain definitions without a source.

### Added

- Nine counts. `lexical`: `word_count` (words by the library's word), `type_count` (V),
  `hapax_count` (V1, words occurring once) and `dislegomena_count` (V2, twice); `sentence`:
  `sent_count`; `paragraph`: `para_count`; `phonetic`: `syllable_count`; `punctuation`:
  `char_count` (whitespace included) and `punct_count` (marks). Divide other counts by them
  to compare texts of different length. Citations: de Vel (2000) Table 2, attributes 1, 3 and
  8; Zheng et al. (2006) Table 3, nos. 1, 54, 60–62, 247 and 248; Tweedie & Baayen (1998)
  pp.325 and 329; de Vel et al. (2001) Table 2; Kincaid et al. (1975) p.38.
- `ngram_matches(text, phrase, lang="tr")`: what one `custom_ngrams` phrase matched, with
  counts, most frequent first: `{"kadın geldi": 2, "kadın güldü": 1}`. The matching is the
  one `analyze` uses, so the counts add up to the phrase's `ngram_{...}_count`. The public API
  has eleven names.
- Five lexical richness measures: `cttr` (Carroll's corrected TTR), `summer_s` (Summer's S),
  `maas_a2` (Maas' a²), `herdan_vm` (Herdan's Vm) and `honore_r` (Honoré's R, 100 · ln N /
  (1 − V1/V)). Citations: Carroll (1964) and Somers (1966) as cited in Torruella & Capsada
  (2013) p.448; Maas (1972), Herdan (1955) and Honoré (1979) as cited in Tweedie & Baayen
  (1998) eqs. (7), (18) and (11).
- `describe_feature(key)["definitions"]`: for every term the `formula` uses (`sentence`,
  `word`, `type`, `syllable`, `pos_tag` … 21 terms), the rule the library counts it with, who
  defines that rule (`tlf`, `spacy`, `zeyrek`, `textstat`, `wordfreq`) and one sentence on
  how it is counted. `describe_feature(key, lang=...)` picks the language's entry where a
  definition differs by language (`syllable`, `type`).
- `examples/10_kelime_oruntuleri.py`: counting your own word and tag phrases and seeing what
  they matched.

### Changed

- **Key names.** A name now says what the feature measures: a share between 0 and 1 ends in
  `_ratio` unless the measure has an established name (`ttr`, `hdd`, `lexical_density`);
  means and medians end the key; one family, one prefix. Values do not change.
  - Punctuation: `punc_,_ratio` → `punct_comma_ratio`, `punc_._ratio` →
    `punct_period_ratio`, `punc_;_ratio` → `punct_semicolon_ratio`, `punc_!_ratio` →
    `punct_exclamation_ratio`, `punc_:_ratio` → `punct_colon_ratio`, `punc_-_ratio` →
    `punct_dash_ratio`, `punc_ellipsis/paren/quote/question_ratio` → `punct_…_ratio`,
    `punct_density` → `punct_char_ratio`, `digit_vs_all` → `digit_ratio`. Column names with
    `.`, `-` or `!` broke attribute access in pandas and were rewritten by R.
  - Means and medians: `avg_sent_len_word` → `sent_len_mean`, `avg_sent_len_char` →
    `sent_len_char_mean`, `med_sent_len` → `sent_len_median`, `avg_word_length` →
    `word_len_mean`, `sentence_syllable_mean` → `sent_syllable_mean`.
  - Shares: `pos_noun` … → `pos_noun_ratio` … (12), `sentfinal_noun` … →
    `sentfinal_noun_ratio` … (14), `char_a` … → `char_a_ratio` …, `hapax_percentage` →
    `hapax_token_ratio` (a share, not a percentage), `question_per_sent` →
    `question_sent_ratio`, `pronoun_freq` → `pronoun_ratio`, `n_lemma_count` → `lemma_count`.
  - Morphology: keys from spaCy's UD tags drop `morph_` (`morph_case_loc` →
    `case_loc_ratio`, 18 keys); keys from Zeyrek take `zeyrek_` (`case_loc_ratio` →
    `zeyrek_case_loc_ratio`, `tense_past_def` → `zeyrek_tense_past_def_ratio`,
    `agglutination_depth` → `zeyrek_agglutination_depth`, 23 keys).
  - Deutsch, Jasbi & Shieber (2020) measures take their source names: `pos_dist_std` →
    `posddev`, `pos_kl_div` → `posdiv`.
  - Feature functions named after a key are renamed the same way.
- **One word.** Every feature except the dependency group counts the same word: a
  whitespace-separated piece with edge punctuation stripped, containing a letter or digit
  (`e-posta`, `%50` and numbers are one word each). On the TOMA set it equals the expert's
  word count in all 57 texts. Features that need a tag per word take the POS tag,
  morphological tags, lemma and Zeyrek analysis from the first token inside the word; spaCy
  splits 0.3% of Turkish and 2.7% of English words (`Türk-Amerikan`, `it's`). Punctuation no
  longer enters the denominators of the `pos_*_ratio` shares and `pronoun_ratio`.
  `syntactic_dep` keeps spaCy's tokens and parser sentences.
- **Turkish lemmas come from Zeyrek**, not spaCy: the dictionary entry of Zeyrek's first
  analysis, lowercased, without the infinitive `-mak/-mek`; circumflexes stay (`millî`). A word
  Zeyrek cannot analyse keeps the part before its apostrophe (`Pittsburgh'tan` →
  `pittsburgh`). spaCy's Turkish lemma left inflected forms as lemmas in 15% of words.
  English lemmas still come from spaCy. Affected: `lemma_count`, `*_variation`, `wordfreq_*`,
  `surface_per_lemma` and the `frequency_structure` group.
- **One sentence rule.** `. ? ! …` end a sentence; `:` only when what follows starts like a new
  sentence (capital letter, quote, dash or opening bracket). The `sentence` group,
  `question_sent_ratio`, `posdiv` and `sent_syllable_mean` use it instead of spaCy's parser
  sentences. The readability formulas use the same conditional colon (Kincaid's rule too);
  the Çetinkaya rule keeps its source's unconditional `:`, and `syntactic_dep` keeps the
  parser.
- **Sentence-length thresholds** are calibrated on newspaper columns with the rules above
  (15th/85th percentile; Turkish 162 columnists / 197,990 sentences, English 30 columnists /
  52,745 sentences): Turkish 4/18 → 4/17, English 7/39 → 8/32. The 15th/85th choice was
  compared with 5/95 to 25/75 on the same columns; the calibration page has the table.
- **`segment_text` and `analyze_corpus(segment_size=...)` count words**, the same word
  `analyze` counts: a `size=1000` segment is exactly 1000 words. They used to count spaCy
  tokens, punctuation included (100 tokens were about 83 words). Segment boundaries change.
- **Punctuation shares.** The ten `punct_*_ratio` keys are each mark type's share of all
  punctuation marks (0-1, summing to 1), no longer marks per word, which could exceed 1. How
  much punctuation a text has is `punct_char_ratio`. A text without punctuation gives `nan`.
- **`custom_ngrams`** keys are `ngram_{...}_count` and the value is the number of matches, not
  matches per window. A phrase item written as an UPPERCASE UD tag (`NOUN`, `VERB` …) matches
  any word with that tag: `["kadın", "VERB"]` counts "kadın" followed by a verb. Matches stay
  inside a sentence. An empty text gives `nan`, like every other feature.
- **Natural logarithm everywhere.** `dugast_u`, `lambda_pa`, `adjusted_modulus` (were log₁₀)
  and `entropy`, `punct_entropy`, `sent_len_entropy`, `zeyrek_suffix_bigram_entropy`, `posdiv`
  (were log₂) change by a constant factor; the ranking of texts does not change. The scale
  `"bits"` is now `"nats"`.
- **Syllable counts** read Turkish ordinals (`3. kat` → üçüncü), times and scores (`10:30` →
  on otuz) and numbers glued to letters (`3kg` → üç kilogram), and add the reading of a listed
  symbol to the number next to it in both languages (`%50` → yüzde elli, `$5` → five dollars).
- **Citations.** Features that had no citation now cite a source read in full, among them
  `sent_len_mean`
  (Flesch 1948), `word_len_mean` (Mendenhall 1887), `sent_len_median` (Yule 1939),
  `hapax_ratio` (de Vel 2000), the letter and punctuation shares (Zheng et al. 2006) and
  `yule_k`, which now cites Yule (1944) itself. Where the library's definition differs from
  the source, the citation says so. Bibliography 45 → 56 works.
- **Verification tolerance** is 1% of the published value instead of a fixed 0.05. One row
  moves from ✅ to 🟡 with its reason written out (`ttr`, QUITA Text 2, a misprint in the
  source). Turkish report: 46 ✅ + 2 🟡; English: 35 ✅ + 3 🟡; no ❌.
- **Examples.** `05` ranks labels by the share of short plus long sentences; `06` counts
  sentences with the library's own rule; `02` no longer lists correlated feature pairs.

### Removed

- `pos_punct`: with shares counted per word there is no punctuation token to count;
  punctuation is measured in the `punctuation` group.
- `ttr_moving_slope` and `FeatureParams.ttr_slope_chunk_size` (passing it now raises
  `TypeError`).
- The eight coefficients of variation (`word_length_cv`, `sentence_length_cv`,
  `para_len_cv`, `sents_per_para_cv`, `syllable_cv`, `sentence_syllable_cv`,
  `verb_dist_cv`, `suffix_chain_cv`), `entropy_std` and `sent_len_skewness`: spread
  statistics without a source of their own.
- `para_count_norm`: exactly 1000 / `para_len_mean`. The plain count is `para_count`.
- `nominal_verbal_ratio`: count `custom_ngrams=[["NOUN"], ["VERB"]]` and divide.
- The `"cv"` and `"signed"` scales, which no key uses any more.
- `exceptions.MissingDependencyError`: it was never raised. A missing optional package gives
  `MissingDependencyWarning` and `nan`; missing language data gives `ModelNotFoundError`.
- The undocumented `LINGUISTIC_FEATURES_NO_ZEYREK_WARMUP` environment variable: skipping the
  Zeyrek warm-up and then analysing Turkish in the same process could crash on Windows.

### Fixed

- `…` (one character) now ends a sentence like `...` in every rule set; before, the same text
  got a different sentence count and readability score depending on how the ellipsis was
  typed.
- Words with a curly apostrophe (`Zeynep’i`) were left unanalysed by Zeyrek and dropped out
  of the `morphological_zeyrek` features; `’` and `‘` are turned into `'` first.
- The minimum spaCy version is 3.8 (`spacy>=3.8,<4`, was 3.5): both language models need it.
- The install hint for a missing optional package names the package itself
  (`pip install 'wordfreq>=3.0'`), not an extra of a package not yet on PyPI.
- Registry and documentation texts: three descriptions ran words together, the parameter
  guide showed `params` as a list (it is a tuple), the `analyze` docstring example gave 3.5
  for a mean of 3.0, four bibliography entries had Turkish fragments.
- The limitations page explains how Zeyrek orders its analyses and that the first one can
  depend on `PYTHONHASHSEED` (200 of 8,215 words on the TOMA set).

## [0.1.0] - 2026-09-28

### Added

- Initial public release.
