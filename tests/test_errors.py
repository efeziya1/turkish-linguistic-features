import warnings

import pytest

from turkish_linguistic_features._warnings import (
    MissingDependencyWarning,
    kurulum_ipucu,
    uyar_eksik_bagimlilik,
)
from turkish_linguistic_features.exceptions import (
    LinguisticFeaturesError,
    MissingDependencyError,
    ModelNotFoundError,
)


def test_hata_hiyerarsisi():
    assert issubclass(MissingDependencyError, LinguisticFeaturesError)
    assert issubclass(MissingDependencyError, ImportError)
    assert issubclass(ModelNotFoundError, OSError)


def test_kurulum_ipucu_bilinen_paket():
    assert "turkish-linguistic-features[lexical_freq]" in kurulum_ipucu("wordfreq")


def test_zorunlu_paketler_tabloda_degil():
    """numpy/spacy/zeyrek/textstat zorunlu — ipucu tablosunda yer almamalı."""
    from turkish_linguistic_features._warnings import _KURULUM_KOMUTU
    for paket in ("numpy", "spacy", "zeyrek", "textstat"):
        assert paket not in _KURULUM_KOMUTU, f"{paket} zorunlu, tabloda olmamalı"


def test_kurulum_ipucu_bilinmeyen_paket():
    assert kurulum_ipucu("acayip_paket") == "pip install acayip_paket"


def test_uyari_kurulum_komutunu_icerir():
    with pytest.warns(MissingDependencyWarning, match="turkish-linguistic-features\\[lexical_freq\\]"):
        uyar_eksik_bagimlilik("wordfreq", "ref_zipf_* (3 öznitelik)")


def test_eksik_opsiyonel_paket_cokertmez():
    """Sözleşme: eksik opsiyonel paket UYARI üretir, hata fırlatmaz — akış devam eder.

    `analyze()` T24'te doğduğunda `wordfreq` kurulu değilse bu yol işleyecek:
    `ref_zipf_*` 0.0 yazılır, kullanıcı uyarıyı görür, kalan öznitelikler
    hesaplanmaya devam eder.
    """
    with warnings.catch_warnings(record=True) as kayit:
        warnings.simplefilter("always")
        sonuc = uyar_eksik_bagimlilik("wordfreq", "ref_zipf_* (3 öznitelik)")
        devam_edildi = True

    assert sonuc is None
    assert devam_edildi
    assert len(kayit) == 1
    assert issubclass(kayit[0].category, MissingDependencyWarning)


def test_except_importerror_ile_yakalanir():
    """Eski kodu kırmamak için ImportError'dan da miras alıyoruz."""
    with pytest.raises(ImportError):
        raise MissingDependencyError("test")
