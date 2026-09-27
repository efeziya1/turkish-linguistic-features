"""Dil verisine bağlı testler için tek kural.

Üç işaretleyici: ``tr_model``, ``en_model`` (spaCy modelleri) ve ``cmudict``
(NLTK; İngilizce hece sayımı). Bir test ihtiyaç duyduğu veriyi işaretleyiciyle
bildirir; kontrol yalnız burada yapılır.

- ``TLF_REQUIRE_MODELS`` yoksa: veri eksikse test **atlanır**, mesajda kurulum
  komutu yazar. Modelsiz geliştirici süiti yine de koşturabilsin.
- ``TLF_REQUIRE_MODELS=1`` ise: eksik veri testi **başarısız** eder. CI'da
  kurulum adımı sessizce bozulursa testlerin yeşil "atlandı" ile geçmesini
  önler.

Kontrol ``pytest_runtest_setup``'ta, fixture'lardan önce yapılır: modeli
yükleyen bir fixture (``test_kaynak_esligi.ozellikler``) hiç çalışmaz.
"""

from __future__ import annotations

import functools
import os

import pytest

_KURULUM = {
    "tr_model": (
        "tr_core_news_md",
        "pip install https://huggingface.co/turkish-nlp-suite/tr_core_news_md/"
        "resolve/main/tr_core_news_md-1.0-py3-none-any.whl",
    ),
    "en_model": ("en_core_web_sm", "python -m spacy download en_core_web_sm"),
    "cmudict": ("NLTK cmudict", "python -m nltk.downloader cmudict"),
}


@functools.cache
def _kurulu(isaret: str) -> bool:
    if isaret == "cmudict":
        import nltk
        try:
            nltk.data.find("corpora/cmudict")            # indirme yapmaz
        except LookupError:
            return False
        return True
    import spacy.util
    return _KURULUM[isaret][0] in spacy.util.get_installed_models()


def pytest_configure(config: pytest.Config) -> None:
    for isaret, (ad, _) in _KURULUM.items():
        config.addinivalue_line("markers", f"{isaret}: test needs {ad} installed")


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item: pytest.Item) -> None:
    zorunlu = os.environ.get("TLF_REQUIRE_MODELS") == "1"
    for isaret, (ad, komut) in _KURULUM.items():
        if item.get_closest_marker(isaret) is None or _kurulu(isaret):
            continue
        if zorunlu:
            pytest.fail(f"{ad} is not installed but TLF_REQUIRE_MODELS=1. "
                        f"Install it with: {komut}", pytrace=False)
        pytest.skip(f"{ad} not installed — install with: {komut}")
