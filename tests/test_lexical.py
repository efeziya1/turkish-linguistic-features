import numpy as np

from turkish_linguistic_features.features.lexical import (
    brunet_w,
    hapax_count,
    hapax_ratio,
    heaps_beta,
    rank_word_freq_table,
    rare_word_metrics,
    shannon_entropy,
    simpsons_d,
    type_token_ratio,
    word_length_stats,
    yules_k,
)
from turkish_linguistic_features.features.params import DEFAULT_PARAMS

# ── frekans tablosu ───────────────────────────────────────────────────


def test_frekans_tablosu_kucuk_harfe_indirger():
    freqs, M, N, items = rank_word_freq_table(["Ev", "ev", "EV", "yol"])
    assert M == 4          # toplam token
    assert N == 2          # "ev" ve "yol"
    assert items[0] == ("ev", 3)


# ── entropi ───────────────────────────────────────────────────────────


def test_entropi_esit_dagilimda_log2_n():
    """4 kelime eşit frekansta → entropi tam olarak 2 bit."""
    assert shannon_entropy(np.array([1, 1, 1, 1])) == 2.0


def test_entropi_tek_kelimede_sifir():
    assert shannon_entropy(np.array([10])) == 0.0


# ── Yule-K ────────────────────────────────────────────────────────────


def test_yule_k_tasmaz_int32_girdide():
    """Taşma regresyonu — `astype(np.float64)` olmadan KIRMIZI dönmeli.

    Elle hesap:  freqs = [100000, 50000, 25000],  M = 175000
      Σf² = 1e10 + 2.5e9 + 6.25e8 = 13_125_000_000
      K   = 10000 · (13_125_000_000 − 175_000) / 175_000²
          = 10000 · 13_124_825_000 / 30_625_000_000
          = 4285.66

    Girdi bilerek `int32`: 100000² = 1e10, int32 tavanının (≈2.1e9)
    üstünde. `astype` unutulursa sonuç 78.34 çıkar — **pozitif**, yani
    planın eski `assert yules_k(freqs) > 0` biçimi bu hatayı KAÇIRIYORDU.
    Tam değer iddiası kaçırmıyor.
    """
    freqs = np.array([100_000, 50_000, 25_000], dtype=np.int32)
    assert yules_k(freqs) == 4285.66


# ── Simpson-D ─────────────────────────────────────────────────────────


def test_simpson_d_elle_hesap():
    # freqs = [3, 1], M = 4 → (3·2 + 1·0) / (4·3) = 6/12 = 0.5
    assert simpsons_d(np.array([3, 1])) == 0.5


# ── Brunet-W ──────────────────────────────────────────────────────────


def test_brunet_w_sekli():
    """🔴 Bu test formülün ŞEKLİNİ donduruyor, SABİTİNİ değil.

    Sabit **Kademe D** (doğrulanmamış, bkz. `00-ANA-PLAN.md` K12 eki-2).
    Bu yüzden sabitten bağımsız, formülün cebirinden çıkan iki özellik
    ölçülüyor:
      1. W = M^(V^−a)  →  V arttıkça üs küçülür  →  W küçülür
      2. V = 1 iken üs = 1  →  W = M   (a'dan bağımsız, her a için doğru)
    """
    assert brunet_w(1000, 100)["brunet_w"] > brunet_w(1000, 200)["brunet_w"]
    assert abs(brunet_w(1000, 1)["brunet_w"] - 1000) < 1e-6


def test_brunet_w_varsayilan_sabit_tweedie_baayen():
    """Kademe C: sabit 0.172. Kaynak OKUNDU, plandan alınmadı.

    Tweedie, F. J. & Baayen, R. H. (1998), "How Variable May a Constant be?
    Measures of Lexical Richness in Perspective", *Computers and the
    Humanities* 32(5): 323-352, **denklem (10)**, s. 328:

        "Finally, in 1978, Brunet introduced a parametric expression
         W = N^(V(N)^-a), where a is usually set to -0.172"

    Makaledeki eksi işareti notasyon kayması: `a = -0.172` ile `V^-a`
    birleşince W ≈ 2.6e8 çıkıyor. Etkin üs `V^(-0.172)` okuması
    literatürün bildirdiği 10 ≤ W ≤ 20 aralığını veriyor; `zipfR` (CRAN)
    de böyle uyguluyor. İkinci bağımsız kaynak olduğu için Kademe C.

    Birincil kaynak (Kademe A) hâlâ okunmadı ve çevrimiçi yok:
    Brunet, E. *Vocabulaire de Jean Giraudoux: Structure et Évolution.*
    Genève: Slatkine, 1978.
    """
    assert DEFAULT_PARAMS.brunet_w_a == 0.172
    assert brunet_w(1000, 400)["brunet_w"] == 11.7612


def test_brunet_w_sabiti_ayarlanabilir():
    """Sabit tartışmalı olduğu için `FeatureParams`'ta görünür ve değiştirilebilir.

    Bazı ikincil kaynaklar 0.165 veriyor (ör. metricgate.com — kaynakça
    bölümü yok). Kullanıcı o değere geçebilsin diye parametre; kütüphane
    ölçer, kullanıcı adına karar vermez (K10).
    """
    varsayilan = brunet_w(1000, 400)["brunet_w"]
    eski_deger = brunet_w(1000, 400, a=0.165)["brunet_w"]
    assert eski_deger == 13.0708
    assert eski_deger > varsayilan            # 0.165 sistematik olarak yüksek
    assert abs(eski_deger - varsayilan) / varsayilan > 0.10   # fark %10'un üstünde


# ── hapax ─────────────────────────────────────────────────────────────


def test_hapax_orani():
    # items: a×1, b×1, c×3 → 2 hapax / 3 tip
    items = [("c", 3), ("a", 1), ("b", 1)]
    assert abs(hapax_ratio(items)["hapax_ratio"] - 2 / 3) < 1e-4


def test_hapax_sayimi_ham_int_doner():
    items = [("c", 3), ("a", 1), ("b", 1)]
    assert hapax_count(items) == 2


# ── TTR ───────────────────────────────────────────────────────────────


def test_ttr_elle_hesap():
    # 4 token, 2 tip → 0.5
    assert type_token_ratio(4, 2)["ttr"] == 0.5


def test_ttr_uzunluga_bagimli_regresyon():
    """TTR'nin bilinen kusuru: aynı çeşitlilikte uzun metin daha düşük TTR verir.

    Bu test bir bug arayışı değil — davranışın kasıtlı olduğunu dondurur.
    Biri 'TTR tuhaf davranıyor' diye düzeltmeye kalkarsa bu test onu durdurur.
    """
    kisa = type_token_ratio(100, 60)["ttr"]
    uzun = type_token_ratio(1000, 300)["ttr"]
    assert kisa > uzun


# ── kelime uzunluğu ───────────────────────────────────────────────────


def test_kelime_uzunlugu_elle_hesap():
    """Uzunluklar [2, 4] → ortalama 3.0, popülasyon std 1.0, CV = 1/3."""
    ort, cv = word_length_stats(["ab", "abcd"])
    assert ort == 3.0
    assert cv == 0.3333


# ── Sichel-S ──────────────────────────────────────────────────────────


def test_sichel_s_elle_hesap():
    """a×2, b×2, c×1, d×1, e×1 → V=5 tip, V₂=2 → S = 2/5 = 0.4."""
    lemmalar = ["a", "a", "b", "b", "c", "d", "e"]
    assert rare_word_metrics(lemmalar)["sichel_s"] == 0.4


# ── Heaps β ───────────────────────────────────────────────────────────


def test_heaps_beta_kisa_metinde_sifir():
    """300 token altında uydurma yapmaz — 0.0 'ölçülemedi' demek."""
    assert heaps_beta(["a"] * 299)["heaps_beta"] == 0.0


def test_heaps_beta_hepsi_tekil_ise_bir():
    """Her token yeni bir tip → V = N → log V = log N → β = 1."""
    assert heaps_beta([f"w{i}" for i in range(1000)])["heaps_beta"] == 1.0


def test_heaps_beta_hepsi_ayni_ise_sifir():
    """V sabit 1 → log V sabit 0 → eğim 0."""
    assert heaps_beta(["a"] * 1000)["heaps_beta"] == 0.0


# ── kenar durumlar (Faz 1 zorunlu 3 testin 2'si ve 3'ü) ───────────────


def test_bos_girdiler_cokmez():
    freqs, M, N, items = rank_word_freq_table([])
    assert M == 0 and N == 0
    assert shannon_entropy(freqs) == 0.0
    assert yules_k(freqs) == 0.0
    assert simpsons_d(freqs) == 0.0
    assert brunet_w(0, 0)["brunet_w"] == 0.0
    assert hapax_ratio([])["hapax_ratio"] == 0.0
    assert hapax_count([]) == 0
    assert word_length_stats([]) == (0.0, 0.0)
    assert type_token_ratio(0, 0)["ttr"] == 0.0
    assert rare_word_metrics([])["sichel_s"] == 0.0
    assert heaps_beta([])["heaps_beta"] == 0.0


def test_tek_elemanli_girdiler_cokmez():
    freqs, M, N, items = rank_word_freq_table(["ev"])
    assert M == 1 and N == 1 and items == [("ev", 1)]
    assert shannon_entropy(freqs) == 0.0
    assert yules_k(freqs) == 0.0          # M ≤ 1 → tanımsız, 0.0
    assert simpsons_d(freqs) == 0.0       # M(M−1) = 0 → sıfıra bölme yok
    assert brunet_w(1, 1)["brunet_w"] == 1.0
    assert hapax_ratio(items)["hapax_ratio"] == 1.0
    assert hapax_count(items) == 1
    assert word_length_stats(["ev"]) == (2.0, 0.0)
    assert type_token_ratio(1, 1)["ttr"] == 1.0
    assert rare_word_metrics(["ev"])["sichel_s"] == 0.0
    assert heaps_beta(["ev"])["heaps_beta"] == 0.0
