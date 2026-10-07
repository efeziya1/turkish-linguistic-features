"""T24 — ``analyze()``: ham metin → öznitelik sözlüğü, tek çağrıda.

Önbellek testleri model GEREKTİRMEZ (``Preprocessor.__init__`` tembel);
gerisi ``tr_core_news_md`` kurulu değilse atlanır.
"""

import pytest

import turkish_linguistic_features as tlf
from turkish_linguistic_features import analyze

# Veri kontrolü tests/conftest.py'de: eksikse atla, TLF_REQUIRE_MODELS=1 ise başarısız ol.
tr_model = pytest.mark.tr_model
en_model = pytest.mark.en_model

TR_TABAN = 205
EN_TABAN = 177


# ── önbellek — model gerektirmez ──────────────────────────────────────


def test_ayni_ayarlar_ayni_preprocessor():
    from turkish_linguistic_features._analyze import _get_preprocessor
    assert _get_preprocessor("tr", None) is _get_preprocessor("tr", None)


def test_farkli_dil_farkli_preprocessor():
    """Dil önbellek anahtarında — aksi halde TR çağrısı EN örneğine düşer."""
    from turkish_linguistic_features._analyze import _get_preprocessor
    assert _get_preprocessor("tr", None) is not _get_preprocessor("en", None)


def test_farkli_model_farkli_preprocessor():
    from turkish_linguistic_features._analyze import _get_preprocessor
    assert _get_preprocessor("tr", None) is not _get_preprocessor("tr", "baska_model")


# ── temel davranış ────────────────────────────────────────────────────


@tr_model
def test_turkce_taban_sema():
    feats = analyze("Bu bir deneme metnidir. İkinci cümle burada.", lang="tr")
    assert isinstance(feats, dict)
    assert len(feats) == TR_TABAN
    assert all(isinstance(v, (int, float)) for v in feats.values())


@en_model
@pytest.mark.cmudict
def test_ingilizce_taban_sema():
    assert len(analyze("This is a test. A second sentence.", lang="en")) == EN_TABAN


@tr_model
def test_bos_metin_cokmez():
    assert isinstance(analyze("", lang="tr"), dict)


@tr_model
def test_model_bir_kez_yuklenir(monkeypatch):
    """Süre değil, ``spacy.load`` çağrı sayısı ölçülüyor.

    Süre testi makine yüküne ve disk önbelleğine bağlıdır, CI'da rastgele
    kırmızı verir.
    """
    import spacy

    from turkish_linguistic_features._analyze import _preprocessor_cache

    _preprocessor_cache.clear()
    sayac = {"n": 0}
    gercek = spacy.load

    def sahte(*a, **k):
        sayac["n"] += 1
        return gercek(*a, **k)

    monkeypatch.setattr(spacy, "load", sahte)
    analyze("İlk çağrı burada.", lang="tr")
    analyze("İkinci çağrı burada.", lang="tr")
    assert sayac["n"] == 1


# ── parametreler ──────────────────────────────────────────────────────


@tr_model
def test_gruplar_parametresi_daraltir():
    metin = "Bu bir deneme metnidir. İkinci cümle burada."
    assert len(analyze(metin, lang="tr", groups=["lexical"])) < len(analyze(metin, lang="tr"))


@tr_model
def test_bilinmeyen_grup_hata():
    with pytest.raises(ValueError, match="lexical"):
        analyze("Deneme.", lang="tr", groups=["boyle_bir_grup_yok"])


@tr_model
def test_custom_ngrams_yalniz_ng_sutunu_ekler():
    """Taban bir TAVAN değil — ama eklenen tek şey ``ng_*`` olmalı."""
    metin = "Bu bir deneme metnidir."
    taban = analyze(metin, lang="tr")
    genis = analyze(metin, lang="tr", custom_ngrams=[["bu", "bir"]])
    assert set(genis) - set(taban) == {"ng_bu_bir"}


@tr_model
def test_params_gecirilebiliyor():
    from turkish_linguistic_features import FeatureParams
    metin = "Bu bir deneme metnidir. " * 30
    p = FeatureParams(mattr_window=10)
    assert analyze(metin, lang="tr", params=p)["mattr"] != analyze(metin, lang="tr")["mattr"]


@tr_model
def test_varsayilan_cagri_ekrana_yazmaz(capsys):
    """Kütüphane kendiliğinden ekrana yazmaz — ``show_progress`` False."""
    analyze("Bu bir deneme metnidir.", lang="tr")
    assert capsys.readouterr().out == ""


def test_desteklenmeyen_dil():
    with pytest.raises(ValueError):
        analyze("Deneme.", lang="de")


# ── kabul ölçütleri ───────────────────────────────────────────────────


@tr_model
def test_zeyrek_grubu_gercekten_olculuyor():
    """24 ``morphological_zeyrek`` anahtarı üretilmeli ve hepsi NaN olmamalı.

    ``zeyrek`` zorunlu bağımlılık (K1) — "kurulu değil" senaryosu yok. Grup
    üretiliyor ama her değer NaN çıkıyorsa Zeyrek sessizce boş dönüyordur.
    """
    import math

    from turkish_linguistic_features.features.registry import STATIC_GROUP_KEYS

    feats = analyze("Kitaplarımızda yazıyordu. Gelmedim çünkü çağırmadılar.", lang="tr")
    zeyrek_anahtarlari = STATIC_GROUP_KEYS["morphological_zeyrek"]
    assert len(zeyrek_anahtarlari) == 24
    assert set(zeyrek_anahtarlari) <= set(feats)
    olculen = [feats[k] for k in zeyrek_anahtarlari if not math.isnan(feats[k])]
    assert olculen, "morphological_zeyrek'in tamamı NaN — Zeyrek boş dönüyor"


@en_model
@pytest.mark.cmudict
def test_ingilizcede_zeyrek_grubu_hic_yok(recwarn):
    """K11 — İngilizcede grup üretilmez ve bunun için uyarı da verilmez."""
    from turkish_linguistic_features.features.registry import STATIC_GROUP_KEYS

    feats = analyze("This is a test. A second sentence here.", lang="en")
    assert not (set(STATIC_GROUP_KEYS["morphological_zeyrek"]) & set(feats))
    assert not [w for w in recwarn if "zeyrek" in str(w.message).lower()]


def test_chunk_chars_ve_clear_cache_yok():
    """İkisi de bilinçli olarak dışarıda (2026-08-25 ve T24 planı)."""
    import inspect

    import turkish_linguistic_features as paket
    from turkish_linguistic_features import _analyze

    assert "chunk_chars" not in inspect.signature(analyze).parameters
    assert not hasattr(paket, "clear_cache")
    assert not hasattr(_analyze, "clear_cache")


@tr_model
@pytest.mark.slow
def test_cok_uzun_metin_cokmuyor():
    """5 MB metin — parçalama devreye girmeli, bellek patlamamalı.

    ``chunk_chars`` imzada olmadığı için bu davranış ayarlanmıyor, sadece
    çalışıyor (2026-08-25).

    🔴 **Ölçüldü: 660 sn (2026-09-19), 1108 sn (2026-09-24)** — 11 ile 18
    dakika. Aradaki farkın nedeni araştırılmadı; ikisi de aynı makinede,
    tek fark oturumun yükü. Elle çalıştıran hangi büyüklüğü beklediğini
    bilsin diye ikisi de burada.

    ``slow`` işaretli ve ``pyproject.toml``'daki ``addopts`` onu varsayılan
    koşudan **çıkarır** (2026-09-24'e kadar künye bunu söylüyordu ama ayar
    bağlı değildi, test her koşuda çalışıyordu ve süitin %87'siydi).
    Hepsini koşmak için: ``pytest -m ""``.

    Bu aynı zamanda bir performans bilgisi — ``analyze()`` 5 MB'lık tek bir
    metne 11-18 dakika harcıyor. T28'de ``docs/limitations.md``'ye girmeli;
    o dosya henüz yok.
    """
    feats = analyze("Bu bir cümledir. " * 300_000, lang="tr")
    assert len(feats) == TR_TABAN


# ── model yoksa: analyze() net hata ───────────────────────────────────


@pytest.mark.parametrize("lang, komut", [
    ("tr", "pip install https://huggingface.co"),
    ("en", "python -m spacy download en_core_web_sm"),
])
def test_analyze_model_yoksa_kurulum_komutunu_soyler(lang, komut):
    """Model adı bilerek var olmayan: gerçek modeller kurulu olsa da hep koşar.

    ``groups=["lexical"]`` — İngilizcede cmudict denetimi devreye girmesin,
    sınanan şey spaCy modelinin yokluğu.
    """
    with pytest.raises(tlf.ModelNotFoundError, match=komut):
        analyze("Deneme.", lang=lang, model="boyle_bir_model_yok", groups=["lexical"])
