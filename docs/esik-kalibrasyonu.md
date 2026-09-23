# Cümle uzunluğu eşiklerinin kalibrasyonu

`short_sent_threshold` ve `long_sent_threshold` **yayımlanmış bir kaynaktan
alınmadı**, roman korpuslarında ölçülerek seçildi. Bu belge ölçümün
yöntemini, sonucunu ve sınırlarını kayda geçirir.

**Ölçüm tarihi:** 2026-07-28 · **Bu depoya taşındı:** 2026-09-23

---

## Sonuç

| | `short_sent_threshold` | `long_sent_threshold` |
|---|---|---|
| **Türkçe** | 4 | 18 |
| **İngilizce** | 7 | 39 |

Bu değerler `DEFAULT_PARAMS_BY_LANG` içinde; `analyze(lang=...)` dile göre
seçer. `FeatureParams`'ın kendi alan varsayılanı olan 5/30 tr/en'de **hiç
kullanılmaz** — yalnız başka bir dil eklenirse devreye girecek nötr yedektir.

Kendi eşiğinizi vermek isterseniz `analyze(params=FeatureParams(...))` her
zaman önceliklidir.

---

## Neden sabit bir eşik yetmiyordu

Önceki sürüm iki dil için tek bir çift kullanıyordu: 5 ve 30. Ölçüm bunun
iki dilde de yanlış yerde durduğunu gösterdi:

- **Türkçede `long=30` neredeyse hiç tetiklenmiyordu.** 30 sözcük, Türkçe
  roman korpusunun **95. yüzdeliğinin (28) bile üstünde**. `long_sent_ratio`
  pratikte sıfıra yakın bir değer üretiyordu.
- **İngilizcede aynı sabit tam 75. yüzdeliğe denk geliyordu.** "Uzun" diye
  işaretlenen kesim metnin çeyreğiydi — gerçek bir kuyruk değil.

Sebebi tipolojik: Türkçe sondan eklemeli, tek sözcük analitik bir dilde yan
cümlenin taşıdığı bilgiyi yüklenebiliyor. Yüzeysel sözcük sayısı iki dilde
aynı şeyi ölçmüyor.

---

## Yöntem

### Korpus

| | Türkçe | İngilizce |
|---|---|---|
| Yazar | 15 | 10 |
| Segment (1000 sözcük) | 9.838 | 6.263 |
| Yaklaşık sözcük | 9,84 M | 6,26 M |
| **Ölçülen cümle** | **1.089.841** | **341.892** |

Her iki set de roman/kurgu. Tam korpus kullanıldı, örnekleme yapılmadı.
Yazar sayısı iki dil arasında eşitlenmedi (15'e 10); yüzdelik kestirimi için
istatistiksel gereklilik değil, mevcut tüm veriyi kullanmak kestirimi daha
kararlı kılar.

### Cümle sınırı

Gerçek spaCy cümle sınırı tespiti — üretimde kullanılanın aynısı, aynı model
ve aynı 1000 sözcüklük segment konvansiyonu. Öznitelik çıkarımı
çalıştırılmadı; yalnız cümle başına sözcük sayısı gerekiyordu.

### Neden yüzdelik, "aykırı değer ortalaması" değil

"Aykırı değer" tanımı zaten bir eşik gerektirir. Eşiği aykırı değerlerin
ortalamasından türetmek döngüsel olurdu. Bunun yerine dağılımın tamamının
yüzdelikleri kullanıldı: eşiksiz ve dile özgü.

---

## Ham yüzdelik tablosu

| Yüzdelik | TR (n = 1.089.841) | EN (n = 341.892) |
|---|---|---|
| 5. | 3,0 | 4,0 |
| 10. | 4,0 | 6,0 |
| **15.** | **4,0** | **7,0** |
| 25. | 6,0 | 10,0 |
| 50. (medyan) | 9,0 | 18,0 |
| 75. | 14,0 | 30,0 |
| **85.** | **18,0** | **39,0** |
| 90. | 22,0 | 46,0 |
| 95. | 28,0 | 58,0 |

---

## Hangi yüzdelik çifti: 15./85. mi, 10./90. mı

İlk öneri 10./90.'dı. 15./85. önerisi geldiğinde ("daha fazla kullanım
yakalar, daha ayırt edici olur") varsayım kabul edilmeden önce ölçüldü:
zaten toplanmış ham veri üzerinden, `short_sent_ratio` ve `long_sent_ratio`
değerlerinin **yazar kimliği tarafından açıklanan varyans oranı** (η²) iki
seçenek için karşılaştırıldı.

| | 10./90. | 15./85. |
|---|---|---|
| TR `short_ratio` | 0,2745 | 0,2745 |
| TR `long_ratio` | 0,4021 | **0,4194** |
| EN `short_ratio` | 0,0893 | **0,1279** |
| EN `long_ratio` | 0,2701 | **0,2801** |

15./85. dört ölçümün hepsinde eşit ya da daha ayırt edici. TR `short_ratio`
eşit çünkü Türkçede 10. ve 15. yüzdelik aynı değeri (4,0) veriyor.

---

## Literatürle karşılaştırma (2026-09-23'te eklendi)

Kalibrasyondan sonra Ateşman (1997) birincil kaynağı bulundu. Makale s.74'te
formülün kalibrasyon uçlarını veriyor:

| | Sözcük uzunluğu (hece) | **Cümle uzunluğu (sözcük)** |
|---|---|---|
| en kolay metin | 2,2 | **4** |
| en zor metin | 3,0 | **30** |

**Türkçe `short_sent_threshold=4`, Ateşman'ın "en kolay metin" değeriyle
birebir aynı.** İki bağımsız yol — 1997'de metin zorluğu üzerinden küme
analizi, 2026'da roman korpusunun dağılımı — aynı sayıyı verdi.

**`long` için Ateşman'ın 30'u kullanılmadı.** O sayı *en zor metnin
ortalaması*, tek bir cümlenin "uzun" sayılma eşiği değil. Eşik olarak
kullanıldığında Türkçede 95. yüzdeliğin üstünde kalıyor ve neredeyse hiç
tetiklenmiyor — eski 5/30 ayarının sorunu tam olarak buydu.

Ateşman s.73 ayrıca Türkçe normunu veriyor: ortalama sözcük 2,6 hece,
ortalama cümle **9-10 sözcük**. Korpusun medyanı 9,0 — bu da tutuyor.

> **Not:** Bir dil modeli "1-10 kısa / 11-20 orta / 21+ uzun" biçiminde bir
> cümle sınıflandırmasını Ateşman'a atfetti. Makalenin dört sayfası da
> okundu; **böyle bir şema yok**. s.74'teki sınıflandırma tablosu
> *okunabilirlik puanının* bantlarıdır (90-100 çok kolay … 1-29 çok zor).
> Şemanın kaynağı bilinmiyor.

---

## Kapsam ve genelleme sınırı

🔴 **Eşikler yalnız roman/kurgu türü için kalibre edildi.**

İngilizce korpus: Christie, Doyle, Dickens, Fitzgerald, Hemingway, Melville,
Austen, Tolkien, Hardy, Chesterton. Türkçe korpus: 15 roman yazarı.

Farklı türlerde — teknik metin, transkript, şiir, hukuk metni, ders kitabı —
aynı eşiklerin uygun olacağı **garanti değildir**. Bu türlerle çalışıyorsanız
kendi korpusunuzun yüzdeliklerini hesaplayıp `FeatureParams` ile geçirin.

## `short_sent_ratio` ve `long_sent_ratio` iki dilde kıyaslanamaz

Aynı isimli sütun iki dilde **farklı eşikle** ölçülür. "Türkçe metinler daha
kısa cümleli" gibi bir sonuç çıkarmadan önce bunu göz önüne alın; ölçülen şey
dil farkı değil, eşik farkı olabilir. Ortak eşik isterseniz aynı
`FeatureParams` nesnesini iki dile de verin.
