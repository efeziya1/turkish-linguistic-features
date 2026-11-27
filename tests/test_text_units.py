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

ANAHTARLAR = {"words", "lemmas", "pos", "syllables", "sentences"}


def _sozlesme(b: dict, oz: dict) -> None:
    assert set(b) == ANAHTARLAR
    assert len(b["words"]) == oz["word_count"]
    assert len(b["sentences"]) == oz["sent_count"]
    assert len(b["lemmas"]) == len(b["pos"]) == len(b["syllables"]) == len(b["words"])
    heceler = [h for h in b["syllables"] if not math.isnan(h)]
    assert sum(heceler) == oz["syllable_count"]
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
    assert b["syllables"] == [2.0, 4.0, 3.0, 2.0, 4.0, 3.0]


@tr_model
def test_okunusu_cikmayan_sozcukte_seslem_nan():
    """Web ve e-posta adresi okunmaz: NaN, toplam ``syllable_count`` ile yine aynı (2026-11-26, Efe)."""
    metin = "Fiyat www.x.com sitesinde değişti, ad@x.com adresine yazın."
    b = tlf.text_units(metin, lang="tr")
    _sozlesme(b, tlf.analyze(metin, lang="tr"))
    hece = dict(zip(b["words"], b["syllables"], strict=True))
    assert math.isnan(hece["www.x.com"]) and math.isnan(hece["ad@x.com"])
    assert hece["Fiyat"] == 2.0


@tr_model
def test_turkce_ozniteliklerle_ayni_birimler():
    """Kısaltma, sayı, tırnak ve üç nokta: sözcük ve tümce kuralı özniteliklerle aynı."""
    metin = ('Dr. Ayşe 3,5 km yürüdü... "Yoruldum!" dedi. Sonra eve, yani '
             'Kadıköy\'deki eve döndü: Akşam olmuştu.')
    _sozlesme(tlf.text_units(metin, lang="tr"), tlf.analyze(metin, lang="tr"))


@tr_model
def test_harfsiz_tumce_her_yerde_ayni_sayilir():
    """``1999!`` bir tümce: text_units, sent_count ve Kalyoncu aynı sayar (2026-11-26, Efe)."""
    metin = "Bu bir tümce. 1999! Bitti."
    b = tlf.text_units(metin, lang="tr")
    oz = tlf.analyze(metin, lang="tr")
    _sozlesme(b, oz)
    assert oz["sent_count"] == 3
    assert b["sentences"] == [["Bu", "bir", "tümce"], ["1999"], ["Bitti"]]


@tr_model
def test_cozumlenemeyen_sozcukte_hiza_bozulmaz():
    """Akana'nın tanımadığı sözcükte lemma boş kalmaz, listeler kaymaz (2026-11-26, Efe)."""
    metin = "Ali xqzptl'yi gördü. Sonra qwvbnm geldi ve zzkrt dedi."
    b = tlf.text_units(metin, lang="tr")
    _sozlesme(b, tlf.analyze(metin, lang="tr"))
    assert all(b["lemmas"])
    assert b["lemmas"][b["words"].index("xqzptl'yi")] == "xqzptl"
    assert b["lemmas"][b["words"].index("gördü")] == "gör"
    assert b["lemmas"][b["words"].index("geldi")] == "gel"


@en_model
@pytest.mark.cmudict            # İngilizce seslem sayımı (``syllables``)
def test_ingilizce_ozniteliklerle_ayni_birimler():
    metin = "Dr. Smith walked 3.5 km... \"I'm tired!\" she said. Then she went home."
    b = tlf.text_units(metin, lang="en")
    _sozlesme(b, tlf.analyze(metin, lang="en"))
    assert b["lemmas"][b["words"].index("walked")] == "walk"


@tr_model
def test_bos_metin():
    b = tlf.text_units("", lang="tr")
    assert b == {"words": [], "lemmas": [], "pos": [], "syllables": [], "sentences": []}
    assert math.isnan(tlf.analyze("", lang="tr")["word_count"])


def test_desteklenmeyen_dil():
    with pytest.raises(ValueError):
        tlf.text_units("metin", lang="de")


@tr_model
def test_bitisik_sozcuk_her_yerde_iki_sozcuk():
    """``geldi.Sonra``: word_count, tümce uzunluğu ve text_units aynı 5 sözcüğü sayar (2026-11-27, Efe)."""
    metin = "Ali eve geldi.Sonra uyudu."
    b = tlf.text_units(metin, lang="tr")
    oz = tlf.analyze(metin, lang="tr")
    _sozlesme(b, oz)
    assert b["sentences"] == [["Ali", "eve", "geldi"], ["Sonra", "uyudu"]]
    assert oz["sent_len_mean"] == oz["word_count"] / oz["sent_count"]
