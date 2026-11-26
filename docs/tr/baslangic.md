# Öğretici — sıfırdan ilk ölçüme

Bu sayfa tek bir akıştır: kurulumdan başlayıp elinizde okunabilir bir sayı
tablosuyla bitirir. Dallanma yok; seçenekleri
[Nasıl yapılır](nasil/index.md) bölümünde bulursunuz.

Süre: yaklaşık 15 dakika, çoğu model indirmekle geçer.

## 1. Aracı kurun

Araç bir Python kütüphanesi olarak dağıtılır:

```bash
pip install turkish-linguistic-features
```

## 2. Dil verisini kurun

`pip install` Python bağımlılıklarını kurar, dil verisini kurmaz.
Kullandığınız dilin verisini bir kez kurun:

```bash
# Türkçe — 156 MB. Model turkish-nlp-suite'e ait ve spaCy'nin model
# listesinde yok, bu yüzden paket dosyası (wheel) doğrudan kurulur:
pip install https://huggingface.co/turkish-nlp-suite/tr_core_news_md/resolve/main/tr_core_news_md-1.0-py3-none-any.whl

# İngilizce — iki parça: spaCy modeli (12 MB) ve seslem sayımı için CMU
# telaffuz sözlüğü (1 MB)
python -m spacy download en_core_web_sm
python -m nltk.downloader cmudict

# İsteğe bağlı — iki wordfreq_* özniteliği için
pip install 'wordfreq>=3.0'
```

Akana (Türkçe biçimbirim çözümleyicisi) araçla birlikte kendiliğinden kurulur.

!!! note "Türkçe modelde hata sanacağınız iki şey"

    **Sürüm numaraları farklı.** Paket dosyasının adında `1.0`, içindeki bilgide
    `3.4.2` yazıyor. `pip` bunu sorun etmez ve kurar; daha katı kurulum araçları
    paketi bozuk sayıp reddedebilir.

    **Model yüklenirken `W094` uyarısı çıkar.** Modelin bilgi dosyası (`meta.json`)
    uyumlu spaCy sürümlerini geniş bir aralıkla belirtmiş, spaCy bu yüzden uyarıyor.
    Uyarı zararsızdır; sizin bir şey yapmanız gerekmez.

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
214
```

Metnin ilk tümcesi Chomsky'nin *Syntactic Structures* (1957) kitabından.

`lang` verilmezse varsayılan `"tr"`'dir; İngilizce metin için `lang="en"`
yazmanız gerekir.

`analyze` **düz bir sözlük** döndürür: anahtarlar öznitelik (İng. *feature*) adları,
değerler sayılar. İç içe yapı yoktur; sonucu kullanmak için `pandas` gerekmez.

## 4. Çıktıyı okuyun

214 sayıya birden bakmanın anlamı yok. Birkaçına bakalım:

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
| `ttr` | 0.96 | Tür/türce oranı (İng. *type-token ratio*). 25 sözcüğün 24'ü farklı; yalnız `bu` iki kez geçiyor. Kısa metinde TTR 1'e yakındır, metin uzadıkça düşer. |
| `word_len_mean` | 6.04 | Sözcük başına 6,04 karakter. |
| `sent_len_mean` | 8.3333 | Tümce başına 8,33 sözcük. |
| `syllable_mean` | 2.48 | Sözcük başına 2,48 seslem (İng. *syllable*). |
| `atesman` | 77.441 | Ateşman (1997) okunabilirlik puanı. Olağan düzyazının puanı 0 ile 100 arasındadır, ama formül bu aralığın dışına da çıkabilir. 70–89 arası "kolay" sayılır. |
| `entropy` | 3.163424 | Sözcük dağılımının Shannon entropisi: Sözcüklerin metne ne kadar çeşitli ve dengeli dağıldığını gösterir. Doğal logaritmayla (nat birimiyle) hesaplanır. |

## 5. Neden bazı değerler `nan`?

```python
print(oz["mattr"])
```

```text
nan
```

Metin 25 sözcük; `mattr` en az 100 sözcük ister. Araç eksik veriyle
sayı **uydurmaz**, `nan` (İng. *not a number*, "sayı değil") döndürür.

Ne kadarı `nan` olur, bakalım:

```python
import math

kisa = tlf.analyze("Kısa bir tümce.", lang="tr")
nan_olan = [k for k, v in kisa.items() if math.isnan(v)]
print(len(kisa), len(nan_olan))
```

```text
214 38
```

Üç sözcüklük bir metinde 214 öznitelikten **38'i** `nan` döner. Bu bir hata
değildir. Ayrıntı: **[NaN ne demek](aciklama/nan.md)**.

## 6. Bir özniteliğin kaynağını görün

Bir sayıyı çalışmanızda kullanacaksanız nereden geldiğini bilmelisiniz:

```python
d = tlf.describe_feature("mattr")
print(d["citation"])
print(d["references"][0])
```

```text
Covington & McFall (2010); default window 50 — C&M recommend a window of 500 (p.97); 50 is used here so that texts of 100+ words can be measured (mattr needs 2 × window)
Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot: The moving-average type–token ratio (MATTR). Journal of Quantitative Linguistics, 17(2), 94–100. DOI 10.1080/09296171003643098
```

`references` (kaynakça kaydı, İng. *reference*) kaynakçanıza kopyalayacağınız şeydir.
`citation` (künye, İng. *citation*) kısa gösterimdir ve **ne bilmediğimizi de söyler**:
yukarıdaki örnekte varsayılan pencere boyunun kaynaktan gelmediğini açıkça yazıyor.
`describe_feature`'ın verdiği öbür alanlar (formül, ölçek, gereken en az veri…): [Bir özniteliğin kaynağını
bul](nasil/kunye.md).

## 7. Bir derlemi tabloya çevirin

Tek metin nadiren yeterlidir. Derleminizin (İng. *corpus*) klasör yapısı şöyle olsun:

```text
derlem/
  yazar_a/
    metin1.txt
    metin2.txt
  yazar_b/
    metin3.txt
```

```python
satirlar = tlf.analyze_corpus("derlem/", lang="tr")
tlf.save_csv(satirlar, "oznitelikler.csv")
print("satır sayısı:", len(satirlar))
print("sütun sayısı:", len(satirlar[0]))
```

```text
satır sayısı: 3
sütun sayısı: 217
```

Her dosya bir satır olur. 217 sütun = 214 öznitelik + üç kimlik sütunu:

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
