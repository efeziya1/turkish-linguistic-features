from turkish_linguistic_features.features.punctuation import (
    all_caps_word_ratio,
    char_freq_vector,
    consecutive_punct_ratio,
    digit_ratio,
    punct_density,
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
    assert "char_ç" in sonuc and "char_ğ" in sonuc


def test_karakter_vektoru_en_26_harf():
    sonuc = char_freq_vector("hello world", lang="en")
    assert len(sonuc) == 26
    assert "char_ç" not in sonuc and "char_w" in sonuc


def test_karakter_oranlari_toplami_bire_yakin():
    sonuc = char_freq_vector("merhaba", lang="tr")
    assert abs(sum(sonuc.values()) - 1.0) < 0.01


def test_ingilizce_q_w_x_sayilir():
    """"wax" → w, a, x üçte bir."""
    sonuc = char_freq_vector("wax", lang="en")
    assert sonuc["char_w"] == sonuc["char_a"] == sonuc["char_x"] == 0.333333


def test_turkce_buyuk_harf_kurali():
    """TR: I → ı, İ → i. Python'un lower()'ı ikisini de 'i' yapardı."""
    sonuc = char_freq_vector("Iİ", lang="tr")
    assert sonuc["char_ı"] == 0.5 and sonuc["char_i"] == 0.5


def test_alfabe_disi_harf_paydaya_girmez():
    """TR alfabesinde w yok: "wa" → yalnız a sayılır → 1.0."""
    assert char_freq_vector("wa", lang="tr")["char_a"] == 1.0


# ── noktalama oranları (kelime başına) ────────────────────────────────


def test_noktalama_orani_elle_hesap():
    # 10 kelime, 2 virgül → 0.2
    sonuc = punctuation_ratios("a, b, c", total_words=10)
    assert sonuc["punc_,_ratio"] == 0.2


def test_on_anahtar():
    assert len(punctuation_ratios("", total_words=0)) == 10


def test_uc_nokta_tek_isaret_ve_nokta_sayilmaz():
    """"..." ve "…" ikisi de bir üç nokta; içindeki noktalar nokta değil. Sondaki "." bir nokta."""
    sonuc = punctuation_ratios("Bekledi... Sonra… gitti.", total_words=10)
    assert sonuc["punc_ellipsis_ratio"] == 0.2
    assert sonuc["punc_._ratio"] == 0.1


def test_tire_uc_bicim():
    assert punctuation_ratios("a-b – c — d", total_words=10)["punc_-_ratio"] == 0.3


def test_parantez_iki_isaret():
    assert punctuation_ratios("(a) (b)", total_words=10)["punc_paren_ratio"] == 0.4


def test_tirnak_genis_kume_kesme_isareti_haric():
    """“ ” « » ve kelime sınırındaki ' ' tırnak: 6. Ankara’ya'daki ’ kesme işareti."""
    metin = "“Ankara’ya” dedi, «evet» 'hayır'."
    assert punctuation_ratios(metin, total_words=10)["punc_quote_ratio"] == 0.6


def test_soru_unlem_iki_nokta_noktali_virgul():
    sonuc = punctuation_ratios("a? b! c: d;", total_words=10)
    assert (sonuc["punc_question_ratio"], sonuc["punc_!_ratio"],
            sonuc["punc_:_ratio"], sonuc["punc_;_ratio"]) == (0.1, 0.1, 0.1, 0.1)


# ── karakter düzeyi oranlar ───────────────────────────────────────────


def test_digit_ratio_elle():
    assert digit_ratio("a1b2")["digit_vs_all"] == 0.5


def test_whitespace_ratio_elle():
    assert whitespace_ratio("a b")["whitespace_ratio"] == 0.333333


def test_punct_density_uc_nokta_tek_isaret():
    """"a...b": 1 işaret / 5 karakter."""
    assert punct_density("a...b")["punct_density"] == 0.2


def test_punct_density_kesme_isareti_sayilmaz():
    assert punct_density("Ankara’ya")["punct_density"] == 0.0


def test_punct_entropy_elle():
    """Virgül + nokta eşit → 1 bit; hep üç nokta → 0."""
    assert punct_entropy("a, b.")["punct_entropy"] == 1.0
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


def test_bos_metin_cokmez():
    assert digit_ratio("")["digit_vs_all"] == 0.0
    assert punct_entropy("")["punct_entropy"] == 0.0
    assert whitespace_ratio("")["whitespace_ratio"] == 0.0


def test_bos_girdiler_hepsi_sifir():
    for sonuc in (punctuation_ratios("a, b", total_words=0), punct_density(""),
                  consecutive_punct_ratio(""), punct_variety(""), uppercase_ratio([]),
                  all_caps_word_ratio([".", "1"]), char_freq_vector("", "tr"),
                  char_freq_vector("123 !", "en")):
        assert sonuc and all(v == 0.0 for v in sonuc.values())
