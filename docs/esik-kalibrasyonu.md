# Cümle uzunluğu eşiklerinin kalibrasyonu

`short_sent_threshold` ve `long_sent_threshold` yayımlanmış bir kaynaktan
alınmadı, roman korpuslarında ölçülerek seçildi. Bu belge ölçümü kayda geçirir.

**Ölçüm:** 2026-07-28

## Sonuç

| | `short_sent_threshold` | `long_sent_threshold` |
|---|---|---|
| **Türkçe** | 4 | 18 |
| **İngilizce** | 7 | 39 |

Eşikler `analyze(lang=...)` çağrısında dile göre çözümlenir. Kendi eşiğinizi
`FeatureParams` ile verirseniz o kazanır; vermediğiniz alan yukarıdaki
değerinde kalır ([ayrıntı](tr/nasil/parametreler.md)).

## Yöntem

| | Türkçe | İngilizce |
|---|---|---|
| Yazar | 15 | 10 |
| Segment (1000 sözcük) | 9.838 | 6.263 |
| **Ölçülen cümle** | **1.089.841** | **341.892** |

Her iki set de roman/kurgu. Tam korpus kullanıldı, örnekleme yapılmadı. Cümle
sınırları üretimde kullanılan spaCy modelinin kendisiyle bulundu; öznitelik
çıkarımı çalıştırılmadı, yalnız cümle başına sözcük sayısı gerekiyordu.

Eşik olarak 15. ve 85. yüzdelik seçildi. "Aykırı değer ortalaması" gibi bir
ölçüt kullanılmadı, çünkü "aykırı değer" tanımı zaten bir eşik gerektirir ve
eşiği oradan türetmek döngüsel olurdu.

### Ham yüzdelik tablosu

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

## Neden dile özgü eşik

İki dil için tek bir eşik çifti, örneğin 5 ve 30, iki dilde de yanlış yerde
durur. Türkçede 30 sözcük 95. yüzdeliğin (28) bile üstünde — `long_sent_ratio`
pratikte sıfır üretir. İngilizcede aynı sayı tam 75. yüzdeliğe denk gelir,
yani "uzun" diye işaretlenen kesim metnin çeyreği olur.

Sebebi tipolojik: Türkçe sondan eklemeli, tek sözcük analitik bir dilde yan
cümlenin taşıdığı bilgiyi yüklenebiliyor. Yüzeysel sözcük sayısı iki dilde aynı
şeyi ölçmüyor.

## 15./85. mi, 10./90. mı

İki aday, `short_sent_ratio` ve `long_sent_ratio` değerlerinin **yazar kimliği
tarafından açıklanan varyans oranı** (η²) üzerinden karşılaştırıldı.

| | 10./90. | 15./85. |
|---|---|---|
| TR `short_ratio` | 0,2745 | 0,2745 |
| TR `long_ratio` | 0,4021 | **0,4194** |
| EN `short_ratio` | 0,0893 | **0,1279** |
| EN `long_ratio` | 0,2701 | **0,2801** |

15./85. dört ölçümün hepsinde eşit ya da daha ayırt edici. TR `short_ratio`
eşit, çünkü Türkçede 10. ve 15. yüzdelik aynı değeri (4,0) veriyor.

## Ateşman (1997) ile karşılaştırma

Ateşman (1997), s.74'te formülün kalibrasyon uçlarını veriyor: en kolay metin
ortalama **4** sözcüklük cümle, en zor metin **30**.

Türkçe `short_sent_threshold=4` kalibrasyondan gelir. Ateşman'ın "en kolay
metin" değeriyle örtüşmesi yalnız bir nottur: o sayı bir metnin ortalamasıdır,
eşik değildir, bu yüzden kaynak olarak gösterilmez — 30 için geçerli olan
gerekçenin aynısı. Ateşman s.73'teki Türkçe normu
(ortalama cümle 9-10 sözcük) da korpusun medyanıyla (9,0) tutuyor.

Ateşman'ın 30'u `long` için **kullanılmadı**: o sayı en zor metnin ortalaması,
tek bir cümlenin "uzun" sayılma eşiği değil. Eşik olarak kullanıldığında
Türkçede 95. yüzdeliğin üstünde kalıyor.

## Kapsam sınırı

🔴 **Eşikler yalnız roman/kurgu türü için kalibre edildi.**

Teknik metin, transkript, şiir, hukuk metni ya da ders kitabında aynı
eşiklerin uygun olacağı **garanti değildir**. Bu türlerle çalışıyorsanız kendi
korpusunuzun yüzdeliklerini hesaplayıp `FeatureParams` ile geçirin.

Ayrıca `short_sent_ratio` ve `long_sent_ratio` **iki dilde kıyaslanamaz**: aynı
isimli sütun iki dilde farklı eşikle ölçülür. "Türkçe metinler daha kısa
cümleli" gibi bir sonuç çıkarmadan önce bunu göz önüne alın; ölçtüğünüz şey dil
farkı değil, eşik farkı olabilir. Ortak eşik isterseniz **iki alanı da**
açıkça verin, örneğin `FeatureParams(short_sent_threshold=5,
long_sent_threshold=30)`, ve aynı nesneyi iki dile geçirin. Yalnız birini
verirseniz öteki yine dile göre çözümlenir.
