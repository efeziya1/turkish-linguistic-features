"""T22 — Zeyrek arka ucu.

Zeyrek'in tek işi ``morpheme_lists``; ``ProcessedText``in geri kalanını
``Preprocessor`` spaCy modelinden dolduruyor (T21). Tokenizasyon, POS, lemma
ve bağımlılık Zeyrek'ten **gelmiyor**.

``zeyrek`` zorunlu bağımlılık (K1), bu yüzden bu dosyada ``skipif`` yok; bütün
testler her ortamda koşar.
"""

from turkish_linguistic_features.pipeline.zeyrek_backend import ZeyrekBackend

# ── kelime çözümleme ──────────────────────────────────────────────────


def test_basit_kelime_cozumleme():
    ms = ZeyrekBackend().analyze_word("kitapları")
    assert ms[0][0] == "Noun" and ms[0][1] == "kitap"
    assert len(ms) >= 1



def test_kivrik_kesme_duz_kesme_gibi_cozumlenir():
    """``’`` ve ``‘`` düz ``'``'ye çevrilir; yoksa özel ad çözümsüz kalıyordu (2026-10-06)."""
    b = ZeyrekBackend()
    assert b.analyze_word("Zeynep’i") == b.analyze_word("Zeynep'i")
    assert b.analyze_word("Türkiye‘de") == b.analyze_word("Türkiye'de")
    assert b.analyze_word("Zeynep’i")[0][0] != "Unk"

def test_cozumlenemeyen_kelime_cokmez():
    """Boş liste DEĞİL — tek elemanlı liste. ``agglutination_depth`` buna bağlı.

    Kök etiketi ``Unk``: T16 çözümsüz kelimeyi paydadan bu etiketle çıkarıyor
    (``morphological._KELIME_DISI_KOK``).
    """
    assert ZeyrekBackend().analyze_word("xyzqwabc") == (("Unk", "xyzqwabc", False),)


def test_morfem_uclusunde_etiket_once():
    """Morpheme = (etiket, yüzey_ek, türetimsel_mi) — etiket POZİSYON 0'da.

    Ters yazılırsa etiket eşleşmeli ~14 öznitelik sessizce 0.0 döner.
    """
    ms = ZeyrekBackend().analyze_word("kitaplarımızda")
    assert ms[0][0] == "Noun" and ms[0][1] == "kitap"
    assert [m[0] for m in ms[1:]] == ["A3pl", "P1pl", "Loc"]
    assert all(isinstance(m[2], bool) for m in ms)


def test_fiil_cozumleme():
    """Etiket birinci öğede; üçlüyü ikiliye açmak ``ValueError`` verirdi."""
    ms = ZeyrekBackend().analyze_word("gelmedim")
    assert [m[0] for m in ms] == ["Verb", "Neg", "Past", "A1sg"]


def test_gorunmeyen_ek_ve_turetme_etiketi_korunuyor():
    """``yazıldı`` → türetme sonrası tür etiketi ve boş yüzeyli ek durmalı.

    T16'nın genel türü ve görünen eki bunlardan okuyor.
    """
    ms = ZeyrekBackend().analyze_word("yazıldı")
    assert ("Pass", "ıl", True) in ms          # türetimsel bayrak
    assert ("Verb", "", False) in ms           # türetmeden sonraki tür
    assert ("A3sg", "", False) in ms           # görünmeyen ek


# ── önbellek ──────────────────────────────────────────────────────────


def test_kelime_onbellegi_ikinci_cagriyi_cozumlemez():
    b = ZeyrekBackend()
    b.analyze_word("kitapları")
    b.analyze_word("kitapları")
    assert b._cozumle.cache_info().hits == 1
    assert b._cozumle.cache_info().maxsize == 50_000


def test_onbellek_ornek_basina():
    """Sınıf seviyesinde ``lru_cache`` ``self``'i anahtara sokar ve sızdırır."""
    b1, b2 = ZeyrekBackend(), ZeyrekBackend()
    b1.analyze_word("kitapları")
    assert b2._cozumle.cache_info().hits == 0
    assert b2._cozumle.cache_info().currsize == 0


def test_punkt_verisi_olmadan_calisir(monkeypatch):
    """``_parse`` yolu NLTK'nin ``punkt_tab`` verisini GEREKTİRMEMELİ."""
    import nltk
    monkeypatch.setattr(nltk.data, "path", ["/erisilemez/yol"])
    assert ZeyrekBackend().analyze_word("kitapları")[0][1] == "kitap"


# ── 🔴 zeyrek sıra bağımlılığı yaması ─────────────────────────────────


def test_cozumleme_sirasi_sonucu_degistirmiyor():
    """obulat/zeyrek#42 — `gelecek` çözümlenince `gelebilir` bozuluyordu.

    Zeyrek paylaşılan `StemTransition` nesnesinin küme alanını değiştiriyor;
    `gel→verbRoot_S` geçişi kalıcı olarak `ExpectsConsonant` kazanıyor ve
    sonraki `gel` + ünlüyle başlayan ek eşleşmiyor. Sessizce başarısız oluyor:
    hata fırlatmıyor, kelime çözümsüz kalıp paydadan düşüyor.
    """
    b = ZeyrekBackend()
    b.analyze_word("gelecek")
    assert "Able" in [m[0] for m in b.analyze_word("gelebilir")]


def test_yama_hala_gerekli():
    """Yama kaldırılınca hata geri gelmeli — zeyrek düzeltirse bu test kırılır.

    Kırıldığında yapılacak: `zeyrek_backend._sira_bagimliligini_duzelt` ve bu
    test silinir, sürüm kilidi yükseltilir.
    """
    from turkish_linguistic_features.pipeline import zeyrek_backend as zb
    with zb._yamasiz():
        b = ZeyrekBackend()
        b.analyze_word("gelecek")
        assert b.analyze_word("gelebilir") == (("Unk", "gelebilir", False),)


# ── golden set: çözümleme sırası tohumdan bağımsız (2026-10-06, Efe) ────


def _golden() -> dict[str, list[str]]:
    import json
    from pathlib import Path
    yol = Path(__file__).parent / "veri" / "zeyrek" / "golden.json"
    return json.loads(yol.read_text(encoding="utf-8"))


def test_golden_set():
    """315 sözcüğün Zeyrek çözümlemeleri, sırasıyla, kayıtlı dosyayla aynı.

    Kırılırsa: Zeyrek ya da tlf'nin Zeyrek katmanı sonucu değiştirmiş demektir. Bilerek
    yapıldıysa ``python scripts/generate_zeyrek_golden.py`` ile yeniden üretin.
    """
    from scripts.generate_zeyrek_golden import uret
    beklenen = _golden()
    bulunan = uret()
    farkli = [s for s in beklenen if bulunan.get(s) != beklenen[s]]
    assert not farkli, f"{len(farkli)} sözcük golden set'ten farklı, örnek: {farkli[:5]}"


def test_cozumleme_sirasi_tohumdan_bagimsiz():
    """Eşit adayların sırası ``PYTHONHASHSEED``'e bağlıydı; iki farklı tohumda aynı olmalı.

    Golden set testi tek süreçte, testi çalıştıran tohumla koşar; bu test iki ayrı tohumu sınar.
    """
    import json
    import os
    import subprocess
    import sys
    sozcukler = ["az", "artık", "ama", "aşırı", "bazı", "başka", "beraber", "bembeyaz"]
    kod = ("import json,sys; from scripts.generate_zeyrek_golden import cozumlemeler; "
           "from turkish_linguistic_features.pipeline.zeyrek_backend import ZeyrekBackend; "
           "b=ZeyrekBackend(); "
           f"print(json.dumps({{s: cozumlemeler(b, s) for s in {sozcukler!r}}}))")
    sonuclar = []
    for tohum in ("1", "2"):
        ortam = {**os.environ, "PYTHONHASHSEED": tohum, "PYTHONIOENCODING": "utf-8"}
        cikti = subprocess.run([sys.executable, "-c", kod], capture_output=True, text=True,
                               encoding="utf-8", env=ortam, check=True,
                               cwd=os.path.dirname(os.path.dirname(__file__))).stdout
        sonuclar.append(json.loads(cikti.strip().splitlines()[-1]))
    golden = _golden()
    assert sonuclar[0] == sonuclar[1] == {s: golden[s] for s in sozcukler}
