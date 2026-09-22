"""Matrisi sakla — pahalı adımı bir kez öde.

Öznitelik çıkarımı kütüphanenin en pahalı adımıdır (spaCy + Zeyrek). Çıkarımı
bir döngünün içine koyarsanız korpus her turda yeniden işlenir. Kalıp şudur:
**çıkar → kaydet → tekrar tekrar yükle.**

🔴 **Neden önbelleğe almak güvenli?** Çıkarım metin başına bağımsızdır: bir
metnin sayıları yalnız o metinden hesaplanır, eğitim kümesinden hiçbir
istatistik öğrenilmez. Yani diskteki matris, aynı sürüm ve aynı parametrelerle
yeniden çalıştırıldığında çıkacak olanın aynısıdır — sızıntı riski yoktur.
(Değişen sürüm ya da değişen ``FeatureParams`` matrisi geçersiz kılar; bu
yüzden sürüm de yanına yazılıyor.)

🔴 **Sütun adları matrisin yanında saklanır.** Adları olmayan bir matris
anlamsızdır: ``analyze()`` sözlük döndürür, ``.npy`` ise adsız bir sayı
dizisi. İkisini ayrı ayrı kaydetmezseniz hangi sütunun hangi öznitelik
olduğunu geri kurtaramazsınız.

numpy zorunlu bağımlılıktır (K1), bu blok koşulsuz çalışır.

Çalıştırma::

    python examples/04_matrisi_sakla.py
"""

import json
from pathlib import Path

import numpy as np

import turkish_linguistic_features as tlf

# Ayarlar en üstte, tek yerde.
DIL = "tr"
CIKTI_DIZINI = Path("examples/output")
MATRIS_YOLU = CIKTI_DIZINI / "matris.npy"
SUTUN_YOLU = CIKTI_DIZINI / "matris_sutunlari.json"

METINLER = [
    "Sabah erken kalktı, pencereyi açtı ve sokağın hâlâ boş olduğunu gördü. "
    "Çayını tazeledi, defterini masaya koydu ve yazmaya başladı.",
    "Tokenizasyon bir metni işlenebilir birimlere ayırır. Birimler çoğunlukla "
    "kelimelerdir; noktalama işaretleri ve sayılar da ayrı birim sayılır.",
    "Parçalama uzun metni eşit bölümlere ayırır. Sözcüksel zenginlik ölçütleri "
    "uzunluğa duyarlı olduğu için bölümlerin yakın uzunlukta olması beklenir.",
]


def main() -> None:
    CIKTI_DIZINI.mkdir(parents=True, exist_ok=True)

    # 1. Pahalı adım — yalnız bir kez.
    print(f"{len(METINLER)} metin çözümleniyor (pahalı adım)...")
    kayitlar = []
    for i, metin in enumerate(METINLER, 1):
        print(f"  [{i}/{len(METINLER)}]")
        kayitlar.append(tlf.analyze(metin, lang=DIL))

    # 2. Sözlükten matrise. Anahtar sırası bütün kayıtlarda aynı (analyze()
    #    aynı şemayı üretir), ama sırayı varsaymak yerine ilk kayıttan
    #    sabitleyip diğerlerini ona göre diziyoruz.
    sutunlar = list(kayitlar[0])
    matris = np.array([[kayit[a] for a in sutunlar] for kayit in kayitlar],
                      dtype=float)

    # 3. İki dosya: sayılar ve adlar. Biri olmadan diğeri işe yaramaz.
    np.save(MATRIS_YOLU, matris)
    SUTUN_YOLU.write_text(
        json.dumps({"version": tlf.__version__, "lang": DIL,
                    "columns": sutunlar}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nKaydedildi:\n  {MATRIS_YOLU}\n  {SUTUN_YOLU}")

    # 4. Geri yükle — bundan sonraki her koşu buradan başlayabilir.
    yuklenen = np.load(MATRIS_YOLU)
    ust_veri = json.loads(SUTUN_YOLU.read_text(encoding="utf-8"))
    yuklenen_sutunlar = ust_veri["columns"]

    print(f"\nGeri yüklendi: şekil {yuklenen.shape} "
          f"({yuklenen.shape[0]} metin x {yuklenen.shape[1]} öznitelik)")
    print(f"Üretildiği sürüm: {ust_veri['version']}, dil: {ust_veri['lang']}")
    print(f"İlk 5 sütun adı: {yuklenen_sutunlar[:5]}")
    assert yuklenen.shape[1] == len(yuklenen_sutunlar), \
        "Matris sütun sayısı ile ad listesi uyuşmuyor"


if __name__ == "__main__":
    main()
