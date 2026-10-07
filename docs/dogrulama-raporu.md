<!-- ÜRETİLMİŞ DOSYA — elle düzenlemeyin.
     Kaynak: scripts/generate_verification_report.py
     Yeniden üretmek için:
       python scripts/generate_verification_report.py -->

# Doğrulama raporu

Bu rapor her özniteliğin ürettiği sayıyı, dayandığı kaynağın **yayımladığı
sayıyla** karşılaştırır. Amaç basit: bir sayıyı çalışmanızda kullanmadan önce
onun literatürdeki değeri tuttuğunu görebilmeniz.

## Durumlar ne anlama geliyor

| | Anlamı |
|---|---|
| ✅ **birebir** | Kaynağın yayımladığı sayıyla tolerans içinde aynı. Küçük bir farkın nedeni biliniyorsa satırın altında not olarak yazılır. |
| 🟡 **belgelenmiş sapma** | Fark **toleransın dışında** ve **nedeni yazılı**. Kaynağın ara değerleri yuvarlaması, ya da kaynağın sayılarının elle üretilmiş olması gibi. Sapmanın sonuca etkisi satırda anlatılır. |
| 🔍 **açık** | Kaynak formülü veriyor ama uygulanmış bir örnek vermiyor. Doğrulanabilir, henüz doğrulanmadı; formül ve sınır durumları kendi test dosyalarında sınanıyor. |
| ❌ **uyuşmazlık** | **Açıklanmamış** fark. **Yayın kapısı:** bir tane bile varsa sürüm çıkmaz. |

Aşağıdaki üç durum **doğrulama adayı değildir** — aranacak bir sayı yoktur:

| | Anlamı |
|---|---|
| ⚪ **kaynak yok** | Adlandırılmış bir literatür ölçüsü değil; saf tanım (`punc_,_ratio`, `char_a`). |
| ⚫ **etiket şeması** | Bir ölçü değil, dış bir şemanın kategorisini sayıyor (`pos_noun` → UD; `case_loc_ratio` → Zeyrek). Şema kategori tanımlar, ölçüm yayımlamaz. |
| 🔧 **türev** | Formül bir kaynaktan, **uygulaması bu kütüphaneden**. `entropy_std` Shannon'ın entropisidir ama parçalar arası standart sapması bizim; `long_sent_ratio`'nun eşiği kendi kalibrasyonumuzdan gelir. Kimse bu ölçüyü yayımlamadı, dolayısıyla karşılaştırılacak sayı da yok. Kendi kalibrasyonumuza karşı sınamak kendi cevabımıza bakmak olurdu. |

Tolerans yayımlanan değerin **%1'i** (göreli). Kaynaklar ara değerleri
yuvarlayarak bastığı için mutlak eşitlik beklenmiyor; göreli tolerans her
ölçekte aynı anlama gelir.

**Toleransı aşan fark otomatik olarak ❌ değildir.** Belirleyici olan farkın
büyüklüğü değil, **nedeninin bilinip bilinmediğidir**: nedeni ölçülmüş ve
yazılmışsa satır 🟡, yazılmamışsa ❌ olur. Gerekçe bir mazeret değil, farkın
nereden geldiğinin kanıtıdır — ilgili satırın altında okuyabilirsiniz.

## Kanıtın iki türü

**Uçtan uca** satırlar kaynağın **metnini** boru hattından geçirir — yani
tokenizasyon, heceleme ve cümle bölme de sınanır. Bunlar en güçlü kanıt.

**Formül** satırları fonksiyona girdileri doğrudan verir (örneğin "hece/sözcük
2,2 ve sözcük/cümle 4"). Formülü ve katsayıları doğrular, boru hattını
doğrulamaz. Kaynak bir metin yayımlamamışsa elde olan budur.

Bu rapor **testlerden üretilir** — `tests/test_kaynak_esligi.py` ile aynı
karşılaştırma tablosunu okur, yani ikisi ayrışamaz. Diğer bilinen-değer
testleri kendi dosyalarında duruyor.


## Türkçe — 211 anahtar, 236 satır

Bir anahtarın birden çok kaynak örneği olabilir; her biri ayrı satır.

**Doğrulama adayı — 95 satır**

| Durum | Satır sayısı |
|---|---|
| ✅ birebir | 46 |
| 🟡 belgelenmiş sapma | 2 |
| 🔍 açık — kaynakta sayısal örnek yok | 47 |


**Doğrulama adayı olmayan — 141 satır.** Bunlarda aranacak yayımlanmış bir sayı yoktur.

| Durum | Satır sayısı |
|---|---|
| ⚪ kaynak yok — saf tanım | 68 |
| ⚫ etiket şeması — ölçü değil | 68 |
| 🔧 türev — uygulaması bu kütüphaneye ait | 5 |

### Sayısal karşılaştırması olanlar

| Anahtar | Kaynak | Örnek | Kanıt | Beklenen | Bizim | Fark | Durum |
|---|---|---|---|---|---|---|---|
| `entropy` | QUITA §6.1.12 | Text 1 · eq. (6.26); kaynak bit ile 6,438043 → × ln 2 | formül | 4.463 | 4.463 | +0.000 | ✅ |
| `entropy` | QUITA §6.1.12 | Text 2 · eq. (6.26); kaynak bit ile 6,395099 → × ln 2 | formül | 4.433 | 4.433 | +0.000 | ✅ |
| `ttr` | QUITA §6.1.1 | Text 1 · V/N = 119/179 | formül | 0.665 | 0.665 | -0.000 | ✅ |
| `ttr` | QUITA §6.1.1 | Text 2 · V/N = 121/202 = 0.599; kaynak 0.590 basmış (baskı hatası) | formül | 0.590 | 0.599 | +0.009 | 🟡 |
| `hapax_percentage` | QUITA §6.1.6 | Text 1 · 98/179 | formül | 0.547 | 0.547 | +0.000 | ✅ |
| `hapax_percentage` | QUITA §6.1.6 | Text 2 · 92/202 | formül | 0.455 | 0.455 | +0.000 | ✅ |
| `mtld` | McCarthy & Jarvis (2010) p.385 | kısmi faktör · TTR .887 → 40.4% | formül | 0.404 | 0.404 | +0.000 | ✅ |
| `h_point` | QUITA §6.1.2 | Text 1 · sıra 5 = sıklık 5 | formül | 5.000 | 5.000 | +0.000 | ✅ |
| `h_point` | QUITA §6.1.2 | Text 2 · ara değerleme, eq. (6.2) | formül | 4.750 | 4.750 | +0.000 | ✅ |
| `vocab_richness_r1` | QUITA §6.1.3 | Text 1 · N=179, h=5 | formül | 0.835 | 0.835 | -0.000 | ✅ |
| `vocab_richness_r1` | QUITA §6.1.3 | Text 2 · N=202, h=4.75 → ⌊h⌋=4 | formül | 0.838 | 0.838 | +0.000 | ✅ |
| `vocab_richness_r4` | QUITA §6.1.9 | Text 1 · 1−G | formül | 0.696 | 0.696 | +0.000 | ✅ |
| `vocab_richness_r4` | QUITA §6.1.9 | Text 2 · 1−G | formül | 0.649 | 0.649 | -0.000 | ✅ |
| `repeat_rate` | QUITA §6.1.4 | Text 1 · N=179 | formül | 0.020 | 0.020 | -0.000 | ✅ |
| `repeat_rate` | QUITA §6.1.4 | Text 2 · N=202 | formül | 0.021 | 0.021 | -0.000 | ✅ |
| `rr_mcintosh` | QUITA §6.1.5 | Text 1 · V=119 | formül | 0.946 | 0.946 | +0.000 | ✅ |
| `rr_mcintosh` | QUITA §6.1.5 | Text 2 · V=121 | formül | 0.939 | 0.939 | -0.000 | ✅ |
| `gini_coef` | QUITA §6.1.8 | Text 1 · m₁=41.88268156 | formül | 0.304 | 0.304 | -0.000 | ✅ |
| `gini_coef` | QUITA §6.1.8 | Text 2 · m₁=39.75742574 | formül | 0.351 | 0.351 | +0.000 | ✅ |
| `curve_length` | QUITA §6.1.10 | Text 1 · eq. (6.21) | formül | 129.356 | 129.356 | +0.000 | ✅ |
| `curve_length` | QUITA §6.1.10 | Text 2 · eq. (6.21) | formül | 134.279 | 134.279 | +0.000 | ✅ |
| `curve_length_r` | QUITA §6.1.11 | Text 1 · Lh=14.29145 | formül | 0.889 | 0.890 | +0.000 | ✅ |
| `curve_length_r` | QUITA §6.1.11 | Text 2 · Lh=18.03607 | formül | 0.866 | 0.866 | -0.000 | ✅ |
| `lambda_pa` | QUITA §6.1.7 | Text 1 · L·ln N/N, L=129.3559482; kaynak log₁₀ ile 1,628 → × ln 10 | formül | 3.749 | 3.749 | +0.000 | ✅ |
| `lambda_pa` | QUITA §6.1.7 | Text 2 · L·ln N/N, L=134.2787065; kaynak log₁₀ ile 1,5325 → × ln 10 | formül | 3.529 | 3.529 | -0.000 | ✅ |
| `adjusted_modulus` | QUITA §6.1.13 | Text 1 · M=24.01416249; kaynak log₁₀ ile 10,6594 → / ln 10 | formül | 4.629 | 4.629 | -0.000 | ✅ |
| `adjusted_modulus` | QUITA §6.1.13 | Text 2 · M=25.81931678; kaynak log₁₀ ile 11,19973 → / ln 10 | formül | 4.864 | 4.864 | +0.000 | ✅ |
| `writers_view_alpha` | QUITA §6.2.3 | Text 1 · arccos(−0.374487816) | formül | 1.955 | 1.955 | -0.000 | ✅ |
| `writers_view_alpha` | QUITA §6.2.3 | Text 2 · arccos(−0.269972586) | formül | 1.844 | 1.844 | +0.000 | ✅ |
| `activity_ratio` | QUITA §6.2.2 | Text 1 · 26 fiil / 14 sıfat | formül | 0.650 | 0.650 | +0.000 | ✅ |
| `activity_ratio` | QUITA §6.2.2 | Text 2 · 35 fiil / 8 sıfat | formül | 0.814 | 0.814 | -0.000 | ✅ |
| `arc_len_mean` | Jing & Liu (2015) p.164 | Figure 3 · 'Mr. Nixon was to…' | formül | 1.167 | 1.167 | +0.000 | ✅ |
| `arc_len_mean` | Liu (2008) eq. (1) | 'I actually live in Beijing' · 5/4 | formül | 1.250 | 1.250 | +0.000 | ✅ |
| `parse_depth_mean` | Jing & Liu (2015) p.164 | Figure 3 · MHD = 12/6 | formül | 2.000 | 2.000 | +0.000 | ✅ |
| `ari` | Kincaid et al. (1975) p.8, Table 1 | Appendix A · 18 passages, mean | uçtan uca | 12.300 | 11.763 | -0.537 | 🟡 |
| `coleman_liau` | Coleman & Liau (1975) p.284 | iki denklemin bileşimi · 13 kelime, 2 cümle | formül | 7.704 | 7.705 | +0.000 | ✅ |
| `coleman_liau` | Coleman & Liau (1975) p.284, Table 1 | cloze 40.4% → 12. sınıf | formül | 12.000 | 11.994 | -0.006 | ✅ |
| `atesman` | Ateşman (1997) | Kalyoncu & Memiş (2024) Table 9 · Text 2 | uçtan uca | 23.094 | 23.094 | -0.000 | ✅ |
| `atesman` | Ateşman (1997) p.74 | kalibrasyon: en kolay metin | formül | 100.000 | 100.000 | -0.000 | ✅ |
| `atesman` | Ateşman (1997) p.74 | kalibrasyon: en zor metin | formül | 0.000 | 0.000 | +0.000 | ✅ |
| `cetinkaya_uzun` | Çetinkaya (2010) | Kalyoncu & Memiş (2024) Table 9 · Text 2 | uçtan uca | 23.084 | 23.084 | -0.000 | ✅ |
| `bezirci_yilmaz` | Bezirci & Yılmaz (2010) | Kalyoncu & Memiş (2024) Table 9 · Text 2 | uçtan uca | 30.423 | 30.392 | -0.031 | ✅ |
| `bezirci_yilmaz` | Bezirci & Yılmaz (2010) Table 5 | E7 3.03 · OKS 7 | formül | 4.610 | 4.605 | -0.005 | ✅ |
| `bezirci_yilmaz` | Bezirci & Yılmaz (2010) Table 5 | E7 8.3 · OKS 10 | formül | 9.110 | 9.110 | +0.000 | ✅ |
| `bezirci_yilmaz` | Bezirci & Yılmaz (2010) Table 5 | E7 18.82 · OKS 14 | formül | 16.230 | 16.232 | +0.002 | ✅ |
| `bezirci_yilmaz` | Bezirci & Yılmaz (2010) Table 3 | en kolay metnin H değerleri | formül | 3.030 | 3.025 | -0.005 | ✅ |
| `bezirci_yilmaz` | Bezirci & Yılmaz (2010) Table 3 | en zor metnin H değerleri | formül | 18.820 | 18.815 | -0.005 | ✅ |
| `bezirci_yilmaz` | Bezirci & Yılmaz (2010) Table 3 | ortalama H değerleri | formül | 8.300 | 8.341 | +0.041 | ✅ |

**`ttr` sapması:** Kaynağın kendi sayıları (V=121, N=202) 121/202 = 0,599 verir; basılan 0,590 bu aritmetikle tutmuyor (baskı hatası). Bizim değer aritmetiğe uyuyor; fark yayımlanan değerin %1,5'i.

**`ari` sapması:** Kaynağın sayıları 1975'te daktiloya takılı mekanik bir sayaçla **elle** üretildi (Ek B, ARI talimatı). 18 pasajın 17'sinde, kaynağın ARI'sını verecek vuruş sayısı bizim saydığımızın 0,996-1,041 katı — yani birkaç karakterlik fark. Pasaj 2 aykırı (oran 1,145) ve kaynağın kendi iki sayısı orada çelişiyor: Tablo 1'in ARI 20,3'ü vuruş/kelime 6,269 gerektiriyor, metnin gerçek değeri 5,475; üstelik o ARI'nın ima ettiği kelime/cümle FKGL'yi 18,69 yapıyor, oysa Tablo 2 16,7 basmış. Bizim vuruş tanımımız ayrıca sınandı: boşluğu sayıma katmak farkı 0,54'ten 4,24'e çıkarıyor, yani boşluksuz sayım doğru.

**`bezirci_yilmaz` sapması:** Makale H6 ara değerini yuvarlamış; fark 0,031 ve iki değer de aynı okunabilirlik sınıfına düşüyor (akademik, 16+).

**`bezirci_yilmaz` sapması:** Makale H6 ortalamasını 0,07 basmış, ama 8,30'u veren değer ~0,0684. 26,25 katsayısı bu yuvarlamayı 0,041'e büyütüyor; katsayıların kendisi doğru.

### 🔍 Açık — doğrulanabilir, henüz doğrulanmadı

47 anahtar. Kaynak formülü yayımlamış ama o formülün uygulandığı bir sayısal örnek vermemiş. Nicel dilbilimde bu olağandır: Yule (1944) K'yı tanımlar, bir romanda K'nın kaç çıktığını basmaz. Bu satırlar **test edilmiyor demek değildir** — formül ve sınır durumları kendi test dosyalarında sınanıyor; burada takip edilen yalnız *kaynağın sayısıyla* karşılaştırma.

| Anahtar | Kaynak | Durum |
|---|---|---|
| `yule_k` | Yule (1944) p.53, eq. (3.22) | 🔍 |
| `simpson_d` | Simpson (1949), as cited in Bestgen (2023) | 🔍 |
| `brunet_w` | Brunet (1978), as cited in Tweedie & Baayen (1998) p.328, eq. (10) | 🔍 |
| `mattr` | Covington & McFall (2010); default window 50 — C&M recommend a window of 500; 50 is used here so that texts of 100+ words can be measured (mattr needs 2 × window) | 🔍 |
| `herdan_c` | Herdan (1960/1964), as cited in Tweedie & Baayen (1998) p.327, eq. (5) | 🔍 |
| `dugast_u` | Dugast (1978), as cited in Malvern et al. (2004) eq. 2.7 | 🔍 |
| `guiraud_r` | Guiraud (1954) p.53, alternative form (all word types), as cited in Daller (2010); his actual law is V/√(2N), content words only | 🔍 |
| `cttr` | Carroll (1964), as cited in Torruella & Capsada (2013) p.448 | 🔍 |
| `summer_s` | Somers (1966), as cited in Torruella & Capsada (2013) p.448, where it is named "Summer"; the source gives no logarithm base, the natural logarithm is this library's choice | 🔍 |
| `maas_a2` | Maas (1972), as cited in Tweedie & Baayen (1998) p.327, eq. (7); natural logarithm, which reproduces the values in Torruella & Capsada (2013) Table 1; all logarithms in this library are natural | 🔍 |
| `herdan_vm` | Herdan (1955), as cited in Tweedie & Baayen (1998) p.330, eq. (18) | 🔍 |
| `heaps_beta` | Heaps (1978), as cited in Manning et al. (2008) §5.1.1 | 🔍 |
| `sichel_s` | Sichel (1975); formula from Malvern et al. (2004) eq. 3.10 | 🔍 |
| `noun_variation` | Lu (2012) Table 2 | 🔍 |
| `verb_variation` | Lu (2012) Table 2 | 🔍 |
| `adj_variation` | Lu (2012) Table 2 | 🔍 |
| `adv_variation` | Lu (2012) Table 2 | 🔍 |
| `zipf_exponent` | Piantadosi (2014) eq. (2); the same source criticises estimating r and f(r) from the same corpus | 🔍 |
| `zipf_r2` | Piantadosi (2014) eq. (2); the same source criticises estimating r and f(r) from the same corpus | 🔍 |
| `zipf_mandelbrot_q` | Piantadosi (2014) eq. (2); the same source criticises estimating r and f(r) from the same corpus | 🔍 |
| `zipf_mandelbrot_s` | Piantadosi (2014) eq. (2); the same source criticises estimating r and f(r) from the same corpus | 🔍 |
| `wordfreq_mean` | van Heuven et al. (2014) (Zipf scale) | 🔍 |
| `wordfreq_rare_ratio` | van Heuven et al. (2014) Table 1 (Zipf ≤ 3 = low frequency) | 🔍 |
| `vocd_d` | Malvern et al. (2004) pp.56–57; procedure from McCarthy & Jarvis (2010) p.383 | 🔍 |
| `hdd` | McCarthy & Jarvis (2007), as cited in McCarthy & Jarvis (2010) p.383 | 🔍 |
| `msttr` | Johnson (1944), as cited in Malvern et al. (2004) p.25 and McCarthy & Jarvis (2010) p.385 | 🔍 |
| `thematic_concentration` | QUITA §6.2.5 | 🔍 |
| `secondary_thematic_concentration` | QUITA §6.2.6 | 🔍 |
| `verb_dist_mean` | QUITA §6.2.1 | 🔍 |
| `verb_dist_cv` | QUITA §6.2.1 | 🔍 |
| `lexical_density` | Lu (2012); definition in the broad Hallidayan sense — all open-class words | 🔍 |
| `pos_dist_std` | Deutsch, Jasbi & Shieber (2020) Definition 3.3 (POSDdev); computed over ratios, 12 UD tags | 🔍 |
| `pos_kl_div` | Deutsch, Jasbi & Shieber (2020) Definition 3.4 (POSdiv); natural logarithm (nats), the source uses bits | 🔍 |
| `suffix_bigram_entropy` | Shannon (1948) — the entropy formula; Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | 🔍 |
| `front_vowel_ratio` | Göksel & Kerslake (2005) ch. 2 (the vowel system, front/back) | 🔍 |
| `back_vowel_ratio` | Göksel & Kerslake (2005) ch. 2 (the vowel system, front/back) | 🔍 |
| `harmony_fronting_ratio` | Göksel & Kerslake (2005) §3.1 (fronting harmony); exceptions §3.4 — the measure counts them as disharmonic | 🔍 |
| `harmony_rounding_ratio` | Göksel & Kerslake (2005) §3.1 (rounding harmony); strictly a suffix phenomenon, measured here as a whole-word pattern | 🔍 |
| `syllable_mean` | Flesch (1948) Formula A, wl; unit there = syllables per 100 words, here per word | 🔍 |
| `syllable_1_ratio` | Bezirci & Yılmaz (2010) Table 1-c | 🔍 |
| `syllable_2_ratio` | Bezirci & Yılmaz (2010) Table 1-c | 🔍 |
| `syllable_3_ratio` | Bezirci & Yılmaz (2010) Table 1-c | 🔍 |
| `syllable_4_ratio` | Bezirci & Yılmaz (2010) Table 1-c | 🔍 |
| `syllable_5_ratio` | Bezirci & Yılmaz (2010) Table 1-c | 🔍 |
| `syllable_6plus_ratio` | Bezirci & Yılmaz (2010) Table 1-c | 🔍 |
| `lix` | Björnsson (1968), as cited in Anderson (1983) p.490; long word = 7+ letters | 🔍 |
| `long_word_ratio` | Anderson (1983); long word = 7+ letters | 🔍 |

### Doğrulama adayı olmayanlar

141 anahtar. ⚪ olanlar saf tanım (`punc_,_ratio`, `char_a`) — adlandırılmış bir literatür ölçüsü değil. ⚫ olanlar bir ölçü değil, dış bir etiket şemasının kategorisini sayıyor; şema kategori tanımlar, ölçüm yayımlamaz. 🔧 olanların formülü bir kaynaktan gelir ama uygulaması bu kütüphaneye aittir. Üçünde de aranacak bir sayı yok.

| Anahtar | Kaynak | Durum |
|---|---|---|
| `n_lemma_count` | — | ⚪ |
| `avg_word_length` | — | ⚪ |
| `word_length_cv` | — | ⚪ |
| `hapax_ratio` | — | ⚪ |
| `entropy_std` | Shannon (1948) — the entropy formula; the standard deviation across segments is this library's own derivation | 🔧 |
| `avg_sent_len_word` | — | ⚪ |
| `sentence_length_cv` | — | ⚪ |
| `sent_len_skewness` | — | ⚪ |
| `med_sent_len` | — | ⚪ |
| `avg_sent_len_char` | — | ⚪ |
| `short_sent_ratio` | This library's threshold calibration (docs/threshold-calibration.md); TR 4, EN 8 — 15th percentile of newspaper columns under the default sentence and word rules. Note: the TR value coincides with Ateşman (1997) p.74, where the easiest text has a mean sentence length of 4 words; that is a text mean, not a threshold, so it is not the source. Calibrated on newspaper columns only | 🔧 |
| `long_sent_ratio` | This library's threshold calibration (docs/threshold-calibration.md); TR 17, EN 32 — 85th percentile of newspaper columns under the default sentence and word rules. Ateşman's 30 was not used: that is the mean of the hardest text, not a single-sentence threshold (in Turkish newspaper columns 30 words is above the 95th percentile, so as a threshold it would almost never fire). Calibrated on newspaper columns only | 🔧 |
| `sent_len_entropy` | Shannon (1948) — the entropy formula; applying it to the distribution of sentence lengths is this library's own decision | 🔧 |
| `para_len_mean` | — | ⚪ |
| `para_len_cv` | — | ⚪ |
| `sents_per_para_mean` | — | ⚪ |
| `sents_per_para_cv` | — | ⚪ |
| `para_count_norm` | — | ⚪ |
| `pos_noun` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_propn` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_verb` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_adj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_adv` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_det` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_adp` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_intj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_cconj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_sconj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_num` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_aux` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `question_per_sent` | — | ⚪ |
| `pronoun_freq` | — | ⚪ |
| `nominal_verbal_ratio` | — | ⚪ |
| `sentfinal_noun` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_propn` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_verb` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_adj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_adv` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_det` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_adp` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_intj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_cconj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_sconj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_num` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_aux` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_pron` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_other` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `surface_per_lemma` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_tense_past` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_tense_pres` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_tense_fut` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_aspect_perf` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_aspect_imp` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_aspect_prog` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_case_nom` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_case_acc` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_case_dat` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_case_loc` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_case_abl` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_case_gen` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_person_1` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_person_2` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_person_3` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_number_sing` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_number_plur` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_voice_pass` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `agglutination_depth` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `suffix_char_length_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `suffix_chain_cv` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `derivational_suffix_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `tense_past_def` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `tense_past_nar` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `tense_present` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `tense_future` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `modal_possibility_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `modal_necessity_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `negation_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `passive_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `plural_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `case_acc_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `case_dat_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `case_loc_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `case_abl_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `case_gen_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `case_ins_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `conditional_suffix_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `causative_suffix_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `question_particle_ratio` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `verb_suffix_diversity` | Zeyrek (a Python port of Zemberek's morphotactics); tag set from Akın & Akın (2007) | ⚫ |
| `vowel_ratio` | — | ⚪ |
| `syllable_cv` | — | ⚪ |
| `sentence_syllable_mean` | — | ⚪ |
| `sentence_syllable_cv` | — | ⚪ |
| `digit_vs_all` | — | ⚪ |
| `punc_,_ratio` | — | ⚪ |
| `punc_._ratio` | — | ⚪ |
| `punc_;_ratio` | — | ⚪ |
| `punc_!_ratio` | — | ⚪ |
| `punc_:_ratio` | — | ⚪ |
| `punc_-_ratio` | — | ⚪ |
| `punc_ellipsis_ratio` | — | ⚪ |
| `punc_paren_ratio` | — | ⚪ |
| `punc_quote_ratio` | — | ⚪ |
| `punc_question_ratio` | — | ⚪ |
| `punc_total_ratio` | — | ⚪ |
| `punct_density` | — | ⚪ |
| `punct_entropy` | Shannon (1948) — the entropy formula; applying it to the distribution of punctuation types is this library's own decision | 🔧 |
| `consecutive_punct_ratio` | — | ⚪ |
| `whitespace_ratio` | — | ⚪ |
| `punct_variety` | — | ⚪ |
| `uppercase_ratio` | — | ⚪ |
| `all_caps_word_ratio` | — | ⚪ |
| `char_a` | — | ⚪ |
| `char_b` | — | ⚪ |
| `char_c` | — | ⚪ |
| `char_ç` | — | ⚪ |
| `char_d` | — | ⚪ |
| `char_e` | — | ⚪ |
| `char_f` | — | ⚪ |
| `char_g` | — | ⚪ |
| `char_ğ` | — | ⚪ |
| `char_h` | — | ⚪ |
| `char_ı` | — | ⚪ |
| `char_i` | — | ⚪ |
| `char_j` | — | ⚪ |
| `char_k` | — | ⚪ |
| `char_l` | — | ⚪ |
| `char_m` | — | ⚪ |
| `char_n` | — | ⚪ |
| `char_o` | — | ⚪ |
| `char_ö` | — | ⚪ |
| `char_p` | — | ⚪ |
| `char_r` | — | ⚪ |
| `char_s` | — | ⚪ |
| `char_ş` | — | ⚪ |
| `char_t` | — | ⚪ |
| `char_u` | — | ⚪ |
| `char_ü` | — | ⚪ |
| `char_v` | — | ⚪ |
| `char_y` | — | ⚪ |
| `char_z` | — | ⚪ |

## İngilizce — 183 anahtar, 200 satır

Bir anahtarın birden çok kaynak örneği olabilir; her biri ayrı satır.

**Doğrulama adayı — 84 satır**

| Durum | Satır sayısı |
|---|---|
| ✅ birebir | 35 |
| 🟡 belgelenmiş sapma | 3 |
| 🔍 açık — kaynakta sayısal örnek yok | 46 |


**Doğrulama adayı olmayan — 116 satır.** Bunlarda aranacak yayımlanmış bir sayı yoktur.

| Durum | Satır sayısı |
|---|---|
| ⚪ kaynak yok — saf tanım | 65 |
| ⚫ etiket şeması — ölçü değil | 45 |
| 🔧 türev — uygulaması bu kütüphaneye ait | 6 |

### Sayısal karşılaştırması olanlar

| Anahtar | Kaynak | Örnek | Kanıt | Beklenen | Bizim | Fark | Durum |
|---|---|---|---|---|---|---|---|
| `entropy` | QUITA §6.1.12 | Text 1 · eq. (6.26); kaynak bit ile 6,438043 → × ln 2 | formül | 4.463 | 4.463 | +0.000 | ✅ |
| `entropy` | QUITA §6.1.12 | Text 2 · eq. (6.26); kaynak bit ile 6,395099 → × ln 2 | formül | 4.433 | 4.433 | +0.000 | ✅ |
| `ttr` | QUITA §6.1.1 | Text 1 · V/N = 119/179 | formül | 0.665 | 0.665 | -0.000 | ✅ |
| `ttr` | QUITA §6.1.1 | Text 2 · V/N = 121/202 = 0.599; kaynak 0.590 basmış (baskı hatası) | formül | 0.590 | 0.599 | +0.009 | 🟡 |
| `hapax_percentage` | QUITA §6.1.6 | Text 1 · 98/179 | formül | 0.547 | 0.547 | +0.000 | ✅ |
| `hapax_percentage` | QUITA §6.1.6 | Text 2 · 92/202 | formül | 0.455 | 0.455 | +0.000 | ✅ |
| `mtld` | McCarthy & Jarvis (2010) p.385 | kısmi faktör · TTR .887 → 40.4% | formül | 0.404 | 0.404 | +0.000 | ✅ |
| `h_point` | QUITA §6.1.2 | Text 1 · sıra 5 = sıklık 5 | formül | 5.000 | 5.000 | +0.000 | ✅ |
| `h_point` | QUITA §6.1.2 | Text 2 · ara değerleme, eq. (6.2) | formül | 4.750 | 4.750 | +0.000 | ✅ |
| `vocab_richness_r1` | QUITA §6.1.3 | Text 1 · N=179, h=5 | formül | 0.835 | 0.835 | -0.000 | ✅ |
| `vocab_richness_r1` | QUITA §6.1.3 | Text 2 · N=202, h=4.75 → ⌊h⌋=4 | formül | 0.838 | 0.838 | +0.000 | ✅ |
| `vocab_richness_r4` | QUITA §6.1.9 | Text 1 · 1−G | formül | 0.696 | 0.696 | +0.000 | ✅ |
| `vocab_richness_r4` | QUITA §6.1.9 | Text 2 · 1−G | formül | 0.649 | 0.649 | -0.000 | ✅ |
| `repeat_rate` | QUITA §6.1.4 | Text 1 · N=179 | formül | 0.020 | 0.020 | -0.000 | ✅ |
| `repeat_rate` | QUITA §6.1.4 | Text 2 · N=202 | formül | 0.021 | 0.021 | -0.000 | ✅ |
| `rr_mcintosh` | QUITA §6.1.5 | Text 1 · V=119 | formül | 0.946 | 0.946 | +0.000 | ✅ |
| `rr_mcintosh` | QUITA §6.1.5 | Text 2 · V=121 | formül | 0.939 | 0.939 | -0.000 | ✅ |
| `gini_coef` | QUITA §6.1.8 | Text 1 · m₁=41.88268156 | formül | 0.304 | 0.304 | -0.000 | ✅ |
| `gini_coef` | QUITA §6.1.8 | Text 2 · m₁=39.75742574 | formül | 0.351 | 0.351 | +0.000 | ✅ |
| `curve_length` | QUITA §6.1.10 | Text 1 · eq. (6.21) | formül | 129.356 | 129.356 | +0.000 | ✅ |
| `curve_length` | QUITA §6.1.10 | Text 2 · eq. (6.21) | formül | 134.279 | 134.279 | +0.000 | ✅ |
| `curve_length_r` | QUITA §6.1.11 | Text 1 · Lh=14.29145 | formül | 0.889 | 0.890 | +0.000 | ✅ |
| `curve_length_r` | QUITA §6.1.11 | Text 2 · Lh=18.03607 | formül | 0.866 | 0.866 | -0.000 | ✅ |
| `lambda_pa` | QUITA §6.1.7 | Text 1 · L·ln N/N, L=129.3559482; kaynak log₁₀ ile 1,628 → × ln 10 | formül | 3.749 | 3.749 | +0.000 | ✅ |
| `lambda_pa` | QUITA §6.1.7 | Text 2 · L·ln N/N, L=134.2787065; kaynak log₁₀ ile 1,5325 → × ln 10 | formül | 3.529 | 3.529 | -0.000 | ✅ |
| `adjusted_modulus` | QUITA §6.1.13 | Text 1 · M=24.01416249; kaynak log₁₀ ile 10,6594 → / ln 10 | formül | 4.629 | 4.629 | -0.000 | ✅ |
| `adjusted_modulus` | QUITA §6.1.13 | Text 2 · M=25.81931678; kaynak log₁₀ ile 11,19973 → / ln 10 | formül | 4.864 | 4.864 | +0.000 | ✅ |
| `writers_view_alpha` | QUITA §6.2.3 | Text 1 · arccos(−0.374487816) | formül | 1.955 | 1.955 | -0.000 | ✅ |
| `writers_view_alpha` | QUITA §6.2.3 | Text 2 · arccos(−0.269972586) | formül | 1.844 | 1.844 | +0.000 | ✅ |
| `activity_ratio` | QUITA §6.2.2 | Text 1 · 26 fiil / 14 sıfat | formül | 0.650 | 0.650 | +0.000 | ✅ |
| `activity_ratio` | QUITA §6.2.2 | Text 2 · 35 fiil / 8 sıfat | formül | 0.814 | 0.814 | -0.000 | ✅ |
| `arc_len_mean` | Jing & Liu (2015) p.164 | Figure 3 · 'Mr. Nixon was to…' | formül | 1.167 | 1.167 | +0.000 | ✅ |
| `arc_len_mean` | Liu (2008) eq. (1) | 'I actually live in Beijing' · 5/4 | formül | 1.250 | 1.250 | +0.000 | ✅ |
| `parse_depth_mean` | Jing & Liu (2015) p.164 | Figure 3 · MHD = 12/6 | formül | 2.000 | 2.000 | +0.000 | ✅ |
| `ari` | Kincaid et al. (1975) p.8, Table 1 | Appendix A · 18 passages, mean | uçtan uca | 12.300 | 11.763 | -0.537 | 🟡 |
| `coleman_liau` | Coleman & Liau (1975) p.284 | iki denklemin bileşimi · 13 kelime, 2 cümle | formül | 7.704 | 7.705 | +0.000 | ✅ |
| `coleman_liau` | Coleman & Liau (1975) p.284, Table 1 | cloze 40.4% → 12. sınıf | formül | 12.000 | 11.994 | -0.006 | ✅ |
| `flesch_kincaid_grade` | Kincaid et al. (1975) p.12, Table 2 | Appendix A · 18 passages, mean | uçtan uca | 10.700 | 10.326 | -0.374 | 🟡 |

**`ttr` sapması:** Kaynağın kendi sayıları (V=121, N=202) 121/202 = 0,599 verir; basılan 0,590 bu aritmetikle tutmuyor (baskı hatası). Bizim değer aritmetiğe uyuyor; fark yayımlanan değerin %1,5'i.

**`ari` sapması:** Kaynağın sayıları 1975'te daktiloya takılı mekanik bir sayaçla **elle** üretildi (Ek B, ARI talimatı). 18 pasajın 17'sinde, kaynağın ARI'sını verecek vuruş sayısı bizim saydığımızın 0,996-1,041 katı — yani birkaç karakterlik fark. Pasaj 2 aykırı (oran 1,145) ve kaynağın kendi iki sayısı orada çelişiyor: Tablo 1'in ARI 20,3'ü vuruş/kelime 6,269 gerektiriyor, metnin gerçek değeri 5,475; üstelik o ARI'nın ima ettiği kelime/cümle FKGL'yi 18,69 yapıyor, oysa Tablo 2 16,7 basmış. Bizim vuruş tanımımız ayrıca sınandı: boşluğu sayıma katmak farkı 0,54'ten 4,24'e çıkarıyor, yani boşluksuz sayım doğru.

**`flesch_kincaid_grade` sapması:** Aynı elle sayım kaynağı. Pasaj başına sapma 18'in 15'inde 0,6'nın altında; pasaj 12 aykırı (-4,28) ve o pasaj FRE bandını da tutturmuyor, yani sapma tek bir pasajda yoğunlaşıyor. Ortalamalar arasındaki fark 0,34 sınıf düzeyi — okunabilirlik sınıflandırmasını değiştirmeyecek kadar küçük.

### 🔍 Açık — doğrulanabilir, henüz doğrulanmadı

46 anahtar. Kaynak formülü yayımlamış ama o formülün uygulandığı bir sayısal örnek vermemiş. Nicel dilbilimde bu olağandır: Yule (1944) K'yı tanımlar, bir romanda K'nın kaç çıktığını basmaz. Bu satırlar **test edilmiyor demek değildir** — formül ve sınır durumları kendi test dosyalarında sınanıyor; burada takip edilen yalnız *kaynağın sayısıyla* karşılaştırma.

| Anahtar | Kaynak | Durum |
|---|---|---|
| `yule_k` | Yule (1944) p.53, eq. (3.22) | 🔍 |
| `simpson_d` | Simpson (1949), as cited in Bestgen (2023) | 🔍 |
| `brunet_w` | Brunet (1978), as cited in Tweedie & Baayen (1998) p.328, eq. (10) | 🔍 |
| `mattr` | Covington & McFall (2010); default window 50 — C&M recommend a window of 500; 50 is used here so that texts of 100+ words can be measured (mattr needs 2 × window) | 🔍 |
| `herdan_c` | Herdan (1960/1964), as cited in Tweedie & Baayen (1998) p.327, eq. (5) | 🔍 |
| `dugast_u` | Dugast (1978), as cited in Malvern et al. (2004) eq. 2.7 | 🔍 |
| `guiraud_r` | Guiraud (1954) p.53, alternative form (all word types), as cited in Daller (2010); his actual law is V/√(2N), content words only | 🔍 |
| `cttr` | Carroll (1964), as cited in Torruella & Capsada (2013) p.448 | 🔍 |
| `summer_s` | Somers (1966), as cited in Torruella & Capsada (2013) p.448, where it is named "Summer"; the source gives no logarithm base, the natural logarithm is this library's choice | 🔍 |
| `maas_a2` | Maas (1972), as cited in Tweedie & Baayen (1998) p.327, eq. (7); natural logarithm, which reproduces the values in Torruella & Capsada (2013) Table 1; all logarithms in this library are natural | 🔍 |
| `herdan_vm` | Herdan (1955), as cited in Tweedie & Baayen (1998) p.330, eq. (18) | 🔍 |
| `heaps_beta` | Heaps (1978), as cited in Manning et al. (2008) §5.1.1 | 🔍 |
| `sichel_s` | Sichel (1975); formula from Malvern et al. (2004) eq. 3.10 | 🔍 |
| `noun_variation` | Lu (2012) Table 2 | 🔍 |
| `verb_variation` | Lu (2012) Table 2 | 🔍 |
| `adj_variation` | Lu (2012) Table 2 | 🔍 |
| `adv_variation` | Lu (2012) Table 2 | 🔍 |
| `zipf_exponent` | Piantadosi (2014) eq. (2); the same source criticises estimating r and f(r) from the same corpus | 🔍 |
| `zipf_r2` | Piantadosi (2014) eq. (2); the same source criticises estimating r and f(r) from the same corpus | 🔍 |
| `zipf_mandelbrot_q` | Piantadosi (2014) eq. (2); the same source criticises estimating r and f(r) from the same corpus | 🔍 |
| `zipf_mandelbrot_s` | Piantadosi (2014) eq. (2); the same source criticises estimating r and f(r) from the same corpus | 🔍 |
| `wordfreq_mean` | van Heuven et al. (2014) (Zipf scale) | 🔍 |
| `wordfreq_rare_ratio` | van Heuven et al. (2014) Table 1 (Zipf ≤ 3 = low frequency) | 🔍 |
| `vocd_d` | Malvern et al. (2004) pp.56–57; procedure from McCarthy & Jarvis (2010) p.383 | 🔍 |
| `hdd` | McCarthy & Jarvis (2007), as cited in McCarthy & Jarvis (2010) p.383 | 🔍 |
| `msttr` | Johnson (1944), as cited in Malvern et al. (2004) p.25 and McCarthy & Jarvis (2010) p.385 | 🔍 |
| `thematic_concentration` | QUITA §6.2.5 | 🔍 |
| `secondary_thematic_concentration` | QUITA §6.2.6 | 🔍 |
| `verb_dist_mean` | QUITA §6.2.1 | 🔍 |
| `verb_dist_cv` | QUITA §6.2.1 | 🔍 |
| `lexical_density` | Lu (2012); definition in the broad Hallidayan sense — all open-class words | 🔍 |
| `pos_dist_std` | Deutsch, Jasbi & Shieber (2020) Definition 3.3 (POSDdev); computed over ratios, 12 UD tags | 🔍 |
| `pos_kl_div` | Deutsch, Jasbi & Shieber (2020) Definition 3.4 (POSdiv); natural logarithm (nats), the source uses bits | 🔍 |
| `front_vowel_ratio` | Göksel & Kerslake (2005) ch. 2 (the vowel system, front/back) | 🔍 |
| `back_vowel_ratio` | Göksel & Kerslake (2005) ch. 2 (the vowel system, front/back) | 🔍 |
| `syllable_mean` | Flesch (1948) Formula A, wl; unit there = syllables per 100 words, here per word | 🔍 |
| `syllable_1_ratio` | Bezirci & Yılmaz (2010) Table 1-c | 🔍 |
| `syllable_2_ratio` | Bezirci & Yılmaz (2010) Table 1-c | 🔍 |
| `syllable_3_ratio` | Bezirci & Yılmaz (2010) Table 1-c | 🔍 |
| `syllable_4_ratio` | Bezirci & Yılmaz (2010) Table 1-c | 🔍 |
| `syllable_5_ratio` | Bezirci & Yılmaz (2010) Table 1-c | 🔍 |
| `syllable_6plus_ratio` | Bezirci & Yılmaz (2010) Table 1-c | 🔍 |
| `lix` | Björnsson (1968), as cited in Anderson (1983) p.490; long word = 7+ letters | 🔍 |
| `long_word_ratio` | Anderson (1983); long word = 7+ letters | 🔍 |
| `flesch_reading_ease` | Flesch (1948) Formula A; coefficient .846, unit = syllables per 100 words | 🔍 |
| `smog` | McLaughlin (1969) p.643, Table 1, eq. (d); p = polysyllabic words in a 30-sentence sample | 🔍 |

### Doğrulama adayı olmayanlar

116 anahtar. ⚪ olanlar saf tanım (`punc_,_ratio`, `char_a`) — adlandırılmış bir literatür ölçüsü değil. ⚫ olanlar bir ölçü değil, dış bir etiket şemasının kategorisini sayıyor; şema kategori tanımlar, ölçüm yayımlamaz. 🔧 olanların formülü bir kaynaktan gelir ama uygulaması bu kütüphaneye aittir. Üçünde de aranacak bir sayı yok.

| Anahtar | Kaynak | Durum |
|---|---|---|
| `n_lemma_count` | — | ⚪ |
| `avg_word_length` | — | ⚪ |
| `word_length_cv` | — | ⚪ |
| `hapax_ratio` | — | ⚪ |
| `entropy_std` | Shannon (1948) — the entropy formula; the standard deviation across segments is this library's own derivation | 🔧 |
| `avg_sent_len_word` | — | ⚪ |
| `sentence_length_cv` | — | ⚪ |
| `sent_len_skewness` | — | ⚪ |
| `med_sent_len` | — | ⚪ |
| `avg_sent_len_char` | — | ⚪ |
| `short_sent_ratio` | This library's threshold calibration (docs/threshold-calibration.md); TR 4, EN 8 — 15th percentile of newspaper columns under the default sentence and word rules. Note: the TR value coincides with Ateşman (1997) p.74, where the easiest text has a mean sentence length of 4 words; that is a text mean, not a threshold, so it is not the source. Calibrated on newspaper columns only | 🔧 |
| `long_sent_ratio` | This library's threshold calibration (docs/threshold-calibration.md); TR 17, EN 32 — 85th percentile of newspaper columns under the default sentence and word rules. Ateşman's 30 was not used: that is the mean of the hardest text, not a single-sentence threshold (in Turkish newspaper columns 30 words is above the 95th percentile, so as a threshold it would almost never fire). Calibrated on newspaper columns only | 🔧 |
| `sent_len_entropy` | Shannon (1948) — the entropy formula; applying it to the distribution of sentence lengths is this library's own decision | 🔧 |
| `para_len_mean` | — | ⚪ |
| `para_len_cv` | — | ⚪ |
| `sents_per_para_mean` | — | ⚪ |
| `sents_per_para_cv` | — | ⚪ |
| `para_count_norm` | — | ⚪ |
| `pos_noun` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_propn` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_verb` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_adj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_adv` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_det` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_adp` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_intj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_cconj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_sconj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_num` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `pos_aux` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `question_per_sent` | — | ⚪ |
| `pronoun_freq` | — | ⚪ |
| `nominal_verbal_ratio` | — | ⚪ |
| `sentfinal_noun` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_propn` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_verb` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_adj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_adv` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_det` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_adp` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_intj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_cconj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_sconj` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_num` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_aux` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_pron` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `sentfinal_other` | de Marneffe et al. (2021) Table 1 (UPOS tag set) | ⚫ |
| `surface_per_lemma` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_tense_past` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_tense_pres` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_tense_fut` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_aspect_perf` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_aspect_imp` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_aspect_prog` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_case_nom` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_case_acc` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_case_dat` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_case_loc` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_case_abl` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_case_gen` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_person_1` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_person_2` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_person_3` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_number_sing` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_number_plur` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `morph_voice_pass` | de Marneffe et al. (2021) Table 2 (universal morphological features) | ⚫ |
| `vowel_ratio` | — | ⚪ |
| `syllable_cv` | — | ⚪ |
| `sentence_syllable_mean` | — | ⚪ |
| `sentence_syllable_cv` | — | ⚪ |
| `polysyllabic_word_ratio` | McLaughlin (1969) p.641; polysyllabic = 3+ syllables — the ratio form of SMOG's input, not the source's own measure | 🔧 |
| `digit_vs_all` | — | ⚪ |
| `punc_,_ratio` | — | ⚪ |
| `punc_._ratio` | — | ⚪ |
| `punc_;_ratio` | — | ⚪ |
| `punc_!_ratio` | — | ⚪ |
| `punc_:_ratio` | — | ⚪ |
| `punc_-_ratio` | — | ⚪ |
| `punc_ellipsis_ratio` | — | ⚪ |
| `punc_paren_ratio` | — | ⚪ |
| `punc_quote_ratio` | — | ⚪ |
| `punc_question_ratio` | — | ⚪ |
| `punc_total_ratio` | — | ⚪ |
| `punct_density` | — | ⚪ |
| `punct_entropy` | Shannon (1948) — the entropy formula; applying it to the distribution of punctuation types is this library's own decision | 🔧 |
| `consecutive_punct_ratio` | — | ⚪ |
| `whitespace_ratio` | — | ⚪ |
| `punct_variety` | — | ⚪ |
| `uppercase_ratio` | — | ⚪ |
| `all_caps_word_ratio` | — | ⚪ |
| `char_a` | — | ⚪ |
| `char_b` | — | ⚪ |
| `char_c` | — | ⚪ |
| `char_d` | — | ⚪ |
| `char_e` | — | ⚪ |
| `char_f` | — | ⚪ |
| `char_g` | — | ⚪ |
| `char_h` | — | ⚪ |
| `char_i` | — | ⚪ |
| `char_j` | — | ⚪ |
| `char_k` | — | ⚪ |
| `char_l` | — | ⚪ |
| `char_m` | — | ⚪ |
| `char_n` | — | ⚪ |
| `char_o` | — | ⚪ |
| `char_p` | — | ⚪ |
| `char_q` | — | ⚪ |
| `char_r` | — | ⚪ |
| `char_s` | — | ⚪ |
| `char_t` | — | ⚪ |
| `char_u` | — | ⚪ |
| `char_v` | — | ⚪ |
| `char_w` | — | ⚪ |
| `char_x` | — | ⚪ |
| `char_y` | — | ⚪ |
| `char_z` | — | ⚪ |

## Heceleme — 10/10

Heceleme sekiz `syllable_*` anahtarını ve üç Türkçe okunabilirlik formülünü birden besliyor. Aşağıdaki karşılaştırma **sayıyı değil bölütlemeyi** sınıyor: yanlış yerden bölünmüş bir kelime doğru sayıda hece verebilir, sayı karşılaştırması onu yakalamaz.

Kaynak: TDK, "Hece Yapısı ve Satır Sonunda Kelimelerin Bölünmesi" (tdk.gov.tr, 2019).

| Kelime | TDK | Bizim | Durum |
|---|---|---|---|
| aldı | `al-dı` | `al-dı` | ✅ |
| altlık | `alt-lık` | `alt-lık` | ✅ |
| türkçe | `türk-çe` | `türk-çe` | ✅ |
| program | `prog-ram` | `prog-ram` | ✅ |
| kontrol | `kont-rol` | `kont-rol` | ✅ |
| santral | `sant-ral` | `sant-ral` | ✅ |
| saat | `sa-at` | `sa-at` | ✅ |
| karaosmanoğlu | `ka-ra-os-ma-noğ-lu` | `ka-ra-os-ma-noğ-lu` | ✅ |
| tren | `tren` | `tren` | ✅ |
| strateji | `stra-te-ji` | `stra-te-ji` | ✅ |

## Ek — Kincaid Ek A, pasaj bazında

Ana tablodaki iki 🟡 satırın (`ari`, `flesch_kincaid_grade`) dayandığı 18 karşılaştırma. Ara değerler (vuruş, kelime) burada duruyor ki fark çıktığında hangi girdiden geldiği görülebilsin.

**FRE bandı** sütunu ayrı bir kontrol: Tablo 1'in Flesch sütunu 0-100 puanı değil, Flesch'in kendi sınıf bandını basıyor (`8-9` = FRE 60-70 gibi). Bizim FRE'miz bandın içine düşüyor mu, ona bakıyor.

Pasaj metinleri `tests/veri/kincaid/`, ölçüm `scripts/kincaid_olcum.py`.

| # | Vuruş | Kelime | ARI kaynak | ARI bizim | Fark | FKGL kaynak | FKGL bizim | Fark | FRE bandı |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 663 | 148 | 10.6 | 10.24 | -0.36 | 9.7 | 9.64 | -0.06 | 8-9 ✅ |
| 2 | 668 | 122 | 20.3 | 16.56 | -3.74 | 16.7 | 15.79 | -0.91 | 16+ ✅ |
| 3 | 684 | 127 | 13.3 | 13.01 | -0.29 | 12.7 | 12.67 | -0.03 | 13-16 ✅ |
| 4 | 749 | 155 | 8.8 | 8.38 | -0.42 | 8.2 | 8.18 | -0.02 | 8-9 ✅ |
| 5 | 517 | 104 | 9.5 | 9.41 | -0.09 | 7.1 | 5.94 | -1.16 | 8-9 ❌ |
| 6 | 685 | 133 | 12.4 | 12.33 | -0.07 | 12.3 | 12.05 | -0.25 | 13-16 ✅ |
| 7 | 1017 | 197 | 12.7 | 12.74 | +0.04 | 11.7 | 11.96 | +0.26 | 13-16 ✅ |
| 8 | 1061 | 197 | 16.4 | 16.25 | -0.15 | 14.7 | 14.98 | +0.28 | 13-16 ✅ |
| 9 | 837 | 181 | 9.7 | 9.40 | -0.30 | 8.0 | 8.16 | +0.16 | 7 ❌ |
| 10 | 1177 | 231 | 13.1 | 12.19 | -0.91 | 11.7 | 11.18 | -0.52 | 13-16 ✅ |
| 11 | 822 | 170 | 7.8 | 7.88 | +0.08 | 8.1 | 7.77 | -0.33 | 8-9 ✅ |
| 12 | 997 | 214 | 16.7 | 15.80 | -0.90 | 11.8 | 7.52 | -4.28 | 10-12 ❌ |
| 13 | 894 | 183 | 13.4 | 13.02 | -0.38 | 10.0 | 10.01 | +0.01 | 10-12 ✅ |
| 14 | 681 | 137 | 12.0 | 11.77 | -0.23 | 12.5 | 12.11 | -0.39 | 13-16 ✅ |
| 15 | 985 | 217 | 9.7 | 8.99 | -0.71 | 8.4 | 8.16 | -0.24 | 8-9 ✅ |
| 16 | 882 | 163 | 13.5 | 13.11 | -0.39 | 13.8 | 14.13 | +0.33 | 16+ ✅ |
| 17 | 1240 | 240 | 10.4 | 9.96 | -0.44 | 9.3 | 8.83 | -0.47 | 10-12 ✅ |
| 18 | 782 | 144 | 10.9 | 10.69 | -0.21 | 6.6 | 6.81 | +0.21 | — |

ARI ortalama mutlak fark **0.54**, en büyük **3.74** (pasaj 2). FKGL ortalama mutlak fark **0.55**, en büyük **4.28** (pasaj 12). FRE bandının içinde: **14/17**.
