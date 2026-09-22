"""docs/dogrulama-raporu.md dosyasını üretir (T31).

Her öznitelik için, dayandığı kaynağın yayımladığı sayıyla karşılaştırmasını
tablolar. Kapsam listesi registry'den üretilir — elle tutulmaz, yani hiçbir
öznitelik rapordan kaçamaz.

Kullanım::

    python scripts/dogrulama_raporu.py

Bu dosya elle DÜZENLENMEZ. Karşılaştırma eklemek için aşağıdaki
``KARSILASTIRMALAR`` tablosuna satır yazın; testler
(``tests/test_kaynak_esligi.py``) aynı tabloyu okuyor, yani rapor ile
testler ayrışamaz.
"""

from __future__ import annotations

import math
from pathlib import Path

import turkish_linguistic_features as tlf

# Kapsam ölçülürken kullanılan örnek metinler. İçerikleri önemsiz —
# yalnız taban şemanın bütün anahtarlarını üretmeye yarıyorlar.
ORNEK_METIN = {
    "tr": "Bu bir deneme metnidir. İkinci cümle burada duruyor, üçüncüsü de geldi.",
    "en": "This is a test sentence. A second one is here, and a third follows.",
}

# ── Kalyoncu & Memiş (2024) Ek-1'deki üç okunabilirlik örneği ─────────
#
# Telif: bunlar makalede yayımlanmış 100 kelimelik örneklerdir ve doğrulama
# amacıyla, hem makale hem özgün ders kitabı gösterilerek alıntılanmıştır.
# Kaynak metinlerin tamamı depoya girmez.

# Metin 1 — Başkaya (2019) s.26, aktaran Kalyoncu & Memiş (2024) Ek-1
METIN_1 = (
    'Yakın zamana kadar köylerde yaşamış veya hâlen yaşamakta olan kişilerin '
    'anılarında dün gibi yaşayan köy odaları geleneği, Türk konukseverliğinin '
    'en iyi örnekleri arasındadır. Köylerdeki köy odalarının konukları, bir '
    'yerden bir yere gitmekte olan yolcular olduğu kadar, köye ticaret amacı '
    'ile gelen veya zanaat sahibi insanlar da olabilmekteydi. Çerçiler, testi '
    'bardak satanlar, ürettiği malı değiş yoluyla veya para ile ticaret '
    'yapanlar, halatçılar, gezici kalaycılar, orakçılar vb. olmak üzere köye '
    'bir nedenle gelenler istediği kadar bu köy odalarında konuk olarak '
    "kalabiliyorlardı. Anadolu'nun birçok köyünde neredeyse her sülalenin köy "
    'odası vardı. Bu köy odaları ya o sülalelerin ya da önde gelen büyüğünün '
    'adıyla anılıyordu.'
)

# Metin 2 — İnan (2023) s.143, aktaran Kalyoncu & Memiş (2024) Ek-1
METIN_2 = (
    'Atatürk, okul programlarıyla bizzat meşgul olur, okutulan kitapları '
    'gözden geçirir ve özellikle tarih derslerinin, ulusun bilincini '
    'yükselteceğine inanır ve Türklük dünyasının tarihini bir bütün olarak, '
    'uygarlık unsurlarına daha çok önem verilerek incelenmesini ve '
    'okutulmasını isterdi. O, Türk büyüklerinden Alparslanlar, Fatihler, '
    'Yavuz ve Kanunilerin hayranı olmakla beraber, bizzat uygarlık eserleri '
    'vücuda getirmiş olan Mimar Sinanlar ve Piri Reislere de ayrı bir değer '
    'verirdi. Çünkü devlet başında ordular yönetmiş kişiler, tarihte Türk '
    'şanını ne kadar yükseltmişlerse diğerleri de Türk dünyasına ölmez '
    'eserler vermişlerdir. Atatürk, her devirde Türk’ün uygarlık yapısına '
    'hizmet eden her bireyin değerini takdir etmenin zorunlu olduğunu prensip '
    'olarak kabul etmişti.'
)

# Metin 3 — Baykent (2017) s.506-507, aktaran Kalyoncu & Memiş (2024) Ek-1
METIN_3 = (
    'Anlam, türetilmiş niyetliliğin bir biçimidir. Konuşan kişinin asli ya da '
    'içsel niyetliliği sözcüklere, cümlelere, işaretlere, sembollere vs. '
    'aktarılmıştır. Anlamlı bir biçimde dile getirilirlerse, bu sözcükler, '
    'cümleler, işaretler ve semboller artık konuşan kişinin düşüncelerinden '
    'türetilmiş niyetliliğe sahiptirler. Sadece uzlaşıma dayalı dilbilimsel '
    'anlam taşımakla kalmazlar, konuşanın kastettiği anlamı da taşırlar. Bir '
    'dilin sözcüklerinin ve cümlelerinin uzlaşımsal niyetliliği, konuşan kişi '
    'tarafından bir söz edimi icra etmek için kullanılabilir. Konuşan kişi '
    'bir söz edimi yerine getirirse, bu semboller üzerine kendi niyetliliğini '
    'yükler. Fakat konuşan kişi bunu tam olarak nasıl yapmaktadır? Daha önce '
    'niyetliliği ele alıp tartışırken yerine getirilme şartlarının açıklamaya '
    'çalıştığım anlamda, niyetliliği anlamak için anahtar mahiyetinde '
    'olduğunu görmüştük.'
)

# ── durum sözlüğü ─────────────────────────────────────────────────────
BIREBIR = "birebir"
SAPMA = "belgelenmis_sapma"
ORNEK_YOK = "kaynakta_sayisal_ornek_yok"
KAYNAK_YOK = "kaynak_yok"
UYUSMAZLIK = "uyusmazlik"

_SIMGE = {BIREBIR: "✅", SAPMA: "🟡", ORNEK_YOK: "⚪", KAYNAK_YOK: "⚪",
          UYUSMAZLIK: "❌"}

# Birebir sayılmak için gereken yakınlık. Kaynaklar ara değerleri yuvarlayarak
# bastığı için mutlak eşitlik beklenmiyor (bkz. plan/kaynak-arastirmasi.md).
TOLERANS = 0.05


# Kanıtın türü. Aradaki fark önemli: uçtan uca karşılaştırma kaynağın
# **metnini** boru hattından geçirir, yani tokenizasyonu, hecelemeyi ve cümle
# bölmeyi de sınar. Formül karşılaştırması fonksiyona girdileri doğrudan
# verir — formülü doğrular, boru hattını değil.
UCTAN_UCA = "uçtan uca"
FORMUL = "formül"


class Karsilastirma:
    """Bir anahtarın kaynaktaki yayımlanmış değeriyle karşılaştırması."""

    def __init__(self, kaynak: str, ornek: str, beklenen: float,
                 hesapla, gerekce: str = "", tur: str = UCTAN_UCA) -> None:
        self.kaynak = kaynak
        self.ornek = ornek
        self.beklenen = beklenen
        self.hesapla = hesapla          # () -> float
        self.gerekce = gerekce          # sapma varsa NEDEN
        self.tur = tur                  # UCTAN_UCA | FORMUL


def _kalyoncu_metin(no: int) -> dict[str, float]:
    """Ek-1'deki metinlerden birinin özniteliklerini verir."""
    return tlf.analyze((METIN_1, METIN_2, METIN_3)[no - 1], lang="tr")


_KM_ONBELLEK: dict[int, dict[str, float]] = {}


def _km(no: int, anahtar: str) -> float:
    if no not in _KM_ONBELLEK:
        _KM_ONBELLEK[no] = _kalyoncu_metin(no)
    return _KM_ONBELLEK[no][anahtar]


_KM = "Kalyoncu & Memiş (2024) Tablo 9"


def _bezirci_e7(h3: float, h4: float, h5: float, h6: float) -> float:
    """Bezirci & Yılmaz denk. (7): hece sayımlarından ara değer."""
    return h3 * 0.84 + h4 * 1.5 + h5 * 3.5 + h6 * 26.25


def _bezirci_e9(oks: float, e7: float) -> float:
    """Bezirci & Yılmaz denk. (9): karekök adımı.

    Tablo 5 tam olarak bunu tablolıyor — ``E7`` makalenin bastığı ara değer,
    yeniden hesaplanmıyor. Katsayı adımını Tablo 3 satırları sınıyor.
    """
    return math.sqrt(oks * e7)


def _atesman(hece_basina: float, sozcuk_basina: float) -> float:
    """Ateşman denk. (2), doğrudan."""
    return 198.825 - 40.175 * hece_basina - 2.610 * sozcuk_basina


def _jing_liu(alan: str) -> float:
    """Jing & Liu (2015) s.164 Figure 3: 'Mr. Nixon was to leave China today'."""
    from turkish_linguistic_features.features.dependency import dependency_features
    cumle = [(0, "PROPN", "flat", 1), (1, "PROPN", "nsubj", 2),
             (2, "VERB", "root", 2), (3, "PART", "mark", 2),
             (4, "VERB", "xcomp", 3), (5, "PROPN", "obj", 4),
             (6, "NOUN", "obl", 4)]
    return dependency_features([cumle])[alan]


# QUITA §6.1.2 Tablo 6.1/6.2 — iki örnek metnin ilk 10 rankı.
_T1 = [16, 7, 7, 7, 5, 5, 3, 3, 3, 3]
_T2 = [20, 9, 8, 7, 4, 4, 4, 4, 4, 3]


def _quita_spektrum(bas: list[int], n: int):
    """QUITA örnek metninin sıklık dizisi.

    Kılavuz yalnız ilk 10 rankı ve ``N``i yayımlıyor. Kuyruk tek-frekanslı
    doldurularak ``N`` tutturuluyor; ``h_point`` ve ``R1`` yalnız baştaki
    ranklara ve ``N``e baktığı için kuyruğun biçimi sonucu etkilemiyor.
    """
    import numpy as np
    return np.array(bas + [1] * (n - sum(bas)), dtype=float)


def _h_point(bas: list[int], n: int) -> float:
    from turkish_linguistic_features.features.frequency_structure import h_point
    return h_point(_quita_spektrum(bas, n))


def _r1(bas: list[int], n: int) -> float:
    from turkish_linguistic_features.features.frequency_structure import (
        h_point,
        vocab_richness_r1,
    )
    f = _quita_spektrum(bas, n)
    return vocab_richness_r1(f, n, h_point(f))["vocab_richness_r1"]


def _liu_mdd() -> float:
    """Liu (2008) denk. (1) örneği: 'I actually live in Beijing' → 5/4."""
    from turkish_linguistic_features.features.dependency import dependency_features
    cumle = [(0, "PRON", "nsubj", 2), (1, "ADV", "advmod", 2),
             (2, "VERB", "root", 2), (3, "ADP", "case", 2),
             (4, "PROPN", "obl", 3)]
    return dependency_features([cumle])["arc_len_mean"]


# Anahtar → karşılaştırma listesi. Bir anahtarın birden çok kaynak örneği
# olabilir; hepsi rapora ayrı satır olarak girer.
KARSILASTIRMALAR: dict[str, list[Karsilastirma]] = {
    "atesman": [
        Karsilastirma("Ateşman (1997)", _KM + " · Metin 2", 23.094,
                      lambda: _km(2, "atesman")),
        Karsilastirma("Ateşman (1997) s.74", "kalibrasyon: en kolay metin", 100.0,
                      lambda: _atesman(2.2, 4), tur=FORMUL),
        Karsilastirma("Ateşman (1997) s.74", "kalibrasyon: en zor metin", 0.0,
                      lambda: _atesman(3.0, 30), tur=FORMUL),
    ],
    "cetinkaya_uzun": [
        Karsilastirma("Çetinkaya (2010)", _KM + " · Metin 2", 23.084,
                      lambda: _km(2, "cetinkaya_uzun")),
    ],
    "bezirci_yilmaz": [
        Karsilastirma("Bezirci & Yılmaz (2010)", _KM + " · Metin 2",
                      math.sqrt(925.5625), lambda: _km(2, "bezirci_yilmaz"),
                      "Makalenin H6 ara değeri yuvarlanmış; fark 0,031 ve iki "
                      "değer de aynı okunabilirlik sınıfına (akademik, 16+) düşüyor."),
        # denk. (9) — karekök adımı. E7 makalenin bastığı ara değer.
        Karsilastirma("Bezirci & Yılmaz (2010) Tablo 5", "E7 3,03 · OKS 7",
                      4.61, lambda: _bezirci_e9(7, 3.03), tur=FORMUL),
        Karsilastirma("Bezirci & Yılmaz (2010) Tablo 5", "E7 8,3 · OKS 10",
                      9.11, lambda: _bezirci_e9(10, 8.3), tur=FORMUL),
        Karsilastirma("Bezirci & Yılmaz (2010) Tablo 5", "E7 18,82 · OKS 14",
                      16.23, lambda: _bezirci_e9(14, 18.82), tur=FORMUL),
        # denk. (7) — hece katsayıları. Ortalama satırı bilinen sapma.
        Karsilastirma("Bezirci & Yılmaz (2010) Tablo 3", "en kolay metnin H değerleri",
                      3.03, lambda: _bezirci_e7(1.36, 0.52, 0.24, 0.01), tur=FORMUL),
        Karsilastirma("Bezirci & Yılmaz (2010) Tablo 3", "en zor metnin H değerleri",
                      18.82, lambda: _bezirci_e7(4.75, 3.21, 1.36, 0.20), tur=FORMUL),
        Karsilastirma("Bezirci & Yılmaz (2010) Tablo 3", "ortalama H değerleri",
                      8.30, lambda: _bezirci_e7(2.57, 1.52, 0.59, 0.07), tur=FORMUL,
                      gerekce="Makale H6 ortalamasını 0,07 diye basmış ama 8,30'u "
                              "veren değer ≈0,0684. 26,25 katsayısı bu yuvarlamayı "
                              "0,041'e büyütüyor; katsayıların kendisi doğru."),
    ],
    "arc_len_mean": [
        Karsilastirma("Jing & Liu (2015) s.164", "Figure 3 · 'Mr. Nixon was to…'",
                      7 / 6, lambda: _jing_liu("arc_len_mean"), tur=FORMUL),
        Karsilastirma("Liu (2008) denk. (1)", "'I actually live in Beijing' · 5/4",
                      1.25, _liu_mdd, tur=FORMUL),
    ],
    "parse_depth_mean": [
        Karsilastirma("Jing & Liu (2015) s.164", "Figure 3 · MHD = 12/6",
                      2.0, lambda: _jing_liu("parse_depth_mean"), tur=FORMUL),
    ],
    "h_point": [
        # QUITA §6.1.2, Tablo 6.1/6.2. İki dal da sınanıyor: Text 1'de bir rank
        # frekansına eşit (h doğrudan okunur), Text 2'de eşit yok (denk. 6.2
        # ile ara değerleme) — asıl hata yapılabilecek yer ikincisi.
        Karsilastirma("QUITA §6.1.2 Tablo 6.1", "Text 1 · rank 5 = frekans 5",
                      5.0, lambda: _h_point(_T1, 179), tur=FORMUL),
        Karsilastirma("QUITA §6.1.2 Tablo 6.2", "Text 2 · ara değerleme, denk. (6.2)",
                      4.75, lambda: _h_point(_T2, 202), tur=FORMUL),
    ],
    "vocab_richness_r1": [
        # QUITA §6.1.3, denk. (6.3). Text 2 ayrıca kesirli h'de toplamanın
        # ⌊h⌋'ye kadar gittiğini sınıyor: kılavuz 20+9+8+7 topluyor, h=4,75.
        Karsilastirma("QUITA §6.1.3", "Text 1 · N=179, h=5", 0.8352,
                      lambda: _r1(_T1, 179), tur=FORMUL),
        Karsilastirma("QUITA §6.1.3", "Text 2 · N=202, h=4,75 → ⌊h⌋=4", 0.838,
                      lambda: _r1(_T2, 202), tur=FORMUL),
    ],
}


# ── dizge karşılaştırmaları ───────────────────────────────────────────
#
# Sayı değil bölütleme sınanıyor. Heceleme 8 ``syllable_*`` anahtarını ve üç
# Türkçe okunabilirlik formülünü birden besliyor, yani buradaki bir hata
# yukarı doğru yayılır. Sayı karşılaştırması bunu yakalamaz: yanlış yerden
# bölünmüş bir kelime doğru sayıda hece verebilir.
#
# Kaynak: TDK, "Hece Yapısı ve Satır Sonunda Kelimelerin Bölünmesi"
# (tdk.gov.tr, 2019) — örnekler kuralın kendi yayımlanmış örnekleri.
TDK_HECELEME: dict[str, str] = {
    "aldı": "al-dı",
    "altlık": "alt-lık",
    "türkçe": "türk-çe",
    "program": "prog-ram",          # Batı kökenli: kural sezgiye aykırı
    "kontrol": "kont-rol",
    "santral": "sant-ral",
    "saat": "sa-at",                # yan yana iki ünlü ayrı hece
    "karaosmanoğlu": "ka-ra-os-ma-noğ-lu",
    "tren": "tren",                 # kelime başı ünsüz kümesi bölünmez
    "strateji": "stra-te-ji",
}


def heceleme_satirlari() -> list[dict[str, object]]:
    """TDK'nın yayımlanmış hecelemeleriyle karşılaştırma."""
    from turkish_linguistic_features.features.phonetic import _syllabify_tr
    return [{"kelime": k, "beklenen": bek, "bizim": "-".join(_syllabify_tr(k)),
             "durum": BIREBIR if "-".join(_syllabify_tr(k)) == bek else UYUSMAZLIK}
            for k, bek in TDK_HECELEME.items()]


def rapor_satirlari(lang: str = "tr") -> list[dict[str, object]]:
    """Taban şemadaki her anahtar için bir satır.

    Kapsam ``analyze()`` çıktısından okunur; registry'ye yeni bir anahtar
    girdiğinde rapor kendiliğinden büyür.
    """
    satirlar: list[dict[str, object]] = []
    for anahtar in tlf.analyze(ORNEK_METIN[lang], lang=lang):
        kunye = tlf.describe_feature(anahtar)["citation"]
        for kars in KARSILASTIRMALAR.get(anahtar, []):
            bizim = kars.hesapla()
            fark = bizim - kars.beklenen
            if abs(fark) <= TOLERANS:
                durum = SAPMA if (abs(fark) > 1e-3 and kars.gerekce) else BIREBIR
            else:
                durum = UYUSMAZLIK
            satirlar.append({"anahtar": anahtar, "kaynak": kars.kaynak,
                             "ornek": kars.ornek, "beklenen": kars.beklenen,
                             "bizim": bizim, "fark": fark, "durum": durum,
                             "gerekce": kars.gerekce, "tur": kars.tur})
        if anahtar not in KARSILASTIRMALAR:
            satirlar.append({
                "anahtar": anahtar, "kaynak": kunye or "—", "ornek": "—",
                "beklenen": None, "bizim": None, "fark": None,
                "durum": ORNEK_YOK if kunye else KAYNAK_YOK,
                "gerekce": "", "tur": "—",
            })
    return satirlar


_BASLIK = """<!-- ÜRETİLMİŞ DOSYA — elle düzenlemeyin.
     Kaynak: scripts/dogrulama_raporu.py
     Yeniden üretmek için:
       python scripts/dogrulama_raporu.py -->

# Doğrulama raporu

Bu rapor her özniteliğin ürettiği sayıyı, dayandığı kaynağın **yayımladığı
sayıyla** karşılaştırır. Amaç basit: bir sayıyı çalışmanızda kullanmadan önce
onun literatürdeki değeri tuttuğunu görebilmeniz.

## Durumlar ne anlama geliyor

| | Anlamı |
|---|---|
| ✅ **birebir** | Kaynağın yayımladığı sayıyla tolerans içinde aynı. |
| 🟡 **belgelenmiş sapma** | Fark var ve **nedeni yazılı**. Genellikle kaynağın ara değerleri yuvarlaması. Sapmanın sonuca etkisi satırda anlatılır. |
| ⚪ **kaynakta sayısal örnek yok** | Kaynak formülü veriyor ama uygulanmış bir örnek vermiyor; yalnız formül ve sınır durumları sınanıyor. |
| ⚪ **kaynak yok** | Adlandırılmış bir literatür ölçüsü değil (`punc_,_ratio` gibi saf tanım). |
| ❌ **uyuşmazlık** | Açıklanmamış fark. **Yayın kapısı:** bir tane bile varsa sürüm çıkmaz. |

Tolerans {tolerans}. Kaynaklar ara değerleri yuvarlayarak bastığı için mutlak
eşitlik beklenmiyor; farkın nereden geldiği bilinmiyorsa satır ❌ olur.

## Kanıtın iki türü

**Uçtan uca** satırlar kaynağın **metnini** boru hattından geçirir — yani
tokenizasyon, heceleme ve cümle bölme de sınanır. Bunlar en güçlü kanıt.

**Formül** satırları fonksiyona girdileri doğrudan verir (örneğin "hece/sözcük
2,2 ve sözcük/cümle 4"). Formülü ve katsayıları doğrular, boru hattını
doğrulamaz. Kaynak bir metin yayımlamamışsa elde olan budur.

Bu rapor **testlerden üretilir** — `tests/test_kaynak_esligi.py` ile aynı
karşılaştırma tablosunu okur, yani ikisi ayrışamaz. Diğer bilinen-değer
testleri (T04B, T05–T07, T10, T13) kendi dosyalarında duruyor.

"""


def _ozet(satirlar: list[dict[str, object]]) -> str:
    from collections import Counter
    sayim = Counter(s["durum"] for s in satirlar)
    satir = ["| Durum | Satır sayısı |", "|---|---|"]
    for durum in (BIREBIR, SAPMA, ORNEK_YOK, KAYNAK_YOK, UYUSMAZLIK):
        if sayim[durum]:
            satir.append(f"| {_SIMGE[durum]} {durum.replace('_', ' ')} | {sayim[durum]} |")
    return "\n".join(satir)


def uret() -> str:
    parcalar = [_BASLIK.replace("{tolerans}", str(TOLERANS))]
    for lang, etiket in (("tr", "Türkçe"), ("en", "İngilizce")):
        satirlar = rapor_satirlari(lang)
        n_anahtar = len({s["anahtar"] for s in satirlar})
        parcalar.append(f"\n## {etiket} — {n_anahtar} anahtar, "
                        f"{len(satirlar)} satır\n\n"
                        "Bir anahtarın birden çok kaynak örneği olabilir; her biri "
                        "ayrı satır.\n\n")
        parcalar.append(_ozet(satirlar))
        parcalar.append("\n\n### Sayısal karşılaştırması olanlar\n\n")
        parcalar.append("| Anahtar | Kaynak | Örnek | Kanıt | Beklenen | Bizim | Fark | Durum |\n")
        parcalar.append("|---|---|---|---|---|---|---|---|\n")
        olculen = [s for s in satirlar if s["beklenen"] is not None]
        for s in olculen:
            parcalar.append(
                f"| `{s['anahtar']}` | {s['kaynak']} | {s['ornek']} | {s['tur']} "
                f"| {s['beklenen']:.3f} | {s['bizim']:.3f} | {s['fark']:+.3f} "
                f"| {_SIMGE[s['durum']]} |\n")
        if not olculen:
            parcalar.append("| — | — | — | — | — | — | — | — |\n")
        for s in olculen:
            if s["gerekce"]:
                parcalar.append(f"\n**`{s['anahtar']}` sapması:** {s['gerekce']}\n")
        parcalar.append("\n### Sayısal örneği olmayanlar\n\n")
        kalan = [s for s in satirlar if s["beklenen"] is None]
        parcalar.append(f"{len(kalan)} anahtar. Kaynağı olanlar formül ve sınır "
                        "durumu testleriyle sınanıyor; kaynağı olmayanlar "
                        "adlandırılmış literatür ölçüsü değil.\n\n")
        parcalar.append("| Anahtar | Kaynak | Durum |\n|---|---|---|\n")
        for s in kalan:
            parcalar.append(f"| `{s['anahtar']}` | {s['kaynak']} | {_SIMGE[s['durum']]} |\n")

    # Heceleme ayrı: sayı değil bölütleme sınanıyor.
    hece = heceleme_satirlari()
    tam = sum(1 for s in hece if s["durum"] == BIREBIR)
    parcalar.append(
        f"\n## Heceleme — {tam}/{len(hece)}\n\n"
        "Heceleme sekiz `syllable_*` anahtarını ve üç Türkçe okunabilirlik "
        "formülünü birden besliyor. Aşağıdaki karşılaştırma **sayıyı değil "
        "bölütlemeyi** sınıyor: yanlış yerden bölünmüş bir kelime doğru sayıda "
        "hece verebilir, sayı karşılaştırması onu yakalamaz.\n\n"
        "Kaynak: TDK, \"Hece Yapısı ve Satır Sonunda Kelimelerin Bölünmesi\" "
        "(tdk.gov.tr, 2019).\n\n"
        "| Kelime | TDK | Bizim | Durum |\n|---|---|---|---|\n")
    for s in hece:
        parcalar.append(f"| {s['kelime']} | `{s['beklenen']}` | `{s['bizim']}` "
                        f"| {_SIMGE[s['durum']]} |\n")
    return "".join(parcalar)


if __name__ == "__main__":
    hedef = Path(__file__).resolve().parents[1] / "docs" / "dogrulama-raporu.md"
    hedef.parent.mkdir(exist_ok=True)
    hedef.write_text(uret(), encoding="utf-8")
    print(f"Yazıldı: {hedef}")
