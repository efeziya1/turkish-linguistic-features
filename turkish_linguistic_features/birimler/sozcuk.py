"""Sözcük birimi: aracın tek sözcük tanımı (2026-10-06, Efe).

Sözcük = boşlukla ayrılan birim, kenar noktalaması atılmış (Flesch 1948; Kincaid ve ark.
1975; Kalyoncu 2025). Kısaltmalı ve tireli biçimler tek sözcük. Harf ya da rakam içermeyen
birim sözcük değil; tek başına duran listedeki sembol ayrı döner. Türkçe sıra sayısı
(``3.`` → üçüncü) noktasıyla sözcük olur.

Öznitelikler (``features``), ön işleme (``pipeline``) ve dosya okuyucu aynı tanımı buradan
alır. Saf hesap; paket içinden yalnız L0'ı ve ``birimler``i görür.
"""

from __future__ import annotations

import re

from ..alfabe import _dil_denetle
from .okunus import SEMBOLLER

__all__ = ["cumle_birimleri", "kelime_birimleri", "word_units"]

# Kelime biriminin kenarından atılan noktalama.
_KENAR = ".,;:!?…\"'“”‘’«»()[]{}–—-/*"

# Two words glued by sentence punctuation with the space left out (geldi.Sonra, gibi...Bu,
# 3.köprü) are two words (2026-11-27, Efe). The left side must end in two letters, or be a
# number whose dot then makes it an ordinal, so dotted initials (G.Saray, T.C.) stay whole.
_BITISIK = re.compile(r"(?<=[^\W\d_]{2})[.?!…]+[\"“”'’()\-]*(?=[^\W\d_])|(?<=\d)\.(?=[^\W\d_])")
# A quote or apostrophe followed by a lower-case letter is a suffix ("kampusu!"na, mm.’lik):
# no split there.
_EK_ONU = re.compile(r"[\"“”'’]")
# Addresses keep their dots (ad@gazete.com, www.x.org, kariyer.net).
_ADRES = re.compile(r"@|://|www\.|\.(?:com|org|net|edu|gov|tr)\b", re.IGNORECASE)


def _bitisikleri_ayir(ham: str, bas: int) -> list[tuple[str, int, int]]:
    """Split a whitespace chunk at glued sentence punctuation: ``(piece, start, end)``.

    A piece ends after the punctuation that follows it, so the model's tokens for that
    punctuation stay with the word before it. An ordinal keeps its dot (``3.köprü`` →
    ``3.``, ``köprü``).
    """
    if _ADRES.search(ham):
        return [(ham, bas, bas + len(ham))]
    parcalar: list[tuple[str, int, int]] = []
    onceki = 0
    for m in _BITISIK.finditer(ham):
        if _EK_ONU.search(m.group()) and ham[m.end()].islower():
            continue
        sol = ham[onceki:m.start()]
        if m.group() == "." and sol[-1:].isdigit():
            sol += "."
        parcalar.append((sol, bas + onceki, bas + m.end()))
        onceki = m.end()
    parcalar.append((ham[onceki:], bas + onceki, bas + len(ham)))
    return parcalar


def kelime_birimleri(raw_text: str, lang: str) -> tuple[list[str], list[str]]:
    """Boşlukla ayrılan birimler → (kelimeler, tek başına listedeki semboller).

    Kenar noktalaması atılır (``okudu.`` → ``okudu``). Harf ya da rakam içeren
    birim kelimedir; yalnız listedeki sembollerden oluşan birim ayrı döner;
    geri kalanlar (``-``, ``#``) sayılmaz.

    Turkish ordinals keep their dot (``3. kat`` → ``3.``) when a word or a
    comma follows; a sentence-final ``3.`` stays the cardinal ``3``
    (2026-10-01, Efe).
    """
    kelimeler: list[str] = []
    tek_semboller: list[str] = []
    for birim, kelime_mi, _, _ in word_units(raw_text, lang):
        (kelimeler if kelime_mi else tek_semboller).append(birim)
    return kelimeler, tek_semboller


def word_units(raw_text: str, lang: str) -> list[tuple[str, bool, int, int]]:
    """Whitespace units with their place in ``raw_text``: ``(unit, is_word, start, end)``.

    ``start``/``end`` delimit the whole whitespace chunk (edge punctuation included),
    so model tokens can be matched to the word they fall in. ``is_word`` False is a
    stand-alone listed symbol; chunks that are neither are left out. Same rules as
    ``kelime_birimleri``, which is built on this.
    """
    _dil_denetle(lang)
    semboller = SEMBOLLER[lang]
    parcalar = [p for m in re.finditer(r"\S+", raw_text)
                for p in _bitisikleri_ayir(m.group(), m.start())]
    out: list[tuple[str, bool, int, int]] = []
    for i, (ham, bas, son) in enumerate(parcalar):
        birim = ham.strip(_KENAR)
        if not birim:
            continue
        sonrakiler = [p for p, _, _ in parcalar[i + 1:i + 2]]
        if lang == "tr" and birim.isdigit() and _ordinal_dot(ham, birim, sonrakiler):
            birim += "."
        if any(c.isalnum() for c in birim):
            out.append((birim, True, bas, son))
        elif all(c in semboller for c in birim):
            out.append((birim, False, bas, son))
    return out


def _ordinal_dot(ham: str, birim: str, sonrakiler: list[str]) -> bool:
    """The dot after the number is ordinal: a comma follows it, or a word."""
    sonra = ham[ham.find(birim) + len(birim):]
    if not sonra.startswith("."):
        return False
    if sonra[1:2] == ",":
        return True
    return sonra == "." and bool(sonrakiler) and any(c.isalnum() for c in sonrakiler[0])


def cumle_birimleri(raw_text: str, cumleler: list[list[str]], lang: str) -> list[list[str]]:
    """Cümle başına kelime birimleri: ham metin cümle sınırlarından kesilir, her parça
    ``kelime_birimleri`` ile sayılır (varsayılan kelime tanımı, 2026-10-06, Efe).

    ``cumleler`` ``kural_cumleleri``'nin çıktısıdır; tokenları ham metinde sırayla aranır. Kesim
    sonraki cümlenin ilk tokenından, önceki cümlenin son harfli/rakamlı tokenına kadar geriye,
    ilk boşluğa çekilir: kural sınırdan sonraki ``%`` gibi işaretleri önceki cümlede bırakır,
    ``%50`` bölünmesin. Arada boşluk yoksa (``geldi.Sonra``) kesim önceki kelimenin hemen
    sonrasıdır, birim iki cümleye bölünür. Token ham metinde bulunamazsa girdiler hizalı
    değildir, ön işleme hatasıdır → ``ValueError``.
    """
    baslar: list[int] = []
    kelime_sonlari: list[int] = []
    imlec = 0
    for cumle in cumleler:
        son = imlec
        for j, token in enumerate(cumle):
            i = raw_text.find(token, imlec)
            if i < 0:
                raise ValueError(f"token {token!r} not found in raw_text after offset {imlec}"
                                 " — preprocessing error")
            if j == 0:
                baslar.append(i)
            imlec = i + len(token)
            if any(c.isalnum() for c in token):
                son = imlec
        kelime_sonlari.append(son)
    if not baslar:
        return []
    kesimler = [0]
    for bas, onceki_son in zip(baslar[1:], kelime_sonlari, strict=False):
        while bas > onceki_son and not raw_text[bas - 1].isspace():
            bas -= 1
        kesimler.append(bas)
    kesimler.append(len(raw_text))
    return [kelime_birimleri(raw_text[a:b], lang)[0] for a, b in zip(kesimler, kesimler[1:], strict=False)]
