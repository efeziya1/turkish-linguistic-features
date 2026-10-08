# Cümle uzunluğu eşiklerinin kalibrasyonu

`short_sent_threshold` ve `long_sent_threshold` yayımlanmış bir kaynaktan
alınmadı, gazete köşe yazılarında, varsayılan cümle kuralı ve varsayılan kelimeyle ölçülerek seçildi. Bu belge ölçümü kayda geçirir.

**Ölçüm:** 2026-10-06 (güncel, varsayılan kelime tanımıyla). Önceki ölçümler aşağıda, "Önceki kalibrasyonlar".

## Sonuç

| | `short_sent_threshold` | `long_sent_threshold` |
|---|---|---|
| **Türkçe** | 4 | 17 |
| **İngilizce** | 8 | 32 |

Eşikler `analyze(lang=...)` çağrısında dile göre çözümlenir. Kendi eşiğinizi
`FeatureParams` ile verirseniz o kazanır; vermediğiniz alan yukarıdaki
değerinde kalır ([ayrıntı](tr/nasil/parametreler.md)).

## Yöntem

| | Türkçe | İngilizce |
|---|---|---|
| Kaynak | KEMİK (YTÜ) köşe yazısı korpusları | KEMİK `30Columnists` |
| Yazar | 162 | 30 |
| Yazı | 4.321 | 1.485 |
| Ölçülen sözcük | 2.108.415 | 1.078.588 |
| **Ölçülen cümle** | **197.990** | **52.745** |

Tam korpus kullanıldı, örnekleme yapılmadı. Metinler paylaşılmaz, yalnız sayılar
yayımlanır. Cümle sınırları kütüphanenin varsayılan cümle kuralıyla bulundu
(`. ? ! …` her zaman, `:` yalnız sonrası yeni cümle gibi başlıyorsa; kısaltma
noktası bitirmez). Uzunluk, cümledeki varsayılan kelime sayısıdır: boşlukla ayrılan, kenar
noktalaması atılan ve harf ya da rakam içeren birim (`sentence` grubuyla aynı yol:
`kural_cumleleri` + `cumle_birimleri`).
Öznitelik çıkarımı çalıştırılmadı, yalnız cümle başına sözcük sayısı gerekiyordu.

Eşik olarak 15. ve 85. yüzdelik seçildi. "Aykırı değer ortalaması" gibi bir
ölçüt kullanılmadı, çünkü "aykırı değer" tanımı zaten bir eşik gerektirir ve
eşiği oradan türetmek döngüsel olurdu.

### Neden 15./85. (2026-10-08)

Aday yüzdelik çiftleri aynı köşe yazılarında karşılaştırıldı: her yazı için
`short_sent_ratio` ve `long_sent_ratio` hesaplandı ve yazılar arasındaki farkın ne
kadarının yazardan geldiği (η², tek yönlü varyans analizi) ölçüldü.

| Çift | TR eşik | TR η² kısa | TR η² uzun | EN eşik | EN η² kısa | EN η² uzun |
|---|---|---|---|---|---|---|
| 5/95 | 2 / 25 | 0,305 | 0,501 | 5 / 43 | 0,275 | 0,518 |
| 10/90 | 3 / 20 | 0,425 | 0,549 | 7 / 36 | 0,371 | 0,549 |
| **15/85** | **4 / 17** | **0,484** | **0,571** | **8 / 32** | **0,394** | **0,545** |
| 20/80 | 5 / 16 | 0,517 | 0,573 | 10 / 29 | 0,449 | 0,532 |
| 25/75 | 5 / 14 | 0,517 | 0,576 | 11 / 27 | 0,469 | 0,522 |

η² tek başına bir çift seçmez: kısa cümle payında eşik medyana yaklaştıkça sürekli
artar, çünkü pay daha çok cümleye dayanır. Ama o noktada "kısa" uç olmaktan çıkar
(25/75'te Türkçe cümlelerin %19'u kısa sayılır). 15/85, uçları ölçmeyi koruyan
çiftler içinde 10/90'dan dört ölçümün üçünde daha ayırt edici; İngilizce uzun
cümlede 10/90 çok az önde (0,549'a 0,545).

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

Türkçede 85. yüzdelik sınırda: 17 eşiğinde cümlelerin %15,0'ı, 18'de %12,9'u uzun sayılır.

## Neden dile özgü eşik

İki dil için tek bir eşik çifti, örneğin 5 ve 30, iki dilde de yanlış yerde
durur. Türkçede 30 sözcük 95. yüzdeliğin (25) bile üstünde: `long_sent_ratio`
pratikte sıfıra yakın üretir. İngilizcede aynı sayı 75. (27) ile 85. (32)
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

## Önceki kalibrasyonlar

### Varsayılan cümle kuralı, eski kelime (2026-10-06, yerini aldı)

Aynı köşe yazıları ve aynı cümleler; kelime = harf ya da rakam içeren spaCy tokenı. Sonuç TR 4/18,
EN 9/33 idi. Aynı gün varsayılan kelime boşluk birimi oldu ve eşikler yeniden ölçüldü. Kelime
tanımı yalnız spaCy'nin bir boşluk birimini böldüğü yerde uzunluğu değiştirir (`e-posta`, `%50`,
İngilizce `don't` → `do` + `n't`): Türkçe cümlelerin %2,8'inde, İngilizce cümlelerin %37,6'sında
uzunluk kısaldı, hiçbirinde uzamadı.

| Yüzdelik | TR (n = 197.990) | EN (n = 52.745) |
|---|---|---|
| 5. | 2,0 | 5,0 |
| 10. | 3,0 | 7,0 |
| 15. | 4,0 | 9,0 |
| 25. | 5,0 | 12,0 |
| 50. (medyan) | 9,0 | 19,0 |
| 75. | 14,0 | 28,0 |
| 85. | 18,0 | 33,0 |
| 90. | 20,0 | 37,0 |
| 95. | 25,0 | 44,0 |

### Roman korpusları, spaCy ayrıştırıcı cümleleri (2026-07-28, yerini aldı)

Eşikler önce roman ağırlıklı korpuslarda, spaCy ayrıştırıcısının cümleleriyle
ölçülmüştü: TR 15 yazar / 1.089.841 cümle, EN 10 yazar / 341.892 cümle.
Sonuç TR 4/18, EN 7/39 idi. 2026-10-06'da `sentence` grubu varsayılan cümle
kuralına geçti; eşikler bu kuralla ölçülen köşe yazılarına göre yeniden belirlendi.
Türkçe değerler (4/18) değişmedi, İngilizce 7/39'dan 9/33'e geçti; aynı gün kelime
tanımı değişince TR 4/17, EN 8/32 oldu (yukarıda).

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
0,2701 / 0,2801). Karşılaştırma 2026-10-08'de köşe yazılarında yeniden yapıldı
(yukarıda, "Neden 15./85.").

## Kapsam sınırı

**Eşikler gazete köşe yazılarıyla kalibre edildi.** Köşe yazısı tek bir tür.

Roman, teknik metin, transkript, şiir, hukuk metni ya da ders kitabında eşiklerin
uygun olacağı **garanti değildir**. Bu türlerle çalışıyorsanız kendi korpusunuzun yüzdeliklerini hesaplayıp
`FeatureParams` ile geçirin.

Ayrıca `short_sent_ratio` ve `long_sent_ratio` **iki dilde kıyaslanamaz**: aynı
isimli sütun iki dilde farklı eşikle ölçülür. "Türkçe metinler daha kısa
cümleli" gibi bir sonuç çıkarmadan önce bunu göz önüne alın; ölçtüğünüz şey dil
farkı değil, eşik farkı olabilir. Ortak eşik isterseniz **iki alanı da**
açıkça verin, örneğin `FeatureParams(short_sent_threshold=5,
long_sent_threshold=30)`, ve aynı nesneyi iki dile geçirin. Yalnız birini
verirseniz öteki yine dile göre çözümlenir.
