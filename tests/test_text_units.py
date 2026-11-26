"""``text_units()`` — sözcükler, sözlükbirimler, sözcük türleri ve tümceler, ayrı listeler.

Sözleşme: listeler özniteliklerin saydığı birimlerin kendisidir. ``words`` uzunluğu
``word_count``, ``sentences`` uzunluğu ``sent_count``; ``lemmas`` ve ``pos`` ``words`` ile
sıra sıra eşleşir; ``sentences`` birleşince ``words`` olur.
"""

import math

import pytest

import turkish_linguistic_features as tlf

tr_model = pytest.mark.tr_model
en_model = pytest.mark.en_model

ANAHTARLAR = {"words", "lemmas", "pos", "sentences"}


def _sozlesme(b: dict, oz: dict) -> None:
    assert set(b) == ANAHTARLAR
    assert len(b["words"]) == oz["word_count"]
    assert len(b["sentences"]) == oz["sent_count"]
    assert len(b["lemmas"]) == len(b["pos"]) == len(b["words"])
    assert [s for t in b["sentences"] for s in t] == b["words"]
    adlar = b["pos"].count("NOUN") / len(b["words"])
    assert oz["pos_noun_ratio"] == pytest.approx(adlar, abs=1e-5)


def test_public_api_de():
    assert "text_units" in tlf.__all__


@tr_model
def test_turkce_ornek():
    b = tlf.text_units("Ali kitapları okudu. Yarın İstanbul'a gidecek.", lang="tr")
    assert b["words"] == ["Ali", "kitapları", "okudu", "Yarın", "İstanbul'a", "gidecek"]
    assert b["lemmas"] == ["ali", "kitap", "oku", "yarın", "istanbul", "git"]
    assert b["sentences"] == [["Ali", "kitapları", "okudu"], ["Yarın", "İstanbul'a", "gidecek"]]
    assert b["pos"][0] == "PROPN" and b["pos"][2] == "VERB"


@tr_model
def test_turkce_ozniteliklerle_ayni_birimler():
    """Kısaltma, sayı, tırnak ve üç nokta: sözcük ve tümce kuralı özniteliklerle aynı."""
    metin = ('Dr. Ayşe 3,5 km yürüdü... "Yoruldum!" dedi. Sonra eve, yani '
             'Kadıköy\'deki eve döndü: Akşam olmuştu.')
    _sozlesme(tlf.text_units(metin, lang="tr"), tlf.analyze(metin, lang="tr"))


@en_model
def test_ingilizce_ozniteliklerle_ayni_birimler():
    metin = "Dr. Smith walked 3.5 km... \"I'm tired!\" she said. Then she went home."
    b = tlf.text_units(metin, lang="en")
    _sozlesme(b, tlf.analyze(metin, lang="en"))
    assert b["lemmas"][b["words"].index("walked")] == "walk"


@tr_model
def test_bos_metin():
    b = tlf.text_units("", lang="tr")
    assert b == {"words": [], "lemmas": [], "pos": [], "sentences": []}
    assert math.isnan(tlf.analyze("", lang="tr")["word_count"])


def test_desteklenmeyen_dil():
    with pytest.raises(ValueError):
        tlf.text_units("metin", lang="de")
