# Doğrulama sistemi

## Sorun

Bir kütüphane "Ateşman okunabilirlik formülünü uyguluyorum" diyebilir. Siz
bunu nasıl kontrol edersiniz? Kaynağı bulup formülü okuyup kodu
inceleyerek — yani kütüphaneyi kullanmamanız gereken kadar uğraşarak.

Bu kütüphane farklı bir şey yapar: **kaynağın yayımladığı sayıyı** alır,
aynı girdiyi kendi koduna verir, ikisini yan yana basar.

Sonuç: [doğrulama raporu](../../dogrulama-raporu.md)
([English](../../verification-report.md)).

## Önce: her öznitelik doğrulanamaz

Bu ayrım raporun en önemli parçası. 208 özniteliğin bir kısmı, tanımı gereği
**doğrulama adayı bile değildir**:

| | Neden aday değil |
|---|---|
| ⚪ **kaynak yok** | Saf tanım. `punc_,_ratio` "virgül / kelime" demektir; aranacak bir literatür sayısı yoktur. `char_a`…`char_z` tek başına 26 anahtar. |
| ⚫ **etiket şeması** | Bir ölçü değil, dış bir şemanın kategorisini sayıyor. `pos_noun` → UD, `case_loc_ratio` → Zeyrek. **Şema kategori tanımlar, ölçüm yayımlamaz** — de Marneffe'in makalesi "morph_case_loc = 0,07" diye bir sayı basmaz, basamaz. |
| 🔧 **türev** | Formül bir kaynaktan, **uygulaması bizden**. `entropy_std` Shannon'ın entropisidir ama parçalar arası standart sapması bizim; `long_sent_ratio`'nun eşiği kendi kalibrasyonumuzdan gelir. Bu ölçüleri kimse yayımlamadı — kendi kalibrasyonumuza karşı sınamak kendi cevabımıza bakmak olurdu. |

Türkçe tarafında **141 satır** bu üçünden biri. Geriye **92 doğrulama
adayı** kalıyor. Gerçek payda budur.

## Aday satırların dört durumu

| | Anlamı |
|---|---|
| ✅ **birebir** | Kaynağın yayımladığı sayıyla tolerans içinde aynı. |
| 🟡 **belgelenmiş sapma** | Fark var ve **nedeni yazılı** — kaynağın ara değeri yuvarlaması, kaynağın sayılarının elle üretilmiş olması gibi. |
| 🔍 **açık** | Kaynak formülü veriyor ama uygulanmış bir örnek vermiyor. Doğrulanabilir, henüz doğrulanmadı. |
| ❌ **uyuşmazlık** | **Açıklanmamış** fark. **Yayın kapısı: bir tane bile varsa sürüm çıkmaz.** |

Bugünkü durum: **92 adayın 48'i bitmiş** (45 ✅ + 3 🟡), 44'ü 🔍 açık.

Tolerans **0,05**. Kaynaklar ara değerleri yuvarlayarak bastığı için mutlak
eşitlik beklenmez.

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

## Neden 44 satır hâlâ 🔍 açık

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
| `readability` | 11 | 3 | 2 |
| `lexical` | 7 | 0 | 23 |
| `phonetic` | 0 | 0 | 12 |

Okunabilirlik formülleri **pratik araçlardır** — yazarları formülü örnek
metinle birlikte yayımlar, çünkü amaç başkasının uygulayabilmesidir.
Sözcüksel zenginlik ölçüleri ise matematiksel tanımlardır; yazarı formülü
verir, örneği okuyucuya bırakır.

## 🔍 nasıl ✅ olur

Kaynağın yayımladığı bir sayı bulunması gerekir. Üç taze örnek:

**QUITA kılavuzu — tek seferde on üç öznitelik.** Kılavuz on dört göstergeyi iki
örnek metin üzerinde baştan sona hesaplayıp sonucu basıyor, üstelik o
metinlerin **sıklık dağılımını da yayımlıyor** (§15.3). Dağılım bu
göstergelerin tek girdisi olduğu için karşılaştırma doğrudan yapılabiliyor:

| | QUITA | bizim |
|---|---|---|
| `repeat_rate` Text 2 | 0,02147 | 0,02147 |
| `gini_coef` Text 1 | 0,3045 | 0,30449 |
| `curve_length` Text 2 | 134,2787 | 134,27870 |
| `entropy` Text 1 | 6,438043 | 6,438043 |

Yirmi sekiz karşılaştırmanın **hepsi** tutuyor; biri hariç hepsi beş
ondalığa kadar.

Not: metinler telifli (Orwell) ve depoya **girmiyor** — saklanan şey 119 ve
121 tam sayıdan ibaret sıklık dağılımı. Ondan metin geri kurulamaz.

**`mtld`** — McCarthy & Jarvis (2010) s.385 şunu yazıyor: *".887 forms
40,4% of the range between 1.00 and the full factor of .720."* 47 tip /
53 token'lık bir dizi üretim kodundan geçince kısmi faktör **0,4043**
çıkıyor. Kaynağın kendi hassasiyetinde birebir. ⚪ → ✅

**`coleman_liau`** — Makale iki ayrı denklem veriyor (cloze % kestirimi,
sonra cloze'dan sınıf düzeyine çevirme). Bizim formülümüz ikisinin
birleşimidir ve makalede o hâliyle basılmaz. Aynı metinde iki yol
karşılaştırıldı: **7,7041** ve **7,7046**. ⚪ → ✅

## 🟡 nasıl görünür — Kincaid örneği

`ari` ve `flesch_kincaid_grade` 🟡'dir. Neden ✅ değil, neden ❌ değil:

Kincaid ve ark. (1975) raporunun Ek A'sında **18 gerçek metin**, Tablo 1 ve
Tablo 2'sinde o metinler için kaynağın kendi hesapladığı değerler var. 18'ini
de boru hattından geçirdik. Ortalama sapma **0,54 ARI puanı** — tolerans
0,05'in üstünde, yani ✅ olamaz.

❌ de değil, çünkü nedenini **ölçtük**:

- **Vuruş tanımı sınandı.** Boşluğu sayıma katmak sapmayı 0,54'ten 4,24'e
  çıkarıyor. Bizim boşluksuz sayımımız doğru.
- **Başlığın sayılıp sayılmadığı sınandı.** Kaynak söylemiyor; başlıklı
  varyant 18 pasajın hepsinde daha kötü. Başlık sayılmıyormuş.
- **Kalan fark ölçüldü.** 18 pasajın 17'sinde, kaynağın sayısını verecek
  vuruş miktarı bizimkinin 0,996–1,041 katı — yani **birkaç karakter**.
  Kaynağın sayıları 1975'te daktiloya takılı mekanik bir sayaçla **elle**
  üretildi; bu büyüklükte bir fark beklenir.
- **Aykırı pasaj tespit edildi.** Pasaj 2'de kaynağın kendi iki sayısı
  birbiriyle çelişiyor: Tablo 1'in ARI'sının ima ettiği cümle uzunluğu,
  Tablo 2'nin FKGL'sini tutturmuyor.

Bütün bunlar raporun sonundaki **pasaj bazında ek tabloda** duruyor — vuruş
ve kelime sayıları dâhil, ki farkın hangi girdiden geldiği görülebilsin.

İşte 🟡'nin anlamı bu: *fark var, ölçtük, nereden geldiğini biliyoruz.*

## Rapor testlerden üretilir

`docs/dogrulama-raporu.md` elle yazılmaz. `scripts/dogrulama_raporu.py`
üretir ve `tests/test_kaynak_esligi.py` **aynı karşılaştırma tablosunu**
okur. Yani rapor ile testler ayrışamaz; rapor bayatsa test düşer.

Kapsam listesi de kayıt defterinden gelir — bir öznitelik eklenip rapora
girmemesi mümkün değil.

## Neye güvenmeli

Bir sayıyı çalışmanızda kullanmadan önce raporda satırına bakın:

- **✅** — kaynağın sayısı tutuyor, kullanın.
- **🟡** — fark var ama nedeni yazılı; nedeni okuyun, sizin kullanımınızı
  etkiliyor mu karar verin.
- **🔍 açık** — formül doğru uygulanmış ama kaynakla sayısal olarak
  karşılaştırılmamış. Künyeyi verin, sayının kaynak tarafından
  doğrulandığını **iddia etmeyin**.
- **⚪ kaynak yok** — bu kütüphanenin tanımı. Yöntem bölümünde tanımı
  kendiniz yazın.
- **⚫ etiket şeması** — sayının kendisi bizim, kategoriler şemanın.
  Şemayı kaynak gösterin (UD ya da Zeyrek), ölçüyü değil.
- **🔧 türev** — formül kaynağın, uygulama bizim. Formülün kaynağını verin
  ama ölçüyü "X (yıl) ölçüsü" diye sunmayın; tanımı kendiniz yazın.
- **❌** — böyle bir satır varsa sürüm çıkmamıştır; görürseniz sorun bildirin.
