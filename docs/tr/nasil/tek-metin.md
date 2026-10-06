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

len(tr)   # 212
len(en)   # 184
```

Aradaki 28'in dökümü:

- **+24** Zeyrek ek çözümlemesi (`morphological_zeyrek`; ek zinciri,
  durum ekleri, kip ve zaman) — yalnız Türkçe.
- **+2** ünlü uyumu (`harmony_fronting_ratio`, `harmony_rounding_ratio`) —
  Türkçenin özelliği; İngilizcede üretilmez.
- **+3** harf: Türkçe alfabe 29 harf, İngilizce 26 (`ç ğ ı ö ş ü` yalnız
  Türkçede, `q w x` yalnız İngilizcede).
- **−1** okunabilirlik: Türkçede üç formül (Ateşman, Çetinkaya-Uzun,
  Bezirci-Yılmaz), İngilizcede dört öznitelik (Flesch, Flesch-Kincaid, SMOG ve çok
  heceli kelime oranı); ortak olanlar iki dilde de var.

`phonetic` grubu Türkçede 15, İngilizcede 13 öznitelik içerir.

`lang` yalnız `"tr"` ve `"en"` alır. Başka bir değer `ValueError` verir.

## Yalnız bazı grupları isteyin

212 özniteliğin hepsini hesaplamak zaman alır. İhtiyacınız yoksa grup seçin:

```python
oz = tlf.analyze(metin, lang="tr", groups=["readability", "lexical"])
len(oz)     # 39
```

Mevcut gruplar ve Türkçede kaç öznitelik içerdikleri:

| Grup | Öznitelik | İçerik |
|---|---|---|
| `lexical` | 36 | Sözcüksel zenginlik, sıklık |
| `chars` | 29 | Harf sıklık vektörü: Türkçe alfabenin her harfi için bir anahtar (İngilizcede 26; `q`, `w`, `x` yalnız orada) |
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

İsteğe bağlı `wordfreq` paketi kurulu değilse kütüphane
`MissingDependencyWarning` basar ve ona bağlı iki özniteliği (`wordfreq_*`)
`nan` bırakır. Bunu bilerek
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
