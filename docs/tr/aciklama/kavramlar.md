# Kavramlar

## Öznitelik

**Öznitelik** (feature), bir metinden çıkarılan tek bir sayıdır. `ttr`,
`word_len_mean`, `atesman` — her biri bir öznitelik. Adları
`snake_case`'dir.

Öznitelik üç şeyden biridir:

1. **Alanyazın ölçüsü** — `mattr`, `yule_k`, `flesch_reading_ease`.
   Bunların künyesi vardır.
2. **Etiket oranı**: bir dış etiket şemasının kategorisi — `pos_noun_ratio` (UD),
   `zeyrek_case_loc_ratio` (Zeyrek). Künyesi şemaya bağlıdır, ölçünün kendisine
   değil.
3. **Yalın tanım** — `punct_dash_ratio` ("tire / bütün noktalama işaretleri"). Künyesi yoktur,
   çünkü kaynak gösterilecek bir alanyazın ölçüsü değildir.

214 anahtarın 203'ünün künyesi vardır, 11'inin yoktur.

## Anahtar adları

Ad, özniteliğin ne ölçtüğünü söyler:

| Ad | Anlamı | Örnek |
|---|---|---|
| `…_ratio` | 0 ile 1 arası pay | `hapax_ratio`, `pos_noun_ratio` |
| `…_mean`, `…_median` | Ortalama, medyan | `sent_len_mean`, `sent_len_median` |
| `…_count` | Sayım | `word_count`, `sent_count`, `lemma_count` |
| Alanyazındaki adı | Adı yerleşik ölçü; `_ratio` almaz | `ttr`, `mattr`, `yule_k`, `posddev` |

Biçimbilimsel öznitelikler iki çözümleyiciden gelir. spaCy'nin UD
etiketlerinden gelenler öneksizdir (`case_loc_ratio`), Zeyrek'ten gelenler
`zeyrek_` ile başlar (`zeyrek_case_loc_ratio`). İkisi aynı sayıyı vermez:
`case_loc_ratio` durum etiketi taşıyan sözcükler içinde bulunma durumunun
payıdır, `zeyrek_case_loc_ratio` çözümlenen bütün sözcükler içinde. Zeyrek
ayrıca -DI ve -mIş geçmişini ayırır (`zeyrek_tense_past_def_ratio`,
`zeyrek_tense_past_nar_ratio`); spaCy'de ikisi tek `tense_past_ratio`'dur.

On `punct_…_ratio` anahtarı (`punct_comma_ratio`, `punct_dash_ratio` …) her işaret
türünün bütün noktalama işaretleri içindeki payıdır; toplamları 1 eder. Metinde ne
kadar noktalama olduğunu `punct_char_ratio` söyler (noktalama işaretleri / karakterler).

## Grup

Öznitelikler 12 gruba ayrılır (`custom_ngrams` verirseniz oluşan `ngram_*`
anahtarlarıyla 14). Grup, hem düzenleme hem de seçim aracıdır:

```python
oz = tlf.analyze(metin, lang="tr", groups=["readability", "lexical"])
```

Gruplar ve büyüklükleri [Tek metni analiz et](../nasil/tek-metin.md)
sayfasında.

## Dinamik anahtarlar

Bazı anahtarlar tek tek yazılmamıştır, kalıptan üretilir:

- `char_*` — harf sıklık vektörü; alfabenin her harfi için bir anahtar
  (Türkçe 29: `char_a_ratio`, `char_ç_ratio` … `char_z_ratio`; İngilizce 26)
- `ngram_*` — `custom_ngrams` verirseniz oluşan n-gram sayaçları
  ([nasıl](../nasil/tek-metin.md#kendi-obeklerinizi-sayn))

`describe_feature("char_a_ratio")` çağırırsanız `formula` ve `requires` alanları
**grup düzeyinde** genel ifadedir, tek harfe özel değil.

## Ölçek (`scale`)

Her özniteliğin bir ölçeği vardır:

| Ölçek | Anlamı | Örnek |
|---|---|---|
| `ratio_0_1` | 0 ile 1 arası pay | `ttr`, `mattr` |
| `score` | Formülün ürettiği puan; sabit bir aralığı yok | `atesman`, `yule_k`, `mtld` |
| `length` | Birimi karakter, sözcük ya da tümce olan ortalama uzunluk | `word_len_mean`, `sent_len_mean` |
| `nats` | Nat cinsinden entropi (doğal logaritma; kütüphanedeki bütün logaritmalar ln) | `entropy`, `punct_entropy` |
| `count` | Sayım | `lemma_count` |

## Sözcük ve tümce

Öznitelikler sözcüğü ve tümceyi kütüphanenin kendi kuralıyla sayar, modelin
türcesiyle değil. Bunlar **varsayılan sözcük** ve **varsayılan tümcedir**; bu adları
kullanan diğer sayfalar buraya gönderir.

### Sözcük

Metin boşluklardan bölünür. Her parçanın kenarındaki noktalama atılır (`. , ; : ! ? …`,
tırnaklar, parantezler, tireler, `/`, `*`). Kalan birim **en az bir harf ya da rakam
içeriyorsa sözcüktür**; içermiyorsa sayılmaz.

| Metin | Sözcükler |
|---|---|
| `Kitabı okudu.` | `Kitabı`, `okudu` — nokta sözcüğe dahil değil |
| `e-posta`, `Ali'nin`, `%50` | her biri bir sözcük — sözcüğün içindeki işaret kalır |
| `1999 yılında` | `1999`, `yılında` — sayı da sözcüktür |
| `Bu — bir deneme ...` | `Bu`, `bir`, `deneme` — tek başına duran `—` ve `...` sözcük değil |
| `3. kat` · `Sonuç 3.` | Yalnız Türkçede: ardından sözcük ya da virgül gelen `3.` tek sözcüktür (sıra sayısı); tümce sonunda `3` olur |

`syntactic` grubu dışındaki her öznitelik bu sözcüğü sayar.

### Tümce

Tümceyi bitirenler:

- **`.` `?` `!` `…`** — her zaman. `...` ile `…` aynı işarettir. `?!` gibi art
  arda gelen işaretler tek tümce bitirir.
- **`:`** — yalnız ardından yeni bir tümce başlıyorsa: büyük harf, tırnak, tire ya da
  açılış parantezi. Ardından küçük harfli bir sözcük ya da sayı gelen iki nokta (liste,
  açıklama, `10:30`) tümce bitirmez.
- **metnin sonu** — işaret olmasa da.

Kısaltmadan sonraki nokta tümce **bitirmez**: `Dr.` tek birimdir. Türkçede `bkz.` gibi
listedeki bir kısaltmanın noktası, ancak ardından büyük harfle başlayan bir sözcük gelirse
tümce bitirir.

| Metin | Tümce |
|---|---|
| `Geldi. Gitti!` | 2 |
| `Ne dedin?! Bilmiyorum.` | 2 |
| `Şunu söyledi: Yarın geliyorum.` | 2 — `:` sonrası büyük harf |
| `Üç şey aldı: ekmek, süt ve peynir.` | 1 — `:` sonrası küçük harf |
| `Toplantı 10:30'da başladı.` | 1 |
| `Dr. Ayşe geldi.` | 1 |
| `Ayrıntı için bkz. şekil 3.` | 1 — `bkz.` sonrası küçük harf |
| `Geldi ve gitti` | 1 — işaret yok, metin bitiyor |

Tümce uzunluğu tümcedeki sözcük sayısıdır. Tümce uzunluğu öznitelikleri ve `sent_count`,
ortalamayı boş yere aşağı çekmesin diye hiç harf içermeyen tümceyi saymaz:
`Bu bir tümce. 1999. Bitti.` 2 tümcedir; `1999` dahil 5 sözcüğün hepsi sayılır.

İki tür öznitelik bu kuralı kullanmaz:

- bazı **okunabilirlik formülleri** kendi kaynaklarının sayım kuralını izler:
  Çetinkaya-Uzun `:` ve parantezde de tümce bitirir, Flesch formülleri `;`'de;
- **sözdizimsel öznitelikler** (`syntactic`) spaCy'nin türcelerini ve ayrıştırıcısının
  tümcelerini kullanır.

### Sözcüğün etiketi

POS etiketi, biçimbilimsel etiket ve sözlükbirim sözcüğün içindeki noktalama olmayan ilk
türceden gelir. Çift tırnak (`"` `“` `”` `«` `»`) modelin verdiği etiketten bağımsız olarak
burada hep noktalama sayılır.
Türkçe sözlükbirim Zeyrek'in sözlük maddesidir, İngilizce sözlükbirim spaCy'nin.

### Çeşitlilik ölçülerinin sayım birimi

Çeşitlilik ölçüleri yüzey biçim sayar: `kitap` ile `kitaplar` iki ayrı tiptir. Bu, aracın
tasarım kararıdır. İstisnalar `*_variation` ve `lemma_count`. Kaynağı başka birim kullanan
ölçülerde (`brunet_w`, `herdan_c`, `yule_k`) fark künyede yazılıdır.

### İçeriksel sözcük

İçeriksel sözcük POS etiketi `NOUN`, `PROPN`, `VERB`, `ADJ` ya da `ADV` olan sözcüktür
(`lexical_density`, sözcük türü çeşitliliği, tematik yoğunlaşma, sıklık ölçüleri). Lu
(2012, s.192) belirteçlerden yalnız sıfattan türeyenleri sayar; araç bütün belirteçleri
sayar, çünkü sözcük türü etiketleyicisi belirteçlerin türünü ayırmaz ve bu ayrım bir
sözcük listesi ya da biçimbirime dayalı bir kural gerektirir.

Bir özniteliğin hangi kuralı kullandığını
`describe_feature(anahtar)["definitions"]` söyler.

## Çözümleme hattı

`analyze` çağırdığınızda sırayla şunlar olur:

```text
ham metin
   ↓  spaCy (tr_core_news_md / en_core_web_sm)
türce · POS etiketi · biçimbilimsel etiket · bağımlılık ağacı · İngilizce sözlükbirim
   ↓  Zeyrek (yalnız Türkçe)
biçimbirim çözümlemesi · Türkçe sözlükbirim
   ↓  kütüphanenin kuralları
sözcük ve tümce sınırları; her sözcük etiketini kendi türcesinden alır
   ↓  öznitelik çıkarıcıları
214 sayı
```

**spaCy modeli sonuçların parçasıdır.** Model değişirse türceler, POS,
biçimbilimsel ve bağımlılık öznitelikleri değişir.

## `FeatureParams`

Pencere boyları, eşikler ve örneklem sayıları burada durur. Ayrıntı:
[Eşikleri değiştir](../nasil/parametreler.md).

Tümce eşikleri (`short_sent_threshold`, `long_sent_threshold`) **dile göre
kalibre edilmiştir** (TR 4/17, EN 8/32).

## Öznitelik dizini (registry)

Öznitelik adları, tanımları, formülleri, gereksinimleri ve künyeleri tek
bir yerde durur. `describe_feature`, [başvuru bölümü](../../reference/index.md)
ve [doğrulama raporu](../../dogrulama-raporu.md) aynı kaynaktan okur; bu yüzden
üçü birbiriyle hep aynıdır.

Öznitelik dizini **İngilizcedir**. Tanımlar, formüller ve künyeler tek dilde
tutulur ki kaynakla karşılaştırırken araya çeviri katmanı girmesin.
