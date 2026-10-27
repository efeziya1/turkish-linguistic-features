"""Kalyoncu (2025) okunabilirlik formülleri K1–K4 ve bileşenleri (yalnız Türkçe).

Kaynak: Kalyoncu, M. R. (2025), *Türkçe için yeni bir okunabilirlik formülü*, yüksek lisans
tezi, Ondokuz Mayıs Üniversitesi. Değişkenler s.71–74, formüller s.96–99 (Tablo 31–34),
sınıf düzeyi tabloları s.101–105. Kararlar 2026-10-27 (Efe, S1–S10):

- **Sözcük:** varsayılan sözcük; rakam içeren sözcük okunuşuyla açılır ve okunuşunun sözcük
  sayısınca sayılır (``1968`` → "bin dokuz yüz altmış sekiz" = 5; Kalyoncu s.xiii). Kısaltma
  açılmaz. Yalnız bu modülde; ``sent_len_mean`` ve öteki öznitelikler değişmez.
- **Tümce:** aracın varsayılan tümcesi; harf içermeyen tümce sayılmaz, sözcükleri sayılır.
  Kalyoncu'nun anlama dayalı tümce tanımı (s.xii) uygulanmaz.
- **Gövde:** Zeyrek sözlükbirimi + yapım ekleri. Çekim ekleri, ettirgen/edilgen (7. kural),
  fiilimsi (4. kural), birleşik fiil ekleri ve ek eylem gövdeye girmez; ilk çekim ekinden sonra
  gelen hiçbir biçimbirim de girmez (``oradaki`` → ``ora``, Rel -ki). İlk atılan ekte durulur.
  Belirsizlikte Zeyrek'in ilk çözümlemesi. Çözümlenemeyen sözcükte gövde küçük harfli sözcük.
- **KL:** listede olmayan sözcük / sözcük × 100. Sözcük şu üç biçimden biri listedeyse liste
  içidir: küçük harfli kendisi, gövdesi, fiilse gövde + -mak/-mek (yumuşamış son ünsüz
  sertleştirilerek de denenir). Karşılaştırmada şapka iki tarafta da silinir (TOMA ile aynı,
  Kalyoncu vd. 2026 s.298). Özel ad (1. kural) ve sayı (9. kural) paydada kalır, paya girmez.
- **Özel ad (0.3.0 düzeltmesi, Efe):** spaCy ``PROPN`` ya da tümce başında olmayıp büyük harfle
  başlayan sözcük (``İstanbul'da``, ``Derya``; düz ve eğri kesme). Tümce başındaki ad yalnız
  ``PROPN`` ise özel addır. Gerekçe: spaCy Türkçe modeli ``Derya``, ``Almanya'da``, ``Hassan'ı``
  PROPN etiketlemiyor, Türkçe yazımda özel adlar büyük harfle yazılır.
- **Sayı (0.3.0 düzeltmesi, Efe):** 9. kural rakam/yazı ayırmaz; yazıyla yazılan sayı da liste
  içidir. Sayı = spaCy ``NUM``; seçilen Zeyrek çözümlemesinin kökü ``Num``; ya da spaCy'nin ad,
  sıfat, belirteç ya da ``X`` dediği sözcüğün çözümlemelerinden birinin kökü ``Num`` (``ikisi``,
  ``üçüncü``, ``beşer``; ``beşer`` spaCy'de ad çıkabiliyor). Zamir, eylem, özel ad etiketi
  bağlayıcıdır: ``onun``, ``ona`` sayı değildir.
- **Çözümleme seçimi (0.3.0 düzeltmesi, Efe):** Zeyrek'in çözümlemeleri arasından, genel türü
  spaCy'nin sözcük türüne uyan ilki alınır (PRON→Pron, NOUN/PROPN→Noun, VERB/AUX→Verb,
  ADJ→Adj, ADV→Adv, NUM→Num); uyan yoksa ilk çözümleme. Gövde, fiilimsi ve karmaşık tümce
  sayımı (TTR, KCO, YCO) bundan. Aracın geri kalanında "ilk çözümleme" kuralı değişmez.
- **TTR:** bir kez geçen gövde / sözcük × 100; ``kalyoncu_ttr_window``'dan (500) uzun metinde
  adımı 1 olan kayan pencerelerin ortalaması (MATTR; s.73). Şapka silinmez.
- **Fiilimsi:** aşağıdaki Zeyrek etiketlerinden birini taşıyan sözcük; ek eylemli ad
  (``öğrenciyken``) sayılmaz. Sözcük başına en çok bir.
- **KCO:** en az bir fiilimsi ya da en az iki fiil (Zeyrek'in son türü ``Verb``) içeren tümce /
  tümce × 100. Kalyoncu "yargı"yı CYargı'da fiil + fiilimsi olarak sayar (s.73).
- **YCO:** fiilimsi / tümce × 10. **OCU:** sözcük / tümce.

Uygulanmayan kurallar: yaygın yapım ekli türevler (3.), yansıma (5.), pekiştirme (6.), uzak
anlam (8.), anlama dayalı tümce sınırı. Zeyrek'in tanımadığı ekler (-alı, -ası, -casına,
-maksızın) ve ilk çözümlemedeki hatalar düzeltilmez.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from functools import lru_cache
from importlib.resources import files
from typing import Any

from ..alfabe import _kucuk_harf
from ..params import DEFAULT_PARAMS, FeatureParams
from .morphological import _ZEYREK_TURLER, _genel_tur
from .okunus import SEMBOLLER, UNITS_AFTER_NUMBER, read_ordinal, read_time, sayi_oku

__all__ = ["KALYONCU_KEYS", "kalyoncu_features", "kalyoncu_list"]

KALYONCU_KEYS = (
    "kalyoncu_kl", "kalyoncu_ttr", "kalyoncu_kco", "kalyoncu_yco", "kalyoncu_ocu",
    "kalyoncu_k1", "kalyoncu_k2", "kalyoncu_k3", "kalyoncu_k4",
)

# Fiilimsi (S5, 2026-10-27, Efe): adeylem, ortaç, ulaç.
_FIILIMSI = frozenset({
    "Inf1", "Inf2", "Inf3",
    "PresPart", "PastPart", "FutPart", "NarrPart", "AorPart",
    "AfterDoingSo", "ByDoingSo", "When", "While", "WithoutHavingDoneSo",
    "WithoutBeingAbleToHaveDoneSo", "AsLongAs", "SinceDoingSo", "AsIf", "Adamantly",
})
# Gövdeye girmeyen yapım etiketleri: çatı (7. kural), birleşik fiil ekleri (-ebil, -iver,
# -eyaz, -akal, -akoy, -adur, -egel) ve ek eylem (``Zero``: ``evdeydi``'nin gövdesi ``ev``).
_CATI = frozenset({"Caus", "Pass"})
_BIRLESIK_FIIL = frozenset({"Able", "Hastily", "Almost", "Stay", "Start", "Repeat", "EverSince"})
_GOVDE_DISI = _FIILIMSI | _CATI | _BIRLESIK_FIIL | {"Zero"}

_SERTLESME = {"ğ": "k", "b": "p", "c": "ç", "d": "t"}
_SAPKA = str.maketrans("âîû", "aiu")
_KALIN = frozenset("aıouâû")
_UNLU = frozenset("aeıioöuüâîû")
# spaCy türü → Zeyrek genel türü (çözümleme seçimi).
_ZEYREK_TUR = {"PRON": "Pron", "NOUN": "Noun", "PROPN": "Noun", "VERB": "Verb", "AUX": "Verb",
               "ADJ": "Adj", "ADV": "Adv", "NUM": "Num"}
_ACIK_SINIF = frozenset({"NOUN", "ADJ", "ADV", "X"})
_SAYI_HARF = re.compile(r"(\d+(?:,\d+)?)([^\W\d_]+)")


@lru_cache(maxsize=1)
def kalyoncu_list() -> tuple[str, ...]:
    """Kalyoncu (2025) Ek-1: 4600 sözcük, kaynaktaki yazımla (şapkalı, küçük harf)."""
    metin = files("turkish_linguistic_features.data").joinpath("kalyoncu_2025_ek1.txt")
    satirlar = metin.read_text(encoding="utf-8").splitlines()
    return tuple(s for s in satirlar if s and not s.startswith("#"))


@lru_cache(maxsize=1)
def _liste_sapkasiz() -> frozenset[str]:
    return frozenset(s.translate(_SAPKA) for s in kalyoncu_list())


# ── sayılar ───────────────────────────────────────────────────────────

def _sayi_sozcukleri(kok: str) -> list[str]:
    """Rakam içeren parçanın okunuşundaki sözcükler; okunamıyorsa parçanın kendisi."""
    for oku in (sayi_oku, read_time, read_ordinal):
        acilim = oku(kok)
        if acilim is not None:
            return acilim.split()
    yapisik = _SAYI_HARF.fullmatch(kok)
    if yapisik is not None:
        sayi = sayi_oku(yapisik.group(1))
        harfler = yapisik.group(2)
        if sayi is not None:
            birim = UNITS_AFTER_NUMBER.get(harfler)
            if birim is not None:
                return sayi.split() + [birim]
            # Küçük harfli ek (1990lar) okunuşa yapışır; büyük harf (3G) ayrı okunur.
            return sayi.split() + ([] if harfler.islower() else [harfler.lower()])
    if "-" in kok or "/" in kok:
        parcalar = [p for p in re.split(r"[-/]", kok) if p]
        if parcalar and len(parcalar) > 1:
            return [s for p in parcalar for s in
                    (_sayi_sozcukleri(p) if any(c.isdigit() for c in p) else [p.lower()])]
    return [_kucuk_harf(kok, "tr")]


def okunus_sozcukleri(birim: str) -> list[str]:
    """Rakam içeren sözcük biriminin okunuşu, sözcük sözcük (``%50'si`` → yüzde elli).

    Kesme işaretinden sonraki ek okunuşa yapışır, ayrı sözcük değildir. Kenardaki semboller
    okunuşlarıyla açılır; kısaltma açılmaz (S2.1, 2026-10-27, Efe).
    """
    kok = birim.replace("’", "'").split("'", 1)[0]
    semboller = SEMBOLLER["tr"]
    on: list[str] = []
    arka: list[str] = []
    while kok and kok[0] in semboller:
        on += semboller[kok[0]].split()
        kok = kok[1:]
    while kok and kok[-1] in semboller:
        arka = semboller[kok[-1]].split() + arka
        kok = kok[:-1]
    return on + (_sayi_sozcukleri(kok) if kok else []) + arka


# ── gövde ─────────────────────────────────────────────────────────────

def _mastar(govde: str) -> str:
    son = next((c for c in reversed(govde) if c in _UNLU), "e")
    return govde + ("mak" if son in _KALIN else "mek")


def govde(morfemler: Any, lemma: str, kelime: str) -> tuple[str, bool]:
    """Sözcüğün gövdesi ve gövdenin fiil olup olmadığı (S3, 2026-10-27, Efe).

    Gövde = Zeyrek sözlükbirimi + yapım ekleri; ilk çekim ekinde (yüzeyde görünen), çatı,
    birleşik fiil, ek eylem ve fiilimsi eklerinde durulur. Çözümlenemeyen sözcükte küçük harfli
    sözcük.
    """
    if not morfemler or morfemler[0][0] == "Unk":
        return _kucuk_harf(kelime, "tr"), False
    sonuc = _kucuk_harf(lemma, "tr")
    tur = morfemler[0][0]
    for etiket, yuzey, turetim in morfemler[1:]:
        if etiket in _ZEYREK_TURLER:
            tur = etiket
            continue
        if not turetim:
            if yuzey:
                break          # ilk çekim biçimbiriminden sonra gövdeye bir şey eklenmez
            continue
        if etiket in _GOVDE_DISI:
            break
        sonuc += _kucuk_harf(yuzey, "tr")
    return sonuc, tur == "Verb"


def _listede(kelime: str, gov: str, fiil: bool) -> bool:
    adaylar = {_kucuk_harf(kelime, "tr"), gov}
    if gov and gov[-1] in _SERTLESME:
        adaylar.add(gov[:-1] + _SERTLESME[gov[-1]])
    if fiil:
        adaylar |= {_mastar(a) for a in tuple(adaylar - {_kucuk_harf(kelime, "tr")})}
    liste = _liste_sapkasiz()
    return any(a.translate(_SAPKA) in liste for a in adaylar)


def cozumleme_sec(etiket: str, morfemler: Any, lemma: str,
                  alternatifler: Any) -> tuple[Any, str]:
    """Genel türü spaCy türüne uyan ilk Zeyrek çözümlemesi; uyan yoksa ilk çözümleme."""
    tur = _ZEYREK_TUR.get(etiket)
    if tur is not None:
        for m, lem in alternatifler or ():
            if _genel_tur(list(m)) == tur:
                return m, lem
    return morfemler, lemma


def sayi_mi(etiket: str, morfemler: Any, alternatifler: Any) -> bool:
    """Yazıyla yazılan sayı: spaCy ``NUM``, seçilen çözümlemenin kökü ``Num``, ya da spaCy'nin
    açık sınıf (ad, sıfat, belirteç, ``X``) dediği sözcüğün çözümlemelerinden birinin kökü ``Num``.

    Kök ``Num`` olunca çekimli (``ikisi``), sıra (``üçüncü``) ve üleştirme (``beşer``) biçimi de
    sayıdır; ``beşer`` spaCy'de ad çıksa da Zeyrek'in sayı çözümlemesi vardır. Zamir, eylem ya da
    özel ad etiketi bağlayıcıdır (``onun``, ``ona`` "on" sayılmaz).
    """
    if etiket == "NUM" or (morfemler and morfemler[0][0] == "Num"):
        return True
    return etiket in _ACIK_SINIF and any(a[0][0][0] == "Num" for a in alternatifler)


def ozel_ad_mi(sozcuk: str, etiket: str, tumce_basi: bool) -> bool:
    """``PROPN`` ya da tümce başında olmayıp büyük harfle başlayan sözcük."""
    return etiket == "PROPN" or (not tumce_basi and sozcuk[:1].isupper())


def fiilimsi_mi(morfemler: Any) -> bool:
    """Zeyrek çözümlemesinde fiilimsi eki var mı; ek eylemli adın ``-ken``'i sayılmaz (S5)."""
    if not morfemler or morfemler[0][0] == "Unk":
        return False
    onceki = morfemler[0][0]
    for etiket, _, _ in morfemler[1:]:
        if etiket in _ZEYREK_TURLER:
            continue
        if etiket in _FIILIMSI and onceki != "Zero":
            return True
        onceki = etiket
    return False


# ── ölçüler ───────────────────────────────────────────────────────────

def _bir_kez_oran(govdeler: list[str], pencere: int) -> float:
    """Bir kez geçen gövde / sözcük × 100; uzun metinde kayan pencerelerin ortalaması."""
    n = len(govdeler)
    if n <= pencere:
        return 100 * sum(1 for s in Counter(govdeler).values() if s == 1) / n
    sayim = Counter(govdeler[:pencere])
    tekil = sum(1 for s in sayim.values() if s == 1)
    toplam = tekil
    for i in range(pencere, n):
        for g, fark in ((govdeler[i - pencere], -1), (govdeler[i], 1)):
            once = sayim[g]
            sayim[g] = once + fark
            tekil += (sayim[g] == 1) - (once == 1)
        toplam += tekil
    return 100 * toplam / ((n - pencere + 1) * pencere)


def kalyoncu_features(words: list[str], pos: list[tuple[str, str]], lemmas: list[str],
                      morphemes: list[Any], sentences: list[list[str]],
                      params: FeatureParams | None = None,
                      alternatives: list[Any] | None = None) -> dict[str, float]:
    """KL, TTR, KCO, YCO, OCU ve K1–K4 (Kalyoncu 2025).

    Girdiler ``word_view``'un sözcük başına listeleri; ``sentences`` sözcükleri tümce tümce
    verir ve sırayla ``words``'ü oluşturur. ``alternatives`` sözcük başına Zeyrek'in tüm
    çözümlemeleridir (``(morfemler, sözlükbirim)``); verilmezse ``morphemes`` ve ``lemmas``
    (ilk çözümleme) kullanılır.
    """
    if params is None:
        params = DEFAULT_PARAMS
    if params.kalyoncu_ttr_window <= 0:
        raise ValueError(f"kalyoncu_ttr_window must be positive: {params.kalyoncu_ttr_window}")

    sozcuk = 0
    liste_disi = 0
    govdeler: list[str] = []
    tumce = karmasik = fiilimsi = 0
    i = 0
    for cumle in sentences:
        c_fiil = c_fiilimsi = 0
        for j, _ in enumerate(cumle):
            w, (_, etiket), lem, m = words[i], pos[i], lemmas[i], morphemes[i]
            if alternatives:
                m, lem = cozumleme_sec(etiket, m, lem, alternatives[i])
            i += 1
            if any(c.isdigit() for c in w):
                okunus = okunus_sozcukleri(w)
                sozcuk += len(okunus)
                govdeler += okunus
                continue
            sozcuk += 1
            gov, fiil = govde(m, lem, w)
            govdeler.append(gov)
            sayi = sayi_mi(etiket, m, alternatives[i - 1] if alternatives else ())
            if not (sayi or ozel_ad_mi(w, etiket, j == 0)) and not _listede(w, gov, fiil):
                liste_disi += 1
            if fiilimsi_mi(m):
                c_fiilimsi += 1
            elif m and m[0][0] != "Unk" and _genel_tur(list(m)) == "Verb":
                c_fiil += 1
        if any(c.isalpha() for w in cumle for c in w):
            tumce += 1
            fiilimsi += c_fiilimsi
            karmasik += c_fiilimsi >= 1 or c_fiil >= 2
    if i != len(words):
        raise ValueError(f"sentences cover {i} words, expected {len(words)}")

    kl = round(100 * liste_disi / sozcuk, 4) if sozcuk else math.nan
    ttr = round(_bir_kez_oran(govdeler, params.kalyoncu_ttr_window), 4) if sozcuk else math.nan
    if tumce:
        kco = round(100 * karmasik / tumce, 4)
        yco = round(10 * fiilimsi / tumce, 4)
        ocu = round(sozcuk / tumce, 4)
    else:
        kco = yco = ocu = math.nan
    # Katsayılar Tablo 31–34 (s.96–99); bileşen NaN ise formül de NaN.
    return {
        "kalyoncu_kl": kl, "kalyoncu_ttr": ttr, "kalyoncu_kco": kco,
        "kalyoncu_yco": yco, "kalyoncu_ocu": ocu,
        "kalyoncu_k1": round(-29.829 + 0.508 * kl + 1.191 * ttr + 0.733 * kco - 0.66 * ocu, 4),
        "kalyoncu_k2": round(25.457 + 0.877 * kl + 0.668 * ttr + 0.333 * ocu, 4),
        "kalyoncu_k3": round(25.153 + 0.834 * kl + 0.686 * ttr + 0.226 * yco, 4),
        "kalyoncu_k4": round(43.368 + 1.008 * kl + 0.624 * ocu, 4),
    }
