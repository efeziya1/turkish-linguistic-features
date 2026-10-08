# Türkçe dokümantasyon

Bu bölüm dört parçaya ayrılır. Hangisine gideceğiniz, şu an ne yapmak
istediğinize bağlı.

| Ne yapmak istiyorsunuz | Nereye gidin |
|---|---|
| Kütüphaneyi hiç kullanmadım, baştan sona anlatın | **[Öğretici](baslangic.md)** |
| Belirli bir işi yapmam lazım | **[Nasıl yapılır](nasil/index.md)** |
| Bir özniteliğin ne olduğunu arıyorum | **[Başvuru](../reference/index.md)** (İngilizce) |
| Neden böyle çalıştığını anlamak istiyorum | **[Açıklama](aciklama/index.md)** |

Emin değilseniz öğreticiden başlayın: kurulumdan ilk tabloya kadar götürür.

## Hızlı bakış

```python
import turkish_linguistic_features as tlf

oz = tlf.analyze("Dil, insanın düşüncesini taşıyan en eski araçtır.", lang="tr")
len(oz)               # 201
oz["word_len_mean"]   # 5.8571
```

Kütüphanenin **on bir** genel adı var, hepsi bu kadar:

| Ad | Ne yapar |
|---|---|
| `analyze` | Bir metinden bütün öznitelikleri çıkarır |
| `analyze_corpus` | Bir klasördeki her metin için `analyze` çalıştırır |
| `ngram_matches` | Kendi verdiğiniz bir kelime öbeğinin metinde neyle eşleştiğini sıklığıyla gösterir |
| `segment_text` | Metni sabit büyüklükte parçalara böler |
| `save_csv` | Çıkan satırları CSV'ye yazar |
| `describe_feature` | Bir özniteliğin tanımını ve kaynağını verir |
| `FeatureParams` | Eşikleri ve pencere boylarını taşıyan ayar nesnesi |
| `LinguisticFeaturesError` | Kütüphanenin bütün hatalarının atası |
| `ModelNotFoundError` | Gereken dil verisi kurulu değilse: spaCy modeli ya da İngilizce hece sayımı için NLTK `cmudict` |
| `MissingDependencyWarning` | İsteğe bağlı bir paket yoksa |
| `ParagraphStructureWarning` | 1000 kelimeyi geçen metinde paragraf sınırı bulunamazsa |

On bir ad, 201 öznitelik. Öznitelik eklemek için yeni fonksiyon öğrenmenize
gerek yok — hepsi `analyze`'dan çıkar.

## Terimler

Doküman boyunca sabit karşılıklar kullanılıyor. Emin olmadığınız bir sözcük
görürseniz: **[terim sözlüğü](sozluk.md)**.
