# Türkçe dokümantasyon

Bu bölüm dört parçaya ayrılır. Hangisine gideceğiniz, şu an ne yapmak
istediğinize bağlı.

| Ne yapmak istiyorsunuz | Nereye gidin |
|---|---|
| Kütüphaneyi hiç kullanmadım, baştan sona anlatın | **[Öğretici](baslangic.md)** |
| Belirli bir işi yapmam lazım | **[Nasıl yapılır](nasil/index.md)** |
| Bir özniteliğin ne olduğunu arıyorum | **[Başvuru](../reference/index.md)** (İngilizce) |
| Neden böyle çalıştığını anlamak istiyorum | **[Açıklama](aciklama/index.md)** |

Bu ayrım keyfî değil: dokümana gelen insan ya öğrenmeye gelir, ya bir işi
yapmaya, ya bir şeyi aramaya, ya da anlamaya. Aynı sayfada dördünü birden
yapmaya çalışmak hepsini bozar.

## Hızlı bakış

```python
import turkish_linguistic_features as tlf

oz = tlf.analyze("Dil, insanın düşüncesini taşıyan en eski araçtır.", lang="tr")
len(oz)                   # 208
oz["avg_word_length"]     # 5.7667
```

Kütüphanenin **dokuz** genel adı var, hepsi bu kadar:

| Ad | Ne yapar |
|---|---|
| `analyze` | Bir metinden bütün öznitelikleri çıkarır |
| `analyze_corpus` | Bir dizindeki bütün dosyaları çıkarır |
| `segment_text` | Metni sabit büyüklükte parçalara böler |
| `save_csv` | Çıkan satırları CSV'ye yazar |
| `describe_feature` | Bir özniteliğin tanımını ve kaynağını verir |
| `FeatureParams` | Eşikleri ve pencere boylarını taşıyan ayar nesnesi |
| `LinguisticFeaturesError` | Kütüphanenin bütün hatalarının atası |
| `ModelNotFoundError` | spaCy modeli kurulu değilse |
| `MissingDependencyWarning` | İsteğe bağlı bir paket yoksa |

Dokuz ad, 208 öznitelik. Öznitelik eklemek için yeni fonksiyon öğrenmenize
gerek yok — hepsi `analyze`'dan çıkar.

## Terimler

Doküman boyunca sabit karşılıklar kullanılıyor. Emin olmadığınız bir sözcük
görürseniz: **[terim sözlüğü](sozluk.md)**.
