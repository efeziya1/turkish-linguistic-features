# turkish-linguistic-features

Türkçe metinden **208**, İngilizce metinden **180 nicel dilbilimsel öznitelik**
çıkarır. Her özniteliğin formülü yazılıdır; Türkçedeki 208 özniteliğin 141'i,
İngilizcedeki 180 özniteliğin 116'sı literatürde bir kaynağa dayanır, geri
kalanı saf tanımdır (örneğin bir harfin metindeki payı).
[Doğrulama raporu](dogrulama-raporu.md), hangilerinin kaynağın yayımladığı bir
sayıyla karşılaştırıldığını gösterir.

Extracts 208 quantitative linguistic features from Turkish text and 180 from
English. Every feature has its formula written out; 141 of the Turkish features
and 116 of the English ones cite a source in the literature, and the rest are
plain definitions (such as a letter's share of the text). The
[verification report](verification-report.md) shows which ones have been
checked against a number their source published.

```python
import turkish_linguistic_features as tlf

oz = tlf.analyze("Dil, insanın düşüncesini taşıyan en eski araçtır.", lang="tr")
oz["avg_word_length"]     # 5.8571
oz["atesman"]             # 77.2479  (Ateşman 1997 okunabilirlik)
```

---

## Dokümantasyon · Documentation

<div class="grid cards" markdown>

- **[Türkçe →](tr/index.md)**

    Kurulum, öğretici, kullanım senaryoları, kavramlar ve sınırlılıklar.

- **[English →](en/index.md)**

    Installation, tutorial, how-to guides, concepts and limitations.

- **[Başvuru · Reference →](reference/index.md)**

    208 özniteliğin tam listesi ve genel API (İngilizce).

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
| Öznitelik | 208 | 180 |
| Künyesi olan öznitelik | 141 | 116 |
| Künyesi olmayan, saf tanım | 67 | 64 |
| Doğrulama adayı rapor satırı | 92 | 81 |
| — kaynağın sayısıyla tolerans içinde tutan (✅) | 47 | 36 |
| — tolerans dışında, nedeni açıklanmış (🟡) | 1 | 2 |

Kaynakçada 45 eser var (iki dil için tek kaynakça).

**Formüller ile doğrulama iki ayrı şeydir.** 208 özniteliğin hepsinin
formülü yazılıdır ve testlerle sınanır. Künyesi olan 141 özniteliğin formülü
kaynağına dayanır; künye sayfa ve denklem numarası verir. Kalan 67'si saf
tanımdır (`char_a`, `punc_,_ratio`), bir kaynağı yoktur.

İkinci katman, kaynağın *yayımladığı bir sayıyı* alıp bizim çıktımızla
karşılaştırmaktır. Bu her öznitelikte mümkün değil. Doğrulama raporunda
141 **satır** aday değildir: saf tanım (`char_a`), bir etiket şemasının
kategorisi (`pos_noun`) ya da bu kütüphanenin kendi türevi (`entropy_std`);
aranacak bir literatür sayısı yoktur. (Yukarıdaki 141 künyeli **öznitelik**
ile aynı sayı olması rastlantıdır; ikisi farklı şeyleri sayar.) Kalan 92
aday satırın 48'i kaynağın sayısıyla karşılaştırıldı; 44'ünde kaynak
formülü yayımlamış ama uygulanmış bir örnek basmamış, bu yüzden açık
duruyor.

Açık bir satır, formülünün yanlış olduğu anlamına **gelmez**; karşılaştırılacak
yayımlanmış bir sayı bulunamadığı anlamına gelir.
Ayrıntı: [doğrulama raporu](dogrulama-raporu.md).
