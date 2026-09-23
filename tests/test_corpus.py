r"""T27 — korpus yükleyici: klasör/CSV → analiz edilebilir kayıtlar.

``segment_text`` spaCy tokenizer'ı kullanıyor (A kararı, 2026-09-19). Ölçüm
gerekçesi: ``\S+`` ile "tam 1000 kelime" diye kesilen parçalar gerçekte
1018–1562 spaCy token çıkıyordu ve bu aralıkta aynı metnin TTR'si %7,6
oynuyordu — yani ``min_fill``'in önlemek için var olduğu uzunluk karışıklığı
sayım yönteminden giriyordu.
"""

import pytest

# ``_load_corpus`` 2026-09-23'te public yüzeyden çıktı (``analyze_corpus``
# zinciri kapatıyor) ama kodu duruyor: üç dosya düzeni algılaması ve CSV
# başlık eşlemesi hâlâ çalışıyor, dolayısıyla testleri de duruyor.
from turkish_linguistic_features.file_loader import (
    _load_corpus,
    save_csv,
    segment_text,
)


def _metin(n: int) -> str:
    return " ".join(f"k{i}" for i in range(n))


# ── segment_text ──────────────────────────────────────────────────────


def test_parca_boyu_TAM_istenen_token_sayisi():
    r"""🔴 A kararının bütün noktası bu: parça boyu yaklaşık değil, tam.

    Noktalama spaCy'de ayrı token — ``\S+`` sayımı burada şişerdi.
    """
    import spacy
    metin = "Ali eve gitti, kitabı okudu. " * 400
    parcalar = segment_text(metin, size=100, lang="tr")
    tokenizer = spacy.blank("tr").tokenizer
    assert parcalar
    assert all(len(tokenizer(p)) == 100 for p in parcalar)


def test_min_fill_varsayilani_yarim_parcayi_atar():
    assert len(segment_text(_metin(250), size=100, lang="tr")) == 2


def test_min_fill_dusurulunce_son_parca_kaliyor():
    assert len(segment_text(_metin(250), size=100, min_fill=0.5, lang="tr")) == 3


def test_min_fill_esigin_altinda_kalan_atilir():
    assert len(segment_text(_metin(230), size=100, min_fill=0.5, lang="tr")) == 2


def test_karakter_birimi():
    parcalar = segment_text("a" * 250, size=100, unit="char")
    assert len(parcalar) == 2
    assert all(len(p) == 100 for p in parcalar)


def test_parca_ham_metin_dilimi():
    """İçerik yeniden birleştirilmiş token listesi değil, ham metin olmalı."""
    metin = "Ali   eve\tgitti. " * 50
    assert segment_text(metin, size=10, lang="tr")[0] in metin


def test_bos_metin():
    assert segment_text("", size=100, lang="tr") == []


def test_kisa_metin_min_fill_1():
    assert segment_text(_metin(10), size=100, lang="tr") == []


def test_gecersiz_dil():
    with pytest.raises(ValueError):
        segment_text("deneme", size=10, lang="de")


def test_gecersiz_birim():
    with pytest.raises(ValueError):
        segment_text("deneme", size=10, unit="hece")


# ── _load_corpus: üç düzen ─────────────────────────────────────────────


def test_duz_dosya_duzeni(tmp_path):
    (tmp_path / "Roman_Sinekli Bakkal.txt").write_text(_metin(250), encoding="utf-8")
    kayitlar = _load_corpus(tmp_path, segment_size=100)
    assert len(kayitlar) == 2
    assert kayitlar[0]["label"] == "Roman"
    assert kayitlar[0]["source"] == "Sinekli Bakkal"
    assert kayitlar[0]["segment_id"] == 0
    assert kayitlar[1]["segment_id"] == 1


def test_alt_klasor_duzeni(tmp_path):
    (tmp_path / "Roman").mkdir()
    (tmp_path / "Roman" / "kitap.txt").write_text(_metin(250), encoding="utf-8")
    kayitlar = _load_corpus(tmp_path, segment_size=100)
    assert {k["label"] for k in kayitlar} == {"Roman"}
    assert kayitlar[0]["source"] == "kitap"


def test_csv_duzeni(tmp_path):
    yol = tmp_path / "korpus.csv"
    yol.write_text("label,text\nRoman," + _metin(250) + "\n", encoding="utf-8")
    kayitlar = _load_corpus(yol, segment_size=100)
    assert len(kayitlar) == 2
    assert kayitlar[0]["label"] == "Roman"


def test_csv_turkce_basliklar(tmp_path):
    yol = tmp_path / "k.csv"
    yol.write_text("etiket,metin\nŞiir," + _metin(150) + "\n", encoding="utf-8")
    assert _load_corpus(yol, segment_size=100)[0]["label"] == "Şiir"


def test_csv_eski_yazar_basligi(tmp_path):
    """Geriye dönük: ``yazar`` da ``label``a haritalanır."""
    yol = tmp_path / "eski.csv"
    yol.write_text("yazar,metin\nAhmet," + _metin(150) + "\n", encoding="utf-8")
    assert _load_corpus(yol, segment_size=100)[0]["label"] == "Ahmet"


# ── kodlama ve kenar durumlar ─────────────────────────────────────────


def test_turkce_karakterli_dosya_adi(tmp_path):
    (tmp_path / "Şiir_Füreya.txt").write_text(_metin(150), encoding="utf-8")
    assert _load_corpus(tmp_path, segment_size=100)[0]["label"] == "Şiir"


def test_utf8_okuma(tmp_path):
    """cp1254 varsayılanı Türkçe karakterleri bozardı."""
    (tmp_path / "Etiket_Kitap.txt").write_text("ğüşiöç " * 200, encoding="utf-8")
    assert "ğ" in _load_corpus(tmp_path, segment_size=100)[0]["text"]


def test_bos_klasor(tmp_path):
    assert _load_corpus(tmp_path) == []


def test_olmayan_yol():
    with pytest.raises((FileNotFoundError, ValueError)):
        _load_corpus("/boyle/bir/yol/yok")


def test_csv_disa_aktarma(tmp_path):
    kayitlar = [{"label": "A", "source": "K", "segment_id": 0, "text": "metin"}]
    cikti = tmp_path / "out.csv"
    save_csv(kayitlar, cikti)
    icerik = cikti.read_text(encoding="utf-8")
    assert "label" in icerik and "metin" in icerik


def test_lang__load_corpus_uzerinden_geciyor(tmp_path):
    """``lang`` artık gerçek bir iş yapıyor — tokenizer'ı seçiyor."""
    (tmp_path / "A_b.txt").write_text(_metin(250), encoding="utf-8")
    assert _load_corpus(tmp_path, segment_size=100, lang="en")


# ── segment_size=None: varsayılan, bölme yok ──────────────────────────


def test_varsayilan_bolmez_dosya_basina_tek_kayit(tmp_path):
    """2026-09-23: varsayılan 1000'den None'a çekildi.

    Eski varsayılan ``min_fill=1.0`` ile birleşince sessizce veri atıyordu:
    1500 kelimelik dosyanın son 500'ü gidiyor, 1000'den kısa dosya hiç kayıt
    üretmiyordu. Ölçüldü: 1500+1500+400 kelimelik korpustan 2000 kelime
    analiz ediliyordu, yani %41'i düşüyordu.
    """
    (tmp_path / "A_uzun.txt").write_text(_metin(1500), encoding="utf-8")
    (tmp_path / "B_kisa.txt").write_text(_metin(400), encoding="utf-8")

    kayitlar = _load_corpus(tmp_path)

    assert len(kayitlar) == 2, "dosya başına tam bir kayıt"
    assert all(k["segment_id"] == 0 for k in kayitlar)
    # Metnin tamamı duruyor: hiçbir kelime atılmadı.
    toplam = sum(len(str(k["text"]).split()) for k in kayitlar)
    assert toplam == 1900


def test_none_ile_kisa_dosya_dusmez(tmp_path):
    """Eski varsayılanın en sinsi yanı: kısa dosya sessizce yok oluyordu."""
    (tmp_path / "A_kisa.txt").write_text(_metin(10), encoding="utf-8")
    assert len(_load_corpus(tmp_path)) == 1
    assert _load_corpus(tmp_path, segment_size=1000) == []


def test_parcalama_kaynak_basina_dosyalar_karismaz(tmp_path):
    """Her dosya kendi segment_id sayacıyla sıfırdan başlar; artıklar birleşmez."""
    (tmp_path / "A_bir.txt").write_text(_metin(150), encoding="utf-8")
    (tmp_path / "B_iki.txt").write_text(_metin(150), encoding="utf-8")

    kayitlar = _load_corpus(tmp_path, segment_size=100, min_fill=0.0)

    kaynaklar = {}
    for k in kayitlar:
        kaynaklar.setdefault(k["source"], []).append(k["segment_id"])
    assert len(kaynaklar) == 2
    assert all(ids == [0, 1] for ids in kaynaklar.values()), (
        "her kaynak 0'dan başlamalı: 150 kelime → 100 + 50"
    )
