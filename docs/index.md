# turkish-linguistic-features

Türkçe metinden **217**, İngilizce metinden **187 nicel dilbilimsel öznitelik**
çıkarır. Her özniteliğin formülü yazılıdır; Türkçedeki 217 özniteliğin 206'sı,
İngilizcedeki 187 özniteliğin 176'sı alanyazında bir kaynağa dayanır, geri
kalanı yalın tanımdır (örneğin tirenin noktalama işaretleri içindeki payı).
[Doğrulama raporu](dogrulama-raporu.md), hangilerinin kaynağın yayımladığı bir
sayıyla karşılaştırıldığını gösterir.

Extracts 217 quantitative linguistic features from Turkish text and 187 from
English. Every feature has its formula written out; 206 of the Turkish features
and 176 of the English ones cite a source in the literature, and the rest are
plain definitions (such as the dash's share of punctuation marks). The
[verification report](verification-report.md) shows which ones have been
checked against a number their source published.

```python
import turkish_linguistic_features as tlf

oz = tlf.analyze("Renksiz yeşil fikirler öfkeyle uyur.", lang="tr")
oz["word_len_mean"]   # 6.2
oz["atesman"]         # 89.355  (Ateşman 1997 okunabilirlik)
```

---

## Belgeler · Documentation

<div class="grid cards" markdown>

- **[Türkçe →](tr/index.md)**

    Kurulum, öğretici, kullanım senaryoları, kavramlar ve sınırlılıklar.

- **[English →](en/index.md)**

    Installation, tutorial, how-to guides, concepts and limitations.

- **[Başvuru · Reference →](reference/index.md)**

    217 özniteliğin tam listesi ve Python'dan çağrılan adlar (İngilizce).

- **[Doğrulama · Verification →](dogrulama-raporu.md)**

    Hangi özniteliğin kaynağında yayımlanmış bir örnekle karşılaştırıldığı ve sonucu.
    [English version](verification-report.md).

</div>

---

## Bu araç ne yapmaz

- **Anlam çıkarmaz.** Duygu, konu, niyet ölçmez. Ölçtüğü şey biçimdir:
  uzunluk, çeşitlilik, dağılım, yapı.
- **Yazar tanıma yapmaz.** Yazar tanımaya *girdi* üretir, kararı vermez.
- **Türkçe ve İngilizce dışında çalışmaz.** `lang` yalnız `"tr"` ve `"en"`
  alır.

## Sayılar

| | Türkçe (TR) | İngilizce (EN) |
|---|---:|---:|
| Öznitelik | 217 | 187 |
| Künyesi olan öznitelik | 206 | 176 |
| Künyesi olmayan, yalın tanım | 11 | 11 |
| Yayımlanmış bir örnekle sınanan öznitelik | 22 | 22 |
| — örtüşen (✅) | 22 | 20 |
| — tolerans dışında, nedeni açıklanmış (🟡) | 0 | 2 |
| Yayımlanmış örnek bulunamadığı için sınanamayan öznitelik (🔍) | 114 | 104 |

Bir öznitelik, mümkün olduğunda birden çok yayımlanmış örnekle sınanmıştır.

Kaynakçada 58 eser var (iki dil için tek kaynakça).

Künye, formülün kaynağını sayfa ve formül numarasıyla verir. Doğrulama
raporu ise aracın sonucunu, kaynağın aynı girdi için yayımladığı sonuçla karşılaştırır. İkisinin farkı ve raporun nasıl okunacağı:
[Doğrulama sistemi](tr/aciklama/dogrulama.md) ·
[The verification system](en/explanation/verification.md).
