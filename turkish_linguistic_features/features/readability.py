"""Okunabilirlik formülleri — ``readability`` grubu (TR 7 · EN 8).

- Türkçe: ``bezirci_yilmaz`` · ``atesman`` · ``cetinkaya_uzun``
- İngilizce: ``flesch_reading_ease`` · ``flesch_kincaid_grade`` · ``smog`` ·
  ``polysyllabic_word_ratio`` (Türkçe eşiği belirlenene kadar yalnız EN)
- İki dilde: ``ari`` · ``coleman_liau`` · ``lix`` · ``long_word_ratio``

Dil ayrımı burada değil, T20'nin birleştiricisinde yapılır: fonksiyonlar dil
koruması taşımaz (2026-09-15, Efe).

Girdiler (2026-09-16, Efe): ``kelimeler`` = noktalama ve sembol (``PUNCT``,
``SYM``) atılmış tokenler, ``cumle_sayisi`` = spaCy cümle sayısı. Tek istisna
``ari``: vuruş sayısı kaynağın tanımı gereği noktalamalı ``surface_tokens``'tan.
Hece sayacı T10'un ``hece_say`` fonksiyonudur (K11: tek sayaç).

Katsayılar birincil kaynaklardan (K12, ``tlf-kaynaklar``). Fonksiyonlar saftır
(K3); kelime ya da cümle yoksa değerler NaN (K4).
"""

from __future__ import annotations

import math

from .phonetic import _hece_sayilari, toplam_hece

# Björnsson: "6 harften uzun" kelime. lix ve long_word_ratio ortak; ayar değil
# (değiştirilirse sonuç artık LIX olmaz — 2026-09-16, Efe).
_UZUN_KELIME_HARF = 7

# McLaughlin (1969): formül 30 cümlelik örnek üzerine kurulu.
_SMOG_MIN_CUMLE = 30


def _harf_sayisi(kelime: str) -> int:
    return sum(1 for ch in kelime if ch.isalpha())


def automated_readability_index(
    surface_tokens: list[str], kelimeler: list[str], cumle_sayisi: int,
) -> dict[str, float]:
    """Automated Readability Index (Smith & Senter 1967).

    ARI = 4.71·(vuruş/kelime) + 0.5·(kelime/cümle) − 21.43
    Katsayılar Kincaid ve ark. (1975) s.14'te "Old" ARI olarak.

    Vuruş = harf + sembol + noktalama: formül daktilo sayacı için kurulmuş,
    Kincaid ve ark. (1975) s.33 "Letters, symbols, and punctuation marks are
    included in the count of strokes." Bu yüzden vuruşlar noktalamalı
    ``surface_tokens``'tan sayılır.
    """
    if not kelimeler or cumle_sayisi == 0:
        return {"ari": math.nan}
    vurus = sum(len(t) for t in surface_tokens)
    return {"ari": round(4.71 * vurus / len(kelimeler)
                         + 0.5 * len(kelimeler) / cumle_sayisi - 21.43, 4)}


def coleman_liau_index(kelimeler: list[str], cumle_sayisi: int) -> dict[str, float]:
    """Coleman-Liau Index (Coleman & Liau 1975, JAP 60(2), s.284).

    CLI = 0.0588·L − 0.296·S − 15.8; L = 100 kelimedeki **harf**, S = 100
    kelimedeki cümle. Makalenin iki denkleminin (cloze % ve sınıf düzeyi)
    birleşimi. Yalnız harf sayılır.
    """
    if not kelimeler:
        return {"coleman_liau": math.nan}
    harf = sum(_harf_sayisi(k) for k in kelimeler)
    L = 100 * harf / len(kelimeler)
    S = 100 * cumle_sayisi / len(kelimeler)
    return {"coleman_liau": round(0.0588 * L - 0.296 * S - 15.8, 4)}


def lix_readability_index(kelimeler: list[str], cumle_sayisi: int) -> dict[str, float]:
    """LIX (Björnsson 1968) = kelime/cümle + 100 · uzun kelime/kelime."""
    if not kelimeler or cumle_sayisi == 0:
        return {"lix": math.nan}
    uzun = sum(1 for k in kelimeler if _harf_sayisi(k) >= _UZUN_KELIME_HARF)
    return {"lix": round(len(kelimeler) / cumle_sayisi + 100 * uzun / len(kelimeler), 4)}


def long_word_ratio(kelimeler: list[str]) -> dict[str, float]:
    """7 veya daha fazla harfli kelimelerin oranı — LIX'in uzun kelime tanımı."""
    if not kelimeler:
        return {"long_word_ratio": math.nan}
    uzun = sum(1 for k in kelimeler if _harf_sayisi(k) >= _UZUN_KELIME_HARF)
    return {"long_word_ratio": round(uzun / len(kelimeler), 5)}


def polysyllabic_word_ratio(kelimeler: list[str], lang: str = "en") -> dict[str, float]:
    """3 veya daha fazla heceli kelimelerin hecelenebilen kelimelere oranı (SMOG'un tanımı).

    Türkçe şemada şimdilik yok: eşik İngilizce geleneğinden, Türkçe eşik
    yeniden gözden geçirilecek (2026-09-16, Efe). Hecelenebilen kelime yoksa NaN.
    """
    heceler = _hece_sayilari(kelimeler, lang)
    if not heceler:
        return {"polysyllabic_word_ratio": math.nan}
    cok = sum(1 for h in heceler if h >= 3)
    return {"polysyllabic_word_ratio": round(cok / len(heceler), 5)}


def english_readability_formulas(
    kelimeler: list[str], cumle_sayisi: int, lang: str = "en",
) -> dict[str, float]:
    """Flesch (1948), Flesch-Kincaid (Kincaid ve ark. 1975), SMOG (McLaughlin 1969).

    - FRE  = 206.835 − 1.015·(kelime/cümle) − 84.6·(hece/kelime)
    - FKGL = 0.39·(kelime/cümle) + 11.8·(hece/kelime) − 15.59
    - SMOG = 3.1291 + 1.0430·√p, p = 30 cümleye düşen 3+ heceli kelime
      (Tablo 1, denklem d)

    FRE yükseldikçe metin kolaylaşır; FKGL ve SMOG eğitim yılı verir.
    ``smog`` 30 cümleden kısa metinde NaN (2026-09-16, Efe) — textstat bu
    kontrolü yapmıyor.
    """
    if not kelimeler or cumle_sayisi == 0:
        return {"flesch_reading_ease": math.nan, "flesch_kincaid_grade": math.nan,
                "smog": math.nan}
    kelime_cumle = len(kelimeler) / cumle_sayisi
    hece_kelime = toplam_hece(kelimeler, lang) / len(kelimeler)
    if cumle_sayisi < _SMOG_MIN_CUMLE:
        smog = math.nan
    else:
        cok_heceli = sum(1 for h in _hece_sayilari(kelimeler, lang) if h >= 3)
        smog = round(3.1291 + 1.0430 * math.sqrt(cok_heceli * 30 / cumle_sayisi), 4)
    return {
        "flesch_reading_ease": round(206.835 - 1.015 * kelime_cumle - 84.6 * hece_kelime, 4),
        "flesch_kincaid_grade": round(0.39 * kelime_cumle + 11.8 * hece_kelime - 15.59, 4),
        "smog": smog,
    }


def turkish_readability_formulas(
    kelimeler: list[str], cumle_sayisi: int, lang: str = "tr",
) -> dict[str, float]:
    """Ateşman (1997) ve Çetinkaya-Uzun (2010).

    İkisi de hece/kelime ve kelime/cümle okur, katsayılarla ayrılır:

    - atesman        = 198.825 − 40.175·(hece/kelime) − 2.610·(kelime/cümle)
    - cetinkaya_uzun = 118.823 − 25.987·(hece/kelime) − 0.971·(kelime/cümle)

    İkisi de yükseldikçe metin kolaylaşır.
    """
    if not kelimeler or cumle_sayisi == 0:
        return {"atesman": math.nan, "cetinkaya_uzun": math.nan}
    hece_kelime = toplam_hece(kelimeler, lang) / len(kelimeler)
    kelime_cumle = len(kelimeler) / cumle_sayisi
    return {
        "atesman": round(198.825 - 40.175 * hece_kelime - 2.610 * kelime_cumle, 4),
        "cetinkaya_uzun": round(118.823 - 25.987 * hece_kelime - 0.971 * kelime_cumle, 4),
    }


# Bezirci & Yılmaz (2010) s.370: Tablo 1-c ortalamalarının EKOK'u (21000) her
# orana bölünüp 100'e bölünmüş — tam sayı oranları, yuvarlama yok.
_BEZIRCI_KATSAYI = {3: 0.84, 4: 1.5, 5: 3.5, 6: 26.25}


def bezirci_yilmaz_score(kelimeler: list[str], cumle_sayisi: int) -> dict[str, float]:
    """Bezirci-Yılmaz (2010) = √(OKS · (0.84·H3 + 1.5·H4 + 3.5·H5 + 26.25·H6)).

    OKS = cümle başına kelime; Hk = cümle başına k heceli kelime (H6 = 6 veya
    daha fazla). Yükseldikçe metin zorlaşır (yaklaşık eğitim yılı).
    """
    if not kelimeler or cumle_sayisi == 0:
        return {"bezirci_yilmaz": math.nan}
    oks = len(kelimeler) / cumle_sayisi
    braket = sum(_BEZIRCI_KATSAYI[min(h, 6)] for h in _hece_sayilari(kelimeler, "tr") if h >= 3)
    return {"bezirci_yilmaz": round(math.sqrt(oks * braket / cumle_sayisi), 4)}
