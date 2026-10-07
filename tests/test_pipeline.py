"""T21 — spaCy ``Preprocessor``: ham metin → ``ProcessedText``.

Parçalama testleri model gerektirmez. Model gerektirenler `tr_core_news_md` ve
`en_core_web_sm` kurulu değilse atlanır.
"""

import pytest

from turkish_linguistic_features.exceptions import ModelNotFoundError
from turkish_linguistic_features.pipeline.spacy_pipeline import Preprocessor, _split_chunks

# Veri kontrolü tests/conftest.py'de: eksikse atla, TLF_REQUIRE_MODELS=1 ise başarısız ol.
tr_model = pytest.mark.tr_model
en_model = pytest.mark.en_model


# ── parçalama — model GEREKTİRMEZ ─────────────────────────────────────


def test_kisa_metin_tek_parca():
    assert _split_chunks("kısa metin", 1000) == ["kısa metin"]


def test_uzun_metin_bolunur():
    metin = "cümle. " * 5000
    parcalar = _split_chunks(metin, 1000)
    assert len(parcalar) > 1
    assert all(len(p) <= 1100 for p in parcalar)


def test_parcalar_birlestiginde_metni_verir():
    metin = "Birinci cümle. İkinci cümle. Üçüncü cümle. " * 200
    assert "".join(_split_chunks(metin, 500)) == metin


def test_paragraf_sinirini_tercih_eder():
    metin = "A" * 400 + "\n\n" + "B" * 400
    assert _split_chunks(metin, 500)[0].endswith("\n\n")


def test_bosluksuz_uzun_metin_donmuyor():
    """Tek kelimelik 5000 karakterlik metin — sert kesim, sonsuz döngü yok."""
    assert len(_split_chunks("A" * 5000, 1000)) == 5


# ── Türkçe ────────────────────────────────────────────────────────────


@tr_model
def test_turkce_isleme():
    pt = Preprocessor(lang="tr").process("Ali kitabı okudu. Ayşe de geldi.")
    assert len(pt.surface_tokens) > 0
    assert len(pt.sentences_as_tokens) == 2
    assert pt.lang == "tr"
    assert pt.dep_data is not None


@tr_model
def test_lemma_noktalama_icermez():
    pt = Preprocessor(lang="tr").process("Ali geldi, gitti.")
    assert "." not in pt.lemma_tokens
    assert "." in pt.surface_tokens


@tr_model
def test_cumle_tokenlari_surface_ile_tutarli():
    pt = Preprocessor(lang="tr").process('Ali, kitabı okudu. "Güzeldi," dedi.')
    assert sum(len(s) for s in pt.sentences_as_tokens) == len(pt.surface_tokens)


@tr_model
def test_bas_gostergeleri_cumle_yerel():
    """Baş göstergesi belge değil **cümle** indeksinde olmalı.

    Belge indeksi kullanılırsa 500. cümledeki bir token'ın yay uzunluğu
    binlerce çıkar ve `arc_len_mean` anlamsızlaşır.
    """
    pt = Preprocessor(lang="tr").process("Ali geldi. Ayşe gitti. Ahmet kaldı.")
    for cumle in pt.dep_data:
        for _, _, _, bas in cumle:
            assert 0 <= bas < len(cumle)


@tr_model
def test_morfem_listesi_tokenlarla_hizali():
    """Her token için bir morfem listesi — hizalama bozulursa T16 çöker."""
    pt = Preprocessor(lang="tr").process("Kitaplarımızda gelmedim yazıyordu.")
    assert len(pt.morpheme_lists) == len(pt.surface_tokens)
    assert any(ms for ms in pt.morpheme_lists)


@tr_model
def test_morfem_uclusunun_sirasi():
    """Morpheme = (etiket, yüzey_ek, türetimsel_mi) — etiket POZİSYON 0'da."""
    pt = Preprocessor(lang="tr").process("Kitaplarımızda")
    etiketler = [m[0] for ms in pt.morpheme_lists for m in ms]
    assert "Loc" in etiketler                 # 'da' ekinin etiketi
    assert "da" not in etiketler              # yüzey biçimi pozisyon 0'da DEĞİL


@tr_model
def test_to_dict_extractor_ile_uyumlu():
    """Türkçe uçtan uca: taban şemanın tamamı, 211 anahtar."""
    from turkish_linguistic_features.features.extractor import _extract_features
    pt = Preprocessor(lang="tr").process(
        "Küçük çocuk bahçede top oynuyordu. Annesi ona seslendi ve eve çağırdı.\n\n"
        "Çocuk koşarak geldi, yorgun görünüyordu."
    )
    feats = _extract_features(**pt.to_dict())
    assert len(feats) == 211


@tr_model
def test_bos_metin():
    pt = Preprocessor(lang="tr").process("")
    assert pt.surface_tokens == ()


@tr_model
def test_uzun_metin_parcalanarak_isleniyor():
    """Parçalama sınırı aşan metinde token ve cümle sayısı korunuyor."""
    metin = "Ali kitabı okudu. Ayşe de geldi. " * 400
    pt = Preprocessor(lang="tr").process(metin)
    assert len(pt.sentences_as_tokens) == 800
    assert sum(len(s) for s in pt.sentences_as_tokens) == len(pt.surface_tokens)


@tr_model
def test_process_many():
    metinler = ["Ali kitabı okudu.", "Ayşe bahçede oynuyor."]
    sonuc = Preprocessor(lang="tr").process_many(metinler)
    assert len(sonuc) == 2
    assert [pt.raw_text for pt in sonuc] == metinler


# ── İngilizce ─────────────────────────────────────────────────────────


@en_model
def test_ingilizcede_morfem_listesi_bos():
    """Zeyrek İngilizce çözümlemiyor — grup hiç üretilmemeli (K11)."""
    pt = Preprocessor(lang="en").process("This is a test sentence.")
    assert pt.morpheme_lists == ()


@en_model
@pytest.mark.cmudict
def test_ingilizce_taban_sema():
    from turkish_linguistic_features.features.extractor import _extract_features
    pt = Preprocessor(lang="en").process(
        "The small child was playing in the garden. His mother called him inside.\n\n"
        "The child came running, looking tired."
    )
    assert len(_extract_features(**pt.to_dict())) == 183


# ── hata yolu ─────────────────────────────────────────────────────────


def test_olmayan_model_net_hata():
    """Mesaj elle çalıştırılabilir bir komut içermeli — `download_model()` yok."""
    prep = Preprocessor(lang="tr", model="boyle_bir_model_yok")
    with pytest.raises(ModelNotFoundError, match="pip install https://huggingface.co"):
        prep.process("test")


def test_ingilizce_model_hatasi_spacy_download_diyor():
    prep = Preprocessor(lang="en", model="boyle_bir_model_yok")
    with pytest.raises(ModelNotFoundError, match="python -m spacy download en_core_web_sm"):
        prep.process("test")


def test_chunk_chars_imzada_gecmiyor():
    """Uzun metnin kaç karakterde bölündüğü kullanıcının bilmesi gereken bir şey değil."""
    import inspect
    for fn in (Preprocessor.__init__, Preprocessor.process, Preprocessor.process_many):
        assert "chunk_chars" not in inspect.signature(fn).parameters


def test_varsayilan_cagri_hicbir_sey_yazdirmiyor(capsys):
    """Boru hattı katmanı sessiz — `show_progress` varsayılanı False."""
    Preprocessor(lang="tr", model="boyle_bir_model_yok")
    _split_chunks("A" * 3000, 1000)
    assert capsys.readouterr().out == ""
