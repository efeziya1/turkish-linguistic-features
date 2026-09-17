import math

import pytest

from turkish_linguistic_features.features.morphological import (
    _parse_morph,
    spacy_morph_ratios,
    surface_per_lemma,
)


def _etiketle(ogeler):
    """[(token, morph, pos)] → (morph_tags, pos_data)."""
    return [(t, m) for t, m, _ in ogeler], [(t, p) for t, _, p in ogeler]


# ── _parse_morph ──────────────────────────────────────────────────────

def test_morph_ayristirma():
    assert _parse_morph("Case=Acc|Number=Sing") == {"Case": "Acc", "Number": "Sing"}
    assert _parse_morph("") == {}
    assert _parse_morph("Bozuk|Case=Acc") == {"Case": "Acc"}   # bozuk parça atlanır


# ── spacy_morph_ratios ────────────────────────────────────────────────

def test_morph_oranlari_18_anahtar():
    assert len(spacy_morph_ratios(*_etiketle([("a", "Case=Acc", "NOUN")]))) == 18


def test_gorunus_orani_paydasi_gorunuslu_tokenler():
    """Aspect=Perf taşıyan 1 token, görünüşlü toplam 2 → 0.5 (S2)."""
    sonuc = spacy_morph_ratios(*_etiketle([
        ("gelmiş", "Aspect=Perf", "VERB"), ("geliyor", "Aspect=Prog", "VERB"),
        ("ev", "", "NOUN"), ("ve", "", "CCONJ"),
    ]))
    assert sonuc["morph_aspect_perf"] == 0.5
    assert sonuc["morph_aspect_prog"] == 0.5
    assert sonuc["morph_aspect_imp"] == 0.0


def test_durum_orani_paydasi_durumlu_tokenler():
    """2 durumlu token (1 Acc), 3 durumsuz → Acc oranı 0.5, 0.2 değil."""
    sonuc = spacy_morph_ratios(*_etiketle([
        ("a", "Case=Acc", "NOUN"), ("b", "Case=Dat", "NOUN"),
        ("c", "", "X"), ("d", "", "X"), ("e", "", "X"),
    ]))
    assert sonuc["morph_case_acc"] == 0.5


def test_listede_olmayan_deger_paydaya_girer():
    """Case=Ins anahtar üretmez ama durumlu tokendir."""
    sonuc = spacy_morph_ratios(*_etiketle([
        ("kalemle", "Case=Ins", "NOUN"), ("evi", "Case=Acc", "NOUN"),
    ]))
    assert sonuc["morph_case_acc"] == 0.5
    assert sonuc["morph_case_nom"] == 0.0


def test_iyelik_kisisi_kisi_sayilmaz():
    """Person[psor] ayrı özelliktir; Person=3 sayılır."""
    sonuc = spacy_morph_ratios(*_etiketle([
        ("kitabım", "Case=Nom|Number=Sing|Number[psor]=Sing|Person=3|Person[psor]=1", "NOUN"),
    ]))
    assert sonuc["morph_person_3"] == 1.0
    assert sonuc["morph_person_1"] == 0.0


def test_etiketi_olmayan_kategori_nan():
    """Metinde hiç Case yok → altı durum oranı NaN, diğerleri ölçülür (S1)."""
    sonuc = spacy_morph_ratios(*_etiketle([("geldi", "Tense=Past", "VERB")]))
    durumlar = [k for k in sonuc if k.startswith("morph_case_")]
    assert len(durumlar) == 6 and all(math.isnan(sonuc[k]) for k in durumlar)
    assert sonuc["morph_tense_past"] == 1.0


def test_edilgen_orani_paydasi_fiiller():
    """3 VERB (1 Pass); AUX paydaya girmez → 1/3 (S6, S8)."""
    sonuc = spacy_morph_ratios(*_etiketle([
        ("geldi", "", "VERB"), ("yazıldı", "Voice=Pass", "VERB"),
        ("yaptırdı", "Voice=Cau", "VERB"), ("değil", "", "AUX"),
    ]))
    assert sonuc["morph_voice_pass"] == pytest.approx(1 / 3, abs=1e-5)


def test_edilgen_orani_fiil_yoksa_nan():
    sonuc = spacy_morph_ratios(*_etiketle([("ev", "Case=Nom", "NOUN")]))
    assert math.isnan(sonuc["morph_voice_pass"])


def test_morph_bos_liste():
    sonuc = spacy_morph_ratios([], [])
    assert len(sonuc) == 18 and all(math.isnan(v) for v in sonuc.values())


def test_morph_hizasiz_girdi_hata():
    with pytest.raises(ValueError):
        spacy_morph_ratios([("a", "Case=Acc")], [])


# ── surface_per_lemma ─────────────────────────────────────────────────

def _spl(yuzey, pos, lemma, lang="tr"):
    return surface_per_lemma(yuzey, list(zip(yuzey, pos)), lemma, lang)["surface_per_lemma"]


def test_yuzey_lemma_orani_turkcede_yuksek():
    yuzey = ["kitap", "kitabı", "kitaplar", "kitabımızda"]
    assert _spl(yuzey, ["NOUN"] * 4, ["kitap"] * 4) == 4.0


def test_tekrar_eden_bicim_bir_kez_sayilir():
    """gel: geldim, geliyor, gelmiş (3) · ev: ev (1) → 2.0 (S5)."""
    yuzey = ["geldim", "geliyor", "gelmiş", "geldim", "ev"]
    lemma = ["gel", "gel", "gel", "gel", "ev"]
    assert _spl(yuzey, ["VERB"] * 4 + ["NOUN"], lemma) == 2.0


def test_buyuk_kucuk_harf_ayni_bicim():
    """Cümle başı "Kitabı" = "kitabı"; lemma "Kitap" = "kitap" (S4, S7)."""
    assert _spl(["Kitabı", "kitabı"], ["NOUN"] * 2, ["Kitap", "kitap"]) == 1.0


def test_turkce_i_kucultme():
    assert _spl(["IŞIK", "ışık"], ["NOUN"] * 2, ["ışık", "ışık"], "tr") == 1.0


def test_noktalama_ve_sembol_sayilmaz():
    """PUNCT ve SYM lemma_tokens'ta yok; yüzeyden de atılır."""
    yuzey = ["ev", ".", "%", "evler"]
    assert _spl(yuzey, ["NOUN", "PUNCT", "SYM", "NOUN"], ["ev", "ev"]) == 2.0


def test_yuzey_lemma_bos_nan():
    assert math.isnan(_spl([], [], []))
    assert math.isnan(_spl(["."], ["PUNCT"], []))


def test_yuzey_lemma_hizasiz_hata():
    with pytest.raises(ValueError):
        _spl(["ev", "evler"], ["NOUN", "NOUN"], ["ev"])
    with pytest.raises(ValueError):
        surface_per_lemma(["ev"], [], ["ev"])
