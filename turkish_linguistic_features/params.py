"""Öznitelik hesaplamalarının paylaştığı ayarlar.

Eşikler ve pencere boyutları fonksiyonların içine gömülmüyor; hepsi burada
tek bir dondurulmuş nesnede duruyor. Böylece iki fonksiyon kazara farklı
değer kullanamıyor ve kullanıcı istediğinde tek yerden değiştirebiliyor.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FeatureParams:
    """Öznitelik fonksiyonlarının eşikleri ve pencere boyutları."""

    # sözcüksel zenginlik
    mattr_window: int = 50
    mtld_threshold: float = 0.72
    mtld_min_tokens: int = 100       # McCarthy & Jarvis 2010 s. 384
    hdd_sample_size: int = 42
    msttr_segment_size: int = 100
    vocd_sample_min: int = 35        # McCarthy & Jarvis (2010) s. 383 · Kademe A
    vocd_sample_max: int = 50
    vocd_num_samples: int = 100      # her boy için çekiliş · s. 383
    vocd_num_runs: int = 3           # tüm işlem 3 tur, D ortalanır · s. 383
    vocd_min_tokens: int = 50
    vocd_random_seed: int = 42
    heaps_min_tokens: int = 300
    heaps_step: int = 50
    ttr_slope_chunk_size: int = 50   # ayrık parça boyu (2026-09-15, Efe)
    # Brunet's W üs sabiti. Kademe C — Tweedie & Baayen (1998),
    # Computers and the Humanities 32(5):323-352, denklem (10).
    # Bazı ikincil kaynaklar 0.165 veriyor; tartışmalı olduğu için
    # gizlenmiyor, buradan değiştirilebiliyor.
    brunet_w_a: float = 0.172
    # biçimbilim — verb_suffix_diversity parça boyu, fiil sayısı (2026-09-17, Efe)
    verb_suffix_window: int = 50
    # Cümle uzunluğu dağılımı. `None` = "dile göre çözümle" (2026-09-24, Efe).
    # Why sentinel: eskiden bu iki alan 5 ve 30 diye sabit yazıyordu ve dile
    # özgü değerler ayrı bir `FeatureParams` nesnesinde tutuluyordu. O düzende
    # `FeatureParams(mattr_window=100)` yazan kullanıcı, dokunmadığı iki cümle
    # eşiğini de kalibre edilmemiş 5/30'a düşürüyordu — ölçüldü ve sessizdi.
    # Sentinel bunu kapatıyor: verilmeyen alan `SENT_THRESHOLDS_BY_LANG`'dan,
    # verilen alan kullanıcıdan gelir. 5/30 diye bir varsayılan artık yok.
    short_sent_threshold: int | None = None
    long_sent_threshold: int | None = None
    # bağımlılık ayrıştırma
    max_parse_depth: int = 20


DEFAULT_PARAMS = FeatureParams()

# Türkçe cümleler İngilizce'den kısa — aynı eşik iki dile uymuyor. Değerler
# gazete köşe yazılarında, varsayılan cümle kuralı ve varsayılan kelime birimiyle ölçülen cümle
# uzunluğu dağılımının 15. ve 85. yüzdeliğinden türetildi (2026-10-06; TR: 162 yazar / 4.321 yazı /
# 197.990 cümle, EN: 30 yazar / 1.485 yazı / 52.745 cümle). Yöntem ve ham yüzdelik tablosu:
# `docs/esik-kalibrasyonu.md`.
SENT_THRESHOLDS_BY_LANG: dict[str, tuple[int, int]] = {
    "tr": (4, 17),
    "en": (8, 32),
}

# Yalnız `SENT_THRESHOLDS_BY_LANG`'da olmayan bir dil için. `analyze()` dili
# {"tr", "en"} ile sınırladığı için bugün ulaşılamaz; yeni bir dil eklenirse
# devreye girecek nötr yedek. Kalibre edilmiş bir değer **değildir** ve
# kullanıcıya varsayılan olarak gösterilmez.
_KALIBRESIZ_ESIKLER = (5, 30)


def resolve_sent_thresholds(params: FeatureParams, lang: str) -> tuple[int, int]:
    """``(short_sent_threshold, long_sent_threshold)`` çiftini çözümler.

    Alan alan çözümlenir: kullanıcının verdiği sayı kazanır, vermediği alan
    ``lang`` için kalibre edilmiş değerde kalır. Yani ilgisiz bir alan
    değiştirmek (``FeatureParams(mattr_window=100)``) cümle eşiklerinin
    kalibrasyonunu bozmaz.

    Parameters
    ----------
    params
        Kullanıcının nesnesi ya da ``DEFAULT_PARAMS``.
    lang
        ``"tr"`` ya da ``"en"``. Tanınmayan dil nötr yedeğe düşer.

    Returns
    -------
    tuple[int, int]
        Kısa ve uzun cümle eşiği, ikisi de ``int``.
    """
    kisa_kalibre, uzun_kalibre = SENT_THRESHOLDS_BY_LANG.get(lang, _KALIBRESIZ_ESIKLER)
    kisa = kisa_kalibre if params.short_sent_threshold is None else params.short_sent_threshold
    uzun = uzun_kalibre if params.long_sent_threshold is None else params.long_sent_threshold
    return kisa, uzun
