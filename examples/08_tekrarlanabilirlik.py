"""Tekrarlanabilirlik — aynı metin yarın da aynı sayıları verir mi?

Bazı ölçüler örnekleme yapar: ``vocd_d`` metinden rastgele örnekler çeker.
Rastgelelik sabitlenmemiş olsaydı tablonuz her çalıştırmada değişir,
makaledeki hiçbir sayı yeniden üretilemezdi. Bu script aynı metni birkaç kez
analiz edip **hiçbir özniteliğin oynamadığını** denetler, sonra rastgelelik
tohumunu (``vocd_random_seed``) değiştirip hangi ölçülerin ona bağlı olduğunu
gösterir.

    python examples/08_tekrarlanabilirlik.py metin.txt

Argüman verilmezse demo metni kullanılır.
"""

import math
import sys
from pathlib import Path

import turkish_linguistic_features as tlf

from _demo import demo_metni

DIL = "tr"
TEKRAR = 3
BASKA_TOHUM = 7            # varsayılan tohum 42


def ayni(a: float, b: float) -> bool:
    """NaN'ı NaN'a eşit sayan karşılaştırma."""
    return (math.isnan(a) and math.isnan(b)) or a == b


def main() -> None:
    if len(sys.argv) > 1:
        dosya = Path(sys.argv[1])
        if not dosya.is_file():
            sys.exit(f"Dosya bulunamadı: {dosya}")
        metin = dosya.read_text(encoding="utf-8")
    else:
        print("Metin verilmedi; demo metni kullanılıyor.\n")
        metin = demo_metni()

    kosular = [tlf.analyze(metin, lang=DIL, warn=False) for _ in range(TEKRAR)]
    oynayan = [a for a in kosular[0]
               if any(not ayni(kosular[0][a], k[a]) for k in kosular[1:])]
    print(f"Aynı metin {TEKRAR} kez, {len(kosular[0])} öznitelik:")
    print(f"  oynayan öznitelik: {', '.join(oynayan) if oynayan else 'yok'}")

    varsayilan = kosular[0]
    baska = tlf.analyze(metin, lang=DIL, params=tlf.FeatureParams(vocd_random_seed=BASKA_TOHUM),
                        warn=False)
    tohuma_bagli = [a for a in varsayilan if not ayni(varsayilan[a], baska[a])]
    print(f"\nvocd_random_seed 42 -> {BASKA_TOHUM}:")
    if not tohuma_bagli:
        print("  hiçbir öznitelik değişmedi")
    for a in tohuma_bagli:
        print(f"  {a:<12} {varsayilan[a]:>12.4f} -> {baska[a]:>12.4f}")

    print("\nVarsayılan ayarlarla çıktı tekrarlanabilir. Tohuma bağlı ölçüleri "
          "raporlarken\nkullandığınız vocd_random_seed değerini yöntem bölümüne yazın.")


if __name__ == "__main__":
    main()
