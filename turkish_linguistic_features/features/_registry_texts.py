"""Registry metin tabloları — 187 statik anahtarın açıklaması, formülü,
ölçüm şartı ve künyesi.

Bu dosya **veridir**, mantık içermez. ``registry.py``'den ayrı durmasının
sebebi 800 satır kuralı değil, iki parçanın farklı sebeplerle değişmesi:
yapı bir kez yazılıp incelenir, künye metinleri arşive yeni kaynak girdikçe
tekrar tekrar düzeltilir (2026-09-18, Efe). Ayrı dosyada künye düzeltmesinin
diff'i mantığa hiç dokunmuyor.

İçerik onaylanmış bir taslaktan bir kez taşındı. **Bundan sonrası elle
bakılır** — taslak tarihsel bir kayıttır, bu dosyayı ondan yeniden üretmek buraya yapılmış düzeltmeleri siler.
Tek public giriş noktası ``registry.describe_feature``; buradaki sözlükler
doğrudan okunabilir ama taahhüt değildir.

**Yazım kuralları.**

- ``description`` ve ``formula`` İngilizce (2026-09-17, Efe).
- Formüllerde **literatür yazımı**: ``N`` token, ``V`` tip, ``V1``/``V2``
  bir/iki kez geçen tip, ``f`` sıklık, ``r`` sıra, ``h`` h-point. Kodun yerel
  değişken adı farklıysa formül yine kaynağı izler (2026-09-18, Efe).
- ``requires`` olumlu şart: önce sayı, sonra parantezde ``FeatureParams``
  alan adı — ``"at least 100 words (mtld_min_tokens)"``. Noktalamanın
  sayıldığı yerde "tokens", sayılmadığı yerde "words".
- ``citation`` yalnız ``tlf-kaynaklar`` arşivindeki bir dosyaya dayanır.
  Özgün yayın arşivde yoksa aktaran kaynak yazılır ve zincir açıkça
  işaretlenir: ``"Ateşman (1997), aktaran Kalyoncu (2025) s.49"``. Künyesi
  olmayan anahtar adlandırılmış bir literatür ölçüsü değildir;
  ``describe_feature`` orada ``citation: None`` döndürür ve bu
  **kasıtlıdır** — literatür ölçüsü gibi göstermek akademik dürüstlük
  ihlali olurdu (K10). ``None`` ölçünün **kime ait olduğunu söylemez**:
  kimi anahtar saf tanımdır, kimi bir dış etiket şemasının kategorilerini
  sayar (2026-09-19, Efe).
"""

from __future__ import annotations

__all__ = [
    "FEATURE_CITATIONS",
    "FEATURE_DESCRIPTIONS",
    "FEATURE_FORMULAS",
    "FEATURE_REQUIRES",
]



# Anahtar → NE ölçtüğü.
FEATURE_DESCRIPTIONS: dict[str, str] = {
    # ── lexical ─────────────────────────────────────────────────
    'lemma_count': 'number of distinct lemmas',
    'word_len_mean': 'mean word length in characters',
    'ttr': 'type-token ratio; falls as the text grows',
    'mattr': 'moving-average TTR',
    'herdan_c': "Herdan's C (LogTTR)",
    'sichel_s': 'share of types occurring exactly twice',
    'zipf_exponent': 'Zipf slope',
    'zipf_r2': 'fit quality of the Zipf line',
    'zipf_mandelbrot_q': 'Zipf-Mandelbrot shift',
    'zipf_mandelbrot_s': 'Zipf-Mandelbrot slope',
    'mtld': 'measure of textual lexical diversity',
    'dugast_u': "Dugast's Uber index",
    'guiraud_r': "Guiraud's root TTR",
    'cttr': "Carroll's corrected TTR",
    'summer_s': "Summer's S, log-log type-token ratio",
    'maas_a2': "Maas' a²; higher = more repetitive",
    'herdan_vm': "Herdan's Vm; higher = more repetitive",
    'heaps_beta': 'vocabulary growth rate',
    'entropy': 'Shannon entropy of word frequencies',
    'yule_k': "Yule's K; higher = more repetitive",
    'simpson_d': 'chance that two words drawn without replacement are the same type',
    'brunet_w': "Brunet's W",
    'hapax_ratio': 'share of types occurring once',
    'hapax_token_ratio': 'share of tokens that occur once',
    'vocd_d': 'voc-D',
    'hdd': 'HD-D',
    'msttr': 'mean segmental TTR',
    'noun_variation': 'noun variation NV',
    'verb_variation': 'verb variation VV1',
    'adj_variation': 'adjective variation AdjV',
    'adv_variation': 'adverb variation AdvV',
    'wordfreq_mean': 'how common the lexical words are in general language',
    'wordfreq_rare_ratio': 'share of rare lexical words',
    # ── frequency_structure ─────────────────────────────────────
    'h_point': 'rank where frequency equals rank',
    'vocab_richness_r1': 'share of the text below the h-point',
    'vocab_richness_r4': 'inverted Gini',
    'repeat_rate': 'chance that two words drawn with replacement are the same type',
    'rr_mcintosh': 'McIntosh relative repeat rate',
    'gini_coef': 'inequality of word use',
    'curve_length': 'arc length of the rank-frequency curve',
    'curve_length_r': 'share of the curve length below the h-point',
    'lambda_pa': 'length-normalised curve length',
    'adjusted_modulus': 'distance from the h-point to the curve ends',
    'writers_view_alpha': 'angle at the h-point, in radians',
    'thematic_concentration': 'weight of content words above the h-point',
    'secondary_thematic_concentration': 'weight of content words up to rank 2h',
    # ── sentence ────────────────────────────────────────────────
    'sent_len_mean': 'mean sentence length in words',
    'sent_len_char_mean': 'mean sentence length in characters',
    'short_sent_ratio': 'share of short sentences',
    'long_sent_ratio': 'share of long sentences',
    'sent_len_median': 'median sentence length',
    'sent_len_entropy': 'variety of sentence lengths',
    # ── paragraph ───────────────────────────────────────────────
    'para_len_mean': 'mean paragraph length',
    'sents_per_para_mean': 'mean sentences per paragraph',
    # ── pos ─────────────────────────────────────────────────────
    'pos_noun_ratio': 'share of NOUN words',
    'pos_propn_ratio': 'share of PROPN words',
    'pos_verb_ratio': 'share of VERB words',
    'pos_adj_ratio': 'share of ADJ words',
    'pos_adv_ratio': 'share of ADV words',
    'pos_det_ratio': 'share of DET words',
    'pos_adp_ratio': 'share of ADP words',
    'pos_aux_ratio': 'share of AUX words',
    'pos_cconj_ratio': 'share of CCONJ words',
    'pos_sconj_ratio': 'share of SCONJ words',
    'pos_num_ratio': 'share of NUM words',
    'pos_intj_ratio': 'share of INTJ words',
    # ── syntactic ───────────────────────────────────────────────
    'question_sent_ratio': 'share of sentences ending in "?"',
    'pronoun_ratio': 'share of pronoun words',
    'verb_dist_mean': 'mean word gap between consecutive verbs',
    'activity_ratio': 'activity Q',
    'lexical_density': 'share of lexical words',
    'posddev': 'how uneven the POS distribution is',
    'posdiv': 'how much sentences differ from the document in POS make-up',
    # ── syntactic_dep ───────────────────────────────────────────
    'arc_len_mean': 'mean dependency distance (MDD2)',
    'parse_depth_mean': 'mean hierarchical distance (MHD2)',
    'sentfinal_noun_ratio': 'share of sentences ending in a NOUN',
    'sentfinal_propn_ratio': 'share of sentences ending in a PROPN',
    'sentfinal_verb_ratio': 'share of sentences ending in a VERB',
    'sentfinal_adj_ratio': 'share of sentences ending in a ADJ',
    'sentfinal_adv_ratio': 'share of sentences ending in a ADV',
    'sentfinal_det_ratio': 'share of sentences ending in a DET',
    'sentfinal_adp_ratio': 'share of sentences ending in a ADP',
    'sentfinal_intj_ratio': 'share of sentences ending in a INTJ',
    'sentfinal_cconj_ratio': 'share of sentences ending in a CCONJ',
    'sentfinal_sconj_ratio': 'share of sentences ending in a SCONJ',
    'sentfinal_num_ratio': 'share of sentences ending in a NUM',
    'sentfinal_aux_ratio': 'share of sentences ending in a AUX',
    'sentfinal_pron_ratio': 'share of sentences ending in a PRON',
    'sentfinal_other_ratio': 'share of sentences ending in any other tag',
    # ── morphological ───────────────────────────────────────────
    'surface_per_lemma': 'distinct forms per lemma',
    'tense_past_ratio': 'share of words tagged Tense=Past',
    'tense_pres_ratio': 'share of words tagged Tense=Pres',
    'tense_fut_ratio': 'share of words tagged Tense=Fut',
    'aspect_perf_ratio': 'share of words tagged Aspect=Perf',
    'aspect_imp_ratio': 'share of words tagged Aspect=Imp',
    'aspect_prog_ratio': 'share of words tagged Aspect=Prog',
    'case_nom_ratio': 'share of words tagged Case=Nom',
    'case_acc_ratio': 'share of words tagged Case=Acc',
    'case_dat_ratio': 'share of words tagged Case=Dat',
    'case_loc_ratio': 'share of words tagged Case=Loc',
    'case_abl_ratio': 'share of words tagged Case=Abl',
    'case_gen_ratio': 'share of words tagged Case=Gen',
    'person_1_ratio': 'share of words tagged Person=1',
    'person_2_ratio': 'share of words tagged Person=2',
    'person_3_ratio': 'share of words tagged Person=3',
    'number_sing_ratio': 'share of words tagged Number=Sing',
    'number_plur_ratio': 'share of words tagged Number=Plur',
    'voice_pass_ratio': 'share of passive verbs',
    # ── morphological_zeyrek ────────────────────────────────────
    'zeyrek_agglutination_depth': 'visible suffixes per word',
    'zeyrek_suffix_char_length_ratio': 'share of word letters in suffixes',
    'zeyrek_suffix_bigram_entropy': 'variety of suffix sequences',
    'zeyrek_derivational_suffix_ratio': 'share of derivational suffixes',
    'zeyrek_verb_suffix_diversity': 'suffix variety on verbs',
    'zeyrek_tense_past_def_ratio': 'share of verbs in the definite past (-DI)',
    'zeyrek_tense_past_nar_ratio': 'share of verbs in the reported past (-mIş)',
    'zeyrek_tense_present_ratio': 'share of verbs in the present',
    'zeyrek_tense_future_ratio': 'share of verbs in the future (-AcAk)',
    'zeyrek_negation_ratio': 'share of negative verbs',
    'zeyrek_passive_ratio': 'share of passive verbs',
    'zeyrek_plural_ratio': 'share of plural nominals',
    'zeyrek_case_acc_ratio': 'share of words in the accusative case',
    'zeyrek_case_dat_ratio': 'share of words in the dative case',
    'zeyrek_case_loc_ratio': 'share of words in the locative case',
    'zeyrek_case_abl_ratio': 'share of words in the ablative case',
    'zeyrek_case_gen_ratio': 'share of words in the genitive case',
    'zeyrek_case_ins_ratio': 'share of words in the instrumental case',
    'zeyrek_conditional_suffix_ratio': 'share of conditional verbs',
    'zeyrek_causative_suffix_ratio': 'share of causative verbs',
    'zeyrek_modal_possibility_ratio': 'share of ability verbs',
    'zeyrek_modal_necessity_ratio': 'share of necessity verbs',
    'zeyrek_question_particle_ratio': 'share of question particles',
    # ── phonetic ────────────────────────────────────────────────
    'vowel_ratio': 'share of vowels',
    'front_vowel_ratio': 'share of front vowels',
    'back_vowel_ratio': 'share of back vowels',
    'harmony_fronting_ratio': 'share of words obeying front/back vowel harmony (TR only)',
    'harmony_rounding_ratio': 'share of words obeying rounding vowel harmony (TR only)',
    'syllable_mean': 'mean syllables per word',
    'syllable_1_ratio': 'share of words with 1 syllable',
    'syllable_2_ratio': 'share of words with 2 syllables',
    'syllable_3_ratio': 'share of words with 3 syllables',
    'syllable_4_ratio': 'share of words with 4 syllables',
    'syllable_5_ratio': 'share of words with 5 syllables',
    'syllable_6plus_ratio': 'share of words with 6 or more syllables',
    'sent_syllable_mean': 'syllables per sentence',
    # ── readability ─────────────────────────────────────────────
    'bezirci_yilmaz': 'Bezirci-Yılmaz; higher = harder',
    'atesman': 'Ateşman; higher = easier',
    'cetinkaya_uzun': 'Çetinkaya-Uzun; higher = easier',
    'flesch_reading_ease': 'Flesch Reading Ease (EN)',
    'flesch_kincaid_grade': 'Flesch-Kincaid grade (EN)',
    'smog': 'SMOG grade (EN)',
    'ari': 'Automated Readability Index',
    'coleman_liau': 'Coleman-Liau index',
    'lix': "Björnsson's LIX",
    'polysyllabic_word_ratio': 'share of 3+ syllable words (EN)',
    'long_word_ratio': 'share of 7+ letter words',
    # ── punctuation ─────────────────────────────────────────────
    'digit_ratio': 'share of digit characters',
    'punct_comma_ratio': 'share of comma marks among all marks',
    'punct_period_ratio': 'share of full stop marks among all marks',
    'punct_semicolon_ratio': 'share of semicolon marks among all marks',
    'punct_exclamation_ratio': 'share of exclamation marks among all marks',
    'punct_colon_ratio': 'share of colon marks among all marks',
    'punct_dash_ratio': 'share of hyphen or dash marks among all marks',
    'punct_ellipsis_ratio': 'share of ellipsis marks among all marks',
    'punct_paren_ratio': 'share of parenthesis marks among all marks',
    'punct_quote_ratio': 'share of quotation marks among all marks',
    'punct_question_ratio': 'share of question marks among all marks',
    'punct_char_ratio': 'share of punctuation marks among characters',
    'punct_entropy': 'variety of punctuation types',
    'consecutive_punct_ratio': 'share of marks directly next to another mark',
    'whitespace_ratio': 'share of whitespace characters',
    'punct_variety': 'number of punctuation types used (0–10)',
    'uppercase_ratio': 'share of capitalised words',
    'all_caps_word_ratio': 'share of all-caps words',
    # ── chars (dinamik grup) ───────────────────────────────────────
    'chars': 'share of that letter among alphabet letters',
    # ── custom_ngrams (dinamik grup) ───────────────────────────────
    'custom_ngrams': 'count of a user-supplied word or POS-tag sequence within sentences',
}

# Anahtar → NASIL hesaplandığı. Anahtarın kendi satırı yoksa describe_feature
# grup adındaki satıra düşer; bu yalnız dinamik gruplarda (chars, custom_ngrams)
# var, 187 statik anahtarın hepsinin kendi satırı var.
FEATURE_FORMULAS: dict[str, str] = {
    # ── lexical ─────────────────────────────────────────────────
    'lemma_count': 'V over lemmas',
    'word_len_mean': 'sum(len(w)) / N',
    'ttr': 'V / N',
    'mattr': 'mean TTR of every sliding window of mattr_window words',
    'herdan_c': 'log(V) / log(N)',
    'sichel_s': 'V2 / V',
    'zipf_exponent': 'abs(slope) of least-squares fit log f(r) ~ log r',
    'zipf_r2': 'R² of that fit',
    'zipf_mandelbrot_q': 'q minimising the residual of log f ~ log(r + q), grid 0–10 step 0.1',
    'zipf_mandelbrot_s': 'abs(slope) at that q',
    'mtld': 'mean words per factor (TTR drops to mtld_threshold), forward and backward averaged',
    'dugast_u': '(ln N)^2 / (ln N - ln V)',
    'guiraud_r': 'V / sqrt(N)',
    'cttr': 'V / sqrt(2N)',
    'summer_s': 'ln(ln V) / ln(ln N)',
    'maas_a2': '(ln N - ln V) / (ln N)^2',
    'herdan_vm': 'sqrt(sum(f^2) / N^2 - 1 / V)',
    'heaps_beta':
        'least-squares slope of log V ~ log N over prefixes every heaps_step words, not '
        'clipped',
    'entropy': '-sum(p * ln p)',
    'yule_k': '10000 * (sum(f^2) - N) / N^2',
    'simpson_d': 'sum(f(f-1)) / (N(N-1))',
    'brunet_w': 'N^(V^-a), a = brunet_w_a',
    'hapax_ratio': 'V1 / V',
    'hapax_token_ratio': 'V1 / N',
    'vocd_d':
        'D fitted to mean TTR of random samples of vocd_sample_min–vocd_sample_max words, '
        'vocd_num_runs runs averaged',
    'hdd': 'expected TTR of a hdd_sample_size-word sample (hypergeometric)',
    'msttr': 'mean TTR of full msttr_segment_size-word segments',
    'noun_variation': 'distinct noun lemmas / lexical words',
    'verb_variation': 'distinct verb lemmas / verbs',
    'adj_variation': 'distinct adjective lemmas / lexical words',
    'adv_variation': 'distinct adverb lemmas / lexical words',
    'wordfreq_mean': 'mean wordfreq Zipf score of lexical-word lemmas (unlisted = 0)',
    'wordfreq_rare_ratio': 'lexical-word lemmas with Zipf score <= 3 / lexical words',
    # ── frequency_structure ─────────────────────────────────────
    'h_point': 'r with f(r) = r, interpolated otherwise',
    'vocab_richness_r1': '1 - (F(h) - h^2 / (2N))',
    'vocab_richness_r4': '1 - G',
    'repeat_rate': 'sum((f/N)^2)',
    'rr_mcintosh': '(1 - sqrt(RR)) / (1 - 1/sqrt(V))',
    'gini_coef': '(V + 1 - 2 * sum(r * f(r)) / N) / V, rank 1 = most frequent',
    'curve_length': 'sum(sqrt((f(r) - f(r+1))^2 + 1))',
    'curve_length_r': '1 - L(h) / L',
    'lambda_pa': 'L * ln(N) / N',
    'adjusted_modulus': 'sqrt((f1/h)^2 + (V/h)^2) / ln(N)',
    'writers_view_alpha': 'arccos of the angle between (1, f1) and (V, 1) seen from (h, h)',
    'thematic_concentration': "sum(2(h - r') f(r')) / (h(h-1) f1), content words with r' < h",
    'secondary_thematic_concentration': "sum((2h - r') f(r')) / (h(2h-1) f1), r' <= 2h",
    # ── sentence ────────────────────────────────────────────────
    'sent_len_mean': 'mean words per sentence',
    'sent_len_char_mean': 'mean len(tokens joined by single spaces)',
    'short_sent_ratio': 'sentences with fewer than short_sent_threshold words / sentences',
    'long_sent_ratio': 'sentences with more than long_sent_threshold words / sentences',
    'sent_len_median': 'median words per sentence',
    'sent_len_entropy': 'Shannon entropy (nats) of the distribution of words per sentence',
    # ── paragraph ───────────────────────────────────────────────
    'para_len_mean': 'mean words per paragraph (blank line = boundary)',
    'sents_per_para_mean': 'mean count of [.!?…]+ per paragraph (at least 1)',
    # ── pos ─────────────────────────────────────────────────────
    'pos_noun_ratio': 'tag count / words',
    'pos_propn_ratio': 'tag count / words',
    'pos_verb_ratio': 'tag count / words',
    'pos_adj_ratio': 'tag count / words',
    'pos_adv_ratio': 'tag count / words',
    'pos_det_ratio': 'tag count / words',
    'pos_adp_ratio': 'tag count / words',
    'pos_aux_ratio': 'tag count / words',
    'pos_cconj_ratio': 'tag count / words',
    'pos_sconj_ratio': 'tag count / words',
    'pos_num_ratio': 'tag count / words',
    'pos_intj_ratio': 'tag count / words',
    # ── syntactic ───────────────────────────────────────────────
    'question_sent_ratio': 'sentences whose final mark contains "?" / sentences',
    'pronoun_ratio': 'PRON / words',
    'verb_dist_mean': 'mean difference of VERB positions',
    'activity_ratio': 'VERB / (VERB + ADJ)',
    'lexical_density': '(NOUN + PROPN + VERB + ADJ + ADV) / all words, PUNCT and SYM excluded',
    'posddev': 'population std of the 12 pos_*_ratio shares',
    'posdiv': 'mean over sentences of KL(sentence POS ‖ document POS), nats',
    # ── syntactic_dep ───────────────────────────────────────────
    'arc_len_mean':
        'mean over sentences of mean abs(word position - head position), punctuation removed, '
        'root excluded',
    'parse_depth_mean': 'mean over sentences of mean steps to the root, capped at max_parse_depth',
    'sentfinal_noun_ratio': 'sentences ending in that tag / sentences',
    'sentfinal_propn_ratio': 'sentences ending in that tag / sentences',
    'sentfinal_verb_ratio': 'sentences ending in that tag / sentences',
    'sentfinal_adj_ratio': 'sentences ending in that tag / sentences',
    'sentfinal_adv_ratio': 'sentences ending in that tag / sentences',
    'sentfinal_det_ratio': 'sentences ending in that tag / sentences',
    'sentfinal_adp_ratio': 'sentences ending in that tag / sentences',
    'sentfinal_intj_ratio': 'sentences ending in that tag / sentences',
    'sentfinal_cconj_ratio': 'sentences ending in that tag / sentences',
    'sentfinal_sconj_ratio': 'sentences ending in that tag / sentences',
    'sentfinal_num_ratio': 'sentences ending in that tag / sentences',
    'sentfinal_aux_ratio': 'sentences ending in that tag / sentences',
    'sentfinal_pron_ratio': 'sentences ending in that tag / sentences',
    'sentfinal_other_ratio': 'sentences ending in a tag outside the 13 / sentences',
    # ── morphological ───────────────────────────────────────────
    'surface_per_lemma': 'distinct (lemma, form) pairs / distinct lemmas, lowercased',
    'tense_past_ratio': 'words with Tense=X / words with any Tense',
    'tense_pres_ratio': 'words with Tense=X / words with any Tense',
    'tense_fut_ratio': 'words with Tense=X / words with any Tense',
    'aspect_perf_ratio': 'words with Aspect=X / words with any Aspect',
    'aspect_imp_ratio': 'words with Aspect=X / words with any Aspect',
    'aspect_prog_ratio': 'words with Aspect=X / words with any Aspect',
    'case_nom_ratio': 'words with Case=X / words with any Case',
    'case_acc_ratio': 'words with Case=X / words with any Case',
    'case_dat_ratio': 'words with Case=X / words with any Case',
    'case_loc_ratio': 'words with Case=X / words with any Case',
    'case_abl_ratio': 'words with Case=X / words with any Case',
    'case_gen_ratio': 'words with Case=X / words with any Case',
    'person_1_ratio': 'words with Person=X / words with any Person',
    'person_2_ratio': 'words with Person=X / words with any Person',
    'person_3_ratio': 'words with Person=X / words with any Person',
    'number_sing_ratio': 'words with Number=X / words with any Number',
    'number_plur_ratio': 'words with Number=X / words with any Number',
    'voice_pass_ratio': 'VERB with Voice=Pass / VERB',
    # ── morphological_zeyrek ────────────────────────────────────
    'zeyrek_agglutination_depth': 'visible suffixes / analysed words',
    'zeyrek_suffix_char_length_ratio': 'suffix letters / word letters',
    'zeyrek_suffix_bigram_entropy': 'Shannon entropy (nats) of within-word visible suffix pairs',
    'zeyrek_derivational_suffix_ratio': 'derivational / visible suffixes',
    'zeyrek_verb_suffix_diversity': 'mean distinct visible suffix tags per verb_suffix_window-verb chunk',
    'zeyrek_tense_past_def_ratio': 'verbs whose last tense tag is X / verbs',
    'zeyrek_tense_past_nar_ratio': 'verbs whose last tense tag is X / verbs',
    'zeyrek_tense_present_ratio': 'verbs whose last tense tag is X / verbs',
    'zeyrek_tense_future_ratio': 'verbs whose last tense tag is X / verbs',
    'zeyrek_negation_ratio': 'verbs with Neg or Unable / verbs',
    'zeyrek_passive_ratio': 'verbs with Pass / verbs',
    'zeyrek_plural_ratio': 'words with A3pl on a non-verb part / analysed words',
    'zeyrek_case_acc_ratio': 'words with Acc … Ins / analysed words',
    'zeyrek_case_dat_ratio': 'words with Acc … Ins / analysed words',
    'zeyrek_case_loc_ratio': 'words with Acc … Ins / analysed words',
    'zeyrek_case_abl_ratio': 'words with Acc … Ins / analysed words',
    'zeyrek_case_gen_ratio': 'words with Acc … Ins / analysed words',
    'zeyrek_case_ins_ratio': 'words with Acc … Ins / analysed words',
    'zeyrek_conditional_suffix_ratio': 'verbs with Cond / verbs',
    'zeyrek_causative_suffix_ratio': 'verbs with Caus / verbs',
    'zeyrek_modal_possibility_ratio': 'verbs with Able or Unable / verbs',
    'zeyrek_modal_necessity_ratio': 'verbs with Neces / verbs',
    'zeyrek_question_particle_ratio': 'words with root Ques / analysed words',
    # ── phonetic ────────────────────────────────────────────────
    'vowel_ratio': 'vowels / alphabet letters',
    'front_vowel_ratio': 'front vowels / alphabet letters',
    'back_vowel_ratio': 'back vowels / alphabet letters',
    'harmony_fronting_ratio':
        'words whose vowels are all front or all back / words with 2+ vowels',
    'harmony_rounding_ratio':
        'words where every vowel after an unrounded one is unrounded and every '
        'vowel after a rounded one is close-rounded or open-unrounded / words '
        'with 2+ vowels',
    'syllable_mean': 'mean syllables per syllabifiable word',
    'syllable_1_ratio': 'words with 1 syllable / syllabifiable words',
    'syllable_2_ratio': 'words with 2 syllables / syllabifiable words',
    'syllable_3_ratio': 'words with 3 syllables / syllabifiable words',
    'syllable_4_ratio': 'words with 4 syllables / syllabifiable words',
    'syllable_5_ratio': 'words with 5 syllables / syllabifiable words',
    'syllable_6plus_ratio': 'words with 6 or more syllables / syllabifiable words',
    'sent_syllable_mean': 'mean syllables per sentence',
    # ── readability ─────────────────────────────────────────────
    'bezirci_yilmaz':
        'sqrt(words/sentence * (0.84 H3 + 1.5 H4 + 3.5 H5 + 26.25 H6)), Hk per sentence',
    'atesman': '198.825 - 40.175 * syllables/word - 2.610 * words/sentence',
    'cetinkaya_uzun':
        '118.823 - 25.987 * syllables/word - 0.971 * words/sentence; ": ( )" end sentences',
    'flesch_reading_ease': '206.835 - 1.015 * words/sentence - 84.6 * syllables/word',
    'flesch_kincaid_grade': '0.39 * words/sentence + 11.8 * syllables/word - 15.59',
    'smog': '3.1291 + 1.0430 * sqrt(polysyllables * 30 / sentences)',
    'ari': '4.71 * strokes/word + 0.5 * words/sentence - 21.43',
    'coleman_liau': '0.0588 * letters per 100 words - 0.296 * sentences per 100 words - 15.8',
    'lix': 'words/sentence + 100 * long words/words, long = 7+ letters',
    'polysyllabic_word_ratio': '3+ syllable words / syllabifiable words',
    'long_word_ratio': 'long words / words',
    # ── punctuation ─────────────────────────────────────────────
    'digit_ratio': 'digits / characters',
    'punct_comma_ratio': 'marks of this type / all marks',
    'punct_period_ratio': 'marks of this type / all marks',
    'punct_semicolon_ratio': 'marks of this type / all marks',
    'punct_exclamation_ratio': 'marks of this type / all marks',
    'punct_colon_ratio': 'marks of this type / all marks',
    'punct_dash_ratio': 'marks of this type / all marks',
    'punct_ellipsis_ratio': 'marks of this type / all marks',
    'punct_paren_ratio': 'marks of this type / all marks',
    'punct_quote_ratio': 'marks of this type / all marks',
    'punct_question_ratio': 'marks of this type / all marks',
    'punct_char_ratio': 'marks / characters',
    'punct_entropy': 'Shannon entropy (nats) of the 10 mark types',
    'consecutive_punct_ratio': 'adjacent marks / marks',
    'whitespace_ratio': 'whitespace / characters',
    'punct_variety': 'distinct mark types',
    'uppercase_ratio': 'words whose first letter is upper case / words with a letter',
    'all_caps_word_ratio': 'words with 2+ letters, all upper case / words with a letter',
    # ── chars (dinamik grup) ───────────────────────────────────────
    'chars': 'letter count / alphabet letters',
    # ── custom_ngrams (dinamik grup) ───────────────────────────────
    'custom_ngrams':
        'matches inside sentences; overlapping matches counted; UPPERCASE UD tags match any word '
        'with that tag',
}

# Anahtar → ölçüm şartı. Sağlanmazsa değer NaN (K4).
FEATURE_REQUIRES: dict[str, str] = {
    # ── lexical ─────────────────────────────────────────────────
    'lemma_count': 'at least 1 word',
    'word_len_mean': 'at least 1 word',
    'ttr': 'at least 1 word',
    'mattr': 'at least 100 words (2 x mattr_window)',
    'herdan_c': 'at least 2 words',
    'sichel_s': 'at least 1 word',
    'zipf_exponent': 'at least 10 distinct words',
    'zipf_r2': 'at least 10 distinct words, not all equally frequent',
    'zipf_mandelbrot_q': 'at least 10 distinct words',
    'zipf_mandelbrot_s': 'at least 10 distinct words',
    'mtld': 'at least 100 words (mtld_min_tokens) with some repetition',
    'dugast_u': 'at least 2 words, at least one repeated',
    'guiraud_r': 'at least 1 word',
    'cttr': 'at least 1 word',
    'summer_s': 'at least 3 words and 2 distinct words',
    'maas_a2': 'at least 2 words',
    'herdan_vm': 'at least 1 word',
    'heaps_beta': 'at least 300 words (heaps_min_tokens)',
    'entropy': 'at least 1 word',
    'yule_k': 'at least 1 word',
    'simpson_d': 'at least 2 words',
    'brunet_w': 'at least 1 word',
    'hapax_ratio': 'at least 1 word',
    'hapax_token_ratio': 'at least 1 word',
    'vocd_d': 'at least 50 words (vocd_min_tokens, vocd_sample_max)',
    'hdd': 'at least 42 words (hdd_sample_size)',
    'msttr': 'at least 100 words (msttr_segment_size)',
    'noun_variation': 'at least 1 lexical word (NOUN, PROPN, VERB, ADJ, ADV)',
    'verb_variation': 'at least 1 verb',
    'adj_variation': 'at least 1 lexical word',
    'adv_variation': 'at least 1 lexical word',
    'wordfreq_mean': 'at least 1 lexical word; wordfreq installed',
    'wordfreq_rare_ratio': 'at least 1 lexical word; wordfreq installed',
    # ── frequency_structure ─────────────────────────────────────
    'h_point': 'at least 1 word',
    'vocab_richness_r1': 'at least 1 word',
    'vocab_richness_r4': 'at least 1 word',
    'repeat_rate': 'at least 1 word',
    'rr_mcintosh': 'at least 2 distinct words',
    'gini_coef': 'at least 1 word',
    'curve_length': 'at least 1 word',
    'curve_length_r': 'at least 2 distinct words',
    'lambda_pa': 'at least 1 word',
    'adjusted_modulus': 'at least 2 words',
    'writers_view_alpha': 'at least 1 word; undefined when the h-point meets a curve end',
    'thematic_concentration': 'at least one repeated word',
    'secondary_thematic_concentration': 'at least 1 word',
    # ── sentence ────────────────────────────────────────────────
    'sent_len_mean': 'at least 1 sentence with a letter',
    'sent_len_char_mean': 'at least 1 sentence',
    'short_sent_ratio': 'at least 1 sentence with a letter',
    'long_sent_ratio': 'at least 1 sentence with a letter',
    'sent_len_median': 'at least 1 sentence with a letter',
    'sent_len_entropy': 'at least 2 sentences with a letter',
    # ── paragraph ───────────────────────────────────────────────
    'para_len_mean': 'at least 1 paragraph',
    'sents_per_para_mean': 'at least 1 paragraph',
    # ── pos ─────────────────────────────────────────────────────
    'pos_noun_ratio': 'at least 1 word',
    'pos_propn_ratio': 'at least 1 word',
    'pos_verb_ratio': 'at least 1 word',
    'pos_adj_ratio': 'at least 1 word',
    'pos_adv_ratio': 'at least 1 word',
    'pos_det_ratio': 'at least 1 word',
    'pos_adp_ratio': 'at least 1 word',
    'pos_aux_ratio': 'at least 1 word',
    'pos_cconj_ratio': 'at least 1 word',
    'pos_sconj_ratio': 'at least 1 word',
    'pos_num_ratio': 'at least 1 word',
    'pos_intj_ratio': 'at least 1 word',
    # ── syntactic ───────────────────────────────────────────────
    'question_sent_ratio': 'at least 1 sentence',
    'pronoun_ratio': 'at least 1 word',
    'verb_dist_mean': 'at least 2 verbs',
    'activity_ratio': 'at least 1 verb or adjective',
    'lexical_density': 'at least 1 word',
    'posddev': 'at least 1 word',
    'posdiv': 'at least 1 word',
    # ── syntactic_dep ───────────────────────────────────────────
    'arc_len_mean': 'at least 1 sentence with 2 words',
    'parse_depth_mean': 'at least 1 sentence with 2 words',
    'sentfinal_noun_ratio': 'at least 1 sentence with a word',
    'sentfinal_propn_ratio': 'at least 1 sentence with a word',
    'sentfinal_verb_ratio': 'at least 1 sentence with a word',
    'sentfinal_adj_ratio': 'at least 1 sentence with a word',
    'sentfinal_adv_ratio': 'at least 1 sentence with a word',
    'sentfinal_det_ratio': 'at least 1 sentence with a word',
    'sentfinal_adp_ratio': 'at least 1 sentence with a word',
    'sentfinal_intj_ratio': 'at least 1 sentence with a word',
    'sentfinal_cconj_ratio': 'at least 1 sentence with a word',
    'sentfinal_sconj_ratio': 'at least 1 sentence with a word',
    'sentfinal_num_ratio': 'at least 1 sentence with a word',
    'sentfinal_aux_ratio': 'at least 1 sentence with a word',
    'sentfinal_pron_ratio': 'at least 1 sentence with a word',
    'sentfinal_other_ratio': 'at least 1 sentence with a word',
    # ── morphological ───────────────────────────────────────────
    'surface_per_lemma': 'at least 1 word',
    'tense_past_ratio': 'at least 1 word with a Tense tag',
    'tense_pres_ratio': 'at least 1 word with a Tense tag',
    'tense_fut_ratio': 'at least 1 word with a Tense tag',
    'aspect_perf_ratio': 'at least 1 word with an Aspect tag',
    'aspect_imp_ratio': 'at least 1 word with an Aspect tag',
    'aspect_prog_ratio': 'at least 1 word with an Aspect tag',
    'case_nom_ratio': 'at least 1 word with a Case tag',
    'case_acc_ratio': 'at least 1 word with a Case tag',
    'case_dat_ratio': 'at least 1 word with a Case tag',
    'case_loc_ratio': 'at least 1 word with a Case tag',
    'case_abl_ratio': 'at least 1 word with a Case tag',
    'case_gen_ratio': 'at least 1 word with a Case tag',
    'person_1_ratio': 'at least 1 word with a Person tag',
    'person_2_ratio': 'at least 1 word with a Person tag',
    'person_3_ratio': 'at least 1 word with a Person tag',
    'number_sing_ratio': 'at least 1 word with a Number tag',
    'number_plur_ratio': 'at least 1 word with a Number tag',
    'voice_pass_ratio': 'at least 1 verb',
    # ── morphological_zeyrek ────────────────────────────────────
    'zeyrek_agglutination_depth': 'at least 1 analysed word',
    'zeyrek_suffix_char_length_ratio': 'at least 1 analysed word',
    'zeyrek_suffix_bigram_entropy': 'at least 1 word with 2 visible suffixes',
    'zeyrek_derivational_suffix_ratio': 'at least 1 visible suffix',
    'zeyrek_verb_suffix_diversity': 'at least 50 verbs (verb_suffix_window)',
    'zeyrek_tense_past_def_ratio': 'at least 1 verb',
    'zeyrek_tense_past_nar_ratio': 'at least 1 verb',
    'zeyrek_tense_present_ratio': 'at least 1 verb',
    'zeyrek_tense_future_ratio': 'at least 1 verb',
    'zeyrek_negation_ratio': 'at least 1 verb',
    'zeyrek_passive_ratio': 'at least 1 verb',
    'zeyrek_plural_ratio': 'at least 1 analysed word',
    'zeyrek_case_acc_ratio': 'at least 1 analysed word',
    'zeyrek_case_dat_ratio': 'at least 1 analysed word',
    'zeyrek_case_loc_ratio': 'at least 1 analysed word',
    'zeyrek_case_abl_ratio': 'at least 1 analysed word',
    'zeyrek_case_gen_ratio': 'at least 1 analysed word',
    'zeyrek_case_ins_ratio': 'at least 1 analysed word',
    'zeyrek_conditional_suffix_ratio': 'at least 1 verb',
    'zeyrek_causative_suffix_ratio': 'at least 1 verb',
    'zeyrek_modal_possibility_ratio': 'at least 1 verb',
    'zeyrek_modal_necessity_ratio': 'at least 1 verb',
    'zeyrek_question_particle_ratio': 'at least 1 analysed word',
    # ── phonetic ────────────────────────────────────────────────
    'vowel_ratio': 'at least 1 alphabet letter',
    'front_vowel_ratio': 'at least 1 alphabet letter',
    'back_vowel_ratio': 'at least 1 alphabet letter',
    'harmony_fronting_ratio': 'at least 1 word with 2 vowels',
    'harmony_rounding_ratio': 'at least 1 word with 2 vowels',
    'syllable_mean': 'at least 1 syllabifiable word',
    'syllable_1_ratio': 'at least 1 syllabifiable word',
    'syllable_2_ratio': 'at least 1 syllabifiable word',
    'syllable_3_ratio': 'at least 1 syllabifiable word',
    'syllable_4_ratio': 'at least 1 syllabifiable word',
    'syllable_5_ratio': 'at least 1 syllabifiable word',
    'syllable_6plus_ratio': 'at least 1 syllabifiable word',
    'sent_syllable_mean': 'at least 1 sentence with a syllabifiable word',
    # ── readability ─────────────────────────────────────────────
    'bezirci_yilmaz': 'at least 1 syllabifiable word',
    'atesman': 'at least 1 syllabifiable word',
    'cetinkaya_uzun': 'at least 1 syllabifiable word',
    'flesch_reading_ease': 'at least 1 syllabifiable word',
    'flesch_kincaid_grade': 'at least 1 syllabifiable word',
    'smog': 'at least 30 sentences',
    'ari': 'at least 1 word',
    'coleman_liau': 'at least 1 word',
    'lix': 'at least 1 word',
    'polysyllabic_word_ratio': 'at least 1 syllabifiable word',
    'long_word_ratio': 'at least 1 word',
    # ── punctuation ─────────────────────────────────────────────
    'digit_ratio': 'non-empty text',
    'punct_comma_ratio': 'at least 1 punctuation mark',
    'punct_period_ratio': 'at least 1 punctuation mark',
    'punct_semicolon_ratio': 'at least 1 punctuation mark',
    'punct_exclamation_ratio': 'at least 1 punctuation mark',
    'punct_colon_ratio': 'at least 1 punctuation mark',
    'punct_dash_ratio': 'at least 1 punctuation mark',
    'punct_ellipsis_ratio': 'at least 1 punctuation mark',
    'punct_paren_ratio': 'at least 1 punctuation mark',
    'punct_quote_ratio': 'at least 1 punctuation mark',
    'punct_question_ratio': 'at least 1 punctuation mark',
    'punct_char_ratio': 'non-empty text',
    'punct_entropy': 'at least 1 punctuation mark',
    'consecutive_punct_ratio': 'at least 1 punctuation mark',
    'whitespace_ratio': 'non-empty text',
    'punct_variety': 'non-empty text',
    'uppercase_ratio': 'at least 1 word with a letter',
    'all_caps_word_ratio': 'at least 1 word with a letter',
    # ── chars (dinamik grup) ───────────────────────────────────────
    'chars': 'at least 1 alphabet letter',
    # ── custom_ngrams (dinamik grup) ───────────────────────────────
    'custom_ngrams': 'none (0 when the phrase is longer than every sentence)',
}

# Anahtar → literatür künyesi. Burada olmayan anahtarın künyesi YOKTUR;
# uydurma kaynak yazmak yerine describe_feature None döndürür.
FEATURE_CITATIONS: dict[str, str] = {
    # ── lexical ─────────────────────────────────────────────
    'ttr': 'Malvern et al. (2004); QUITA §6.1.1',
    'mattr':
        'Covington & McFall (2010); default window 50 — C&M recommend a window of 500; '
        '50 is used here so that texts of 100+ words can be measured (mattr needs '
        '2 × window)',
    'herdan_c':
        'Herdan (1960/1964), as cited in Tweedie & Baayen (1998) p.327, eq. (5)',
    'sichel_s': 'Sichel (1975); formula from Malvern et al. (2004) eq. 3.10',
    'zipf_exponent':
        'Piantadosi (2014) eq. (2); the same source criticises estimating r and f(r) '
        'from the same corpus',
    'zipf_r2':
        'Piantadosi (2014) eq. (2); the same source criticises estimating r and f(r) '
        'from the same corpus',
    'zipf_mandelbrot_q':
        'Piantadosi (2014) eq. (2); the same source criticises estimating r and f(r) '
        'from the same corpus',
    'zipf_mandelbrot_s':
        'Piantadosi (2014) eq. (2); the same source criticises estimating r and f(r) '
        'from the same corpus',
    'mtld':
        'McCarthy (2005) is the dissertation that introduced the measure — its '
        'abstract (p.vii) reads "we introduce and test a new measure of lexical '
        'diversity: the measure of textual, lexical diversity (MTLD)"; the body of the '
        'dissertation could not be obtained, so no page is given. The procedure '
        'implemented follows McCarthy & Jarvis (2010) pp.383–385',
    'dugast_u': 'Dugast (1978), as cited in Malvern et al. (2004) eq. 2.7',
    'guiraud_r':
        'Guiraud (1954) p.53, alternative form (all word types), as cited in Daller '
        '(2010); his actual law is V/√(2N), content words only',
    'cttr': 'Carroll (1964), as cited in Torruella & Capsada (2013) p.448',
    'summer_s':
        'Somers (1966), as cited in Torruella & Capsada (2013) p.448, where it is named '
        "\"Summer\"; the source gives no logarithm base, the natural logarithm is this library's "
        'choice',
    'maas_a2':
        'Maas (1972), as cited in Tweedie & Baayen (1998) p.327, eq. (7); natural logarithm, '
        'which reproduces the values in Torruella & Capsada (2013) Table 1; all logarithms in '
        'this library are natural',
    'herdan_vm': 'Herdan (1955), as cited in Tweedie & Baayen (1998) p.330, eq. (18)',
    'heaps_beta': 'Heaps (1978), as cited in Manning et al. (2008) §5.1.1',
    # Shannon entropisi beş anahtarda kullanılıyor. Formülün kaynağı hepsinde
    # aynı (Shannon 1948); ayrıldıkları yer formülün NEYE uygulandığı. Künye
    # bunu tek tek söylüyor — "Shannon (1948)" deyip bırakmak, dağılımın
    # seçimini de Shannon'a mal ederdi (2026-09-23, Efe).
    'entropy': 'Shannon (1948), as cited in QUITA §6.1.12',
    'punct_entropy':
        'Shannon (1948) — the entropy formula; applying it to the distribution of '
        "punctuation types is this library's own decision",
    # Flesch (1948) p.223, element (1); earlier use: Sherman (1888), Yule (1939) — not read,
    # so not cited (K10, 2026-10-07, Efe).
    'sent_len_mean': 'Flesch (1948) p.223, element (1) "Average Sentence Length in Words"',
    'short_sent_ratio':
        "This library's threshold calibration (docs/threshold-calibration.md); "
        'TR 4, EN 8 — 15th percentile of newspaper columns under the default sentence and word '
        'rules. Note: the '
        'TR value coincides with Ateşman (1997) p.74, where the easiest text has a '
        'mean sentence length of 4 words; that is a text mean, not a threshold, '
        'so it is not the source. Calibrated on newspaper columns only',
    'long_sent_ratio':
        "This library's threshold calibration (docs/threshold-calibration.md); "
        'TR 17, EN 32 — 85th percentile of newspaper columns under the default sentence and word '
        "rules. Ateşman's "
        '30 was not used: that is the mean of the hardest text, not a single-sentence '
        'threshold (in Turkish newspaper columns 30 words is above the 95th percentile, so as a '
        'threshold it would almost never fire). Calibrated on newspaper columns only',
    'sent_len_entropy':
        'Shannon (1948) — the entropy formula; applying it to the distribution of '
        "sentence lengths is this library's own decision",
    'yule_k': 'Yule (1944) p.53, eq. (3.22)',
    'simpson_d': 'Simpson (1949), as cited in Bestgen (2023)',
    'brunet_w': 'Brunet (1978), as cited in Tweedie & Baayen (1998) p.328, eq. (10)',
    'hapax_token_ratio': 'QUITA §6.1.6',
    'vocd_d':
        'Malvern et al. (2004) pp.56–57; procedure from McCarthy & Jarvis (2010) p.383',
    'hdd': 'McCarthy & Jarvis (2007), as cited in McCarthy & Jarvis (2010) p.383',
    'msttr':
        'Johnson (1944), as cited in Malvern et al. (2004) p.25 and McCarthy & Jarvis '
        '(2010) p.385',
    'noun_variation': 'Lu (2012) Table 2',
    'verb_variation': 'Lu (2012) Table 2',
    'adj_variation': 'Lu (2012) Table 2',
    'adv_variation': 'Lu (2012) Table 2',
    'wordfreq_mean': 'van Heuven et al. (2014) (Zipf scale)',
    'wordfreq_rare_ratio':
        'van Heuven et al. (2014) Table 1 (Zipf ≤ 3 = low frequency)',
    # ── frequency_structure ─────────────────────────────────
    'h_point': 'QUITA §6.1.2; Popescu & Altmann (2006)',
    'vocab_richness_r1': 'Popescu et al. (2009) eq. 3.8',
    'vocab_richness_r4': 'Popescu et al. (2009) eq. 3.24',
    'repeat_rate': 'QUITA §6.1.4',
    'rr_mcintosh': 'QUITA §6.1.5',
    'gini_coef': 'QUITA §6.1.8',
    'curve_length': 'QUITA §6.1.10',
    'curve_length_r': 'QUITA §6.1.11',
    'lambda_pa': 'QUITA §6.1.7; Popescu, Čech & Altmann (2011)',
    'adjusted_modulus': 'QUITA §6.1.13',
    'writers_view_alpha': 'Popescu, Mačutek & Altmann (2009) eq. 4.5',
    'thematic_concentration': 'QUITA §6.2.5',
    'secondary_thematic_concentration': 'QUITA §6.2.6',
    # ── pos ─────────────────────────────────────────────────
    'pos_noun_ratio': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'pos_propn_ratio': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'pos_verb_ratio': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'pos_adj_ratio': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'pos_adv_ratio': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'pos_det_ratio': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'pos_adp_ratio': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'pos_aux_ratio': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'pos_cconj_ratio': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'pos_sconj_ratio': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'pos_num_ratio': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'pos_intj_ratio': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    # ── syntactic ───────────────────────────────────────────
    'verb_dist_mean': 'QUITA §6.2.1',
    'activity_ratio': 'QUITA §6.2.2',
    'lexical_density':
        'Lu (2012); definition in the broad Hallidayan sense — all open-class words',
    'posddev':
        'Deutsch, Jasbi & Shieber (2020) Definition 3.3 (POSDdev); computed over '
        'ratios, 12 UD tags',
    'posdiv':
        'Deutsch, Jasbi & Shieber (2020) Definition 3.4 (POSdiv); natural logarithm (nats), the '
        'source uses bits',
    # ── syntactic_dep ───────────────────────────────────────
    'arc_len_mean':
        'Liu (2008) eq. (1); text level from Jing & Liu (2015) p.164, eq. (3) (MDD2)',
    'parse_depth_mean': 'Jing & Liu (2015) p.164, eq. (2) and (4) (MHD2)',
    'sentfinal_noun_ratio': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'sentfinal_propn_ratio': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'sentfinal_verb_ratio': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'sentfinal_adj_ratio': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'sentfinal_adv_ratio': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'sentfinal_det_ratio': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'sentfinal_adp_ratio': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'sentfinal_intj_ratio': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'sentfinal_cconj_ratio': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'sentfinal_sconj_ratio': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'sentfinal_num_ratio': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'sentfinal_aux_ratio': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'sentfinal_pron_ratio': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'sentfinal_other_ratio': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    # ── morphological ───────────────────────────────────────
    'surface_per_lemma':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'tense_past_ratio':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'tense_pres_ratio':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'tense_fut_ratio':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'aspect_perf_ratio':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'aspect_imp_ratio':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'aspect_prog_ratio':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'case_nom_ratio':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'case_acc_ratio':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'case_dat_ratio':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'case_loc_ratio':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'case_abl_ratio':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'case_gen_ratio':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'person_1_ratio':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'person_2_ratio':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'person_3_ratio':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'number_sing_ratio':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'number_plur_ratio':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'voice_pass_ratio':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    # ── morphological_zeyrek ────────────────────────────────
    'zeyrek_agglutination_depth':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'zeyrek_suffix_char_length_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'zeyrek_suffix_bigram_entropy':
        "Shannon (1948) — the entropy formula; Zeyrek (a Python port of Zemberek's "
        'morphotactics); tag set from Akın & Akın (2007)',
    'zeyrek_derivational_suffix_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'zeyrek_verb_suffix_diversity':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'zeyrek_tense_past_def_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'zeyrek_tense_past_nar_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'zeyrek_tense_present_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'zeyrek_tense_future_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'zeyrek_negation_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'zeyrek_passive_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'zeyrek_plural_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'zeyrek_case_acc_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'zeyrek_case_dat_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'zeyrek_case_loc_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'zeyrek_case_abl_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'zeyrek_case_gen_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'zeyrek_case_ins_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'zeyrek_conditional_suffix_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'zeyrek_causative_suffix_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'zeyrek_modal_possibility_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'zeyrek_modal_necessity_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'zeyrek_question_particle_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    # ── phonetic ────────────────────────────────────────────
    'front_vowel_ratio':
        'Göksel & Kerslake (2005) ch. 2 (the vowel system, front/back)',
    'back_vowel_ratio': 'Göksel & Kerslake (2005) ch. 2 (the vowel system, front/back)',
    'harmony_fronting_ratio':
        'Göksel & Kerslake (2005) §3.1 (fronting harmony); exceptions §3.4 — the '
        'measure counts them as disharmonic',
    'harmony_rounding_ratio':
        'Göksel & Kerslake (2005) §3.1 (rounding harmony); strictly a suffix '
        'phenomenon, measured here as a whole-word pattern',
    # Flesch (1948) p.223 defines "average word length in syllables" as an
    # element of its own; Ateşman (1997) p.73 adapts Flesch's formula. The
    # measure is not language-specific. The CV of syllables is not a named
    # measure (K10, 2026-10-01, Efe); syllable_cv was removed on 2026-10-07.
    'syllable_mean':
        'Flesch (1948) Formula A, wl; unit there = syllables per 100 words, here per word',
    'syllable_1_ratio': 'Bezirci & Yılmaz (2010) Table 1-c',
    'syllable_2_ratio': 'Bezirci & Yılmaz (2010) Table 1-c',
    'syllable_3_ratio': 'Bezirci & Yılmaz (2010) Table 1-c',
    'syllable_4_ratio': 'Bezirci & Yılmaz (2010) Table 1-c',
    'syllable_5_ratio': 'Bezirci & Yılmaz (2010) Table 1-c',
    'syllable_6plus_ratio': 'Bezirci & Yılmaz (2010) Table 1-c',
    # ── readability ─────────────────────────────────────────
    'bezirci_yilmaz': 'Bezirci & Yılmaz (2010) p.371, eq. (9)',
    'atesman': 'Ateşman (1997) p.74, eq. (2)',
    'cetinkaya_uzun': 'Çetinkaya (2010) p.85; counting rules p.93',
    'flesch_reading_ease':
        'Flesch (1948) Formula A; coefficient .846, unit = syllables per 100 words',
    'flesch_kincaid_grade': 'Kincaid et al. (1975) p.14, Table 3, "New"',
    'smog':
        'McLaughlin (1969) p.643, Table 1, eq. (d); p = polysyllabic words in a '
        '30-sentence sample',
    'polysyllabic_word_ratio':
        'McLaughlin (1969) p.641; polysyllabic = 3+ syllables — the ratio form of '
        "SMOG's input, not the source's own measure",
    'ari':
        'Smith & Senter (1967) p.8, AMRL-TR-66-220; reproduced verbatim in Kincaid et '
        'al. (1975) p.14, Table 3 ("Old")',
    'coleman_liau':
        'Coleman & Liau (1975) p.284; the formula is a composition of two equations, '
        'it does not appear in this form in the article',
    'lix':
        'Björnsson (1968), as cited in Anderson (1983) p.490; long word = 7+ letters',
    'long_word_ratio': 'Anderson (1983); long word = 7+ letters',
    # ── 2026-10-07 citation search (Efe): primary sources read in tlf-kaynaklar ──
    # Dynamic group: every char_* key takes this citation (registry._citation).
    'chars':
        'Zheng et al. (2006) Table 3, p.384, no. 7-32 "Frequency of letters (26 features)", A-Z; '
        "here each letter of the language's alphabet (Turkish 29, English 26) as a share of all "
        'its letters',
    'word_len_mean':
        'Mendenhall (1887) p.237 "mean word-length"; computed as letters per word, p.241',
    'sent_len_median': 'Yule (1939) p.369, median sentence length alongside the mean',
    # Chain traced: Deutsch et al. -> Vajjala Balakrishna (2015) software ("several other POS tag
    # density features", no source) -> nothing further (2026-10-07, Efe).
    'pronoun_ratio':
        'Deutsch, Jasbi & Shieber (2020) Table 6 "pronouns per word", listed among existing '
        'features; original source not traced',
    'hapax_ratio':
        'de Vel (2000) Table 2, attribute 14 "Ratio of words used once to total number of '
        'vocabulary words"',
    'whitespace_ratio':
        'de Vel et al. (2001) Table 2, p.60 "Total number of white-space characters/C"',
    'punct_char_ratio': 'de Vel et al. (2001) Table 2, p.60 "Total number of punctuations/C"',
    'digit_ratio':
        'de Vel et al. (2001) Table 2, p.60 "Total number of digit characters in words/C"; '
        'here digits anywhere in the text',
    'para_len_mean': 'Zheng et al. (2006) Table 3, p.384, no. 251 "Number of words per paragraph"',
    'sents_per_para_mean':
        'Zheng et al. (2006) Table 3, p.384, no. 249 "Number of sentences per paragraph"',
    'sent_len_char_mean':
        'Zheng et al. (2006) Table 3, p.384, no. 58 "Average sentence length in terms of character"',
    'punct_comma_ratio':
        'Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); '
        "here the share among all marks",
    'punct_period_ratio':
        'Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); '
        "here the share among all marks",
    'punct_semicolon_ratio':
        'Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); '
        "here the share among all marks",
    'punct_exclamation_ratio':
        'Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); '
        "here the share among all marks",
    'punct_colon_ratio':
        'Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); '
        "here the share among all marks",
    'punct_question_ratio':
        'Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); '
        "here the share among all marks",
    'punct_quote_ratio':
        'Zheng et al. (2006) Table 3, p.384, no. 88-95 (frequencies of eight marks, this one among them); '
        "here the share among all marks",
}


# ── kaynakça ─────────────────────────────────────────────────────────
# Künye dizeleri kısa işaretçidir; tam bibliyografik kayıt burada durur.
# Her künye en az bir anahtarı birebir içerir ve her kayıt en az bir
# künyede geçer — ikisini de ``test_registry.py`` sınıyor. Uydurma bir
# kaynak adı o testten geçemez (2026-09-19, Efe).
BIBLIOGRAPHY: dict[str, str] = {
    'Akın & Akın (2007)':
        'Akın, A. A., & Akın, M. D. (2007). Zemberek, an open source NLP framework for '
        'Turkic Languages. 8 pp. Source code: github.com/ahmetaa/zemberek-nlp. (The '
        'document does not state a place of publication.)',
    'Anderson (1983)':
        'Anderson, J. (1983). Lix and Rix: Variations on a little-known readability '
        'index. Journal of Reading, 26(6), 490–496. JSTOR 40031755.',
    "This library's threshold calibration":
        "This library's own measurement, not a published source. short_sent_threshold "
        'and long_sent_threshold were derived from the 15th and 85th percentiles of '
        'the sentence-length distribution of newspaper columns under the default sentence '
        'and word rules: TR 162 columnists / 4,321 articles / 197,990 sentences, EN 30 columnists / '
        '1,485 articles / 52,745 sentences. Method and raw percentile '
        'table: docs/threshold-calibration.md.',
    'Ateşman (1997)':
        'Ateşman, E. (1997). Türkçede okunabilirliğin ölçülmesi. Dil Dergisi, 58, '
        '71–74. Ankara Üniversitesi TÖMER. ISSN 1300-3542.',
    'Bestgen (2023)':
        'Bestgen, Y. (2023). Measuring lexical diversity in texts: The twofold length '
        'problem. arXiv:2307.04626. Published version: Language Learning, 74(3), '
        '638–671 (2024), DOI 10.1111/lang.12630 — the preprint was used here.',
    'Bezirci & Yılmaz (2010)':
        'Bezirci, B., & Yılmaz, A. E. (2010). Türkçe için yeni bir okunabilirlik '
        'ölçütü önerisi. SIU2010 — IEEE 18. Sinyal İşleme ve İletişim Uygulamaları '
        'Kurultayı, Diyarbakır, 368–371.',
    'Björnsson (1968)':
        'Björnsson, C. H. (1968). Läsbarhet. Stockholm: Bokförlaget Liber. (Book.) The '
        'record was verified from three secondary reference lists: Anderson (1983), '
        'Çetinkaya (2010), Falkenjack et al. (2013). The primary source could not be '
        'obtained.',
    'Brunet (1978)':
        'Brunet, E. (1978). Vocabulaire de Jean Giraudoux: structure et évolution. '
        'Genève: Slatkine. (Book.) The record was verified from the reference list of '
        'Popescu, Čech & Altmann (2011). The primary source could not be obtained.',
    'Carroll (1964)':
        'Carroll, J. B. (1964). Language and Thought. Englewood Cliffs, NJ: Prentice-Hall. '
        'The record was verified from the reference list of Torruella & Capsada (2013). The '
        'primary source could not be obtained.',
    'Coleman & Liau (1975)':
        'Coleman, M., & Liau, T. L. (1975). A computer readability formula designed '
        'for machine scoring. Journal of Applied Psychology, 60(2), 283–284. '
        'DOI 10.1037/h0076540',
    'Covington & McFall (2010)':
        'Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot: The '
        'moving-average type–token ratio (MATTR). Journal of Quantitative '
        'Linguistics, 17(2), 94–100. DOI 10.1080/09296171003643098',
    'Daller (2010)':
        "Daller, M. (2010). Guiraud's Index. BAAL 2010, Aberdeen. (Presentation.)",
    'de Marneffe et al. (2021)':
        'de Marneffe, M.-C., Manning, C. D., Nivre, J., & Zeman, D. (2021). '
        'Universal Dependencies. Computational Linguistics, 47(2), 255–308. DOI '
        '10.1162/COLI_a_00402',
    'de Vel (2000)':
        'de Vel, O. (2000). Mining e-mail authorship. In KDD-2000 Workshop on Text Mining, '
        'Boston, August 20, 2000.',
    'de Vel et al. (2001)':
        'de Vel, O., Anderson, A., Corney, M., & Mohay, G. (2001). Mining e-mail content for '
        'author identification forensics. ACM SIGMOD Record, 30(4), 55–64. DOI 10.1145/604264.604272',
    'Deutsch, Jasbi & Shieber (2020)':
        'Deutsch, T., Jasbi, M., & Shieber, S. (2020). Linguistic features for '
        'readability assessment. Proceedings of the 15th Workshop on Innovative Use '
        'of NLP for Building Educational Applications (BEA), 1–17. '
        'DOI 10.18653/v1/2020.bea-1.1',
    'Dugast (1978)':
        "Dugast, D. (1978). Sur quoi se fonde la notion d'étendue théoretique du "
        'vocabulaire? Le Français Moderne, 46(1), 25–32. The record was verified from '
        'four secondary reference lists: Malvern et al. (2004), McCarthy & Jarvis '
        '(2010), Šišková (2012) and an authorship-attribution review. The primary '
        'source could not be obtained. The literature often cites Dugast (1978, 1979) '
        'together; 1979 is a separate work (Vocabulaire et stylistique I, Travaux de '
        'linguistique quantitative 8, Genève: Slatkine-Champion) and is not used here.',
    'Flesch (1948)':
        'Flesch, R. (1948). A new readability yardstick. Journal of Applied '
        'Psychology, 32(3), 221–233. DOI 10.1037/h0057532',
    'Guiraud (1954)':
        'Guiraud, P. (1954). Les Caractères Statistiques du Vocabulaire. Essai de '
        'méthodologie. Paris: Presses Universitaires de France.',
    'Göksel & Kerslake (2005)':
        'Göksel, A., & Kerslake, C. (2005). Turkish: A Comprehensive Grammar. '
        'London & New York: Routledge. 535 pp. ISBN 0-415-11494-2 (pbk), 0-415-21761-X (hbk).',
    'Heaps (1978)':
        'Heaps, H. S. (1978). Information Retrieval: Computational and Theoretical '
        'Aspects. New York: Academic Press.',
    'Herdan (1955)':
        "Herdan, G. (1955). A new derivation and interpretation of Yule's characteristic K. "
        'Zeitschrift für Angewandte Mathematik und Physik, 6. The record was verified from the '
        'reference list of Tweedie & Baayen (1998). The primary source could not be obtained.',
    'Herdan (1960/1964)':
        'Herdan, G. (1960). Type-Token Mathematics. The Hague: Mouton. / Herdan, G. '
        '(1964). Quantitative Linguistics. London: Butterworths.',
    'Jing & Liu (2015)':
        'Jing, Y., & Liu, H. (2015). Mean hierarchical distance: Augmenting mean '
        'dependency distance. Proceedings of Depling 2015, Uppsala, 161–170.',
    'Johnson (1944)':
        'Johnson, W. (1944). Studies in language behavior: I. A program of '
        'research. Psychological Monographs, 56(2), 1–15. DOI 10.1037/h0093508',
    'Kincaid et al. (1975)':
        'Kincaid, J. P., Fishburne, R. P., Rogers, R. L., & Chissom, B. S. (1975). '
        'Derivation of new readability formulas for Navy enlisted personnel. '
        'Research Branch Report 8-75. Millington, TN: Naval Air Station Memphis. '
        'DOI 10.21236/ADA006655',
    'Liu (2008)':
        'Liu, H. (2008). Dependency distance as a metric of language comprehension '
        'difficulty. Journal of Cognitive Science, 9(2), 159–191. '
        'DOI 10.17791/jcs.2008.9.2.159',
    'Lu (2012)':
        'Lu, X. (2012). The relationship of lexical richness to the quality of ESL '
        "learners' oral narratives. The Modern Language Journal, 96(2), 190–208. "
        'DOI 10.1111/j.1540-4781.2011.01232.x',
    'Maas (1972)':
        'Maas, H.-D. (1972). Zusammenhang zwischen Wortschatzumfang und Länge eines Textes. '
        'Zeitschrift für Literaturwissenschaft und Linguistik, 8, 73–79. The record was '
        'verified from the reference list of Tweedie & Baayen (1998). The primary source '
        'could not be obtained.',
    'Malvern et al. (2004)':
        'Malvern, D., Richards, B., Chipere, N., & Durán, P. (2004). Lexical '
        'Diversity and Language Development: Quantification and Assessment. '
        'Basingstoke: Palgrave Macmillan. ISBN 978-1-4039-0232-0. DOI 10.1057/9780230511804.',
    'Manning et al. (2008)':
        'Manning, C. D., Raghavan, P., & Schütze, H. (2008). Introduction to '
        'Information Retrieval. Cambridge University Press. (The file in the archive '
        'is the 2009 online edition.) DOI 10.1017/CBO9780511809071',
    'McCarthy & Jarvis (2007)':
        'McCarthy, P. M., & Jarvis, S. (2007). vocd: A theoretical and empirical '
        'evaluation. Language Testing, 24(4), 459–488. DOI 10.1177/0265532207080767',
    'McCarthy (2005)':
        'McCarthy, P. M. (2005). An Assessment of the Range and Usefulness of Lexical '
        'Diversity Measures and the Potential of the Measure of Textual, Lexical '
        'Diversity (MTLD). Doctoral dissertation, The University of Memphis, August '
        '2005. Advisor: Charles E. Hall. (Only a preview is available: 24 pages of '
        'front matter + abstract, no body.)',
    'McCarthy & Jarvis (2010)':
        'McCarthy, P. M., & Jarvis, S. (2010). MTLD, vocd-D, and HD-D: A validation '
        'study of sophisticated approaches to lexical diversity assessment. '
        'Behavior Research Methods, 42(2), 381–392. DOI 10.3758/BRM.42.2.381',
    'McLaughlin (1969)':
        'McLaughlin, G. H. (1969). SMOG grading — a new readability formula. '
        'Journal of Reading, 12(8), 639–646.',
    'Mendenhall (1887)':
        'Mendenhall, T. C. (1887). The characteristic curves of composition. Science, 9(214), '
        '237–249. JSTOR 1764604.',
    'Piantadosi (2014)':
        "Piantadosi, S. T. (2014). Zipf's word frequency law in natural language: A "
        'critical review and future directions. Psychonomic Bulletin & Review, '
        '21(5), 1112–1130. DOI 10.3758/s13423-014-0585-6',
    'Popescu & Altmann (2006)':
        'Popescu, I.-I., & Altmann, G. (2006). Some aspects of word frequencies. '
        'Glottometrics, 13, 23–46. RAM-Verlag; journal ISSN 2625-8226.',
    'Popescu et al. (2009)':
        'Popescu, I.-I., Altmann, G., Grzybek, P., et al. (2009). Word Frequency '
        'Studies. Berlin: Mouton de Gruyter. (Quantitative Linguistics 64.) '
        'ISBN 978-3-11-021852-7, ISSN 0179-3616. DOI 10.1515/9783110218534',
    'Popescu, Mačutek & Altmann (2009)':
        'Popescu, I.-I., Mačutek, J., & Altmann, G. (2009). Aspects of Word '
        'Frequencies. Lüdenscheid: RAM-Verlag.',
    'Popescu, Čech & Altmann (2011)':
        'Popescu, I.-I., Čech, R., & Altmann, G. (2011). The Lambda-structure of '
        'Texts. Lüdenscheid: RAM-Verlag. ISBN 978-3-942303-05-7.',
    'QUITA':
        'Kubát, M., Matlach, V., & Čech, R. (2014). QUITA — Quantitative Index Text '
        'Analyzer. Lüdenscheid: RAM-Verlag. ISBN 978-3-942303-28-6.',
    'Shannon (1948)':
        'Shannon, C. E. (1948). A mathematical theory of communication. Bell System '
        'Technical Journal, 27(3), 379–423; 27(4), 623–656. '
        'DOI 10.1002/j.1538-7305.1948.tb01338.x',
    'Sichel (1975)':
        'Sichel, H. S. (1975). On a distribution law for word frequencies. Journal '
        'of the American Statistical Association, 70(351a), 542–547. DOI '
        '10.1080/01621459.1975.10482469',
    'Simpson (1949)':
        'Simpson, E. H. (1949). Measurement of diversity. Nature, 163(4148), 688. '
        'DOI 10.1038/163688a0',
    'Smith & Senter (1967)':
        'Smith, E. A., & Senter, R. J. (1967). Automated readability index. '
        'AMRL-TR-66-220. Wright-Patterson AFB, OH: Aerospace Medical Research '
        'Laboratories. 22 pp.',
    'Somers (1966)':
        'Somers, H. H. (1966). Statistical methods in literary analysis. In J. Leeds (Ed.), The '
        'Computer and Literary Style (pp. 128–140). Kent, OH: Kent State University Press. The '
        'record was verified from the reference list of Torruella & Capsada (2013). The '
        'primary source could not be obtained.',
    'Torruella & Capsada (2013)':
        'Torruella, J., & Capsada, R. (2013). Lexical statistics and tipological structures: '
        'A measure of lexical richness. Procedia - Social and Behavioral Sciences, 95, '
        '447–454. DOI 10.1016/j.sbspro.2013.10.668',
    'Tweedie & Baayen (1998)':
        'Tweedie, F. J., & Baayen, R. H. (1998). How variable may a constant be? '
        'Measures of lexical richness in perspective. Computers and the Humanities, '
        '32(5), 323–352. DOI 10.1023/A:1001749303137',
    'van Heuven et al. (2014)':
        'van Heuven, W. J. B., Mandera, P., Keuleers, E., & Brysbaert, M. (2014). '
        'SUBTLEX-UK: A new and improved word frequency database for British '
        'English. Quarterly Journal of Experimental Psychology, 67(6), 1176–1190. '
        'DOI 10.1080/17470218.2013.850521',
    'Yule (1939)':
        'Yule, G. U. (1939). On sentence-length as a statistical characteristic of style in prose: '
        'With application to two cases of disputed authorship. Biometrika, 30(3/4), 363–390. '
        'JSTOR 2332655.',
    'Yule (1944)':
        'Yule, G. U. (1944). The Statistical Study of Literary Vocabulary. '
        'Cambridge University Press.',
    'Zeyrek':
        'Zeyrek — a Python port of the Zemberek morphological analyser. '
        'github.com/obulat/zeyrek',
    'Zheng et al. (2006)':
        'Zheng, R., Li, J., Chen, H., & Huang, Z. (2006). A framework for authorship identification '
        'of online messages: Writing-style features and classification techniques. Journal of the '
        'American Society for Information Science and Technology, 57(3), 378–393. '
        'DOI 10.1002/asi.20316',
    'Çetinkaya (2010)':
        'Çetinkaya, G. (2010). Türkçe metinlerin okunabilirlik düzeylerinin '
        'tanımlanması ve sınıflandırılması [Unpublished doctoral dissertation]. Ankara '
        'Üniversitesi, Sosyal Bilimler Enstitüsü. Advisor: Leylâ Uzun. 252 pp. '
        'hdl:20.500.12812/519962',
}

