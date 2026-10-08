# Metni parçalara böl

## Neden gerekli

Sözcüksel zenginlik öznitelikleri **metin uzunluğuna duyarlıdır.** TTR uzun
metinde mutlaka düşer, `hapax_ratio` düşer, `yule_k` oynar. 50 000 sözcüklük
bir romanla 800 sözcüklük bir köşe yazısını aynı tabloda karşılaştırırsanız
ölçtüğünüz şey üslup değil, uzunluk olur. `mattr`, `mtld` ve `vocd_d` TTR'den
daha az duyarlıdır ama bağımsız değildir
([ölçüm örneği](https://github.com/efeziya1/turkish-linguistic-features/blob/main/examples/09_uzunluk_duyarliligi.py)).

Çözüm: hepsini aynı boya getirin.

```python
parcalar = tlf.segment_text(metin, segment_size=1000, lang="tr")
```

## Parça boyu sözcükle ölçülür

`segment_size`, `analyze`'ın saydığı sözcüğü sayar: boşlukla ayrılan, kenar
noktalaması atılan, harf ya da rakam içeren birim. Noktalama sözcük değildir
([tam tanım](../aciklama/kavramlar.md#sozcuk)).
[Öğreticideki](../baslangic.md) 25 sözcüklük `metin` ile:

```python
uzun = " ".join([metin] * 15)                  # 375 sözcük
parcalar = tlf.segment_text(uzun, segment_size=100, lang="tr")
len(parcalar)                                  # 3
[len(p.split()) for p in parcalar]             # [100, 100, 100]
```

375 sözcük ÷ 100 = 3 tam parça, artan 75 sözcük atılır. Her parça
`analyze`'da tam 100 sözcük eder; `mattr` gibi "en az 100 sözcük" isteyen bir
ölçüye yeter.

## Son parça: `min_fill`

Varsayılan `min_fill=1.0` yalnız **tam** parçaları tutar. Eksik kalan son
parça atılır.

```python
tlf.segment_text(uzun, segment_size=100, lang="tr")                # 3 parça
tlf.segment_text(uzun, segment_size=100, min_fill=0.5, lang="tr")  # 4 parça
```

Artık 75 sözcük, yani parçanın %75'i: `1.0` eşiğinin altında, `0.5`'in
üstünde.

| `min_fill` | Anlamı |
|---|---|
| `1.0` (varsayılan) | Yalnız tam parçalar. En temiz karşılaştırma. |
| `0.5` | Yarısından çok dolu son parçayı da tut. |
| `0.0` | Ne kalırsa tut. **Uzunluk karşılaştırmasını bozar.** |

!!! warning "Atılan veri sessizce atılır"

    Kütüphane kaç parça attığını size söylemez. `min_fill=1.0` ile 1400
    sözcüklük bir dosyadan `segment_size=1000` ile **tek** parça çıkar; kalan 400
    sözcük gider. Korpusunuzda kısa dosyalar varsa hiç parça
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

`unit="char"` ham karakter sayar; sözcük kuralı devreye girmez, dolayısıyla
`lang` anlamsızlaşır. Sözcük sınırına saygı göstermez — parça bir sözcüğün
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

`lang` metnin diliyle aynı olmalı. Varsayılan `"tr"`. Sözcük kuralı iki dilde
neredeyse aynıdır; fark sıra sayısındadır (Türkçede `3. kat`'taki `3.` tek
sözcük), yani İngilizce bir metinde parça sınırları nadiren kayar.

Parça içeriği **ham metin dilimidir** — yeniden birleştirilmiş sözcük listesi
değil. Yani noktalama, boşluk ve satır sonları olduğu gibi kalır.
