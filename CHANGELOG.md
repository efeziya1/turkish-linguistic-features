# Changelog

## [Unreleased]

### Changed

- Default word definition (decided 2026-10-06): a whitespace-separated piece of the raw text with
  edge punctuation stripped, counted as a word when it contains a letter or digit (`space_unit`,
  the readability formulas' word). On the TOMA set (57 texts) it equals the expert's word count in
  every text; spaCy-token words did not. Hyphenated forms (`e-posta`, `akvam-ı`) and symbol-number
  forms (`%50`) are one word; numbers stay words. Features that only count words or read their
  written form switch to it: sentence lengths (7), paragraph lengths (3), syllable features (10),
  vowel harmony (2), punctuation per word (10), capitalisation (2), surface-form lexical richness
  (`ttr`, `mtld`, `yule_k`, `avg_word_length` … 26) and `custom_ngrams`. Features that need a
  spaCy or Zeyrek label per word (POS, lemma, morphology, dependency) keep the spaCy token
  (`pos_token`). `describe_feature(key)["definitions"]["word"]` says which one a feature uses; the
  word names `alnum_token`, `letter_token`, `syllabifiable_token`, `space_split` and the word sense
  of `spacy_token` are gone. On TOMA 57 features change; most move under 1% (median), texts with
  Ottoman izafet (`ulüvv-i`, which spaCy split into a separate one-syllable word `i`) move most,
  up to 36% in `syllable_1_ratio`. The verification reports do not change (46 ✅ + 2 🟡).

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
  the eight `sentence` features, `question_per_sent`, `pos_kl_div`, `sentence_syllable_mean` and
  `sentence_syllable_cv`. The values change; on the 57 TOMA texts the median change is 0% but single
  texts move up to about ±16% (`avg_sent_len_word`) and `question_per_sent` rises (median +29% where
  non-zero). `syntactic_dep` (16 features, parser) and the paragraph group (`sents_per_para_*`,
  regex `[.!?…]+`) keep their own definitions; `describe_feature` names them.
- The default sentence-length thresholds are now calibrated on newspaper columns with the default
  sentence rule (15th/85th percentile; TR 162 columnists / 197,990 sentences, EN 30 columnists /
  52,745 sentences): Turkish stays 4/18, English changes from 7/39 to 9/33 (`short_sent_threshold`,
  `long_sent_threshold`; only `short_sent_ratio` and `long_sent_ratio` move). The earlier
  calibration (novel corpora, parser sentences) is kept in `docs/threshold-calibration.md` as
  history. On Turkish novels the new thresholds give 26.5% short and 6.6% long sentences (columns:
  12.1% / 13.0%); for fiction pass your own thresholds through `FeatureParams`.

### Fixed

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

### Removed

- The undocumented `LINGUISTIC_FEATURES_NO_ZEYREK_WARMUP` environment variable.
  The Zeyrek warm-up now always runs on import: skipping it and then analysing
  Turkish in the same process could crash on Windows.

## [0.1.0] - 2026-09-28

### Added

- Initial public release.
