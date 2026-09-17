import math
import re

import pytest

from turkish_linguistic_features.features.phonetic import toplam_hece
from turkish_linguistic_features.features.readability import (
    automated_readability_index,
    bezirci_yilmaz_score,
    coleman_liau_index,
    english_readability_formulas,
    lix_readability_index,
    long_word_ratio,
    polysyllabic_word_ratio,
    turkish_readability_formulas,
)


def _nan(x: float) -> bool:
    return isinstance(x, float) and math.isnan(x)


# ── ARI ve Coleman-Liau ───────────────────────────────────────────────


def test_ari_noktalamayi_vurus_sayar():
    """Kincaid ve ark. (1975) s.33 — noktalama vuruş sayılır (2026-09-16, Efe)."""
    yuzey = ["Ali", ",", "kitabı", "okudu", "."]
    kelimeler = ["Ali", "kitabı", "okudu"]
    sonuc = automated_readability_index(yuzey, kelimeler, 1)
    beklenen = 4.71 * (16 / 3) + 0.5 * (3 / 1) - 21.43   # 14 harf + 2 noktalama
    assert sonuc["ari"] == pytest.approx(beklenen, abs=1e-3)


def test_ari_uzun_cumlede_yuksek():
    kisa = automated_readability_index(["Git", ".", "Gel", ".", "Bak", "."], ["Git", "Gel", "Bak"], 3)
    uzun_cumle = ["kelime"] * 40
    uzun = automated_readability_index(uzun_cumle, uzun_cumle, 1)
    assert uzun["ari"] > kisa["ari"]


def test_coleman_liau_yalniz_harf_sayar():
    """Coleman & Liau (1975): L = 100 kelimedeki harf sayısı."""
    sonuc = coleman_liau_index(["Ali", "kitabı", "okudu"], 1)
    L, S = 100 * 14 / 3, 100 * 1 / 3
    assert sonuc["coleman_liau"] == pytest.approx(0.0588 * L - 0.296 * S - 15.8, abs=1e-3)


def test_coleman_liau_iki_denklemin_birlesimi():
    """Makalenin iki denklemi (cloze % → sınıf) birleşince CLI formülünü verir."""
    cloze = (141.8401 - 0.214590 * 300 + 1.079812 * 10) / 100
    sinif = -27.4004 * cloze + 23.06395
    assert sinif == pytest.approx(0.0588 * 300 - 0.296 * 10 - 15.8, abs=0.01)


# ── LIX ve uzun kelime ────────────────────────────────────────────────


def test_lix_elle():
    """5 kelime, 2 cümle, 1 uzun kelime → 2.5 + 100·(1/5) = 22.5"""
    sonuc = lix_readability_index(["uzunkelime", "kısa", "a", "b", "c"], 2)
    assert sonuc["lix"] == pytest.approx(22.5)


def test_uzun_kelime_orani_elle():
    """7 veya daha fazla harf: 'kelimeler' → 1 / 3"""
    sonuc = long_word_ratio(["kelimeler", "ev", "yol"])
    assert sonuc["long_word_ratio"] == pytest.approx(1 / 3, abs=1e-4)


def test_uzun_kelime_esigi_yedi_harf():
    """6 harf uzun değil, 7 harf uzun (Björnsson: "6 harften uzun")."""
    assert long_word_ratio(["kalemi", "kitapçı"])["long_word_ratio"] == 0.5


def test_uzun_kelime_yalniz_harf_sayar():
    """Kesme işareti harf değil: Türk'ün 6 harf."""
    assert long_word_ratio(["Türk'ün"])["long_word_ratio"] == 0.0


# ── İngilizce formüller ───────────────────────────────────────────────


def test_ingilizce_formuller_kaynak_katsayilari():
    """Kademe A katsayıları; hece T10'dan gelir, burada da oradan okunur."""
    kelimeler = ["The", "cat", "ate", "a", "banana"] * 2
    h = toplam_hece(kelimeler, "en") / 10
    sonuc = english_readability_formulas(kelimeler, 2, "en")
    assert set(sonuc) == {"flesch_reading_ease", "flesch_kincaid_grade", "smog"}
    assert sonuc["flesch_reading_ease"] == pytest.approx(206.835 - 1.015 * 5 - 84.6 * h, abs=1e-3)
    assert sonuc["flesch_kincaid_grade"] == pytest.approx(0.39 * 5 + 11.8 * h - 15.59, abs=1e-3)


def test_smog_30_cumleden_kisada_nan():
    """Kontrolü textstat yapmıyor, biz yapıyoruz (2026-09-16, Efe)."""
    kelimeler = ["comprehension"] * 30
    assert _nan(english_readability_formulas(kelimeler, 29, "en")["smog"])
    # 30 cümlede 30 çok heceli kelime → p = 30
    assert english_readability_formulas(kelimeler, 30, "en")["smog"] == pytest.approx(
        3.1291 + 1.0430 * math.sqrt(30), abs=1e-3)


def test_smog_30_cumleye_olceklenir():
    """60 cümlede 30 çok heceli kelime → 30 cümleye düşen p = 15."""
    kelimeler = ["comprehension"] * 30 + ["cat"] * 30
    assert english_readability_formulas(kelimeler, 60, "en")["smog"] == pytest.approx(
        3.1291 + 1.0430 * math.sqrt(15), abs=1e-3)


def test_ingilizce_formuller_bos_girdide_nan():
    assert all(_nan(v) for v in english_readability_formulas([], 0, "en").values())


def test_cok_heceli_kelime_orani():
    """SMOG'un tanımı: 3 veya daha fazla hece (beautiful 3, cat 1)."""
    sonuc = polysyllabic_word_ratio(["beautiful", "cat", "dog", "banana"], "en")
    assert sonuc["polysyllabic_word_ratio"] == 0.5


def test_cok_heceli_kelime_orani_hecelenemeyen_yoksa_nan():
    assert _nan(polysyllabic_word_ratio(["1990"], "en")["polysyllabic_word_ratio"])


# ── K12 bilinen değer testleri ────────────────────────────────────────


def _hazirla(ham: str) -> tuple[list[str], int]:
    """Ham metni (kelimeler, cümle sayısı) çiftine çevirir — spaCy YOK.

    Bilinen değer testleri spaCy modeline bağlı olmamalı: model sürümü
    değişince tokenizasyon değişir ve makaleden alınan değerler sessizce
    kayar. Cümle sınırı `.`/`!`/`?` sonrası boşluk. Kelime = harf dizisi
    (kesme işaretli birleşikler tek token: ``Türk'ün``).
    """
    cumleler = [c.strip() for c in re.split(r"(?<=[.!?])\s+", ham.strip()) if c.strip()]
    kelimeler = [w for c in cumleler for w in re.findall(r"[^\W\d_]+(?:['’][^\W\d_]+)?", c)]
    return kelimeler, len(cumleler)


# Kalyoncu & Memiş (2024), Ana Dili Eğitimi Dergisi 12(2), 414-436, Ek-1 Metin 2.
# 100 kelime · 4 cümle · 275 hece · OKS=25.0 · H3=7.75 · H4=4.25 · H5=1.25 · H6=0.75
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
    kelimeler, cumle = _hazirla(METIN2)
    assert (len(kelimeler), cumle, toplam_hece(kelimeler, "tr")) == (100, 4, 275)


def test_atesman_bilinen_deger():
    """Makale Tablo 9: Metin 2 → 23,094"""
    sonuc = turkish_readability_formulas(*_hazirla(METIN2), "tr")
    assert sonuc["atesman"] == pytest.approx(23.094, abs=0.01)


def test_cetinkaya_uzun_bilinen_deger():
    """Makale Tablo 9: Metin 2 → 23,084"""
    sonuc = turkish_readability_formulas(*_hazirla(METIN2), "tr")
    assert sonuc["cetinkaya_uzun"] == pytest.approx(23.084, abs=0.01)


def test_bezirci_yilmaz_katsayilari():
    """Dört katsayı tek tek (Bezirci & Yılmaz 2010 s.370: EKOK 21000'den türetilmiş).

    Tek cümle, tek kelime: OKS = 1, puan = √katsayı.
    """
    for kelime, katsayi in [
        ("kitaplar", 0.84), ("kitaplarım", 1.50),
        ("kitaplarımız", 3.50), ("kitaplarımızda", 26.25),
    ]:
        sonuc = bezirci_yilmaz_score([kelime], 1)
        assert sonuc["bezirci_yilmaz"] == pytest.approx(math.sqrt(katsayi), abs=1e-4), kelime


def test_bezirci_yilmaz_iki_heceli_kelime_puana_girmez():
    assert bezirci_yilmaz_score(["kitap"], 1)["bezirci_yilmaz"] == 0.0


def test_bezirci_yilmaz_formul_sekli():
    """Makalenin Tablo 5'i: puan = √(OKS · braket), dokuz hücrenin dokuzu."""
    for oks, braket, beklenen in [
        (7, 3.03, 4.61), (10, 3.03, 5.50), (14, 3.03, 6.51),
        (7, 8.30, 7.62), (10, 8.30, 9.11), (14, 8.30, 10.78),
        (7, 18.82, 11.48), (10, 18.82, 13.72), (14, 18.82, 16.23),
    ]:
        assert math.sqrt(oks * braket) == pytest.approx(beklenen, abs=0.005)


def test_bezirci_yilmaz_kalyoncu_memis_metin2():
    """Bilinçli uyuşmazlık: makale 30,4231 (H6'yı 26,35 diye yanlış aktarmış),
    birincil katsayı 26.25 ile 30.3922."""
    sonuc = bezirci_yilmaz_score(*_hazirla(METIN2))
    assert sonuc["bezirci_yilmaz"] == pytest.approx(30.3922, abs=0.01)


# ── boş girdi (K4) ────────────────────────────────────────────────────


def test_bos_girdiler_nan():
    assert _nan(automated_readability_index([], [], 0)["ari"])
    assert _nan(coleman_liau_index([], 0)["coleman_liau"])
    assert _nan(lix_readability_index([], 0)["lix"])
    assert _nan(long_word_ratio([])["long_word_ratio"])
    assert _nan(bezirci_yilmaz_score([], 0)["bezirci_yilmaz"])
    sonuc = turkish_readability_formulas([], 0, "tr")
    assert set(sonuc) == {"atesman", "cetinkaya_uzun"}
    assert all(_nan(v) for v in sonuc.values())


def test_cumle_sayisi_sifirsa_nan():
    assert _nan(automated_readability_index(["ev"], ["ev"], 0)["ari"])
    assert _nan(lix_readability_index(["ev"], 0)["lix"])
    assert _nan(bezirci_yilmaz_score(["ev"], 0)["bezirci_yilmaz"])
    assert all(_nan(v) for v in turkish_readability_formulas(["ev"], 0, "tr").values())
