# Türkçe dokümantasyon

Bu bölüm dört parçaya ayrılır. Hangisine gideceğiniz, şu an ne yapmak
istediğinize bağlı.

| Ne yapmak istiyorsunuz | Nereye gidin |
|---|---|
| Kütüphaneyi hiç kullanmadım, baştan sona anlatın | **[Öğretici](baslangic.md)** |
| Belirli bir işi yapmam lazım | **[Nasıl yapılır](nasil/index.md)** |
| Bir özniteliğin ne olduğunu arıyorum | **[Başvuru](../reference/index.md)** (İngilizce) |
| Neden böyle çalıştığını anlamak istiyorum | **[Açıklama](aciklama/index.md)** |
| Çalışan bir betikten başlamak istiyorum | **[Örnek betikler](https://github.com/efeziya1/turkish-linguistic-features/tree/main/examples)** (on betik, her biri bir soruya cevap) |

Emin değilseniz öğreticiden başlayın: kurulumdan ilk tabloya kadar götürür.

## Hızlı bakış

```python
import turkish_linguistic_features as tlf

oz = tlf.analyze("Renksiz yeşil fikirler öfkeyle uyur.", lang="tr")
len(oz)               # 208
oz["word_len_mean"]   # 6.2
```

Kütüphanenin **on bir** genel adı var, hepsi bu kadar:

| Ad | Ne yapar |
|---|---|
| `analyze` | Bir metinden bütün öznitelikleri çıkarır |
| `analyze_corpus` | Bir klasördeki her metin için `analyze` çalıştırır |
| `ngram_matches` | Verdiğiniz bir sözcük ya da POS etiketi dizisinin (`["ADJ", "NOUN"]` gibi) metinde neyle eşleştiğini, sıklıklarıyla gösterir |
| `segment_text` | Metni sabit büyüklükte parçalara böler |
| `save_csv` | Çıkan satırları CSV'ye yazar |
| `describe_feature` | Bir özniteliğin tanımını, formülünü, ölçeğini, hesaplanması için gereken en az veriyi ve künyesini verir |
| `FeatureParams` | Eşikleri ve pencere boylarını taşıyan ayar nesnesi |
| `LinguisticFeaturesError` | Kütüphanenin kendi hatalarının atası |
| `ModelNotFoundError` | Gereken dil verisi kurulu değilse: spaCy modeli ya da İngilizce hece sayımı için NLTK `cmudict` |
| `MissingDependencyWarning` | İsteğe bağlı bir paket yoksa |
| `ParagraphStructureWarning` | 1000 sözcüğü geçen metinde paragraf sınırı bulunamazsa |

On bir ad, 208 öznitelik. Öznitelik eklemek için yeni fonksiyon öğrenmenize
gerek yok — hepsi `analyze`'dan çıkar.

## Terimler

Doküman boyunca sabit karşılıklar kullanılıyor. Emin olmadığınız bir sözcük
görürseniz: **[terim sözlüğü](sozluk.md)**.
