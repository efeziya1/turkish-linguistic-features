"""Ses ve yazı örüntüleri: ünlü oranları ile büyük ve küçük ünlü uyumu.

Bu modül ``phonetic`` grubunun 15 anahtarını üretir:

- T09 (5): ``vowel_ratio`` · ``front_vowel_ratio`` · ``back_vowel_ratio`` ·
  ``harmony_fronting_ratio`` · ``harmony_rounding_ratio``
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
import re
from collections import Counter

import numpy as np
import textstat

from ..alfabe import _ALFABE, _kucuk_harf
from ..exceptions import ModelNotFoundError
from .okunus import SEMBOLLER, UNITS_AFTER_NUMBER, okunus, sayi_oku, sayi_oku_en

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


def _dil_denetle(lang: str) -> None:
    if lang not in _ALFABE:
        raise ValueError(f"Unsupported language: {lang!r}. Expected one of: {sorted(_ALFABE)}")


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
    return len(kok) if kok.isupper() else None


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
      sayıyı ayırmak bağlam ister (``toplam_hece``). Okunuşu çıkarılamayan
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


_ORDINAL_TOKEN = re.compile(r"\d+\.")


def _in_context(tokens: list[str], lang: str) -> list[str]:
    """Turkish "3." is an ordinal only if a word or a comma follows it;
    otherwise the dot ends the sentence and the number is a cardinal."""
    if lang != "tr":
        return tokens
    out = []
    for i, tok in enumerate(tokens):
        if _ORDINAL_TOKEN.fullmatch(tok):
            nxt = tokens[i + 1] if i + 1 < len(tokens) else ""
            if not (nxt == "," or any(c.isalnum() for c in nxt)):
                tok = tok[:-1]
        out.append(tok)
    return out


def toplam_hece(tokens: list[str], lang: str = "tr") -> int:
    """Hecelenebilen tokenlerin toplam hece sayısı. T13 bunu kullanır."""
    return sum(_hece_sayilari(tokens, lang))


def _symbol_targets(tokens: list[str], lang: str) -> dict[int, list[str]]:
    """Number index → readings of the listed symbols that belong to it.

    spaCy splits "%50" into "%" + "50". The symbol is not a word, but it is
    read aloud with the number, so its reading joins that number: first the
    number after it ("%50", "$5"), else the one before it ("25°"). Each symbol
    joins one number only, so "5 + 3" reads "artı" once (2026-10-01, Efe).
    """
    semboller = SEMBOLLER[lang]

    def is_number(i: int) -> bool:
        return 0 <= i < len(tokens) and any(c.isdigit() for c in tokens[i])

    targets: dict[int, list[str]] = {}
    for i, tok in enumerate(tokens):
        if tok not in semboller:
            continue
        hedef = i + 1 if is_number(i + 1) else i - 1 if is_number(i - 1) else None
        if hedef is not None:
            targets.setdefault(hedef, []).append(semboller[tok])
    return targets


def _hece_sayilari(tokens: list[str], lang: str) -> list[int]:
    tokens = _in_context(tokens, lang)
    targets = _symbol_targets(tokens, lang)
    sayilar = []
    for i, tok in enumerate(tokens):
        h = hece_say(tok, lang)
        if h is None:
            continue
        for okunus_ in targets.get(i, []):
            h += sum(hece_say(k, lang) or 0 for k in okunus_.split())
        sayilar.append(h)
    return sayilar


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
