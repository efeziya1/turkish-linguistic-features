import ast
import inspect
import math
import warnings

import pytest

from turkish_linguistic_features import ParagraphStructureWarning, vocab
from turkish_linguistic_features.features.syntactic import (
    activity_ratio,
    lexical_density,
    paragraph_stats,
    pos_distribution_stats,
    pos_ratios,
    pronoun_ratio,
    question_sent_ratio,
    sent_len_char_mean,
    sent_len_entropy,
    sentence_distribution_stats,
    sentence_stats,
    verb_distance_stats,
    word_ngram_counts,
    word_ngram_matches,
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
    assert len(POS_TAGS) == 12 and "PRON" not in POS_TAGS and "PUNCT" not in POS_TAGS
    assert NOUN_POS == ("NOUN", "PROPN")
    assert LEXICAL_POS == ("NOUN", "PROPN", "VERB", "ADJ", "ADV")   # Ure 1971, Lu 2012
    assert THEMATIC_POS == ("NOUN", "PROPN", "VERB", "ADJ")         # QUITA, zarf yok
    assert not hasattr(vocab, "AUTOSEMANTIC_POS")
    assert not hasattr(vocab, "DEP_RELATIONS")                       # dep_* çıktı
    assert len(vocab.SENT_FINAL_POS) == 13


# ── POS oranları ve ızgara ────────────────────────────────────────────


def test_pos_oranlari_12_anahtar():
    assert len(pos_ratios([("a", "NOUN")])) == 12


def test_pos_orani_elle():
    pos = [("a", "NOUN"), ("b", "NOUN"), ("c", "VERB"), ("d", "PUNCT")]
    sonuc = pos_ratios(pos)
    assert sonuc["pos_noun_ratio"] == 0.5
    assert sonuc["pos_verb_ratio"] == 0.25


# ── fiil mesafesi ve activity ─────────────────────────────────────────


def test_fiil_mesafesi_elle_aux_sayilmaz():
    """VERB 0, 2, 6'da; 3'teki AUX fiil DEĞİL → mesafeler 2, 4 → ort 3.

    AUX sayılsaydı konumlar 0, 2, 3, 6 → ortalama 2 çıkardı.
    """
    pos = [("a", "VERB"), ("b", "NOUN"), ("c", "VERB"), ("d", "AUX"),
           ("e", "NOUN"), ("f", "NOUN"), ("g", "VERB")]
    sonuc = verb_distance_stats(pos)
    assert sonuc["verb_dist_mean"] == 3.0


def test_fiil_mesafesi_tek_fiilde_sifir():
    assert _hepsi_nan(verb_distance_stats([("a", "VERB")]))


def test_fiil_mesafesi_iki_fiilde_tek_mesafe():
    sonuc = verb_distance_stats([("a", "VERB"), ("b", "NOUN"), ("c", "VERB")])
    assert sonuc["verb_dist_mean"] == 2.0


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
    """Hepsi NOUN → 12'lik oran vektörü [1, 0×11] → std = √11 / 12."""
    pos = [("a", "NOUN")] * 4
    assert pos_distribution_stats(pos, [["a"] * 4])["posddev"] == 0.27639


def test_pos_kl_div_elle():
    """[N N] ve [V V] cümleleri, belge N=V=0.5 → her cümle ln 2 nat (1 bit) → ortalama ln 2."""
    pos = [("a", "NOUN"), ("b", "NOUN"), ("c", "VERB"), ("d", "VERB")]
    assert pos_distribution_stats(pos, [["a", "b"], ["c", "d"]])["posdiv"] == round(math.log(2), 5)


def test_pos_kl_div_ozdes_cumlelerde_sifir():
    """Tüm cümleler aynı POS dizisi → her cümle belge dağılımına eşit."""
    pos = [("a", "NOUN"), ("b", "VERB")] * 3
    cumleler = [["a", "b"], ["a", "b"], ["a", "b"]]
    assert pos_distribution_stats(pos, cumleler)["posdiv"] == 0.0


def test_pos_dist_std_tek_pos_hepsiyse_buyuk():
    tek = [("a", "NOUN")] * 4
    kari = [("a", "NOUN"), ("b", "VERB"), ("c", "ADJ"), ("d", "ADV")]
    c = [["a", "b", "c", "d"]]
    assert (pos_distribution_stats(tek, [["a"] * 4])["posddev"]
            > pos_distribution_stats(kari, c)["posddev"])


def test_pos_dagilim_hizalama_bozuksa_hata():
    """Token sayıları uyuşmuyor → ön işleme hatası, ValueError (2026-09-16, Efe)."""
    with pytest.raises(ValueError, match="not aligned"):
        pos_distribution_stats([("a", "NOUN")], [["a", "b", "c"]])


# ── cümle istatistikleri ──────────────────────────────────────────────


def test_cumle_istatistikleri_elle():
    """Uzunluklar 2, 4 → ort 3, medyan 3; çarpıklık ve CV kalktı (Efe)."""
    sonuc = sentence_stats([["a", "b"], ["c", "d", "e", "f"]])
    assert sonuc == {"sent_len_mean": 3.0, "sent_len_median": 3.0, "sent_count": 2.0}


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
    assert sent_len_char_mean([["a", "bb"], ["abc"]])["sent_len_char_mean"] == 3.5


def test_sent_len_entropy_elle():
    iki_uzunluk = [["a"] * 2, ["a"] * 2, ["a"] * 4, ["a"] * 4]
    assert sent_len_entropy(iki_uzunluk)["sent_len_entropy"] == round(math.log(2), 5)
    assert sent_len_entropy([["a"] * 3] * 3)["sent_len_entropy"] == 0.0
    assert _nan(sent_len_entropy([["a"] * 3])["sent_len_entropy"])   # tek cümle


# ── paragraf ──────────────────────────────────────────────────────────


def test_paragraf_elle():
    """3 ve 2 kelime, 1'er cümle, 5 kelimede 2 paragraf."""
    sonuc = paragraph_stats("Bir iki üç.\n\nDört beş.")
    assert sonuc == {
        "para_count": 2.0,
        "para_len_mean": 2.5,
        "sents_per_para_mean": 1.0,
    }


def test_tek_paragraf():
    sonuc = paragraph_stats("Bir iki üç. Dört.")
    assert sonuc["para_len_mean"] == 4.0 and sonuc["sents_per_para_mean"] == 2.0


def test_paragraf_bos_satirla_bolunur():
    metin = "Birinci paragraf.\n\nİkinci paragraf. İki cümle."
    assert paragraph_stats(metin)["sents_per_para_mean"] == 1.5


def test_tek_satir_sonu_paragraf_saymaz():
    """Bilinen sınırlama — belgeleyici test."""
    tek = paragraph_stats("Birinci satır.\nİkinci satır.")
    cift = paragraph_stats("Birinci satır.\n\nİkinci satır.")
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
        assert paragraph_stats(metin)["para_len_mean"] == 100.0


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
    assert sonuc["sent_len_mean"] == 2.0
    assert sonuc["sent_len_median"] == 2.0


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
    assert sonuc["sent_len_mean"] == 2.0


def test_rakam_kelimedir_ama_tek_basina_cumle_degildir():
    """Sayı kelime sayılır (isalnum); ama alfabesiz cümle cümle sayılmaz (isalpha)."""
    assert sentence_stats([["Yıl", "1999", "."]])["sent_len_mean"] == 2.0
    assert _hepsi_nan(sentence_stats([["1999", "."]]))


def test_yalniz_noktalama_cumlesi_hepsi_nan():
    """Hiç cümle kalmazsa boş girdiyle aynı sonuç."""
    assert _hepsi_nan(sentence_stats([["..."], ["?!"]]))
    assert _hepsi_nan(sentence_distribution_stats([["..."]], 5, 30))
    assert _nan(sent_len_entropy([["..."], ["?!"]])["sent_len_entropy"])


# ── boş ve tek eleman ─────────────────────────────────────────────────


def test_bos_girdiler_hepsi_nan():
    for sonuc in (pos_ratios([]), verb_distance_stats([]), activity_ratio([]),
                  lexical_density([]), pos_distribution_stats([], []), sentence_stats([]),
                  sentence_distribution_stats([], 5, 30), sent_len_char_mean([]),
                  sent_len_entropy([]), paragraph_stats(""), paragraph_stats("  \n\n ")):
        assert _hepsi_nan(sonuc)


def test_tek_cumlede_yayilim_nan():
    sonuc = sentence_stats([["tek"]])
    assert sonuc["sent_len_mean"] == 1.0
    assert sonuc["sent_len_median"] == 1.0


# ── T12: soru cümlesi, zamir, kullanıcı n-gramları ────────────────────


def test_soru_cumlesi_orani():
    cumleler = [["Ne", "?"], ["Evet", "."]]
    assert question_sent_ratio(cumleler)["question_sent_ratio"] == 0.5


def test_soru_cumlesi_sondaki_tirnak_ve_parantez_atlanir():
    cumleler = [
        ["Geliyor", "musun", "?", '"'],
        ["Neden", "?", ")"],
        ["Ciddi", "misin", "?!"],
        ["Gel", "!?"],
        ["Bu", "mu", "?", "»"],
    ]
    assert question_sent_ratio(cumleler)["question_sent_ratio"] == 1.0


def test_soru_cumlesi_yalniz_sona_bakar():
    cumleler = [
        ["Ne", "?", "dedi", "."],       # ? ortada — sayılmaz
        ["Geliyor", "musun"],           # "mı" var ama ? yok — sayılmaz
        ["Tamam", '"', ")"],            # yalnız kapanış işaretleri
    ]
    assert question_sent_ratio(cumleler)["question_sent_ratio"] == 0.0


def test_zamir_orani_pron_etiketinden():
    pos = [("o", "PRON"), ("o", "DET"), ("ev", "NOUN"), (".", "PUNCT")]
    assert pronoun_ratio(pos)["pronoun_ratio"] == 0.25


def _c(*kelimeler: str) -> list[tuple[str, str]]:
    """Etiketsiz cümle: ``kelime/ETİKET`` yazılmamışsa etiket X."""
    return [tuple(k.split("/")) if "/" in k else (k, "X") for k in kelimeler]


def test_ngram_her_uzunlukta():
    sonuc = word_ngram_counts([_c("ne", "var", "ki", "diye", "ne", "var")],
                              [["diye"], ["ne", "var", "ki"]])
    assert sonuc == {"ngram_diye_count": 1.0, "ngram_ne_var_ki_count": 1.0}


def test_ngram_duz_sayim():
    """Değer oran değil, sayım (2026-10-08, Efe)."""
    sonuc = word_ngram_counts([_c("ne", "var", "ki", "kimse", "ki")], [["ki"]])
    assert sonuc["ngram_ki_count"] == 2.0


def test_ngram_ortusen_eslesmeler_sayilir():
    sonuc = word_ngram_counts([_c("ha", "ha", "ha")], [["ha", "ha"]])
    assert sonuc["ngram_ha_ha_count"] == 2.0


def test_ngram_etiket_eslesir_anahtarda_buyuk_harf():
    """Büyük harfli UD etiketi o etiketli herhangi bir kelimeyle eşleşir."""
    cumleler = [_c("Kadın/NOUN", "geldi/VERB"), _c("Kadın/NOUN", "güldü/VERB", "ve/CCONJ",
                                                  "kadın/NOUN", "oturdu/VERB")]
    sonuc = word_ngram_counts(cumleler, [["kadın", "VERB"], ["NOUN", "VERB"]])
    assert sonuc == {"ngram_kadın_VERB_count": 3.0, "ngram_NOUN_VERB_count": 3.0}


def test_ngram_cumle_sinirini_asmaz():
    """``geldi. Kadın``: fiil ile sonraki cümlenin ismi yan yana sayılmaz."""
    cumleler = [_c("o/PRON", "geldi/VERB"), _c("kadın/NOUN", "güldü/VERB")]
    assert word_ngram_counts(cumleler, [["VERB", "NOUN"]])["ngram_VERB_NOUN_count"] == 0.0


def test_ngram_kucuk_harfli_etiket_adi_kelimedir():
    cumleler = [_c("noun/NOUN", "verb/VERB")]
    sonuc = word_ngram_counts(cumleler, [["noun"]], lang="en")
    assert sonuc == {"ngram_noun_count": 1.0}


def test_ngram_kullanici_obegi_de_kucuk_harfe_iner():
    sonuc = word_ngram_counts([_c("ırmak", "İzmir")], [["Irmak"], ["İZMİR"]])
    assert sonuc == {"ngram_ırmak_count": 1.0, "ngram_izmir_count": 1.0}


def test_ngram_ingilizcede_i_noktasiz_olmaz():
    sonuc = word_ngram_counts([_c("I", "think")], [["I", "think"]], lang="en")
    assert sonuc == {"ngram_i_think_count": 1.0}


def test_ngram_metinden_uzun_obek_sifir():
    assert word_ngram_counts([_c("tek")], [["iki", "kelime"]]) == {"ngram_iki_kelime_count": 0.0}


def test_ngram_bos_obek_hata():
    with pytest.raises(ValueError):
        word_ngram_counts([_c("tek")], [[]])


def test_ngram_eslesmeleri_sikliga_gore_sirali():
    """Büyükten küçüğe; eşitlikte metindeki ilk geçiş (2026-10-08, Efe)."""
    cumleler = [_c("kadın/NOUN", "güldü/VERB"), _c("Kadın/NOUN", "geldi/VERB"),
                _c("kadın/NOUN", "oturdu/VERB"), _c("kadın/NOUN", "geldi/VERB")]
    sonuc = word_ngram_matches(cumleler, ["kadın", "VERB"])
    assert list(sonuc.items()) == [("kadın geldi", 2), ("kadın güldü", 1), ("kadın oturdu", 1)]


def test_ngram_eslesmeleri_toplami_sayima_esit():
    cumleler = [_c("ha", "ha", "ha"), _c("ha", "ha")]
    eslesme = word_ngram_matches(cumleler, ["ha", "ha"])
    assert eslesme == {"ha ha": 3}
    assert sum(eslesme.values()) == word_ngram_counts(cumleler, [["ha", "ha"]])["ngram_ha_ha_count"]


def test_ngram_eslesmesi_yoksa_bos():
    assert word_ngram_matches([_c("tek")], ["iki", "kelime"]) == {}


def test_bos_girdiler():
    assert _nan(question_sent_ratio([])["question_sent_ratio"])
    assert _nan(pronoun_ratio([])["pronoun_ratio"])
    assert word_ngram_counts([], []) == {}
    assert word_ngram_counts([], [["diye"]]) == {"ngram_diye_count": 0.0}
