"""Kütüphaneye özgü hata tipleri.

Neden ayrı tipler? Kullanıcı `except LinguisticFeaturesError` yazarak bu
kütüphanenin hatalarını yakalayabilsin, ama `except ImportError` yazan
mevcut kodu da kırmayalım — bu yüzden çoklu miras kullanıyoruz.

🔴 **Hata metinleri İngilizcedir** (2026-09-24, Efe) — uyarılarla aynı kural,
bkz. `_warnings.py`. Kod içi yorum ve docstring Türkçe kalıyor; `raise` içine
yazılan metin İngilizce. Kapsam yalnız bu dosyadaki tipler değil: paket
içindeki bütün `raise` çağrıları (25 metin, 11 dosya) ve `show_progress=True`
çıktısı. Yeni bir hata eklerken metnini İngilizce yaz.
"""


class LinguisticFeaturesError(Exception):
    """Bu kütüphanenin ürettiği tüm hataların ortak atası."""


# `MissingDependencyError` 2026-10-08'de kaldırıldı (Efe): hiç fırlatılmıyordu. İsteğe bağlı
# paket eksikse `MissingDependencyWarning` + `nan`; zorunlu paket eksikse Python'un kendi
# `ModuleNotFoundError`'ı; dil verisi eksikse `ModelNotFoundError`.


class ModelNotFoundError(LinguisticFeaturesError, OSError):
    """Gereken dil verisi kurulu değil: spaCy modeli ya da (İngilizce hece için)
    NLTK ``cmudict``. İkisi de kullanıcının bir kez kurduğu, kütüphanenin
    kendiliğinden indirmediği veri; mesaj kurulum komutunu içerir."""
