# Eşikleri değiştir

Pencere boyları, eşikler ve örneklem sayıları `FeatureParams` içinde durur.

## Kullanım

```python
import turkish_linguistic_features as tlf
from turkish_linguistic_features import FeatureParams

# metin: öğreticideki üç cümlelik örnek (7, 7 ve 16 kelime)
p = FeatureParams(short_sent_threshold=3, long_sent_threshold=12)
oz = tlf.analyze(metin, lang="tr", params=p)
```

`FeatureParams` bir dataclass'tır; vermediğiniz alanlar varsayılanda kalır.
Cümle eşiklerinin varsayılanı sabit bir sayı değil, dilin kalibre edilmiş
değeridir — [aşağıda](#cumle-esikleri-dile-gore-cozumlenir).

Çıktı (`short_sent_ratio`, `long_sent_ratio`):

```text
varsayılan (TR 4/18): short=0.0      long=0.0
elle (3/12)         : short=0.0      long=0.333333
```

Aynı metin, farklı eşik, farklı sayı. Üç cümlenin biri 12 kelimeyi geçiyor;
18'i geçen yok.

## Bütün alanlar

| Alan | Varsayılan | Etkilediği |
|---|---|---|
| `mattr_window` | 50 | `mattr` |
| `mtld_threshold` | 0.72 | `mtld` |
| `mtld_min_tokens` | 100 | `mtld` |
| `hdd_sample_size` | 42 | `hdd` |
| `msttr_segment_size` | 100 | `msttr` |
| `vocd_sample_min` | 35 | `vocd_d` |
| `vocd_sample_max` | 50 | `vocd_d` |
| `vocd_num_samples` | 100 | `vocd_d` |
| `vocd_num_runs` | 3 | `vocd_d` |
| `vocd_min_tokens` | 50 | `vocd_d` |
| `vocd_random_seed` | 42 | `vocd_d` |
| `heaps_min_tokens` | 300 | `heaps_beta` |
| `heaps_step` | 50 | `heaps_beta` |
| `ttr_slope_chunk_size` | 50 | `ttr_moving_slope` |
| `brunet_w_a` | 0.172 | `brunet_w` |
| `verb_suffix_window` | 50 | `verb_suffix_diversity` |
| `short_sent_threshold` | TR **4** · EN **9** | `short_sent_ratio` |
| `long_sent_threshold` | TR **18** · EN **33** | `long_sent_ratio` |
| `max_parse_depth` | 20 | `parse_depth_mean` |

## Cümle eşikleri dile göre çözümlenir

Tablodaki tek sayı olmayan iki alan bunlar. Sebep tipolojik: Türkçe cümleler
İngilizce cümlelerden kısa, aynı eşik iki dile uymuyor.

| Dil | short | long |
|---|---|---|
| Türkçe | **4** | **18** |
| İngilizce | **7** | **39** |

Değerler roman korpuslarında cümle uzunluğu dağılımının 15. ve 85.
yüzdeliğinden türetildi (TR: 15 yazar / 1 089 841 cümle; EN: 10 yazar /
341 892 cümle). Yöntem: [Eşik kalibrasyonu](../../esik-kalibrasyonu.md).

**Çözümleme alan alandır.** Verdiğiniz alan sizin sayınızı, vermediğiniz alan
dilin kalibre edilmiş değerini kullanır. Yani ilgisiz bir alanı değiştirmek
cümle eşiklerini bozmaz:

```python
metin = ("Kapı açıldı. Sabah erkenden yola çıktık. Köyün girişindeki "
         "yaşlı çınarın altında oturan adam, uzun yıllar önce bu yollardan "
         "geçen kervanları, pazar günlerini ve kaybolan komşularını anlattı.")
p = FeatureParams(mattr_window=100)          # eşiklere dokunulmadı
oz = tlf.analyze(metin, lang="tr", params=p)  # eşikler hâlâ TR 4/18
```

Çıktı — cümlelerin kelime sayıları 2, 4 ve 20:

```text
params=None                       short=0.333333   long=0.333333
FeatureParams(mattr_window=100)   short=0.333333   long=0.333333
```

İki satır aynı, çünkü `mattr_window` cümle eşikleriyle ilgisiz.

## Hangi öznitelik hangi parametreden etkilenir

```python
tlf.describe_feature("mattr")["params"]
```

```text
('mattr_window',)
```

Boş demet `()` dönerse o öznitelik hiçbir parametreye bağlı değildir.

## `mattr_window` neden 50

Covington & McFall (2010) üslup analizi için **500** öneriyor. Kütüphanenin
varsayılanı 50 — onda biri. Neden:

- Pencere boyu aynı zamanda **alt sınırdır**: `mattr` en az `2 × window`
  kelime ister. 500 olsaydı 1000 kelimeden kısa hiçbir metin sayı
  üretemezdi.

Künye bu ayrımı açıkça yazar. 500 istiyorsanız:

```python
p = FeatureParams(mattr_window=500)
```

ve metinlerinizin en az 1000 kelime olduğundan emin olun. Cümle eşiklerini
elle taşımanız gerekmiyor; kalibre edilmiş değerlerinde kalırlar.
