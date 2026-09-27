"""Dile bağlı alfabe tablosu ve küçük harf dönüşümü.

Bu dosya paket içinden hiçbir şey import etmez (L0). İçeriği 2026-09-21'de
``features/punctuation.py``'den ayrıldı: hem öznitelik modülleri hem kökteki
``_analyze`` ve ``file_loader`` okuyor, yani noktalama özniteliklerinin
yanında durması kökü features katmanına bağlıyordu.

Alfabeler: TR 29 harf, EN 26
(``q``, ``w``, ``x`` 2026-09-15'te eklendi).
"""


_ALFABE: dict[str, str] = {
    "tr": "abcçdefgğhıijklmnoöprsştuüvyz",   # 29 harf
    "en": "abcdefghijklmnopqrstuvwxyz",      # 26 harf
}


def _kucuk_harf(metin: str, lang: str) -> str:
    """Dile göre küçük harf. TR'de ``I → ı`` ve ``İ → i``; ``str.lower()`` bunu yapmaz."""
    if lang == "tr":
        metin = metin.replace("I", "ı").replace("İ", "i")
    return metin.lower()
