"""Korpustan öznitelik matrisi — ``_load_corpus`` ile ``analyze`` arasındaki köprü (L3).

Ayrı dosya, çünkü üç iş üç yerde durmalı: ``file_loader`` okur ve parçalar,
``_analyze`` tek metni ölçer, burası ikisini zincire bağlar.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._analyze import analyze
from .file_loader import _load_corpus

if TYPE_CHECKING:
    from pathlib import Path

    from .params import FeatureParams

__all__ = ["analyze_corpus"]


def analyze_corpus(path: str | Path, lang: str = "tr", segment_size: int = 1000,
                   *, min_fill: float = 1.0, unit: str = "word",
                   model: str | None = None,
                   groups: list[str] | None = None,
                   params: FeatureParams | None = None,
                   custom_ngrams: list[list[str]] | None = None,
                   show_progress: bool = False,
                   warn: bool = True) -> list[dict[str, object]]:
    """Bir korpusu okur, parçalar ve her parçanın özniteliklerini çıkarır.

    Zincirin tamamı tek çağrıda::

        rows = analyze_corpus("korpus/", lang="tr", segment_size=1000)
        save_csv(rows, "sonuc.csv")

    2026-09-23'ten önce bu zinciri kullanıcı kuruyordu: ``load_corpus()``
    kayıt listesi veriyor ama onunla ne yapılacağını söylemiyordu, zinciri
    kapatan ``records_to_csv`` ise public değildi. ``examples/02`` aradaki
    döngüyü elle yazıyordu — yani örnek script eksik API'nin yerine geçmişti.

    Korpus düzeni ``_load_corpus``'un algıladığı üç biçimden biri::

        korpus/Etiket_Başlık.txt      düz dosya
        korpus/Etiket/dosya.txt       etiket alt klasörü
        korpus.csv                    etiket + metin sütunu

    Parameters
    ----------
    path
        Korpus klasörü ya da CSV dosyası.
    lang
        ``"tr"`` ya da ``"en"``. Hem parçalamaya hem analize geçer.
    segment_size
        Parça başına token (``unit="word"``) ya da karakter (``"char"``).
    min_fill
        Son parça bu orandan az doluysa atılır. Ayrıntı → ``segment_text``.
    unit
        ``"word"`` ya da ``"char"``.
    model, groups, params, custom_ngrams, warn
        Olduğu gibi ``analyze()``'a geçer; anlamları orada.
    show_progress
        Parça sayacı yazdırılsın mı: ``[12/87] Etiket_Başlık.txt #3``.
        Varsayılan ``False`` — kütüphane kendiliğinden ekrana yazmaz.

        ``analyze()``'a **her zaman** ``show_progress=False`` geçilir:
        onunki tek metin ön işlenirken ilerleme gösteriyor, korpus
        koşusunda iki sayaç iç içe girip çıktıyı okunmaz hale getirirdi.

    Returns
    -------
    list[dict]
        Parça başına bir düz sözlük::

            {"label": ..., "source": ..., "segment_id": ..., **öznitelikler}

        Doğrudan ``save_csv()``'ye verilebilir. Hiç parça çıkmazsa boş liste —
        metinler ``segment_size``'dan kısaysa olağan sonuç budur.

    Raises
    ------
    FileNotFoundError
        ``path`` yoksa.
    ModelNotFoundError
        Dil modeli kurulu değilse; mesaj kurulum komutunu içerir.

    See Also
    --------
    analyze : Tek metin.
    segment_text : Yalnız parçalama, analiz yok.
    save_csv : Dönen kayıtları CSV'ye yazar.
    """
    kayitlar = _load_corpus(path, segment_size=segment_size, min_fill=min_fill,
                            unit=unit, lang=lang)

    satirlar: list[dict[str, object]] = []
    for i, kayit in enumerate(kayitlar, 1):
        if show_progress:
            print(f"  [{i}/{len(kayitlar)}] {kayit['source']} #{kayit['segment_id']}")
        oznitelikler = analyze(str(kayit["text"]), lang=lang, model=model,
                               groups=groups, params=params,
                               custom_ngrams=custom_ngrams,
                               show_progress=False, warn=warn)
        satirlar.append({"label": kayit["label"], "source": kayit["source"],
                         "segment_id": kayit["segment_id"], **oznitelikler})
    return satirlar
