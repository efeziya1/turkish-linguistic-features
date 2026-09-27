"""Sözcüksel temel: frekans tablosu ve klasik kelime zenginliği ölçütleri.

Bu modül 31 öznitelik anahtarı üretir (`lexical` grubunun 32'sinden; kalan
``n_lemma_count`` T20'de sayılır):

- T04 (11): ``ttr`` · ``entropy`` · ``yule_k`` · ``simpson_d`` · ``brunet_w`` ·
  ``hapax_ratio`` · ``hapax_percentage`` · ``avg_word_length`` ·
  ``word_length_cv`` · ``sichel_s`` · ``heaps_beta``
- T05 (11): ``mattr`` · ``entropy_std`` · ``herdan_c`` · ``mtld`` ·
  ``dugast_u`` · ``guiraud_r`` · ``ttr_moving_slope`` · ``noun_variation`` ·
  ``verb_variation`` · ``adj_variation`` · ``adv_variation``
- T06 (3): ``vocd_d`` · ``hdd`` · ``msttr``
- T07 (6): ``zipf_exponent`` · ``zipf_r2`` · ``zipf_mandelbrot_q`` ·
  ``zipf_mandelbrot_s`` · ``wordfreq_mean`` · ``wordfreq_rare_ratio``

Bütün fonksiyonlar saftır: girdi token listesi, çıktı sayı. NLP modeli
gerekmez — tokenizasyonu çağıran taraf yapmıştır.

**Kelime birimi (2026-09-15, Efe):** çeşitlilik ölçüleri küçük harfli,
noktalamasız **yüzey biçimleri** sayar — klasik literatürün (McCarthy &
Jarvis 2010, Covington & McFall 2010, Tweedie & Baayen 1998) birimi.
Listeyi T20 hazırlar. İstisnalar: ``*_variation`` lemma sayar (Lu 2012),
``n_lemma_count`` adı gereği lemma.

**K4 (2026-09-16, Efe):** ``0.0`` yalnız "ölçüldü ve sıfır çıktı" demektir.
Ölçülemeyen değer — boş girdi, en az uzunluğun altı, boş alt küme, tanımsız
formül, tek değerden yayılım — ``math.nan`` döner. Her fonksiyonun
docstring'i NaN durumlarını söyler. Hizasız girdi ve geçersiz parametre
``ValueError`` fırlatır.
"""

from __future__ import annotations

import math
import random
from collections import Counter

import numpy as np

from ..vocab import LEXICAL_POS, NON_WORD_POS, NOUN_POS

# Brunet's W üs sabiti — Kademe C.
#
# Kaynak OKUNDU: Tweedie, F. J. & Baayen, R. H. (1998), "How Variable May
# a Constant be? Measures of Lexical Richness in Perspective", Computers
# and the Humanities 32(5): 323-352, denklem (10), s. 328. Bağımsız ikinci
# kaynak: zipfR (CRAN, Evert & Baroni) aynı değeri kullanıyor.
#
# Birincil kaynak (Kademe A) çevrimiçi yok ve okunmadı:
#   Brunet, E. Vocabulaire de Jean Giraudoux: Structure et Évolution.
#   Genève: Slatkine, 1978.
#
# Bazı ikincil kaynaklar 0.165 veriyor. Tartışmalı olduğu için sabit
# gizlenmiyor: `FeatureParams.brunet_w_a` ile değiştirilebilir.
_BRUNET_A = 0.172


def rank_word_freq_table(tokens: list[str]) -> tuple[np.ndarray, int, int, list]:
    """Küçük harfe indirgenmiş frekans tablosu.

    Returns
    -------
    freqs : np.ndarray      azalan sıralı frekanslar
    N : int                 toplam token sayısı
    V : int                 tekil tip sayısı
    items : list            (kelime, frekans) çiftleri, azalan sıralı
    """
    counter = Counter(t.lower() for t in tokens)
    items = counter.most_common()
    freqs = np.array([f for _, f in items], dtype=np.int64)
    return freqs, int(freqs.sum()), len(items), items


def type_token_ratio(N: int, V: int) -> dict[str, float]:
    """Düz TTR = V / N.

    **Metin uzunluğuna bağımlıdır — bu kasıtlı.** TTR uzun metinlerde
    sistematik olarak düşer, çünkü metin uzadıkça aynı kelimeler tekrar
    eder. Aynı çeşitlilikteki iki metinden uzun olanı daha düşük TTR
    verir; farklı uzunluktaki metinleri TTR ile karşılaştırmak yanıltır.

    ``mattr``, ``mtld`` ve ``msttr`` tam olarak bunu düzeltmek için var.
    ``ttr`` yine de üretiliyor çünkü literatürün en çok raporladığı ölçüt
    bu ve kullanıcının eski çalışmalarla karşılaştırabilmesi gerekiyor.
    Kütüphane ölçer, yorumlamaz (K10) — ama kusuru gizlemez.
    """
    if N == 0:
        return {"ttr": math.nan}
    return {"ttr": round(V / N, 6)}


def shannon_entropy(freqs: np.ndarray) -> float:
    """Frekans dağılımının Shannon entropisi, bit cinsinden: ``-Σ p·log₂(p)``. Boşsa NaN."""
    N = freqs.sum()
    if N == 0:
        return math.nan
    p = freqs.astype(np.float64) / N
    return round(float(-np.sum(p * np.log2(p))), 6)


def yules_k(freqs: np.ndarray) -> float:
    """Yule's K = ``10000·(Σf² − N)/N²``. Tekrar yoğunluğu; yüksek = tekrarlı. Boşsa NaN."""
    N = int(freqs.sum())
    if N == 0:
        return math.nan
    S2 = np.sum(freqs.astype(np.float64) ** 2)   # ← float64 ŞART
    return round(10000 * (S2 - N) / (N ** 2), 2)


def simpsons_d(freqs: np.ndarray) -> float:
    """Simpson's D = ``Σ f(f−1) / (N(N−1))``.

    Metinden rastgele çekilen iki tokenin aynı tip olma olasılığı. ``N ≤ 1``
    → payda ``N(N−1)`` sıfır → NaN.
    """
    N = int(freqs.sum())
    if N <= 1:
        return math.nan
    f = freqs.astype(np.float64)
    return round(float(np.sum(f * (f - 1)) / (N * (N - 1))), 6)


def brunet_w(N: int, V: int, a: float = _BRUNET_A) -> dict[str, float]:
    """Brunet's W = ``N^(V^−a)``; ``N`` toplam token, ``V`` tekil tip.

    Parameters
    ----------
    N : int
        Toplam token sayısı.
    V : int
        Tekil tip sayısı.
    a : float
        Üs sabiti; varsayılan 0.172 (``FeatureParams.brunet_w_a``).
        Bazı ikincil kaynaklar 0.165 veriyor — fark çıktıda %8–16.
        Kademe C, gerekçe ``_BRUNET_A`` yorumunda.

    Notes
    -----
    Sabitten bağımsız olarak formülün şekli şunu garanti eder: V arttıkça
    üs küçülür ve W küçülür; V = 1 iken üs 1 olur ve W = N çıkar.
    """
    if N == 0 or V == 0:
        return {"brunet_w": math.nan}
    return {"brunet_w": round(float(N ** (V ** -a)), 4)}


def hapax_count(items: list) -> int:
    """Tam olarak bir kez geçen tip sayısı (ham sayım)."""
    return sum(1 for _, f in items if f == 1)


def hapax_ratio(items: list) -> dict[str, float]:
    """Bir kez geçen tip / toplam **tip** (V1 / V). Boşsa NaN.

    Paydası tip olduğu için "kelime dağarcığının ne kadarı tek kullanımlık"
    sorusunu yanıtlar. QUITA'nın ölçütü bu değil — o ``hapax_percentage``.
    """
    if not items:
        return {"hapax_ratio": math.nan}
    return {"hapax_ratio": round(hapax_count(items) / len(items), 6)}


def hapax_percentage(items: list) -> dict[str, float]:
    """Bir kez geçen tip / toplam **token** (V1 / N) — QUITA §6.1.6. Boşsa NaN.

    ``hapax_ratio`` ile payı aynı, paydası farklı: orada V (tip), burada N
    (token). 5 token / 3 tipin 2'si tek geçiyorsa yüzde 0.4, oran 0.667.
    İki ölçüt de tutuluyor (2026-09-18, Efe): QUITA karşılaştırması için
    yüzde, dağarcık okuması için oran.
    """
    if not items:
        return {"hapax_percentage": math.nan}
    n = sum(f for _, f in items)
    return {"hapax_percentage": round(hapax_count(items) / n, 6)}


def word_length_stats(tokens: list[str]) -> tuple[float, float]:
    """Kelime uzunluğunun ortalaması ve değişim katsayısı.

    Returns
    -------
    (ortalama, cv) : tuple[float, float]
        ``cv = std / ortalama``. Standart sapma **popülasyon** sapmasıdır
        (``ddof=0``) — elimizdeki token listesi örneklem değil, metnin
        kendisi.

    Not: bu **kelime** uzunluğunun değişkenliğidir, cümle uzunluğunun
    değil. Cümle versiyonu ayrı bir anahtar: ``sentence_length_cv``.

    Boşsa ikisi de NaN; tek kelimede CV NaN (tek değerden değişkenlik ölçülmez).
    """
    if not tokens:
        return (math.nan, math.nan)
    uzunluklar = np.array([len(t) for t in tokens], dtype=np.float64)
    ortalama = float(uzunluklar.mean())
    if len(tokens) < 2 or ortalama == 0.0:
        return (round(ortalama, 4), math.nan)
    cv = float(uzunluklar.std()) / ortalama
    return (round(ortalama, 4), round(cv, 4))


def rare_word_metrics(tokens: list[str]) -> dict[str, float]:
    """Sichel's S = V₂ / V — tam olarak iki kez geçen tiplerin oranı. Boşsa NaN."""
    if not tokens:
        return {"sichel_s": math.nan}
    sayim = Counter(tokens)
    V = len(sayim)
    V2 = sum(1 for f in sayim.values() if f == 2)
    return {"sichel_s": round(V2 / V, 6)}


def heaps_beta(tokens: list[str], min_tokens: int = 300,
               step: int = 50) -> dict[str, float]:
    """Heaps yasası ``V = K·N^β``; ``log V ~ β·log N`` regresyonunun eğimi.

    Metin uzadıkça kelime dağarcığının ne hızla büyüdüğünü ölçer.

    Ölçülemediği iki durumda NaN: metin ``min_tokens``'tan kısa, ya da
    5'ten az regresyon noktası düşüyor. ``0.0`` gerçek sıfır eğimdir (hep
    aynı kelime).

    β kırpılmaz (2026-09-17, Efe): tip sayısı hiç azalmadığı için eğim eksi
    olamaz, ama tekrarla başlayıp açılan metinde 1'i aşabilir ve olduğu gibi
    yazılır. Ölçek bu yüzden ``score``, ``ratio_0_1`` değil.
    """
    N = len(tokens)
    if N < min_tokens:
        return {"heaps_beta": math.nan}     # kısa metinde uydurma yapma

    nt: list[int] = []
    vt: list[int] = []
    for kesim in range(step, N + 1, step):
        nt.append(kesim)
        vt.append(len(set(tokens[:kesim])))

    if len(nt) < 5:                          # 5 noktadan az → regresyon güvenilmez
        return {"heaps_beta": math.nan}

    beta = float(np.polyfit(np.log(nt), np.log(vt), 1)[0])
    return {"heaps_beta": round(beta, 4) + 0.0}      # + 0.0: -0.0 → 0.0


# ── T05: pencereli ve eğri tabanlı zenginlik ──────────────────────────
#
# Pencere ve parça boyları (MATTR 50 kayan, entropy_std ve ttr_moving_slope
# 50'lik ayrık parça) 2026-09-15'te geçici kabul edildi; Efe'nin notuyla
# ileride yeniden gözden geçirilecek.


def _hizala(lemma_tokens: list[str], pos_data: list[tuple[str, str]]) -> list[str]:
    """``pos_data``'dan kelime dışı (PUNCT, SYM) atılmış etiketler.

    Sonuç ``lemma_tokens`` ile hizalı olmalı.

    ``lemma_tokens``'a bunlar girmez, ``pos_data``'ya girer (T21). Uzunluklar
    tutmuyorsa bu metnin özelliği değil ön işleme hatasıdır → ``ValueError``
    (2026-09-16, Efe).
    """
    kelime_pos = [p for _, p in pos_data if p not in NON_WORD_POS]
    if len(kelime_pos) != len(lemma_tokens):
        raise ValueError(
            f"lemma_tokens ({len(lemma_tokens)}) is not aligned with pos_data after "
            f"non-word tokens were dropped ({len(kelime_pos)}) — preprocessing error"
        )
    return kelime_pos


def _parcalar(tokens: list[str], boy: int) -> list[list[str]]:
    """Üst üste binmeyen tam parçalar; sondaki eksik parça atılır.

    Eksik parçanın entropisi ve TTR'si başka boydaki parçalarla
    karşılaştırılamaz — kısa parça kendiliğinden yüksek TTR verir.
    """
    if boy <= 0:
        return []
    return [tokens[i:i + boy] for i in range(0, len(tokens) - boy + 1, boy)]


def advanced_lexical_richness(tokens: list[str], window: int = 50) -> dict[str, float]:
    """MATTR, entropy_std, Herdan-C.

    - ``mattr`` — 1'er kayan ``window``'luk pencerelerin TTR ortalaması
      (Covington & McFall 2010). **2 × window**'dan kısa metinde NaN
      (2026-09-23, Efe). Eski eşik ``window``'du ve metin tam pencere
      boyundayken tek pencere kalıyordu: ortalama alacak bir şey olmuyor,
      MATTR matematiksel olarak düz TTR'a çöküyordu — yani düzeltmek için
      var olduğu şeye dönüşüp bunu sessizce yapıyordu.
    - ``entropy_std`` — ``window``'luk **ayrık** parçaların entropileri (bit)
      arasındaki popülasyon sapması (2026-09-15, Efe). 2'den az tam parça → NaN.
    - ``herdan_c`` — ``log V / log N``; taban oranda sadeleşir. ``N = 1`` → NaN.

    ``bigram_entropy`` 2026-09-15'te çıkarıldı (Efe): lemma çiftlerinin çoğu
    tek seferlik olduğundan değer metin uzunluğunu izliyordu.
    """
    N = len(tokens)
    if window <= 0:
        raise ValueError(f"window must be positive: {window}")
    if N == 0:
        return {"mattr": math.nan, "entropy_std": math.nan, "herdan_c": math.nan}
    V = len(set(tokens))

    if N < 2 * window:            # tek/az pencere = ortalama değil, bkz. docstring
        mattr = math.nan
    else:
        sayim = Counter(tokens[:window])
        toplam = len(sayim)
        for i in range(window, N):
            eski = tokens[i - window]
            sayim[eski] -= 1
            if sayim[eski] == 0:
                del sayim[eski]
            sayim[tokens[i]] += 1
            toplam += len(sayim)
        mattr = toplam / ((N - window + 1) * window)

    parcalar = _parcalar(tokens, window)
    if len(parcalar) >= 2:
        entropiler = [shannon_entropy(np.array(list(Counter(p).values()), dtype=np.float64))
                      for p in parcalar]
        entropy_std = float(np.std(entropiler))
    else:
        entropy_std = math.nan

    herdan = math.log(V) / math.log(N) if N > 1 else math.nan
    return {"mattr": round(mattr, 5), "entropy_std": round(entropy_std, 5),
            "herdan_c": round(herdan, 5)}


def _mtld_tek_yon(tokens: list[str], esik: float) -> float:
    """Tek yönde MTLD: toplam token / faktör sayısı. Faktör yoksa NaN."""
    faktor = 0.0
    tipler: set[str] = set()
    sayac = 0
    ttr = 1.0
    for t in tokens:
        tipler.add(t)
        sayac += 1
        ttr = len(tipler) / sayac
        if ttr <= esik:                     # faktör 0.72'ye ulaşınca biter
            faktor += 1
            tipler = set()
            sayac = 0
    if sayac > 0:                           # artık kısım → kısmi faktör
        faktor += (1 - ttr) / (1 - esik)
    return len(tokens) / faktor if faktor > 0 else math.nan


def mtld(tokens: list[str], threshold: float = 0.72,
         min_tokens: int = 100) -> dict[str, float]:
    """Measure of Textual Lexical Diversity (McCarthy & Jarvis 2010).

    TTR ``threshold``'a düşene kadar geçen ortalama kelime sayısı; ileri ve
    geri yönün ortalaması. Eşik Kademe C (iki ikincil kaynak). Metin boyunca
    hiç faktör oluşmazsa (tamamen tekrarsız metin) formül sıfıra bölünür → NaN.

    ``min_tokens`` (100): McCarthy & Jarvis (2010, s. 384) "texts as short as
    100 tokens can be used. Texts shorter than this […] their accuracy is
    questionable" — daha kısa metinde NaN (2026-09-16, Efe).
    """
    if len(tokens) < max(min_tokens, 1):
        return {"mtld": math.nan}
    ileri = _mtld_tek_yon(tokens, threshold)
    geri = _mtld_tek_yon(tokens[::-1], threshold)
    return {"mtld": round((ileri + geri) / 2, 4)}


def dugast_u(tokens: list[str]) -> dict[str, float]:
    """Dugast'ın Uber indeksi ``U = (log₁₀ N)² / (log₁₀ N − log₁₀ V)``.

    Taban 10 (2026-09-15, Efe): quanteda ve koRpus ile aynı. Taban sonucu
    ölçekler (ln ile 2.3 kat), sıralamayı değiştirmez. ``N < 2`` ya da
    ``N == V`` (payda 0) → NaN. ``V = 1`` tanımlıdır: ``U = log₁₀ N``.
    """
    N = len(tokens)
    V = len(set(tokens))
    if N < 2 or N == V:
        return {"dugast_u": math.nan}
    return {"dugast_u": round(math.log10(N) ** 2 / (math.log10(N) - math.log10(V)), 4)}


def guiraud_r(tokens: list[str]) -> dict[str, float]:
    """Guiraud kökü ``R = V / √N`` (Guiraud 1960). Boşsa NaN."""
    if not tokens:
        return {"guiraud_r": math.nan}
    return {"guiraud_r": round(len(set(tokens)) / math.sqrt(len(tokens)), 5)}


def ttr_moving_slope(tokens: list[str], chunk_size: int = 50) -> dict[str, float]:
    """Ayrık ``chunk_size``'lık parçaların TTR'lerine doğrusal eğim.

    Negatif = metnin sonuna doğru kelime tekrarı artıyor. Parça boyu sabit
    (2026-09-15, Efe): plandaki "4 eşit parça" hem 4 noktadan oynak eğim
    veriyordu hem de uzun metinde parçaları uzatıp eğimi uzunluğa bağlıyordu.
    Sondaki eksik parça atılır; 2'den az tam parça → NaN.
    """
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be positive: {chunk_size}")
    parcalar = _parcalar(tokens, chunk_size)
    if len(parcalar) < 2:
        return {"ttr_moving_slope": math.nan}
    ttrler = [len(set(p)) / len(p) for p in parcalar]
    egim = float(np.polyfit(np.arange(len(ttrler), dtype=np.float64), ttrler, 1)[0])
    return {"ttr_moving_slope": round(egim, 5)}


def pos_lexical_variation(lemma_tokens: list[str],
                          pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """Sözcük türü çeşitliliği — Lu (2012), The Modern Language Journal 96(2), Tablo 2.

    - ``verb_variation`` = VV1 = ``T_verb / N_verb`` (Harley & King 1989)
    - ``noun_variation`` = NV = ``T_noun / N_lex`` (McClure 1991)
    - ``adj_variation`` = AdjV = ``T_adj / N_lex``
    - ``adv_variation`` = AdvV = ``T_adv / N_lex``

    ``T`` farklı **lemma** sayısı (Lu s. 196: örneklem lemmalanmıştı).
    İsim = ``NOUN_POS`` (NOUN + PROPN); ``N_lex`` = ``LEXICAL_POS`` token
    sayısı (2026-09-16, Efe). ``AUX`` hiçbir yerde sayılmaz. Lu'nun zarf
    sınırlaması (-ly) Türkçeye aktarılamadığı için bütün ADV sayılır.
    İngilizcede asıl fiil ``be``/``have`` VERB etiketi aldığında sayılır —
    Lu saymıyor; liste gerektirdiği için bilinçli sapma.

    NaN: sözcüksel kelime yoksa NV/AdjV/AdvV, fiil yoksa VV1. Sözcüksel kelime
    var ama sıfat yoksa AdjV gerçek sıfırdır. Hizasız girdi → ``ValueError``.
    """
    kelime_pos = _hizala(lemma_tokens, pos_data)
    sonuc = {"noun_variation": math.nan, "verb_variation": math.nan,
             "adj_variation": math.nan, "adv_variation": math.nan}
    siniflar = {"noun": NOUN_POS, "verb": ("VERB",), "adj": ("ADJ",), "adv": ("ADV",)}
    tipler: dict[str, set[str]] = {s: set() for s in siniflar}
    fiil_token = 0
    n_lex = 0
    for lem, p in zip(lemma_tokens, kelime_pos):
        if p in LEXICAL_POS:
            n_lex += 1
        fiil_token += p == "VERB"
        for sinif, etiketler in siniflar.items():
            if p in etiketler:
                tipler[sinif].add(lem)
    if n_lex:
        for sinif in ("noun", "adj", "adv"):
            sonuc[f"{sinif}_variation"] = round(len(tipler[sinif]) / n_lex, 5)
    if fiil_token:
        sonuc["verb_variation"] = round(len(tipler["verb"]) / fiil_token, 5)
    return sonuc


# ── T06: örneklemeli çeşitlilik ───────────────────────────────────────
#
# Kaynak: McCarthy & Jarvis (2010), Behavior Research Methods 42(2), s. 383–385
# (Kademe A; tlf-kaynaklar/2010-BRM-42__McCarthy-Jarvis__MTLD-vocd-HDD__BIRINCIL.pdf).
# Girdi: küçük harfli, noktalamasız yüzey biçimler (2026-09-15, Efe).


def _vocd_model(D: float, n: int) -> float:
    """voc-D kuramsal eğrisi ``TTR(n) = (D/n)·(√(1 + 2n/D) − 1)``."""
    return (D / n) * (math.sqrt(1 + 2 * n / D) - 1)


def _vocd_uydur(boylar: list[int], ttrler: list[float]) -> float:
    """Ölçülen TTR eğrisine en küçük kareler anlamında en iyi uyan D.

    Model D'de monoton olduğundan hata tek dipli; log D üzerinde altın oran
    araması yeterli. Arama aralığı [0.01, 100000]: tamamen tekrarsız metinde
    D sonsuza gider ve üst sınıra yapışır.
    """
    def hata(log_d: float) -> float:
        D = math.exp(log_d)
        return sum((_vocd_model(D, n) - t) ** 2 for n, t in zip(boylar, ttrler))

    a, b = math.log(0.01), math.log(100_000.0)
    oran = (math.sqrt(5) - 1) / 2
    c, d = b - oran * (b - a), a + oran * (b - a)
    for _ in range(200):
        if hata(c) < hata(d):
            b, d = d, c
            c = b - oran * (b - a)
        else:
            a, c = c, d
            d = a + oran * (b - a)
    return math.exp((a + b) / 2)


def vocd_d(tokens: list[str], sample_min: int = 35, sample_max: int = 50,
           num_samples: int = 100, num_runs: int = 3, min_tokens: int = 50,
           random_seed: int = 42) -> dict[str, float]:
    """voc-D (McKee, Malvern & Richards 2000; tarif McCarthy & Jarvis 2010, s. 383).

    35, 36, …, 50 tokenlik her boy için ``num_samples`` rastgele örneklem
    (yerine koymadan) çekilir, ortalama TTR eğrisine D uydurulur. Tüm işlem
    ``num_runs`` kez yapılıp D'ler ortalanır. Özgün ayarlar 100 örneklem ve
    3 tur (2026-09-15, Efe — plandaki 30 örneklem düzeltildi).

    Kendi ``random.Random(random_seed)`` üretecini kullanır; global ``random``
    durumuna dokunmaz. Metin ``min_tokens``'tan ya da en büyük örneklemden
    kısaysa NaN. Geçersiz parametre → ``ValueError``.
    """
    if sample_min < 1 or sample_min > sample_max or num_samples < 1 or num_runs < 1:
        raise ValueError(
            f"Invalid voc-D parameters: sample_min={sample_min}, sample_max={sample_max}, "
            f"num_samples={num_samples}, num_runs={num_runs}"
        )
    N = len(tokens)
    if N < max(min_tokens, sample_max):
        return {"vocd_d": math.nan}
    rng = random.Random(random_seed)
    boylar = list(range(sample_min, sample_max + 1))
    dler = []
    for _ in range(num_runs):
        ttrler = [
            sum(len(set(rng.sample(tokens, n))) / n for _ in range(num_samples)) / num_samples
            for n in boylar
        ]
        dler.append(_vocd_uydur(boylar, ttrler))
    return {"vocd_d": round(sum(dler) / len(dler), 4)}


def hdd(tokens: list[str], sample_size: int = 42) -> dict[str, float]:
    """HD-D (McCarthy & Jarvis 2007; 2010 s. 383): 42'lik örneklemin beklenen TTR'si.

    Her tip için hipergeometrik dağılımdan "örneklemde en az bir kez görülme"
    olasılığı ``1 − C(N−f, n)/C(N, n)``; olasılıklar toplanıp ``n``'e bölünür
    (0–1 ölçeği, 2026-09-15, Efe). Makale ham toplamı (0–42) raporluyor;
    bölmek sıralamayı değiştirmez.

    Metin ``sample_size``'dan kısaysa NaN.

    ``C(N−f, n)/C(N, n) = Π_{i<n} (N−f−i)/(N−i)`` olarak kayan noktada
    hesaplanır — büyük N'de dev tamsayılar üretmez. ``N − f < n`` ise tip
    örnekleme **kesinlikle** girer, görülmeme olasılığı 0.
    """
    if sample_size < 1:
        raise ValueError(f"sample_size must be positive: {sample_size}")
    N = len(tokens)
    if N < sample_size:
        return {"hdd": math.nan}
    frekans_sayilari = Counter(Counter(tokens).values())   # f → o frekanstaki tip sayısı
    toplam = 0.0
    for f, tip_sayisi in frekans_sayilari.items():
        if N - f < sample_size:
            gorulmeme = 0.0
        else:
            gorulmeme = 1.0
            for i in range(sample_size):
                gorulmeme *= (N - f - i) / (N - i)
        toplam += tip_sayisi * (1.0 - gorulmeme)
    return {"hdd": round(toplam / sample_size, 5)}


def msttr(tokens: list[str], segment_size: int = 100) -> dict[str, float]:
    """Mean Segmental TTR (Johnson 1944): tam segmentlerin TTR ortalaması.

    McCarthy & Jarvis (2010, s. 385): "segments of a set length (typically,
    100 words). The remaining words are discarded." Tam segment yoksa NaN
    (2026-09-16, Efe).
    """
    if segment_size <= 0:
        raise ValueError(f"segment_size must be positive: {segment_size}")
    parcalar = _parcalar(tokens, segment_size)
    if not parcalar:
        return {"msttr": math.nan}
    return {"msttr": round(sum(len(set(p)) / len(p) for p in parcalar) / len(parcalar), 5)}


# ── T07: Zipf, Zipf-Mandelbrot, referans frekans ──────────────────────
#
# Eğim yöntemi (2026-09-16, Efe): klasik log-log en küçük kareler — sıra ve
# sıklık aynı metinden. Piantadosi (2014, s. 3) bunun sıra ve sıklık
# hatalarını ilişkilendirdiğini, özellikle nadir kelimelerde sahte düzen
# ürettiğini gösteriyor; ikiye bölme çözümü literatürdeki değerlerle
# karşılaştırılabilirliği bozacağı için uygulanmadı. Değerler bu bilinen
# yanlılığı taşır.


def zipf(freqs: np.ndarray) -> dict[str, float]:
    """Zipf yasası: ``log f(r) ~ −α·log r`` doğrusal regresyonu.

    ``zipf_exponent`` α (pozitife çevrilmiş), ``zipf_r2`` log-log uyum
    kalitesi. 10 sıradan az veride regresyon anlamsız → ikisi de NaN.
    Bütün frekanslar eşitse eğim 0 (tanımlı), R² = 0/0 → NaN.
    """
    if len(freqs) < 10:
        return {"zipf_exponent": math.nan, "zipf_r2": math.nan}
    log_s = np.log(np.arange(1, len(freqs) + 1, dtype=np.float64))
    log_f = np.log(freqs.astype(np.float64))
    egim, kesim = np.polyfit(log_s, log_f, 1)
    tahmin = egim * log_s + kesim
    ss_res = float(np.sum((log_f - tahmin) ** 2))
    ss_tot = float(np.sum((log_f - log_f.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 1e-12 else math.nan   # eşit frekans: 0/0
    return {"zipf_exponent": round(abs(float(egim)), 4), "zipf_r2": round(r2, 4)}


def zipf_mandelbrot(freqs: np.ndarray) -> dict[str, float]:
    """Zipf-Mandelbrot ``f(r) = C / (r + q)^s``.

    ``q`` 0–10 arasında 0.1 adımlı ızgarada aranır; her aday için
    ``log f ~ −s·log(r + q)`` doğrusal regresyonu yapılır, artık kareler
    toplamı en küçük olan seçilir. scipy bağımlılığı eklememek için ızgara.
    10 sıradan az veride NaN.
    """
    if len(freqs) < 10:
        return {"zipf_mandelbrot_q": math.nan, "zipf_mandelbrot_s": math.nan}
    siralar = np.arange(1, len(freqs) + 1, dtype=np.float64)
    log_f = np.log(freqs.astype(np.float64))
    en_iyi = (math.inf, 0.0, 0.0)            # (hata, q, s)
    for q in np.round(np.arange(0.0, 10.0 + 1e-9, 0.1), 1):
        log_rq = np.log(siralar + q)
        egim, kesim = np.polyfit(log_rq, log_f, 1)
        hata = float(np.sum((log_f - (egim * log_rq + kesim)) ** 2))
        if hata < en_iyi[0]:
            en_iyi = (hata, float(q), abs(float(egim)))
    return {"zipf_mandelbrot_q": round(en_iyi[1], 4), "zipf_mandelbrot_s": round(en_iyi[2], 4)}


# Düşük sıklık sınırı — van Heuven ve ark. (2014), QJEP 67(6), Tablo 1 notu:
# "Words with Zipf values of 3 or lower are low-frequency words". Zipf 3 =
# milyon kelimede bir geçiş. Kademe A.
_NADIR_ESIK = 3.0


def reference_frequency_sophistication(lemma_tokens: list[str],
                                       pos_data: list[tuple[str, str]],
                                       lang: str = "tr") -> dict[str, float]:
    """Sözcük seçkinliği — metnin kelimeleri genel dilde ne kadar yaygın.

    Kararlar (2026-09-16, Efe):

    - Yalnız **anlamlı kelimeler** (``LEXICAL_POS``) ve **lemma** ile sorgulanır
      — Lu (2012) gibi. Türkçede çekimli biçimler wordfreq listesinde yok;
      yüzey biçimle "kitaplarımızdan" nadir görünürdü.
    - ``wordfreq_mean`` — anlamlı kelime tokenlerinin ortalama wordfreq Zipf
      puanı (log₁₀ milyar kelimedeki geçiş; 3 = milyonda bir). Listede
      olmayan kelime **0 puan** alır (wordfreq'in kendi kuralı).
    - ``wordfreq_rare_ratio`` — Zipf puanı **≤ 3** olan (milyonda bir ya da
      daha seyrek) anlamlı kelime tokeni oranı; van Heuven ve ark. (2014)
      Tablo 1'in düşük sıklık tanımı (2026-09-16, Efe). "En sık 2000 dışı"
      (Lu 2012) Türkçe listesi çekimli biçimlerle dolu olduğu için seçilmedi.

    Hizalama ``pos_lexical_variation`` ile aynı (hizasız → ``ValueError``).
    Anlamlı kelime yoksa NaN. wordfreq kurulu değilse ikisi de NaN **ve**
    ``MissingDependencyWarning`` (2026-09-16, Efe).
    """
    olculemedi = {"wordfreq_mean": math.nan, "wordfreq_rare_ratio": math.nan}
    try:
        from wordfreq import zipf_frequency
    except ImportError:
        # Sessiz kalmak yasak (2026-08-25): kullanıcı NaN'ın nedenini bilmeli.
        from .._warnings import uyar_eksik_bagimlilik
        uyar_eksik_bagimlilik("wordfreq", "wordfreq_* (2 features)")
        return olculemedi
    kelime_pos = _hizala(lemma_tokens, pos_data)
    anlamli = [lem for lem, p in zip(lemma_tokens, kelime_pos) if p in LEXICAL_POS]
    if not anlamli:
        return olculemedi
    puanlar = [zipf_frequency(lem, lang) for lem in anlamli]
    nadir = sum(1 for puan in puanlar if puan <= _NADIR_ESIK)
    return {"wordfreq_mean": round(sum(puanlar) / len(puanlar), 4),
            "wordfreq_rare_ratio": round(nadir / len(anlamli), 5)}
