# Metni parçalara böl

## Neden gerekli

Sözcüksel zenginlik öznitelikleri **metin uzunluğuna duyarlıdır.** TTR uzun
metinde mutlaka düşer, `hapax_ratio` düşer, `yule_k` oynar. 50 000 kelimelik
bir romanla 800 kelimelik bir köşe yazısını aynı tabloda karşılaştırırsanız
ölçtüğünüz şey üslup değil, uzunluk olur. `mattr`, `mtld` ve `vocd_d` TTR'den
daha az duyarlıdır ama bağımsız değildir
([ölçüm örneği](https://github.com/efeziya1/turkish-linguistic-features/blob/main/examples/09_uzunluk_duyarliligi.py)).

Çözüm: hepsini aynı boya getirin.

```python
parcalar = tlf.segment_text(metin, size=1000, lang="tr")
```

## `size` spaCy token sayar, boşlukla ayrılmış kelime değil

Bu en çok şaşırtan noktadır. [Öğreticideki](../baslangic.md) 30 kelimelik
`metin` ile:

```python
import spacy

tokenizer = spacy.blank("tr").tokenizer
uzun = " ".join([metin] * 12)
len(uzun.split())              # 360  ← boşlukla ayrılmış "kelime"
len(tokenizer(uzun))           # 432  ← spaCy token
```

Oran 1,20 — fark noktalama işaretlerinden geliyor; spaCy onları ayrı token
sayar. Dolayısıyla:

```python
parcalar = tlf.segment_text(uzun, size=100, lang="tr")
len(parcalar)                                  # 4
[len(p.split()) for p in parcalar]             # [83, 84, 84, 83]
```

432 token ÷ 100 = 4 tam parça, artan 32 token atılır. Her parça 100
**token** ama 83–84 **kelime**.

`size` spaCy token sayar, çünkü boşlukla bölmek parça boylarını %50'ye
varan oranda değiştiriyordu.

## Son parça: `min_fill`

Varsayılan `min_fill=1.0` yalnız **tam** parçaları tutar. Eksik kalan son
parça atılır.

```python
tlf.segment_text(uzun, size=100, lang="tr")                   # 4 parça
tlf.segment_text(uzun, size=100, min_fill=0.5, lang="tr")     # 4 parça
```

Yukarıdaki örnekte ikisi de 4 veriyor çünkü artık 32 token = %32, yani
`0.5` eşiğinin de altında.

| `min_fill` | Anlamı |
|---|---|
| `1.0` (varsayılan) | Yalnız tam parçalar. En temiz karşılaştırma. |
| `0.5` | Yarısından çok dolu son parçayı da tut. |
| `0.0` | Ne kalırsa tut. **Uzunluk karşılaştırmasını bozar.** |

!!! warning "Atılan veri sessizce atılır"

    Kütüphane kaç parça attığını size söylemez. `min_fill=1.0` ile 1400
    tokenlık bir dosyadan `size=1000` ile **tek** parça çıkar; kalan 400
    token (noktalama dahil, ~330 kelime) gider. Korpusunuzda kısa dosyalar varsa hiç parça
    üretmeyebilirler.

    Bunu bilerek kullanın. Şüpheliyseniz önce sayın:

    ```python
    for yol in dosyalar:
        n = len(tlf.segment_text(yol.read_text(encoding="utf-8"),
                                 size=1000, lang="tr"))
        print(yol.name, n)
    ```

## Karakterle bölmek

```python
tlf.segment_text(metin, size=5000, unit="char", lang="tr")
```

`unit="char"` ham karakter sayar; tokenizer devreye girmez, dolayısıyla
`lang` anlamsızlaşır. Kelime sınırına saygı göstermez — parça bir kelimenin
ortasında bitebilir. Yalnız kaba bir bölme yeterliyse kullanın.

## Korpusta doğrudan kullanın

Tek tek bölüp `analyze` çağırmanıza gerek yok:

```python
satirlar = tlf.analyze_corpus("korpus/", lang="tr", segment_size=1000)
```

`segment_size`, `min_fill` ve `unit` aynı anlamdadır ve **her dosyaya ayrı
ayrı** uygulanır.

## Tam imza

```python
segment_text(
    text: str,
    size: int = 1000,
    min_fill: float = 1.0,
    unit: str = "word",
    lang: str = "tr",
) -> list[str]
```

`lang` metnin diliyle aynı olmalı. Varsayılan `"tr"`; kesme işareti ve
kısaltmalar iki dilde farklı tokenlara ayrıldığı için İngilizce bir metni
`lang="en"` vermeden bölerseniz parça sınırları değişir.

Parça içeriği **ham metin dilimidir** — yeniden birleştirilmiş token listesi
değil. Yani noktalama, boşluk ve satır sonları olduğu gibi kalır.
