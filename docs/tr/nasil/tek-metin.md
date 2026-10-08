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
len(en)   # 181
```

Aradaki 27'nin dökümü:

- **+23** Zeyrek ek çözümlemesi: `morphological_zeyrek` grubu (ek zinciri,
  durum ekleri, kip ve zaman; anahtarların hepsi `zeyrek_` ile başlar) — yalnız
  Türkçe.
- **+2** ünlü uyumu (`harmony_fronting_ratio`, `harmony_rounding_ratio`) —
  Türkçenin özelliği; İngilizcede üretilmez.
- **+3** harf: Türkçe alfabe 29 harf, İngilizce 26 (`ç ğ ı ö ş ü` yalnız
  Türkçede, `q w x` yalnız İngilizcede).
- **−1** okunabilirlik: Türkçeye özgü 3 öznitelik (Ateşman, Çetinkaya-Uzun ve
  Bezirci-Yılmaz formülleri), İngilizceye özgü 4 öznitelik (Flesch, Flesch-Kincaid
  ve SMOG formülleri ile çok heceli kelime oranı); ortak olanlar iki dilde de var.

`phonetic` grubu Türkçede 14, İngilizcede 12 öznitelik içerir.

`lang` yalnız `"tr"` ve `"en"` alır. Başka bir değer `ValueError` verir.

## Yalnız bazı grupları isteyin

208 özniteliğin hepsine ihtiyacınız yoksa grup seçin; çıktı yalnız o grupların
anahtarlarını taşır:

```python
oz = tlf.analyze(metin, lang="tr", groups=["readability", "lexical"])
len(oz)     # 45
```

Grup seçmek az hız kazandırır. Sürenin çoğu spaCy ve Zeyrek ön işlemesinde
geçer ve o her durumda bir kez yapılır; grup seçimi yalnız sonraki hesabı
kısaltır. 1000 kelimelik bir metinde bütün gruplar yaklaşık 1,2 saniye, yalnız
`readability` yaklaşık 0,85 saniye sürer.

Mevcut gruplar ve Türkçede kaç öznitelik içerdikleri:

| Grup | Öznitelik | İçerik |
|---|---|---|
| `lexical` | 38 | Sözcüksel zenginlik, sıklık |
| `chars` | 29 | Harf sıklık vektörü: Türkçe alfabenin her harfi için bir anahtar (İngilizcede 26; `q`, `w`, `x` yalnız orada) |
| `morphological_zeyrek` | 23 | Zeyrek ek çözümlemesi (yalnız TR) |
| `morphological` | 19 | UD morfolojik özellikleri |
| `punctuation` | 20 | Noktalama türlerinin payı, noktalama yoğunluğu, büyük harf |
| `syntactic_dep` | 16 | Bağlılık ayrıştırması |
| `phonetic` | 14 | Hece, ünlü, ses örüntüsü |
| `frequency_structure` | 13 | Zipf, h-noktası, tematik yoğunlaşma |
| `pos` | 12 | Sözcük türü payları |
| `syntactic` | 7 | Cümle yapısı |
| `sentence` | 7 | Cümle uzunluğu dağılımı |
| `readability` | 7 | Okunabilirlik formülleri |
| `paragraph` | 3 | Paragraf yapısı |

Bir özniteliğin hangi grupta olduğunu `describe_feature(anahtar)["group"]`
söyler.

## Kendi öbeklerinizi sayın

Hazır özniteliklerin dışında aradığınız bir kalıp varsa `custom_ngrams` ile
verin:

```python
metin = ("Eski ev yıkıldı. Yerine yeni bir bina yapıldı, ama büyük bahçe kaldı. "
         "Ne var ki kimse eski evi unutmadı.")
oz = tlf.analyze(metin, lang="tr", custom_ngrams=[["ne", "var", "ki"], ["ADJ", "NOUN"]])
oz["ngram_ne_var_ki_count"]   # 1.0
oz["ngram_ADJ_NOUN_count"]    # 3.0
```

Her öbek bir anahtar olur; değeri metindeki eşleşme sayısıdır.

- Kelimeler küçük harfe indirilerek karşılaştırılır. Yazılı biçim aranır,
  lemma değil: `eski ev` ile `eski evi` ayrı eşleşmelerdir.
- Büyük harfle yazılmış bir UD sözcük türü etiketi (`NOUN`, `VERB`, `ADJ`…)
  o etiketi taşıyan herhangi bir kelimeyle eşleşir. `["ADJ", "NOUN"]` bir sıfat
  ve hemen ardından bir isim demektir; `yeni bir bina` eşleşmez, çünkü arada
  `bir` var.
- Eşleşme cümle sınırını aşmaz: `kaldı. Ne` yan yana sayılmaz.
- Değer düz sayımdır. Uzunlukları farklı metinleri karşılaştıracaksanız
  `word_count`'a bölün (`oz["ngram_ADJ_NOUN_count"] / oz["word_count"]`) ya
  da metinleri aynı boya getirin (`segment_size`).

Sayı "kaç kez" sorusunu cevaplar. Öbeğin **neyle** eşleştiğini görmek için:

```python
tlf.ngram_matches(metin, ["ADJ", "NOUN"], lang="tr")
```

```text
{'eski ev': 1, 'büyük bahçe': 1, 'eski evi': 1}
```

En sık eşleşme önce gelir; sayıların toplamı `ngram_ADJ_NOUN_count` ile
aynıdır. Cümle ve konum bilgisi verilmez. Birden çok metin için sonuçları
`collections.Counter` ile toplayın. Çalışan örnek:
[`examples/10_kelime_oruntuleri.py`](https://github.com/efeziya1/turkish-linguistic-features/blob/main/examples/10_kelime_oruntuleri.py).

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

    Tokenlara ayırma, sözcük türü, biçimbirim etiketleri ve bağlılık
    ayrıştırması modelden gelir. Farklı modelle çıkan tabloyu eskisiyle aynı çalışmada
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
