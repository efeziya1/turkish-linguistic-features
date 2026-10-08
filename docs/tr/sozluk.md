# Terim sözlüğü

Doküman boyunca bu karşılıklar kullanılır. Amaç tutarlılık: aynı şeye iki
sayfada iki ad vermemek.

## Kütüphane kavramları

| Türkçe | İngilizce | Ne |
|---|---|---|
| **öznitelik** | feature | Metinden çıkarılan tek bir sayı (`ttr`, `atesman`) |
| **anahtar** | key | Özniteliğin adı; sözlükteki `dict` anahtarı |
| **grup** | group | Özniteliklerin 13 kümesinden biri (`lexical`, `readability`…; `custom_ngrams` ile 14) |
| **künye** | citation | Kısa kaynak işaretçisi — yöntem bölümüne parantez içi |
| **kaynakça kaydı** | reference | Tam bibliyografik kayıt — kaynakçaya kopyalanan |
| **kayıt defteri** | registry | Bütün öznitelik üstverisinin durduğu tek yer |
| **boru hattı** | pipeline | Ham metinden sayılara giden adımlar zinciri |
| **ölçek** | scale | Değerin türü: `ratio_0_1`, `score`, `count`… |
| **parça** | segment | `segment_text` ile kesilmiş metin dilimi |
| **etiket** | label | Korpusta klasör adı; yazar, sınıf ya da deney kolu |

## Ölçüm terimleri

| Türkçe | İngilizce | Ne |
|---|---|---|
| **kelime** | word | Boşlukla ayrılan, kenar noktalaması atılan, harf ya da rakam içeren birim; kütüphanenin saydığı kelime |
| **cümle** | sentence | `. ? ! …` ile biten birim; `:` yalnız ardından yeni cümle geliyorsa |
| **spaCy tokenı** | spaCy token | Modelin metni böldüğü birim; noktalama ayrı tokendır. `segment_text` bunu sayar |
| **lemma** | lemma | Kelimenin sözlük biçimi; Türkçede Zeyrek'ten, İngilizcede spaCy'den |
| **sözcük türü etiketi** | POS tag | UD'nin 17 etiketinden biri (`NOUN`, `VERB`, `ADJ`…) |
| **n-gram** | n-gram | Ardışık kelimelerden oluşan öbek; `custom_ngrams` ile sayılır |
| **tip** | type | Metindeki farklı kelimelerden biri |
| **token** | token | Tip/token oranında: metindeki kelime örneklerinden biri |
| **tip/token oranı** | type-token ratio (TTR) | Tip sayısı / token sayısı |
| **hapax** | hapax legomenon | Metinde bir kez geçen kelime |
| **vuruş** | stroke / character | Boşluk dışı her karakter (ARI'nin girdisi) |
| **pencere** | window | Kayan hesapta bir seferde bakılan kelime sayısı |
| **eşik** | threshold | Bir sınıflamayı başlatan sınır değer |
| **yüzdelik** | percentile | Dağılımda altında verinin %n'inin kaldığı değer |
| **kalibrasyon** | calibration | Bir eşiği veriden türetme işlemi |

## Doğrulama terimleri

| Türkçe | İngilizce | Ne |
|---|---|---|
| **birebir** | exact | Kaynağın sayısıyla tolerans içinde aynı (✅) |
| **belgelenmiş sapma** | documented deviation | Fark var, nedeni yazılı (🟡) |
| **uyuşmazlık** | mismatch | Açıklanmamış fark (❌) |
| **uçtan uca** | end-to-end | Kaynağın metni boru hattından geçirilerek sınandı |
| **formül** | formula | Girdiler doğrudan verilerek sınandı |
| **aktaran** | as cited in | Birincil kaynağa ulaşılamadı, ikincilden alındı |
| **yayın kapısı** | release gate | Sağlanmazsa sürüm çıkmayan koşul |

## Neden "öznitelik", "özellik" değil

"Özellik" gündelik dilde bir niteliktir ("bu metnin özelliği uzun
olması"). Burada kastedilen şey **ölçülmüş bir değişkendir** ve
istatistiksel modele girer. Türkçe nicel dilbilim ve makine öğrenmesi
yazınında bunun yerleşik karşılığı "öznitelik"tir.

## Neden "künye" ve "kaynakça kaydı" ayrı

İngilizcede ikisi de citation/reference diye geçebiliyor ve karışıyor.
Kütüphanede bunlar **iki ayrı alandır**:

```python
tlf.describe_feature("mattr")["citation"]   # künye: kısa işaretçi
tlf.describe_feature("mattr")["references"] # kaynakça kaydı: tam kaynakça kaydı
```

Künyeyi metin içinde, kaynakça kaydını kaynakçada kullanırsınız.
