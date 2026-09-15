"""Eksik bağımlılıkta 'çök' yerine 'uyar ve devam et' davranışı."""

from __future__ import annotations

import warnings


class MissingDependencyWarning(UserWarning):
    """Bir öznitelik grubu atlandı ama işlem devam etti."""


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
