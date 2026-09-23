# Örnek scriptler

"Nasıl kullanılır?" sorusunun çalışan cevabı. Dört script, dört ayrı soru —
hepsi çalıştırılmış ve aşağıdaki çıktılar gerçek koşulardan alınmıştır.

## Çalıştırma

Scriptler kütüphaneyi normal bir paket gibi import eder:

```bash
pip install -e .          # depodan
python examples/01_hizli_baslangic.py
```

Kütüphaneyi kurmadan, doğrudan depo kökünden çalıştırmak isterseniz depo
kökünü import yoluna ekleyin:

```bash
# Windows PowerShell
$env:PYTHONPATH="."; python examples/01_hizli_baslangic.py
# Linux / macOS
PYTHONPATH=. python examples/01_hizli_baslangic.py
```

Türkçe için `tr_core_news_md` modeli kurulu olmalıdır (kurulum komutu depo
kökündeki `README.md`'de). Model yoksa `analyze()` kurulum komutunu içeren bir
`ModelNotFoundError` verir.

**Kurulum gereksinimleri:** dördü de temel kurulumla çalışır. `pandas`
opsiyoneldir — yalnız `02`'nin son iki bloğu onu kullanır ve kurulu değilse o
bloklar atlanır, script yine baştan sona koşar. Hiçbiri `sklearn` import etmez.

Çıktılar `examples/output/` altına yazılır; o dizin `.gitignore`'da.

Bütün scriptlerde import biçimi aynıdır — depo genelinde kullanılan biçim:

```python
import turkish_linguistic_features as tlf

tlf.analyze(metin)
tlf.describe_feature("ttr")
```

> **Yorum yok (K10).** Hiçbir script "daha iyi", "daha zor", "aynı yazar" gibi
> bir yargı ya da benzerlik skoru basmaz. Kütüphane ölçer; ölçtüğünün ne
> anlama geldiğine siz karar verirsiniz.

---

## `01_hizli_baslangic.py` — tek metin (Türkçe + İngilizce)

Bir metinden 208 öznitelik çıkarır, `describe_feature()` ile tek bir gruba
süzüp hizalanmış tablo basar, sonra seçilen anahtarların **formülünü** ve
**ölçeğini** yazdırır. Kütüphanenin iki temel çağrısını (`analyze` ve
`describe_feature`) tek dosyada gösterir. Sonda aynı çağrıyı `lang="en"` ile
tekrarlar: **her iki dili de kapsayan tek script budur.**

```
Metin çözümleniyor (530 karakter)...
208 öznitelik çıkarıldı.

-- pos - Part-of-speech ratios --------------------
pos_noun                           0.3095
pos_propn                          0.0000
pos_verb                           0.1905
...
pos_punct                          0.1310

-- Seçilen özniteliklerin formülü --------------------
ttr                                0.8493   V / N
                                            ölçek: ratio_0_1
mattr                              0.9250   mean TTR of every sliding window of mattr_window words
                                            ölçek: ratio_0_1
avg_sent_len_word                 12.1667   mean words per sentence
                                            ölçek: length

-- İngilizce şema (lang="en") --------------------
182 öznitelik çıkarıldı (Türkçe: 208).
anahtar                            tr     en
agglutination_depth               var    yok
atesman                           var    yok
flesch_reading_ease               yok    var
polysyllabic_word_ratio           yok    var
```

> **Şema dile göre değişir (K11).** Taban şema Türkçede 208, İngilizcede 182
> anahtar. Fark tek bir sayı değil: `morphological_zeyrek` grubunun 24 anahtarı
> ile Türkçeye özgü okunabilirlik formülleri İngilizcede yok; Flesch/SMOG
> ailesi ve `char_q`/`char_w`/`char_x` ise yalnız İngilizcede var. Bu yüzden
> anahtarları elle listelemek yerine `k in oznitelikler` diye sorun.

---

## `02_korpus_analizi.py` — korpus → CSV

Zincirin tamamı: `analyze_corpus()` → `save_csv()`. Ardından parçalar
arasında en çok değişen oranları
sıralar; `pandas` varsa sabit sütunları eler ve birbirini tekrarlayan
öznitelik çiftlerini listeler.

```bash
python examples/02_korpus_analizi.py korpus/   # kendi korpusunuz
python examples/02_korpus_analizi.py           # küçük demo korpus üretir
```

Depoda korpus yok, bu yüzden argümansız çalıştırıldığında script
`examples/output/demo_korpus/` altına dört küçük metin yazar ve onları
çözümler. Var olmayan bir dizin verirseniz traceback değil, net bir mesajla
çıkar:

```
Korpus bulunamadı: yok_boyle_bir_korpus
Beklenen düzen: korpus/Etiket_Başlık.txt
```

Demo korpusla gerçek çıktı:

```
4 parça yüklendi (4 kaynak).
  [1/4] akşam #0
  ...
CSV yazıldı: examples\output\korpus_oznitelikleri.csv (4 satır, 211 sütun)

-- Parçalar arasında en çok değişen 10 oran ------------
tense_past_def                 sd=  0.4815
morph_tense_past               sd=  0.4320
morph_tense_pres               sd=  0.4159
...

Sabit sütunlar elendi: 208 -> 163
|r| >= 0.95 olan çift sayısı: 1193
  hapax_ratio                  sichel_s                     r=1.000
  zipf_exponent                zipf_mandelbrot_s            r=1.000
```

`pandas` kurulu değilken aynı script:

```
(pandas kurulu değil; sabit sütun ve korelasyon blokları atlandı.)
Kurmak için: pip install pandas
```

> **Demo korpusun sayıları yorumlanmaz.** Dört parçayla hesaplanan bir
> korelasyon katsayısı güvenilir değildir — 1193 çift, korpusun küçüklüğünün
> sonucudur, metinlerin bir özelliği değil. Blok kalıbı gösterir.

> `save_csv` 2026-09-23'te public oldu (`__all__` dokuz ad) ve adı
> `records_to_csv`'ydi. Zinciri kapatan adım public olmadığı sürece kullanıcı
> onu bulamıyordu. `to_csv` denmedi: pandas'ta o bir metot (`df.to_csv`),
> serbest fonksiyon olarak özneyi kaybeder.
>
> Aynı tarihte `load_corpus` ters yöne gitti — `_load_corpus` olup public
> yüzeyden çıktı. `analyze_corpus` onun işini de yaptığı için tek başına
> çağrılmasına gerek kalmadı; kodu ve testleri duruyor.

---

## `03_duzenleme_oncesi_sonrasi.py` — aynı metnin iki sürümü

Bir metni düzenlediniz, çevirdiniz ya da sadeleştirdiniz: ölçülebilir olarak
**ne değişti?** Script bir grubu yan yana iki sütun hâlinde basar, sonra bütün
şemayı mutlak farka göre sıralayıp en çok kayan 10 özniteliği
`describe_feature(k)["description"]` ile birlikte gösterir.

```
-- sentence - Sentence statistics ----------------
öznitelik                            önce      sonra       fark
avg_sent_len_word                 30.5000     6.8333   -23.6667
long_sent_ratio                    0.5000     0.0000    -0.5000
sent_len_entropy                   1.0000     1.9183    +0.9183

-- En çok kayan 10 öznitelik ------------------------
avg_sent_len_char                307.0000 ->    56.1667 (-250.8333)
                               mean sentence length in characters
sentence_syllable_mean           113.0000 ->    20.5000 (-92.5000)
                               syllables per sentence
...
195 öznitelik karşılaştırıldı, 13 tanesi ölçülemediği için atlandı.
Sayılar betimlemedir; hangisinin önemli olduğuna siz karar verirsiniz.
```

> **Ham fark ölçeğe bağlıdır.** Okunabilirlik puanı onlarca birim oynayabilir,
> bir oran en çok 1 oynar; bu yüzden liste büyük ölçekli anahtarlarla başlar.
> Tek ölçekte kalmak için `describe_feature(k)["scale"]` ile süzün.

---

## `04_matrisi_sakla.py` — pahalı adımı bir kez öde

Öznitelik çıkarımı kütüphanenin en pahalı adımıdır. Script
**çıkar → kaydet → tekrar tekrar yükle** kalıbını gösterir: matris `.npy`,
sütun adları ayrı bir JSON dosyasında.

```
3 metin çözümleniyor (pahalı adım)...
Kaydedildi:
  examples\output\matris.npy
  examples\output\matris_sutunlari.json

Geri yüklendi: şekil (3, 208) (3 metin x 208 öznitelik)
Üretildiği sürüm: 0.1.0, dil: tr
İlk 5 sütun adı: ['n_lemma_count', 'avg_word_length', 'word_length_cv', 'entropy', 'yule_k']
```

> **Neden önbelleğe almak güvenli?** Çıkarım metin başına bağımsızdır: bir
> metnin sayıları yalnız o metinden hesaplanır, eğitim kümesinden hiçbir
> istatistik öğrenilmez. Diskteki matris, aynı sürüm ve aynı parametrelerle
> yeniden çalıştırıldığında çıkacak olanın aynısıdır.

> **Sütun adları matrisin yanında saklanır.** `analyze()` sözlük döndürür,
> `.npy` ise adsız bir sayı dizisi — ikisini ayrı ayrı kaydetmezseniz hangi
> sütunun hangi öznitelik olduğunu geri kurtaramazsınız. Script sürümü ve dili
> de yazar: ikisi değişirse matris geçersizdir.

Script model seçmez, `sklearn` import etmez, başarım sayısı yazdırmaz.
