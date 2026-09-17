import math

import pytest

from turkish_linguistic_features.features.dependency import dependency_features
from turkish_linguistic_features.features.params import FeatureParams

# Token: (sıra, POS, ilişki, baş sırası); kök kendini gösterir.

# Jing & Liu (2015) örneğinin yapısı: 7 kelime, MDD (1+1+1+1+1+2)/6 = 1.17,
# MHD (2+1+1+2+3+3)/6 = 2. Araya bir virgül, sona nokta eklendi — sayılmamalı.
JING_LIU = (
    (0, "NOUN", "nmod", 1),
    (1, "NOUN", "nsubj", 2),
    (2, "VERB", "root", 2),
    (3, "NOUN", "obl", 2),
    (4, "PUNCT", "punct", 2),
    (5, "NOUN", "nmod", 3),
    (6, "ADJ", "amod", 5),
    (7, "ADJ", "amod", 5),
    (8, "PUNCT", "punct", 2),
)

IKI_KELIME = ((0, "PROPN", "nsubj", 1), (1, "VERB", "root", 1), (2, "PUNCT", "punct", 1))
UC_KELIME = ((0, "NOUN", "obl", 2), (1, "NOUN", "obj", 2), (2, "VERB", "root", 2))


def test_16_anahtar():
    sonuc = dependency_features((IKI_KELIME,))
    assert len(sonuc) == 16
    assert {"arc_len_mean", "parse_depth_mean", "sentfinal_other"} <= set(sonuc)


def test_jing_liu_ornegi_noktalama_atilir():
    """Noktalama atılır ve sıralar yeniden sayılır: virgül 3–5 bağını uzatmaz."""
    sonuc = dependency_features((JING_LIU,))
    assert sonuc["arc_len_mean"] == pytest.approx(7 / 6, abs=1e-5)
    assert sonuc["parse_depth_mean"] == 2.0


def test_liu_2008_cumle_mdd():
    """Liu (2008) Şekil 1: mesafeler 1 1 1 2 → 5/4 = 1.25."""
    cumle = ((0, "DET", "det", 1), (1, "NOUN", "nsubj", 2), (2, "VERB", "root", 2),
             (3, "NOUN", "obj", 2), (4, "ADV", "advmod", 2))
    assert dependency_features((cumle,))["arc_len_mean"] == 1.25


def test_metin_ortalamasi_cumle_ortalamalarinin_ortalamasi():
    """MDD 1 ve 1.5 → 1.25 (Jing & Liu 2015, formül 3); havuzlu olsaydı 4/3."""
    assert dependency_features((IKI_KELIME, UC_KELIME))["arc_len_mean"] == 1.25


def test_tek_kelimelik_cumle_hesaba_girmez():
    tek = ((0, "VERB", "root", 0), (1, "PUNCT", "punct", 0))
    assert dependency_features((tek, IKI_KELIME))["arc_len_mean"] == 1.0
    sonuc = dependency_features((tek,))
    assert math.isnan(sonuc["arc_len_mean"]) and math.isnan(sonuc["parse_depth_mean"])


def test_derinlik_sinirli():
    zincir = tuple((i, "NOUN", "nmod", i + 1) for i in range(9)) + ((9, "VERB", "root", 9),)
    sonuc = dependency_features((zincir,), FeatureParams(max_parse_depth=3))
    assert sonuc["parse_depth_mean"] <= 3


def test_dongu_sonsuza_girmez():
    """İki token birbirini baş gösteriyor — takılmadan dönmeli."""
    bozuk = ((0, "NOUN", "dep", 1), (1, "NOUN", "dep", 0))
    assert dependency_features((bozuk,))["parse_depth_mean"] == 1.0


def test_cumle_sonu_noktalama_atlanir():
    sonuc = dependency_features((IKI_KELIME, UC_KELIME))
    assert sonuc["sentfinal_verb"] == 1.0
    assert sonuc["sentfinal_noun"] == 0.0


def test_cumle_sonu_diger_kovasi_toplam_bir():
    """PART 13 türde yok → sentfinal_other; 14 oranın toplamı 1."""
    soru = ((0, "VERB", "root", 0), (1, "PART", "discourse", 0), (2, "PUNCT", "punct", 0))
    sifat = ((0, "NOUN", "nsubj", 1), (1, "ADJ", "root", 1))
    sonuc = dependency_features((soru, sifat))
    assert sonuc["sentfinal_other"] == 0.5
    assert sonuc["sentfinal_adj"] == 0.5
    assert sum(v for k, v in sonuc.items() if k.startswith("sentfinal_")) == 1.0


def test_yalniz_noktalama_cumlesi_sayilmaz():
    nokta = ((0, "PUNCT", "punct", 0),)
    assert dependency_features((nokta, IKI_KELIME))["sentfinal_verb"] == 1.0


def test_bos_girdi():
    for girdi in ((), (((0, "PUNCT", "punct", 0),),)):
        sonuc = dependency_features(girdi)
        assert len(sonuc) == 16 and all(math.isnan(v) for v in sonuc.values())
