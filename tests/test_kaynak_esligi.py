"""T31 — kaynaklarla eşlik doğrulaması.

Her test bir özniteliğin ürettiği sayıyı, dayandığı kaynağın **yayımladığı
sayıyla** karşılaştırır. Amaç kullanıcının bir sayıya güvenmeden önce onun
literatürdeki değeri tuttuğunu görebilmesi.

Her testin künyesinde kaynak, sayfa/tablo numarası ve tolerans yazılıdır.
Tolerans keyfî değil: kaynaklar ara değerleri yuvarlayarak bastığı için
birebir eşitlik beklenemez (bkz. `plan/kaynak-arastirmasi.md`, Çıplak ve
Bezirci örnekleri).

**Telif:** Aşağıdaki üç metin Kalyoncu & Memiş (2024) Ek-1'de yayımlanmış
100 kelimelik okunabilirlik örnekleridir ve doğrulama amacıyla, kaynakları
tam gösterilerek alıntılanmıştır. Kaynak metinlerin tamamı depoya girmez.

K12 bilinen-değer testleri (T04B, T05-T07, T10, T13) buraya **taşınmadı**;
onlar kendi dosyalarında duruyor ve rapor onlara referans veriyor.
"""

import math

import pytest

from scripts.dogrulama_raporu import METIN_1, METIN_2, METIN_3
from turkish_linguistic_features import analyze

# Kalyoncu & Memiş (2024) Tablo 9 — üç metnin okunabilirlik değerleri.
# Bezirci-Yılmaz sütunu makalede karekök içinde basılmış (√606,202 gibi).
BEKLENEN = {
    "atesman": (35.946, 23.094, 41.393),
    "cetinkaya_uzun": (27.953, 23.084, 26.403),
    "bezirci_yilmaz": (math.sqrt(606.202), math.sqrt(925.5625), math.sqrt(338.1)),
}

# Ölçüldü (2026-09-19): dokuz karşılaştırmanın en büyük farkı 0,031.
# Üçü (Metin 2'nin atesman ve cetinkaya_uzun'u) üç ondalığa kadar birebir.
TOLERANS = 0.05


@pytest.fixture(scope="module")
def ozellikler():
    return [analyze(m, lang="tr") for m in (METIN_1, METIN_2, METIN_3)]


@pytest.mark.parametrize("anahtar", sorted(BEKLENEN))
@pytest.mark.parametrize("metin_no", (1, 2, 3))
def test_kalyoncu_memis_tablo9(ozellikler, anahtar, metin_no):
    """Kalyoncu & Memiş (2024) Tablo 9 · Ana Dili Eğitimi Dergisi 12(2), 417-436."""
    bizim = ozellikler[metin_no - 1][anahtar]
    beklenen = BEKLENEN[anahtar][metin_no - 1]
    assert bizim == pytest.approx(beklenen, abs=TOLERANS), (
        f"{anahtar} / Metin {metin_no}: bizim {bizim:.3f}, makalede {beklenen:.3f}"
    )


def test_metin2_birebir(ozellikler):
    """🔴 En güçlü kanıt: Metin 2'de iki formül de ÜÇ ONDALIĞA KADAR tutuyor.

    Tolerans gevşetilirse bu test onu yakalar — birebir eşlik kaybolursa
    tokenizasyon, heceleme ya da cümle bölmede bir şey kaymış demektir.
    """
    f = ozellikler[1]
    assert f["atesman"] == pytest.approx(23.094, abs=0.001)
    assert f["cetinkaya_uzun"] == pytest.approx(23.084, abs=0.001)


def test_bezirci_sapmasi_belgelenmis(ozellikler):
    """🟡 Belgelenmiş sapma: Metin 2'de 30,392 ↔ 30,423 (fark 0,031).

    Plan bu sapmayı önceden biliyordu (makalenin H6 sabiti). Fark sonucu
    etkilemiyor: her iki değer de Bezirci-Yılmaz ölçeğinde aynı sınıfa
    (akademik, 16+) düşüyor. Sapma büyürse bu test kırılır.
    """
    fark = ozellikler[1]["bezirci_yilmaz"] - math.sqrt(925.5625)
    assert -0.05 < fark < 0.0, f"beklenen sapma ~-0.031, bulunan {fark:.4f}"


# ── rapor kapsamı ve yayın kapısı ─────────────────────────────────────


@pytest.mark.parametrize("lang", ("tr", "en"))
def test_raporda_her_taban_anahtar_var(lang):
    """Kapsam: hiçbir öznitelik rapordan kaçamaz.

    Kapsam listesi ``analyze()``dan okunuyor, elle tutulmuyor — registry'ye
    yeni bir anahtar girdiğinde rapor kendiliğinden büyür.
    """
    from scripts.dogrulama_raporu import ORNEK_METIN, rapor_satirlari
    anahtarlar = {s["anahtar"] for s in rapor_satirlari(lang)}
    assert anahtarlar == set(analyze(ORNEK_METIN[lang], lang=lang))


@pytest.mark.parametrize("lang", ("tr", "en"))
def test_raporda_uyusmazlik_yok(lang):
    """🔴 Yayın kapısı: açıklanmamış bir fark varsa T30 başlamaz."""
    from scripts.dogrulama_raporu import UYUSMAZLIK, rapor_satirlari
    kotu = [s for s in rapor_satirlari(lang) if s["durum"] == UYUSMAZLIK]
    assert not kotu, f"açıklanmamış fark: {[s['anahtar'] for s in kotu]}"


@pytest.mark.parametrize("lang", ("tr", "en"))
def test_sapma_satirlarinin_gerekcesi_var(lang):
    """🟡 sayılmak için sapmanın NEDENİ yazılı olmalı — yoksa o bir ❌."""
    from scripts.dogrulama_raporu import SAPMA, rapor_satirlari
    gerekcesiz = [s["anahtar"] for s in rapor_satirlari(lang)
                  if s["durum"] == SAPMA and not s["gerekce"]]
    assert not gerekcesiz, f"gerekçesiz sapma: {gerekcesiz}"


def test_rapor_guncel():
    """Üretilen rapor commit'lenmiş dosyayla aynı olmalı.

    CI yok (2026-09-21, Efe: v1.0.0'a kadar) — kontrol testte duruyor.
    """
    from pathlib import Path

    from scripts.dogrulama_raporu import uret
    yol = Path(__file__).resolve().parents[1] / "docs" / "dogrulama-raporu.md"
    assert yol.read_text(encoding="utf-8") == uret(), (
        "docs/dogrulama-raporu.md bayat — "
        "python scripts/dogrulama_raporu.py"
    )


# ── heceleme: bölütleme, sayı değil ───────────────────────────────────


def test_tdk_heceleme():
    """TDK'nın yayımlanmış hecelemeleri — 8 ``syllable_*`` anahtarının temeli.

    Sayı karşılaştırması yetmez: yanlış yerden bölünmüş bir kelime doğru
    sayıda hece verebilir. Burada bölütlemenin kendisi sınanıyor.
    """
    from scripts.dogrulama_raporu import UYUSMAZLIK, heceleme_satirlari
    kotu = [(s["kelime"], s["bizim"], s["beklenen"])
            for s in heceleme_satirlari() if s["durum"] == UYUSMAZLIK]
    assert not kotu, f"TDK ile uyuşmayan heceleme: {kotu}"
