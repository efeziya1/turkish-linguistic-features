<!-- GENERATED FILE — do not edit by hand.
     Source: scripts/generate_verification_report.py
     To regenerate:
       python scripts/generate_verification_report.py -->

# Verification report

This report compares the number each feature produces against the number
**published by the source it rests on**. The purpose is plain: before you use
a number in your own work, you should be able to see that it matches the
value in the literature.

## What the statuses mean

| | Meaning |
|---|---|
| ✅ **exact** | Within tolerance of the number the source published. If the cause of a small difference is known, it is noted under the row. |
| 🟡 **documented deviation** | The difference is **beyond the tolerance** and **the reason is written down** — the source rounded an intermediate value, or the source's own numbers were produced by hand, and so on. The effect of the deviation is explained in the row. |
| 🔍 **open** | The source gives the formula but no applied example. Verifiable, not yet verified; the formula and its edge cases are tested in their own test files. |
| ❌ **mismatch** | An **unexplained** difference. **Release gate:** a single one blocks a release. |

The three statuses below are **not verification candidates** — there is no
number to look for:

| | Meaning |
|---|---|
| ⚪ **no source** | Not a named measure from the literature; a plain definition (`punc_,_ratio`, `char_a`). |
| ⚫ **tag scheme** | Not a measure but a count of an external scheme's categories (`pos_noun` → UD; `case_loc_ratio` → Zeyrek). A scheme defines categories; it does not publish measurements. |
| 🔧 **derivative** | The formula comes from a source, **the application is this library's**. `entropy_std` is Shannon's entropy, but taking its standard deviation across segments is ours; `long_sent_ratio`'s threshold comes from our own calibration. Nobody has published this measure, so there is no number to compare against. Testing it against our own calibration would be reading our own answer sheet. |

The tolerance is **1% relative** to the published value. Sources print rounded
intermediate values, so exact equality is not expected; a relative tolerance
means the same thing at every scale.

**Exceeding the tolerance does not automatically make a row ❌.** What decides
is not the size of the difference but **whether its cause is known**: if the
cause has been measured and written down the row is 🟡, and if it has not the
row is ❌. A reason is not an excuse — it is evidence of where the difference
came from, and you can read it under the row.

## Two kinds of evidence

**End-to-end** rows push the source's **own text** through the pipeline, so
tokenisation, syllabification and sentence splitting are tested too. This is
the strongest evidence.

**Formula** rows feed the inputs to the function directly (for example
"syllables per word 2.2 and words per sentence 4"). They verify the formula
and its coefficients, not the pipeline. This is what is available when the
source published no text.

This report is **generated from the tests** — it reads the same comparison
table as `tests/test_kaynak_esligi.py`, so the two cannot drift apart. The
other known-value tests live in their own files.


## Turkish — 211 keys, 236 rows

A key may have more than one worked example in its source; each one is its own row.

**Verification candidates — 114 rows**

| Status | Rows |
|---|---|
| ✅ exact | 46 |
| 🟡 documented deviation | 2 |
| 🔍 open — no worked example in source | 66 |


**Not verification candidates — 122 rows.** There is no published number to look for in these.

| Status | Rows |
|---|---|
| ⚪ no source — plain definition | 49 |
| ⚫ tag scheme — not a measure | 68 |
| 🔧 derivative — the application is this library's | 5 |

### Keys with a numeric comparison

| Key | Source | Example | Evidence | Expected | Ours | Diff | Status |
|---|---|---|---|---|---|---|---|
| `entropy` | QUITA §6.1.12 | Text 1 · eq. (6.26); source 6.438043 in bits → × ln 2 | formula | 4.463 | 4.463 | +0.000 | ✅ |
| `entropy` | QUITA §6.1.12 | Text 2 · eq. (6.26); source 6.395099 in bits → × ln 2 | formula | 4.433 | 4.433 | +0.000 | ✅ |
| `ttr` | QUITA §6.1.1 | Text 1 · V/N = 119/179 | formula | 0.665 | 0.665 | -0.000 | ✅ |
| `ttr` | QUITA §6.1.1 | Text 2 · V/N = 121/202 = 0.599; source printed 0.590 (typo) | formula | 0.590 | 0.599 | +0.009 | 🟡 |
| `hapax_percentage` | QUITA §6.1.6 | Text 1 · 98/179 | formula | 0.547 | 0.547 | +0.000 | ✅ |
| `hapax_percentage` | QUITA §6.1.6 | Text 2 · 92/202 | formula | 0.455 | 0.455 | +0.000 | ✅ |
| `mtld` | McCarthy & Jarvis (2010) p.385 | partial factor · TTR .887 → 40.4% | formula | 0.404 | 0.404 | +0.000 | ✅ |
| `h_point` | QUITA §6.1.2 | Text 1 · rank 5 = frequency 5 | formula | 5.000 | 5.000 | +0.000 | ✅ |
| `h_point` | QUITA §6.1.2 | Text 2 · interpolation, eq. (6.2) | formula | 4.750 | 4.750 | +0.000 | ✅ |
| `vocab_richness_r1` | QUITA §6.1.3 | Text 1 · N=179, h=5 | formula | 0.835 | 0.835 | -0.000 | ✅ |
| `vocab_richness_r1` | QUITA §6.1.3 | Text 2 · N=202, h=4.75 → ⌊h⌋=4 | formula | 0.838 | 0.838 | +0.000 | ✅ |
| `vocab_richness_r4` | QUITA §6.1.9 | Text 1 · 1−G | formula | 0.696 | 0.696 | +0.000 | ✅ |
| `vocab_richness_r4` | QUITA §6.1.9 | Text 2 · 1−G | formula | 0.649 | 0.649 | -0.000 | ✅ |
| `repeat_rate` | QUITA §6.1.4 | Text 1 · N=179 | formula | 0.020 | 0.020 | -0.000 | ✅ |
| `repeat_rate` | QUITA §6.1.4 | Text 2 · N=202 | formula | 0.021 | 0.021 | -0.000 | ✅ |
| `rr_mcintosh` | QUITA §6.1.5 | Text 1 · V=119 | formula | 0.946 | 0.946 | +0.000 | ✅ |
| `rr_mcintosh` | QUITA §6.1.5 | Text 2 · V=121 | formula | 0.939 | 0.939 | -0.000 | ✅ |
| `gini_coef` | QUITA §6.1.8 | Text 1 · m₁=41.88268156 | formula | 0.304 | 0.304 | -0.000 | ✅ |
| `gini_coef` | QUITA §6.1.8 | Text 2 · m₁=39.75742574 | formula | 0.351 | 0.351 | +0.000 | ✅ |
| `curve_length` | QUITA §6.1.10 | Text 1 · eq. (6.21) | formula | 129.356 | 129.356 | +0.000 | ✅ |
| `curve_length` | QUITA §6.1.10 | Text 2 · eq. (6.21) | formula | 134.279 | 134.279 | +0.000 | ✅ |
| `curve_length_r` | QUITA §6.1.11 | Text 1 · Lh=14.29145 | formula | 0.889 | 0.890 | +0.000 | ✅ |
| `curve_length_r` | QUITA §6.1.11 | Text 2 · Lh=18.03607 | formula | 0.866 | 0.866 | -0.000 | ✅ |
| `lambda_pa` | QUITA §6.1.7 | Text 1 · L·ln N/N, L=129.3559482; source 1.628 in log₁₀ → × ln 10 | formula | 3.749 | 3.749 | +0.000 | ✅ |
| `lambda_pa` | QUITA §6.1.7 | Text 2 · L·ln N/N, L=134.2787065; source 1.5325 in log₁₀ → × ln 10 | formula | 3.529 | 3.529 | -0.000 | ✅ |
| `adjusted_modulus` | QUITA §6.1.13 | Text 1 · M=24.01416249; source 10.6594 in log₁₀ → / ln 10 | formula | 4.629 | 4.629 | -0.000 | ✅ |
| `adjusted_modulus` | QUITA §6.1.13 | Text 2 · M=25.81931678; source 11.19973 in log₁₀ → / ln 10 | formula | 4.864 | 4.864 | +0.000 | ✅ |
| `writers_view_alpha` | QUITA §6.2.3 | Text 1 · arccos(−0.374487816) | formula | 1.955 | 1.955 | -0.000 | ✅ |
| `writers_view_alpha` | QUITA §6.2.3 | Text 2 · arccos(−0.269972586) | formula | 1.844 | 1.844 | +0.000 | ✅ |
| `activity_ratio` | QUITA §6.2.2 | Text 1 · 26 verbs / 14 adjectives | formula | 0.650 | 0.650 | +0.000 | ✅ |
| `activity_ratio` | QUITA §6.2.2 | Text 2 · 35 verbs / 8 adjectives | formula | 0.814 | 0.814 | -0.000 | ✅ |
| `arc_len_mean` | Jing & Liu (2015) p.164 | Figure 3 · 'Mr. Nixon was to…' | formula | 1.167 | 1.167 | +0.000 | ✅ |
| `arc_len_mean` | Liu (2008) eq. (1) | 'I actually live in Beijing' · 5/4 | formula | 1.250 | 1.250 | +0.000 | ✅ |
| `parse_depth_mean` | Jing & Liu (2015) p.164 | Figure 3 · MHD = 12/6 | formula | 2.000 | 2.000 | +0.000 | ✅ |
| `ari` | Kincaid et al. (1975) p.8, Table 1 | Appendix A · 18 passages, mean | end-to-end | 12.300 | 11.763 | -0.537 | 🟡 |
| `coleman_liau` | Coleman & Liau (1975) p.284 | composition of the two equations · 13 words, 2 sentences | formula | 7.704 | 7.705 | +0.000 | ✅ |
| `coleman_liau` | Coleman & Liau (1975) p.284, Table 1 | cloze 40.4% → grade 12 | formula | 12.000 | 11.994 | -0.006 | ✅ |
| `atesman` | Ateşman (1997) | Kalyoncu & Memiş (2024) Table 9 · Text 2 | end-to-end | 23.094 | 23.094 | -0.000 | ✅ |
| `atesman` | Ateşman (1997) p.74 | calibration: easiest text | formula | 100.000 | 100.000 | -0.000 | ✅ |
| `atesman` | Ateşman (1997) p.74 | calibration: hardest text | formula | 0.000 | 0.000 | +0.000 | ✅ |
| `cetinkaya_uzun` | Çetinkaya (2010) | Kalyoncu & Memiş (2024) Table 9 · Text 2 | end-to-end | 23.084 | 23.084 | -0.000 | ✅ |
| `bezirci_yilmaz` | Bezirci & Yılmaz (2010) | Kalyoncu & Memiş (2024) Table 9 · Text 2 | end-to-end | 30.423 | 30.392 | -0.031 | ✅ |
| `bezirci_yilmaz` | Bezirci & Yılmaz (2010) Table 5 | E7 3.03 · OKS 7 | formula | 4.610 | 4.605 | -0.005 | ✅ |
| `bezirci_yilmaz` | Bezirci & Yılmaz (2010) Table 5 | E7 8.3 · OKS 10 | formula | 9.110 | 9.110 | +0.000 | ✅ |
| `bezirci_yilmaz` | Bezirci & Yılmaz (2010) Table 5 | E7 18.82 · OKS 14 | formula | 16.230 | 16.232 | +0.002 | ✅ |
| `bezirci_yilmaz` | Bezirci & Yılmaz (2010) Table 3 | H values of the easiest text | formula | 3.030 | 3.025 | -0.005 | ✅ |
| `bezirci_yilmaz` | Bezirci & Yılmaz (2010) Table 3 | H values of the hardest text | formula | 18.820 | 18.815 | -0.005 | ✅ |
| `bezirci_yilmaz` | Bezirci & Yılmaz (2010) Table 3 | mean H values | formula | 8.300 | 8.341 | +0.041 | ✅ |

**`ttr` deviation:** The source's own counts (V=121, N=202) give 121/202 = 0.599; the printed 0.590 does not match that arithmetic (typo). Our value follows the arithmetic; the difference is 1.5% of the published value.

**`ari` deviation:** The source's numbers were produced **by hand** in 1975 with a mechanical counter attached to a typewriter (Appendix B, ARI instructions). In 17 of the 18 passages, the stroke count that would yield the source's ARI is 0.996-1.041 times ours — a difference of a few characters. Passage 2 is an outlier (ratio 1.145), and there the source's own two numbers contradict each other: Table 1's ARI of 20.3 requires 6.269 strokes per word, while the text's actual value is 5.475; moreover, the words per sentence implied by that ARI give an FKGL of 18.69, whereas Table 2 printed 16.7. Our stroke definition was tested separately: counting spaces raises the difference from 0.54 to 4.24, so counting without spaces is correct.

**`bezirci_yilmaz` deviation:** The paper rounded its H6 intermediate value; the difference is 0.031 and both values fall in the same readability class (academic, 16+).

**`bezirci_yilmaz` deviation:** The paper prints the H6 mean as 0.07, but the value that yields 8.30 is ~0.0684. The coefficient 26.25 inflates that rounding to 0.041; the coefficients themselves are correct.

### 🔍 Open — verifiable, not yet verified

66 keys. The source published the formula but never applied it to anything and printed the result. In quantitative linguistics this is ordinary: Yule (1944) defines K; he does not print what K comes to for a particular novel. These rows are **not untested** — their formulas and edge cases are tested in their own test files. What is tracked here is only the comparison *against the source's number*.

| Key | Source | Status |
|---|---|---|
| `avg_word_length` | Mendenhall (1887) p.237 "mean word-length"; computed as letters per word, p.241 | 🔍 |
| `yule_k` | Yule (1944) p.53, eq. (3.22) | 🔍 |
| `simpson_d` | Simpson (1949), as cited in Bestgen (2023) | 🔍 |
| `brunet_w` | Brunet (1978), as cited in Tweedie & Baayen (1998) p.328, eq. (10) | 🔍 |
| `hapax_ratio` | de Vel (2000) Table 2, attribute 14 "Ratio of words used once to total number of vocabulary words" | 🔍 |
| `mattr` | Covington & McFall (2010); default window 50 — C&M recommend a window of 500; 50 is used here so that texts of 100+ words can be measured (mattr needs 2 × window) | 🔍 |
| `herdan_c` | Herdan (1960/1964), as cited in Tweedie & Baayen (1998) p.327, eq. (5) | 🔍 |
| `dugast_u` | Dugast (1978), as cited in Malvern et al. (2004) eq. 2.7 | 🔍 |
| `guiraud_r` | Guiraud (1954) p.53, alternative form (all word types), as cited in Daller (2010); his actual law is V/√(2N), content words only | 🔍 |
| `cttr` | Carroll (1964), as cited in Torruella & Capsada (2013) p.448 | 🔍 |
| `summer_s` | Somers (1966), as cited in Torruella & Capsada (2013) p.448, where it is named "Summer"; the source gives no logarithm base, the natural logarithm is this library's choice | 🔍 |
| `maas_a2` | Maas (1972), as cited in Tweedie & Baayen (1998) p.327, eq. (7); natural logarithm, which reproduces the values in Torruella & Capsada (2013) Table 1; all logarithms in this library are natural | 🔍 |
| `herdan_vm` | Herdan (1955), as cited in Tweedie & Baayen (1998) p.330, eq. (18) | 🔍 |
| `heaps_beta` | Heaps (1978), as cited in Manning et al. (2008) §5.1.1 | 🔍 |
| `sichel_s` | Sichel (1975); formula from Malvern et al. (2004) eq. 3.10 | 🔍 |
| `noun_variation` | Lu (2012) Table 2 | 🔍 |
| `verb_variation` | Lu (2012) Table 2 | 🔍 |
| `adj_variation` | Lu (2012) Table 2 | 🔍 |
| `adv_variation` | Lu (2012) Table 2 | 🔍 |
| `zipf_exponent` | Piantadosi (2014) eq. (2); the same source criticises estimating r and f(r) from the same corpus | 🔍 |
| `zipf_r2` | Piantadosi (2014) eq. (2); the same source criticises estimating r and f(r) from the same corpus | 🔍 |
| `zipf_mandelbrot_q` | Piantadosi (2014) eq. (2); the same source criticises estimating r and f(r) from the same corpus | 🔍 |
| `zipf_mandelbrot_s` | Piantadosi (2014) eq. (2); the same source criticises estimating r and f(r) from the same corpus | 🔍 |
| `wordfreq_mean` | van Heuven et al. (2014) (Zipf scale) | 🔍 |
| `wordfreq_rare_ratio` | van Heuven et al. (2014) Table 1 (Zipf ≤ 3 = low frequency) | 🔍 |
| `vocd_d` | Malvern et al. (2004) pp.56–57; procedure from McCarthy & Jarvis (2010) p.383 | 🔍 |
| `hdd` | McCarthy & Jarvis (2007), as cited in McCarthy & Jarvis (2010) p.383 | 🔍 |
| `msttr` | Johnson (1944), as cited in Malvern et al. (2004) p.25 and McCarthy & Jarvis (2010) p.385 | 🔍 |
| `thematic_concentration` | QUITA §6.2.5 | 🔍 |
| `secondary_thematic_concentration` | QUITA §6.2.6 | 🔍 |
| `avg_sent_len_word` | Flesch (1948) p.223, element (1) "Average Sentence Length in Words" | 🔍 |
| `med_sent_len` | Yule (1939) p.369, median sentence length alongside the mean | 🔍 |
| `avg_sent_len_char` | Zheng et al. (2006) Table 3, p.384, no. 58 "Average sentence length in terms of character" | 🔍 |
| `para_len_mean` | Zheng et al. (2006) Table 3, p.384, no. 251 "Number of words per paragraph" | 🔍 |
| `sents_per_para_mean` | Zheng et al. (2006) Table 3, p.384, no. 249 "Number of sentences per paragraph" | 🔍 |
| `pronoun_freq` | Deutsch, Jasbi & Shieber (2020) Table 6 "pronouns per word", listed among existing features; original source not traced | 🔍 |
| `nominal_verbal_ratio` | Wells (1960) p.214, Noun-Verb Quotient (NVQ), "the proportion of nouns to verbs in a given text"; nouns = NOUN + PROPN, verbs = VERB (the copula is left out, a choice Wells leaves open) | 🔍 |
| `verb_dist_mean` | QUITA §6.2.1 | 🔍 |
| `verb_dist_cv` | QUITA §6.2.1 | 🔍 |
| `lexical_density` | Lu (2012); definition in the broad Hallidayan sense — all open-class words | 🔍 |
| `pos_dist_std` | Deutsch, Jasbi & Shieber (2020) Definition 3.3 (POSDdev); computed over ratios, 12 UD tags | 🔍 |
| `pos_kl_div` | Deutsch, Jasbi & Shieber (2020) Definition 3.4 (POSdiv); natural logarithm (nats), the source uses bits | 🔍 |
| `suffix_bigram_entropy` | Shannon (1948) — the entropy formula; Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | 🔍 |
| `front_vowel_ratio` | Göksel & Kerslake (2005) ch. 2 (the vowel system, front/back) | 🔍 |
| `back_vowel_ratio` | Göksel & Kerslake (2005) ch. 2 (the vowel system, front/back) | 🔍 |
| `harmony_fronting_ratio` | Göksel & Kerslake (2005) §3.1 (fronting harmony); exceptions §3.4 — the measure counts them as disharmonic | 🔍 |
| `harmony_rounding_ratio` | Göksel & Kerslake (2005) §3.1 (rounding harmony); strictly a suffix phenomenon, measured here as a whole-word pattern | 🔍 |
| `syllable_mean` | Flesch (1948) Formula A, wl; unit there = syllables per 100 words, here per word | 🔍 |
| `syllable_1_ratio` | Bezirci & Yılmaz (2010) Table 1-c | 🔍 |
| `syllable_2_ratio` | Bezirci & Yılmaz (2010) Table 1-c | 🔍 |
| `syllable_3_ratio` | Bezirci & Yılmaz (2010) Table 1-c | 🔍 |
| `syllable_4_ratio` | Bezirci & Yılmaz (2010) Table 1-c | 🔍 |
| `syllable_5_ratio` | Bezirci & Yılmaz (2010) Table 1-c | 🔍 |
| `syllable_6plus_ratio` | Bezirci & Yılmaz (2010) Table 1-c | 🔍 |
| `lix` | Björnsson (1968), as cited in Anderson (1983) p.490; long word = 7+ letters | 🔍 |
| `long_word_ratio` | Anderson (1983); long word = 7+ letters | 🔍 |
| `digit_vs_all` | de Vel et al. (2001) Table 2, p.60 "Total number of digit characters in words/C"; here digits anywhere in the text | 🔍 |
| `punc_,_ratio` | Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); per-word normalisation is this library's | 🔍 |
| `punc_._ratio` | Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); per-word normalisation is this library's | 🔍 |
| `punc_;_ratio` | Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); per-word normalisation is this library's | 🔍 |
| `punc_!_ratio` | Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); per-word normalisation is this library's | 🔍 |
| `punc_:_ratio` | Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); per-word normalisation is this library's | 🔍 |
| `punc_quote_ratio` | Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); per-word normalisation is this library's | 🔍 |
| `punc_question_ratio` | Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); per-word normalisation is this library's | 🔍 |
| `punct_density` | de Vel et al. (2001) Table 2, p.60 "Total number of punctuations/C" | 🔍 |
| `whitespace_ratio` | de Vel et al. (2001) Table 2, p.60 "Total number of white-space characters/C" | 🔍 |

### Not verification candidates

122 keys. The ⚪ ones are plain definitions (`punc_,_ratio`, `char_a`) — not named measures from the literature. The ⚫ ones are not measures at all but counts of an external tag scheme's categories; a scheme defines categories, it does not publish measurements. The 🔧 ones take their formula from a source but their application is this library's. None of the three has a number to look for.

| Key | Source | Status |
|---|---|---|
| `n_lemma_count` | — | ⚪ |
| `word_length_cv` | — | ⚪ |
| `entropy_std` | Shannon (1948) — the entropy formula; the standard deviation across segments is this library's own derivation | 🔧 |
| `sentence_length_cv` | — | ⚪ |
| `sent_len_skewness` | — | ⚪ |
| `short_sent_ratio` | This library's threshold calibration (docs/threshold-calibration.md); TR 4, EN 8 — 15th percentile of newspaper columns under the default sentence and word rules. Note: the TR value coincides with Ateşman (1997) p.74, where the easiest text has a mean sentence length of 4 words; that is a text mean, not a threshold, so it is not the source. Calibrated on newspaper columns only | 🔧 |
| `long_sent_ratio` | This library's threshold calibration (docs/threshold-calibration.md); TR 17, EN 32 — 85th percentile of newspaper columns under the default sentence and word rules. Ateşman's 30 was not used: that is the mean of the hardest text, not a single-sentence threshold (in Turkish newspaper columns 30 words is above the 95th percentile, so as a threshold it would almost never fire). Calibrated on newspaper columns only | 🔧 |
| `sent_len_entropy` | Shannon (1948) — the entropy formula; applying it to the distribution of sentence lengths is this library's own decision | 🔧 |
| `para_len_cv` | — | ⚪ |
| `sents_per_para_cv` | — | ⚪ |
| `para_count_norm` | — | ⚪ |
| `pos_noun` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_propn` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_verb` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_adj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_adv` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_det` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_adp` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_intj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_cconj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_sconj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_num` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_aux` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `question_per_sent` | — | ⚪ |
| `sentfinal_noun` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_propn` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_verb` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_adj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_adv` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_det` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_adp` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_intj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_cconj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_sconj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_num` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_aux` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_pron` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_other` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `surface_per_lemma` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_tense_past` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_tense_pres` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_tense_fut` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_aspect_perf` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_aspect_imp` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_aspect_prog` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_case_nom` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_case_acc` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_case_dat` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_case_loc` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_case_abl` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_case_gen` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_person_1` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_person_2` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_person_3` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_number_sing` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_number_plur` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_voice_pass` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `agglutination_depth` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `suffix_char_length_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `suffix_chain_cv` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `derivational_suffix_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `tense_past_def` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `tense_past_nar` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `tense_present` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `tense_future` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `modal_possibility_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `modal_necessity_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `negation_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `passive_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `plural_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `case_acc_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `case_dat_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `case_loc_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `case_abl_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `case_gen_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `case_ins_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `conditional_suffix_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `causative_suffix_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `question_particle_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `verb_suffix_diversity` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `vowel_ratio` | — | ⚪ |
| `syllable_cv` | — | ⚪ |
| `sentence_syllable_mean` | — | ⚪ |
| `sentence_syllable_cv` | — | ⚪ |
| `punc_-_ratio` | — | ⚪ |
| `punc_ellipsis_ratio` | — | ⚪ |
| `punc_paren_ratio` | — | ⚪ |
| `punc_total_ratio` | — | ⚪ |
| `punct_entropy` | Shannon (1948) — the entropy formula; applying it to the distribution of punctuation types is this library's own decision | 🔧 |
| `consecutive_punct_ratio` | — | ⚪ |
| `punct_variety` | — | ⚪ |
| `uppercase_ratio` | — | ⚪ |
| `all_caps_word_ratio` | — | ⚪ |
| `char_a` | — | ⚪ |
| `char_b` | — | ⚪ |
| `char_c` | — | ⚪ |
| `char_ç` | — | ⚪ |
| `char_d` | — | ⚪ |
| `char_e` | — | ⚪ |
| `char_f` | — | ⚪ |
| `char_g` | — | ⚪ |
| `char_ğ` | — | ⚪ |
| `char_h` | — | ⚪ |
| `char_ı` | — | ⚪ |
| `char_i` | — | ⚪ |
| `char_j` | — | ⚪ |
| `char_k` | — | ⚪ |
| `char_l` | — | ⚪ |
| `char_m` | — | ⚪ |
| `char_n` | — | ⚪ |
| `char_o` | — | ⚪ |
| `char_ö` | — | ⚪ |
| `char_p` | — | ⚪ |
| `char_r` | — | ⚪ |
| `char_s` | — | ⚪ |
| `char_ş` | — | ⚪ |
| `char_t` | — | ⚪ |
| `char_u` | — | ⚪ |
| `char_ü` | — | ⚪ |
| `char_v` | — | ⚪ |
| `char_y` | — | ⚪ |
| `char_z` | — | ⚪ |

## English — 183 keys, 200 rows

A key may have more than one worked example in its source; each one is its own row.

**Verification candidates — 103 rows**

| Status | Rows |
|---|---|
| ✅ exact | 35 |
| 🟡 documented deviation | 3 |
| 🔍 open — no worked example in source | 65 |


**Not verification candidates — 97 rows.** There is no published number to look for in these.

| Status | Rows |
|---|---|
| ⚪ no source — plain definition | 46 |
| ⚫ tag scheme — not a measure | 45 |
| 🔧 derivative — the application is this library's | 6 |

### Keys with a numeric comparison

| Key | Source | Example | Evidence | Expected | Ours | Diff | Status |
|---|---|---|---|---|---|---|---|
| `entropy` | QUITA §6.1.12 | Text 1 · eq. (6.26); source 6.438043 in bits → × ln 2 | formula | 4.463 | 4.463 | +0.000 | ✅ |
| `entropy` | QUITA §6.1.12 | Text 2 · eq. (6.26); source 6.395099 in bits → × ln 2 | formula | 4.433 | 4.433 | +0.000 | ✅ |
| `ttr` | QUITA §6.1.1 | Text 1 · V/N = 119/179 | formula | 0.665 | 0.665 | -0.000 | ✅ |
| `ttr` | QUITA §6.1.1 | Text 2 · V/N = 121/202 = 0.599; source printed 0.590 (typo) | formula | 0.590 | 0.599 | +0.009 | 🟡 |
| `hapax_percentage` | QUITA §6.1.6 | Text 1 · 98/179 | formula | 0.547 | 0.547 | +0.000 | ✅ |
| `hapax_percentage` | QUITA §6.1.6 | Text 2 · 92/202 | formula | 0.455 | 0.455 | +0.000 | ✅ |
| `mtld` | McCarthy & Jarvis (2010) p.385 | partial factor · TTR .887 → 40.4% | formula | 0.404 | 0.404 | +0.000 | ✅ |
| `h_point` | QUITA §6.1.2 | Text 1 · rank 5 = frequency 5 | formula | 5.000 | 5.000 | +0.000 | ✅ |
| `h_point` | QUITA §6.1.2 | Text 2 · interpolation, eq. (6.2) | formula | 4.750 | 4.750 | +0.000 | ✅ |
| `vocab_richness_r1` | QUITA §6.1.3 | Text 1 · N=179, h=5 | formula | 0.835 | 0.835 | -0.000 | ✅ |
| `vocab_richness_r1` | QUITA §6.1.3 | Text 2 · N=202, h=4.75 → ⌊h⌋=4 | formula | 0.838 | 0.838 | +0.000 | ✅ |
| `vocab_richness_r4` | QUITA §6.1.9 | Text 1 · 1−G | formula | 0.696 | 0.696 | +0.000 | ✅ |
| `vocab_richness_r4` | QUITA §6.1.9 | Text 2 · 1−G | formula | 0.649 | 0.649 | -0.000 | ✅ |
| `repeat_rate` | QUITA §6.1.4 | Text 1 · N=179 | formula | 0.020 | 0.020 | -0.000 | ✅ |
| `repeat_rate` | QUITA §6.1.4 | Text 2 · N=202 | formula | 0.021 | 0.021 | -0.000 | ✅ |
| `rr_mcintosh` | QUITA §6.1.5 | Text 1 · V=119 | formula | 0.946 | 0.946 | +0.000 | ✅ |
| `rr_mcintosh` | QUITA §6.1.5 | Text 2 · V=121 | formula | 0.939 | 0.939 | -0.000 | ✅ |
| `gini_coef` | QUITA §6.1.8 | Text 1 · m₁=41.88268156 | formula | 0.304 | 0.304 | -0.000 | ✅ |
| `gini_coef` | QUITA §6.1.8 | Text 2 · m₁=39.75742574 | formula | 0.351 | 0.351 | +0.000 | ✅ |
| `curve_length` | QUITA §6.1.10 | Text 1 · eq. (6.21) | formula | 129.356 | 129.356 | +0.000 | ✅ |
| `curve_length` | QUITA §6.1.10 | Text 2 · eq. (6.21) | formula | 134.279 | 134.279 | +0.000 | ✅ |
| `curve_length_r` | QUITA §6.1.11 | Text 1 · Lh=14.29145 | formula | 0.889 | 0.890 | +0.000 | ✅ |
| `curve_length_r` | QUITA §6.1.11 | Text 2 · Lh=18.03607 | formula | 0.866 | 0.866 | -0.000 | ✅ |
| `lambda_pa` | QUITA §6.1.7 | Text 1 · L·ln N/N, L=129.3559482; source 1.628 in log₁₀ → × ln 10 | formula | 3.749 | 3.749 | +0.000 | ✅ |
| `lambda_pa` | QUITA §6.1.7 | Text 2 · L·ln N/N, L=134.2787065; source 1.5325 in log₁₀ → × ln 10 | formula | 3.529 | 3.529 | -0.000 | ✅ |
| `adjusted_modulus` | QUITA §6.1.13 | Text 1 · M=24.01416249; source 10.6594 in log₁₀ → / ln 10 | formula | 4.629 | 4.629 | -0.000 | ✅ |
| `adjusted_modulus` | QUITA §6.1.13 | Text 2 · M=25.81931678; source 11.19973 in log₁₀ → / ln 10 | formula | 4.864 | 4.864 | +0.000 | ✅ |
| `writers_view_alpha` | QUITA §6.2.3 | Text 1 · arccos(−0.374487816) | formula | 1.955 | 1.955 | -0.000 | ✅ |
| `writers_view_alpha` | QUITA §6.2.3 | Text 2 · arccos(−0.269972586) | formula | 1.844 | 1.844 | +0.000 | ✅ |
| `activity_ratio` | QUITA §6.2.2 | Text 1 · 26 verbs / 14 adjectives | formula | 0.650 | 0.650 | +0.000 | ✅ |
| `activity_ratio` | QUITA §6.2.2 | Text 2 · 35 verbs / 8 adjectives | formula | 0.814 | 0.814 | -0.000 | ✅ |
| `arc_len_mean` | Jing & Liu (2015) p.164 | Figure 3 · 'Mr. Nixon was to…' | formula | 1.167 | 1.167 | +0.000 | ✅ |
| `arc_len_mean` | Liu (2008) eq. (1) | 'I actually live in Beijing' · 5/4 | formula | 1.250 | 1.250 | +0.000 | ✅ |
| `parse_depth_mean` | Jing & Liu (2015) p.164 | Figure 3 · MHD = 12/6 | formula | 2.000 | 2.000 | +0.000 | ✅ |
| `ari` | Kincaid et al. (1975) p.8, Table 1 | Appendix A · 18 passages, mean | end-to-end | 12.300 | 11.763 | -0.537 | 🟡 |
| `coleman_liau` | Coleman & Liau (1975) p.284 | composition of the two equations · 13 words, 2 sentences | formula | 7.704 | 7.705 | +0.000 | ✅ |
| `coleman_liau` | Coleman & Liau (1975) p.284, Table 1 | cloze 40.4% → grade 12 | formula | 12.000 | 11.994 | -0.006 | ✅ |
| `flesch_kincaid_grade` | Kincaid et al. (1975) p.12, Table 2 | Appendix A · 18 passages, mean | end-to-end | 10.700 | 10.326 | -0.374 | 🟡 |

**`ttr` deviation:** The source's own counts (V=121, N=202) give 121/202 = 0.599; the printed 0.590 does not match that arithmetic (typo). Our value follows the arithmetic; the difference is 1.5% of the published value.

**`ari` deviation:** The source's numbers were produced **by hand** in 1975 with a mechanical counter attached to a typewriter (Appendix B, ARI instructions). In 17 of the 18 passages, the stroke count that would yield the source's ARI is 0.996-1.041 times ours — a difference of a few characters. Passage 2 is an outlier (ratio 1.145), and there the source's own two numbers contradict each other: Table 1's ARI of 20.3 requires 6.269 strokes per word, while the text's actual value is 5.475; moreover, the words per sentence implied by that ARI give an FKGL of 18.69, whereas Table 2 printed 16.7. Our stroke definition was tested separately: counting spaces raises the difference from 0.54 to 4.24, so counting without spaces is correct.

**`flesch_kincaid_grade` deviation:** Same hand-counting source. The per-passage deviation is below 0.6 in 15 of the 18 passages; passage 12 is an outlier (-4.28) and also misses its FRE band, so the deviation is concentrated in a single passage. The difference between the means is 0.34 grade levels — too small to change the readability classification.

### 🔍 Open — verifiable, not yet verified

65 keys. The source published the formula but never applied it to anything and printed the result. In quantitative linguistics this is ordinary: Yule (1944) defines K; he does not print what K comes to for a particular novel. These rows are **not untested** — their formulas and edge cases are tested in their own test files. What is tracked here is only the comparison *against the source's number*.

| Key | Source | Status |
|---|---|---|
| `avg_word_length` | Mendenhall (1887) p.237 "mean word-length"; computed as letters per word, p.241 | 🔍 |
| `yule_k` | Yule (1944) p.53, eq. (3.22) | 🔍 |
| `simpson_d` | Simpson (1949), as cited in Bestgen (2023) | 🔍 |
| `brunet_w` | Brunet (1978), as cited in Tweedie & Baayen (1998) p.328, eq. (10) | 🔍 |
| `hapax_ratio` | de Vel (2000) Table 2, attribute 14 "Ratio of words used once to total number of vocabulary words" | 🔍 |
| `mattr` | Covington & McFall (2010); default window 50 — C&M recommend a window of 500; 50 is used here so that texts of 100+ words can be measured (mattr needs 2 × window) | 🔍 |
| `herdan_c` | Herdan (1960/1964), as cited in Tweedie & Baayen (1998) p.327, eq. (5) | 🔍 |
| `dugast_u` | Dugast (1978), as cited in Malvern et al. (2004) eq. 2.7 | 🔍 |
| `guiraud_r` | Guiraud (1954) p.53, alternative form (all word types), as cited in Daller (2010); his actual law is V/√(2N), content words only | 🔍 |
| `cttr` | Carroll (1964), as cited in Torruella & Capsada (2013) p.448 | 🔍 |
| `summer_s` | Somers (1966), as cited in Torruella & Capsada (2013) p.448, where it is named "Summer"; the source gives no logarithm base, the natural logarithm is this library's choice | 🔍 |
| `maas_a2` | Maas (1972), as cited in Tweedie & Baayen (1998) p.327, eq. (7); natural logarithm, which reproduces the values in Torruella & Capsada (2013) Table 1; all logarithms in this library are natural | 🔍 |
| `herdan_vm` | Herdan (1955), as cited in Tweedie & Baayen (1998) p.330, eq. (18) | 🔍 |
| `heaps_beta` | Heaps (1978), as cited in Manning et al. (2008) §5.1.1 | 🔍 |
| `sichel_s` | Sichel (1975); formula from Malvern et al. (2004) eq. 3.10 | 🔍 |
| `noun_variation` | Lu (2012) Table 2 | 🔍 |
| `verb_variation` | Lu (2012) Table 2 | 🔍 |
| `adj_variation` | Lu (2012) Table 2 | 🔍 |
| `adv_variation` | Lu (2012) Table 2 | 🔍 |
| `zipf_exponent` | Piantadosi (2014) eq. (2); the same source criticises estimating r and f(r) from the same corpus | 🔍 |
| `zipf_r2` | Piantadosi (2014) eq. (2); the same source criticises estimating r and f(r) from the same corpus | 🔍 |
| `zipf_mandelbrot_q` | Piantadosi (2014) eq. (2); the same source criticises estimating r and f(r) from the same corpus | 🔍 |
| `zipf_mandelbrot_s` | Piantadosi (2014) eq. (2); the same source criticises estimating r and f(r) from the same corpus | 🔍 |
| `wordfreq_mean` | van Heuven et al. (2014) (Zipf scale) | 🔍 |
| `wordfreq_rare_ratio` | van Heuven et al. (2014) Table 1 (Zipf ≤ 3 = low frequency) | 🔍 |
| `vocd_d` | Malvern et al. (2004) pp.56–57; procedure from McCarthy & Jarvis (2010) p.383 | 🔍 |
| `hdd` | McCarthy & Jarvis (2007), as cited in McCarthy & Jarvis (2010) p.383 | 🔍 |
| `msttr` | Johnson (1944), as cited in Malvern et al. (2004) p.25 and McCarthy & Jarvis (2010) p.385 | 🔍 |
| `thematic_concentration` | QUITA §6.2.5 | 🔍 |
| `secondary_thematic_concentration` | QUITA §6.2.6 | 🔍 |
| `avg_sent_len_word` | Flesch (1948) p.223, element (1) "Average Sentence Length in Words" | 🔍 |
| `med_sent_len` | Yule (1939) p.369, median sentence length alongside the mean | 🔍 |
| `avg_sent_len_char` | Zheng et al. (2006) Table 3, p.384, no. 58 "Average sentence length in terms of character" | 🔍 |
| `para_len_mean` | Zheng et al. (2006) Table 3, p.384, no. 251 "Number of words per paragraph" | 🔍 |
| `sents_per_para_mean` | Zheng et al. (2006) Table 3, p.384, no. 249 "Number of sentences per paragraph" | 🔍 |
| `pronoun_freq` | Deutsch, Jasbi & Shieber (2020) Table 6 "pronouns per word", listed among existing features; original source not traced | 🔍 |
| `nominal_verbal_ratio` | Wells (1960) p.214, Noun-Verb Quotient (NVQ), "the proportion of nouns to verbs in a given text"; nouns = NOUN + PROPN, verbs = VERB (the copula is left out, a choice Wells leaves open) | 🔍 |
| `verb_dist_mean` | QUITA §6.2.1 | 🔍 |
| `verb_dist_cv` | QUITA §6.2.1 | 🔍 |
| `lexical_density` | Lu (2012); definition in the broad Hallidayan sense — all open-class words | 🔍 |
| `pos_dist_std` | Deutsch, Jasbi & Shieber (2020) Definition 3.3 (POSDdev); computed over ratios, 12 UD tags | 🔍 |
| `pos_kl_div` | Deutsch, Jasbi & Shieber (2020) Definition 3.4 (POSdiv); natural logarithm (nats), the source uses bits | 🔍 |
| `front_vowel_ratio` | Göksel & Kerslake (2005) ch. 2 (the vowel system, front/back) | 🔍 |
| `back_vowel_ratio` | Göksel & Kerslake (2005) ch. 2 (the vowel system, front/back) | 🔍 |
| `syllable_mean` | Flesch (1948) Formula A, wl; unit there = syllables per 100 words, here per word | 🔍 |
| `syllable_1_ratio` | Bezirci & Yılmaz (2010) Table 1-c | 🔍 |
| `syllable_2_ratio` | Bezirci & Yılmaz (2010) Table 1-c | 🔍 |
| `syllable_3_ratio` | Bezirci & Yılmaz (2010) Table 1-c | 🔍 |
| `syllable_4_ratio` | Bezirci & Yılmaz (2010) Table 1-c | 🔍 |
| `syllable_5_ratio` | Bezirci & Yılmaz (2010) Table 1-c | 🔍 |
| `syllable_6plus_ratio` | Bezirci & Yılmaz (2010) Table 1-c | 🔍 |
| `lix` | Björnsson (1968), as cited in Anderson (1983) p.490; long word = 7+ letters | 🔍 |
| `long_word_ratio` | Anderson (1983); long word = 7+ letters | 🔍 |
| `flesch_reading_ease` | Flesch (1948) Formula A; coefficient .846, unit = syllables per 100 words | 🔍 |
| `smog` | McLaughlin (1969) p.643, Table 1, eq. (d); p = polysyllabic words in a 30-sentence sample | 🔍 |
| `digit_vs_all` | de Vel et al. (2001) Table 2, p.60 "Total number of digit characters in words/C"; here digits anywhere in the text | 🔍 |
| `punc_,_ratio` | Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); per-word normalisation is this library's | 🔍 |
| `punc_._ratio` | Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); per-word normalisation is this library's | 🔍 |
| `punc_;_ratio` | Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); per-word normalisation is this library's | 🔍 |
| `punc_!_ratio` | Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); per-word normalisation is this library's | 🔍 |
| `punc_:_ratio` | Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); per-word normalisation is this library's | 🔍 |
| `punc_quote_ratio` | Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); per-word normalisation is this library's | 🔍 |
| `punc_question_ratio` | Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); per-word normalisation is this library's | 🔍 |
| `punct_density` | de Vel et al. (2001) Table 2, p.60 "Total number of punctuations/C" | 🔍 |
| `whitespace_ratio` | de Vel et al. (2001) Table 2, p.60 "Total number of white-space characters/C" | 🔍 |

### Not verification candidates

97 keys. The ⚪ ones are plain definitions (`punc_,_ratio`, `char_a`) — not named measures from the literature. The ⚫ ones are not measures at all but counts of an external tag scheme's categories; a scheme defines categories, it does not publish measurements. The 🔧 ones take their formula from a source but their application is this library's. None of the three has a number to look for.

| Key | Source | Status |
|---|---|---|
| `n_lemma_count` | — | ⚪ |
| `word_length_cv` | — | ⚪ |
| `entropy_std` | Shannon (1948) — the entropy formula; the standard deviation across segments is this library's own derivation | 🔧 |
| `sentence_length_cv` | — | ⚪ |
| `sent_len_skewness` | — | ⚪ |
| `short_sent_ratio` | This library's threshold calibration (docs/threshold-calibration.md); TR 4, EN 8 — 15th percentile of newspaper columns under the default sentence and word rules. Note: the TR value coincides with Ateşman (1997) p.74, where the easiest text has a mean sentence length of 4 words; that is a text mean, not a threshold, so it is not the source. Calibrated on newspaper columns only | 🔧 |
| `long_sent_ratio` | This library's threshold calibration (docs/threshold-calibration.md); TR 17, EN 32 — 85th percentile of newspaper columns under the default sentence and word rules. Ateşman's 30 was not used: that is the mean of the hardest text, not a single-sentence threshold (in Turkish newspaper columns 30 words is above the 95th percentile, so as a threshold it would almost never fire). Calibrated on newspaper columns only | 🔧 |
| `sent_len_entropy` | Shannon (1948) — the entropy formula; applying it to the distribution of sentence lengths is this library's own decision | 🔧 |
| `para_len_cv` | — | ⚪ |
| `sents_per_para_cv` | — | ⚪ |
| `para_count_norm` | — | ⚪ |
| `pos_noun` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_propn` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_verb` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_adj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_adv` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_det` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_adp` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_intj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_cconj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_sconj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_num` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_aux` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `question_per_sent` | — | ⚪ |
| `sentfinal_noun` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_propn` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_verb` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_adj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_adv` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_det` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_adp` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_intj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_cconj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_sconj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_num` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_aux` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_pron` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_other` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `surface_per_lemma` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_tense_past` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_tense_pres` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_tense_fut` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_aspect_perf` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_aspect_imp` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_aspect_prog` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_case_nom` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_case_acc` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_case_dat` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_case_loc` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_case_abl` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_case_gen` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_person_1` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_person_2` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_person_3` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_number_sing` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_number_plur` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_voice_pass` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `vowel_ratio` | — | ⚪ |
| `syllable_cv` | — | ⚪ |
| `sentence_syllable_mean` | — | ⚪ |
| `sentence_syllable_cv` | — | ⚪ |
| `polysyllabic_word_ratio` | McLaughlin (1969) p.641; polysyllabic = 3+ syllables — the ratio form of SMOG's input, not the source's own measure | 🔧 |
| `punc_-_ratio` | — | ⚪ |
| `punc_ellipsis_ratio` | — | ⚪ |
| `punc_paren_ratio` | — | ⚪ |
| `punc_total_ratio` | — | ⚪ |
| `punct_entropy` | Shannon (1948) — the entropy formula; applying it to the distribution of punctuation types is this library's own decision | 🔧 |
| `consecutive_punct_ratio` | — | ⚪ |
| `punct_variety` | — | ⚪ |
| `uppercase_ratio` | — | ⚪ |
| `all_caps_word_ratio` | — | ⚪ |
| `char_a` | — | ⚪ |
| `char_b` | — | ⚪ |
| `char_c` | — | ⚪ |
| `char_d` | — | ⚪ |
| `char_e` | — | ⚪ |
| `char_f` | — | ⚪ |
| `char_g` | — | ⚪ |
| `char_h` | — | ⚪ |
| `char_i` | — | ⚪ |
| `char_j` | — | ⚪ |
| `char_k` | — | ⚪ |
| `char_l` | — | ⚪ |
| `char_m` | — | ⚪ |
| `char_n` | — | ⚪ |
| `char_o` | — | ⚪ |
| `char_p` | — | ⚪ |
| `char_q` | — | ⚪ |
| `char_r` | — | ⚪ |
| `char_s` | — | ⚪ |
| `char_t` | — | ⚪ |
| `char_u` | — | ⚪ |
| `char_v` | — | ⚪ |
| `char_w` | — | ⚪ |
| `char_x` | — | ⚪ |
| `char_y` | — | ⚪ |
| `char_z` | — | ⚪ |

## Syllabification — 10/10

Syllabification feeds eight `syllable_*` keys and all three Turkish readability formulas at once. The comparison below tests **the split, not the count**: a word broken in the wrong place can still yield the right number of syllables, and a count comparison would not catch it.

Source: TDK, "Hece Yapısı ve Satır Sonunda Kelimelerin Bölünmesi" (tdk.gov.tr, 2019).

| Word | TDK | Ours | Status |
|---|---|---|---|
| aldı | `al-dı` | `al-dı` | ✅ |
| altlık | `alt-lık` | `alt-lık` | ✅ |
| türkçe | `türk-çe` | `türk-çe` | ✅ |
| program | `prog-ram` | `prog-ram` | ✅ |
| kontrol | `kont-rol` | `kont-rol` | ✅ |
| santral | `sant-ral` | `sant-ral` | ✅ |
| saat | `sa-at` | `sa-at` | ✅ |
| karaosmanoğlu | `ka-ra-os-ma-noğ-lu` | `ka-ra-os-ma-noğ-lu` | ✅ |
| tren | `tren` | `tren` | ✅ |
| strateji | `stra-te-ji` | `stra-te-ji` | ✅ |

## Appendix — Kincaid Appendix A, passage by passage

The 18 comparisons behind the two 🟡 rows in the main table (`ari`, `flesch_kincaid_grade`). The intermediate counts (strokes, words) are here so that when a number differs you can see which input it came from.

The **FRE band** column is a separate check: Table 1's Flesch column prints not a 0-100 score but Flesch's own grade band (`8-9` = FRE 60-70, and so on). It asks whether our FRE falls inside that band.

Passage texts: `tests/veri/kincaid/`. Measurement: `scripts/kincaid_olcum.py`.

| # | Strokes | Words | ARI source | ARI ours | Diff | FKGL source | FKGL ours | Diff | FRE band |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 663 | 148 | 10.6 | 10.24 | -0.36 | 9.7 | 9.64 | -0.06 | 8-9 ✅ |
| 2 | 668 | 122 | 20.3 | 16.56 | -3.74 | 16.7 | 15.79 | -0.91 | 16+ ✅ |
| 3 | 684 | 127 | 13.3 | 13.01 | -0.29 | 12.7 | 12.67 | -0.03 | 13-16 ✅ |
| 4 | 749 | 155 | 8.8 | 8.38 | -0.42 | 8.2 | 8.18 | -0.02 | 8-9 ✅ |
| 5 | 517 | 104 | 9.5 | 9.41 | -0.09 | 7.1 | 5.94 | -1.16 | 8-9 ❌ |
| 6 | 685 | 133 | 12.4 | 12.33 | -0.07 | 12.3 | 12.05 | -0.25 | 13-16 ✅ |
| 7 | 1017 | 197 | 12.7 | 12.74 | +0.04 | 11.7 | 11.96 | +0.26 | 13-16 ✅ |
| 8 | 1061 | 197 | 16.4 | 16.25 | -0.15 | 14.7 | 14.98 | +0.28 | 13-16 ✅ |
| 9 | 837 | 181 | 9.7 | 9.40 | -0.30 | 8.0 | 8.16 | +0.16 | 7 ❌ |
| 10 | 1177 | 231 | 13.1 | 12.19 | -0.91 | 11.7 | 11.18 | -0.52 | 13-16 ✅ |
| 11 | 822 | 170 | 7.8 | 7.88 | +0.08 | 8.1 | 7.77 | -0.33 | 8-9 ✅ |
| 12 | 997 | 214 | 16.7 | 15.80 | -0.90 | 11.8 | 7.52 | -4.28 | 10-12 ❌ |
| 13 | 894 | 183 | 13.4 | 13.02 | -0.38 | 10.0 | 10.01 | +0.01 | 10-12 ✅ |
| 14 | 681 | 137 | 12.0 | 11.77 | -0.23 | 12.5 | 12.11 | -0.39 | 13-16 ✅ |
| 15 | 985 | 217 | 9.7 | 8.99 | -0.71 | 8.4 | 8.16 | -0.24 | 8-9 ✅ |
| 16 | 882 | 163 | 13.5 | 13.11 | -0.39 | 13.8 | 14.13 | +0.33 | 16+ ✅ |
| 17 | 1240 | 240 | 10.4 | 9.96 | -0.44 | 9.3 | 8.83 | -0.47 | 10-12 ✅ |
| 18 | 782 | 144 | 10.9 | 10.69 | -0.21 | 6.6 | 6.81 | +0.21 | — |

ARI mean absolute difference **0.54**, largest **3.74** (passage 2). FKGL mean absolute difference **0.55**, largest **4.28** (passage 12). Inside the FRE band: **14/17**.
