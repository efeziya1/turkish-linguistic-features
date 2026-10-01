"""Registry metin tabloları — 183 statik anahtarın açıklaması, formülü,
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
    'n_lemma_count': 'number of distinct lemmas',
    'avg_word_length': 'mean word length in characters',
    'word_length_cv': 'spread of word length',
    'ttr': 'type-token ratio; falls as the text grows',
    'mattr': 'moving-average TTR',
    'entropy_std': 'how much word entropy varies across the text',
    'herdan_c': "Herdan's C (LogTTR)",
    'sichel_s': 'share of types occurring exactly twice',
    'zipf_exponent': 'Zipf slope',
    'zipf_r2': 'fit quality of the Zipf line',
    'zipf_mandelbrot_q': 'Zipf-Mandelbrot shift',
    'zipf_mandelbrot_s': 'Zipf-Mandelbrot slope',
    'mtld': 'measure of textual lexical diversity',
    'dugast_u': "Dugast's Uber index",
    'guiraud_r': "Guiraud's root TTR",
    'ttr_moving_slope': 'whether vocabulary thins out towards the end',
    'heaps_beta': 'vocabulary growth rate',
    'entropy': 'Shannon entropy of word frequencies',
    'yule_k': "Yule's K; higher = more repetitive",
    'simpson_d': 'chance that two words drawn without replacement are the same type',
    'brunet_w': "Brunet's W",
    'hapax_ratio': 'share of types occurring once',
    'hapax_percentage': 'share of tokens that occur once',
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
    'secondary_thematic_concentration': 'same, up to rank 2h',
    # ── sentence ────────────────────────────────────────────────
    'avg_sent_len_word': 'mean sentence length in words',
    'avg_sent_len_char': 'mean sentence length in characters',
    'sentence_length_cv': 'spread of sentence length',
    'sent_len_skewness': 'skew of sentence length; positive = long-sentence tail',
    'short_sent_ratio': 'share of short sentences',
    'long_sent_ratio': 'share of long sentences',
    'med_sent_len': 'median sentence length',
    'sent_len_entropy': 'variety of sentence lengths',
    # ── paragraph ───────────────────────────────────────────────
    'para_len_mean': 'mean paragraph length',
    'para_len_cv': 'spread of paragraph length',
    'sents_per_para_mean': 'mean sentences per paragraph',
    'sents_per_para_cv': 'spread of sentences per paragraph',
    'para_count_norm': 'paragraphs per 1000 words',
    # ── pos ─────────────────────────────────────────────────────
    'pos_noun': 'share of NOUN tokens',
    'pos_propn': 'share of PROPN tokens',
    'pos_verb': 'share of VERB tokens',
    'pos_adj': 'share of ADJ tokens',
    'pos_adv': 'share of ADV tokens',
    'pos_det': 'share of DET tokens',
    'pos_adp': 'share of ADP tokens',
    'pos_aux': 'share of AUX tokens',
    'pos_cconj': 'share of CCONJ tokens',
    'pos_sconj': 'share of SCONJ tokens',
    'pos_num': 'share of NUM tokens',
    'pos_intj': 'share of INTJ tokens',
    'pos_punct': 'share of PUNCT tokens',
    # ── syntactic ───────────────────────────────────────────────
    'question_per_sent': 'share of sentences ending in "?"',
    'pronoun_freq': 'share of pronoun tokens',
    'nominal_verbal_ratio': 'noun-to-verb balance',
    'verb_dist_mean': 'mean token gap between consecutive verbs',
    'verb_dist_cv': 'spread of verb gaps',
    'activity_ratio': 'activity Q',
    'lexical_density': 'share of lexical words',
    'pos_dist_std': 'how uneven the POS distribution is',
    'pos_kl_div': 'how much sentences differ from the document in POS make-up',
    # ── syntactic_dep ───────────────────────────────────────────
    'arc_len_mean': 'mean dependency distance (MDD2)',
    'parse_depth_mean': 'mean hierarchical distance (MHD2)',
    'sentfinal_noun': 'share of sentences ending in a NOUN',
    'sentfinal_propn': 'share of sentences ending in a PROPN',
    'sentfinal_verb': 'share of sentences ending in a VERB',
    'sentfinal_adj': 'share of sentences ending in a ADJ',
    'sentfinal_adv': 'share of sentences ending in a ADV',
    'sentfinal_det': 'share of sentences ending in a DET',
    'sentfinal_adp': 'share of sentences ending in a ADP',
    'sentfinal_intj': 'share of sentences ending in a INTJ',
    'sentfinal_cconj': 'share of sentences ending in a CCONJ',
    'sentfinal_sconj': 'share of sentences ending in a SCONJ',
    'sentfinal_num': 'share of sentences ending in a NUM',
    'sentfinal_aux': 'share of sentences ending in a AUX',
    'sentfinal_pron': 'share of sentences ending in a PRON',
    'sentfinal_other': 'share of sentences ending in any other tag',
    # ── morphological ───────────────────────────────────────────
    'surface_per_lemma': 'distinct forms per lemma',
    'morph_tense_past': 'share of tokens tagged Tense=Past',
    'morph_tense_pres': 'share of tokens tagged Tense=Pres',
    'morph_tense_fut': 'share of tokens tagged Tense=Fut',
    'morph_aspect_perf': 'share of tokens tagged Aspect=Perf',
    'morph_aspect_imp': 'share of tokens tagged Aspect=Imp',
    'morph_aspect_prog': 'share of tokens tagged Aspect=Prog',
    'morph_case_nom': 'share of tokens tagged Case=Nom',
    'morph_case_acc': 'share of tokens tagged Case=Acc',
    'morph_case_dat': 'share of tokens tagged Case=Dat',
    'morph_case_loc': 'share of tokens tagged Case=Loc',
    'morph_case_abl': 'share of tokens tagged Case=Abl',
    'morph_case_gen': 'share of tokens tagged Case=Gen',
    'morph_person_1': 'share of tokens tagged Person=1',
    'morph_person_2': 'share of tokens tagged Person=2',
    'morph_person_3': 'share of tokens tagged Person=3',
    'morph_number_sing': 'share of tokens tagged Number=Sing',
    'morph_number_plur': 'share of tokens tagged Number=Plur',
    'morph_voice_pass': 'share of passive verbs',
    # ── morphological_zeyrek ────────────────────────────────────
    'agglutination_depth': 'visible suffixes per word',
    'suffix_char_length_ratio': 'share of word letters in suffixes',
    'suffix_bigram_entropy': 'variety of suffix sequences',
    'derivational_suffix_ratio': 'share of derivational suffixes',
    'verb_suffix_diversity': 'suffix variety on verbs',
    'tense_past_def': 'share of verbs in the definite past (-DI)',
    'tense_past_nar': 'share of verbs in the reported past (-mIş)',
    'tense_present': 'share of verbs in the present',
    'tense_future': 'share of verbs in the future (-AcAk)',
    'negation_ratio': 'share of negative verbs',
    'passive_ratio': 'share of passive verbs',
    'plural_ratio': 'share of plural nominals',
    'case_acc_ratio': 'share of words in the accusative case',
    'case_dat_ratio': 'share of words in the dative case',
    'case_loc_ratio': 'share of words in the locative case',
    'case_abl_ratio': 'share of words in the ablative case',
    'case_gen_ratio': 'share of words in the genitive case',
    'case_ins_ratio': 'share of words in the instrumental case',
    'conditional_suffix_ratio': 'share of conditional verbs',
    'causative_suffix_ratio': 'share of causative verbs',
    'suffix_chain_cv': 'spread of suffix-chain length',
    'modal_possibility_ratio': 'share of ability verbs',
    'modal_necessity_ratio': 'share of necessity verbs',
    'question_particle_ratio': 'share of question particles',
    # ── phonetic ────────────────────────────────────────────────
    'vowel_ratio': 'share of vowels',
    'front_vowel_ratio': 'share of front vowels',
    'back_vowel_ratio': 'share of back vowels',
    'harmony_fronting_ratio': 'share of words obeying front/back vowel harmony (TR only)',
    'harmony_rounding_ratio': 'share of words obeying rounding vowel harmony (TR only)',
    'syllable_mean': 'mean syllables per word',
    'syllable_cv': 'spread of syllables per word',
    'syllable_1_ratio': 'share of words with 1 syllable',
    'syllable_2_ratio': 'share of words with 2 syllables',
    'syllable_3_ratio': 'share of words with 3 syllables',
    'syllable_4_ratio': 'share of words with 4 syllables',
    'syllable_5_ratio': 'share of words with 5 syllables',
    'syllable_6plus_ratio': 'share of words with 6 or more syllables',
    'sentence_syllable_mean': 'syllables per sentence',
    'sentence_syllable_cv': 'spread of syllables per sentence',
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
    'digit_vs_all': 'share of digit characters',
    'punc_,_ratio': 'comma marks per word',
    'punc_._ratio': 'full stop marks per word',
    'punc_;_ratio': 'semicolon marks per word',
    'punc_!_ratio': 'exclamation mark marks per word',
    'punc_:_ratio': 'colon marks per word',
    'punc_-_ratio': 'hyphen or dash marks per word',
    'punc_ellipsis_ratio': 'ellipsis marks per word',
    'punc_paren_ratio': 'parenthesis marks per word',
    'punc_quote_ratio': 'quotation mark marks per word',
    'punc_question_ratio': 'question mark marks per word',
    'punct_density': 'punctuation marks per character',
    'punct_entropy': 'variety of punctuation types',
    'consecutive_punct_ratio': 'share of marks directly next to another mark',
    'whitespace_ratio': 'share of whitespace characters',
    'punct_variety': 'number of punctuation types used (0–10)',
    'uppercase_ratio': 'share of capitalised tokens',
    'all_caps_word_ratio': 'share of all-caps tokens',
    # ── chars (dinamik grup) ───────────────────────────────────────
    'chars': 'share of that letter among alphabet letters',
    # ── custom_ngrams (dinamik grup) ───────────────────────────────
    'custom_ngrams': 'rate of a user-supplied word sequence',
}

# Anahtar → NASIL hesaplandığı. Anahtarın kendi satırı yoksa describe_feature
# grup adındaki satıra düşer; bu yalnız dinamik gruplarda (chars, custom_ngrams)
# var, 183 statik anahtarın hepsinin kendi satırı var.
FEATURE_FORMULAS: dict[str, str] = {
    # ── lexical ─────────────────────────────────────────────────
    'n_lemma_count': 'V over lemmas',
    'avg_word_length': 'sum(len(w)) / N',
    'word_length_cv': 'std(len(w)) / mean(len(w)), population std',
    'ttr': 'V / N',
    'mattr': 'mean TTR of every sliding window of mattr_window words',
    'entropy_std': 'population std of entropies (bits) of disjoint mattr_window-word chunks',
    'herdan_c': 'log(V) / log(N)',
    'sichel_s': 'V2 / V',
    'zipf_exponent': 'abs(slope) of least-squares fit log f(r) ~ log r',
    'zipf_r2': 'R² of that fit',
    'zipf_mandelbrot_q': 'q minimising the residual of log f ~ log(r + q), grid 0–10 step 0.1',
    'zipf_mandelbrot_s': 'abs(slope) at that q',
    'mtld': 'mean words per factor (TTR drops to mtld_threshold), forward and backward averaged',
    'dugast_u': 'log10(N)^2 / (log10(N) - log10(V))',
    'guiraud_r': 'V / sqrt(N)',
    'ttr_moving_slope': 'linear slope of TTR over disjoint ttr_slope_chunk_size-word chunks',
    'heaps_beta':
        'least-squares slope of log V ~ log N over prefixes every heaps_step words, not'
        'clipped',
    'entropy': '-sum(p * log2 p)',
    'yule_k': '10000 * (sum(f^2) - N) / N^2',
    'simpson_d': 'sum(f(f-1)) / (N(N-1))',
    'brunet_w': 'N^(V^-a), a = brunet_w_a',
    'hapax_ratio': 'V1 / V',
    'hapax_percentage': 'V1 / N',
    'vocd_d':
        'D fitted to mean TTR of random samples of vocd_sample_min–vocd_sample_max words,'
        'vocd_num_runs runs averaged',
    'hdd': 'expected TTR of a hdd_sample_size-word sample (hypergeometric)',
    'msttr': 'mean TTR of full msttr_segment_size-word segments',
    'noun_variation': 'distinct noun lemmas / lexical-word tokens',
    'verb_variation': 'distinct verb lemmas / verb tokens',
    'adj_variation': 'distinct adjective lemmas / lexical-word tokens',
    'adv_variation': 'distinct adverb lemmas / lexical-word tokens',
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
    'lambda_pa': 'L * log10(N) / N',
    'adjusted_modulus': 'sqrt((f1/h)^2 + (V/h)^2) / log10(N)',
    'writers_view_alpha': 'arccos of the angle between (1, f1) and (V, 1) seen from (h, h)',
    'thematic_concentration': "sum(2(h - r') f(r')) / (h(h-1) f1), content words with r' < h",
    'secondary_thematic_concentration': "sum((2h - r') f(r')) / (h(2h-1) f1), r' <= 2h",
    # ── sentence ────────────────────────────────────────────────
    'avg_sent_len_word': 'mean words per sentence',
    'avg_sent_len_char': 'mean len(tokens joined by single spaces)',
    'sentence_length_cv': 'population std / mean of words per sentence',
    'sent_len_skewness': 'Fisher-Pearson g1 = m3 / m2^1.5 over words per sentence',
    'short_sent_ratio': 'sentences with fewer than short_sent_threshold words / sentences',
    'long_sent_ratio': 'sentences with more than long_sent_threshold words / sentences',
    'med_sent_len': 'median words per sentence',
    'sent_len_entropy': 'Shannon entropy (bits) of the distribution of words per sentence',
    # ── paragraph ───────────────────────────────────────────────
    'para_len_mean': 'mean whitespace-separated words per paragraph (blank line = boundary)',
    'para_len_cv': 'population std / mean',
    'sents_per_para_mean': 'mean count of [.!?…]+ per paragraph (at least 1)',
    'sents_per_para_cv': 'population std / mean',
    'para_count_norm': 'paragraphs / words * 1000',
    # ── pos ─────────────────────────────────────────────────────
    'pos_noun': 'tag count / all tokens (punctuation included)',
    'pos_propn': 'tag count / all tokens (punctuation included)',
    'pos_verb': 'tag count / all tokens (punctuation included)',
    'pos_adj': 'tag count / all tokens (punctuation included)',
    'pos_adv': 'tag count / all tokens (punctuation included)',
    'pos_det': 'tag count / all tokens (punctuation included)',
    'pos_adp': 'tag count / all tokens (punctuation included)',
    'pos_aux': 'tag count / all tokens (punctuation included)',
    'pos_cconj': 'tag count / all tokens (punctuation included)',
    'pos_sconj': 'tag count / all tokens (punctuation included)',
    'pos_num': 'tag count / all tokens (punctuation included)',
    'pos_intj': 'tag count / all tokens (punctuation included)',
    'pos_punct': 'tag count / all tokens (punctuation included)',
    # ── syntactic ───────────────────────────────────────────────
    'question_per_sent': 'sentences whose final mark contains "?" / sentences',
    'pronoun_freq': 'PRON / all tokens',
    'nominal_verbal_ratio': '(NOUN + PROPN) / VERB',
    'verb_dist_mean': 'mean difference of VERB positions',
    'verb_dist_cv': 'population std / mean of those gaps',
    'activity_ratio': 'VERB / (VERB + ADJ)',
    'lexical_density': '(NOUN + PROPN + VERB + ADJ + ADV) / all words, PUNCT and SYM excluded',
    'pos_dist_std': 'population std of the 13 pos_* shares',
    'pos_kl_div': 'mean over sentences of KL(sentence POS ‖ document POS), bits',
    # ── syntactic_dep ───────────────────────────────────────────
    'arc_len_mean':
        'mean over sentences of mean abs(word position - head position), punctuation removed,'
        'root excluded',
    'parse_depth_mean': 'mean over sentences of mean steps to the root, capped at max_parse_depth',
    'sentfinal_noun': 'sentences ending in that tag / sentences',
    'sentfinal_propn': 'sentences ending in that tag / sentences',
    'sentfinal_verb': 'sentences ending in that tag / sentences',
    'sentfinal_adj': 'sentences ending in that tag / sentences',
    'sentfinal_adv': 'sentences ending in that tag / sentences',
    'sentfinal_det': 'sentences ending in that tag / sentences',
    'sentfinal_adp': 'sentences ending in that tag / sentences',
    'sentfinal_intj': 'sentences ending in that tag / sentences',
    'sentfinal_cconj': 'sentences ending in that tag / sentences',
    'sentfinal_sconj': 'sentences ending in that tag / sentences',
    'sentfinal_num': 'sentences ending in that tag / sentences',
    'sentfinal_aux': 'sentences ending in that tag / sentences',
    'sentfinal_pron': 'sentences ending in that tag / sentences',
    'sentfinal_other': 'same, tags outside the 13',
    # ── morphological ───────────────────────────────────────────
    'surface_per_lemma': 'distinct (lemma, form) pairs / distinct lemmas, lowercased',
    'morph_tense_past': 'tokens with Tense=X / tokens with any Tense',
    'morph_tense_pres': 'tokens with Tense=X / tokens with any Tense',
    'morph_tense_fut': 'tokens with Tense=X / tokens with any Tense',
    'morph_aspect_perf': 'same with Aspect',
    'morph_aspect_imp': 'same with Aspect',
    'morph_aspect_prog': 'same with Aspect',
    'morph_case_nom': 'same with Case',
    'morph_case_acc': 'same with Case',
    'morph_case_dat': 'same with Case',
    'morph_case_loc': 'same with Case',
    'morph_case_abl': 'same with Case',
    'morph_case_gen': 'same with Case',
    'morph_person_1': 'same with Person',
    'morph_person_2': 'same with Person',
    'morph_person_3': 'same with Person',
    'morph_number_sing': 'same with Number',
    'morph_number_plur': 'same with Number',
    'morph_voice_pass': 'VERB with Voice=Pass / VERB',
    # ── morphological_zeyrek ────────────────────────────────────
    'agglutination_depth': 'visible suffixes / analysed words',
    'suffix_char_length_ratio': 'suffix letters / word letters',
    'suffix_bigram_entropy': 'Shannon entropy (bits) of within-word visible suffix pairs',
    'derivational_suffix_ratio': 'derivational / visible suffixes',
    'verb_suffix_diversity': 'mean distinct visible suffix tags per verb_suffix_window-verb chunk',
    'tense_past_def': 'verbs whose last tense tag is X / verbs',
    'tense_past_nar': 'verbs whose last tense tag is X / verbs',
    'tense_present': 'verbs whose last tense tag is X / verbs',
    'tense_future': 'verbs whose last tense tag is X / verbs',
    'negation_ratio': 'verbs with Neg or Unable / verbs',
    'passive_ratio': 'verbs with Pass / verbs',
    'plural_ratio': 'words with A3pl on a non-verb part / analysed words',
    'case_acc_ratio': 'words with Acc … Ins / analysed words',
    'case_dat_ratio': 'words with Acc … Ins / analysed words',
    'case_loc_ratio': 'words with Acc … Ins / analysed words',
    'case_abl_ratio': 'words with Acc … Ins / analysed words',
    'case_gen_ratio': 'words with Acc … Ins / analysed words',
    'case_ins_ratio': 'words with Acc … Ins / analysed words',
    'conditional_suffix_ratio': 'verbs with Cond / verbs',
    'causative_suffix_ratio': 'verbs with Caus / verbs',
    'suffix_chain_cv': 'population std / mean of visible suffixes per word',
    'modal_possibility_ratio': 'verbs with Able or Unable / verbs',
    'modal_necessity_ratio': 'verbs with Neces / verbs',
    'question_particle_ratio': 'words with root Ques / analysed words',
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
    'syllable_cv': 'population std / mean of syllables per syllabifiable word',
    'syllable_1_ratio': 'words with 1 syllable / syllabifiable words',
    'syllable_2_ratio': 'words with 2 syllables / syllabifiable words',
    'syllable_3_ratio': 'words with 3 syllables / syllabifiable words',
    'syllable_4_ratio': 'words with 4 syllables / syllabifiable words',
    'syllable_5_ratio': 'words with 5 syllables / syllabifiable words',
    'syllable_6plus_ratio': 'words with 6 or more syllables / syllabifiable words',
    'sentence_syllable_mean': 'mean syllables per sentence',
    'sentence_syllable_cv': 'population std / mean',
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
    'digit_vs_all': 'digits / characters',
    'punc_,_ratio': 'marks / words',
    'punc_._ratio': 'marks / words',
    'punc_;_ratio': 'marks / words',
    'punc_!_ratio': 'marks / words',
    'punc_:_ratio': 'marks / words',
    'punc_-_ratio': 'marks / words',
    'punc_ellipsis_ratio': 'marks / words',
    'punc_paren_ratio': 'marks / words',
    'punc_quote_ratio': 'marks / words',
    'punc_question_ratio': 'marks / words',
    'punct_density': 'marks / characters',
    'punct_entropy': 'Shannon entropy (bits) of the 10 mark types',
    'consecutive_punct_ratio': 'adjacent marks / marks',
    'whitespace_ratio': 'whitespace / characters',
    'punct_variety': 'distinct mark types',
    'uppercase_ratio': 'tokens whose first letter is upper case / tokens with a letter',
    'all_caps_word_ratio': 'tokens with 2+ letters, all upper case / tokens with a letter',
    # ── chars (dinamik grup) ───────────────────────────────────────
    'chars': 'letter count / alphabet letters',
    # ── custom_ngrams (dinamik grup) ───────────────────────────────
    'custom_ngrams': 'matches / (words - n + 1), overlapping matches counted',
}

# Anahtar → ölçüm şartı. Sağlanmazsa değer NaN (K4).
FEATURE_REQUIRES: dict[str, str] = {
    # ── lexical ─────────────────────────────────────────────────
    'n_lemma_count': 'at least 1 word',
    'avg_word_length': 'at least 1 word',
    'word_length_cv': 'at least 2 words',
    'ttr': 'at least 1 word',
    'mattr': 'at least 100 words (2 x mattr_window)',
    'entropy_std': 'at least 100 words (2 x mattr_window)',
    'herdan_c': 'at least 2 words',
    'sichel_s': 'at least 1 word',
    'zipf_exponent': 'at least 10 distinct words',
    'zipf_r2': 'at least 10 distinct words, not all equally frequent',
    'zipf_mandelbrot_q': 'at least 10 distinct words',
    'zipf_mandelbrot_s': 'at least 10 distinct words',
    'mtld': 'at least 100 words (mtld_min_tokens) with some repetition',
    'dugast_u': 'at least 2 words, at least one repeated',
    'guiraud_r': 'at least 1 word',
    'ttr_moving_slope': 'at least 100 words (2 x ttr_slope_chunk_size)',
    'heaps_beta': 'at least 300 words (heaps_min_tokens)',
    'entropy': 'at least 1 word',
    'yule_k': 'at least 1 word',
    'simpson_d': 'at least 2 words',
    'brunet_w': 'at least 1 word',
    'hapax_ratio': 'at least 1 word',
    'hapax_percentage': 'at least 1 word',
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
    'avg_sent_len_word': 'at least 1 sentence with a letter',
    'avg_sent_len_char': 'at least 1 sentence',
    'sentence_length_cv': 'at least 2 sentences with a letter',
    'sent_len_skewness': 'at least 2 sentences of different length',
    'short_sent_ratio': 'at least 1 sentence with a letter',
    'long_sent_ratio': 'at least 1 sentence with a letter',
    'med_sent_len': 'at least 1 sentence with a letter',
    'sent_len_entropy': 'at least 2 sentences with a letter',
    # ── paragraph ───────────────────────────────────────────────
    'para_len_mean': 'at least 1 paragraph',
    'para_len_cv': 'at least 2 paragraphs',
    'sents_per_para_mean': 'at least 1 paragraph',
    'sents_per_para_cv': 'at least 2 paragraphs',
    'para_count_norm': 'at least 1 paragraph',
    # ── pos ─────────────────────────────────────────────────────
    'pos_noun': 'at least 1 token',
    'pos_propn': 'at least 1 token',
    'pos_verb': 'at least 1 token',
    'pos_adj': 'at least 1 token',
    'pos_adv': 'at least 1 token',
    'pos_det': 'at least 1 token',
    'pos_adp': 'at least 1 token',
    'pos_aux': 'at least 1 token',
    'pos_cconj': 'at least 1 token',
    'pos_sconj': 'at least 1 token',
    'pos_num': 'at least 1 token',
    'pos_intj': 'at least 1 token',
    'pos_punct': 'at least 1 token',
    # ── syntactic ───────────────────────────────────────────────
    'question_per_sent': 'at least 1 sentence',
    'pronoun_freq': 'at least 1 token',
    'nominal_verbal_ratio': 'at least 1 verb',
    'verb_dist_mean': 'at least 2 verbs',
    'verb_dist_cv': 'at least 3 verbs',
    'activity_ratio': 'at least 1 verb or adjective',
    'lexical_density': 'at least 1 word',
    'pos_dist_std': 'at least 1 token',
    'pos_kl_div': 'at least 1 token',
    # ── syntactic_dep ───────────────────────────────────────────
    'arc_len_mean': 'at least 1 sentence with 2 words',
    'parse_depth_mean': 'at least 1 sentence with 2 words',
    'sentfinal_noun': 'at least 1 sentence with a word',
    'sentfinal_propn': 'at least 1 sentence with a word',
    'sentfinal_verb': 'at least 1 sentence with a word',
    'sentfinal_adj': 'at least 1 sentence with a word',
    'sentfinal_adv': 'at least 1 sentence with a word',
    'sentfinal_det': 'at least 1 sentence with a word',
    'sentfinal_adp': 'at least 1 sentence with a word',
    'sentfinal_intj': 'at least 1 sentence with a word',
    'sentfinal_cconj': 'at least 1 sentence with a word',
    'sentfinal_sconj': 'at least 1 sentence with a word',
    'sentfinal_num': 'at least 1 sentence with a word',
    'sentfinal_aux': 'at least 1 sentence with a word',
    'sentfinal_pron': 'at least 1 sentence with a word',
    'sentfinal_other': 'at least 1 sentence with a word',
    # ── morphological ───────────────────────────────────────────
    'surface_per_lemma': 'at least 1 word',
    'morph_tense_past': 'at least 1 token with a Tense tag',
    'morph_tense_pres': 'at least 1 token with a Tense tag',
    'morph_tense_fut': 'at least 1 token with a Tense tag',
    'morph_aspect_perf': 'at least 1 token with an Aspect tag',
    'morph_aspect_imp': 'at least 1 token with an Aspect tag',
    'morph_aspect_prog': 'at least 1 token with an Aspect tag',
    'morph_case_nom': 'at least 1 token with a Case tag',
    'morph_case_acc': 'at least 1 token with a Case tag',
    'morph_case_dat': 'at least 1 token with a Case tag',
    'morph_case_loc': 'at least 1 token with a Case tag',
    'morph_case_abl': 'at least 1 token with a Case tag',
    'morph_case_gen': 'at least 1 token with a Case tag',
    'morph_person_1': 'at least 1 token with a Person tag',
    'morph_person_2': 'at least 1 token with a Person tag',
    'morph_person_3': 'at least 1 token with a Person tag',
    'morph_number_sing': 'at least 1 token with a Number tag',
    'morph_number_plur': 'at least 1 token with a Number tag',
    'morph_voice_pass': 'at least 1 verb',
    # ── morphological_zeyrek ────────────────────────────────────
    'agglutination_depth': 'at least 1 analysed word',
    'suffix_char_length_ratio': 'at least 1 analysed word',
    'suffix_bigram_entropy': 'at least 1 word with 2 visible suffixes',
    'derivational_suffix_ratio': 'at least 1 visible suffix',
    'verb_suffix_diversity': 'at least 50 verbs (verb_suffix_window)',
    'tense_past_def': 'at least 1 verb',
    'tense_past_nar': 'at least 1 verb',
    'tense_present': 'at least 1 verb',
    'tense_future': 'at least 1 verb',
    'negation_ratio': 'at least 1 verb',
    'passive_ratio': 'at least 1 verb',
    'plural_ratio': 'at least 1 analysed word',
    'case_acc_ratio': 'at least 1 analysed word',
    'case_dat_ratio': 'at least 1 analysed word',
    'case_loc_ratio': 'at least 1 analysed word',
    'case_abl_ratio': 'at least 1 analysed word',
    'case_gen_ratio': 'at least 1 analysed word',
    'case_ins_ratio': 'at least 1 analysed word',
    'conditional_suffix_ratio': 'at least 1 verb',
    'causative_suffix_ratio': 'at least 1 verb',
    'suffix_chain_cv': 'at least 2 analysed words, at least 1 suffix',
    'modal_possibility_ratio': 'at least 1 verb',
    'modal_necessity_ratio': 'at least 1 verb',
    'question_particle_ratio': 'at least 1 analysed word',
    # ── phonetic ────────────────────────────────────────────────
    'vowel_ratio': 'at least 1 alphabet letter',
    'front_vowel_ratio': 'at least 1 alphabet letter',
    'back_vowel_ratio': 'at least 1 alphabet letter',
    'harmony_fronting_ratio': 'at least 1 word with 2 vowels',
    'harmony_rounding_ratio': 'at least 1 word with 2 vowels',
    'syllable_mean': 'at least 1 syllabifiable word',
    'syllable_cv': 'at least 2 syllabifiable words',
    'syllable_1_ratio': 'at least 1 syllabifiable word',
    'syllable_2_ratio': 'at least 1 syllabifiable word',
    'syllable_3_ratio': 'at least 1 syllabifiable word',
    'syllable_4_ratio': 'at least 1 syllabifiable word',
    'syllable_5_ratio': 'at least 1 syllabifiable word',
    'syllable_6plus_ratio': 'at least 1 syllabifiable word',
    'sentence_syllable_mean': 'at least 1 sentence with a syllabifiable word',
    'sentence_syllable_cv': 'at least 2 such sentences',
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
    'digit_vs_all': 'non-empty text',
    'punc_,_ratio': 'at least 1 word',
    'punc_._ratio': 'at least 1 word',
    'punc_;_ratio': 'at least 1 word',
    'punc_!_ratio': 'at least 1 word',
    'punc_:_ratio': 'at least 1 word',
    'punc_-_ratio': 'at least 1 word',
    'punc_ellipsis_ratio': 'at least 1 word',
    'punc_paren_ratio': 'at least 1 word',
    'punc_quote_ratio': 'at least 1 word',
    'punc_question_ratio': 'at least 1 word',
    'punct_density': 'non-empty text',
    'punct_entropy': 'at least 1 punctuation mark',
    'consecutive_punct_ratio': 'at least 1 punctuation mark',
    'whitespace_ratio': 'non-empty text',
    'punct_variety': 'non-empty text',
    'uppercase_ratio': 'at least 1 token with a letter',
    'all_caps_word_ratio': 'at least 1 token with a letter',
    # ── chars (dinamik grup) ───────────────────────────────────────
    'chars': 'at least 1 alphabet letter',
    # ── custom_ngrams (dinamik grup) ───────────────────────────────
    'custom_ngrams': 'at least n words for an n-word phrase',
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
    'heaps_beta': 'Heaps (1978), as cited in Manning et al. (2008) §5.1.1',
    # Shannon entropisi beş anahtarda kullanılıyor. Formülün kaynağı hepsinde
    # aynı (Shannon 1948); ayrıldıkları yer formülün NEYE uygulandığı. Künye
    # bunu tek tek söylüyor — "Shannon (1948)" deyip bırakmak, dağılımın
    # seçimini de Shannon'a mal ederdi (2026-09-23, Efe).
    'entropy': 'Shannon (1948), as cited in QUITA §6.1.12',
    'entropy_std':
        'Shannon (1948) — the entropy formula; the standard deviation across segments '
        "is this library's own derivation",
    'punct_entropy':
        'Shannon (1948) — the entropy formula; applying it to the distribution of '
        "punctuation types is this library's own decision",
    'short_sent_ratio':
        "This library's threshold calibration (docs/threshold-calibration.md); "
        'TR 4, EN 7 — 15th percentile. Note: the '
        'TR value coincides with Ateşman (1997) p.74, where the easiest text has a '
        'mean sentence length of 4 words; that is a text mean, not a threshold, '
        'so it is not the source. Calibrated on novels/fiction only',
    'long_sent_ratio':
        "This library's threshold calibration (docs/threshold-calibration.md); "
        "TR 18, EN 39 — 85th percentile. Ateşman's "
        '30 was not used: that is the mean of the hardest text, not a single-sentence '
        'threshold (in Turkish novels 30 words is above the 95th percentile, so as a '
        'threshold it would almost never fire). Calibrated on novels/fiction only',
    'sent_len_entropy':
        'Shannon (1948) — the entropy formula; applying it to the distribution of '
        "sentence lengths is this library's own decision",
    'yule_k': 'Yule (1944), as cited in Malvern et al. (2004) eq. 3.9',
    'simpson_d': 'Simpson (1949), as cited in Bestgen (2023)',
    'brunet_w': 'Brunet (1978), as cited in Tweedie & Baayen (1998) p.328, eq. (10)',
    'hapax_percentage': 'QUITA §6.1.6',
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
    'pos_noun': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'pos_propn': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'pos_verb': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'pos_adj': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'pos_adv': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'pos_det': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'pos_adp': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'pos_aux': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'pos_cconj': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'pos_sconj': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'pos_num': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'pos_intj': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'pos_punct': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    # ── syntactic ───────────────────────────────────────────
    'verb_dist_mean': 'QUITA §6.2.1',
    'verb_dist_cv': 'QUITA §6.2.1',
    'activity_ratio': 'QUITA §6.2.2',
    'lexical_density':
        'Lu (2012); definition in the broad Hallidayan sense — all open-class words',
    'pos_dist_std':
        'Deutsch, Jasbi & Shieber (2020) Definition 3.3 (POSDdev); computed over '
        'ratios, 13 UD tags',
    'pos_kl_div': 'Deutsch, Jasbi & Shieber (2020) Definition 3.4 (POSdiv), in bits',
    # ── syntactic_dep ───────────────────────────────────────
    'arc_len_mean':
        'Liu (2008) eq. (1); text level from Jing & Liu (2015) p.164, eq. (3) (MDD2)',
    'parse_depth_mean': 'Jing & Liu (2015) p.164, eq. (2) and (4) (MHD2)',
    'sentfinal_noun': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'sentfinal_propn': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'sentfinal_verb': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'sentfinal_adj': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'sentfinal_adv': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'sentfinal_det': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'sentfinal_adp': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'sentfinal_intj': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'sentfinal_cconj': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'sentfinal_sconj': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'sentfinal_num': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'sentfinal_aux': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'sentfinal_pron': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    'sentfinal_other': 'de Marneffe et al. (2021) Table 1 (UPOS tag set)',
    # ── morphological ───────────────────────────────────────
    'surface_per_lemma':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'morph_tense_past':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'morph_tense_pres':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'morph_tense_fut':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'morph_aspect_perf':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'morph_aspect_imp':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'morph_aspect_prog':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'morph_case_nom':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'morph_case_acc':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'morph_case_dat':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'morph_case_loc':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'morph_case_abl':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'morph_case_gen':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'morph_person_1':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'morph_person_2':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'morph_person_3':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'morph_number_sing':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'morph_number_plur':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    'morph_voice_pass':
        'de Marneffe et al. (2021) Table 2 (universal morphological features)',
    # ── morphological_zeyrek ────────────────────────────────
    'agglutination_depth':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'suffix_char_length_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'suffix_bigram_entropy':
        "Shannon (1948) — the entropy formula; Zeyrek (a Python port of Zemberek's "
        'morphotactics); tag set from Akın & Akın (2007)',
    'derivational_suffix_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'verb_suffix_diversity':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'tense_past_def':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'tense_past_nar':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'tense_present':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'tense_future':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'negation_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'passive_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'plural_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'case_acc_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'case_dat_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'case_loc_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'case_abl_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'case_gen_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'case_ins_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'conditional_suffix_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'causative_suffix_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'suffix_chain_cv':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'modal_possibility_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'modal_necessity_ratio':
        "Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın "
        '(2007)',
    'question_particle_ratio':
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
    # Ateşman (1997) p.73 gives mean syllables per word as a Turkish norm
    # (2.6) and uses it in eq. (2); the CV of syllables is not a named
    # measure, so syllable_cv has no citation (K10, 2026-10-01, Efe).
    'syllable_mean': 'Ateşman (1997) p.73',
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
        'the sentence-length distribution in novel corpora: TR 15 authors / 1,089,841 '
        'sentences, EN 10 authors / 341,892 sentences. Method and raw percentile '
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
    'Coleman & Liau (1975)':
        'Coleman, M., & Liau, T. L. (1975). A computer readability formula designed '
        'for machine scoring. Journal of Applied Psychology, 60(2), 283–284. '
        'DOI 10.1037/h0076540',
    'Covington & McFall (2010)':
        'Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot: The '
        'moving-average type–token ratio (MATTR). Journal of Quantitative '
        'Linguistics, 17(2), 94–100. DOI 10.1080/09296171003643098',
    'Daller (2010)':
        "Daller, M. (2010). Guiraud's Index. BAAL 2010, Aberdeen. (Sunum.)",
    'de Marneffe et al. (2021)':
        'de Marneffe, M.-C., Manning, C. D., Nivre, J., & Zeman, D. (2021). '
        'Universal Dependencies. Computational Linguistics, 47(2), 255–308. DOI '
        '10.1162/COLI_a_00402',
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
        'London & New York: Routledge. 535 s. ISBN 0-415-11494-2 (pbk), 0-415-21761-X (hbk).',
    'Heaps (1978)':
        'Heaps, H. S. (1978). Information Retrieval: Computational and Theoretical '
        'Aspects. New York: Academic Press.',
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
    'Piantadosi (2014)':
        "Piantadosi, S. T. (2014). Zipf's word frequency law in natural language: A "
        'critical review and future directions. Psychonomic Bulletin & Review, '
        '21(5), 1112–1130. DOI 10.3758/s13423-014-0585-6',
    'Popescu & Altmann (2006)':
        'Popescu, I.-I., & Altmann, G. (2006). Some aspects of word frequencies. '
        'Glottometrics, 13, 23–46. RAM-Verlag; dergi ISSN 2625-8226.',
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
        'Laboratories. 22 s.',
    'Tweedie & Baayen (1998)':
        'Tweedie, F. J., & Baayen, R. H. (1998). How variable may a constant be? '
        'Measures of lexical richness in perspective. Computers and the Humanities, '
        '32(5), 323–352. DOI 10.1023/A:1001749303137',
    'van Heuven et al. (2014)':
        'van Heuven, W. J. B., Mandera, P., Keuleers, E., & Brysbaert, M. (2014). '
        'SUBTLEX-UK: A new and improved word frequency database for British '
        'English. Quarterly Journal of Experimental Psychology, 67(6), 1176–1190. '
        'DOI 10.1080/17470218.2013.850521',
    'Yule (1944)':
        'Yule, G. U. (1944). The Statistical Study of Literary Vocabulary. '
        'Cambridge University Press.',
    'Zeyrek':
        'Zeyrek — a Python port of the Zemberek morphological analyser. '
        'github.com/obulat/zeyrek',
    'Çetinkaya (2010)':
        'Çetinkaya, G. (2010). Türkçe metinlerin okunabilirlik düzeylerinin '
        'tanımlanması ve sınıflandırılması [Unpublished doctoral dissertation]. Ankara '
        'Üniversitesi, Sosyal Bilimler Enstitüsü. Advisor: Leylâ Uzun. 252 pp. '
        'hdl:20.500.12812/519962',
}

