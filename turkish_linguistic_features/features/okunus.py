"""Okunuş: sayıların, yaygın kısaltmaların ve sembollerin yazıya açılması.

Türkçe sayı ve kısaltma (2026-09-16), İngilizce sayı ve iki dilde sembol
(2026-09-17) — Efe'nin kararları.

T10'un hece sayacı (``phonetic.hece_say``) bu modülü kullanır. Çetinkaya-Uzun
(2010) sayım protokolü sembol, kısaltma ve sayıları okunuşlarına göre sayar:
"Cm 4 hece, 1918 7 hece" (Çetinkaya 2010, s.93; Güven 2014, s.516 "1916" diye
aktarıyor). Burada sayılar kuralla, kısaltmalar sabit bir listeyle açılır
(2026-09-16, Efe); hece sayımı açılan metin üzerinden yapılır.

Sıra sayısı (``3.``), saat/skor (``10:30``) ve sayıdan sonraki tek harfli
birim (``100m``) 2026-10-01'den beri okunur (Efe). Okunuşu metinden
belirlenemeyenler (tek başına ``m``, ``/``, ``#``) okunmaz; hece sayımından
atlanırlar — sınırlılıklar §10 (``docs/tr/aciklama/sinirliliklar.md``).
Gerçek kelimeyle aynı yazılan kısaltmalar (tel, sok, av, no) yazıldığı gibi
okunur, bu yüzden listede yok.
"""

from __future__ import annotations

import re

from ..alfabe import _kucuk_harf

_BIRLER = ("", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz")
_ONLAR = ("", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan")
_RAKAMLAR = ("sıfır",) + _BIRLER[1:]
_BUYUKLER = ((10**12, "trilyon"), (10**9, "milyar"), (10**6, "milyon"), (10**3, "bin"))
_UST_SINIR = 10**15

# Tam sayı ya da binlik noktalı sayı, isteğe bağlı ondalık virgülle.
_SAYI = re.compile(r"(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d+))?")

# Yaygın kısaltmalar (2026-09-16, Efe). Anahtar küçük harfli ve noktasız;
# eşleşmede büyük/küçük harf ve noktalar önemsenmez. Gerçek kelimeyle aynı
# yazılanlar (tel, sok, av, no) ve tek harfliler (m, g, l, s) bilerek yok.
KISALTMALAR: dict[str, str] = {
    # uzunluk, ağırlık, hacim, alan
    "mm": "milimetre", "cm": "santimetre", "km": "kilometre",
    "mg": "miligram", "gr": "gram", "kg": "kilogram",
    "ml": "mililitre", "cl": "santilitre", "lt": "litre", "cc": "santimetreküp",
    "m²": "metrekare", "m³": "metreküp",
    # zaman, hız
    "ms": "milisaniye", "sn": "saniye", "dk": "dakika", "km/s": "kilometre bölü saat",
    # bilişim, enerji
    "kw": "kilovat", "mb": "megabayt", "gb": "gigabayt",
    # yazı dili
    "vb": "ve benzeri", "vs": "vesaire", "vd": "ve diğerleri", "bkz": "bakınız",
    "örn": "örneğin", "yy": "yüzyıl",
    # tarih
    "mö": "milattan önce",
    # unvan, adres
    "dr": "doktor", "prof": "profesör", "doç": "doçent",
    "cad": "cadde", "mah": "mahalle", "apt": "apartman",
    # kurum, para
    "tc": "Türkiye Cumhuriyeti", "abd": "a be de", "tl": "Türk lirası",
}

# Büyük/küçük harfe göre anlamı değişenler — önce bunlara bakılır.
_KISALTMA_TAM_YAZIM: dict[str, str] = {
    "MS": "milattan sonra",     # ms → milisaniye
    "Sn": "sayın",              # sn, SN → saniye
}


def _uc_basamak(n: int) -> list[str]:
    """1–999 arası sayının kelimeleri; 100 → "yüz" ("bir yüz" değil)."""
    yuz, kalan = divmod(n, 100)
    on, bir = divmod(kalan, 10)
    kelimeler = []
    if yuz:
        kelimeler += ([_BIRLER[yuz]] if yuz > 1 else []) + ["yüz"]
    return kelimeler + [k for k in (_ONLAR[on], _BIRLER[bir]) if k]


def _tam_sayi(n: int) -> list[str]:
    """Tam sayının kelimeleri; 1000 → "bin" ("bir bin" değil), 10**6 → "bir milyon"."""
    if n == 0:
        return ["sıfır"]
    kelimeler: list[str] = []
    for deger, ad in _BUYUKLER:
        kat, n = divmod(n, deger)
        if kat:
            if not (deger == 1000 and kat == 1):
                kelimeler += _uc_basamak(kat)
            kelimeler.append(ad)
    return kelimeler + (_uc_basamak(n) if n else [])


def _basamaklar(rakamlar: str) -> list[str] | None:
    """Başı sıfırsa rakam rakam okunur (0532, ondalık 05); değilse tam sayı."""
    if len(rakamlar) > 1 and rakamlar[0] == "0":
        return [_RAKAMLAR[int(c)] for c in rakamlar]
    n = int(rakamlar)
    return None if n >= _UST_SINIR else _tam_sayi(n)


def sayi_oku(token: str) -> str | None:
    """Sayıyı Türkçe okunuşuna çevirir; sayı biçiminde değilse ``None``.

    ``1916`` → "bin dokuz yüz on altı" · ``12.500.000`` (binlik nokta) ·
    ``3,5`` → "üç virgül beş" · ``0532`` → rakam rakam. 10**15 ve üstü,
    sıra sayısı (``2.``), saat (``10:30``) ve karışık biçimler (``3G``) → ``None``.
    """
    m = _SAYI.fullmatch(token)
    if m is None:
        return None
    tam = _basamaklar(m.group(1).replace(".", ""))
    if tam is None:
        return None
    if m.group(2) is None:
        return " ".join(tam)
    ondalik = _basamaklar(m.group(2))
    return None if ondalik is None else " ".join(tam + ["virgül"] + ondalik)


def kisaltma_oku(token: str) -> str | None:
    """Listedeki kısaltmanın açılımı; listede yoksa ``None``."""
    yalin = token.replace(".", "")
    if yalin in _KISALTMA_TAM_YAZIM:
        return _KISALTMA_TAM_YAZIM[yalin]
    return KISALTMALAR.get(_kucuk_harf(yalin, "tr"))


def okunus(token: str) -> str | None:
    """Kısaltma, sayı, saat/skor ya da sıra sayısıysa Türkçe okunuşu, değilse ``None``."""
    for oku in (kisaltma_oku, sayi_oku, read_time, read_ordinal):
        acilim = oku(token)
        if acilim is not None:
            return acilim
    return None


# ── Turkish ordinals, times, units after a number (2026-10-01, Efe) ──
#
# The token alone cannot tell an ordinal "3." from a sentence-final "3.";
# callers that see the next token decide (``phonetic``, ``readability``).

_ORDINAL = re.compile(r"(\d+)\.")
_COLON_PAIR = re.compile(r"(\d+):(\d+)")
# Turkish writes the decimal separator as a comma and groups thousands in
# threes, so "10.30" (two digits after the dot) can only be a time.
_DOT_TIME = re.compile(r"(\d{1,2})\.(\d{2})")

# Single-letter units are ambiguous on their own ("m": metre or minute) but
# not right after a number ("100m"). Lowercase only: "3G" is read as letters.
UNITS_AFTER_NUMBER: dict[str, str] = {"m": "metre", "g": "gram", "l": "litre"}

_FRONT_VOWELS = frozenset("eiöü")
_ROUNDED_VOWELS = frozenset("ouöü")


def _ordinal_suffix(word: str) -> str:
    """-(I)ncI with vowel harmony; the buffer vowel drops after a vowel."""
    last = next(c for c in reversed(word) if c in "aeıioöuü")
    front, rounded = last in _FRONT_VOWELS, last in _ROUNDED_VOWELS
    vowel = ("ü" if rounded else "i") if front else ("u" if rounded else "ı")
    suffix = f"nc{vowel}"
    return suffix if word[-1] in "aeıioöuü" else vowel + suffix


def read_ordinal(token: str) -> str | None:
    """``3.`` → "üçüncü"; ``None`` if the token is not digits + one dot."""
    m = _ORDINAL.fullmatch(token)
    if m is None:
        return None
    n = int(m.group(1))
    if n >= _UST_SINIR:
        return None
    words = _tam_sayi(n)
    last = "dörd" if words[-1] == "dört" else words[-1]   # t → d before a vowel
    return " ".join(words[:-1] + [last + _ordinal_suffix(last)])


def read_time(token: str) -> str | None:
    """``10:30`` / ``10.30`` → "on otuz"; ``3:2`` → "üç iki" (scores, ratios).

    In a time the hour is read as a number and ":00" is not read
    (``14:00`` → "on dört"); other minutes keep a leading zero ("sıfır beş").
    """
    m = _COLON_PAIR.fullmatch(token) or _DOT_TIME.fullmatch(token)
    if m is None:
        return None
    left, right = m.group(1), m.group(2)
    is_time = len(right) == 2 and int(left) <= 24 and int(right) < 60
    if m.re is _DOT_TIME and not is_time:
        return None
    if is_time:
        hour = _tam_sayi(int(left))
        return " ".join(hour if right == "00" else hour + (_basamaklar(right) or []))
    parts = [_basamaklar(left), _basamaklar(right)]
    if parts[0] is None or parts[1] is None:
        return None
    return " ".join(parts[0] + parts[1])


# ── İngilizce sayılar (2026-09-17, Efe) ──────────────────────────────
#
# Kincaid ve ark. (1975) Flesch talimatı: sayılar okunuşuyla hecelenir,
# "1918 (nineteen eighteen) 4 syllables". ABD okunuşu ("and" yok).
# Ayırıcısız dört haneli 1100–1999 ve 2010–2099 yıl gibi ikişer okunur;
# "1500 soldiers" gibi miktarlar da böyle okunur — bilinen sınırlama.

_EN_BIRLER = ("", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
              "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
              "seventeen", "eighteen", "nineteen")
_EN_ONLAR = ("", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety")
_EN_RAKAMLAR = ("zero",) + _EN_BIRLER[1:10]
_EN_BUYUKLER = ((10**12, "trillion"), (10**9, "billion"), (10**6, "million"), (10**3, "thousand"))
_EN_SAYI = re.compile(r"(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d+))?")


def _en_iki_basamak(n: int) -> list[str]:
    """1–99."""
    if n < 20:
        return [_EN_BIRLER[n]]
    on, bir = divmod(n, 10)
    return [_EN_ONLAR[on]] + ([_EN_BIRLER[bir]] if bir else [])


def _en_uc_basamak(n: int) -> list[str]:
    """1–999; 105 → "one hundred five"."""
    yuz, kalan = divmod(n, 100)
    kelimeler = [_EN_BIRLER[yuz], "hundred"] if yuz else []
    return kelimeler + (_en_iki_basamak(kalan) if kalan else [])


def _en_tam_sayi(n: int) -> list[str]:
    if n == 0:
        return ["zero"]
    kelimeler: list[str] = []
    for deger, ad in _EN_BUYUKLER:
        kat, n = divmod(n, deger)
        if kat:
            kelimeler += _en_uc_basamak(kat) + [ad]
    return kelimeler + (_en_uc_basamak(n) if n else [])


def _en_yil(n: int) -> list[str]:
    """1918 → nineteen eighteen · 1905 → nineteen oh five · 1900 → nineteen hundred."""
    bas, son = divmod(n, 100)
    if son == 0:
        return _en_iki_basamak(bas) + ["hundred"]
    if son < 10:
        return _en_iki_basamak(bas) + ["oh", _EN_BIRLER[son]]
    return _en_iki_basamak(bas) + _en_iki_basamak(son)


def sayi_oku_en(token: str) -> str | None:
    """Sayıyı İngilizce okunuşuna çevirir; sayı biçiminde değilse ``None``.

    Virgül binlik ayırıcı (``32,008``), nokta ondalık (``3.14`` → "three point
    one four"); başı sıfırsa rakam rakam. 10**15 ve üstü → ``None``.
    """
    m = _EN_SAYI.fullmatch(token)
    if m is None:
        return None
    tam, ondalik = m.group(1), m.group(2)
    if len(tam) > 1 and tam[0] == "0":
        kelimeler = [_EN_RAKAMLAR[int(c)] for c in tam]
    else:
        n = int(tam.replace(",", ""))
        if n >= _UST_SINIR:
            return None
        yil = "," not in tam and ondalik is None and (1100 <= n <= 1999 or 2010 <= n <= 2099)
        kelimeler = _en_yil(n) if yil else _en_tam_sayi(n)
    if ondalik is not None:
        kelimeler += ["point"] + [_EN_RAKAMLAR[int(c)] for c in ondalik]
    return " ".join(kelimeler)


# ── Semboller (2026-09-17, Efe) ──────────────────────────────────────
#
# Kincaid ve ark. (1975) ve Çetinkaya protokolü sembolleri okunuşlarıyla
# sayar. Düz yazıda geçen semboller; okunuşu bağlama göre değişenler
# (#, /, *, ~, ^, |) ve noktalama olarak kullanılan tire (-) bilerek yok.

SEMBOLLER: dict[str, dict[str, str]] = {
    "tr": {
        "%": "yüzde", "$": "dolar", "€": "avro", "£": "sterlin", "₺": "lira",
        "¢": "sent", "&": "ve", "+": "artı", "−": "eksi", "=": "eşittir",
        "°": "derece", "§": "paragraf", "@": "et", "×": "çarpı", "÷": "bölü",
        "<": "küçüktür", ">": "büyüktür", "±": "artı eksi",
    },
    "en": {
        "%": "percent", "$": "dollars", "€": "euros", "£": "pounds", "₺": "lira",
        "¢": "cents", "&": "and", "+": "plus", "−": "minus", "=": "equals",
        "°": "degrees", "§": "section", "@": "at", "×": "times", "÷": "divided by",
        "<": "less than", ">": "greater than", "±": "plus or minus",
    },
}


def sembol_oku(sembol: str, lang: str) -> str | None:
    """Listedeki sembolün okunuşu; listede yoksa ``None``."""
    return SEMBOLLER[lang].get(sembol)
