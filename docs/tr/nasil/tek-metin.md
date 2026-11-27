# Tek metni analiz et

## En kısa hâli

```python
import turkish_linguistic_features as tlf

oz = tlf.analyze(metin, lang="tr")
```

`analyze` düz bir Python sözlüğü (`dict`) döndürür: anahtarlar öznitelik (İng. *feature*) adları, değerler sayılardır.

## Dil seçimi öznitelik kümesini değiştirir

```python
tr = tlf.analyze(tr_metin, lang="tr")
en = tlf.analyze(en_metin, lang="en")

len(tr)   # 217
len(en)   # 187
```

Türkçedeki 30 fazla öznitelik şunlardan gelir:

- **+23** Akana biçimbirim (İng. *morpheme*) çözümlemesi: `morphological_akana` grubu (ek
  zinciri, durum ekleri, kip ve zaman; anahtarların hepsi `akana_` ile başlar); yalnız
  Türkçe.
- **+2** büyük ve küçük ünlü uyumu (`harmony_fronting_ratio`, `harmony_rounding_ratio`);
  Türkçenin özelliği, İngilizcede üretilmez.
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

217 özniteliğin hepsi gerekmiyorsa grup seçilebilir; çıktı yalnız o grupların
anahtarlarını taşır:

```python
oz = tlf.analyze(metin, lang="tr", groups=["readability", "lexical"])
len(oz)     # 48
```

Grup seçmek hızı pek değiştirmez: Sürenin çoğu spaCy ve Akana ön işlemesinde geçer ve
bu her durumda bir kez yapılır (1000 sözcüklük bir metinde bütün gruplar yaklaşık 0,6
saniye, yalnız `readability` yaklaşık 0,5 saniye). Grup seçimi, çıktıyı gereken
özniteliklere indirmek içindir.

Gruplar ve Türkçede kaç öznitelik içerdikleri:

| Grup | Ad | İçerik | Öznitelik |
|---|---|---|---|
| `lexical` | Sözcüksel zenginlik ve sıklık | sözcüksel çeşitlilik (İng. *lexical diversity*), sözcük sıklığı ve sözcüksel yoğunluk | 35 |
| `chars` | Karakter sıklıkları | her harfin oranı | 32 |
| `morphological_akana` | Biçimbilimsel öznitelikler (Akana) | biçimbirim çözümlemesine dayalı oranlar | 23 |
| `punctuation` | Noktalama ve yazım | noktalama, büyük harf, rakam | 20 |
| `morphological` | Biçimbilimsel öznitelikler (spaCy) | durum, zaman, kişi, görünüş, çatı | 19 |
| `frequency_structure` | Sıklık yapısı | h-noktasına ve Zipf yasasına dayalı sıklık yapısı ölçüleri | 17 |
| `pos` | Sözcük türleri | sözcük türlerinin (İng. *parts of speech*) oranları ve çeşitliliği | 17 |
| `syntactic` | Sözdizimsel öznitelikler | bağımlılık uzaklığı, hiyerarşik uzaklık, tümce sonundaki sözcüğün türü | 16 |
| `phonological` | Sesbilimsel öznitelikler | ünlü dağılımı, ünlü uyumu, seslem sayısı | 14 |
| `readability` | Okunabilirlik | okunabilirlik formülleri ve bileşenleri | 13 |
| `sentence` | Tümce öznitelikleri | tümce sayısı, uzunluğu ve soru tümcesi oranı | 8 |
| `paragraph` | Paragraf yapısı | paragraf sayısı ve uzunluğu | 3 |

`chars` yalnız harfleri sayar: İki dilde aynı 32 harfin her biri için bir anahtar (Türkçe ve
İngilizce alfabelerin birleşimi). Türkçe bir metinde geçen `w` ya da İngilizce bir metinde geçen
`ş` da sayılır. `morphological_akana` yalnız Türkçede üretilir.

Bir özniteliğin hangi grupta olduğunu `describe_feature(anahtar)["group"]`
söyler.

## Kendi sözcük dizilerinizi sayın

Hazır özniteliklerin dışında bir kalıp aranıyorsa `custom_ngrams` ile
sözcük dizisi (İng. *n-gram*) olarak verilir:

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
| Sözcük türü etiketi (İng. *POS tag*; `NOUN`, `VERB`, `ADJ`…; [liste](#sozcuk-turu-etiketleri)) | O etiketi taşıyan her sözcük | büyük harf (`NOUN`) |
| Tamamı büyük harf, en az 2 harf (`EV`, `GİT`, `İZMİR`) | Sözlükbirimi (İng. *lemma*) o olan her sözcük | büyük harf (`EV`) |
| Geri kalan her şey (`ev`, `izmir`, `I`) | Küçük harfe indirilmiş yazılı biçim | küçük harf (`ev`) |

**Yazılı biçim araması.** Küçük harfle yazılan öge sözcüğün yazılı biçimiyle eşleşir:
`eski ev` ile `eski evi` ayrı eşleşmelerdir. Büyük harfli yazımları da yakalar: `izmir`,
"İzmir" ve "İZMİR"i bulur, ama çekimli biçimleri ("İzmir'e") bulmaz.

**Sözlükbirim araması.** Çekimli biçimleri de yakalamak için öge tamamen büyük harfle
yazılır; o sözlükbirimi taşıyan her sözcükle eşleşir:

```python
ornek = "Eve gittim. Evden çıktık. Evdeki kedi uyudu."
tlf.ngram_matches(ornek, ["EV", "VERB"], lang="tr")
# {'eve gittim': 1, 'evden çıktık': 1}
tlf.analyze(ornek, lang="tr", custom_ngrams=[["EV", "VERB"]])["ngram_EV_VERB_count"]   # 2.0
```

**Sözcük türü etiketi.** `["ADJ", "NOUN"]` bir sıfat ve hemen ardından bir ad demektir;
`yeni bir bina` eşleşmez, çünkü arada `bir` var.

Ayrıntılar:

- Sözcük, sözlükbirim ve etiket aynı dizide birlikte kullanılabilir: `["eski", "EV", "GİT"]` →
  `ngram_eski_EV_GİT_count`; `["ADJ", "EV"]`; `["çok", "ADJ"]` (`çok` sözcüğünden hemen
  sonra bir sıfat).
- Sözlükbirimin kaynağı aracın geri kalanıyla aynıdır: Türkçede Akana'nın seçtiği çözümleme,
  İngilizcede spaCy.
- Eylemler mastar eki olmadan yazılır: `GİT`, `GO` (`["GO", "home"]` → "went home",
  "goes home").
- Büyük harfli öge Türkçenin kuralıyla küçültülür: `İZMİR` → izmir, `IRMAK` → ırmak.
  Noktasız `IZMIR` ise ızmır olur.
- Tek harfli öge, büyük harfle yazılsa da yazılı biçimiyle aranır: `["O", "VERB"]`'deki `O`
  sözlükbirim değil, "o" sözcüğüdür.
- Büyük harfle yazılan öge bir etiket adıyla aynıysa etiket olarak aranır: `PART` parçacık
  etiketidir, İngilizce *part* sözlükbirimi değildir. Böyle bir sözcük küçük harfle, yazılı
  biçimiyle aranır (`part`).
- Eşleşme tümce sınırını aşmaz: `kaldı. Ne` yan yana sayılmaz.

Diğer notlar:
- Değer düz sayımdır. Uzunlukları farklı metinler karşılaştırılırken değer `word_count`'a
  bölünmeli (`oz["ngram_ADJ_NOUN_count"] / oz["word_count"]`) ya da metinler aynı boya
  getirilmelidir (`segment_size`).

Sayı "kaç kez" sorusunu cevaplar. Dizinin **neyle** eşleştiğini görmek için:

```python
tlf.ngram_matches(metin, ["ADJ", "NOUN"], lang="tr")
```

```text
{'eski ev': 1, 'büyük bahçe': 1, 'eski evi': 1}
```

En sık eşleşme önce gelir; sayıların toplamı `ngram_ADJ_NOUN_count` ile
aynıdır. Tümce ve konum bilgisi verilmez. Çalışan örnek:
[`examples/10_kelime_oruntuleri.py`](https://github.com/efeziya1/turkish-linguistic-features/blob/main/examples/10_kelime_oruntuleri.py).

### Sözcük türü etiketleri

Etiketler Evrensel Bağımlılıklar (İng. *Universal Dependencies*) şemasından gelir ve iki dilde
aynıdır:

| Etiket | Sözcük türü | Örnek |
|---|---|---|
| `NOUN` | ad | `ev`, `kitap` |
| `PROPN` | özel ad | `Ali`, `İstanbul` |
| `VERB` | eylem | `geldi`, `okuyor` |
| `ADJ` | sıfat | `güzel`, `büyük` |
| `ADV` | belirteç | `hızla`, `yavaşça` |
| `PRON` | adıl | `ben`, `bunu` |
| `DET` | belirleyici | `bir`, `her` |
| `NUM` | sayı | `iki`, `1999` |
| `ADP` | ilgeç | `için`, `gibi` |
| `AUX` | yardımcı sözcük | `değil`, `mi` |
| `CCONJ` | sıralama bağlacı | `ve`, `ama`, `ki` |
| `SCONJ` | yantümce bağlacı | Türkçede seyrek; İngilizce `because`, `if` |
| `PART` | parçacık | Türkçede seyrek; İngilizce `not`, `to` |
| `INTJ` | ünlem | `hadi`, `sakın` |
| `X` | öteki | yabancı sözcük, yazım hatası |

Noktalama (`PUNCT`) ve simge (`SYM`) sözcük sayılmadığı için dizilerde eşleşmez. Etiketi
spaCy modeli verir; aynı sözcük tümceye göre farklı etiket alabilir.

## Sayılan birimleri görün

Bir sayının hangi sözcüklerden çıktığını denetlemek ya da kendi sayımını yapmak için
özniteliklerin saydığı birimlerin kendisi görülebilir. `text_units`, özniteliklerin saydığı
sözcükleri ([sözcüğün tanımı](../aciklama/kavramlar.md#sozcuk)), sözlükbirimleri (İng.
*lemmas*), sözcük türü etiketlerini, seslem sayılarını ve tümceleri ayrı listeler hâlinde verir:

```python
b = tlf.text_units("Ali kitapları okudu. Yarın İstanbul'a gidecek.", lang="tr")
b["words"]      # ['Ali', 'kitapları', 'okudu', 'Yarın', "İstanbul'a", 'gidecek']
b["lemmas"]     # ['ali', 'kitap', 'oku', 'yarın', 'istanbul', 'git']
b["pos"]        # ['PROPN', 'NOUN', 'VERB', 'NOUN', 'PROPN', 'VERB']
b["syllables"]  # [2.0, 4.0, 3.0, 2.0, 4.0, 3.0]
b["sentences"]  # [['Ali', 'kitapları', 'okudu'], ['Yarın', "İstanbul'a", 'gidecek']]
```

Sözlükbirim, etiket ve seslem listeleri sözcüklerle sıra sıra eşleşir: `b["lemmas"][1]`,
`b["words"][1]`'in sözlükbirimidir. Sözcük sayısı `word_count`'a, tümce sayısı
`sent_count`'a, seslemlerin toplamı `syllable_count`'a eşittir; bir sayının hangi
birimlerden çıktığı buradan görülebilir. Okunuşu yazıdan çıkarılamayan sözcüğün
(e-posta ya da web adresi) seslemi `nan`'dır ve toplama girmez
([Sınırlılıklar](../aciklama/sinirliliklar.md#seslem-saymnda-okunusla-saylanlar-ve-atlananlar)).

`analyze`'daki `lemma_count` yalnız kaç *farklı* sözlükbirim olduğunu söyler. Hangi
sözlükbirimin kaç kez geçtiğini, yani bir sıklık listesini görmek için Python'un kendi
`Counter`'ı kullanılabilir (araçla gelmez, Python'da hazır bulunur):

```python
from collections import Counter
Counter(b["lemmas"]).most_common(10)   # en sık 10 sözlükbirim ve sayıları
```

## İlerleme göstergesi

Uzun metinlerde ilerlemeyi görmek için:

```python
oz = tlf.analyze(metin, lang="tr", show_progress=True)
```

## Uyarıları susturun

İsteğe bağlı `wordfreq` paketi kurulu değilse araç
`MissingDependencyWarning` uyarısı verir ve ona bağlı iki özniteliği (`wordfreq_*`)
`nan` bırakır. Bu bilerek kabul ediliyorsa uyarı kapatılabilir:

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
`ModelNotFoundError` verilir; iletide kurulum komutu yazar.

!!! warning "Model değiştirmek sayıları değiştirir"

    Türceler (İng. *tokens*), sözcük türü etiketleri, biçimbilimsel etiketler ve
    bağımlılık çözümlemesi modelden gelir. Farklı modelle çıkan tablo eskisiyle aynı
    çalışmada karşılaştırılmamalıdır.

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
