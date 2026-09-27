# İki sürümü karşılaştır

Aynı metnin iki hâlini ölçmek — düzenleme öncesi/sonrası, çeviri/asıl,
taslak/son — kütüphanenin en doğrudan kullanımıdır. Karşılaştırma adildir
çünkü **aynı metin**, aynı boru hattından iki kez geçer.

## Yöntem

```python
import turkish_linguistic_features as tlf

once  = tlf.analyze(once_metin, lang="tr")
sonra = tlf.analyze(sonra_metin, lang="tr")

for k in ("avg_sent_len_word", "atesman", "syllable_mean"):
    print(f"{k:22s} {once[k]:10.4f} {sonra[k]:10.4f} {sonra[k]-once[k]:+10.4f}")
```

## Gerçek bir örnek

Akademik bir paragrafın ağır hâli ve sadeleştirilmiş hâli:

=== "Önce (36 kelime)"

    > Çalışmanın amacı, Türkçe metinlerin okunabilirlik düzeylerinin
    > belirlenmesinde kullanılan formüllerin karşılaştırmalı olarak
    > değerlendirilmesi ve bu formüllerin birbirleriyle olan uyumluluk
    > derecelerinin ortaya konulmasıdır. Bu bağlamda, alanyazında yer alan ve
    > yaygın biçimde kullanılmakta olan üç farklı formül ele alınmıştır.

=== "Sonra (20 kelime)"

    > Bu çalışma Türkçe okunabilirlik formüllerini karşılaştırır. Amaç,
    > formüllerin birbiriyle ne kadar uyuştuğunu göstermektir. Alanyazında
    > yaygın olan üç formül ele alındı.

Ölçüm:

```text
anahtar                      önce      sonra       fark
avg_sent_len_word         18.0000     6.6667   -11.3333
avg_word_length            8.0278     7.2500    -0.7778
syllable_mean              3.3611     3.0500    -0.3111
atesman                   16.8124    58.8913   +42.0789
cetinkaya_uzun            13.9998    33.0893   +19.0895
ttr                        0.8889     1.0000    +0.1111
long_word_ratio            0.5278     0.4500    -0.0778
```

Okunuşu:

- **Cümle uzunluğu 18 → 6,7 kelime.** Asıl değişiklik bu; bir uzun cümle
  üçe bölündü.
- **Ateşman 16,8 → 58,9.** 0–100 ölçeğinde 16,8 "çok zor", 58,9 "orta".
  42 puanlık sıçramanın çoğu cümle uzunluğundan geliyor, çünkü formülde
  sözcük/cümle terimi var.
- **Hece ortalaması 3,36 → 3,05.** "değerlendirilmesi" gibi uzun türetmeler
  gitti.
- **`ttr` 0,89 → 1,00 ama bu anlamlı değil.** İkinci metin kısaldığı için
  TTR yükseldi; üslup değişikliğinin değil uzunluğun sonucu. Bu tam olarak
  TTR'nin neden tek başına okunmaması gerektiğinin örneğidir.

## Neye dikkat edin

!!! warning "Uzunluk değiştiyse sözcüksel zenginliğe bakmayın"

    Düzenleme metni kısaltmışsa `ttr`, `hapax_ratio`, `yule_k` gibi
    öznitelikler **uzunluk yüzünden** değişir. Bu ölçülerde gerçek bir
    karşılaştırma istiyorsanız iki metni aynı boya getirin:

    ```python
    p1 = tlf.segment_text(once_metin,  size=500, lang="tr")[0]
    p2 = tlf.segment_text(sonra_metin, size=500, lang="tr")[0]
    ```

    Uzunluktan bağımsız tasarlanmış ölçüler `mattr`, `mtld` ve `vocd_d`'dir
    — ama onlar da en az 100 kelime ister.

Cümle uzunluğu, hece ortalaması, kelime uzunluğu ve okunabilirlik
formülleri uzunluktan görece bağımsızdır; kısa metinlerde bile
karşılaştırılabilirler.

## Birden çok çifti karşılaştırmak

Elinizde çok sayıda çift varsa tablo hâline getirin:

```python
import turkish_linguistic_features as tlf

satirlar = []
for ad, once_m, sonra_m in ciftler:
    for etiket, metin in (("once", once_m), ("sonra", sonra_m)):
        satirlar.append({"label": etiket, "source": ad, "segment_id": 0,
                         **tlf.analyze(metin, lang="tr")})

tlf.save_csv(satirlar, "oncesi-sonrasi.csv")
```

`label` sütunu `once`/`sonra` olduğu için CSV doğrudan eşleştirilmiş bir
analize girer.
