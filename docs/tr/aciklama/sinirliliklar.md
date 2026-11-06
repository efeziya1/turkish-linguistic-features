# Sınırlılıklar

Bu sayfa iki kısımdan oluşur. İlki aracın nerede zayıf olduğunu anlatır;
ikincisi aracın zayıflığı olmayan ama sonuçları yorumlarken bilmeniz
gereken noktaları.

## Aracın sınırlılıkları

### Tümce eşikleri yalnız gazete köşe yazılarıyla kalibre edildi

`short_sent_ratio` ve `long_sent_ratio` eşikleri (İng. *thresholds*; TR 4/17, EN 8/32)
gazete köşe yazılarında, varsayılan tümce kuralı ve varsayılan sözcükle ölçülen
tümce uzunluğu dağılımının 15. ve 85. yüzdeliğinden türetildi:

| Dil | Yazar | Tümce |
|---|---:|---:|
| Türkçe | 137 | 198.225 |
| İngilizce | 30 | 52.745 |

Köşe yazısı **tek bir tür**. Tümce uzunluğu metin türüne göre de değiştiği için roman,
teknik metin, konuşma dökümü, şiir ya da çocuk kitabında eşikler farklı çıkabilir. İki
derlem de sınırlı sayıda yazarın yazılarından oluşur; özellikle 30 yazarlık İngilizce
derlemde eşikler bu yazarların üslubundan etkilenmiş olabilir. Eşikler tümcelerin
dağılımdaki yerini gösterir; okurların bu tümceleri gerçekten kısa ya da uzun bulup
bulmadığını göstermez. Yöntem: [Eşik kalibrasyonu](../../esik-kalibrasyonu.md).

### Kaynaktan alınan sabitler Türkçede sınanmadı

MTLD'nin 0,72 eşiği, HD-D'nin 42 sözcüklük örneklemi ve Brunet ölçüsünün 0,172 değeri
kaynaklarından alındı ve Türkçe metinlerle sınanmadı. Türkçeye aktarılamayacakları
söylenemez, ama aktarılabildikleri de gösterilmedi. Ayrıntı:
[Eşikleri değiştir](../nasil/parametreler.md#kaynaktan-alnan-sabitler-turkcede-snanmad).

### On üç künye ikincil kaynaktan

**13** künye (Türkçede 12) `as cited in` ile işaretlidir: Birincil kaynağa (İng. *primary
source*) ulaşılamadı, formül aktaran kaynaktan alındı. Örnek:

```text
Herdan (1960/1964), as cited in Tweedie & Baayen (1998) p.327, eq. (5)
```

Etkilenen ölçüler arasında `herdan_c`, `herdan_vm`, `honore_r`, `maas_a2`,
`dugast_u`, `simpson_d`, `heaps_beta`, `lix`, `cttr`, `summer_s` var. Formüller doğrulandı
ama **birincil kaynağın kendi ifadesiyle** karşılaştırılmadı.

### Dil modelinin doğruluğu

Sözcük türü etiketleri, biçimbilimsel etiketler, İngilizce sözlükbirimler ve bağımlılık
öznitelikleri spaCy modelinden gelir. Model değişirse bu sayılar değişir. Türkçe
sözlükbirimler Zeyrek'ten gelir (aşağıda).

Türkçe modeli geliştiren Altinok (2023, s.13747), kendi sınama verisinde modelin sözcük
türünü %90 oranında doğru bulduğunu, bağımlılıkta ise bu oranın bağın türüyle birlikte
%63'e düştüğünü bildirir. Model resmî yazılı dil kaynaklarıyla eğitilmiştir; başka türden
metinlerde doğruluk farklı olabilir. Bu bilgilere dayanan öznitelikleri, özellikle
doğruluğun en düşük olduğu bağımlılık ölçülerini (`syntactic`), dikkatle yorumlayın.

Sözcük ve tümce aracın kendi kuralıyla sayılır
([Kavramlar](kavramlar.md#sozcuk-ve-tumce)). Hangi özniteliğin hangi sözcüğü kullandığını
`describe_feature(key)["definitions"]["word"]` söyler.

Sınanan sürümler: spaCy 3.8.16, `en_core_web_sm` 3.8.0,
`tr_core_news_md` 1.0 (model sürümü 3.4.2), Zeyrek 0.1.3.

### Bölünen sözcükler

spaCy bir sözcüğü birden çok türceye (İng. *token*) ayırdığında araç sözcüğün türünü ve
biçimbilimsel etiketlerini ilk türceden alır. Sözgelimi `sosyo-ekonomik` sıfat olduğu halde
ad sayılır. Bu yalnız bu etiketleri kullanan öznitelikleri etkiler; sözcük, seslem ve tümce
sayımlarına ve okunabilirlik formüllerine dokunmaz. Köşe yazılarında sözcüklerin Türkçede
%0,65'i, İngilizcede %2,70'i birden çok türceye bölünür.

### Türkçe biçimbilim Zeyrek'e bağlı

`morphological_zeyrek` grubundaki 23 öznitelik ve Türkçe sözlükbirimler Zeyrek'ten gelir.
Zeyrek bir sözcük için birden çok çözümleme döndürebilir; araç bağlama bakmadan ilkini alır
(Kalyoncu formüllerinde spaCy'nin sözcük türüne uyanı). Aynı sayıları yeniden almak için
Python'u `PYTHONHASHSEED=0` ile başlatın.

### Adayların üçte ikisi hâlâ doğrulanmadı

**172 doğrulama adayının 61'i** doğrulanmış (61 ✅), **111'i 🔍 açık**: kaynakların
çoğu formülü yayımlar, o formülün uygulandığı bir sayısal örnek vermez. Ayrıntı:
[doğrulama sistemi](dogrulama.md).

### Erken geliştirme aşaması (0.x)

1.0'a kadar anahtar adları ve Python'dan çağrılan adlar değişebilir; değişiklikler sürüm
notlarında duyurulur.

## Kullanırken bilmeniz gerekenler

Bunlar aracın eksiği değil: ölçülerin kendi davranışı, girdi
gereksinimi ya da künye kuralı. Yine de sonuçları etkiler.

### Araca özgü öznitelikler

Bazı öznitelikler alanyazın ölçüsü değil, bu aracın tanımlarıdır. Künyeleri bunu açıkça
yazar:

- `punct_entropy`, `sent_len_entropy`: Shannon formülünün noktalama ve
  tümce uzunluğu dağılımına uygulanması. Formül Shannon'ın, uygulama kararı
  bizim.
- `polysyllabic_word_ratio`: SMOG'un girdisinin oran biçimi. McLaughlin'in
  kendi ölçüsü değil.

Bunları kullanmakta sakınca yok; formülün kaynağını verin, ama ölçüyü o
kaynağın ölçüsü gibi göstermeyin.

### Paragraf öznitelikleri girdinin biçimlendirmesine bağlı

`paragraph` grubunun üç özniteliği paragraf sınırını boş satırdan bulur; tek
satır sonu paragraf saymaz. Metinde boş satır yoksa metnin tamamı tek paragraf
sayılır; bu, PDF ve EPUB'dan çıkarılan metinlerde sık olur. 1000 sözcüğü geçen
bir metinde hiç paragraf sınırı yoksa `ParagraphStructureWarning` basılır.

### Seslem sayımında okunuşla sayılanlar ve atlananlar

Okunabilirlik formülleri ve seslem (İng. *syllable*) öznitelikleri, Çetinkaya'nın (2010,
s.93) seslemleri okunduğu biçimiyle sayma ilkesini izler; sayıları, kısaltmaları ve
simgeleri **okunuşlarıyla** sayar: `1918` → bin dokuz yüz on sekiz (7 seslem), `cm` →
santimetre, `%50` → yüzde elli, `3. kat` → üçüncü kat, `10:30` → on otuz, `3kg` → üç
kilogram, `TBMM` → te-be-me-me.

Sayıdan sonraki nokta, ardından sözcük ya da virgül geliyorsa sıra sayısıdır
(`3. kat`); gelmiyorsa tümce sonudur (`Sonuç 3.` → üç).

Okunuşu metinden belirlenemeyen biçimler tahmin edilmez, seslem sayımından
**atlanır**: tek başına birim harfi (`m` metre de olabilir dakika da),
okunuşu bağlama göre değişen simgeler (`/`, `#`, `*`), listede olmayan, ünlü
içermeyen küçük harfli kısaltmalar. Bu yüzden simge ve kısaltma yoğun bir metinde seslem
sayısı, elle yapılan sayımdan biraz düşük çıkar.

### Sesbilimsel ölçüler harfle hesaplanır

`phonological` grubunun ölçüleri (ünlü oranları, ünlü uyumu) sesbirimlerden
(İng. *phonemes*) değil, yazıdaki harflerden hesaplanır; ön ve art ünlüler gibi sınıflar
birer harf listesidir. IPA çevriyazısıyla (İng. *transcription*) çalışılmaz; bu, ileriki
sürümlere bırakıldı.

### Heaps β kısa metinde güvenilir değil

`heaps_beta` metin boyunca 20 eşit noktada ölçülür (Tweedie ve Baayen 1998, s.333); her
metin aynı sayıda noktayla ölçülür. En az uzunluk sınırı yoktur, değer en az 20 sözcüklük
her metinde hesaplanır; 20 sözcükten kısa metinde `nan` döner. Yasa büyük derlemlerde iyi
uyar, kısa metinlerde güvenilir değildir (Manning vd. 2008, s.81).

### Kalyoncu formülleri elle sayımın yaklaşığı

`kalyoncu_*` anahtarları Kalyoncu'nun (2025) elle yaptığı sayımı Zeyrek ve spaCy ile yaklaşık
olarak yeniden üretir. Kalyoncu'nun dokuz kuralından dördü (yaygın türetme ekli türevler,
yansıma, pekiştirme, uzak anlam) ve anlama dayalı tümce tanımı uygulanmaz. KL uzman yargısına
dayanır (3., 5., 8. kurallar), bu yüzden uzman değerleriyle tam örtüşmesi beklenmez. Yazıyla
yazılan sayılar liste içidir; büyük harfle başlayan (tümce başında olmayan) sözcük özel ad
sayılır; gövde ve fiilimsi sayımı spaCy türüne uyan Zeyrek çözümlemesinden yapılır (bu üç kural
yalnız `kalyoncu_*` anahtarlarında). Zeyrek'in tanımadığı fiilimsi ekleri ve seçilen
çözümlemedeki hatalar sonucu değiştirir. Ayrıntı:
[Kalyoncu formülleri](kalyoncu.md).
