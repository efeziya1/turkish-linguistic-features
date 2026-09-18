"""T22 — Zeyrek arka ucu ve ``TurkishPreprocessor``.

``zeyrek`` zorunlu bağımlılık (K1), bu yüzden bu dosyada ``skipif`` yok; bütün
testler her ortamda koşar.
"""

import math

from turkish_linguistic_features.pipeline.preprocess import TurkishPreprocessor
from turkish_linguistic_features.pipeline.zeyrek_backend import ZeyrekBackend

# ── kelime çözümleme ──────────────────────────────────────────────────


def test_basit_kelime_cozumleme():
    sonuc = ZeyrekBackend().analyze_word("kitapları")
    assert sonuc["lemma"] == "kitap"
    assert sonuc["pos"] == "NOUN"
    assert len(sonuc["morphemes"]) >= 1


def test_fiil_lemmasi_mastar_bicimi():
    """Fiil lemması sözlük biçimi: ``gelmek``, kök ``gel`` değil (2026-09-18, Efe).

    `wordfreq` Türkçe fiilleri mastarla tutuyor; İngilizce tarafında spaCy de
    sözlük biçimi veriyor. İki boru hattı aynı ilkeyi izliyor.
    """
    assert ZeyrekBackend().analyze_word("gelmedim")["lemma"] == "gelmek"


def test_cozumlenemeyen_kelime_cokmez():
    """Boş liste DEĞİL — tek elemanlı liste. ``agglutination_depth`` buna bağlı.

    Kök etiketi ``Unk``: T16 çözümsüz kelimeyi paydadan bu etiketle çıkarıyor
    (``morphological._KELIME_DISI_KOK``).
    """
    sonuc = ZeyrekBackend().analyze_word("xyzqwabc")
    assert sonuc["lemma"] == "xyzqwabc"
    assert sonuc["pos"] == "X"
    assert sonuc["morphemes"] == [("Unk", "xyzqwabc", False)]


def test_morfem_uclusunde_etiket_once():
    """Morpheme = (etiket, yüzey_ek, türetimsel_mi) — etiket POZİSYON 0'da.

    Ters yazılırsa etiket eşleşmeli ~14 öznitelik sessizce 0.0 döner.
    """
    ms = ZeyrekBackend().analyze_word("kitaplarımızda")["morphemes"]
    assert ms[0][0] == "Noun" and ms[0][1] == "kitap"
    assert [m[0] for m in ms[1:]] == ["A3pl", "P1pl", "Loc"]
    assert all(isinstance(m[2], bool) for m in ms)


def test_fiil_cozumleme():
    """Etiket birinci öğede; üçlüyü ikiliye açmak ``ValueError`` verirdi."""
    sonuc = ZeyrekBackend().analyze_word("gelmedim")
    assert sonuc["pos"] == "VERB"
    assert "Neg" in [m[0] for m in sonuc["morphemes"]]


def test_gorunmeyen_ek_ve_turetme_etiketi_korunuyor():
    """``yazıldı`` → türetme sonrası tür etiketi ve boş yüzeyli ek durmalı.

    T16'nın genel türü ve görünen eki bunlardan okuyor.
    """
    ms = ZeyrekBackend().analyze_word("yazıldı")["morphemes"]
    assert ("Pass", "ıl", True) in ms          # türetimsel bayrak
    assert ("Verb", "", False) in ms           # türetmeden sonraki tür
    assert ("A3sg", "", False) in ms           # görünmeyen ek


def test_pos_haritasi_enum_degerini_kullaniyor():
    """Zeyrek'in POS enum'unda ``.name`` ile ``.value`` 14 etiketin 12'sinde farklı.

    ``PrimaryPos.Adverb.value == "Adv"``; ``.name`` kullanılırsa 12 etiket
    haritayı ıskalar ve hepsi ``X``'e düşer.
    """
    assert ZeyrekBackend().analyze_word("koşarak")["pos"] == "ADV"


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
    assert ZeyrekBackend().analyze_word("kitapları")["lemma"] == "kitap"


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
    sonuc = b.analyze_word("gelebilir")
    assert sonuc["lemma"] == "gelmek"
    assert "Able" in [m[0] for m in sonuc["morphemes"]]


def test_yama_hala_gerekli():
    """Yama kaldırılınca hata geri gelmeli — zeyrek düzeltirse bu test kırılır.

    Kırıldığında yapılacak: `zeyrek_backend._sira_bagimliligini_duzelt` ve bu
    test silinir, sürüm kilidi yükseltilir.
    """
    from turkish_linguistic_features.pipeline import zeyrek_backend as zb
    with zb._yamasiz():
        b = ZeyrekBackend()
        b.analyze_word("gelecek")
        assert b.analyze_word("gelebilir")["pos"] == "X"


# ── TurkishPreprocessor ───────────────────────────────────────────────


def test_turkish_preprocessor_morfoloji_uretir():
    pt = TurkishPreprocessor().process("Güzel bir gün, çalışmak için ideal.")
    assert len(pt.morpheme_lists) == len(pt.surface_tokens)
    assert pt.dep_data is None                 # Zeyrek ayrıştırma yapmaz
    assert pt.morph_tags != ()                 # morph_tags DOLDURULUR
    assert pt.lang == "tr"


def test_cumle_tokenlari_surface_ile_tutarli():
    """Cümle token'ları `.split()` ile değil, spaCy tokenizer ile kurulmalı.

    Aksi halde aynı metin için iki farklı kelime sayısı oluşur ve `sentence`
    grubunun 8 özniteliği hangi boru hattını seçtiğinize göre değişir.
    """
    pt = TurkishPreprocessor().process('Ali, kitabı okudu. "Güzeldi," dedi.')
    assert sum(len(s) for s in pt.sentences_as_tokens) == len(pt.surface_tokens)


def test_noktalama_ayri_token():
    """`okudu.` tek token OLMAMALI."""
    pt = TurkishPreprocessor().process("Ali kitabı okudu.")
    assert "okudu" in pt.surface_tokens
    assert "." in pt.surface_tokens
    assert "okudu." not in pt.surface_tokens


def test_lemma_noktalama_icermez():
    """`lemma_tokens`'a NON_WORD_POS girmez; `pos_data` ile hizalı olmalı (T21)."""
    from turkish_linguistic_features.features.vocab import NON_WORD_POS
    pt = TurkishPreprocessor().process("Ali, kitabı okudu.")
    assert "." not in pt.lemma_tokens
    kelime_pos = [p for _, p in pt.pos_data if p not in NON_WORD_POS]
    assert len(kelime_pos) == len(pt.lemma_tokens)


def test_morph_tags_pos_data_ile_hizali():
    pt = TurkishPreprocessor().process("Kitapları okudum.")
    assert len(pt.morph_tags) == len(pt.pos_data)


def test_ud_morfoloji_dizgisi_uretiliyor():
    """`morph_tags` UD biçiminde: 'Özellik=Değer' çiftleri '|' ile ayrılmış."""
    pt = TurkishPreprocessor().process("Kitabı okudum.")
    dizgiler = [m for _, m in pt.morph_tags if m]
    assert dizgiler, "hiç morfoloji dizgisi üretilmedi"
    for d in dizgiler:
        for parca in d.split("|"):
            assert "=" in parca, f"UD biçimi değil: {d}"


def test_sifir_ekli_ucuncu_tekil_varsayiliyor():
    """Türkçede 3. tekil hem fiilde hem isimde sıfır ekli — alan boş kalmamalı."""
    pt = TurkishPreprocessor().process("Kitap okudu.")
    ozellikler = dict(pt.morph_tags)
    assert "Person=3" in ozellikler["okudu"]
    assert "Number=Sing" in ozellikler["okudu"]


# ── uçtan uca ─────────────────────────────────────────────────────────


def test_morfoloji_ozellikleri_uretiliyor():
    from turkish_linguistic_features.features.extractor import _extract_features
    pt = TurkishPreprocessor().process("Kitaplarımızda gelmedim yazıyordu.")
    feats = _extract_features(**pt.to_dict())
    assert feats["agglutination_depth"] > 0
    assert "negation_ratio" in feats


def test_uctan_uca_taban_sema():
    """Türkçe boru hattı → 207 anahtar eksi `syntactic_dep` (Zeyrek ayrıştırmaz)."""
    from turkish_linguistic_features.features.extractor import _extract_features
    pt = TurkishPreprocessor().process(
        "Küçük çocuk bahçede top oynuyordu. Annesi ona seslendi ve eve çağırdı.\n\n"
        "Çocuk koşarak geldi, yorgun görünüyordu."
    )
    feats = _extract_features(**pt.to_dict())
    assert len(feats) == 207 - 16
    assert all(isinstance(v, float) for v in feats.values())
    assert not any(math.isinf(v) for v in feats.values())


def test_bos_metin_cokmez():
    pt = TurkishPreprocessor().process("")
    assert pt.surface_tokens == ()
    assert pt.lemma_tokens == ()
