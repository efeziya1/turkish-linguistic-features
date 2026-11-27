# Metni parçalara böl

## Neden gerekli

Sözcüksel zenginlik (İng. *lexical richness*) öznitelikleri **metin uzunluğundan
etkilenir.** TTR uzun metinde mutlaka düşer, `hapax_ratio` düşer, `yule_k` değişir. 50.000
sözcüklük bir romanla 800 sözcüklük bir köşe yazısı aynı tabloda karşılaştırılırsa
ölçülen şey üslup değil, uzunluk olur. `mattr`, `mtld` ve `vocd_d` TTR'den
daha az etkilenir ama uzunluktan bağımsız değildir
([ölçüm örneği](https://github.com/efeziya1/turkish-linguistic-features/blob/main/examples/09_uzunluk_duyarliligi.py)).

Çözüm: hepsini aynı boya getirmek.

```python
parcalar = tlf.segment_text(metin, segment_size=1000, lang="tr")
```

## Parça boyu sözcükle ölçülür

`segment_size`, `analyze`'ın saydığı sözcüğü (İng. *word*) sayar: boşlukla ayrılan, kenar
noktalaması atılan, harf ya da rakam içeren birim. Noktalama sözcük değildir
([tam tanım](../aciklama/kavramlar.md#sozcuk)).
[Öğreticideki](../baslangic.md) 25 sözcüklük `metin` ile:

```python
uzun = " ".join([metin] * 15)                  # 375 sözcük
parcalar = tlf.segment_text(uzun, segment_size=100, lang="tr")
len(parcalar)                                  # 3
```

375 sözcük ÷ 100 = 3 tam parça (İng. *segment*), artan 75 sözcük atılır. Her parça
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
üstündedir.

| `min_fill` | Anlamı |
|---|---|
| `1.0` (varsayılan) | Yalnız tam parçalar. En temiz karşılaştırma. |
| `0.5` | En az yarısı dolu son parçayı da tut. |
| `0.0` | Ne kalırsa tut. **Uzunluk karşılaştırmasını bozar.** |

!!! warning "Atılan veri sessizce atılır"

    Araç kaç parça attığını söylemez. `min_fill=1.0` ile 1400
    sözcüklük bir dosyadan `segment_size=1000` ile **tek** parça çıkar; kalan 400
    sözcük gider. Derlemdeki kısa dosyalar hiç parça
    üretmeyebilir.

## Derlemde doğrudan kullanın

Bir derlemi parçalamak için `analyze_corpus`'a `segment_size` vermek yeter:
[Derlemi CSV'ye çıkar](korpus.md#dosyalar-parcalara-bolerek-analiz-edin).

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

`lang` metnin diliyle aynı olmalıdır. Varsayılan `"tr"`'dir. Sözcük kuralı iki dilde aynıdır,
tek fark Türkçedeki sıra sayısıdır: `3. kat`'taki `3.` tek sözcüktür. İngilizce sıra
sayısını `3rd` diye yazdığı için bu kurala gerek duymaz.

Parça içeriği **ham metin dilimidir**, yeniden birleştirilmiş sözcük listesi
değildir. Yani noktalama, boşluk ve satır sonları olduğu gibi kalır.
