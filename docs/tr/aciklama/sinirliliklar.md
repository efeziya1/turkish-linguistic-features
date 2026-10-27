# Sınırlılıklar

Bu sayfa iki kısımdan oluşur. İlki kütüphanenin nerede zayıf olduğunu anlatır;
ikincisi kütüphanenin zayıflığı olmayan ama sonuçları yorumlarken bilmeniz
gereken noktaları.

## Kütüphanenin sınırlılıkları

### 1. Tümce eşikleri yalnız gazete köşe yazılarıyla kalibre edildi

`short_sent_ratio` ve `long_sent_ratio` eşikleri (TR 4/17, EN 8/32) gazete
köşe yazılarında, varsayılan tümce kuralı ve varsayılan sözcükle ölçülen
tümce uzunluğu dağılımının 15. ve 85. yüzdeliğinden türetildi:

| Dil | Tümce |
|---|---|
| Türkçe | 197 990 |
| İngilizce | 52 745 |

Köşe yazısı **tek bir tür**. Roman, teknik metin, transkript, şiir ya da
çocuk kitabı için genelleneceği **garanti değil.** Yöntem:
[Eşik kalibrasyonu](../../esik-kalibrasyonu.md).

### 2. On beş künye ikincil kaynaktan

**15** künye `as cited in` ile işaretlidir — birincil kaynağa ulaşılamadı, formül aktaran kaynaktan alındı. Örnek:

```text
Herdan (1960/1964), as cited in Tweedie & Baayen (1998) p.327, eq. (5)
```

Etkilenen ölçüler arasında `herdan_c`, `herdan_vm`, `honore_r`, `maas_a2`, `brunet_w`,
`dugast_u`, `simpson_d`, `heaps_beta`, `lix`, `cttr`, `summer_s` var. Formüller doğrulandı ama **birincil
kaynağın kendi ifadesiyle** karşılaştırılmadı.

### 3. spaCy modeli sonuçların parçası

POS etiketleri, biçimbilimsel etiketler, İngilizce sözlükbirimler ve bağımlılık
öznitelikleri (ayrıştırıcının kendi tümceleriyle) modelden gelir. Model
değişirse bu sayılar değişir. Türkçe sözlükbirimler Zeyrek'ten gelir (§4).

Sözcük ve tümce kütüphanenin kendi kuralıyla sayılır
([Kavramlar](kavramlar.md#sozcuk-ve-tumce)). Hangi özniteliğin hangi sözcüğü kullandığını
`describe_feature(key)["definitions"]["word"]` söyler.

Sınanan sürümler: spaCy 3.8.16, `en_core_web_sm` 3.8.0,
`tr_core_news_md` 1.0.

### 4. Türkçe morfoloji Zeyrek'e bağlı

`morphological_zeyrek` grubundaki 23 öznitelik ve Türkçe sözlükbirimler Zeyrek'ten
gelir. Zeyrek bir sözcük için birden çok çözümleme döndürebilir; kütüphane bağlama
bakmadan ilkini alır. Hangisinin ilk geldiği Python'un her çalıştırılışında az da
olsa değişebilir; tekrar üretilebilir sayılar için Python'u `PYTHONHASHSEED=0` ile
başlatın.

### 5. Adayların üçte ikisi hâlâ doğrulanmadı

**163 doğrulama adayının 51'i** doğrulanmış (51 ✅), **112'si 🔍 açık**: kaynakların
çoğu formülü yayımlar, o formülün uygulandığı bir sayısal örnek vermez. Ayrıntı:
[doğrulama sistemi](dogrulama.md).

### 6. Erken geliştirme aşaması (0.x)

1.0'a kadar anahtar adları ve genel API değişebilir; değişiklikler sürüm notlarında duyurulur.

## Kullanırken bilmeniz gerekenler

Bunlar kütüphanenin eksiği değil: ölçülerin kendi davranışı, girdi
gereksinimi ya da künye kuralı. Yine de sonuçları etkiler.

### 7. Araca özgü öznitelikler

Bazı öznitelikler alanyazın ölçüsü değil, bu kütüphanenin
tanımlarıdır. Künyeleri bunu açıkça yazar:

- `punct_entropy`, `sent_len_entropy` — Shannon formülünün noktalama ve
  tümce uzunluğu dağılımına uygulanması. Formül Shannon'ın, uygulama kararı
  bizim.
- `polysyllabic_word_ratio` — SMOG'un girdisinin oran biçimi. McLaughlin'in
  kendi ölçüsü değil.

Bunları kullanmakta sakınca yok; formülün kaynağını verin, ama ölçüyü o
kaynağın ölçüsü gibi göstermeyin.

### 8. Paragraf öznitelikleri girdinin biçimlendirmesine bağlı

`paragraph` grubunun üç özniteliği paragraf sınırını boş satırdan bulur; tek
satır sonu paragraf saymaz. Metinde boş satır yoksa metnin tamamı tek paragraf
sayılır; bu, PDF ve EPUB'dan çıkarılan metinlerde sık olur. 1000 sözcüğü geçen
bir metinde hiç paragraf sınırı yoksa `ParagraphStructureWarning` basılır.

### 9. Seslem sayımında okunuşla sayılanlar ve atlananlar

Okunabilirlik formülleri ve seslem öznitelikleri, Çetinkaya-Uzun (2010) sayım
protokolündeki gibi sayıları, kısaltmaları ve sembolleri **okunuşlarıyla**
sayar: `1918` → bin dokuz yüz on sekiz (7 seslem), `cm` → santimetre, `%50` →
yüzde elli, `3. kat` → üçüncü kat, `10:30` → on otuz, `3kg` → üç kilogram,
`TBMM` → te-be-me-me.

Sayıdan sonraki nokta, ardından sözcük ya da virgül geliyorsa sıra sayısıdır
(`3. kat`); gelmiyorsa tümce sonudur (`Sonuç 3.` → üç).

Okunuşu metinden belirlenemeyen biçimler tahmin edilmez, seslem sayımından
**atlanır**: tek başına birim harfi (`m` metre de olabilir dakika da),
okunuşu bağlama göre değişen semboller (`/`, `#`, `*`), listede olmayan, ünlü
içermeyen küçük harfli kısaltmalar. Bu yüzden sembol ve kısaltma yoğun bir metinde seslem
sayısı, protokole göre elle yapılan sayımdan biraz düşük çıkar.

`phonological` grubunun ölçüleri yazıdaki harflerle ve harf listeleriyle (ünlüler, ön ve
art ünlüler) hesaplanır; sesbirimlerle (IPA çevriyazısı) çalışılmaz.

### 10. Heaps β kısa metinde güvenilir değil

`heaps_beta` metin boyunca 20 eşit noktada ölçülür (Tweedie ve Baayen 1998, s.333); her
metin aynı sayıda noktayla ölçülür. En az uzunluk sınırı yoktur, değer en az 20 sözcüklük
her metinde hesaplanır; 20 sözcükten kısa metinde `nan` döner. Yasa büyük derlemlerde iyi
uyar, kısa metinlerde güvenilir değildir (Manning vd. 2008, s.81).

### 11. Kalyoncu formülleri elle sayımın yaklaşığı

`kalyoncu_*` anahtarları Kalyoncu'nun (2025) elle yaptığı sayımı Zeyrek ve spaCy ile yaklaşık
olarak yeniden üretir. Kalyoncu'nun dokuz kuralından dördü (yaygın türetme ekli türevler,
yansıma, pekiştirme, uzak anlam) ve anlama dayalı tümce tanımı uygulanmaz. Zeyrek'in tanımadığı
fiilimsi ekleri ve ilk çözümlemedeki hatalar sonucu değiştirir. Ayrıntı:
[Kalyoncu formülleri](kalyoncu.md).
