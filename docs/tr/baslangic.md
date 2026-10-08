# Öğretici — sıfırdan ilk ölçüme

Bu sayfa tek bir akıştır: kurulumdan başlayıp elinizde okunabilir bir sayı
tablosuyla bitirir. Dallanma yok; seçenekleri
[Nasıl yapılır](nasil/index.md) bölümünde bulursunuz.

Süre: yaklaşık 15 dakika, çoğu model indirmekle geçer.

## 1. Kütüphaneyi kurun

Paket henüz PyPI'da değil. Depoyu klonlayın ve paketi depodan kurun:

```bash
git clone https://github.com/efeziya1/turkish-linguistic-features.git
cd turkish-linguistic-features
pip install -e .
```

`-e` seçeneği paketi kopyalamaz, depodaki dosyalara bağlar. Bu yüzden bir kez
kurmanız yeter: depoyu `git pull` ile güncellediğinizde kurulu paket de güncellenir.

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

!!! note "Türkçe modelde hata sanacağınız iki şey"

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
    "Renksiz yeşil fikirler öfkeyle uyur. Chomsky bu tümceyi, dilbilgisine "
    "uygun bir tümcenin anlamsız da olabileceğini göstermek için kurdu. Bu "
    "kütüphane de anlamı değil, biçimi ölçer."
)

oz = tlf.analyze(metin, lang="tr")
print(len(oz))
```

```text
208
```

Metnin ilk tümcesi Chomsky'nin *Syntactic Structures* (1957) kitabından.

`lang` verilmezse varsayılan `"tr"`'dir; İngilizce metin için `lang="en"`
yazmanız gerekir.

`analyze` **düz bir sözlük** döndürür: anahtarlar öznitelik adları, değerler
sayılar. İç içe yapı yok, sınıf yok, `pandas` zorunluluğu yok.

## 4. Çıktıyı okuyun

208 sayıya birden bakmanın anlamı yok. Birkaçına bakalım:

```python
for k in ("ttr", "word_len_mean", "sent_len_mean",
          "syllable_mean", "atesman", "entropy"):
    print(f"{k:20s} {oz[k]}")
```

```text
ttr                  0.96
word_len_mean        6.04
sent_len_mean        8.3333
syllable_mean        2.48
atesman              77.441
entropy              3.163424
```

Bunlar ne anlatıyor:

| Anahtar | Değer | Okunuşu |
|---|---|---|
| `ttr` | 0.96 | Tip/token oranı. 25 sözcüğün 24'ü farklı; yalnız `bu` iki kez geçiyor. Kısa metinde TTR 1'e yakındır, metin uzadıkça düşer. |
| `word_len_mean` | 6.04 | Sözcük başına 6,04 karakter. |
| `sent_len_mean` | 8.3333 | Tümce başına 8,33 sözcük. |
| `syllable_mean` | 2.48 | Sözcük başına 2,48 hece. |
| `atesman` | 77.441 | Ateşman (1997) okunabilirlik puanı. Olağan düzyazı 0–100 arasına düşer, ama bu bir sınır değildir. 70–89 "kolay" bandı. |
| `entropy` | 3.163424 | Sözcük dağılımının Shannon entropisi, nat (doğal logaritma). |

## 5. Neden bazı değerler `nan`?

```python
print(oz["mattr"])
```

```text
nan
```

Metin 25 sözcük; `mattr` en az 100 sözcük ister. Kütüphane eksik veriyle
sayı **uydurmaz**, `nan` döndürür.

Ne kadarı `nan` olur, bakalım:

```python
kisa = tlf.analyze("Kısa bir cümle.", lang="tr")
nan_olan = [k for k, v in kisa.items() if isinstance(v, float) and v != v]
print(len(kisa), len(nan_olan))
```

```text
208 37
```

Üç sözcüklük bir metinde 208 öznitelikten **37'si** `nan` döner. Bu bir hata
değil, dürüstlüktür. Ayrıntı: **[NaN ne demek](aciklama/nan.md)**.

## 6. Bir özniteliğin kaynağını görün

Bir sayıyı çalışmanızda kullanacaksanız nereden geldiğini bilmelisiniz:

```python
d = tlf.describe_feature("mattr")
print(d["citation"])
print(d["references"][0])
```

```text
Covington & McFall (2010); default window 50 — C&M recommend a window of 500; 50 is used here so that texts of 100+ words can be measured (mattr needs 2 × window)
Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot: The moving-average type–token ratio (MATTR). Journal of Quantitative Linguistics, 17(2), 94–100. DOI 10.1080/09296171003643098
```

`references` alanı yöntem bölümünüze kopyalayacağınız şeydir. `citation`
kısa işaretçidir ve **ne bilmediğimizi de söyler** — yukarıdaki örnekte
varsayılan pencere boyunun kaynaktan gelmediğini açıkça yazıyor. Sözlükteki öbür
alanlar (formül, ölçek, gereken en az veri…): [Bir özniteliğin kaynağını
bul](nasil/kunye.md).

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
label,source,segment_id,lemma_count,word_count,word_len_mean,entropy,yu...
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
