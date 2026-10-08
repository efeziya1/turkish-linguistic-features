import math

import pytest

from turkish_linguistic_features.features.punctuation import (
    all_caps_word_ratio,
    char_freq_vector,
    consecutive_punct_ratio,
    digit_ratio,
    punct_char_ratio,
    punct_count,
    punct_entropy,
    punct_variety,
    punctuation_ratios,
    uppercase_ratio,
    whitespace_ratio,
)

# ── harf vektörü ──────────────────────────────────────────────────────


def test_karakter_vektoru_tr_29_harf():
    sonuc = char_freq_vector("merhaba dünya", lang="tr")
    assert len(sonuc) == 29
    assert "char_ç_ratio" in sonuc and "char_ğ_ratio" in sonuc


def test_karakter_vektoru_en_26_harf():
    sonuc = char_freq_vector("hello world", lang="en")
    assert len(sonuc) == 26
    assert "char_ç_ratio" not in sonuc and "char_w_ratio" in sonuc


def test_karakter_oranlari_toplami_bire_yakin():
    sonuc = char_freq_vector("merhaba", lang="tr")
    assert abs(sum(sonuc.values()) - 1.0) < 0.01


def test_ingilizce_q_w_x_sayilir():
    """"wax" → w, a, x üçte bir."""
    sonuc = char_freq_vector("wax", lang="en")
    assert sonuc["char_w_ratio"] == sonuc["char_a_ratio"] == sonuc["char_x_ratio"] == 0.333333


def test_turkce_buyuk_harf_kurali():
    """TR: I → ı, İ → i. Python'un lower()'ı ikisini de 'i' yapardı."""
    sonuc = char_freq_vector("Iİ", lang="tr")
    assert sonuc["char_ı_ratio"] == 0.5 and sonuc["char_i_ratio"] == 0.5


def test_alfabe_disi_harf_paydaya_girmez():
    """TR alfabesinde w yok: "wa" → yalnız a sayılır → 1.0."""
    assert char_freq_vector("wa", lang="tr")["char_a_ratio"] == 1.0


# ── noktalama oranları (işaretler içindeki pay, 2026-10-08) ───────────


def test_noktalama_orani_elle_hesap():
    # 2 virgül + 1 nokta = 3 işaret → virgül 2/3
    sonuc = punctuation_ratios("a, b, c.")
    assert sonuc["punct_comma_ratio"] == round(2 / 3, 6)
    assert sonuc["punct_period_ratio"] == round(1 / 3, 6)


def test_on_anahtar():
    """On tür; `punct_total_ratio` 2026-10-08'de kaldırıldı (Efe)."""
    assert len(punctuation_ratios("")) == 10


def test_paylarin_toplami_bir():
    sonuc = punctuation_ratios("Geldi, gitti... Sonra? (Hayır!)")   # , … ? ( ! ) = 6 işaret
    assert sum(sonuc.values()) == pytest.approx(1.0, abs=1e-5)
    assert sonuc["punct_paren_ratio"] == round(2 / 6, 6)


def test_uc_nokta_tek_isaret_ve_nokta_sayilmaz():
    """"..." ve "…" ikisi de bir üç nokta; içindeki noktalar nokta değil. Sondaki "." bir nokta."""
    sonuc = punctuation_ratios("Bekledi... Sonra… gitti.")
    assert sonuc["punct_ellipsis_ratio"] == round(2 / 3, 6)
    assert sonuc["punct_period_ratio"] == round(1 / 3, 6)


def test_tire_uc_bicim():
    assert punctuation_ratios("a-b – c — d.")["punct_dash_ratio"] == 0.75


def test_parantez_iki_isaret():
    assert punctuation_ratios("(a) (b).")["punct_paren_ratio"] == 0.8


def test_tirnak_genis_kume_kesme_isareti_haric():
    """“ ” « » ve kelime sınırındaki ' ' tırnak: 6, artı , ve . → 6/8. Ankara’ya'daki ’ kesme işareti."""
    metin = "“Ankara’ya” dedi, «evet» 'hayır'."
    assert punctuation_ratios(metin)["punct_quote_ratio"] == 0.75


def test_soru_unlem_iki_nokta_noktali_virgul():
    sonuc = punctuation_ratios("a? b! c: d;")
    assert (sonuc["punct_question_ratio"], sonuc["punct_exclamation_ratio"],
            sonuc["punct_colon_ratio"], sonuc["punct_semicolon_ratio"]) == (0.25, 0.25, 0.25, 0.25)


# ── karakter düzeyi oranlar ───────────────────────────────────────────


def test_digit_ratio_elle():
    assert digit_ratio("a1b2")["digit_ratio"] == 0.5


def test_whitespace_ratio_elle():
    assert whitespace_ratio("a b")["whitespace_ratio"] == 0.333333


def test_punct_char_ratio_uc_nokta_tek_isaret():
    """"a...b": 1 işaret / 5 karakter."""
    assert punct_char_ratio("a...b")["punct_char_ratio"] == 0.2


def test_punct_count_uc_nokta_tek_isaret():
    """"Ne... Gel!": üç nokta bir işaret + ünlem = 2. Boş metinde NaN."""
    assert punct_count("Ne... Gel!")["punct_count"] == 2.0
    assert punct_count("ev")["punct_count"] == 0.0
    assert math.isnan(punct_count("")["punct_count"])


def test_punct_char_ratio_kesme_isareti_sayilmaz():
    assert punct_char_ratio("Ankara’ya")["punct_char_ratio"] == 0.0


def test_punct_entropy_elle():
    """Virgül + nokta eşit → ln 2 nat (1 bit); hep üç nokta → 0."""
    assert punct_entropy("a, b.")["punct_entropy"] == round(math.log(2), 6)
    assert punct_entropy("a... b…")["punct_entropy"] == 0.0


def test_punct_entropy_tirnak_bicimi_etkilemez():
    """Düz ve kıvrık tırnak aynı tür: tipografi entropiyi değiştirmemeli.

    İkisinde de 4 tırnak + 1 virgül + 1 nokta → aynı dağılım, sıfırdan büyük.
    """
    duz = punct_entropy('"a", "b".')["punct_entropy"]
    assert duz > 0.0
    assert duz == punct_entropy("“a”, «b».")["punct_entropy"]


def test_ardisik_noktalama():
    """'!!!' üç işaretin hepsi bir dizide → oran 1.0"""
    assert consecutive_punct_ratio("Ne!!!")["consecutive_punct_ratio"] == 1.0


def test_uc_nokta_tek_basina_ardisik_degil():
    assert consecutive_punct_ratio("Bekledi...")["consecutive_punct_ratio"] == 0.0
    assert consecutive_punct_ratio("a, b. c")["consecutive_punct_ratio"] == 0.0


def test_noktalama_cesitliligi():
    """3 farklı işaret kullanılmış."""
    assert punct_variety("a. b, c!")["punct_variety"] == 3.0


def test_cesitlilik_tur_duzeyinde():
    """“ ” ve « » hepsi tırnak türü → 1."""
    assert punct_variety("“a” «b»")["punct_variety"] == 1.0


# ── büyük harf ────────────────────────────────────────────────────────


def test_uppercase_ratio_payda_harfli_tokenler():
    """Harfli tokenler: Ali, geldi → 1/2. "." ve "123" paydaya girmez."""
    assert uppercase_ratio(["Ali", "geldi", ".", "123"])["uppercase_ratio"] == 0.5


def test_all_caps_en_az_iki_harf():
    """NATO sayılır; tek harfli A ve I sayılmaz → 1/4."""
    assert all_caps_word_ratio(["NATO", "A", "ev", "I"])["all_caps_word_ratio"] == 0.25


def test_turkce_buyuk_harf_isupper():
    assert all_caps_word_ratio(["İZMİR", "IŞIK"])["all_caps_word_ratio"] == 1.0


# ── boş girdi ─────────────────────────────────────────────────────────


def _hepsi_nan(d: dict) -> bool:
    return bool(d) and all(isinstance(v, float) and math.isnan(v) for v in d.values())


def test_bos_girdiler_hepsi_nan():
    for sonuc in (punctuation_ratios("a b"), punct_char_ratio(""),
                  digit_ratio(""), whitespace_ratio(""), punct_entropy(""),
                  consecutive_punct_ratio(""), punct_variety(""), uppercase_ratio([]),
                  all_caps_word_ratio([".", "1"]), char_freq_vector("", "tr"),
                  char_freq_vector("123 !", "en")):
        assert _hepsi_nan(sonuc)


def test_isaretsiz_metinde():
    """İşaret yok: entropi ve bitişiklik paydası boş → NaN; çeşit sayısı gerçekten 0."""
    assert _hepsi_nan(punct_entropy("bir iki"))
    assert _hepsi_nan(consecutive_punct_ratio("bir iki"))
    assert punct_variety("bir iki")["punct_variety"] == 0.0
    assert punct_char_ratio("bir iki")["punct_char_ratio"] == 0.0
