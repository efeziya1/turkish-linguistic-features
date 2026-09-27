"""``analyze_corpus`` — korpus zincirini tek çağrıda kapatan giriş noktası.

2026-09-23'te eklendi. Öncesinde kullanıcı ``load_corpus()`` → döngü →
``analyze()`` → ``records_to_csv()`` zincirini kendisi kuruyordu; ortadaki
döngü public API'de yoktu, son halka da ``__all__``'da değildi.

Testler kısa metinlerle koşuyor: burada ölçülen şey öznitelik değerleri
değil (onlar ``test_analyze.py``'nin işi), **zincirin şekli** — kayıt
alanları, parça sayısı, parametre geçişi.
"""

import pytest

import turkish_linguistic_features as tlf
from turkish_linguistic_features._corpus import analyze_corpus

# Her test Türkçe analiz yapıyor (conftest.py'deki kural).
pytestmark = pytest.mark.tr_model


def _korpus_yaz(kok, metin_uzunlugu: int = 120) -> None:
    """``Etiket_Başlık.txt`` düzeninde iki dosyalık minik korpus."""
    cumle = "Kedi bahçede oturdu ve uzun uzun etrafı seyretti. "
    tekrar = cumle * (metin_uzunlugu // len(cumle.split()) + 1)
    (kok / "Anlatı_bir.txt").write_text(tekrar, encoding="utf-8")
    (kok / "Deneme_iki.txt").write_text(tekrar, encoding="utf-8")


def test_kayit_alanlari_duz_sozluk(tmp_path):
    """Kayıt = üstveri + öznitelikler, iç içe değil — save_csv'ye doğrudan gider."""
    _korpus_yaz(tmp_path)
    satirlar = analyze_corpus(tmp_path, lang="tr", segment_size=30)

    assert satirlar, "korpus parçalanmalıydı"
    ilk = satirlar[0]
    assert {"label", "source", "segment_id"} <= set(ilk)
    # Öznitelikler üstveriyle aynı düzlemde: iç içe sözlük yok.
    assert len(ilk) > 100, "öznitelikler kayda katılmamış"
    assert all(not isinstance(d, dict) for d in ilk.values())


def test_etiket_dosya_adindan_geliyor(tmp_path):
    _korpus_yaz(tmp_path)
    satirlar = analyze_corpus(tmp_path, lang="tr", segment_size=30)
    assert {s["label"] for s in satirlar} == {"Anlatı", "Deneme"}


def test_segment_size_parca_sayisini_belirliyor(tmp_path):
    """Küçük parça boyu daha çok kayıt üretmeli — parçalama gerçekten geçiyor."""
    _korpus_yaz(tmp_path, metin_uzunlugu=200)
    az = analyze_corpus(tmp_path, lang="tr", segment_size=100)
    cok = analyze_corpus(tmp_path, lang="tr", segment_size=25)
    assert len(cok) > len(az)


def test_groups_analyze_e_geciyor(tmp_path):
    """``groups`` daraltması zincirden geçmeli, yoksa parametre yutulmuş olur."""
    _korpus_yaz(tmp_path)
    dar = analyze_corpus(tmp_path, lang="tr", segment_size=30,
                         groups=["punctuation"])
    genis = analyze_corpus(tmp_path, lang="tr", segment_size=30)
    assert len(dar[0]) < len(genis[0])


def test_parca_cikmazsa_bos_liste(tmp_path):
    """Metin segment_size'dan kısaysa hata değil, boş liste — olağan sonuç."""
    (tmp_path / "A_b.txt").write_text("Kısa metin.", encoding="utf-8")
    assert analyze_corpus(tmp_path, lang="tr", segment_size=5000) == []


def test_olmayan_yol_filenotfound(tmp_path):
    import pytest
    with pytest.raises(FileNotFoundError):
        analyze_corpus(tmp_path / "yok", lang="tr")


def test_show_progress_varsayilan_sessiz(tmp_path, capsys):
    """K9: kütüphane çağrılmadan ekrana yazmaz."""
    _korpus_yaz(tmp_path)
    analyze_corpus(tmp_path, lang="tr", segment_size=30)
    assert capsys.readouterr().out == ""


def test_show_progress_acikken_parca_sayaci(tmp_path, capsys):
    _korpus_yaz(tmp_path)
    satirlar = analyze_corpus(tmp_path, lang="tr", segment_size=30,
                              show_progress=True)
    cikti = capsys.readouterr().out
    assert f"[1/{len(satirlar)}]" in cikti
    assert cikti.count("[") == len(satirlar), "her parça için bir satır"


def test_save_csv_zinciri_kapatiyor(tmp_path):
    """analyze_corpus → save_csv: ara dönüşüm gerekmiyor."""
    _korpus_yaz(tmp_path)
    satirlar = analyze_corpus(tmp_path, lang="tr", segment_size=30)
    cikti = tmp_path / "sonuc.csv"
    tlf.save_csv(satirlar, cikti)

    satir_sayisi = len(cikti.read_text(encoding="utf-8").strip().splitlines())
    assert satir_sayisi == len(satirlar) + 1, "başlık + her kayıt bir satır"


def test_public_yuzeyde(tmp_path):
    """Sözleşme: analyze_corpus ve save_csv __all__'da, load_corpus değil."""
    assert "analyze_corpus" in tlf.__all__
    assert "save_csv" in tlf.__all__
    assert not hasattr(tlf, "load_corpus")
    assert not hasattr(tlf, "records_to_csv")


def test_varsayilan_dosya_dosya_isler(tmp_path):
    """segment_size verilmezse bölme yok — her dosya tek satır."""
    _korpus_yaz(tmp_path)
    satirlar = analyze_corpus(tmp_path, lang="tr")

    assert len(satirlar) == 2, "iki dosya, iki satır"
    assert all(s["segment_id"] == 0 for s in satirlar)
    assert {s["source"] for s in satirlar} == {"bir", "iki"}


def test_varsayilan_kisa_dosyayi_atmaz(tmp_path):
    """Eski varsayılan (1000) kısa dosyaları sessizce düşürüyordu."""
    (tmp_path / "A_kisa.txt").write_text(
        "Kedi bahçede oturdu ve uzun uzun etrafı seyretti.", encoding="utf-8")
    assert len(analyze_corpus(tmp_path, lang="tr")) == 1
