# Changelog

## [Unreleased]

### Changed

- `segment_text(unit="word")` and `analyze_corpus(segment_size=...)` count the library's
  default word instead of spaCy tokens (decided 2026-10-08): a `size=1000` segment is exactly
  1000 words in `analyze`. Before, punctuation counted too and 100 tokens were about 83 words.
  Segment boundaries, and so segment counts and values, change; `segment_text` no longer loads
  a spaCy tokenizer.
- Every logarithm in the library is now the natural logarithm (decided 2026-10-06). Changed:
  `dugast_u`, `lambda_pa` and `adjusted_modulus` (were log₁₀) and the entropy measures
  `entropy`, `punct_entropy`, `sent_len_entropy`, `zeyrek_suffix_bigram_entropy` and `posdiv`
  (were log₂). Values scale by a constant (log₁₀ → ln: × ln 10 for `dugast_u` and
  `lambda_pa`, ÷ ln 10 for `adjusted_modulus`; bits → nats: × ln 2), so the ranking of texts does
  not change. The scale name `"bits"` is now `"nats"`. QUITA publishes these in log₁₀ and bits;
  the verification report converts the published values to ln units, and all six rows stay ✅.
- Default word definition (decided 2026-10-06): a whitespace-separated piece of the raw text with
  edge punctuation stripped, counted as a word when it contains a letter or digit (`space_unit`,
  the readability formulas' word). On the TOMA set (57 texts) it equals the expert's word count in
  every text; spaCy-token words did not. Hyphenated forms (`e-posta`, `akvam-ı`) and symbol-number
  forms (`%50`) are one word; numbers stay words. Features that only count words or read their
  written form switch to it: sentence lengths (7), paragraph lengths (3), syllable features (10),
  vowel harmony (2), punctuation per word (10), capitalisation (2), surface-form lexical richness
  (`ttr`, `mtld`, `yule_k`, `word_len_mean` … 26) and `custom_ngrams`. Features that need a
  label per word followed on 2026-10-07 (next item). `describe_feature(key)["definitions"]["word"]`
  says which word a feature uses; the
  word names `alnum_token`, `letter_token`, `syllabifiable_token`, `space_split` and the word sense
  of `spacy_token` are gone. On TOMA 57 features change; most move under 1% (median), texts with
  Ottoman izafet (`ulüvv-i`, which spaCy split into a separate one-syllable word `i`) move most,
  up to 36% in `syllable_1_ratio`. The verification reports do not change (46 ✅ + 2 🟡). The
  internal token-based syllable helpers (`phonetic.toplam_hece` and its helpers) and the unused
  `okunus.sembol_oku` were removed; `phonetic.birim_hecesi` is the one syllable counter.
- Eighteen features that had no citation now cite a source read in full (decided
  2026-10-07): `sent_len_mean` → Flesch (1948) p.223; `word_len_mean` → Mendenhall (1887)
  p.237; `sent_len_median` → Yule (1939) p.369; `hapax_ratio` → de Vel (2000) Table 2;
  `whitespace_ratio`, `punct_char_ratio`, `digit_ratio` → de Vel et al. (2001) Table 2;
  `para_len_mean`, `sents_per_para_mean`, `sent_len_char_mean` and seven `punct_*_ratio` keys
  (comma, full stop, semicolon, exclamation, colon, question, quote) → Zheng et al. (2006)
  Table 3; `pronoun_ratio` →
  Deutsch, Jasbi & Shieber (2020) Table 6 (the original source could
  not be traced, and the citation says so). The letter-frequency keys (`char_*`, TR 29, EN 26)
  cite Zheng et al. (2006) Table 3, no. 7-32; Zheng counts the 26 letters A-Z, here each language
  keeps its own alphabet. Where our definition differs from the source the citation says so.
  `pos_punct` (it cited the UPOS tag set) is gone. With the removals below, cited features:
  TR 144 → 187, EN 119 → 160; uncited: TR 11, EN 11; verification candidates: TR 95 → 141,
  EN 84 → 127; bibliography 50 → 55 works. No values change.
- Feature keys renamed so that a key says what it measures (decided 2026-10-07/08). No values
  change unless stated below. Rules: a 0-1 share ends in `_ratio` unless the measure has an
  established name (`ttr`, `hdd`, `lexical_density`); means and medians end the key; one family,
  one prefix.
  - Punctuation: `punct_` and the mark's name. `punc_,_ratio` → `punct_comma_ratio`,
    `punc_._ratio` → `punct_period_ratio`, `punc_;_ratio` → `punct_semicolon_ratio`,
    `punc_!_ratio` → `punct_exclamation_ratio`, `punc_:_ratio` → `punct_colon_ratio`,
    `punc_-_ratio` → `punct_dash_ratio`, `punc_ellipsis/paren/quote/question_ratio` →
    `punct_…_ratio`, `punct_density` → `punct_char_ratio`, `digit_vs_all` → `digit_ratio`
    (column names with `.`, `-` or `!` broke attribute access in pandas and were rewritten by R).
  - Means and medians: `avg_sent_len_word` → `sent_len_mean`, `avg_sent_len_char` →
    `sent_len_char_mean`, `med_sent_len` → `sent_len_median`, `avg_word_length` →
    `word_len_mean`, `sentence_syllable_mean` → `sent_syllable_mean`.
  - Shares: `pos_noun` … → `pos_noun_ratio` … (12), `sentfinal_noun` … → `sentfinal_noun_ratio`
    … (14), `char_a` … → `char_a_ratio` … (TR 29, EN 26), `hapax_percentage` →
    `hapax_token_ratio` (a 0-1 share, not a percentage), `question_per_sent` →
    `question_sent_ratio`, `pronoun_freq` → `pronoun_ratio`, `n_lemma_count` → `lemma_count`.
  - Morphology: the spaCy (UD) keys drop `morph_` (`morph_case_loc` → `case_loc_ratio`,
    `morph_tense_past` → `tense_past_ratio`, `morph_voice_pass` → `voice_pass_ratio`, 18 keys);
    the Zeyrek keys take `zeyrek_` (`case_loc_ratio` → `zeyrek_case_loc_ratio`, `tense_past_def`
    → `zeyrek_tense_past_def_ratio`, `agglutination_depth` → `zeyrek_agglutination_depth`, 23
    keys). The two analysers' measures of the same category no longer look alike.
  - Deutsch, Jasbi & Shieber (2020) measures take their source names: `pos_dist_std` →
    `posddev`, `pos_kl_div` → `posdiv`; with the old names a `pos_*` column filter caught them.
  - Feature functions named after a key are renamed the same way (`hapax_percentage`,
    `avg_sent_len_char`, `question_per_sent`, `pronoun_freq`, `punct_density`, the Zeyrek
    functions).
- The ten `punct_*_ratio` keys are now each mark type's share of all punctuation marks (0-1,
  summing to 1) instead of marks per word, which could exceed 1 (decided 2026-10-08). How much
  punctuation a text has is `punct_char_ratio`. A text without punctuation gives `nan`. Values
  change.
- `custom_ngrams` (decided 2026-10-08): keys are `ngram_{...}_count` (were `ng_{...}`) and the
  value is the number of matches, not matches per window; divide by the word count if you need a
  rate. A phrase item written as an UPPERCASE UD tag (`NOUN`, `VERB` …) matches any word with that
  tag: `["kadın", "VERB"]` counts "kadın" followed by a verb (`ngram_kadın_VERB_count`). Matches no
  longer cross sentence boundaries.
- One word definition for every feature except the dependency group (decided 2026-10-07). The
  POS, syntactic, morphological and Zeyrek features, the lemma-based lexical features
  (`lemma_count`, `*_variation`, `wordfreq_*`) and `frequency_structure` now count the default
  word (`space_unit`) instead of the spaCy token. A word takes its POS tag, morphological tags,
  lemma and Zeyrek analysis from the first token inside it that is not punctuation; the model
  splits 0.3% of Turkish and 2.7% of English words (Turkish `Türk-Amerikan`, `4-5`; English
  `it's`, `don't`), and these take their first part's labels. Punctuation no longer enters the
  denominators of the `pos_*` shares and `pronoun_ratio`, and `verb_dist_*` measure distances in
  words. `syntactic_dep` keeps the spaCy token and the parser's sentences.
- Turkish lemmas now come from Zeyrek instead of spaCy (decided 2026-10-07): the dictionary entry
  of Zeyrek's first analysis, lowercased, without the infinitive `-mak/-mek`; circumflexes stay
  as in Zeyrek's dictionary (`millî`). A word Zeyrek cannot analyse keeps the part before its
  apostrophe (`Pittsburgh'tan` → `pittsburgh`). spaCy's Turkish lemma left inflected forms as
  lemmas in 15% of words (TOMA, 11 texts). Changed: `lemma_count`, `noun_variation`,
  `verb_variation`, `adj_variation`, `adv_variation`, `wordfreq_mean`, `wordfreq_rare_ratio`,
  `surface_per_lemma` and the 13 `frequency_structure` features. English lemmas still come from
  spaCy; `describe_feature(key, lang=...)["definitions"]["type"]` names the source per language.

- The verification tolerance changed from a fixed absolute 0.05 to 1% relative
  to the published value (`math.isclose(rel_tol=0.01)`, with a 1e-9 absolute
  floor only as float-arithmetic safety for expected values of 0). The fixed
  difference was far too loose for ratios in 0-1 (`ttr`) and far too tight for
  values in the hundreds (`curve_length` ≈ 134). One row moves: `ttr` QUITA
  §6.1.1 Text 2 (published 0.590, ours 0.599, difference 1.5%; the source's
  own counts give 121/202 = 0.599) goes from ✅ to 🟡, with its reason now
  written in the report. Turkish report: 47 ✅ + 1 🟡 → 46 ✅ + 2 🟡; English
  report: 36 ✅ + 2 🟡 → 35 ✅ + 3 🟡. No row became ❌ and every other row
  keeps its status.
- Turkish syllable counts now read ordinals (`3. kat` → üçüncü), times and
  scores (`10:30` → on otuz) and numbers glued to letters (`3kg` → üç
  kilogram, `100m` → yüz metre, `3G` → üç ge). These forms used to be skipped
  or, in the readability formulas, counted as cardinals. The readability
  formulas and the syllable features change on texts that contain them; no
  verification row changed.
- Syllable features (both languages) now add the reading of a listed symbol to
  the number next to it (`%50` → yüzde elli, `$5` → five dollars), as the
  readability formulas already did. The symbol still does not count as a word.
- Registry metadata of `syllable_mean` and `syllable_cv` (description,
  formula, requirement, citation) had been copied from the syllable-bucket
  keys. `syllable_mean` now cites Flesch (1948), whose Formula A defines
  average word length in syllables (per 100 words; per word here) and which
  Ateşman (1997) adapted for Turkish; `syllable_cv` has no citation (not a
  named measure) and requires at least 2 syllabifiable words, as the code
  always did. Cited features: TR 141 → 140, EN 116 → 115; verification
  candidates: TR 92 → 91, EN 81 → 80. No values change.

### Added

- `word_count` in the `lexical` group (decided 2026-10-08): the number of words, by the
  library's default word. Divide `ngram_{...}_count` values by it to compare texts of different
  length. Cites de Vel (2000) Table 2, attribute 1, and Zheng et al. (2006) Table 3, no. 54.
  Keys: TR 198 → 199, EN 171 → 172.
- `ngram_matches(text, phrase, lang="tr")` (decided 2026-10-08): what one `custom_ngrams`
  phrase matched, as `{"kadın geldi": 2, "kadın güldü": 1}`, most frequent first. The matching is
  the one `analyze` uses, so the values add up to `ngram_{...}_count`. Sentence and position are
  not returned. The public API has eleven names.
- `examples/10_kelime_oruntuleri.py`: counting your own word and tag phrases with
  `custom_ngrams` and seeing what they matched with `ngram_matches`.
- Four lexical richness measures in the `lexical` group (TR 208 → 212 keys, EN 180 → 184):
  `cttr` (Carroll's corrected TTR, V/√(2N)), `summer_s` (Summer's S, ln(ln V)/ln(ln N)),
  `maas_a2` (Maas' a², (ln N − ln V)/(ln N)²) and `herdan_vm` (Herdan's Vm,
  √(Σf²/N² − 1/V)). Citations: Carroll (1964) and Somers (1966) as cited in Torruella &
  Capsada (2013) p.448; Maas (1972) and Herdan (1955) as cited in Tweedie & Baayen (1998)
  eqs. (7) and (18). The sources give no logarithm base; the natural logarithm reproduces the
  Maas values in Torruella & Capsada (2013) Table 1 and, with `dugast_u` now also in ln,
  `maas_a2 = 1 / dugast_u` exactly. Cited features: TR 140 → 144, EN 115 → 119;
  verification candidates: TR 91 → 95, EN 80 → 84; bibliography 45 → 50 works.
- `yule_k` now cites the primary source, Yule (1944) p.53, eq. (3.22), instead of Malvern et
  al. (2004); secondary citations 11 → 14 of 148.
- Default sentence rule of the readability formulas (decided 2026-10-06): `. ? ! …` always end a
  sentence, and `:` ends it only when what follows starts like a new sentence (capital letter,
  quote, dash or opening bracket); a colon followed by a lowercase letter or digit (lists,
  explanations, `10:30`) does not. The Kincaid rule set uses the same conditional colon (its source
  counts `:` only before a full sentence); the Çetinkaya rule keeps its source's unconditional `:`.
  `cumle_sayisi` takes a new optional `kosullu` argument. Texts with a colon followed by a capital
  letter, quote or dash get more sentences, so `atesman`, `cetinkaya_uzun` (unchanged: its own
  rule), `bezirci_yilmaz`, `lix`, `ari`, `coleman_liau` and the English formulas change on them.
- `describe_feature(key)["definitions"]`: for each term the feature's `formula` uses, the rule tlf
  counts it with: `{"name", "source", "description"}`, e.g. `sentence` → `default`, source `tlf`,
  and one sentence on how it is counted. `source` says who defines the rule (`tlf`, `spacy`,
  `zeyrek`, `textstat`, `wordfreq`). 21 terms: `sentence`, `word`, `type`, `token`,
  `syllable`, `polysyllable`, `letter`, `character`, `long_word`, `paragraph`, `mark`, `noun`, `verb`,
  `lexical_word`, `content_word`, `suffix` (tlf's own rules) and `pos_tag`, `morph_feature`,
  `dependency`, `zipf_score`, `zeyrek_tag` (a library's output used directly). A term the formula
  does not use is absent. `describe_feature(key, lang=...)` is new: where a definition differs by
  language (`syllable`: Turkish vowel count, English `textstat`) it picks that language's entry;
  without `lang` both are returned. Mapping in `features/_registry_definitions.py`, texts in
  `features/_registry_definition_texts.py`, read from the code on 2026-10-06; a test checks that
  every term named in a formula is present.
- `readability.kural_cumleleri(surface_tokens, lang)`: the sentence list under the default rule
  (same boundaries as `cumle_sayisi(..., "varsayilan")`; concatenating it gives back the tokens).

### Changed (sentence definition)

- The twelve features that used spaCy's parser sentences now use the default sentence rule:
  the eight `sentence` features, `question_sent_ratio`, `posdiv`, `sent_syllable_mean` and
  `sentence_syllable_cv`. The values change; on the 57 TOMA texts the median change is 0% but single
  texts move up to about ±16% (`sent_len_mean`) and `question_sent_ratio` rises (median +29% where
  non-zero). `syntactic_dep` (16 features, parser) and the paragraph group (`sents_per_para_*`,
  regex `[.!?…]+`) keep their own definitions; `describe_feature` names them.
- The default sentence-length thresholds are now calibrated on newspaper columns with the default
  sentence rule and the default word (15th/85th percentile; TR 162 columnists / 197,990 sentences,
  EN 30 columnists / 52,745 sentences): Turkish changes from 4/18 to 4/17, English from 7/39 to
  8/32 (`short_sent_threshold`, `long_sent_threshold`; only `short_sent_ratio` and
  `long_sent_ratio` move). Measured with the earlier word (spaCy token) the same columns gave
  4/18 and 9/33; both earlier calibrations are kept in `docs/threshold-calibration.md` as history.
  On Turkish novels the new thresholds give 26.5% short and 7.6% long sentences (columns:
  12.2% / 15.0%); for fiction pass your own thresholds through `FeatureParams`.

### Fixed

- The Zheng et al. (2006) citations gave Table 3 as p.384; the table is on p.385 (p.384 only
  refers to it). Checked against the article PDF.
- `describe_feature(key)["inputs"]` still listed the inputs from before the one-word definition;
  the groups that count words or take a tag per word now list `raw_text`, `surface_tokens`,
  `lemma_tokens` and `pos_data`.
- `examples/02_korpus_analizi.py` no longer prints highly correlated feature pairs; the library
  measures and leaves feature selection to the user.
- `examples/06_esik_kalibrasyonu.py` split sentences with spaCy's parser while the library
  uses its own sentence rule, so its built-in check reported a different median; it now counts
  sentences and words with the library's rule and prints the calibrated default thresholds
  (TR 4/17) instead of the old novel-based 4/18.
- The readability formulas counted `...` (three dots) as a sentence end but not
  the single character `…`, so the same text got a different sentence count (and
  different `atesman`, `cetinkaya_uzun`, `bezirci_yilmaz`, `lix`, `ari`,
  `coleman_liau`) depending on how the ellipsis was typed. `…` now ends a sentence
  in every rule set, like `...`. Texts that contain `…` change; texts without it
  do not.
- `segment_text(unit="word")` no longer counts whitespace and line-break
  tokens. `analyze` discards them, so a text with hard line breaks produced
  segments with fewer real tokens than `size` (about 11% fewer in a text
  wrapped every 8 words: 178 instead of 200). Each segment now holds exactly
  `size` tokens by the same count `analyze` uses. Segment boundaries, and so
  segment counts and values, change for texts with line breaks or repeated
  spaces; single-spaced text is unaffected.
- Three registry description texts ran words together ("notclipped",
  "words,vocd_num_runs", "removed,root"); they appear in `describe_feature()`
  and in the feature reference.
- The `describe_feature(...)["params"]` examples in the parameter guide showed
  a list; the function returns a tuple.
- The minimum spaCy version is now 3.8 (`spacy>=3.8,<4`, was 3.5): both language
  models (`tr_core_news_md`, `en_core_web_sm` 3.8.0) require it.
- The install hint for a missing optional package named an extra of the package
  on PyPI, where the package is not yet published; it now names the package
  itself (`pip install 'wordfreq>=3.0'`, `pip install 'pandas>=1.5'`).
- The `analyze` docstring example gave 3.5 for a text whose mean sentence length
  is 3.0; four bibliography entries had Turkish fragments ("Sunum", "s.",
  "dergi"); the reference index said "208 feature keys" (the fixed keys plus the
  `char_` and `ng_` families); the feature reference ended with a blank line that
  the pre-commit end-of-file fixer removes, which broke its freshness test.
- Words with a curly apostrophe (`Zeynep’i`, `Türkiye’de`) were left unanalysed by Zeyrek,
  which recognises only the straight `'`, and dropped out of the `morphological_zeyrek`
  features (0.9% of the words in 11 TOMA texts, mostly proper names). `’` and `‘` are now
  turned into `'` before analysis. Texts typed with curly apostrophes change.
- The limitations page now explains how Zeyrek orders its analyses and that the
  first one can depend on `PYTHONHASHSEED` (200 of 8,215 words on the TOMA set).

### Removed

- `pos_punct` (decided 2026-10-07): with POS shares counted per word there is no punctuation
  token left to count; the `punctuation` group measures punctuation. The `pos` group has 12
  keys. The verification reports' verified rows do not change.
- `ttr_moving_slope` and its parameter `FeatureParams.ttr_slope_chunk_size` (decided 2026-10-07):
  the slope of TTR over disjoint chunks was hard to read and had no source. Keys: TR 212 → 211,
  EN 184 → 183; `lexical` 36 → 35. Passing `ttr_slope_chunk_size` to `FeatureParams` now
  raises `TypeError`.
- Six coefficient-of-variation features (decided 2026-10-07): `word_length_cv`,
  `sentence_length_cv`, `para_len_cv`, `sents_per_para_cv`, `syllable_cv` and
  `sentence_syllable_cv`. None had a source and what they showed was unclear; two repeated
  another in syllables, two depended on blank-line paragraph boundaries. Keys: TR 211 → 205,
  EN 183 → 177; `lexical` 35 → 34, `sentence` 8 → 7, `paragraph` 5 → 3, `phonetic` TR 15 → 13,
  EN 13 → 11. `examples/05_cumle_ritmi.py` now ranks labels by the share of short plus long
  sentences instead of the CV.
- Seven more features (decided 2026-10-08): the last two coefficients of variation
  (`verb_dist_cv`, `suffix_chain_cv`); `entropy_std` and `sent_len_skewness` (spread statistics
  with no source of their own; summary statistics over a distribution may return as one general
  function); `para_count_norm` (exactly 1000 / `para_len_mean`); `nominal_verbal_ratio` (count
  `custom_ngrams=[["NOUN"], ["VERB"]]` and divide); `punct_total_ratio` (the same information as `punct_char_ratio`, per
  word). The `"cv"` and `"signed"` scales go with them. Keys: TR 205 → 198, EN 177 → 171;
  `lexical` 34 → 33, `sentence` 7 → 6, `paragraph` 3 → 2, `syntactic` 9 → 7,
  `morphological_zeyrek` 24 → 23, `punctuation` 19 → 18. Wells (1960) leaves the bibliography.
- The undocumented `LINGUISTIC_FEATURES_NO_ZEYREK_WARMUP` environment variable.
  The Zeyrek warm-up now always runs on import: skipping it and then analysing
  Turkish in the same process could crash on Windows.

## [0.1.0] - 2026-09-28

### Added

- Initial public release.
