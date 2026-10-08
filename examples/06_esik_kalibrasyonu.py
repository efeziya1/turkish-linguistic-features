"""Eşik kalibrasyonu — kısa/uzun tümce eşiğini kendi korpusumdan türetmek.

Varsayılan eşikler (Türkçe kısa < 4, uzun > 17) gazete köşe yazılarında tümce
uzunluğu dağılımının 15. ve 85. yüzdeliğinden gelir ([belge](../docs/esik-kalibrasyonu.md)).
Başka bir türle — roman, akademik metin, transkript — çalışıyorsanız aynı
yöntemi kendi korpusunuza uygulayabilirsiniz.

    python examples/06_esik_kalibrasyonu.py korpus/

**Tek kural: tümceyi kütüphaneyle aynı biçimde bölün.** Nokta/soru işaretine
göre bölen kaba bir bölücü kısaltmada, baş harfte ve üç noktada sahte tümce
üretir ve dağılımı aşağı çeker; ortaya çıkan fark "korpusum farklı" diye
okunur ama aslında yöntem farkıdır. Bu script tümceleri ve sözcükleri
kütüphanenin kendi kuralıyla sayar ve bunu **kendisi denetler**: her dosyada
kendi medyanını kütüphanenin ``sent_len_median`` değeriyle karşılaştırır.

Argüman verilmezse demo korpus kullanılır (tümce sayısı az; yüzdelikler
yalnız yöntemi gösterir).
"""

import statistics
import sys
from pathlib import Path

import turkish_linguistic_features as tlf
from _demo import demo_korpus_yaz

# Kütüphanenin tümce ve sözcük kuralı genel API'de ayrı bir fonksiyon olarak
# yok; eşiği aynı kuralla türetmek için iç yardımcıları doğrudan çağırıyoruz.
from turkish_linguistic_features._analyze import _get_preprocessor
from turkish_linguistic_features.features.readability import cumle_birimleri, kural_cumleleri
from turkish_linguistic_features.features.syntactic import _cumle_kelimeleri
from turkish_linguistic_features.params import DEFAULT_PARAMS, resolve_sent_thresholds

DIL = "tr"
DOSYA_BASINA_KARAKTER = 100_000   # uzun dosyaların ortasından bu kadarı okunur
YUZDELIKLER = (15, 85)
CIKTI_DIZINI = Path("examples/output")


def orta_dilim(metin: str, karakter: int) -> str:
    """Ortadan dilim: kapak, künye, içindekiler ölçüme karışmasın."""
    if len(metin) <= karakter:
        return metin
    bas = (len(metin) - karakter) // 2
    return metin[bas:bas + karakter]


def cumle_uzunluklari(metin: str) -> list[int]:
    """Kütüphanenin kuralı: varsayılan tümce kuralı ve varsayılan sözcük
    (boşlukla ayrılan, kenar noktalaması atılan birim); harfsiz tümce sayılmaz."""
    tokenlar = _get_preprocessor(DIL, None).process(metin).to_dict()["surface_tokens"]
    cumleler = cumle_birimleri(metin, kural_cumleleri(tokenlar, DIL), DIL)
    return [len(c) for c in _cumle_kelimeleri(cumleler)]


def yuzdelik(sirali: list[int], p: float) -> int:
    return sirali[min(len(sirali) - 1, int(len(sirali) * p / 100))]


def main() -> None:
    if len(sys.argv) > 1:
        korpus = Path(sys.argv[1])
        if not korpus.is_dir():
            sys.exit(f"Korpus dizini bulunamadı: {korpus}")
    else:
        korpus = CIKTI_DIZINI / "demo_korpus"
        print(f"Korpus verilmedi; demo korpus kullanılıyor: {korpus}\n")
        demo_korpus_yaz(korpus)

    tum_uzunluklar: list[int] = []
    ilk_metin = ""
    print(f"{'dosya':<34}{'tümce':>7}{'medyanım':>10}{'kütüphane':>11}")
    for dosya in sorted(korpus.glob("*.txt")):
        metin = orta_dilim(dosya.read_text(encoding="utf-8"), DOSYA_BASINA_KARAKTER)
        uzunluklar = cumle_uzunluklari(metin)
        if not uzunluklar:
            continue
        ilk_metin = ilk_metin or metin
        tum_uzunluklar.extend(uzunluklar)
        kutuphane = tlf.analyze(metin, lang=DIL, groups=["sentence"],
                                warn=False)["sent_len_median"]
        benim = statistics.median(uzunluklar)
        isaret = "" if abs(benim - kutuphane) < 1e-9 else "   <- FARKLI"
        print(f"{dosya.stem[:33]:<34}{len(uzunluklar):>7}{benim:>10.1f}"
              f"{kutuphane:>11.1f}{isaret}")

    if not tum_uzunluklar:
        sys.exit("Korpusta ölçülecek tümce bulunamadı.")

    sirali = sorted(tum_uzunluklar)
    kisa, uzun = (yuzdelik(sirali, p) for p in YUZDELIKLER)
    print(f"\nToplam {len(sirali):,} tümce, medyan {statistics.median(sirali):.1f} sözcük")
    for p in (5, 10, 15, 25, 50, 75, 85, 90, 95):
        isaret = "   <- eşik" if p in YUZDELIKLER else ""
        print(f"  {p:>3}. yüzdelik: {yuzdelik(sirali, p):>3} sözcük{isaret}")

    print(f"\nKorpusunuzun eşiği : kısa < {kisa}, uzun > {uzun}")
    v_kisa, v_uzun = resolve_sent_thresholds(DEFAULT_PARAMS, DIL)
    print(f"Varsayılan         : kısa < {v_kisa}, uzun > {v_uzun} (köşe yazıları)")

    # Türetilen eşiği kullanmak: FeatureParams ile vermek yeter.
    kendi = tlf.FeatureParams(short_sent_threshold=kisa, long_sent_threshold=uzun)
    varsayilan = tlf.analyze(ilk_metin, lang=DIL, groups=["sentence"], warn=False)
    benim = tlf.analyze(ilk_metin, lang=DIL, groups=["sentence"], params=kendi,
                        warn=False)
    print("\nİlk dosya iki eşikle:")
    for ad, oz in (("varsayılan", varsayilan), ("kendi eşiğim", benim)):
        print(f"  {ad:<13} short_sent_ratio={oz['short_sent_ratio']:.4f}  "
              f"long_sent_ratio={oz['long_sent_ratio']:.4f}")
    print("\nKendi eşiğinizle ürettiğiniz sayıları raporlarken eşik değerlerini de "
          "yazın;\nfarklı eşikle ölçülmüş iki korpus bu iki sütunda kıyaslanamaz.")


if __name__ == "__main__":
    main()
