import math

import pytest

from turkish_linguistic_features.features.phonetic import (
    _syllabify_tr,
    hece_say,
    sentence_syllable_stats,
    syllable_count_stats,
    syllable_length_distribution,
    toplam_hece,
    vowel_harmony_compliance,
    vowel_ratios,
)

# ── ünlü oranları ─────────────────────────────────────────────────────


def test_ince_kalin_unlu_orani():
    """'okul' → 4 harf, ince 0, kalın 2."""
    assert vowel_ratios("okul", "tr") == {
        "vowel_ratio": 0.5, "front_vowel_ratio": 0.0, "back_vowel_ratio": 0.5,
    }


def test_ince_ve_kalin_toplami_unlu_orani():
    sonuc = vowel_ratios("Kitaplığımızdaki gözlükler", "tr")
    assert sonuc["front_vowel_ratio"] + sonuc["back_vowel_ratio"] == pytest.approx(
        sonuc["vowel_ratio"], abs=1e-4)


def test_payda_yalniz_harfler():
    """Boşluk, rakam, noktalama paydaya girmez: 'ev, 12 ev!' → 4 harf, 2 ünlü."""
    assert vowel_ratios("ev, 12 ev!", "tr")["vowel_ratio"] == 0.5


def test_turkce_buyuk_harf_i():
    """'IŞIK' → ı, ı (kalın); Türkçe küçük harf kuralı I → ı."""
    sonuc = vowel_ratios("IŞIK", "tr")
    assert sonuc["back_vowel_ratio"] == 0.5
    assert sonuc["front_vowel_ratio"] == 0.0


def test_ingilizce_unluler_yaziya_gore():
    """'boat' → o, a kalın; 'see' → e, e ince; y ünsüz sayılır."""
    assert vowel_ratios("boat", "en")["back_vowel_ratio"] == 0.5
    assert vowel_ratios("see", "en")["front_vowel_ratio"] == pytest.approx(2 / 3, abs=1e-4)
    assert vowel_ratios("sky", "en")["vowel_ratio"] == 0.0


# ── ünlü uyumu ────────────────────────────────────────────────────────


def test_unlu_uyumu_uyumlu_kelime():
    """'okullar' → o, u, a hepsi kalın → uyumlu."""
    assert vowel_harmony_compliance(["okullar"])["vowel_harmony_compliance"] == 1.0


def test_unlu_uyumu_uyumsuz_kelime():
    """'televizyon' → e, i (ince) + o (kalın) → uyumsuz."""
    assert vowel_harmony_compliance(["televizyon"])["vowel_harmony_compliance"] == 0.0


def test_unlu_uyumu_kitap_alinti():
    """Plan örneği düzeltildi: 'kitaplar' → i (ince), a, a → uyumsuz."""
    assert vowel_harmony_compliance(["kitaplar"])["vowel_harmony_compliance"] == 0.0


def test_unlu_uyumu_duz_kural_yor_ekini_de_sayar():
    """Bilinen sınır (2026-09-16, Efe): 'geliyor' yerli ama e, i, o → uyumsuz."""
    assert vowel_harmony_compliance(["geliyor"])["vowel_harmony_compliance"] == 0.0


def test_unlu_uyumu_tek_unlulu_kelime_sayilmaz():
    """'ev' tek ünlü — uyum tanımsız, paydaya girmemeli."""
    sonuc = vowel_harmony_compliance(["ev", "okullar", "televizyon"])
    assert sonuc["vowel_harmony_compliance"] == 0.5


def test_unlu_uyumu_buyuk_harf_ve_kesme():
    """'IŞIKLI' → ı, ı, ı kalın; 'Ankara'da' → a, a, a, a kalın; noktalama yok sayılır."""
    sonuc = vowel_harmony_compliance(["IŞIKLI", "Ankara'da", ","])
    assert sonuc["vowel_harmony_compliance"] == 1.0


def test_unlu_uyumu_ingilizce():
    """'mountain' → o, u, a, i → karışık; 'garden' → a, e → karışık; 'about' → a, o, u kalın."""
    sonuc = vowel_harmony_compliance(["mountain", "garden", "about"], "en")
    assert sonuc["vowel_harmony_compliance"] == pytest.approx(1 / 3, abs=1e-4)


def _nan(x) -> bool:
    return isinstance(x, float) and math.isnan(x)


def test_unlu_uyumu_sayilacak_kelime_yoksa_nan():
    assert _nan(vowel_harmony_compliance(["!!!", "123", "ev"])["vowel_harmony_compliance"])


def test_bos_metin():
    assert all(_nan(v) for v in vowel_ratios("", "tr").values())
    assert all(_nan(v) for v in vowel_ratios("123 !", "tr").values())
    assert _nan(vowel_harmony_compliance([])["vowel_harmony_compliance"])


def test_bilinmeyen_dil():
    with pytest.raises(ValueError):
        vowel_ratios("ev", "de")


# ── T10: heceleme ─────────────────────────────────────────────────────


@pytest.mark.parametrize("kelime,beklenen", [
    ("kitap",          ["ki", "tap"]),
    ("kitaplarımızda", ["ki", "tap", "la", "rı", "mız", "da"]),
    ("ev",             ["ev"]),
    ("a",              ["a"]),
    ("türkçe",         ["türk", "çe"]),
    ("tren",           ["tren"]),
    ("saat",           ["sa", "at"]),
])
def test_heceleme(kelime, beklenen):
    assert _syllabify_tr(kelime) == beklenen


def test_heceleme_unlusuz_kelime():
    """Ünlü yoksa tek parça döner, sonsuz döngüye girmez."""
    assert _syllabify_tr("krş") == ["krş"]


def test_heceleme_tdk_bati_kokenli():
    """TDK (2019): "prog-ram, kont-rol"; kelime başı öbek ilk hecede kalır."""
    assert _syllabify_tr("program") == ["prog", "ram"]
    assert _syllabify_tr("kontrol") == ["kont", "rol"]
    assert _syllabify_tr("elektrik") == ["e", "lekt", "rik"]
    assert _syllabify_tr("strateji") == ["stra", "te", "ji"]


@pytest.mark.parametrize("kelime,beklenen", [
    ("başöğretmen",    ["ba", "şöğ", "ret", "men"]),
    ("ilkokul",        ["il", "ko", "kul"]),
    ("karaosmanoğlu",  ["ka", "ra", "os", "ma", "noğ", "lu"]),
    ("müdafaa",        ["mü", "da", "fa", "a"]),
    ("santral",        ["sant", "ral"]),
    ("sürpriz",        ["sürp", "riz"]),
    ("portre",         ["port", "re"]),
])
def test_heceleme_tdk_ornekleri(kelime, beklenen):
    """TDK, Hece Yapısı ve Satır Sonunda Kelimelerin Bölünmesi (2019) örnekleri."""
    assert _syllabify_tr(kelime) == beklenen


def test_heceleme_sapkali_unlu():
    assert _syllabify_tr("kâğıt") == ["kâ", "ğıt"]
    assert _syllabify_tr("millî") == ["mil", "lî"]


# ── T10: hece sayacı ──────────────────────────────────────────────────


def test_hece_say_turkce():
    assert hece_say("Kitaplarımızda", "tr") == 6
    assert hece_say("İSTANBUL", "tr") == 3          # büyük harf, Türkçe küçük harf kuralı
    assert hece_say("Ankara'da", "tr") == 4         # kesme işaretli ek kelimeye bitişik
    assert hece_say("kâğıt", "tr") == 2


def test_hece_say_buyuk_harf_unsuz_kisaltma():
    """TBMM → te-be-me-me: Türkçe harf adları tek heceli (2026-09-16, Efe)."""
    assert hece_say("TBMM", "tr") == 4
    assert hece_say("PTT", "tr") == 3


def test_hece_say_sayilamayan_tokenler():
    """Okunuşu çıkarılamayan biçimler, listede olmayan küçük harfli ünsüz
    tokenler ve noktalama hecelenmez."""
    for token in ("3G", "10:30", "4x4", "2.", "1.5", "xyz", "%", ".", "", "..."):
        assert hece_say(token, "tr") is None, token
    assert hece_say("3G", "en") is None


def test_hece_say_sayilar_okunusuyla():
    """Çetinkaya-Uzun protokolü: "1916: yedi hece" (Güven 2014) (2026-09-16, Efe)."""
    beklenen = {
        "1916": 7,          # bin do-kuz yüz on al-tı
        "0": 2,             # sı-fır
        "100": 1,           # yüz — "bir yüz" değil
        "1000": 1,          # bin — "bir bin" değil
        "101": 2,           # yüz bir
        "2001": 4,          # i-ki bin bir
        "1000000": 3,       # bir mil-yon
        "1.916": 7,         # binlik nokta
        "12.500.000": 8,    # on i-ki mil-yon beş yüz bin
        "3,5": 4,           # üç vir-gül beş
        "3,05": 6,          # üç vir-gül sı-fır beş
        "1916'da": 8,       # sayı + ek
        "0532": 6,          # başta sıfır → rakam rakam: sı-fır beş üç i-ki
    }
    for token, hece in beklenen.items():
        assert hece_say(token, "tr") == hece, token


def test_hece_say_cok_buyuk_sayi_okunmaz():
    assert hece_say("1" + "0" * 15, "tr") is None


def test_hece_say_kisaltmalar_acilir():
    """Sabit liste; büyük/küçük harf ve noktalar önemsiz (2026-09-16, Efe)."""
    beklenen = {
        "cm": 4, "CM": 4, "Kg": 3, "kg.": 3,        # san-ti-met-re · ki-lo-gram
        "km/s": 8, "m²": 4,                          # ki-lo-met-re bö-lü sa-at · met-re-ka-re
        "vb.": 4, "vs": 4, "bkz.": 3, "Dr.": 2,      # ve ben-ze-ri · ve-sa-i-re
        "T.C.": 8, "TL": 4, "ABD": 3,                # liste büyük harf kuralından önce gelir
        "M.Ö.": 5, "MÖ": 5, "mö": 5,                 # mi-lat-tan ön-ce
    }
    for token, hece in beklenen.items():
        assert hece_say(token, "tr") == hece, token


def test_hece_say_buyuk_kucuk_harf_ayrilan_kisaltmalar():
    """MS milattan sonra, ms milisaniye; Sn sayın, sn saniye (2026-09-16, Efe)."""
    assert hece_say("MS", "tr") == 5
    assert hece_say("M.S.", "tr") == 5
    assert hece_say("ms", "tr") == 5                # mi-li-sa-ni-ye
    assert hece_say("Sn.", "tr") == 2               # sa-yın
    assert hece_say("sn", "tr") == 3                # sa-ni-ye
    assert hece_say("SN", "tr") == 3


def test_hece_say_gercek_kelimeyle_ayni_kisaltma_acilmaz():
    """tel, sok, av, no gerçek kelime; listede yok (2026-09-16, Efe)."""
    assert hece_say("tel", "tr") == 1
    assert hece_say("sok", "tr") == 1


def test_hece_say_kesmeli_ek_kisaltmaya_eklenir():
    assert hece_say("TBMM'de", "tr") == 5
    assert hece_say("cm'lik", "tr") == 5


def test_hece_say_ingilizce_textstat():
    assert hece_say("make", "en") == 1              # sessiz e — ünlü öbeği sayımı 2 derdi
    assert hece_say("beautiful", "en") == 3


def test_hece_say_ingilizce_unlusuz_kelime():
    """textstat 0 verirse 1 sayılır (2026-09-16, Efe)."""
    assert hece_say("shh", "en") == 1


def test_toplam_hece_sayilamayanlari_atlar():
    assert toplam_hece(["Ali", "3G", "okula", ".", "gitti"], "tr") == 7


# ── T10: kelime başına hece ───────────────────────────────────────────


def test_hece_ortalamasi_ve_cv_elle():
    """ki-tap (2) + ev (1) → ortalama 1.5; std 0.5 → CV 1/3."""
    sonuc = syllable_count_stats(["kitap", "ev"], "tr")
    assert sonuc["syllable_mean"] == 1.5
    assert sonuc["syllable_cv"] == pytest.approx(1 / 3, abs=1e-4)


def test_hece_istatistigi_sayilamayanlari_atlar():
    assert syllable_count_stats(["xyz", "3G", "kitap", "masa"], "tr")["syllable_mean"] == 2.0


def test_hece_istatistigi_bos_ve_tek():
    assert all(_nan(v) for v in syllable_count_stats([], "tr").values())
    assert all(_nan(v) for v in syllable_count_stats(["3G", "."], "tr").values())
    sonuc = syllable_count_stats(["ev"], "tr")
    assert sonuc["syllable_mean"] == 1.0
    assert _nan(sonuc["syllable_cv"])               # tek değer


# ── T10: hece uzunluğu dağılımı ───────────────────────────────────────


def test_hece_dagilimi_toplami_bir():
    """Altı kova bir bölüşüm; round(x, 6) kovalara ayrı uygulandığı için tolerans 1e-5."""
    tokens = ["ev", "kitap", "kitaplar", "kitaplarım",
              "kitaplarımız", "kitaplarımızda", "kitaplarımızdakiler"]
    sonuc = syllable_length_distribution(tokens, "tr")
    assert abs(sum(sonuc.values()) - 1.0) < 1e-5


def test_hece_dagilimi_elle():
    sonuc = syllable_length_distribution(["ev", "kitap", "kitaplar", "kitaplarım", "."], "tr")
    assert sonuc == {
        "syllable_1_ratio": 0.25, "syllable_2_ratio": 0.25, "syllable_3_ratio": 0.25,
        "syllable_4_ratio": 0.25, "syllable_5_ratio": 0.0, "syllable_6plus_ratio": 0.0,
    }


def test_hece_dagilimi_6plus_ustten_toplar():
    sonuc = syllable_length_distribution(
        ["kitaplarımızda", "kitaplarımızdaki", "kitaplarımızdakiler"], "tr")
    assert sonuc["syllable_6plus_ratio"] == 1.0


def test_hece_dagilimi_bos_girdi():
    sonuc = syllable_length_distribution([], "tr")
    assert len(sonuc) == 6 and all(_nan(v) for v in sonuc.values())


# ── T10: cümle başına hece ────────────────────────────────────────────


def test_cumle_hecesi_elle():
    """7, 8, 13 hece → ortalama 9.3333; std 2.6247 → CV 0.2812. Noktalama sayılmaz."""
    cumleler = [["Ali", "okula", "gitti", "."],
                ["Öğretmen", "dersi", "anlattı", "."],
                ["Kitaplarımızdaki", "resimler", "güzeldi", "."]]
    sonuc = sentence_syllable_stats(cumleler, "tr")
    assert sonuc["sentence_syllable_mean"] == pytest.approx(28 / 3, abs=1e-4)
    assert sonuc["sentence_syllable_cv"] == pytest.approx(0.2812, abs=1e-4)


def test_cumle_hecesi_hecesiz_cumle_sayilmaz():
    """Yalnız rakam/noktalama içeren cümlenin hecesi ölçülemez, hesaba girmez."""
    sonuc = sentence_syllable_stats([["ev", "."], ["3G", "."], ["okul", "."]], "tr")
    assert sonuc["sentence_syllable_mean"] == 1.5


def test_cumle_hecesi_bos_ve_tek():
    assert all(_nan(v) for v in sentence_syllable_stats([], "tr").values())
    sonuc = sentence_syllable_stats([["kitap", "okudu"]], "tr")
    assert sonuc["sentence_syllable_mean"] == 5.0
    assert _nan(sonuc["sentence_syllable_cv"])
