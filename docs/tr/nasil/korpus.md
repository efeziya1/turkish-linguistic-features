# Korpusu CSV'ye çıkar

## Dizin düzeni

`analyze_corpus` üç düzeni kendiliğinden tanır. Her satır bir `label`
(etiket) ve bir `source` (kaynak) taşır.

**1. Alt klasör — klasör adı etikettir:**

```text
korpus/
  yazar_a/
    metin1.txt      → label "yazar_a", source "metin1"
    metin2.txt
  yazar_b/
    metin3.txt
```

**2. Kökte `Etiket_Başlık.txt` — dosya adının ilk alt çizgisine kadarki kısım
etikettir:**

```text
korpus/
  Roman_Yaban.txt     → label "Roman", source "Yaban"
  notlar.txt          → label "" (alt çizgi yok), source "notlar"
```

!!! warning "Alt çizgili dosya adları"

    Kökteki bir dosyanın adında alt çizgi varsa ilk kısım **etiket** olur:
    `metin_1.txt` → label `"metin"`, source `"1"`. Etiket istemiyorsanız
    dosya adında alt çizgi kullanmayın ya da alt klasör düzenini seçin.

İki düzen aynı klasörde birlikte bulunabilir.

**3. Tek bir CSV ya da TSV dosyası** — `analyze_corpus("korpus.csv")`. Sütun
başlıkları şu adlardan biri olmalı (ilk eşleşen kullanılır):

| Alan | Kabul edilen başlıklar |
|---|---|
| metin (zorunlu) | `text`, `Text`, `metin`, `Metin`, `METIN`, `content` |
| etiket | `label`, `Label`, `etiket`, `Etiket`, `ETIKET`, `author`, `Author`, `yazar`, `Yazar`, `kategori`, `category` |
| kaynak | `source`, `Source`, `kaynak`, `Kaynak`, `başlık`, `title`, `book`, `file` |

Kaynak sütunu yoksa dosyanın adı kullanılır. `.tsv` uzantılı dosya sekmeyle
ayrılmış okunur.

Etiket yazar olmak zorunda değil — dönem, tür, sınıf düzeyi, deney kolu,
ne ölçüyorsanız o.

Dosyalar **UTF-8** olmalı. UTF-8 olmayan dosya varsa analiz başlamadan hata
verilir ve okunamayan dosyaların hepsi adıyla listelenir.

## İki çağrı

```python
import turkish_linguistic_features as tlf

satirlar = tlf.analyze_corpus("korpus/", lang="tr")
tlf.save_csv(satirlar, "oznitelikler.csv")
print("satır sayısı:", len(satirlar))
print("sütun sayısı:", len(satirlar[0]))
```

Bu kadar. Zincirin tamamı bu.

## Ne çıkıyor

```text
satır sayısı: 3
sütun sayısı: 204
```

Her dosya bir satır. 204 sütun = 201 öznitelik + üç kimlik sütunu:

```text
label=yazar_a  source=metin1     segment_id=0  ttr=1.0
label=yazar_a  source=metin2     segment_id=0  ttr=1.0
label=yazar_b  source=metin3     segment_id=0  ttr=1.0
```

| Sütun | Ne |
|---|---|
| `label` | Klasör adı |
| `source` | Dosya adı (uzantısız) |
| `segment_id` | Parça numarası; `segment_size` verilmediyse hep `0` |

CSV başlığı:

```text
label,source,segment_id,lemma_count,word_count,word_len_mean,entropy,yu...
```

## İlerlemeyi görün

Korpus büyükse:

```python
satirlar = tlf.analyze_corpus("korpus/", lang="tr", show_progress=True)
```

```text
  [1/3] metin1 #0
  [2/3] metin2 #0
  [3/3] metin3 #0
```

## Dosyaları parçalara bölerek analiz edin

```python
satirlar = tlf.analyze_corpus("korpus/", lang="tr", segment_size=1000)
```

Örneğin 648 kelimelik tek bir dosya içeren `tek_dosya/` klasöründe:

```python
butun   = tlf.analyze_corpus("tek_dosya/", lang="tr")
parcali = tlf.analyze_corpus("tek_dosya/", lang="tr", segment_size=200)
print(len(butun), len(parcali), [s["segment_id"] for s in parcali])
```

Çıktı:

```text
1 3 [0, 1, 2]
```

648 ÷ 200 = 3 tam parça; kalan 48 kelime varsayılan `min_fill=1.0` ile atılır.

!!! danger "Parçalama dosya dosya yapılır, korpus geneli değil"

    `segment_size=1000`, **her dosyayı ayrı ayrı** 1000'lik parçalara
    böler. Bütün dosyaları birleştirip baştan sona 1000'er kesmez.
    Dolayısıyla her dosyanın sonunda `size`'dan kısa bir artık kalır ve
    varsayılan `min_fill=1.0` ile **atılır**.

    Neden ve ne zaman parçalamalısınız →
    [Metni parçalara böl](segmentleme.md).

## Tam imza

```python
analyze_corpus(
    path: str | Path,
    lang: str = "tr",
    segment_size: int | None = None,
    *,
    min_fill: float = 1.0,
    unit: str = "word",
    model: str | None = None,
    groups: list[str] | None = None,
    params: FeatureParams | None = None,
    custom_ngrams: list[list[str]] | None = None,
    show_progress: bool = False,
    warn: bool = True,
) -> list[dict[str, object]]
```

`groups`, `params`, `model`, `custom_ngrams`, `warn` — hepsi `analyze` ile aynı
anlamda ve her parçaya uygulanır. `custom_ngrams` sayıları parça başınadır.

## CSV yerine DataFrame

`save_csv` diskle çalışır. Bellekte kalmak isterseniz dönen liste zaten
`pandas`'a hazırdır:

```python
import pandas as pd
df = pd.DataFrame(tlf.analyze_corpus("korpus/", lang="tr"))
```

`pandas` kütüphanenin zorunlu bağımlılığı değildir; bunu siz kurarsınız.
