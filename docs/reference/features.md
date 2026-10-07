<!-- GENERATED FILE — do not edit by hand.
     Source: scripts/generate_feature_reference.py
     To regenerate:
       python scripts/generate_feature_reference.py -->

# Feature reference

Every feature the library can produce, grouped as it is grouped in the code.
This page is **generated from the registry**, so it cannot fall out of step
with what `describe_feature()` returns.

**Reading the columns**

| Column | Meaning |
|---|---|
| Key | The `dict` key `analyze()` returns |
| Description | One-sentence definition |
| Formula | The computation, in words |
| Requires | Minimum data needed; below it the feature returns `nan`. A "word" is any token that is not punctuation or a symbol |
| Source | Short citation. `—` means it is not a named measure from the literature |

Whether a feature's number has been checked against the number its source
published is a separate question — see the
[verification report](../verification-report.md).

## Groups

| Group | Keys | What it covers |
|---|---|---|
| `lexical` | 34 | Lexical richness & frequency |
| `frequency_structure` | 13 | Frequency structure (h-point family, Popescu & Altmann) |
| `sentence` | 7 | Sentence statistics |
| `paragraph` | 3 | Paragraph structure |
| `pos` | 12 | Part-of-speech ratios |
| `syntactic` | 9 | Discourse & syntax |
| `syntactic_dep` | 16 | Dependency tree (distance, depth, sentence-final POS) |
| `morphological` | 19 | Morphological style (spaCy) |
| `morphological_zeyrek` | 24 | Morphological style (Zeyrek, TR only) |
| `phonetic` | 13 | Phonetic patterns |
| `readability` | 11 | Readability scores |
| `punctuation` | 19 | Punctuation & digits |
| `chars` | dynamic | Character frequency vector  [dynamic: one key per letter — TR 29, EN 26] |
| `custom_ngrams` | dynamic | User-defined n-gram ratios  [dynamic: ng_{...}] |


## `lexical` — Lexical richness & frequency

34 keys.

| Key | Description | Formula | Requires | Source |
|---|---|---|---|---|
| `n_lemma_count` | number of distinct lemmas | `V over lemmas` | at least 1 word | — |
| `avg_word_length` | mean word length in characters | `sum(len(w)) / N` | at least 1 word | Mendenhall (1887) p.237 "mean word-length"; computed as letters per word, p.241 |
| `ttr` | type-token ratio; falls as the text grows | `V / N` | at least 1 word | Malvern et al. (2004); QUITA §6.1.1 |
| `mattr` | moving-average TTR | `mean TTR of every sliding window of mattr_window words` | at least 100 words (2 x mattr_window) | Covington & McFall (2010); default window 50 — C&M recommend a window of 500; 50 is used here so that texts of 100+ words can be measured (mattr needs 2 × window) |
| `entropy_std` | how much word entropy varies across the text | `population std of entropies (nats) of disjoint mattr_window-word chunks` | at least 100 words (2 x mattr_window) | Shannon (1948) — the entropy formula; the standard deviation across segments is this library's own derivation |
| `herdan_c` | Herdan's C (LogTTR) | `log(V) / log(N)` | at least 2 words | Herdan (1960/1964), as cited in Tweedie & Baayen (1998) p.327, eq. (5) |
| `sichel_s` | share of types occurring exactly twice | `V2 / V` | at least 1 word | Sichel (1975); formula from Malvern et al. (2004) eq. 3.10 |
| `zipf_exponent` | Zipf slope | `abs(slope) of least-squares fit log f(r) ~ log r` | at least 10 distinct words | Piantadosi (2014) eq. (2); the same source criticises estimating r and f(r) from the same corpus |
| `zipf_r2` | fit quality of the Zipf line | `R² of that fit` | at least 10 distinct words, not all equally frequent | Piantadosi (2014) eq. (2); the same source criticises estimating r and f(r) from the same corpus |
| `zipf_mandelbrot_q` | Zipf-Mandelbrot shift | `q minimising the residual of log f ~ log(r + q), grid 0–10 step 0.1` | at least 10 distinct words | Piantadosi (2014) eq. (2); the same source criticises estimating r and f(r) from the same corpus |
| `zipf_mandelbrot_s` | Zipf-Mandelbrot slope | `abs(slope) at that q` | at least 10 distinct words | Piantadosi (2014) eq. (2); the same source criticises estimating r and f(r) from the same corpus |
| `mtld` | measure of textual lexical diversity | `mean words per factor (TTR drops to mtld_threshold), forward and backward averaged` | at least 100 words (mtld_min_tokens) with some repetition | McCarthy (2005) is the dissertation that introduced the measure — its abstract (p.vii) reads "we introduce and test a new measure of lexical diversity: the measure of textual, lexical diversity (MTLD)"; the body of the dissertation could not be obtained, so no page is given. The procedure implemented follows McCarthy & Jarvis (2010) pp.383–385 |
| `dugast_u` | Dugast's Uber index | `(ln N)^2 / (ln N - ln V)` | at least 2 words, at least one repeated | Dugast (1978), as cited in Malvern et al. (2004) eq. 2.7 |
| `guiraud_r` | Guiraud's root TTR | `V / sqrt(N)` | at least 1 word | Guiraud (1954) p.53, alternative form (all word types), as cited in Daller (2010); his actual law is V/√(2N), content words only |
| `cttr` | Carroll's corrected TTR | `V / sqrt(2N)` | at least 1 word | Carroll (1964), as cited in Torruella & Capsada (2013) p.448 |
| `summer_s` | Summer's S, log-log type-token ratio | `ln(ln V) / ln(ln N)` | at least 3 words and 2 distinct words | Somers (1966), as cited in Torruella & Capsada (2013) p.448, where it is named "Summer"; the source gives no logarithm base, the natural logarithm is this library's choice |
| `maas_a2` | Maas' a²; higher = more repetitive | `(ln N - ln V) / (ln N)^2` | at least 2 words | Maas (1972), as cited in Tweedie & Baayen (1998) p.327, eq. (7); natural logarithm, which reproduces the values in Torruella & Capsada (2013) Table 1; all logarithms in this library are natural |
| `herdan_vm` | Herdan's Vm; higher = more repetitive | `sqrt(sum(f^2) / N^2 - 1 / V)` | at least 1 word | Herdan (1955), as cited in Tweedie & Baayen (1998) p.330, eq. (18) |
| `heaps_beta` | vocabulary growth rate | `least-squares slope of log V ~ log N over prefixes every heaps_step words, not clipped` | at least 300 words (heaps_min_tokens) | Heaps (1978), as cited in Manning et al. (2008) §5.1.1 |
| `entropy` | Shannon entropy of word frequencies | `-sum(p * ln p)` | at least 1 word | Shannon (1948), as cited in QUITA §6.1.12 |
| `yule_k` | Yule's K; higher = more repetitive | `10000 * (sum(f^2) - N) / N^2` | at least 1 word | Yule (1944) p.53, eq. (3.22) |
| `simpson_d` | chance that two words drawn without replacement are the same type | `sum(f(f-1)) / (N(N-1))` | at least 2 words | Simpson (1949), as cited in Bestgen (2023) |
| `brunet_w` | Brunet's W | `N^(V^-a), a = brunet_w_a` | at least 1 word | Brunet (1978), as cited in Tweedie & Baayen (1998) p.328, eq. (10) |
| `hapax_ratio` | share of types occurring once | `V1 / V` | at least 1 word | de Vel (2000) Table 2, attribute 14 "Ratio of words used once to total number of vocabulary words" |
| `hapax_percentage` | share of tokens that occur once | `V1 / N` | at least 1 word | QUITA §6.1.6 |
| `vocd_d` | voc-D | `D fitted to mean TTR of random samples of vocd_sample_min–vocd_sample_max words, vocd_num_runs runs averaged` | at least 50 words (vocd_min_tokens, vocd_sample_max) | Malvern et al. (2004) pp.56–57; procedure from McCarthy & Jarvis (2010) p.383 |
| `hdd` | HD-D | `expected TTR of a hdd_sample_size-word sample (hypergeometric)` | at least 42 words (hdd_sample_size) | McCarthy & Jarvis (2007), as cited in McCarthy & Jarvis (2010) p.383 |
| `msttr` | mean segmental TTR | `mean TTR of full msttr_segment_size-word segments` | at least 100 words (msttr_segment_size) | Johnson (1944), as cited in Malvern et al. (2004) p.25 and McCarthy & Jarvis (2010) p.385 |
| `noun_variation` | noun variation NV | `distinct noun lemmas / lexical words` | at least 1 lexical word (NOUN, PROPN, VERB, ADJ, ADV) | Lu (2012) Table 2 |
| `verb_variation` | verb variation VV1 | `distinct verb lemmas / verbs` | at least 1 verb | Lu (2012) Table 2 |
| `adj_variation` | adjective variation AdjV | `distinct adjective lemmas / lexical words` | at least 1 lexical word | Lu (2012) Table 2 |
| `adv_variation` | adverb variation AdvV | `distinct adverb lemmas / lexical words` | at least 1 lexical word | Lu (2012) Table 2 |
| `wordfreq_mean` | how common the lexical words are in general language | `mean wordfreq Zipf score of lexical-word lemmas (unlisted = 0)` | at least 1 lexical word; wordfreq installed | van Heuven et al. (2014) (Zipf scale) |
| `wordfreq_rare_ratio` | share of rare lexical words | `lexical-word lemmas with Zipf score <= 3 / lexical words` | at least 1 lexical word; wordfreq installed | van Heuven et al. (2014) Table 1 (Zipf ≤ 3 = low frequency) |

## `frequency_structure` — Frequency structure (h-point family, Popescu & Altmann)

13 keys.

| Key | Description | Formula | Requires | Source |
|---|---|---|---|---|
| `h_point` | rank where frequency equals rank | `r with f(r) = r, interpolated otherwise` | at least 1 word | QUITA §6.1.2; Popescu & Altmann (2006) |
| `vocab_richness_r1` | share of the text below the h-point | `1 - (F(h) - h^2 / (2N))` | at least 1 word | Popescu et al. (2009) eq. 3.8 |
| `vocab_richness_r4` | inverted Gini | `1 - G` | at least 1 word | Popescu et al. (2009) eq. 3.24 |
| `repeat_rate` | chance that two words drawn with replacement are the same type | `sum((f/N)^2)` | at least 1 word | QUITA §6.1.4 |
| `rr_mcintosh` | McIntosh relative repeat rate | `(1 - sqrt(RR)) / (1 - 1/sqrt(V))` | at least 2 distinct words | QUITA §6.1.5 |
| `gini_coef` | inequality of word use | `(V + 1 - 2 * sum(r * f(r)) / N) / V, rank 1 = most frequent` | at least 1 word | QUITA §6.1.8 |
| `curve_length` | arc length of the rank-frequency curve | `sum(sqrt((f(r) - f(r+1))^2 + 1))` | at least 1 word | QUITA §6.1.10 |
| `curve_length_r` | share of the curve length below the h-point | `1 - L(h) / L` | at least 2 distinct words | QUITA §6.1.11 |
| `lambda_pa` | length-normalised curve length | `L * ln(N) / N` | at least 1 word | QUITA §6.1.7; Popescu, Čech & Altmann (2011) |
| `adjusted_modulus` | distance from the h-point to the curve ends | `sqrt((f1/h)^2 + (V/h)^2) / ln(N)` | at least 2 words | QUITA §6.1.13 |
| `writers_view_alpha` | angle at the h-point, in radians | `arccos of the angle between (1, f1) and (V, 1) seen from (h, h)` | at least 1 word; undefined when the h-point meets a curve end | Popescu, Mačutek & Altmann (2009) eq. 4.5 |
| `thematic_concentration` | weight of content words above the h-point | `sum(2(h - r') f(r')) / (h(h-1) f1), content words with r' < h` | at least one repeated word | QUITA §6.2.5 |
| `secondary_thematic_concentration` | same, up to rank 2h | `sum((2h - r') f(r')) / (h(2h-1) f1), r' <= 2h` | at least 1 word | QUITA §6.2.6 |

## `sentence` — Sentence statistics

7 keys.

| Key | Description | Formula | Requires | Source |
|---|---|---|---|---|
| `avg_sent_len_word` | mean sentence length in words | `mean words per sentence` | at least 1 sentence with a letter | Flesch (1948) p.223, element (1) "Average Sentence Length in Words" |
| `avg_sent_len_char` | mean sentence length in characters | `mean len(tokens joined by single spaces)` | at least 1 sentence | Zheng et al. (2006) Table 3, p.384, no. 58 "Average sentence length in terms of character" |
| `sent_len_skewness` | skew of sentence length; positive = long-sentence tail | `Fisher-Pearson g1 = m3 / m2^1.5 over words per sentence` | at least 2 sentences of different length | — |
| `short_sent_ratio` | share of short sentences | `sentences with fewer than short_sent_threshold words / sentences` | at least 1 sentence with a letter | This library's threshold calibration (docs/threshold-calibration.md); TR 4, EN 8 — 15th percentile of newspaper columns under the default sentence and word rules. Note: the TR value coincides with Ateşman (1997) p.74, where the easiest text has a mean sentence length of 4 words; that is a text mean, not a threshold, so it is not the source. Calibrated on newspaper columns only |
| `long_sent_ratio` | share of long sentences | `sentences with more than long_sent_threshold words / sentences` | at least 1 sentence with a letter | This library's threshold calibration (docs/threshold-calibration.md); TR 17, EN 32 — 85th percentile of newspaper columns under the default sentence and word rules. Ateşman's 30 was not used: that is the mean of the hardest text, not a single-sentence threshold (in Turkish newspaper columns 30 words is above the 95th percentile, so as a threshold it would almost never fire). Calibrated on newspaper columns only |
| `med_sent_len` | median sentence length | `median words per sentence` | at least 1 sentence with a letter | Yule (1939) p.369, median sentence length alongside the mean |
| `sent_len_entropy` | variety of sentence lengths | `Shannon entropy (nats) of the distribution of words per sentence` | at least 2 sentences with a letter | Shannon (1948) — the entropy formula; applying it to the distribution of sentence lengths is this library's own decision |

## `paragraph` — Paragraph structure

3 keys.

| Key | Description | Formula | Requires | Source |
|---|---|---|---|---|
| `para_len_mean` | mean paragraph length | `mean words per paragraph (blank line = boundary)` | at least 1 paragraph | Zheng et al. (2006) Table 3, p.384, no. 251 "Number of words per paragraph" |
| `sents_per_para_mean` | mean sentences per paragraph | `mean count of [.!?…]+ per paragraph (at least 1)` | at least 1 paragraph | Zheng et al. (2006) Table 3, p.384, no. 249 "Number of sentences per paragraph" |
| `para_count_norm` | paragraphs per 1000 words | `paragraphs / words * 1000` | at least 1 paragraph | — |

## `pos` — Part-of-speech ratios

12 keys.

| Key | Description | Formula | Requires | Source |
|---|---|---|---|---|
| `pos_noun` | share of NOUN words | `tag count / words` | at least 1 word | de Marneffe et al. (2021) Table 1 (UPOS tag set) |
| `pos_propn` | share of PROPN words | `tag count / words` | at least 1 word | de Marneffe et al. (2021) Table 1 (UPOS tag set) |
| `pos_verb` | share of VERB words | `tag count / words` | at least 1 word | de Marneffe et al. (2021) Table 1 (UPOS tag set) |
| `pos_adj` | share of ADJ words | `tag count / words` | at least 1 word | de Marneffe et al. (2021) Table 1 (UPOS tag set) |
| `pos_adv` | share of ADV words | `tag count / words` | at least 1 word | de Marneffe et al. (2021) Table 1 (UPOS tag set) |
| `pos_det` | share of DET words | `tag count / words` | at least 1 word | de Marneffe et al. (2021) Table 1 (UPOS tag set) |
| `pos_adp` | share of ADP words | `tag count / words` | at least 1 word | de Marneffe et al. (2021) Table 1 (UPOS tag set) |
| `pos_aux` | share of AUX words | `tag count / words` | at least 1 word | de Marneffe et al. (2021) Table 1 (UPOS tag set) |
| `pos_cconj` | share of CCONJ words | `tag count / words` | at least 1 word | de Marneffe et al. (2021) Table 1 (UPOS tag set) |
| `pos_sconj` | share of SCONJ words | `tag count / words` | at least 1 word | de Marneffe et al. (2021) Table 1 (UPOS tag set) |
| `pos_num` | share of NUM words | `tag count / words` | at least 1 word | de Marneffe et al. (2021) Table 1 (UPOS tag set) |
| `pos_intj` | share of INTJ words | `tag count / words` | at least 1 word | de Marneffe et al. (2021) Table 1 (UPOS tag set) |

## `syntactic` — Discourse & syntax

9 keys.

| Key | Description | Formula | Requires | Source |
|---|---|---|---|---|
| `question_per_sent` | share of sentences ending in "?" | `sentences whose final mark contains "?" / sentences` | at least 1 sentence | — |
| `pronoun_freq` | share of pronoun words | `PRON / words` | at least 1 word | Deutsch, Jasbi & Shieber (2020) Table 6 "pronouns per word", listed among existing features; original source not traced |
| `nominal_verbal_ratio` | noun-to-verb balance | `(NOUN + PROPN) / VERB` | at least 1 verb | Wells (1960) p.214, Noun-Verb Quotient (NVQ), "the proportion of nouns to verbs in a given text"; nouns = NOUN + PROPN, verbs = VERB (the copula is left out, a choice Wells leaves open) |
| `verb_dist_mean` | mean word gap between consecutive verbs | `mean difference of VERB positions` | at least 2 verbs | QUITA §6.2.1 |
| `verb_dist_cv` | spread of verb gaps | `population std / mean of those gaps` | at least 3 verbs | QUITA §6.2.1 |
| `activity_ratio` | activity Q | `VERB / (VERB + ADJ)` | at least 1 verb or adjective | QUITA §6.2.2 |
| `lexical_density` | share of lexical words | `(NOUN + PROPN + VERB + ADJ + ADV) / all words, PUNCT and SYM excluded` | at least 1 word | Lu (2012); definition in the broad Hallidayan sense — all open-class words |
| `pos_dist_std` | how uneven the POS distribution is | `population std of the 12 pos_* shares` | at least 1 word | Deutsch, Jasbi & Shieber (2020) Definition 3.3 (POSDdev); computed over ratios, 12 UD tags |
| `pos_kl_div` | how much sentences differ from the document in POS make-up | `mean over sentences of KL(sentence POS ‖ document POS), nats` | at least 1 word | Deutsch, Jasbi & Shieber (2020) Definition 3.4 (POSdiv); natural logarithm (nats), the source uses bits |

## `syntactic_dep` — Dependency tree (distance, depth, sentence-final POS)

16 keys.

| Key | Description | Formula | Requires | Source |
|---|---|---|---|---|
| `arc_len_mean` | mean dependency distance (MDD2) | `mean over sentences of mean abs(word position - head position), punctuation removed, root excluded` | at least 1 sentence with 2 words | Liu (2008) eq. (1); text level from Jing & Liu (2015) p.164, eq. (3) (MDD2) |
| `parse_depth_mean` | mean hierarchical distance (MHD2) | `mean over sentences of mean steps to the root, capped at max_parse_depth` | at least 1 sentence with 2 words | Jing & Liu (2015) p.164, eq. (2) and (4) (MHD2) |
| `sentfinal_noun` | share of sentences ending in a NOUN | `sentences ending in that tag / sentences` | at least 1 sentence with a word | de Marneffe et al. (2021) Table 1 (UPOS tag set) |
| `sentfinal_propn` | share of sentences ending in a PROPN | `sentences ending in that tag / sentences` | at least 1 sentence with a word | de Marneffe et al. (2021) Table 1 (UPOS tag set) |
| `sentfinal_verb` | share of sentences ending in a VERB | `sentences ending in that tag / sentences` | at least 1 sentence with a word | de Marneffe et al. (2021) Table 1 (UPOS tag set) |
| `sentfinal_adj` | share of sentences ending in a ADJ | `sentences ending in that tag / sentences` | at least 1 sentence with a word | de Marneffe et al. (2021) Table 1 (UPOS tag set) |
| `sentfinal_adv` | share of sentences ending in a ADV | `sentences ending in that tag / sentences` | at least 1 sentence with a word | de Marneffe et al. (2021) Table 1 (UPOS tag set) |
| `sentfinal_det` | share of sentences ending in a DET | `sentences ending in that tag / sentences` | at least 1 sentence with a word | de Marneffe et al. (2021) Table 1 (UPOS tag set) |
| `sentfinal_adp` | share of sentences ending in a ADP | `sentences ending in that tag / sentences` | at least 1 sentence with a word | de Marneffe et al. (2021) Table 1 (UPOS tag set) |
| `sentfinal_intj` | share of sentences ending in a INTJ | `sentences ending in that tag / sentences` | at least 1 sentence with a word | de Marneffe et al. (2021) Table 1 (UPOS tag set) |
| `sentfinal_cconj` | share of sentences ending in a CCONJ | `sentences ending in that tag / sentences` | at least 1 sentence with a word | de Marneffe et al. (2021) Table 1 (UPOS tag set) |
| `sentfinal_sconj` | share of sentences ending in a SCONJ | `sentences ending in that tag / sentences` | at least 1 sentence with a word | de Marneffe et al. (2021) Table 1 (UPOS tag set) |
| `sentfinal_num` | share of sentences ending in a NUM | `sentences ending in that tag / sentences` | at least 1 sentence with a word | de Marneffe et al. (2021) Table 1 (UPOS tag set) |
| `sentfinal_aux` | share of sentences ending in a AUX | `sentences ending in that tag / sentences` | at least 1 sentence with a word | de Marneffe et al. (2021) Table 1 (UPOS tag set) |
| `sentfinal_pron` | share of sentences ending in a PRON | `sentences ending in that tag / sentences` | at least 1 sentence with a word | de Marneffe et al. (2021) Table 1 (UPOS tag set) |
| `sentfinal_other` | share of sentences ending in any other tag | `same, tags outside the 13` | at least 1 sentence with a word | de Marneffe et al. (2021) Table 1 (UPOS tag set) |

## `morphological` — Morphological style (spaCy)

19 keys.

| Key | Description | Formula | Requires | Source |
|---|---|---|---|---|
| `surface_per_lemma` | distinct forms per lemma | `distinct (lemma, form) pairs / distinct lemmas, lowercased` | at least 1 word | de Marneffe et al. (2021) Table 2 (universal morphological features) |
| `morph_tense_past` | share of words tagged Tense=Past | `words with Tense=X / words with any Tense` | at least 1 word with a Tense tag | de Marneffe et al. (2021) Table 2 (universal morphological features) |
| `morph_tense_pres` | share of words tagged Tense=Pres | `words with Tense=X / words with any Tense` | at least 1 word with a Tense tag | de Marneffe et al. (2021) Table 2 (universal morphological features) |
| `morph_tense_fut` | share of words tagged Tense=Fut | `words with Tense=X / words with any Tense` | at least 1 word with a Tense tag | de Marneffe et al. (2021) Table 2 (universal morphological features) |
| `morph_aspect_perf` | share of words tagged Aspect=Perf | `same with Aspect` | at least 1 word with an Aspect tag | de Marneffe et al. (2021) Table 2 (universal morphological features) |
| `morph_aspect_imp` | share of words tagged Aspect=Imp | `same with Aspect` | at least 1 word with an Aspect tag | de Marneffe et al. (2021) Table 2 (universal morphological features) |
| `morph_aspect_prog` | share of words tagged Aspect=Prog | `same with Aspect` | at least 1 word with an Aspect tag | de Marneffe et al. (2021) Table 2 (universal morphological features) |
| `morph_case_nom` | share of words tagged Case=Nom | `same with Case` | at least 1 word with a Case tag | de Marneffe et al. (2021) Table 2 (universal morphological features) |
| `morph_case_acc` | share of words tagged Case=Acc | `same with Case` | at least 1 word with a Case tag | de Marneffe et al. (2021) Table 2 (universal morphological features) |
| `morph_case_dat` | share of words tagged Case=Dat | `same with Case` | at least 1 word with a Case tag | de Marneffe et al. (2021) Table 2 (universal morphological features) |
| `morph_case_loc` | share of words tagged Case=Loc | `same with Case` | at least 1 word with a Case tag | de Marneffe et al. (2021) Table 2 (universal morphological features) |
| `morph_case_abl` | share of words tagged Case=Abl | `same with Case` | at least 1 word with a Case tag | de Marneffe et al. (2021) Table 2 (universal morphological features) |
| `morph_case_gen` | share of words tagged Case=Gen | `same with Case` | at least 1 word with a Case tag | de Marneffe et al. (2021) Table 2 (universal morphological features) |
| `morph_person_1` | share of words tagged Person=1 | `same with Person` | at least 1 word with a Person tag | de Marneffe et al. (2021) Table 2 (universal morphological features) |
| `morph_person_2` | share of words tagged Person=2 | `same with Person` | at least 1 word with a Person tag | de Marneffe et al. (2021) Table 2 (universal morphological features) |
| `morph_person_3` | share of words tagged Person=3 | `same with Person` | at least 1 word with a Person tag | de Marneffe et al. (2021) Table 2 (universal morphological features) |
| `morph_number_sing` | share of words tagged Number=Sing | `same with Number` | at least 1 word with a Number tag | de Marneffe et al. (2021) Table 2 (universal morphological features) |
| `morph_number_plur` | share of words tagged Number=Plur | `same with Number` | at least 1 word with a Number tag | de Marneffe et al. (2021) Table 2 (universal morphological features) |
| `morph_voice_pass` | share of passive verbs | `VERB with Voice=Pass / VERB` | at least 1 verb | de Marneffe et al. (2021) Table 2 (universal morphological features) |

## `morphological_zeyrek` — Morphological style (Zeyrek, TR only)

24 keys.

| Key | Description | Formula | Requires | Source |
|---|---|---|---|---|
| `agglutination_depth` | visible suffixes per word | `visible suffixes / analysed words` | at least 1 analysed word | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) |
| `suffix_char_length_ratio` | share of word letters in suffixes | `suffix letters / word letters` | at least 1 analysed word | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) |
| `suffix_bigram_entropy` | variety of suffix sequences | `Shannon entropy (nats) of within-word visible suffix pairs` | at least 1 word with 2 visible suffixes | Shannon (1948) — the entropy formula; Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) |
| `derivational_suffix_ratio` | share of derivational suffixes | `derivational / visible suffixes` | at least 1 visible suffix | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) |
| `verb_suffix_diversity` | suffix variety on verbs | `mean distinct visible suffix tags per verb_suffix_window-verb chunk` | at least 50 verbs (verb_suffix_window) | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) |
| `tense_past_def` | share of verbs in the definite past (-DI) | `verbs whose last tense tag is X / verbs` | at least 1 verb | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) |
| `tense_past_nar` | share of verbs in the reported past (-mIş) | `verbs whose last tense tag is X / verbs` | at least 1 verb | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) |
| `tense_present` | share of verbs in the present | `verbs whose last tense tag is X / verbs` | at least 1 verb | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) |
| `tense_future` | share of verbs in the future (-AcAk) | `verbs whose last tense tag is X / verbs` | at least 1 verb | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) |
| `negation_ratio` | share of negative verbs | `verbs with Neg or Unable / verbs` | at least 1 verb | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) |
| `passive_ratio` | share of passive verbs | `verbs with Pass / verbs` | at least 1 verb | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) |
| `plural_ratio` | share of plural nominals | `words with A3pl on a non-verb part / analysed words` | at least 1 analysed word | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) |
| `case_acc_ratio` | share of words in the accusative case | `words with Acc … Ins / analysed words` | at least 1 analysed word | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) |
| `case_dat_ratio` | share of words in the dative case | `words with Acc … Ins / analysed words` | at least 1 analysed word | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) |
| `case_loc_ratio` | share of words in the locative case | `words with Acc … Ins / analysed words` | at least 1 analysed word | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) |
| `case_abl_ratio` | share of words in the ablative case | `words with Acc … Ins / analysed words` | at least 1 analysed word | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) |
| `case_gen_ratio` | share of words in the genitive case | `words with Acc … Ins / analysed words` | at least 1 analysed word | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) |
| `case_ins_ratio` | share of words in the instrumental case | `words with Acc … Ins / analysed words` | at least 1 analysed word | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) |
| `conditional_suffix_ratio` | share of conditional verbs | `verbs with Cond / verbs` | at least 1 verb | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) |
| `causative_suffix_ratio` | share of causative verbs | `verbs with Caus / verbs` | at least 1 verb | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) |
| `suffix_chain_cv` | spread of suffix-chain length | `population std / mean of visible suffixes per word` | at least 2 analysed words, at least 1 suffix | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) |
| `modal_possibility_ratio` | share of ability verbs | `verbs with Able or Unable / verbs` | at least 1 verb | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) |
| `modal_necessity_ratio` | share of necessity verbs | `verbs with Neces / verbs` | at least 1 verb | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) |
| `question_particle_ratio` | share of question particles | `words with root Ques / analysed words` | at least 1 analysed word | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) |

## `phonetic` — Phonetic patterns

13 keys.

| Key | Description | Formula | Requires | Source |
|---|---|---|---|---|
| `vowel_ratio` | share of vowels | `vowels / alphabet letters` | at least 1 alphabet letter | — |
| `front_vowel_ratio` | share of front vowels | `front vowels / alphabet letters` | at least 1 alphabet letter | Göksel & Kerslake (2005) ch. 2 (the vowel system, front/back) |
| `back_vowel_ratio` | share of back vowels | `back vowels / alphabet letters` | at least 1 alphabet letter | Göksel & Kerslake (2005) ch. 2 (the vowel system, front/back) |
| `harmony_fronting_ratio` | share of words obeying front/back vowel harmony (TR only) | `words whose vowels are all front or all back / words with 2+ vowels` | at least 1 word with 2 vowels | Göksel & Kerslake (2005) §3.1 (fronting harmony); exceptions §3.4 — the measure counts them as disharmonic |
| `harmony_rounding_ratio` | share of words obeying rounding vowel harmony (TR only) | `words where every vowel after an unrounded one is unrounded and every vowel after a rounded one is close-rounded or open-unrounded / words with 2+ vowels` | at least 1 word with 2 vowels | Göksel & Kerslake (2005) §3.1 (rounding harmony); strictly a suffix phenomenon, measured here as a whole-word pattern |
| `syllable_mean` | mean syllables per word | `mean syllables per syllabifiable word` | at least 1 syllabifiable word | Flesch (1948) Formula A, wl; unit there = syllables per 100 words, here per word |
| `syllable_1_ratio` | share of words with 1 syllable | `words with 1 syllable / syllabifiable words` | at least 1 syllabifiable word | Bezirci & Yılmaz (2010) Table 1-c |
| `syllable_2_ratio` | share of words with 2 syllables | `words with 2 syllables / syllabifiable words` | at least 1 syllabifiable word | Bezirci & Yılmaz (2010) Table 1-c |
| `syllable_3_ratio` | share of words with 3 syllables | `words with 3 syllables / syllabifiable words` | at least 1 syllabifiable word | Bezirci & Yılmaz (2010) Table 1-c |
| `syllable_4_ratio` | share of words with 4 syllables | `words with 4 syllables / syllabifiable words` | at least 1 syllabifiable word | Bezirci & Yılmaz (2010) Table 1-c |
| `syllable_5_ratio` | share of words with 5 syllables | `words with 5 syllables / syllabifiable words` | at least 1 syllabifiable word | Bezirci & Yılmaz (2010) Table 1-c |
| `syllable_6plus_ratio` | share of words with 6 or more syllables | `words with 6 or more syllables / syllabifiable words` | at least 1 syllabifiable word | Bezirci & Yılmaz (2010) Table 1-c |
| `sentence_syllable_mean` | syllables per sentence | `mean syllables per sentence` | at least 1 sentence with a syllabifiable word | — |

## `readability` — Readability scores

11 keys.

| Key | Description | Formula | Requires | Source |
|---|---|---|---|---|
| `bezirci_yilmaz` | Bezirci-Yılmaz; higher = harder | `sqrt(words/sentence * (0.84 H3 + 1.5 H4 + 3.5 H5 + 26.25 H6)), Hk per sentence` | at least 1 syllabifiable word | Bezirci & Yılmaz (2010) p.371, eq. (9) |
| `atesman` | Ateşman; higher = easier | `198.825 - 40.175 * syllables/word - 2.610 * words/sentence` | at least 1 syllabifiable word | Ateşman (1997) p.74, eq. (2) |
| `cetinkaya_uzun` | Çetinkaya-Uzun; higher = easier | `118.823 - 25.987 * syllables/word - 0.971 * words/sentence; ": ( )" end sentences` | at least 1 syllabifiable word | Çetinkaya (2010) p.85; counting rules p.93 |
| `flesch_reading_ease` | Flesch Reading Ease (EN) | `206.835 - 1.015 * words/sentence - 84.6 * syllables/word` | at least 1 syllabifiable word | Flesch (1948) Formula A; coefficient .846, unit = syllables per 100 words |
| `flesch_kincaid_grade` | Flesch-Kincaid grade (EN) | `0.39 * words/sentence + 11.8 * syllables/word - 15.59` | at least 1 syllabifiable word | Kincaid et al. (1975) p.14, Table 3, "New" |
| `smog` | SMOG grade (EN) | `3.1291 + 1.0430 * sqrt(polysyllables * 30 / sentences)` | at least 30 sentences | McLaughlin (1969) p.643, Table 1, eq. (d); p = polysyllabic words in a 30-sentence sample |
| `ari` | Automated Readability Index | `4.71 * strokes/word + 0.5 * words/sentence - 21.43` | at least 1 word | Smith & Senter (1967) p.8, AMRL-TR-66-220; reproduced verbatim in Kincaid et al. (1975) p.14, Table 3 ("Old") |
| `coleman_liau` | Coleman-Liau index | `0.0588 * letters per 100 words - 0.296 * sentences per 100 words - 15.8` | at least 1 word | Coleman & Liau (1975) p.284; the formula is a composition of two equations, it does not appear in this form in the article |
| `lix` | Björnsson's LIX | `words/sentence + 100 * long words/words, long = 7+ letters` | at least 1 word | Björnsson (1968), as cited in Anderson (1983) p.490; long word = 7+ letters |
| `polysyllabic_word_ratio` | share of 3+ syllable words (EN) | `3+ syllable words / syllabifiable words` | at least 1 syllabifiable word | McLaughlin (1969) p.641; polysyllabic = 3+ syllables — the ratio form of SMOG's input, not the source's own measure |
| `long_word_ratio` | share of 7+ letter words | `long words / words` | at least 1 word | Anderson (1983); long word = 7+ letters |

## `punctuation` — Punctuation & digits

19 keys.

| Key | Description | Formula | Requires | Source |
|---|---|---|---|---|
| `digit_vs_all` | share of digit characters | `digits / characters` | non-empty text | de Vel et al. (2001) Table 2, p.60 "Total number of digit characters in words/C"; here digits anywhere in the text |
| `punc_,_ratio` | comma marks per word | `marks / words` | at least 1 word | Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); per-word normalisation is this library's |
| `punc_._ratio` | full stop marks per word | `marks / words` | at least 1 word | Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); per-word normalisation is this library's |
| `punc_;_ratio` | semicolon marks per word | `marks / words` | at least 1 word | Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); per-word normalisation is this library's |
| `punc_!_ratio` | exclamation mark marks per word | `marks / words` | at least 1 word | Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); per-word normalisation is this library's |
| `punc_:_ratio` | colon marks per word | `marks / words` | at least 1 word | Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); per-word normalisation is this library's |
| `punc_-_ratio` | hyphen or dash marks per word | `marks / words` | at least 1 word | — |
| `punc_ellipsis_ratio` | ellipsis marks per word | `marks / words` | at least 1 word | — |
| `punc_paren_ratio` | parenthesis marks per word | `marks / words` | at least 1 word | — |
| `punc_quote_ratio` | quotation mark marks per word | `marks / words` | at least 1 word | Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); per-word normalisation is this library's |
| `punc_question_ratio` | question mark marks per word | `marks / words` | at least 1 word | Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); per-word normalisation is this library's |
| `punc_total_ratio` | punctuation marks of all ten types per word | `marks / words` | at least 1 word | — |
| `punct_density` | punctuation marks per character | `marks / characters` | non-empty text | de Vel et al. (2001) Table 2, p.60 "Total number of punctuations/C" |
| `punct_entropy` | variety of punctuation types | `Shannon entropy (nats) of the 10 mark types` | at least 1 punctuation mark | Shannon (1948) — the entropy formula; applying it to the distribution of punctuation types is this library's own decision |
| `consecutive_punct_ratio` | share of marks directly next to another mark | `adjacent marks / marks` | at least 1 punctuation mark | — |
| `whitespace_ratio` | share of whitespace characters | `whitespace / characters` | non-empty text | de Vel et al. (2001) Table 2, p.60 "Total number of white-space characters/C" |
| `punct_variety` | number of punctuation types used (0–10) | `distinct mark types` | non-empty text | — |
| `uppercase_ratio` | share of capitalised words | `words whose first letter is upper case / words with a letter` | at least 1 word with a letter | — |
| `all_caps_word_ratio` | share of all-caps words | `words with 2+ letters, all upper case / words with a letter` | at least 1 word with a letter | — |

## `chars` — Character frequency vector  [dynamic: one key per letter — TR 29, EN 26]

Dynamic group: keys are generated with the prefix `char_`. The description, formula and requirement below are stated at the group level, not per key.

| Key | Description | Formula | Requires | Source |
|---|---|---|---|---|
| `char_…` | share of that letter among alphabet letters | `letter count / alphabet letters` | at least 1 alphabet letter | — |


## `custom_ngrams` — User-defined n-gram ratios  [dynamic: ng_{...}]

Dynamic group: keys are generated with the prefix `ng_`. The description, formula and requirement below are stated at the group level, not per key.

Created only when you pass `custom_ngrams` to `analyze()`.


## Bibliography

56 works. Every citation above names at least one of these verbatim, and every entry here is named by at least one citation — both directions are tested.

**Akın & Akın (2007)**
:   Akın, A. A., & Akın, M. D. (2007). Zemberek, an open source NLP framework for Turkic Languages. 8 pp. Source code: github.com/ahmetaa/zemberek-nlp. (The document does not state a place of publication.)

**Anderson (1983)**
:   Anderson, J. (1983). Lix and Rix: Variations on a little-known readability index. Journal of Reading, 26(6), 490–496. JSTOR 40031755.

**Ateşman (1997)**
:   Ateşman, E. (1997). Türkçede okunabilirliğin ölçülmesi. Dil Dergisi, 58, 71–74. Ankara Üniversitesi TÖMER. ISSN 1300-3542.

**Bestgen (2023)**
:   Bestgen, Y. (2023). Measuring lexical diversity in texts: The twofold length problem. arXiv:2307.04626. Published version: Language Learning, 74(3), 638–671 (2024), DOI 10.1111/lang.12630 — the preprint was used here.

**Bezirci & Yılmaz (2010)**
:   Bezirci, B., & Yılmaz, A. E. (2010). Türkçe için yeni bir okunabilirlik ölçütü önerisi. SIU2010 — IEEE 18. Sinyal İşleme ve İletişim Uygulamaları Kurultayı, Diyarbakır, 368–371.

**Björnsson (1968)**
:   Björnsson, C. H. (1968). Läsbarhet. Stockholm: Bokförlaget Liber. (Book.) The record was verified from three secondary reference lists: Anderson (1983), Çetinkaya (2010), Falkenjack et al. (2013). The primary source could not be obtained.

**Brunet (1978)**
:   Brunet, E. (1978). Vocabulaire de Jean Giraudoux: structure et évolution. Genève: Slatkine. (Book.) The record was verified from the reference list of Popescu, Čech & Altmann (2011). The primary source could not be obtained.

**Carroll (1964)**
:   Carroll, J. B. (1964). Language and Thought. Englewood Cliffs, NJ: Prentice-Hall. The record was verified from the reference list of Torruella & Capsada (2013). The primary source could not be obtained.

**Coleman & Liau (1975)**
:   Coleman, M., & Liau, T. L. (1975). A computer readability formula designed for machine scoring. Journal of Applied Psychology, 60(2), 283–284. DOI 10.1037/h0076540

**Covington & McFall (2010)**
:   Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot: The moving-average type–token ratio (MATTR). Journal of Quantitative Linguistics, 17(2), 94–100. DOI 10.1080/09296171003643098

**Daller (2010)**
:   Daller, M. (2010). Guiraud's Index. BAAL 2010, Aberdeen. (Presentation.)

**Deutsch, Jasbi & Shieber (2020)**
:   Deutsch, T., Jasbi, M., & Shieber, S. (2020). Linguistic features for readability assessment. Proceedings of the 15th Workshop on Innovative Use of NLP for Building Educational Applications (BEA), 1–17. DOI 10.18653/v1/2020.bea-1.1

**Dugast (1978)**
:   Dugast, D. (1978). Sur quoi se fonde la notion d'étendue théoretique du vocabulaire? Le Français Moderne, 46(1), 25–32. The record was verified from four secondary reference lists: Malvern et al. (2004), McCarthy & Jarvis (2010), Šišková (2012) and an authorship-attribution review. The primary source could not be obtained. The literature often cites Dugast (1978, 1979) together; 1979 is a separate work (Vocabulaire et stylistique I, Travaux de linguistique quantitative 8, Genève: Slatkine-Champion) and is not used here.

**Flesch (1948)**
:   Flesch, R. (1948). A new readability yardstick. Journal of Applied Psychology, 32(3), 221–233. DOI 10.1037/h0057532

**Guiraud (1954)**
:   Guiraud, P. (1954). Les Caractères Statistiques du Vocabulaire. Essai de méthodologie. Paris: Presses Universitaires de France.

**Göksel & Kerslake (2005)**
:   Göksel, A., & Kerslake, C. (2005). Turkish: A Comprehensive Grammar. London & New York: Routledge. 535 pp. ISBN 0-415-11494-2 (pbk), 0-415-21761-X (hbk).

**Heaps (1978)**
:   Heaps, H. S. (1978). Information Retrieval: Computational and Theoretical Aspects. New York: Academic Press.

**Herdan (1955)**
:   Herdan, G. (1955). A new derivation and interpretation of Yule's characteristic K. Zeitschrift für Angewandte Mathematik und Physik, 6. The record was verified from the reference list of Tweedie & Baayen (1998). The primary source could not be obtained.

**Herdan (1960/1964)**
:   Herdan, G. (1960). Type-Token Mathematics. The Hague: Mouton. / Herdan, G. (1964). Quantitative Linguistics. London: Butterworths.

**Jing & Liu (2015)**
:   Jing, Y., & Liu, H. (2015). Mean hierarchical distance: Augmenting mean dependency distance. Proceedings of Depling 2015, Uppsala, 161–170.

**Johnson (1944)**
:   Johnson, W. (1944). Studies in language behavior: I. A program of research. Psychological Monographs, 56(2), 1–15. DOI 10.1037/h0093508

**Kincaid et al. (1975)**
:   Kincaid, J. P., Fishburne, R. P., Rogers, R. L., & Chissom, B. S. (1975). Derivation of new readability formulas for Navy enlisted personnel. Research Branch Report 8-75. Millington, TN: Naval Air Station Memphis. DOI 10.21236/ADA006655

**Liu (2008)**
:   Liu, H. (2008). Dependency distance as a metric of language comprehension difficulty. Journal of Cognitive Science, 9(2), 159–191. DOI 10.17791/jcs.2008.9.2.159

**Lu (2012)**
:   Lu, X. (2012). The relationship of lexical richness to the quality of ESL learners' oral narratives. The Modern Language Journal, 96(2), 190–208. DOI 10.1111/j.1540-4781.2011.01232.x

**Maas (1972)**
:   Maas, H.-D. (1972). Zusammenhang zwischen Wortschatzumfang und Länge eines Textes. Zeitschrift für Literaturwissenschaft und Linguistik, 8, 73–79. The record was verified from the reference list of Tweedie & Baayen (1998). The primary source could not be obtained.

**Malvern et al. (2004)**
:   Malvern, D., Richards, B., Chipere, N., & Durán, P. (2004). Lexical Diversity and Language Development: Quantification and Assessment. Basingstoke: Palgrave Macmillan. ISBN 978-1-4039-0232-0. DOI 10.1057/9780230511804.

**Manning et al. (2008)**
:   Manning, C. D., Raghavan, P., & Schütze, H. (2008). Introduction to Information Retrieval. Cambridge University Press. (The file in the archive is the 2009 online edition.) DOI 10.1017/CBO9780511809071

**McCarthy & Jarvis (2007)**
:   McCarthy, P. M., & Jarvis, S. (2007). vocd: A theoretical and empirical evaluation. Language Testing, 24(4), 459–488. DOI 10.1177/0265532207080767

**McCarthy & Jarvis (2010)**
:   McCarthy, P. M., & Jarvis, S. (2010). MTLD, vocd-D, and HD-D: A validation study of sophisticated approaches to lexical diversity assessment. Behavior Research Methods, 42(2), 381–392. DOI 10.3758/BRM.42.2.381

**McCarthy (2005)**
:   McCarthy, P. M. (2005). An Assessment of the Range and Usefulness of Lexical Diversity Measures and the Potential of the Measure of Textual, Lexical Diversity (MTLD). Doctoral dissertation, The University of Memphis, August 2005. Advisor: Charles E. Hall. (Only a preview is available: 24 pages of front matter + abstract, no body.)

**McLaughlin (1969)**
:   McLaughlin, G. H. (1969). SMOG grading — a new readability formula. Journal of Reading, 12(8), 639–646.

**Mendenhall (1887)**
:   Mendenhall, T. C. (1887). The characteristic curves of composition. Science, 9(214), 237–249. JSTOR 1764604.

**Piantadosi (2014)**
:   Piantadosi, S. T. (2014). Zipf's word frequency law in natural language: A critical review and future directions. Psychonomic Bulletin & Review, 21(5), 1112–1130. DOI 10.3758/s13423-014-0585-6

**Popescu & Altmann (2006)**
:   Popescu, I.-I., & Altmann, G. (2006). Some aspects of word frequencies. Glottometrics, 13, 23–46. RAM-Verlag; journal ISSN 2625-8226.

**Popescu et al. (2009)**
:   Popescu, I.-I., Altmann, G., Grzybek, P., et al. (2009). Word Frequency Studies. Berlin: Mouton de Gruyter. (Quantitative Linguistics 64.) ISBN 978-3-11-021852-7, ISSN 0179-3616. DOI 10.1515/9783110218534

**Popescu, Mačutek & Altmann (2009)**
:   Popescu, I.-I., Mačutek, J., & Altmann, G. (2009). Aspects of Word Frequencies. Lüdenscheid: RAM-Verlag.

**Popescu, Čech & Altmann (2011)**
:   Popescu, I.-I., Čech, R., & Altmann, G. (2011). The Lambda-structure of Texts. Lüdenscheid: RAM-Verlag. ISBN 978-3-942303-05-7.

**QUITA**
:   Kubát, M., Matlach, V., & Čech, R. (2014). QUITA — Quantitative Index Text Analyzer. Lüdenscheid: RAM-Verlag. ISBN 978-3-942303-28-6.

**Shannon (1948)**
:   Shannon, C. E. (1948). A mathematical theory of communication. Bell System Technical Journal, 27(3), 379–423; 27(4), 623–656. DOI 10.1002/j.1538-7305.1948.tb01338.x

**Sichel (1975)**
:   Sichel, H. S. (1975). On a distribution law for word frequencies. Journal of the American Statistical Association, 70(351a), 542–547. DOI 10.1080/01621459.1975.10482469

**Simpson (1949)**
:   Simpson, E. H. (1949). Measurement of diversity. Nature, 163(4148), 688. DOI 10.1038/163688a0

**Smith & Senter (1967)**
:   Smith, E. A., & Senter, R. J. (1967). Automated readability index. AMRL-TR-66-220. Wright-Patterson AFB, OH: Aerospace Medical Research Laboratories. 22 pp.

**Somers (1966)**
:   Somers, H. H. (1966). Statistical methods in literary analysis. In J. Leeds (Ed.), The Computer and Literary Style (pp. 128–140). Kent, OH: Kent State University Press. The record was verified from the reference list of Torruella & Capsada (2013). The primary source could not be obtained.

**This library's threshold calibration**
:   This library's own measurement, not a published source. short_sent_threshold and long_sent_threshold were derived from the 15th and 85th percentiles of the sentence-length distribution of newspaper columns under the default sentence and word rules: TR 162 columnists / 4,321 articles / 197,990 sentences, EN 30 columnists / 1,485 articles / 52,745 sentences. Method and raw percentile table: docs/threshold-calibration.md.

**Torruella & Capsada (2013)**
:   Torruella, J., & Capsada, R. (2013). Lexical statistics and tipological structures: A measure of lexical richness. Procedia - Social and Behavioral Sciences, 95, 447–454. DOI 10.1016/j.sbspro.2013.10.668

**Tweedie & Baayen (1998)**
:   Tweedie, F. J., & Baayen, R. H. (1998). How variable may a constant be? Measures of lexical richness in perspective. Computers and the Humanities, 32(5), 323–352. DOI 10.1023/A:1001749303137

**Wells (1960)**
:   Wells, R. (1960). Nominal and verbal style. In T. A. Sebeok (Ed.), Style in Language (pp. 213–220). Cambridge, MA: Technology Press of MIT; New York: Wiley. Pages checked in the 1966 printing.

**Yule (1939)**
:   Yule, G. U. (1939). On sentence-length as a statistical characteristic of style in prose: With application to two cases of disputed authorship. Biometrika, 30(3/4), 363–390. JSTOR 2332655.

**Yule (1944)**
:   Yule, G. U. (1944). The Statistical Study of Literary Vocabulary. Cambridge University Press.

**Zeyrek**
:   Zeyrek — a Python port of the Zemberek morphological analyser. github.com/obulat/zeyrek

**Zheng et al. (2006)**
:   Zheng, R., Li, J., Chen, H., & Huang, Z. (2006). A framework for authorship identification of online messages: Writing-style features and classification techniques. Journal of the American Society for Information Science and Technology, 57(3), 378–393. DOI 10.1002/asi.20316

**de Marneffe et al. (2021)**
:   de Marneffe, M.-C., Manning, C. D., Nivre, J., & Zeman, D. (2021). Universal Dependencies. Computational Linguistics, 47(2), 255–308. DOI 10.1162/COLI_a_00402

**de Vel (2000)**
:   de Vel, O. (2000). Mining e-mail authorship. In KDD-2000 Workshop on Text Mining, Boston, August 20, 2000.

**de Vel et al. (2001)**
:   de Vel, O., Anderson, A., Corney, M., & Mohay, G. (2001). Mining e-mail content for author identification forensics. ACM SIGMOD Record, 30(4), 55–64. DOI 10.1145/604264.604272

**van Heuven et al. (2014)**
:   van Heuven, W. J. B., Mandera, P., Keuleers, E., & Brysbaert, M. (2014). SUBTLEX-UK: A new and improved word frequency database for British English. Quarterly Journal of Experimental Psychology, 67(6), 1176–1190. DOI 10.1080/17470218.2013.850521

**Çetinkaya (2010)**
:   Çetinkaya, G. (2010). Türkçe metinlerin okunabilirlik düzeylerinin tanımlanması ve sınıflandırılması [Unpublished doctoral dissertation]. Ankara Üniversitesi, Sosyal Bilimler Enstitüsü. Advisor: Leylâ Uzun. 252 pp. hdl:20.500.12812/519962
