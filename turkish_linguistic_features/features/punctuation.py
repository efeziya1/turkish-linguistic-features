"""Noktalama, rakam, boşluk, büyük harf ve harf dağılımı.

Bu modül iki grubun anahtarlarını üretir:

- ``punctuation`` (18): ``digit_ratio``, 10 × ``punct_*_ratio``, ``punct_char_ratio``,
  ``punct_entropy``, ``consecutive_punct_ratio``, ``whitespace_ratio``,
  ``punct_variety``, ``uppercase_ratio``, ``all_caps_word_ratio``
- ``chars`` (dinamik): ``char_{harf}_ratio`` — TR 29, EN 26

Noktalama **işaret** düzeyinde sayılır, karakter düzeyinde değil (Efe'nin
kararları, 2026-09-15):

- ``...`` (3 ve üstü nokta) ve ``…`` tek bir üç nokta işaretidir; içindeki
  noktalar nokta sayılmaz
- ``“ ” ‘ ’ « »`` ve düz tırnaklar aynı **tırnak** türüdür, ``- – —`` aynı **tire**
  türü — tipografi tercihi entropiyi ve çeşitliliği değiştirmez
- ``'`` ya da ``’`` iki harf arasındaysa (``Ankara’ya``, ``don’t``) kesme
  işaretidir: noktalama sayılmaz

Fonksiyonlar saftır (K3). K4 (2026-09-16, Efe): ölçülemeyen değer ``math.nan``
döner — boş metin, harfli token yok, işaret yokken işaret dağılımı. ``0.0``
yalnız gerçek sıfırdır (işaretsiz metinde ``punct_char_ratio``).
"""

from __future__ import annotations

import math
from collections import Counter

from ..alfabe import _ALFABE, _kucuk_harf

# Karakter → işaret türü. Tür adları punct_{tür}_ratio anahtarlarının ortasıdır.
_TUR: dict[str, str] = {
    ",": "comma", ".": "period", ";": "semicolon", "!": "exclamation", ":": "colon", "?": "question",
    "-": "dash", "–": "dash", "—": "dash",
    "…": "ellipsis",
    "(": "paren", ")": "paren",
    '"': "quote", "“": "quote", "”": "quote", "«": "quote", "»": "quote",
    "'": "quote", "‘": "quote", "’": "quote",
}
_PUNCT_CHARS = frozenset(_TUR)
_TURLER = ("comma", "period", "semicolon", "exclamation", "colon", "dash",
           "ellipsis", "paren", "quote", "question")
_KESME = frozenset("'’")


def _isaretler(metin: str) -> list[tuple[int, int, str]]:
    """Metindeki noktalama işaretleri, soldan sağa: ``(başlangıç, bitiş, tür)``."""
    out: list[tuple[int, int, str]] = []
    i, n = 0, len(metin)
    while i < n:
        ch = metin[i]
        if ch == ".":
            j = i
            while j < n and metin[j] == ".":
                j += 1
            if j - i >= 3:
                out.append((i, j, "ellipsis"))
            else:
                out.extend((k, k + 1, "period") for k in range(i, j))
            i = j
            continue
        if ch in _PUNCT_CHARS:
            kelime_ici = ch in _KESME and 0 < i < n - 1 and metin[i - 1].isalpha() and metin[i + 1].isalpha()
            if not kelime_ici:
                out.append((i, i + 1, _TUR[ch]))
        i += 1
    return out


def _entropy_nats(sayimlar: Counter) -> float:
    toplam = sum(sayimlar.values())
    if toplam == 0:
        return math.nan
    return -sum((c / toplam) * math.log(c / toplam) for c in sayimlar.values()) + 0.0


# ── işaretler içindeki pay ────────────────────────────────────────────


def punctuation_ratios(text: str) -> dict[str, float]:
    """10 noktalama türünün bütün işaretler içindeki payı; toplamları 1.

    Pay olarak (2026-10-08, Efe); önceden kelime başına sıklıktı ve 1'i
    aşabiliyordu. Noktalamanın yoğunluğu ``punct_char_ratio``'da;
    ``punct_total_ratio`` aynı bilgiyi kelime başına verdiği için kaldırıldı.

    ``punct_dash_ratio`` üç tireyi (``- – —``), ``punct_quote_ratio`` bütün tırnak
    biçimlerini, ``punct_paren_ratio`` iki parantezi ayrı ayrı sayar. İşaret yoksa NaN.
    """
    say = Counter(tur for _, _, tur in _isaretler(text))
    toplam = sum(say.values())
    if toplam == 0:
        return {f"punct_{t}_ratio": math.nan for t in _TURLER}
    return {f"punct_{t}_ratio": round(say.get(t, 0) / toplam, 6) for t in _TURLER}


# ── karakter düzeyi oranlar ───────────────────────────────────────────


def digit_ratio(text: str) -> dict[str, float]:
    """Rakam karakteri / tüm karakterler. Boş metinde NaN."""
    if not text:
        return {"digit_ratio": math.nan}
    return {"digit_ratio": round(sum(ch.isdecimal() for ch in text) / len(text), 6)}


def whitespace_ratio(text: str) -> dict[str, float]:
    """Boşluk karakteri (satır sonu ve sekme dahil) / tüm karakterler. Boş metinde NaN."""
    if not text:
        return {"whitespace_ratio": math.nan}
    return {"whitespace_ratio": round(sum(ch.isspace() for ch in text) / len(text), 6)}


def punct_char_ratio(text: str) -> dict[str, float]:
    """Noktalama işareti sayısı / tüm karakterler. ``...`` bir işarettir. Boş metinde NaN."""
    if not text:
        return {"punct_char_ratio": math.nan}
    return {"punct_char_ratio": round(len(_isaretler(text)) / len(text), 6)}


def punct_entropy(text: str) -> dict[str, float]:
    """Noktalama **türü** dağılımının Shannon entropisi, nat cinsinden. İşaret yoksa NaN."""
    return {"punct_entropy": round(_entropy_nats(Counter(t for _, _, t in _isaretler(text))), 6)}


def consecutive_punct_ratio(text: str) -> dict[str, float]:
    """Arada karakter olmadan başka bir işarete bitişik işaretlerin oranı.

    ``Ne!!!`` → 1.0. ``Bekledi...`` → 0.0: üç nokta tek işarettir, dizi değil.
    İşaret yoksa NaN.
    """
    isaretler = _isaretler(text)
    if not isaretler:
        return {"consecutive_punct_ratio": math.nan}
    bitisik = sum(
        1 for k, (bas, son, _) in enumerate(isaretler)
        if (k > 0 and isaretler[k - 1][1] == bas) or (k + 1 < len(isaretler) and isaretler[k + 1][0] == son)
    )
    return {"consecutive_punct_ratio": round(bitisik / len(isaretler), 6)}


def punct_variety(text: str) -> dict[str, float]:
    """Kullanılan farklı noktalama türü sayısı (en fazla 10). Boş metinde NaN, işaretsiz metinde 0."""
    if not text:
        return {"punct_variety": math.nan}
    return {"punct_variety": float(len({t for _, _, t in _isaretler(text)}))}


# ── büyük harf ────────────────────────────────────────────────────────


def _harfli(tokenler: list[str]) -> list[list[str]]:
    """Her harf içeren tokenin yalnız harfleri; harfsiz tokenler atlanır."""
    return [h for h in ([ch for ch in t if ch.isalpha()] for t in tokenler) if h]


def uppercase_ratio(surface_tokens: list[str]) -> dict[str, float]:
    """İlk harfi büyük olan tokenler / harf içeren tokenler.

    Noktalama ve sayı tokenleri paydaya girmez. Cümle başı büyük harfi dahildir.
    Harfli token yoksa NaN.
    """
    harfli = _harfli(surface_tokens)
    if not harfli:
        return {"uppercase_ratio": math.nan}
    return {"uppercase_ratio": round(sum(h[0].isupper() for h in harfli) / len(harfli), 6)}


def all_caps_word_ratio(surface_tokens: list[str]) -> dict[str, float]:
    """Tamamı büyük harf, en az 2 harfli tokenler / harf içeren tokenler.

    Tek harfli ``A`` ya da İngilizce ``I`` sayılmaz. Harfli token yoksa NaN.
    """
    harfli = _harfli(surface_tokens)
    if not harfli:
        return {"all_caps_word_ratio": math.nan}
    caps = sum(1 for h in harfli if len(h) >= 2 and all(ch.isupper() for ch in h))
    return {"all_caps_word_ratio": round(caps / len(harfli), 6)}


# ── harf dağılımı ─────────────────────────────────────────────────────


def char_freq_vector(text: str, lang: str) -> dict[str, float]:
    """Alfabedeki her harfin oranı: ``harf sayısı / alfabedeki harflerin toplamı``.

    Metin dile göre küçük harfe indirilir (TR'de ``I → ı``, ``İ → i``). Alfabe
    dışı harfler (TR'de ``q w x``) sayılmaz; vektörün toplamı 1'dir. Alfabe
    harfi yoksa bütün vektör NaN.

    Raises
    ------
    ValueError
        ``lang`` ``"tr"`` ya da ``"en"`` değilse.
    """
    if lang not in _ALFABE:
        raise ValueError(f"Unsupported language: {lang!r}. Expected one of: {sorted(_ALFABE)}")
    alfabe = _ALFABE[lang]
    say = Counter(ch for ch in _kucuk_harf(text, lang) if ch in alfabe)
    toplam = sum(say.values())
    return {f"char_{h}_ratio": round(say.get(h, 0) / toplam, 6) if toplam else math.nan for h in alfabe}
