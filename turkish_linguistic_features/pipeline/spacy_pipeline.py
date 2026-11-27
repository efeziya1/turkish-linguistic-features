"""spaCy boru hattı — ham metin → ``ProcessedText`` (T21).

``analyze()``'ın kullandığı tek ön işleme yolu, iki dil için de.
``surface_tokens``, ``sentences_as_tokens``, ``pos_data``, ``morph_tags`` ve
``dep_data`` eğitilmiş spaCy modelinden gelir; ``lemma_tokens`` İngilizcede de.

İki istisna Türkçede ``AkanaBackend``'den gelir: ``morpheme_lists`` (spaCy
morfolojik **ek bölütlemesi** üretmiyor, K11) ve ``lemma_tokens`` (2026-10-07,
Efe: çözümleyicinin sözlük maddesi). İngilizcede ``morpheme_lists`` boş kalır. Akana her sözcüğün
çözümlemesini belirsizlik gidericisiyle seçer; gidericiye aracın tümce kuralının
tümceleri gider (``units.sentences.kural_cumleleri``; 0.4.0, Efe).

Katman **sessiz**: varsayılan çağrıda hiçbir şey yazdırmaz, uyarı vermez
(2026-08-25).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import spacy

from ..alphabet import _kucuk_harf
from ..exceptions import ModelNotFoundError
from ..units.sentences import kural_cumleleri
from ..vocab import NON_WORD_POS
from .preprocess import Morpheme, ProcessedText

if TYPE_CHECKING:
    from .akana_backend import AkanaBackend

__all__ = ["Preprocessor"]

_DEFAULT_MODEL = {"tr": "tr_core_news_md", "en": "en_core_web_sm"}

# İç sabit — hiçbir imzada geçmiyor (2026-08-25). Uzun metnin kaç karakterlik
# parçalara bölüneceği kullanıcının bilmesi gereken bir şey değil.
_DEFAULT_CHUNK_CHARS = 50_000

# Model kurulumu kullanıcıya bırakıldı (2026-09-18, Efe): `download_model()`
# çıkarıldı. Kütüphanenin çalışma anında kullanıcının ortamına paket kurması
# salt-okunur konteynerde, kısıtlı CI'da ve bazı conda kurulumlarında
# çalışmıyor; üstelik tek bir HuggingFace deposunun sabit sürümlü URL'ine
# bağlıydı. Komutlar hata mesajında ve README'de; kullanıcı elle çalıştırıyor.
_KURULUM = {
    "en": "To install it:\n  python -m spacy download en_core_web_sm",
    "tr": ("To install it (this model is not in the spaCy registry; install the wheel directly):\n"
           "  pip install https://huggingface.co/turkish-nlp-suite/"
           "tr_core_news_md/resolve/main/tr_core_news_md-1.0-py3-none-any.whl"),
}


def _split_chunks(text: str, max_chars: int) -> list[str]:
    """Metni en fazla ``max_chars`` uzunluğunda parçalara böler.

    spaCy'nin varsayılan bellek sınırı ~1 MB; bir roman bunu aşar. Kesim
    noktası önceliği: paragraf sonu → satır sonu → cümle sonu → boşluk.
    Hiçbiri bulunamazsa sert kesim (çok uzun tek kelime).
    """
    if len(text) <= max_chars:
        return [text]

    parcalar: list[str] = []
    bas = 0
    while bas < len(text):
        son = min(bas + max_chars, len(text))
        if son == len(text):
            parcalar.append(text[bas:])
            break
        for ayirac in ("\n\n", "\n", ". ", " "):
            kesim = text.rfind(ayirac, bas, son)
            if kesim != -1:
                kesim += len(ayirac)
                break
        else:
            kesim = son                      # boşluk yok — sert kes
        # 🔴 `rfind` parça başlangıcından önce bir ayraç bulursa `kesim` geriye
        # gider ve döngü ilerlemez → program donar. Bu satır o korumadır.
        if kesim <= bas:
            kesim = son
        parcalar.append(text[bas:kesim])
        bas = kesim

    return [p for p in parcalar if p.strip()]


class Preprocessor:
    """Ham metni öznitelik katmanının beklediği yapıya çevirir.

    Parameters
    ----------
    lang
        ``"tr"`` ya da ``"en"``. Dil şemayı belirler (K11).
    model
        spaCy model adı. ``None`` ise dilin varsayılanı.
    """

    def __init__(self, lang: str = "tr", model: str | None = None) -> None:
        self.lang = lang
        self.model_name = model or _DEFAULT_MODEL.get(lang, _DEFAULT_MODEL["en"])
        self._nlp: spacy.language.Language | None = None
        self._morph_backend: AkanaBackend | None = None

    def _ensure_loaded(self) -> None:
        if self._nlp is not None:
            return
        try:
            # NER hiçbir öznitelik tarafından kullanılmıyor (`doc.ents` okuyan
            # yok); devre dışı bırakmak belge başına süreyi ~yarıya indiriyor.
            self._nlp = spacy.load(self.model_name, exclude=["ner"])
        except OSError:
            raise ModelNotFoundError(
                f"spaCy model '{self.model_name}' not found.\n\n"
                f"{_KURULUM.get(self.lang, _KURULUM['en'])}\n\n"
                "Details and known quirks: see README, 'Language data'."
            ) from None

    @staticmethod
    def _tokens_from_doc(doc, lang: str) -> tuple:
        """Bir spaCy ``Doc``'undan altı alanı çıkarır.

        Returns
        -------
        (surface_tokens, pos_data, morph_tags, sentences_as_tokens,
         lemma_tokens, dep_data)
        """
        surface_tokens: list[str] = []
        pos_data: list[tuple[str, str]] = []
        morph_tags: list[tuple[str, str]] = []
        lemma_tokens: list[str] = []
        sentences_as_tokens: list[tuple[str, ...]] = []
        dep_data: list[tuple] = []

        for tok in doc:
            if tok.is_space:
                continue
            surface_tokens.append(tok.text)
            pos_data.append((tok.text, tok.pos_))
            morph_tags.append((tok.text, str(tok.morph)))
            # Noktalama ve sembol `lemma_tokens`'a GİRMEZ — kelime zenginliği
            # ölçüleri bunları saymamalı. `surface_tokens`'a girer: karakter ve
            # noktalama oranları için gerekli.
            if tok.pos_ not in NON_WORD_POS:
                # Dile göre küçük harf: `str.lower()` "İstanbul"u U+0307'li
                # "i̇stanbul" yapıyordu, "istanbul"la aynı lemma sayılmıyordu.
                lemma_tokens.append(_kucuk_harf(tok.lemma_, lang))

        for sent in doc.sents:
            toks = [t for t in sent if not t.is_space]
            if not toks:
                continue
            sentences_as_tokens.append(tuple(t.text for t in toks))
            # Belge içi index → cümle içi index. Baş göstergeleri cümle-yerel
            # uzaya çevrilir; böylece yay uzunluğu ve derinlik yürüyüşü asla
            # cümle sınırını aşmaz. Belge indeksi kalsaydı 500. cümledeki bir
            # token'ın yay uzunluğu binlerce çıkardı.
            yerel = {t.i: i for i, t in enumerate(toks)}
            dep_data.append(tuple(
                (i, t.pos_, t.dep_, yerel.get(t.head.i, i))
                for i, t in enumerate(toks)
            ))

        return (surface_tokens, pos_data, morph_tags, sentences_as_tokens,
                lemma_tokens, dep_data)

    def _akana(self, surface: list[str],
               pos: list[tuple[str, str]]) -> tuple[tuple[tuple[Morpheme, ...], ...], list[str]]:
        """Turkish ``morpheme_lists`` and ``lemma_tokens`` from Akana, sentence by sentence.

        Akana's disambiguator picks each token's analysis within a sentence of the library's
        own sentence rule (``kural_cumleleri``), the same sentences every other group uses;
        not spaCy's parser sentences (0.4.0, Efe, 2026-11-24). On the 57 TOMA texts the two
        splits changed one analysis in 21,251 tokens and no feature value.

        ``morpheme_lists`` is aligned with ``surface_tokens``; ``lemma_tokens`` with
        its word tokens (punctuation and symbols left out, T21). spaCy's Turkish lemma left
        inflected forms as lemmas (15 % of words in TOMA); the analyser's dictionary entry
        replaces it (2026-10-07, Efe). ``akana`` is a required dependency (K1).
        """
        cumleler = kural_cumleleri(surface, "tr")
        morf = self._morph()
        secilen = [a for c in cumleler for a in morf.analyze_sentence(c)]
        morfemler = tuple(m for m, _ in secilen)
        lemmas = [_kucuk_harf(lem, "tr")
                  for (_, lem), (_, p) in zip(secilen, pos, strict=True) if p not in NON_WORD_POS]
        return morfemler, lemmas

    def _morph(self) -> AkanaBackend:
        if self._morph_backend is None:
            from .akana_backend import AkanaBackend
            self._morph_backend = AkanaBackend()
            self._morph_backend._ensure_loaded()
        return self._morph_backend

    def _ozel_adlar(self, doc, pos: list[tuple[str, str]]) -> list[tuple[str, str]]:
        """Turkish: tokens inside a person, place or organisation name become ``PROPN``.

        Names come from Akana's named-entity recogniser (``AkanaBackend.proper_noun_spans``);
        spaCy's Turkish model leaves many of them ``NOUN`` or ``ADJ`` (``Derya``,
        ``Almanya'da``). Punctuation, symbols and tokens without a letter keep their tag
        (0.4.0, Efe, 2026-11-25). ``dep_data`` keeps spaCy's tags, so ``syntactic`` is
        unaffected. ``pos`` is aligned with the non-space tokens of ``doc``.
        """
        araliklar = self._morph().proper_noun_spans(doc.text)
        if not araliklar:
            return pos
        out = list(pos)
        i = 0
        for tok in doc:
            if tok.is_space:
                continue
            a, b = tok.idx, tok.idx + len(tok.text)
            if (out[i][1] not in NON_WORD_POS and any(c.isalpha() for c in tok.text)
                    and any(s < b and a < e for s, e in araliklar)):
                out[i] = (out[i][0], "PROPN")
            i += 1
        return out

    def _birlestir(self, raw_text: str, dokumanlar: list) -> ProcessedText:
        """Parça ``Doc``'larını tek ``ProcessedText``te toplar."""
        surface: list[str] = []
        pos: list[tuple[str, str]] = []
        morph: list[tuple[str, str]] = []
        cumleler: list[tuple[str, ...]] = []
        lemma: list[str] = []
        dep: list[tuple] = []

        for doc in dokumanlar:
            s, p, m, c, lm, d = self._tokens_from_doc(doc, self.lang)
            if self.lang == "tr":
                p = self._ozel_adlar(doc, p)
            surface += s
            pos += p
            morph += m
            cumleler += c
            lemma += lm
            dep += d

        morfemler: tuple[tuple[Morpheme, ...], ...] = ()
        if self.lang == "tr":
            # İngilizcede morpheme_lists boş (K11), lemma spaCy'nin.
            morfemler, lemma = self._akana(surface, pos)

        return ProcessedText(
            raw_text=raw_text,
            surface_tokens=tuple(surface),
            lemma_tokens=tuple(lemma),
            pos_data=tuple(pos),
            sentences_as_tokens=tuple(cumleler),
            morpheme_lists=morfemler,
            morph_tags=tuple(morph),
            lang=self.lang,
            dep_data=tuple(dep),
        )

    def process(self, text: str, show_progress: bool = False) -> ProcessedText:
        """Tek metni işler.

        Uzun metin ``_DEFAULT_CHUNK_CHARS`` sınırında cümle sınırından
        parçalanır, parçalar ayrı ayrı işlenip tek çıktıda birleştirilir.
        """
        self._ensure_loaded()
        assert self._nlp is not None                   # _ensure_loaded doldurdu

        parcalar = _split_chunks(text, _DEFAULT_CHUNK_CHARS) if text.strip() else []
        dokumanlar = []
        for i, parca in enumerate(parcalar, 1):
            if show_progress:
                print(f"  chunk {i}/{len(parcalar)}", flush=True)
            dokumanlar.append(self._nlp(parca))

        return self._birlestir(text, dokumanlar)
