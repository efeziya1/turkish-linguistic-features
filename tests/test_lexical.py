import math

import numpy as np
import pytest

from turkish_linguistic_features.features.lexical import (
    advanced_lexical_richness,
    brunet_w,
    dugast_u,
    guiraud_r,
    hapax_count,
    hapax_ratio,
    hdd,
    heaps_beta,
    msttr,
    mtld,
    pos_lexical_variation,
    rank_word_freq_table,
    rare_word_metrics,
    shannon_entropy,
    simpsons_d,
    ttr_moving_slope,
    type_token_ratio,
    vocd_d,
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


# ── T05: pencereli ve eğri tabanlı zenginlik ──────────────────────────


def test_zenginlik_anahtarlari_bigram_entropy_yok():
    """bigram_entropy 2026-09-15'te çıkarıldı (Efe)."""
    sonuc = advanced_lexical_richness([f"k{i}" for i in range(10)])
    assert set(sonuc) == {"mattr", "entropy_std", "herdan_c"}


def test_mattr_tamamen_tekrarli_metinde_dusuk():
    assert advanced_lexical_richness(["aynı"] * 200, window=50)["mattr"] < 0.05


def test_mattr_tamamen_farkli_metinde_bir():
    tokens = [f"kelime{i}" for i in range(200)]
    assert advanced_lexical_richness(tokens, window=50)["mattr"] == 1.0


def test_mattr_bilinen_deger():
    """a b a b, pencere 3 → aba (2/3), bab (2/3) → 2/3."""
    sonuc = advanced_lexical_richness(["a", "b", "a", "b"], window=3)
    assert sonuc["mattr"] == pytest.approx(2 / 3, abs=1e-4)


def test_mattr_pencereden_kisa_metinde_duz_ttr():
    """20 token, pencere 50 — düz TTR'ye düşer, hata vermez."""
    tokens = [f"k{i % 10}" for i in range(20)]
    assert advanced_lexical_richness(tokens, window=50)["mattr"] == 0.5


def test_entropy_std_ayrik_parcalar_artik_atilir():
    """Parça 2: [a b] H=1 bit, [a a] H=0 → popülasyon sapması 0.5.
    Sondaki tek kelimelik artık parça ('c') hesaba girmez."""
    sonuc = advanced_lexical_richness(["a", "b", "a", "a", "c"], window=2)
    assert sonuc["entropy_std"] == pytest.approx(0.5, abs=1e-4)


def test_entropy_std_tek_parcada_sifir():
    assert advanced_lexical_richness(["a", "b", "c"], window=2)["entropy_std"] == 0.0


def test_herdan_c_bilinen_deger():
    """N=100, V=10 → log 10 / log 100 = 0.5 (taban fark etmez)."""
    tokens = [f"k{i % 10}" for i in range(100)]
    assert advanced_lexical_richness(tokens)["herdan_c"] == pytest.approx(0.5, abs=1e-4)


def test_herdan_c_araligi():
    tokens = [f"k{i % 30}" for i in range(300)]
    assert 0.0 < advanced_lexical_richness(tokens)["herdan_c"] < 1.0


def test_mtld_cesitli_metinde_tekrarlidan_yuksek():
    cesitli = [f"k{i % 100}" for i in range(300)]
    tekrarli = ["a", "b"] * 150
    assert mtld(cesitli)["mtld"] > mtld(tekrarli)["mtld"]


def test_mtld_iki_yonun_ortalamasi_yon_bagimsiz():
    tokens = [f"k{(i * 7) % 23}" for i in range(120)] + ["a", "b", "c"]
    assert mtld(tokens)["mtld"] == pytest.approx(mtld(tokens[::-1])["mtld"], abs=1e-4)


def test_dugast_u_tum_kelimeler_farkliysa_sifir():
    """N == V → payda sıfır → 0.0 dönmeli, ZeroDivisionError değil."""
    assert dugast_u(["a", "b", "c"])["dugast_u"] == 0.0


def test_guiraud_r_bilinen_deger():
    """V=3, N=9 → 3/3 = 1.0"""
    assert guiraud_r(["a", "b", "c"] * 3)["guiraud_r"] == 1.0


def test_guiraud_r_uzunlukla_ttr_kadar_hizli_dusmez():
    """Guiraud'nun var olma sebebi bu: √N düzeltmesi TTR'den yavaş düşer."""
    kisa = [f"k{i % 20}" for i in range(40)]
    uzun = [f"k{i % 20}" for i in range(400)]
    ttr_dususu = (len(set(kisa)) / len(kisa)) / (len(set(uzun)) / len(uzun))
    g_dususu = guiraud_r(kisa)["guiraud_r"] / guiraud_r(uzun)["guiraud_r"]
    assert g_dususu < ttr_dususu


def test_ttr_egimi_sabit_parcalar_bilinen_deger():
    """Parça 2: [a b]=1, [c c]=0.5, [d d]=0.5 → eğim −0.25. Artık 'e' atılır."""
    tokens = ["a", "b", "c", "c", "d", "d", "e"]
    sonuc = ttr_moving_slope(tokens, chunk_size=2)
    assert sonuc["ttr_moving_slope"] == pytest.approx(-0.25, abs=1e-4)


def test_ttr_egimi_iki_parcadan_azsa_sifir():
    assert ttr_moving_slope(["a", "b", "c"], chunk_size=2)["ttr_moving_slope"] == 0.0


def test_pos_variation_bilinen_deger():
    """3 isim token, 2 benzersiz isim lemma → 2/3."""
    lemmalar = ["kitap", "kitap", "kalem", "oku"]
    pos = [("kitabı", "NOUN"), ("kitap", "NOUN"), ("kalem", "NOUN"), ("okudu", "VERB")]
    sonuc = pos_lexical_variation(lemmalar, pos)
    assert sonuc["noun_variation"] == pytest.approx(2 / 3, abs=1e-4)
    assert sonuc["verb_variation"] == 1.0


def test_pos_variation_noktalama_hizayi_bozmaz():
    """lemma_tokens'ta noktalama yok, pos_data'da var (T21) — PUNCT atılıp hizalanır."""
    lemmalar = ["kitap", "oku", "kitap"]
    pos = [("Kitap", "NOUN"), (",", "PUNCT"), ("okudu", "VERB"), ("kitabı", "NOUN"), (".", "PUNCT")]
    sonuc = pos_lexical_variation(lemmalar, pos)
    assert sonuc["noun_variation"] == 0.5
    assert sonuc["verb_variation"] == 1.0


def test_pos_variation_hizasiz_listelerde_sifir():
    sonuc = pos_lexical_variation(["a", "b"], [("a", "NOUN")])
    assert all(v == 0.0 for v in sonuc.values())


def test_pos_variation_ozel_isim_ve_aux_sayilmaz():
    """noun_variation yalnız NOUN, verb_variation yalnız VERB (2026-09-15, Efe)."""
    lemmalar = ["ahmet", "ahmet", "ev", "i", "gel"]
    pos = [("Ahmet", "PROPN"), ("Ahmet", "PROPN"), ("ev", "NOUN"), ("idi", "AUX"), ("geldi", "VERB")]
    sonuc = pos_lexical_variation(lemmalar, pos)
    assert sonuc["noun_variation"] == 1.0
    assert sonuc["verb_variation"] == 1.0


def test_pos_variation_sinif_yoksa_sifir():
    """K4 — metinde hiç sıfat yok, payda sıfır."""
    assert pos_lexical_variation(["oku"], [("okudu", "VERB")])["adj_variation"] == 0.0


def test_pos_variation_pos_noun_ile_bagimsiz():
    """İsim ağırlıklı ama tekrarlı metin: oran yüksek, çeşitlilik düşük."""
    lemmalar = ["kitap"] * 9 + ["oku"]
    pos = [("kitap", "NOUN")] * 9 + [("okudu", "VERB")]
    assert pos_lexical_variation(lemmalar, pos)["noun_variation"] < 0.2


def test_t05_bos_girdiler():
    for sonuc in (mtld([]), dugast_u([]), ttr_moving_slope([]), guiraud_r([]),
                  advanced_lexical_richness([]), pos_lexical_variation([], [])):
        assert all(v == 0.0 for v in sonuc.values())


# ── T06: örneklemeli çeşitlilik ───────────────────────────────────────


def _cesitli(n: int = 400) -> list[str]:
    return [f"k{(i * 7919) % 300}" for i in range(n)]


def _tekrarli(n: int = 400) -> list[str]:
    return [f"k{i % 12}" for i in range(n)]


def test_vocd_deterministik():
    """Aynı girdi + aynı tohum → aynı sonuç."""
    assert vocd_d(_cesitli())["vocd_d"] == vocd_d(_cesitli())["vocd_d"]


def test_vocd_global_random_kirletmez():
    import random
    random.seed(1)
    once = random.random()
    random.seed(1)
    vocd_d(_cesitli())
    assert random.random() == once


def test_vocd_kisa_metinde_sifir():
    assert vocd_d(["a"] * 10)["vocd_d"] == 0.0


def test_vocd_en_buyuk_orneklemden_kisa_metinde_sifir():
    """35–50 aralığında 50'lik çekiliş yapılamıyorsa ölçülemez."""
    assert vocd_d(_cesitli(49), min_tokens=10)["vocd_d"] == 0.0


def test_vocd_cesitli_metinde_tekrarlidan_yuksek():
    assert vocd_d(_cesitli())["vocd_d"] > vocd_d(_tekrarli())["vocd_d"]


def test_vocd_modelden_uretilen_egriyi_geri_bulur():
    """TTR(n) = (D/n)(√(1+2n/D) − 1) eğrisine D=60 ile uyan veri → D ≈ 60."""
    from turkish_linguistic_features.features.lexical import _vocd_uydur
    D = 60.0
    boylar = list(range(35, 51))
    ttrler = [(D / n) * (math.sqrt(1 + 2 * n / D) - 1) for n in boylar]
    assert _vocd_uydur(boylar, ttrler) == pytest.approx(60.0, rel=1e-3)


def test_hdd_tum_tokenler_ayniysa_dusuk():
    assert hdd(["aynı"] * 100)["hdd"] < 0.05


def test_hdd_tum_tokenler_farkliysa_bir():
    """Her tipin 42'lik örneklemde görülme olasılığı 42/200 → toplam 42 → /42 = 1."""
    assert hdd([f"k{i}" for i in range(200)])["hdd"] == pytest.approx(1.0, abs=1e-4)


def test_hdd_bilinen_deger():
    """[a a b c], n=2: P(a)=1−C(2,2)/C(4,2)=5/6, P(b)=P(c)=1−3/6=1/2 → (11/6)/2."""
    assert hdd(["a", "a", "b", "c"], sample_size=2)["hdd"] == pytest.approx(11 / 12, abs=1e-4)


def test_hdd_orneklemden_kisa_metinde_sifir():
    assert hdd([f"k{i}" for i in range(41)])["hdd"] == 0.0


def test_msttr_bilinen_deger_artik_atilir():
    """Segment 4: [ev yol ev su]=0.75, [kedi kedi kedi köpek]=0.5; 'kuş' atılır."""
    tokens = ["ev", "yol", "ev", "su", "kedi", "kedi", "kedi", "köpek", "kuş"]
    assert msttr(tokens, segment_size=4)["msttr"] == pytest.approx(0.625, abs=1e-4)


def test_msttr_segmentten_kisa_metinde_sifir():
    """50 token, segment 100 → tam segment yok → 0.0 (2026-09-15, Efe)."""
    assert msttr([f"k{i}" for i in range(50)], 100)["msttr"] == 0.0


def test_t06_bos_girdiler():
    assert vocd_d([])["vocd_d"] == 0.0
    assert hdd([])["hdd"] == 0.0
    assert msttr([])["msttr"] == 0.0
