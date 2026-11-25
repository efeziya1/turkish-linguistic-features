"""Akana arka ucu: ``morpheme_lists`` ve Türkçe ``lemma_tokens``.

Ön işleme Akana'ya tümce tümce türce verir; belirsizlik gidericisi her türcenin çözümlemesini
seçer (``AkanaBackend.analyze_sentence``). ``ProcessedText``in geri kalanını ``Preprocessor``
spaCy modelinden dolduruyor (T21).

``akana`` zorunlu bağımlılık (K1), bu yüzden bu dosyada ``skipif`` yok.
"""

import akana
import pytest

from turkish_linguistic_features.exceptions import LinguisticFeaturesError
from turkish_linguistic_features.pipeline import akana_backend as ab
from turkish_linguistic_features.pipeline.akana_backend import AkanaBackend


def _tek(sozcuk):
    """Tek türcelik tümcenin ``(morfemler, lemma)`` çifti."""
    return AkanaBackend().analyze_sentence([sozcuk])[0]


# ── çözümleme dizesinin çevrilmesi ─────────────────────────────────────


def test_turetme_sinirinda_tur_ayri_oge():
    """``|ek:Etiket→Tür``: türetme eki türetimsel, ardından yeni tür boş yüzeyle."""
    assert ab._morfemler("merkez:Noun+A3sg|li:With→Adj") == (
        ("Noun", "merkez", False), ("A3sg", "", False),
        ("With", "li", True), ("Adj", "", False))


def test_yuzeysiz_turetme():
    assert ab._morfemler("yüz:Num|Zero→Noun+A3sg") == (
        ("Num", "yüz", False), ("Zero", "", True), ("Noun", "", False), ("A3sg", "", False))


def test_beklenmeyen_bicim_hata_verir():
    with pytest.raises(LinguisticFeaturesError):
        ab._cevir({"analysis": "biçimsiz dize"})


# ── sözcük çözümleme ──────────────────────────────────────────────────


def test_basit_kelime_cozumleme():
    ms, _ = _tek("kitapları")
    assert ms[0][0] == "Noun" and ms[0][1] == "kitap"


def test_morfem_uclusunde_etiket_once():
    """Morpheme = (etiket, yüzey_ek, türetimsel_mi) — etiket POZİSYON 0'da."""
    ms, _ = _tek("kitaplarımızda")
    assert ms == (("Noun", "kitap", False), ("A3pl", "lar", False),
                  ("P1pl", "ımız", False), ("Loc", "da", False))


def test_fiil_cozumleme():
    ms, _ = _tek("gelmedim")
    assert [m[0] for m in ms] == ["Verb", "Neg", "Past", "A1sg"]


def test_gorunmeyen_ek_ve_turetme_etiketi_korunuyor():
    ms, _ = _tek("yazıldı")
    assert ("Pass", "ıl", True) in ms
    assert ("Verb", "", False) in ms
    assert ("A3sg", "", False) in ms


@pytest.mark.parametrize("duz", [
    "İstanbul'da", "Ahmet'in", "Zeynep'i", "Türkiye'de", "TBMM'de", "O'nun", "1990'larda",
])
@pytest.mark.parametrize("kesme", ["’", "‘"])
def test_kivrik_kesme_duz_kesme_gibi_cozumlenir(duz, kesme):
    """Akana eğri kesmeyi düz kesmeyle aynı çözümlüyor; araç sözcüğü düzleştirmeden verir."""
    egri = _tek(duz.replace("'", kesme))
    assert egri == _tek(duz)
    assert egri[0][0][0] != "Unk"


def test_cozumlenemeyen_kelime_cokmez():
    """Boş liste DEĞİL — tek elemanlı liste, kök etiketi ``Unk``."""
    assert _tek("xyzqwabc")[0] == (("Unk", "xyzqwabc", False),)


def test_noktalama_kelime_disi():
    """Akana noktalamayı çözümlemiyor: kök ``Unk``; noktalama spaCy etiketiyle de paydadan düşer."""
    assert _tek(".")[0] == (("Unk", ".", False),)


def test_onceki_cagri_sonrakini_etkilemez():
    """Bir tümcenin çözümlenmesi sonraki tümcenin sonucunu değiştirmemeli."""
    b = AkanaBackend()
    b.analyze_sentence(["gelecek"])
    assert "Able" in [m[0] for m in b.analyze_sentence(["gelebilir"])[0][0]]


# ── lemma ─────────────────────────────────────────────────────────────


def test_lemma_kurallari():
    assert _tek("gelmedim")[1] == "gel"                 # fiilde mastar eki yok
    assert _tek("millî")[1] == "millî"                  # düzeltme işareti kalır
    assert _tek("Zeynep’i")[1] == "Zeynep"              # büyük harf korunur
    assert _tek("xyzqw'den")[1] == "xyzqw"              # çözümsüz: kesmeden önceki kısım
    assert _tek("xyzqw’den")[1] == "xyzqw"              # eğri kesmede de
    assert _tek("xyzqw‘den")[1] == "xyzqw"


# ── belirsizlik gidericisi ────────────────────────────────────────────


def test_tumce_icinde_baglama_gore_secer():
    """Akana'nın ilk çözümlemesinde ``yüz`` ad; ``Yüz kişi geldi`` tümcesinde giderici sayı seçer."""
    assert akana.Morphology().analyze("yüz")[0]["primary_pos"] == "Noun"
    secilen = AkanaBackend().analyze_sentence(["Yüz", "kişi", "geldi", "."])
    assert [m[0][0] for m, _ in secilen] == ["Num", "Noun", "Verb", "Unk"]
    assert [lem for _, lem in secilen][:3] == ["yüz", "kişi", "gel"]


def test_tumce_cozumsuz_turce_bicimi():
    """Noktalama ve çözümsüz sözcük tek ``Unk`` öğesi; boş tümce boş liste."""
    secilen = AkanaBackend().analyze_sentence(["xqzpw", "%", "."])
    assert [m for m, _ in secilen] == [(("Unk", "xqzpw", False),), (("Unk", "%", False),),
                                       (("Unk", ".", False),)]
    assert AkanaBackend().analyze_sentence([]) == []
