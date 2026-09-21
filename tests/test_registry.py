"""T19 — registry tabloları ve ``describe_feature``.

Bu testler registry'nin **eksiksiz** ve **tutarlı** olduğunu denetler: her
anahtarın açıklaması, formülü ve ölçüm şartı var mı; ölçekler kapalı kümeden mi
geliyor; grup kayıtları gerçekten okunan alanları mı söylüyor.

Değerlerin doğruluğu burada değil, her modülün kendi test dosyasında.
"""

from collections import Counter
from dataclasses import fields

import pytest

from turkish_linguistic_features.params import FeatureParams
from turkish_linguistic_features.features.registry import (
    BIBLIOGRAPHY,
    DYNAMIC_PREFIXES,
    FEATURE_CITATIONS,
    FEATURE_DESCRIPTIONS,
    FEATURE_FORMULAS,
    FEATURE_PARAMS,
    FEATURE_REQUIRES,
    FEATURE_SCALES,
    GROUP_INPUTS,
    GROUP_LABELS,
    GROUP_SCALES,
    SCALES,
    STATIC_GROUP_KEYS,
    UNVERIFIED_CONSTANTS,
    describe_feature,
    get_group,
)

TUM_STATIK = [k for ks in STATIC_GROUP_KEYS.values() for k in ks]


# ── kapsam: tablolar eksiksiz mi ──────────────────────────────────────


def test_grup_sayilari():
    """12 statik + 2 dinamik = 14 grup (sözleşme §3)."""
    assert len(STATIC_GROUP_KEYS) == 12
    assert len(DYNAMIC_PREFIXES) == 2
    assert len(GROUP_LABELS) == 14


def test_statik_anahtar_sayisi():
    """Sözleşme §4 toplamı: 183 statik anahtar (TR 208, EN 182 dinamikle)."""
    assert len(TUM_STATIK) == 183


def test_anahtarlar_gruplar_arasi_tekrarlanmaz():
    tekrar = [k for k, n in Counter(TUM_STATIK).items() if n > 1]
    assert not tekrar, f"Birden fazla grupta olan anahtarlar: {tekrar}"


def test_her_grubun_etiketi_var():
    for grup in list(STATIC_GROUP_KEYS) + list(DYNAMIC_PREFIXES):
        assert grup in GROUP_LABELS


def test_her_statik_anahtarin_aciklamasi_var():
    eksik = [k for k in TUM_STATIK if k not in FEATURE_DESCRIPTIONS]
    assert not eksik, f"Açıklaması olmayan anahtarlar: {eksik}"


def test_her_statik_anahtarin_formulu_var():
    eksik = [k for k in TUM_STATIK if k not in FEATURE_FORMULAS]
    assert not eksik, f"Formülü olmayan anahtarlar: {eksik}"


def test_her_dinamik_grubun_formulu_var():
    eksik = [g for g in DYNAMIC_PREFIXES if g not in FEATURE_FORMULAS]
    assert not eksik, f"Formülü olmayan dinamik gruplar: {eksik}"


def test_her_statik_anahtarin_sarti_var():
    eksik = [k for k in TUM_STATIK if k not in FEATURE_REQUIRES]
    assert not eksik, f"Ölçüm şartı olmayan anahtarlar: {eksik}"


def test_her_dinamik_grubun_sarti_var():
    assert set(DYNAMIC_PREFIXES) <= set(FEATURE_REQUIRES)


def test_her_grubun_inputs_kaydi_var():
    eksik = [g for g in GROUP_LABELS if g not in GROUP_INPUTS]
    assert not eksik, f"GROUP_INPUTS'ta olmayan gruplar: {eksik}"


# ── get_group ─────────────────────────────────────────────────────────


def test_get_group_statik():
    assert get_group("mattr") == "lexical"
    assert get_group("arc_len_mean") == "syntactic_dep"


def test_get_group_dinamik():
    assert get_group("char_a") == "chars"
    assert get_group("ng_ve_bir") == "custom_ngrams"


def test_get_group_bilinmeyen_anahtar():
    with pytest.raises(KeyError):
        get_group("boyle_bir_sey_yok")


def test_kullanici_ngrami_registryde_kayitli():
    """custom_ngrams grubu yoksa ``analyze(custom_ngrams=...)`` T20'yi kırar."""
    assert DYNAMIC_PREFIXES["custom_ngrams"] == "ng_"
    assert "custom_ngrams" in GROUP_LABELS
    assert describe_feature("ng_ve_bir")["group"] == "custom_ngrams"


def test_cumle_sonu_anahtarlari_vocab_ile_uyumlu():
    from turkish_linguistic_features.vocab import SENT_FINAL_POS
    son = [k for k in STATIC_GROUP_KEYS["syntactic_dep"] if k.startswith("sentfinal_")]
    assert len(son) == len(SENT_FINAL_POS) + 1 == 14   # + sentfinal_other


# ── describe_feature ──────────────────────────────────────────────────


def test_describe_on_bir_alan():
    d = describe_feature("mattr")
    assert set(d) == {"key", "group", "group_label", "description",
                      "formula", "scale", "inputs", "params", "requires",
                      "citation", "references"}


def test_describe_statik_anahtar():
    d = describe_feature("mattr")
    assert d["group"] == "lexical"
    assert d["params"] == ("mattr_window",)
    assert "lemma_tokens" in d["inputs"]
    assert d["citation"] is not None
    assert d["scale"] == "ratio_0_1"


def test_describe_dinamik_anahtar_grup_formulunu_alir():
    """``char_a``'nın kendi formülü yok, grubunki dönmeli."""
    d = describe_feature("char_a")
    assert d["group"] == "chars"
    assert d["formula"] == FEATURE_FORMULAS["chars"]
    assert d["inputs"] == ("raw_text",)


def test_describe_literatur_olcusu_degilse_citation_none():
    """Adlandırılmış literatür ölçüsü olmayanlarda ``citation`` None — K10.

    ``None`` ölçünün bize ait olduğunu **söylemez**; yalnız adlandırılmış bir
    literatür ölçüsü olmadığını söyler (2026-09-19, Efe).
    """
    assert describe_feature("ttr_moving_slope")["citation"] is None


def test_describe_ayarlanamayan_ozellik_bos_params():
    assert describe_feature("vowel_ratio")["params"] == ()


def test_describe_bilinmeyen_anahtar():
    with pytest.raises(KeyError):
        describe_feature("boyle_bir_sey_yok")


def test_her_statik_anahtar_describe_edilebiliyor():
    """183 statik anahtarın hiçbiri boş alan döndürmemeli."""
    for k in TUM_STATIK:
        d = describe_feature(k)
        assert d["description"], f"{k}: açıklama boş"
        assert d["formula"], f"{k}: formül boş"
        assert d["requires"], f"{k}: şart boş"


# ── ölçek ─────────────────────────────────────────────────────────────


def test_her_grubun_scale_varsayilani_var():
    """GROUP_SCALES eksiksiz olmalı — 14 grubun hepsi."""
    assert set(GROUP_SCALES) == set(GROUP_LABELS)


def test_scale_degerleri_kapali_kumeden():
    for k, v in list(GROUP_SCALES.items()) + list(FEATURE_SCALES.items()):
        assert v in SCALES, f"{k} geçersiz ölçek: {v}"


def test_feature_scales_grup_varsayiliyla_ayni_deger_icermez():
    """Çift kayıt yasak — biri güncellenip diğeri unutulur."""
    for k, v in FEATURE_SCALES.items():
        assert v != GROUP_SCALES[get_group(k)], (
            f"{k} zaten grup varsayılanı ({v}) — FEATURE_SCALES'ten sil"
        )


def test_feature_scales_anahtarlari_registryde_kayitli():
    """Yazım hatası yakalar: olmayan bir anahtara ölçek atanamaz."""
    for k in FEATURE_SCALES:
        get_group(k)          # bilinmiyorsa KeyError


def test_scale_gruptan_miras_alinir():
    assert describe_feature("pos_noun")["scale"] == GROUP_SCALES["pos"]
    assert describe_feature("char_a")["scale"] == "ratio_0_1"


def test_scale_istisnalari_gruptan_farkli():
    assert describe_feature("entropy")["scale"] == "bits"
    assert describe_feature("n_lemma_count")["scale"] == "count"
    assert describe_feature("sent_len_skewness")["scale"] == "signed"
    assert describe_feature("word_length_cv")["scale"] == "cv"
    assert describe_feature("h_point")["scale"] == "score"
    assert describe_feature("verb_dist_mean")["scale"] == "length"


def test_olcek_ilkesi_taniminda_0_1_olmayanlar_ratio_degil():
    """2026-09-18 kararları: bunların hepsi 1'i aşabiliyor → ``score``."""
    for k in ("para_count_norm", "thematic_concentration",
              "secondary_thematic_concentration", "heaps_beta",
              "punc_,_ratio", "punc_question_ratio"):
        assert describe_feature(k)["scale"] == "score", k


# ── FEATURE_PARAMS ────────────────────────────────────────────────────


def test_feature_params_alanlari_gercekten_var():
    """FEATURE_PARAMS'ta yazım hatası olmasın — FeatureParams'ta olmalı."""
    gecerli = {f.name for f in fields(FeatureParams)}
    for anahtar, alanlar in FEATURE_PARAMS.items():
        bilinmeyen = set(alanlar) - gecerli
        assert not bilinmeyen, f"{anahtar}: FeatureParams'ta yok: {bilinmeyen}"


def test_feature_params_anahtarlari_registryde_kayitli():
    bilinmeyen = set(FEATURE_PARAMS) - set(TUM_STATIK)
    assert not bilinmeyen, f"Registry'de olmayan anahtarlar: {bilinmeyen}"


# ── künye ─────────────────────────────────────────────────────────────


def test_citation_anahtarlari_registryde_kayitli():
    bilinmeyen = set(FEATURE_CITATIONS) - set(TUM_STATIK) - set(DYNAMIC_PREFIXES)
    assert not bilinmeyen, f"Registry'de olmayan anahtarlar: {bilinmeyen}"


def test_dogrulanmamis_sabit_kunyeye_yaziliyor():
    """K12 Kademe D — liste şu an boş, mekanizma yine de çalışmalı."""
    assert isinstance(UNVERIFIED_CONSTANTS, frozenset)
    for k in UNVERIFIED_CONSTANTS:
        assert describe_feature(k)["citation"].endswith(" [doğrulanmamış sabit]")


def test_inputs_kaydi_gercekten_okunan_alanlari_iceriyor():
    """🔴 Kaydın VAR olması yetmez, DOĞRU olması gerekir.

    ``frequency_structure`` (2026-08-25) ve ``syntactic`` (2026-08-26) iki kez
    eksik kaydedildi; ikisi de "kaydı var mı" testinden geçiyordu.
    """
    bilinen = {
        "activity_ratio":          "pos_data",   # syntactic grubu
        "lexical_density":         "pos_data",
        "pos_kl_div":              "pos_data",
        "noun_variation":          "pos_data",   # lexical grubu
        "thematic_concentration":  "pos_data",   # frequency_structure grubu
    }
    for anahtar, beklenen in bilinen.items():
        assert beklenen in describe_feature(anahtar)["inputs"], (
            f"{anahtar} {beklenen} okuyor ama GROUP_INPUTS söylemiyor"
        )


# ── kaynakça ──────────────────────────────────────────────────────────


def test_her_kunye_kaynakcada_karsiligi_olan_bir_esere_atif_yapiyor():
    """🔴 Uydurma kaynak adına karşı tek güvenlik ağı (2026-09-19, Efe).

    Künye dizeleri kısa işaretçidir (``"Lu (2012) Tablo 2"``); tam kayıt
    ``BIBLIOGRAPHY``de durur. Her künye **en az bir** kaynakça anahtarını
    birebir içermeli — içermiyorsa ya yazım hatası vardır ya da hiç
    doğrulanmamış bir kaynak uydurulmuştur.

    Bu testten önce böyle bir denetim yoktu: yanlış bir künye sessizce
    geçiyordu (bkz. `plan/kaynak-arastirmasi.md`, kaynaklarda bulunan altı
    hata).
    """
    eksik = {
        anahtar: kunye
        for anahtar, kunye in FEATURE_CITATIONS.items()
        if not any(eser in kunye for eser in BIBLIOGRAPHY)
    }
    assert not eksik, f"Kaynakçada karşılığı olmayan künyeler: {eksik}"


def test_kaynakcadaki_her_eser_en_az_bir_kunyede_kullaniliyor():
    """Ölü kayıt bırakma — kullanılmayan kaynakça girdisi eskir."""
    kullanilmayan = {
        eser for eser in BIBLIOGRAPHY
        if not any(eser in kunye for kunye in FEATURE_CITATIONS.values())
    }
    assert not kullanilmayan, f"Hiçbir künyede geçmeyen eserler: {kullanilmayan}"


def test_describe_feature_tam_kaydi_dondurur():
    """``references`` künyedeki eserlerin tam bibliyografik kayıtları."""
    d = describe_feature("hdd")
    assert d["references"], "hdd'nin künyesi var, tam kaydı da olmalı"
    assert any("Behavior Research Methods" in r for r in d["references"])


def test_citation_yoksa_references_bos():
    d = describe_feature("ttr_moving_slope")
    assert d["citation"] is None
    assert d["references"] == ()
