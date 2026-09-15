import ast
import inspect

from turkish_linguistic_features.features import vocab
from turkish_linguistic_features.features.syntactic import (
    activity_ratio,
    avg_sent_len_char,
    lexical_density,
    nominal_verbal_ratio,
    paragraph_stats,
    pos_bigram_ratios,
    pos_distribution_stats,
    pos_ratios,
    sent_len_entropy,
    sentence_distribution_stats,
    sentence_stats,
    verb_distance_stats,
)
from turkish_linguistic_features.features.vocab import AUTOSEMANTIC_POS, POS_TAGS

# ── vocab.py ──────────────────────────────────────────────────────────


def test_vocab_hicbir_sey_import_etmez():
    """registry.py erken import ediyor — bağımlılık dairesel import yaratır."""
    agac = ast.parse(inspect.getsource(vocab))
    assert not [n for n in ast.walk(agac) if isinstance(n, (ast.Import, ast.ImportFrom))]


def test_vocab_sozlesme_sabitleri():
    assert len(POS_TAGS) == 13 and "PRON" not in POS_TAGS
    assert AUTOSEMANTIC_POS == ("NOUN", "PROPN", "VERB", "ADJ", "ADV")
    assert len(vocab.DEP_RELATIONS) == 38 and vocab.DEP_RELATIONS[-1] == "other"
    assert len(vocab.SENT_FINAL_POS) == 13


# ── POS oranları ve ızgara ────────────────────────────────────────────


def test_pos_oranlari_13_anahtar():
    assert len(pos_ratios([("a", "NOUN")])) == 13


def test_pos_orani_elle():
    pos = [("a", "NOUN"), ("b", "NOUN"), ("c", "VERB"), ("d", "PUNCT")]
    sonuc = pos_ratios(pos)
    assert sonuc["pos_noun"] == 0.5
    assert sonuc["pos_verb"] == 0.25


def test_pos_bigram_her_zaman_169():
    for pos in ([], [("a", "NOUN")], [("a", "NOUN"), ("b", "VERB")]):
        assert len(pos_bigram_ratios(pos)) == 169


def test_pos_bigram_gorulmeyen_cift_sifir():
    sonuc = pos_bigram_ratios([("a", "NOUN"), ("b", "VERB")])
    assert sonuc["posbg_NOUN_VERB"] == 1.0
    assert sonuc["posbg_ADJ_ADV"] == 0.0


def test_nominal_verbal_ratio_elle():
    """AUX paydaya girmez: 3 NOUN / 1 VERB = 3."""
    pos = [("a", "NOUN"), ("b", "NOUN"), ("c", "NOUN"), ("d", "VERB"), ("e", "AUX")]
    assert nominal_verbal_ratio(pos)["nominal_verbal_ratio"] == 3.0
    assert nominal_verbal_ratio([("a", "NOUN")])["nominal_verbal_ratio"] == 0.0


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
    assert verb_distance_stats([("a", "VERB")]) == {"verb_dist_mean": 0.0, "verb_dist_cv": 0.0}


def test_activity_ratio_elle_aux_sayilmaz():
    """2 VERB + 1 ADJ → 2/3. AUX sayılsaydı 3/4 = 0.75 çıkardı."""
    pos = [("a", "VERB"), ("b", "AUX"), ("c", "VERB"), ("d", "ADJ")]
    assert activity_ratio(pos)["activity_ratio"] == 0.66667


def test_activity_ratio_fiil_sifat_yoksa_cokmez():
    assert activity_ratio([("a", "NOUN")])["activity_ratio"] == 0.0


# ── yoğunluk ve dağılım ───────────────────────────────────────────────


def test_lexical_density_bilinen_deger():
    """3 içerik + 1 noktalama → 0.75"""
    pos = [("kitap", "NOUN"), ("güzel", "ADJ"), ("okudu", "VERB"), (".", "PUNCT")]
    assert lexical_density(pos)["lexical_density"] == 0.75


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


def test_pos_dagilim_hizalama_bozuksa_sifir():
    """Token sayıları uyuşmuyor → çökme yok, 0.0."""
    sonuc = pos_distribution_stats([("a", "NOUN")], [["a", "b", "c"]])
    assert sonuc == {"pos_dist_std": 0.0, "pos_kl_div": 0.0}


# ── cümle istatistikleri ──────────────────────────────────────────────


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


# ── boş ve tek eleman ─────────────────────────────────────────────────


def test_bos_girdiler_hepsi_sifir():
    for sonuc in (pos_ratios([]), pos_bigram_ratios([]),
                  nominal_verbal_ratio([]), verb_distance_stats([]), activity_ratio([]),
                  lexical_density([]), pos_distribution_stats([], []), sentence_stats([]),
                  sentence_distribution_stats([], 5, 30), avg_sent_len_char([]),
                  sent_len_entropy([]), paragraph_stats(""), paragraph_stats("  \n\n ")):
        assert sonuc and all(v == 0.0 for v in sonuc.values())


def test_tek_cumle_cokmez():
    sonuc = sentence_stats([["tek"]])
    assert sonuc["avg_sent_len_word"] == 1.0
    assert sonuc["sentence_length_cv"] == 0.0
    assert sonuc["sent_len_skewness"] == 0.0
