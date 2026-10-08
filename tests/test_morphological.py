import math

import pytest

from turkish_linguistic_features.features.morphological import (
    _parse_morph,
    case_suffix_ratios,
    modal_suffix_ratios,
    mood_suffix_ratios,
    spacy_morph_ratios,
    suffix_ngrams,
    surface_per_lemma,
    tense_ratios,
    zeyrek_agglutination_depth,
    zeyrek_derivational_suffix_ratio,
    zeyrek_morfoloji,
    zeyrek_negation_ratio,
    zeyrek_passive_ratio,
    zeyrek_plural_ratio,
    zeyrek_question_particle_ratio,
    zeyrek_suffix_char_length_ratio,
    zeyrek_verb_suffix_diversity,
)
from turkish_linguistic_features.params import FeatureParams


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
    assert sonuc["aspect_perf_ratio"] == 0.5
    assert sonuc["aspect_prog_ratio"] == 0.5
    assert sonuc["aspect_imp_ratio"] == 0.0


def test_durum_orani_paydasi_durumlu_tokenler():
    """2 durumlu token (1 Acc), 3 durumsuz → Acc oranı 0.5, 0.2 değil."""
    sonuc = spacy_morph_ratios(*_etiketle([
        ("a", "Case=Acc", "NOUN"), ("b", "Case=Dat", "NOUN"),
        ("c", "", "X"), ("d", "", "X"), ("e", "", "X"),
    ]))
    assert sonuc["case_acc_ratio"] == 0.5


def test_listede_olmayan_deger_paydaya_girer():
    """Case=Ins anahtar üretmez ama durumlu tokendir."""
    sonuc = spacy_morph_ratios(*_etiketle([
        ("kalemle", "Case=Ins", "NOUN"), ("evi", "Case=Acc", "NOUN"),
    ]))
    assert sonuc["case_acc_ratio"] == 0.5
    assert sonuc["case_nom_ratio"] == 0.0


def test_iyelik_kisisi_kisi_sayilmaz():
    """Person[psor] ayrı özelliktir; Person=3 sayılır."""
    sonuc = spacy_morph_ratios(*_etiketle([
        ("kitabım", "Case=Nom|Number=Sing|Number[psor]=Sing|Person=3|Person[psor]=1", "NOUN"),
    ]))
    assert sonuc["person_3_ratio"] == 1.0
    assert sonuc["person_1_ratio"] == 0.0


def test_etiketi_olmayan_kategori_nan():
    """Metinde hiç Case yok → altı durum oranı NaN, diğerleri ölçülür (S1)."""
    sonuc = spacy_morph_ratios(*_etiketle([("geldi", "Tense=Past", "VERB")]))
    durumlar = [k for k in sonuc if k.startswith("case_")]
    assert len(durumlar) == 6 and all(math.isnan(sonuc[k]) for k in durumlar)
    assert sonuc["tense_past_ratio"] == 1.0


def test_edilgen_orani_paydasi_fiiller():
    """3 VERB (1 Pass); AUX paydaya girmez → 1/3 (S6, S8)."""
    sonuc = spacy_morph_ratios(*_etiketle([
        ("geldi", "", "VERB"), ("yazıldı", "Voice=Pass", "VERB"),
        ("yaptırdı", "Voice=Cau", "VERB"), ("değil", "", "AUX"),
    ]))
    assert sonuc["voice_pass_ratio"] == pytest.approx(1 / 3, abs=1e-5)


def test_edilgen_orani_fiil_yoksa_nan():
    sonuc = spacy_morph_ratios(*_etiketle([("ev", "Case=Nom", "NOUN")]))
    assert math.isnan(sonuc["voice_pass_ratio"])


def test_morph_bos_liste():
    sonuc = spacy_morph_ratios([], [])
    assert len(sonuc) == 18 and all(math.isnan(v) for v in sonuc.values())


def test_morph_hizasiz_girdi_hata():
    with pytest.raises(ValueError):
        spacy_morph_ratios([("a", "Case=Acc")], [])


# ── surface_per_lemma ─────────────────────────────────────────────────

def _spl(yuzey, pos, lemma, lang="tr"):
    return surface_per_lemma(yuzey, list(zip(yuzey, pos, strict=False)), lemma, lang)["surface_per_lemma"]


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


# ── T16: Zeyrek ───────────────────────────────────────────────────────
#
# Morpheme = (etiket, yüzey, türetimsel_mi) — ETİKET ÖNCE. Zeyrek'in gerçek
# çıktısına göre: görünmeyen ekler boş yüzeyle (A3sg), türetmeden sonraki
# tür etiketi ayrı öge (("Verb", "", False)), çözümsüz kelime ("Unk", ...).

KITAPLARIMIZDA = [("Noun", "kitap", False), ("A3pl", "lar", False),
                  ("P1pl", "ımız", False), ("Loc", "da", False)]
EV = [("Noun", "ev", False), ("A3sg", "", False)]
GELMEDIM = [("Verb", "gel", False), ("Neg", "me", False), ("Past", "di", False), ("A1sg", "m", False)]
GELMEM = [("Verb", "gel", False), ("Neg", "me", False), ("Aor", "", False), ("A1sg", "m", False)]
GELEMEDIM = [("Verb", "gel", False), ("Unable", "eme", False), ("Past", "di", False), ("A1sg", "m", False)]
GELEBILIRIM = [("Verb", "gel", False), ("Able", "ebil", True), ("Verb", "", False),
               ("Aor", "ir", False), ("A1sg", "im", False)]
GITMELIYIM = [("Verb", "git", False), ("Neces", "meli", False), ("A1sg", "yim", False)]
GIDIYORDUM = [("Verb", "gid", False), ("Prog1", "iyor", False), ("Past", "du", False), ("A1sg", "m", False)]
GELIRSE = [("Verb", "gel", False), ("Aor", "ir", False), ("Cond", "se", False), ("A3sg", "", False)]
YAPTIRDI = [("Verb", "yap", False), ("Caus", "tır", True), ("Verb", "", False),
            ("Past", "dı", False), ("A3sg", "", False)]
YAZILDI = [("Verb", "yaz", False), ("Pass", "ıl", True), ("Verb", "", False),
           ("Past", "dı", False), ("A3sg", "", False)]
YAZILAN = [("Verb", "yaz", False), ("Pass", "ıl", True), ("Verb", "", False),
           ("PresPart", "an", True), ("Adj", "", False)]
EVDEYDI = [("Noun", "ev", False), ("A3sg", "", False), ("Loc", "de", False),
           ("Zero", "", True), ("Verb", "", False), ("Past", "ydi", False), ("A3sg", "", False)]
OGRENCILERDI = [("Noun", "öğrenci", False), ("A3pl", "ler", False), ("Zero", "", True),
                ("Verb", "", False), ("Past", "di", False), ("A3sg", "", False)]
GELDILER = [("Verb", "gel", False), ("Past", "di", False), ("A3pl", "ler", False)]
MI = [("Ques", "mı", False), ("Pres", "", False), ("A3sg", "", False)]
BILINMEYEN = [("Unk", "xqzt", False)]
NOKTA = [("Punc", ".", False)]


def _z(*kelimeler):
    """(morpheme_lists, pos_data); pos_data yalnız noktalama süzgeci için okunur."""
    pos = [(m[0][1], "PUNCT" if m[0][0] == "Punc" else "X") for m in kelimeler]
    return list(kelimeler), pos


def test_ek_derinligi_elle():
    """kitaplarımızda: 3 ek, ev: 0 görünen ek → 1.5 (S1)."""
    assert zeyrek_agglutination_depth(*_z(KITAPLARIMIZDA, EV))["zeyrek_agglutination_depth"] == 1.5


def test_derinlik_gorunmeyen_ek_ve_tur_etiketi_sayilmaz():
    """evdeydi: de + ydi = 2; A3sg, Zero, Verb sayılmaz."""
    assert zeyrek_agglutination_depth(*_z(EV))["zeyrek_agglutination_depth"] == 0.0
    assert zeyrek_agglutination_depth(*_z(EVDEYDI))["zeyrek_agglutination_depth"] == 2.0


def test_bilinmeyen_ve_noktalama_paydada_yok():
    """S6: Unk ve noktalama hiçbir paydaya girmez."""
    sonuc = zeyrek_agglutination_depth(*_z(KITAPLARIMIZDA, BILINMEYEN, NOKTA))
    assert sonuc["zeyrek_agglutination_depth"] == 3.0


def test_cogul_orani():
    assert zeyrek_plural_ratio(*_z(KITAPLARIMIZDA, EV))["zeyrek_plural_ratio"] == 0.5


def test_cogul_bagli_oldugu_parcaya_bakar():
    """S10: öğrencilerdi → isme bağlı -ler çoğul; geldiler → kişi eki."""
    assert zeyrek_plural_ratio(*_z(OGRENCILERDI, GELDILER))["zeyrek_plural_ratio"] == 0.5


def test_olumsuzluk_paydasi_fiiller_eme_dahil():
    """S5a, S9: 3 fiil (gelmedim, gelemedim olumsuz) + isim → 2/3."""
    sonuc = zeyrek_negation_ratio(*_z(GELMEDIM, GELEMEDIM, GELIRSE, EV))
    assert sonuc["zeyrek_negation_ratio"] == pytest.approx(2 / 3, abs=1e-5)


def test_kip_ayrimi_eme_yeterlilik_sayilir():
    """S9: gelebilirim, gelemedim → Able; gitmeliyim → Neces."""
    sonuc = modal_suffix_ratios(*_z(GELEBILIRIM, GELEMEDIM, GITMELIYIM, EV))
    assert sonuc["zeyrek_modal_possibility_ratio"] == pytest.approx(2 / 3, abs=1e-5)
    assert sonuc["zeyrek_modal_necessity_ratio"] == pytest.approx(1 / 3, abs=1e-5)


def test_edilgen_fiil_genel_etiketle():
    """yazılan sıfat (genel etiket Adj) → payda ve paya girmez → 1/2."""
    assert zeyrek_passive_ratio(*_z(YAZILDI, YAZILAN, GELMEDIM))["zeyrek_passive_ratio"] == 0.5


def test_zaman_orani_paydasi_fiiller():
    """1 fiil (geçmiş) + 3 isim → zeyrek_tense_past_def_ratio = 1.0, 0.25 değil."""
    assert tense_ratios(*_z(GELMEDIM, EV, EV, EV))["zeyrek_tense_past_def_ratio"] == 1.0


def test_birlesik_zamanda_son_ek_sayilir():
    """S3: gidiyordum → yalnız geçmiş."""
    sonuc = tense_ratios(*_z(GIDIYORDUM))
    assert sonuc["zeyrek_tense_past_def_ratio"] == 1.0 and sonuc["zeyrek_tense_present_ratio"] == 0.0


def test_simdiki_genis_zaman_ve_ek_fiil():
    """S4: geniş zaman (görünmeyen dahil) present; evdeydi fiil sayılır."""
    assert tense_ratios(*_z(GELIRSE, GELMEM))["zeyrek_tense_present_ratio"] == 1.0
    assert tense_ratios(*_z(EVDEYDI))["zeyrek_tense_past_def_ratio"] == 1.0


def test_sart_ve_ettirgen():
    sonuc = mood_suffix_ratios(*_z(GELIRSE, YAPTIRDI, EV))
    assert sonuc["zeyrek_conditional_suffix_ratio"] == 0.5
    assert sonuc["zeyrek_causative_suffix_ratio"] == 0.5


def test_durum_eki_orani():
    sonuc = case_suffix_ratios(*_z(KITAPLARIMIZDA, EV))
    assert sonuc["zeyrek_case_loc_ratio"] == 0.5
    assert sonuc["zeyrek_case_acc_ratio"] == 0.0


def test_soru_eki_orani():
    sonuc = zeyrek_question_particle_ratio(*_z(MI, EV, BILINMEYEN))
    assert sonuc["zeyrek_question_particle_ratio"] == 0.5


def test_ek_karakter_orani():
    """kitaplarımızda: kök 5, ek 9 karakter → 9/14; noktalama sayılmaz."""
    sonuc = zeyrek_suffix_char_length_ratio(*_z(KITAPLARIMIZDA, NOKTA))
    assert sonuc["zeyrek_suffix_char_length_ratio"] == pytest.approx(9 / 14, abs=1e-5)


def test_yapim_eki_orani_zeyrek_isareti():
    """S2: yazıldı → ıl yapım, dı çekim → 0.5."""
    assert zeyrek_derivational_suffix_ratio(*_z(YAZILDI))["zeyrek_derivational_suffix_ratio"] == 0.5
    assert zeyrek_derivational_suffix_ratio(*_z(GELMEDIM))["zeyrek_derivational_suffix_ratio"] == 0.0
    assert math.isnan(zeyrek_derivational_suffix_ratio(*_z(EV))["zeyrek_derivational_suffix_ratio"])


def test_ek_bigram_entropisi():
    """kitaplarımızda: (A3pl,P1pl), (P1pl,Loc) eşit → ln 2 nat (1 bit); tek desen 0."""
    assert suffix_ngrams(*_z(KITAPLARIMIZDA))["zeyrek_suffix_bigram_entropy"] == round(math.log(2), 5)
    assert suffix_ngrams(*_z(GELDILER, GELDILER))["zeyrek_suffix_bigram_entropy"] == 0.0
    assert math.isnan(suffix_ngrams(*_z(EV))["zeyrek_suffix_bigram_entropy"])


def test_fiil_eki_cesitliligi_parcali():
    """S7: 2'şer fiil; {Neg,Past,A1sg,Prog1}=4, {Neg,Past,A1sg}=3 → 3.5; artık atılır."""
    params = FeatureParams(verb_suffix_window=2)
    sonuc = zeyrek_verb_suffix_diversity(
        *_z(GELMEDIM, EV, GIDIYORDUM, GELMEDIM, GELMEDIM, GIDIYORDUM), params)
    assert sonuc["zeyrek_verb_suffix_diversity"] == 3.5


def test_fiil_eki_cesitliligi_kisa_metin_nan():
    assert FeatureParams().verb_suffix_window == 50
    assert math.isnan(zeyrek_verb_suffix_diversity(*_z(GELMEDIM))["zeyrek_verb_suffix_diversity"])


def test_zeyrek_morfoloji_23_anahtar():
    assert len(zeyrek_morfoloji(*_z(KITAPLARIMIZDA, GELMEDIM))) == 23


def test_bos_morfem_listesi():
    """Boş girdi → 23'ü de NaN (K4)."""
    sonuc = zeyrek_morfoloji([], [])
    assert len(sonuc) == 23 and all(math.isnan(v) for v in sonuc.values())


def test_zeyrek_hizasiz_girdi_hata():
    with pytest.raises(ValueError):
        zeyrek_agglutination_depth([EV], [])
