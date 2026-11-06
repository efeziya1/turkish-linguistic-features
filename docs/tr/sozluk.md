# Terim sözlüğü

Belgeler boyunca bu karşılıklar kullanılır. Terimler, aracın anlatıldığı tezdeki terimlerle
aynıdır. Her sayfada bir terim ilk geçtiğinde İngilizcesi parantez içinde verilir:
"türce (İng. *token*)". Hatırlamadığınız bir terim olursa buraya bakın.

## Aracın kavramları

| Türkçe | İngilizce | Ne |
|---|---|---|
| **öznitelik** | feature | Metinden çıkarılan tek bir sayı (`ttr`, `atesman`) |
| **anahtar** | key | Özniteliğin adı; dönen sözlükteki `dict` anahtarı |
| **grup** | group | Özniteliklerin 12 kümesinden biri (`lexical`, `readability`…; `custom_ngrams` ile 13) |
| **künye** | citation | Kısa kaynak gösterimi; yöntem bölümünde parantez içinde verilen |
| **kaynakça kaydı** | reference | Eserin tam kaydı; kaynakçaya kopyalanan |
| **öznitelik dizini** | registry | Her özniteliğin tanımının, formülünün ve künyesinin durduğu tek yer |
| **çözümleme hattı** | pipeline | Ham metinden sayılara giden adımlar: spaCy, Zeyrek ve aracın kuralları |
| **ölçek** | scale | Değerin türü: `ratio_0_1`, `score`, `count`… |
| **parça** | segment | `segment_text` ile kesilmiş metin dilimi |
| **etiket** | label | Derlemde klasör adı; yazar, sınıf ya da deney kolu |
| **parametre** | parameter | Kullanıcının değiştirebildiği pencere boyu, eşik ya da örneklem sayısı (`FeatureParams`) |
| **sabit** | constant | Formülde sabit duran sayı: MTLD'nin 0,72'si, Brunet'nin 0,172'si, okunabilirlik formüllerinin katsayıları |
| **sözcük dizisi** | n-gram | Kullanıcının verdiği, yan yana gelen sözcükler, sözlükbirimler ya da sözcük türü etiketleri; `custom_ngrams` ile sayılır |

## Dil işleme

| Türkçe | İngilizce | Ne |
|---|---|---|
| **türce** | token | spaCy'nin metni böldüğü en küçük birim; noktalama da ayrı türcedir. Tür/türce oranında ise metindeki her sözcük bir türcedir |
| **tür** | type | Metindeki farklı sözcüklerden biri; `ev` üç kez geçse de bir türdür |
| **tür/türce oranı** | type-token ratio (TTR) | Tür sayısı / türce sayısı |
| **sözlükbirim** | lemma | Sözcüğün sözlükteki biçimi; Türkçede Zeyrek'ten, İngilizcede spaCy'den |
| **biçimbirim** | morpheme | Zeyrek çözümlemesindeki kök ya da ek |
| **sözcük türü** | part of speech | Ad, eylem, sıfat… |
| **sözcük türü etiketi** | POS tag | Evrensel Bağımlılıklar'ın 17 etiketinden biri (`NOUN`, `VERB`, `ADJ`…) |
| **bağımlılık** | dependency | Ayrıştırıcının tümcedeki iki sözcük arasında kurduğu bağ |
| **ayrıştırıcı** | parser | Tümcenin bağımlılık yapısını çıkaran bileşen (spaCy) |
| **çözümleyici** | analyzer | Sözcüğü biçimbirimlerine ayıran bileşen; bu araçta Zeyrek |
| **etiketleyici** | tagger | Sözcüklere sözcük türü etiketi veren bileşen (spaCy) |
| **türceleyici** | tokenizer | Metni türcelere bölen bileşen |
| **belirsizlik giderme** | disambiguation | Bir sözcüğün birden çok çözümlemesinden bağlama uyanı seçmek; Zeyrek bunu yapmaz |
| **karma tohumu** | hash seed | Python'un her çalıştırılışta değişen iç sayısı; `PYTHONHASHSEED=0` ile sabitlenir |
| **tümce sınırı** | sentence boundary | Bir tümcenin bittiği yer; aracın kendi kuralıyla bulunur |
| **içeriksel sözcük** | content word | Ad, özel ad, eylem, sıfat ya da belirteç |
| **belirteç** | adverb | Zarf |
| **sesbirim** | phoneme | Dilde anlam ayırt eden ses birimi; araç sesbirimle değil harfle çalışır |
| **seslem** | syllable | Okunabilirlik formüllerinin ve seslem özniteliklerinin saydığı birim |
| **çevriyazı** | transcription | Seslerin IPA gibi bir yazıyla gösterimi |

## Ölçüm

| Türkçe | İngilizce | Ne |
|---|---|---|
| **sözcük** | word | Boşlukla ayrılan, kenar noktalaması atılan, harf ya da rakam içeren birim; aracın saydığı sözcük |
| **tümce** | sentence | `. ? ! …` ile biten birim; `:` yalnız ardından yeni tümce geliyorsa |
| **derlem** | corpus | Birlikte çözümlenen metinler |
| **ölçü** | measure | Alanyazında önerilmiş bir hesaplama (MTLD, Ateşman formülü) |
| **sözcüksel çeşitlilik** | lexical diversity | Metinde ne kadar farklı sözcük kullanıldığı (TTR, MATTR, MTLD) |
| **sözcüksel zenginlik** | lexical richness | Sözcük dağarının genişliği; çeşitlilik ve sıklık ölçülerini kapsar |
| **sözcüksel yoğunluk** | lexical density | İçeriksel sözcüklerin bütün sözcükler içindeki payı |
| **sözdizimsel karmaşıklık** | syntactic complexity | Tümce yapısının ne kadar karmaşık olduğu |
| **bağımlılık uzaklığı** | dependency distance | Birbirine bağlı iki sözcüğün tümcedeki konumları arasındaki fark |
| **hiyerarşik uzaklık** | hierarchical distance | Bir sözcüğün bağımlılık ağacında köke uzaklığı |
| **okunabilirlik** | readability | Bir metni okumanın ne kadar kolay ya da güç olduğu |
| **okunabilirlik formülü** | readability formula | Okunabilirliği sözcük ve tümce özelliklerinden kestiren formül |
| **h-noktası** | h-point | Sıra–sıklık dağılımında sıranın sıklığa eşit olduğu nokta |
| **sıra–sıklık** | rank–frequency | Sözcüklerin sıklık sırasına göre dizildiği dağılım |
| **tematik yoğunlaşma** | thematic concentration | Metnin birkaç içeriksel sözcükte ne kadar toplandığı |
| **hapax** | hapax legomenon | Metinde bir kez geçen sözcük |
| **vuruş** | stroke | Boşluk dışı her karakter (ARI'nin girdisi) |
| **pencere** | window | Bir seferde ölçülen ardışık sözcükler |
| **eşik** | threshold | Bir sınıflamayı başlatan sınır değer |
| **yüzdelik** | percentile | n. yüzdelik: değerlerin %n'i ona eşit ya da ondan küçük |
| **ortanca** | median | Sıraya dizilen değerlerin ortasındaki değer (50. yüzdelik) |
| **kalibrasyon** | calibration | Bir eşiği derlemden ölçerek belirleme |
| **sayı değil (NaN)** | not a number | "Bu metinde bu sayı hesaplanamaz" işareti |

## Doğrulama

| Türkçe | İngilizce | Ne |
|---|---|---|
| **alanyazın** | literature | Konuyla ilgili yayınların bütünü |
| **alanyazın ölçüsü** | literature measure | Alanyazında adı olan, künyeli ölçü |
| **etiket oranı** | tag ratio | Dış bir etiket şemasının bir kategorisinin payı |
| **yalın tanım** | plain definition | Kaynağı olmayan tanım |
| **araca özgü** | tool-specific | Formülü kaynaktan, hangi veriye uygulanacağı bu araçtan |
| **kalibre edilmiş** | calibrated | Eşiği bu aracın kalibrasyonundan |
| **birincil kaynak** | primary source | Ölçüyü öneren yayının kendisi |
| **ikincil kaynak** | secondary source | Ölçüyü başka bir yayından aktaran kaynak |
| **aktaran (akt.)** | as cited in | Birincil kaynağa ulaşılamadı, ikincil kaynaktan alındı |
| **karşılaştırma** | comparison | Raporda bir öznitelik ile kaynağın yayımladığı bir sayının eşleştirilmesi |
| **örtüşen** | match | Kaynağın sayısıyla tolerans içinde aynı (✅) |
| **belgelenmiş sapma** | documented deviation | Fark var, nedeni yazılı (🟡) |
| **açık** | open | Kaynağın yayımladığı bir sayı henüz bulunamadı (🔍) |
| **uyuşmazlık** | mismatch | Nedeni açıklanmamış fark (❌) |
| **göreli tolerans** | relative tolerance | İzin verilen fark, yayımlanan değerin yüzdesi olarak (%1) |
| **uçtan uca karşılaştırma** | end-to-end comparison | Kaynağın metni çözümleme hattından geçirilerek sınandı |
| **formül karşılaştırması** | formula comparison | Formüle girdiler doğrudan verilerek sınandı |
| **sınama veri seti** | test dataset | Bir yazılımı sınamak için hazırlanmış, değerleri bilinen metinler (TOMA veri seti) |
| **yayın kapısı** | release gate | Sağlanmazsa sürüm çıkmayan koşul |
