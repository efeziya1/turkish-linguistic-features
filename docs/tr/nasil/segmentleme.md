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
parcalar = tlf.segment_text(metin, segment_size=1000, lang="tr")
```

## Parça boyu kelimeyle ölçülür

`segment_size`, `analyze`'ın saydığı kelimeyi sayar: boşlukla ayrılan, kenar
noktalaması atılan, harf ya da rakam içeren birim. Noktalama kelime değildir.
[Öğreticideki](../baslangic.md) 30 kelimelik `metin` ile:

```python
uzun = " ".join([metin] * 12)                  # 360 kelime
parcalar = tlf.segment_text(uzun, segment_size=100, lang="tr")
len(parcalar)                                  # 3
[len(p.split()) for p in parcalar]             # [100, 100, 100]
```

360 kelime ÷ 100 = 3 tam parça, artan 60 kelime atılır. Her parça
`analyze`'da tam 100 kelime eder; `mattr` gibi "en az 100 kelime" isteyen bir
ölçüye yeter.

## Son parça: `min_fill`

Varsayılan `min_fill=1.0` yalnız **tam** parçaları tutar. Eksik kalan son
parça atılır.

```python
tlf.segment_text(uzun, segment_size=100, lang="tr")                # 3 parça
tlf.segment_text(uzun, segment_size=100, min_fill=0.5, lang="tr")  # 4 parça
```

Artık 60 kelime, yani parçanın %60'ı: `1.0` eşiğinin altında, `0.5`'in
üstünde.

| `min_fill` | Anlamı |
|---|---|
| `1.0` (varsayılan) | Yalnız tam parçalar. En temiz karşılaştırma. |
| `0.5` | Yarısından çok dolu son parçayı da tut. |
| `0.0` | Ne kalırsa tut. **Uzunluk karşılaştırmasını bozar.** |

!!! warning "Atılan veri sessizce atılır"

    Kütüphane kaç parça attığını size söylemez. `min_fill=1.0` ile 1400
    kelimelik bir dosyadan `segment_size=1000` ile **tek** parça çıkar; kalan 400
    kelime gider. Korpusunuzda kısa dosyalar varsa hiç parça
    üretmeyebilirler.

    Bunu bilerek kullanın. Şüpheliyseniz önce sayın:

    ```python
    for yol in dosyalar:
        n = len(tlf.segment_text(yol.read_text(encoding="utf-8"),
                                 segment_size=1000, lang="tr"))
        print(yol.name, n)
    ```

## Karakterle bölmek

```python
tlf.segment_text(metin, segment_size=5000, unit="char", lang="tr")
```

`unit="char"` ham karakter sayar; kelime kuralı devreye girmez, dolayısıyla
`lang` anlamsızlaşır. Kelime sınırına saygı göstermez — parça bir kelimenin
ortasında bitebilir. Yalnız kaba bir bölme yeterliyse kullanın.

## Korpusta doğrudan kullanın

Tek tek bölüp `analyze` çağırmanıza gerek yok:

```python
satirlar = tlf.analyze_corpus("korpus/", lang="tr", segment_size=1000)
```

## Tam imza

```python
segment_text(
    text: str,
    segment_size: int = 1000,
    min_fill: float = 1.0,
    unit: str = "word",
    lang: str = "tr",
) -> list[str]
```

`lang` metnin diliyle aynı olmalı. Varsayılan `"tr"`. Kelime kuralı iki dilde
neredeyse aynıdır; fark sıra sayısındadır (Türkçede `3. kat`'taki `3.` tek
kelime), yani İngilizce bir metinde parça sınırları nadiren kayar.

Parça içeriği **ham metin dilimidir** — yeniden birleştirilmiş kelime listesi
değil. Yani noktalama, boşluk ve satır sonları olduğu gibi kalır.
