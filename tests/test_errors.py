import warnings

import pytest

from turkish_linguistic_features._warnings import (
    MissingDependencyWarning,
    kurulum_ipucu,
    uyar_eksik_bagimlilik,
)
from turkish_linguistic_features.exceptions import (
    LinguisticFeaturesError,
    ModelNotFoundError,
)


def test_hata_hiyerarsisi():
    assert issubclass(ModelNotFoundError, LinguisticFeaturesError)
    assert issubclass(ModelNotFoundError, OSError)


def test_kurulum_ipucu_bilinen_paket():
    # Paket PyPI'da yok: ekstra değil paketin kendisi önerilir (2026-10-06).
    assert kurulum_ipucu("wordfreq") == "pip install 'wordfreq>=3.0'"


def test_zorunlu_paketler_tabloda_degil():
    """numpy/spacy/zeyrek/textstat zorunlu — ipucu tablosunda yer almamalı."""
    from turkish_linguistic_features._warnings import _KURULUM_KOMUTU
    for paket in ("numpy", "spacy", "zeyrek", "textstat"):
        assert paket not in _KURULUM_KOMUTU, f"{paket} zorunlu, tabloda olmamalı"


def test_kurulum_ipucu_bilinmeyen_paket():
    assert kurulum_ipucu("acayip_paket") == "pip install acayip_paket"


def test_uyari_kurulum_komutunu_icerir():
    with pytest.warns(MissingDependencyWarning, match="wordfreq>=3.0"):
        uyar_eksik_bagimlilik("wordfreq", "wordfreq_* (2 öznitelik)")


def test_eksik_opsiyonel_paket_cokertmez():
    """Sözleşme: eksik opsiyonel paket UYARI üretir, hata fırlatmaz — akış devam eder.

    `analyze()` T24'te doğduğunda `wordfreq` kurulu değilse bu yol işleyecek:
    `wordfreq_*` 0.0 yazılır, kullanıcı uyarıyı görür, kalan öznitelikler
    hesaplanmaya devam eder.
    """
    with warnings.catch_warnings(record=True) as kayit:
        warnings.simplefilter("always")
        sonuc = uyar_eksik_bagimlilik("wordfreq", "wordfreq_* (2 öznitelik)")
        devam_edildi = True

    assert sonuc is None
    assert devam_edildi
    assert len(kayit) == 1
    assert issubclass(kayit[0].category, MissingDependencyWarning)


def test_missing_dependency_error_yok():
    """Hiç fırlatılmadığı için 2026-10-08'de kaldırıldı (Efe)."""
    import turkish_linguistic_features.exceptions as hatalar

    assert not hasattr(hatalar, "MissingDependencyError")
