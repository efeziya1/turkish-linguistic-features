"""Ses ve yazı örüntüleri: ünlü oranları ve büyük ünlü uyumu.

Bu modül T09'un 4 anahtarını üretir (``phonetic`` grubunun 20'sinden; kalan
16'sı T10 heceleme):
``vowel_ratio`` · ``front_vowel_ratio`` · ``back_vowel_ratio`` ·
``vowel_harmony_compliance``.

Ölçüler **yazıya** bakar, sese değil. Türkçe yazım sese çok yakın; İngilizcede
ince/kalın ayrımı yalnız harflere göredir (``e i`` ince, ``a o u`` kalın) ve
``y`` ünsüz sayılır. Grubun bütün öznitelikleri iki dilde üretilir
(2026-09-16, Efe).

Fonksiyonlar saftır (K3); ölçülemeyen değer ``0.0`` döner (K4).
"""

from __future__ import annotations

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
    """
    _dil_denetle(lang)
    alfabe = _ALFABE[lang]
    harfler = [c for c in _kucuk_harf(text, lang) if c in alfabe]
    if not harfler:
        return {"vowel_ratio": 0.0, "front_vowel_ratio": 0.0, "back_vowel_ratio": 0.0}
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
    onlar için tanımsız.

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
        return {"vowel_harmony_compliance": 0.0}
    return {"vowel_harmony_compliance": round(uyumlu / sayilan, 5)}
