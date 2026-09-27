import math
import random

import numpy as np
import pytest

from turkish_linguistic_features.features.lexical import (
    advanced_lexical_richness,
    brunet_w,
    dugast_u,
    guiraud_r,
    hapax_count,
    hapax_percentage,
    hapax_ratio,
    hdd,
    heaps_beta,
    msttr,
    mtld,
    pos_lexical_variation,
    rank_word_freq_table,
    rare_word_metrics,
    reference_frequency_sophistication,
    shannon_entropy,
    simpsons_d,
    ttr_moving_slope,
    type_token_ratio,
    vocd_d,
    word_length_stats,
    yules_k,
    zipf,
    zipf_mandelbrot,
)
from turkish_linguistic_features.params import DEFAULT_PARAMS


def _nan(x) -> bool:
    return isinstance(x, float) and math.isnan(x)


def _hepsi_nan(d: dict) -> bool:
    return bool(d) and all(_nan(v) for v in d.values())

# ── frekans tablosu ───────────────────────────────────────────────────


def test_frekans_tablosu_kucuk_harfe_indirger():
    freqs, N, V, items = rank_word_freq_table(["Ev", "ev", "EV", "yol"])
    assert N == 4          # toplam token
    assert V == 2          # "ev" ve "yol"
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

    Elle hesap:  freqs = [100000, 50000, 25000],  N = 175000
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
    # freqs = [3, 1], N = 4 → (3·2 + 1·0) / (4·3) = 6/12 = 0.5
    assert simpsons_d(np.array([3, 1])) == 0.5


# ── Brunet-W ──────────────────────────────────────────────────────────


def test_brunet_w_sekli():
    """🔴 Bu test formülün ŞEKLİNİ donduruyor, SABİTİNİ değil.

    Sabit **Kademe D** (birincil kaynağa karşı doğrulanmamış).
    Bu yüzden sabitten bağımsız, formülün cebirinden çıkan iki özellik
    ölçülüyor:
      1. W = N^(V^−a)  →  V arttıkça üs küçülür  →  W küçülür
      2. V = 1 iken üs = 1  →  W = N   (a'dan bağımsız, her a için doğru)
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


def test_hapax_yuzdesi_paydasi_token():
    """5 token, 3 tip, 2'si bir kez geçiyor → yüzde 2/5, oran 2/3."""
    _, N, V, items = rank_word_freq_table(["ev", "ev", "ev", "yol", "kapı"])
    assert (N, V) == (5, 3)
    assert hapax_percentage(items)["hapax_percentage"] == 0.4
    assert hapax_ratio(items)["hapax_ratio"] == 0.666667


def test_hapax_yuzdesi_hepsi_bir_kez_geciyorsa_bir():
    """Her kelime bir kez → V1 = N → 1.0. Oran da 1.0, ama tesadüfen."""
    items = [("a", 1), ("b", 1), ("c", 1)]
    assert hapax_percentage(items)["hapax_percentage"] == 1.0
    assert hapax_ratio(items)["hapax_ratio"] == 1.0


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


def test_heaps_beta_kisa_metinde_nan():
    """300 token altında uydurma yapmaz — NaN 'ölçülemedi' demek (K4, 2026-09-16)."""
    assert _nan(heaps_beta(["a"] * 299)["heaps_beta"])


def test_heaps_beta_hepsi_tekil_ise_bir():
    """Her token yeni bir tip → V = N → log V = log N → β = 1."""
    assert heaps_beta([f"w{i}" for i in range(1000)])["heaps_beta"] == 1.0


def test_heaps_beta_hepsi_ayni_ise_sifir():
    """V sabit 1 → log V sabit 0 → eğim 0."""
    assert heaps_beta(["a"] * 1000)["heaps_beta"] == 0.0


def test_heaps_beta_kirpilmaz():
    """Tekrarla başlayıp açılan metinde eğim 1'i aşar; olduğu gibi yazılır (2026-09-17, Efe)."""
    tokens = ["ve"] * 300 + [f"k{i}" for i in range(300)]
    assert heaps_beta(tokens)["heaps_beta"] == pytest.approx(2.829, abs=1e-3)


def _heaps_beta_eski(tokens, min_tokens=300, step=50):
    """O(N²/step) özgün uygulama — tek geçişli sürümün referansı (değiştirme)."""
    N = len(tokens)
    if N < min_tokens:
        return {"heaps_beta": math.nan}
    nt, vt = [], []
    for kesim in range(step, N + 1, step):
        nt.append(kesim)
        vt.append(len(set(tokens[:kesim])))
    if len(nt) < 5:
        return {"heaps_beta": math.nan}
    beta = float(np.polyfit(np.log(nt), np.log(vt), 1)[0])
    return {"heaps_beta": round(beta, 4) + 0.0}


def test_heaps_beta_tek_gecis_eskisiyle_birebir():
    """Tek geçişli sayım, eski ``len(set(tokens[:kesim]))`` ile BİREBİR aynı sonucu verir.

    Uzunluk, sözlük büyüklüğü, ``min_tokens`` ve ``step`` rastgele; NaN
    dalları (kısa metin, 5'ten az nokta) da kapsanıyor. Geçersiz parametre
    (``step <= 0``, ``min_tokens < 0``) artık hata verir, ayrı sınanıyor.
    """
    rng = random.Random(20260927)
    for _ in range(300):
        n = rng.choice([0, 1, 7, 249, 300, 301, 551, rng.randint(0, 3000)])
        sozluk = rng.choice([1, 2, 10, 200, 5000])
        tokens = [f"w{rng.randrange(sozluk)}" for _ in range(n)]
        min_tokens = rng.choice([0, 1, 50, 300, rng.randint(0, 800)])
        step = rng.choice([1, 3, 50, 97, rng.randint(1, 400)])
        yeni = heaps_beta(tokens, min_tokens, step)["heaps_beta"]
        eski = _heaps_beta_eski(tokens, min_tokens, step)["heaps_beta"]
        assert (_nan(yeni) and _nan(eski)) or yeni == eski, (n, sozluk, min_tokens, step)


@pytest.mark.parametrize("min_tokens, step, mesaj", [
    (300, 0, "step must be positive"),
    (300, -5, "step must be positive"),
    (-1, 50, "min_tokens must be non-negative"),
])
def test_heaps_beta_gecersiz_parametre_hata(min_tokens, step, mesaj):
    """Diğer pencere/parça parametreleri gibi (mattr, msttr, ttr_moving_slope)."""
    with pytest.raises(ValueError, match=mesaj):
        heaps_beta(["a"] * 400, min_tokens, step)


def test_heaps_beta_min_tokens_sifir_gecerli():
    assert heaps_beta([f"w{i}" for i in range(300)], 0, 50)["heaps_beta"] == 1.0


# ── kenar durumlar (Faz 1 zorunlu 3 testin 2'si ve 3'ü) ───────────────


def test_bos_girdiler_cokmez():
    freqs, N, V, items = rank_word_freq_table([])
    assert N == 0 and V == 0
    assert _nan(shannon_entropy(freqs))
    assert _nan(yules_k(freqs))
    assert _nan(simpsons_d(freqs))
    assert _nan(brunet_w(0, 0)["brunet_w"])
    assert _nan(hapax_ratio([])["hapax_ratio"])
    assert _nan(hapax_percentage([])["hapax_percentage"])
    assert hapax_count([]) == 0
    assert all(_nan(v) for v in word_length_stats([]))
    assert _nan(type_token_ratio(0, 0)["ttr"])
    assert _nan(rare_word_metrics([])["sichel_s"])
    assert _nan(heaps_beta([])["heaps_beta"])


def test_tek_elemanli_girdiler_cokmez():
    freqs, N, V, items = rank_word_freq_table(["ev"])
    assert N == 1 and V == 1 and items == [("ev", 1)]
    assert shannon_entropy(freqs) == 0.0
    assert yules_k(freqs) == 0.0          # N = 1: 10000·(1 − 1)/1 = 0, tanımlı
    assert _nan(simpsons_d(freqs))        # N(N−1) = 0 → tanımsız
    assert brunet_w(1, 1)["brunet_w"] == 1.0
    assert hapax_ratio(items)["hapax_ratio"] == 1.0
    assert hapax_percentage(items)["hapax_percentage"] == 1.0
    assert hapax_count(items) == 1
    ort, cv = word_length_stats(["ev"])
    assert ort == 2.0 and _nan(cv)        # tek değerden değişkenlik ölçülmez
    assert type_token_ratio(1, 1)["ttr"] == 1.0
    assert rare_word_metrics(["ev"])["sichel_s"] == 0.0
    assert _nan(heaps_beta(["ev"])["heaps_beta"])


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
    """a b a b a b, pencere 3 → dört pencere, hepsi 2/3 → 2/3.

    Metin 2 x pencere (6 token) olmak zorunda: altında NaN döner.
    """
    sonuc = advanced_lexical_richness(["a", "b", "a", "b", "a", "b"], window=3)
    assert sonuc["mattr"] == pytest.approx(2 / 3, abs=1e-4)


def test_mattr_pencereden_kisa_metinde_nan():
    """20 token, pencere 50 → NaN (Covington & McFall: pencere metinden kısa olmalı)."""
    tokens = [f"k{i % 10}" for i in range(20)]
    assert _nan(advanced_lexical_richness(tokens, window=50)["mattr"])


def test_mattr_pencere_metne_esitse_nan():
    """Tek pencere kalırsa MATTR düz TTR'a çöker — sayı vermektense NaN.

    2026-09-23'e kadar bu vaka 0.75 döndürüyordu, ki o değer metnin düz
    TTR'sinin ta kendisiydi (4 token, 3 tür). Kullanıcı "uzunluktan bağımsız"
    sanarak TTR'ı alıyordu. Eşik 2 x pencereye çekildi.
    """
    assert _nan(advanced_lexical_richness(["a", "b", "a", "c"], window=4)["mattr"])


def test_mattr_esik_tam_iki_katinda_hesaplaniyor():
    """Sınır: tam 2 x pencerede hesaplanır, bir altında NaN."""
    tokens = [f"k{i}" for i in range(6)]
    assert not _nan(advanced_lexical_richness(tokens, window=3)["mattr"])
    assert _nan(advanced_lexical_richness(tokens[:5], window=3)["mattr"])


def test_entropy_std_ayrik_parcalar_artik_atilir():
    """Parça 2: [a b] H=1 bit, [a a] H=0 → popülasyon sapması 0.5.
    Sondaki tek kelimelik artık parça ('c') hesaba girmez."""
    sonuc = advanced_lexical_richness(["a", "b", "a", "a", "c"], window=2)
    assert sonuc["entropy_std"] == pytest.approx(0.5, abs=1e-4)


def test_entropy_std_tek_parcada_sifir():
    assert _nan(advanced_lexical_richness(["a", "b", "c"], window=2)["entropy_std"])


def test_herdan_c_tek_token_nan_tek_tip_sifir():
    """N = 1 → log N = 0 payda; V = 1, N > 1 → log 1 / log N = 0 (tanımlı)."""
    assert _nan(advanced_lexical_richness(["a"])["herdan_c"])
    assert advanced_lexical_richness(["a", "a"])["herdan_c"] == 0.0


def test_herdan_c_bilinen_deger():
    """N=100, V=10 → log 10 / log 100 = 0.5 (taban fark etmez)."""
    tokens = [f"k{i % 10}" for i in range(100)]
    assert advanced_lexical_richness(tokens)["herdan_c"] == pytest.approx(0.5, abs=1e-4)


def test_herdan_c_araligi():
    tokens = [f"k{i % 30}" for i in range(300)]
    assert 0.0 < advanced_lexical_richness(tokens)["herdan_c"] < 1.0


def test_mtld_100_kelimeden_kisa_metinde_nan():
    """McCarthy & Jarvis (2010, s. 384): 100 tokenden kısa metin güvenilmez."""
    assert _nan(mtld(["a", "b"] * 49)["mtld"])
    assert not _nan(mtld(["a", "b"] * 50)["mtld"])


def test_mtld_hic_faktor_yoksa_nan():
    assert _nan(mtld([f"k{i}" for i in range(20)], min_tokens=10)["mtld"])


def test_mtld_cesitli_metinde_tekrarlidan_yuksek():
    cesitli = [f"k{i % 100}" for i in range(300)]
    tekrarli = ["a", "b"] * 150
    assert mtld(cesitli)["mtld"] > mtld(tekrarli)["mtld"]


def test_mtld_iki_yonun_ortalamasi_yon_bagimsiz():
    tokens = [f"k{(i * 7) % 23}" for i in range(120)] + ["a", "b", "c"]
    assert mtld(tokens)["mtld"] == pytest.approx(mtld(tokens[::-1])["mtld"], abs=1e-4)


def test_dugast_u_tum_kelimeler_farkliysa_sifir():
    """N == V → payda sıfır → NaN, ZeroDivisionError değil."""
    assert _nan(dugast_u(["a", "b", "c"])["dugast_u"])


def test_dugast_u_tek_tipte_log_n():
    """V = 1 → U = (log N)² / log N = log₁₀ N."""
    assert dugast_u(["a"] * 100)["dugast_u"] == 2.0


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
    assert _nan(ttr_moving_slope(["a", "b", "c"], chunk_size=2)["ttr_moving_slope"])


def test_pos_variation_bilinen_deger():
    """Lu (2012) Tablo 2: NV = T_noun / N_lex, VV1 = T_verb / N_verb.

    4 sözcüksel kelime; 2 farklı isim lemması → NV = 2/4; 1 fiil tipi / 1 fiil → 1.0.
    """
    lemmalar = ["kitap", "kitap", "kalem", "oku"]
    pos = [("kitabı", "NOUN"), ("kitap", "NOUN"), ("kalem", "NOUN"), ("okudu", "VERB")]
    sonuc = pos_lexical_variation(lemmalar, pos)
    assert sonuc["noun_variation"] == 0.5
    assert sonuc["verb_variation"] == 1.0


def test_pos_variation_sifat_zarf_paydasi_sozcuksel_kelime():
    """AdjV = T_adj / N_lex, AdvV = T_adv / N_lex (McClure 1991, Lu 2012)."""
    lemmalar = ["güzel", "güzel", "iyi", "ev", "gel", "hızlı"]
    pos = [("güzel", "ADJ"), ("güzel", "ADJ"), ("iyi", "ADJ"), ("ev", "NOUN"),
           ("geldi", "VERB"), ("hızlıca", "ADV")]
    sonuc = pos_lexical_variation(lemmalar, pos)
    assert sonuc["adj_variation"] == pytest.approx(2 / 6, abs=1e-4)
    assert sonuc["adv_variation"] == pytest.approx(1 / 6, abs=1e-4)
    assert sonuc["noun_variation"] == pytest.approx(1 / 6, abs=1e-4)


def test_pos_variation_noktalama_hizayi_bozmaz():
    """lemma_tokens'ta noktalama yok, pos_data'da var (T21) — PUNCT atılıp hizalanır."""
    lemmalar = ["kitap", "oku", "kitap"]
    pos = [("Kitap", "NOUN"), (",", "PUNCT"), ("okudu", "VERB"), ("kitabı", "NOUN"), (".", "PUNCT")]
    sonuc = pos_lexical_variation(lemmalar, pos)
    assert sonuc["noun_variation"] == pytest.approx(1 / 3, abs=1e-4)
    assert sonuc["verb_variation"] == 1.0


def test_pos_variation_sembol_de_hizadan_atilir():
    """SYM kelime değil (2026-09-16, Efe) — lemma_tokens'a girmez, hizada atılır."""
    lemmalar = ["yüz", "art"]
    pos = [("yüzde", "NOUN"), ("%", "SYM"), ("arttı", "VERB")]
    sonuc = pos_lexical_variation(lemmalar, pos)
    assert sonuc["verb_variation"] == 1.0


def test_kelime_disi_pos_kumesi():
    from turkish_linguistic_features.vocab import NON_WORD_POS
    assert NON_WORD_POS == ("PUNCT", "SYM")


def test_pos_variation_hizasiz_listelerde_hata():
    """Hizasızlık ön işleme hatasıdır, metnin özelliği değil (2026-09-16, Efe)."""
    with pytest.raises(ValueError, match="not aligned"):
        pos_lexical_variation(["a", "b"], [("a", "NOUN")])


def test_pos_variation_ozel_isim_isimdir_aux_sayilmaz():
    """İsim = NOUN + PROPN; sözcüksel kelime = LEXICAL_POS; AUX hiç sayılmaz (2026-09-16, Efe).

    Sözcüksel: Ahmet, Ahmet, ev, geldi = 4; isim tipleri {ahmet, ev} = 2 → NV = 2/4.
    """
    lemmalar = ["ahmet", "ahmet", "ev", "i", "gel"]
    pos = [("Ahmet", "PROPN"), ("Ahmet", "PROPN"), ("ev", "NOUN"), ("idi", "AUX"), ("geldi", "VERB")]
    sonuc = pos_lexical_variation(lemmalar, pos)
    assert sonuc["noun_variation"] == 0.5
    assert sonuc["verb_variation"] == 1.0        # VV1: 1 fiil tipi / 1 fiil


def test_pos_variation_sozcuksel_kelime_yoksa_nan():
    """K4 — yalnız işlev kelimesi, payda boş → NaN."""
    sonuc = pos_lexical_variation(["ve", "bu"], [("ve", "CCONJ"), ("bu", "DET")])
    assert _hepsi_nan(sonuc)


def test_pos_variation_fiil_yoksa_yalniz_vv1_nan():
    sonuc = pos_lexical_variation(["ev"], [("ev", "NOUN")])
    assert _nan(sonuc["verb_variation"])
    assert sonuc["noun_variation"] == 1.0
    assert sonuc["adj_variation"] == 0.0     # sözcüksel kelime var, sıfat yok → gerçek sıfır


def test_pos_variation_sinif_yoksa_gercek_sifir():
    assert pos_lexical_variation(["oku"], [("okudu", "VERB")])["adj_variation"] == 0.0


def test_pos_variation_pos_noun_ile_bagimsiz():
    """İsim ağırlıklı ama tekrarlı metin: oran yüksek, çeşitlilik düşük."""
    lemmalar = ["kitap"] * 9 + ["oku"]
    pos = [("kitap", "NOUN")] * 9 + [("okudu", "VERB")]
    assert pos_lexical_variation(lemmalar, pos)["noun_variation"] < 0.2


def test_t05_bos_girdiler():
    for sonuc in (mtld([]), dugast_u([]), ttr_moving_slope([]), guiraud_r([]),
                  advanced_lexical_richness([]), pos_lexical_variation([], [])):
        assert _hepsi_nan(sonuc)


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


def test_vocd_kisa_metinde_nan():
    assert _nan(vocd_d(["a"] * 10)["vocd_d"])


def test_vocd_en_buyuk_orneklemden_kisa_metinde_nan():
    """35–50 aralığında 50'lik çekiliş yapılamıyorsa ölçülemez."""
    assert _nan(vocd_d(_cesitli(49), min_tokens=10)["vocd_d"])


def test_ornekleme_parametre_hatasi():
    with pytest.raises(ValueError):
        vocd_d(_cesitli(), sample_min=51, sample_max=50)
    with pytest.raises(ValueError):
        hdd(_cesitli(), sample_size=0)
    with pytest.raises(ValueError):
        msttr(_cesitli(), segment_size=0)


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


def test_hdd_orneklemden_kisa_metinde_nan():
    assert _nan(hdd([f"k{i}" for i in range(41)])["hdd"])


def test_msttr_bilinen_deger_artik_atilir():
    """Segment 4: [ev yol ev su]=0.75, [kedi kedi kedi köpek]=0.5; 'kuş' atılır."""
    tokens = ["ev", "yol", "ev", "su", "kedi", "kedi", "kedi", "köpek", "kuş"]
    assert msttr(tokens, segment_size=4)["msttr"] == pytest.approx(0.625, abs=1e-4)


def test_msttr_segmentten_kisa_metinde_nan():
    """50 token, segment 100 → tam segment yok → NaN (2026-09-16, Efe)."""
    assert _nan(msttr([f"k{i}" for i in range(50)], 100)["msttr"])


def test_t06_bos_girdiler():
    assert _nan(vocd_d([])["vocd_d"])
    assert _nan(hdd([])["hdd"])
    assert _nan(msttr([])["msttr"])


# ── T07: Zipf, Zipf-Mandelbrot, referans frekans ──────────────────────


def test_zipf_tam_yasada_us_bir_uyum_bir():
    freqs = np.array([1000.0 / r for r in range(1, 51)])
    sonuc = zipf(freqs)
    assert sonuc["zipf_exponent"] == pytest.approx(1.0, abs=1e-4)
    assert sonuc["zipf_r2"] == pytest.approx(1.0, abs=1e-4)


def test_zipf_sentetik_dagilimda_us_bire_yakin():
    """f = 1000/r ile üretilmiş tamsayı dağılımda α ≈ 1.0 olmalı."""
    freqs = np.array([max(1, int(1000 / r)) for r in range(1, 101)])
    sonuc = zipf(freqs)
    assert 0.85 < sonuc["zipf_exponent"] < 1.15
    assert sonuc["zipf_r2"] > 0.95


def test_zipf_az_veri_ile_nan():
    assert _hepsi_nan(zipf(np.array([5, 3, 1])))


def test_zipf_esit_frekansta_r2_tanimsiz():
    """Bütün frekanslar eşit → eğim 0 (tanımlı), R² = 0/0 → NaN."""
    sonuc = zipf(np.array([3] * 12))
    assert sonuc["zipf_exponent"] == 0.0
    assert _nan(sonuc["zipf_r2"])


def test_mandelbrot_q_ve_s_geri_bulunur():
    """f = C/(r + 2.5)^1.2 → q ≈ 2.5, s ≈ 1.2 (ızgara adımı 0.1)."""
    freqs = np.array([5000.0 / (r + 2.5) ** 1.2 for r in range(1, 151)])
    m = zipf_mandelbrot(freqs)
    assert m["zipf_mandelbrot_q"] == pytest.approx(2.5, abs=0.05)
    assert m["zipf_mandelbrot_s"] == pytest.approx(1.2, abs=0.01)


def test_mandelbrot_az_veri_ile_nan():
    assert _hepsi_nan(zipf_mandelbrot(np.array([5, 3, 1])))


class _SahteWordfreq:
    """Gerçek veri dosyasına bağlı kalmadan formülü sınamak için."""

    PUAN = {"kitap": 5.0, "oku": 6.0, "epistemoloji": 2.0, "ve": 7.0, "sınır": 3.0}

    @staticmethod
    def zipf_frequency(kelime: str, lang: str) -> float:
        return _SahteWordfreq.PUAN.get(kelime, 0.0)


@pytest.fixture
def sahte_wordfreq(monkeypatch):
    import sys
    import types

    modul = types.ModuleType("wordfreq")
    modul.zipf_frequency = _SahteWordfreq.zipf_frequency
    monkeypatch.setitem(sys.modules, "wordfreq", modul)


def test_wordfreq_yalniz_anlamli_kelimeler_lemma_ile(sahte_wordfreq):
    """ve (CCONJ) ve noktalama sayılmaz. Anlamlı: kitap 5, oku 6, epistemoloji 2,
    xyz 0 (listede yok → 0 puan) → ortalama 13/4. Zipf ≤ 3: epistemoloji, xyz → 2/4."""
    lemmalar = ["kitap", "ve", "oku", "epistemoloji", "xyz"]
    pos = [("Kitabı", "NOUN"), ("ve", "CCONJ"), ("okudu", "VERB"), (",", "PUNCT"),
           ("epistemolojiyi", "NOUN"), ("xyz", "PROPN")]
    sonuc = reference_frequency_sophistication(lemmalar, pos, "tr")
    assert sonuc["wordfreq_mean"] == pytest.approx(13 / 4, abs=1e-4)
    assert sonuc["wordfreq_rare_ratio"] == 0.5


def test_wordfreq_nadir_esigi_dahil(sahte_wordfreq):
    """van Heuven ve ark. (2014) Tablo 1: "Zipf values of 3 or lower are low-frequency"."""
    sonuc = reference_frequency_sophistication(["sınır", "kitap"],
                                               [("sınır", "NOUN"), ("kitap", "NOUN")], "tr")
    assert sonuc["wordfreq_rare_ratio"] == 0.5


def test_wordfreq_anlamli_kelime_yoksa_nan(sahte_wordfreq):
    assert _hepsi_nan(reference_frequency_sophistication(["ve"], [("ve", "CCONJ")], "tr"))
    assert _hepsi_nan(reference_frequency_sophistication([], [], "tr"))


def test_wordfreq_hizasiz_listelerde_hata(sahte_wordfreq):
    with pytest.raises(ValueError, match="not aligned"):
        reference_frequency_sophistication(["kitap", "oku"], [("kitap", "NOUN")], "tr")


def test_wordfreq_gercek_veriyle_calisir():
    pytest.importorskip("wordfreq")
    sonuc = reference_frequency_sophistication(
        ["kitap", "epistemoloji"], [("kitap", "NOUN"), ("epistemoloji", "NOUN")], "tr")
    assert 0.0 < sonuc["wordfreq_mean"] < 8.0
    assert sonuc["wordfreq_rare_ratio"] == 0.5


def test_wordfreq_yoksa_nan_doner_ve_uyarir(monkeypatch):
    """wordfreq kurulu değilse çökmemeli ama SESSİZ de kalmamalı."""
    import builtins

    from turkish_linguistic_features._warnings import MissingDependencyWarning

    gercek_import = builtins.__import__

    def sahte(ad, *a, **k):
        if ad == "wordfreq":
            raise ImportError("test")
        return gercek_import(ad, *a, **k)

    monkeypatch.setattr(builtins, "__import__", sahte)
    with pytest.warns(MissingDependencyWarning, match="wordfreq"):
        sonuc = reference_frequency_sophistication(["kitap"], [("kitap", "NOUN")], "tr")
    assert _hepsi_nan(sonuc)
