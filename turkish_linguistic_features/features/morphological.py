"""Biçimbilim: spaCy'nin UD etiketlerinden ve Zeyrek çözümlemelerinden.

İki grup, iki kaynak (K11) — biri öbürünü tamamlamaz:

- ``morphological`` (19, T15, spaCy): ``spacy_morph_ratios`` (18) ·
  ``surface_per_lemma`` (1)
- ``morphological_zeyrek`` (23, T16, yalnız Türkçe): ``zeyrek_morfoloji``;
  kararlar aşağıda, "T16" bölümünde.

T15 kararları (2026-09-17, Efe):

- Payda, o kategorinin etiketini taşıyan tokenlerdir (``Case=Acc`` / ``Case``
  taşıyan). Listede anahtarı olmayan değerler (``Case=Ins``) paydaya girer.
- İstisna ``voice_pass_ratio``: UD'de etken fiile çoğunlukla ``Voice`` yazılmaz;
  payda VERB etiketli tokenlerdir (AUX sayılmaz).
- Kategoriden hiç etiket yoksa (fiil yoksa) oranlar NaN (K4).
- ``Person[psor]`` gibi iyelik özellikleri ayrı özelliktir, sayılmaz.
"""

from __future__ import annotations

import math
from collections import Counter

from ..alfabe import _kucuk_harf
from ..params import DEFAULT_PARAMS, FeatureParams
from ..vocab import ASPECT_TAGS, NON_WORD_POS
from .lexical import _hizala

# (UD özelliği, anahtar öneki, [(UD değeri, anahtar soneki)])
_KATEGORILER: tuple[tuple[str, str, tuple[tuple[str, str], ...]], ...] = (
    ("Tense", "tense", (("Past", "past"), ("Pres", "pres"), ("Fut", "fut"))),
    ("Aspect", "aspect", tuple((d, d.lower()) for d in ASPECT_TAGS)),
    ("Case", "case", (("Nom", "nom"), ("Acc", "acc"), ("Dat", "dat"),
                      ("Loc", "loc"), ("Abl", "abl"), ("Gen", "gen"))),
    ("Person", "person", (("1", "1"), ("2", "2"), ("3", "3"))),
    ("Number", "number", (("Sing", "sing"), ("Plur", "plur"))),
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
    ``ValueError``. Örnek: ``case_acc_ratio`` = ``Case=Acc`` token / ``Case``
    taşıyan token. ``voice_pass_ratio`` = ``Voice=Pass`` taşıyan VERB / VERB.
    """
    if len(morph_tags) != len(pos_data):
        raise ValueError(
            f"morph_tags ({len(morph_tags)}) is not aligned with pos_data "
            f"({len(pos_data)}) — preprocessing error"
        )
    ozellikler = [_parse_morph(m) for _, m in morph_tags]
    sonuc: dict[str, float] = {}
    for ozellik, onek, degerler in _KATEGORILER:
        tasiyan = [o[ozellik] for o in ozellikler if ozellik in o]
        for deger, sonek in degerler:
            sonuc[f"{onek}_{sonek}_ratio"] = _oran(tasiyan.count(deger), len(tasiyan))
    fiiller = [o for o, (_, p) in zip(ozellikler, pos_data, strict=False) if p == "VERB"]
    edilgen = sum(1 for o in fiiller if o.get("Voice") == "Pass")
    sonuc["voice_pass_ratio"] = _oran(edilgen, len(fiiller))
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
            f"surface_tokens ({len(surface_tokens)}) is not aligned with pos_data "
            f"({len(pos_data)}) — preprocessing error"
        )
    _hizala(lemma_tokens, pos_data)
    kelimeler = [s for s, (_, p) in zip(surface_tokens, pos_data, strict=False) if p not in NON_WORD_POS]
    ciftler = {(_kucuk_harf(lem, lang), _kucuk_harf(s, lang))
               for lem, s in zip(lemma_tokens, kelimeler, strict=False)}
    kokler = {lem for lem, _ in ciftler}
    return {"surface_per_lemma": _oran(len(ciftler), len(kokler))}


# ── T16: Zeyrek ───────────────────────────────────────────────────────
#
# Girdi ``morpheme_lists``: token başına ``(etiket, yüzey, türetimsel_mi)``
# listesi; ilk öge kök. Zeyrek türetmeden sonraki türü ayrı öge olarak yazar
# (``yaz|ıl:Pass→Verb`` → ``("Pass", "ıl", True), ("Verb", "", False)``);
# yazıda görünmeyen ekler boş yüzeyle gelir (``A3sg``); çözümsüz kelime
# ``[("Unk", kelime, False)]``.
#
# Kararlar (2026-09-17, Efe):
# - Kelime: noktalama/sembol (``pos_data``) ve ``Unk`` hiçbir paydaya girmez.
# - Fiil: Zeyrek'in genel (son) türü ``Verb``. ``yazılan`` (→Adj) fiil
#   değil; ``evdeydi`` (Noun→Zero→Verb) fiil. Fiil oranlarının paydası budur.
# - Ek sayan ölçüler (derinlik, karakter, zincir, yapım, çeşitlilik) yalnız
#   yazıda görünen ekleri sayar; tür etiketleri ek değildir. Etiket oranları
#   görünmeyen etiketi de okur (``gelmem``: görünmeyen ``Aor``).
# - Yapım eki: Zeyrek'in türetimsellik işareti (çatı ve ``-ebil`` dahil).
# - Birleşik zamanda son zaman eki sayılır (``gidiyordum`` → geçmiş).
# - ``-eme`` (``Unable``) hem olumsuzluk hem yeterlilik.
# - Çoğul: ``A3pl`` isim parçasına bağlıysa (``öğrencilerdi``), fiil
#   parçasına bağlıysa kişi eki (``geldiler``).

Morpheme = tuple[str, str, bool]

_ZEYREK_TURLER = frozenset({
    "Noun", "Verb", "Adj", "Adv", "Pron", "Det", "Conj", "Postp", "Num",
    "Interj", "Punc", "Ques", "Dup", "Unk",
})
_KELIME_DISI_KOK = frozenset({"Unk", "Punc"})
_ZAMANLAR: dict[str, str] = {
    "Past": "zeyrek_tense_past_def_ratio", "Narr": "zeyrek_tense_past_nar_ratio",
    "Fut": "zeyrek_tense_future_ratio", "Prog1": "zeyrek_tense_present_ratio",
    "Prog2": "zeyrek_tense_present_ratio", "Aor": "zeyrek_tense_present_ratio",
}
_ZAMAN_ANAHTARLARI = ("zeyrek_tense_past_def_ratio", "zeyrek_tense_past_nar_ratio",
                      "zeyrek_tense_present_ratio", "zeyrek_tense_future_ratio")
_DURUMLAR = (("Acc", "zeyrek_case_acc_ratio"), ("Dat", "zeyrek_case_dat_ratio"),
             ("Loc", "zeyrek_case_loc_ratio"), ("Abl", "zeyrek_case_abl_ratio"),
             ("Gen", "zeyrek_case_gen_ratio"), ("Ins", "zeyrek_case_ins_ratio"))


def _kelime_morfemleri(morpheme_lists: list[list[Morpheme]],
                       pos_data: list[tuple[str, str]]) -> list[list[Morpheme]]:
    """Kelime olan ve çözümlenebilen tokenlerin morfemleri; hizasızlıkta ``ValueError``."""
    if len(morpheme_lists) != len(pos_data):
        raise ValueError(
            f"morpheme_lists ({len(morpheme_lists)}) is not aligned with pos_data "
            f"({len(pos_data)}) — preprocessing error"
        )
    return [m for m, (_, p) in zip(morpheme_lists, pos_data, strict=False)
            if m and p not in NON_WORD_POS and m[0][0] not in _KELIME_DISI_KOK]


def _ekler(m: list[Morpheme]) -> list[Morpheme]:
    """Kök ve tür etiketleri dışındaki ögeler (görünmeyenler dahil)."""
    return [e for e in m[1:] if e[0] not in _ZEYREK_TURLER]


def _gorunen_ekler(m: list[Morpheme]) -> list[Morpheme]:
    return [e for e in _ekler(m) if e[1]]


def _etiketler(m: list[Morpheme]) -> set[str]:
    return {e[0] for e in _ekler(m)}


def _genel_tur(m: list[Morpheme]) -> str:
    """Zeyrek'in genel sözcük türü: listedeki son tür etiketi."""
    return next((e[0] for e in reversed(m) if e[0] in _ZEYREK_TURLER), m[0][0])


def _fiiller(kelimeler: list[list[Morpheme]]) -> list[list[Morpheme]]:
    return [m for m in kelimeler if _genel_tur(m) == "Verb"]


def _fiil_orani(fiiller: list[list[Morpheme]], etiketler: set[str]) -> float:
    """Etiketlerden birini taşıyan fiil / fiil; fiil yoksa NaN."""
    return _oran(sum(1 for m in fiiller if _etiketler(m) & etiketler), len(fiiller))


def zeyrek_agglutination_depth(morpheme_lists: list[list[Morpheme]],
                        pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """Kelime başına ortalama görünen ek sayısı."""
    kelimeler = _kelime_morfemleri(morpheme_lists, pos_data)
    if not kelimeler:
        return {"zeyrek_agglutination_depth": math.nan}
    ortalama = sum(len(_gorunen_ekler(m)) for m in kelimeler) / len(kelimeler)
    return {"zeyrek_agglutination_depth": round(ortalama, 5)}


def zeyrek_suffix_char_length_ratio(morpheme_lists: list[list[Morpheme]],
                             pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """Ek harfleri / kelime harfleri (kök + ekler, Zeyrek yüzeyleriyle)."""
    kelimeler = _kelime_morfemleri(morpheme_lists, pos_data)
    ek = sum(len(e[1]) for m in kelimeler for e in _ekler(m))
    toplam = sum(len(e[1]) for m in kelimeler for e in m)
    return {"zeyrek_suffix_char_length_ratio": _oran(ek, toplam)}


def suffix_ngrams(morpheme_lists: list[list[Morpheme]],
                  pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """Ek zinciri: kelime içi ardışık ek çiftlerinin entropisi (nat).

    Çift yoksa NaN. ``suffix_chain_cv`` 2026-10-08'de kaldırıldı (Efe).
    """
    kelimeler = _kelime_morfemleri(morpheme_lists, pos_data)
    zincirler = [[e[0] for e in _gorunen_ekler(m)] for m in kelimeler]
    ciftler = Counter(c for z in zincirler for c in zip(z, z[1:], strict=False))
    entropi = math.nan
    if ciftler:
        n = sum(ciftler.values())
        entropi = round(-sum(k / n * math.log(k / n) for k in ciftler.values()), 5) + 0.0
    return {"zeyrek_suffix_bigram_entropy": entropi}


def zeyrek_derivational_suffix_ratio(morpheme_lists: list[list[Morpheme]],
                              pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """Yapım eki / görünen ek (Zeyrek'in türetimsellik işareti)."""
    ekler = [e for m in _kelime_morfemleri(morpheme_lists, pos_data) for e in _gorunen_ekler(m)]
    return {"zeyrek_derivational_suffix_ratio": _oran(sum(1 for e in ekler if e[2]), len(ekler))}


def zeyrek_verb_suffix_diversity(morpheme_lists: list[list[Morpheme]], pos_data: list[tuple[str, str]],
                          params: FeatureParams = DEFAULT_PARAMS) -> dict[str, float]:
    """Sabit boy fiil parçalarında farklı görünen ek türü sayısının ortalaması.

    Fiiller ``params.verb_suffix_window``'luk ardışık parçalara bölünür, sondaki
    eksik parça atılır (MSTTR mantığı: metin uzunluğundan bağımsız). Tam parça
    yoksa NaN.
    """
    fiiller = _fiiller(_kelime_morfemleri(morpheme_lists, pos_data))
    boy = params.verb_suffix_window
    parcalar = [fiiller[i:i + boy] for i in range(0, len(fiiller) - boy + 1, boy)] if boy > 0 else []
    if not parcalar:
        return {"zeyrek_verb_suffix_diversity": math.nan}
    turler = [len({e[0] for m in p for e in _gorunen_ekler(m)}) for p in parcalar]
    return {"zeyrek_verb_suffix_diversity": round(sum(turler) / len(turler), 5)}


def tense_ratios(morpheme_lists: list[list[Morpheme]],
                 pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """Zaman eki taşıyan fiil / fiil; fiilin son zaman eki sayılır.

    Şimdiki/geniş = ``Prog1`` (-yor), ``Prog2`` (-makta), ``Aor`` (-r).
    """
    fiiller = _fiiller(_kelime_morfemleri(morpheme_lists, pos_data))
    sayac: Counter[str] = Counter()
    for m in fiiller:
        zamanlar = [_ZAMANLAR[e[0]] for e in _ekler(m) if e[0] in _ZAMANLAR]
        if zamanlar:
            sayac[zamanlar[-1]] += 1
    return {k: _oran(sayac[k], len(fiiller)) for k in _ZAMAN_ANAHTARLARI}


def modal_suffix_ratios(morpheme_lists: list[list[Morpheme]],
                        pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """Kip eki oranları — payda fiil, ``tense_ratios`` ile aynı.

    Öngörü kipi için ayrı anahtar yok — ``zeyrek_tense_future_ratio`` onu ölçüyor.
    """
    fiiller = _fiiller(_kelime_morfemleri(morpheme_lists, pos_data))
    return {"zeyrek_modal_possibility_ratio": _fiil_orani(fiiller, {"Able", "Unable"}),
            "zeyrek_modal_necessity_ratio": _fiil_orani(fiiller, {"Neces"})}


def zeyrek_negation_ratio(morpheme_lists: list[list[Morpheme]],
                   pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """Olumsuz fiil (``-me``, ``-eme``) / fiil."""
    fiiller = _fiiller(_kelime_morfemleri(morpheme_lists, pos_data))
    return {"zeyrek_negation_ratio": _fiil_orani(fiiller, {"Neg", "Unable"})}


def zeyrek_passive_ratio(morpheme_lists: list[list[Morpheme]],
                  pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """Edilgen fiil / fiil."""
    fiiller = _fiiller(_kelime_morfemleri(morpheme_lists, pos_data))
    return {"zeyrek_passive_ratio": _fiil_orani(fiiller, {"Pass"})}


def mood_suffix_ratios(morpheme_lists: list[list[Morpheme]],
                       pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """Şart (``-se``) ve ettirgen (``-dır``, ``-t``) fiil / fiil."""
    fiiller = _fiiller(_kelime_morfemleri(morpheme_lists, pos_data))
    return {"zeyrek_conditional_suffix_ratio": _fiil_orani(fiiller, {"Cond"}),
            "zeyrek_causative_suffix_ratio": _fiil_orani(fiiller, {"Caus"})}


def _isim_cogulu(m: list[Morpheme]) -> bool:
    """Fiil olmayan bir parçaya bağlı ``A3pl`` var mı?"""
    tur = m[0][0]
    for e in m[1:]:
        if e[0] in _ZEYREK_TURLER:
            tur = e[0]
        elif e[0] == "A3pl" and tur != "Verb":
            return True
    return False


def zeyrek_plural_ratio(morpheme_lists: list[list[Morpheme]],
                 pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """Çoğul (``-ler`` isim parçasında) kelime / kelime."""
    kelimeler = _kelime_morfemleri(morpheme_lists, pos_data)
    return {"zeyrek_plural_ratio": _oran(sum(1 for m in kelimeler if _isim_cogulu(m)), len(kelimeler))}


def case_suffix_ratios(morpheme_lists: list[list[Morpheme]],
                       pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """Hâl eki taşıyan kelime / kelime (altı hâl)."""
    kelimeler = _kelime_morfemleri(morpheme_lists, pos_data)
    etiketler = [_etiketler(m) for m in kelimeler]
    return {anahtar: _oran(sum(1 for e in etiketler if hal in e), len(kelimeler))
            for hal, anahtar in _DURUMLAR}


def zeyrek_question_particle_ratio(morpheme_lists: list[list[Morpheme]],
                            pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """Soru eki (Zeyrek türü ``Ques``, çekimliler dahil) / kelime."""
    kelimeler = _kelime_morfemleri(morpheme_lists, pos_data)
    return {"zeyrek_question_particle_ratio": _oran(sum(1 for m in kelimeler if m[0][0] == "Ques"),
                                             len(kelimeler))}


def zeyrek_morfoloji(morpheme_lists: list[list[Morpheme]], pos_data: list[tuple[str, str]],
                     params: FeatureParams = DEFAULT_PARAMS) -> dict[str, float]:
    """``morphological_zeyrek`` grubunun 23 anahtarı."""
    sonuc: dict[str, float] = {}
    for fonksiyon in (zeyrek_agglutination_depth, zeyrek_suffix_char_length_ratio, suffix_ngrams,
                      zeyrek_derivational_suffix_ratio, tense_ratios, modal_suffix_ratios,
                      zeyrek_negation_ratio, zeyrek_passive_ratio, zeyrek_plural_ratio, case_suffix_ratios,
                      mood_suffix_ratios, zeyrek_question_particle_ratio):
        sonuc.update(fonksiyon(morpheme_lists, pos_data))
    sonuc.update(zeyrek_verb_suffix_diversity(morpheme_lists, pos_data, params))
    return sonuc
