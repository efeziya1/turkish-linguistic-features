# Sınırlılıklar

Bu sayfa iki kısımdan oluşur. İlki kütüphanenin nerede zayıf olduğunu anlatır;
ikincisi kütüphanenin zayıflığı olmayan ama sonuçları yorumlarken bilmeniz
gereken noktaları. Yöntem bölümü yazarken ikisine de bakın.

## Kütüphanenin sınırlılıkları

### 1. Cümle eşikleri yalnız gazete köşe yazılarıyla kalibre edildi

`short_sent_ratio` ve `long_sent_ratio` eşikleri (TR 4/17, EN 8/32) gazete
köşe yazılarında, varsayılan cümle kuralı ve varsayılan kelimeyle ölçülen
cümle uzunluğu dağılımının 15. ve 85. yüzdeliğinden türetildi:

| Dil | Yazar | Cümle |
|---|---|---|
| Türkçe | 162 | 197 990 |
| İngilizce | 30 | 52 745 |

Köşe yazısı **tek bir tür**. Roman, teknik metin, transkript, şiir ya da
çocuk kitabı için genelleneceği **garanti değil.** Kendi türünüzde çalışıyorsanız eşikleri
kendi korpusunuzdan türetmeyi düşünün —
[yöntem burada](../../esik-kalibrasyonu.md).

### 2. On dört künye ikincil kaynaktan

165 künyenin **14'ü** `as cited in` ile işaretlidir — birincil kaynağa
ulaşılamadı, formül aktaran kaynaktan alındı. Örnek:

```text
Herdan (1960/1964), as cited in Tweedie & Baayen (1998) p.327, eq. (5)
```

Etkilenen ölçüler arasında `herdan_c`, `herdan_vm`, `maas_a2`, `brunet_w`,
`dugast_u`, `simpson_d`, `heaps_beta`, `lix`, `cttr`, `summer_s` var. Formüller doğrulandı ama **birincil
kaynağın kendi ifadesiyle** karşılaştırılmadı.

Yöntem bölümünüzde aktarımı aynen taşıyın; birincil kaynağı okumuş gibi
göstermeyin.

### 3. spaCy modeli sonuçların parçası

Sözcük türü, biçimbilim etiketleri, İngilizce lemmalar ve bağlılık
öznitelikleri (ayrıştırıcının kendi cümleleriyle) modelden gelir. Model
değişirse bu sayılar değişir. Türkçe lemmalar Zeyrek'ten gelir (§4).

Kelime ve cümle sayımı modelin etiketlerini kullanmaz. Varsayılan kelime,
boşlukla ayrılan ve kenar noktalaması atılan birimdir; varsayılan cümle
kuralı cümle bitiren işaretleri modelin tokenizer'ından okur. Bağlılık
öznitelikleri dışında her öznitelik bu kelimeyi sayar. Kelime başına etiket
isteyen öznitelikler (sözcük türü, lemma, biçimbilim) etiketi kelimenin
içindeki ilk kelime tokenından alır: model `Türk-Amerikan`'ı ya da İngilizce
`it's`'i birden çok tokena böler, kelime ilk parçanın etiketini taşır
(`Türk`, `it`). Bu, Türkçe köşe yazılarında kelimelerin %0,3'ünde,
İngilizcelerde %2,7'sinde olur. Bağlılık öznitelikleri modelin tokenlarını
sayar. Hangi özniteliğin hangi kelimeyi kullandığını
`describe_feature(key)["definitions"]["word"]` söyler.

Doğrulanmış kombinasyon: spaCy 3.8.16, `en_core_web_sm` 3.8.0,
`tr_core_news_md` 1.0.

Türkçe modelin hata sanılabilecek iki tuhaflığı (sürüm numarası çelişkisi ve
`W094` uyarısı) [öğreticide](../baslangic.md#2-dil-verisini-kurun)
anlatılıyor; ikisi de zararsız.

### 4. Türkçe morfoloji Zeyrek'e bağlı

`morphological_zeyrek` grubundaki 23 öznitelik ve Türkçe lemmalar Zeyrek'ten
gelir — Zemberek morfotaktiğinin Python aktarımı. Zeyrek'in çözümleyemediği bir
kelime Zeyrek özniteliklerinden düşer; lemması kesme işaretinden önceki kısmı
olur (`Pittsburgh'tan` → `pittsburgh`).

Zeyrek bir **çözümleyicidir, belirsizlik gidericisi değildir**: aynı yüzey
biçimi için birden çok çözümleme dönebilir ve bağlama bakarak doğrusunu
seçmez. Kütüphane bağlama bakmadan **ilk** çözümlemeyi alır.

Zeyrek çözümlemeleri ek geçişi sayısına göre sıralar, en azı önce gelir;
eşitlikte sıra, Python'un iç bir kümesinin dolaşım sırasında kalır ve bu sıra
`PYTHONHASHSEED`'e bağlıdır. TOMA veri setinde (57 metin, 8.215 farklı
sözcük) sözcüklerin %58,2'sinin birden çok çözümlemesi var ve **200 sözcüğün
(%2,4)** ilk çözümlemesi 0–3 tohumları arasında değişti. Yani aynı metnin
Zeyrek öznitelikleri Python süreçleri arasında az da olsa farklı çıkabilir.
Tekrar üretilebilir sayılar için tohumu Python başlamadan sabitleyin, örneğin
`PYTHONHASHSEED=0`.

### 5. Adayların yarısı hâlâ doğrulanmadı

82 satır doğrulama adayı bile değil (saf tanım, etiket şeması ya da
bizim türevimiz).
Kalan **144 adayın 48'i** bitmiş (46 ✅ + 2 🟡), **96'ü 🔍 açık**.

Sebebi [doğrulama sistemi](dogrulama.md) sayfasında: kaynakların çoğu
formülü yayımlar, o formülün uygulandığı bir sayısal örnek vermez. Bu
özellikle `lexical` grubunda belirgin — 36 adayın 7'si doğrulanmış.

### 6. Paket henüz PyPI'da değil

Erken geliştirme aşamasında (0.x). Kurulum klondan yapılır. 1.0'a kadar anahtar
adları ve genel API değişebilir; değişiklikler sürüm notlarında duyurulur.

## Kullanırken bilmeniz gerekenler

Bunlar kütüphanenin eksiği değil: ölçülerin kendi davranışı, girdi
gereksinimi ya da künye kuralı. Yine de sonuçları etkiler.

### 7. Bu kütüphanenin kendi türevleri

Bazı öznitelikler literatürde adı olan ölçüler değil, bu kütüphanenin
tanımlarıdır. Künyeleri bunu açıkça yazar:

- `punct_entropy`, `sent_len_entropy` — Shannon formülünün noktalama ve
  cümle uzunluğu dağılımına uygulanması. Formül Shannon'ın, uygulama kararı
  bizim.
- `polysyllabic_word_ratio` — SMOG'un girdisinin oran biçimi. McLaughlin'in
  kendi ölçüsü değil.

Bunları kullanmakta sakınca yok. Tek koşul, künyeyi doğru kurmak: formülün
kaynağını verin, ölçünün kendisini kaynağa mal etmeyin. Yöntem bölümünüzde:

- ✗ "Shannon (1948) `sent_len_entropy` ölçüsü"
- ✓ "Shannon (1948) entropisinin cümle uzunluğu dağılımına uygulanması
  (turkish-linguistic-features'ın tanımı)"

Sebep basit: Shannon entropiyi tanımladı, cümle uzunluklarına
uygulamadı. Birinci yazım okuyucuya, kaynakta aranınca bulunacak bir ölçü
olduğunu ima ediyor.

### 8. Metin uzunluğuna duyarlılık

Sözcüksel zenginlik ölçülerinin çoğu uzunlukla değişir. `ttr` en uçtaki
örnektir: metin uzadıkça mutlaka düşer.

`mattr`, `mtld` ve `vocd_d` uzunluğa TTR'den daha az duyarlıdır ama
bağımsız değildir; `mtld` ve `vocd_d` Türkçede belirgin biçimde kayar
([ölçüm örneği](https://github.com/efeziya1/turkish-linguistic-features/blob/main/examples/09_uzunluk_duyarliligi.py)). Onlar da en az
100 kelime ister. Farklı uzunluktaki metinleri karşılaştırıyorsanız önce
`segment_size` ile aynı boya getirin ([nasıl](../nasil/segmentleme.md)).

### 9. Paragraf öznitelikleri girdinin biçimlendirmesine bağlı

İki `para_*` özniteliği paragraf sınırını **boş satırdan** bulur. Tek satır
sonu paragraf saymaz — aksi hâlde satır satır sarılmış bir metinde her satır
paragraf olurdu.

Sonuç: metninizde boş satır yoksa metnin tamamı tek paragraf sayılır.
`para_len_mean` bütün metnin kelime sayısına eşitlenir.
Kütüphane bunu düzeltemez — silinmiş paragraf sınırı geri getirilemez.

Bu, PDF ve EPUB'dan çıkarılmış metinlerde **yaygındır**: paragraflar arasındaki
boş satırlar çıkarım sırasında kaybolur. Değer `nan` olmadığı için bunu
sayılardan fark etmezsiniz; uyarı aşağıda.

1000 kelimeyi geçen bir metinde hiç paragraf sınırı bulunamazsa
`ParagraphStructureWarning` basılır. Uyarıyı görürseniz iki yol var: kaynak
metni paragrafları boş satırla ayrılmış hâlde yeniden çıkarın, ya da
`groups` ile `paragraph` grubunu dışarıda bırakın.

### 10. Hece sayımında okunuşla sayılanlar ve atlananlar

Okunabilirlik formülleri ve hece öznitelikleri, Çetinkaya-Uzun (2010) sayım
protokolündeki gibi sayıları, kısaltmaları ve sembolleri **okunuşlarıyla**
sayar: `1918` → bin dokuz yüz on sekiz (7 hece), `cm` → santimetre, `%50` →
yüzde elli, `3. kat` → üçüncü kat, `10:30` → on otuz, `3kg` → üç kilogram,
`TBMM` → te-be-me-me.

Sayıdan sonraki nokta, ardından kelime ya da virgül geliyorsa sıra sayısıdır
(`3. kat`); gelmiyorsa cümle sonudur (`Sonuç 3.` → üç).

Okunuşu metinden belirlenemeyen biçimler tahmin edilmez, hece sayımından
**atlanır**: tek başına birim harfi (`m` metre de olabilir dakika da),
okunuşu bağlama göre değişen semboller (`/`, `#`, `*`), listede olmayan ünsüz
küçük harfli kısaltmalar. Bu yüzden sembol ve kısaltma yoğun bir metinde hece
sayısı, protokole göre elle yapılan sayımdan biraz düşük çıkar.
