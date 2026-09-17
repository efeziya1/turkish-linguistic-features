"""T13 — okunabilirlik. Sayım kuralları kaynaklara göre (2026-09-17, Efe).

Testler spaCy modeli gerektirmez: ``surface_tokens`` boş dil nesnesinin
tokenizer'ından gelir; kısaltma kuralları modelle aynıdır.
"""

import math

import pytest
import spacy

from turkish_linguistic_features.features.phonetic import hece_say
from turkish_linguistic_features.features.readability import (
    birim_hecesi,
    cumle_sayisi,
    english_readability_formulas,
    general_readability_formulas,
    kelime_birimleri,
    turkish_readability_formulas,
)

_NLP = {lang: spacy.blank(lang) for lang in ("tr", "en")}


def _tok(metin: str, lang: str) -> list[str]:
    return [t.text for t in _NLP[lang](metin) if not t.is_space]


def _nan(x: float) -> bool:
    return isinstance(x, float) and math.isnan(x)


# ── kelime birimi ─────────────────────────────────────────────────────


def test_kelime_bosluk_arasi_birim_kenar_noktalama_atilir():
    """Flesch 1948, Kincaid 1975, Kalyoncu 2025: iki boşluk arası."""
    kelimeler, semboller = kelime_birimleri('"Ali," dedi (kısaca) - evet.', "tr")
    assert kelimeler == ["Ali", "dedi", "kısaca", "evet"]
    assert semboller == []


def test_kisaltmali_ve_tireli_bicim_tek_kelime():
    """Kincaid: couldn't, second-grade, 32,008 birer kelime."""
    kelimeler, _ = kelime_birimleri("I couldn't pay 32,008 for second-grade F.O.B. goods.", "en")
    assert kelimeler == ["I", "couldn't", "pay", "32,008", "for", "second-grade", "F.O.B", "goods"]


def test_tek_basina_sembol_ayri_tutulur():
    kelimeler, semboller = kelime_birimleri("Fiyat % 50 ve $ ile # işareti", "tr")
    assert kelimeler == ["Fiyat", "50", "ve", "ile", "işareti"]
    assert semboller == ["%", "$"]           # # listede yok, sayılmaz


# ── birim hecesi ──────────────────────────────────────────────────────


def test_tireli_kelime_parcalarin_toplami():
    assert birim_hecesi("Türk-İslam", "tr") == 3
    assert birim_hecesi("well-known", "en") == 2


def test_sembollu_birim_okunusuyla():
    assert birim_hecesi("%50", "tr") == 4        # yüz-de el-li
    assert birim_hecesi("50%", "en") == 4        # fif-ty per-cent
    assert birim_hecesi("$", "en") == 2          # dol-lars
    assert birim_hecesi("¢", "en") == 1          # Kincaid: "¢ (cent) 1 syllable"


def test_noktali_bas_harfler_harf_harf():
    assert birim_hecesi("F.O.B", "en") == 3
    assert birim_hecesi("A.Ş", "tr") == 2
    assert birim_hecesi("W.H.O", "en") == 5      # double-u


def test_kisaltmali_bicim_ingilizce():
    assert birim_hecesi("couldn't", "en") == hece_say("couldnt", "en")


def test_hecelenemeyen_birim():
    assert birim_hecesi("3G", "tr") is None


# ── cümle sayısı ──────────────────────────────────────────────────────


def test_cumle_nokta_soru_unlem():
    """McLaughlin 1969: . ? ! ile biten dizi."""
    tok = _tok("Geldi mi? Evet! Gitti. Son", "tr")
    assert cumle_sayisi(tok, ".?!", "tr") == 4        # işaretsiz son +1


def test_ardisik_isaretler_tek_sinir():
    """?!, ... ve ." birer sınır."""
    tok = _tok('Ne?! Gitti... Bitti."', "tr")
    assert cumle_sayisi(tok, ".?!", "tr") == 3


def test_noktali_virgul_ve_iki_nokta_formule_gore():
    """Kincaid'in Flesch talimatı: ; ve : genellikle bağımsız cümle bitirir."""
    tok = _tok("They won; we lost: badly.", "en")
    assert cumle_sayisi(tok, ".?!", "en") == 1
    assert cumle_sayisi(tok, ".?!;:", "en") == 3      # fonksiyon işaret kümesini olduğu gibi uygular


def test_kisaltma_noktasi_cumle_bitirmez():
    assert cumle_sayisi(_tok("Dr. Smith paid on Jan. 3. Then left.", "en"), ".?!", "en") == 2
    # spaCy TR "bkz." kısaltmasını böler; ardından küçük harf geliyorsa sınır değil
    assert cumle_sayisi(_tok("Tabloya bkz. ekte var. Sonra bitti.", "tr"), ".?!", "tr") == 2


def test_bos_metin_sifir_cumle():
    assert cumle_sayisi([], ".?!", "tr") == 0


# ── K12: Kalyoncu & Memiş (2024) Metin 2 ─────────────────────────────

# Ana Dili Eğitimi Dergisi 12(2), 414-436, Ek-1.
# 100 kelime · 4 cümle · 275 hece · H3=7.75 · H4=4.25 · H5=1.25 · H6=0.75
METIN2 = (
    "Atatürk, okul programlarıyla bizzat meşgul olur, okutulan kitapları "
    "gözden geçirir ve özellikle tarih derslerinin, ulusun bilincini "
    "yükselteceğine inanır ve Türklük dünyasının tarihini bir bütün olarak, "
    "uygarlık unsurlarına daha çok önem verilerek incelenmesini ve "
    "okutulmasını isterdi. O, Türk büyüklerinden Alparslanlar, Fatihler, "
    "Yavuz ve Kanunilerin hayranı olmakla beraber, bizzat uygarlık eserleri "
    "vücuda getirmiş olan Mimar Sinanlar ve Piri Reislere de ayrı bir değer "
    "verirdi. Çünkü devlet başında ordular yönetmiş kişiler, tarihte Türk "
    "şanını ne kadar yükseltmişlerse diğerleri de Türk dünyasına ölmez "
    "eserler vermişlerdir. Atatürk, her devirde Türk'ün uygarlık yapısına "
    "hizmet eden her bireyin değerini takdir etmenin zorunlu olduğunu "
    "prensip olarak kabul etmişti."
)


def test_metin2_sayilari_makaleyle_ayni():
    kelimeler, _ = kelime_birimleri(METIN2, "tr")
    assert len(kelimeler) == 100
    assert sum(birim_hecesi(k, "tr") for k in kelimeler) == 275
    assert cumle_sayisi(_tok(METIN2, "tr"), ".?!", "tr") == 4


def test_turkce_formuller_metin2():
    """Makale Tablo 9: Ateşman 23,094 · Çetinkaya 23,084. Bezirci-Yılmaz'da makale
    30,4231 (H6'yı 26,35 diye yanlış aktarmış); birincil katsayı 26.25 ile 30.3922."""
    sonuc = turkish_readability_formulas(METIN2, _tok(METIN2, "tr"))
    assert set(sonuc) == {"atesman", "cetinkaya_uzun", "bezirci_yilmaz"}
    assert sonuc["atesman"] == pytest.approx(23.094, abs=0.01)
    assert sonuc["cetinkaya_uzun"] == pytest.approx(23.084, abs=0.01)
    assert sonuc["bezirci_yilmaz"] == pytest.approx(30.3922, abs=0.01)


def test_bezirci_yilmaz_katsayilari():
    """Bezirci & Yılmaz 2010 s.370: EKOK 21000'den türetilmiş katsayılar.
    Tek kelimelik tek cümle: OKS = 1, puan = √katsayı."""
    for kelime, katsayi in [
        ("kitaplar", 0.84), ("kitaplarım", 1.50),
        ("kitaplarımız", 3.50), ("kitaplarımızda", 26.25), ("kitap", 0.0),
    ]:
        metin = kelime + "."
        sonuc = turkish_readability_formulas(metin, _tok(metin, "tr"))
        assert sonuc["bezirci_yilmaz"] == pytest.approx(math.sqrt(katsayi), abs=1e-4), kelime


def test_bezirci_yilmaz_formul_sekli():
    """Makalenin Tablo 5'i: puan = √(OKS · braket), dokuz hücrenin dokuzu."""
    for oks, braket, beklenen in [
        (7, 3.03, 4.61), (10, 3.03, 5.50), (14, 3.03, 6.51),
        (7, 8.30, 7.62), (10, 8.30, 9.11), (14, 8.30, 10.78),
        (7, 18.82, 11.48), (10, 18.82, 13.72), (14, 18.82, 16.23),
    ]:
        assert math.sqrt(oks * braket) == pytest.approx(beklenen, abs=0.005)


def test_cetinkaya_sembolu_ve_iki_noktayi_sayar_atesman_saymaz():
    """Çetinkaya protokolü sembolü kelime, iki noktayı cümle sonu sayar."""
    metin = "Sonuç: fiyat % elli arttı."
    sonuc = turkish_readability_formulas(metin, _tok(metin, "tr"))
    # Ateşman: 4 kelime (so-nuç fi-yat el-li art-tı), 1 cümle, 8 hece
    assert sonuc["atesman"] == pytest.approx(198.825 - 40.175 * 8 / 4 - 2.610 * 4, abs=1e-3)
    # Çetinkaya: 5 kelime (+ %), 2 cümle, 10 hece (+ yüz-de)
    assert sonuc["cetinkaya_uzun"] == pytest.approx(118.823 - 25.987 * 10 / 5 - 0.971 * 5 / 2, abs=1e-3)


@pytest.mark.parametrize("metin, cumle", [
    ("Ali geldi (dün akşam) ve oturdu.", 3),
    ("Ali geldi (dün akşam).", 2),
    ("Ali geldi. (Dün akşamdı.)", 2),
])
def test_cetinkaya_parantez_ici_ayri_cumle(metin, cumle):
    """Çetinkaya (2010, s.93): "iki parantez ( ) bitirilmiş bir tümce" — açılan ve
    kapanan parantez sınır (2026-09-17, Efe). Ateşman parantezi saymaz."""
    sonuc = turkish_readability_formulas(metin, _tok(metin, "tr"))
    kelimeler = kelime_birimleri(metin, "tr")[0]
    hece = sum(birim_hecesi(k, "tr") for k in kelimeler)
    n = len(kelimeler)
    assert sonuc["cetinkaya_uzun"] == pytest.approx(
        118.823 - 25.987 * hece / n - 0.971 * n / cumle, abs=1e-3)
    ates_cumle = cumle_sayisi(_tok(metin, "tr"), ".?!", "tr")
    assert sonuc["atesman"] == pytest.approx(
        198.825 - 40.175 * hece / n - 2.610 * n / ates_cumle, abs=1e-3)


def test_cetinkaya_unlem_cumle_sonu():
    """Ünlem yönergenin listesinde yok ama "bağımsız birim" ölçütüne girer."""
    metin = "Ne güzel! Geldik."
    sonuc = turkish_readability_formulas(metin, _tok(metin, "tr"))
    assert sonuc["cetinkaya_uzun"] == pytest.approx(118.823 - 25.987 * 5 / 3 - 0.971 * 3 / 2, abs=1e-3)


# ── İngilizce formüller ───────────────────────────────────────────────


def test_flesch_ve_fkgl_kincaid_sayimi():
    """Kelime: sembol dahil; cümle: . ? ! ; (Kincaid ve ark. 1975; iki nokta
    yargı gerektirdiği için cümle sonu sayılmaz — 2026-09-17, Efe)."""
    metin = "The cat ate a banana; the dog ate $ 5."
    sonuc = english_readability_formulas(metin, _tok(metin, "en"))
    kelime, cumle = 10, 2
    hece = sum(hece_say(k, "en") for k in "The cat ate a banana the dog ate".split()) + 2 + 1
    assert sonuc["flesch_reading_ease"] == pytest.approx(
        206.835 - 1.015 * kelime / cumle - 84.6 * hece / kelime, abs=1e-3)
    assert sonuc["flesch_kincaid_grade"] == pytest.approx(
        0.39 * kelime / cumle + 11.8 * hece / kelime - 15.59, abs=1e-3)


def test_flesch_iki_noktayi_cumle_sonu_saymaz():
    metin = "They won: we lost."
    sonuc = english_readability_formulas(metin, _tok(metin, "en"))
    hece = sum(hece_say(k, "en") for k in "They won we lost".split())
    assert sonuc["flesch_reading_ease"] == pytest.approx(
        206.835 - 1.015 * 4 / 1 - 84.6 * hece / 4, abs=1e-3)


def test_smog_30_cumleden_kisada_nan():
    metin = "Comprehension matters. " * 29
    assert _nan(english_readability_formulas(metin, _tok(metin, "en"))["smog"])


def test_smog_mclaughlin_denklem_d():
    """30 cümlede 30 çok heceli kelime → 3.1291 + 1.0430·√30."""
    metin = "Comprehension matters. " * 30
    assert english_readability_formulas(metin, _tok(metin, "en"))["smog"] == pytest.approx(
        3.1291 + 1.0430 * math.sqrt(30), abs=1e-3)


def test_smog_30_cumleye_olceklenir():
    metin = "Comprehension matters. " * 30 + "The cat sat. " * 30
    assert english_readability_formulas(metin, _tok(metin, "en"))["smog"] == pytest.approx(
        3.1291 + 1.0430 * math.sqrt(15), abs=1e-3)


def test_cok_heceli_kelime_orani():
    metin = "A beautiful cat and a banana."
    sonuc = english_readability_formulas(metin, _tok(metin, "en"))
    assert sonuc["polysyllabic_word_ratio"] == pytest.approx(2 / 6, abs=1e-4)


# ── iki dilde ────────────────────────────────────────────────────────


def test_ari_vurus_bosluk_disi_her_karakter():
    """Kincaid s.33: harf + sembol + noktalama; kelime = boşluk tuşu."""
    metin = "Ali, kitabı okudu."
    sonuc = general_readability_formulas(metin, _tok(metin, "tr"), "tr")
    assert sonuc["ari"] == pytest.approx(4.71 * 16 / 3 + 0.5 * 3 / 1 - 21.43, abs=1e-3)


def test_ari_sembolu_kelime_sayar():
    metin = "Fiyat % arttı."
    sonuc = general_readability_formulas(metin, _tok(metin, "tr"), "tr")
    assert sonuc["ari"] == pytest.approx(4.71 * 12 / 3 + 0.5 * 3 / 1 - 21.43, abs=1e-3)


def test_coleman_liau_yalniz_harf():
    metin = "Ali, kitabı okudu."
    sonuc = general_readability_formulas(metin, _tok(metin, "tr"), "tr")
    L, S = 100 * 14 / 3, 100 * 1 / 3
    assert sonuc["coleman_liau"] == pytest.approx(0.0588 * L - 0.296 * S - 15.8, abs=1e-3)


def test_coleman_liau_iki_denklemin_birlesimi():
    """Makalenin iki denklemi (cloze % → sınıf) birleşince CLI formülünü verir."""
    cloze = (141.8401 - 0.214590 * 300 + 1.079812 * 10) / 100
    sinif = -27.4004 * cloze + 23.06395
    assert sinif == pytest.approx(0.0588 * 300 - 0.296 * 10 - 15.8, abs=0.01)


def test_lix_ve_uzun_kelime():
    """Anderson 1983: uzun kelime = yedi veya daha fazla harf."""
    metin = "Uzunkelime kısa. A b c."
    sonuc = general_readability_formulas(metin, _tok(metin, "tr"), "tr")
    assert sonuc["lix"] == pytest.approx(5 / 2 + 100 * 1 / 5)
    assert sonuc["long_word_ratio"] == pytest.approx(1 / 5)


def test_uzun_kelime_esigi_ve_harf_sayimi():
    metin = "kalemi kitapçı Türk'ün"                  # 6 · 7 · 6 harf
    sonuc = general_readability_formulas(metin, _tok(metin, "tr"), "tr")
    assert sonuc["long_word_ratio"] == pytest.approx(1 / 3, abs=1e-4)


# ── boş girdi (K4) ────────────────────────────────────────────────────


def test_bos_metinde_hepsi_nan():
    for sonuc in (turkish_readability_formulas("", []),
                  english_readability_formulas("", []),
                  general_readability_formulas("", [], "tr")):
        assert all(_nan(v) for v in sonuc.values())


def test_yalniz_noktalama_nan():
    sonuc = general_readability_formulas("...", ["..."], "tr")
    assert all(_nan(v) for v in sonuc.values())
