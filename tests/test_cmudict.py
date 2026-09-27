"""İngilizce hece sayımı NLTK'nın ``cmudict`` verisini ister; kütüphane onu indirmez.

textstat ≥ 0.7.10 veri yoksa ``nltk.download()`` ile internete çıkıyor, ağ
yoksa ``LookupError`` ile çöküyor. Kütüphane textstat'ı çağırmadan önce
``nltk.data.find`` ile bakar (indirme yapmaz) ve yoksa kurulum komutunu
söyleyen ``ModelNotFoundError`` verir — spaCy modelleriyle aynı ilke.
"""

import socket

import pytest
import spacy.util

import turkish_linguistic_features as tlf
from turkish_linguistic_features.features import phonetic

_KURULU = spacy.util.get_installed_models()


@pytest.fixture
def cmudict_yok(monkeypatch, tmp_path):
    """NLTK arama yolu boş bir klasör, ağ kapalı, önbellek sıfır."""
    import nltk
    monkeypatch.setattr(nltk.data, "path", [str(tmp_path)])
    monkeypatch.setattr(phonetic, "_CMUDICT_VAR", False)
    ag_denemeleri = []

    def _ag_yok(*a, **k):
        ag_denemeleri.append(a)
        raise OSError("network disabled in test")

    monkeypatch.setattr(socket.socket, "connect", _ag_yok)
    monkeypatch.setattr(socket, "create_connection", _ag_yok)
    return ag_denemeleri


def test_ingilizce_veri_yoksa_indirmeden_acik_hata(cmudict_yok, monkeypatch):
    """Hata spaCy yüklenmeden verilir ve kurulum komutunu söyler."""
    def _spacy_yuklenmemeli(*a, **k):
        raise AssertionError("spaCy should not load before the cmudict check")

    monkeypatch.setattr(spacy, "load", _spacy_yuklenmemeli)
    with pytest.raises(tlf.ModelNotFoundError, match="nltk.downloader cmudict"):
        tlf.analyze("The cat sat on the mat.", lang="en")
    assert cmudict_yok == []                          # hiç ağ denemesi yok


def test_analyze_corpus_da_korpusu_okumadan_hata_verir(cmudict_yok, tmp_path):
    with pytest.raises(tlf.ModelNotFoundError):
        tlf.analyze_corpus(tmp_path / "olmayan_klasor", lang="en")


def test_hece_sayaci_textstat_i_verisiz_cagirmaz(cmudict_yok):
    """İç yoldan (``hece_say``) çağrılsa da indirme tetiklenmez."""
    with pytest.raises(tlf.ModelNotFoundError):
        phonetic.hece_say("window", "en")
    assert cmudict_yok == []


@pytest.mark.skipif("en_core_web_sm" not in _KURULU, reason="en_core_web_sm not installed")
def test_hece_gerektirmeyen_ingilizce_grup_veri_istemez(cmudict_yok):
    oz = tlf.analyze("The cat sat on the mat. It was warm.", lang="en", groups=["lexical"])
    assert "ttr" in oz


@pytest.mark.skipif("tr_core_news_md" not in _KURULU, reason="tr_core_news_md not installed")
def test_turkce_etkilenmez(cmudict_yok):
    oz = tlf.analyze("Kedi paspasın üstüne oturdu. Hava ılıktı.", lang="tr")
    assert len(oz) == 208
