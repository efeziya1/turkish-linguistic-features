# Örnek scriptler

Dokuz çalışan script. Her biri ayrı bir soruya cevap verir.

| Script | Soru | Ayrıntılı anlatım |
|---|---|---|
| `01_hizli_baslangic.py` | Tek metinden sayıları nasıl alırım? | [Öğretici](../docs/tr/baslangic.md) |
| `02_korpus_analizi.py` | Bir klasörü nasıl CSV'ye çeviririm? | [Korpusu CSV'ye çıkar](../docs/tr/nasil/korpus.md) |
| `03_duzenleme_oncesi_sonrasi.py` | Düzenleme neyi değiştirdi? | [İki sürümü karşılaştır](../docs/tr/nasil/karsilastirma.md) |
| `04_matrisi_sakla.py` | Pahalı adımı nasıl bir kez öderim? | [Metni parçalara böl](../docs/tr/nasil/segmentleme.md) |
| `05_cumle_ritmi.py` | Etiketler cümle uzunluğunun dağılımıyla ayrışıyor mu? | [Korpusu CSV'ye çıkar](../docs/tr/nasil/korpus.md) |
| `06_esik_kalibrasyonu.py` | Kısa/uzun cümle eşiğini kendi korpusumdan nasıl türetirim? | [Eşik kalibrasyonu](../docs/esik-kalibrasyonu.md) |
| `07_nan_haritasi.py` | Metnim ne kadar kısa olabilir? | [NaN ne demek](../docs/tr/aciklama/nan.md) |
| `08_tekrarlanabilirlik.py` | Aynı metin yarın da aynı sayıları verir mi? | [Eşikleri değiştir](../docs/tr/nasil/parametreler.md) |
| `09_uzunluk_duyarliligi.py` | Hangi zenginlik ölçüsü metin boyundan bağımsız? | [Sınırlılıklar](../docs/tr/aciklama/sinirliliklar.md) |

## Çalıştırma

```bash
pip install -e .
python examples/01_hizli_baslangic.py
```

Kurmadan, depo kökünden:

```bash
# Windows PowerShell
$env:PYTHONPATH="."; python examples/01_hizli_baslangic.py
# Linux / macOS
PYTHONPATH=. python examples/01_hizli_baslangic.py
```

Türkçe için `tr_core_news_md` kurulu olmalı — kurulum komutu depo kökündeki
[README](../README.md)'de. Model yoksa `analyze()` kurulum komutunu içeren bir
`ModelNotFoundError` verir.

Hepsi temel kurulumla çalışır. `pandas` yalnız `02`'nin son iki bloğunda
kullanılır; kurulu değilse o kısım atlanır.

`05`–`09` kendi korpusunuzu ya da metninizi argüman olarak alır
(`python examples/05_cumle_ritmi.py korpus/`, `python examples/07_nan_haritasi.py metin.txt`).
Argüman verilmezse `_demo.py`'deki küçük demo metinler kullanılır; bunlar
script'in nasıl çalıştığını gösterir, sayılarını yorumlamak için değildir.

Çıktılar `examples/output/` altına yazılır ve depoya girmez.

---

**Bütün dokümantasyon → [docs/](../docs/index.md)** (Türkçe ve İngilizce)
