"""Hızlı başlangıç — tek metin.

Bir metnin özniteliklerini çıkarır, ``describe_feature()`` ile tek bir gruba
süzüp hizalanmış tablo basar, sonra seçilen anahtarların formülünü yazdırır.

Çalıştırma::

    python examples/01_hizli_baslangic.py
"""

import turkish_linguistic_features as tlf

# Ayarlar en üstte, tek yerde.
METIN = (
    "Kütüphane bir metni sayılara çevirir. Sayılar metnin ne kadar çeşitli bir "
    "söz varlığı kullandığını, cümlelerinin ne kadar uzun olduğunu ve hangi "
    "sözcük türlerinin ne sıklıkla geçtiğini betimler. Yorum okuyucuya kalır; "
    "kütüphane ölçer, karar vermez. Bu kısa paragraf örnek olsun diye burada "
    "duruyor ve kendi metninizle değiştirilebilir. Metni değiştirdiğinizde "
    "tablodaki bütün sayılar da değişir, çünkü her sayı yalnız bu metinden "
    "hesaplanır. Bazı öznitelikler asgari uzunluk ister; metin kısa kalırsa "
    "onlar ölçülemez ve NaN döner."
)
DIL = "tr"
GRUP = "pos"                       # tabloya basılacak öznitelik grubu
FORMULU_YAZILACAK = ("ttr", "mattr", "avg_sent_len_word", "lexical_density",
                     "harmony_fronting_ratio")


def main() -> None:
    print(f"Metin çözümleniyor ({len(METIN)} karakter)...")
    oznitelikler = tlf.analyze(METIN, lang=DIL)
    print(f"{len(oznitelikler)} öznitelik çıkarıldı.")

    # 1. Gruba göre süzme — grup bilgisi registry'den, describe_feature ile gelir.
    anahtarlar = [k for k in oznitelikler
                  if tlf.describe_feature(k)["group"] == GRUP]
    etiket = tlf.describe_feature(anahtarlar[0])["group_label"]
    print(f"\n-- {GRUP} - {etiket} " + "-" * 20)
    for anahtar in anahtarlar:
        print(f"{anahtar:<30} {oznitelikler[anahtar]:>10.4f}")

    # 2. Bir sayının nasıl hesaplandığı da registry'de yazılı.
    print("\n-- Seçilen özniteliklerin formülü " + "-" * 20)
    for anahtar in FORMULU_YAZILACAK:
        if anahtar not in oznitelikler:
            # Şema dile göre değişir (K11); olmayan anahtarı sessizce atlamak
            # yerine söylüyoruz — sessiz atlama yazım hatasını gizler.
            print(f"{anahtar:<30} {'(bu dilin şemasında yok)':>10}")
            continue
        bilgi = tlf.describe_feature(anahtar)
        print(f"{anahtar:<30} {oznitelikler[anahtar]:>10.4f}   {bilgi['formula']}")
        print(f"{'':<30} {'':>10}   ölçek: {bilgi['scale']}")


if __name__ == "__main__":
    main()
