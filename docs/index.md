# turkish-linguistic-features

Türkçe metinden **208**, İngilizce metinden **180 nicel dilbilimsel öznitelik**
çıkarır. Her özniteliğin formülü yazılıdır; Türkçedeki 208 özniteliğin 141'i
literatürde bir kaynağa dayanır, geri kalanı saf tanımdır. Bir kısmı da
kaynağın yayımladığı sayıyla karşılaştırılmıştır.

Extracts **208 quantitative linguistic features** from Turkish text and **180**
from English. Every feature has its formula written out; 141 of the 208
Turkish features rest on a source in the literature, the rest are plain
definitions. Some have also been checked against the number their source
published.

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

| | |
|---|---|
| Öznitelik (Türkçe) | 208 |
| Öznitelik (İngilizce) | 180 |
| Künyesi olan öznitelik (Türkçe) | 141 |
| Künyesi olmayan, saf tanım (Türkçe) | 67 |
| Kaynakçadaki eser | 45 |
| Doğrulama adayı rapor satırı (Türkçe) | 92 |
| — kaynağın sayısıyla tolerans içinde tutan (✅) | 47 |
| — tolerans dışında, nedeni açıklanmış (🟡) | 1 |

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
