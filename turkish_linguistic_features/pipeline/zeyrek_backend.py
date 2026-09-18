"""Zeyrek morfolojik çözümleyici arka ucu — Java gerektirmez (T22).

Zeyrek **tokenizasyon yapmaz**; hazır bir kelimeyi alıp eklerine ayırır.
Kelime sınırlarını her zaman spaCy belirler (K11).

Çıktı iki yerde **UD biçimine** çevrilir — ``pos`` ve ``morph`` — böylece
Türkçe ve İngilizce boru hatları öznitelik katmanına aynı şekli verir.
``spacy_morph_ratios`` (T15) adı spaCy olmasına rağmen aslında UD dizgisi
okuyor; bu çeviri sayesinde Türkçede de çalışıyor.
"""

# ruff: noqa: I001
# 🔴 I001 (import sıralaması) bu dosyada KAPALI — sıra kasıtlı, aşağıya bakın.

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


import zeyrek.morphotactics as _mt  # noqa: E402

_HAM_INITIAL = _mt.SearchPath.initial
_sira_bagimliligini_duzelt()


# ── Zeyrek → UD çevirisi ──────────────────────────────────────────────

# Zeyrek'in POS enum'unda `.name` ile `.value` 14 etiketin 12'sinde farklı
# (`PrimaryPos.Adverb.value == "Adv"`). Harita `.value` anahtarlarıyla yazılı;
# `.name` kullanılırsa 12 etiket ıskalanıp `X`'e düşer.
_ZEYREK_POS_MAP: dict[str, str] = {
    "Noun": "NOUN", "Verb": "VERB", "Adj": "ADJ", "Adv": "ADV",
    "Pron": "PRON", "Det": "DET", "Conj": "CCONJ", "Postp": "ADP",
    "Num": "NUM", "Interj": "INTJ", "Punc": "PUNCT", "Ques": "PART",
    "Dup": "X", "Unk": "X",
}

_PROPER_NOUN = zeyrek.attributes.SecondaryPos.ProperNoun

_ZEYREK_CASE_MAP = {"Acc": "Acc", "Dat": "Dat", "Loc": "Loc",
                    "Abl": "Abl", "Gen": "Gen"}

_ZEYREK_AGREEMENT_MAP = {
    "A1sg": ("1", "Sing"), "A2sg": ("2", "Sing"), "A3sg": ("3", "Sing"),
    "A1pl": ("1", "Plur"), "A2pl": ("2", "Plur"), "A3pl": ("3", "Plur"),
}

# Zaman: -DI ve -mIş geçmiş, -yor/-mAktA/-Ir şimdi, -AcAk gelecek.
# T16'nın `_ZAMANLAR` tablosuyla aynı okuma.
_ZEYREK_TENSE_MAP = {"Past": "Past", "Narr": "Past", "Fut": "Fut",
                     "Prog1": "Pres", "Prog2": "Pres", "Aor": "Pres"}

# Görünüş: yalnız tartışmasız olanlar. -Ir (Aor) UD Türkçede `Aspect=Hab`
# alıyor ama `vocab.ASPECT_TAGS` (Perf, Imp, Prog) onu tanımıyor; uydurma
# eşleme yapmak yerine o tokenler Aspect taşımıyor.
_ZEYREK_ASPECT_MAP = {"Prog1": "Prog", "Prog2": "Prog",
                      "Past": "Perf", "Narr": "Perf"}

# Sıfır ekli 3. tekil varsayımının uygulandığı türler. Bağlaç, edat ve
# noktalama kişi/sayı taşımaz.
_CEKIMLI_POS = frozenset({"NOUN", "PROPN", "PRON", "VERB"})


def _zeyrek_to_ud_morph(morphemes: tuple[Morpheme, ...], pos: str) -> str:
    """Zeyrek morfem etiketlerini UD morfoloji dizgisine çevirir.

    Türkçede 3. tekil şahıs hem fiil çekiminde hem isim tekilliğinde **sıfır
    ekli**dir ("okudu", "kitap" — hiç ek yok). Hiç A-etiketi yoksa Person=3 /
    Number=Sing varsayılır; bu spaCy'nin aynı biçimlerdeki davranışıyla uyuşur
    ve alanı boş bırakmaktan daha doğrudur. Aynı gerekçeyle işaretsiz nominal
    ``Case=Nom`` alır — yoksa ``morph_case_nom`` Türkçede hep 0.0 kalır ve
    işaretli hallerin oranı şişer.
    """
    etiketler = [m[0] for m in morphemes]
    ozellikler: dict[str, str] = {}

    for etiket in etiketler:
        if etiket in _ZEYREK_TENSE_MAP:
            ozellikler.setdefault("Tense", _ZEYREK_TENSE_MAP[etiket])
        if etiket in _ZEYREK_ASPECT_MAP:
            ozellikler.setdefault("Aspect", _ZEYREK_ASPECT_MAP[etiket])
        if etiket in _ZEYREK_CASE_MAP:
            ozellikler.setdefault("Case", _ZEYREK_CASE_MAP[etiket])
        if etiket in _ZEYREK_AGREEMENT_MAP:
            kisi, sayi = _ZEYREK_AGREEMENT_MAP[etiket]
            ozellikler.setdefault("Person", kisi)
            ozellikler.setdefault("Number", sayi)
        if etiket == "Pass":
            ozellikler.setdefault("Voice", "Pass")

    if pos in _CEKIMLI_POS:
        ozellikler.setdefault("Person", "3")
        ozellikler.setdefault("Number", "Sing")
        if pos != "VERB":
            ozellikler.setdefault("Case", "Nom")

    sira = ("Case", "Number", "Person", "Tense", "Aspect", "Voice")
    return "|".join(f"{a}={ozellikler[a]}" for a in sira if a in ozellikler)


class ZeyrekBackend:
    """Kelime → kök ve ekler. Kelime başına memoize edilir.

    Zeyrek bağlam kullanmıyor — aynı kelime her zaman aynı sonucu verir, yani
    memoizasyon tanım gereği güvenli. Önbellek **örnek başına**: sınıf
    seviyesinde ``lru_cache`` ``self``'i anahtara sokar ve örnekler arası
    sızdırır.

    **Belirsizlik:** Zeyrek bir kelime için birden çok çözümleme döndürebilir
    (``yüz`` → organ / sayı / fiil). Kural **ilk çözümlemeyi al**. Bağlam
    kullanılmıyor; bu bir sınırlama ve ``docs/limitations.md``'de yazılı.
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
                    "Kurulu zeyrek sürümü beklenen API'yi sunmuyor.\n"
                    "Gerekli: zeyrek>=0.1.3,<0.2 — kurulu sürümü kontrol edin."
                )

        if self._nlp is None:
            # Boş tokenizer: eğitilmiş model İNDİRİLMESİ GEREKMİYOR.
            self._nlp = spacy.blank("tr")
            self._nlp.add_pipe("sentencizer")

    @staticmethod
    def _sec(word: str, cozumlemeler: list):
        """Adaylardan birini seçer: kural **ilk çözümleme**, bir istisnayla.

        İstisna: küçük harfle başlayan token için özel isim okuması atlanır.
        Zeyrek eşit adaylar arasında kararlı bir sıralama tanımlamadığı için
        (ölçüldü, 2026-09-18) ``kitapları`` bazen ``Kitap`` özel ismini
        döndürüyordu; lemma sıklıkları ve ``*_variation`` bundan doğrudan
        etkileniyor.

        🔴 **Bu bir varsayım, kural değil (2026-09-18, Efe).** Standart Türkçe
        imlası özel isimleri büyük harfle yazar, ama gerçek kullanım her zaman
        buna uymaz: gayriresmî yazı, tamamı küçük harfle yazılmış metin, OCR
        çıktısı, transkript. Böyle metinlerde gerçek bir özel isim, rakip bir
        cins isim okuması varsa yanlış çözümlenir.

        Yine de varsayılan bu, çünkü alternatifi daha kötü: kural olmadan seçim
        Zeyrek'in keyfî sırasına kalıyor ve ``kitapları`` gibi sıradan
        kelimeler özel isim okuması alıyor. Hasarı sınırlayan şey geri düşüş —
        bütün adaylar özel isimse ilk aday korunur, yani yalnızca özel isim
        okuması olan ``ankara`` etkilenmez.

        Kütüphane düzenlenmiş metin (edebî, akademik korpus) için
        tasarlandığından varsayım oraya uyuyor. ``docs/limitations.md``'ye
        yazılacak.

        Bu bir belirsizlik giderme kuralı değil. Anlamsal seçim (``düş|ünce``
        mi ``düşünce`` mi) hâlâ açık ve ölçülmeden eklenmeyecek.
        """
        if word[:1].isupper():
            return cozumlemeler[0]
        for aday in cozumlemeler:
            if aday.dict_item.secondary_pos != _PROPER_NOUN:
                return aday
        return cozumlemeler[0]         # hepsi özel isim: elde başka aday yok

    def _cozumle_ham(self, word: str) -> dict:
        self._ensure_loaded()
        analyzer = self._analyzer
        assert analyzer is not None                    # _ensure_loaded doldurdu
        cozumlemeler = analyzer._parse(word)           # analyze() DEĞİL
        if not cozumlemeler:
            # Boş liste DEĞİL, tek elemanlı liste: `agglutination_depth`
            # kelime başına morfem sayıyor. Kök etiketi `Unk` — T16 çözümsüz
            # kelimeyi paydadan bu etiketle çıkarıyor.
            return {"surface": word, "lemma": word, "pos": "X",
                    "morphemes": [("Unk", word, False)]}

        ilk = self._sec(word, cozumlemeler)
        morphemes = [(m.id_, yuzey, bool(m.derivational)) for m, yuzey in ilk.morphemes]
        pos = _ZEYREK_POS_MAP.get(ilk.pos.value, "X")
        return {
            "surface": word,
            # Sözlük biçimi: fiillerde mastar (`gelmek`), kök (`gel`) değil
            # (2026-09-18, Efe). `wordfreq` Türkçe fiilleri mastarla tutuyor.
            "lemma": ilk.dict_item.lemma,
            "pos": pos,
            "morphemes": morphemes,
        }

    def analyze_word(self, word: str) -> dict:
        """Tek kelimeyi çözümler; ``surface``, ``lemma``, ``pos``, ``morphemes``.

        ``morphemes`` = ``(etiket, yüzey_ek, türetimsel_mi)`` üçlüleri; ilki
        kök, geri kalanı ek. **Etiket pozisyon 0'da** — öznitelik fonksiyonları
        ``m[0]``'dan okuyor, ters yazılırsa ~14 öznitelik sessizce 0.0 döner.

        Çözümlenemeyen kelimede ``lemma`` kelimenin kendisi, ``pos`` ``"X"``,
        ``morphemes`` ``[("Unk", kelime, False)]`` — **boş liste değil**.
        """
        return self._cozumle(word)

    def tokenize(self, text: str) -> list[list[str]]:
        """Metni cümlelere, cümleleri token'lara böler — **spaCy ile**.

        Tokenizasyonun tek kaynağı burası. ``.split()`` noktalamayı kelimeye
        yapıştırır ve aynı metin için iki farklı kelime sayısı üretir.
        """
        self._ensure_loaded()
        nlp = self._nlp
        assert nlp is not None                         # _ensure_loaded doldurdu
        belge = nlp(text)
        return [[t.text for t in cumle if not t.is_space]
                for cumle in belge.sents
                if any(not t.is_space for t in cumle)]
