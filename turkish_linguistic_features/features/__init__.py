"""Öznitelik katmanı (L1) — saf fonksiyonlar, NLP modeli gerektirmez (K3).

Paket sınırını geçen tek **public** ad ``describe_feature``
(``API-SOZLESMESI.md`` §1). Geri kalan her şey iç koddur ve derin yoldan
alınır::

    from .features.extractor import _extract_features
    from turkish_linguistic_features.features.registry import FEATURE_CITATIONS

Ayrım bilerek: façade'da görünen ad taahhüttür, derin yoldaki değildir.
``_extract_features`` sözleşmenin kendi ifadesiyle "iç koddur, kullanıcı
görmez" — buraya konsaydı arayüze terfi etmiş olurdu.

``FeatureParams`` 2026-09-21'de köke (``params.py``) taşındı, artık bu
paketin parçası değil.
"""

from .registry import describe_feature

__all__ = ["describe_feature"]
