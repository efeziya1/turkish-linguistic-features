"""Kalyoncu (2025) K1–K4 ve bileşenleri: elle kurulmuş Zeyrek çözümlemeleriyle (model gerekmez)."""

import math
from collections import Counter

import pytest

from turkish_linguistic_features.features.kalyoncu import (
    KALYONCU_KEYS,
    _bir_kez_oran,
    fiilimsi_mi,
    govde,
    kalyoncu_features,
    kalyoncu_list,
    okunus_sozcukleri,
    ozel_ad_mi,
    sayi_mi,
    cozumleme_sec,
)
from turkish_linguistic_features.features.registry import STATIC_GROUP_KEYS, describe_feature
from turkish_linguistic_features.params import FeatureParams

EV = (("Noun", "ev", False), ("A3sg", "", False))
EVE = (("Noun", "ev", False), ("A3sg", "", False), ("Dat", "e", False))
GELDI = (("Verb", "gel", False), ("Past", "di", False), ("A3sg", "", False))
GITTI = (("Verb", "git", False), ("Past", "ti", False), ("A3sg", "", False))
GELEBILDI = (("Verb", "gel", False), ("Able", "ebil", True), ("Verb", "", False),
             ("Past", "di", False), ("A3sg", "", False))
KITAPCILAR = (("Noun", "kitap", False), ("A3sg", "", False), ("Agt", "çı", True),
              ("Noun", "", False), ("A3pl", "lar", False))
OGRETMENLIGI = (("Noun", "öğretmen", False), ("A3sg", "", False), ("Ness", "liğ", True),
                ("Noun", "", False), ("A3sg", "", False), ("Acc", "i", False))
KUCULTULMEK = (("Verb", "küçül", False), ("Caus", "t", True), ("Verb", "", False),
               ("Pass", "ül", True), ("Verb", "", False), ("Inf1", "mek", True),
               ("Noun", "", False), ("A3sg", "", False))
OKUYARAK = (("Verb", "oku", False), ("ByDoingSo", "yarak", True), ("Adv", "", False))
OKURKEN = (("Verb", "oku", False), ("Aor", "r", False), ("While", "ken", True), ("Adv", "", False))
OGRENCIYKEN = (("Noun", "öğrenci", False), ("A3sg", "", False), ("Zero", "", True),
               ("Verb", "", False), ("While", "yken", True), ("Adv", "", False))
EVDEYDI = (("Noun", "ev", False), ("A3sg", "", False), ("Loc", "de", False),
           ("Zero", "", True), ("Verb", "", False), ("Past", "ydi", False), ("A3sg", "", False))
HIKAYE = (("Noun", "hikâye", False), ("A3sg", "", False))
AHMET = (("Noun", "Ahmet", False), ("A3sg", "", False))
BILINMEYEN = (("Unk", "xqzt", False),)


def _girdi(*cumleler):
    """Tümce tümce (sözcük, etiket, sözlükbirim, morfemler) → kalyoncu_features girdileri."""
    words, pos, lemmas, morphemes, sentences = [], [], [], [], []
    for cumle in cumleler:
        sentences.append([w for w, *_ in cumle])
        for w, etiket, lem, m in cumle:
            words.append(w)
            pos.append((w, etiket))
            lemmas.append(lem)
            morphemes.append(m)
    return words, pos, lemmas, morphemes, sentences


# ── liste ─────────────────────────────────────────────────────────────

def test_liste_4600_sozcuk_kaynaktaki_yazimla():
    """s.71 "toplam 4600 kelime"; şapka ayırt edici (hala ≠ hâlâ), Çita kaynaktaki gibi."""
    liste = kalyoncu_list()
    assert len(liste) == 4600
    assert len(set(liste)) == 4600
    assert {"a", "aa", "aaa", "o", "iş", "be", "hala", "hâlâ", "çita", "kılmak",
            "hoşçakal", "yurtdışı"} <= set(liste)
    assert "çıta" not in liste
    assert all(w == w.lower() and "*" not in w and "(" not in w for w in liste)


# ── sayıların okunuşu ─────────────────────────────────────────────────

@pytest.mark.parametrize(("birim", "sayi"), [
    ("1968", 5),          # bin dokuz yüz altmış sekiz (s.xiii)
    ("1999'da", 5),       # ek okunuşa yapışır
    ("%50", 2),           # yüzde elli
    ("10:30", 2),         # on otuz
    ("3.", 1),            # üçüncü
    ("3,5", 3),           # üç virgül beş
    ("100m", 2),          # yüz metre
    ("1990lar", 4),       # bin dokuz yüz doksanlar
    ("4-5", 2),
])
def test_rakamli_sozcuk_okunusunun_sozcukleriyle_sayilir(birim, sayi):
    assert len(okunus_sozcukleri(birim)) == sayi


# ── gövde ve fiilimsi ─────────────────────────────────────────────────

@pytest.mark.parametrize(("m", "lemma", "kelime", "beklenen"), [
    (EVE, "ev", "eve", ("ev", False)),                          # çekim atılır
    (KITAPCILAR, "kitap", "kitapçılar", ("kitapçı", False)),    # yapım eki kalır
    (OGRETMENLIGI, "öğretmen", "öğretmenliği", ("öğretmenliğ", False)),
    (KUCULTULMEK, "küçül", "küçültülmek", ("küçül", True)),     # çatıda durulur
    (GELEBILDI, "gel", "gelebildi", ("gel", True)),             # birleşik fiilde durulur
    (EVDEYDI, "ev", "evdeydi", ("ev", False)),                  # ek eylemde durulur
    (BILINMEYEN, "xqzt", "Xqzt", ("xqzt", False)),
])
def test_govde(m, lemma, kelime, beklenen):
    assert govde(m, lemma, kelime) == beklenen


def test_fiilimsi_ek_eylemli_ad_sayilmaz():
    assert fiilimsi_mi(OKUYARAK)
    assert fiilimsi_mi(OKURKEN)
    assert not fiilimsi_mi(OGRENCIYKEN)
    assert not fiilimsi_mi(GELDI)
    assert not fiilimsi_mi(BILINMEYEN)


# ── ölçüler ───────────────────────────────────────────────────────────

def test_ocu_sayiyi_okunusuyla_sayar_harfsiz_tumceyi_saymaz():
    """"Bu bir tümce. 1999. Bitti." → 3 + 5 + 1 = 9 sözcük, 2 tümce, OCU 4,5 (2026-10-27, Efe)."""
    girdi = _girdi(
        [("Bu", "DET", "bu", (("Det", "bu", False),)),
         ("bir", "DET", "bir", (("Det", "bir", False),)),
         ("tümce", "NOUN", "tümce", (("Noun", "tümce", False), ("A3sg", "", False)))],
        [("1999", "NUM", "1999", (("Num", "1999", False),))],
        [("Bitti", "VERB", "bit", (("Verb", "bit", False), ("Past", "ti", False),
                                   ("A3sg", "", False)))],
    )
    sonuc = kalyoncu_features(*girdi)
    assert sonuc["kalyoncu_ocu"] == 4.5


def test_kl_ozel_ad_ve_sayi_liste_ici_sapka_silinir():
    """Ahmet (PROPN) ve sayı paya girmez; "hikaye" listedeki "hikâye" ile eşleşir."""
    girdi = _girdi([("Ahmet", "PROPN", "ahmet", AHMET),
                    ("eve", "NOUN", "ev", EVE),
                    ("hikaye", "NOUN", "hikâye", HIKAYE),
                    ("12", "NUM", "12", (("Num", "12", False),)),
                    ("kitapçılar", "NOUN", "kitap", KITAPCILAR),
                    ("geldi", "VERB", "gel", GELDI)])
    sonuc = kalyoncu_features(*girdi)
    # 7 sözcük (12 = on iki); liste dışı yalnız "kitapçılar" (gövde kitapçı listede yok).
    assert sonuc["kalyoncu_kl"] == round(100 / 7, 4)


def test_kl_fiil_mastarla_ve_yumusamis_unsuz_sertlesmis_bulunur():
    girdi = _girdi([("gelebildi", "VERB", "gel", GELEBILDI),
                    ("küçültülmek", "VERB", "küçül", KUCULTULMEK),
                    ("öğretmenliği", "NOUN", "öğretmen", OGRETMENLIGI)])
    assert kalyoncu_features(*girdi)["kalyoncu_kl"] == 0.0


def test_kco_fiilimsi_ya_da_iki_fiil():
    """Tek fiil basit; fiilimsi ya da iki fiil karmaşık; ek eylemli ad -ken fiilimsi değil."""
    girdi = _girdi(
        [("Geldi", "VERB", "gel", GELDI)],
        [("Okuyarak", "VERB", "oku", OKUYARAK), ("geldi", "VERB", "gel", GELDI)],
        [("Geldi", "VERB", "gel", GELDI), ("gitti", "VERB", "git", GITTI)],
        [("Öğrenciyken", "NOUN", "öğrenci", OGRENCIYKEN), ("geldi", "VERB", "gel", GELDI)],
    )
    sonuc = kalyoncu_features(*girdi)
    assert sonuc["kalyoncu_kco"] == 50.0
    assert sonuc["kalyoncu_yco"] == 2.5          # 1 fiilimsi / 4 tümce × 10


def test_ttr_bir_kez_gecen_govde_cekim_ayni_sozcuk():
    """ev, eve, evdeydi tek gövde (ev); geldi bir kez → 1/4 × 100."""
    girdi = _girdi([("ev", "NOUN", "ev", EV), ("eve", "NOUN", "ev", EVE),
                    ("evdeydi", "VERB", "ev", EVDEYDI), ("geldi", "VERB", "gel", GELDI)])
    assert kalyoncu_features(*girdi)["kalyoncu_ttr"] == 25.0


def test_ttr_kayan_pencere_dogrudan_tanimla_ayni():
    govdeler = [f"g{i % 7}" if i % 3 else f"t{i}" for i in range(40)]
    pencere = 10
    beklenen = sum(
        sum(1 for s in Counter(govdeler[i:i + pencere]).values() if s == 1)
        for i in range(len(govdeler) - pencere + 1)
    ) * 100 / ((len(govdeler) - pencere + 1) * pencere)
    assert _bir_kez_oran(govdeler, pencere) == pytest.approx(beklenen)
    assert _bir_kez_oran(govdeler[:pencere], pencere) == pytest.approx(
        100 * sum(1 for s in Counter(govdeler[:pencere]).values() if s == 1) / pencere)


def test_formuller_tablo_katsayilariyla():
    girdi = _girdi([("Ahmet", "PROPN", "ahmet", AHMET), ("eve", "NOUN", "ev", EVE),
                    ("geldi", "VERB", "gel", GELDI)])
    s = kalyoncu_features(*girdi)
    kl, ttr, kco, yco, ocu = (s[k] for k in KALYONCU_KEYS[:5])
    assert s["kalyoncu_k1"] == pytest.approx(-29.829 + 0.508 * kl + 1.191 * ttr + 0.733 * kco
                                             - 0.66 * ocu, abs=1e-4)
    assert s["kalyoncu_k2"] == pytest.approx(25.457 + 0.877 * kl + 0.668 * ttr + 0.333 * ocu,
                                             abs=1e-4)
    assert s["kalyoncu_k3"] == pytest.approx(25.153 + 0.834 * kl + 0.686 * ttr + 0.226 * yco,
                                             abs=1e-4)
    assert s["kalyoncu_k4"] == pytest.approx(43.368 + 1.008 * kl + 0.624 * ocu, abs=1e-4)


def test_bos_metin_nan_ve_harfsiz_tumce():
    assert all(math.isnan(v) for v in kalyoncu_features(*_girdi()).values())
    sadece_sayi = kalyoncu_features(*_girdi([("1999", "NUM", "1999", (("Num", "1999", False),))]))
    assert sadece_sayi["kalyoncu_kl"] == 0.0
    assert math.isnan(sadece_sayi["kalyoncu_ocu"]) and math.isnan(sadece_sayi["kalyoncu_k1"])


def test_pencere_parametresi_dogrulanir():
    with pytest.raises(ValueError, match="kalyoncu_ttr_window"):
        kalyoncu_features(*_girdi(), FeatureParams(kalyoncu_ttr_window=0))


def test_kayit_yalniz_turkce_ve_readability_grubunda():
    assert set(KALYONCU_KEYS) <= set(STATIC_GROUP_KEYS["readability"])
    for k in KALYONCU_KEYS:
        assert describe_feature(k)["citation"].startswith("Kalyoncu (2025) p.")
    assert describe_feature("kalyoncu_ttr")["params"] == ("kalyoncu_ttr_window",)


# ── 0.3.0 düzeltmeleri: yazıyla sayı, özel ad, çözümleme seçimi ──────

IKI = (("Num", "iki", False), ("A3sg", "", False))
IKISI = (("Num", "iki", False), ("A3sg", "", False), ("P3pl", "si", False), ("Noun", "", False))
UCUNCU = (("Num", "üç", False), ("Ord", "üncü", True), ("Adj", "", False))
BESER = (("Num", "beş", False), ("Distrib", "er", True), ("Adv", "", False))
BESER_AD = (("Noun", "beşer", False), ("A3sg", "", False))
ON_SAYI = (("Num", "on", False), ("A3sg", "", False), ("Gen", "un", False), ("Noun", "", False))
ONUN_ZAMIR = (("Pron", "o", False), ("A3sg", "", False), ("Gen", "nun", False))
XQZT_FIIL = (("Verb", "xqzt", False), ("Imp", "", False), ("A2sg", "", False))
XQZT_AD = (("Noun", "xqzt", False), ("A3sg", "", False))


@pytest.mark.parametrize(("etiket", "m", "alt", "beklenen"), [
    ("NUM", IKI, (), True),                             # spaCy NUM
    ("NUM", IKISI, (), True),                           # çekimli
    ("ADJ", UCUNCU, (), True),                          # sıra: seçilen çözümlemenin kökü Num
    ("NOUN", BESER_AD, ((BESER, "beş"),), True),        # üleştirme, spaCy ad dese de
    ("PRON", ONUN_ZAMIR, ((ON_SAYI, "on"),), False),    # onun ≠ on
    ("VERB", GELDI, ((ON_SAYI, "on"),), False),
    ("NOUN", EV, (), False),
])
def test_sayi_mi_yazili_sayi(etiket, m, alt, beklenen):
    assert sayi_mi(etiket, m, alt) is beklenen


def test_kl_yazili_sayi_paya_girmez_paydada_kalir():
    """"xqzt" liste dışı; "iki", "ikisi", "üçüncü", "beşer" sayı: payda 5, pay 1."""
    girdi = _girdi([("iki", "NUM", "iki", IKI), ("ikisi", "NUM", "iki", IKISI),
                    ("üçüncü", "ADJ", "üç", UCUNCU), ("beşer", "ADV", "beş", BESER),
                    ("xqzt", "NOUN", "xqzt", XQZT_AD)])
    assert kalyoncu_features(*girdi)["kalyoncu_kl"] == 20.0


@pytest.mark.parametrize(("sozcuk", "etiket", "tumce_basi", "beklenen"), [
    ("Derya", "NOUN", False, True),            # büyük harf, tümce başında değil
    ("İstanbul'da", "NOUN", False, True),      # düz kesme
    ("İstanbul’da", "NOUN", False, True),      # eğri kesme
    ("Hassan'ı", "X", False, True),
    ("Derya", "NOUN", True, False),            # tümce başı: yalnız PROPN'e kalır
    ("Derya", "PROPN", True, True),
    ("kitap", "NOUN", False, False),
    ("ankara'da", "NOUN", False, False),
])
def test_ozel_ad_mi(sozcuk, etiket, tumce_basi, beklenen):
    assert ozel_ad_mi(sozcuk, etiket, tumce_basi) is beklenen


def test_kl_buyuk_harfli_ad_paya_girmez_tumce_basindaki_girer():
    """"Ben Derya'yı gördüm": Derya'yı özel ad (pay dışı). "Xqzt geldi" tümce başı: pay içi."""
    girdi = _girdi(
        [("Ben", "PRON", "ben", (("Pron", "ben", False), ("A1sg", "", False))),
         ("Derya'yı", "NOUN", "Derya", AHMET), ("geldi", "VERB", "gel", GELDI)],
        [("Xqzt", "NOUN", "xqzt", XQZT_AD), ("geldi", "VERB", "gel", GELDI)],
    )
    assert kalyoncu_features(*girdi)["kalyoncu_kl"] == 20.0     # 1 / 5


def test_cozumleme_secimi_spacy_turune_uyan_ilk_cozumleme():
    alt = ((XQZT_FIIL, "xqzt"), (XQZT_AD, "xqzt"))
    assert cozumleme_sec("NOUN", XQZT_FIIL, "xqzt", alt)[0] == XQZT_AD     # uyan ilk
    assert cozumleme_sec("VERB", XQZT_FIIL, "xqzt", alt)[0] == XQZT_FIIL
    assert cozumleme_sec("ADJ", XQZT_FIIL, "xqzt", alt)[0] == XQZT_FIIL    # uyan yok: ilk
    assert cozumleme_sec("NOUN", XQZT_FIIL, "xqzt", ())[0] == XQZT_FIIL    # çözümleme yok


def test_secilen_cozumleme_govdeyi_ve_tumce_sayimini_belirler():
    """Zeyrek ilk çözümlemesi fiil; spaCy ad der: ad seçilir, fiil sayılmaz, KCO değişir."""
    cumle = [("geldi", "VERB", "gel", GELDI), ("xqzt", "NOUN", "xqzt", XQZT_FIIL)]
    girdi = _girdi(cumle)
    assert kalyoncu_features(*girdi)["kalyoncu_kco"] == 100.0              # iki fiil
    alt = [(), ((XQZT_FIIL, "xqzt"), (XQZT_AD, "xqzt"))]
    assert kalyoncu_features(*girdi, alternatives=alt)["kalyoncu_kco"] == 0.0
