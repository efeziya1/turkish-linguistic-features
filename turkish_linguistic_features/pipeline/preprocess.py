"""Boru hattı çıktısının ortak veri yapısı."""

from __future__ import annotations

from dataclasses import dataclass

Morpheme = tuple[str, str, bool]      # (etiket, yüzey_ek, türetimsel_mi)
DepToken = tuple[int, str, str, int]  # (index, pos, deprel, head_index)

# Why bu sıra: etiket POZISYON 0'da. Tüm etiket eşleşmeli öznitelik
# fonksiyonları `m[0]`dan okuyor (`if m[0] == "A3pl"`). Ters yazılırsa
# hiçbir etiket tutmaz ve ~14 öznitelik sessizce 0.0 döner; hata T20'ye
# kadar görünmez. Ölçüldü (2026-08-21): çalışan eski kod
# `(morph.id_, surf, morph.derivational)` üretiyor.
#
# Why üçüncü alan: `derivational_suffix_ratio()` (T16) türetimsel ekleri
# elle tutulan bir yüzey-biçim listesinden değil, Zeyrek'in kendi
# morfotaktik modelinden okuyor. Bu bayrak olmadan o öznitelik
# hesaplanamaz — ölçüldü: eski kodda ikili tuple `IndexError` veriyor.


@dataclass(frozen=True)
class ProcessedText:
    """Ön işlemeden çıkan yapılandırılmış metin.

    Tüm alanlar ``_extract_features()``'ın beklediği formatta. Doğrudan
    açmak için ``to_dict()`` kullan.
    """

    raw_text:            str
    surface_tokens:      tuple[str, ...]
    lemma_tokens:        tuple[str, ...]
    pos_data:            tuple[tuple[str, str], ...]
    sentences_as_tokens: tuple[tuple[str, ...], ...]
    morpheme_lists:      tuple[tuple[Morpheme, ...], ...] = ()
    morph_tags:          tuple[tuple[str, str], ...] = ()
    lang:                str = "tr"
    dep_data:            tuple[tuple[DepToken, ...], ...] | None = None

    def to_dict(self) -> dict:
        """``_extract_features(**processed.to_dict())`` için kwargs döndürür.

        İç mekanizma — kullanıcıya öğretilen bir kalıp değil (normal yol
        ``analyze()``).
        """
        return {
            "raw_text":            self.raw_text,
            "surface_tokens":      list(self.surface_tokens),
            "lemma_tokens":        list(self.lemma_tokens),
            "pos_data":            [tuple(p) for p in self.pos_data],
            "sentences_as_tokens": [list(s) for s in self.sentences_as_tokens],
            "morpheme_lists":      [list(m) for m in self.morpheme_lists],
            "morph_tags":          [tuple(m) for m in self.morph_tags],
            "lang":                self.lang,
            "dep_data":            self.dep_data,
        }
