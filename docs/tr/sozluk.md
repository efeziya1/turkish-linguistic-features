# Terim sözlüğü

Doküman boyunca bu karşılıklar kullanılır. Amaç tutarlılık: aynı şeye iki
sayfada iki ad vermemek.

## Kütüphane kavramları

| Türkçe | İngilizce | Ne |
|---|---|---|
| **öznitelik** | feature | Metinden çıkarılan tek bir sayı (`ttr`, `atesman`) |
| **anahtar** | key | Özniteliğin adı; sözlükteki `dict` anahtarı |
| **grup** | group | Özniteliklerin 12 kümesinden biri (`lexical`, `readability`…; `custom_ngrams` ile 13) |
| **künye** | citation | Kısa kaynak işaretçisi — yöntem bölümüne parantez içi |
| **kaynakça kaydı** | reference | Tam bibliyografik kayıt — kaynakçaya kopyalanan |
| **öznitelik dizini** | registry | Bütün öznitelik üstverisinin durduğu tek yer |
| **çözümleme hattı** | pipeline | Ham metinden sayılara giden adımlar zinciri: spaCy, Zeyrek ve kütüphanenin kuralları |
| **ölçek** | scale | Değerin türü: `ratio_0_1`, `score`, `count`… |
| **parça** | segment | `segment_text` ile kesilmiş metin dilimi |
| **etiket** | label | Derlemde klasör adı; yazar, sınıf ya da deney kolu |

## Ölçüm terimleri

| Türkçe | İngilizce | Ne |
|---|---|---|
| **sözcük** | word | Boşlukla ayrılan, kenar noktalaması atılan, harf ya da rakam içeren birim; kütüphanenin saydığı sözcük |
| **tümce** | sentence | `. ? ! …` ile biten birim; `:` yalnız ardından yeni tümce geliyorsa |
| **spaCy türcesi** | spaCy token | Modelin metni böldüğü birim; noktalama ayrı türcedir. Bağımlılık öznitelikleri bunu sayar |
| **sözlükbirim** | lemma | Sözcüğün sözlük biçimi; Türkçede Zeyrek'ten, İngilizcede spaCy'den |
| **POS etiketi** | POS tag | UD'nin 17 etiketinden biri (`NOUN`, `VERB`, `ADJ`…) |
| **n-gram** | n-gram | Ardışık sözcüklerden oluşan öbek; `custom_ngrams` ile sayılır |
| **tür** | type | Metindeki farklı sözcüklerden biri |
| **türce** | token | Tür/türce oranında: metindeki sözcük örneklerinden biri |
| **tür/türce oranı** | type-token ratio (TTR) | Tür sayısı / türce sayısı |
| **seslem** | syllable | Okunabilirlik formüllerinin ve seslem özniteliklerinin saydığı birim |
| **biçimbirim** | morpheme | Zeyrek çözümlemesindeki kök ya da ek |
| **bağımlılık** | dependency | Ayrıştırıcının iki sözcük arasında kurduğu bağ |
| **derlem** | corpus | Birlikte çözümlenen metinler |
| **hapax** | hapax legomenon | Metinde bir kez geçen sözcük |
| **vuruş** | stroke / character | Boşluk dışı her karakter (ARI'nin girdisi) |
| **pencere** | window | Bir seferde ölçülen ardışık birimlerden oluşan öbek |
| **eşik** | threshold | Bir sınıflamayı başlatan sınır değer |
| **yüzdelik** | percentile | n. yüzdelik: değerlerin %n'i ona eşit ya da ondan küçük |
| **kalibrasyon** | calibration | Bir eşiği veriden türetme işlemi |

## Doğrulama terimleri

| Türkçe | İngilizce | Ne |
|---|---|---|
| **alanyazın ölçüsü** | literature measure | Alanyazında adı olan, künyeli ölçü |
| **etiket oranı** | tag ratio | Dış bir etiket şemasının kategorisinin payı |
| **yalın tanım** | plain definition | Kaynağı olmayan tanım |
| **araca özgü** | tool-specific | Formülü kaynaktan, uygulaması bu kütüphaneden |
| **kalibre edilmiş** | calibrated | Eşiği bu kütüphanenin kalibrasyonundan |
| **karşılaştırma** | comparison | Raporda bir öznitelik ile bir kaynak sayısının eşleşmesi |
| **örtüşen** | match | Kaynağın sayısıyla tolerans içinde aynı (✅) |
| **belgelenmiş sapma** | documented deviation | Fark var, nedeni yazılı (🟡) |
| **uyuşmazlık** | mismatch | Açıklanmamış fark (❌) |
| **uçtan uca** | end-to-end | Kaynağın metni çözümleme hattından geçirilerek sınandı |
| **formül** | formula | Girdiler doğrudan verilerek sınandı |
| **aktaran** | as cited in | Birincil kaynağa ulaşılamadı, ikincilden alındı |
| **yayın kapısı** | release gate | Sağlanmazsa sürüm çıkmayan koşul |
