"""Tümce kuralı: aracın tümce tanımı ve okunabilirlik formüllerinin tümce sayımı.

Tümce = formüle özel işaretlerden biriyle biten dizi (``_CUMLE_SONU``). İşaretler spaCy
türcelerinden okunur, böylece ``Dr.`` tümce bitirmez. Varsayılan kural (``kural_cumleleri``)
bütün aracın tümcesidir; Akana'nın belirsizlik gidericisine giden tümceler de bunlardır.
Yalnız ``syntactic`` spaCy'nin ayrıştırıcı tümcesini kullanır.

Saf hesap; paket içinden yalnız L0'ı ve ``units``i görür.
"""

from __future__ import annotations

from ..alphabet import _kucuk_harf
from .spoken_forms import kisaltma_oku

__all__ = ["cumle_sayisi", "kural_cumleleri"]

# Formüle göre cümle bitiren işaretler.
#
# Üç nokta (2026-10-06, Efe): "..." ve tek karakterli "…" aynı işarettir (noktalama modülü de öyle
# sayıyor) ve ikisi de cümle bitirir. Eskiden "..." tokenı "." içerdiği için bitiriyordu, "…"
# bitirmiyordu; aynı metin yazım biçimine göre farklı sayılıyordu. Bu yüzden "…" her kümede var.
#
# Varsayılan cümle tanımı (2026-10-06, Efe): . ? ! … her zaman, ":" KOŞULLU. Koşullu işaret yalnız
# sonrası yeni bir cümle gibi başlıyorsa (büyük harf, tırnak, tire ya da açılış parantezi) cümle
# bitirir; küçük harf ya da rakamla sürüyorsa (liste, açıklama, 10:30) bitirmez. Gerekçe ve veri:
# tez klasörü acik-konular.md §1.
_CUMLE_SONU = {
    "varsayilan": ".?!…",       # McLaughlin 1969; Kincaid ARI; Coleman & Liau; kaynağı kural vermeyenler
    # Kincaid ve ark. 1975 Flesch talimatı ; ve : sayıyor ama iki noktadan sonra tam cümle gelmiyorsa
    # saymıyor. "Tam cümle" yargısının yaklaşığı koşullu ":" (büyük harf/tırnak/tire/parantez).
    "kincaid": ".?!;…",
    # Çetinkaya (2010, s.93): nokta, soru, iki nokta ve "iki parantez ( ) bitirilmiş bir
    # tümce"; parantezin içi ayrı cümle. Ünlem listede yok ama "dilbilgisel olarak bağımsız
    # her birim tümcedir" ölçütüne girer (2026-09-17, Efe). Kaynak ":" için koşul koymuyor.
    "cetinkaya": ".?!:()…",
}
# Koşullu cümle bitiren işaretler (kümenin kendi işaretlerine ek).
_CUMLE_KOSULLU = {"varsayilan": ":", "kincaid": ":", "cetinkaya": ""}

# Koşullu işaretten sonra yeni cümleyi gösteren açılış karakterleri (büyük harf ayrıca denetlenir).
_YENI_CUMLE_ACILIS = "\"'“”‘’«»‹›—–-(["
# Yalnız açılış olduğu kesin olanlar: cümle sınırından sonra sonraki cümleye geçerler.
_ACILIS_ONLY = "“‘«‹([—–-"
# Reference abbreviations point at what follows ("bkz. Ek 2"), so their dot never ends a
# sentence, even before a capital (2026-11-26, Efe). "bk." and "bknz." spell the same word.
_REFERENCE_ABBREVIATIONS = frozenset({"bkz", "bk", "bknz"})


def _kucuk_harfli_kisaltma(token: str) -> bool:
    """A token spaCy kept together with its dot (``vb.``, ``dk.``) that starts lower case.

    Turkish writes titles, addresses and company types with a capital (``Dr.``, ``Cad.``,
    ``Ltd.``): they lead into the name after them and never end a sentence. A lower-case
    abbreviation can close a sentence, so it ends one when a capital follows (2026-11-26, Efe).
    """
    return (len(token) > 1 and token.endswith(".") and token[0].islower()
            and any(c.isalpha() for c in token)
            and _kucuk_harf(token.rstrip("."), "tr") not in _REFERENCE_ABBREVIATIONS)


def _isaret_mi(token: str) -> bool:
    return bool(token) and not any(c.isalnum() for c in token)


def _baslik_harfli(token: str) -> bool:
    return token[:1].isupper()


def _yeni_cumle_basliyor(sonraki: list[str]) -> bool:
    """İşaretten sonra gelen tokenlar yeni bir cümle gibi mi başlıyor?

    İlk token büyük harfle başlıyorsa ya da bir tırnak, tire, açılış parantezi ise evet; küçük harf
    ya da rakamla başlıyorsa hayır; metin bitiyorsa evet (son cümle zaten ayrı sayılır).

    İşaret sözcüğe bitişikse de ilk karaktere bakılır (2026-10-26, Efe): spaCy ``: -Bence``'yi
    ``-Bence`` diye tek token tutar; belgedeki kurala göre tire cümle bitirir.
    """
    if not sonraki:
        return True
    ilk = sonraki[0]
    if ilk[0] in _YENI_CUMLE_ACILIS:
        return True
    if _isaret_mi(ilk):
        return False
    return ilk[0].isupper()


def _sinirlar(surface_tokens: list[str], isaretler: str, lang: str,
              kosullu: str = "") -> tuple[list[int], bool]:
    """Cümle bitiren işaret tokenlarının indeksleri ve metnin açık cümleyle bitip bitmediği."""
    sinirlar: list[int] = []
    acik = False
    onceki = ""
    for i, token in enumerate(surface_tokens):
        if not _isaret_mi(token):
            if any(c.isalnum() for c in token):
                acik = True
                onceki = token
                if lang == "tr" and "." in isaretler and _kucuk_harfli_kisaltma(token):
                    sonraki = next((t for t in surface_tokens[i + 1:] if not _isaret_mi(t)), None)
                    if sonraki is not None and _baslik_harfli(sonraki):
                        sinirlar.append(i)
                        acik = False
            continue
        if not acik:
            continue
        if any(c in isaretler for c in token):
            if lang == "tr" and token == "." and kisaltma_oku(onceki) is not None:
                sonraki = next((t for t in surface_tokens[i + 1:] if not _isaret_mi(t)), None)
                if sonraki is not None and (_kucuk_harf(onceki, "tr") in _REFERENCE_ABBREVIATIONS
                                            or not _baslik_harfli(sonraki)):
                    continue
        elif kosullu and any(c in kosullu for c in token):
            if not _yeni_cumle_basliyor(surface_tokens[i + 1:]):
                continue
        else:
            continue
        sinirlar.append(i)
        acik = False
    return sinirlar, acik


def cumle_sayisi(surface_tokens: list[str], isaretler: str, lang: str, kosullu: str = "") -> int:
    """``isaretler``den biriyle biten cümle sayısı; işaretsiz biten metin +1.

    Ardışık işaret tokenları (``?!``, ``."``) tek sınırdır. spaCy'nin tek token
    tuttuğu kısaltmalar (``Dr.``, ``Jan.``) cümle bitirmez. Türkçede spaCy'nin
    böldüğü listedeki kısaltmadan (``km`` + ``.``) sonraki nokta, ardından
    büyük harfle başlayan bir kelime gelmiyorsa sınır sayılmaz; gönderme kısaltmasından
    (``bkz``) sonraki nokta hiç sınır sayılmaz. spaCy'nin noktasıyla tek token tuttuğu küçük
    harfli kısaltma (``vb.``) ardından büyük harf gelirse cümle bitirir; büyük harfli olan
    (``Dr.``) bitirmez.

    ``kosullu``: yalnız sonrası yeni bir cümle gibi başlıyorsa (büyük harf, tırnak, tire, açılış
    parantezi) cümle bitiren işaretler (varsayılan kuralda ``":"``). ``10:30`` gibi rakamlar arası
    iki nokta tek token olduğundan hiç sınır olmaz.
    """
    sinirlar, acik = _sinirlar(surface_tokens, isaretler, lang, kosullu)
    return len(sinirlar) + (1 if acik else 0)


def kural_cumleleri(surface_tokens: list[str], lang: str) -> list[list[str]]:
    """Varsayılan kuralla cümle listesi; birleştirilince ``surface_tokens``'i verir.

    Sınırlar ``cumle_sayisi(..., "varsayilan")`` ile aynı koddan gelir. Sınırdan sonra gelen
    işaret tokenları (kapanış tırnağı ``."``) önceki cümlede kalır; yalnız açılış karakterleri
    (``“ ‘ « ( [`` ve tireler) sonraki cümleyi başlatır. Düz ``"`` belirsiz olduğundan öncekinde
    kalır. Sınır hiç yoksa tek cümledir; boş girdi için ``[]``.
    """
    sinirlar, _ = _sinirlar(surface_tokens, _CUMLE_SONU["varsayilan"], lang,
                            _CUMLE_KOSULLU["varsayilan"])
    n = len(surface_tokens)
    cumleler: list[list[str]] = []
    bas = 0
    for b in sinirlar:
        son = b + 1
        while (son < n and _isaret_mi(surface_tokens[son])
               and surface_tokens[son][0] not in _ACILIS_ONLY):
            son += 1
        cumleler.append(list(surface_tokens[bas:son]))
        bas = son
    if bas < n:
        if cumleler and not any(any(c.isalnum() for c in t) for t in surface_tokens[bas:]):
            cumleler[-1].extend(surface_tokens[bas:])
        else:
            cumleler.append(list(surface_tokens[bas:]))
    return cumleler
