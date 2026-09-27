# turkish-linguistic-features

Türkçe ve İngilizce metinlerden **208 nicel dilbilimsel öznitelik** çıkarır.
Her öznitelik bir literatür kaynağına bağlıdır ve o kaynağın yayımladığı
sayıyla karşılaştırılmıştır.

Extracts **208 quantitative linguistic features** from Turkish and English
text. Every feature is tied to a source in the literature and compared
against the number that source published.

```python
import turkish_linguistic_features as tlf

oz = tlf.analyze("Dil, insanın düşüncesini taşıyan en eski araçtır.", lang="tr")
oz["avg_word_length"]     # 5.7667
oz["atesman"]             # 70.9483  (Ateşman 1997 okunabilirlik)
```

---

## Dokümantasyon · Documentation

<div class="grid cards" markdown>

- **[Türkçe →](tr/index.md)**

    Kurulum, öğretici, kullanım senaryoları, kavramlar ve sınırlılıklar.

- **[English →](en/index.md)**

    Installation, tutorial, how-to guides, concepts and limitations.

- **[Başvuru · Reference →](reference/index.md)**

    208 özniteliğin tam listesi ve genel API. Bu bölüm İngilizcedir —
    kaynağı registry'dir. *This section is in English.*

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
| Öznitelik (İngilizce) | 182 |
| Kaynağa bağlı öznitelik | 141 |
| Kaynakçadaki eser | 45 |
| Doğrulama adayı satır | 92 |
| — kaynağın sayısıyla birebir tutan (✅) | 45 |
| — farkı ölçülmüş ve açıklanmış (🟡) | 3 |

**Formüller ile doğrulama iki ayrı şeydir.** 208 özniteliğin **hepsinin**
formülü kaynağındaki denklemle karşılaştırılıp yazıldı; künye sayfa ve
denklem numarası verir, testler sınır durumlarını sınar. Bunun üstüne bir
katman daha var: kaynağın *yayımladığı bir sayıyı* alıp bizim çıktımızla
karşılaştırmak. O ikinci katman her öznitelikte mümkün değil — 141 satır
saf tanım (`char_a`), bir etiket şemasının kategorisi (`pos_noun`) ya da bu
kütüphanenin kendi türevi (`entropy_std`), yani aranacak bir literatür sayısı
yok. Kalan 92 adayın 44'ü de kaynağı formülü yayımlamış ama uygulanmış bir
örnek basmamış olduğu için açık duruyor.

Açık bir satır, formülünün yanlış olduğu anlamına **gelmez**; karşılaştırılacak
yayımlanmış bir sayı bulunamadığı anlamına gelir.
Ayrıntı: [doğrulama raporu](dogrulama-raporu.md).
