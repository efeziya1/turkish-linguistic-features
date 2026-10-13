# Tümce uzunluğu eşiklerinin kalibrasyonu

`short_sent_threshold` ve `long_sent_threshold` yayımlanmış bir kaynaktan
alınmadı, gazete köşe yazılarında, varsayılan tümce kuralı ve varsayılan sözcükle ölçülerek seçildi. Bu belge ölçümü kayda geçirir.

**Ölçüm:** 2026-10-06.

## Sonuç

| | `short_sent_threshold` | `long_sent_threshold` |
|---|---|---|
| **Türkçe** | 4 | 17 |
| **İngilizce** | 8 | 32 |

Eşikler `analyze(lang=...)` çağrısında dile göre uygulanır. Kendi eşiğinizi
`FeatureParams` ile verirseniz o kazanır; vermediğiniz alan yukarıdaki
değerinde kalır ([ayrıntı](tr/nasil/parametreler.md)).

## Yöntem

| | Türkçe | İngilizce |
|---|---|---|
| Kaynak | KEMİK (YTÜ) köşe yazısı korpusları | KEMİK `30Columnists` |
| Yazar | 162 | 30 |
| Yazı | 4.321 | 1.485 |
| Ölçülen sözcük | 2.108.415 | 1.078.588 |
| **Ölçülen tümce** | **197.990** | **52.745** |

Tam korpus kullanıldı, örnekleme yapılmadı. Metinler paylaşılmaz, yalnız sayılar
yayımlanır. Tümceler ve sözcükler `sentence` grubunun saydığı gibi, kütüphanenin varsayılan
tümce kuralı ve varsayılan sözcüğüyle sayıldı; ikisinin örnekli tanımı
[Kavramlar](tr/aciklama/kavramlar.md#sozcuk-ve-tumce) sayfasında. Bir tümcenin uzunluğu
içindeki sözcük sayısıdır; hiç harf içermeyen tümce sayılmaz. Yalnız bu uzunluklar gerektiği
için başka öznitelik hesaplanmadı.

Eşik olarak 15. ve 85. yüzdelik seçildi. "Aykırı değer ortalaması" gibi bir
ölçüt kullanılmadı, çünkü "aykırı değer" tanımı zaten bir eşik gerektirir ve
eşiği oradan türetmek döngüsel olurdu.

### Ham yüzdelik tablosu

| Yüzdelik | TR (n = 197.990) | EN (n = 52.745) |
|---|---|---|
| 5. | 2,0 | 5,0 |
| 10. | 3,0 | 7,0 |
| **15.** | **4,0** | **8,0** |
| 25. | 5,0 | 11,0 |
| 50. (medyan) | 9,0 | 19,0 |
| 75. | 14,0 | 27,0 |
| **85.** | **17,0** | **32,0** |
| 90. | 20,0 | 36,0 |
| 95. | 25,0 | 43,0 |

Türkçede 85. yüzdelik sınırda: 17 eşiğinde tümcelerin %15,0'ı, 18'de %12,9'u uzun sayılır.

## Neden dile özgü eşik

İki dil için tek bir eşik çifti, örneğin 5 ve 30, iki dilde de yanlış yerde
durur. Türkçede 30 sözcük 95. yüzdeliğin (25) bile üstünde: `long_sent_ratio`
pratikte sıfıra yakın üretir. İngilizcede aynı sayı 75. (27) ile 85. (32)
yüzdelik arasına denk gelir.

Sebebi tipolojik: Türkçe sondan eklemeli, tek sözcük analitik bir dilde yan
tümcenin taşıdığı bilgiyi yüklenebiliyor. Yüzeysel sözcük sayısı iki dilde aynı
şeyi ölçmüyor.

## Ateşman (1997) ile karşılaştırma

Ateşman (1997, s.73) Türkçede ortalama tümce uzunluğunu 9-10 sözcük olarak veriyor;
korpusun medyanı (9,0) bununla tutuyor.

## Kapsam sınırı

**Eşikler gazete köşe yazılarıyla kalibre edildi.** Köşe yazısı tek bir tür.

Roman, teknik metin, transkript, şiir, hukuk metni ya da ders kitabında eşiklerin
uygun olacağı **garanti değildir**.

Ayrıca `short_sent_ratio` ve `long_sent_ratio` **iki dilde kıyaslanamaz**: aynı
isimli sütun iki dilde farklı eşikle ölçülür. Ortak eşik isterseniz **iki alanı
da** açıkça verin, örneğin `FeatureParams(short_sent_threshold=5,
long_sent_threshold=30)`, ve aynı nesneyi iki dile geçirin. Yalnız birini
verirseniz öteki yine dile göre uygulanır.
