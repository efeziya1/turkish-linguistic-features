import pytest

from turkish_linguistic_features.features.okunus import (
    SEMBOLLER,
    sayi_oku,
    sayi_oku_en,
    sembol_oku,
)
from turkish_linguistic_features.features.phonetic import hece_say

# ── Türkçe sayı ───────────────────────────────────────────────────────


def test_turkce_sayi_okunusu():
    assert sayi_oku("1916") == "bin dokuz yüz on altı"
    assert sayi_oku("12.500.000") == "on iki milyon beş yüz bin"
    assert sayi_oku("3,05") == "üç virgül sıfır beş"
    assert sayi_oku("3G") is None


# ── İngilizce sayı (2026-09-17, Efe) ──────────────────────────────────


@pytest.mark.cmudict            # İngilizce hece sayımı
def test_ingilizce_yil_ikiser_okunur():
    """Kincaid ve ark. (1975): "1918 (nineteen eighteen) 4 syllables"."""
    assert sayi_oku_en("1918") == "nineteen eighteen"
    assert sayi_oku_en("1905") == "nineteen oh five"
    assert sayi_oku_en("1900") == "nineteen hundred"
    assert sayi_oku_en("2024") == "twenty twenty four"
    assert hece_say("1918", "en") == 4


def test_ingilizce_2000lerin_ilk_on_yili_tam_sayi():
    assert sayi_oku_en("2005") == "two thousand five"
    assert sayi_oku_en("2000") == "two thousand"


def test_ingilizce_tam_sayi_abd_okunusu():
    """"and" yok (ABD okunuşu; Kincaid ABD Donanması raporu)."""
    assert sayi_oku_en("105") == "one hundred five"
    assert sayi_oku_en("32,008") == "thirty two thousand eight"
    assert sayi_oku_en("1000000") == "one million"
    assert sayi_oku_en("2500") == "two thousand five hundred"   # yıl aralığı dışında
    assert sayi_oku_en("0") == "zero"


def test_ingilizce_ondalik_ve_bastaki_sifir():
    assert sayi_oku_en("3.14") == "three point one four"
    assert sayi_oku_en("007") == "zero zero seven"


def test_ingilizce_okunamayanlar():
    for token in ("3G", "10:30", "1.000.000", "2.", "1" + "0" * 15):
        assert sayi_oku_en(token) is None, token


@pytest.mark.cmudict            # İngilizce hece sayımı
def test_ingilizce_sayi_hecesi():
    assert hece_say("105", "en") == 4              # one hun-dred five
    assert hece_say("3.5", "en") == 3              # three point five


# ── sembol okunuşu (2026-09-17, Efe) ──────────────────────────────────


def test_sembol_listesi_iki_dilde_ayni_semboller():
    assert set(SEMBOLLER["tr"]) == set(SEMBOLLER["en"])
    assert "#" not in SEMBOLLER["tr"]              # okunuşu belirsiz, listede yok


def test_sembol_okunusu():
    assert sembol_oku("%", "tr") == "yüzde"
    assert sembol_oku("%", "en") == "percent"
    assert sembol_oku("¢", "en") == "cents"         # Kincaid: "¢ (cent) 1 syllable"
    assert sembol_oku("#", "tr") is None
    assert sembol_oku("*", "en") is None
