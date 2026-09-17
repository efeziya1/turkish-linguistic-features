"""Biçimbilim: spaCy'nin UD morfoloji etiketlerinden üslup özellikleri.

Bu modül ``morphological`` grubunun 19 anahtarını üretir (T15):

- ``spacy_morph_ratios`` (18): zaman, görünüş, durum, kişi, sayı, çatı oranları
- ``surface_per_lemma`` (1): kök başına farklı yüzey biçimi

``morphological_zeyrek`` grubuna dokunmaz (K11); o grup yalnız Zeyrek'ten gelir.

Kararlar (2026-09-17, Efe):

- Payda, o kategorinin etiketini taşıyan tokenlerdir (``Case=Acc`` / ``Case``
  taşıyan). Listede anahtarı olmayan değerler (``Case=Ins``) paydaya girer.
- İstisna ``morph_voice_pass``: UD'de etken fiile çoğunlukla ``Voice`` yazılmaz;
  payda VERB etiketli tokenlerdir (AUX sayılmaz).
- Kategoriden hiç etiket yoksa (fiil yoksa) oranlar NaN (K4).
- ``Person[psor]`` gibi iyelik özellikleri ayrı özelliktir, sayılmaz.
"""

from __future__ import annotations

import math

from .lexical import _hizala
from .punctuation import _kucuk_harf
from .vocab import ASPECT_TAGS, NON_WORD_POS

# (UD özelliği, anahtar öneki, [(UD değeri, anahtar soneki)])
_KATEGORILER: tuple[tuple[str, str, tuple[tuple[str, str], ...]], ...] = (
    ("Tense", "morph_tense", (("Past", "past"), ("Pres", "pres"), ("Fut", "fut"))),
    ("Aspect", "morph_aspect", tuple((d, d.lower()) for d in ASPECT_TAGS)),
    ("Case", "morph_case", (("Nom", "nom"), ("Acc", "acc"), ("Dat", "dat"),
                            ("Loc", "loc"), ("Abl", "abl"), ("Gen", "gen"))),
    ("Person", "morph_person", (("1", "1"), ("2", "2"), ("3", "3"))),
    ("Number", "morph_number", (("Sing", "sing"), ("Plur", "plur"))),
)


def _parse_morph(morph_str: str) -> dict[str, str]:
    """'Case=Acc|Number=Sing' → {'Case': 'Acc', 'Number': 'Sing'}; bozuk parça atlanır."""
    if not morph_str:
        return {}
    return dict(parca.split("=", 1) for parca in morph_str.split("|") if "=" in parca)


def _oran(pay: int, payda: int) -> float:
    return round(pay / payda, 5) if payda else math.nan


def spacy_morph_ratios(morph_tags: list[tuple[str, str]],
                       pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """18 UD morfoloji oranı: zaman, görünüş, durum, kişi, sayı, çatı.

    ``morph_tags`` ve ``pos_data`` aynı tokenleri taşır; uzunluklar tutmuyorsa
    ``ValueError``. Örnek: ``morph_case_acc`` = ``Case=Acc`` token / ``Case``
    taşıyan token. ``morph_voice_pass`` = ``Voice=Pass`` taşıyan VERB / VERB.
    """
    if len(morph_tags) != len(pos_data):
        raise ValueError(
            f"morph_tags ({len(morph_tags)}) ile pos_data ({len(pos_data)}) hizalı değil"
            " — ön işleme hatası"
        )
    ozellikler = [_parse_morph(m) for _, m in morph_tags]
    sonuc: dict[str, float] = {}
    for ozellik, onek, degerler in _KATEGORILER:
        tasiyan = [o[ozellik] for o in ozellikler if ozellik in o]
        for deger, sonek in degerler:
            sonuc[f"{onek}_{sonek}"] = _oran(tasiyan.count(deger), len(tasiyan))
    fiiller = [o for o, (_, p) in zip(ozellikler, pos_data) if p == "VERB"]
    edilgen = sum(1 for o in fiiller if o.get("Voice") == "Pass")
    sonuc["morph_voice_pass"] = _oran(edilgen, len(fiiller))
    return sonuc


def surface_per_lemma(surface_tokens: list[str], pos_data: list[tuple[str, str]],
                      lemma_tokens: list[str], lang: str = "tr") -> dict[str, float]:
    """Kök başına düşen farklı yüzey biçimi sayısı.

    Türkçede yüksektir (gel → geldim, geliyor, gelmiş = 3): eklemeli yapının
    doğrudan ölçüsü. Hesap: farklı (kök, biçim) çifti / farklı kök; tekrar eden
    biçim bir kez sayılır. Biçim ve kök küçük harfe indirilir (``Kitabı`` =
    ``kitabı``). Kelime dışı tokenler (``NON_WORD_POS``) atılır; ``lemma_tokens``
    kalan tokenlerle hizalı olmalı, değilse ``ValueError``. Kelime yoksa NaN.
    """
    if len(surface_tokens) != len(pos_data):
        raise ValueError(
            f"surface_tokens ({len(surface_tokens)}) ile pos_data ({len(pos_data)})"
            " hizalı değil — ön işleme hatası"
        )
    _hizala(lemma_tokens, pos_data)
    kelimeler = [s for s, (_, p) in zip(surface_tokens, pos_data) if p not in NON_WORD_POS]
    ciftler = {(_kucuk_harf(lem, lang), _kucuk_harf(s, lang))
               for lem, s in zip(lemma_tokens, kelimeler)}
    kokler = {lem for lem, _ in ciftler}
    return {"surface_per_lemma": _oran(len(ciftler), len(kokler))}
