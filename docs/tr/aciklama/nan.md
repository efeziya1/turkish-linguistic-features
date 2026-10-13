# NaN ne demek

## Kısa cevap

`nan`, **"bu metinde bu sayıyı hesaplayamam"** demektir. Hata değildir,
eksik veri işaretidir.

Kütüphane yetersiz veriyle sayı **uydurmaz**. Uydursaydı, tablonuzda
gerçek görünen ama anlamsız bir sütun olurdu ve bunu fark etmenin yolu
olmazdı.

## Ne kadar sık

Üç sözcüklük bir metinde:

```python
kisa = tlf.analyze("Kısa bir tümce.", lang="tr")
nan_olan = [k for k, v in kisa.items() if isinstance(v, float) and v != v]
len(kisa), len(nan_olan)
```

```text
(208, 36)
```

208 öznitelikten **36'sı** `nan`. Örnekler:

```text
['aspect_imp_ratio', 'aspect_perf_ratio', 'aspect_prog_ratio', 'dugast_u',
 'hdd', 'heaps_beta', 'honore_r', 'mattr']
```

Aynı metinde `ttr` yine de sayı döner:

```text
mattr  = nan   (en az 100 sözcük ister)
ttr    = 1.0   (her uzunlukta hesaplanır)
```

## Neden `nan` dönüyor

Üç sebep var.

### 1. Metin çok kısa

Her özniteliğin bir alt sınırı var ve künyede yazılı:

```python
tlf.describe_feature("mattr")["requires"]
```

```text
'at least 100 words (2 x mattr_window)'
```

Buradaki **sözcük** kütüphanenin varsayılan sözcüğüdür
([Kavramlar](kavramlar.md#sozcuk-ve-tumce)). `segment_text`'in `segment_size` değeri de
aynı sözcüğü sayar: 100 sözcüklük parça 100 sözcük isteyen bir ölçüye yeter.

Sınırın altındaysanız `nan` gelir. Sınırların bir kısmı kaynaktan gelir
(`mtld` için "texts as short as 100 tokens can be used"), bir kısmı
matematikten: `mattr` tek pencerede düz TTR'a çöker, yani "hareketli
ortalama" olmaktan çıkar — o yüzden eşik `2 × pencere`dir.

### 2. Gereken yapı yok

`zeyrek_derivational_suffix_ratio` metinde hiç türetme eki bulamazsa paydası sıfır
olur. `parse_depth_mean` tümce ayrıştırılamazsa değer üretemez.
`verb_dist_mean` metinde en az iki fiil yoksa ölçülemez.
Metinde hiç noktalama işareti yoksa `punct_…_ratio` öznitelikleri hesaplanamaz.

### 3. İsteğe bağlı bir paket kurulu değil

`wordfreq` kurulu değilse `wordfreq_mean` ve `wordfreq_rare_ratio` `nan`
döner ve kütüphane bir `MissingDependencyWarning` basar.

```python
oz = tlf.analyze(metin, lang="tr", warn=False)
```

`warn=False` yalnız uyarıyı susturur; öznitelik yine `nan` kalır. Aynı bayrak
`ParagraphStructureWarning`'ı da susturur.

## `nan` dönmeyen ama yanıltan durum: paragraf

Paragraf sınırı boş satırla bulunur. Metinde boş satır yoksa metnin tamamı tek
paragraf sayılır ve `para_len_mean` bütün metnin sözcük sayısına eşitlenir: değer
`nan` olmaz ama paragraf hakkında bir şey söylemez. Ayrıntı:
[sınırlılıklar §8](sinirliliklar.md).

## Neden `None` değil de `nan`

`nan` bir `float`'tır. Yani dönen sözlüğün bütün değerleri aynı tiptedir ve
tablo doğrudan `pandas`, `numpy`, R ya da CSV'ye geçer. `None` koysaydık
sütun tipi `object` olur, aritmetik bozulur, CSV'de boş hücre ile gerçek
sıfırı ayırt etmek zorlaşırdı.
