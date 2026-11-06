# Eşikleri değiştir

Pencere boyları, eşikler (İng. *thresholds*) ve örneklem sayıları `FeatureParams` içinde
durur. Bunlara parametre (İng. *parameter*) denir; araçta 21 parametre var ve hepsini
değiştirebilirsiniz.

## Kullanım

```python
import turkish_linguistic_features as tlf

# metin: öğreticideki üç tümcelik örnek (5, 13 ve 7 sözcük)
p = tlf.FeatureParams(short_sent_threshold=3, long_sent_threshold=12)
oz = tlf.analyze(metin, lang="tr", params=p)
```

`FeatureParams` bir dataclass'tır; vermediğiniz alanlar varsayılanda kalır.
Tümce eşiklerinin varsayılanı sabit bir sayı değil, dilin kalibre edilmiş
değeridir — [aşağıda](#tumce-esikleri-dile-gore-uygulanr).

Çıktı (`short_sent_ratio`, `long_sent_ratio`):

```text
varsayılan (TR 4/17): short=0.0      long=0.0
elle (3/12)         : short=0.0      long=0.333333
```

Aynı metin, farklı eşik, farklı sayı. Üç tümcenin biri 12 sözcüğü geçiyor;
17'yi geçen yok.

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
| `verb_suffix_window` | 10 | `zeyrek_verb_suffix_diversity` |
| `verb_suffix_num_samples` | 100 | `zeyrek_verb_suffix_diversity` |
| `verb_suffix_random_seed` | 42 | `zeyrek_verb_suffix_diversity` |
| `kalyoncu_ttr_window` | 500 | `kalyoncu_ttr`, `kalyoncu_k1`–`kalyoncu_k3` |
| `short_sent_threshold` | TR **4** · EN **8** | `short_sent_ratio` |
| `long_sent_threshold` | TR **17** · EN **32** | `long_sent_ratio` |
| `max_parse_depth` | 20 | `parse_depth_mean` |

`zeyrek_verb_suffix_diversity` metnin eylemlerinden 100 rastgele örneklem çeker; her örneklem
10 eylemdir, örneklem içinde eylem tekrarlanmaz. Sonuç, örneklemlerde görünen farklı ek
türü sayısının ortalamasıdır (Brezina ve Pallotti 2019, s.107-108: MC10). Araç yalnız
örneklem içi çeşitliliği ölçer; MC10'un örneklemler arası bileşeni yoktur, ölçü MC10a'ya
yakındır.

## Kaynaktan alınan sabitler Türkçede sınanmadı

Tablodaki bazı değerler kaynağın kendi sabitidir (İng. *constant*): MTLD'nin 0,72 eşiği
(McCarthy ve Jarvis 2010, s.385), HD-D'nin 42 sözcüklük örneklemi (s.383) ve Brunet
ölçüsünün 0,172 değeri (Brunet 1978, s.49). Bu sayılar İngilizce ya da Fransızca metinlerle
belirlenmiştir ve Türkçe metinlerle sınanmamıştır. Türkçeye aktarılamayacakları
söylenemez, ama aktarılabildikleri de gösterilmemiştir.

Okunabilirlik formüllerinde bu sorunun nasıl çözüldüğü bilinir: Ateşman (1997, s.73–74)
Flesch formülünü Türkçeye uygularken yapısını korumuş, katsayılarını Türkçe metinlerden
yeniden hesaplamıştır. Araçta da tümce eşikleri iki dil için ayrı ölçülmüştür (aşağıda).
Kendi derleminizde bir sabiti denemek isterseniz yukarıdaki alanlarla değiştirebilirsiniz.

## Tümce eşikleri dile göre uygulanır

Tablodaki tek sayı olmayan iki alan bunlar. Sebep tipolojik: Türkçe tümceler
İngilizce tümcelerden kısa, aynı eşik iki dile uymuyor. Türkçenin 17 sözcüklük uzun tümce
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

Boş demet `()` dönerse o öznitelik hiçbir parametreye bağlı değildir.

## `mattr_window` neden 50

Covington & McFall (2010) üslup analizi için **500** öneriyor. Aracın
varsayılanı 50 — onda biri, çünkü pencere boyu aynı zamanda **alt sınırdır**:
`mattr` en az `2 × window` sözcük ister. 500 olsaydı 1000 sözcükten kısa hiçbir
metin sayı üretemezdi.

Künye bu ayrımı açıkça yazar. 500 istiyorsanız:

```python
p = tlf.FeatureParams(mattr_window=500)
```
