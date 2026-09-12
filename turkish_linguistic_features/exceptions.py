"""Kütüphaneye özgü hata tipleri.

Neden ayrı tipler? Kullanıcı `except LinguisticFeaturesError` yazarak bu
kütüphanenin hatalarını yakalayabilsin, ama `except ImportError` yazan
mevcut kodu da kırmayalım — bu yüzden çoklu miras kullanıyoruz.
"""


class LinguisticFeaturesError(Exception):
    """Bu kütüphanenin ürettiği tüm hataların ortak atası."""


class MissingDependencyError(LinguisticFeaturesError, ImportError):
    """Opsiyonel bir paket kurulu değil."""


class ModelNotFoundError(LinguisticFeaturesError, OSError):
    """İstenen spaCy modeli sistemde bulunamadı."""
