"""Frekans yapısı: Popescu & Altmann'ın h-point ailesi — QUITA bataryası.

Bu modül ``frequency_structure`` grubunun 13 anahtarını üretir:
``h_point`` · ``vocab_richness_r1`` · ``vocab_richness_r4`` · ``repeat_rate`` ·
``rr_mcintosh`` · ``gini_coef`` · ``curve_length`` · ``curve_length_r`` ·
``lambda_pa`` · ``adjusted_modulus`` · ``writers_view_alpha`` ·
``thematic_concentration`` · ``secondary_thematic_concentration``.

Girdi ``rank_word_freq_table()`` (``lexical.py``) çıktısıdır: ``freqs`` azalan
sıralı, ``N`` toplam token, ``V`` tekil tip, ``items`` ``(kelime, frekans)``.
Rank 1 en sık kelimedir.

**Birim: lemma (2026-09-16, Efe).** Bütün grup lemma sıklıklarından hesaplanır
— TC h-point'i kullandığı için birim grup içinde tek olmalı. Kaynak: Čech,
Popescu & Altmann (2012) "lemmatization is a more adequately focused approach
eliminating the effect of synthetic morphology"; Čech, Garabík & Altmann
(2015) kelime biçimlerini bu amaç için "scarcely relevant" buluyor. ``lexical``
grubu ise yüzey biçim sayar (farklı gelenek, farklı karar). TC/STC'ye verilen
``pos_data`` bu yüzden **lemma → POS** eşlemesi olmalıdır: ``items``'taki
kelimeler lemma, ``pos_data``'nın ilk alanı da lemma (T20 hizalar).

Formüller birincil kaynaktan okundu (K12, Kademe A):

- Popescu, Altmann, Grzybek et al. (2009), *Word Frequency Studies*, Mouton de
  Gruyter — R1 s. 30 denk. (3.8), R4 s. 57 denk. (3.24)
- Popescu, Mačutek & Altmann (2009), *Aspects of Word Frequencies*, RAM-Verlag
  — writer's view s. 27 denk. (4.5)
- Kubát, Matlach & Čech (2014), *QUITA*, RAM-Verlag — h-point (6.2), Lambda
  (6.13-14), Gini (6.15), L (6.21), R (6.22-23), A (6.29-30), α (6.34),
  TC (6.37), STC (6.42)

Kaynak arşivi ve doğrulanmış fikstürler: ``tlf-kaynaklar/00-INDEKS.md``.

K4 (2026-09-16, Efe): ölçülemeyen değer ``math.nan`` — boş girdi ya da payda
sıfır (V = 1'de McIntosh, N ≤ 1'de A, tek noktalı eğride R, h ≤ 1'de TC,
noktaya inen üçgende α). Girdi olarak gelen NaN (``h``, ``RR``, ``L``) NaN
olarak yayılır. TC'de h-point üstünde konu kelimesi yoksa 0.0 gerçek sıfırdır.
"""

from __future__ import annotations

import math
from collections import Counter

import numpy as np

from .vocab import THEMATIC_POS


def h_point(freqs: np.ndarray) -> float:
    """Frekansın ranka eşit olduğu nokta.

    Tam eşleşme varsa o rank. Yoksa eğrinin köşegeni kestiği iki rank
    arasında ara değerleme (QUITA denk. 6.2)::

        h = (f(r₁)·r₂ − f(r₂)·r₁) / (r₂ − r₁ + f(r₁) − f(r₂))

    ``r₁`` = f(r) > r olan son rank, ``r₂ = r₁ + 1``. Eşit frekanslı kelimeler
    burada **düz** rank alır (QUITA'nın Orwell örneği bununla birebir tutuyor).

    Eğri gözlenen ranklarda köşegeni hiç kesmiyorsa (her rankta f > r, yalnız
    çok kısa ve tekrarlı metinlerde) ``h = V`` döner: h gözlenen rank
    sayısını aşamaz. Boş girdide NaN.
    """
    if len(freqs) == 0:
        return math.nan
    for r, f in enumerate(freqs.tolist(), start=1):
        if f == r:
            return float(r)
        if f < r:
            f1 = freqs[r - 2]
            return round(float((f1 * r - f * (r - 1)) / (1 + f1 - f)), 6)
    return float(len(freqs))


def repeat_rate(freqs: np.ndarray, N: int) -> dict[str, float]:
    """``RR = Σ (f/N)²`` — rastgele iki tokenin aynı tip olma olasılığı (yanlı).

    ``simpson_d`` bunun yansız karşılığıdır; ikisi yüksek korelasyonludur ve bu
    beklenen davranıştır.
    """
    if N == 0:
        return {"repeat_rate": math.nan}
    p = freqs.astype(np.float64) / N
    return {"repeat_rate": round(float(np.sum(p * p)), 6)}


def rr_mcintosh(RR: float, V: int) -> dict[str, float]:
    """McIntosh göreli tekrar oranı ``(1 − √RR) / (1 − 1/√V)``, [0, 1] aralığında.

    ``V ≤ 1`` → payda 0 → NaN; ``RR`` NaN ise NaN.
    """
    if V <= 1 or not RR > 0:
        return {"rr_mcintosh": math.nan}
    return {"rr_mcintosh": round((1 - math.sqrt(RR)) / (1 - 1 / math.sqrt(V)), 6)}


def gini_coef(freqs: np.ndarray, N: int, V: int) -> dict[str, float]:
    """``G = (V + 1 − 2·Σ(r·fᵣ)/N) / V``, rank **azalan** sırada (r=1 en sık).

    QUITA'nın düz yazısı Lorenz eğrisi için ters rank diyor, ama bu kapalı
    form azalan rank ister: ters rankla G negatif çıkar. Azalan rankla QUITA
    Metin 1 ve 2'nin yayımlanmış değerleri (0.3045, 0.3511) birebir üretiliyor.
    """
    if N == 0 or V == 0:
        return {"gini_coef": math.nan}
    r = np.arange(1, V + 1, dtype=np.float64)
    return {"gini_coef": round(float((V + 1 - 2 * np.sum(r * freqs) / N) / V), 6)}


def vocab_richness_r1(freqs: np.ndarray, N: int, h: float) -> dict[str, float]:
    """``R1 = 1 − (F(h) − h²/(2N))`` — metnin h-point altında kalan payı.

    ``F(h)`` **bağıl** birikimli frekans, toplam rank ``1..⌊h⌋``; kare ise tam
    kesirli ``h``'yi kullanır. Kesirli h'de ⌈h⌉'ye kadar toplamak ya da kısmi
    rank eklemek yanlıştır (Glottometrics 22, 2011, s. 68 dipnot 3).
    h-point tanımı gereği ``F(h) ≥ h²/N`` olduğu için R1 ∈ (0, 1).
    """
    if N == 0 or not h > 0:
        return {"vocab_richness_r1": math.nan}
    F = float(freqs[:int(h)].sum()) / N
    return {"vocab_richness_r1": round(1 - (F - h * h / (2 * N)), 6)}


def vocab_richness_r4(freqs: np.ndarray, N: int, V: int) -> dict[str, float]:
    """``R4 = 1 − G`` — ters çevrilmiş Gini katsayısı.

    R1 ile aynı formülün iki adı **değil**: R1 h-point sınırının altındaki
    payı, R4 kelime kullanımının eşitsizliğini ölçer. Boş metinde NaN.
    """
    if N == 0 or V == 0:
        return {"vocab_richness_r4": math.nan}
    return {"vocab_richness_r4": round(1 - gini_coef(freqs, N, V)["gini_coef"], 6)}


def _segments(freqs: np.ndarray) -> np.ndarray:
    """Komşu rank noktaları arasındaki Öklid mesafeleri ``√((fᵢ − fᵢ₊₁)² + 1)``."""
    f = freqs.astype(np.float64)
    return np.sqrt(np.diff(f) ** 2 + 1)


def curve_length(freqs: np.ndarray) -> dict[str, float]:
    """Frekans-rank eğrisinin yay uzunluğu ``L = Σᵢ₌₁^{V−1} √((fᵢ − fᵢ₊₁)² + 1)``.

    Boşsa NaN; tek tipte eğri bir noktadır, uzunluk gerçekten 0.
    """
    if len(freqs) == 0:
        return {"curve_length": math.nan}
    return {"curve_length": round(float(_segments(freqs).sum()), 4)}


def curve_length_indicator(freqs: np.ndarray, h: float) -> dict[str, float]:
    """``R = 1 − Lh / L`` — eğri uzunluğunun h-point altında kalan payı.

    ``Lh = Σ_{r=1}^{⌊h⌋} √((f(r) − f(r+1))² + 1)``, en fazla ``V − 1`` segment.
    QUITA s. 37'nin yazılı ifadesi 4 terim gösteriyor ama yayımlanan sonuç
    (14.29145) 5 terimle, yani ``r = 1..⌊h⌋`` ile tutuyor.

    ``V < 2`` (L = 0, payda sıfır) ya da geçersiz ``h`` → NaN.
    """
    if len(freqs) < 2 or not h > 0:
        return {"curve_length_r": math.nan}
    seg = _segments(freqs)
    L = float(seg.sum())
    Lh = float(seg[:min(int(h), len(seg))].sum())
    return {"curve_length_r": round(1 - Lh / L, 6)}


def lambda_pa(L: float, N: int) -> dict[str, float]:
    """``Λ = L · log₁₀(N) / N`` — metin uzunluğuna göre normalize eğri uzunluğu.

    Boş metinde ya da ``L`` NaN ise NaN; ``N = 1``'de Λ = 0 (tanımlı).
    """
    if N == 0 or math.isnan(L):
        return {"lambda_pa": math.nan}
    return {"lambda_pa": round(L * math.log10(N) / N, 4)}


def adjusted_modulus(f1: int, V: int, h: float, N: int) -> dict[str, float]:
    """``A = √((f₁/h)² + (V/h)²) / log₁₀(N)`` — h-point'ten eğri uçlarına mesafe.

    ``N ≤ 1`` (log₁₀N = 0) ya da geçersiz ``h`` → NaN.
    """
    if not h > 0 or N <= 1:
        return {"adjusted_modulus": math.nan}
    return {"adjusted_modulus": round(math.hypot(f1, V) / h / math.log10(N), 4)}


def writers_view(f1: int, V: int, h: float) -> dict[str, float]:
    """h-point tepesindeki açı, **radyan** (kosinüs değil).

    Üçgenin köşeleri: tepe ``H = (h, h)`` · üst ``(1, f₁)`` · son ``(V, 1)``::

        cos α = −[(h−1)(f₁−h) + (h−1)(V−h)] / (√((h−1)² + (f₁−h)²) · √((h−1)² + (V−h)²))
        α = arccos(cos α)

    ``(h−1)`` varyantı yazarların 2009 düzeltmesidir (*Aspects of Word
    Frequencies* s. 27 dipnot 1); 2007 makalesi ``h`` kullanıyor ve kendi içinde
    tutarsız. Beklenen aralık ~1.57–3.15; kosinüs okuması her zaman negatif olurdu.

    Boş girdi, geçersiz ``h`` ya da noktaya inen üçgen (açı tanımsız) → NaN.
    """
    if V == 0 or not h > 0:
        return {"writers_view_alpha": math.nan}
    ax, ay = 1 - h, f1 - h
    bx, by = V - h, 1 - h
    na, nb = math.hypot(ax, ay), math.hypot(bx, by)
    if na == 0 or nb == 0:
        return {"writers_view_alpha": math.nan}
    cos_a = max(-1.0, min(1.0, (ax * bx + ay * by) / (na * nb)))
    return {"writers_view_alpha": round(math.acos(cos_a), 4)}


def _ortalama_ranklar(items: list[tuple[str, int]]) -> list[float]:
    """Eşit frekanslı kelimelere ortalama rank (QUITA TC örneği, s. 49-51).

    ``Counter.most_common`` eşitlikleri ekleme sırasıyla dizer; ortalama rank
    TC'yi o keyfi sıradan bağımsız kılar.
    """
    ranklar: list[float] = []
    i = 0
    while i < len(items):
        j = i
        while j + 1 < len(items) and items[j + 1][1] == items[i][1]:
            j += 1
        ranklar.extend([(i + 1 + j + 1) / 2] * (j - i + 1))
        i = j + 1
    return ranklar


def _pos_haritasi(pos_data: list[tuple[str, str]]) -> dict[str, str]:
    """Küçük harfli kelime → en sık aldığı POS etiketi."""
    sayim: dict[str, Counter] = {}
    for token, pos in pos_data:
        sayim.setdefault(token.lower(), Counter())[pos] += 1
    return {k: c.most_common(1)[0][0] for k, c in sayim.items()}


def _tematik_toplam(items: list[tuple[str, int]], pos_data: list[tuple[str, str]],
                    ust_sinir: float) -> float:
    """``Σ (ust_sinir − r')·f(r')`` — rank'ı ``ust_sinir``'dan küçük otosemantikler."""
    pos = _pos_haritasi(pos_data)
    return sum((ust_sinir - r) * f
               for (kelime, f), r in zip(items, _ortalama_ranklar(items))
               if r < ust_sinir and pos.get(kelime.lower()) in THEMATIC_POS)


def thematic_concentration(items: list[tuple[str, int]], pos_data: list[tuple[str, str]],
                           h: float) -> dict[str, float]:
    """``TC = Σ 2(h − r')·f(r') / (h(h−1)·f₁)`` — h-point üstündeki içerik kelimeleri.

    ``r'`` konu kelimesinin (``THEMATIC_POS``: isim, özel isim, fiil, sıfat) ortalama rankı, yalnız
    ``r' < h``. ``f₁`` en sık kelimenin frekansı (işlev kelimesi olsa bile).
    Tek konulu metin konu isimlerini h-point üstüne taşır → TC büyür.

    Boş girdi ya da ``h ≤ 1`` (payda ``h(h−1)`` sıfır) → NaN. h-point üstünde
    konu kelimesi yoksa TC gerçekten 0.
    """
    if not items or not h > 1:
        return {"thematic_concentration": math.nan}
    f1 = items[0][1]
    toplam = _tematik_toplam(items, pos_data, h)
    return {"thematic_concentration": round(2 * toplam / (h * (h - 1) * f1), 6)}


def secondary_thematic_concentration(items: list[tuple[str, int]],
                                     pos_data: list[tuple[str, str]],
                                     h: float) -> dict[str, float]:
    """``STC = Σ_{r' ≤ 2h} (2h − r')·f(r') / (h(2h−1)·f₁)`` — QUITA denk. (6.42).

    TC'nin h yerine 2h ile hesaplanmış hali: rank 1'den 2h'ye kadar **bütün**
    otosemantikleri kapsar, yalnız ``h..2h`` bandını değil. TC'nin sık sık 0
    çıkması sorununu hafifletmek için var. ``V < 2h`` olan kısa metinde taşma
    olmaz — mevcut kelimeler üzerinden toplanır.

    Boş girdi ya da ``h ≤ 0.5`` (payda ``h(2h−1)`` sıfır ya da negatif) → NaN.
    """
    if not items or not h > 0.5:
        return {"secondary_thematic_concentration": math.nan}
    f1 = items[0][1]
    toplam = _tematik_toplam(items, pos_data, 2 * h)
    return {"secondary_thematic_concentration": round(toplam / (h * (2 * h - 1) * f1), 6)}
