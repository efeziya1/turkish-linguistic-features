"""Skip-gram entropisi — ``ngrams`` grubunun 2 anahtarı.

``skipgram_1_entropy`` ve ``skipgram_2_entropy``: aralarında sabit sayıda kelime
atlanmış kelime çiftlerinin dağılımının Shannon entropisi, bit cinsinden.

3 ve üstü n-gram entropileri (kelime ve karakter 3/4-gram) 2026-09-15'te şemadan
çıkarıldı; skip-gramlar iki elemanlı gram oldukları için kaldı.

Fonksiyon saftır (K3): girdi spaCy ``surface_tokens``. Ölçülemeyen değer 0.0 (K4).
"""

from __future__ import annotations

import math
from collections import Counter


def _kucuk_harf(metin: str, lang: str) -> str:
    """Dile göre küçük harf. TR'de ``I → ı`` ve ``İ → i``; ``str.lower()`` bunu yapmaz."""
    if lang == "tr":
        metin = metin.replace("I", "ı").replace("İ", "i")
    return metin.lower()


def skipgram_entropy(tokens: list[str], skip: int = 1, lang: str = "tr") -> dict[str, float]:
    """Skip-gram entropisi, bit → ``skipgram_{skip}_entropy``.

    ``skip=1`` → ``(token[i], token[i+2])`` çiftleri (aradaki 1 kelime atlanır);
    ``skip=2`` → ``(token[i], token[i+3])``.

    Tokenler dile göre küçük harfe indirilir ve **noktalama tokenleri çıkarılır**
    (içinde hiç harf ya da rakam olmayan token); atlama çıkarmadan sonraki
    listede yapılır. Böylece yalnız kelime dizilimi ölçülür — noktalama ayrı
    grupta. Hep aynı çift → 0; ``skip + 1``'den kısa listede 0.0.
    """
    anahtar = f"skipgram_{skip}_entropy"
    kelimeler = [_kucuk_harf(t, lang) for t in tokens if any(ch.isalnum() for ch in t)]
    adim = skip + 1
    if len(kelimeler) <= adim:
        return {anahtar: 0.0}
    ciftler = Counter(zip(kelimeler, kelimeler[adim:]))
    n = sum(ciftler.values())
    h = -sum((c / n) * math.log2(c / n) for c in ciftler.values())
    return {anahtar: round(h, 5) + 0.0}
