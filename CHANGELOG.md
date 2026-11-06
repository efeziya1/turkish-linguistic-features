# Changelog

## [0.3.0] - 2026-10-27

This release renames and regroups feature groups, removes three Turkish keys and adds
Kalyoncu's (2025) four readability formulas; code that selects groups by name or expects
0.2.0's column set must be updated. Keys: Turkish 208 → 214, English 181. Cited features:
Turkish 197 → 203, English 170. Groups: 13 → 12 (13 with
`custom_ngrams`).

### Added

- **Kalyoncu (2025) K1–K4** (Turkish only, `readability` group): `kalyoncu_k1` …
  `kalyoncu_k4` and their components `kalyoncu_kl` (share of words not in Kalyoncu's word
  list), `kalyoncu_ttr` (share of stems occurring once), `kalyoncu_kco` (share of complex
  sentences), `kalyoncu_yco` (verbals per sentence) and `kalyoncu_ocu` (words per sentence).
  Numbers count as the words they are read as (`1968` = 5 words), in these keys only. Four of
  Kalyoncu's nine word-list rules and his meaning-based sentence definition are not applied;
  see the Kalyoncu formulas page. The values approximate Kalyoncu's hand counts. In these keys
  only: numbers written in words (`iki`, `ikisi`, `üçüncü`, `beşer`) count as in the list
  (rule 9 does not tell digits from words); a word tagged `PROPN`, or capitalised and not at
  the start of a sentence (`İstanbul'da`, `İstanbul’da`), is a proper noun and stays out of the
  numerator; and the stem, verbal and complex-sentence counts use the first Zeyrek analysis
  whose type matches spaCy's word class (the first analysis if none does). KL rests on expert
  judgement (rules 3, 5, 8 are not applied), so it is not expected to match the expert values
  exactly. The stem stops at the first inflectional suffix (`oradaki` → `ora`, not `oraki`).
  `ProcessedText` gains `morpheme_alternatives` (all Zeyrek analyses per token).
- The word list (Kalyoncu 2025, Appendix 1, 4,600 words) ships as
  `turkish_linguistic_features/data/kalyoncu_2025_ek1.txt`. It is not covered by the MIT
  licence.
- `FeatureParams.kalyoncu_ttr_window` (500): texts longer than this get a moving-window
  `kalyoncu_ttr` (Kalyoncu 2025, p. 73).
- `FeatureParams.verb_suffix_num_samples` (100) and `FeatureParams.verb_suffix_random_seed`
  (42, the same as `vocd_random_seed`) for `zeyrek_verb_suffix_diversity`.
- `FeatureParams.heaps_points` (20): the number of measurement points for `heaps_beta`.
- **Lemma items in `custom_ngrams` and `ngram_matches`.** An item written in capitals that is
  not a UD tag matches any word with that lemma: `["EV", "VERB"]` matches `eve gittim` and
  `evden çıktık` (key `ngram_EV_VERB_count`). Words, lemmas and tags can be mixed in one phrase
  (`["eski", "EV"]`, `["ADJ", "EV"]`). The lemma is the library's own: Zeyrek's first analysis
  in Turkish, spaCy in English; verbs without the infinitive suffix (`GİT`, `GO`). An item
  needs at least two letters to be a lemma (`I` stays a word), and a UD tag name is always a
  tag (`PART`). Lowercase items match the written form, as before.
- The verification report has a rule for a source's own arithmetic: when the number a source
  printed contradicts the arithmetic of the inputs it gives, and the library's value gives the
  correct arithmetic, the comparison counts as ✅ with the reason written under it.
- Kalyoncu & Memiş (2024) Text 1 and Text 3 are in the verification report: six more
  end-to-end comparisons for `atesman`, `cetinkaya_uzun` and `bezirci_yilmaz`, all within
  0.1%. The tests already checked these values.

### Changed

- **`brunet_w` follows Brunet (1978), read in the original.** The formula is the one Brunet
  calls more exact, `N^((V-b)^-a)` (p.65), with the new parameter `brunet_w_b` (default 20; `0`
  gives the form without `b`, p.49). `V ≤ b` gives `nan`, so a text needs more than 20 distinct
  words. `a` stays 0.172 (p.49). Values change. The citation now names the primary source, so
  secondary citations go from 15 to 14 (Turkish 14 → 13). The verification report compares the
  default against the ten rows of Brunet's p.65 table, formula rows with `V > 20`.
- **One counting rule for diversity measures.** They count surface forms; this is the library's
  design decision, and `*_variation` and `lemma_count` remain the exceptions. Where the source
  counts otherwise the citation says so: `brunet_w`, `herdan_c`, `yule_k`. Values of `herdan_c`
  and `yule_k` do not change.
- **`custom_ngrams`: an item in capitals is a lemma** (see Added). In 0.2.0 `İZMİR` matched
  the written form `izmir`; it now matches words with the lemma `izmir` (`İzmir'e` too).
  Write `izmir` for the written form.
- **`custom_ngrams` in English: `izmir` matches `İzmir`.** Python lowercases `İ` to `i` plus a
  combining dot, so the two did not match. The dot is dropped in n-gram matching only; other
  English features still lowercase as before.
- **`hdd` citation** names both primary sources: the computation is McCarthy & Jarvis's
  (2007, pp. 465-466) ATTR-42; the name HD-D and the 42-word sample come from McCarthy &
  Jarvis (2010, p. 383), who report the sum of probabilities (0-42), which the library divides
  by 42. It was a secondary citation, so secondary citations go from 14 to 13 (Turkish 13 → 12).
  The value does not change.
- **Threshold calibration re-measured with 0.3.0:** Turkish columns now give 198,225 sentences
  (was 197,990) under 0.3.0's sentence rule; the thresholds (TR 4/17, EN 8/32) do not change.
- **`sichel_s` citation** is now Tweedie & Baayen (1998) p.329, eq. (12); the ratio does not
  appear in Sichel (1975). The value does not change.
- **Group names.** `phonetic` is now `phonological` and `syntactic_dep` is now `syntactic`;
  the old names are not kept and raise `ValueError`. The 0.2.0 `syntactic` group is gone and
  its seven features moved by content: `pronoun_ratio`, `verb_dist_mean`, `activity_ratio`,
  `posddev`, `posdiv` → `pos`; `lexical_density` → `lexical`; `question_sent_ratio` →
  `sentence`. **`groups=["syntactic"]` now returns the dependency features** (dependency
  distance, hierarchical distance, sentence-final word class). The four Zipf measures
  (`zipf_exponent`, `zipf_r2`, `zipf_mandelbrot_q`, `zipf_mandelbrot_s`) moved from `lexical`
  to `frequency_structure`; they are still computed on word forms. Key names and values do
  not change.
- **Group labels** (`describe_feature(key)["group_label"]`): Lexical richness & frequency,
  Frequency structure, Sentence features, Paragraph structure, Parts of speech, Syntactic
  features, Morphological features (spaCy), Morphological features (Zeyrek), Phonological
  features, Readability, Punctuation & orthography, Character frequencies, User-defined
  n-grams.
- **`describe_feature(key)["inputs"]`** lists the fields that feature reads, not its group's:
  `mattr` reads `raw_text` only.
- **`thematic_concentration` and `secondary_thematic_concentration`** count the same lexical
  words as `lexical_density` (NOUN, PROPN, VERB, ADJ, ADV); they left out ADV. QUITA leaves
  the choice of thematic words to the researcher (pp. 50-51). Values change.
- **A double quote is punctuation when a word's tag is chosen.** spaCy sometimes tags an
  opening quote NOUN or ADJ (`Herkes "büyük" bir…`); the word then took the quote's tag.
  `"` `“` `”` `«` `»` are now skipped whatever their tag. Apostrophes are not affected, nor
  are punctuation counts. Part-of-speech shares change slightly.
- **A colon followed by an attached dash ends a sentence** (`: -Bence`), as the documented
  rule says; spaCy keeps `-Bence` as one token and the rule looked only at its capital
  letter. Sentence counts, sentence features and readability scores can change.
- **`zeyrek_verb_suffix_diversity`** follows Brezina & Pallotti (2019, pp. 107-108): the mean
  number of distinct suffix types in 100 random samples of 10 verbs (no verb repeated within a
  sample), instead of consecutive chunks of 50 verbs. It measures only the within-sample
  variety (close to MC10a). A text needs 10 verbs instead of 50. Values change.
- **`heaps_beta`** is measured at 20 equally spaced points through the text (Tweedie & Baayen
  1998, p. 333) instead of every 50 words, with no minimum length; texts shorter than 20 words
  give `nan` (it needed 300 words). The law fits large collections well and is not reliable on
  short texts (Manning et al. 2008, p. 81). Values change.
- **Verification report.** The 🔧 "derivative" class is split into 🔧 tool-specific
  (`punct_entropy`, `sent_len_entropy`, `polysyllabic_word_ratio`) and 📐 calibrated
  (`short_sent_ratio`, `long_sent_ratio`). English names of the feature types: literature
  measure, plain definition (was "no source"), tag ratio (was "tag scheme"), tool-specific,
  calibrated; the ✅ status is "match" (was "exact"). QUITA's `ttr` on Text 2 (printed 0.59,
  its own counts give 121/202 = 0.599: the source truncated instead of rounding) is ✅ under the arithmetic rule. The two Ateşman
  formula rows are labelled as the easiest and hardest texts Ateşman used to derive the
  formula. Turkish report: 61 ✅ + 0 🟡; English: 46 ✅ + 2 🟡; no ❌.
- **Citations** give the place in the source for `mattr` (p. 97), `lexical_density`
  (p. 192), `punct_entropy` and `sent_len_entropy` (Shannon 1948, Theorem 2),
  `long_word_ratio` (p. 491), `wordfreq_mean` (p. 1179) and `simpson_d` (Bestgen 2023,
  p. 4 of the preprint). Bibliography 56 → 58 works (Brezina & Pallotti 2019, Kalyoncu 2025).
- **Turkish documentation** uses the thesis terms: tümce, sözcük, türce, sözlükbirim, seslem,
  derlem, bağımlılık, alanyazın, öznitelik dizini, yalın tanım, etiket oranı, örtüşen,
  çözümleme hattı (was "boru hattı").
- **Documentation in both languages:** each Turkish page gives a term's English equivalent
  where it first appears ("türce (İng. *token*)"); the Turkish and English glossaries follow
  the thesis glossary and the English one gains a Turkish column. "öbek" is now "sözcük
  dizisi", "kütüphane" mostly "araç", "fiil" "eylem".
- **New documentation sections:** the five feature types with their counts; the four
  pipeline stages and how many features depend on spaCy and Zeyrek; the counting rules of
  the readability formulas; why the colon rule exists; constants taken from sources and not
  tested on Turkish (MTLD 0.72, HD-D 42, Brunet 0.172); the Turkish model's reported accuracy,
  split words; why `nan` and not zero; where each sentence threshold
  falls in the other language; a summary of how much of the tool could be checked against
  published numbers.
- The concepts page defines the content word (`NOUN`, `PROPN`, `VERB`, `ADJ`, `ADV`) and
  says how it differs from Lu (2012, p. 192): Lu counts only adverbs derived from adjectives,
  the tool counts all adverbs because the tagger does not tell adverb types apart. The
  definition itself is unchanged.
- The threshold calibration documents say how short and long sentences are counted (shorter
  / longer than the threshold; a sentence of exactly the threshold is in neither) and why, and
  give 137 Turkish columnists instead of 162 (the same author was spelled differently across
  corpora).

### Removed

- `ari`, `coleman_liau` and `lix` from the Turkish feature set: a readability formula is
  computed only in the language it was built for. They stay in English. `long_word_ratio`, a
  descriptive measure, stays in both languages.
- `FeatureParams.heaps_min_tokens` and `FeatureParams.heaps_step` (passing them now raises
  `TypeError`); `verb_suffix_window` defaults to 10 instead of 50.

## [0.2.0] - 2026-10-13

This release renames and removes feature keys; tables built with 0.1.0 will not line up
column for column. Keys: Turkish 208 (the same number, not the same keys), English 180 → 181. Cited features: Turkish
141 → 197, English 116 → 170; 11 keys in each language are plain definitions without a source.

### Added

- The package is on PyPI: `pip install turkish-linguistic-features`. The language data
  is still installed separately.
- Nine counts. `lexical`: `word_count` (words by the library's word), `type_count` (V),
  `hapax_count` (V1, words occurring once) and `dislegomena_count` (V2, twice); `sentence`:
  `sent_count`; `paragraph`: `para_count`; `phonetic`: `syllable_count`; `punctuation`:
  `char_count` (whitespace included) and `punct_count` (marks). Divide other counts by them
  to compare texts of different length. Citations: de Vel (2000) Table 2, attributes 1, 3 and
  8; Zheng et al. (2006) Table 3, nos. 1, 54, 60–62, 247 and 248; Tweedie & Baayen (1998)
  pp.325 and 329; de Vel et al. (2001) Table 2; Kincaid et al. (1975) p.38.
- `ngram_matches(text, phrase, lang="tr")`: what one `custom_ngrams` phrase matched, with
  counts, most frequent first: `{"eski ev": 2, "büyük bahçe": 1}`. The matching is the
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

- `analyze_corpus` still stops at the first segment it cannot analyse, but the `ValueError` now
  names that segment's `label`, `source` and `segment_id`; the original error is its `__cause__`.
- Python 3.13 is tested in CI and listed in the package classifiers.
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
  sentences. `sents_per_para_mean` is now `sent_count` / `para_count`; it counted runs of
  `.!?…` in each paragraph, so `Dr.` ended a sentence. The readability formulas use the same conditional colon (Kincaid's rule too);
  the Çetinkaya rule keeps its source's unconditional `:`, and `syntactic_dep` keeps the
  parser.
- **Sentence-length thresholds** are calibrated on newspaper columns with the rules above
  (15th/85th percentile; Turkish 162 columnists / 197,990 sentences, English 30 columnists /
  52,745 sentences): Turkish 4/18 → 4/17, English 7/39 → 8/32.
- **`segment_text` and `analyze_corpus(segment_size=...)` count words**, the same word
  `analyze` counts: a `segment_size=1000` segment is exactly 1000 words. They used to count
  spaCy tokens, punctuation included (100 tokens were about 83 words). Segment boundaries
  change.
- **`segment_text(size=...)` is now `segment_text(segment_size=...)`**, the name
  `analyze_corpus` already uses for the same thing. Passing `size=` raises `TypeError`.
- **Punctuation shares.** The ten `punct_*_ratio` keys are each mark type's share of all
  punctuation marks (0-1, summing to 1), no longer marks per word, which could exceed 1. How
  much punctuation a text has is `punct_char_ratio`. A text without punctuation gives `nan`.
- **`custom_ngrams`** keys are `ngram_{...}_count` and the value is the number of matches, not
  matches per window. A phrase item written as an UPPERCASE UD tag (`NOUN`, `VERB` …) matches
  any word with that tag: `["ADJ", "NOUN"]` counts an adjective followed by a noun. Matches stay
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
  (`pip install 'wordfreq>=3.0'`), not an extra of this package.
- Registry and documentation texts: three descriptions ran words together, the parameter
  guide showed `params` as a list (it is a tuple), the `analyze` docstring example gave 3.5
  for a mean of 3.0, four bibliography entries had Turkish fragments.
- The limitations page says that Zeyrek's first analysis can differ between Python runs and
  that `PYTHONHASHSEED=0` makes the numbers reproducible.

## [0.1.0] - 2026-09-28

### Added

- Initial public release.
