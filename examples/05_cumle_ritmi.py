"""Cümle ritmi — etiketler cümle uzunluğunun dağılımıyla ayrışıyor mu?

Ortalama cümle uzunluğu tek başına az şey söyler: iki yazar aynı ortalamayla
biri hep orta boy, öteki kısa ve çok uzun cümleleri karıştırarak yazabilir.
Üslup çoğu zaman **değişkenlikte** durur. Bu script korpustaki her etiket
için ortalama, medyan ve kısa/uzun cümle oranını yan yana koyar;
kısa ve uzun cümlelerin toplam payı ("uçlar") ritmin ne kadar dalgalı
olduğunu gösterir.

    python examples/05_cumle_ritmi.py korpus/

Argüman verilmezse demo korpus kullanılır. Beklenen düzen
``korpus/Etiket_Başlık.txt``; etiket dosya adının ``_`` öncesinden gelir.
Aynı etiketin birden çok dosyası varsa hepsinin parçaları birlikte sayılır.
"""

import statistics
import sys
from pathlib import Path

import turkish_linguistic_features as tlf
from _demo import demo_korpus_yaz

PARCA_BOYUTU = 1500        # gerçek korpus için (spaCy tokenı)
DEMO_PARCA_BOYUTU = 60     # demo metinleri ~120 token
DIL = "tr"
CIKTI_DIZINI = Path("examples/output")
OLCULER = {
    "sent_len_mean": "ortalama",
    "sent_len_median": "medyan",
    "short_sent_ratio": "kısa",
    "long_sent_ratio": "uzun",
}


def main() -> None:
    if len(sys.argv) > 1:
        korpus, parca_boyutu = Path(sys.argv[1]), PARCA_BOYUTU
        if not korpus.is_dir():
            sys.exit(f"Korpus dizini bulunamadı: {korpus}")
    else:
        korpus, parca_boyutu = CIKTI_DIZINI / "demo_korpus", DEMO_PARCA_BOYUTU
        print(f"Korpus verilmedi; demo korpus kullanılıyor: {korpus}\n")
        demo_korpus_yaz(korpus)

    # Yalnız `sentence` grubu: cümle ölçüleri için bütün öznitelikleri
    # hesaplamak gereksiz, grup seçmek süreyi birkaç kat kısaltır.
    satirlar = tlf.analyze_corpus(korpus, lang=DIL, segment_size=parca_boyutu,
                                  groups=["sentence"], warn=False)
    if not satirlar:
        sys.exit(f"Hiç parça çıkmadı; metinler {parca_boyutu} kelimeden kısa olabilir.")

    etiketler: dict[str, list[dict]] = {}
    for satir in satirlar:
        etiketler.setdefault(str(satir["label"]), []).append(satir)

    # Etiket başına parça ortalaması. NaN'lı parça o ölçünün ortalamasına girmez.
    ozet = []
    for etiket, parcalar in etiketler.items():
        kayit = {"label": etiket, "parca": len(parcalar)}
        for anahtar in OLCULER:
            degerler = [float(p[anahtar]) for p in parcalar
                        if float(p[anahtar]) == float(p[anahtar])]
            kayit[anahtar] = round(statistics.mean(degerler), 4) if degerler else float("nan")
        # Uçlar: kısa + uzun cümlelerin payı; yüksekse ritim dalgalı.
        kayit["uclar"] = round(kayit["short_sent_ratio"] + kayit["long_sent_ratio"], 4)
        ozet.append(kayit)
    ozet.sort(key=lambda k: k["uclar"])

    sutunlar = {**OLCULER, "uclar": "uçlar"}
    print(f"{'etiket':<24}{'parça':>6}" + "".join(f"{b:>11}" for b in sutunlar.values()))
    for k in ozet:
        print(f"{k['label']:<24}{k['parca']:>6}"
              + "".join(f"{k[a]:>11.3f}" for a in sutunlar))

    en_duzenli, en_dalgali = ozet[0], ozet[-1]
    print(f"\nEn düzenli ritim : {en_duzenli['label']} (uçlar {en_duzenli['uclar']:.3f})")
    print(f"En dalgalı ritim : {en_dalgali['label']} (uçlar {en_dalgali['uclar']:.3f})")
    print("\nUçlar = kısa + uzun cümlelerin payı: cümle uzunluğunun ne kadar oynadığı.")
    print("Kısa/uzun eşikleri dile göre kalibre edilmiştir (Türkçe 4 / 17 kelime).")

    CIKTI_DIZINI.mkdir(parents=True, exist_ok=True)
    yol = CIKTI_DIZINI / "cumle_ritmi.csv"
    tlf.save_csv(ozet, yol)
    print(f"\nCSV yazıldı: {yol}")


if __name__ == "__main__":
    main()
