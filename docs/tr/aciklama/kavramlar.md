# Kavramlar

## Öznitelik

**Öznitelik** (feature), bir metinden çıkarılan tek bir sayıdır. `ttr`,
`avg_word_length`, `atesman` — her biri bir öznitelik. Adları
`snake_case`'dir ve hiç değişmez; sürüm yükseltmeleri anahtar adını
bozmaz.

Öznitelik üç şeyden biridir:

1. **Literatürde adı olan bir ölçü** — `mattr`, `yule_k`, `flesch_reading_ease`.
   Bunların künyesi vardır.
2. **Bir dış etiket şemasının kategorisi** — `pos_noun` (UD),
   `case_loc_ratio` (Zeyrek). Künyesi şemaya bağlıdır, ölçünün kendisine
   değil.
3. **Saf tanım** — `punc_,_ratio` ("virgül / kelime"). Künyesi yoktur,
   çünkü tanımlanacak bir şey yoktur.

208 anahtarın 141'inin künyesi vardır, 67'sinin yoktur.

## Grup

Öznitelikler 13 gruba ayrılır. Grup, hem düzenleme hem de seçim aracıdır:

```python
oz = tlf.analyze(metin, lang="tr", groups=["readability", "lexical"])
```

Gruplar ve büyüklükleri [Tek metni analiz et](../nasil/tek-metin.md)
sayfasında.

## Dinamik anahtarlar

Bazı anahtarlar tek tek yazılmamıştır, kalıptan üretilir:

- `char_a` … `char_z` — harf sıklık vektörü
- `punc_,_ratio`, `punc_._ratio` … — noktalama oranları
- `ng_*` — `custom_ngrams` verirseniz oluşan n-gram sayaçları

`describe_feature("char_a")` çağırırsanız `formula` ve `requires` alanları
**grup düzeyinde** genel ifadedir, tek harfe özel değil.

## Ölçek (`scale`)

Her özniteliğin bir ölçeği vardır ve grafik kurarken bu önemlidir:

| Ölçek | Anlamı | Örnek |
|---|---|---|
| `ratio_0_1` | 0 ile 1 arası oran | `ttr`, `mattr` |
| `score` | Formülün ürettiği puan, sınırı yok | `atesman`, `ari` |
| `count` | Sayım | `n_lemma_count` |
| `chars` / `words` | Birimi karakter ya da kelime olan ortalama | `avg_word_length` |

`ratio_0_1` olan iki özniteliği aynı eksende çizebilirsiniz; `score` olanı
onların yanına koymak yanıltır.

## Boru hattı

`analyze` çağırdığınızda sırayla şunlar olur:

```text
ham metin
   ↓  spaCy (tr_core_news_md / en_core_web_sm)
yüzey token · lemma · sözcük türü · bağlılık ağacı · cümle sınırları
   ↓  Zeyrek (yalnız Türkçe)
ek çözümlemesi
   ↓  öznitelik çıkarıcıları
208 sayı
```

Bunun iki sonucu var:

1. **spaCy modeli sonuçların parçasıdır.** Model değişirse cümle bölme,
   sözcük türü ve bağlılık öznitelikleri değişir. Hangi modeli
   kullandığınızı yöntem bölümüne yazın.
2. **Ön işleme bir kez yapılır.** 208 özniteliğin hepsi aynı çözümlemeden
   beslenir; `groups` ile az öznitelik istemek ön işlemeyi hızlandırmaz,
   yalnız çıkarım adımını kısaltır.

## `FeatureParams`

Pencere boyları, eşikler ve örneklem sayıları burada durur. Ayrıntı:
[Eşikleri değiştir](../nasil/parametreler.md).

Kritik nokta: `params=None` bıraktığınızda kütüphane **dile özel kalibre
edilmiş** değerleri kullanır (TR 4/18, EN 7/39). `FeatureParams()`
verdiğiniz anda o kalibrasyon devre dışı kalır.

## Kayıt defteri (registry)

Öznitelik adları, tanımları, formülleri, gereksinimleri ve künyeleri tek
bir yerde durur: `features/_registry_texts.py`. `describe_feature` oradan
okur, [başvuru bölümü](../../reference/index.md) oradan üretilir,
[doğrulama raporu](../../dogrulama-raporu.md) kapsam listesini oradan alır.

Bu kasıtlı: bir öznitelik eklenip kayıt defterine yazılmazsa testler
düşer. Hiçbir öznitelik dokümandan kaçamaz.

Kayıt defteri **İngilizcedir**. Tanımlar, formüller ve künyeler tek dilde
tutulur ki kaynakla karşılaştırırken araya çeviri katmanı girmesin.
