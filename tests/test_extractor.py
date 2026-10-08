"""T20 — ``_extract_features()`` bütün öznitelik modüllerini tek çağrıda birleştirir.

Bu testler **anahtar kümesini** ve sözleşmenin vaatlerini denetler, değerlerin
doğruluğunu değil. Bir formülün doğru sayı ürettiğini garanti eden tek şey o
formülü yazan görevin kendi "bilinen değer" testidir (K12).
"""

import math

import pytest

from turkish_linguistic_features.features.extractor import _extract_features
from turkish_linguistic_features.features.registry import (
    DYNAMIC_PREFIXES,
    SCALES,
    STATIC_GROUP_KEYS,
    describe_feature,
)

# Türkçe, üç cümle, iki paragraf. Cümle uzunlukları 5 ve 6 kelime: TR eşiği
# (4) ile EN eşiği (7) arasında kalıyor, böylece dil varsayılanı testi gerçek
# bir fark ölçüyor.
METIN = (
    "Küçük çocuk bahçede top oynuyordu. Annesi ona seslendi ve eve çağırdı.\n\n"
    "Çocuk koşarak geldi, yorgun görünüyordu."
)
TOKENLER = ["Küçük", "çocuk", "bahçede", "top", "oynuyordu", ".",
            "Annesi", "ona", "seslendi", "ve", "eve", "çağırdı", ".",
            "Çocuk", "koşarak", "geldi", ",", "yorgun", "görünüyordu", "."]
# `lemma_tokens`'a noktalama ve sembol GİRMEZ (T21) — `pos_data`'dan
# NON_WORD_POS atılınca kalanla birebir hizalı olmak zorunda.
LEMMALAR = ["küçük", "çocuk", "bahçe", "top", "oyna",
            "anne", "o", "seslen", "ve", "ev", "çağır",
            "çocuk", "koş", "gel", "yorgun", "görün"]
POS = [("Küçük", "ADJ"), ("çocuk", "NOUN"), ("bahçede", "NOUN"), ("top", "NOUN"),
       ("oynuyordu", "VERB"), (".", "PUNCT"),
       ("Annesi", "NOUN"), ("ona", "PRON"), ("seslendi", "VERB"), ("ve", "CCONJ"),
       ("eve", "NOUN"), ("çağırdı", "VERB"), (".", "PUNCT"),
       ("Çocuk", "NOUN"), ("koşarak", "ADV"), ("geldi", "VERB"), (",", "PUNCT"),
       ("yorgun", "ADJ"), ("görünüyordu", "VERB"), (".", "PUNCT")]
CUMLELER = [TOKENLER[:6], TOKENLER[6:13], TOKENLER[13:]]
MORFEMLER = [[("Noun", t, False)] for t in TOKENLER]
MORPH_ETIKET = [(t, "Case=Nom|Number=Sing") for t, _ in POS]

ORNEK_GIRDI = dict(
    raw_text=METIN,
    surface_tokens=TOKENLER,
    lemma_tokens=LEMMALAR,
    pos_data=POS,
    sentences_as_tokens=CUMLELER,
    morpheme_lists=MORFEMLER,
    morph_tags=MORPH_ETIKET,
    lang="tr",
)

BOS_GIRDI = dict(raw_text="", surface_tokens=[], lemma_tokens=[], pos_data=[],
                 sentences_as_tokens=[], morpheme_lists=[], morph_tags=[], lang="tr")

# Sözleşme §6'dan türetilmiş beklenti — koddan ölçülmedi.
# TR taban 199; `dep_data` verilmediği için `syntactic_dep` (16) atlanır.
TR_DEP_SIZ = 199 - 16
EN_DEP_SIZ = 172 - 16


# ── 🔴 registry tutarlılık testi — projenin sigortası ─────────────────


def test_uretilen_anahtarlar_registryle_birebir_ayni():
    """Üretilen her anahtar registry'de kayıtlı, kayıtlı her anahtar üretiliyor."""
    uretilen = set(_extract_features(**ORNEK_GIRDI))
    kayitli = {k for ks in STATIC_GROUP_KEYS.values() for k in ks}
    onekler = tuple(DYNAMIC_PREFIXES.values())

    kayitsiz = {k for k in uretilen
                if k not in kayitli and not k.startswith(onekler)}
    assert not kayitsiz, f"Registry'de olmayan anahtarlar üretildi: {sorted(kayitsiz)}"

    # `syntactic_dep` hariç (dep_data yok); `morphological_zeyrek` DAHİL (lang="tr", K11).
    # İngilizceye özgü okunabilirlik anahtarları da Türkçede üretilmez.
    beklenen = (kayitli
                - set(STATIC_GROUP_KEYS["syntactic_dep"])
                - {"flesch_reading_ease", "flesch_kincaid_grade", "smog",
                   "polysyllabic_word_ratio"})
    eksik = beklenen - uretilen
    assert not eksik, f"Registry'de kayıtlı ama üretilmeyen anahtarlar: {sorted(eksik)}"


def test_uretilen_her_anahtarin_gecerli_olcegi_var():
    """`describe_feature` `GROUP_SCALES[grup]` okuyor — eksik grup KeyError olur."""
    for k in _extract_features(**ORNEK_GIRDI):
        olcek = describe_feature(k)["scale"]
        assert olcek in SCALES, f"{k} geçersiz ölçek: {olcek}"


def test_ratio_olcekli_anahtarlar_gercekten_0_1_arasinda():
    """``scale == "ratio_0_1"`` bir VAAT — testle tutuluyor.

    Kullanıcının ölçekleme kodu bu vaade güveniyor: "ratio_0_1 ise ham
    bırakabilirim". Vaat tutulmazsa sessizce yanlış ölçeklenmiş bir matris
    üretilir.
    """
    for k, v in _extract_features(**ORNEK_GIRDI).items():
        if describe_feature(k)["scale"] == "ratio_0_1" and not math.isnan(v):
            assert 0.0 <= v <= 1.0, f"{k} = {v} ama scale ratio_0_1 diyor"


# ── anahtar sayısı sabite bağlı ───────────────────────────────────────


def test_taban_anahtar_sayisi_tr():
    assert len(_extract_features(**ORNEK_GIRDI)) == TR_DEP_SIZ


@pytest.mark.cmudict            # İngilizce hece sayımı
def test_taban_anahtar_sayisi_en():
    assert len(_extract_features(**{**ORNEK_GIRDI, "lang": "en"})) == EN_DEP_SIZ


# ── dil ve grup davranışı ─────────────────────────────────────────────


@pytest.mark.cmudict            # İngilizce hece sayımı
def test_ingilizcede_zeyrek_grubu_hic_uretilmez():
    """EN şemasında `morphological_zeyrek` YOK — Zeyrek İngilizce çözümlemiyor."""
    feats = _extract_features(**{**ORNEK_GIRDI, "lang": "en"})
    assert not (set(STATIC_GROUP_KEYS["morphological_zeyrek"]) & set(feats))


@pytest.mark.cmudict            # İngilizce hece sayımı
def test_okunabilirlik_dile_gore_ayriliyor():
    """TR'de 3 Türkçe formül, EN'de 4 İngilizce formül; karşı tarafta hiç yok."""
    tr = _extract_features(**ORNEK_GIRDI)
    en = _extract_features(**{**ORNEK_GIRDI, "lang": "en"})
    assert {"bezirci_yilmaz", "atesman", "cetinkaya_uzun"} <= set(tr)
    assert not {"bezirci_yilmaz", "atesman", "cetinkaya_uzun"} & set(en)
    assert {"flesch_reading_ease", "flesch_kincaid_grade", "smog",
            "polysyllabic_word_ratio"} <= set(en)
    assert not {"flesch_reading_ease", "smog"} & set(tr)


@pytest.mark.cmudict            # İngilizce hece sayımı
def test_unlu_uyumu_yalniz_turkcede():
    """Ünlü uyumu Türkçeye özgü (Göksel & Kerslake 2005): EN'de anahtar hiç yok."""
    uyum = {"harmony_fronting_ratio", "harmony_rounding_ratio"}
    tr = _extract_features(**ORNEK_GIRDI)
    en = _extract_features(**{**ORNEK_GIRDI, "lang": "en"})
    assert uyum <= set(tr)
    assert not uyum & set(en)
    for k in uyum:
        assert "(TR only)" in describe_feature(k)["description"]


@pytest.mark.cmudict            # İngilizce hece sayımı
def test_params_none_ise_dil_varsayilani():
    """TR ve EN farklı cümle eşikleri kullanır (4 / 7) → farklı sonuç."""
    tr = _extract_features(**ORNEK_GIRDI)
    en = _extract_features(**{**ORNEK_GIRDI, "lang": "en"})
    assert tr["short_sent_ratio"] != en["short_sent_ratio"]


def test_gruplar_parametresi_daralttir():
    tam = _extract_features(**ORNEK_GIRDI)
    kismi = _extract_features(**ORNEK_GIRDI, groups=["lexical", "pos"])
    assert len(kismi) < len(tam)
    assert "mattr" in kismi
    assert "vowel_ratio" not in kismi


def test_bilinmeyen_grup_hata_verir():
    with pytest.raises(ValueError, match="Unknown group"):
        _extract_features(**ORNEK_GIRDI, groups=["olmayan_grup"])


def test_girdi_yoksa_grup_sessizce_atlanir():
    """`dep_data` verilmedi → `syntactic_dep` hiç üretilmez, hata da yok."""
    feats = _extract_features(**ORNEK_GIRDI)
    assert not (set(STATIC_GROUP_KEYS["syntactic_dep"]) & set(feats))


def test_hizalanmasi_gereken_uc_alan_yoksa_grup_atlanir():
    """`morph_tags` ve `morpheme_lists` de `pos_data` ile hizalı olmak zorunda.

    Verilmemişlerse grup `syntactic_dep` gibi sessizce atlanır — `ValueError`
    fırlatmak yerine. `analyze()` yolunda üçü de dolu gelir (T21).
    """
    eksik = {k: v for k, v in ORNEK_GIRDI.items()
             if k not in ("morph_tags", "morpheme_lists")}
    feats = _extract_features(**eksik)
    for grup in ("morphological", "morphological_zeyrek", "syntactic_dep"):
        assert not (set(STATIC_GROUP_KEYS[grup]) & set(feats)), grup
    assert len(feats) == TR_DEP_SIZ - 19 - 23


# ── kullanıcı n-gramları ──────────────────────────────────────────────


def test_kullanici_ngrami_sema_disina_sutun_ekler():
    """`custom_ngrams` taban şemayı GENİŞLETİR — istenen davranış."""
    taban = _extract_features(**ORNEK_GIRDI)
    genis = _extract_features(**ORNEK_GIRDI, custom_ngrams=[["çocuk", "koşarak"]])
    assert set(genis) - set(taban) == {"ngram_çocuk_koşarak_count"}


def test_custom_ngrams_verilmezse_hic_ng_anahtari_yok():
    """`custom_ngrams` taban şemanın parçası değil."""
    assert not {k for k in _extract_features(**ORNEK_GIRDI) if k.startswith("ngram_")}


# ── K4: değer sözleşmesi ──────────────────────────────────────────────


def test_tum_degerler_float_ve_sonsuz_degil():
    """NaN = ölçülemedi, izinli; inf hiçbir zaman."""
    for k, v in _extract_features(**ORNEK_GIRDI).items():
        assert isinstance(v, float), f"{k} float değil: {type(v)}"
        assert not math.isinf(v), f"{k} sonsuz"


def test_bos_metin_cokmez():
    sonuc = _extract_features(**BOS_GIRDI)
    assert len(sonuc) > 0
    assert all(isinstance(v, float) for v in sonuc.values())


def test_bos_metinde_ngram_sayimi_nan():
    """Boş metin ölçülemez (K4); n-gram sayımı da `word_count` gibi NaN döner."""
    oz = _extract_features(**BOS_GIRDI, custom_ngrams=[["NOUN"]])
    assert math.isnan(oz["ngram_NOUN_count"])


def test_bos_metinde_olculebilen_yok():
    """Boş metinde hiçbir öznitelik ölçülemez → hepsi NaN (K4)."""
    olculen = {k: v for k, v in _extract_features(**BOS_GIRDI).items()
               if not math.isnan(v)}
    assert not olculen, f"Boş metinde sayı üreten anahtarlar: {olculen}"


def test_tek_kelime_cokmez():
    sonuc = _extract_features(
        raw_text="Ev", surface_tokens=["Ev"], lemma_tokens=["ev"],
        pos_data=[("Ev", "NOUN")], sentences_as_tokens=[["Ev"]],
        morpheme_lists=[[("Noun", "Ev", False)]], morph_tags=[("Ev", "Case=Nom")],
        lang="tr",
    )
    assert all(isinstance(v, float) for v in sonuc.values())
    assert not any(math.isinf(v) for v in sonuc.values())


def test_varsayilan_kelime_tanimi_bosluk_birimi():
    """Sayıya ve yazılı biçime bakan gruplar boşluk birimini sayar (2026-10-06, Efe):
    spaCy "e-posta"yı üç tokena böler, kelime birimi tek kelimedir."""
    metin = "E-posta geldi."
    tok = ["E", "-", "posta", "geldi", "."]
    pos = [("E", "NOUN"), ("-", "PUNCT"), ("posta", "NOUN"), ("geldi", "VERB"), (".", "PUNCT")]
    oz = _extract_features(raw_text=metin, surface_tokens=tok, lemma_tokens=["e", "posta", "gel"],
                           pos_data=pos, lang="tr",
                           groups=["sentence", "paragraph", "lexical", "punctuation"])
    assert oz["sent_len_mean"] == 2.0
    assert oz["para_len_mean"] == 2.0
    assert oz["ttr"] == 1.0 and oz["word_len_mean"] == 6.0      # "e-posta" 7, "geldi" 5
    assert oz["punct_period_ratio"] == 0.5
    # Tek kelime tanımı (2026-10-07, Efe): "E-posta" bir kelime, lemması ilk kelime
    # tokenının ("e") lemması; etiket grupları da iki kelime sayar.
    assert oz["lemma_count"] == 2.0


def test_etiket_gruplari_varsayilan_kelimeyi_sayar():
    """Sözcük türü kelime başına (2026-10-07, Efe): bölünen kelime ilk parçasının etiketini
    alır, noktalama paydaya girmez, `pos_punct` yok; noktalama payları işaretler içinde."""
    metin = "E-posta geldi."
    tok = ["E", "-", "posta", "geldi", "."]
    pos = [("E", "NOUN"), ("-", "PUNCT"), ("posta", "NOUN"), ("geldi", "VERB"), (".", "PUNCT")]
    oz = _extract_features(raw_text=metin, surface_tokens=tok, lemma_tokens=["e", "posta", "gel"],
                           pos_data=pos, lang="tr", groups=["pos", "syntactic", "punctuation"])
    assert oz["pos_noun_ratio"] == 0.5 and oz["pos_verb_ratio"] == 0.5
    assert "pos_punct" not in oz
    assert oz["lexical_density"] == 1.0
    assert oz["punct_dash_ratio"] == oz["punct_period_ratio"] == 0.5     # "-" ve "." / 2 işaret
