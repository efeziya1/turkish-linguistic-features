import math

import pytest

from turkish_linguistic_features.features.phonetic import (
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
