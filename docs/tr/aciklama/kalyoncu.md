# Kalyoncu (2025) formülleri

Kalyoncu (2025) Türkçe için dört okunabilirlik formülü önerir (K1–K4). Formüllerin
çıktısı "Metin Zorluğu"dur: **yüksek değer daha zor metin** demektir. Araç dört formülü
ve beş bileşenini `readability` grubunda verir. Bu anahtarlar yalnız Türkçede üretilir.

| Anahtar | Kalyoncu'daki adı | Tanım | Kaynak |
|---|---|---|---|
| `kalyoncu_kl` | KL | listede olmayan sözcük / sözcük × 100 | s.71–72 |
| `kalyoncu_ttr` | TTR | bir kez geçen gövde / sözcük × 100 | s.73 |
| `kalyoncu_kco` | KCO | karmaşık tümce / tümce × 100 | s.73 |
| `kalyoncu_yco` | YCO | fiilimsi / tümce × 10 | s.74 |
| `kalyoncu_ocu` | OCU | sözcük / tümce | s.77 |
| `kalyoncu_k1` … `kalyoncu_k4` | Birinci … Dördüncü formül | aşağıda | s.97–99 |

`kalyoncu_ttr` aracın `ttr`'si değildir: farklı sözcük oranını değil, **yalnız bir kez geçen**
gövdelerin oranını ölçer. Kalyoncu bu ölçüye TTR adını verir.

## Formüller

| Anahtar | Formül (Tablo 31–34) |
|---|---|
| `kalyoncu_k1` | −29,829 + 0,508·KL + 1,191·TTR + 0,733·KCO − 0,66·OCU |
| `kalyoncu_k2` | 25,457 + 0,877·KL + 0,668·TTR + 0,333·OCU |
| `kalyoncu_k3` | 25,153 + 0,834·KL + 0,686·TTR + 0,226·YCO |
| `kalyoncu_k4` | 43,368 + 1,008·KL + 0,624·OCU |

Bileşenlerden biri `nan` ise formül de `nan` olur.

## Sözcük ve tümce

**Sözcük** aracın varsayılan sözcüğüdür, bir farkla: rakam içeren sözcük okunuşuyla açılır ve
okunuşunun sözcük sayısınca sayılır (Kalyoncu s.xiii). `1968` "bin dokuz yüz altmış sekiz"
olarak 5 sözcüktür, `%50` "yüzde elli" olarak 2 sözcüktür. Kısaltmalar açılmaz. Bu kural yalnız
Kalyoncu anahtarlarında geçerlidir.

Bu yüzden `kalyoncu_ocu` aracın `sent_len_mean`'inden farklı olabilir:

| Metin | `sent_len_mean` | `kalyoncu_ocu` |
|---|---|---|
| `Bu bir tümce. 1999. Bitti.` | 5 / 2 = 2,5 | 9 / 2 = 4,5 |

**Tümce** aracın varsayılan tümcesidir ([Kavramlar](kavramlar.md#tumce)); harf içermeyen tümce
sayılmaz. Kalyoncu tümceyi anlama göre ayırır: tırnak ya da ara tümce içindeki, kendi anlam
bütünlüğü olan tümceler ve iki noktadan sonraki söylem ve açıklamalar ayrı tümcedir (s.xii).
Bu kural **uygulanmaz**; anlam bütünlüğü otomatik sınanamaz. TOMA'nın 57 metninde aracın
tümce kuralı uzmanın sayımından toplam 41 tümce (yaklaşık %2) farklıdır, 37 metinde birebir
aynıdır.

**Gövde** Zeyrek'in sözlükbirimine türetme eklerinin eklenmesiyle bulunur: `kitapçılar` →
`kitapçı`, `öğretmenliği` → `öğretmenlik`. Çekim ekleri atılır. Ettirgen ve edilgen ekleri,
fiilimsi ekleri, birleşik fiil ekleri (-ebil, -iver, -eyaz, -akal, -akoy, -adur, -egel) ve ek
fiil de gövdeye girmez: `küçültülmek` → `küçül`, `gelebildi` → `gel`, `evdeydi` → `ev`.
Zeyrek birden çok çözümleme verirse ilki alınır.

## KL: listeyle karşılaştırma

Liste Kalyoncu'nun bilinirlik temelli sözcük listesidir (Ek-1, s.129–160, 4600 sözcük). Bir
sözcük şu üç biçimden biri listedeyse **liste içidir**: küçük harfli kendisi, gövdesi, fiilse
gövde + -mak/-mek. Yumuşamış son ünsüz (`öğretmenliğ`) sertleştirilerek de aranır.
Karşılaştırmada şapka iki tarafta da silinir: metindeki `hikaye` de `hikâye` de listedeki
maddeyle eşleşir. KL bilinirliğe bakar; şapkasız biçimi başka bir sözcük olan durumlarda
(`hala`/`hâlâ`, `dahi`/`dâhi`) iki biçim de bilinen sözcük olduğu için sonuç değişmez. Şapka
yalnız KL'de silinir; `kalyoncu_ttr` dahil başka hiçbir yerde silinmez.

Kalyoncu'nun dokuz kuralı (s.71–72):

| Kural | Araçta |
|---|---|
| 1. Özel adlar liste dışı sayılmaz | uygulanır: spaCy'nin `PROPN` etiketi; paydada kalır, paya girmez |
| 2. Çekimli biçim listedeki sözcük sayılır | uygulanır: gövde |
| 3. Yaygın türetme ekli türevler liste dışı sayılmaz | **uygulanmaz**: hangi eklerin yaygın sayıldığı belirtilmemiş |
| 4. Fiilimsi olarak kullanılan liste fiilleri | uygulanır: Zeyrek'in fiilimsi etiketleri |
| 5. Yansıma sözcükler liste dışı sayılmaz | **uygulanmaz** |
| 6. Pekiştirilmiş biçimler (`büsbüyük`) | **uygulanmaz** |
| 7. Ettirgen ve edilgen biçimler | uygulanır: Zeyrek'in çatı etiketleri |
| 8. Uzak anlamda kullanılan liste sözcüğü liste dışıdır | **uygulanmaz**: bağlam yorumu gerektirir |
| 9. Sayılar liste dışı sayılmaz | uygulanır: okunuşla açılan sayı sözcükleri liste içi |

## Fiilimsi ve karmaşık tümce

**Fiilimsi**, Zeyrek çözümlemesinde isim-fiil (-mak, -ma, -ış), sıfat-fiil (-an, -dık, -acak,
-mış, -ar/-maz) ya da zarf-fiil (-ip, -arak, -ınca, -ken, -madan, -dıkça…) etiketi taşıyan
sözcüktür. Ek fiilli adın -ken'i (`öğrenciyken`) sayılmaz. Bir sözcük en çok bir fiilimsi sayılır.

**Karmaşık tümce** (KCO) en az bir fiilimsi ya da en az iki fiil içeren tümcedir. Kalyoncu
karmaşık tümceyi "birden fazla yargıya sahip olan, içerisinde fiilimsi barındıran ya da bağlı
cümle durumunda olan" tümce diye tanımlar (s.73). "Yargı"yı tanımlamaz, ama CYargı
değişkeninde fiil ve fiilimsi sayısıyla ölçer (s.73); araç da öyle sayar. Fiil, Zeyrek'in son
türü `Verb` olan sözcüktür (`evdeydi` dahil). Bağlaçla birleşmiş tümcelerin çoğu iki fiil
içerdiği için yakalanır; ek fiilsiz ad tümceleri (`Hava güzel ama soğuk.`) yakalanmaz.

## Sınıf düzeyleri

Araç yalnız sayıyı verir. Kalyoncu'nun sınıf düzeyi tabloları (s.102–105):

| Düzey | K1 | K2 | K3 | K4 |
|---|---|---|---|---|
| 3. sınıf öncesi | <30 | <35 | <35 | <40 |
| 3 ve 4. sınıf | 30–40 | 35–45 | 35–45 | 40–50 |
| 5 ve 6. sınıf | 40–50 | 45–55 | 45–55 | 50–55 |
| 7 ve 8. sınıf | 50–60 | 55–60 | 55–60 | 55–59 |
| 9 ve 10. sınıf | 60–70 | 60–64 | 60–65 | 59–65 |
| 11 ve 12. sınıf | 70–76 | 64–70 | 65–70 | 65–72 |
| Lisans | 76–85 | 70–85 | 70–85 | 72–85 |
| Lisansüstü | >85 | >85 | >85 | >85 |

Kaynakta metin ile tablolar dört yerde ayrışır; değerler tablolardan alındı:

- K1: metin "70–75 arası 11 ve 12. sınıf, 76–85 lisans" der, tablo "70–76" der.
- K4: metin 7 ve 8. sınıf için "50–59" der, tablo "55–59" der.
- Sınır değerinin hangi aralığa girdiği yazılmaz; metin "30 puan ve aşağısı" der, tablo "<30".
- Metin tablolara 37–40 diye atıf yapar, tablo başlıklarında 36–39 yazar.

## TOMA ile farklar

TOMA (Kalyoncu vd. 2026) K1–K4'ü otomatik hesaplayan masaüstü programıdır.

- KL'de şapkayı TOMA da siler (s.298); bu konuda aynıdır.
- TOMA KL'de salt rakamdan oluşan sözcükleri hesap dışı bırakır (s.298). Araç onları
  okunuşla açar ve liste içi sayar.
- TOMA KCO ve YCO'yu Stanza bağımlılık çözümlemesiyle hesaplar; araç Zeyrek'le hesaplar.
- TOMA ana sayımlarda tümceyi hangi araçla böldüğünü yazmaz.

## Sınırlılıklar

Bu değerler Kalyoncu'nun elle yaptığı sayımın yaklaşığıdır.

- Zeyrek'in tanımadığı ekler (-alı, -ası, -casına, -maksızın) fiilimsi sayılamaz.
- Zeyrek'in ilk çözümlemesi yanlışsa sonuç da yanlış olur: `okuma` isim-fiil değil "ok-um-a"
  diye çözümlenir; `okunur kitap`'taki sıfat-fiil çekimli fiil sayılır.
- Zeyrek'in çözümleyemediği sözcükte gövde küçük harfli sözcüğün kendisidir; yabancı sözcük ve
  yazım hatası her biçimiyle ayrı gövde sayılır.
- KCO en yaklaşık bileşendir. TOMA'da da uzman değerinden en çok sapan değişken KCO'dur
  (Kalyoncu vd. 2026).

## Liste

Liste `turkish_linguistic_features/data/kalyoncu_2025_ek1.txt` dosyasında, Kalyoncu'nun
yazdığı sırayla ve yazımla durur (şapkalı yazımlar dahil). **Paketin MIT lisansının kapsamında
değildir**; hakları yazarındadır. PDF'in metin katmanı ğ, ş, ı ve baştaki İ/Ş'yi bozduğu için
her madde sayfa görüntüsüyle karşılaştırıldı. Kaynakta "Çita" noktalı i ile yazılıdır ve öyle
bırakıldı.
