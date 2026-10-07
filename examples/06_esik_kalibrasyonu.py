"""Eşik kalibrasyonu — kısa/uzun cümle eşiğini kendi korpusumdan türetmek.

Varsayılan eşikler (Türkçe kısa < 4, uzun > 18) roman korpusunda cümle
uzunluğu dağılımının 15. ve 85. yüzdeliğinden gelir ([belge](../docs/esik-kalibrasyonu.md)).
Başka bir türle — haber, akademik metin, transkript — çalışıyorsanız aynı
yöntemi kendi korpusunuza uygulayabilirsiniz.

    python examples/06_esik_kalibrasyonu.py korpus/

**Tek kural: cümleyi kütüphaneyle aynı biçimde bölün.** Nokta/soru işaretine
göre bölen kaba bir bölücü kısaltmada, baş harfte ve üç noktada sahte cümle
üretir ve dağılımı aşağı çeker; ortaya çıkan fark "korpusum farklı" diye
okunur ama aslında yöntem farkıdır. Bu script cümleleri kütüphanenin
kullandığı spaCy modeliyle böler ve bunu **kendisi denetler**: her dosyada
kendi medyanını kütüphanenin ``sent_len_median`` değeriyle karşılaştırır.

Argüman verilmezse demo korpus kullanılır (cümle sayısı az; yüzdelikler
yalnız yöntemi gösterir).
"""

import statistics
import sys
from pathlib import Path

import spacy

import turkish_linguistic_features as tlf
from _demo import demo_korpus_yaz

DIL = "tr"
MODEL = {"tr": "tr_core_news_md", "en": "en_core_web_sm"}[DIL]
DOSYA_BASINA_KARAKTER = 100_000   # uzun dosyaların ortasından bu kadarı okunur
YUZDELIKLER = (15, 85)
CIKTI_DIZINI = Path("examples/output")


def orta_dilim(metin: str, karakter: int) -> str:
    """Ortadan dilim: kapak, künye, içindekiler ölçüme karışmasın."""
    if len(metin) <= karakter:
        return metin
    bas = (len(metin) - karakter) // 2
    return metin[bas:bas + karakter]


def cumle_uzunluklari(nlp: spacy.language.Language, metin: str) -> list[int]:
    """Kütüphanenin kuralı: spaCy cümlesi; harf ya da rakam içeren token
    kelimedir (noktalama düşer); hiç harf içermeyen cümle sayılmaz."""
    uzunluklar = []
    for cumle in nlp(metin).sents:
        tokenlar = [t.text for t in cumle if not t.is_space]
        if not any(c.isalpha() for t in tokenlar for c in t):
            continue
        uzunluklar.append(sum(1 for t in tokenlar if any(c.isalnum() for c in t)))
    return uzunluklar


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

    # Kütüphane Zeyrek'i spaCy'den önce yükler; Windows'ta bu sıra önemli.
    # Kendi spaCy modelimizi o yüklemeden SONRA açıyoruz.
    tlf.analyze("Hazırlık.", lang=DIL, groups=["morphological_zeyrek"], warn=False)
    nlp = spacy.load(MODEL, exclude=["ner"])
    tum_uzunluklar: list[int] = []
    ilk_metin = ""
    print(f"{'dosya':<34}{'cümle':>7}{'medyanım':>10}{'kütüphane':>11}")
    for dosya in sorted(korpus.glob("*.txt")):
        metin = orta_dilim(dosya.read_text(encoding="utf-8"), DOSYA_BASINA_KARAKTER)
        uzunluklar = cumle_uzunluklari(nlp, metin)
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
        sys.exit("Korpusta ölçülecek cümle bulunamadı.")

    sirali = sorted(tum_uzunluklar)
    kisa, uzun = (yuzdelik(sirali, p) for p in YUZDELIKLER)
    print(f"\nToplam {len(sirali):,} cümle, medyan {statistics.median(sirali):.1f} kelime")
    for p in (5, 10, 15, 25, 50, 75, 85, 90, 95):
        isaret = "   <- eşik" if p in YUZDELIKLER else ""
        print(f"  {p:>3}. yüzdelik: {yuzdelik(sirali, p):>3} kelime{isaret}")

    print(f"\nKorpusunuzun eşiği : kısa < {kisa}, uzun > {uzun}")
    print("Varsayılan (roman)  : kısa < 4, uzun > 18")

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
