"""Uzunluk duyarlılığı — hangi zenginlik ölçüsü metin boyundan bağımsız?

``ttr`` (farklı kelime / toplam kelime) metin uzadıkça düşer: yeni kelime
çıkma olasılığı azalır. Uzunlukları farklı metinleri ``ttr`` ile
karşılaştırırsanız ölçtüğünüz şey üslup değil metin boyu olur. ``mattr``,
``hdd``, ``msttr`` gibi ölçüler bu etkiye karşı tasarlanmıştır. Bu script
aynı metinden artan uzunlukta parçalar alıp ölçülerin ne kadar kaydığını
gösterir.

    python examples/09_uzunluk_duyarliligi.py metin.txt

Argüman verilmezse demo metni kullanılır (~300 kelime; kısa boylarla).
"""

import math
import sys
from pathlib import Path

import turkish_linguistic_features as tlf
from _demo import demo_metni

DIL = "tr"
BOYLAR = [250, 500, 1000, 2000, 4000]
DEMO_BOYLAR = [100, 200, 300]
OLCULER = ["ttr", "mattr", "hdd", "msttr", "herdan_c", "mtld", "vocd_d"]
DAYANIKLI_ESIK = 15.0      # yüzde yayılım; altı "dayanıklı" sayılır
CIKTI_DIZINI = Path("examples/output")


def main() -> None:
    if len(sys.argv) > 1:
        dosya = Path(sys.argv[1])
        if not dosya.is_file():
            sys.exit(f"Dosya bulunamadı: {dosya}")
        metin, boylar = dosya.read_text(encoding="utf-8"), BOYLAR
    else:
        print("Metin verilmedi; demo metni kullanılıyor.\n")
        metin, boylar = demo_metni(), DEMO_BOYLAR

    satirlar = []
    for boy in boylar:
        parcalar = tlf.segment_text(metin, segment_size=boy, lang=DIL)
        if not parcalar:
            print(f"  {boy:>5} kelime: metin bu boydan kısa, atlandı")
            continue
        oz = tlf.analyze(parcalar[0], lang=DIL, groups=["lexical"], warn=False)
        satirlar.append({"kelime": boy, **{o: oz[o] for o in OLCULER}})

    if len(satirlar) < 2:
        sys.exit("Karşılaştırma için en az iki boy gerekiyor; daha uzun bir metin verin.")

    print(f"{'kelime':>7}" + "".join(f"{o:>10}" for o in OLCULER))
    for s in satirlar:
        print(f"{s['kelime']:>7}" + "".join(f"{s[o]:>10.4f}" for o in OLCULER))

    # Yayılım: en büyük ve en küçük değer arasındaki fark, ortalamanın yüzdesi.
    print(f"\n{'ölçü':<10}{'yayılım':>10}")
    for o in OLCULER:
        degerler = [s[o] for s in satirlar if not math.isnan(s[o])]
        if len(degerler) < 2:
            print(f"{o:<10}{'—':>10}   bu boylarda ölçülemedi")
            continue
        yayilim = (max(degerler) - min(degerler)) / (sum(degerler) / len(degerler)) * 100
        durum = "dayanıklı" if yayilim < DAYANIKLI_ESIK else "uzunluğa duyarlı"
        print(f"{o:<10}{yayilim:>9.1f}%   {durum}")

    print("\nUzunlukları eşit olmayan metinleri karşılaştıracaksanız ya parçaları "
          "eşitleyin\n(analyze_corpus(..., segment_size=...)) ya da dayanıklı bir ölçü seçin.")

    CIKTI_DIZINI.mkdir(parents=True, exist_ok=True)
    yol = CIKTI_DIZINI / "uzunluk_duyarliligi.csv"
    tlf.save_csv(satirlar, yol)
    print(f"\nCSV yazıldı: {yol}")


if __name__ == "__main__":
    main()
