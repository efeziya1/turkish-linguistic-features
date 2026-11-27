"""Akana morfolojik çözümleyici arka ucu (2026-11-10, Efe).

Akana (``altaidevorg/akana``, Rust çekirdek + Python bağlantısı, MIT/Apache-2.0)
Zemberek'in morfotaktiğini taşıyor. Akana burada **tokenizasyon yapmaz**: hazır türceleri
alır, türce sınırlarını spaCy belirler.

Üç işi var: ``morpheme_lists`` (``morphological_akana`` grubunun anahtarları), Türkçe
``lemma_tokens`` ve özel ad aralıkları (``proper_noun_spans``; Akana'nın ad tanıyıcısı).

**Seçim (0.4.0, Efe, 2026-11-24):** Akana'nın belirsizlik gidericisi
(``akana.Disambiguator``) her sözcüğün çözümlemesini **tümcesinin içinde** seçer.
Giderici ağaç bankalarından elde edilmiş sıklık puanına ve yakın sözcüklere bakan birkaç
sınırlı kurala dayanır (ilgi–iyelik uyumu, ilgecin istediği durum, hafif eylemler,
belirleyiciler; Akana README): ``Yüz kişi geldi`` → *yüz* sayı, tek başına çözümlenince
ilk çözümleme ad. Öğrenilmiş bir dil modeli yok. Tümceler aracın tümce kuralından gelir
(``Preprocessor._akana``). Seçilen çözümleme her zaman ``Morphology.analyze``'ın
adaylarından biridir; aynı sürümde aynı girdi her zaman aynı sonucu verir. Gerekçe UD ağaç
bankası sınamaları (sözlükbirim ve sözcük türü uyumu ilk çözümlemeden biraz daha iyi), TOMA
değil.
"""

from __future__ import annotations

import re

import akana

from ..exceptions import LinguisticFeaturesError

Morpheme = tuple[str, str, bool]
Analysis = tuple[tuple[Morpheme, ...], str]       # (morfemler, sözlükbirim)

__all__ = ["AkanaBackend"]

# Özel ad sayılan ad türleri (Akana NER): kişi, yer, kurum. Tarih, para ve yüzde sayılmaz.
_OZEL_AD_TURLERI = frozenset({"PER", "LOC", "ORG"})

# Çözümsüz sözcüğün lemma yedeği kesmeden önceki kısım; düz ve eğri kesme. Akana eğri
# kesmeyi düz kesmeyle aynı çözümlüyor, sözcük ona çevrilmeden verilir.
_KESME = re.compile("['’‘]")

# Akana'nın çözümleme dizesi: "[sözlükbirim:Tür(,AltTür)] kök:Tür+ek:Etiket|ek:Etiket→Tür+…"
_BASLIK = re.compile(r"^\[(.+):([A-Za-z]+)(?:,([A-Za-z]+))?\] (.*)$")


def _oge(s: str) -> tuple[str, str]:
    """``'li:With'`` → ``('li', 'With')``; ``'A3sg'`` → ``('', 'A3sg')``."""
    if ":" in s:
        yuzey, etiket = s.rsplit(":", 1)
        return yuzey, etiket
    return "", s


def _morfemler(govde: str) -> tuple[Morpheme, ...]:
    """Çözümleme gövdesi → ``(etiket, yüzey, türetimsel_mi)`` üçlüleri.

    Türetme sınırı (``|``) sonrası: türetme eki ``(etiket, yüzey, True)``, ardından
    yeni tür ``(Tür, '', False)``. ``merkez:Noun+A3sg|li:With→Adj`` →
    ``Noun/merkez, A3sg, With/li (türetimsel), Adj``.
    """
    out: list[Morpheme] = []
    for i, kume in enumerate(govde.split("|")):
        parcalar = kume.split("+")
        if i == 0:
            yuzey, etiket = _oge(parcalar[0])
            out.append((etiket, yuzey, False))
        else:
            tureten, tur = parcalar[0].split("→")
            yuzey, etiket = _oge(tureten)
            out += [(etiket, yuzey, True), (tur, "", False)]
        for p in parcalar[1:]:
            yuzey, etiket = _oge(p)
            out.append((etiket, yuzey, False))
    return tuple(out)


def _dictionary_lemma(lemma: str, primary_pos: str) -> str:
    """Sözlük maddesi → lemma: fiilde mastar eki atılır (``gelmek`` → ``gel``)."""
    if primary_pos == "Verb" and lemma.endswith(("mak", "mek")):
        return lemma[:-3]
    return lemma


def _cevir(cozumleme: dict) -> Analysis:
    m = _BASLIK.match(cozumleme["analysis"])
    if m is None:
        raise LinguisticFeaturesError(
            f"Unexpected Akana analysis format: {cozumleme['analysis']!r}.\n"
            "Required: akana==0.12.0 — check the installed version."
        )
    lemma, tur, _alt, govde = m.groups()
    return _morfemler(govde), _dictionary_lemma(lemma, tur)


class AkanaBackend:
    """Tümce → türce başına kök ve ekler, Akana'nın belirsizlik gidericisiyle."""

    def __init__(self) -> None:
        self._secici: akana.Disambiguator | None = None

    def _ensure_loaded(self) -> None:
        if self._secici is None:
            self._secici = akana.Disambiguator()
            # Sürüm duman testi: çözümleme dizesinin biçimi sürümler arasında değişebilir.
            ornek = self._secici.disambiguate(["kitap"])
            if not ornek or "analysis" not in ornek[0]:
                raise LinguisticFeaturesError(
                    "The installed akana version does not expose the expected API.\n"
                    "Required: akana==0.12.0 — check the installed version."
                )
            _cevir(ornek[0])

    def analyze_sentence(self, tokens: list[str]) -> list[tuple[tuple[Morpheme, ...], str]]:
        """Bir tümcenin sözcükleri için ``(morfemler, lemma)``, belirsizlik gidericisiyle.

        ``tokens`` bir tümcenin türceleri (boşluksuz). Morfemler ``(etiket, yüzey_ek,
        türetimsel_mi)`` üçlüleri; ilki kök, **etiket pozisyon 0'da**. Çözümlenemeyen türcede
        (noktalama dahil) boş demet değil ``(("Unk", türce, False),)``: ``akana_agglutination_depth``
        sözcük başına morfem sayıyor, kök etiketi ``Unk`` sözcüğü paydadan çıkarır
        (``_KELIME_DISI_KOK``). Lemma: büyük/küçük harf korunur (küçük harfe çeviren çağıran),
        fiilde mastar eki atılır, şapka kalır (``millî``), çözümsüz sözcükte kesmeden önceki kısım.
        """
        if not tokens:
            return []
        self._ensure_loaded()
        assert self._secici is not None                # _ensure_loaded doldurdu
        secilen = self._secici.disambiguate(list(tokens))
        if len(secilen) != len(tokens):
            raise LinguisticFeaturesError(
                f"Akana's disambiguator returned {len(secilen)} readings for "
                f"{len(tokens)} tokens.\n"
                "Required: akana==0.12.0 — check the installed version."
            )
        out: list[tuple[tuple[Morpheme, ...], str]] = []
        for tok, c in zip(tokens, secilen, strict=True):
            if c.get("primary_pos") == "Unk":
                # Morphology.analyze bu türcelere hiç çözümleme vermiyor; aynı biçim.
                out.append(((("Unk", tok, False),), _KESME.split(tok, maxsplit=1)[0] or tok))
            else:
                out.append(_cevir(c))
        return out

    def proper_noun_spans(self, text: str) -> list[tuple[int, int]]:
        """Kişi, yer ve kurum adlarının ``text`` içindeki karakter aralıkları (0.4.0, Efe).

        Akana'nın ad tanıyıcısından (``akana.extract_entities``). UD Türkçe ağaç bankalarının
        sınama bölümlerinde (10 banka, 85.629 sözcük) spaCy'nin ``PROPN`` etiketine eklenince
        özel ad F1 75,6 → 84,5; büyük harf kuralı 79,3, spaCy'nin kendi NER'i 79,4 kaldı
        (2026-11-25; ölçüm ``akana/sonuclar/ozel-ad``).
        """
        if not text:
            return []
        return [(e.start, e.end) for e in akana.extract_entities(text)
                if e.label in _OZEL_AD_TURLERI]
