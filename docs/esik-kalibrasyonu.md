# Cümle uzunluğu eşiklerinin kalibrasyonu

`short_sent_threshold` ve `long_sent_threshold` yayımlanmış bir kaynaktan
alınmadı, gazete köşe yazılarında, varsayılan cümle kuralıyla ölçülerek seçildi. Bu belge ölçümü kayda geçirir.

**Ölçüm:** 2026-10-06 (güncel). Önceki ölçüm 2026-07-28, aşağıda "Önceki kalibrasyon".

## Sonuç

| | `short_sent_threshold` | `long_sent_threshold` |
|---|---|---|
| **Türkçe** | 4 | 18 |
| **İngilizce** | 9 | 33 |

Eşikler `analyze(lang=...)` çağrısında dile göre çözümlenir. Kendi eşiğinizi
`FeatureParams` ile verirseniz o kazanır; vermediğiniz alan yukarıdaki
değerinde kalır ([ayrıntı](tr/nasil/parametreler.md)).

## Yöntem

| | Türkçe | İngilizce |
|---|---|---|
| Kaynak | KEMİK (YTÜ) köşe yazısı korpusları | KEMİK `30Columnists` |
| Yazar | 162 | 30 |
| Yazı | 4.321 | 1.485 |
| Ölçülen sözcük | 2.114.978 | 1.106.919 |
| **Ölçülen cümle** | **197.990** | **52.745** |

Tam korpus kullanıldı, örnekleme yapılmadı. Metinler paylaşılmaz, yalnız sayılar
yayımlanır. Cümle sınırları kütüphanenin varsayılan cümle kuralıyla bulundu
(`. ? ! …` her zaman, `:` yalnız sonrası yeni cümle gibi başlıyorsa; kısaltma
noktası bitirmez); uzunluk noktalamasız sözcük sayısıdır (`sentence` grubuyla aynı).
Öznitelik çıkarımı çalıştırılmadı, yalnız cümle başına sözcük sayısı gerekiyordu.

Eşik olarak 15. ve 85. yüzdelik seçildi. "Aykırı değer ortalaması" gibi bir
ölçüt kullanılmadı, çünkü "aykırı değer" tanımı zaten bir eşik gerektirir ve
eşiği oradan türetmek döngüsel olurdu.

### Ham yüzdelik tablosu

| Yüzdelik | TR (n = 197.990) | EN (n = 52.745) |
|---|---|---|
| 5. | 2,0 | 5,0 |
| 10. | 3,0 | 7,0 |
| **15.** | **4,0** | **9,0** |
| 25. | 5,0 | 12,0 |
| 50. (medyan) | 9,0 | 19,0 |
| 75. | 14,0 | 28,0 |
| **85.** | **18,0** | **33,0** |
| 90. | 20,0 | 37,0 |
| 95. | 25,0 | 44,0 |

## Neden dile özgü eşik

İki dil için tek bir eşik çifti, örneğin 5 ve 30, iki dilde de yanlış yerde
durur. Türkçede 30 sözcük 95. yüzdeliğin (25) bile üstünde: `long_sent_ratio`
pratikte sıfıra yakın üretir. İngilizcede aynı sayı 75. (28) ile 85. (33)
yüzdelik arasına denk gelir.

Sebebi tipolojik: Türkçe sondan eklemeli, tek sözcük analitik bir dilde yan
cümlenin taşıdığı bilgiyi yüklenebiliyor. Yüzeysel sözcük sayısı iki dilde aynı
şeyi ölçmüyor.

## Ateşman (1997) ile karşılaştırma

Ateşman (1997), s.74'te formülün kalibrasyon uçlarını veriyor: en kolay metin
ortalama **4** sözcüklük cümle, en zor metin **30**.

Türkçe `short_sent_threshold=4` kalibrasyondan gelir. Ateşman'ın "en kolay
metin" değeriyle örtüşmesi yalnız bir nottur: o sayı bir metnin ortalamasıdır,
eşik değildir, bu yüzden kaynak olarak gösterilmez, 30 için geçerli olan
gerekçenin aynısı. Ateşman s.73'teki Türkçe normu
(ortalama cümle 9-10 sözcük) da korpusun medyanıyla (9,0) tutuyor.

Ateşman'ın 30'u `long` için **kullanılmadı**: o sayı en zor metnin ortalaması,
tek bir cümlenin "uzun" sayılma eşiği değil. Eşik olarak kullanıldığında
Türkçede 95. yüzdeliğin üstünde kalıyor.

## Önceki kalibrasyon (2026-07-28, yerini aldı)

Eşikler önce roman ağırlıklı korpuslarda, spaCy ayrıştırıcısının cümleleriyle
ölçülmüştü: TR 15 yazar / 1.089.841 cümle, EN 10 yazar / 341.892 cümle.
Sonuç TR 4/18, EN 7/39 idi. 2026-10-06'da `sentence` grubu varsayılan cümle
kuralına geçti; eşikler bu kuralla ölçülen köşe yazılarına göre yeniden belirlendi.
Türkçe değerler (4/18) değişmedi, İngilizce 7/39'dan 9/33'e geçti.

| Yüzdelik | TR (n = 1.089.841) | EN (n = 341.892) |
|---|---|---|
| 5. | 3,0 | 4,0 |
| 10. | 4,0 | 6,0 |
| 15. | 4,0 | 7,0 |
| 25. | 6,0 | 10,0 |
| 50. (medyan) | 9,0 | 18,0 |
| 75. | 14,0 | 30,0 |
| 85. | 18,0 | 39,0 |
| 90. | 22,0 | 46,0 |
| 95. | 28,0 | 58,0 |

O dönemde 15./85. ile 10./90. adayı, `short_sent_ratio` ve `long_sent_ratio`
değerlerinin yazar kimliği tarafından açıklanan varyans oranı (η²) ile
karşılaştırılmıştı; 15./85. dört ölçümün hepsinde eşit ya da daha ayırt ediciydi
(TR short 0,2745 / 0,2745; TR long 0,4021 / 0,4194; EN short 0,0893 / 0,1279; EN long
0,2701 / 0,2801). Bu karşılaştırma yeni korpusta **tekrarlanmadı**; 15./85. seçimi
önceki sonuca dayanır.

## Kapsam sınırı

**Eşikler gazete köşe yazılarıyla kalibre edildi.** Köşe yazısı tek bir tür.

Romanda diyalog satırları çok kısa cümle ürettiği için aynı eşikler başka dağılım verir:
Türkçe romanda varsayılan kuralla cümlelerin yaklaşık %26,5'i 4 sözcükten kısa,
%6,6'sı 18 sözcükten uzun (köşe yazısında %12,1 ve %13,0). Teknik metin, transkript,
şiir, hukuk metni ya da ders kitabında da eşiklerin uygun olacağı **garanti
değildir**. Bu türlerle çalışıyorsanız kendi korpusunuzun yüzdeliklerini hesaplayıp
`FeatureParams` ile geçirin.

Ayrıca `short_sent_ratio` ve `long_sent_ratio` **iki dilde kıyaslanamaz**: aynı
isimli sütun iki dilde farklı eşikle ölçülür. "Türkçe metinler daha kısa
cümleli" gibi bir sonuç çıkarmadan önce bunu göz önüne alın; ölçtüğünüz şey dil
farkı değil, eşik farkı olabilir. Ortak eşik isterseniz **iki alanı da**
açıkça verin, örneğin `FeatureParams(short_sent_threshold=5,
long_sent_threshold=30)`, ve aynı nesneyi iki dile geçirin. Yalnız birini
verirseniz öteki yine dile göre çözümlenir.
