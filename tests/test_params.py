from dataclasses import FrozenInstanceError

import pytest

from turkish_linguistic_features.features.params import (
    DEFAULT_PARAMS,
    DEFAULT_PARAMS_BY_LANG,
    DEFAULT_PARAMS_EN,
    DEFAULT_PARAMS_TR,
    FeatureParams,
)
from turkish_linguistic_features.pipeline.preprocess import ProcessedText


def test_params_degistirilemez():
    p = FeatureParams()
    with pytest.raises(FrozenInstanceError):
        p.mattr_window = 100


def test_params_yazim_hatasi_hemen_patlar():
    with pytest.raises(TypeError):
        FeatureParams(mattr_windwo=100)


def test_params_hashlenebilir():
    assert hash(FeatureParams()) == hash(FeatureParams())


def test_dil_varsayilanlari_farkli():
    """TR cümleleri EN'den kısa — eşikler de farklı olmalı."""
    assert DEFAULT_PARAMS_TR.short_sent_threshold == 4
    assert DEFAULT_PARAMS_EN.short_sent_threshold == 7
    assert DEFAULT_PARAMS_TR.long_sent_threshold < DEFAULT_PARAMS_EN.long_sent_threshold


def test_bilinmeyen_dil_genel_varsayilana_duser():
    assert DEFAULT_PARAMS_BY_LANG.get("de", DEFAULT_PARAMS) is DEFAULT_PARAMS


def test_processed_text_to_dict_anahtarlari():
    pt = ProcessedText(
        raw_text="Merhaba dünya.",
        surface_tokens=("Merhaba", "dünya", "."),
        lemma_tokens=("merhaba", "dünya", "."),
        pos_data=(("Merhaba", "INTJ"), ("dünya", "NOUN"), (".", "PUNCT")),
        sentences_as_tokens=(("Merhaba", "dünya", "."),),
    )
    d = pt.to_dict()
    assert set(d) == {
        "raw_text", "surface_tokens", "lemma_tokens", "pos_data",
        "sentences_as_tokens", "morpheme_lists", "morph_tags", "lang", "dep_data",
    }
    assert isinstance(d["surface_tokens"], list)   # dışarıda liste
    assert d["dep_data"] is None
