# Derlemi CSV'ye çıkar

Derlem (İng. *corpus*), birlikte çözümlenecek metinlerdir. Bu sayfa bir derlemi tek
seferde öznitelik tablosuna çevirmeyi anlatır.

## Klasör düzeni

`analyze_corpus` üç düzeni kendiliğinden tanır. Her satır bir `label`
(etiket) ve bir `source` (kaynak) taşır.

**1. Alt klasör — klasör adı etikettir:**

```text
derlem/
  yazar_a/
    metin1.txt      → label "yazar_a", source "metin1"
    metin2.txt
  yazar_b/
    metin3.txt
```

**2. Kökte `Etiket_Başlık.txt` — dosya adının ilk alt çizgisine kadarki kısım
etikettir:**

```text
derlem/
  Roman_Yaban.txt     → label "Roman", source "Yaban"
  notlar.txt          → label "" (alt çizgi yok), source "notlar"
```

Dikkat: `metin_1.txt` gibi bir adda da ilk kısım etiket olur (label `"metin"`, source `"1"`).
İki düzen aynı klasörde birlikte bulunabilir.

**3. Tek bir CSV ya da TSV dosyası** — `analyze_corpus("derlem.csv")`. Her satır bir
metindir. Sütun başlıkları `text` (metin), `label` (etiket) ve `source` (kaynak) olur;
Türkçeleri de kabul edilir (`metin`, `etiket`, `kaynak`). Yalnız metin sütunu zorunludur;
kaynak sütunu yoksa dosyanın adı kullanılır. `.tsv` dosyası sekmeyle ayrılmış okunur.

??? note "Kabul edilen bütün başlıklar"

    | Alan | Başlıklar (ilk eşleşen kullanılır) |
    |---|---|
    | metin | `text`, `Text`, `metin`, `Metin`, `METIN`, `content` |
    | etiket | `label`, `Label`, `etiket`, `Etiket`, `ETIKET`, `author`, `Author`, `yazar`, `Yazar`, `kategori`, `category` |
    | kaynak | `source`, `Source`, `kaynak`, `Kaynak`, `başlık`, `title`, `book`, `file` |

Etiket yazar olmak zorunda değildir: dönem, tür, sınıf düzeyi, deney kolu, ne ölçülüyorsa o.

Dosyalar **UTF-8** olmalı; olmayan dosya varsa analiz başlamadan hepsi adıyla listelenir.
Bir metin çözümlenirken hata çıkarsa çalışma durur ve ileti hangi dosyada durduğunu söyler.

## İki çağrı

```python
import turkish_linguistic_features as tlf

satirlar = tlf.analyze_corpus("derlem/", lang="tr")
tlf.save_csv(satirlar, "oznitelikler.csv")
```

Dosyanın nereye kaydedildiği: [Öğretici, 7. adım](../baslangic.md#7-bir-derlemi-tabloya-cevirin).

## Ne çıkıyor

Her dosya bir satır: 3 satır, 220 sütun. 220 sütun = 217 öznitelik (İng. *feature*) + üç
kimlik sütunu:

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

Derlem büyükse:

```python
satirlar = tlf.analyze_corpus("derlem/", lang="tr", show_progress=True)
```

```text
  [1/3] metin1 #0
  [2/3] metin2 #0
  [3/3] metin3 #0
```

## Dosyaları parçalara bölerek analiz edin

```python
satirlar = tlf.analyze_corpus("derlem/", lang="tr", segment_size=1000)
```

Örneğin 648 sözcüklük tek bir dosya içeren `tek_dosya/` klasöründe:

```python
butun   = tlf.analyze_corpus("tek_dosya/", lang="tr")
parcali = tlf.analyze_corpus("tek_dosya/", lang="tr", segment_size=200)
print(len(butun), len(parcali))
```

Çıktı:

```text
1 3
```

648 ÷ 200 = 3 tam parça; kalan 48 sözcük varsayılan `min_fill=1.0` ile atılır.

Tümce uzunluğu dağılımını etiketlere göre karşılaştıran çalışan örnek:
[`examples/05_cumle_ritmi.py`](https://github.com/efeziya1/turkish-linguistic-features/blob/main/examples/05_cumle_ritmi.py).

!!! note "Parçalama dosya dosya yapılır, derlemin bütününe değil"

    `segment_size=1000`, **her dosyayı ayrı ayrı** 1000'lik parçalara
    böler. Bütün dosyaları birleştirip baştan sona 1000'er kesmez.
    Dolayısıyla her dosyanın sonunda `segment_size`'dan kısa bir artık kalır ve
    varsayılan `min_fill=1.0` ile **atılır**.

    Neden ve ne zaman parçalamak gerekir →
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

`groups`, `params`, `model`, `custom_ngrams`, `warn`: hepsi `analyze` ile aynı
anlamda ve her parçaya uygulanır. `custom_ngrams` sayıları parça başınadır.
