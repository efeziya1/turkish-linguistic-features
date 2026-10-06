import pytest

from turkish_linguistic_features.features.okunus import (
    SEMBOLLER,
    read_ordinal,
    read_time,
    sayi_oku,
    sayi_oku_en,
    sembol_oku,
)
from turkish_linguistic_features.features.phonetic import (
    _hece_sayilari,
    hece_say,
    syllable_count_stats,
    toplam_hece,
)

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


# ── Turkish ordinals, times, number + unit (2026-10-01, Efe) ──────────


@pytest.mark.parametrize("token,expected", [
    ("1.", "birinci"), ("2.", "ikinci"), ("3.", "üçüncü"), ("4.", "dördüncü"),
    ("6.", "altıncı"), ("9.", "dokuzuncu"), ("10.", "onuncu"), ("19.", "on dokuzuncu"),
    ("20.", "yirminci"), ("40.", "kırkıncı"), ("60.", "altmışıncı"), ("90.", "doksanıncı"),
    ("100.", "yüzüncü"), ("1000.", "bininci"), ("2000000.", "iki milyonuncu"),
])
def test_read_ordinal(token, expected):
    assert read_ordinal(token) == expected


def test_read_ordinal_rejects_other_forms():
    for token in ("3", "1.000", "3.5", ".", "a.", "3.."):
        assert read_ordinal(token) is None, token


@pytest.mark.parametrize("token,expected", [
    ("10:30", "on otuz"), ("10.30", "on otuz"), ("09:05", "dokuz sıfır beş"),
    ("14:00", "on dört"), ("0.15", "sıfır on beş"),
    ("3:2", "üç iki"), ("3:0", "üç sıfır"), ("1:100", "bir yüz"),
])
def test_read_time_and_score(token, expected):
    assert read_time(token) == expected


def test_read_time_rejects_other_forms():
    # dot form is a time only with hour <= 24 and two-digit minutes < 60
    for token in ("25.30", "10.75", "1.5", "10.300", "10:30:15", "10:", ":30"):
        assert read_time(token) is None, token


@pytest.mark.parametrize("token,expected", [
    ("3.", 3),          # ü-çün-cü
    ("2.", 3),          # i-kin-ci
    ("4.", 3),          # dör-dün-cü
    ("10:30", 3),       # on o-tuz
    ("10.30", 3),
    ("14:00", 2),       # on dört
    ("3:2", 3),         # üç i-ki
    ("3kg", 4),         # üç ki-lo-gram
    ("100m", 3),        # yüz met-re
    ("5g", 2),          # beş gram
    ("2l", 4),          # i-ki lit-re
    ("3G", 2),          # üç ge: capital letters are letter names
    ("100TL", 5),       # yüz Türk li-ra-sı
    ("2li", 3),         # i-ki-li
    ("5km'de", 6),      # beş ki-lo-met-re de
])
def test_turkish_syllables_of_new_forms(token, expected):
    assert hece_say(token, "tr") == expected


def test_single_letter_units_only_after_a_number():
    # on its own "m" may be metre or minute: not read (2026-10-01, Efe)
    assert hece_say("m", "tr") is None
    assert hece_say("3x", "tr") is None          # x is not a unit
    assert hece_say("4x4", "tr") is None


def test_ordinal_needs_a_following_word():
    """A number with a dot is an ordinal only when a word or a comma follows it."""
    assert toplam_hece(["3.", "kat"], "tr") == 4           # ü-çün-cü kat
    assert toplam_hece(["Sonuç", "3."], "tr") == 3          # so-nuç üç
    assert toplam_hece(["3.", "!"], "tr") == 1              # üç
    assert toplam_hece(["3.", ",", "4.", "ve"], "tr") == 7  # üçüncü, dördüncü ve


# ── listed symbols next to a number, syllable features (2026-10-01, Efe) ──


def test_symbol_reading_joins_the_adjacent_number():
    """spaCy splits "%50"; the symbol is not a word, its reading joins the number."""
    assert _hece_sayilari(["%", "50", "indirim"], "tr") == [4, 3]   # yüz-de el-li
    assert _hece_sayilari(["₺", "10"], "tr") == [3]                  # li-ra on
    assert _hece_sayilari(["25", "°"], "tr") == [6]                  # yir-mi beş de-re-ce


def test_symbol_between_two_numbers_is_counted_once():
    assert _hece_sayilari(["5", "+", "3"], "tr") == [1, 3]           # beş | ar-tı üç


def test_symbol_without_a_number_is_skipped():
    assert _hece_sayilari(["%", "oran"], "tr") == [2]
    # Hece öznitelikleri kelime birimi okur (2026-10-06): "%50" tek birim, yüz-de el-li.
    assert syllable_count_stats(["%50"], "tr")["syllable_mean"] == 4.0


@pytest.mark.cmudict            # English syllable counts
def test_symbol_reading_joins_the_adjacent_number_english():
    assert toplam_hece(["$", "5"], "en") == 3                        # dol-lars five
