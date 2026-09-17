"""Öznitelik katmanı — saf fonksiyonlar, NLP modeli gerektirmez (K3).

Paket sınırını geçen üç ad burada toplanıyor: ayar sözleşmesi, keşif arayüzü
ve birleştirici. Modüllerin geri kalanı (``lexical``, ``syntactic``, …) ve
registry'nin ham sözlükleri kendi modüllerinden okunur — ``describe_feature``
tek keşif giriş noktasıdır, ham tablolar ileri kullanım içindir.

``_extract_features`` alt çizgiyle başlıyor çünkü public API'nin parçası
değil: ``analyze()`` onu içeriden çağırır (T24).
"""

from .extractor import _extract_features
from .params import FeatureParams
from .registry import describe_feature

__all__ = [
    "FeatureParams",
    "_extract_features",
    "describe_feature",
]
