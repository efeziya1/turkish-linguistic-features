"""Bağımlılık ağacı: ortalama mesafe, ortalama derinlik ve cümle sonu türü (T17).

``syntactic_dep`` grubunun 16 anahtarı:

- ``arc_len_mean`` — ortalama bağımlılık mesafesi (MDD2)
- ``parse_depth_mean`` — ortalama hiyerarşik mesafe (MHD2)
- 14 × ``sentfinal_*`` — son kelimesi o türde olan cümle / cümle

Kaynak: Liu (2008) mesafeyi, Jing & Liu (2015) derinliği ve ikisinin metin
düzeyini tanımlıyor. Kararlar (2026-09-17, Efe):

- Metin değeri = cümle değerlerinin ortalaması (Jing & Liu 2015, formül 3–4).
  Liu (2008, formül 2) bütün bağları tek havuzda ortalıyor; bu yol seçilmedi.
- Noktalama ve sembol (``NON_WORD_POS``) atılır ve kelimeler yeniden
  sıralanır ("punctuation marks are rejected", Jing & Liu 2015). Kökün
  mesafesi ve derinliği sayılmaz. Kelimesi kökten ibaret cümle hesaba girmez.
- Cümle sonu: noktalama atlanır; 13 türe girmeyen son ``sentfinal_other``'a
  düşer, 14 oranın toplamı 1.
- ``dep_*`` oranları, ``_cv``/``_max`` özetleri, bağlaç ve sıfat ayrımı,
  devriklik ve mesafe entropisi çıkarıldı; ``dep_*`` sonra yeniden bakılacak.

spaCy'nin İngilizce modeli UD değil, başka bir ağaç şeması kullanıyor;
İngilizce ve Türkçe değerler karşılaştırılamaz (T21'de yeniden bakılacak).
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Sequence

from .params import DEFAULT_PARAMS, FeatureParams
from .vocab import NON_WORD_POS, SENT_FINAL_POS

DepToken = tuple[int, str, str, int]   # (sıra, POS, ilişki, baş sırası); kök kendini gösterir

_SONLAR = tuple(p.lower() for p in SENT_FINAL_POS) + ("other",)


def _derinlik(baslar: dict[int, int], baslangic: int, max_depth: int) -> int:
    """Kelimeden köke adım sayısı; döngüde ya da ``max_depth``'te durur."""
    derinlik = 0
    su_an = baslangic
    gorulen = {baslangic}
    while derinlik < max_depth:
        bas = baslar.get(su_an, su_an)
        if bas == su_an or bas in gorulen:
            break
        gorulen.add(bas)
        su_an = bas
        derinlik += 1
    return derinlik


def _ortalama(degerler: list[float]) -> float:
    return round(sum(degerler) / len(degerler), 5) if degerler else math.nan


def dependency_features(dep_data: Sequence[Sequence[DepToken]],
                        params: FeatureParams = DEFAULT_PARAMS) -> dict[str, float]:
    """``syntactic_dep`` grubunun 16 anahtarı; girdi cümle başına token dizisi."""
    mdd: list[float] = []
    mhd: list[float] = []
    sonlar: Counter[str] = Counter()
    for cumle in dep_data:
        kelimeler = [t for t in cumle if t[1] not in NON_WORD_POS]
        if not kelimeler:
            continue
        son = kelimeler[-1][1]
        sonlar[son.lower() if son in SENT_FINAL_POS else "other"] += 1
        sira = {t[0]: k for k, t in enumerate(kelimeler)}
        baslar = {t[0]: t[3] for t in cumle}
        bagli = [t for t in kelimeler if t[3] != t[0]]
        mesafeler = [abs(sira[t[0]] - sira[t[3]]) for t in bagli if t[3] in sira]
        if mesafeler:
            mdd.append(sum(mesafeler) / len(mesafeler))
        if bagli:
            derinlikler = [_derinlik(baslar, t[0], params.max_parse_depth) for t in bagli]
            mhd.append(sum(derinlikler) / len(derinlikler))
    n_cumle = sum(sonlar.values())
    sonuc = {"arc_len_mean": _ortalama(mdd), "parse_depth_mean": _ortalama(mhd)}
    for ad in _SONLAR:
        sonuc[f"sentfinal_{ad}"] = round(sonlar[ad] / n_cumle, 5) if n_cumle else math.nan
    return sonuc
