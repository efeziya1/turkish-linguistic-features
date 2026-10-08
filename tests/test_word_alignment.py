"""Tek kelime tanımı: varsayılan kelime ↔ model tokenı eşlemesi (2026-10-07, Efe)."""

import pytest

from turkish_linguistic_features.features.word_alignment import word_token_indices, word_view


def test_bolunen_kelime_ilk_kelime_tokenini_alir():
    metin = "Türk-Amerikan ilişkisi"
    tok = ["Türk", "-", "Amerikan", "ilişkisi"]
    pos = [("Türk", "PROPN"), ("-", "PUNCT"), ("Amerikan", "ADJ"), ("ilişkisi", "NOUN")]
    assert word_token_indices(metin, tok, pos, "tr") == [0, 3]


def test_ingilizce_kisaltma_ilk_parca():
    metin = "It's John's book, don't."
    tok = ["It", "'s", "John", "'s", "book", ",", "do", "n't", "."]
    pos = [("It", "PRON"), ("'s", "AUX"), ("John", "PROPN"), ("'s", "PART"), ("book", "NOUN"),
           (",", "PUNCT"), ("do", "AUX"), ("n't", "PART"), (".", "PUNCT")]
    assert word_token_indices(metin, tok, pos, "en") == [0, 2, 4, 6]


def test_kenar_noktalamasi_ve_sira_sayisi():
    metin = '"Ev" 3. kat'
    tok = ['"', "Ev", '"', "3.", "kat"]
    pos = [('"', "PUNCT"), ("Ev", "NOUN"), ('"', "PUNCT"), ("3.", "ADJ"), ("kat", "NOUN")]
    assert word_token_indices(metin, tok, pos, "tr") == [1, 3, 4]


def test_word_view_kelime_duzeyi_listeler():
    metin = "E-posta geldi."
    tok = ["E", "-", "posta", "geldi", "."]
    pos = [("E", "NOUN"), ("-", "PUNCT"), ("posta", "NOUN"), ("geldi", "VERB"), (".", "PUNCT")]
    morf = [("E", "Case=Nom"), ("-", ""), ("posta", "Case=Nom"), ("geldi", "Tense=Past"), (".", "")]
    zeyrek = [(("Noun", "e", False),), (("Punc", "-", False),), (("Noun", "posta", False),),
              (("Verb", "gel", False), ("Past", "di", False)), (("Punc", ".", False),)]
    wv = word_view(metin, ["E-posta", "geldi"], tok, pos, ["e", "posta", "gel"], morf, zeyrek,
                   [tok], "tr")
    assert wv.pos == [("E-posta", "NOUN"), ("geldi", "VERB")]
    assert wv.lemmas == ["e", "gel"]
    assert wv.morph == [("E-posta", "Case=Nom"), ("geldi", "Tense=Past")]
    assert wv.morphemes == [zeyrek[0], zeyrek[3]]
    assert wv.sentences == [["E-posta", "geldi"]]


def test_word_view_cumleler_temsilci_tokena_gore():
    metin = "Geldi. Gitti."
    tok = ["Geldi", ".", "Gitti", "."]
    pos = [("Geldi", "VERB"), (".", "PUNCT"), ("Gitti", "VERB"), (".", "PUNCT")]
    wv = word_view(metin, ["Geldi", "Gitti"], tok, pos, ["gel", "git"], None, None,
                   [["Geldi", "."], ["Gitti", "."]], "tr")
    assert wv.sentences == [["Geldi"], ["Gitti"]]
    assert wv.morph is None and wv.morphemes is None


def test_bos_metin_olculdu_sayilir():
    wv = word_view("", [], [], [], [], [], (), [], "tr")
    assert wv.pos == [] and wv.morphemes == [] and wv.morph == []


def test_ingilizcede_bos_morfem_listesi_grubu_kapatir():
    wv = word_view("Hi.", ["Hi"], ["Hi", "."], [("Hi", "INTJ"), (".", "PUNCT")], ["hi"],
                   [("Hi", ""), (".", "")], (), [["Hi", "."]], "en")
    assert wv.morphemes is None


def test_hizasiz_girdi_hata():
    with pytest.raises(ValueError):
        word_token_indices("ev", ["ev", "."], [("ev", "NOUN")], "tr")
    with pytest.raises(ValueError):
        word_token_indices("ev", ["okul"], [("okul", "NOUN")], "tr")
    with pytest.raises(ValueError):
        word_view("ev geldi", ["ev", "geldi"], ["ev", "geldi"], [("ev", "NOUN"), ("geldi", "VERB")],
                  ["ev"], None, None, [["ev", "geldi"]], "tr")
