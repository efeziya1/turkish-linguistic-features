# Tek metni analiz et

## En kısa hâli

```python
import turkish_linguistic_features as tlf

oz = tlf.analyze(metin, lang="tr")
```

Dönen şey düz bir `dict`: anahtar öznitelik adı, değer sayı.

## Dil seçimi öznitelik kümesini değiştirir

```python
tr = tlf.analyze(tr_metin, lang="tr")
en = tlf.analyze(en_metin, lang="en")

len(tr)   # 208
len(en)   # 182
```

Aradaki 26 öznitelik Türkçeye özgüdür: ünlü uyumu, ek zinciri derinliği,
durum eki oranları, Ateşman/Çetinkaya/Bezirci-Yılmaz okunabilirlik
formülleri. İngilizcede bunların yerine Flesch, Flesch-Kincaid ve SMOG var.

`lang` yalnız `"tr"` ve `"en"` alır. Başka bir değer `ValueError` verir.

## Yalnız bazı grupları isteyin

208 özniteliğin hepsini hesaplamak zaman alır. İhtiyacınız yoksa grup seçin:

```python
oz = tlf.analyze(metin, lang="tr", groups=["readability", "lexical"])
len(oz)     # 39
```

Mevcut gruplar ve Türkçede kaç öznitelik içerdikleri:

| Grup | Öznitelik | İçerik |
|---|---|---|
| `lexical` | 32 | Sözcüksel zenginlik, sıklık |
| `chars` | 29 | Harf sıklık vektörü (`char_a`…`char_z` + 3) |
| `morphological_zeyrek` | 24 | Zeyrek ek çözümlemesi (yalnız TR) |
| `morphological` | 19 | UD morfolojik özellikleri |
| `punctuation` | 18 | Noktalama oranları |
| `syntactic_dep` | 16 | Bağlılık ayrıştırması |
| `phonetic` | 15 | Hece, ünlü, ses örüntüsü |
| `frequency_structure` | 13 | Zipf, h-noktası, tematik yoğunlaşma |
| `pos` | 13 | Sözcük türü oranları |
| `syntactic` | 9 | Cümle yapısı |
| `sentence` | 8 | Cümle uzunluğu dağılımı |
| `readability` | 7 | Okunabilirlik formülleri |
| `paragraph` | 5 | Paragraf yapısı |

Bir özniteliğin hangi grupta olduğunu `describe_feature(anahtar)["group"]`
söyler.

## İlerleme göstergesi

Uzun metinlerde ne olduğunu görmek isterseniz:

```python
oz = tlf.analyze(metin, lang="tr", show_progress=True)
```

## Uyarıları susturun

İsteğe bağlı bir paket (`pandas`, `wordfreq`) kurulu değilse kütüphane
`MissingDependencyWarning` basar ve o özniteliği `nan` bırakır. Bunu bilerek
kabul ediyorsanız:

```python
oz = tlf.analyze(metin, lang="tr", warn=False)
```

`warn=False` **hesaplamayı değiştirmez**, yalnız uyarıyı bastırır. Eksik
öznitelik yine `nan` döner.

## Farklı bir spaCy modeli kullanın

```python
oz = tlf.analyze(metin, lang="tr", model="tr_core_news_trf")
```

Varsayılanlar `tr_core_news_md` ve `en_core_web_sm`. Model kurulu değilse
`ModelNotFoundError` alırsınız — mesajda kurulum komutu yazar.

!!! warning "Model değiştirmek sayıları değiştirir"

    Cümle bölme, sözcük türü ve bağlılık ayrıştırması modelden gelir.
    Farklı modelle çıkan tabloyu eskisiyle aynı çalışmada
    karşılaştırmayın. Hangi modeli kullandığınızı yöntem bölümüne yazın.

## Tam imza

```python
analyze(
    text: str,
    lang: str = "tr",
    model: str | None = None,
    groups: list[str] | None = None,
    params: FeatureParams | None = None,
    custom_ngrams: list[list[str]] | None = None,
    show_progress: bool = False,
    warn: bool = True,
) -> dict[str, float]
```

`params` için → [Eşikleri değiştir](parametreler.md).
