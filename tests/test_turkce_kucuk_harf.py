"""Türkçe küçük harf: ``I → ı``, ``İ → i``.

``str.lower()`` Türkçede yanlış: ``"I".lower() == "i"`` (olması gereken
``ı``) ve ``"İ".lower()`` sonuna birleşik nokta (U+0307) ekleyip iki
karakterlik dize üretir. Sonuç: "Işık" ile "ışık", "İstanbul" ile "istanbul"
farklı tip sayılıyor, ``İ`` ile başlayan kelime bir harf uzun ölçülüyordu.
Kelime listesi, lemma ve frekans tablosu dile göre küçültülmeli.
"""

import pytest

from turkish_linguistic_features.features.extractor import _extract_features
from turkish_linguistic_features.features.frequency_structure import thematic_concentration
from turkish_linguistic_features.features.lexical import rank_word_freq_table

# Aynı iki kelime, biri büyük harfle: doğru küçültmede 2 tip.
KELIMELER = ["Işık", "ışık", "İstanbul", "istanbul"]


def _girdi(kelimeler: list[str], lang: str) -> dict:
    return {
        "raw_text": " ".join(kelimeler),
        "surface_tokens": kelimeler,
        "lemma_tokens": [k.lower() for k in kelimeler],   # lemma yolu ayrıca sınanıyor
        "pos_data": [(k, "NOUN") for k in kelimeler],
        "lang": lang,
        "groups": ["lexical"],
    }


def test_ttr_ve_kelime_uzunlugu_turkce_kucuk_harfle():
    """🔴 Regresyon: ``str.lower()`` ile ttr 1.0, avg_word_length 6.25 çıkıyordu."""
    oz = _extract_features(**_girdi(KELIMELER, "tr"))
    assert oz["ttr"] == 0.5
    assert oz["avg_word_length"] == 6.0


def test_frekans_tablosu_turkce_I_ve_noktali_I():
    _, N, V, items = rank_word_freq_table(["Işık", "ışık", "İstanbul", "istanbul"], lang="tr")
    assert (N, V) == (4, 2)
    assert dict(items) == {"ışık": 2, "istanbul": 2}


def test_tematik_yogunluk_buyuk_harfli_lemmayi_eslestirir():
    """POS haritası da dile göre küçültülmeli: "Işık" → "ışık" eşleşmeli."""
    items = [("ışık", 3), ("ve", 2), ("x", 1)]
    pos = [("Işık", "NOUN")] * 3 + [("ve", "CCONJ")] * 2 + [("x", "X")]
    assert thematic_concentration(items, pos, h=3.0, lang="tr")["thematic_concentration"] > 0.0


def test_ingilizce_davranis_degismedi():
    """İngilizcede ``I → i`` doğru; ``ı`` üretilmemeli."""
    oz = _extract_features(**_girdi(["It", "it", "Is", "is"], "en"))
    assert oz["ttr"] == 0.5
    _, _, V, items = rank_word_freq_table(["It", "it", "India"], lang="en")
    assert V == 2
    assert dict(items) == {"it": 2, "india": 1}


@pytest.mark.tr_model
def test_lemma_yolu_turkce_kucuk_harf():
    """spaCy lemmaları da dile göre küçültülür (``Preprocessor``)."""
    from turkish_linguistic_features.pipeline.spacy_pipeline import Preprocessor
    lemmalar = Preprocessor(lang="tr").process("İstanbul büyük. Işık yandı.").lemma_tokens
    assert "i̇stanbul" not in lemmalar                  # U+0307'li bozuk biçim yok
    assert all("̇" not in lem for lem in lemmalar)
    assert "istanbul" in lemmalar
