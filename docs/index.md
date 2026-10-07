# turkish-linguistic-features

Türkçe metinden **198**, İngilizce metinden **171 nicel dilbilimsel öznitelik**
çıkarır. Her özniteliğin formülü yazılıdır; Türkçedeki 198 özniteliğin 187'si,
İngilizcedeki 171 özniteliğin 160'ı literatürde bir kaynağa dayanır, geri
kalanı saf tanımdır (örneğin tirenin noktalama işaretleri içindeki payı).
[Doğrulama raporu](dogrulama-raporu.md), hangilerinin kaynağın yayımladığı bir
sayıyla karşılaştırıldığını gösterir.

Extracts 198 quantitative linguistic features from Turkish text and 171 from
English. Every feature has its formula written out; 187 of the Turkish features
and 160 of the English ones cite a source in the literature, and the rest are
plain definitions (such as the dash's share of punctuation marks). The
[verification report](verification-report.md) shows which ones have been
checked against a number their source published.

```python
import turkish_linguistic_features as tlf

oz = tlf.analyze("Dil, insanın düşüncesini taşıyan en eski araçtır.", lang="tr")
oz["word_len_mean"]   # 5.8571
oz["atesman"]         # 77.2479  (Ateşman 1997 okunabilirlik)
```

---

## Dokümantasyon · Documentation

<div class="grid cards" markdown>

- **[Türkçe →](tr/index.md)**

    Kurulum, öğretici, kullanım senaryoları, kavramlar ve sınırlılıklar.

- **[English →](en/index.md)**

    Installation, tutorial, how-to guides, concepts and limitations.

- **[Başvuru · Reference →](reference/index.md)**

    198 özniteliğin tam listesi ve genel API (İngilizce).

- **[Doğrulama · Verification →](dogrulama-raporu.md)**

    Hangi özniteliğin kaynağıyla birebir tuttuğu, hangisinin tutmadığı.
    [English version](verification-report.md).

</div>

---

## Bu kütüphane ne yapmaz

- **Anlam çıkarmaz.** Duygu, konu, niyet ölçmez. Ölçtüğü şey biçimdir:
  uzunluk, çeşitlilik, dağılım, yapı.
- **Yazar tanıma yapmaz.** Yazar tanımaya *girdi* üretir, kararı vermez.
- **Türkçe ve İngilizce dışında çalışmaz.** `lang` yalnız `"tr"` ve `"en"`
  alır.

## Sayılar

| | Türkçe (TR) | İngilizce (EN) |
|---|---:|---:|
| Öznitelik | 198 | 171 |
| Künyesi olan öznitelik | 187 | 160 |
| Künyesi olmayan, saf tanım | 11 | 11 |
| Doğrulama adayı rapor satırı | 141 | 127 |
| — kaynağın sayısıyla tolerans içinde tutan (✅) | 46 | 35 |
| — tolerans dışında, nedeni açıklanmış (🟡) | 2 | 3 |

Kaynakçada 56 eser var (iki dil için tek kaynakça).

**Formüller ile doğrulama iki ayrı şeydir.** 198 özniteliğin hepsinin
formülü yazılıdır ve testlerle sınanır. Künyesi olan 187 özniteliğin formülü
kaynağına dayanır; künye sayfa ve denklem numarası verir. Kalan 11'i saf
tanımdır (`uppercase_ratio`, `punct_dash_ratio`), bir kaynağı yoktur.

İkinci katman, kaynağın *yayımladığı bir sayıyı* alıp bizim çıktımızla
karşılaştırmaktır. Bu her öznitelikte mümkün değil. Doğrulama raporunda
82 **satır** aday değildir: saf tanım (`uppercase_ratio`), bir etiket şemasının
kategorisi (`pos_noun_ratio`) ya da bu kütüphanenin kendi türevi (`sent_len_entropy`);
aranacak bir literatür sayısı yoktur. Kalan 141
aday satırın 48'i kaynağın sayısıyla karşılaştırıldı; 93'ünde kaynak
formülü yayımlamış ama uygulanmış bir örnek basmamış, bu yüzden açık
duruyor.

Açık bir satır, formülünün yanlış olduğu anlamına **gelmez**; karşılaştırılacak
yayımlanmış bir sayı bulunamadığı anlamına gelir.
Ayrıntı: [doğrulama raporu](dogrulama-raporu.md).
