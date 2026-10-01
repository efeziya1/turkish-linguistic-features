# NaN ne demek

## Kısa cevap

`nan`, **"bu metinde bu sayıyı hesaplayamam"** demektir. Hata değildir,
eksik veri işaretidir.

Kütüphane yetersiz veriyle sayı **uydurmaz**. Uydursaydı, tablonuzda
gerçek görünen ama anlamsız bir sütun olurdu ve bunu fark etmenin yolu
olmazdı.

## Ne kadar sık

Üç kelimelik bir metinde:

```python
kisa = tlf.analyze("Kısa bir cümle.", lang="tr")
nan_olan = [k for k, v in kisa.items() if isinstance(v, float) and v != v]
len(kisa), len(nan_olan)
```

```text
(208, 46)
```

208 öznitelikten **46'sı** `nan`. Örnekler:

```text
['causative_suffix_ratio', 'conditional_suffix_ratio',
 'derivational_suffix_ratio', 'dugast_u', 'entropy_std', 'hdd',
 'heaps_beta', 'mattr']
```

Aynı metinde `ttr` yine de sayı döner:

```text
mattr  = nan   (en az 100 kelime ister)
ttr    = 1.0   (her uzunlukta hesaplanır)
```

## Neden `nan` dönüyor

Dört sebep var.

### 1. Metin çok kısa

Her özniteliğin bir alt sınırı var ve künyede yazılı:

```python
tlf.describe_feature("mattr")["requires"]
```

```text
'at least 100 words (2 x mattr_window)'
```

Buradaki **kelime**, noktalama ya da sembol olmayan tokendır; sayılar kelime
sayılır. `segment_text`'in `size` değeri ise noktalamayı da sayar: 100 tokenlık
parça ~83 kelime eder ve 100 kelime isteyen bir ölçüye yetmeyebilir.

Sınırın altındaysanız `nan` gelir. Sınırların bir kısmı kaynaktan gelir
(`mtld` için "texts as short as 100 tokens can be used"), bir kısmı
matematikten: `mattr` tek pencerede düz TTR'a çöker, yani "hareketli
ortalama" olmaktan çıkar — o yüzden eşik `2 × pencere`dir.

### 2. Gereken yapı yok

`derivational_suffix_ratio` metinde hiç türetme eki bulamazsa paydası sıfır
olur. `parse_depth_mean` cümle ayrıştırılamazsa değer üretemez.
`hapax_ratio` tek kelimelik metinde anlamsızdır.

### 3. Girdide paragraf sınırı yok

`para_len_cv` ve `sents_per_para_cv` en az **iki** paragraf ister —
değişkenlik tek değerden ölçülmez. Paragraf sınırı boş satırla bulunur, tek
satır sonu saymaz. Metninizde boş satır yoksa metnin tamamı tek paragraf
sayılır, bu iki öznitelik `nan` döner ve `para_len_mean` bütün metnin kelime
sayısına eşitlenir.

1000 kelimeyi geçen metinde hiç sınır bulunamazsa `ParagraphStructureWarning`
basılır:

```python
import warnings
with warnings.catch_warnings(record=True) as kayit:
    warnings.simplefilter("always")
    oz = tlf.analyze(kitap_metni, lang="tr")
print(kayit[0].message)
```

```text
No paragraph boundary found: the text contains no blank line, so all 52521
words and 7347 sentences were counted as a single paragraph. ...
```

Uyarı metinleri İngilizcedir — öznitelik anahtarları ve künyeler de öyle.

Bu genellikle metnin PDF/EPUB'dan çıkarılırken satır sonlarını kaybetmesinden
olur; [sınırlılıklar §9](sinirliliklar.md) ölçümü veriyor.

### 4. İsteğe bağlı bir paket kurulu değil

`wordfreq` kurulu değilse `wordfreq_mean` ve `wordfreq_rare_ratio` `nan`
döner ve kütüphane bir `MissingDependencyWarning` basar.

```python
oz = tlf.analyze(metin, lang="tr", warn=False)
```

`warn=False` yalnız uyarıyı susturur; öznitelik yine `nan` kalır. Aynı bayrak
`ParagraphStructureWarning`'i de susturur.

## Tabloda ne yapmalı

**`nan`'ı sıfırla doldurmayın.** Sıfır bir ölçümdür, `nan` ölçüm
yokluğudur. `ttr = 0` "hiç çeşitlilik yok" demektir; `ttr = nan` "ölçemedim"
demektir. İkisini karıştırırsanız istatistiğiniz bozulur.

Sağlam yol:

```python
import pandas as pd
df = pd.DataFrame(tlf.analyze_corpus("korpus/", lang="tr"))

# hangi sütunlar hiç ölçülememiş
bos = df.columns[df.isna().all()]

# hangi sütunlarda kısmen eksik var
kismi = df.columns[df.isna().any() & ~df.isna().all()]
```

Hepsi `nan` olan sütunları **düşürün** — o öznitelik sizin korpusunuzda
çalışmıyor. Kısmen eksik olanlarda ise kararı siz verin: satırları mı
atacaksınız, o sütunu mu?

## `nan`'dan kaçınmanın yolu

Metinleri yeterince uzun tutun. Eşikleri aşmak için en pratik yol
parçalama:

```python
satirlar = tlf.analyze_corpus("korpus/", lang="tr", segment_size=1000)
```

1000 tokenlık parçalar 208 özniteliğin neredeyse tamamını besler. Ayrıntı:
[Metni parçalara böl](../nasil/segmentleme.md).

## Neden `None` değil de `nan`

`nan` bir `float`'tır. Yani dönen sözlüğün bütün değerleri aynı tiptedir ve
tablo doğrudan `pandas`, `numpy`, R ya da CSV'ye geçer. `None` koysaydık
sütun tipi `object` olur, aritmetik bozulur, CSV'de boş hücre ile gerçek
sıfırı ayırt etmek zorlaşırdı.
