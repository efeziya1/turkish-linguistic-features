# Türkçe belgeler

Bu bölüm dört parçaya ayrılır. Hangisine gideceğiniz, şu an ne yapmak
istediğinize bağlı.

| Ne yapmak istiyorsunuz | Nereye gidin |
|---|---|
| Aracı hiç kullanmadım, baştan sona anlatın | **[Öğretici](baslangic.md)** |
| Belirli bir işi yapmam lazım | **[Nasıl yapılır](nasil/index.md)** |
| Bir özniteliğin ne olduğunu arıyorum | **[Başvuru](../reference/index.md)** (İngilizce) |
| Neden böyle çalıştığını anlamak istiyorum | **[Açıklama](aciklama/index.md)** |
| Çalışan bir betikten başlamak istiyorum | **[Örnek betikler](https://github.com/efeziya1/turkish-linguistic-features/tree/main/examples)** (on betik, her biri bir soruya cevap) |

Emin değilseniz öğreticiden başlayın: kurulumdan ilk tabloya kadar götürür.

## Hızlı bakış

```python
import turkish_linguistic_features as tlf

oz = tlf.analyze("Renksiz yeşil fikirler öfkeyle uyur.", lang="tr")
len(oz)               # 214
oz["word_len_mean"]   # 6.2
```

Aracın Python'dan çağrılan **on bir** adı var, hepsi bu kadar:

| Ad | Ne yapar |
|---|---|
| `analyze` | Bir metinden bütün öznitelikleri (İng. *features*) çıkarır |
| `analyze_corpus` | Bir klasördeki her metin için `analyze` çalıştırır |
| `ngram_matches` | Verdiğiniz bir sözcük dizisinin (İng. *n-gram*) metinde neyle eşleştiğini, sıklıklarıyla gösterir; dizi sözcüklerden, sözlükbirimlerden ya da sözcük türü etiketlerinden (`["EV", "VERB"]`, `["ADJ", "NOUN"]` gibi) oluşabilir |
| `segment_text` | Metni eşit büyüklükte parçalara böler |
| `save_csv` | Çıkan satırları CSV'ye yazar |
| `describe_feature` | Bir özniteliğin tanımını, formülünü, ölçeğini, hesaplanması için gereken en az veriyi ve künyesini verir |
| `FeatureParams` | Eşikleri ve pencere boylarını taşıyan ayar nesnesi |
| `LinguisticFeaturesError` | Aracın kendi hatalarının atası |
| `ModelNotFoundError` | Gereken dil verisi kurulu değilse: spaCy modeli ya da İngilizce seslem sayımı için NLTK `cmudict` |
| `MissingDependencyWarning` | İsteğe bağlı bir paket yoksa |
| `ParagraphStructureWarning` | 1000 sözcüğü geçen metinde paragraf sınırı bulunamazsa |

Bütün öznitelikler, `custom_ngrams` ile saydığınız sözcük dizileri de dahil,
`analyze`'dan çıkar.

## Terimler

Belgelerdeki terimler, aracın anlatıldığı tezdeki terimlerle aynıdır. Bir terim bir sayfada
ilk geçtiğinde İngilizcesi yanında verilir: türce (İng. *token*), derlem (İng. *corpus*).
Hepsi tek yerde: **[terim sözlüğü](sozluk.md)**.
