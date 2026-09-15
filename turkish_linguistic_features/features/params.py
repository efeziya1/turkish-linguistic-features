"""Öznitelik hesaplamalarının paylaştığı ayarlar.

Eşikler ve pencere boyutları fonksiyonların içine gömülmüyor; hepsi burada
tek bir dondurulmuş nesnede duruyor. Böylece iki fonksiyon kazara farklı
değer kullanamıyor ve kullanıcı istediğinde tek yerden değiştirebiliyor.

İçerik `API-SOZLESMESI.md` §2.3'te dondurulmuş — değiştirmeden önce oraya bak.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FeatureParams:
    """Öznitelik fonksiyonlarının eşikleri ve pencere boyutları."""

    # sözcüksel zenginlik
    mattr_window: int = 50
    mtld_threshold: float = 0.72
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
    # cümle uzunluğu dağılımı
    short_sent_threshold: int = 5
    long_sent_threshold: int = 30
    # metin içi kayma
    drift_window_size: int = 200
    drift_stride: int = 100
    drift_n_words: int = 100
    # bağımlılık ayrıştırma
    max_parse_depth: int = 20
    arc_len_bins: int = 10


# Türkçe cümleler İngilizce'den kısa — aynı eşik iki dile uymuyor.
DEFAULT_PARAMS = FeatureParams()
DEFAULT_PARAMS_TR = FeatureParams(short_sent_threshold=4, long_sent_threshold=18)
DEFAULT_PARAMS_EN = FeatureParams(short_sent_threshold=7, long_sent_threshold=39)
DEFAULT_PARAMS_BY_LANG: dict[str, FeatureParams] = {
    "tr": DEFAULT_PARAMS_TR,
    "en": DEFAULT_PARAMS_EN,
}
