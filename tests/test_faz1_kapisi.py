"""Faz 1 kapısı: her öznitelik fonksiyonu boş ve tek elemanlı girdide çökmez.

Değerler ya sonlu ya NaN'dır (K4); sonsuz ya da istisna yoktur. "Bilinen değer"
testleri her modülün kendi test dosyasında. Yeni bir public fonksiyon
eklenirse ``DURUMLAR`` tablosuna da eklenmeli — ``test_tablo_eksiksiz`` bunu denetler.
"""

import importlib
import inspect
import math

import numpy as np
import pytest

MODULLER = ("dependency", "frequency_structure", "lexical", "morphological",
            "phonetic", "punctuation", "readability", "syntactic")

BOS = np.array([], dtype=float)
BIR = np.array([1.0])
POS_EV = [("ev", "NOUN")]
ZEYREK_EV = [[("Noun", "ev", False), ("A3sg", "", False)]]

# ad: (boş girdi, tek elemanlı girdi)
DURUMLAR: dict[str, tuple[tuple, tuple]] = {
    "dependency.dependency_features": (((),), ((((0, "VERB", "root", 0),),),)),
    "frequency_structure.adjusted_modulus": ((0, 0, 0.0, 0), (1, 1, 1.0, 1)),
    "frequency_structure.curve_length": ((BOS,), (BIR,)),
    "frequency_structure.curve_length_indicator": ((BOS, 0.0), (BIR, 1.0)),
    "frequency_structure.gini_coef": ((BOS, 0, 0), (BIR, 1, 1)),
    "frequency_structure.h_point": ((BOS,), (BIR,)),
    "frequency_structure.lambda_pa": ((0.0, 0), (0.0, 1)),
    "frequency_structure.repeat_rate": ((BOS, 0), (BIR, 1)),
    "frequency_structure.rr_mcintosh": ((math.nan, 0), (1.0, 1)),
    "frequency_structure.secondary_thematic_concentration": (([], [], 0.0), ([("ev", 1)], POS_EV, 1.0)),
    "frequency_structure.thematic_concentration": (([], [], 0.0), ([("ev", 1)], POS_EV, 1.0)),
    "frequency_structure.vocab_richness_r1": ((BOS, 0, 0.0), (BIR, 1, 1.0)),
    "frequency_structure.vocab_richness_r4": ((BOS, 0, 0), (BIR, 1, 1)),
    "frequency_structure.writers_view": ((0, 0, 0.0), (1, 1, 1.0)),
    "lexical.advanced_lexical_richness": (([],), (["ev"],)),
    "lexical.brunet_w": ((0, 0), (1, 1)),
    "lexical.dugast_u": (([],), (["ev"],)),
    "lexical.guiraud_r": (([],), (["ev"],)),
    "lexical.hapax_count": (([],), (["ev"],)),
    "lexical.hapax_ratio": (([],), (["ev"],)),
    "lexical.hdd": (([],), (["ev"],)),
    "lexical.heaps_beta": (([],), (["ev"],)),
    "lexical.msttr": (([],), (["ev"],)),
    "lexical.mtld": (([],), (["ev"],)),
    "lexical.pos_lexical_variation": (([], []), (["ev"], POS_EV)),
    "lexical.rank_word_freq_table": (([],), (["ev"],)),
    "lexical.rare_word_metrics": (([],), (["ev"],)),
    "lexical.reference_frequency_sophistication": (([], []), (["ev"], POS_EV)),
    "lexical.shannon_entropy": ((BOS,), (BIR,)),
    "lexical.simpsons_d": ((BOS,), (BIR,)),
    "lexical.ttr_moving_slope": (([],), (["ev"],)),
    "lexical.type_token_ratio": ((0, 0), (1, 1)),
    "lexical.vocd_d": (([],), (["ev"],)),
    "lexical.word_length_stats": (([],), (["ev"],)),
    "lexical.yules_k": ((BOS,), (BIR,)),
    "lexical.zipf": ((BOS,), (BIR,)),
    "lexical.zipf_mandelbrot": ((BOS,), (BIR,)),
    "morphological.spacy_morph_ratios": (([], []), ([("ev", "Case=Nom")], POS_EV)),
    "morphological.surface_per_lemma": (([], [], []), (["ev"], POS_EV, ["ev"])),
    "phonetic.hece_say": (("",), ("ev",)),
    "phonetic.sentence_syllable_stats": (([],), ([["ev"]],)),
    "phonetic.syllable_count_stats": (([],), (["ev"],)),
    "phonetic.syllable_length_distribution": (([],), (["ev"],)),
    "phonetic.toplam_hece": (([],), (["ev"],)),
    "phonetic.vowel_harmony_compliance": (([],), (["ev"],)),
    "phonetic.vowel_ratios": (("",), ("ev",)),
    "punctuation.all_caps_word_ratio": (([],), (["EV"],)),
    "punctuation.char_freq_vector": (("", "tr"), ("e", "tr")),
    "punctuation.consecutive_punct_ratio": (("",), (".",)),
    "punctuation.digit_ratio": (("",), ("1",)),
    "punctuation.punct_density": (("",), (".",)),
    "punctuation.punct_entropy": (("",), (".",)),
    "punctuation.punct_variety": (("",), (".",)),
    "punctuation.punctuation_ratios": (("", 0), ("ev.", 1)),
    "punctuation.uppercase_ratio": (([],), (["Ev"],)),
    "punctuation.whitespace_ratio": (("",), (" ",)),
    "readability.birim_hecesi": (("", "tr"), ("ev", "tr")),
    "readability.cumle_sayisi": (([], ".?!", "tr"), (["ev"], ".?!", "tr")),
    "readability.english_readability_formulas": (("", []), ("Home.", ["Home", "."])),
    "readability.general_readability_formulas": (("", [], "tr"), ("Ev.", ["Ev", "."], "tr")),
    "readability.kelime_birimleri": (("", "tr"), ("ev", "tr")),
    "readability.turkish_readability_formulas": (("", []), ("Ev.", ["Ev", "."])),
    "syntactic.activity_ratio": (([],), (POS_EV,)),
    "syntactic.avg_sent_len_char": (([],), ([["ev"]],)),
    "syntactic.lexical_density": (([],), (POS_EV,)),
    "syntactic.nominal_verbal_ratio": (([],), (POS_EV,)),
    "syntactic.paragraph_stats": (("",), ("ev",)),
    "syntactic.pos_bigram_ratios": (([],), (POS_EV,)),
    "syntactic.pos_distribution_stats": (([], []), (POS_EV, [["ev"]])),
    "syntactic.pos_ratios": (([],), (POS_EV,)),
    "syntactic.pronoun_freq": (([],), (POS_EV,)),
    "syntactic.question_per_sent": (([],), ([["ev"]],)),
    "syntactic.sent_len_entropy": (([],), ([["ev"]],)),
    "syntactic.sentence_distribution_stats": (([], 4, 18), ([["ev"]], 4, 18)),
    "syntactic.sentence_stats": (([],), ([["ev"]],)),
    "syntactic.verb_distance_stats": (([],), (POS_EV,)),
    "syntactic.word_ngram_ratios": (([], []), (["ev"], [["ev"]])),
}
for _ad in ("agglutination_depth", "case_suffix_ratios", "derivational_suffix_ratio",
            "modal_suffix_ratios", "mood_suffix_ratios", "negation_ratio", "passive_ratio",
            "plural_ratio", "question_particle_ratio", "suffix_char_length_ratio",
            "suffix_ngrams", "tense_ratios", "verb_suffix_diversity", "zeyrek_morfoloji"):
    DURUMLAR[f"morphological.{_ad}"] = (([], []), (ZEYREK_EV, POS_EV))


def _public_fonksiyonlar() -> dict[str, object]:
    sonuc = {}
    for m in MODULLER:
        mod = importlib.import_module(f"turkish_linguistic_features.features.{m}")
        for ad, f in inspect.getmembers(mod, inspect.isfunction):
            if f.__module__ == mod.__name__ and not ad.startswith("_"):
                sonuc[f"{m}.{ad}"] = f
    return sonuc


FONKSIYONLAR = _public_fonksiyonlar()


def _sayilar(deger: object) -> list[float]:
    """Sonuçtaki sayılar; dizi, liste ve metin atlanır."""
    if isinstance(deger, dict):
        return [x for v in deger.values() for x in _sayilar(v)]
    if isinstance(deger, tuple):
        return [x for v in deger for x in _sayilar(v)]
    if isinstance(deger, bool) or deger is None:
        return []
    if isinstance(deger, (int, float, np.integer, np.floating)):
        return [float(deger)]
    return []


def test_tablo_eksiksiz():
    assert set(FONKSIYONLAR) == set(DURUMLAR)


@pytest.mark.parametrize("ad", sorted(DURUMLAR))
@pytest.mark.parametrize("hal", ["bos", "tek"])
def test_bos_ve_tek_eleman_cokmez(ad, hal):
    girdi = DURUMLAR[ad][0 if hal == "bos" else 1]
    sonuc = FONKSIYONLAR[ad](*girdi)
    for x in _sayilar(sonuc):
        assert math.isnan(x) or math.isfinite(x), (ad, hal, sonuc)
