# Sınırlılıklar

Bu sayfa kütüphanenin nerede zayıf olduğunu anlatır. Yöntem bölümü yazarken
buraya bakın.

## 1. Cümle eşikleri yalnız roman/kurgu için kalibre edildi

`short_sent_ratio` ve `long_sent_ratio` eşikleri (TR 4/18, EN 7/39) roman
korpuslarında cümle uzunluğu dağılımının 15. ve 85. yüzdeliğinden
türetildi:

| Dil | Yazar | Cümle |
|---|---|---|
| Türkçe | 15 | 1 089 841 |
| İngilizce | 10 | 341 892 |

Her iki set de **aynı tür**: roman/kurgu. Teknik metin, transkript, şiir
ya da çocuk kitabı için genelleneceği **garanti değil.** Kendi türünüzde
çalışıyorsanız eşikleri kendi korpusunuzdan türetmeyi düşünün —
[yöntem burada](../../esik-kalibrasyonu.md).

## 2. Bu kütüphanenin kendi türevleri

Bazı öznitelikler literatürde adı olan ölçüler değil, bu kütüphanenin
tanımlarıdır. Künyeleri bunu açıkça yazar:

- `entropy_std` — Shannon entropisinin **parçalar arası standart sapması**.
  Entropi Shannon'ın, standart sapma bizim.
- `punct_entropy`, `sent_len_entropy` — Shannon formülünün noktalama ve
  cümle uzunluğu dağılımına uygulanması. Formül Shannon'ın, uygulama kararı
  bizim.
- `polysyllabic_word_ratio` — SMOG'un girdisinin oran biçimi. McLaughlin'in
  kendi ölçüsü değil.

Bunları kullanmakta sakınca yok. Tek koşul, künyeyi doğru kurmak: formülün
kaynağını verin, ölçünün kendisini kaynağa mal etmeyin. Yöntem bölümünüzde:

- ✗ "Shannon (1948) `entropy_std` ölçüsü"
- ✓ "Shannon (1948) entropisinin parçalar arası standart sapması
  (turkish-linguistic-features'ın tanımı)"

Sebep basit: Shannon entropiyi tanımladı, parçalar arası standart sapmasını
tanımlamadı. Birinci yazım okuyucuya, kaynakta aranınca bulunacak bir ölçü
olduğunu ima ediyor.

## 3. On bir künye ikincil kaynaktan

145 künyenin **11'i** `as cited in` ile işaretlidir — birincil kaynağa
ulaşılamadı, formül aktaran kaynaktan alındı. Örnek:

```text
Herdan (1960/1964), as cited in Tweedie & Baayen (1998) p.327, eq. (5)
```

Etkilenen ölçüler arasında `herdan_c`, `brunet_w`, `dugast_u`, `yule_k`,
`simpson_d`, `heaps_beta`, `lix` var. Formüller doğrulandı ama **birincil
kaynağın kendi ifadesiyle** karşılaştırılmadı.

Yöntem bölümünüzde aktarımı aynen taşıyın; birincil kaynağı okumuş gibi
göstermeyin.

## 4. spaCy modeli sonuçların parçası

Cümle bölme, sözcük türü ve bağlılık öznitelikleri modelden gelir. Model
değişirse sayılar değişir.

Doğrulanmış kombinasyon: spaCy 3.8.16, `en_core_web_sm` 3.8.0,
`tr_core_news_md` 1.0.

Türkçe modelin hata sanılabilecek iki tuhaflığı (sürüm numarası çelişkisi ve
`W094` uyarısı) [öğreticide](../baslangic.md#2-dil-verisini-kurun)
anlatılıyor; ikisi de zararsız.

## 5. Türkçe morfoloji Zeyrek'e bağlı

`morphological_zeyrek` grubundaki 24 öznitelik Zeyrek'ten gelir — Zemberek
morfotaktiğinin Python aktarımı. Zeyrek'in çözümleyemediği bir kelime
öznitelikten düşer.

Zeyrek bir **çözümleyicidir, belirsizlik gidericisi değildir**: aynı yüzey
biçimi için birden çok çözümleme dönebilir ve bağlama bakarak doğrusunu
seçmez.

## 6. Metin uzunluğuna duyarlılık

Sözcüksel zenginlik ölçülerinin çoğu uzunlukla değişir. `ttr` en uçtaki
örnektir: metin uzadıkça mutlaka düşer.

`mattr`, `mtld` ve `vocd_d` uzunluğa TTR'den daha az duyarlıdır ama
bağımsız değildir; `mtld` ve `vocd_d` Türkçede belirgin biçimde kayar
([ölçüm örneği](https://github.com/efeziya1/turkish-linguistic-features/blob/main/examples/09_uzunluk_duyarliligi.py)). Onlar da en az
100 kelime ister. Farklı uzunluktaki metinleri karşılaştırıyorsanız önce
`segment_size` ile aynı boya getirin ([nasıl](../nasil/segmentleme.md)).

## 7. Paragraf öznitelikleri girdinin biçimlendirmesine bağlı

Beş `para_*` özniteliği paragraf sınırını **boş satırdan** bulur. Tek satır
sonu paragraf saymaz — aksi hâlde satır satır sarılmış bir metinde her satır
paragraf olurdu.

Sonuç: metninizde boş satır yoksa metnin tamamı tek paragraf sayılır.
`para_len_mean` bütün metnin kelime sayısına eşitlenir, iki CV NaN döner.
Kütüphane bunu düzeltemez — silinmiş paragraf sınırı geri getirilemez.

Bu, PDF ve EPUB'dan çıkarılmış metinlerde **yaygındır**: paragraflar arasındaki
boş satırlar çıkarım sırasında kaybolur. Kendi metninizde hangi özniteliklerin
bu yüzden ölçülemediğini [NaN haritası örneğiyle](https://github.com/efeziya1/turkish-linguistic-features/blob/main/examples/07_nan_haritasi.py)
görebilirsiniz.

1000 kelimeyi geçen bir metinde hiç paragraf sınırı bulunamazsa
`ParagraphStructureWarning` basılır. Uyarıyı görürseniz iki yol var: kaynak
metni paragrafları boş satırla ayrılmış hâlde yeniden çıkarın, ya da
`groups` ile `paragraph` grubunu dışarıda bırakın.

## 8. Adayların yarısı hâlâ doğrulanmadı

141 satır doğrulama adayı bile değil (saf tanım, etiket şeması ya da
bizim türevimiz).
Kalan **92 adayın 48'i** bitmiş (47 ✅ + 1 🟡), **44'ü 🔍 açık**.

Sebebi [doğrulama sistemi](dogrulama.md) sayfasında: kaynakların çoğu
formülü yayımlar, o formülün uygulandığı bir sayısal örnek vermez. Bu
özellikle `lexical` grubunda belirgin — 30 adayın 7'si doğrulanmış.

## 9. Paket henüz PyPI'da değil

Erken geliştirme aşamasında (0.x). Kurulum klondan yapılır. 1.0'a kadar anahtar
adları ve genel API değişebilir; değişiklikler sürüm notlarında duyurulur.
