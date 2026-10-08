"""NaN haritası — metnim ne kadar kısa olabilir?

Metin kısaldıkça bazı öznitelikler ölçülemez hâle gelir ve ``nan`` döner:
tek tümcede tümce uzunluklarının entropisi ölçülmez, 50 sözcükte 100'lük
pencereyle MATTR hesaplanmaz. Bu script aynı metinden artan uzunlukta
parçalar alıp her uzunlukta kaç özniteliğin ölçülebildiğini ve hangilerinin
hangi uzunlukta "kurtulduğunu" gösterir. Sonuç örneklem tasarımına girer:
bütün öznitelikleri istiyorsanız parçalarınız en az kaç sözcük olmalı?

    python examples/07_nan_haritasi.py metin.txt

Parça boyu ``segment_text`` gibi **sözcük** sayar, künyedeki "at least N words"
koşuluyla aynı sözcüğü: 300 sözcüklük parça "300 sözcük" isteyen bir ölçüye
yeter.

Argüman verilmezse demo metni kullanılır (~300 sözcük; uzun boylar atlanır).
Ayrıntı: [NaN ne demek](../docs/tr/aciklama/nan.md).
"""

import math
import sys
from pathlib import Path

import turkish_linguistic_features as tlf
from _demo import demo_metni

DIL = "tr"
BOYLAR = [50, 100, 200, 300, 500, 1000, 2000, 3000]
CIKTI_DIZINI = Path("examples/output")


def nan_anahtarlari(oz: dict[str, float]) -> set[str]:
    return {a for a, v in oz.items() if isinstance(v, float) and math.isnan(v)}


def main() -> None:
    if len(sys.argv) > 1:
        dosya = Path(sys.argv[1])
        if not dosya.is_file():
            sys.exit(f"Dosya bulunamadı: {dosya}")
        metin = dosya.read_text(encoding="utf-8")
    else:
        print("Metin verilmedi; demo metni kullanılıyor.\n")
        metin = demo_metni()

    satirlar, nanlar = [], {}
    for boy in BOYLAR:
        parcalar = tlf.segment_text(metin, segment_size=boy, lang=DIL)
        if not parcalar:
            print(f"  {boy:>5} sözcük -> metin bu boydan kısa, atlandı")
            continue
        oz = tlf.analyze(parcalar[0], lang=DIL, warn=False)
        nanlar[boy] = nan_anahtarlari(oz)
        olculen = len(oz) - len(nanlar[boy])
        satirlar.append({"sözcük": boy, "oznitelik": len(oz), "nan": len(nanlar[boy]),
                         "olculebilen": olculen})
        print(f"  {boy:>5} sözcük -> {olculen:>3}/{len(oz)} ölçülebildi "
              f"({len(nanlar[boy])} nan)")

    if not satirlar:
        sys.exit("Metin en kısa boydan bile kısa.")

    print("\nHangi uzunlukta ne ölçülebilir oldu:")
    boylar = sorted(nanlar)
    for onceki, simdiki in zip(boylar, boylar[1:], strict=False):
        kurtulan = nanlar[onceki] - nanlar[simdiki]
        if kurtulan:
            print(f"  {simdiki:>5} sözcük: {', '.join(sorted(kurtulan))}")

    # Neden hâlâ nan? Her özniteliğin koşulu künyesinde yazılı: kimi daha
    # uzun metin ister, kimi metinde hiç olmayan bir yapı (paragraf sınırı,
    # belirli bir ek) ister — o durumda uzunluk artırmak işe yaramaz.
    kalan = nanlar[boylar[-1]]
    print(f"\nEn uzun parçada ({boylar[-1]} sözcük) hâlâ nan olan {len(kalan)} öznitelik:")
    if not kalan:
        print("  yok")
    for anahtar in sorted(kalan):
        print(f"  {anahtar:<24} koşul: {tlf.describe_feature(anahtar)['requires']}")

    CIKTI_DIZINI.mkdir(parents=True, exist_ok=True)
    yol = CIKTI_DIZINI / "nan_haritasi.csv"
    tlf.save_csv(satirlar, yol)
    print(f"\nCSV yazıldı: {yol}")


if __name__ == "__main__":
    main()
