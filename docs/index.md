# turkish-linguistic-features

Türkçe metinden **202**, İngilizce metinden **175 nicel dilbilimsel öznitelik**
çıkarır. Her özniteliğin formülü yazılıdır; Türkçedeki 202 özniteliğin 191'i,
İngilizcedeki 175 özniteliğin 164'ü literatürde bir kaynağa dayanır, geri
kalanı saf tanımdır (örneğin tirenin noktalama işaretleri içindeki payı).
[Doğrulama raporu](dogrulama-raporu.md), hangilerinin kaynağın yayımladığı bir
sayıyla karşılaştırıldığını gösterir.

Extracts 202 quantitative linguistic features from Turkish text and 175 from
English. Every feature has its formula written out; 191 of the Turkish features
and 164 of the English ones cite a source in the literature, and the rest are
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

    202 özniteliğin tam listesi ve genel API (İngilizce).

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
| Öznitelik | 202 | 175 |
| Künyesi olan öznitelik | 191 | 164 |
| Künyesi olmayan, saf tanım | 11 | 11 |
| Doğrulama adayı rapor satırı | 145 | 131 |
| — kaynağın sayısıyla tolerans içinde tutan (✅) | 46 | 35 |
| — tolerans dışında, nedeni açıklanmış (🟡) | 2 | 3 |

Kaynakçada 56 eser var (iki dil için tek kaynakça).

Künye, formülün kaynağını sayfa ve denklem numarasıyla verir. Doğrulama
raporu ayrıca, kaynağın yayımladığı bir sayıyla karşılaştırılabilen satırları
listeler. İkisinin farkı ve raporun nasıl okunacağı:
[Doğrulama sistemi](tr/aciklama/dogrulama.md) ·
[The verification system](en/explanation/verification.md).
