"""``analyze()`` — ham metinden öznitelik sözlüğüne, tek çağrıda (T24).

Ön işleme (``Preprocessor``, T21) ile öznitelik çıkarımını
(``_extract_features``, T18) birleştirir. Kütüphanenin ana giriş noktası;
kullanıcıların çoğu yalnız bunu çağırır.
"""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from ._warnings import MissingDependencyWarning, ParagraphStructureWarning
from .alfabe import _ALFABE
from .features.extractor import _extract_features

if TYPE_CHECKING:
    from .params import FeatureParams
    from .pipeline.spacy_pipeline import Preprocessor

__all__ = ["analyze"]

# 🔴 Model önbelleği. spaCy modelini yüklemek 2–5 saniye sürüyor; önbelleksiz
# 1000 metinlik bir korpus yalnız yükleme yaparak saatler harcardı.
#
# Anahtar ``(lang, model)``. ``chunk_chars`` 2026-08-25'te iç sabite
# dönüştüğü için anahtarın parçası değil — anahtar uzayı pratikte 1–2 girdi.
#
# ``clear_cache()`` YAZILMIYOR: iki önbellek de sınırlı. Bu sözlük 1–2 girdi,
# Zeyrek'in kelime memo'su ``lru_cache(50_000)`` ile 18,1 MB tavanlı. Soğuk
# başlangıç isteyen test bu sözlüğü doğrudan ``clear()`` eder; public bir
# fonksiyon gerekmiyor.
_preprocessor_cache: dict[tuple[str, str | None], Preprocessor] = {}


def _get_preprocessor(lang: str, model: str | None) -> Preprocessor:
    """Önbellekten preprocessor getirir, yoksa oluşturur.

    ``Preprocessor.__init__`` tembeldir — modeli ilk ``process()`` çağrısında
    yükler. Bu yüzden bu fonksiyon model kurulu olmadan da çalışır ve önbellek
    testleri modele bağlı değildir.
    """
    anahtar = (lang, model)
    if anahtar not in _preprocessor_cache:
        from .pipeline.spacy_pipeline import Preprocessor
        _preprocessor_cache[anahtar] = Preprocessor(lang=lang, model=model)
    return _preprocessor_cache[anahtar]


def analyze(text: str, lang: str = "tr", model: str | None = None,
            groups: list[str] | None = None,
            params: FeatureParams | None = None,
            custom_ngrams: list[list[str]] | None = None,
            show_progress: bool = False,
            warn: bool = True) -> dict[str, float]:
    """Bir metinden nicel dilsel öznitelikleri çıkarır.

    Model ilk çağrıda yüklenip önbelleğe alınır; aynı ayarlarla sonraki
    çağrılar onu yeniden kullanır.

    Parameters
    ----------
    text
        Analiz edilecek ham metin. Boş metin çökmez; ölçülemeyen öznitelikler
        ``NaN`` döner (K4).
    lang
        ``"tr"`` ya da ``"en"``. Dil şemayı belirler (K11).
    model
        Belirli bir spaCy modeli. ``None`` ise dilin varsayılanı.
    groups
        Yalnız bu öznitelik grupları üretilir. Pahalı grupları atlamak
        (``syntactic_dep``, ``lexical``) korpus çalıştırmalarını hızlandırır.
    params
        Metrik sabitleri. ``None`` ise ``DEFAULT_PARAMS``.
    custom_ngrams
        Kendi kelime öbekleriniz → ``ng_{...}`` sütunları. Taban şemayı
        **genişletir**; taban bir tavan değildir.
    show_progress
        Uzun metin parçalanırken ilerleme yazdırılsın mı. Varsayılan
        ``False`` — kütüphane kendiliğinden ekrana yazmaz.
    warn
        ``False`` ise bu kütüphanenin kendi uyarıları bastırılır: eksik
        opsiyonel bağımlılık (şu an yalnız ``wordfreq``) ve paragraf sınırı
        bulunamadı uyarısı. Üçüncü taraf uyarıları susturulmaz.

    Returns
    -------
    dict[str, float]
        Öznitelik anahtarı → değer. Taban şema Türkçede 208, İngilizcede 182
        anahtar; ``custom_ngrams`` verilirse üstüne sütun eklenir.

    Raises
    ------
    ValueError
        Desteklenmeyen dil ya da bilinmeyen öznitelik grubu.
    ModelNotFoundError
        spaCy modeli kurulu değilse; mesaj kurulum komutunu içerir.

    Examples
    --------
    >>> feats = analyze("Bu bir deneme metnidir. İkinci cümle.", lang="tr")
    >>> feats["avg_sent_len_word"]
    3.5
    """
    if lang not in _ALFABE:
        raise ValueError(f"Unsupported language: {lang!r}. Expected one of: {sorted(_ALFABE)}")

    islenmis = _get_preprocessor(lang, model).process(text, show_progress=show_progress)
    with warnings.catch_warnings():
        if not warn:
            warnings.simplefilter("ignore", MissingDependencyWarning)
            warnings.simplefilter("ignore", ParagraphStructureWarning)
        return _extract_features(**islenmis.to_dict(), groups=groups, params=params,
                                 custom_ngrams=custom_ngrams)
