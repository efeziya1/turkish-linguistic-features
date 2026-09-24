# Eşikleri değiştir

Pencere boyları, eşikler ve örneklem sayıları `FeatureParams` içinde durur.

## Kullanım

```python
import turkish_linguistic_features as tlf
from turkish_linguistic_features import FeatureParams

p = FeatureParams(short_sent_threshold=3, long_sent_threshold=12)
oz = tlf.analyze(metin, lang="tr", params=p)
```

`FeatureParams` bir dataclass'tır; vermediğiniz alanlar varsayılanda kalır.

Ölçüm:

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
| `short_sent_threshold` | 5 | `short_sent_ratio` |
| `long_sent_threshold` | 30 | `long_sent_ratio` |
| `max_parse_depth` | 20 | `parse_depth_mean` |

## ⚠️ Cümle eşiklerinde önemli bir ayrıntı

Tabloda `short_sent_threshold=5` ve `long_sent_threshold=30` yazıyor, **ama
bu değerler kullanılmıyor.**

`params` vermediğinizde kütüphane **dile özel** kalibre edilmiş değerleri
kullanır:

| Dil | short | long |
|---|---|---|
| Türkçe | **4** | **18** |
| İngilizce | **7** | **39** |

Bunlar roman korpuslarında cümle uzunluğu dağılımının 15. ve 85.
yüzdeliğinden türetildi (TR: 15 yazar / 1 089 841 cümle; EN: 10 yazar /
341 892 cümle). Yöntem: [Eşik kalibrasyonu](../../esik-kalibrasyonu.md).

Dataclass'ın kendi varsayılanı olan 5/30 **ulaşılamaz bir yedektir** —
yalnız tanınmayan bir dil verilseydi devreye girerdi, ki `lang` zaten
yalnız `"tr"` ve `"en"` alıyor.

!!! danger "`params` verirseniz kalibrasyonu kaybedersiniz"

    `FeatureParams(mattr_window=100)` yazarsanız `short_sent_threshold` de
    **5**'e döner, 4'e değil. Dile özel çözümleme yalnız `params=None`
    iken çalışır.

    Yalnız bir alanı değiştirmek istiyorsanız kalibre edilmiş değerleri
    elle taşıyın:

    ```python
    p = FeatureParams(mattr_window=100,
                      short_sent_threshold=4, long_sent_threshold=18)
    ```

## Hangi öznitelik hangi parametreden etkilenir

```python
tlf.describe_feature("mattr")["params"]
```

```text
['mattr_window']
```

Boş liste dönerse o öznitelik hiçbir parametreye bağlı değildir.

## `mattr_window` neden 50

Covington & McFall (2010) üslup analizi için **500** öneriyor. Kütüphanenin
varsayılanı 50 — onda biri. Neden:

- 50, dil öğrenimi yazınının yerleşik değeri (MSTTR, MTTRSS çalışmalarında
  `n` genelde 50).
- Pencere boyu aynı zamanda **alt sınırdır**: `mattr` en az `2 × window`
  kelime ister. 500 olsaydı 1000 kelimeden kısa hiçbir metin sayı
  üretemezdi.
- Ölçüldü: 15 Türkçe romanda w=50 uzunluk değişimine %0,52 duyarlı,
  w=500 %1,26. Ayırt edicilik sinyal/gürültü oranı pencere boyları
  arasında düz (~1,2).

Künye bu ayrımı açıkça yazar. 500 istiyorsanız:

```python
p = FeatureParams(mattr_window=500,
                  short_sent_threshold=4, long_sent_threshold=18)
```

ve metinlerinizin en az 1000 kelime olduğundan emin olun.
