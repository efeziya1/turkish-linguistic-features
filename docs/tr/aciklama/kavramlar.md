# Kavramlar

## Öznitelik

**Öznitelik** (İng. *feature*), bir metinden çıkarılan tek bir sayıdır. `ttr`,
`word_len_mean`, `atesman`: her biri bir özniteliktir. Adları küçük harfle, sözcükler alt çizgiyle
ayrılarak yazılır.

Türkçedeki 217 öznitelik, dayandıkları kaynak bakımından beş türe ayrılır:

| Tür | Sayı | Ne | Örnek |
|---|---:|---|---|
| **Alanyazın ölçüsü** (İng. *literature measure*) | 136 | Alanyazında önerilmiş bir ölçü; künyesi vardır | `mattr`, `mtld`, `atesman` |
| **Etiket oranı** (İng. *tag ratio*) | 66 | spaCy'nin ya da Akana'nın sözcüklere verdiği bir etiketin metindeki payı; künyesi etiketi tanımlayan şemadır, ölçünün kendisi değil | `pos_noun_ratio` (Evrensel Bağımlılıklar), `akana_case_loc_ratio` (Akana) |
| **Yalın tanım** (İng. *plain definition*) | 11 | Alanyazında adı olan bir ölçüye dayanmaz; künyesi yoktur | `question_sent_ratio`: soru işaretiyle biten tümcelerin payı |
| **Araca özgü** (İng. *tool-specific*) | 2 | Formülü alanyazından alınmıştır; hangi veriye uygulanacağını araç belirler | `sent_len_entropy`: Shannon entropisinin tümce uzunluklarına uygulanması |
| **Kalibre edilmiş** (İng. *calibrated*) | 2 | Eşiği bu aracın derlemlerde yaptığı ölçümden gelir | `short_sent_ratio`, `long_sent_ratio` |

217 anahtarın 206'sının künyesi vardır, 11'inin yoktur. Bu ayrım, hangi özniteliğin
kaynağında yayımlanmış bir örnekle sınanabileceğini de belirler
([Doğrulama sistemi](dogrulama.md)).

Araç bir okunabilirlik formülünün yalnız sonucunu vermez; formüle giren ölçüleri, sözgelimi
ortalama tümce uzunluğunu ve sözcük başına seslem sayısını, ayrı öznitelikler olarak da
verir. Yeni bir formül kurulurken değişken adayları bu ölçülerden ve aracın öteki
özniteliklerinden seçilip sınanabilir.

## Anahtar adları

Ad, özniteliğin ne ölçtüğünü söyler:

| Ad | Anlamı | Örnek |
|---|---|---|
| `…_ratio` | 0 ile 1 arası pay | `hapax_ratio`, `pos_noun_ratio` |
| `…_mean`, `…_median` | Ortalama, ortanca (İng. *median*) | `sent_len_mean`, `sent_len_median` |
| `…_count` | Sayım | `word_count`, `sent_count`, `lemma_count` |
| Alanyazındaki adı | Adı yerleşik ölçü; `_ratio` almaz | `ttr`, `mattr`, `yule_k`, `posddev` |

Biçimbilimsel öznitelikler iki çözümleyiciden (İng. *analyzer*) gelir. spaCy'nin
Evrensel Bağımlılıklar etiketlerinden gelenler öneksizdir (`case_loc_ratio`), Akana'dan
gelenler `akana_` ile başlar (`akana_case_loc_ratio`). İkisi aynı sayıyı vermez:
`case_loc_ratio` durum etiketi taşıyan sözcükler içinde bulunma durumunun
payıdır, `akana_case_loc_ratio` ise çözümlenen bütün sözcükler içindeki payı. Akana
evrensel etiketlerin ayırmadığı ayrımları da verir: -DI ve -mIş geçmişi ayrıdır
(`akana_tense_past_def_ratio`, `akana_tense_past_nar_ratio`); spaCy'de ikisi tek
`tense_past_ratio`'dur.

On `punct_…_ratio` anahtarı (`punct_comma_ratio`, `punct_dash_ratio` …) her işaret
türünün bütün noktalama işaretleri içindeki payıdır; toplamları 1 eder. Metinde ne
kadar noktalama olduğunu `punct_char_ratio` söyler (noktalama işaretleri / karakterler).

## Grup

Öznitelikler 12 gruba ayrılır (`custom_ngrams` verilince oluşan `ngram_*`
anahtarlarıyla 13). Grup hem düzenlemeye hem seçmeye yarar: Yalnız gereken gruplar
hesaplatılabilir.

```python
oz = tlf.analyze(metin, lang="tr", groups=["readability", "lexical"])
```

Gruplar, içerikleri ve büyüklükleri [Tek metni analiz et](../nasil/tek-metin.md)
sayfasındadır.

## Kalıptan üretilen anahtarlar

Bazı anahtarlar tek tek yazılmamıştır, kalıptan üretilir:

- `char_*`: harf sıklık vektörü; iki dilde aynı 32 harfin her biri için bir anahtar
  (Türkçe ve İngilizce alfabelerin birleşimi: `char_a_ratio`, `char_ç_ratio` … `char_z_ratio`)
- `ngram_*`: `custom_ngrams` ile verilen sözcük dizilerinin (İng. *n-grams*) sayaçları
  ([nasıl](../nasil/tek-metin.md#kendi-sozcuk-dizilerinizi-sayn))

`describe_feature("char_a_ratio")` çağrısında `formula` ve `requires` alanları
**grup düzeyinde** genel ifadedir, tek harfe özel değildir.

## Ölçek (`scale`)

Her özniteliğin bir ölçeği (İng. *scale*) vardır:

| Ölçek | Anlamı | Örnek |
|---|---|---|
| `ratio_0_1` | 0 ile 1 arası pay | `ttr`, `mattr` |
| `score` | Formülün ürettiği puan; sabit bir aralığı yok | `atesman`, `yule_k`, `mtld` |
| `length` | Birimi karakter, sözcük ya da tümce olan ortalama uzunluk | `word_len_mean`, `sent_len_mean` |
| `nats` | Nat cinsinden entropi (doğal logaritma; araçtaki bütün logaritmalar ln) | `entropy`, `punct_entropy` |
| `count` | Sayım | `lemma_count` |

## Sözcük ve tümce

Bir özniteliğin değeri sözcüğün, tümcenin ve seslemin nasıl sayıldığına bağlıdır.
Öznitelikler sözcüğü ve tümceyi aracın kendi kuralıyla sayar, modelin türcesiyle
(İng. *token*) değildir. Bunlar **varsayılan sözcük** ve **varsayılan tümcedir**; bu adları
kullanan öbür sayfalar buraya gönderir.

### Sözcük

Metin boşluklardan bölünür. Her parçanın kenarındaki noktalama atılır (`. , ; : ! ? …`,
tırnaklar, ayraçlar, çizgiler, `/`, `*`). Kalan birim **en az bir harf ya da rakam
içeriyorsa sözcüktür** (İng. *word*); içermiyorsa sayılmaz.

| Metin | Sözcükler |
|---|---|
| `Kitabı okudu.` | `Kitabı`, `okudu`: nokta sözcüğe dahil değil |
| `e-posta`, `Ali'nin`, `%50` | her biri bir sözcük: sözcüğün içindeki işaret kalır |
| `1999 yılında` | `1999`, `yılında`: sayı da sözcüktür |
| `Bu — bir deneme ...` | `Bu`, `bir`, `deneme`: tek başına duran `—` ve `...` sözcük değil |
| `3. kat` · `Sonuç 3.` | Yalnız Türkçede: ardından sözcük ya da virgül gelen `3.` tek sözcüktür (sıra sayısı); tümce sonunda `3` olur |
| `geldi.Sonra` · `3.köprü` | Boşluk unutulmuşsa noktalamayla bitişik iki sözcük iki sözcüktür: `geldi`, `Sonra` · `3.`, `köprü`. Tek harfli baş harf (`G.Saray`), adres (`kariyer.net`), sayı (`1.5`) ve tırnak ya da kesmeden sonra gelen ek (`“kampusu!”na`) bölünmez |

Sıra sayısı kuralı Türkçeye özgüdür, çünkü Türkçede sıra sayısı rakamdan sonra nokta konarak
yazılır; İngilizcede `3rd` yazıldığı için bu kurala gerek yoktur.

Araç sözcük sayarken noktalamayı etikete bakarak değil, sözcüğün kenarındaki işaretleri
atarak ayıklar. `syntactic` grubu dışındaki her öznitelik bu sözcüğü sayar.

### Tümce

Tümceyi (İng. *sentence*) bitirenler:

- **`.` `?` `!` `…`**: her zaman tümce bitirir. Üç nokta `...` diye de yazılabilir.
- **Art arda gelen işaretler** (`?!`, `!!!`) tek bir tümce sonu sayılır.
- **`:`**: ardından büyük harfle başlayan bir sözcük, tırnak, çizgi ya da açılış ayracı
  geliyorsa tümce bitirir. Küçük harf ya da sayı geliyorsa (liste, açıklama, `10:30`)
  bitirmez.
- **metnin sonu**: işaret olmasa da.

Türkçede kısaltmadan sonraki nokta:

- **Büyük harfle yazılan kısaltmada** (`Dr.`, `Cad.`, `Ltd.`) tümce bitirmez; bu kısaltmalar
  ardındaki ada bağlanır.
- **Küçük harfle yazılan kısaltmada** (`vb.`, `dk.`, `km.`) ardından büyük harf gelirse tümce
  bitirir, küçük harf gelirse bitirmez.
- **`bkz.`** (bakınız) tümce bitirmez, ardından büyük harf gelse de: Ardından gösterilen yer
  gelir (`bkz. Ek 2`).

İngilizcede `Dr.` gibi tek birim yazılan kısaltma tümce bitirmez.

| Metin | Tümce |
|---|---|
| `Geldi. Gitti!` | 2 |
| `Ne dedin?! Bilmiyorum.` | 2 |
| `Şunu söyledi: Yarın geliyorum.` | 2: `:` sonrası büyük harf |
| `Üç şey aldı: ekmek, süt ve peynir.` | 1: `:` sonrası küçük harf |
| `Toplantı 10:30'da başladı.` | 1 |
| `Dr. Ayşe geldi.` | 1 |
| `Elma, armut vb. Sonra eve döndük.` | 2: `vb.` sonrası büyük harf |
| `Ayrıntı için bkz. Ek 2.` | 1: `bkz.` tümce bitirmez |
| `Geldi ve gitti` | 1: işaret yok, metin bitiyor |

İki noktaya bu koşulun konmasının nedeni, iki noktanın her zaman tümce sınırı olmamasıdır.
Türkçe köşe yazılarında (4.321 yazı) iki noktaların %93,9'undan sonraki türce büyük harf,
tırnak, çizgi ya da açılış ayracıyla başlar; İngilizce köşe yazılarında (1.485 yazı) bu oran
%62,4'tür. Koşul, ardından küçük harfle başlayan bir liste ya da açıklama gelen iki noktayı
tümce sonu saymamak için konmuştur. Kural iki dilde aynıdır.

Tümce uzunluğu tümcedeki sözcük sayısıdır. Yalnız sayıdan oluşan tümce de tümcedir:
`Bu bir tümce. 1999! Bitti.` 3 tümcedir. Bütün öznitelikler ve `text_units` tümceyi aynı
biçimde sayar.

Türkçede rakamdan sonraki nokta, ardından bir sözcük geliyorsa sıra sayısının noktası sayılır
ve tümce bitirmez (`3. kat`). Bu yüzden `Yıl 1999. Bitti.` tek tümcedir: Yazıda `1999. Bitti`
ile `2. Dünya Savaşı` aynı biçimdedir ve kural ikisini ayırt edemez.

İki tür öznitelik bu kuralı kullanmaz:

- bazı **okunabilirlik formülleri** kendi kaynaklarının sayım kuralını izler
  (aşağıdaki tablo);
- **sözdizimsel öznitelikler** (`syntactic`) spaCy'nin türcelerini ve ayrıştırıcısının
  (İng. *parser*) bulduğu tümceleri kullanır.

### Okunabilirlik formüllerinde sayım

Bazı okunabilirlik formüllerinin kaynağı sözcüğün ya da tümcenin nasıl sayılacağını kendisi
belirtir. Araç bu formüllerde genel kural yerine kaynağın kuralını izler; böylece formül,
kaynağın hesapladığı biçimde hesaplanır.

| Formül | Sözcük | Tümce | Kaynak |
|---|---|---|---|
| Çetinkaya-Uzun | Tek başına duran simgeler (`%`, `$`, `+` gibi) de sözcüktür | İki nokta her durumda, ayraçlar da tümce bitirir | Çetinkaya (2010) s.93 |
| Flesch, Flesch-Kincaid | Tek başına duran simgeler de sözcüktür | Noktalı virgül de tümce bitirir | Kincaid vd. (1975) s.38 |
| ARI | Tek başına duran simgeler de sözcüktür | Genel kural | Kincaid vd. (1975) s.33 |
| Kalyoncu'nun dört formülü ve bileşenleri | Sayı, okunuşundaki sözcüklerle sayılır: `1968`, "bin dokuz yüz altmış sekiz" olarak 5 sözcüktür | Genel kural | Kalyoncu (2025) s.xiii |

Tabloda olmayan formüller (Ateşman, Bezirci-Yılmaz, SMOG, Coleman-Liau, LIX) genel kuralı
kullanır. Seslemler (İng. *syllables*) bütün formüllerde okunuşa göre sayılır: `1918`
"bin dokuz yüz on sekiz" olarak 7 seslemdir, `%50` ve `TBMM` 4'er seslemdir. Ayrıntı:
[Sınırlılıklar](sinirliliklar.md).

### Sözcüğün etiketi

spaCy metni kendi kurallarıyla böldüğü için bir sözcük birden çok türceye denk gelebilir:
`Ankara-İstanbul` sözcüğü `Ankara`, `-` ve `İstanbul` türcelerine ayrılır. Bu durumda sözcük
bir kez sayılır; sözcük türü etiketi (İng. *POS tag*), biçimbilimsel etiketleri ve
sözlükbirimi (İng. *lemma*) içindeki noktalama olmayan ilk türceden alınır. Çift tırnak
(`"` `“` `”` `«` `»`) modelin verdiği etiketten bağımsız olarak burada hep noktalama sayılır.
Türkçe sözlükbirim Akana'nın sözlük maddesidir, İngilizce sözlükbirim spaCy'ninkidir.

Türkçede özel adları Akana'nın ad tanıyıcısı (İng. *named entity recognizer*) bulur. Ad
tanıyıcının kişi, yer ya da kurum adı dediği her sözcük, spaCy hangi etiketi vermiş olursa
olsun özel ad (`PROPN`) sayılır; `Mustafa Kemal` gibi birden çok sözcüklü bir adın her sözcüğü
de öyle sayılır. Bunun nedeni, spaCy Türkçe modelinin `Derya`, `Almanya'da` gibi sözcükleri çoğu zaman
`PROPN` etiketlememesidir. Bağımlılık çözümlemesine dayanan `syntactic` grubu spaCy'nin türcelerini okuduğu
için bundan etkilenmez.

### Çeşitlilik ölçülerinin sayım birimi

Sözcüksel çeşitlilik (İng. *lexical diversity*) ölçülerinde tür (İng. *type*), sözcüğün
küçük harfe çevrilmiş yüzey biçimidir. Böylece tümce başında büyük harfle yazılan sözcük ayrı
bir tür olmaz. Türkçede küçük harfe çevirme Türkçenin kuralıyla yapılır (I → ı, İ → i);
yazılımların varsayılan dönüşümü `IŞIK`'ı `işik`'e çevirdiği için bu ayrıca gözetilir.

Tür yüzey biçime dayandığı için çekimli biçimler ayrı türdür: `kitap` ile `kitaplar` iki
ayrı türdür. Bu, aracın tasarım kararıdır. Bunun istisnası, sözlükbirim sayan `*_variation`
ölçüleri ve `lemma_count`'tur.
Kaynağı başka birim kullanan ölçülerde (`brunet_w`, `herdan_c`, `yule_k`) fark künyede
yazılıdır.

### İçeriksel sözcük

İçeriksel sözcük (İng. *content word*), sözcük türü etiketi `NOUN`, `PROPN`, `VERB`, `ADJ`
ya da `ADV` olan sözcüktür: ad, özel ad, eylem, sıfat ve belirteç. Yardımcı sözcükler
(`AUX`) eylem sayılmaz. Bu tanımı sözcüksel yoğunluk (`lexical_density`), sözcük türü
çeşitliliği, tematik yoğunlaşma ve sıklık ölçüleri kullanır.

Tanım Lu'nun (2012) tanımıdır, bir farkla: Lu (2012, s.192) belirteçlerden yalnız sıfattan
türeyenleri sayar; araç bütün belirteçleri sayar, çünkü sözcük türü etiketleyicisi
(İng. *tagger*) belirteçlerin türünü ayırmaz ve bu ayrım bir sözcük listesi ya da
biçimbirime dayalı bir kural gerektirir. QUITA ise hangi sözcüklerin içeriksel sayılacağını
araştırmacıya bırakır (Kubát vd. 2014, s.50–51).

Bir özniteliğin hangi kuralı kullandığını
`describe_feature(anahtar)["definitions"]` söyler.

## Çözümleme hattı

`analyze` çağrılınca metin dört aşamadan geçer; bu adımların bütününe çözümleme hattı
(İng. *pipeline*) denir:

```text
ham metin
   ↓  1. spaCy (tr_core_news_md / en_core_web_sm)
türce · sözcük türü etiketi · biçimbilimsel etiket · bağımlılık ağacı · İngilizce sözlükbirim
   ↓  2. Akana (yalnız Türkçe)
biçimbirim çözümlemesi · Türkçe sözlükbirim · özel adlar
   ↓  3. aracın kuralları
sözcük ve tümce sınırları; her sözcük etiketini kendi türcesinden alır
   ↓  4. öznitelik hesaplayıcıları
217 sayı (İngilizcede 187)
```

Akana, Türkçe biçimbirim çözümleyicisidir: Zemberek'in kurallarını taşıyan, Rust ile yazılmış ve
Python'dan çağrılan bir pakettir. Java gibi ek bir ortam gerektirmez. Bir sözcüğün birden çok
çözümlemesi varsa Akana'nın belirsizlik gidericisi (İng. *disambiguator*) birini seçer:
Çözümlemeleri ağaç bankalarından çıkarılmış sıklıklarına göre sıralar ve tümcedeki yakın
sözcüklere bakan birkaç kuralla düzeltir.

**spaCy modeli ve Akana sonuçların parçasıdır.** Biri değişirse ona dayanan öznitelikler de
değişir. Türkçedeki 217 öznitelikten 105'i bu iki çözümleyiciden en az birine dayanır; kalan
112'si yalnız aracın kendi kurallarıyla hesaplanır. Bu yüzden bir sonucu yeniden
üretebilmek için aracın sürümüyle birlikte spaCy modelinin ve Akana'nın sürümü de verilmelidir.
Aracın sınandığı sürümler: Python 3.12, spaCy 3.8.16, `tr_core_news_md` 1.0 (model
sürümü 3.4.2), `en_core_web_sm` 3.8.0, Akana 0.12.0.

## `FeatureParams`

Pencere boyları, eşikler ve örneklem sayıları burada durur. Ayrıntı:
[Eşikleri değiştir](../nasil/parametreler.md).

Tümce eşikleri (`short_sent_threshold`, `long_sent_threshold`) **her dil için ayrı
ölçülmüştür** (TR 4/17, EN 8/32).

## Öznitelik dizini

Öznitelik dizini (İng. *registry*), her özniteliğin adını, ne ölçtüğünü, formülünü,
ölçeğini, parametrelerini, hesaplanması için gereken en az veriyi, künyesini ve formüldeki
terimlerin araçtaki tanımlarını tek bir yerde tutar. `describe_feature`,
[başvuru bölümü](../../reference/index.md) ve [doğrulama raporu](../../dogrulama-raporu.md)
aynı kaynaktan okur; bu yüzden üçündeki bilgi hep aynıdır.

Öznitelik dizini **İngilizcedir**. Tanımlar, formüller ve künyeler tek dilde
tutulur ki çoğu İngilizce olan kaynaklarla karşılaştırırken araya çeviri katmanı girmesin.
