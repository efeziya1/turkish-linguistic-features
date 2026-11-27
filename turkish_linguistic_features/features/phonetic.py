"""Ses ve yazı örüntüleri: ünlü oranları ile büyük ve küçük ünlü uyumu.

Bu modül ``phonological`` grubunun 14 anahtarını üretir (İngilizcede ünlü uyumu yok, 12):

- T09 (5): ``vowel_ratio`` · ``front_vowel_ratio`` · ``back_vowel_ratio`` ·
  ``harmony_fronting_ratio`` · ``harmony_rounding_ratio``
- T10 (9): ``syllable_count`` · ``syllable_mean`` · ``syllable_1_ratio`` … ``syllable_5_ratio`` ·
  ``syllable_6plus_ratio`` · ``sent_syllable_mean``

T10'un ``hece_say`` / ``birim_hecesi`` fonksiyonları T13'ün Türkçe okunabilirlik
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
import re
from collections import Counter

import numpy as np
import textstat

from ..alphabet import _ALFABE, _dil_denetle, _kucuk_harf
from ..exceptions import ModelNotFoundError
from ..units.spoken_forms import SEMBOLLER, UNITS_AFTER_NUMBER, okunus, sayi_oku, sayi_oku_en

_UNLULER: dict[str, str] = {"tr": "aeıioöuü", "en": "aeiou"}
_ON: dict[str, str] = {"tr": "eiöü", "en": "ei"}
_ARKA: dict[str, str] = {"tr": "aıou", "en": "aou"}
# Küçük ünlü uyumu (Göksel & Kerslake 2005 s.22). İngilizcede böyle bir olgu
# yok; kümeler yalnız grubun iki dilde de üretilmesi için tanımlı.
_YUVARLAK: dict[str, str] = {"tr": "oöuü", "en": "ou"}
_DAR_YUVARLAK: dict[str, str] = {"tr": "uü", "en": "u"}
_GENIS_DUZ: dict[str, str] = {"tr": "ae", "en": "ae"}


# İngilizce hece sayımı (textstat ≥ 0.7.10) NLTK'nın `cmudict` verisini ister
# ve veri yoksa textstat onu kendisi internetten indirir; ağ yoksa `LookupError`
# ile çöker. Kütüphane ortama kendiliğinden bir şey yazmaz (spaCy modelleriyle
# aynı ilke): textstat'ı çağırmadan önce `nltk.data.find` ile bakıyoruz —
# indirme yapmaz, `NLTK_DATA` ortam değişkenine uyar. Bulununca bayrak
# kalkar, kelime başına tekrar aranmaz.
_CMUDICT_VAR = False
_CMUDICT_KOMUTU = "python -m nltk.downloader cmudict"


def _cmudict_denetle() -> None:
    """cmudict kurulu değilse ``ModelNotFoundError``; kuruluysa hiçbir şey."""
    global _CMUDICT_VAR
    if _CMUDICT_VAR:
        return
    import nltk
    try:
        nltk.data.find("corpora/cmudict")
    except LookupError:
        raise ModelNotFoundError(
            "NLTK's 'cmudict' corpus is required for English syllable counts "
            "(phonetic and readability features) but is not installed.\n\n"
            f"Install it once with:\n    {_CMUDICT_KOMUTU}\n\n"
            "The library never downloads it by itself. To use a custom location, "
            "set the NLTK_DATA environment variable."
        ) from None
    _CMUDICT_VAR = True


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


def vowel_harmony_ratios(surface_tokens: list[str], lang: str = "tr") -> dict[str, float]:
    """Türkçenin iki ünlü uyumuna uyan kelime oranları.

    Göksel & Kerslake (2005) s.22 iki ayrı süreç tanımlıyor ve ikisi
    bağımsız — ``kitap`` büyük uyuma uymaz ama küçük uyuma uyar:

    ``harmony_fronting_ratio`` (büyük ünlü uyumu)
        *"A front vowel can only be followed by a front vowel and a back
        vowel can only be followed by a back vowel."* Kelimenin bütün
        ünlüleri ya ince ya kalınsa uyumludur.

    ``harmony_rounding_ratio`` (küçük ünlü uyumu)
        *"Unless it is in the first syllable of a word, a rounded vowel
        occurs only when it is preceded by another rounded vowel"* ve
        *"'o' and 'ö' only occur in the initial syllable"*. İkisi birlikte:
        düz ünlüden sonra düz; yuvarlaktan sonra ya dar yuvarlak ya geniş düz.

    En az iki ünlüsü olmayan kelime (``ev``, noktalama, sayı) **iki ölçüde
    de** paydaya girmez — uyum onlar için tanımsız; hiç sayılacak kelime
    yoksa NaN.

    🔴 Ölçü **yüzey örüntüsü** sayıyor, dilbilgisel doğruluk değil. Göksel &
    Kerslake §3.4 uyuma girmeyen sözcükleri kuralın **istisnası** olarak
    veriyor: yerli kökler (``anne``, ``elma``), bileşikler (``bugün``) ve
    alıntılar (``kitap``, ``kalem``, ``fasulye``). Uyuma girmeyen ekler
    (``-yor``, ``-ki``, ``-ken``) de yerli kelimeyi uyumsuz yapıyor
    (``geliyor``). Yani ölçü alıntı ve bu eklerin sıklığını birlikte taşır;
    düşük değer "daha az Türkçe" demek değildir (2026-09-19, Efe).

    Küçük uyum aslında bir **ek** olayı (G&K: *"only affects suffixes and
    clitics with high vowels"*); bütün-kelime örüntüsü olarak ölçmek bilinçli
    bir basitleştirmedir.
    """
    _dil_denetle(lang)
    on, arka = set(_ON[lang]), set(_ARKA[lang])
    unluler = set(_UNLULER[lang])
    yuvarlak = set(_YUVARLAK[lang])
    yuvarlak_sonrasi = set(_DAR_YUVARLAK[lang]) | set(_GENIS_DUZ[lang])
    ince_kalin = 0
    duz_yuvarlak = 0
    sayilan = 0
    for token in surface_tokens:
        v = [c for c in _kucuk_harf(token, lang) if c in unluler]
        if len(v) < 2:
            continue
        sayilan += 1
        if all(c in on for c in v) or all(c in arka for c in v):
            ince_kalin += 1
        if all((sonraki in yuvarlak_sonrasi) if onceki in yuvarlak
               else (sonraki not in yuvarlak)
               for onceki, sonraki in zip(v, v[1:], strict=False)):
            duz_yuvarlak += 1
    if sayilan == 0:
        return {"harmony_fronting_ratio": math.nan, "harmony_rounding_ratio": math.nan}
    return {"harmony_fronting_ratio": round(ince_kalin / sayilan, 5),
            "harmony_rounding_ratio": round(duz_yuvarlak / sayilan, 5)}


# ── T10: heceleme ─────────────────────────────────────────────────────
#
# Heceleme kuralı = TDK, "Hece Yapısı ve Satır Sonunda Kelimelerin Bölünmesi"
# (tdk.gov.tr, 2019): iki ünlü arasındaki ünsüzlerden yalnız sonuncusu sonraki
# ünlüyle hece kurar (al-dı, alt-lık, Türk-çe); Batı kökenli kelimelere de aynı
# kural uygulanır (prog-ram, kont-rol, sant-ral); yan yana iki ünlü ayrı hecedir
# (sa-at, Ka-ra-os-ma-noğ-lu). Kelime başı ve sonu ünsüzleri ilk/son hecede
# kalır (tren, stra-te-ji). Liste gerekmez. KEMİK hece tablosu da bu kuralla
# hecelenmiş (tlf-kaynaklar/00-INDEKS.md).

# â î û are vowels: the circumflex is placed over a vowel (Göksel & Kerslake 2005, p.xxiii).
_TR_HECE_UNLULERI = frozenset("aeıioöuüâîû")
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
    for v1, v2 in zip(unluler, unluler[1:], strict=False):
        sinir = v1 + 1 if v2 == v1 + 1 else v2 - 1   # yan yana ünlü | son ünsüz sonraki heceye
        heceler.append(word[bas:sinir])
        bas = sinir
    heceler.append(word[bas:])
    return heceler


def _unlu_sayisi(metin: str) -> int:
    return sum(1 for c in _kucuk_harf(metin, "tr") if c in _TR_HECE_UNLULERI)


# A number glued to letters: "3kg", "100m", "3G", "2li" (2026-10-01, Efe).
_NUMBER_LETTERS = re.compile(r"(\d+(?:,\d+)?)([^\W\d_]+)")


def _tr_kok_hecesi(kok: str) -> int | None:
    """Kesme işaretinden önceki kısmın hecesi (Türkçe)."""
    acilim = okunus(kok)
    if acilim is not None:
        return _unlu_sayisi(acilim)
    glued = _NUMBER_LETTERS.fullmatch(kok)
    if glued is not None:
        number = sayi_oku(glued.group(1))
        letters = glued.group(2)
        unit = UNITS_AFTER_NUMBER.get(letters)
        rest = _unlu_sayisi(unit) if unit is not None else _tr_kok_hecesi(letters)
        return None if number is None or rest is None else _unlu_sayisi(number) + rest
    if not kok.isalpha():
        return None
    n = _unlu_sayisi(kok)
    if n > 0:
        return n
    # A vowelless abbreviation is read letter by letter: all capitals at any length (TBMM),
    # other spellings at 2-4 letters (tv, Hz, Mszp). Longer vowelless strings are foreign
    # words (rhythm) and a single lower-case consonant may be a unit (m): both stay unread
    # (2026-11-26, Efe).
    return len(kok) if kok.isupper() or 1 < len(kok) <= 4 else None


def hece_say(word: str, lang: str = "tr") -> int | None:
    """Bir tokenin hece sayısı; hecelenemiyorsa ``None`` (2026-09-16, Efe).

    - TR — ünlü sayısı (``â î û`` dahil). Kesme işaretinden sonraki ek ayrıca
      sayılıp eklenir (``Ankara'da`` → 4, ``TBMM'de`` → 5).
      Çetinkaya-Uzun protokolüne göre okunuşla sayılanlar (``okunus`` modülü):
      sayılar (``1916`` → 7) ve listedeki kısaltmalar (``cm`` → 4, ``vb.`` → 4).
      Listede olmayan ünlüsüz token tamamı büyük harfse harf adları tek heceli
      olduğu için hece = harf sayısı (``TBMM`` → 4); değilse ``None``.
      Saat ve skor (``10:30`` → 3), sıra sayısı (``3.`` → üçüncü → 3) ve
      harfe bitişik sayı (``3kg`` → 4, ``100m`` → 3, ``3G`` → 2) okunuşuyla
      (2026-10-01, Efe). Tek başına ``3.`` sıra sayısı sayılır; cümle sonundaki
      sayıyı ayırmak bağlam ister (``units.words.kelime_birimleri``). Okunuşu çıkarılamayan
      biçimler (``4x4``, tek başına ``m``) ve noktalama → ``None``.
    - EN — harflerden oluşan tokenler ``textstat.syllable_count`` ile, 0 verirse
      1 (``shh``). Sayılar okunuşuyla (``1918`` → nineteen eighteen → 4;
      Kincaid ve ark. 1975, 2026-09-17, Efe).
    """
    _dil_denetle(lang)
    if lang == "en":
        _cmudict_denetle()           # textstat'ı verisiz çağırma: indirme tetikler
        sayi = sayi_oku_en(word)
        if sayi is not None:
            return sum(max(1, int(textstat.syllable_count(k))) for k in sayi.split())
        yalin = word.translate(_KESMELER)
        if not yalin or not yalin.isalpha():
            return None
        return max(1, int(textstat.syllable_count(yalin)))
    kok, _, ek = word.replace("’", "'").partition("'")
    ek = ek.replace("'", "")
    if ek and not ek.isalpha():
        return None
    kok_hece = _tr_kok_hecesi(kok) if kok else None
    return None if kok_hece is None else kok_hece + _unlu_sayisi(ek)


# Noktalı baş harfler: F.O.B, i.e, A.Ş — harf harf okunur.
_BAS_HARFLER = re.compile(r"(?:[^\W\d_]\.)+[^\W\d_]?")

# Turkish written forms the reading can still be taken from (2026-11-26, Efe):
# a quote between two letters stands for an apostrophe (siyaset"i = siyaset'i) ...
_ICTE_TIRNAK = re.compile(r'(?<=[^\W\d_])["“”«»](?=[^\W\d_])')
# Apostrophe look-alikes are one apostrophe: ‘ ´ ` ʼ ′ after a letter or digit, before a
# letter (Ankara´da, 70`ini) (2026-11-27, Efe).
_KESME_BENZERI = re.compile(r"(?<=[^\W_])[’‘´`ʼ′](?=[^\W\d_])")
# A word, an apostrophe and a number: a shortened year (Dersim'38 = dersim otuz sekiz).
_KESME_SAYI = re.compile(r"([^\W\d_]+)['’](\d+)")
# ... brackets inside a word are dropped (konul(a)mayan = konulamayan) ...
_ICTE_AYRAC = re.compile(r"[()\[\]]")
# ... and two words glued by punctuation are read as two words (mısınız?"diye).
_BITISTIREN = re.compile(r'[?!"“”«»;:,…—–_]+|-(?=["“”«»])|(?<=["“”«»])-')
# Letters and a number written together (F1, TR325, A2'den, meselâ12): letters as a word or
# letter names, the number as a number (2026-11-27, Efe).
_HARF_RAKAM = re.compile(r"([^\W\d_]+)(\d+(?:,\d+)?)((?:['’][^\W\d_]+)?)")
# Letters and numbers alternating in three or four parts (5N1K, M354J) are read part by part;
# five parts or more is a number-for-letter joke spelling (H4R1KUL4D3) and stays unread
# (2026-11-27, Efe).
_HARF_RAKAM_PARCA = re.compile(r"(?:\d+|[^\W\d_]+)")
_EN_COK_PARCA = 4
# An x or * between two numbers is read "çarpı" (4x4, 73x92, 4*5) (2026-11-27, Efe).
_CARPI = re.compile(r"(\d+)[xX*](\d+)")
# One elided letter before an apostrophe (n'olmuş, l'Amour): read with the word.
_TEK_HARF_KESME = re.compile(r"[^\W\d_]'[^\W\d_]+")
_KENAR_ISARET = ".,;:!?…\"'“”‘’«»()[]{}–—-/*_"
# Dotted initials before a word or suffix: each initial is one letter name, one syllable
# (G.Saray = ge + saray, T.C.'nin = te + ce + nin). The full name (Galatasaray) cannot be
# read from the text; the shortfall is accepted (2026-11-26, Efe).
# A slash between exactly two numbers is a fraction, read "bölü" (1/2 = bir bölü iki); with
# three numbers it is a date and is not read (12/05/2020), nor between words (ve/veya)
# (2026-11-26, Efe).
_KESIR = re.compile(r"(\d+)/(\d+)")
# A date with dots is read like one with slashes: the dots are not read and each part is a
# number (13.3.2008 = on üç üç iki bin sekiz). The middle part has at most two digits, so a
# thousands group (12.500.000) never matches (2026-11-27, Efe).
_NOKTALI_TARIH = re.compile(r"(\d{1,2})\.(\d{1,2})\.(\d{2}|\d{4})(['’][^\W\d_]+)?")
_BAS_HARF_VE_SOZCUK = re.compile(r"((?:[A-ZÇĞİÖŞÜ]\.)+)(['’]?[^\W\d_].*)")
# E-mail and web addresses have no reading to count (2026-11-26, Efe).
_ADRES = re.compile(r"@|https?:|www\.")


def _tr_yazim_hecesi(birim: str) -> int | None:
    """Syllables of a Turkish unit after the written-form rules above; ``None`` if none apply.

    Order: apostrophe look-alikes and quotes as apostrophes, brackets dropped, one elided
    letter (``n'olmuş``), ``x``/``*`` between numbers (``4x4``), letters + number (``F1``),
    dotted initials before a word, a date with dots (``13.3.2008``), a fraction of two numbers
    (``1/2`` = bir bölü iki), split at gluing punctuation, dashes and ``_``, then split at
    ``/`` (not read: ``ve/veya`` = ve + veya) and at listed symbols (read: ``4+4+4`` = dört artı
    dört artı dört). Every part must be readable, otherwise the unit stays unread.
    """
    if _ADRES.search(birim):
        return None
    duz = _ICTE_AYRAC.sub("", _ICTE_TIRNAK.sub("'", _KESME_BENZERI.sub("'", birim)))
    if duz != birim:
        return birim_hecesi(duz, "tr") if duz else None
    if _TEK_HARF_KESME.fullmatch(birim):
        return _unlu_sayisi(birim)
    kesme_sayi = _KESME_SAYI.fullmatch(birim)
    if kesme_sayi is not None:
        h_sozcuk, h_yil = (birim_hecesi(x, "tr") for x in kesme_sayi.groups())
        return None if h_sozcuk is None or h_yil is None else h_sozcuk + h_yil
    carpi = _CARPI.fullmatch(birim)
    if carpi is not None:
        sol, sag = (birim_hecesi(x, "tr") for x in carpi.groups())
        return None if sol is None or sag is None else sol + _unlu_sayisi("çarpı") + sag
    harf_rakam = _HARF_RAKAM.fullmatch(birim)
    if harf_rakam is not None:
        harf, sayi, ek = harf_rakam.groups()
        h_harf, h_sayi = birim_hecesi(harf, "tr"), birim_hecesi(sayi, "tr")
        if h_harf is None or h_sayi is None:
            return None
        return h_harf + h_sayi + _unlu_sayisi(ek)
    govde, _, ek = birim.replace("’", "'").partition("'")
    if govde.isalnum() and (not ek or ek.isalpha()):
        parcalar = _HARF_RAKAM_PARCA.findall(govde)
        if 3 <= len(parcalar) <= _EN_COK_PARCA:
            heceler = [birim_hecesi(x, "tr") for x in parcalar]
            if None in heceler:
                return None
            return sum(h for h in heceler if h is not None) + _unlu_sayisi(ek)
    bas_harf = _BAS_HARF_VE_SOZCUK.fullmatch(birim)
    if bas_harf is not None:
        harfler, kalan = bas_harf.groups()
        kalan_hece = (_unlu_sayisi(kalan) if kalan[0] in "'’" else birim_hecesi(kalan, "tr"))
        return None if kalan_hece is None else harfler.count(".") + kalan_hece
    tarih = _NOKTALI_TARIH.fullmatch(birim)
    if tarih is not None:
        gun, ay, yil, ek = tarih.groups()
        heceler = [birim_hecesi(x, "tr") for x in (gun, ay, yil)]
        if None in heceler:
            return None
        return sum(h for h in heceler if h is not None) + (_unlu_sayisi(ek) if ek else 0)
    kesir = _KESIR.fullmatch(birim)
    if kesir is not None:
        pay, payda = (birim_hecesi(x, "tr") for x in kesir.groups())
        return None if pay is None or payda is None else pay + _unlu_sayisi("bölü") + payda
    for ayirici in (_BITISTIREN, re.compile(r"/")):
        parcalar = [q for q in (p.strip(_KENAR_ISARET) for p in ayirici.split(birim)) if q]
        if len(parcalar) > 1:
            heceler = [birim_hecesi(p, "tr") for p in parcalar]
            return None if None in heceler else sum(h for h in heceler if h is not None)
    semboller = SEMBOLLER["tr"]
    if any(c in semboller for c in birim):
        parcalar = re.split("(" + "|".join(re.escape(c) for c in semboller) + ")", birim)
        toplam = 0
        for p in (p for p in parcalar if p):
            h = _okunus_hecesi(semboller[p], "tr") if p in semboller else birim_hecesi(p, "tr")
            if h is None:
                return None
            toplam += h
        return toplam
    return None


def _okunus_hecesi(okunus_: str, lang: str) -> int:
    return sum(hece_say(k, lang) or 0 for k in okunus_.split())


def birim_hecesi(birim: str, lang: str) -> int | None:
    """Kelime biriminin (``units.words.kelime_birimleri``) hecesi; hecelenemiyorsa ``None``.

    Sırayla: ``hece_say`` (kelime, sayı, listedeki kısaltma) → kenardaki
    listedeki semboller okunur (``%50`` → yüzde elli) → tireli kelime
    parçaların toplamı → noktalı baş harfler harf harf (İngilizcede W üç hece).
    """
    h = hece_say(birim, lang)
    if h is not None:
        return h
    semboller = SEMBOLLER[lang]
    bas, son = 0, len(birim)
    while bas < son and birim[bas] in semboller:
        bas += 1
    while son > bas and birim[son - 1] in semboller:
        son -= 1
    if bas or son < len(birim):
        ek = sum(_okunus_hecesi(semboller[c], lang) for c in birim[:bas] + birim[son:])
        if bas == son:
            return ek
        govde = birim_hecesi(birim[bas:son], lang)
        return None if govde is None else ek + govde
    if "-" in birim:
        parcalar = [p.strip(_KENAR_ISARET) for p in birim.split("-")]
        heceler = [birim_hecesi(p, lang) for p in parcalar if p]
        if len(heceler) == len(parcalar) and all(x is not None for x in heceler):
            return sum(x for x in heceler if x is not None)
        return None
    if _BAS_HARFLER.fullmatch(birim):
        harfler = [c for c in birim if c.isalpha()]
        return sum(3 if lang == "en" and c.lower() == "w" else 1 for c in harfler)
    return _tr_yazim_hecesi(birim) if lang == "tr" else None


def birim_heceleri(birimler: list[str], lang: str) -> list[int]:
    """Hecelenebilen kelime birimlerinin hece sayıları (hecelenemeyen atlanır)."""
    return [h for h in (birim_hecesi(b, lang) for b in birimler) if h is not None]


def _ortalama(degerler: list[int]) -> float:
    """Ortalama; boşsa NaN (K4). CV'ler 2026-10-07'de kaldırıldı (Efe)."""
    if not degerler:
        return math.nan
    return round(float(np.mean(degerler)), 4)


def syllable_count_stats(birimler: list[str], lang: str = "tr") -> dict[str, float]:
    """Kelime başına ortalama hece.

    Kelime = varsayılan kelime birimi (``units.words.kelime_birimleri``, 2026-10-06, Efe);
    yalnız hecelenebilen birimler sayılır (``birim_hecesi``).
    """
    return {"syllable_mean": _ortalama(birim_heceleri(birimler, lang))}


def syllable_count(birimler: list[str], lang: str = "tr") -> dict[str, float]:
    """Metnin hece sayısı: hecelenebilen kelime birimlerinin hecelerinin toplamı.

    Kelime yoksa 0; boş metni NaN'a çeviren ``extractor`` (K4, ``word_count`` gibi;
    2026-10-08, Efe).
    """
    return {"syllable_count": float(sum(birim_heceleri(birimler, lang)))}


_HECE_KOVALARI = ("syllable_1_ratio", "syllable_2_ratio", "syllable_3_ratio",
                  "syllable_4_ratio", "syllable_5_ratio", "syllable_6plus_ratio")


def syllable_length_distribution(birimler: list[str], lang: str = "tr") -> dict[str, float]:
    """Kelimelerin hece sayısına göre dağılımı: 1, 2, 3, 4, 5, 6+ (toplam 1).

    Kovalar Bezirci & Yılmaz (2010, Tablo 1-c) ile aynı; üst kova sabit 6+.
    Kelime = varsayılan kelime birimi. Hecelenebilen birim yoksa altısı da NaN.
    """
    sayilar = birim_heceleri(birimler, lang)
    if not sayilar:
        return dict.fromkeys(_HECE_KOVALARI, math.nan)
    kova = Counter(min(h, 6) for h in sayilar)
    n = len(sayilar)
    return {ad: round(kova.get(i, 0) / n, 6) for i, ad in enumerate(_HECE_KOVALARI, start=1)}


def sentence_syllable_stats(cumleler: list[list[str]], lang: str = "tr") -> dict[str, float]:
    """Cümle başına ortalama hece.

    ``cumleler`` cümle başına kelime birimleridir (``units.words.cumle_birimleri``).
    Cümlenin hecesi, hecelenebilen birimlerinin toplamıdır. Hiç hecelenebilen
    birimi olmayan cümle ölçülemez, hesaba girmez. Cümle yoksa NaN.
    """
    heceler = []
    for cumle in cumleler:
        sayilar = birim_heceleri(cumle, lang)
        if sayilar:
            heceler.append(sum(sayilar))
    return {"sent_syllable_mean": _ortalama(heceler)}
