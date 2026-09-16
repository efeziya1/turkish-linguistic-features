"""T04B — h-point ailesi.

Bilinen değerlerin kaynağı YAYIMLANMIŞ sonuçlar (K12, Kademe A):
QUITA kılavuzu (Kubát, Matlach & Čech 2014) Ek 15.3'teki iki Orwell metninin
tam frekans listeleri ve kılavuzun kendi çalışılmış örnekleri. Sayfa/denklem
numaraları → D:/Masaüstü/tlf-kaynaklar/00-INDEKS.md
"""

import math

import numpy as np

from turkish_linguistic_features.features.frequency_structure import (
    adjusted_modulus,
    curve_length,
    curve_length_indicator,
    gini_coef,
    h_point,
    lambda_pa,
    repeat_rate,
    rr_mcintosh,
    secondary_thematic_concentration,
    thematic_concentration,
    vocab_richness_r1,
    vocab_richness_r4,
    writers_view,
)


def _rle(ciftler):
    return np.array([f for f, n in ciftler for _ in range(n)], dtype=np.int64)


# QUITA Ek 15.3 — rank sıralı tam frekans listeleri
ORWELL_1984 = _rle([(16, 1), (7, 3), (5, 2), (3, 4), (2, 11), (1, 98)])          # N=179 V=119
ANIMAL_FARM = _rle([(20, 1), (9, 1), (8, 1), (7, 1), (4, 5), (3, 6), (2, 14), (1, 92)])  # N=202 V=121


def test_fikstur_yayimlanan_n_v_ile_tutuyor():
    assert (ORWELL_1984.sum(), len(ORWELL_1984)) == (179, 119)
    assert (ANIMAL_FARM.sum(), len(ANIMAL_FARM)) == (202, 121)


# ── h-point ───────────────────────────────────────────────────────────


def test_h_point_tam_eslesme():
    """freqs=[5,4,3,2,1] → rank 3'te f=3, tam h-point."""
    assert h_point(np.array([5, 4, 3, 2, 1])) == 3


def test_h_point_ara_degerleme_elle():
    """f(2)=5>2, f(3)=2<3 → (5·3 − 2·2)/(3 − 2 + 5 − 2) = 11/4."""
    assert h_point(np.array([10, 5, 2, 1])) == 2.75


def test_h_point_quita():
    """QUITA s. 12: Metin 1 tam eşleşme h=5, Metin 2 ara değerleme h=4.75."""
    assert h_point(ORWELL_1984) == 5.0
    assert h_point(ANIMAL_FARM) == 4.75


def test_h_point_kesisme_yoksa_v_ile_sinirli():
    """Her rankta f > r → eğri köşegeni gözlenen ranklarda kesmiyor; h = V."""
    assert h_point(np.array([10])) == 1.0
    assert h_point(np.array([9, 9])) == 2.0


# ── tekrar oranı ve Gini ──────────────────────────────────────────────


def test_repeat_rate_esit_dagilimda():
    # 4 tip eşit frekansta: RR = 4·(1/4)² = 0.25
    assert abs(repeat_rate(np.array([1, 1, 1, 1]), 4)["repeat_rate"] - 0.25) < 1e-9


def test_rr_mcintosh_elle_ve_quita():
    """Eşit dağılım: (1 − √0.25)/(1 − 1/√4) = 1. QUITA Metin 1: 0.946 (s. 19)."""
    assert rr_mcintosh(0.25, 4)["rr_mcintosh"] == 1.0
    rr = repeat_rate(ORWELL_1984, 179)["repeat_rate"]
    assert abs(rr_mcintosh(rr, 119)["rr_mcintosh"] - 0.946) < 5e-4


def test_gini_elle():
    """[3,2,1]: Σr·f = 10 → (3 + 1 − 2·10/6)/3 = 2/9."""
    assert abs(gini_coef(np.array([3, 2, 1]), 6, 3)["gini_coef"] - 2 / 9) < 1e-6


def test_gini_quita():
    """QUITA s. 34: G(Metin 1) = 0.3045, G(Metin 2) = 0.3511."""
    assert abs(gini_coef(ORWELL_1984, 179, 119)["gini_coef"] - 0.3045) < 5e-5
    assert abs(gini_coef(ANIMAL_FARM, 202, 121)["gini_coef"] - 0.3511) < 5e-5


def test_gini_tek_tip_maksimum_esitsizlik():
    """Tek tip → Gini tanımlı ve çökmüyor."""
    assert isinstance(gini_coef(np.array([10]), 10, 1)["gini_coef"], float)


# ── sözcük zenginliği R1 ve R4 ────────────────────────────────────────


def test_r1_quita_tam_h():
    """WFS s. 30 denk. (3.8) · QUITA s. 16: R1(Metin 1) = 0.8352."""
    assert abs(vocab_richness_r1(ORWELL_1984, 179, 5.0)["vocab_richness_r1"] - 0.835196) < 5e-6


def test_r1_kesirli_h_tabana_kadar_toplar():
    """🔴 Tuzak: h=4.75 → toplam rank 1..4, kare 4.75². Doğru 0.838026.

    ⌈h⌉=5'e kadar toplamak 0.818, kısmi rank 0.823 verir ve kitabın
    "Metin 2 daha zengin" sonucunu tersine çevirir.
    """
    assert abs(vocab_richness_r1(ANIMAL_FARM, 202, 4.75)["vocab_richness_r1"] - 0.838026) < 5e-6


def test_r1_bagil_frekans_kullanir():
    """Mutlak F(h) −42.94 verirdi; bağıl F(h) ile R1 her zaman (0, 1) içinde."""
    assert 0.0 < vocab_richness_r1(ANIMAL_FARM, 202, 4.75)["vocab_richness_r1"] < 1.0


def test_r4_quita():
    """WFS s. 57 denk. (3.24) R4 = 1 − G · QUITA s. 34: 0.6955 ve 0.6489."""
    assert abs(vocab_richness_r4(ORWELL_1984, 179, 119)["vocab_richness_r4"] - 0.6955) < 5e-5
    assert abs(vocab_richness_r4(ANIMAL_FARM, 202, 121)["vocab_richness_r4"] - 0.6489) < 5e-5


# ── eğri geometrisi ───────────────────────────────────────────────────


def test_curve_length_elle_hesap():
    # freqs=[3,1]: √((3−1)²+1) = √5 ≈ 2.2360
    assert abs(curve_length(np.array([3, 1]))["curve_length"] - 5 ** 0.5) < 1e-4


def test_curve_length_quita():
    """QUITA s. 36: L(Metin 1) = 129.3559, L(Metin 2) = 134.2787."""
    assert abs(curve_length(ORWELL_1984)["curve_length"] - 129.3559) < 1e-4
    assert abs(curve_length(ANIMAL_FARM)["curve_length"] - 134.2787) < 1e-4


def test_curve_length_r_quita():
    """QUITA s. 37 denk. (6.22-23): Lh(Metin 1) = 14.29145 → R = 1 − 14.29145/129.3559.

    Kılavuzun yazılı ifadesi 4 terim gösteriyor ama sonuç 5 terimle tutuyor:
    toplam r = 1..⌊h⌋, son segment f(5) → f(6).
    """
    beklenen = 1 - 14.29145 / 129.3559
    assert abs(curve_length_indicator(ORWELL_1984, 5.0)["curve_length_r"] - beklenen) < 5e-5


def test_lambda_quita_formulu():
    """QUITA s. 22 denk. (6.13): Λ = L·log₁₀(N)/N, L doğrulanmış değer."""
    beklenen = 129.3559 * math.log10(179) / 179
    assert abs(lambda_pa(129.3559, 179)["lambda_pa"] - beklenen) < 1e-4


def test_adjusted_modulus_quita():
    """QUITA s. 41: A(Metin 1) = 10.6594; M(Metin 2) = 25.81931678 → A = M/log₁₀202."""
    assert abs(adjusted_modulus(16, 119, 5.0, 179)["adjusted_modulus"] - 10.6594) < 1e-4
    beklenen_2 = 25.81931678 / math.log10(202)
    assert abs(adjusted_modulus(20, 121, 4.75, 202)["adjusted_modulus"] - beklenen_2) < 1e-4


def test_writers_view_radyan_quita():
    """QUITA s. 46 denk. (6.34): cos α = −0.374487816 ve −0.269972586 → radyan."""
    assert abs(writers_view(16, 119, 5.0)["writers_view_alpha"] - math.acos(-0.374487816)) < 1e-4
    assert abs(writers_view(20, 121, 4.75)["writers_view_alpha"] - math.acos(-0.269972586)) < 1e-4


def test_writers_view_2009_varyanti_h_eksi_1():
    """Sm 05 (N=447, V=124, f₁=39, h=11): (h−1) → 2.0021; 2007'nin h varyantı 2.0422 verirdi."""
    assert abs(writers_view(39, 124, 11.0)["writers_view_alpha"] - 2.0021) < 1e-4


def test_writers_view_aci_kosinus_degil():
    """Açı ikinci çeyrekte: π/2 ile π arası pozitif. Kosinüs okuması negatif olurdu."""
    alfa = writers_view(16, 119, 5.0)["writers_view_alpha"]
    assert math.pi / 2 < alfa < math.pi


# ── tematik yoğunlaşma ────────────────────────────────────────────────


def test_tc_sadece_otosemantik_sayar():
    """İşlev kelimeleri TC'ye girmez. ev r'=2: 2(3−2)·8 / (3·2·10) = 16/60."""
    items = [("ve", 10), ("ev", 8), ("yol", 5)]
    pos = [("ve", "CCONJ"), ("ev", "NOUN"), ("yol", "NOUN")]
    hepsi_islev = [("ve", "CCONJ"), ("ev", "CCONJ"), ("yol", "CCONJ")]
    tc = thematic_concentration(items, pos, h=3.0)["thematic_concentration"]
    assert abs(tc - 16 / 60) < 1e-6
    assert thematic_concentration(items, hepsi_islev, h=3.0)["thematic_concentration"] == 0.0


def test_tc_konu_kelimesi_zarf_saymaz_ozel_isim_sayar():
    """THEMATIC_POS = NOUN, PROPN, VERB, ADJ (QUITA s. 50; 2026-09-16, Efe).

    ev (ADV) r'=2 sayılmaz → 0; aynı kelime PROPN olunca 16/60.
    """
    items = [("ve", 10), ("ev", 8), ("yol", 5)]
    zarf = [("ve", "CCONJ"), ("ev", "ADV"), ("yol", "CCONJ")]
    ozel = [("ve", "CCONJ"), ("ev", "PROPN"), ("yol", "CCONJ")]
    assert thematic_concentration(items, zarf, h=3.0)["thematic_concentration"] == 0.0
    tc = thematic_concentration(items, ozel, h=3.0)["thematic_concentration"]
    assert abs(tc - 16 / 60) < 1e-6


def test_tc_esit_frekansta_ortalama_rank():
    """QUITA s. 49-51: eşit frekanslı kelimeler ortalama rank alır.

    [6,4,4,1] → h = 3.25; ev ve ve rank 2-3'te eşit → ikisi de 2.5.
    TC = 2(3.25 − 2.5)·4 / (3.25·2.25·6) = 6/43.875. Sıra değişince sonuç değişmemeli.
    """
    pos = [("a", "DET"), ("ev", "NOUN"), ("ve", "CCONJ"), ("x", "NOUN")]
    bir = thematic_concentration([("a", 6), ("ev", 4), ("ve", 4), ("x", 1)], pos, h=3.25)
    iki = thematic_concentration([("a", 6), ("ve", 4), ("ev", 4), ("x", 1)], pos, h=3.25)
    assert abs(bir["thematic_concentration"] - 6 / 43.875) < 1e-6
    assert bir == iki


def test_stc_kaynak_formulu_ve_kisa_metinde_tasmaz():
    """QUITA s. 52 denk. (6.42): Σ_{r'≤2h} (2h−r')f / (h(2h−1)f₁).

    V=2 < 2h=4 → taşma yok. ev r'=1: 3·3=9, yol r'=2: 2·1=2 → 11 / (2·3·3) = 11/18.
    """
    items = [("ev", 3), ("yol", 1)]
    pos = [("ev", "NOUN"), ("yol", "NOUN")]
    r = secondary_thematic_concentration(items, pos, h=2.0)
    assert abs(r["secondary_thematic_concentration"] - 11 / 18) < 1e-6


def test_pos_buyuk_kucuk_harf_duyarsiz():
    """items küçük harfli gelir (rank_word_freq_table), pos_data metindeki haliyle."""
    items = [("ve", 10), ("ev", 8), ("yol", 5)]
    pos = [("Ve", "CCONJ"), ("Ev", "NOUN"), ("yol", "NOUN")]
    assert thematic_concentration(items, pos, h=3.0)["thematic_concentration"] > 0.0


# ── boş ve dejenere girdi (K4) ────────────────────────────────────────


def test_bos_girdi_hepsi_sifir():
    bos = np.array([], dtype=np.int64)
    assert h_point(bos) == 0.0
    assert repeat_rate(bos, 0)["repeat_rate"] == 0.0
    assert curve_length(bos)["curve_length"] == 0.0
    assert gini_coef(bos, 0, 0)["gini_coef"] == 0.0
    assert rr_mcintosh(0.0, 0)["rr_mcintosh"] == 0.0
    assert vocab_richness_r1(bos, 0, 0.0)["vocab_richness_r1"] == 0.0
    assert vocab_richness_r4(bos, 0, 0)["vocab_richness_r4"] == 0.0
    assert curve_length_indicator(bos, 0.0)["curve_length_r"] == 0.0
    assert lambda_pa(0.0, 0)["lambda_pa"] == 0.0
    assert adjusted_modulus(0, 0, 0.0, 0)["adjusted_modulus"] == 0.0
    assert writers_view(0, 0, 0.0)["writers_view_alpha"] == 0.0
    assert thematic_concentration([], [], 0.0)["thematic_concentration"] == 0.0
    assert secondary_thematic_concentration([], [], 0.0)["secondary_thematic_concentration"] == 0.0


def test_dejenere_paydalar_cokmez():
    """M ≤ 1 → log₁₀M ≤ 0 · h ≤ 1 → h(h−1) = 0 · V ≤ 1 → RRmc paydası 0."""
    assert rr_mcintosh(1.0, 1)["rr_mcintosh"] == 0.0
    assert adjusted_modulus(1, 1, 1.0, 1)["adjusted_modulus"] == 0.0
    assert lambda_pa(0.0, 1)["lambda_pa"] == 0.0
    assert thematic_concentration([("ev", 1)], [("ev", "NOUN")], 1.0)["thematic_concentration"] == 0.0
    assert math.isfinite(writers_view(1, 1, 1.0)["writers_view_alpha"])
