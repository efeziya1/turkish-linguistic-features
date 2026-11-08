# Tek metni analiz et

## En kısa hâli

```python
import turkish_linguistic_features as tlf

oz = tlf.analyze(metin, lang="tr")
```

Dönen şey düz bir `dict`: anahtar öznitelik (İng. *feature*) adı, değer sayı.

## Dil seçimi öznitelik kümesini değiştirir

```python
tr = tlf.analyze(tr_metin, lang="tr")
en = tlf.analyze(en_metin, lang="en")

len(tr)   # 214
len(en)   # 181
```

Aradaki 33'ün dökümü:

- **+23** Zeyrek biçimbirim (İng. *morpheme*) çözümlemesi: `morphological_zeyrek` grubu (ek
  zinciri, durum ekleri, kip ve zaman; anahtarların hepsi `zeyrek_` ile başlar); yalnız
  Türkçe.
- **+2** büyük ve küçük ünlü uyumu (`harmony_fronting_ratio`, `harmony_rounding_ratio`);
  Türkçenin özelliği, İngilizcede üretilmez.
- **+3** harf: Türkçe alfabe 29 harf, İngilizce 26 (`ç ğ ı ö ş ü` yalnız
  Türkçede, `q w x` yalnız İngilizcede).
- **+5** okunabilirlik: Türkçeye özgü 12 öznitelik (Ateşman, Çetinkaya-Uzun ve
  Bezirci-Yılmaz formülleri; Kalyoncu'nun dört formülü ve beş
  bileşeni), İngilizceye özgü 7 öznitelik (Flesch, Flesch-Kincaid,
  SMOG, ARI, Coleman-Liau ve LIX formülleri ile çok seslemli sözcük oranı); ortak olan
  `long_word_ratio` iki dilde de var.

Okunabilirlik formülü yalnız kurulduğu dilde hesaplanır. Bir formülün katsayıları kurulduğu
dilin metinlerinden belirlenir; Ateşman (1997) da Flesch formülünü Türkçeye uygularken
katsayıları Türkçe metinlerden yeniden hesaplamıştır. Bu yüzden Türkçe metinde Flesch,
İngilizce metinde Ateşman verilmez.

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

Gruplar ve Türkçede kaç öznitelik içerdikleri:

| Grup | Ad | İçerik | Öznitelik |
|---|---|---|---|
| `lexical` | Sözcüksel zenginlik ve sıklık | sözcüksel çeşitlilik (İng. *lexical diversity*), sözcük sıklığı ve sözcüksel yoğunluk | 35 |
| `chars` | Karakter sıklıkları | her harfin oranı | 29 |
| `morphological_zeyrek` | Biçimbilimsel öznitelikler (Zeyrek) | biçimbirim çözümlemesine dayalı oranlar | 23 |
| `punctuation` | Noktalama ve yazım | noktalama, büyük harf, rakam | 20 |
| `morphological` | Biçimbilimsel öznitelikler (spaCy) | durum, zaman, kişi, görünüş, çatı | 19 |
| `frequency_structure` | Sıklık yapısı | h-noktasına ve Zipf yasasına dayalı sıklık yapısı ölçüleri | 17 |
| `pos` | Sözcük türleri | sözcük türlerinin (İng. *parts of speech*) oranları ve çeşitliliği | 17 |
| `syntactic` | Sözdizimsel öznitelikler | bağımlılık uzaklığı, hiyerarşik uzaklık, tümce sonundaki sözcüğün türü | 16 |
| `phonological` | Sesbilimsel öznitelikler | ünlü dağılımı, ünlü uyumu, seslem sayısı | 14 |
| `readability` | Okunabilirlik | okunabilirlik formülleri ve bileşenleri | 13 |
| `sentence` | Tümce öznitelikleri | tümce sayısı, uzunluğu ve soru tümcesi oranı | 8 |
| `paragraph` | Paragraf yapısı | paragraf sayısı ve uzunluğu | 3 |

`chars` yalnız harfleri sayar: Türkçe alfabenin her harfi için bir anahtar (İngilizcede 26;
`q`, `w`, `x` yalnız orada). `morphological_zeyrek` yalnız Türkçede üretilir.

Bir özniteliğin hangi grupta olduğunu `describe_feature(anahtar)["group"]`
söyler.

## Kendi sözcük dizilerinizi sayın

Hazır özniteliklerin dışında aradığınız bir kalıp varsa `custom_ngrams` ile
sözcük dizisi (İng. *n-gram*) olarak verin:

```python
metin = ("Eski ev yıkıldı. Yerine yeni bir bina yapıldı, ama büyük bahçe kaldı. "
         "Ne var ki kimse eski evi unutmadı.")
oz = tlf.analyze(metin, lang="tr", custom_ngrams=[["ne", "var", "ki"], ["ADJ", "NOUN"]])
oz["ngram_ne_var_ki_count"]   # 1.0
oz["ngram_ADJ_NOUN_count"]    # 3.0
```

Her dizi bir anahtar olur; değeri metindeki eşleşme sayısıdır. Dizi tek bir öge de
olabilir; o zaman o ögenin metinde kaç kez geçtiğini verir.

### Bir öge neyle eşleşir

Dizideki her öge şu sırayla yorumlanır:

| Öge | Neyle eşleşir | Anahtarda |
|---|---|---|
| Sözcük türü etiketi (İng. *POS tag*; `NOUN`, `VERB`, `ADJ`…) | O etiketi taşıyan her sözcük | büyük harf (`NOUN`) |
| Tamamı büyük harf, en az 2 harf (`EV`, `GİT`, `İZMİR`) | Sözlükbirimi (İng. *lemma*) o olan her sözcük | büyük harf (`EV`) |
| Geri kalan her şey (`ev`, `izmir`, `I`) | Küçük harfe indirilmiş yazılı biçim | küçük harf (`ev`) |

**Yazılı biçim araması.** Küçük harfle yazdığınız öge sözcüğün yazılı biçimiyle eşleşir:
`eski ev` ile `eski evi` ayrı eşleşmelerdir. Büyük harfli yazımları da yakalar: `izmir`,
"İzmir" ve "İZMİR"i bulur, ama çekimli biçimleri ("İzmir'e") bulmaz.

**Sözlükbirim araması.** Çekimli biçimleri de yakalamak için ögeyi tamamen büyük harfle
yazın; o sözlükbirimi taşıyan her sözcükle eşleşir:

```python
ornek = "Eve gittim. Evden çıktık. Evdeki kedi uyudu."
tlf.ngram_matches(ornek, ["EV", "VERB"], lang="tr")
# {'eve gittim': 1, 'evden çıktık': 1}
tlf.analyze(ornek, lang="tr", custom_ngrams=[["EV", "VERB"]])["ngram_EV_VERB_count"]   # 2.0
```

**Sözcük türü etiketi.** `["ADJ", "NOUN"]` bir sıfat ve hemen ardından bir ad demektir;
`yeni bir bina` eşleşmez, çünkü arada `bir` var.

Ayrıntılar:

- Sözcük, sözlükbirim ve etiket aynı dizide karışabilir: `["eski", "EV", "GİT"]` →
  `ngram_eski_EV_GİT_count`; `["ADJ", "EV"]`; `["çok", "ADJ"]` (`çok` sözcüğünden hemen
  sonra bir sıfat).
- Sözlükbirimin kaynağı aracın geri kalanıyla aynıdır: Türkçede Zeyrek'in ilk çözümlemesi,
  İngilizcede spaCy.
- Eylemler mastar eki olmadan yazılır: `GİT`, `GO` (`["GO", "home"]` → "went home",
  "goes home").
- Büyük harfli öge Türkçenin kuralıyla küçültülür: `İZMİR` → izmir, `IRMAK` → ırmak.
  Noktasız `IZMIR` ise ızmır olur.
- Tek harfli öge sözcük sayılır, sözlükbirim araması yapılmaz (`I`, `O`).
- Etiket adıyla aynı olan sözlükbirim her zaman etiket sayılır: İngilizce "part"
  sözlükbirimi `PART` diye aranamaz.
- Eşleşme tümce sınırını aşmaz: `kaldı. Ne` yan yana sayılmaz.

Diğer notlar:
- Değer düz sayımdır. Uzunlukları farklı metinleri karşılaştıracaksanız
  `word_count`'a bölün (`oz["ngram_ADJ_NOUN_count"] / oz["word_count"]`) ya
  da metinleri aynı boya getirin (`segment_size`).

Sayı "kaç kez" sorusunu cevaplar. Dizinin **neyle** eşleştiğini görmek için:

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

İsteğe bağlı `wordfreq` paketi kurulu değilse araç
`MissingDependencyWarning` basar ve ona bağlı iki özniteliği (`wordfreq_*`)
`nan` bırakır. Bunu bilerek kabul ediyorsanız:

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
`ModelNotFoundError` alırsınız; mesajda kurulum komutu yazar.

!!! warning "Model değiştirmek sayıları değiştirir"

    Türceler (İng. *tokens*), sözcük türü etiketleri, biçimbilimsel etiketler ve
    bağımlılık çözümlemesi modelden gelir. Farklı modelle çıkan tabloyu eskisiyle aynı
    çalışmada karşılaştırmayın.

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
