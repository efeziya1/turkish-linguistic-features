# Sınırlılıklar

Bu sayfa iki kısımdan oluşur. İlki aracın nerede zayıf olduğunu anlatır;
ikincisi aracın zayıflığı olmayan ama sonuçlar yorumlanırken bilinmesi
gereken noktaları.

## Aracın sınırlılıkları

### Tümce eşikleri yalnız gazete köşe yazılarından ölçüldü

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

MTLD'nin 0,72 eşiği (McCarthy ve Jarvis 2010, s.385), HD-D'nin 42 sözcüklük örneklemi
(s.383) ve Brunet ölçüsünün 0,172 değeri (Brunet 1978, s.49) İngilizce ya da Fransızca
metinlerle belirlendi ve Türkçe metinlerle sınanmadı. Türkçeye aktarılamayacakları
söylenemez, ama aktarılabildikleri de gösterilmedi. Bir sabitin bir derlemde denenmesi
için: [Eşikleri değiştir](../nasil/parametreler.md).

### On üç künye ikincil kaynaktan

**13** künye (Türkçede 12) `as cited in` ile işaretlidir: Birincil kaynağa (İng. *primary
source*) ulaşılamadı, formül aktaran kaynaktan alındı. Örnek:

```text
Herdan (1960/1964), as cited in Tweedie & Baayen (1998) p.327, eq. (5)
```

Etkilenen ölçüler arasında `herdan_c`, `herdan_vm`, `honore_r`, `maas_a2`,
`dugast_u`, `simpson_d`, `heaps_beta`, `lix`, `cttr`, `summer_s` var. Formüller aktaran
kaynakla karşılaştırıldı, ama **birincil kaynağın kendisiyle** karşılaştırılamadı.

### Dil modelinin doğruluğu

Sözcük türü etiketleri, biçimbilimsel etiketler ve bağımlılık öznitelikleri iki dilde de
spaCy modelinden gelir; Türkçe sözlükbirimler ve özel adlar Akana'dan (aşağıda). Model
değişirse bu sayılar değişir.

Altinok'un (2023, s.13747) bildirdiğine göre spaCy'nin Türkçe modeli (`tr_core_news_md`)
sözcüklerin %90'ının türünü doğru bulur. Bağımlılık çözümlemesinde bu oran %63'tür; burada bir
sözcüğün hangi sözcüğe bağlandığı ve bağın türü birlikte doğru olmalıdır. Model resmî yazılı
metinlerle eğitildiği için başka türden metinlerde doğruluk farklı olabilir. Bağımlılık
ölçüleri (`syntactic`) özellikle dikkatle yorumlanmalıdır.

Sözcük ve tümce aracın kendi kuralıyla sayılır
([Kavramlar](kavramlar.md#sozcuk-ve-tumce)). Hangi özniteliğin hangi sözcüğü kullandığını
`describe_feature(key)["definitions"]["word"]` söyler.

Sınanan sürümler: spaCy 3.8.16, `en_core_web_sm` 3.8.0,
`tr_core_news_md` 1.0 (model sürümü 3.4.2), Akana 0.12.0.

### Bölünen sözcükler

spaCy bir sözcüğü birden çok türceye (İng. *token*) ayırdığında araç sözcüğün türünü ve
biçimbilimsel etiketlerini ilk türceden alır. Sözgelimi `sosyo-ekonomik` sıfat olduğu halde
ad sayılır. Bu yalnız bu etiketleri kullanan öznitelikleri etkiler; sözcük, seslem ve tümce
sayımlarına ve okunabilirlik formüllerine dokunmaz. Köşe yazılarında sözcüklerin Türkçede
%0,65'i, İngilizcede %2,70'i birden çok türceye bölünür.

### Türkçe biçimbilim Akana'ya bağlı

`morphological_akana` grubundaki 23 öznitelik, Türkçe sözlükbirimler ve özel adlar Akana'dan
gelir. Bir sözcüğün birden çok çözümlemesi varsa Akana tümceye bakarak birini seçer; seçim bazen
yanlıştır: *Bakan dün geldi* tümcesinde `bakan` fiilimsi (bak-an) sayılır. Özel adları bulan ad
tanıyıcı da aynı zamanda sözcük olan bazı adları kaçırır: *Kitabı Sevgi bana verdi* tümcesinde
`Sevgi` ad (`NOUN`) sayılır.

### Özniteliklerin çoğu için yayımlanmış örnek yok

**136 aday özniteliğin 22'si** yayımlanmış bir örnekle karşılaştırıldı ve hepsi örtüştü (✅). **114'ü** için
kaynaklarda yayımlanmış bir örnek bulunamadı (🔍 açık): Kaynakların çoğu formülü yayımlar,
ama formülü bir metne uyguladığı bir örnek vermez. Ayrıntı:
[doğrulama sistemi](dogrulama.md).

### Erken geliştirme aşaması (0.x)

1.0'a kadar anahtar adları ve Python'dan çağrılan adlar değişebilir; değişiklikler sürüm
notlarında duyurulur.

## Kullanırken bilmeniz gerekenler

Bunlar aracın eksiği değildir: ölçülerin kendi davranışı, girdi
gereksinimi ya da künye kuralıdır. Yine de sonuçları etkiler.

### Araca özgü öznitelikler

Bazı öznitelikler alanyazın ölçüsü değil, bu aracın tanımlarıdır. Künyeleri bunu açıkça
yazar:

- `punct_entropy`, `sent_len_entropy`: Shannon formülünün noktalama ve
  tümce uzunluğu dağılımına uygulanması. Formül Shannon'ındır, nereye uygulanacağı
  aracın kararıdır.
- `polysyllabic_word_ratio`: SMOG'un girdisinin oran biçimidir. McLaughlin'in
  kendi ölçüsü değildir.

Bunları kullanmakta sakınca yok; formülün kaynağı verilmeli, ama ölçü o
kaynağın ölçüsü gibi gösterilmemelidir.

### Paragraf öznitelikleri girdinin biçimlendirmesine bağlı

`paragraph` grubunun üç özniteliği paragraf sınırını boş satırdan bulur; tek
satır sonu paragraf saymaz. Metinde boş satır yoksa metnin tamamı tek paragraf
sayılır; bu, PDF ve EPUB'dan çıkarılan metinlerde sık olur. 1000 sözcüğü geçen
bir metinde hiç paragraf sınırı yoksa `ParagraphStructureWarning` uyarısı verilir.

### Seslem sayımında okunuşla sayılanlar ve atlananlar

Okunabilirlik formülleri ve seslem (İng. *syllable*) öznitelikleri, Çetinkaya'nın (2010,
s.93) seslemleri okunduğu biçimiyle sayma ilkesini izler; sayıları, kısaltmaları ve
simgeleri **okunuşlarıyla** sayar: `1918` → bin dokuz yüz on sekiz (7 seslem), `cm` →
santimetre, `%50` → yüzde elli, `3. kat` → üçüncü kat, `10:30` → on otuz, `3kg` → üç
kilogram, `TBMM` → te-be-me-me.

Sayıdan sonraki nokta, ardından sözcük ya da virgül geliyorsa sıra sayısıdır
(`3. kat`); gelmiyorsa tümce sonudur (`Sonuç 3.` → üç).

Sayının içindeki nokta: Noktadan önce 0–24 arası bir saat, sonra 00–59 arası iki basamak varsa
saat okunur (`8.15` → sekiz on beş, `12.30` → on iki otuz); yoksa ondalıktır ve "nokta" diye
okunur (`1.5` → bir nokta beş, `1.60`, `25.30` → yirmi beş nokta otuz). Tek başına `0` saat
sayılmaz (`0.25` → sıfır nokta yirmi beş; gece yarısı `00.25` diye yazılır). Noktadan sonra
üç basamak varsa binliktir (`2.850` → iki bin sekiz yüz elli). Saate benzeyen ondalıklar
(`4.50` lira) saat okunur ve iki seslem eksik sayılır.

Başka örnekler:

| Biçim | Okunuşu | Seslem |
|---|---|---:|
| `ve/veya`, `4+4+4` (simgeyle birleşik) | ve veya · dört artı dört artı dört | 3 · 7 |
| `1/2` (kesir) | bir bölü iki | 5 |
| `12/05/2020`, `13.3.2008` (tarih) | on iki sıfır beş iki bin yirmi · on üç üç iki bin sekiz | 11 · 8 |
| `4x4` (sayılar arasında `x`) | dört çarpı dört | 4 |
| `F1`, `A2'den` (harf + rakam) | fe bir · a iki den | 2 · 4 |
| `5N1K` | beş ne bir ke | 4 |
| `Dersim'38` (kısaltılmış yıl) | dersim otuz sekiz | 6 |
| `tv` (ünlüsüz kısaltma) | te ve | 2 |

Okunuşu metinden belirlenemeyen biçimler tahmin edilmez, seslem sayımından **atlanır**: tek
başına küçük ünsüz harf, e-posta ve web adresleri. Köşe yazılarında sözcüklerin %0,03'ü böyle
atlanır.

### Sesbilimsel ölçüler harfle hesaplanır

`phonological` grubunun ölçüleri (ünlü oranları, ünlü uyumu) sesbirimlerden
(İng. *phonemes*) değil, yazıdaki harflerden hesaplanır; ön ve art ünlüler gibi sınıflar
birer harf listesidir. IPA çevriyazısıyla (İng. *transcription*) çalışılmaz; bu, ileriki
sürümlere bırakıldı.

### Heaps β kısa metinde güvenilir değil

`heaps_beta` metin boyunca 20 eşit noktada ölçülür (Tweedie ve Baayen 1998, s.333); her
metin aynı sayıda noktayla ölçülür. Değer en az 20 sözcüklük her metinde hesaplanır, daha
kısa metinde `nan` döner. Yasa büyük derlemlerde iyi
uyar, kısa metinlerde güvenilir değildir (Manning vd. 2008, s.81).

### İnsan yargısı gerektiren ölçüler yaklaşık hesaplanır

Bazı ölçülerin kaynakları sayımı elle, uzman yargısıyla yapmıştır: Bir sözcüğün listede sayılıp
sayılmayacağına ya da bir tümcenin anlamca nerede bittiğine uzman karar verir. Araç bu kararları
kurallarla verdiği için sonuç uzman sayımına yakındır ama onunla aynı değildir. Bu durumdaki
öznitelikler Kalyoncu'nun (2025) formülleri ve bileşenleridir (`kalyoncu_*`).
