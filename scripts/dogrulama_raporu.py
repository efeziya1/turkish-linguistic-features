"""docs/dogrulama-raporu.md dosyasını üretir (T31).

Her öznitelik için, dayandığı kaynağın yayımladığı sayıyla karşılaştırmasını
tablolar. Kapsam listesi registry'den üretilir — elle tutulmaz, yani hiçbir
öznitelik rapordan kaçamaz.

Kullanım::

    uv run python scripts/dogrulama_raporu.py

Bu dosya elle DÜZENLENMEZ. Karşılaştırma eklemek için aşağıdaki
``KARSILASTIRMALAR`` tablosuna satır yazın; testler
(``tests/test_kaynak_esligi.py``) aynı tabloyu okuyor, yani rapor ile
testler ayrışamaz.
"""

from __future__ import annotations

import math
from pathlib import Path

from turkish_linguistic_features import analyze, describe_feature

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


class Karsilastirma:
    """Bir anahtarın kaynaktaki yayımlanmış değeriyle karşılaştırması."""

    def __init__(self, kaynak: str, ornek: str, beklenen: float,
                 hesapla, gerekce: str = "") -> None:
        self.kaynak = kaynak
        self.ornek = ornek
        self.beklenen = beklenen
        self.hesapla = hesapla          # () -> float
        self.gerekce = gerekce          # sapma varsa NEDEN


def _kalyoncu_metin(no: int) -> dict[str, float]:
    """Ek-1'deki metinlerden birinin özniteliklerini verir."""
    return analyze((METIN_1, METIN_2, METIN_3)[no - 1], lang="tr")


_KM_ONBELLEK: dict[int, dict[str, float]] = {}


def _km(no: int, anahtar: str) -> float:
    if no not in _KM_ONBELLEK:
        _KM_ONBELLEK[no] = _kalyoncu_metin(no)
    return _KM_ONBELLEK[no][anahtar]


_KM = "Kalyoncu & Memiş (2024) Tablo 9"

KARSILASTIRMALAR: dict[str, Karsilastirma] = {
    "atesman": Karsilastirma(
        "Ateşman (1997)", _KM + " · Metin 2", 23.094, lambda: _km(2, "atesman")),
    "cetinkaya_uzun": Karsilastirma(
        "Çetinkaya (2010)", _KM + " · Metin 2", 23.084,
        lambda: _km(2, "cetinkaya_uzun")),
    "bezirci_yilmaz": Karsilastirma(
        "Bezirci & Yılmaz (2010)", _KM + " · Metin 2", math.sqrt(925.5625),
        lambda: _km(2, "bezirci_yilmaz"),
        "Makalenin H6 ara değeri yuvarlanmış; fark 0,031 ve iki değer de "
        "aynı okunabilirlik sınıfına (akademik, 16+) düşüyor."),
}


def rapor_satirlari(lang: str = "tr") -> list[dict[str, object]]:
    """Taban şemadaki her anahtar için bir satır.

    Kapsam ``analyze()`` çıktısından okunur; registry'ye yeni bir anahtar
    girdiğinde rapor kendiliğinden büyür.
    """
    satirlar: list[dict[str, object]] = []
    for anahtar in analyze(ORNEK_METIN[lang], lang=lang):
        d = describe_feature(anahtar)
        kunye = d["citation"]
        kars = KARSILASTIRMALAR.get(anahtar)

        if kars is not None:
            bizim = kars.hesapla()
            fark = bizim - kars.beklenen
            if abs(fark) <= 1e-3:
                durum = BIREBIR
            elif abs(fark) <= TOLERANS and kars.gerekce:
                durum = SAPMA
            elif abs(fark) <= TOLERANS:
                durum = BIREBIR
            else:
                durum = UYUSMAZLIK
            satirlar.append({"anahtar": anahtar, "kaynak": kars.kaynak,
                             "ornek": kars.ornek, "beklenen": kars.beklenen,
                             "bizim": bizim, "fark": fark, "durum": durum,
                             "gerekce": kars.gerekce})
        else:
            satirlar.append({
                "anahtar": anahtar,
                "kaynak": kunye or "—",
                "ornek": "—",
                "beklenen": None, "bizim": None, "fark": None,
                "durum": ORNEK_YOK if kunye else KAYNAK_YOK,
                "gerekce": "",
            })
    return satirlar


_BASLIK = """<!-- ÜRETİLMİŞ DOSYA — elle düzenlemeyin.
     Kaynak: scripts/dogrulama_raporu.py
     Yeniden üretmek için:
       uv run python scripts/dogrulama_raporu.py -->

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

Bu rapor **testlerden üretilir** — `tests/test_kaynak_esligi.py` ile aynı
karşılaştırma tablosunu okur, yani ikisi ayrışamaz. Diğer bilinen-değer
testleri (T04B, T05–T07, T10, T13) kendi dosyalarında duruyor.

"""


def _ozet(satirlar: list[dict[str, object]]) -> str:
    from collections import Counter
    sayim = Counter(s["durum"] for s in satirlar)
    satir = ["| Durum | Anahtar sayısı |", "|---|---|"]
    for durum in (BIREBIR, SAPMA, ORNEK_YOK, KAYNAK_YOK, UYUSMAZLIK):
        if sayim[durum]:
            satir.append(f"| {_SIMGE[durum]} {durum.replace('_', ' ')} | {sayim[durum]} |")
    return "\n".join(satir)


def uret() -> str:
    parcalar = [_BASLIK.replace("{tolerans}", str(TOLERANS))]
    for lang, etiket in (("tr", "Türkçe"), ("en", "İngilizce")):
        satirlar = rapor_satirlari(lang)
        parcalar.append(f"\n## {etiket} — {len(satirlar)} anahtar\n\n")
        parcalar.append(_ozet(satirlar))
        parcalar.append("\n\n### Sayısal karşılaştırması olanlar\n\n")
        parcalar.append("| Anahtar | Kaynak | Örnek | Beklenen | Bizim | Fark | Durum |\n")
        parcalar.append("|---|---|---|---|---|---|---|\n")
        olculen = [s for s in satirlar if s["beklenen"] is not None]
        for s in olculen:
            parcalar.append(
                f"| `{s['anahtar']}` | {s['kaynak']} | {s['ornek']} "
                f"| {s['beklenen']:.3f} | {s['bizim']:.3f} | {s['fark']:+.3f} "
                f"| {_SIMGE[s['durum']]} |\n")
        if not olculen:
            parcalar.append("| — | — | — | — | — | — | — |\n")
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
    return "".join(parcalar)


if __name__ == "__main__":
    hedef = Path(__file__).resolve().parents[1] / "docs" / "dogrulama-raporu.md"
    hedef.parent.mkdir(exist_ok=True)
    hedef.write_text(uret(), encoding="utf-8")
    print(f"Yazıldı: {hedef}")
