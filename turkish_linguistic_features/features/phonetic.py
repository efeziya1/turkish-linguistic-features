"""Ses ve yazı örüntüleri: ünlü oranları ve büyük ünlü uyumu.

Bu modül ``phonetic`` grubunun 14 anahtarını üretir:

- T09 (4): ``vowel_ratio`` · ``front_vowel_ratio`` · ``back_vowel_ratio`` ·
  ``vowel_harmony_compliance``
- T10 (10): ``syllable_mean`` · ``syllable_cv`` · ``syllable_1_ratio`` …
  ``syllable_5_ratio`` · ``syllable_6plus_ratio`` · ``sentence_syllable_mean`` ·
  ``sentence_syllable_cv``

T10'un ``hece_say`` / ``toplam_hece`` fonksiyonları T13'ün Türkçe okunabilirlik
formüllerinin de hece sayacıdır (K11: tek sayaç).

Ölçüler **yazıya** bakar, sese değil. Türkçe yazım sese çok yakın; İngilizcede
ince/kalın ayrımı yalnız harflere göredir (``e i`` ince, ``a o u`` kalın) ve
``y`` ünsüz sayılır. Grubun bütün öznitelikleri iki dilde üretilir
(2026-09-16, Efe).

Fonksiyonlar saftır (K3). K4 (2026-09-16, Efe): ölçülemeyen değer ``math.nan``
— alfabe harfi yoksa oranlar, en az iki ünlülü kelime yoksa ünlü uyumu.
"""

from __future__ import annotations

import math
from collections import Counter

import numpy as np
import textstat

from .punctuation import _ALFABE, _kucuk_harf

_UNLULER: dict[str, str] = {"tr": "aeıioöuü", "en": "aeiou"}
_ON: dict[str, str] = {"tr": "eiöü", "en": "ei"}
_ARKA: dict[str, str] = {"tr": "aıou", "en": "aou"}


def _dil_denetle(lang: str) -> None:
    if lang not in _ALFABE:
        raise ValueError(f"Desteklenmeyen dil: {lang!r}. Beklenen: {sorted(_ALFABE)}")


def vowel_ratios(text: str, lang: str = "tr") -> dict[str, float]:
    """Ünlü, ince ünlü ve kalın ünlü oranları.

    Payda dilin alfabesindeki harf sayısıdır; boşluk, rakam, noktalama ve
    alfabe dışı harfler sayılmaz. İnce ve kalın oranları **tüm harflere**
    bölünür (2026-09-16, Efe): ünlülere bölünseydi toplamları hep 1 olur,
    biri öbürünü tekrarlardı. Bu yüzden ``front + back = vowel_ratio``.
    Alfabe harfi yoksa üçü de NaN.
    """
    _dil_denetle(lang)
    alfabe = _ALFABE[lang]
    harfler = [c for c in _kucuk_harf(text, lang) if c in alfabe]
    if not harfler:
        return {"vowel_ratio": math.nan, "front_vowel_ratio": math.nan, "back_vowel_ratio": math.nan}
    n = len(harfler)
    on = sum(1 for c in harfler if c in _ON[lang])
    arka = sum(1 for c in harfler if c in _ARKA[lang])
    unlu = sum(1 for c in harfler if c in _UNLULER[lang])
    return {"vowel_ratio": round(unlu / n, 5),
            "front_vowel_ratio": round(on / n, 5),
            "back_vowel_ratio": round(arka / n, 5)}


def vowel_harmony_compliance(surface_tokens: list[str], lang: str = "tr") -> dict[str, float]:
    """Büyük ünlü uyumuna uyan kelime oranı.

    Bir kelimenin bütün ünlüleri ya ince ya kalınsa uyumludur. En az iki
    ünlüsü olmayan kelime (``ev``, noktalama, sayı) paydaya girmez — uyum
    onlar için tanımsız; hiç sayılacak kelime yoksa NaN.

    Düz kural (2026-09-16, Efe): uyuma girmeyen ekler (``-yor``, ``-ki``,
    ``-ken``) yerli kelimeyi de uyumsuz yapar (``geliyor``). Ölçü alıntı
    kelimeyle birlikte bu eklerin sıklığını da taşır.
    """
    _dil_denetle(lang)
    on, arka, unluler = set(_ON[lang]), set(_ARKA[lang]), set(_UNLULER[lang])
    uyumlu = 0
    sayilan = 0
    for token in surface_tokens:
        kelime_unluleri = [c for c in _kucuk_harf(token, lang) if c in unluler]
        if len(kelime_unluleri) < 2:
            continue
        sayilan += 1
        if all(c in on for c in kelime_unluleri) or all(c in arka for c in kelime_unluleri):
            uyumlu += 1
    if sayilan == 0:
        return {"vowel_harmony_compliance": math.nan}
    return {"vowel_harmony_compliance": round(uyumlu / sayilan, 5)}


# ── T10: heceleme ─────────────────────────────────────────────────────
#
# Heceleme kuralı = TDK, "Hece Yapısı ve Satır Sonunda Kelimelerin Bölünmesi"
# (tdk.gov.tr, 2019): iki ünlü arasındaki ünsüzlerden yalnız sonuncusu sonraki
# ünlüyle hece kurar (al-dı, alt-lık, Türk-çe); Batı kökenli kelimelere de aynı
# kural uygulanır (prog-ram, kont-rol, sant-ral); yan yana iki ünlü ayrı hecedir
# (sa-at, Ka-ra-os-ma-noğ-lu). Kelime başı ve sonu ünsüzleri ilk/son hecede
# kalır (tren, stra-te-ji). Liste gerekmez. KEMİK hece tablosu da bu kuralla
# hecelenmiş (tlf-kaynaklar/00-INDEKS.md).

_TR_HECE_UNLULERI = frozenset("aeıioöuüâîû")      # şapkalı ünlüler dahil (Zeyrek de sayıyor)
_KESMELER = str.maketrans("", "", "'’")


def _syllabify_tr(word: str) -> list[str]:
    """Küçük harfli Türkçe kelimeyi TDK kuralıyla hecelere böler.

    Ünlü sayısı hece sayısıdır. Ünlüsüz ya da tek ünlülü kelime tek parça döner.
    """
    unluler = [i for i, c in enumerate(word) if c in _TR_HECE_UNLULERI]
    if len(unluler) <= 1:
        return [word]
    heceler = []
    bas = 0
    for v1, v2 in zip(unluler, unluler[1:]):
        sinir = v1 + 1 if v2 == v1 + 1 else v2 - 1   # yan yana ünlü | son ünsüz sonraki heceye
        heceler.append(word[bas:sinir])
        bas = sinir
    heceler.append(word[bas:])
    return heceler


def hece_say(word: str, lang: str = "tr") -> int | None:
    """Bir tokenin hece sayısı; hecelenemiyorsa ``None`` (2026-09-16, Efe).

    - Yalnız harflerden oluşan tokenler hecelenir; kesme işaretinden sonraki ek
      kelimeye bitişik sayılır (``Ankara'da`` → 4). Rakam içeren tokenler
      (``1990``, ``2023'te``) ve noktalama → ``None``: okunuşları yazıdan
      çıkarılamaz.
    - TR — ünlü sayısı (``â î û`` dahil). Ünlüsüz token tamamı büyük harfse
      kısaltmadır, harf adları tek heceli olduğu için hece = harf sayısı
      (``TBMM`` → 4); küçük harfliyse (``km``, ``vb``) kelime olarak okunur,
      sayılamaz → ``None``.
    - EN — ``textstat.syllable_count``; 0 verirse 1 (``shh``).
    """
    _dil_denetle(lang)
    yalin = word.translate(_KESMELER)
    if not yalin or not yalin.isalpha():
        return None
    if lang == "en":
        return max(1, int(textstat.syllable_count(yalin)))
    kucuk = _kucuk_harf(yalin, lang)
    n = sum(1 for c in kucuk if c in _TR_HECE_UNLULERI)
    if n > 0:
        return n
    return len(yalin) if yalin.isupper() else None


def toplam_hece(tokens: list[str], lang: str = "tr") -> int:
    """Hecelenebilen tokenlerin toplam hece sayısı. T13 bunu kullanır."""
    return sum(h for h in (hece_say(t, lang) for t in tokens) if h is not None)


def _hece_sayilari(tokens: list[str], lang: str) -> list[int]:
    return [h for h in (hece_say(t, lang) for t in tokens) if h is not None]


def _ortalama_cv(degerler: list[int]) -> tuple[float, float]:
    """Ortalama ve popülasyon CV'si; boşsa ikisi NaN, tek değerde CV NaN (K4)."""
    if not degerler:
        return math.nan, math.nan
    d = np.array(degerler, dtype=np.float64)
    ortalama = float(d.mean())
    cv = float(d.std()) / ortalama if len(d) > 1 and ortalama > 0 else math.nan
    return round(ortalama, 4), round(cv, 4)


def syllable_count_stats(tokens: list[str], lang: str = "tr") -> dict[str, float]:
    """Kelime başına hece: ortalama ve CV (``syllable_stdev`` → CV, 2026-09-16, Efe).

    Yalnız hecelenebilen tokenler sayılır (``hece_say``). CV popülasyon
    standart sapması / ortalama — ``word_length_cv`` ile aynı kalıp.
    """
    ortalama, cv = _ortalama_cv(_hece_sayilari(tokens, lang))
    return {"syllable_mean": ortalama, "syllable_cv": cv}


_HECE_KOVALARI = ("syllable_1_ratio", "syllable_2_ratio", "syllable_3_ratio",
                  "syllable_4_ratio", "syllable_5_ratio", "syllable_6plus_ratio")


def syllable_length_distribution(tokens: list[str], lang: str = "tr") -> dict[str, float]:
    """Kelimelerin hece sayısına göre dağılımı: 1, 2, 3, 4, 5, 6+ (toplam 1).

    Kovalar Bezirci & Yılmaz (2010, Tablo 1-c) ile aynı; üst kova sabit 6+.
    Hecelenebilen token yoksa altısı da NaN.
    """
    sayilar = _hece_sayilari(tokens, lang)
    if not sayilar:
        return dict.fromkeys(_HECE_KOVALARI, math.nan)
    kova = Counter(min(h, 6) for h in sayilar)
    n = len(sayilar)
    return {ad: round(kova.get(i, 0) / n, 6) for i, ad in enumerate(_HECE_KOVALARI, start=1)}


def sentence_syllable_stats(cumleler: list[list[str]], lang: str = "tr") -> dict[str, float]:
    """Cümle başına hece: ortalama ve CV.

    Cümlenin hecesi, hecelenebilen tokenlerinin toplamıdır (noktalama ve rakam
    sayılmaz). Hiç hecelenebilen tokeni olmayan cümle ölçülemez, hesaba girmez.
    Cümle yoksa ikisi NaN; tek cümlede CV NaN.
    """
    heceler = []
    for cumle in cumleler:
        sayilar = _hece_sayilari(cumle, lang)
        if sayilar:
            heceler.append(sum(sayilar))
    ortalama, cv = _ortalama_cv(heceler)
    return {"sentence_syllable_mean": ortalama, "sentence_syllable_cv": cv}
