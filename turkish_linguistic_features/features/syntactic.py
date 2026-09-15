"""Sözdizimi yüzeyi: POS oranları, POS ızgarası, cümle ve paragraf istatistikleri.

Bu modül T11'in anahtarlarını üretir:

- ``pos`` (13): ``pos_noun`` … ``pos_punct``
- ``pos_bigrams`` (169): ``posbg_{A}_{B}``, sabit 13×13 ızgara
- ``sentence`` (8) ve ``paragraph`` (5)
- ``syntactic`` grubunun 8'i: ``pos_trigram_entropy``, ``nominal_verbal_ratio``,
  ``verb_dist_mean``, ``verb_dist_cv``, ``activity_ratio``, ``lexical_density``,
  ``pos_dist_std``, ``pos_kl_div`` (kalan 8'i T12)

Fonksiyonlar saftır (K3): girdi ``pos_data`` = ``[(token, POS), …]``,
``sentences_as_tokens`` = ``[[token, …], …]`` ya da ham metin. NLP modeli almaz.
Ölçülemeyen değer ``0.0`` döner (K4).

Standart sapmalar **popülasyon** sapmasıdır (``ddof=0``) — ``lexical.py`` ile
aynı gerekçe: elimizdeki liste örneklem değil, metnin kendisi.
"""

from __future__ import annotations

import math
import re
from collections import Counter

import numpy as np

from .vocab import AUTOSEMANTIC_POS, POS_TAGS

_VERB_POS = ("VERB", "AUX")
_PARA_SPLIT = re.compile(r"\n[ \t]*\n")   # boş satır = paragraf sınırı
_SENT_END = re.compile(r"[.!?…]+")        # cümle sonu işareti


def _entropy_bits(sayimlar: Counter) -> float:
    """Sayım dağılımının Shannon entropisi, bit cinsinden."""
    toplam = sum(sayimlar.values())
    if toplam == 0:
        return 0.0
    return -sum((c / toplam) * math.log2(c / toplam) for c in sayimlar.values())


def _cv(degerler: np.ndarray) -> float:
    """Değişim katsayısı ``std / ortalama``; ortalama 0 ise 0.0."""
    ortalama = float(degerler.mean())
    return float(degerler.std()) / ortalama if ortalama > 0 else 0.0


# ── POS oranları ve ızgara ────────────────────────────────────────────


def pos_ratios(pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """13 POS etiketinin token oranı: ``etiket sayısı / toplam token``.

    Payda **tüm** tokenlerdir — ``POS_TAGS`` dışındaki etiketler (PRON, X, SYM)
    paydaya girer ama sütunu yoktur, bu yüzden 13 oranın toplamı 1'den küçük
    olabilir.
    """
    if not pos_data:
        return {f"pos_{t.lower()}": 0.0 for t in POS_TAGS}
    sayimlar = Counter(p for _, p in pos_data)
    n = len(pos_data)
    return {f"pos_{t.lower()}": round(sayimlar.get(t, 0) / n, 5) for t in POS_TAGS}


def pos_bigram_ratios(pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """13×13 sabit POS-çifti ızgarası: ``çift sayısı / (token sayısı − 1)``.

    Metinde hangi çiftler geçerse geçsin **her zaman 169 anahtar** döner.
    Görülmeyen çiftler 0.0 olur. Sabit ızgara, korpustan türetilmiş
    dinamik sözlüğün aksine çapraz doğrulamada sızıntı yaratmaz.
    """
    etiketler = [p for _, p in pos_data]
    sayimlar = Counter(zip(etiketler, etiketler[1:]))
    toplam = max(len(etiketler) - 1, 1)
    return {
        f"posbg_{a}_{b}": round(sayimlar.get((a, b), 0) / toplam, 5)
        for a in POS_TAGS for b in POS_TAGS
    }


def pos_trigram_entropy(pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """Ardışık POS üçlülerinin dağılımının Shannon entropisi, bit cinsinden.

    Yüksek = etiket dizilimleri çeşitli; 3'ten az tokende 0.0.
    """
    etiketler = [p for _, p in pos_data]
    if len(etiketler) < 3:
        return {"pos_trigram_entropy": 0.0}
    uclu = Counter(zip(etiketler, etiketler[1:], etiketler[2:]))
    return {"pos_trigram_entropy": round(_entropy_bits(uclu), 5)}


def nominal_verbal_ratio(pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """``NOUN sayısı / VERB sayısı``. Fiil yoksa 0.0.

    Tanım referans registry'deki "noun count / verb count" okumasıdır:
    yalnız ``NOUN`` ve yalnız ``VERB``. ``verb_distance_stats`` ve
    ``activity_ratio`` ise ``AUX``'u da fiil sayar — bu fark bilinçli değil
    tanımdan geliyor ve T11'in karar kaydında açık soru olarak duruyor.
    """
    sayimlar = Counter(p for _, p in pos_data)
    fiil = sayimlar.get("VERB", 0)
    if fiil == 0:
        return {"nominal_verbal_ratio": 0.0}
    return {"nominal_verbal_ratio": round(sayimlar.get("NOUN", 0) / fiil, 5)}


# ── fiil mesafesi ve activity ─────────────────────────────────────────


def verb_distance_stats(pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """Ardışık fiiller arasındaki token mesafesinin ortalaması ve CV'si.

    QUITA "Verb Distances (VD)". ``arc_len_mean`` ile KARIŞTIRMA: o bağımlılık
    yayının uzunluğu, bu yüzey konum mesafesi. ``AUX`` fiil sayılır: Türkçe'de
    ``-dir``, ``imek``, ``değil`` yüklem konumunda ``AUX`` etiketleniyor.
    """
    idx = [i for i, (_, p) in enumerate(pos_data) if p in _VERB_POS]
    if len(idx) < 2:
        return {"verb_dist_mean": 0.0, "verb_dist_cv": 0.0}
    d = np.diff(np.array(idx, dtype=np.float64))
    return {"verb_dist_mean": round(float(d.mean()), 4), "verb_dist_cv": round(_cv(d), 4)}


def activity_ratio(pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """QUITA "Activity (Q)" = fiil / (fiil + sıfat); fiil = ``VERB`` + ``AUX``.

    Descriptivity (D) = 1 − Q ayrı anahtar olarak üretilmez: tam ters
    bağıntılı ikinci bir sütun bilgi taşımaz.
    """
    v = sum(1 for _, p in pos_data if p in _VERB_POS)
    a = sum(1 for _, p in pos_data if p == "ADJ")
    if v + a == 0:
        return {"activity_ratio": 0.0}
    return {"activity_ratio": round(v / (v + a), 5)}


# ── yoğunluk ve dağılım ───────────────────────────────────────────────


def lexical_density(pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """Otosemantik (içerik) token oranı — Ure 1971.

    Süzgeç ``AUTOSEMANTIC_POS``: NOUN, PROPN, VERB, ADJ, ADV. Bu kümenin
    dışındaki her POS işlev sayılır — PUNCT dahil. ``nominal_verbal_ratio``
    bunun yerine geçmez: o isim/fiil dengesini, bu içerik/işlev dengesini verir.
    """
    if not pos_data:
        return {"lexical_density": 0.0}
    icerik = sum(1 for _, p in pos_data if p in AUTOSEMANTIC_POS)
    return {"lexical_density": round(icerik / len(pos_data), 5)}


def pos_distribution_stats(pos_data: list[tuple[str, str]],
                           sentences_as_tokens: list[list[str]]) -> dict[str, float]:
    """POSDdev ve POSdiv (Deutsch et al. 2020).

    ``pos_dist_std`` — 13 ``pos_*`` oranından oluşan vektörün standart sapması.
    Tek bir POS her şeyse büyük, POS'lar eşit dağılmışsa küçüktür.

    ``pos_kl_div`` — her cümlenin POS dağılımının belge POS dağılımına
    Kullback-Leibler ıraksaması, cümle sayısına bölünmüş, bit cinsinden.
    Düzleştirme yok: cümlede geçen bir POS belgede de geçtiği için payda
    hiçbir zaman sıfır olmaz.

    Cümle sınırı ``pos_data``'da yok; cümle uzunluklarıyla dilimlenir. Token
    sayıları uyuşmazsa çökmek yerine iki anahtar da 0.0 döner.
    """
    n = sum(len(c) for c in sentences_as_tokens)
    if not pos_data or n != len(pos_data):
        return {"pos_dist_std": 0.0, "pos_kl_div": 0.0}

    oranlar = np.array(list(pos_ratios(pos_data).values()), dtype=np.float64)

    etiketler = [p for _, p in pos_data]
    belge = Counter(etiketler)
    toplam = len(etiketler)
    kl_toplam = 0.0
    bas = 0
    cumle_sayisi = 0
    for cumle in sentences_as_tokens:
        dilim = etiketler[bas:bas + len(cumle)]
        bas += len(cumle)
        if not dilim:
            continue
        cumle_sayisi += 1
        yerel = Counter(dilim)
        for etiket, c in yerel.items():
            p = c / len(dilim)
            q = belge[etiket] / toplam
            kl_toplam += p * math.log2(p / q)

    kl = kl_toplam / cumle_sayisi if cumle_sayisi else 0.0
    return {"pos_dist_std": round(float(oranlar.std()), 5), "pos_kl_div": round(abs(kl), 5)}


# ── cümle istatistikleri ──────────────────────────────────────────────


def sentence_stats(cumleler: list[list[str]]) -> dict[str, float]:
    """Cümle uzunluğu (spaCy token sayısı): ortalama, CV, çarpıklık, medyan.

    Çarpıklık Fisher-Pearson ``g1 = m3 / m2^1.5`` (popülasyon momentleri);
    simetrik dağılımda 0, uzun cümleler kuyruk yapıyorsa pozitif.
    """
    if not cumleler:
        return {"avg_sent_len_word": 0.0, "sentence_length_cv": 0.0,
                "sent_len_skewness": 0.0, "med_sent_len": 0.0}
    u = np.array([len(c) for c in cumleler], dtype=np.float64)
    sapma = u - u.mean()
    m2 = float(np.mean(sapma ** 2))
    carpiklik = float(np.mean(sapma ** 3)) / m2 ** 1.5 if m2 > 0 else 0.0
    return {
        "avg_sent_len_word": round(float(u.mean()), 4),
        "sentence_length_cv": round(_cv(u), 4),
        "sent_len_skewness": round(carpiklik, 4),
        "med_sent_len": round(float(np.median(u)), 4),
    }


def sentence_distribution_stats(cumleler: list[list[str]], short_threshold: int,
                                long_threshold: int) -> dict[str, float]:
    """Eşikten **kesin** kısa ve **kesin** uzun cümlelerin oranı.

    Eşikler dile göre farklı (``FeatureParams.short_sent_threshold`` /
    ``long_sent_threshold``); tam eşikteki cümle iki tarafa da girmez.
    """
    if not cumleler:
        return {"short_sent_ratio": 0.0, "long_sent_ratio": 0.0}
    n = len(cumleler)
    kisa = sum(1 for c in cumleler if len(c) < short_threshold)
    uzun = sum(1 for c in cumleler if len(c) > long_threshold)
    return {"short_sent_ratio": round(kisa / n, 6), "long_sent_ratio": round(uzun / n, 6)}


def avg_sent_len_char(cumleler: list[list[str]]) -> dict[str, float]:
    """Cümle başına ortalama karakter, tokenler arasındaki tek boşluklar dahil."""
    if not cumleler:
        return {"avg_sent_len_char": 0.0}
    uzunluklar = [len(" ".join(c)) for c in cumleler]
    return {"avg_sent_len_char": round(sum(uzunluklar) / len(uzunluklar), 4)}


def sent_len_entropy(cumleler: list[list[str]]) -> dict[str, float]:
    """Cümle uzunluğu dağılımının Shannon entropisi (bit) — ritim çeşitliliği.

    Her farklı uzunluk bir kategori. Hep aynı uzunlukta cümle → 0.
    """
    return {"sent_len_entropy": round(_entropy_bits(Counter(len(c) for c in cumleler)), 5)}


# ── paragraf ──────────────────────────────────────────────────────────


def paragraph_stats(raw_text: str) -> dict[str, float]:
    """Paragraf uzunluğu, paragraf başına cümle ve 1000 kelimede paragraf sayısı.

    Üç kural: paragraf = boş satır (tek satır sonu saymaz); paragraf başına
    kelime = boşlukla bölme; paragraf başına cümle = ``[.!?…]+`` sayımı, hiç
    yoksa 1. ``\\r\\n`` önce ``\\n``'e çevrilir — aksi halde Windows'ta yazılmış
    korpus farklı bölünür.

    ``para_len_mean`` boşlukla ayrılmış kelime sayar, ``avg_sent_len_word``
    spaCy token'ı sayar; ikisi sistematik olarak farklıdır, karşılaştırılmamalı.
    """
    sifir = {"para_len_mean": 0.0, "para_len_cv": 0.0, "sents_per_para_mean": 0.0,
             "sents_per_para_cv": 0.0, "para_count_norm": 0.0}
    paras = [p for p in _PARA_SPLIT.split(raw_text.replace("\r\n", "\n")) if p.strip()]
    if not paras:
        return sifir
    # K11 istisnası: yerel sayım — paragrafı token akışına hizalamak ikinci geçiş ister
    kelime = np.array([len(p.split()) for p in paras], dtype=np.float64)
    cumle = np.array([max(len(_SENT_END.findall(p)), 1) for p in paras], dtype=np.float64)
    toplam_kelime = float(kelime.sum())
    return {
        "para_len_mean": round(float(kelime.mean()), 4),
        "para_len_cv": round(_cv(kelime), 4),
        "sents_per_para_mean": round(float(cumle.mean()), 4),
        "sents_per_para_cv": round(_cv(cumle), 4),
        "para_count_norm": round(len(paras) / toplam_kelime * 1000, 4) if toplam_kelime else 0.0,
    }
