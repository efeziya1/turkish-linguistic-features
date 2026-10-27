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

len(tr)   # 214
len(en)   # 181
```

Aradaki 33'ün dökümü:

- **+23** Zeyrek biçimbirim çözümlemesi: `morphological_zeyrek` grubu (ek zinciri,
  durum ekleri, kip ve zaman; anahtarların hepsi `zeyrek_` ile başlar) — yalnız
  Türkçe.
- **+2** büyük ve küçük ünlü uyumu (`harmony_fronting_ratio`, `harmony_rounding_ratio`) —
  Türkçenin özelliği; İngilizcede üretilmez.
- **+3** harf: Türkçe alfabe 29 harf, İngilizce 26 (`ç ğ ı ö ş ü` yalnız
  Türkçede, `q w x` yalnız İngilizcede).
- **+5** okunabilirlik: Türkçeye özgü 12 öznitelik (Ateşman, Çetinkaya-Uzun ve
  Bezirci-Yılmaz formülleri; [Kalyoncu'nun](../aciklama/kalyoncu.md) dört formülü ve beş
  bileşeni), İngilizceye özgü 7 öznitelik (Flesch, Flesch-Kincaid,
  SMOG, ARI, Coleman-Liau ve LIX formülleri ile çok seslemli sözcük oranı); ortak olan
  `long_word_ratio` iki dilde de var. Okunabilirlik formülü yalnız kurulduğu dilde
  hesaplanır.

`phonological` grubu Türkçede 14, İngilizcede 12 öznitelik içerir.

`lang` yalnız `"tr"` ve `"en"` alır. Başka bir değer `ValueError` verir.

## Yalnız bazı grupları isteyin

214 özniteliğin hepsine ihtiyacınız yoksa grup seçin; çıktı yalnız o grupların
anahtarlarını taşır:

```python
oz = tlf.analyze(metin, lang="tr", groups=["readability", "lexical"])
len(oz)     # 48
```

Grup seçmek az hız kazandırır. Sürenin çoğu spaCy ve Zeyrek ön işlemesinde
geçer ve o her durumda bir kez yapılır; grup seçimi yalnız sonraki hesabı
kısaltır. 1000 sözcüklük bir metinde bütün gruplar yaklaşık 1,1 saniye, yalnız
`readability` yaklaşık 0,95 saniye sürer.

Mevcut gruplar ve Türkçede kaç öznitelik içerdikleri:

| Grup | Ad | Öznitelik |
|---|---|---|
| `lexical` | Sözcüksel zenginlik ve sıklık | 35 |
| `chars` | Karakter sıklıkları | 29 |
| `morphological_zeyrek` | Biçimbilimsel öznitelikler (Zeyrek) | 23 |
| `punctuation` | Noktalama ve yazım | 20 |
| `morphological` | Biçimbilimsel öznitelikler (spaCy) | 19 |
| `frequency_structure` | Sıklık yapısı | 17 |
| `pos` | Sözcük türleri | 17 |
| `syntactic` | Sözdizimsel öznitelikler | 16 |
| `phonological` | Sesbilimsel öznitelikler | 14 |
| `sentence` | Tümce öznitelikleri | 8 |
| `readability` | Okunabilirlik | 13 |
| `paragraph` | Paragraf yapısı | 3 |

`chars` yalnız harfleri sayar: Türkçe alfabenin her harfi için bir anahtar (İngilizcede 26;
`q`, `w`, `x` yalnız orada). `morphological_zeyrek` yalnız Türkçede üretilir.

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

- Sözcükler küçük harfe indirilerek karşılaştırılır. Yazılı biçim aranır,
  sözlükbirim değil: `eski ev` ile `eski evi` ayrı eşleşmelerdir.
- Büyük harfle yazılmış bir UD POS etiketi (`NOUN`, `VERB`, `ADJ`…)
  o etiketi taşıyan herhangi bir sözcükle eşleşir. `["ADJ", "NOUN"]` bir sıfat
  ve hemen ardından bir isim demektir; `yeni bir bina` eşleşmez, çünkü arada
  `bir` var.
- Eşleşme tümce sınırını aşmaz: `kaldı. Ne` yan yana sayılmaz.
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
aynıdır. Tümce ve konum bilgisi verilmez. Birden çok metin için sonuçları
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

    Türceleme, POS etiketleri, biçimbilimsel etiketler ve bağımlılık
    ayrıştırması modelden gelir. Farklı modelle çıkan tabloyu eskisiyle aynı çalışmada
    karşılaştırmayın.

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
