# Doğrulama sistemi

## Sorun

Bir kütüphane "Ateşman okunabilirlik formülünü uyguluyorum" diyebilir. Siz
bunu nasıl kontrol edersiniz? Kaynağı bulup formülü okuyup kodu
inceleyerek — yani kütüphaneyi kullanmamanız gereken kadar uğraşarak.

Bu kütüphane farklı bir şey yapar: **kaynağın yayımladığı sayıyı** alır,
aynı girdiyi kendi koduna verir, ikisini yan yana basar.

Sonuç: [doğrulama raporu](../../dogrulama-raporu.md)
([English](../../verification-report.md)).

## İki ayrı şeyi karıştırmayın

Bu sayfanın geri kalanı bir şey anlatıyor: raporda kaç satırın kaynağın
*yayımladığı sayısıyla* karşılaştırıldığı. O başka bir katman. Altındaki
katmanı da açıkça yazmak gerekiyor, çünkü rapordaki "açık" sayısı kolayca
yanlış okunuyor.

| Katman | Ne garanti eder | Kapsam |
|---|---|---|
| **Formül eşdeğerliği** | Kod, kaynaktaki denklemi uyguluyor. Künye sayfa ve denklem numarası verir; testler formülü ve sınır durumlarını sınar. | Künyesi olan 140 öznitelik (Türkçe; 68'i saf tanım, kaynağı yok) |
| **Kaynak sayısı doğrulaması** | Kaynağın *yayımladığı bir sayı* bulundu ve bizim çıktımızla karşılaştırıldı. | 91 aday rapor satırının 48'i (Türkçe) |

İkinci katman ek bir çalışmadır, birincinin koşulu değil. Bir öznitelik "🔍
açık" diye işaretliyse **formülü şüpheli değildir**; karşılaştırılacak
yayımlanmış bir sayı bulunamamıştır. Yule (1944) K'yı tanımlar, bir romanda
K'nın kaç çıktığını basmaz — basmadığı için bizim K'mız yanlış olmuyor.

Her özniteliğin formülü yazılıdır. Künyesi olmayan 68 öznitelik saf tanımdır
(bir harfin ya da noktalama işaretinin payı gibi); bir kaynağa dayanmadıkları
için kaynakla eşlenecek bir denklemleri de yoktur.

## Önce: her öznitelik doğrulanamaz

Bu ayrım raporun en önemli parçası. 212 özniteliğin bir kısmı, tanımı gereği
**doğrulama adayı bile değildir**:

| | Neden aday değil |
|---|---|
| ⚪ **kaynak yok** | Saf tanım. `punc_,_ratio` "virgül / kelime" demektir; aranacak bir literatür sayısı yoktur. Harf sıklık vektörü tek başına 29 anahtar (Türkçe). |
| ⚫ **etiket şeması** | Bir ölçü değil, dış bir şemanın kategorisini sayıyor. `pos_noun` → UD, `case_loc_ratio` → Zeyrek. **Şema kategori tanımlar, ölçüm yayımlamaz** — de Marneffe'in makalesi "morph_case_loc = 0,07" diye bir sayı basmaz, basamaz. |
| 🔧 **türev** | Formül bir kaynaktan, **uygulaması bizden**. `entropy_std` Shannon'ın entropisidir ama parçalar arası standart sapması bizim; `long_sent_ratio`'nun eşiği kendi kalibrasyonumuzdan gelir. Bu ölçüleri kimse yayımlamadı — kendi kalibrasyonumuza karşı sınamak kendi cevabımıza bakmak olurdu. |

Türkçe tarafında **142 satır** bu üçünden biri. Geriye **91 doğrulama
adayı** kalıyor. Gerçek payda budur.

## Aday satırların dört durumu

| | Anlamı |
|---|---|
| ✅ **birebir** | Kaynağın yayımladığı sayıyla tolerans içinde aynı. Küçük bir farkın nedeni biliniyorsa satırın altında not olarak yazılır. |
| 🟡 **belgelenmiş sapma** | Fark **toleransın dışında** ve **nedeni yazılı** — kaynağın ara değeri yuvarlaması, kaynağın sayılarının elle üretilmiş olması gibi. |
| 🔍 **açık** | Kaynak formülü veriyor ama uygulanmış bir örnek vermiyor. Doğrulanabilir, henüz doğrulanmadı. |
| ❌ **uyuşmazlık** | **Açıklanmamış** fark. **Yayın kapısı: bir tane bile varsa sürüm çıkmaz.** |

Bugünkü durum: **91 adayın 48'i bitmiş** (46 ✅ + 2 🟡), 43'ü 🔍 açık.

Tolerans yayımlanan değerin **%1'i** (göreli). Kaynaklar ara değerleri
yuvarlayarak bastığı için mutlak eşitlik beklenmez. Göreli tolerans her ölçekte
aynı şeyi söyler: eskiden sabit 0,05 fark, 0–1 arası oranlarda (`ttr`) çok
gevşek, yüzlerle ölçülen değerlerde (`curve_length` ≈ 134) çok sıkıydı.

**Toleransı aşan fark otomatik olarak ❌ değildir.** Belirleyici olan farkın
büyüklüğü değil, **nedeninin bilinip bilinmediğidir**. Nedeni ölçülmüş ve
yazılmışsa satır 🟡 olur; yazılmamışsa ❌ olur ve sürüm çıkmaz.

Bu bir kaçış kapısı değil. Gerekçe "herhalde yuvarlamadır" cinsinden bir
tahmin olamaz; farkın nereden geldiğini gösteren bir ölçüm olmak zorundadır.
Aşağıdaki Kincaid örneği bunun nasıl göründüğünü anlatıyor.

## İki kanıt türü

Bu ayrım önemli ve raporda ayrı sütunda durur.

**Uçtan uca**, kaynağın **kendi metnini** boru hattından geçirir. Yani
tokenizasyon, heceleme ve cümle bölme de sınanır. En güçlü kanıttır: bir
sayı tutuyorsa yalnız formül değil, ona giden bütün adımlar doğrudur.

**Formül**, fonksiyona girdileri doğrudan verir — örneğin "hece/sözcük 2,2
ve sözcük/cümle 4". Formülü ve katsayıları doğrular, boru hattını
doğrulamaz. Kaynak bir metin yayımlamamışsa elde olan budur.

## Neden 43 satır hâlâ 🔍 açık

Kaynak formülü yayımlamış ama o formülü bir metne uygulayıp sonucu basmamış.
Bu, nicel dilbilim literatüründe **olağandır**. Yule (1944) K'yı tanımlar,
bir romanda K'nın kaç çıktığını basmaz. Böyle bir sayı olmayınca
karşılaştıracak bir şey de olmaz.

**Bu satırlar test edilmiyor demek değildir.** Formül ve sınır durumları
kendi test dosyalarında sınanır. Rapor yalnız *kaynağın sayısıyla*
karşılaştırmayı takip eder.

Hangi grupların doğrulandığı türle ilgili, tesadüf değil:

| Grup | ✅ | 🟡 | 🔍 |
|---|---|---|---|
| `frequency_structure` | 22 | 0 | 2 |
| `readability` | 13 | 1 | 2 |
| `lexical` | 6 | 1 | 22 |
| `phonetic` | 0 | 0 | 11 |

Okunabilirlik formülleri **pratik araçlardır** — yazarları formülü örnek
metinle birlikte yayımlar, çünkü amaç başkasının uygulayabilmesidir.
Sözcüksel zenginlik ölçüleri ise matematiksel tanımlardır; yazarı formülü
verir, örneği okuyucuya bırakır.

## 🔍 nasıl ✅ olur

Kaynağın yayımladığı bir sayı bulunması gerekir. Üç örnek:

**QUITA kılavuzu — tek seferde on dört öznitelik.** Kılavuz on dört göstergeyi iki
örnek metin üzerinde baştan sona hesaplayıp sonucu basıyor, üstelik o
metinlerin **sıklık dağılımını da yayımlıyor** (§15.3). Dağılım bu
göstergelerin tek girdisi olduğu için karşılaştırma doğrudan yapılabiliyor:

| | QUITA | bizim |
|---|---|---|
| `repeat_rate` Text 2 | 0,02147 | 0,02147 |
| `gini_coef` Text 1 | 0,3045 | 0,30449 |
| `curve_length` Text 2 | 134,2787 | 134,27870 |
| `entropy` Text 1 | 6,438043 | 6,438043 |

Yirmi sekiz karşılaştırmanın yirmi yedisi tolerans içinde (en büyük göreli
fark %0,1'in altında; çoğunda sapma sıfır). Kalan bir tanesinde sapma 0,009,
yani yayımlanan değerin %1,5'i; %1 toleransın dışında kaldığı için satır 🟡 ve
nedeni belli: `ttr` Text 2 için kaynak 0,590 basmış, ama kendi verdiği sayıları
bölünce 121 ÷ 202 = **0,599** çıkıyor. Yayımlanmış sayıda basım hatası var;
bizim değerimiz aritmetik olarak doğru olan.

Depoda duran şey iki sıklık dağılımı: 119 ve 121 tam sayı. Metinlerin kendisi
telifli (Orwell) ve depoya girmiyor; sayılardan metin geri kurulamaz.

**`mtld`** — Bu ölçü metni tarayıp TTR 0,72'nin altına her düştüğünde bir
"faktör" sayar; artan kısım kesirli bir faktör olarak eklenir. McCarthy &
Jarvis (2010) s.385 tam da o kesri örnekliyor: *".887 forms 40,4% of the range
between 1.00 and the full factor of .720."* Aynı diziyi üretim kodundan
geçirdik, kesirli faktör **0,4043** çıktı — kaynağın bastığı %40,4 ile aynı.

**`coleman_liau`** — Makale ölçüyü iki adımda tanımlıyor: önce metnin cloze
yüzdesi kestiriliyor, sonra o yüzde sınıf düzeyine çevriliyor. Uygulamada bu
iki adım tek denklemde birleştirilir; literatürde standart olan kullanım da
budur. İki adımı ayrı ayrı yürütmekle tek denklemi kullanmanın aynı sonucu
verdiğini ölçtük: **7,7041** ve **7,7046**. Aradaki 0,0005 kaynağın ara değeri
yuvarlamasından geliyor.

## 🟡 nasıl görünür — Kincaid örneği

İngilizce raporda iki okunabilirlik özniteliği, `ari` ve
`flesch_kincaid_grade`, 🟡 durumunda. `ari` Türkçe şemada da var ve aynı
karşılaştırmayla orada da 🟡; `flesch_kincaid_grade` yalnız İngilizcede var.
Üç soruyla anlatılabilir.

**Ne karşılaştırıldı?** Bu iki ölçünün kaynağı 1975 tarihli bir ABD Donanması
teknik raporu. Rapor yalnız formülü vermiyor: ekinde eğitim malzemesinden
alınmış **18 gerçek metin parçası**, tablolarında da o 18 parça için kendi
hesapladığı ARI ve FKGL değerleri var. Yani kaynak hem girdiyi hem cevabı
basmış — doğrulama için elde olabilecek en iyi malzeme. 18 parçanın hepsini
boru hattımızdan geçirdik.

**Sapma ne kadar?** Pasaj başına mutlak farkların ortalaması **0,54 ARI
puanı**. Raporda görünen −0,485 başka bir sayıdır: kaynağın Tablo 1'de
bastığı ortalama (12,3) ile bizim 18 pasajlık ortalamamız arasındaki fark.
Yayımlanan değere oranı yaklaşık %3,9 (0,485 ÷ 12,3); %1 toleransın çok üstünde, yani ✅ olamıyor.

**Neden ❌ değil?** Çünkü sapmanın nereden geldiğini tahmin etmedik, ölçtük.
Her iki formülün girdisi "kelime başına vuruş" (harf ve rakam sayısı), ve
1975'te bu sayım elle yapılıyordu: daktiloya takılı mekanik bir sayaçla. Farkın
oradan gelip gelmediğini şöyle sınadık: kaynağın bastığı sayıyı verecek vuruş
miktarı bizimkinin kaç katı olmalıydı? 18 parçanın 17'sinde cevap
**0,996–1,041 katı** — yani parça başına birkaç karakter. Elle sayımda beklenen
büyüklük bu.

İki alternatif açıklama da sınandı ve elendi: boşlukları vuruşa katmak sapmayı
0,54'ten 4,24'e çıkarıyor (yani bizim boşluksuz sayımımız doğru), metin
başlıklarını saymak ise 18 parçanın hepsinde sonucu kötüleştiriyor (yani kaynak
başlıkları saymamış). Bir parça da kendi içinde tutarsız: 2 numaralı parçada
kaynağın ARI'sının ima ettiği cümle uzunluğu, kendi FKGL'sini tutturmuyor.

Parça bazında bütün sayılar — vuruş ve kelime sayıları dâhil — raporun sonundaki
ek tabloda duruyor, farkın hangi girdiden geldiği görülebilsin diye.

İşte 🟡'nin anlamı bu: *fark var, ölçtük, nereden geldiğini biliyoruz.*

## Rapor testlerden üretilir

`docs/dogrulama-raporu.md` elle yazılmaz.
`scripts/generate_verification_report.py` üretir ve
`tests/test_kaynak_esligi.py` **aynı karşılaştırma tablosunu** okur. Yani
rapor ile testler ayrışamaz; rapor bayatsa test düşer.

Kapsam listesi de kayıt defterinden gelir — bir öznitelik eklenip rapora
girmemesi mümkün değil.

## Neye güvenmeli

Bir sayıyı çalışmanızda kullanmadan önce raporda satırına bakın:

- **✅** — kaynağın sayısı tutuyor, kullanın.
- **🟡** — fark var ama nedeni yazılı; nedeni okuyun, sizin kullanımınızı
  etkiliyor mu karar verin.
- **🔍 açık** — formül kaynağındaki denklemle eşlenmiş, ama kaynağın
  yayımladığı bir sayıyla karşılaştırılmamış. Künyeyi verin; "kaynağın kendi
  sayısıyla doğrulandı" demeyin.
- **⚪ kaynak yok** — bu kütüphanenin tanımı, çünkü aranacak bir literatür
  sayısı yok (`punc_,_ratio` = virgül / kelime).
- **⚫ etiket şeması** — sayının kendisi bizim, kategoriler şemanın.
  Şemayı kaynak gösterin (UD ya da Zeyrek), ölçüyü değil.
- **🔧 türev** — formül kaynağın, o formülü bu veriye uygulama kararı bizim.
- **❌** — böyle bir satır varsa sürüm çıkmamıştır; görürseniz sorun bildirin.

### ⚪ ve 🔧 için tanımı biz veriyoruz

Bu iki durumda ölçünün tanımını yöntem bölümünüz için sıfırdan yazmanız
gerekmiyor. Kayıt defteri her öznitelik için alıntılanabilir bir tanım
tutuyor:

```python
tlf.describe_feature("entropy_std")["formula"]
```

```text
'population std of entropies (bits) of disjoint mattr_window-word chunks'
```

Örnek olarak altısı:

| Öznitelik | Tanım | Kaynağa ait olan |
|---|---|---|
| `entropy_std` | ayrık `mattr_window` kelimelik parçaların entropilerinin (bit) popülasyon standart sapması | entropi formülü — Shannon (1948) |
| `punct_entropy` | on noktalama türünün dağılımının Shannon entropisi (bit) | entropi formülü — Shannon (1948) |
| `sent_len_entropy` | cümle başına kelime dağılımının Shannon entropisi (bit) | entropi formülü — Shannon (1948) |
| `short_sent_ratio` | `short_sent_threshold` kelimeden az cümle / cümle | eşik değeri — [eşik kalibrasyonu](../../esik-kalibrasyonu.md) |
| `long_sent_ratio` | `long_sent_threshold` kelimeden çok cümle / cümle | eşik değeri — [eşik kalibrasyonu](../../esik-kalibrasyonu.md) |
| `polysyllabic_word_ratio` | 3+ heceli kelime / hecelenebilir kelime | çok heceli tanımı — McLaughlin (1969) s.641 |

Tek kural künyeyi doğru kurmak: formülün kaynağını verin, ölçünün kendisini
kaynağa mal etmeyin.

- ✗ "Shannon (1948) `entropy_std` ölçüsü"
- ✓ "Shannon (1948) entropisinin parçalar arası standart sapması
  (turkish-linguistic-features'ın tanımı)"

Birinci yazım okuyucuya, kaynakta aranınca bulunacak bir ölçü olduğunu ima
ediyor. Shannon entropiyi tanımladı, parçalar arası standart sapmasını
tanımlamadı.
