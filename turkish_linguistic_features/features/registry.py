"""Öznitelik registry — 174 statik anahtarın tek doğruluk kaynağı (T19).

``describe_feature(key)`` bir anahtar hakkında bilinen her şeyi tek çağrıda
döndürür: ne ölçtüğü, nasıl hesaplandığı, hangi ölçekte olduğu, hangi
``ProcessedText`` alanlarını okuduğu, hangi ayarların değeri değiştirdiği, ne
kadar metin gerektirdiği ve künyesi. Kullanıcı üç ayrı sözlüğe bakmak zorunda
kalmasın diye tek giriş noktası budur.

Taban şema **TR 199 · EN 172**: 174 statik anahtardan dile özgü olanlar + dile
göre 26–29 ``char_*``.
``custom_ngrams`` istenmedikçe anahtar üretmez, bu yüzden toplama girmez.
14 grup = 12 statik + 2 dinamik.

Metin tabloları ``_registry_texts.py``'de — orası veri, burası yapı ve mantık
(2026-09-18, Efe).

**Anahtar isimleri bu görevde donuyor (K8).** İlk yayına (T30) kadar
değiştirilebilir, ama her değişiklik registry, doküman ve
sayılarla **birlikte** yapılır.
"""

from __future__ import annotations

from ..alfabe import _ALFABE
from ._registry_definitions import definitions_of
from ._registry_texts import (
    BIBLIOGRAPHY,
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
    "chars": "Character frequency vector  [dynamic: one key per letter — TR 29, EN 26]",
    "custom_ngrams": "User-defined n-gram counts  [dynamic: ngram_{...}_count]",
}

# Anahtar sayısı sabit olmayan, önekle eşleşen gruplar. ``pos_bigrams`` üçüncü
# dinamik gruptu; 2026-09-18'de taban şemadan çıktı (Karar Günlüğü).
DYNAMIC_PREFIXES: dict[str, str] = {
    "chars": "char_",
    "custom_ngrams": "ngram_",
}

# Geçerli `char_` son ekleri: iki dilin alfabesinin birleşimi.
_CHAR_HARFLERI: frozenset[str] = frozenset("".join(_ALFABE.values()))

STATIC_GROUP_KEYS: dict[str, tuple[str, ...]] = {
    "lexical": (
        'lemma_count', 'word_count', 'word_len_mean', 'ttr', 'mattr', 'herdan_c', 'sichel_s',
        'zipf_exponent', 'zipf_r2',
        'zipf_mandelbrot_q',
        'zipf_mandelbrot_s', 'mtld', 'dugast_u', 'guiraud_r', 'cttr', 'summer_s', 'maas_a2',
        'herdan_vm', 'heaps_beta',
        'entropy', 'yule_k', 'simpson_d', 'brunet_w', 'hapax_ratio', 'hapax_token_ratio',
        'vocd_d', 'hdd', 'msttr', 'noun_variation', 'verb_variation', 'adj_variation',
        'adv_variation', 'wordfreq_mean', 'wordfreq_rare_ratio',
    ),
    "frequency_structure": (
        'h_point', 'vocab_richness_r1', 'vocab_richness_r4', 'repeat_rate', 'rr_mcintosh',
        'gini_coef', 'curve_length', 'curve_length_r', 'lambda_pa', 'adjusted_modulus',
        'writers_view_alpha', 'thematic_concentration', 'secondary_thematic_concentration',
    ),
    "sentence": (
        'sent_len_mean', 'sent_len_char_mean', 'short_sent_ratio', 'long_sent_ratio', 'sent_len_median',
        'sent_len_entropy',
    ),
    "paragraph": (
        'para_len_mean', 'sents_per_para_mean',
            ),
    "pos": (
        'pos_noun_ratio', 'pos_propn_ratio', 'pos_verb_ratio', 'pos_adj_ratio', 'pos_adv_ratio',
        'pos_det_ratio', 'pos_adp_ratio',
        'pos_aux_ratio', 'pos_cconj_ratio', 'pos_sconj_ratio', 'pos_num_ratio', 'pos_intj_ratio',
    ),
    "syntactic": (
        'question_sent_ratio', 'pronoun_ratio', 'verb_dist_mean',
        'activity_ratio', 'lexical_density', 'posddev', 'posdiv',
    ),
    "syntactic_dep": (
        'arc_len_mean', 'parse_depth_mean', 'sentfinal_noun_ratio', 'sentfinal_propn_ratio',
        'sentfinal_verb_ratio', 'sentfinal_adj_ratio', 'sentfinal_adv_ratio', 'sentfinal_det_ratio',
        'sentfinal_adp_ratio',
        'sentfinal_intj_ratio', 'sentfinal_cconj_ratio', 'sentfinal_sconj_ratio', 'sentfinal_num_ratio',
        'sentfinal_aux_ratio', 'sentfinal_pron_ratio', 'sentfinal_other_ratio',
    ),
    "morphological": (
        'surface_per_lemma', 'tense_past_ratio', 'tense_pres_ratio', 'tense_fut_ratio',
        'aspect_perf_ratio', 'aspect_imp_ratio', 'aspect_prog_ratio', 'case_nom_ratio',
        'case_acc_ratio', 'case_dat_ratio', 'case_loc_ratio', 'case_abl_ratio',
        'case_gen_ratio', 'person_1_ratio', 'person_2_ratio', 'person_3_ratio',
        'number_sing_ratio', 'number_plur_ratio', 'voice_pass_ratio',
    ),
    "morphological_zeyrek": (
        'zeyrek_agglutination_depth', 'zeyrek_suffix_char_length_ratio', 'zeyrek_suffix_bigram_entropy',
        'zeyrek_derivational_suffix_ratio', 'zeyrek_verb_suffix_diversity', 'zeyrek_tense_past_def_ratio',
        'zeyrek_tense_past_nar_ratio', 'zeyrek_tense_present_ratio', 'zeyrek_tense_future_ratio',
        'zeyrek_negation_ratio', 'zeyrek_passive_ratio',
        'zeyrek_plural_ratio', 'zeyrek_case_acc_ratio', 'zeyrek_case_dat_ratio', 'zeyrek_case_loc_ratio',
        'zeyrek_case_abl_ratio',
        'zeyrek_case_gen_ratio', 'zeyrek_case_ins_ratio', 'zeyrek_conditional_suffix_ratio',
        'zeyrek_causative_suffix_ratio', 'zeyrek_modal_possibility_ratio',
        'zeyrek_modal_necessity_ratio', 'zeyrek_question_particle_ratio',
    ),
    "phonetic": (
        'vowel_ratio', 'front_vowel_ratio', 'back_vowel_ratio',
        'harmony_fronting_ratio', 'harmony_rounding_ratio',
        'syllable_mean', 'syllable_1_ratio', 'syllable_2_ratio',
        'syllable_3_ratio', 'syllable_4_ratio', 'syllable_5_ratio', 'syllable_6plus_ratio',
        'sent_syllable_mean',
    ),
    "readability": (
        'bezirci_yilmaz', 'atesman', 'cetinkaya_uzun', 'flesch_reading_ease',
        'flesch_kincaid_grade', 'smog', 'ari', 'coleman_liau', 'lix',
        'polysyllabic_word_ratio', 'long_word_ratio',
    ),
    "punctuation": (
        'digit_ratio', 'punct_comma_ratio', 'punct_period_ratio', 'punct_semicolon_ratio',
        'punct_exclamation_ratio', 'punct_colon_ratio', 'punct_dash_ratio', 'punct_ellipsis_ratio',
        'punct_paren_ratio', 'punct_quote_ratio', 'punct_question_ratio', 'punct_char_ratio', 'punct_entropy',
        'consecutive_punct_ratio', 'whitespace_ratio', 'punct_variety', 'uppercase_ratio',
        'all_caps_word_ratio',
    ),
}

# Grubun fonksiyonlarının **gerçekten** okuduğu ``ProcessedText`` alanları,
# fazlası değil. Kaydın var olması yetmez, doğru olması gerekir:
# ``frequency_structure`` (2026-08-25) ve ``syntactic`` (2026-08-26) iki kez
# eksik kaydedildi ve ikisi de "kaydı var mı" testinden geçiyordu.
GROUP_INPUTS: dict[str, tuple[str, ...]] = {
    # Kelime ham metinden sayılır, etiketi konumla tokendan alınır (2026-10-07, Efe):
    # etiket isteyen grup `raw_text` + `surface_tokens` + `pos_data` + `lemma_tokens` okur.
    "lexical": ("raw_text", "surface_tokens", "lemma_tokens", "pos_data"),
    "frequency_structure": ("raw_text", "surface_tokens", "lemma_tokens", "pos_data"),
    "sentence": ("raw_text", "surface_tokens"),
    "paragraph": ("raw_text",),
    "pos": ("raw_text", "surface_tokens", "lemma_tokens", "pos_data"),
    "syntactic": ("raw_text", "surface_tokens", "lemma_tokens", "pos_data"),
    "syntactic_dep": ("dep_data",),
    "morphological": ("raw_text", "surface_tokens", "lemma_tokens", "pos_data", "morph_tags"),
    "morphological_zeyrek": ("raw_text", "surface_tokens", "lemma_tokens", "pos_data",
                             "morpheme_lists"),
    "phonetic": ("raw_text", "surface_tokens"),
    "readability": ("raw_text", "surface_tokens"),
    "punctuation": ("raw_text", "surface_tokens"),
    "chars": ("raw_text",),
    "custom_ngrams": ("raw_text", "surface_tokens", "lemma_tokens", "pos_data"),
}


# ── ölçek ─────────────────────────────────────────────────────────────

# Kapalı küme. Yeni bir değer eklemek ölçek tablosunu da değiştirir (`docs/en/explanation/concepts.md`,
# `docs/tr/aciklama/kavramlar.md`).
SCALES: frozenset[str] = frozenset({
    "ratio_0_1", "nats", "length", "count", "score",
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
    "custom_ngrams": "count",
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
    "lemma_count": "count",
    "word_count": "count",
    "word_len_mean": "length",
    "entropy": "nats",
    "yule_k": "score",
    "brunet_w": "score",
    "mtld": "score",
    "dugast_u": "score",
    "guiraud_r": "score",
    "cttr": "score",
    "summer_s": "score",
    "maas_a2": "score",
    "herdan_vm": "score",
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
    "short_sent_ratio": "ratio_0_1",
    "long_sent_ratio": "ratio_0_1",
    "sent_len_entropy": "nats",
    # paragraph
    # syntactic
    "verb_dist_mean": "length",
    "posdiv": "nats",
    # syntactic_dep
    "arc_len_mean": "length",
    "parse_depth_mean": "length",
    # morphological
    "surface_per_lemma": "score",
    # morphological_zeyrek
    "zeyrek_agglutination_depth": "length",
    "zeyrek_suffix_bigram_entropy": "nats",
    "zeyrek_verb_suffix_diversity": "count",
    # phonetic
    "syllable_mean": "length",
    "sent_syllable_mean": "length",
    # readability (grup varsayılanı score)
    "polysyllabic_word_ratio": "ratio_0_1",
    "long_word_ratio": "ratio_0_1",
    # punctuation
    "punct_entropy": "nats",
    "punct_variety": "count",
}


# ── ayarlar ───────────────────────────────────────────────────────────

# Anahtar → değeri değiştiren ``FeatureParams`` alanları. Listede olmayan
# anahtar için ``describe_feature`` boş tuple döndürür: ayarlanamaz demektir.
FEATURE_PARAMS: dict[str, tuple[str, ...]] = {
    "mattr": ("mattr_window",),
    "mtld": ("mtld_threshold", "mtld_min_tokens"),
    "hdd": ("hdd_sample_size",),
    "msttr": ("msttr_segment_size",),
    "vocd_d": ("vocd_sample_min", "vocd_sample_max", "vocd_num_samples",
               "vocd_num_runs", "vocd_min_tokens", "vocd_random_seed"),
    "brunet_w": ("brunet_w_a",),
    "heaps_beta": ("heaps_min_tokens", "heaps_step"),
    "zeyrek_verb_suffix_diversity": ("verb_suffix_window",),
    "short_sent_ratio": ("short_sent_threshold",),
    "long_sent_ratio": ("long_sent_threshold",),
    "parse_depth_mean": ("max_parse_depth",),
}


# ── künye ─────────────────────────────────────────────────────────────

UNVERIFIED_CONSTANTS: frozenset[str] = frozenset({
    # K12 Kademe D — sabiti birincil kaynağa karşı doğrulanmamış anahtarlar.
    # Bir sabit doğrulandığında buradan SİLİNİR; listeye eklemek serbest,
    # silmek için birincil kaynak ya da çapraz uygulama testi şart.
    # 2026-09-12: `brunet_w` buradan SİLİNDİ — Kademe C'ye yükseldi
    # (Tweedie & Baayen 1998 denk. 10 okundu + zipfR çapraz kontrolü).
    # Liste şu an boş; yeni Kademe D sabiti çıkarsa buraya yazılır.
})


def _references(kunye: str | None) -> tuple[str, ...]:
    """Künyede adı geçen eserlerin tam bibliyografik kayıtları.

    Künye kısa işaretçidir (``"Yule (1944), aktaran Malvern et al. (2004)
    denk. 3.9"``); yöntem bölümüne kopyalanacak olan tam kayıttır. Bir künye
    birden çok esere atıf yapabildiği için demet döner — yukarıdaki örnekte
    hem Yule hem Malvern.

    Eşleşme dizge içinde arama ile yapılır; bunun güvenli olmasının sebebi
    ``test_registry.py``in her künyenin **en az bir** kaynakça anahtarını
    birebir içermesini şart koşmasıdır (2026-09-19, Efe).
    """
    if not kunye:
        return ()
    return tuple(BIBLIOGRAPHY[ad] for ad in sorted(BIBLIOGRAPHY) if ad in kunye)


def _citation(key: str) -> str | None:
    """Künye — sabiti doğrulanmamışsa bunu açıkça söyler.

    K10'un uzantısı: neyi bilmediğimizi de söyleriz. Kullanıcı ``brunet_w``'yi
    çalışmasında kullanacaksa, sabitinin doğrulanmadığını **bilerek** kullansın.
    Uyarı ayrı bir alana değil künyenin sonuna yazılıyor, çünkü zarar
    alıntılama anında oluşuyor: ek, yöntem bölümüne kopyalanacak dizenin
    kendisine yapışıyor.
    """
    kunye = FEATURE_CITATIONS.get(key)
    if kunye is None and not any(key in v for v in STATIC_GROUP_KEYS.values()):
        # Dinamik anahtar (`char_a_ratio`): künye grup adıyla tutulur (2026-10-07, Efe).
        grup = next((g for g, onek in DYNAMIC_PREFIXES.items() if key.startswith(onek)), None)
        kunye = FEATURE_CITATIONS.get(grup) if grup else None
    if kunye and key in UNVERIFIED_CONSTANTS:
        return kunye + " [unverified constant]"
    return kunye


# ── keşif ─────────────────────────────────────────────────────────────


def get_group(key: str) -> str:
    """Bir öznitelik anahtarının hangi gruba ait olduğunu döndürür.

    Önce statik listeler, sonra dinamik önekler denenir. **Sıra önemli:**
    statik bir anahtar ileride bir dinamik önekle (``char_``, ``ngram_``)
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
        if not key.startswith(onek):
            continue
        # `char_{harf}_ratio`: harf iki dilin alfabesinin birleşiminden tek bir
        # harf olmalı (TR 29 + EN'deki q, w, x). Yalnız önek denetlenince
        # `char_zzz` de kabul ediliyordu. `ngram_{...}_count`: öbek serbest,
        # kullanıcı seçer; yalnız son ek denetlenir.
        if grup == "chars" and not (key.endswith("_ratio")
                                    and key[len(onek):-len("_ratio")] in _CHAR_HARFLERI):
            break
        if grup == "custom_ngrams" and not (key.endswith("_count") and len(key) > len("ngram__count")):
            break
        return grup
    raise KeyError(f"Unknown feature key: {key!r}")


def describe_feature(key: str, lang: str | None = None) -> dict:
    """Bir öznitelik anahtarı hakkında bilinen her şey.

    Parameters
    ----------
    key : str
        Öznitelik anahtarı. Dinamik grup anahtarları da kabul edilir
        (``char_a_ratio``, ``ngram_ve_bir_count``…); bu durumda ``formula`` ve ``requires``
        grup düzeyindeki genel ifadedir.
    lang : str, optional
        ``"tr"`` ya da ``"en"``. Yalnız ``definitions``'ı etkiler: dile göre değişen
        terimlerin (``syllable``) tek dilli kaydını seçer.

    Returns
    -------
    dict
        ``key``, ``group``, ``group_label``, ``description``, ``formula``,
        ``scale``, ``inputs``, ``params``, ``requires``, ``citation``,
        ``references``, ``definitions``.
        ``definitions`` = ``{terim: {"name", "source", "description"}}``: formülün
        kullandığı terimlerin (``sentence``, ``word``, ``syllable``…) tlf'deki tanımı,
        kuralı kimin koyduğu (``tlf``, ``spacy``, ``zeyrek``, ``textstat``,
        ``wordfreq``) ve tek cümleyle nasıl hesaplandığı. Formülde olmayan terim sözlükte
        yoktur. Dile göre değişen terimde (``syllable``) ``lang`` verilirse o dilin kaydı, verilmezse
        ``{"tr": kayıt, "en": kayıt}`` döner; yalnız tek dilde üretilen öznitelikte
        (``atesman`` yalnız Türkçe, ``flesch_reading_ease`` yalnız İngilizce) o dilin kaydı. Adların anlamı
        ``_registry_definition_texts.py``'de.
        ``citation`` kısa işaretçidir, ``references`` ise onda adı geçen
        eserlerin tam bibliyografik kayıtları — yöntem bölümüne kopyalanacak
        olan budur.

        ``citation`` ``None`` ise o anahtar adlandırılmış bir literatür
        ölçüsü değildir, saf tanımdır (``punct_variety``, ``lemma_count``). Dış
        bir etiket şemasının kategorisini sayan anahtarların künyesi
        ``None`` değildir, şemayı gösterir (``case_loc_ratio`` → UD;
        ``zeyrek_case_loc_ratio`` → Zeyrek).

    Raises
    ------
    KeyError
        Anahtar hiçbir gruba ait değilse.

    Examples
    --------
    >>> describe_feature("mattr")["formula"]
    'mean TTR of every sliding window of mattr_window words'
    >>> describe_feature("mattr")["requires"]
    'at least 100 words (2 x mattr_window)'
    >>> describe_feature("lemma_count")["citation"] is None
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
        "references": _references(_citation(key)),
        "definitions": definitions_of(key, grup, lang),
    }
