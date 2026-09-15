"""Sözcüksel temel: frekans tablosu ve klasik kelime zenginliği ölçütleri.

Bu modül 21 öznitelik anahtarı üretir (`lexical` grubunun 31'inden):

- T04 (10): ``ttr`` · ``entropy`` · ``yule_k`` · ``simpson_d`` · ``brunet_w`` ·
  ``hapax_ratio`` · ``avg_word_length`` · ``word_length_cv`` · ``sichel_s`` ·
  ``heaps_beta``
- T05 (11): ``mattr`` · ``entropy_std`` · ``herdan_c`` · ``mtld`` ·
  ``dugast_u`` · ``guiraud_r`` · ``ttr_moving_slope`` · ``noun_variation`` ·
  ``verb_variation`` · ``adj_variation`` · ``adv_variation``

Bütün fonksiyonlar saftır: girdi token listesi, çıktı sayı. NLP modeli
gerekmez — tokenizasyonu çağıran taraf yapmıştır.

Boş ve tek elemanlı girdide hiçbiri çökmez; ölçülemeyen değer ``0.0``
döner. ``0.0`` burada "ölçülemedi" değil **"ölçüldü ve sıfır çıktı"**
anlamına gelir; tek istisnası ``heaps_beta``, docstring'inde yazılı.
"""

from __future__ import annotations

import math
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


# ── T05: pencereli ve eğri tabanlı zenginlik ──────────────────────────
#
# Pencere ve parça boyları (MATTR 50 kayan, entropy_std ve ttr_moving_slope
# 50'lik ayrık parça) 2026-09-15'te geçici kabul edildi; Efe'nin notuyla
# ileride yeniden gözden geçirilecek (00-ANA-PLAN.md §0 "Açık notlar").


def _parcalar(tokens: list[str], boy: int) -> list[list[str]]:
    """Üst üste binmeyen tam parçalar; sondaki eksik parça atılır.

    Eksik parçanın entropisi ve TTR'si başka boydaki parçalarla
    karşılaştırılamaz — kısa parça kendiliğinden yüksek TTR verir.
    """
    if boy <= 0:
        return []
    return [tokens[i:i + boy] for i in range(0, len(tokens) - boy + 1, boy)]


def advanced_lexical_richness(lemma_tokens: list[str], window: int = 50) -> dict[str, float]:
    """MATTR, entropy_std, Herdan-C.

    - ``mattr`` — 1'er kayan ``window``'luk pencerelerin TTR ortalaması
      (Covington & McFall 2010). Metin pencereden kısaysa düz TTR.
    - ``entropy_std`` — ``window``'luk **ayrık** parçaların entropileri (bit)
      arasındaki popülasyon sapması (2026-09-15, Efe). 2'den az tam parça → 0.0.
    - ``herdan_c`` — ``log V / log N``; taban oranda sadeleşir.

    ``bigram_entropy`` 2026-09-15'te çıkarıldı (Efe): lemma çiftlerinin çoğu
    tek seferlik olduğundan değer metin uzunluğunu izliyordu.
    """
    N = len(lemma_tokens)
    if N == 0:
        return {"mattr": 0.0, "entropy_std": 0.0, "herdan_c": 0.0}
    V = len(set(lemma_tokens))

    if N <= window or window <= 0:
        mattr = V / N
    else:
        sayim = Counter(lemma_tokens[:window])
        toplam = len(sayim)
        for i in range(window, N):
            eski = lemma_tokens[i - window]
            sayim[eski] -= 1
            if sayim[eski] == 0:
                del sayim[eski]
            sayim[lemma_tokens[i]] += 1
            toplam += len(sayim)
        mattr = toplam / ((N - window + 1) * window)

    parcalar = _parcalar(lemma_tokens, window)
    if len(parcalar) >= 2:
        entropiler = [shannon_entropy(np.array(list(Counter(p).values()), dtype=np.float64))
                      for p in parcalar]
        entropy_std = float(np.std(entropiler))
    else:
        entropy_std = 0.0

    herdan = math.log(V) / math.log(N) if N > 1 else 0.0
    return {"mattr": round(mattr, 5), "entropy_std": round(entropy_std, 5),
            "herdan_c": round(herdan, 5)}


def _mtld_tek_yon(tokens: list[str], esik: float) -> float:
    """Tek yönde MTLD: toplam token / faktör sayısı. Faktör yoksa 0.0."""
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
    return len(tokens) / faktor if faktor > 0 else 0.0


def mtld(lemma_tokens: list[str], threshold: float = 0.72) -> dict[str, float]:
    """Measure of Textual Lexical Diversity (McCarthy & Jarvis 2010).

    TTR ``threshold``'a düşene kadar geçen ortalama kelime sayısı; ileri ve
    geri yönün ortalaması. Eşik Kademe C (iki ikincil kaynak). Metin boyunca
    hiç faktör oluşmazsa (tamamen tekrarsız kısa metin) formül sıfıra bölünür
    → 0.0 (K4, 2026-09-15, Efe).
    """
    if not lemma_tokens:
        return {"mtld": 0.0}
    ileri = _mtld_tek_yon(lemma_tokens, threshold)
    geri = _mtld_tek_yon(lemma_tokens[::-1], threshold)
    return {"mtld": round((ileri + geri) / 2, 4)}


def dugast_u(lemma_tokens: list[str]) -> dict[str, float]:
    """Dugast'ın Uber indeksi ``U = (log₁₀ N)² / (log₁₀ N − log₁₀ V)``.

    Taban 10 (2026-09-15, Efe): quanteda ve koRpus ile aynı. Taban sonucu
    ölçekler (ln ile 2.3 kat), sıralamayı değiştirmez. ``N == V`` → payda 0 → 0.0.
    """
    N = len(lemma_tokens)
    V = len(set(lemma_tokens))
    if N < 2 or V < 2 or N == V:
        return {"dugast_u": 0.0}
    return {"dugast_u": round(math.log10(N) ** 2 / (math.log10(N) - math.log10(V)), 4)}


def guiraud_r(lemma_tokens: list[str]) -> dict[str, float]:
    """Guiraud kökü ``R = V / √N`` (Guiraud 1960)."""
    if not lemma_tokens:
        return {"guiraud_r": 0.0}
    return {"guiraud_r": round(len(set(lemma_tokens)) / math.sqrt(len(lemma_tokens)), 5)}


def ttr_moving_slope(lemma_tokens: list[str], chunk_size: int = 50) -> dict[str, float]:
    """Ayrık ``chunk_size``'lık parçaların TTR'lerine doğrusal eğim.

    Negatif = metnin sonuna doğru kelime tekrarı artıyor. Parça boyu sabit
    (2026-09-15, Efe): plandaki "4 eşit parça" hem 4 noktadan oynak eğim
    veriyordu hem de uzun metinde parçaları uzatıp eğimi uzunluğa bağlıyordu.
    Sondaki eksik parça atılır; 2'den az tam parça → 0.0.
    """
    parcalar = _parcalar(lemma_tokens, chunk_size)
    if len(parcalar) < 2:
        return {"ttr_moving_slope": 0.0}
    ttrler = [len(set(p)) / len(p) for p in parcalar]
    egim = float(np.polyfit(np.arange(len(ttrler), dtype=np.float64), ttrler, 1)[0])
    return {"ttr_moving_slope": round(egim, 5)}


_VARYASYON_POS = ("NOUN", "VERB", "ADJ", "ADV")


def pos_lexical_variation(lemma_tokens: list[str],
                          pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """POS sınıfına kısıtlanmış TTR (Lu 2011): benzersiz lemma / o sınıfın tokeni.

    Yalnız ``NOUN`` (``PROPN`` değil), yalnız ``VERB`` (``AUX`` değil) —
    2026-09-15, Efe.

    Hizalama: ``lemma_tokens``'a noktalama girmez, ``pos_data``'ya girer (T21).
    Bu yüzden ``pos_data``'dan önce ``PUNCT`` atılır; listeler yine eşit
    uzunlukta değilse çökmek yerine hepsi 0.0 döner.
    """
    kelime_pos = [p for _, p in pos_data if p != "PUNCT"]
    sonuc = {f"{p.lower()}_variation": 0.0 for p in _VARYASYON_POS}
    if not lemma_tokens or len(kelime_pos) != len(lemma_tokens):
        return sonuc
    for etiket in _VARYASYON_POS:
        lemmalar = [lem for lem, p in zip(lemma_tokens, kelime_pos) if p == etiket]
        if lemmalar:
            sonuc[f"{etiket.lower()}_variation"] = round(len(set(lemmalar)) / len(lemmalar), 5)
    return sonuc
