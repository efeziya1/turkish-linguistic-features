"""Sözcüksel temel: frekans tablosu ve klasik kelime zenginliği ölçütleri.

Bu modül 10 öznitelik anahtarı üretir (`lexical` grubunun 33'ünden):
``ttr`` · ``entropy`` · ``yule_k`` · ``simpson_d`` · ``brunet_w`` ·
``hapax_ratio`` · ``avg_word_length`` · ``word_length_cv`` · ``sichel_s`` ·
``heaps_beta``.

Bütün fonksiyonlar saftır: girdi token listesi, çıktı sayı. NLP modeli
gerekmez — tokenizasyonu çağıran taraf yapmıştır.

Boş ve tek elemanlı girdide hiçbiri çökmez; ölçülemeyen değer ``0.0``
döner. ``0.0`` burada "ölçülemedi" değil **"ölçüldü ve sıfır çıktı"**
anlamına gelir; tek istisnası ``heaps_beta``, docstring'inde yazılı.
"""

from __future__ import annotations

from collections import Counter

import numpy as np

# Brunet's W üs sabiti — Kademe C (bkz. 00-ANA-PLAN.md K12 eki-2).
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
    M : int                 toplam token sayısı
    N : int                 tekil tip sayısı
    items : list            (kelime, frekans) çiftleri, azalan sıralı
    """
    counter = Counter(t.lower() for t in tokens)
    items = counter.most_common()
    freqs = np.array([f for _, f in items], dtype=np.int64)
    return freqs, int(freqs.sum()), len(items), items


def type_token_ratio(M: int, V: int) -> dict[str, float]:
    """Düz TTR = V / M.

    **Metin uzunluğuna bağımlıdır — bu kasıtlı.** TTR uzun metinlerde
    sistematik olarak düşer, çünkü metin uzadıkça aynı kelimeler tekrar
    eder. Aynı çeşitlilikteki iki metinden uzun olanı daha düşük TTR
    verir; farklı uzunluktaki metinleri TTR ile karşılaştırmak yanıltır.

    ``mattr``, ``mtld`` ve ``msttr`` tam olarak bunu düzeltmek için var.
    ``ttr`` yine de üretiliyor çünkü literatürün en çok raporladığı ölçüt
    bu ve kullanıcının eski çalışmalarla karşılaştırabilmesi gerekiyor.
    Kütüphane ölçer, yorumlamaz (K10) — ama kusuru gizlemez.
    """
    if M == 0:
        return {"ttr": 0.0}
    return {"ttr": round(V / M, 6)}


def shannon_entropy(freqs: np.ndarray) -> float:
    """Frekans dağılımının Shannon entropisi, bit cinsinden: ``-Σ p·log₂(p)``."""
    M = freqs.sum()
    if M == 0:
        return 0.0
    p = freqs.astype(np.float64) / M
    return round(float(-np.sum(p * np.log2(p))), 6)


def yules_k(freqs: np.ndarray) -> float:
    """Yule's K = ``10000·(Σf² − M)/M²``. Tekrar yoğunluğu; yüksek = tekrarlı."""
    M = int(freqs.sum())
    if M <= 1:
        return 0.0
    S2 = np.sum(freqs.astype(np.float64) ** 2)   # ← float64 ŞART
    return round(10000 * (S2 - M) / (M ** 2), 2)


def simpsons_d(freqs: np.ndarray) -> float:
    """Simpson's D = ``Σ f(f−1) / (M(M−1))``.

    Metinden rastgele çekilen iki tokenin aynı tip olma olasılığı.
    """
    M = int(freqs.sum())
    if M <= 1:
        return 0.0
    f = freqs.astype(np.float64)
    return round(float(np.sum(f * (f - 1)) / (M * (M - 1))), 6)


def brunet_w(M: int, V: int, a: float = _BRUNET_A) -> dict[str, float]:
    """Brunet's W = ``M^(V^−a)``; ``M`` toplam token, ``V`` tekil tip.

    Parameters
    ----------
    M : int
        Toplam token sayısı (kaynakta ``N``).
    V : int
        Tekil tip sayısı.
    a : float
        Üs sabiti; varsayılan 0.172 (``FeatureParams.brunet_w_a``).
        Bazı ikincil kaynaklar 0.165 veriyor — fark çıktıda %8–16.
        Kademe C, gerekçe ``_BRUNET_A`` yorumunda.

    Notes
    -----
    Sabitten bağımsız olarak formülün şekli şunu garanti eder: V arttıkça
    üs küçülür ve W küçülür; V = 1 iken üs 1 olur ve W = M çıkar.
    """
    if M == 0 or V == 0:
        return {"brunet_w": 0.0}
    return {"brunet_w": round(float(M ** (V ** -a)), 4)}


def hapax_count(items: list) -> int:
    """Tam olarak bir kez geçen tip sayısı (ham sayım)."""
    return sum(1 for _, f in items if f == 1)


def hapax_ratio(items: list) -> dict[str, float]:
    """Bir kez geçen tip / toplam tip."""
    if not items:
        return {"hapax_ratio": 0.0}
    return {"hapax_ratio": round(hapax_count(items) / len(items), 6)}


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
    """
    if not tokens:
        return (0.0, 0.0)
    uzunluklar = np.array([len(t) for t in tokens], dtype=np.float64)
    ortalama = float(uzunluklar.mean())
    if ortalama == 0.0:
        return (0.0, 0.0)
    cv = float(uzunluklar.std()) / ortalama
    return (round(ortalama, 4), round(cv, 4))


def rare_word_metrics(lemma_tokens: list[str]) -> dict[str, float]:
    """Sichel's S = V₂ / V — tam olarak iki kez geçen tiplerin oranı."""
    if not lemma_tokens:
        return {"sichel_s": 0.0}
    sayim = Counter(lemma_tokens)
    V = len(sayim)
    V2 = sum(1 for f in sayim.values() if f == 2)
    return {"sichel_s": round(V2 / V, 6)}


def heaps_beta(lemma_tokens: list[str], min_tokens: int = 300,
               step: int = 50) -> dict[str, float]:
    """Heaps yasası ``V = K·N^β``; ``log V ~ β·log N`` regresyonunun eğimi.

    Metin uzadıkça kelime dağarcığının ne hızla büyüdüğünü ölçer.

    ``0.0`` burada iki anlama gelebilir ve ayırt edilemez: gerçekten
    sıfır eğim (hep aynı kelime), ya da **ölçülemedi**. Ölçülemediği iki
    durum: metin ``min_tokens``'tan kısa, ya da 5'ten az regresyon
    noktası düşüyor. Kısa metinde uydurma değer üretmektense sıfır
    yazılıyor.

    β her zaman ``[0, 1]`` aralığına kırpılır — kısa veya tekrarlı
    metinlerde regresyon 1'den büyük ya da negatif çıkabilir, ikisi de
    anlamsızdır.
    """
    N = len(lemma_tokens)
    if N < min_tokens:
        return {"heaps_beta": 0.0}          # kısa metinde uydurma yapma

    nt: list[int] = []
    vt: list[int] = []
    for kesim in range(step, N + 1, step):
        nt.append(kesim)
        vt.append(len(set(lemma_tokens[:kesim])))

    if len(nt) < 5:                          # 5 noktadan az → regresyon güvenilmez
        return {"heaps_beta": 0.0}

    beta = float(np.polyfit(np.log(nt), np.log(vt), 1)[0])
    return {"heaps_beta": round(float(np.clip(beta, 0.0, 1.0)), 4)}
