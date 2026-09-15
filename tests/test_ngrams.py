from turkish_linguistic_features.features.ngrams import skipgram_entropy


def test_skipgram_atlar():
    """['a','b','c','d'] skip=1 → (a,c), (b,d)"""
    sonuc = skipgram_entropy(["a", "b", "c", "d"], skip=1)
    assert sonuc["skipgram_1_entropy"] == 1.0    # 2 eşit olasılıklı çift → 1 bit


def test_skip_2_uc_kelime_atlar():
    """skip=2 → (a,d), (b,e) → 1 bit; anahtar adı skip'i taşır."""
    assert skipgram_entropy(["a", "b", "c", "d", "e"], skip=2) == {"skipgram_2_entropy": 1.0}


def test_bilinen_deger_elle():
    """x y x z x y, skip=1 → (x,x) (y,z) (x,x) (z,y) → p = ½ ¼ ¼ → 1.5 bit."""
    assert skipgram_entropy(["x", "y", "x", "z", "x", "y"], 1)["skipgram_1_entropy"] == 1.5


def test_tekrarli_metinde_entropi_sifir():
    assert skipgram_entropy(["a"] * 150, 1)["skipgram_1_entropy"] == 0.0


def test_noktalama_atlamadan_once_cikarilir():
    """["Ev", ",", "güzel", ".", "ev"] → [ev, güzel, ev] → tek çift (ev, ev) → 0.

    Noktalama kalsaydı 3 farklı çift → log₂3.
    """
    assert skipgram_entropy(["Ev", ",", "güzel", ".", "ev"], 1)["skipgram_1_entropy"] == 0.0


def test_turkce_kucuk_harf():
    """TR'de "Irmak" → "ırmak": çiftler (ırmak,ırmak)×2 + (a,b) → 0.9183 bit.

    Python'un str.lower()'ı "irmak" yapardı → 3 farklı çift → 1.585.
    """
    tokens = ["Irmak", "a", "ırmak", "b", "ırmak"]
    assert skipgram_entropy(tokens, 1, lang="tr")["skipgram_1_entropy"] == 0.91830
    assert skipgram_entropy(tokens, 1, lang="en")["skipgram_1_entropy"] == 1.58496


def test_bos_ve_kisa_girdiler():
    assert skipgram_entropy([], 1)["skipgram_1_entropy"] == 0.0
    assert skipgram_entropy(["a", "b"], 1)["skipgram_1_entropy"] == 0.0   # skip+1'den kısa
    assert skipgram_entropy([".", ","], 1)["skipgram_1_entropy"] == 0.0   # hepsi noktalama
