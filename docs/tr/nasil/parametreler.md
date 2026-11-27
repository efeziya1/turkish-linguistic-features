# Eşikleri değiştir

Pencere boyları, eşikler (İng. *thresholds*) ve örneklem sayıları `FeatureParams` içinde
durur. Bunlara parametre (İng. *parameter*) denir; araçta 21 parametre var ve hepsi
değiştirilebilir.

## Kullanım

```python
import turkish_linguistic_features as tlf

metin = ("Kapı açıldı. Yaşlı adam yavaşça içeri girdi ve masaya oturdu. Herkes susmuş, "
         "onun ne söyleyeceğini merakla beklerken dışarıda yağmur bütün gece boyunca "
         "durmadan yağmaya devam etti ve sokaklar sular altında kaldı.")

p = tlf.FeatureParams(short_sent_threshold=10, long_sent_threshold=25)
oz = tlf.analyze(metin, lang="tr", params=p)
print(oz["short_sent_ratio"], oz["long_sent_ratio"])
```

```text
0.666667 0.0
```

Metnin üç tümcesi 2, 8 ve 21 sözcüktür. Varsayılan eşiklerle (4 ve 17) sonuç
`0.333333 0.333333`: birer kısa ve uzun tümce vardır. Eşikler 10 ve 25 olunca iki tümce kısa
sayılır, uzun tümce kalmaz.

Verilmeyen alanlar varsayılan değerinde kalır. Tümce eşiklerinin varsayılanı her dil için
ayrı ölçülmüştür — [aşağıda](#tumce-esikleri-dile-gore-uygulanr).

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
| `heaps_points` | 20 | `heaps_beta` |
| `brunet_w_a` | 0.172 | `brunet_w` |
| `brunet_w_b` | 20 | `brunet_w` |
| `verb_suffix_window` | 10 | `akana_verb_suffix_diversity` |
| `verb_suffix_num_samples` | 100 | `akana_verb_suffix_diversity` |
| `verb_suffix_random_seed` | 42 | `akana_verb_suffix_diversity` |
| `kalyoncu_ttr_window` | 500 | `kalyoncu_ttr`, `kalyoncu_k1`–`kalyoncu_k3` |
| `short_sent_threshold` | TR **4** · EN **8** | `short_sent_ratio` |
| `long_sent_threshold` | TR **17** · EN **32** | `long_sent_ratio` |
| `max_parse_depth` | 20 | `parse_depth_mean` |

`akana_verb_suffix_diversity`, metnin eylemlerinden rastgele 10'ar eylem seçip her seçimde
kaç farklı ek görüldüğünü sayar ve bunun ortalamasını verir; üç `verb_suffix_*` alanı bu
seçimin boyunu, sayısını ve rastgeleliğin tohumunu belirler.

## Tümce eşikleri dile göre uygulanır

Tablodaki iki alanın varsayılanı tek bir sayı değil, dile göre değişir. Nedeni şu: Türkçe
tümceler İngilizce tümcelerden kısadır, aynı eşik iki dile uymaz. Türkçenin 17 sözcüklük uzun tümce
eşiği İngilizce köşe yazılarında tümcelerin %54'ünü "uzun" sayar; kendi dilinde bu pay
%15'tir.

| Dil | short | long |
|---|---|---|
| Türkçe | **4** | **17** |
| İngilizce | **8** | **32** |

Değerler gazete köşe yazılarında, varsayılan tümce kuralı ve varsayılan
sözcükle ölçülen tümce uzunluğu dağılımının 15. ve 85. yüzdeliğinden (İng. *percentile*)
türetildi (TR: 198.225 tümce; EN: 52.745 tümce). Yöntem: [Eşik kalibrasyonu](../../esik-kalibrasyonu.md).

## Hangi öznitelik hangi parametreden etkilenir

```python
tlf.describe_feature("mattr")["params"]
```

```text
('mattr_window',)
```

Boş bir değer (`()`) dönerse o öznitelik hiçbir parametreye bağlı değildir.
