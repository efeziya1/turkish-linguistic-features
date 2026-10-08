"""Kelime örüntüleri — kendi öbeklerinizi sayın, neyle eşleştiklerini görün.

``custom_ngrams`` kütüphanenin hazır öznitelikleri dışında **sizin**
aradığınız kalıbı sayar. Öbekte kelime de yazabilirsiniz, büyük harfle bir UD
sözcük türü etiketi de: ``["bir", "NOUN"]`` "bir" ve hemen ardından herhangi bir
isim demektir, ``["ADJ", "NOUN"]`` sıfat + isim. Eşleşme cümle sınırını aşmaz.

``analyze`` her öbek için bir sayı döndürür (``ngram_bir_NOUN_count``).
``ngram_matches`` aynı öbeğin metinde **hangi kelimelerle** eşleştiğini,
en sık olandan başlayarak verir; sayıların toplamı ``analyze``'dakiyle aynıdır.

    python examples/10_kelime_oruntuleri.py metin.txt

Argüman verilmezse demo metni kullanılır. Sondaki etiket karşılaştırması her
zaman demo korpusla yapılır.
"""

import sys
from collections import Counter
from pathlib import Path

import turkish_linguistic_features as tlf
from _demo import DEMO_METINLER, demo_metni

DIL = "tr"
OBEKLER = [["ve"], ["bir", "NOUN"], ["ADJ", "NOUN"], ["NOUN", "VERB"]]
GOSTERILECEK = 5           # öbek başına gösterilen eşleşme
KARSILASTIRILAN = ["ADJ", "NOUN"]


def main() -> None:
    if len(sys.argv) > 1:
        dosya = Path(sys.argv[1])
        if not dosya.is_file():
            sys.exit(f"Dosya bulunamadı: {dosya}")
        metin = dosya.read_text(encoding="utf-8")
    else:
        print("Metin verilmedi; demo metni kullanılıyor.\n")
        metin = demo_metni()

    # Yalnız `custom_ngrams` grubu: öbek sayımı için bütün öznitelikleri
    # hesaplamaya gerek yok.
    oz = tlf.analyze(metin, lang=DIL, custom_ngrams=OBEKLER,
                     groups=["custom_ngrams", "lexical"])
    kelime = oz["word_count"]
    print(f"-- Sayımlar ({kelime:.0f} kelime) " + "-" * 26)
    print(f"{'anahtar':<28}{'sayı':>6}{'1000 kelimede':>16}")
    for anahtar, sayi in oz.items():
        if anahtar.startswith("ngram_"):
            print(f"{anahtar:<28}{sayi:>6.0f}{sayi / kelime * 1000:>16.1f}")

    # Sayı tek başına "kaç kez" der; "hangi kelimelerle" sorusunun cevabı burada.
    for obek in OBEKLER:
        eslesmeler = tlf.ngram_matches(metin, obek, lang=DIL)
        print(f"\n-- {' '.join(obek)}: {sum(eslesmeler.values())} eşleşme, "
              f"{len(eslesmeler)} farklı biçim")
        for bicim, sayi in list(eslesmeler.items())[:GOSTERILECEK]:
            print(f"  {bicim:<30}{sayi:>4}")

    # Birden çok metin: her metnin sonucunu Counter ile toplayın.
    print(f"\n-- Etikete göre en sık {' '.join(KARSILASTIRILAN)} " + "-" * 20)
    etiketler: dict[str, Counter] = {}
    for ad, demo in DEMO_METINLER.items():
        etiket = ad.split("_")[0]
        etiketler.setdefault(etiket, Counter()).update(
            tlf.ngram_matches(demo, KARSILASTIRILAN, lang=DIL))
    for etiket, toplam in etiketler.items():
        ilk = ", ".join(f"{b} ({s})" for b, s in toplam.most_common(3)) or "—"
        print(f"  {etiket:<10}{ilk}")

    print("\nSayımlar düz sayıdır; uzunlukları farklı metinleri karşılaştırırken "
          "word_count'a\nbölün ya da metinleri aynı boya getirin (segment_size).")


if __name__ == "__main__":
    main()
