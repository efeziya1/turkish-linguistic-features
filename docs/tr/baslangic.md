# Öğretici — sıfırdan ilk ölçüme

Bu sayfa tek bir akıştır: kurulumdan başlayıp elinizde okunabilir bir sayı
tablosuyla bitirir. Dallanma yok; seçenekleri
[Nasıl yapılır](nasil/index.md) bölümünde bulursunuz.

Süre: yaklaşık 15 dakika, çoğu model indirmekle geçer.

## 1. Kütüphaneyi kurun

Paket henüz PyPI'da değil. Depoyu klonlayıp düzenlenebilir kurulum yapın:

```bash
git clone https://github.com/efeziya1/turkish-linguistic-features.git
cd turkish-linguistic-features
pip install -e .
```

`-e` (editable) kurulum, depoyu güncellediğinizde paketin de güncel kalmasını
sağlar. Bir kez kurarsınız, `git pull` yeter.

## 2. Dil verisini kurun

`pip install` Python bağımlılıklarını kurar, dil verisini kurmaz.
Kullandığınız dilin verisini bir kez kurun:

```bash
# Türkçe — 156 MB. Model turkish-nlp-suite'e ait ve spaCy'nin kayıt
# defterinde yok, bu yüzden wheel doğrudan kurulur:
pip install https://huggingface.co/turkish-nlp-suite/tr_core_news_md/resolve/main/tr_core_news_md-1.0-py3-none-any.whl

# İngilizce — iki parça: spaCy modeli (12 MB) ve hece sayımı için CMU
# telaffuz sözlüğü (1 MB)
python -m spacy download en_core_web_sm
python -m nltk.downloader cmudict
```

!!! warning "Türkçe modelde hata sanacağınız iki şey"

    **Wheel kendisiyle çelişiyor.** Dosya adı `1.0` diyor, içindeki üstveri
    `3.4.2` diyor. `pip` bunu kabul eder ve kurar; daha katı kurucular
    bozuk wheel diye reddeder.

    **Yüklenirken `W094` uyarısı basar.** Modelin kendi `meta.json`'ı spaCy
    sürüm aralığını gevşek yazmış. Zararsızdır, iki tarafta da
    düzeltilecek bir şey yoktur.

Kurulumu doğrulayın:

```bash
python -c "import spacy; spacy.load('tr_core_news_md'); print('tamam')"
```

## 3. İlk ölçüm

```python
import turkish_linguistic_features as tlf

metin = (
    "Dil, insanın düşüncesini taşıyan en eski araçtır. Yazı ise o düşünceyi "
    "zamanın dışına çıkarır. Bir metni ölçmek, onun taşıdığı yükü tartmaya "
    "benzer; tartıyı doğru kurarsanız metin size kendi biçimini anlatır."
)

oz = tlf.analyze(metin, lang="tr")
print(len(oz))
```

```text
208
```

`lang` verilmezse varsayılan `"tr"`'dir; İngilizce metin için `lang="en"`
yazmanız gerekir.

`analyze` **düz bir sözlük** döndürür: anahtarlar öznitelik adları, değerler
sayılar. İç içe yapı yok, sınıf yok, `pandas` zorunluluğu yok.

## 4. Çıktıyı okuyun

208 sayıya birden bakmanın anlamı yok. Birkaçına bakalım:

```python
for k in ("ttr", "avg_word_length", "avg_sent_len_word",
          "syllable_mean", "atesman", "entropy"):
    print(f"{k:20s} {oz[k]}")
```

```text
ttr                  1.0
avg_word_length      5.7667
avg_sent_len_word    10.0
syllable_mean        2.5333
atesman              70.9483
entropy              4.906891
```

Bunlar ne anlatıyor:

| Anahtar | Değer | Okunuşu |
|---|---|---|
| `ttr` | 1.0 | Tip/token oranı. **1.0 = her kelime bir kez geçmiş.** 30 kelimelik bir metinde bu normaldir; uzun metinde imkânsızdır. |
| `avg_word_length` | 5.7667 | Kelime başına 5,77 karakter. |
| `avg_sent_len_word` | 10.0 | Cümle başına 10 kelime. Türkçe roman korpusunda medyan 9'dur. |
| `syllable_mean` | 2.5333 | Kelime başına 2,53 hece. |
| `atesman` | 70.9483 | Ateşman (1997) okunabilirlik puanı, 0–100. 70 "kolay"a yakın. |
| `entropy` | 4.906891 | Kelime dağılımının Shannon entropisi, bit. |

!!! note "`ttr = 1.0` sizi yanıltmasın"

    TTR metin uzunluğuna çok duyarlıdır: metin uzadıkça mutlaka düşer.
    Bu yüzden farklı uzunluktaki metinleri TTR ile karşılaştıramazsınız.
    `mattr`, `mtld` ve `vocd_d` uzunluğa daha az duyarlıdır ama bağımsız
    değildir ([ölçüm örneği](https://github.com/efeziya1/turkish-linguistic-features/blob/main/examples/09_uzunluk_duyarliligi.py)); daha uzun
    metin de isterler (bkz. adım 5). Farklı uzunluktaki metinleri
    karşılaştırırken önce `segment_size` ile aynı boya getirin.

## 5. Neden bazı değerler `nan`?

```python
print(oz["mattr"])
```

```text
nan
```

Metin 30 kelime; `mattr` en az 100 kelime ister. Kütüphane eksik veriyle
sayı **uydurmaz**, `nan` döndürür.

Ne kadarı `nan` olur, bakalım:

```python
kisa = tlf.analyze("Kısa bir cümle.", lang="tr")
nan_olan = [k for k, v in kisa.items() if isinstance(v, float) and v != v]
print(len(kisa), len(nan_olan))
```

```text
208 46
```

Üç kelimelik bir metinde 208 öznitelikten **46'sı** `nan` döner. Bu bir hata
değil, dürüstlüktür. Ayrıntı: **[NaN ne demek](aciklama/nan.md)**.

## 6. Bir özniteliğin kaynağını görün

Bir sayıyı çalışmanızda kullanacaksanız nereden geldiğini bilmelisiniz:

```python
import json
print(json.dumps(tlf.describe_feature("mattr"), ensure_ascii=False, indent=2))
```

```json
{
  "key": "mattr",
  "group": "lexical",
  "group_label": "Lexical richness & frequency",
  "description": "moving-average TTR",
  "formula": "mean TTR of every sliding window of mattr_window words",
  "scale": "ratio_0_1",
  "inputs": ["surface_tokens", "lemma_tokens", "pos_data"],
  "params": ["mattr_window"],
  "requires": "at least 100 words (2 x mattr_window)",
  "citation": "Covington & McFall (2010); default window 50 — C&M recommend a window of 500; 50 is used here so that texts of 100+ words can be measured (mattr needs 2 × window)",
  "references": [
    "Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot: The moving-average type–token ratio (MATTR). Journal of Quantitative Linguistics, 17(2), 94–100. DOI 10.1080/09296171003643098"
  ]
}
```

`references` alanı yöntem bölümünüze kopyalayacağınız şeydir. `citation`
kısa işaretçidir ve **ne bilmediğimizi de söyler** — yukarıdaki örnekte
varsayılan pencere boyunun kaynaktan gelmediğini açıkça yazıyor.

## 7. Bir korpusu tabloya çevirin

Tek metin nadiren yeterlidir. Dizin yapınız şöyle olsun:

```text
korpus/
  yazar_a/
    metin1.txt
    metin2.txt
  yazar_b/
    metin3.txt
```

```python
satirlar = tlf.analyze_corpus("korpus/", lang="tr")
tlf.save_csv(satirlar, "oznitelikler.csv")
print("satır sayısı:", len(satirlar))
print("sütun sayısı:", len(satirlar[0]))
```

```text
satır sayısı: 3
sütun sayısı: 211
```

Her dosya bir satır olur. 211 sütun = 208 öznitelik + üç kimlik sütunu:

```text
label=yazar_a  source=metin1     segment_id=0
label=yazar_a  source=metin2     segment_id=0
label=yazar_b  source=metin3     segment_id=0
```

`label` klasör adıdır (çoğu çalışmada yazar ya da sınıf), `source` dosya
adıdır. CSV'nin ilk satırı:

```text
label,source,segment_id,n_lemma_count,avg_word_length,word_length_cv,entropy,yule_k,simpso...
```

Bu dosyayı `pandas`, R ya da SPSS ile doğrudan açabilirsiniz.

## Bitti — sırada ne var

Elinizde çalışan bir kurulum ve bir öznitelik tablosu var. Şimdi:

- Belirli bir iş yapmanız gerekiyorsa → **[Nasıl yapılır](nasil/index.md)**
- Metinleriniz çok uzunsa ve parçalamanız gerekiyorsa →
  **[Metni parçalara böl](nasil/segmentleme.md)**
- Sayıların ne kadarına güvenebileceğinizi merak ediyorsanız →
  **[Doğrulama sistemi](aciklama/dogrulama.md)** ve
  **[Sınırlılıklar](aciklama/sinirliliklar.md)**
