"""Öznitelik registry — 182 statik anahtarın tek doğruluk kaynağı (T19).

``describe_feature(key)`` bir anahtar hakkında bilinen her şeyi tek çağrıda
döndürür: ne ölçtüğü, nasıl hesaplandığı, hangi ölçekte olduğu, hangi
``ProcessedText`` alanlarını okuduğu, hangi ayarların değeri değiştirdiği, ne
kadar metin gerektirdiği ve künyesi. Kullanıcı üç ayrı sözlüğe bakmak zorunda
kalmasın diye tek giriş noktası budur.

Taban şema **TR 207 · EN 181**: 182 statik anahtar + dile göre 26–29 ``char_*``.
``custom_ngrams`` istenmedikçe anahtar üretmez, bu yüzden toplama girmez.
14 grup = 12 statik + 2 dinamik.

Metin tabloları ``_registry_texts.py``'de — orası veri, burası yapı ve mantık
(2026-09-18, Efe).

**Anahtar isimleri bu görevde donuyor (K8).** İlk yayına (T30) kadar
değiştirilebilir, ama her değişiklik registry, ``API-SOZLESMESI.md`` ve
sayılarla **birlikte** yapılır.
"""

from __future__ import annotations

from ._registry_texts import (
    FEATURE_CITATIONS,
    FEATURE_DESCRIPTIONS,
    FEATURE_FORMULAS,
    FEATURE_REQUIRES,
)

__all__ = ["describe_feature"]


# ── gruplar ───────────────────────────────────────────────────────────

GROUP_LABELS: dict[str, str] = {
    "lexical": "Lexical richness & frequency",
    "frequency_structure": "Frequency structure (h-point family, Popescu & Altmann)",
    "sentence": "Sentence statistics",
    "paragraph": "Paragraph structure",
    "pos": "Part-of-speech ratios",
    "syntactic": "Discourse & syntax",
    "syntactic_dep": "Dependency tree (distance, depth, sentence-final POS)",
    "morphological": "Morphological style (spaCy)",
    "morphological_zeyrek": "Morphological style (Zeyrek, TR only)",
    "phonetic": "Phonetic patterns",
    "readability": "Readability scores",
    "punctuation": "Punctuation & digits",
    "chars": "Character frequency vector  [dynamic: char_a...char_z]",
    "custom_ngrams": "User-defined n-gram ratios  [dynamic: ng_{...}]",
}

# Anahtar sayısı sabit olmayan, önekle eşleşen gruplar. ``pos_bigrams`` üçüncü
# dinamik gruptu; 2026-09-18'de taban şemadan çıktı (Karar Günlüğü).
DYNAMIC_PREFIXES: dict[str, str] = {
    "chars": "char_",
    "custom_ngrams": "ng_",
}

# `API-SOZLESMESI.md` §4'ten birebir.
STATIC_GROUP_KEYS: dict[str, tuple[str, ...]] = {
    "lexical": (
        'n_lemma_count', 'avg_word_length', 'word_length_cv', 'ttr', 'mattr', 'entropy_std',
        'herdan_c', 'sichel_s', 'zipf_exponent', 'zipf_r2', 'zipf_mandelbrot_q',
        'zipf_mandelbrot_s', 'mtld', 'dugast_u', 'guiraud_r', 'ttr_moving_slope', 'heaps_beta',
        'entropy', 'yule_k', 'simpson_d', 'brunet_w', 'hapax_ratio', 'hapax_percentage',
        'vocd_d', 'hdd', 'msttr', 'noun_variation', 'verb_variation', 'adj_variation',
        'adv_variation', 'wordfreq_mean', 'wordfreq_rare_ratio',
    ),
    "frequency_structure": (
        'h_point', 'vocab_richness_r1', 'vocab_richness_r4', 'repeat_rate', 'rr_mcintosh',
        'gini_coef', 'curve_length', 'curve_length_r', 'lambda_pa', 'adjusted_modulus',
        'writers_view_alpha', 'thematic_concentration', 'secondary_thematic_concentration',
    ),
    "sentence": (
        'avg_sent_len_word', 'avg_sent_len_char', 'sentence_length_cv', 'sent_len_skewness',
        'short_sent_ratio', 'long_sent_ratio', 'med_sent_len', 'sent_len_entropy',
    ),
    "paragraph": (
        'para_len_mean', 'para_len_cv', 'sents_per_para_mean', 'sents_per_para_cv',
        'para_count_norm',
    ),
    "pos": (
        'pos_noun', 'pos_propn', 'pos_verb', 'pos_adj', 'pos_adv', 'pos_det', 'pos_adp',
        'pos_aux', 'pos_cconj', 'pos_sconj', 'pos_num', 'pos_intj', 'pos_punct',
    ),
    "syntactic": (
        'question_per_sent', 'pronoun_freq', 'nominal_verbal_ratio', 'verb_dist_mean',
        'verb_dist_cv', 'activity_ratio', 'lexical_density', 'pos_dist_std', 'pos_kl_div',
    ),
    "syntactic_dep": (
        'arc_len_mean', 'parse_depth_mean', 'sentfinal_noun', 'sentfinal_propn',
        'sentfinal_verb', 'sentfinal_adj', 'sentfinal_adv', 'sentfinal_det', 'sentfinal_adp',
        'sentfinal_intj', 'sentfinal_cconj', 'sentfinal_sconj', 'sentfinal_num',
        'sentfinal_aux', 'sentfinal_pron', 'sentfinal_other',
    ),
    "morphological": (
        'surface_per_lemma', 'morph_tense_past', 'morph_tense_pres', 'morph_tense_fut',
        'morph_aspect_perf', 'morph_aspect_imp', 'morph_aspect_prog', 'morph_case_nom',
        'morph_case_acc', 'morph_case_dat', 'morph_case_loc', 'morph_case_abl',
        'morph_case_gen', 'morph_person_1', 'morph_person_2', 'morph_person_3',
        'morph_number_sing', 'morph_number_plur', 'morph_voice_pass',
    ),
    "morphological_zeyrek": (
        'agglutination_depth', 'suffix_char_length_ratio', 'suffix_bigram_entropy',
        'derivational_suffix_ratio', 'verb_suffix_diversity', 'tense_past_def',
        'tense_past_nar', 'tense_present', 'tense_future', 'negation_ratio', 'passive_ratio',
        'plural_ratio', 'case_acc_ratio', 'case_dat_ratio', 'case_loc_ratio', 'case_abl_ratio',
        'case_gen_ratio', 'case_ins_ratio', 'conditional_suffix_ratio',
        'causative_suffix_ratio', 'suffix_chain_cv', 'modal_possibility_ratio',
        'modal_necessity_ratio', 'question_particle_ratio',
    ),
    "phonetic": (
        'vowel_ratio', 'front_vowel_ratio', 'back_vowel_ratio', 'vowel_harmony_compliance',
        'syllable_mean', 'syllable_cv', 'syllable_1_ratio', 'syllable_2_ratio',
        'syllable_3_ratio', 'syllable_4_ratio', 'syllable_5_ratio', 'syllable_6plus_ratio',
        'sentence_syllable_mean', 'sentence_syllable_cv',
    ),
    "readability": (
        'bezirci_yilmaz', 'atesman', 'cetinkaya_uzun', 'flesch_reading_ease',
        'flesch_kincaid_grade', 'smog', 'ari', 'coleman_liau', 'lix',
        'polysyllabic_word_ratio', 'long_word_ratio',
    ),
    "punctuation": (
        'digit_vs_all', 'punc_,_ratio', 'punc_._ratio', 'punc_;_ratio', 'punc_!_ratio',
        'punc_:_ratio', 'punc_-_ratio', 'punc_ellipsis_ratio', 'punc_paren_ratio',
        'punc_quote_ratio', 'punc_question_ratio', 'punct_density', 'punct_entropy',
        'consecutive_punct_ratio', 'whitespace_ratio', 'punct_variety', 'uppercase_ratio',
        'all_caps_word_ratio',
    ),
}

# Grubun fonksiyonlarının **gerçekten** okuduğu ``ProcessedText`` alanları,
# fazlası değil. Kaydın var olması yetmez, doğru olması gerekir:
# ``frequency_structure`` (2026-08-25) ve ``syntactic`` (2026-08-26) iki kez
# eksik kaydedildi ve ikisi de "kaydı var mı" testinden geçiyordu.
GROUP_INPUTS: dict[str, tuple[str, ...]] = {
    "lexical": ("surface_tokens", "lemma_tokens", "pos_data"),
    "frequency_structure": ("lemma_tokens", "pos_data"),
    "sentence": ("sentences_as_tokens",),
    "paragraph": ("raw_text",),
    "pos": ("pos_data",),
    "syntactic": ("pos_data", "sentences_as_tokens"),
    "syntactic_dep": ("dep_data",),
    "morphological": ("morph_tags", "pos_data", "surface_tokens", "lemma_tokens"),
    "morphological_zeyrek": ("morpheme_lists", "pos_data"),
    "phonetic": ("raw_text", "surface_tokens", "sentences_as_tokens"),
    "readability": ("raw_text", "surface_tokens"),
    "punctuation": ("raw_text", "surface_tokens"),
    "chars": ("raw_text",),
    "custom_ngrams": ("surface_tokens",),
}


# ── ölçek ─────────────────────────────────────────────────────────────

# Kapalı küme. Yeni bir değer eklemek `docs/kullanim.md`'yi de değiştirir.
SCALES: frozenset[str] = frozenset({
    "ratio_0_1", "bits", "length", "cv", "signed", "count", "score",
})

# Her grubun varsayılanı — 14'ünün hepsi burada olmak zorunda.
GROUP_SCALES: dict[str, str] = {
    "lexical": "ratio_0_1",
    "frequency_structure": "ratio_0_1",
    "sentence": "length",
    "paragraph": "length",
    "pos": "ratio_0_1",
    "syntactic": "ratio_0_1",
    "syntactic_dep": "ratio_0_1",
    "morphological": "ratio_0_1",
    "morphological_zeyrek": "ratio_0_1",
    "phonetic": "ratio_0_1",
    "readability": "score",
    "punctuation": "ratio_0_1",
    "chars": "ratio_0_1",
    "custom_ngrams": "ratio_0_1",
}

# YALNIZCA grup varsayılanından sapanlar. Varsayılanla aynı değeri buraya
# yazmak yasak — çift kayıt ileride birinin güncellenip diğerinin unutulmasına
# yol açar; ``test_feature_scales_grup_varsayiliyla_ayni_deger_icermez`` denetler.
#
# Ölçek ilkesi (2026-09-17, Efe): bir anahtar **tanımı gereği** [0, 1]
# içindeyse ``ratio_0_1``, değilse başka ölçek. "Pratikte genelde 0-1 çıkıyor"
# yetmez.
FEATURE_SCALES: dict[str, str] = {
    # lexical
    "n_lemma_count": "count",
    "avg_word_length": "length",
    "word_length_cv": "cv",
    "entropy": "bits",
    "entropy_std": "bits",
    "ttr_moving_slope": "signed",
    "yule_k": "score",
    "brunet_w": "score",
    "mtld": "score",
    "dugast_u": "score",
    "guiraud_r": "score",
    "vocd_d": "score",
    "heaps_beta": "score",            # kırpılmıyor, 1'i aşabilir (2026-09-17)
    "zipf_exponent": "score",
    "zipf_mandelbrot_q": "score",
    "zipf_mandelbrot_s": "score",
    "wordfreq_mean": "score",
    # frequency_structure
    "h_point": "score",
    "curve_length": "score",
    "lambda_pa": "score",
    "adjusted_modulus": "score",
    "writers_view_alpha": "score",    # radyan cinsinden AÇI (~1.57-3.15), kosinüs değil
    "thematic_concentration": "score",            # 1'i aşabiliyor: eşit sıklıklı
    "secondary_thematic_concentration": "score",  # kelimelere ortalama sıra verilmesi
                                                  # ve kesirli h-point yüzünden
    # sentence
    "sentence_length_cv": "cv",
    "sent_len_skewness": "signed",
    "short_sent_ratio": "ratio_0_1",
    "long_sent_ratio": "ratio_0_1",
    "sent_len_entropy": "bits",
    # paragraph
    "para_len_cv": "cv",
    "sents_per_para_cv": "cv",
    "para_count_norm": "score",       # 1000 kelimedeki paragraf; 1'i aşar
    # syntactic
    "nominal_verbal_ratio": "score",
    "verb_dist_mean": "length",
    "verb_dist_cv": "cv",
    "pos_kl_div": "bits",
    # syntactic_dep
    "arc_len_mean": "length",
    "parse_depth_mean": "length",
    # morphological
    "surface_per_lemma": "score",
    # morphological_zeyrek
    "agglutination_depth": "length",
    "suffix_bigram_entropy": "bits",
    "suffix_chain_cv": "cv",
    "verb_suffix_diversity": "count",
    # phonetic
    "syllable_mean": "length",
    "syllable_cv": "cv",
    "sentence_syllable_mean": "length",
    "sentence_syllable_cv": "cv",
    # readability (grup varsayılanı score)
    "polysyllabic_word_ratio": "ratio_0_1",
    "long_word_ratio": "ratio_0_1",
    # punctuation
    "punct_entropy": "bits",
    "punct_variety": "count",
    # Kelime başına işaret sayısı — "Ne!!!" → 3. Oran değil (2026-09-18).
    **{f"punc_{isaret}_ratio": "score" for isaret in
       (",", ".", ";", "!", ":", "-", "ellipsis", "paren", "quote", "question")},
}


# ── ayarlar ───────────────────────────────────────────────────────────

# Anahtar → değeri değiştiren ``FeatureParams`` alanları. Listede olmayan
# anahtar için ``describe_feature`` boş tuple döndürür: ayarlanamaz demektir.
FEATURE_PARAMS: dict[str, tuple[str, ...]] = {
    "mattr": ("mattr_window",),
    "entropy_std": ("mattr_window",),
    "mtld": ("mtld_threshold", "mtld_min_tokens"),
    "hdd": ("hdd_sample_size",),
    "msttr": ("msttr_segment_size",),
    "vocd_d": ("vocd_sample_min", "vocd_sample_max", "vocd_num_samples",
               "vocd_num_runs", "vocd_min_tokens", "vocd_random_seed"),
    "brunet_w": ("brunet_w_a",),
    "heaps_beta": ("heaps_min_tokens", "heaps_step"),
    "ttr_moving_slope": ("ttr_slope_chunk_size",),
    "verb_suffix_diversity": ("verb_suffix_window",),
    "short_sent_ratio": ("short_sent_threshold",),
    "long_sent_ratio": ("long_sent_threshold",),
    "parse_depth_mean": ("max_parse_depth",),
}


# ── künye ─────────────────────────────────────────────────────────────

UNVERIFIED_CONSTANTS: frozenset[str] = frozenset({
    # K12 Kademe D — sabiti birincil kaynağa karşı doğrulanmamış anahtarlar.
    # Bkz. 00-ANA-PLAN.md "K12 eki-2 — doğrulama kademeleri".
    # Bir sabit doğrulandığında buradan SİLİNİR; listeye eklemek serbest,
    # silmek için birincil kaynak ya da çapraz uygulama testi şart.
    # 2026-09-12: `brunet_w` buradan SİLİNDİ — Kademe C'ye yükseldi
    # (Tweedie & Baayen 1998 denk. 10 okundu + zipfR çapraz kontrolü).
    # Liste şu an boş; yeni Kademe D sabiti çıkarsa buraya yazılır.
})


def _citation(key: str) -> str | None:
    """Künye — sabiti doğrulanmamışsa bunu açıkça söyler.

    K10'un uzantısı: neyi bilmediğimizi de söyleriz. Kullanıcı ``brunet_w``'yi
    çalışmasında kullanacaksa, sabitinin doğrulanmadığını **bilerek** kullansın.
    Uyarı ayrı bir alana değil künyenin sonuna yazılıyor, çünkü zarar
    alıntılama anında oluşuyor: ek, yöntem bölümüne kopyalanacak dizenin
    kendisine yapışıyor.
    """
    kunye = FEATURE_CITATIONS.get(key)
    if kunye and key in UNVERIFIED_CONSTANTS:
        return kunye + " [doğrulanmamış sabit]"
    return kunye


# ── keşif ─────────────────────────────────────────────────────────────


def get_group(key: str) -> str:
    """Bir öznitelik anahtarının hangi gruba ait olduğunu döndürür.

    Önce statik listeler, sonra dinamik önekler denenir. **Sıra önemli:**
    statik bir anahtar ileride bir dinamik önekle (``char_``, ``ng_``)
    başlayacak şekilde adlandırılırsa yanlış gruba düşer.

    Raises
    ------
    KeyError
        Anahtar hiçbir gruba ait değilse.
    """
    for grup, anahtarlar in STATIC_GROUP_KEYS.items():
        if key in anahtarlar:
            return grup
    for grup, onek in DYNAMIC_PREFIXES.items():
        if key.startswith(onek):
            return grup
    raise KeyError(f"Bilinmeyen feature anahtarı: {key!r}")


def describe_feature(key: str) -> dict:
    """Bir öznitelik anahtarı hakkında bilinen her şey.

    Parameters
    ----------
    key : str
        Öznitelik anahtarı. Dinamik grup anahtarları da kabul edilir
        (``char_a``, ``ng_ve_bir``…); bu durumda ``formula`` ve ``requires``
        grup düzeyindeki genel ifadedir.

    Returns
    -------
    dict
        ``key``, ``group``, ``group_label``, ``description``, ``formula``,
        ``scale``, ``inputs``, ``params``, ``requires``, ``citation``.
        ``citation`` ``None`` ise o anahtar adlandırılmış bir literatür
        ölçüsü değildir. Ölçünün **kime ait olduğu** hakkında bir şey
        söylemez: kimi anahtar saf tanımdır (``punc_,_ratio``), kimi ise
        bir dış etiket şemasının kategorilerini sayar (``morph_case_loc``
        → UD; ``case_loc_ratio`` → Zeyrek).

    Raises
    ------
    KeyError
        Anahtar hiçbir gruba ait değilse.

    Examples
    --------
    >>> describe_feature("mattr")["formula"]
    'mean TTR of every sliding window of mattr_window words'
    >>> describe_feature("mattr")["requires"]
    'at least 50 words (mattr_window)'
    >>> describe_feature("ttr_moving_slope")["citation"] is None
    True
    """
    grup = get_group(key)                      # KeyError'ı o fırlatır
    return {
        "key": key,
        "group": grup,
        "group_label": GROUP_LABELS[grup],
        "description": FEATURE_DESCRIPTIONS.get(key) or FEATURE_DESCRIPTIONS.get(grup, ""),
        "formula": FEATURE_FORMULAS.get(key) or FEATURE_FORMULAS.get(grup, ""),
        # 🔴 Köşeli parantez bilerek: eksik bir grup KeyError fırlatmalı.
        # `.get(grup, "")` olsaydı yeni bir grup eklenip kaydı unutulduğunda
        # `scale` sessizce "" olur ve kullanıcının ölçekleme kodu bunu
        # "oran değil" diye yorumlardı. `description` ve `formula` açıklayıcı,
        # `scale` makine tarafından okunuyor.
        "scale": FEATURE_SCALES.get(key) or GROUP_SCALES[grup],
        "inputs": GROUP_INPUTS[grup],
        "params": FEATURE_PARAMS.get(key, ()),
        "requires": FEATURE_REQUIRES.get(key) or FEATURE_REQUIRES[grup],
        "citation": _citation(key),
    }
