"""Okunabilirlik formülleri — ``readability`` grubu (TR 13 · EN 8).

- Türkçe: ``atesman`` · ``cetinkaya_uzun`` · ``bezirci_yilmaz``; Kalyoncu (2025) K1–K4 ve
  bileşenleri (9) ayrı modülde, ``kalyoncu``
- İngilizce: ``flesch_reading_ease`` · ``flesch_kincaid_grade`` · ``smog`` ·
  ``polysyllabic_word_ratio`` (Türkçe eşiği belirlenene kadar yalnız EN) ·
  ``ari`` · ``coleman_liau`` · ``lix``
- İki dilde: ``long_word_ratio``

Dil ayrımı T20'nin birleştiricisinde yapılır (2026-09-15, Efe).

**Okunabilirlik formülü yalnız kurulduğu dilde hesaplanır (ilke D; 2026-10-15, Efe).**
Formül bir okur kitlesinin anlamasını kestiren modeldir; kitle değişince sonucun
karşılığı kalmaz. ARI, Coleman-Liau ve LIX İngilizce için kuruldu (LIX'in İngilizce
normları Anderson 1983'te), Türkçede hesaplanmaz. Betimleyici ölçü (``long_word_ratio``)
metnin özelliğini verir, iki dilde kalır.

**Sayım kuralları kaynaklara göre (2026-09-17, Efe).** Bu grup kütüphanenin
spaCy kelimesini ve spaCy cümlesini kullanmaz; her formül kendi birincil
kaynağının sayımını izler:

- Kelime = boşlukla ayrılan birim, kenar noktalaması atılmış (Flesch 1948;
  Kincaid ve ark. 1975; Kalyoncu 2025). Kısaltmalı ve tireli biçimler tek
  kelime. Harf ya da rakam içermeyen birim kelime değil; tek başına duran
  sembol yalnız kaynağı sayan formüllerde kelime (FRE, FKGL, ARI, Çetinkaya).
- Cümle = formüle özel işaretlerden biriyle biten dizi (``_CUMLE_SONU``).
  İşaretler spaCy tokenlarından okunur, böylece ``Dr.`` cümle bitirmez.
- Hece = T10'un ``hece_say``'i; tireli kelime parçaların toplamı, sembol ve
  noktalı baş harf okunuşuyla (``phonetic.birim_hecesi``). Türkçe sıra sayısı
  (``3.`` → üçüncü) noktasıyla kelime olur (``kelime_birimleri``).
- Ortalama hece yalnız hecelenebilen kelimelerden hesaplanır; cümle uzunluğu
  bütün kelimelerden.

Katsayılar birincil kaynaklardan (K12, ``tlf-kaynaklar``). Fonksiyonlar saftır
(K3); kelime ya da cümle yoksa değerler NaN (K4).
"""

from __future__ import annotations

import math

from ..birimler.sozcuk import kelime_birimleri
from ..birimler.tumce import _CUMLE_KOSULLU, _CUMLE_SONU, cumle_sayisi
from .phonetic import birim_hecesi

# Björnsson: "6 harften uzun" kelime (Anderson 1983 s.491: seven or more letters).
_UZUN_KELIME_HARF = 7

# McLaughlin (1969): formül 30 cümlelik örnek üzerine kurulu.
_SMOG_MIN_CUMLE = 30

# Bezirci & Yılmaz (2010) s.370: EKOK 21000 / (Tablo 1-c oranı × 1000) / 100.
_BEZIRCI_KATSAYI = {3: 0.84, 4: 1.5, 5: 3.5, 6: 26.25}


# ── sayım ─────────────────────────────────────────────────────────────


def _sayim(surface_tokens: list[str], kume: str, lang: str) -> int:
    """Adlandırılmış kuralla cümle sayısı (``_CUMLE_SONU`` + ``_CUMLE_KOSULLU``)."""
    return cumle_sayisi(surface_tokens, _CUMLE_SONU[kume], lang, _CUMLE_KOSULLU[kume])


def _heceler(kelimeler: list[str], lang: str) -> list[int]:
    return [h for h in (birim_hecesi(k, lang) for k in kelimeler) if h is not None]


def _harf_sayisi(kelime: str) -> int:
    return sum(1 for c in kelime if c.isalpha())


# ── formüller ─────────────────────────────────────────────────────────


def turkish_readability_formulas(raw_text: str, surface_tokens: list[str]) -> dict[str, float]:
    """Ateşman (1997), Çetinkaya-Uzun (2010), Bezirci-Yılmaz (2010).

    - atesman        = 198.825 − 40.175·(hece/kelime) − 2.610·(kelime/cümle)
    - cetinkaya_uzun = 118.823 − 25.987·(hece/kelime) − 0.971·(kelime/cümle)
      Sembol kelime sayılır; ``:`` ve parantezler cümle bitirir (Çetinkaya 2010, s.93).
    - bezirci_yilmaz = √(OKS · (0.84·H3 + 1.5·H4 + 3.5·H5 + 26.25·H6)),
      OKS ve Hk cümle başına (H6 = 6 veya daha fazla heceli).

    Ateşman ve Çetinkaya yükseldikçe metin kolaylaşır; Bezirci-Yılmaz zorlaşır.
    Ateşman ve Bezirci-Yılmaz kaynakları kelime ve cümle tanımı vermiyor;
    varsayılan kural uygulanır.
    """
    kelimeler, semboller = kelime_birimleri(raw_text, "tr")
    sonuc = {"atesman": math.nan, "cetinkaya_uzun": math.nan, "bezirci_yilmaz": math.nan}

    heceler = _heceler(kelimeler, "tr")
    cumle = _sayim(surface_tokens, "varsayilan", "tr")
    if heceler and cumle:
        hece_kelime = sum(heceler) / len(heceler)
        kelime_cumle = len(kelimeler) / cumle
        sonuc["atesman"] = round(198.825 - 40.175 * hece_kelime - 2.610 * kelime_cumle, 4)
        braket = sum(_BEZIRCI_KATSAYI[min(h, 6)] for h in heceler if h >= 3) / cumle
        sonuc["bezirci_yilmaz"] = round(math.sqrt(kelime_cumle * braket), 4)

    c_kelimeler = kelimeler + semboller
    c_heceler = _heceler(c_kelimeler, "tr")
    c_cumle = _sayim(surface_tokens, "cetinkaya", "tr")
    if c_heceler and c_cumle:
        sonuc["cetinkaya_uzun"] = round(
            118.823 - 25.987 * sum(c_heceler) / len(c_heceler)
            - 0.971 * len(c_kelimeler) / c_cumle, 4)
    return sonuc


def english_readability_formulas(raw_text: str, surface_tokens: list[str]) -> dict[str, float]:
    """Flesch (1948), Flesch-Kincaid (Kincaid ve ark. 1975), SMOG (McLaughlin 1969).

    - FRE  = 206.835 − 1.015·(kelime/cümle) − 84.6·(hece/kelime)
    - FKGL = 0.39·(kelime/cümle) + 11.8·(hece/kelime) − 15.59
      İkisinde sembol kelime, ``;`` cümle sonu (Kincaid talimatı; ``:`` hariç).
    - SMOG = 3.1291 + 1.0430·√p, p = 30 cümleye düşen 3+ heceli kelime
      (Tablo 1, denklem d). Kelime = varsayılan kelime (harf ya da rakam içeren
      boşluk birimi, sembol sayılmaz); cümle varsayılan kuraldan: ``. ? ! …`` her
      zaman, ``:`` yalnız ardından yeni cümle başlıyorsa.
      30 cümleden kısa metinde NaN (2026-09-16, Efe).
    - polysyllabic_word_ratio = 3+ heceli kelime / hecelenebilen kelime
      (SMOG'un kelime ve hece tanımıyla).

    FRE yükseldikçe metin kolaylaşır; FKGL ve SMOG eğitim yılı verir.
    """
    kelimeler, semboller = kelime_birimleri(raw_text, "en")
    sonuc = {"flesch_reading_ease": math.nan, "flesch_kincaid_grade": math.nan,
             "smog": math.nan, "polysyllabic_word_ratio": math.nan}

    k_kelimeler = kelimeler + semboller
    k_heceler = _heceler(k_kelimeler, "en")
    k_cumle = _sayim(surface_tokens, "kincaid", "en")
    if k_heceler and k_cumle:
        kelime_cumle = len(k_kelimeler) / k_cumle
        hece_kelime = sum(k_heceler) / len(k_heceler)
        sonuc["flesch_reading_ease"] = round(206.835 - 1.015 * kelime_cumle - 84.6 * hece_kelime, 4)
        sonuc["flesch_kincaid_grade"] = round(0.39 * kelime_cumle + 11.8 * hece_kelime - 15.59, 4)

    heceler = _heceler(kelimeler, "en")
    if heceler:
        cok_heceli = sum(1 for h in heceler if h >= 3)
        sonuc["polysyllabic_word_ratio"] = round(cok_heceli / len(heceler), 5)
        cumle = _sayim(surface_tokens, "varsayilan", "en")
        if cumle >= _SMOG_MIN_CUMLE:
            sonuc["smog"] = round(3.1291 + 1.0430 * math.sqrt(cok_heceli * 30 / cumle), 4)
    return sonuc


def general_readability_formulas(
    raw_text: str, surface_tokens: list[str], lang: str,
) -> dict[str, float]:
    """ARI (Smith & Senter 1967), Coleman-Liau (1975), LIX (Björnsson 1968); yalnız İngilizce.

    - ari = 4.71·(vuruş/kelime) + 0.5·(kelime/cümle) − 21.43 — vuruş = boşluk
      dışı her karakter, sembol kelime sayılır (Kincaid ve ark. 1975 s.14, s.33)
    - coleman_liau = 0.0588·L − 0.296·S − 15.8; L = 100 kelimedeki harf,
      S = 100 kelimedeki cümle (Coleman & Liau 1975 s.284)
    - lix = kelime/cümle + 100·uzun kelime/kelime; uzun = 7 veya daha fazla harf
    - long_word_ratio = uzun kelime / kelime (LIX'in tanımı)

    Cümle sayan üçünde (ARI, Coleman-Liau, LIX) cümle varsayılan kuraldan: ``. ? ! …``
    her zaman, ``:`` yalnız ardından yeni cümle başlıyorsa.

    Türkçede (``lang="tr"``) yalnız ``long_word_ratio`` döner: üç formül yalnız kurulduğu
    dilde hesaplanır (ilke D, modül başı).
    """
    kelimeler, semboller = kelime_birimleri(raw_text, lang)
    cumle = _sayim(surface_tokens, "varsayilan", lang)
    sonuc = {"long_word_ratio": math.nan}
    if lang == "en":
        sonuc.update({"ari": math.nan, "coleman_liau": math.nan, "lix": math.nan})
    if not kelimeler:
        return sonuc

    uzun = sum(1 for k in kelimeler if _harf_sayisi(k) >= _UZUN_KELIME_HARF)
    sonuc["long_word_ratio"] = round(uzun / len(kelimeler), 5)
    if lang != "en":
        return sonuc
    harf = sum(_harf_sayisi(k) for k in kelimeler)
    sonuc["coleman_liau"] = round(
        0.0588 * 100 * harf / len(kelimeler) - 0.296 * 100 * cumle / len(kelimeler) - 15.8, 4)
    if cumle:
        sonuc["lix"] = round(len(kelimeler) / cumle + 100 * uzun / len(kelimeler), 4)
        a_kelime = len(kelimeler) + len(semboller)
        vurus = sum(len(parca) for parca in raw_text.split())
        sonuc["ari"] = round(4.71 * vurus / a_kelime + 0.5 * a_kelime / cumle - 21.43, 4)
    return sonuc
