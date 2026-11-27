# İki sürümü karşılaştır

Aynı metnin iki hâlini ölçmek — düzenleme öncesi/sonrası, çeviri/asıl,
taslak/son — aracın en doğrudan kullanımıdır. Karşılaştırma adildir, çünkü iki hâl de
aynı çözümleme hattından (İng. *pipeline*) aynı ayarlarla geçer.

## Yöntem

```python
import turkish_linguistic_features as tlf

once  = tlf.analyze(once_metin, lang="tr")
sonra = tlf.analyze(sonra_metin, lang="tr")

print(once["atesman"], sonra["atesman"])
```

```text
16.8124 58.8913
```

Bir özniteliğin iki değeri adıyla alınıp yan yana konur.

## Gerçek bir örnek

Akademik bir paragrafın ağır hâli ve sadeleştirilmiş hâli:

=== "Önce (36 sözcük)"

    > Çalışmanın amacı, Türkçe metinlerin okunabilirlik düzeylerinin
    > belirlenmesinde kullanılan formüllerin karşılaştırmalı olarak
    > değerlendirilmesi ve bu formüllerin birbirleriyle olan uyumluluk
    > derecelerinin ortaya konulmasıdır. Bu bağlamda, alanyazında yer alan ve
    > yaygın biçimde kullanılmakta olan üç farklı formül ele alınmıştır.

=== "Sonra (20 sözcük)"

    > Bu çalışma Türkçe okunabilirlik formüllerini karşılaştırır. Amaç,
    > formüllerin birbiriyle ne kadar uyuştuğunu göstermektir. Alanyazında
    > yaygın olan üç formül ele alındı.

Birkaç özniteliğin iki hâldeki değeri:

| Öznitelik | Önce | Sonra |
|---|---:|---:|
| `sent_len_mean` | 18,00 | 6,67 |
| `word_len_mean` | 8,03 | 7,25 |
| `syllable_mean` | 3,36 | 3,05 |
| `atesman` | 16,81 | 58,89 |
| `cetinkaya_uzun` | 14,00 | 33,09 |
| `ttr` | 0,89 | 1,00 |
| `long_word_ratio` | 0,53 | 0,45 |

Okunuşu:

- **Ortalama tümce uzunluğu 18 → 6,7 sözcük.** Asıl değişiklik bu; iki uzun tümce
  üç kısa tümceye bölündü.
- **Ateşman 16,8 → 58,9.** Ateşman'ın bantlarına göre 16,8 "çok zor", 58,9 "orta".
  42 puanlık sıçramanın çoğu tümce uzunluğundan geliyor, çünkü formülde
  sözcük/tümce terimi var.
- **Seslem (İng. *syllable*) ortalaması 3,36 → 3,05.** "değerlendirilmesi" gibi uzun türetmeler
  gitti.
- **`ttr` (tür/türce oranı, İng. *type-token ratio*) 0,89 → 1,00 ama bu anlamlı değildir.** İkinci metin kısaldığı için
  TTR yükseldi; üslup değişikliğinin değil uzunluğun sonucudur.

## Birden çok çifti karşılaştırmak

Çok sayıda çift varsa iki hâl iki klasöre konur; bir çiftin iki dosyası aynı adı taşır:

```text
ciftler/
  once/
    metin1.txt
    metin2.txt
  sonra/
    metin1.txt
    metin2.txt
```

```python
satirlar = tlf.analyze_corpus("ciftler/", lang="tr")
tlf.save_csv(satirlar, "oncesi-sonrasi.csv")
```

Tabloda `label` sütunu `once` ya da `sonra`, `source` sütunu dosya adıdır; aynı `source`
taşıyan iki satır bir çifttir. Klasör düzeni: [Derlemi CSV'ye çıkar](korpus.md).
