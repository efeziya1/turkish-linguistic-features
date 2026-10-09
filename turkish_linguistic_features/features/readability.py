"""Okunabilirlik formülleri — ``readability`` grubu (TR 7 · EN 8).

- Türkçe: ``atesman`` · ``cetinkaya_uzun`` · ``bezirci_yilmaz``
- İngilizce: ``flesch_reading_ease`` · ``flesch_kincaid_grade`` · ``smog`` ·
  ``polysyllabic_word_ratio`` (Türkçe eşiği belirlenene kadar yalnız EN)
- İki dilde: ``ari`` · ``coleman_liau`` · ``lix`` · ``long_word_ratio``

Dil ayrımı T20'nin birleştiricisinde yapılır (2026-09-15, Efe).

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
import re

from .okunus import SEMBOLLER, kisaltma_oku
from .phonetic import _dil_denetle, birim_hecesi

# Kelime biriminin kenarından atılan noktalama.
_KENAR = ".,;:!?…\"'“”‘’«»()[]{}–—-/*"

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


# Björnsson: "6 harften uzun" kelime (Anderson 1983 s.491: seven or more letters).
_UZUN_KELIME_HARF = 7

# McLaughlin (1969): formül 30 cümlelik örnek üzerine kurulu.
_SMOG_MIN_CUMLE = 30

# Bezirci & Yılmaz (2010) s.370: EKOK 21000 / (Tablo 1-c oranı × 1000) / 100.
_BEZIRCI_KATSAYI = {3: 0.84, 4: 1.5, 5: 3.5, 6: 26.25}


# ── sayım ─────────────────────────────────────────────────────────────


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
    parcalar = [(m.group(), m.start(), m.end()) for m in re.finditer(r"\S+", raw_text)]
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


def _isaret_mi(token: str) -> bool:
    return bool(token) and not any(c.isalnum() for c in token)


def _baslik_harfli(token: str) -> bool:
    return token[:1].isupper()


def _yeni_cumle_basliyor(sonraki: list[str]) -> bool:
    """İşaretten sonra gelen tokenlar yeni bir cümle gibi mi başlıyor?

    İlk token büyük harfle başlıyorsa ya da bir tırnak, tire, açılış parantezi ise evet; küçük harf
    ya da rakamla başlıyorsa hayır; metin bitiyorsa evet (son cümle zaten ayrı sayılır).
    """
    if not sonraki:
        return True
    ilk = sonraki[0]
    if _isaret_mi(ilk):
        return ilk[0] in _YENI_CUMLE_ACILIS
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
            continue
        if not acik:
            continue
        if any(c in isaretler for c in token):
            if lang == "tr" and token == "." and kisaltma_oku(onceki) is not None:
                sonraki = next((t for t in surface_tokens[i + 1:] if not _isaret_mi(t)), None)
                if sonraki is not None and not _baslik_harfli(sonraki):
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
    böldüğü listedeki kısaltmadan (``bkz`` + ``.``) sonraki nokta, ardından
    büyük harfle başlayan bir kelime gelmiyorsa sınır sayılmaz.

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
    """ARI (Smith & Senter 1967), Coleman-Liau (1975), LIX (Björnsson 1968).

    - ari = 4.71·(vuruş/kelime) + 0.5·(kelime/cümle) − 21.43 — vuruş = boşluk
      dışı her karakter, sembol kelime sayılır (Kincaid ve ark. 1975 s.14, s.33)
    - coleman_liau = 0.0588·L − 0.296·S − 15.8; L = 100 kelimedeki harf,
      S = 100 kelimedeki cümle (Coleman & Liau 1975 s.284)
    - lix = kelime/cümle + 100·uzun kelime/kelime; uzun = 7 veya daha fazla harf
    - long_word_ratio = uzun kelime / kelime (LIX'in tanımı)

    Cümle sayan üçünde (ARI, Coleman-Liau, LIX) cümle varsayılan kuraldan: ``. ? ! …``
    her zaman, ``:`` yalnız ardından yeni cümle başlıyorsa.
    """
    kelimeler, semboller = kelime_birimleri(raw_text, lang)
    cumle = _sayim(surface_tokens, "varsayilan", lang)
    sonuc = {"ari": math.nan, "coleman_liau": math.nan, "lix": math.nan,
             "long_word_ratio": math.nan}
    if not kelimeler:
        return sonuc

    uzun = sum(1 for k in kelimeler if _harf_sayisi(k) >= _UZUN_KELIME_HARF)
    sonuc["long_word_ratio"] = round(uzun / len(kelimeler), 5)
    harf = sum(_harf_sayisi(k) for k in kelimeler)
    sonuc["coleman_liau"] = round(
        0.0588 * 100 * harf / len(kelimeler) - 0.296 * 100 * cumle / len(kelimeler) - 15.8, 4)
    if cumle:
        sonuc["lix"] = round(len(kelimeler) / cumle + 100 * uzun / len(kelimeler), 4)
        a_kelime = len(kelimeler) + len(semboller)
        vurus = sum(len(parca) for parca in raw_text.split())
        sonuc["ari"] = round(4.71 * vurus / a_kelime + 0.5 * a_kelime / cumle - 21.43, 4)
    return sonuc
