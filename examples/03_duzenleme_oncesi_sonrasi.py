"""Düzenleme öncesi / sonrası — aynı metnin iki sürümü.

Bir metni düzenlediniz, çevirdiniz ya da sadeleştirdiniz. Ölçülebilir olarak
**ne değişti?** Script iki sürümü yan yana koyar, farkı hesaplar ve mutlak
farka göre en çok kayan öznitelikleri açıklamalarıyla birlikte basar.

🔴 Script yalnız **betimler**. "Daha iyi", "daha kötü", "aynı yazar" gibi bir
yargı ya da bir benzerlik skoru üretmez — kütüphane ölçer, karar vermez (K10).
Sayının ne anlama geldiğine okuyucu karar verir.

Çalıştırma::

    python examples/03_duzenleme_oncesi_sonrasi.py
"""

import math

import turkish_linguistic_features as tlf

# Ayarlar en üstte, tek yerde.
DIL = "tr"
GRUP = "sentence"          # yan yana tam basılacak grup
EN_COK_DEGISEN = 10

METIN_ONCE = (
    "Çalışmanın kapsamı, dilsel özniteliklerin nicel olarak ölçülmesi yoluyla "
    "metinler arasındaki biçimsel farklılıkların betimlenmesi ve bu "
    "betimlemenin yeniden üretilebilir bir yöntemle sunulması olarak "
    "belirlenmiş olup, söz konusu ölçümlerin gerçekleştirilmesinde kullanılan "
    "araçların seçimi, ölçülen değerlerin karşılaştırılabilirliğini doğrudan "
    "etkileyen bir unsur olduğundan, yöntem bölümünde ayrıntılı biçimde "
    "açıklanmaktadır. Ölçümlerin tekrarlanabilirliğinin sağlanabilmesi "
    "amacıyla, kullanılan bütün parametrelerin ve eşik değerlerinin, "
    "çalışmanın ekinde eksiksiz olarak listelenmesi tercih edilmiştir."
)

METIN_SONRA = (
    "Bu çalışma metinler arasındaki biçimsel farkları nicel olarak ölçer. "
    "Amaç, farkları yeniden üretilebilir bir yöntemle betimlemektir. Ölçüm "
    "aracının seçimi sonucu doğrudan etkiler. Bu yüzden aracı yöntem "
    "bölümünde açıkça yazdık. Kullandığımız bütün parametreleri ve eşik "
    "değerlerini de ekte listeledik. Böylece ölçümler tekrarlanabilir."
)


def main() -> None:
    print("Düzenleme öncesi sürüm çözümleniyor...")
    once = tlf.analyze(METIN_ONCE, lang=DIL)
    print("Düzenleme sonrası sürüm çözümleniyor...")
    sonra = tlf.analyze(METIN_SONRA, lang=DIL)

    # 1. Seçilen grubu iki sütun hâlinde yan yana bas.
    anahtarlar = [k for k in once if tlf.describe_feature(k)["group"] == GRUP]
    etiket = tlf.describe_feature(anahtarlar[0])["group_label"]
    print(f"\n-- {GRUP} - {etiket} " + "-" * 16)
    print(f"{'öznitelik':<30} {'önce':>10} {'sonra':>10} {'fark':>10}")
    for anahtar in anahtarlar:
        a, b = once[anahtar], sonra[anahtar]
        print(f"{anahtar:<30} {a:>10.4f} {b:>10.4f} {b - a:>+10.4f}")

    # 2. Bütün şema üzerinde mutlak farka göre sırala.
    #    NaN dönen öznitelikler (ölçülemeyenler) sıralamaya girmez: farkları
    #    tanımsızdır, sıfır değil.
    #    Ham fark ölçeğe bağlıdır — okunabilirlik puanı onlarca birim oynarken
    #    bir oran en çok 1 oynayabilir, bu yüzden liste büyük ölçekli
    #    anahtarlarla başlar. Tek ölçekte kalmak için
    #    ``describe_feature(k)["scale"]`` ile süzün.
    farklar = {k: sonra[k] - once[k] for k in once
               if math.isfinite(once[k]) and math.isfinite(sonra[k])}
    atlanan = len(once) - len(farklar)

    print(f"\n-- En çok kayan {EN_COK_DEGISEN} öznitelik " + "-" * 24)
    for anahtar in sorted(farklar, key=lambda k: abs(farklar[k]),
                          reverse=True)[:EN_COK_DEGISEN]:
        bilgi = tlf.describe_feature(anahtar)
        print(f"{anahtar:<30} {once[anahtar]:>10.4f} -> {sonra[anahtar]:>10.4f} "
              f"({farklar[anahtar]:+.4f})")
        print(f"{'':<30} {bilgi['description']}")

    print(f"\n{len(farklar)} öznitelik karşılaştırıldı, {atlanan} tanesi "
          "ölçülemediği için atlandı.")
    print("Sayılar betimlemedir; hangisinin önemli olduğuna siz karar verirsiniz.")


if __name__ == "__main__":
    main()
