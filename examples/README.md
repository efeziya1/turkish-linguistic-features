# Örnek scriptler

Dört çalışan script. Her biri ayrı bir soruya cevap verir.

| Script | Soru | Ayrıntılı anlatım |
|---|---|---|
| `01_hizli_baslangic.py` | Tek metinden sayıları nasıl alırım? | [Öğretici](../docs/tr/baslangic.md) |
| `02_korpus_analizi.py` | Bir klasörü nasıl CSV'ye çeviririm? | [Korpusu CSV'ye çıkar](../docs/tr/nasil/korpus.md) |
| `03_duzenleme_oncesi_sonrasi.py` | Düzenleme neyi değiştirdi? | [İki sürümü karşılaştır](../docs/tr/nasil/karsilastirma.md) |
| `04_matrisi_sakla.py` | Pahalı adımı nasıl bir kez öderim? | [Metni parçalara böl](../docs/tr/nasil/segmentleme.md) |

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

Dördü de temel kurulumla çalışır. `pandas` yalnız `02`'nin son iki bloğunda
kullanılır; kurulu değilse o kısım atlanır.

Çıktılar `examples/output/` altına yazılır ve depoya girmez.

---

**Bütün dokümantasyon → [docs/](../docs/index.md)** (Türkçe ve İngilizce)
