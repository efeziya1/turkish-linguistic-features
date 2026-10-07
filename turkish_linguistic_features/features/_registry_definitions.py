"""Formüldeki terimlerin tanımları: hangi öznitelik hangi terimi hangi kuralla sayıyor.

``describe_feature(key)["definitions"]`` bunu okur: formülün kullandığı her terim için
``{"name", "source", "description"}``. ``source`` kuralı kimin koyduğunu söyler (``tlf``,
``spacy``, ``zeyrek``, ``textstat``, ``wordfreq``), ``description`` tek cümleyle nasıl
hesaplandığını. Dile göre
değişen terimde (``syllable``) ``describe_feature(key, lang="tr")`` o dilin kaydını, ``lang``
verilmezse ``{"tr": ..., "en": ...}`` döndürür. Formülün kullanmadığı terim sözlükte yoktur.

Bu dosya yalnız **eşlemeyi** tutar (hangi öznitelik hangi tanım adını kullanıyor); her adın anlamı
ve kaynağı ``_registry_definition_texts.py``'de. Tablolar 2026-10-06'da koddan okunarak çıkarıldı.

Düzen: terim başına bir grup tablosu (grup varsayılanı, yoksa ``None``) ve yalnız ondan sapanlar
(``FEATURE_SCALES`` ile aynı düzen). ``None`` = bu özniteliğin formülünde o terim yok.

Terimler: ``sentence``, ``word``, ``type``, ``token``, ``syllable``, ``polysyllable``, ``letter``,
``character``, ``long_word``, ``paragraph``, ``mark``, ``noun``, ``verb``, ``lexical_word``,
``content_word``, ``suffix`` (tlf'nin kendi kuralı), ``pos_tag``, ``morph_feature``, ``dependency``,
``zipf_score``, ``zeyrek_tag`` (bir kütüphanenin çıktısı doğrudan kullanılır).
"""

from __future__ import annotations

from ._registry_definition_texts import DEFINITION_INFO

__all__ = ["TERMS", "TERM_VALUES", "LANGUAGE_NAMES", "PER_LANGUAGE", "ONLY_LANGUAGE",
           "SENTENCE_DEFINITIONS", "WORD_DEFINITIONS", "definitions_of",
           "GROUP_SENTENCE", "FEATURE_SENTENCE", "GROUP_WORD", "FEATURE_WORD"]

TERM_VALUES: dict[str, frozenset[str]] = {
    "sentence": frozenset({"default", "kincaid", "cetinkaya", "spacy_parser", "regex_paragraph"}),
    "word": frozenset({
        "space_unit", "space_unit_with_symbols", "pos_token", "zeyrek_analysed_word",
    }),
    "type": frozenset({"lowercase_surface", "spacy_lemma", "zeyrek_lemma"}),
    "token": frozenset({"spacy_token"}),
    "syllable": frozenset({"vowel_count", "textstat_cmudict"}),
    "polysyllable": frozenset({"3_plus_syllables"}),
    "letter": frozenset({"unicode_letter", "alphabet_letter", "zeyrek_surface_letter"}),
    "character": frozenset({
        "token_string_length", "non_space_character", "raw_character", "sentence_joined_character",
    }),
    "long_word": frozenset({"7_plus_letters"}),
    "paragraph": frozenset({"blank_line"}),
    "mark": frozenset({"ten_mark_types"}),
    "noun": frozenset({"noun_propn"}),
    "verb": frozenset({"verb_only", "zeyrek_final_type_verb"}),
    "lexical_word": frozenset({"noun_propn_verb_adj_adv"}),
    "content_word": frozenset({"noun_propn_verb_adj"}),
    "suffix": frozenset({"zeyrek_visible_suffix"}),
    "pos_tag": frozenset({"spacy_upos"}),
    "morph_feature": frozenset({"spacy_morph"}),
    "dependency": frozenset({"spacy_head"}),
    "zipf_score": frozenset({"wordfreq_zipf"}),
    "zeyrek_tag": frozenset({"zeyrek_tag"}),
}

# Dile göre değişen terimler: öznitelik tablosunda "per_language" yazar, ad buradan çözülür.
LANGUAGE_NAMES: dict[str, dict[str, str]] = {
    "syllable": {"tr": "vowel_count", "en": "textstat_cmudict"},
    # Türkçe lemma Zeyrek'ten, İngilizce spaCy'den (2026-10-07, Efe).
    "type": {"tr": "zeyrek_lemma", "en": "spacy_lemma"},
}
PER_LANGUAGE = "per_language"

# Yalnız tek dilde üretilen öznitelikler: dile göre değişen terim bu dilin kaydına iner (extractor'daki
# `turkish_readability_formulas` ve `english_readability_formulas` ayrımı).
ONLY_LANGUAGE: dict[str, str] = {
    **dict.fromkeys(("atesman", "bezirci_yilmaz", "cetinkaya_uzun"), "tr"),
    **dict.fromkeys(("flesch_reading_ease", "flesch_kincaid_grade", "smog",
                     "polysyllabic_word_ratio"), "en"),
}
SENTENCE_DEFINITIONS = TERM_VALUES["sentence"]
WORD_DEFINITIONS = TERM_VALUES["word"]

_PUNC_TURLER = (",", ".", ";", "!", ":", "-", "ellipsis", "paren", "quote", "question")
_PUNC = tuple(f"punc_{t}_ratio" for t in _PUNC_TURLER) + ("punc_total_ratio",)
_SYLLABLE_PHONETIC = (
    "syllable_mean", "syllable_1_ratio", "syllable_2_ratio", "syllable_3_ratio",
    "syllable_4_ratio", "syllable_5_ratio", "syllable_6plus_ratio",
    "sentence_syllable_mean",
)
_SYLLABLE_READABILITY = (
    "bezirci_yilmaz", "atesman", "cetinkaya_uzun", "flesch_reading_ease", "flesch_kincaid_grade",
    "smog", "polysyllabic_word_ratio",
)
_ZEYREK_VERB = (
    "verb_suffix_diversity", "tense_past_def", "tense_past_nar", "tense_present", "tense_future",
    "negation_ratio", "passive_ratio", "conditional_suffix_ratio", "causative_suffix_ratio",
    "modal_possibility_ratio", "modal_necessity_ratio",
)
_POS_TAG_KEYS = (
    "sentfinal_noun", "sentfinal_propn", "sentfinal_verb", "sentfinal_adj", "sentfinal_adv",
    "sentfinal_det", "sentfinal_adp", "sentfinal_intj", "sentfinal_cconj", "sentfinal_sconj",
    "sentfinal_num", "sentfinal_aux", "sentfinal_pron", "sentfinal_other",
    "pronoun_freq", "nominal_verbal_ratio", "verb_dist_mean", "verb_dist_cv", "activity_ratio",
    "lexical_density", "pos_dist_std", "pos_kl_div", "noun_variation", "verb_variation",
    "adj_variation", "adv_variation", "thematic_concentration",
    "secondary_thematic_concentration", "morph_voice_pass", "wordfreq_mean", "wordfreq_rare_ratio",
)
_ZEYREK_TAG_KEYS = (
    "tense_past_def", "tense_past_nar", "tense_present", "tense_future", "negation_ratio",
    "passive_ratio", "plural_ratio", "case_acc_ratio", "case_dat_ratio", "case_loc_ratio",
    "case_abl_ratio", "case_gen_ratio", "case_ins_ratio", "conditional_suffix_ratio",
    "causative_suffix_ratio", "modal_possibility_ratio", "modal_necessity_ratio",
    "question_particle_ratio", "verb_suffix_diversity", "suffix_bigram_entropy",
)
_ZEYREK_WORD = (
    "agglutination_depth", "suffix_char_length_ratio", "suffix_bigram_entropy",
    "derivational_suffix_ratio", "plural_ratio", "case_acc_ratio", "case_dat_ratio",
    "case_loc_ratio", "case_abl_ratio", "case_gen_ratio", "case_ins_ratio", "suffix_chain_cv",
    "question_particle_ratio",
)


def _hepsi(deger: str, anahtarlar: tuple[str, ...]) -> dict[str, str | None]:
    return dict.fromkeys(anahtarlar, deger)


# ── cümle ─────────────────────────────────────────────────────────────

GROUP_SENTENCE: dict[str, str | None] = {"sentence": "default", "syntactic_dep": "spacy_parser"}
FEATURE_SENTENCE: dict[str, str | None] = {
    "sents_per_para_mean": "regex_paragraph",
    "question_per_sent": "default", "pos_kl_div": "default",
    "sentence_syllable_mean": "default",
    "atesman": "default", "bezirci_yilmaz": "default", "cetinkaya_uzun": "cetinkaya",
    "flesch_reading_ease": "kincaid", "flesch_kincaid_grade": "kincaid", "smog": "default",
    "ari": "default", "coleman_liau": "default", "lix": "default",
}

# ── sözcük ────────────────────────────────────────────────────────────
# Tek sözcük tanımı `space_unit` (2026-10-07, Efe): etiket isteyen öznitelikler de onu sayar,
# etiket kelimenin ilk kelime tokenından gelir. Yalnız `syntactic_dep` `pos_token`ta kalır;
# Zeyrek öznitelikleri Zeyrek'in çözümleyebildiği kelimeleri sayar (`zeyrek_analysed_word`).

_LEMMA_POS_LEXICAL = ("n_lemma_count", "noun_variation", "verb_variation", "adj_variation",
                      "adv_variation", "wordfreq_mean", "wordfreq_rare_ratio")

GROUP_WORD: dict[str, str | None] = {
    "lexical": "space_unit", "frequency_structure": "space_unit", "sentence": "space_unit",
    "pos": "space_unit", "syntactic": "space_unit", "morphological": "space_unit",
    "syntactic_dep": "pos_token", "readability": "space_unit", "custom_ngrams": "space_unit",
}
FEATURE_WORD: dict[str, str | None] = {
    "avg_sent_len_char": None,
    **_hepsi("space_unit", ("para_len_mean", "para_count_norm",
                            "harmony_fronting_ratio", "harmony_rounding_ratio",
                            "uppercase_ratio", "all_caps_word_ratio")),
    **_hepsi("space_unit", _SYLLABLE_PHONETIC + _PUNC),
    **_hepsi("space_unit_with_symbols", ("cetinkaya_uzun", "flesch_reading_ease",
                                         "flesch_kincaid_grade", "ari")),
    **_hepsi("zeyrek_analysed_word", _ZEYREK_WORD),
    "question_per_sent": None,
}

# ── öteki terimler: (grup tablosu, öznitelik tablosu) ─────────────────

_TYPE_LEMMA = ("n_lemma_count", "noun_variation", "verb_variation", "adj_variation",
               "adv_variation", "wordfreq_mean", "wordfreq_rare_ratio", "surface_per_lemma")

TERMS: dict[str, tuple[dict[str, str | None], dict[str, str | None]]] = {
    "sentence": (GROUP_SENTENCE, FEATURE_SENTENCE),
    "word": (GROUP_WORD, FEATURE_WORD),
    "type": (
        {"lexical": "lowercase_surface", "frequency_structure": PER_LANGUAGE},
        {**_hepsi(PER_LANGUAGE, _TYPE_LEMMA), "avg_word_length": None},
    ),
    "token": ({}, {"avg_sent_len_char": "spacy_token"}),
    "syllable": ({}, _hepsi(PER_LANGUAGE, _SYLLABLE_PHONETIC + _SYLLABLE_READABILITY)),
    "polysyllable": ({}, _hepsi("3_plus_syllables", ("smog", "polysyllabic_word_ratio"))),
    "letter": (
        {"chars": "alphabet_letter"},
        {**_hepsi("alphabet_letter", ("vowel_ratio", "front_vowel_ratio", "back_vowel_ratio")),
         **_hepsi("unicode_letter", ("coleman_liau", "lix", "long_word_ratio", "uppercase_ratio",
                                     "all_caps_word_ratio")),
         "suffix_char_length_ratio": "zeyrek_surface_letter"},
    ),
    "character": ({}, {
        "avg_word_length": "token_string_length",
        "ari": "non_space_character",
        **_hepsi("raw_character", ("digit_vs_all", "punct_density", "whitespace_ratio")),
        "avg_sent_len_char": "sentence_joined_character",
    }),
    "long_word": ({}, _hepsi("7_plus_letters", ("lix", "long_word_ratio"))),
    "paragraph": ({}, _hepsi("blank_line", ("para_len_mean", "sents_per_para_mean",
                                            "para_count_norm"))),
    "mark": ({}, _hepsi("ten_mark_types", _PUNC + ("punct_density", "punct_entropy",
                                                   "consecutive_punct_ratio", "punct_variety"))),
    "noun": ({}, _hepsi("noun_propn", ("nominal_verbal_ratio", "noun_variation"))),
    "verb": ({}, {
        **_hepsi("verb_only", ("nominal_verbal_ratio", "verb_dist_mean", "verb_dist_cv",
                               "activity_ratio", "verb_variation", "morph_voice_pass")),
        **_hepsi("zeyrek_final_type_verb", _ZEYREK_VERB),
    }),
    "lexical_word": ({}, _hepsi("noun_propn_verb_adj_adv", (
        "lexical_density", "noun_variation", "adj_variation", "adv_variation",
        "wordfreq_mean", "wordfreq_rare_ratio"))),
    "content_word": ({}, _hepsi("noun_propn_verb_adj", ("thematic_concentration",
                                                        "secondary_thematic_concentration"))),
    "suffix": ({}, _hepsi("zeyrek_visible_suffix", (
        "agglutination_depth", "suffix_char_length_ratio", "suffix_bigram_entropy",
        "derivational_suffix_ratio", "verb_suffix_diversity", "suffix_chain_cv"))),
    "pos_tag": (
        {"pos": "spacy_upos"},
        _hepsi("spacy_upos", _POS_TAG_KEYS),
    ),
    "morph_feature": ({"morphological": "spacy_morph"}, {"surface_per_lemma": None}),
    "dependency": ({}, _hepsi("spacy_head", ("arc_len_mean", "parse_depth_mean"))),
    "zipf_score": ({}, _hepsi("wordfreq_zipf", ("wordfreq_mean", "wordfreq_rare_ratio"))),
    "zeyrek_tag": ({}, _hepsi("zeyrek_tag", _ZEYREK_TAG_KEYS)),
}


def _kayit(terim: str, ad: str) -> dict[str, object]:
    kaynak, aciklama = DEFINITION_INFO[(terim, ad)]
    return {"name": ad, "source": kaynak, "description": aciklama}


def definitions_of(key: str, grup: str, lang: str | None = None) -> dict[str, dict]:
    """Özniteliğin formülünün kullandığı terimler; her biri ``{name, source, description}``.

    Dile göre değişen terimde (``syllable``) ``lang`` verilmişse o dilin kaydı, verilmemişse
    ``{"tr": kayıt, "en": kayıt}`` döner; yalnız tek dilde üretilen öznitelikte (``ONLY_LANGUAGE``,
    ör. ``atesman``) o dilin kaydı. ``None`` olan terimler atılır.
    """
    if lang not in (None, "tr", "en"):
        raise ValueError(f"lang must be 'tr', 'en' or None, got {lang!r}")
    sonuc: dict[str, dict] = {}
    for terim, (grup_tablosu, ozellik_tablosu) in TERMS.items():
        ad = ozellik_tablosu[key] if key in ozellik_tablosu else grup_tablosu.get(grup)
        if ad is None:
            continue
        if ad == PER_LANGUAGE:
            diller = LANGUAGE_NAMES[terim]
            dil = lang if lang is not None else ONLY_LANGUAGE.get(key)
            sonuc[terim] = (_kayit(terim, diller[dil]) if dil is not None
                            else {d: _kayit(terim, a) for d, a in diller.items()})
        else:
            sonuc[terim] = _kayit(terim, ad)
    return sonuc
