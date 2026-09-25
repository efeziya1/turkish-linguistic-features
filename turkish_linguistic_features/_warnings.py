"""'Çök' yerine 'uyar ve devam et' davranışının uyarı türleri.

İki durum var: eksik opsiyonel bağımlılık (``MissingDependencyWarning``) ve
girdinin bir özniteliği anlamsız kılması (``ParagraphStructureWarning``).
Ortak kural: bir öznitelik girdinin bir eksiği yüzünden bilgi taşımayan bir
sayı dönüyorsa **bu sessiz kalmaz**.
"""

from __future__ import annotations

import warnings


class MissingDependencyWarning(UserWarning):
    """Bir öznitelik grubu atlandı ama işlem devam etti."""


class ParagraphStructureWarning(UserWarning):
    """Metinde paragraf sınırı bulunamadı; ``para_*`` metin düzeyi sayı."""


# Sadece OPSİYONEL paketler burada. numpy, spaCy, zeyrek ve textstat
# zorunlu (K1) — onlar eksikse paket zaten kurulamamış demektir, ipucu
# vermenin anlamı yok. 2026-08-25'te zeyrek ve textstat bu tablodan çıktı.
_KURULUM_KOMUTU: dict[str, str] = {
    "pandas": "pip install 'turkish-linguistic-features[pandas]'",
    "wordfreq": "pip install 'turkish-linguistic-features[lexical_freq]'",
}


def kurulum_ipucu(paket: str) -> str:
    """Paket için kurulum komutunu döndürür."""
    return _KURULUM_KOMUTU.get(paket, f"pip install {paket}")


def uyar_eksik_bagimlilik(paket: str, atlanan: str) -> None:
    """Eksik paket yüzünden bir özellik atlandığında uyarı verir.

    Parameters
    ----------
    paket : str
        Eksik olan paketin adı, örn. ``"wordfreq"``.
    atlanan : str
        Atlanan özelliğin/grubun adı, örn. ``"wordfreq_* (2 öznitelik)"``.

    Notes
    -----
    2026-08-25'ten sonra tek çağrı yeri ``wordfreq``. Kural: bir opsiyonel
    paket eksikliği yüzünden bir öznitelik ``0.0`` dönüyorsa **bu uyarı
    verilmek zorunda**. Sessizce sıfıra düşen öznitelik bırakılmaz.
    """
    warnings.warn(
        f"{atlanan} atlandı: '{paket}' kurulu değil. "
        f"Kurmak için: {kurulum_ipucu(paket)}",
        MissingDependencyWarning,
        stacklevel=3,
    )


def uyar_paragraf_yok(cumle_sayisi: int, kelime_sayisi: int) -> None:
    """Uzun bir metinde hiç paragraf sınırı yokken verilen uyarı.

    Parameters
    ----------
    cumle_sayisi : int
        Tek paragraf sayılan metindeki cümle sayısı.
    kelime_sayisi : int
        Aynı metnin kelime sayısı — ``para_len_mean``'in döndüğü sayının
        kendisi. İkisi birlikte "gerçekten tek paragraf mı?" sorusunu
        kullanıcının kendi verisi üzerinden cevaplatıyor.

    Notes
    -----
    Ölçüldü (2026-09-24): PDF/EPUB'dan çıkarılmış Türkçe roman derlemelerinde
    163 dosyanın **120'sinde** hiç boş satır yok; bir dosyanın tamamı tek
    satır (191.806 karakter, 7.347 cümle). O dosyalarda ``para_len_mean``
    bütün kitabın kelime sayısına eşitleniyor — makul görünen, ama bilgi
    taşımayan bir sayı.

    Değer değiştirilmiyor (2026-09-24, Efe: yalnız uyarı, sayılar kalır);
    yalnız görünür kılınıyor. Eşik ``syntactic._PARA_UYARI_KELIME``.
    """
    warnings.warn(
        f"No paragraph boundary found: the text contains no blank line, so all "
        f"{kelime_sayisi} words and {cumle_sayisi} sentences were counted as a "
        f"single paragraph. `para_len_mean` and `para_count_norm` are therefore "
        f"text-level rather than paragraph-level numbers, and `para_len_cv` and "
        f"`sents_per_para_cv` return NaN. Paragraph boundaries are marked by "
        f"blank lines; text extracted from PDF or EPUB may have lost its line "
        f"breaks.",
        ParagraphStructureWarning,
        stacklevel=3,
    )
