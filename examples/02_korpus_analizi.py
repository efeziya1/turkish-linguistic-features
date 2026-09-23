"""Korpus analizi — korpustan CSV'ye, uçtan uca.

Zincir: ``analyze_corpus()`` → ``save_csv()``. İki çağrı.

Kendi korpusunuzu vermek için dizini argüman olarak geçin::

    python examples/02_korpus_analizi.py korpus/

Argüman verilmezse depoda korpus olmadığı için ``examples/output/`` altına
küçük bir **demo korpus** yazılır ve o çözümlenir::

    python examples/02_korpus_analizi.py

Beklenen düzen: ``korpus/Etiket_Başlık.txt`` (ya da ``korpus/Etiket/*.txt``,
ya da tek bir ``korpus.csv``).

pandas **opsiyonel**: kurulu değilse script yine baştan sona çalışır, yalnız
sondaki iki blok atlanır.
"""

import math
import statistics
import sys
from pathlib import Path

import turkish_linguistic_features as tlf

# Ayarlar en üstte, tek yerde.
PARCA_BOYUTU = 1000        # gerçek korpus için tipik değer (kelime)
DEMO_PARCA_BOYUTU = 60     # demo metinleri kısa; 1000 ile hiç parça çıkmazdı
DIL = "tr"
CIKTI_DIZINI = Path("examples/output")
KORELASYON_ESIGI = 0.95
EN_COK_DEGISEN = 10

# Demo korpus: iki etiket, ikişer dosya. İçerik bu depo için yazıldı.
DEMO_METINLER = {
    "Anlatı_sabah": (
        "Sabah erken kalktı. Pencereyi açtığında sokak henüz boştu ve uzaktan "
        "bir kamyonun sesi geliyordu. Çayını tazeledi, defterini masaya koydu "
        "ve dün gece yarım bıraktığı cümleyi yeniden okudu. Cümle ona artık "
        "yabancı geliyordu; sanki başka biri yazmıştı. Kalemi eline aldı, "
        "birkaç kelimeyi çizdi, yerine daha kısa olanları yazdı. Dışarıda "
        "yağmur başlamıştı. Camın kenarında biriken damlaları izledi ve "
        "yazmaya devam etti. Öğleye doğru defteri kapattı, paltosunu giydi ve "
        "kapıyı arkasından yavaşça çekti. Merdivenlerde komşusuyla karşılaştı, "
        "selamlaştılar, hava üzerine iki cümle kurdular. Sokağa çıktığında "
        "yağmur dinmiş, kaldırımlar ıslak kalmıştı."
    ),
    "Anlatı_akşam": (
        "Akşam olduğunda ışıkları yakmadı. Karanlık odada oturdu ve caddeden "
        "gelen sesleri dinledi. Bir araba korna çaldı, ardından biri güldü. "
        "Masanın üstünde duran defteri eline aldı ama açmadı. Ne yazacağını "
        "biliyordu, yalnız başlamak istemiyordu. Mutfağa gitti, bir bardak su "
        "içti ve geri döndü. Saat geç olmuştu. Sonunda lambayı yaktı, defteri "
        "açtı ve sabah bıraktığı yerden devam etti. Yazdıkça cümleler "
        "kısalıyordu. Gece yarısına doğru son noktayı koydu, defteri kapattı "
        "ve uyumaya gitti. Ertesi sabah aynı cümleyi bir kez daha okuyacaktı."
    ),
    "Bilgi_tokenizasyon": (
        "Tokenizasyon, bir metni işlenebilir birimlere ayırma işlemidir. "
        "Birimler çoğunlukla kelimelerdir, ancak noktalama işaretleri ve "
        "sayılar da ayrı birim sayılır. Ayırma kuralları dile göre değişir: "
        "Türkçede kesme işareti ekleri ayırırken, İngilizcede kısaltmaların "
        "içinde geçebilir. Bu nedenle dilden bağımsız bir kural kümesi "
        "yeterli olmaz. Ayrıca aynı metnin iki farklı yöntemle sayılması "
        "farklı birim sayıları verir; uzunluğa duyarlı ölçütler bu farktan "
        "doğrudan etkilenir. Ölçümlerin karşılaştırılabilir olması için "
        "tokenizasyon yönteminin baştan sabitlenmesi ve raporlanması gerekir."
    ),
    "Bilgi_parcalama": (
        "Parçalama, uzun bir metni eşit büyüklükte bölümlere ayırma işlemidir. "
        "Sözcüksel zenginlik ölçütlerinin çoğu metin uzunluğuna duyarlıdır, "
        "yani aynı metnin uzun ve kısa bölümleri farklı değerler üretir. "
        "Bu yüzden karşılaştırılacak bölümlerin yakın uzunlukta olması "
        "beklenir. Son bölüm çoğu zaman eksik kalır; eşiğin altındaki artığı "
        "atmak, ölçülen farkın metinden mi yoksa bölüm uzunluğundan mı "
        "geldiği sorusunu ortadan kaldırır. Bölüm boyu seçimi yöntem "
        "bölümünde belirtilmesi gereken bir karardır."
    ),
}


def demo_korpus_yaz(dizin: Path) -> None:
    """Depoda korpus yok; küçük bir demo korpusu diske yazar."""
    dizin.mkdir(parents=True, exist_ok=True)
    for ad, metin in DEMO_METINLER.items():
        (dizin / f"{ad}.txt").write_text(metin, encoding="utf-8")


def main() -> None:
    if len(sys.argv) > 1:
        korpus_dizini, parca_boyutu = Path(sys.argv[1]), PARCA_BOYUTU
        if not korpus_dizini.exists():
            print(f"Korpus bulunamadı: {korpus_dizini}")
            print("Beklenen düzen: korpus/Etiket_Başlık.txt")
            sys.exit(1)
    else:
        korpus_dizini, parca_boyutu = CIKTI_DIZINI / "demo_korpus", DEMO_PARCA_BOYUTU
        print(f"Korpus verilmedi; demo korpus yazılıyor: {korpus_dizini}")
        print("Kendi korpusunuz için: python examples/02_korpus_analizi.py korpus/\n")
        demo_korpus_yaz(korpus_dizini)

    # 1. Oku, parçala, her parçayı analiz et — tek çağrı.
    #    show_progress pahalı adımı görünür kılıyor: parça başına bir
    #    analyze() çağrısı var, büyük korpusta dakikalar sürer.
    satirlar = tlf.analyze_corpus(korpus_dizini, lang=DIL,
                                  segment_size=parca_boyutu,
                                  show_progress=True)
    if not satirlar:
        print(f"Hiç parça çıkmadı. Metinler {parca_boyutu} kelimeden kısa olabilir;")
        print("PARCA_BOYUTU'nu küçültün ya da min_fill'i düşürün.")
        sys.exit(1)
    print(f"{len(satirlar)} parça analiz edildi "
          f"({len({s['source'] for s in satirlar})} kaynak).")

    # 2. Ham değerleri CSV'ye yaz — ölçeklenmemiş, olduğu gibi.
    CIKTI_DIZINI.mkdir(parents=True, exist_ok=True)
    csv_yolu = CIKTI_DIZINI / "korpus_oznitelikleri.csv"
    tlf.save_csv(satirlar, csv_yolu)
    print(f"\nCSV yazıldı: {csv_yolu} ({len(satirlar)} satır, "
          f"{len(satirlar[0])} sütun)")

    # 3. Parçalar arasında en çok değişen öznitelikler.
    #    Yalnız ``ratio_0_1`` ölçeğindekiler karşılaştırılıyor: hepsi [0, 1]
    #    aralığında olduğu için standart sapmaları aynı birimde. Ölçekleri
    #    karışık anahtarları yan yana sıralamak büyük sayılı olanı öne atardı.
    #    Ölçülemeyen öznitelikler NaN döner (eksik opsiyonel paket, metinde
    #    hiç geçmeyen etiket); onlar sıralamaya girmez.
    oznitelik_adlari = [a for a in satirlar[0]
                        if a not in ("label", "source", "segment_id")]
    sutunlar = {a: [float(s[a]) for s in satirlar] for a in oznitelik_adlari}
    oranlar = [a for a, v in sutunlar.items()
               if tlf.describe_feature(a)["scale"] == "ratio_0_1"
               and all(math.isfinite(x) for x in v)]
    sapmalar = {a: statistics.pstdev(sutunlar[a]) for a in oranlar}
    print(f"\n-- Parçalar arasında en çok değişen {EN_COK_DEGISEN} oran "
          + "-" * 12)
    for anahtar, sapma in sorted(sapmalar.items(),
                                 key=lambda p: p[1], reverse=True)[:EN_COK_DEGISEN]:
        print(f"{anahtar:<30} sd={sapma:>8.4f}")

    # 4. Buradan sonrası pandas gerektirir — opsiyonel bağımlılık.
    try:
        import pandas as pd
    except ImportError:
        print("\n(pandas kurulu değil; sabit sütun ve korelasyon blokları "
              "atlandı.)")
        print("Kurmak için: pip install pandas")
        return

    df = pd.DataFrame(satirlar).set_index(["label", "source", "segment_id"])

    # 5a. Sabit sütunlar: korpusta hiç değişmeyen öznitelik ayırt edici değil.
    degisenler = df.loc[:, df.nunique() > 1]
    print(f"\nSabit sütunlar elendi: {df.shape[1]} -> {degisenler.shape[1]}")

    # 5b. Birbirini tekrarlayan öznitelik çiftleri.
    #    Az sayıda parçayla korelasyon katsayısı güvenilir değildir; bu blok
    #    kalıbı gösterir, demo korpusun sayılarını yorumlamak için değil.
    korelasyon = degisenler.corr().abs()
    ciftler = [(a, b, korelasyon.loc[a, b])
               for i, a in enumerate(korelasyon.columns)
               for b in korelasyon.columns[i + 1:]
               if korelasyon.loc[a, b] >= KORELASYON_ESIGI]
    print(f"|r| >= {KORELASYON_ESIGI} olan çift sayısı: {len(ciftler)}")
    for a, b, r in sorted(ciftler, key=lambda p: p[2], reverse=True)[:10]:
        print(f"  {a:<28} {b:<28} r={r:.3f}")


if __name__ == "__main__":
    main()
