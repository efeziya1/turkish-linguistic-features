from dataclasses import FrozenInstanceError

import pytest

from turkish_linguistic_features.params import (
    DEFAULT_PARAMS,
    SENT_THRESHOLDS_BY_LANG,
    FeatureParams,
    resolve_sent_thresholds,
)
from turkish_linguistic_features.pipeline.preprocess import ProcessedText


def test_params_degistirilemez():
    p = FeatureParams()
    with pytest.raises(FrozenInstanceError):
        p.mattr_window = 100


def test_params_yazim_hatasi_hemen_patlar():
    with pytest.raises(TypeError):
        FeatureParams(mattr_windwo=100)


def test_params_hashlenebilir():
    assert hash(FeatureParams()) == hash(FeatureParams())


def test_dil_varsayilanlari_farkli():
    """TR cümleleri EN'den kısa — eşikler de farklı olmalı."""
    assert resolve_sent_thresholds(DEFAULT_PARAMS, "tr") == (4, 18)
    assert resolve_sent_thresholds(DEFAULT_PARAMS, "en") == (7, 39)
    tr_uzun = resolve_sent_thresholds(DEFAULT_PARAMS, "tr")[1]
    en_uzun = resolve_sent_thresholds(DEFAULT_PARAMS, "en")[1]
    assert tr_uzun < en_uzun


def test_cumle_esigi_alan_varsayilani_yok():
    """5/30 diye bir varsayılan kalmadı — iki alan sentinel.

    Eskiden bu iki alan 5 ve 30 yazıyordu; hiçbir dilde kullanılmayan bu
    sayılar dokümanda "varsayılan" diye görünüyordu (2026-09-24, Efe).
    """
    assert FeatureParams().short_sent_threshold is None
    assert FeatureParams().long_sent_threshold is None


def test_ilgisiz_alan_kalibrasyonu_bozmaz():
    """`FeatureParams(mattr_window=100)` cümle eşiklerini düşürmemeli.

    B1 öncesi davranış: `params` nesnesi komple değiştiği için eşikler sınıf
    varsayılanı 5/30'a düşüyordu — kullanıcı istemediği hâlde, sessizce.
    """
    p = FeatureParams(mattr_window=100)
    assert resolve_sent_thresholds(p, "tr") == (4, 18)
    assert resolve_sent_thresholds(p, "en") == (7, 39)


def test_acik_verilen_esik_kalibrasyonu_yener():
    """Kullanıcı sayı verirse o sayı kazanır; vermediği alan kalibre kalır."""
    p = FeatureParams(long_sent_threshold=12)
    assert resolve_sent_thresholds(p, "tr") == (4, 12)      # kısa kalibre, uzun elle
    assert resolve_sent_thresholds(p, "en") == (7, 12)
    tam = FeatureParams(short_sent_threshold=3, long_sent_threshold=12)
    assert resolve_sent_thresholds(tam, "tr") == (3, 12)


def test_kalibre_esikler_tek_kaynaktan():
    """Eşikler tek sözlükte durur — iki yerde 4/18 tutulmaz."""
    assert SENT_THRESHOLDS_BY_LANG == {"tr": (4, 18), "en": (7, 39)}


def test_brunet_sabiti_parametre_olarak_gorunur():
    """Tartışmalı sabitler gizlenmez, `FeatureParams`'ta görünür.

    0.172 = Tweedie & Baayen (1998), Computers and the Humanities
    32(5):323-352, denklem (10). Bazı ikincil kaynaklar 0.165 veriyor;
    kullanıcı istediğine geçebilsin diye ayarlanabilir (K10).
    """
    assert DEFAULT_PARAMS.brunet_w_a == 0.172
    assert FeatureParams(brunet_w_a=0.165).brunet_w_a == 0.165


def test_bilinmeyen_dil_notr_yedege_duser():
    """`analyze()` dili tr/en ile sınırlıyor; yedek yine de patlamamalı."""
    assert resolve_sent_thresholds(DEFAULT_PARAMS, "de") == (5, 30)


def test_processed_text_to_dict_anahtarlari():
    pt = ProcessedText(
        raw_text="Merhaba dünya.",
        surface_tokens=("Merhaba", "dünya", "."),
        lemma_tokens=("merhaba", "dünya", "."),
        pos_data=(("Merhaba", "INTJ"), ("dünya", "NOUN"), (".", "PUNCT")),
        sentences_as_tokens=(("Merhaba", "dünya", "."),),
    )
    d = pt.to_dict()
    assert set(d) == {
        "raw_text", "surface_tokens", "lemma_tokens", "pos_data",
        "sentences_as_tokens", "morpheme_lists", "morph_tags", "lang", "dep_data",
    }
    assert isinstance(d["surface_tokens"], list)   # dışarıda liste
    assert d["dep_data"] is None
