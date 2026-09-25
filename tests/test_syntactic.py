import ast
import inspect
import math
import warnings

import pytest

from turkish_linguistic_features import ParagraphStructureWarning, vocab
from turkish_linguistic_features.features.syntactic import (
    activity_ratio,
    avg_sent_len_char,
    lexical_density,
    nominal_verbal_ratio,
    paragraph_stats,
    pos_distribution_stats,
    pos_ratios,
    pronoun_freq,
    question_per_sent,
    sent_len_entropy,
    sentence_distribution_stats,
    sentence_stats,
    verb_distance_stats,
    word_ngram_ratios,
)
from turkish_linguistic_features.vocab import (
    LEXICAL_POS,
    NOUN_POS,
    POS_TAGS,
    THEMATIC_POS,
)


def _nan(x) -> bool:
    return isinstance(x, float) and math.isnan(x)


def _hepsi_nan(d: dict) -> bool:
    return bool(d) and all(_nan(v) for v in d.values())


# ── vocab.py ──────────────────────────────────────────────────────────


def test_vocab_hicbir_sey_import_etmez():
    """registry.py erken import ediyor — bağımlılık dairesel import yaratır."""
    agac = ast.parse(inspect.getsource(vocab))
    assert not [n for n in ast.walk(agac) if isinstance(n, (ast.Import, ast.ImportFrom))]


def test_vocab_sozlesme_sabitleri():
    assert len(POS_TAGS) == 13 and "PRON" not in POS_TAGS
    assert NOUN_POS == ("NOUN", "PROPN")
    assert LEXICAL_POS == ("NOUN", "PROPN", "VERB", "ADJ", "ADV")   # Ure 1971, Lu 2012
    assert THEMATIC_POS == ("NOUN", "PROPN", "VERB", "ADJ")         # QUITA, zarf yok
    assert not hasattr(vocab, "AUTOSEMANTIC_POS")
    assert not hasattr(vocab, "DEP_RELATIONS")                       # dep_* çıktı
    assert len(vocab.SENT_FINAL_POS) == 13


# ── POS oranları ve ızgara ────────────────────────────────────────────


def test_pos_oranlari_13_anahtar():
    assert len(pos_ratios([("a", "NOUN")])) == 13


def test_pos_orani_elle():
    pos = [("a", "NOUN"), ("b", "NOUN"), ("c", "VERB"), ("d", "PUNCT")]
    sonuc = pos_ratios(pos)
    assert sonuc["pos_noun"] == 0.5
    assert sonuc["pos_verb"] == 0.25


def test_nominal_verbal_ratio_elle():
    """AUX paydaya girmez: 3 NOUN / 1 VERB = 3."""
    pos = [("a", "NOUN"), ("b", "NOUN"), ("c", "NOUN"), ("d", "VERB"), ("e", "AUX")]
    assert nominal_verbal_ratio(pos)["nominal_verbal_ratio"] == 3.0
    assert _nan(nominal_verbal_ratio([("a", "NOUN")])["nominal_verbal_ratio"])   # fiil yok


def test_nominal_verbal_ratio_ozel_isim_isimdir():
    """Kaynaklarda "isim" = NOUN + PROPN (2026-09-16, Efe): 1 NOUN + 1 PROPN / 1 VERB."""
    pos = [("ev", "NOUN"), ("Ahmet", "PROPN"), ("geldi", "VERB")]
    assert nominal_verbal_ratio(pos)["nominal_verbal_ratio"] == 2.0


# ── fiil mesafesi ve activity ─────────────────────────────────────────


def test_fiil_mesafesi_elle_aux_sayilmaz():
    """VERB 0, 2, 6'da; 3'teki AUX fiil DEĞİL → mesafeler 2, 4 → ort 3, CV 1/3.

    AUX sayılsaydı konumlar 0, 2, 3, 6 → ortalama 2 çıkardı.
    """
    pos = [("a", "VERB"), ("b", "NOUN"), ("c", "VERB"), ("d", "AUX"),
           ("e", "NOUN"), ("f", "NOUN"), ("g", "VERB")]
    sonuc = verb_distance_stats(pos)
    assert sonuc["verb_dist_mean"] == 3.0
    assert sonuc["verb_dist_cv"] == 0.3333


def test_fiil_mesafesi_tek_fiilde_sifir():
    assert _hepsi_nan(verb_distance_stats([("a", "VERB")]))


def test_fiil_mesafesi_iki_fiilde_cv_nan():
    """Tek mesafeden değişkenlik ölçülmez (2026-09-16, Efe)."""
    sonuc = verb_distance_stats([("a", "VERB"), ("b", "NOUN"), ("c", "VERB")])
    assert sonuc["verb_dist_mean"] == 2.0
    assert _nan(sonuc["verb_dist_cv"])


def test_activity_ratio_elle_aux_sayilmaz():
    """2 VERB + 1 ADJ → 2/3. AUX sayılsaydı 3/4 = 0.75 çıkardı."""
    pos = [("a", "VERB"), ("b", "AUX"), ("c", "VERB"), ("d", "ADJ")]
    assert activity_ratio(pos)["activity_ratio"] == 0.66667


def test_activity_ratio_fiil_sifat_yoksa_nan():
    assert _nan(activity_ratio([("a", "NOUN")])["activity_ratio"])


# ── yoğunluk ve dağılım ───────────────────────────────────────────────


def test_lexical_density_bilinen_deger():
    """3 içerik + 1 işlev + 1 noktalama → 3/4. Payda kelime, token değil (Lu 2012)."""
    pos = [("kitap", "NOUN"), ("güzel", "ADJ"), ("okudu", "VERB"),
           ("ve", "CCONJ"), (".", "PUNCT")]
    assert lexical_density(pos)["lexical_density"] == 0.75


def test_lexical_density_sym_de_dusulur():
    """NON_WORD_POS iki etiket: PUNCT ve SYM. 1 içerik + 1 işlev → 0.5."""
    pos = [("kitap", "NOUN"), ("ve", "CCONJ"), ("%", "SYM")]
    assert lexical_density(pos)["lexical_density"] == 0.5


def test_lexical_density_yalniz_noktalamada_nan():
    """Kelime yoksa oran ölçülemez (K4)."""
    assert _nan(lexical_density([(".", "PUNCT"), ("%", "SYM")])["lexical_density"])


def test_lexical_density_nominal_verbal_ratio_ile_bagimsiz():
    """Aynı isim/fiil dengesi, farklı içerik/işlev dengesi."""
    az_islev = [("kitap", "NOUN"), ("okudu", "VERB")]
    cok_islev = [("kitap", "NOUN"), ("okudu", "VERB"),
                 ("ve", "CCONJ"), ("ile", "ADP"), ("bu", "DET")]
    assert (lexical_density(az_islev)["lexical_density"]
            > lexical_density(cok_islev)["lexical_density"])


def test_pos_dist_std_elle():
    """Hepsi NOUN → 13'lük oran vektörü [1, 0×12] → std = √12 / 13."""
    pos = [("a", "NOUN")] * 4
    assert pos_distribution_stats(pos, [["a"] * 4])["pos_dist_std"] == 0.26647


def test_pos_kl_div_elle():
    """[N N] ve [V V] cümleleri, belge N=V=0.5 → her cümle 1 bit → ortalama 1."""
    pos = [("a", "NOUN"), ("b", "NOUN"), ("c", "VERB"), ("d", "VERB")]
    assert pos_distribution_stats(pos, [["a", "b"], ["c", "d"]])["pos_kl_div"] == 1.0


def test_pos_kl_div_ozdes_cumlelerde_sifir():
    """Tüm cümleler aynı POS dizisi → her cümle belge dağılımına eşit."""
    pos = [("a", "NOUN"), ("b", "VERB")] * 3
    cumleler = [["a", "b"], ["a", "b"], ["a", "b"]]
    assert pos_distribution_stats(pos, cumleler)["pos_kl_div"] == 0.0


def test_pos_dist_std_tek_pos_hepsiyse_buyuk():
    tek = [("a", "NOUN")] * 4
    kari = [("a", "NOUN"), ("b", "VERB"), ("c", "ADJ"), ("d", "ADV")]
    c = [["a", "b", "c", "d"]]
    assert (pos_distribution_stats(tek, [["a"] * 4])["pos_dist_std"]
            > pos_distribution_stats(kari, c)["pos_dist_std"])


def test_pos_dagilim_hizalama_bozuksa_hata():
    """Token sayıları uyuşmuyor → ön işleme hatası, ValueError (2026-09-16, Efe)."""
    with pytest.raises(ValueError, match="not aligned"):
        pos_distribution_stats([("a", "NOUN")], [["a", "b", "c"]])


# ── cümle istatistikleri ──────────────────────────────────────────────


def test_esit_cumlelerde_cv_sifir_carpiklik_nan():
    """Hep aynı uzunluk → CV gerçekten 0; çarpıklık 0/0 → NaN."""
    sonuc = sentence_stats([["a", "b"], ["c", "d"]])
    assert sonuc["sentence_length_cv"] == 0.0
    assert _nan(sonuc["sent_len_skewness"])


def test_cumle_istatistikleri_elle():
    """Uzunluklar 2, 4 → ort 3, std 1, CV 1/3, medyan 3, simetrik → çarpıklık 0."""
    sonuc = sentence_stats([["a", "b"], ["c", "d", "e", "f"]])
    assert sonuc["avg_sent_len_word"] == 3.0
    assert sonuc["sentence_length_cv"] == 0.3333
    assert sonuc["med_sent_len"] == 3.0
    assert sonuc["sent_len_skewness"] == 0.0


def test_carpiklik_elle():
    """Uzunluklar 1, 1, 4 → m2 = 2, m3 = 2 → g1 = 2 / 2^1.5 = 0.7071."""
    sonuc = sentence_stats([["a"], ["b"], ["c", "d", "e", "f"]])
    assert sonuc["sent_len_skewness"] == 0.7071


def test_kisa_uzun_cumle_orani_esik_kullanir():
    cumleler = [["a"] * 3, ["a"] * 10, ["a"] * 40]
    sonuc = sentence_distribution_stats(cumleler, short_threshold=5, long_threshold=30)
    assert abs(sonuc["short_sent_ratio"] - 1 / 3) < 1e-6
    assert abs(sonuc["long_sent_ratio"] - 1 / 3) < 1e-6


def test_esik_sinirinda_kesin_kucukluk():
    """Tam 5 kelime, eşik 5 → kısa DEĞİL ("shorter than")."""
    sonuc = sentence_distribution_stats([["a"] * 5, ["a"] * 30], 5, 30)
    assert sonuc == {"short_sent_ratio": 0.0, "long_sent_ratio": 0.0}


def test_avg_sent_len_char_bosluklar_dahil():
    """"a bb" = 4, "abc" = 3 → 3.5"""
    assert avg_sent_len_char([["a", "bb"], ["abc"]])["avg_sent_len_char"] == 3.5


def test_sent_len_entropy_elle():
    assert sent_len_entropy([["a"] * 2, ["a"] * 2, ["a"] * 4, ["a"] * 4])["sent_len_entropy"] == 1.0
    assert sent_len_entropy([["a"] * 3] * 3)["sent_len_entropy"] == 0.0
    assert _nan(sent_len_entropy([["a"] * 3])["sent_len_entropy"])   # tek cümle


# ── paragraf ──────────────────────────────────────────────────────────


def test_paragraf_elle():
    """3 ve 2 kelime, 1'er cümle, 5 kelimede 2 paragraf."""
    sonuc = paragraph_stats("Bir iki üç.\n\nDört beş.")
    assert sonuc == {
        "para_len_mean": 2.5,
        "para_len_cv": 0.2,
        "sents_per_para_mean": 1.0,
        "sents_per_para_cv": 0.0,
        "para_count_norm": 400.0,
    }


def test_tek_paragrafta_cv_nan():
    sonuc = paragraph_stats("Bir iki üç. Dört.")
    assert sonuc["para_len_mean"] == 4.0
    assert _nan(sonuc["para_len_cv"]) and _nan(sonuc["sents_per_para_cv"])


def test_paragraf_bos_satirla_bolunur():
    metin = "Birinci paragraf.\n\nİkinci paragraf. İki cümle."
    assert paragraph_stats(metin)["sents_per_para_mean"] == 1.5


def test_tek_satir_sonu_paragraf_saymaz():
    """Bilinen sınırlama — belgeleyici test."""
    tek = paragraph_stats("Birinci satır.\nİkinci satır.")
    cift = paragraph_stats("Birinci satır.\n\nİkinci satır.")
    assert tek["para_count_norm"] > 0
    assert tek["sents_per_para_mean"] == 2.0
    assert cift["sents_per_para_mean"] == 1.0


def test_noktalamasiz_paragraf_bir_cumle_sayilir():
    assert paragraph_stats("Noktalama olmayan bir paragraf")["sents_per_para_mean"] == 1.0


def test_ucnokta_tek_cumle_sonu():
    assert paragraph_stats("Bekledi... Sonra gitti.")["sents_per_para_mean"] == 2.0


def test_paragraf_windows_satir_sonu():
    """\\r\\n de \\n gibi bölünmeli."""
    assert paragraph_stats("A.\n\nB.") == paragraph_stats("A.\r\n\r\nB.")


# ── paragraf sınırı yok: uyar, sayıyı değiştirme (2026-09-24, Efe) ────


def test_uzun_metin_paragraf_sinirsizsa_uyarir():
    """1000 kelimeyi geçen metin tek paragraf çıkıyorsa uyarı basılır.

    PDF/EPUB dökümü metinlerde satır sonları silinmiş oluyor; ölçüldü
    (2026-09-24): bir roman derlemesinde 163 dosyanın 120'sinde hiç boş satır
    yok. O dosyalarda `para_len_mean` bütün kitabın kelime sayısına eşitleniyor.
    """
    metin = " ".join(f"Cümle {i}." for i in range(600))      # 1200 kelime
    with pytest.warns(ParagraphStructureWarning, match="No paragraph boundary found"):
        sonuc = paragraph_stats(metin)
    # Karar (2026-09-24, Efe): sayılar değişmez, yalnız görünür kılınır.
    assert sonuc["para_len_mean"] == 1200.0
    assert _nan(sonuc["para_len_cv"])


def test_uyari_mesaji_kullanicinin_sayisini_verir():
    """Mesaj İngilizce ve kullanıcının kendi sayılarını taşır (2026-09-24, Efe)."""
    metin = " ".join(f"Cümle {i}." for i in range(600))
    with pytest.warns(ParagraphStructureWarning) as kayit:
        paragraph_stats(metin)
    mesaj = str(kayit[0].message)
    assert "1200 words" in mesaj and "600 sentences" in mesaj


def test_paragrafli_uzun_metin_uyarmaz():
    """Eşiği geçse de boş satır varsa uyarı yok — ölçüt paragraf, uzunluk değil."""
    metin = "\n\n".join(" ".join(f"Cümle {i}." for i in range(50)) for _ in range(12))
    with warnings.catch_warnings():
        warnings.simplefilter("error", ParagraphStructureWarning)
        assert paragraph_stats(metin)["para_len_cv"] == 0.0


def test_kisa_tek_paragraf_uyarmaz():
    """Öğretici ve docstring örnekleri uyarı basmamalı (2026-09-24, Efe).

    Ölçüldü: dokümandaki örnek metinler 7-24 kelime. Kısa metnin gerçekten
    tek paragraf olması normaldir; orada uyarı gürültü olur.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("error", ParagraphStructureWarning)
        assert paragraph_stats("Bu bir deneme metnidir. İkinci cümle.")["para_len_mean"] == 6.0
        assert paragraph_stats("Tek bir cümle var.")["para_len_mean"] == 4.0
        assert _nan(paragraph_stats("")["para_len_mean"])


# ── cümle uzunluğu: payda kelime, token değil ─────────────────────────


def test_cumle_uzunlugu_noktalamayi_saymaz():
    """["Ali", "geldi", "."] 3 token ama 2 kelime."""
    sonuc = sentence_stats([["Ali", "geldi", "."]])
    assert sonuc["avg_sent_len_word"] == 2.0
    assert sonuc["med_sent_len"] == 2.0


def test_kisa_uzun_cumle_orani_noktalamayi_saymaz():
    """5 + "." ve 30 + "!" → eşik kelimeyle ölçülür, ikisi de tam sınırda."""
    sonuc = sentence_distribution_stats([["a"] * 5 + ["."], ["a"] * 30 + ["!"]], 5, 30)
    assert sonuc == {"short_sent_ratio": 0.0, "long_sent_ratio": 0.0}


def test_sent_len_entropy_noktalamayi_saymaz():
    """Kelime sayıları 2 ve 2 → tek kategori → 0 bit."""
    assert sent_len_entropy([["a", "b", "."], ["c", "d"]])["sent_len_entropy"] == 0.0


def test_alfabesiz_cumle_sayilmaz():
    """"..." cümle değil; geriye tek cümle kalır, tek değerden yayılım ölçülmez."""
    sonuc = sentence_stats([["Ali", "geldi", "."], ["..."]])
    assert sonuc["avg_sent_len_word"] == 2.0
    assert _nan(sonuc["sentence_length_cv"])


def test_rakam_kelimedir_ama_tek_basina_cumle_degildir():
    """Sayı kelime sayılır (isalnum); ama alfabesiz cümle cümle sayılmaz (isalpha)."""
    assert sentence_stats([["Yıl", "1999", "."]])["avg_sent_len_word"] == 2.0
    assert _hepsi_nan(sentence_stats([["1999", "."]]))


def test_yalniz_noktalama_cumlesi_hepsi_nan():
    """Hiç cümle kalmazsa boş girdiyle aynı sonuç."""
    assert _hepsi_nan(sentence_stats([["..."], ["?!"]]))
    assert _hepsi_nan(sentence_distribution_stats([["..."]], 5, 30))
    assert _nan(sent_len_entropy([["..."], ["?!"]])["sent_len_entropy"])


# ── boş ve tek eleman ─────────────────────────────────────────────────


def test_bos_girdiler_hepsi_nan():
    for sonuc in (pos_ratios([]), nominal_verbal_ratio([]), verb_distance_stats([]), activity_ratio([]),
                  lexical_density([]), pos_distribution_stats([], []), sentence_stats([]),
                  sentence_distribution_stats([], 5, 30), avg_sent_len_char([]),
                  sent_len_entropy([]), paragraph_stats(""), paragraph_stats("  \n\n ")):
        assert _hepsi_nan(sonuc)


def test_tek_cumlede_yayilim_nan():
    sonuc = sentence_stats([["tek"]])
    assert sonuc["avg_sent_len_word"] == 1.0
    assert sonuc["med_sent_len"] == 1.0
    assert _nan(sonuc["sentence_length_cv"])
    assert _nan(sonuc["sent_len_skewness"])


# ── T12: soru cümlesi, zamir, kullanıcı n-gramları ────────────────────


def test_soru_cumlesi_orani():
    cumleler = [["Ne", "?"], ["Evet", "."]]
    assert question_per_sent(cumleler)["question_per_sent"] == 0.5


def test_soru_cumlesi_sondaki_tirnak_ve_parantez_atlanir():
    cumleler = [
        ["Geliyor", "musun", "?", '"'],
        ["Neden", "?", ")"],
        ["Ciddi", "misin", "?!"],
        ["Gel", "!?"],
        ["Bu", "mu", "?", "»"],
    ]
    assert question_per_sent(cumleler)["question_per_sent"] == 1.0


def test_soru_cumlesi_yalniz_sona_bakar():
    cumleler = [
        ["Ne", "?", "dedi", "."],       # ? ortada — sayılmaz
        ["Geliyor", "musun"],           # "mı" var ama ? yok — sayılmaz
        ["Tamam", '"', ")"],            # yalnız kapanış işaretleri
    ]
    assert question_per_sent(cumleler)["question_per_sent"] == 0.0


def test_zamir_orani_pron_etiketinden():
    pos = [("o", "PRON"), ("o", "DET"), ("ev", "NOUN"), (".", "PUNCT")]
    assert pronoun_freq(pos)["pronoun_freq"] == 0.25


def test_ngram_her_uzunlukta():
    tokens = ["ne", "var", "ki", "diye", "ne", "var"]
    sonuc = word_ngram_ratios(tokens, [["diye"], ["ne", "var", "ki"]])
    assert set(sonuc) == {"ng_diye", "ng_ne_var_ki"}


def test_ngram_paydasi_ayni_uzunluktaki_pencere_sayisi():
    tokens = ["ne", "var", "ki", "kimse", "gelmedi"]
    sonuc = word_ngram_ratios(tokens, [["ne", "var", "ki"], ["ki"]])
    assert sonuc["ng_ne_var_ki"] == round(1 / 3, 5)   # 3 üçlü pencere
    assert sonuc["ng_ki"] == 0.2                       # 5 tekli pencere


def test_ngram_ortusen_eslesmeler_sayilir():
    sonuc = word_ngram_ratios(["ha", "ha", "ha"], [["ha", "ha"]])
    assert sonuc["ng_ha_ha"] == 1.0                    # 2 eşleşme / 2 pencere


def test_ngram_kucuk_harf_ve_noktalama_atilir():
    tokens = ["Ne", ",", "var", "ki", "...", "İşte", "!"]
    sonuc = word_ngram_ratios(tokens, [["ne", "var", "ki"], ["işte"]])
    # noktalama atılınca: ne var ki işte → 2 üçlü pencere, 4 tekli pencere
    assert sonuc["ng_ne_var_ki"] == 0.5
    assert sonuc["ng_işte"] == 0.25


def test_ngram_kullanici_obegi_de_kucuk_harfe_iner():
    sonuc = word_ngram_ratios(["ırmak", "İzmir"], [["Irmak"], ["İZMİR"]])
    assert sonuc == {"ng_ırmak": 0.5, "ng_izmir": 0.5}


def test_ngram_ingilizcede_i_noktasiz_olmaz():
    sonuc = word_ngram_ratios(["I", "think"], [["I", "think"]], lang="en")
    assert sonuc == {"ng_i_think": 1.0}


def test_ngram_metinden_uzun_obek_nan():
    assert _hepsi_nan(word_ngram_ratios(["tek"], [["iki", "kelime"]]))


def test_ngram_bos_obek_hata():
    with pytest.raises(ValueError):
        word_ngram_ratios(["tek"], [[]])


def test_bos_girdiler():
    assert _nan(question_per_sent([])["question_per_sent"])
    assert _nan(pronoun_freq([])["pronoun_freq"])
    assert word_ngram_ratios([], []) == {}
    assert _hepsi_nan(word_ngram_ratios([], [["diye"]]))
