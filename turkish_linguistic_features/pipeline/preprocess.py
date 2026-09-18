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


class TurkishPreprocessor:
    """Türkçe boru hattı — morfoloji Zeyrek'ten, tokenizasyon spaCy'den.

    Zeyrek bağımlılık ayrıştırması yapmaz, bu yüzden ``dep_data`` her zaman
    ``None`` ve ``syntactic_dep`` grubunun 16 anahtarı üretilmez. Kalanı
    Türkçe taban şemanın tamamı: 207 − 16 = 191 anahtar.

    Eğitilmiş spaCy modeli **gerekmez** — yalnız ``spacy.blank("tr")``
    tokenizer'ı ve cümle bölücü kullanılıyor.
    """

    def __init__(self) -> None:
        from .zeyrek_backend import ZeyrekBackend
        self._backend = ZeyrekBackend()

    def process(self, text: str) -> ProcessedText:
        """Ham metni ``ProcessedText``e çevirir.

        ``sentences_as_tokens`` ve ``surface_tokens`` **aynı** tokenizer'dan
        gelir. ``.split()`` ile kurmak noktalamayı kelimeye yapıştırır ve aynı
        metin için iki farklı kelime sayısı üretir; ölçüldü (plan T22):
        ``avg_sent_len_word`` spaCy yolunda 5.5, ``.split()`` yolunda 3.0.
        """
        cumleler = self._backend.tokenize(text)

        surface_tokens: list[str] = []
        lemma_tokens: list[str] = []
        pos_data: list[tuple[str, str]] = []
        morpheme_lists: list[tuple[Morpheme, ...]] = []
        morph_tags: list[tuple[str, str]] = []

        from ..features.vocab import NON_WORD_POS
        from .zeyrek_backend import _zeyrek_to_ud_morph

        for cumle in cumleler:
            for token in cumle:
                cozum = self._backend.analyze_word(token)
                pos = cozum["pos"]
                morphemes = tuple(cozum["morphemes"])

                surface_tokens.append(token)
                pos_data.append((token, pos))
                morpheme_lists.append(morphemes)
                morph_tags.append((token, _zeyrek_to_ud_morph(morphemes, pos)))
                # Noktalama ve sembol lemma'ya girmez — `lemma_tokens`
                # NON_WORD_POS atılmış `pos_data` ile hizalı olmak zorunda (T21).
                if pos not in NON_WORD_POS:
                    lemma_tokens.append(cozum["lemma"].lower())

        return ProcessedText(
            raw_text=text,
            surface_tokens=tuple(surface_tokens),
            lemma_tokens=tuple(lemma_tokens),
            pos_data=tuple(pos_data),
            sentences_as_tokens=tuple(tuple(c) for c in cumleler),
            morpheme_lists=tuple(morpheme_lists),
            morph_tags=tuple(morph_tags),
            lang="tr",
            dep_data=None,            # Zeyrek ayrıştırma yapmaz
        )
