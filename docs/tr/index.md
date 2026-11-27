# Türkçe belgeler

Bu bölüm dört parçaya ayrılır; hangi parçaya bakılacağı yapılacak işe bağlıdır.

| Amaç | Sayfa |
|---|---|
| Aracı ilk kez kullanmak, baştan sona öğrenmek | **[Öğretici](baslangic.md)** |
| Belirli bir işi yapmak | **[Nasıl yapılır](nasil/index.md)** |
| Bir özniteliğin ne olduğunu bulmak | **[Başvuru](../reference/index.md)** (İngilizce) |
| Aracın neden böyle çalıştığını anlamak | **[Açıklama](aciklama/index.md)** |
| Çalışan bir betikten başlamak | **[Örnek betikler](https://github.com/efeziya1/turkish-linguistic-features/tree/main/examples)** (on betik, her biri bir soruya cevap) |

Araca yeni başlayanlar için en uygun başlangıç öğreticidir: Kurulumdan ilk tabloya kadar götürür.

## Hızlı bakış

```python
import turkish_linguistic_features as tlf

oz = tlf.analyze("Renksiz yeşil fikirler öfkeyle uyur.", lang="tr")
len(oz)               # 217
oz["word_len_mean"]   # 6.2
```

Aracın Python'dan çağrılan **on iki** adı var, hepsi bu kadar:

| Ad | Ne yapar |
|---|---|
| `analyze` | Bir metinden bütün öznitelikleri (İng. *features*) çıkarır |
| `analyze_corpus` | Bir klasördeki her metin için `analyze` çalıştırır |
| `ngram_matches` | Verilen bir sözcük dizisinin (İng. *n-gram*) metinde neyle eşleştiğini, sıklıklarıyla gösterir; dizi sözcüklerden, sözlükbirimlerden ya da sözcük türü etiketlerinden (`["EV", "VERB"]`, `["ADJ", "NOUN"]` gibi) oluşabilir |
| `text_units` | Metnin sözcüklerini, sözlükbirimlerini (İng. *lemmas*), sözcük türü etiketlerini, seslem sayılarını ve tümcelerini ayrı listeler hâlinde verir; bunlar özniteliklerin saydığı birimlerdir |
| `segment_text` | Metni eşit büyüklükte parçalara böler |
| `save_csv` | Çıkan satırları CSV'ye yazar |
| `describe_feature` | Bir özniteliğin tanımını, formülünü, ölçeğini, hesaplanması için gereken en az veriyi ve künyesini verir |
| `FeatureParams` | Eşik, pencere boyu gibi ayarları değiştirmeye yarar |
| `LinguisticFeaturesError` | Aracın verdiği hataların ortak türü |
| `ModelNotFoundError` | Gereken dil verisi (spaCy modeli ya da İngilizce seslem sayımı için NLTK `cmudict`) kurulu değilse verilen hata |
| `MissingDependencyWarning` | İsteğe bağlı bir paket kurulu değilse verilen uyarı |
| `ParagraphStructureWarning` | 1000 sözcüğü geçen bir metinde paragraf sınırı bulunamazsa verilen uyarı |

Bütün öznitelikler, `custom_ngrams` ile sayılan sözcük dizileri de dahil,
`analyze`'dan çıkar.

## Terimler

Bir terim bir sayfada ilk geçtiğinde İngilizcesi yanında verilir: türce (İng. *token*), derlem (İng. *corpus*).
Hepsi tek yerde: **[terim sözlüğü](sozluk.md)**.
