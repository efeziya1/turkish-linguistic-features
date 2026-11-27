# Doğrulama sistemi

## Sorun

Bir araç "Ateşman okunabilirlik formülünü uyguluyorum" diyebilir. Bunu
denetlemenin yolu kaynağı bulup formülü okumak ve kodu incelemektir. Bu, kullanıcıdan beklenmeyecek kadar uzun bir iştir.

Bu araç farklı bir şey yapar: **kaynağın yayımladığı sonucu** alır, aynı girdiyi
kendi koduna verir ve iki sonucu yan yana gösterir. Bu eşleştirmenin her birine
karşılaştırma (İng. *comparison*) denir.

Sonuç: [doğrulama raporu](../../dogrulama-raporu.md)
([English](../../verification-report.md)).

## Doğrulamanın iki katmanı

### 1. Formül eşdeğerliği

Künyesi olan bütün özniteliklerin formülü kaynağıyla karşılaştırılarak kontrol
edildi; kaynak çoğunlukla birincil, Türkçede 12 künyede ikincildir (aktaran, İng. *as cited in*).
Her künye, formülün kaynakta geçtiği sayfayı ve numarasını gösterir (örneğin
`p.327, eq. (5)`). Testler formülü ve sınır durumlarını sınar.
Künyesi olmayan 11 öznitelik yalın tanımdır; karşılaştırılacak bir kaynakları yoktur.

### 2. Kaynak sayısı doğrulaması

Birinci katmanın üstüne eklenen ek bir kontroldür: Kaynağın bir metin ya da girdi için
yayımladığı sonuç bulunur ve aracın sonucuyla karşılaştırılır. Doğrulama adayı olan 136
özniteliğin 22'si bu katmanda doğrulanmıştır. Bu sayfanın geri kalanı bu katmanı anlatır.

İkinci katman birincinin koşulu değildir. 🔍 açık işaretli bir özniteliğin formülü
şüpheli değildir; yalnız karşılaştırılacak yayımlanmış bir örnek bulunamamıştır.

## Önce: her öznitelik doğrulanamaz

217 özniteliğin bir kısmı, tanımı gereği
**doğrulama adayı bile değildir**:

| | Neden aday değil |
|---|---|
| ⚪ **yalın tanım** (İng. *plain definition*) | Kaynağı yoktur. `punct_dash_ratio` "tire / bütün noktalama işaretleri" demektir; alanyazında aranacak bir sayı yoktur. |
| ⚫ **etiket oranı** (İng. *tag ratio*) | Bir ölçü değil, dış bir şemanın kategorisini sayıyor. `pos_noun_ratio` → UD, `akana_case_loc_ratio` → Akana. **Şema kategori tanımlar, ölçüm yayımlamaz** — de Marneffe'in makalesinde "case_loc_ratio = 0,07" gibi bir sonuç yoktur, olamaz. |
| 🔧 **araca özgü** (İng. *tool-specific*) | Formül bir kaynaktan, **nereye uygulanacağı araçtan**. `sent_len_entropy` Shannon'ın entropisidir, ama tümce uzunluklarına uygulanması aracın kararıdır. Bu ölçüyü kimse yayımlamadı. |
| 📐 **kalibre edilmiş** (İng. *calibrated*) | Eşik aracın kendi kalibrasyonundan gelir: `long_sent_ratio`. Aracı kendi kalibrasyonuyla sınamak, cevabı yine kendisinden almak olurdu. |

Türkçede **81 öznitelik** bu dört türden biridir; kalan **136 öznitelik** doğrulama adayıdır.
Bir öznitelik, mümkün olduğunda birden çok yayımlanmış örnekle sınanmıştır.

## Adayların dört durumu

| | Anlamı |
|---|---|
| ✅ **örtüşen** (İng. *match*) | Kaynağın yayımladığı sayıyla tolerans içinde aynı. Küçük bir farkın nedeni biliniyorsa karşılaştırmanın altında not olarak yazılır. |
| 🟡 **belgelenmiş sapma** (İng. *documented deviation*) | Fark **toleransın dışında** ve **nedeni yazılı** — kaynağın ara değeri yuvarlaması, kaynağın sayılarının elle üretilmiş olması gibi. |
| 🔍 **açık** (İng. *open*) | Kaynak formülü veriyor ama formülü bir metne uyguladığı bir örnek vermiyor; yayımlanmış bir örnek bulunursa doğrulanabilir. |
| ❌ **uyuşmazlık** (İng. *mismatch*) | **Açıklanmamış** fark. **Yayın kapısı (İng. *release gate*): bir tane bile varsa sürüm çıkmaz.** |

Bugünkü durum: **136 aday özniteliğin 22'si doğrulanmış** (✅), 114'ü 🔍 açıktır. Türkçede 🟡 yoktur;
İngilizcede iki öznitelik 🟡: `ari` kaynaktan %4,4 (0,54 puan), `flesch_kincaid_grade` %3,5
(0,37 puan) sapar. İkisinin de nedeni, kaynağın 1975'te karakterleri elle saymasıdır; parça
parça sayılar [doğrulama raporunun](../../dogrulama-raporu.md) ekindedir.

Tolerans yayımlanan değerin **%1'i** (göreli tolerans, İng. *relative tolerance*). Kaynaklar ara değerleri
yuvarlayarak verdiği için tam eşitlik beklenmez.

**Toleransı aşan fark otomatik olarak ❌ değildir.** Belirleyici olan farkın
büyüklüğü değil, **nedeninin bilinip bilinmediğidir**. Nedeni ölçülmüş ve
yazılmışsa karşılaştırma 🟡 olur; yazılmamışsa ❌ olur ve sürüm çıkmaz.

**İstisna: kaynağın kendi hesabı.** Kaynak hem girdileri hem sonucu yayımlamışsa, sonuç o
girdilerden yeniden hesaplanabilir. Yayımlanan sonuç bu hesapla tutmuyorsa (sözgelimi kaynak
121 ÷ 202 = 0,599'u yuvarlamak yerine kesip 0,59 yazmışsa) ve aracın değeri kaynağın kendi
girdileriyle yapılan hesapla aynıysa karşılaştırma ✅ sayılır; durum karşılaştırmanın altında
yazılır. Bu istisna yalnız kaynağın kendi sayılarıyla denetlenebilen durumlar içindir ve bugün
tek bir yerde uygulanır: QUITA'nın Text 2 metninde `ttr` ([aşağıda](#nasl-olur)).

Toleransı aşan bir farkın 🟡 sayılması için de gerekçe bir tahmin olamaz ("herhalde
yuvarlamadır"); farkın nereden geldiğini gösteren bir ölçüm gerekir. İngilizcedeki iki 🟡
buna örnektir (yukarıda).

## İki kanıt türü

Bu ayrım önemli ve raporda ayrı sütunda durur.

**Uçtan uca karşılaştırma** (İng. *end-to-end comparison*), kaynağın **kendi metnini** çözümleme hattından geçirir. Yani
türceleme, seslem sayımı ve tümce bölme de sınanır. En güçlü kanıttır: bir
sayı tutuyorsa yalnız formül değil, ona giden bütün adımlar doğrudur.

**Formül karşılaştırması** (İng. *formula comparison*), fonksiyona girdileri doğrudan verir — örneğin "seslem/sözcük 2,2
ve sözcük/tümce 4". Formülü ve katsayıları doğrular, çözümleme hattını
doğrulamaz. Türkçede doğrulanan 22 özniteliğin 19'u bu yolla sınanmıştır; uçtan uca sınananlar
Ateşman, Çetinkaya-Uzun ve Bezirci-Yılmaz formülleridir.

## Neden 114 öznitelik hâlâ 🔍 açık

Kaynak formülü yayımlamış, ama o formülü bir metne uygulayıp sonucunu vermemiş.
Bu, nicel dilbilim alanyazınında **olağandır**. Böyle bir sayı olmayınca
karşılaştıracak bir şey de olmaz.

`yule_k` başka bir durumdur. Yule (1944) K değerlerini verir, ama bunları tek bir sözcük
sınıfının, çoğunlukla adların, sözlükbirimleriyle hesaplar. Araç bütün sözcüklerin yüzey
biçimini saydığı için aynı girdiyle karşılaştırılamaz.

**Bu öznitelikler test edilmiyor demek değildir.** Formül ve sınır durumları
kendi test dosyalarında sınanır. Rapor yalnız *kaynağın sayısıyla*
karşılaştırmayı takip eder.

Hangi grupların daha çok doğrulanabildiği ölçünün türüyle ilgilidir (öznitelik sayıları):

| Grup | ✅ | 🔍 |
|---|---:|---:|
| `frequency_structure` | 11 | 6 |
| `lexical` | 5 | 29 |
| `readability` | 3 | 10 |
| `syntactic` | 2 | 0 |
| `pos` | 1 | 4 |

Okunabilirlik formülleri **pratik araçlardır**: Yazarları formülü örnek metinle birlikte
yayımlar, çünkü amaç başkasının uygulayabilmesidir. Ateşman, Çetinkaya-Uzun ve
Bezirci-Yılmaz formülleri bu yüzden doğrulanabildi; açık kalanlar formüllerin
bileşenleri ve Kalyoncu formülleridir. Sözcüksel zenginlik ölçüleri ise matematiksel
tanımlardır; yazarı formülü verir, örneği okura bırakır.

## 🔍 nasıl ✅ olur

Kaynağın yayımladığı bir sayı bulunması gerekir. Örnek:

**QUITA kılavuzu — tek seferde on dört öznitelik.** Kılavuz on dört göstergeyi iki
örnek metin üzerinde baştan sona hesaplayıp sonucu veriyor, üstelik o
metinlerin **sıklık dağılımını da yayımlıyor** (§15.3). Dağılım bu
göstergelerin tek girdisi olduğu için karşılaştırma doğrudan yapılabiliyor:

| | QUITA | araç |
|---|---|---|
| `repeat_rate` Text 2 | 0,02147 | 0,02147 |
| `gini_coef` Text 1 | 0,3045 | 0,30449 |
| `curve_length` Text 2 | 134,2787 | 134,27870 |
| `entropy` Text 1 | 6,438043 bit = 4,462511 nat | 4,462512 |

QUITA bir yazılımın kılavuzudur: Formüller için ikincil kaynaktır (her formülün özgün
kaynağı künyede yazılı), karşılaştırılan sayılar ise kılavuzun kendi hesaplarıdır. QUITA
entropiyi bit cinsinden verir; araç doğal logaritma kullandığı için değer nata çevrilerek
karşılaştırılır.

On dört özniteliğin hepsi iki metinde de kaynakla örtüşür (en büyük göreli fark %0,1'in
altında; çoğunda sapma sıfır). Yalnız `ttr`'nin Text 2 değerinde sapma 0,009, yani
yayımlanan değerin %1,5'idir: Kaynak 0,59 vermiş, ama kendi
verdiği sayıları bölünce 121 ÷ 202 = **0,599** çıkıyor. Kaynak sonucu yuvarlamak
yerine kesmiş (iki ondalığa yuvarlanmışı 0,60). Aracın değeri aritmetik olarak
doğru olduğu için bu karşılaştırma da ✅ sayılır (kaynağın kendi hesabı istisnası, yukarıda).

## Kısaca: ne kadarı sınanabildi

Türkçedeki 136 alanyazın ölçüsünün yalnız 22'si kaynağın yayımladığı bir hesaplama örneğiyle
karşılaştırılabildi ve hepsi kaynakla örtüşür. Bu
özniteliklerden yalnız üçü uçtan uca, yani sözcük, seslem ve tümce sayımıyla birlikte
sınanabildi. Kaynakların çoğu ölçüyü formülüyle tanımlar, ama formülü bir metne uygulayıp
sonucunu yayımlamaz.

Raporun dışında, uzman değerlerini içeren bir sınama veri seti (İng. *test dataset*) de
kullanıldı: TOMA programı için yayımlanan 57 metin (Kalyoncu vd. 2026). Bu veri setinde
aracın sözcük ve seslem sayıları uzman değerleriyle neredeyse tamamen, tümce sayıları ve
Türkçe okunabilirlik formülleri metinlerin çoğunda örtüşür. İnsan yargısına dayanan
değişkenlerde (Kalyoncu'nun KL ve KCO'su) araç uzman değerlerini üretmez.

## ⚪, 🔧 ve 📐 için tanımı araç verir

Bu özniteliklerin alanyazında bir kaynağı yoktur; bir çalışmada kullanıldıklarında tanımlarının
yazılması gerekir. Araç her özniteliğin tanımını hazır verir, yöntem bölümüne buradan
alınabilir:

```python
tlf.describe_feature("sent_len_entropy")["formula"]
```

```text
'Shannon entropy (nats) of the distribution of words per sentence'
```

Örnek olarak beşi:

| Öznitelik | Tanım | Kaynağa ait olan |
|---|---|---|
| ⚪ `lemma_count` | metindeki farklı sözlükbirim sayısı | — (kaynağı yok) |
| ⚪ `sent_syllable_mean` | tümce başına ortalama seslem | — (kaynağı yok) |
| 🔧 `sent_len_entropy` | tümce uzunluklarının dağılımının Shannon entropisi (nat) | entropi formülü — Shannon (1948) |
| 📐 `short_sent_ratio` | 4 sözcükten kısa tümce / tümce (İngilizcede 8) | eşik değeri — [eşik kalibrasyonu](../../esik-kalibrasyonu.md) |
| 📐 `long_sent_ratio` | 17 sözcükten uzun tümce / tümce (İngilizcede 32) | eşik değeri — [eşik kalibrasyonu](../../esik-kalibrasyonu.md) |

Formülün kaynağı verilmeli, ama ölçü o kaynağın ölçüsü gibi gösterilmemelidir.

- ✗ "Shannon (1948) `sent_len_entropy` ölçüsü"
- ✓ "Shannon (1948) entropisinin tümce uzunluğu dağılımına uygulanması
  (turkish-linguistic-features, doi:10.5281/zenodo.23009540)"

Birinci yazım okuyucuya, kaynakta aranınca bulunacak bir ölçü olduğunu ima
ediyor. Shannon entropiyi tanımladı, tümce uzunluklarına uygulamadı.
