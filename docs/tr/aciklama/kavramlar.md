# Kavramlar

## Öznitelik

**Öznitelik** (feature), bir metinden çıkarılan tek bir sayıdır. `ttr`,
`word_len_mean`, `atesman` — her biri bir öznitelik. Adları
`snake_case`'dir. Sürüm 1.0'a kadar anahtar adları değişebilir; değişen
adlar sürüm notlarında duyurulur.

Öznitelik üç şeyden biridir:

1. **Literatürde adı olan bir ölçü** — `mattr`, `yule_k`, `flesch_reading_ease`.
   Bunların künyesi vardır.
2. **Bir dış etiket şemasının kategorisi** — `pos_noun_ratio` (UD),
   `zeyrek_case_loc_ratio` (Zeyrek). Künyesi şemaya bağlıdır, ölçünün kendisine
   değil.
3. **Saf tanım** — `punct_dash_ratio` ("tire / bütün noktalama işaretleri"). Künyesi yoktur,
   çünkü tanımlanacak bir şey yoktur.

198 anahtarın 187'sinin künyesi vardır, 11'inin yoktur.

## Anahtar adları

Ad, özniteliğin ne ölçtüğünü okunur kılacak biçimde kurulur:

| Ad | Anlamı | Örnek |
|---|---|---|
| `…_ratio` | 0 ile 1 arası pay | `hapax_ratio`, `pos_noun_ratio` |
| `…_mean`, `…_median` | Ortalama, medyan | `sent_len_mean`, `sent_len_median` |
| `…_count` | Sayım | `lemma_count` |
| Literatürdeki adı | Adı yerleşik ölçü; `_ratio` almaz | `ttr`, `mattr`, `yule_k`, `posddev` |

Biçimbirim öznitelikleri iki çözümleyiciden gelir. spaCy'nin UD
etiketlerinden gelenler öneksizdir (`case_loc_ratio`), Zeyrek'ten gelenler
`zeyrek_` ile başlar (`zeyrek_case_loc_ratio`). İkisi aynı sayıyı vermez:
`case_loc_ratio` durum etiketi taşıyan kelimeler içinde bulunma durumunun
payıdır, `zeyrek_case_loc_ratio` çözümlenen bütün kelimeler içinde. Zeyrek
ayrıca -DI ve -mIş geçmişini ayırır (`zeyrek_tense_past_def_ratio`,
`zeyrek_tense_past_nar_ratio`); spaCy'de ikisi tek `tense_past_ratio`'dur.

## Grup

Öznitelikler 13 gruba ayrılır (`custom_ngrams` verirseniz oluşan `ngram_*`
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

Her özniteliğin bir ölçeği vardır ve grafik kurarken bu önemlidir:

| Ölçek | Anlamı | Örnek |
|---|---|---|
| `ratio_0_1` | 0 ile 1 arası oran | `ttr`, `mattr` |
| `score` | Formülün ürettiği puan; sabit bir aralığı yok | `atesman`, `yule_k`, `mtld` |
| `length` | Birimi karakter, kelime ya da cümle olan ortalama uzunluk | `word_len_mean`, `sent_len_mean` |
| `nats` | Nat cinsinden entropi (doğal logaritma; kütüphanedeki bütün logaritmalar ln) | `entropy`, `punct_entropy` |
| `count` | Sayım | `lemma_count` |

`ratio_0_1` olan iki özniteliği aynı eksende çizebilirsiniz; `score` olanı
onların yanına koymak yanıltır.

## Kelime ve cümle

Öznitelikler kelimeyi ve cümleyi kütüphanenin kendi kuralıyla sayar, modelin
tokenıyla değil:

- **Kelime** — boşlukla ayrılan, kenar noktalaması atılan, harf ya da rakam
  içeren birim. `e-posta`, `%50` ve sayılar birer kelimedir. Bağlılık
  öznitelikleri dışında her öznitelik bu kelimeyi sayar.
- **Cümle** — `. ? ! …` cümleyi bitirir; `:` yalnız ardından yeni bir cümle
  başlıyorsa. `Dr.` gibi kısaltmalar cümle bitirmez.
- **Kelimenin etiketi** — sözcük türü, biçimbirim etiketi ve lemma, kelimenin
  içindeki ilk tokendan gelir. Türkçe lemma Zeyrek'in sözlük maddesidir,
  İngilizce lemma spaCy'nin.

Bir özniteliğin hangi kuralı kullandığını
`describe_feature(anahtar)["definitions"]` söyler.

## Boru hattı

`analyze` çağırdığınızda sırayla şunlar olur:

```text
ham metin
   ↓  spaCy (tr_core_news_md / en_core_web_sm)
token · sözcük türü · biçimbirim etiketi · bağlılık ağacı · İngilizce lemma
   ↓  Zeyrek (yalnız Türkçe)
ek çözümlemesi · Türkçe lemma
   ↓  kütüphanenin kuralları
kelime ve cümle sınırları; her kelime etiketini kendi tokenından alır
   ↓  öznitelik çıkarıcıları
198 sayı
```

Bunun iki sonucu var:

1. **spaCy modeli sonuçların parçasıdır.** Model değişirse tokenlar,
   sözcük türü, biçimbirim ve bağlılık öznitelikleri değişir. Hangi modeli
   kullandığınızı yöntem bölümüne yazın.
2. **Ön işleme bir kez yapılır.** 198 özniteliğin hepsi aynı çözümlemeden
   beslenir; `groups` ile az öznitelik istemek ön işlemeyi hızlandırmaz,
   yalnız çıkarım adımını kısaltır.

## `FeatureParams`

Pencere boyları, eşikler ve örneklem sayıları burada durur. Ayrıntı:
[Eşikleri değiştir](../nasil/parametreler.md).

Cümle eşikleri (`short_sent_threshold`, `long_sent_threshold`) **dile göre
kalibre edilmiştir** (TR 4/17, EN 8/32) ve alan alan çözümlenir: verdiğiniz
alan kazanır, vermediğiniz alan kalibre değerinde kalır. Yani
`FeatureParams(mattr_window=100)` cümle eşiklerini değiştirmez.

## Kayıt defteri (registry)

Öznitelik adları, tanımları, formülleri, gereksinimleri ve künyeleri tek
bir yerde durur: `features/_registry_texts.py`. `describe_feature` oradan
okur, [başvuru bölümü](../../reference/index.md) oradan üretilir,
[doğrulama raporu](../../dogrulama-raporu.md) kapsam listesini oradan alır.

Bu kasıtlı: bir öznitelik eklenip kayıt defterine yazılmazsa testler
düşer. Hiçbir öznitelik dokümandan kaçamaz.

Kayıt defteri **İngilizcedir**. Tanımlar, formüller ve künyeler tek dilde
tutulur ki kaynakla karşılaştırırken araya çeviri katmanı girmesin.
