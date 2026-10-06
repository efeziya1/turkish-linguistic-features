"""Zeyrek morfolojik çözümleyici arka ucu — Java gerektirmez (T22).

Zeyrek **tokenizasyon yapmaz**; hazır bir kelimeyi alıp eklerine ayırır.
Kelime sınırlarını her zaman spaCy belirler (K11).

Tek işi ``morpheme_lists``: ``morphological_zeyrek`` grubunun 24 anahtarı.
``ProcessedText``in geri kalan alanlarını (POS, lemma, morfoloji, bağımlılık)
``Preprocessor`` spaCy modelinden dolduruyor — spaCy Türkçe morfolojik **ek
bölütlemesi** üretmediği için yalnız bu alan Zeyrek'ten geliyor (K11, T21).
"""

# 🔴 Import sırası bu dosyada KASITLI — gerekçe aşağıda, `_mt` import'unun yanında.

from __future__ import annotations

import functools
import logging
from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING

# 🔴 YÜKLEME SIRASI — ZEYREK ÖNCE, SPACY SONRA.
# Windows'ta spaCy'nin C uzantıları Zeyrek'inkinden önce yüklenirse paylaşılan
# native durum bozuluyor ve sonraki ilgisiz çağrılar traceback'siz çöküyor.
# Bu iki satırın sırası değiştirilemez; isort alfabetik sıralayıp spacy'yi öne
# alacağı için kural bu dosyada kapatıldı.
import zeyrek
import zeyrek.attributes
import spacy

from ..exceptions import LinguisticFeaturesError

if TYPE_CHECKING:
    from spacy.language import Language

Morpheme = tuple[str, str, bool]

# Zeyrek yalnız düz kesmeyi (') tanıyor; kıvrık kesmeler ona çevrilir.
_KESME_DUZ = str.maketrans({"’": "'", "‘": "'"})

__all__ = ["ZeyrekBackend"]


# ── zeyrek#42 — çözümleme sırası sonucu değiştiriyor ──────────────────

def _sira_bagimliligini_duzelt() -> None:
    """``SearchPath.initial`` kök geçişinin küme alanını kopyalar.

    obulat/zeyrek#42 (2026-07-31, açık): ``RuleBasedAnalyzer.advance``
    ``tail_equals_surface`` dalında ``path.phonetic_attributes``'ı referansla
    alıp ``.add()`` / ``.discard()`` ile değiştiriyor. O küme
    ``StemTransitionsMapBased``'te **paylaşılan** ``StemTransition`` nesnesinin
    alanı, yani bozulma kalıcı: ``gelecek`` çözümlendikten sonra
    ``gel→verbRoot_S`` geçişi ``ExpectsConsonant`` kazanıyor ve ``gelebilir``
    artık eşleşmiyor.

    Sessizce başarısız oluyor — hata fırlatmıyor, kelime çözümsüz kalıp
    ``Unk`` etiketiyle paydadan düşüyor. Ölçüldü (2026-09-18): "gelecek" geçen
    31 farklı kelimelik bir paragrafta 2 kelime çözümsüz kaldı.

    Yukarı akış açık ve depo 2024'ten beri sürüm çıkarmadı, bu yüzden düzeltme
    burada. ``test_yama_hala_gerekli`` yamayı kaldırıp hatanın durduğunu
    doğruluyor; zeyrek düzeltirse o test kırılır ve bu fonksiyon silinir.
    """
    import zeyrek.attributes as attrs
    import zeyrek.morphotactics as mt
    import zeyrek.rulebasedanalyzer as rba

    if getattr(mt.SearchPath, "_tlf_yamali", False):
        return

    _ham_initial = mt.SearchPath.initial.__func__

    def initial(cls, stem_transition, tail):
        yol = _ham_initial(cls, stem_transition, tail)
        yol.phonetic_attributes = set(yol.phonetic_attributes)
        return yol

    mt.SearchPath.initial = classmethod(initial)
    mt.SearchPath._tlf_yamali = True

    # İkinci dal: `advance` bu fonksiyonun döndürdüğü lru_cache'li kümeyi de
    # değiştiriyor. İki modül onu doğrudan import ettiği için ikisinde de
    # değiştirilmeli.
    _ham_cpa = attrs.calculate_phonetic_attributes

    def cpa(word, predecessor_attrs=None):
        return set(_ham_cpa(word, predecessor_attrs))

    for modul in (attrs, mt, rba):
        modul.calculate_phonetic_attributes = cpa
    attrs._tlf_ham_cpa = _ham_cpa


@contextmanager
def _yamasiz() -> Iterator[None]:
    """Yamayı geçici olarak kaldırır — yalnız ``test_yama_hala_gerekli`` için."""
    import zeyrek.attributes as attrs
    import zeyrek.morphotactics as mt
    import zeyrek.rulebasedanalyzer as rba

    yamali_initial = mt.SearchPath.initial
    yamali_cpa = mt.calculate_phonetic_attributes

    mt.SearchPath.initial = _HAM_INITIAL
    for modul in (attrs, mt, rba):
        modul.calculate_phonetic_attributes = attrs._tlf_ham_cpa
    try:
        yield
    finally:
        mt.SearchPath.initial = yamali_initial
        for modul in (attrs, mt, rba):
            modul.calculate_phonetic_attributes = yamali_cpa


# Geç import kasıtlı: ham `initial`ı yakalayıp hemen yamalayan blokla yan yana dursun.
import zeyrek.morphotactics as _mt  # noqa: E402

_HAM_INITIAL = _mt.SearchPath.initial
_sira_bagimliligini_duzelt()


class ZeyrekBackend:
    """Kelime → kök ve ekler. Kelime başına memoize edilir.

    Zeyrek bağlam kullanmıyor — aynı kelime her zaman aynı sonucu verir, yani
    memoizasyon tanım gereği güvenli. Önbellek **örnek başına**: sınıf
    seviyesinde ``lru_cache`` ``self``'i anahtara sokar ve örnekler arası
    sızdırır.

    **Belirsizlik:** Zeyrek bir kelime için birden çok çözümleme döndürebilir
    (``yüz`` → organ / sayı / fiil). Kural **ilk çözümlemeyi al**. Bağlam
    kullanılmıyor; bu bir sınırlama ve sınırlılıklar §4'te yazılı
    (``docs/tr/aciklama/sinirliliklar.md``).
    Ölçüldü (2026-09-18): eşit adaylar arasında Zeyrek kararlı bir sıralama
    tanımlamıyor, yani bu kelimelerde seçim keyfî.
    """

    # Önbellek tavanı ölçümle seçildi (165 Türkçe roman, 1,5M token): 50k →
    # %79,7 isabet, 18,1 MB; 100k yalnız %3,4 daha iyi ama 36 MB istiyor.
    _CACHE_BOYU = 50_000

    def __init__(self) -> None:
        self._analyzer: zeyrek.MorphAnalyzer | None = None
        self._nlp: Language | None = None
        self._cozumle = functools.lru_cache(maxsize=self._CACHE_BOYU)(self._cozumle_ham)

    def _ensure_loaded(self) -> None:
        """Zeyrek ÖNCE, spaCy SONRA — sıra Windows çökmesini önlüyor."""
        if self._analyzer is None:
            # zeyrek her aday çözümlemeyi WARNING seviyesinde logluyor
            # ("APPENDING RESULT: ..."), her kelimede stderr'i dolduruyor.
            # Üçüncü parti bir logger'ın sesini kısıyoruz, kendi loglarımızı değil.
            logging.getLogger("zeyrek").setLevel(logging.ERROR)
            self._analyzer = zeyrek.MorphAnalyzer()

            # Sürüm duman testi: `_parse` private, sürüm kilidi tek başına yetmez.
            ornek = self._analyzer._parse("kitap")
            if not ornek or not hasattr(ornek[0], "morphemes"):
                raise LinguisticFeaturesError(
                    "The installed zeyrek version does not expose the expected API.\n"
                    "Required: zeyrek>=0.1.3,<0.2 — check the installed version."
                )

        if self._nlp is None:
            # spaCy BURADA yükleniyor — Zeyrek'ten sonra. Tokenizer'ı
            # kullanmıyoruz (`Preprocessor` kendi modelini yüklüyor); amaç
            # native uzantıların doğru sırada yüklendiğini garanti etmek.
            self._nlp = spacy.blank("tr")

    def _cozumle_ham(self, word: str) -> tuple[Morpheme, ...]:
        self._ensure_loaded()
        analyzer = self._analyzer
        assert analyzer is not None                    # _ensure_loaded doldurdu
        cozumlemeler = analyzer._parse(word)           # analyze() DEĞİL
        if not cozumlemeler:
            # Boş demet DEĞİL, tek elemanlı: `agglutination_depth` kelime
            # başına morfem sayıyor. Kök etiketi `Unk` — T16 çözümsüz kelimeyi
            # paydadan bu etiketle çıkarıyor (`_KELIME_DISI_KOK`).
            return (("Unk", word, False),)

        # Belirsizlikte ilk çözümleme alınır; bağlam kullanılmıyor. Bu bir
        # sınırlama ve sınırlılıklar §4'te yazılı. Zeyrek eşit adaylar
        # arasında kararlı bir sıralama da tanımlamıyor (ölçüldü, 2026-09-18),
        # yani o kelimelerde seçim keyfî.
        return tuple((m.id_, yuzey, bool(m.derivational))
                     for m, yuzey in cozumlemeler[0].morphemes)

    def analyze_word(self, word: str) -> tuple[Morpheme, ...]:
        """Kelimenin morfem üçlüleri: ``(etiket, yüzey_ek, türetimsel_mi)``.

        İlki kök, geri kalanı ek. **Etiket pozisyon 0'da** — öznitelik
        fonksiyonları ``m[0]``'dan okuyor, ters yazılırsa etiket eşleşmeli
        ~14 öznitelik sessizce 0.0 döner.

        Çözümlenemeyen kelimede ``(("Unk", kelime, False),)`` döner — **boş
        demet değil**.

        Yalnız morfem döndürüyor: lemma, POS ve morfoloji etiketleri
        ``Preprocessor``da spaCy modelinden geliyor (T21), Zeyrek'ten değil.

        Kıvrık kesme işaretleri (``’`` ``‘``) düz ``'``'ye çevrilir (2026-10-06, Efe): Zeyrek
        yalnız düz kesmeyi tanıyor, ``Zeynep’i`` ve ``Türkiye’de`` çözümsüz kalıp Zeyrek
        özniteliklerinden düşüyordu (TOMA'nın 11 metninde sözcüklerin %0,9'u).
        """
        return self._cozumle(word.translate(_KESME_DUZ))
