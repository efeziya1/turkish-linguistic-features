"""Sözdizimi yüzeyi: POS oranları, POS ızgarası, cümle ve paragraf istatistikleri.

Bu modül T11'in anahtarlarını üretir:

- ``pos`` (13): ``pos_noun`` … ``pos_punct``
- ``sentence`` (8) ve ``paragraph`` (5)
- ``syntactic`` grubunun 7'si: ``nominal_verbal_ratio``, ``verb_dist_mean``,
  ``verb_dist_cv``, ``activity_ratio``, ``lexical_density``, ``pos_dist_std``,
  ``pos_kl_div`` (kalan 2'si T12: ``question_per_sent``, ``pronoun_freq``)
- ``custom_ngrams`` (dinamik): ``ng_{...}``, T12

Fonksiyonlar saftır (K3): girdi ``pos_data`` = ``[(token, POS), …]``,
``sentences_as_tokens`` = ``[[token, …], …]`` ya da ham metin. NLP modeli almaz.

K4 (2026-09-16, Efe): ölçülemeyen değer ``math.nan`` döner — boş girdi, boş
alt küme (fiil yoksa fiil oranları), tek değerden yayılım (tek cümlede CV).
``0.0`` yalnız gerçek sıfırdır. Hizasız girdi ``ValueError`` fırlatır.

Standart sapmalar **popülasyon** sapmasıdır (``ddof=0``) — ``lexical.py`` ile
aynı gerekçe: elimizdeki liste örneklem değil, metnin kendisi.
"""

from __future__ import annotations

import math
import re
from collections import Counter

import numpy as np

from .punctuation import _kucuk_harf
from .vocab import LEXICAL_POS, NON_WORD_POS, NOUN_POS, POS_TAGS

_PARA_SPLIT = re.compile(r"\n[ \t]*\n")   # boş satır = paragraf sınırı
_SENT_END = re.compile(r"[.!?…]+")        # cümle sonu işareti


def _entropy_bits(sayimlar: Counter) -> float:
    """Sayım dağılımının Shannon entropisi, bit cinsinden. Boşsa NaN."""
    toplam = sum(sayimlar.values())
    if toplam == 0:
        return math.nan
    return -sum((c / toplam) * math.log2(c / toplam) for c in sayimlar.values())


def _cv(degerler: np.ndarray) -> float:
    """Değişim katsayısı ``std / ortalama``; 2'den az değer ya da ortalama 0 → NaN."""
    if len(degerler) < 2:
        return math.nan
    ortalama = float(degerler.mean())
    return float(degerler.std()) / ortalama if ortalama > 0 else math.nan


def _noktalama_mi(token: str) -> bool:
    """Harf ya da rakam içermeyen token noktalamadır (``,``, ``...``, ``?!``)."""
    return not any(c.isalnum() for c in token)


def _cumle_kelimeleri(cumleler: list[list[str]]) -> list[list[str]]:
    """Cümle listesini kelimeye indirger; uzunluk ölçüleri bunun üzerinde çalışır.

    İki süzgeç, iki ayrı kural (2026-09-18, Efe):

    - **Token**: noktalama düşer, sayı kalır (``_noktalama_mi``, ``isalnum``).
      "Yıl 1999." iki kelimedir — okunabilirlik formülleri de sayıyı kelime sayar.
    - **Cümle**: içinde hiç alfabetik karakter olmayan cümle düşer (``isalpha``).
      Tek başına ``"..."`` cümle değildir; uzunluğu 0 sayıp ortalamayı aşağı
      çekmesindense hiç sayılmaz.

    Cümle uzunluğu literatürde kelimeyle ölçülür, ``sentences_as_tokens`` ise
    noktalamayı da taşır; süzme bu yüzden fonksiyonların **içinde** yapılır.
    ``pos_distribution_stats`` bu yardımcıyı **kullanmaz**: orada cümleler
    ``pos_data`` ile token token dilimlenir, süzülmüş liste hizayı bozar.
    """
    return [[t for t in cumle if not _noktalama_mi(t)]
            for cumle in cumleler
            if any(ch.isalpha() for t in cumle for ch in t)]


# ── POS oranları ve ızgara ────────────────────────────────────────────


def pos_ratios(pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """13 POS etiketinin token oranı: ``etiket sayısı / toplam token``.

    Payda **tüm** tokenlerdir — ``POS_TAGS`` dışındaki etiketler (PRON, X, SYM)
    paydaya girer ama sütunu yoktur, bu yüzden 13 oranın toplamı 1'den küçük
    olabilir.
    """
    if not pos_data:
        return {f"pos_{t.lower()}": math.nan for t in POS_TAGS}
    sayimlar = Counter(p for _, p in pos_data)
    n = len(pos_data)
    return {f"pos_{t.lower()}": round(sayimlar.get(t, 0) / n, 5) for t in POS_TAGS}


def nominal_verbal_ratio(pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """``isim sayısı / VERB sayısı``. Fiil yoksa NaN.

    İsim = ``NOUN_POS`` (NOUN + PROPN, 2026-09-16, Efe). Yalnız ``VERB``;
    ``AUX`` fiil sayılmaz — modülün tamamında geçerli kural, gerekçesi
    ``verb_distance_stats``'ta.
    """
    sayimlar = Counter(p for _, p in pos_data)
    fiil = sayimlar.get("VERB", 0)
    if fiil == 0:
        return {"nominal_verbal_ratio": math.nan}
    isim = sum(sayimlar.get(p, 0) for p in NOUN_POS)
    return {"nominal_verbal_ratio": round(isim / fiil, 5)}


# ── fiil mesafesi ve activity ─────────────────────────────────────────


def verb_distance_stats(pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """Ardışık fiiller arasındaki token mesafesinin ortalaması ve CV'si.

    QUITA "Verb Distances (VD)". ``arc_len_mean`` ile KARIŞTIRMA: o bağımlılık
    yayının uzunluğu, bu yüzey konum mesafesi.

    Yalnız ``VERB`` sayılır, ``AUX`` sayılmaz (2026-09-15). Ek-fiil (``-dir``,
    ``imek``) ve ``değil`` yardımcı ögedir, sözcüksel fiil değil; onları fiil
    saymak ad cümlesini eylem cümlesi gibi ölçer. İngilizcede de aynı hata
    ``have``/``be``/``will`` ile fiil sayısını şişirirdi.

    2'den az fiil → ikisi de NaN; tam 2 fiil (tek mesafe) → CV NaN.
    """
    idx = [i for i, (_, p) in enumerate(pos_data) if p == "VERB"]
    if len(idx) < 2:
        return {"verb_dist_mean": math.nan, "verb_dist_cv": math.nan}
    d = np.diff(np.array(idx, dtype=np.float64))
    return {"verb_dist_mean": round(float(d.mean()), 4), "verb_dist_cv": round(_cv(d), 4)}


def activity_ratio(pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """QUITA "Activity (Q)" = VERB / (VERB + ADJ). ``AUX`` fiil sayılmaz.

    Descriptivity (D) = 1 − Q ayrı anahtar olarak üretilmez: tam ters
    bağıntılı ikinci bir sütun bilgi taşımaz. Fiil de sıfat da yoksa NaN.
    """
    v = sum(1 for _, p in pos_data if p == "VERB")
    a = sum(1 for _, p in pos_data if p == "ADJ")
    if v + a == 0:
        return {"activity_ratio": math.nan}
    return {"activity_ratio": round(v / (v + a), 5)}


# ── yoğunluk ve dağılım ───────────────────────────────────────────────


def lexical_density(pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """Otosemantik (içerik) kelime oranı — Ure 1971.

    Pay ``LEXICAL_POS``: NOUN, PROPN, VERB, ADJ, ADV. Payda **kelime**:
    ``NON_WORD_POS`` (PUNCT, SYM) düşer, geriye kalan her POS işlev sayılır
    (2026-09-18, Efe — Lu 2012: "sözcüksel kelime / toplam kelime").
    ``nominal_verbal_ratio`` bunun yerine geçmez: o isim/fiil dengesini,
    bu içerik/işlev dengesini verir.

    Kelime yoksa NaN — yalnız noktalamadan oluşan girdide oran ölçülemez (K4).
    """
    kelimeler = [p for _, p in pos_data if p not in NON_WORD_POS]
    if not kelimeler:
        return {"lexical_density": math.nan}
    icerik = sum(1 for p in kelimeler if p in LEXICAL_POS)
    return {"lexical_density": round(icerik / len(kelimeler), 5)}


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
    sayıları uyuşmazsa ön işleme hatasıdır → ``ValueError`` (2026-09-16, Efe).
    Boş girdide ikisi de NaN.
    """
    n = sum(len(c) for c in sentences_as_tokens)
    if n != len(pos_data):
        raise ValueError(
            f"cümle token toplamı ({n}) ile pos_data ({len(pos_data)}) hizalı değil — ön işleme hatası"
        )
    if not pos_data:
        return {"pos_dist_std": math.nan, "pos_kl_div": math.nan}

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

    kl = kl_toplam / cumle_sayisi
    return {"pos_dist_std": round(float(oranlar.std()), 5), "pos_kl_div": round(abs(kl), 5)}


# ── cümle istatistikleri ──────────────────────────────────────────────


def sentence_stats(cumleler: list[list[str]]) -> dict[str, float]:
    """Cümle uzunluğu (**kelime** sayısı): ortalama, CV, çarpıklık, medyan.

    Uzunluk ``_cumle_kelimeleri`` üzerinden ölçülür — noktalama tokenı
    kelime sayılmaz, alfabesiz cümle cümle sayılmaz.

    Çarpıklık Fisher-Pearson ``g1 = m3 / m2^1.5`` (popülasyon momentleri);
    simetrik dağılımda 0, uzun cümleler kuyruk yapıyorsa pozitif.

    NaN: cümle yoksa hepsi; tek cümlede CV ve çarpıklık (tek değerden yayılım
    ölçülmez); bütün cümleler eşit uzunluktaysa çarpıklık (0/0). Eşit
    uzunlukta CV gerçekten 0'dır.
    """
    kelimeler = _cumle_kelimeleri(cumleler)
    if not kelimeler:
        return {"avg_sent_len_word": math.nan, "sentence_length_cv": math.nan,
                "sent_len_skewness": math.nan, "med_sent_len": math.nan}
    u = np.array([len(c) for c in kelimeler], dtype=np.float64)
    sapma = u - u.mean()
    m2 = float(np.mean(sapma ** 2))
    carpiklik = float(np.mean(sapma ** 3)) / m2 ** 1.5 if m2 > 0 else math.nan
    return {
        "avg_sent_len_word": round(float(u.mean()), 4),
        "sentence_length_cv": round(_cv(u), 4),
        "sent_len_skewness": round(carpiklik, 4),
        "med_sent_len": round(float(np.median(u)), 4),
    }


def sentence_distribution_stats(cumleler: list[list[str]], short_threshold: int,
                                long_threshold: int) -> dict[str, float]:
    """Eşikten **kesin** kısa ve **kesin** uzun cümlelerin oranı.

    Uzunluk **kelimeyle** ölçülür (``_cumle_kelimeleri``). Eşikler dile göre
    farklı (``FeatureParams.short_sent_threshold`` / ``long_sent_threshold``);
    tam eşikteki cümle iki tarafa da girmez. Cümle yoksa NaN.
    """
    kelimeler = _cumle_kelimeleri(cumleler)
    if not kelimeler:
        return {"short_sent_ratio": math.nan, "long_sent_ratio": math.nan}
    n = len(kelimeler)
    kisa = sum(1 for c in kelimeler if len(c) < short_threshold)
    uzun = sum(1 for c in kelimeler if len(c) > long_threshold)
    return {"short_sent_ratio": round(kisa / n, 6), "long_sent_ratio": round(uzun / n, 6)}


def avg_sent_len_char(cumleler: list[list[str]]) -> dict[str, float]:
    """Cümle başına ortalama karakter, tokenler arasındaki tek boşluklar dahil. Cümle yoksa NaN."""
    if not cumleler:
        return {"avg_sent_len_char": math.nan}
    uzunluklar = [len(" ".join(c)) for c in cumleler]
    return {"avg_sent_len_char": round(sum(uzunluklar) / len(uzunluklar), 4)}


def sent_len_entropy(cumleler: list[list[str]]) -> dict[str, float]:
    """Cümle uzunluğu dağılımının Shannon entropisi (bit) — ritim çeşitliliği.

    Uzunluk **kelimeyle** ölçülür (``_cumle_kelimeleri``); her farklı uzunluk
    bir kategori. Hep aynı uzunlukta cümle → 0. 2'den az cümle → NaN (tek
    değerden çeşitlilik ölçülmez).
    """
    kelimeler = _cumle_kelimeleri(cumleler)
    if len(kelimeler) < 2:
        return {"sent_len_entropy": math.nan}
    return {"sent_len_entropy": round(_entropy_bits(Counter(len(c) for c in kelimeler)), 5)}


# ── paragraf ──────────────────────────────────────────────────────────


def paragraph_stats(raw_text: str) -> dict[str, float]:
    """Paragraf uzunluğu, paragraf başına cümle ve 1000 kelimede paragraf sayısı.

    Üç kural: paragraf = boş satır (tek satır sonu saymaz); paragraf başına
    kelime = boşlukla bölme; paragraf başına cümle = ``[.!?…]+`` sayımı, hiç
    yoksa 1. ``\\r\\n`` önce ``\\n``'e çevrilir — aksi halde Windows'ta yazılmış
    korpus farklı bölünür.

    ``para_len_mean`` boşlukla ayrılmış kelime sayar, ``avg_sent_len_word``
    spaCy token'ı sayar; ikisi sistematik olarak farklıdır, karşılaştırılmamalı.

    Paragraf yoksa hepsi NaN; tek paragrafta iki CV NaN.
    """
    paras = [p for p in _PARA_SPLIT.split(raw_text.replace("\r\n", "\n")) if p.strip()]
    if not paras:
        return {"para_len_mean": math.nan, "para_len_cv": math.nan, "sents_per_para_mean": math.nan,
                "sents_per_para_cv": math.nan, "para_count_norm": math.nan}
    # K11 istisnası: yerel sayım — paragrafı token akışına hizalamak ikinci geçiş ister
    kelime = np.array([len(p.split()) for p in paras], dtype=np.float64)
    cumle = np.array([max(len(_SENT_END.findall(p)), 1) for p in paras], dtype=np.float64)
    toplam_kelime = float(kelime.sum())
    return {
        "para_len_mean": round(float(kelime.mean()), 4),
        "para_len_cv": round(_cv(kelime), 4),
        "sents_per_para_mean": round(float(cumle.mean()), 4),
        "sents_per_para_cv": round(_cv(cumle), 4),
        "para_count_norm": round(len(paras) / toplam_kelime * 1000, 4),
    }


# ── T12: soru cümlesi, zamir, kullanıcı n-gramları ────────────────────

# Cümle sonunda atlanan kapanış işaretleri: her tür tırnak ve kapanan parantez.
_KAPANIS = "\"'“”‘’«»‹›)]}"


def question_per_sent(sentences_as_tokens: list[list[str]]) -> dict[str, float]:
    """Soru işaretiyle biten cümle / toplam cümle → ``question_per_sent``.

    Cümlenin **sonundaki** tırnak ve kapanan parantezler atlanır; kalan son
    işaret ``?`` içeriyorsa (``?``, ``?!``, ``!?``, ``…?``) cümle soru sayılır
    (2026-09-15, Efe). Yalnız noktalamaya bakılır: ``?`` taşımayan ``mı``lı
    cümle sayılmaz, cümle ortasındaki ``?`` sayılmaz. Cümle yoksa NaN.
    """
    if not sentences_as_tokens:
        return {"question_per_sent": math.nan}
    soru = 0
    for cumle in sentences_as_tokens:
        for token in reversed(cumle):
            kalan = token.rstrip(_KAPANIS)
            if not kalan:
                continue
            i = len(kalan)
            while i and not kalan[i - 1].isalnum():   # sondaki işaret öbeği
                i -= 1
            soru += "?" in kalan[i:]
            break
    return {"question_per_sent": round(soru / len(sentences_as_tokens), 5)}


def pronoun_freq(pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """spaCy ``PRON`` etiketli token / toplam token → ``pronoun_freq``.

    Payda ``pos_ratios`` ile aynı: noktalama dahil tüm tokenler. Boşsa NaN.
    """
    if not pos_data:
        return {"pronoun_freq": math.nan}
    pron = sum(1 for _, p in pos_data if p == "PRON")
    return {"pronoun_freq": round(pron / len(pos_data), 5)}


def word_ngram_ratios(
    tokens: list[str], ngrams: list[list[str]], lang: str = "tr",
) -> dict[str, float]:
    """Kullanıcı tanımlı n-gramların oranı → ``ng_{...}`` anahtarları.

    Öbek **her uzunlukta** olabilir: ``[["diye"]]`` tek kelime,
    ``[["ne", "var", "ki"]]`` üç kelime (2026-09-15, Efe).

    Kurallar (2026-09-15, Efe):

    - Metin ve öbek dile göre küçük harfe iner; noktalama tokenleri atılır.
    - Oran = eşleşme sayısı / aynı uzunluktaki pencere sayısı
      (``token − n + 1``), ``posbg_*`` ile aynı mantık.
    - Üst üste binen eşleşmeler sayılır: ``ha ha ha`` içinde ``ha ha`` = 2.

    Metin öbekten kısaysa (pencere yok) NaN. Boş öbek → ``ValueError``.

    ``custom_ngrams`` verilmezse **boş sözlük** döner — bu grup taban
    şemanın parçası değildir.
    """
    kelimeler = [_kucuk_harf(t, lang) for t in tokens if not _noktalama_mi(t)]
    sonuc: dict[str, float] = {}
    for obek in ngrams:
        aranan = tuple(_kucuk_harf(k, lang) for k in obek)
        n = len(aranan)
        pencere = len(kelimeler) - n + 1
        anahtar = "ng_" + "_".join(aranan)
        if n == 0:
            raise ValueError("custom_ngrams içinde boş öbek var")
        if pencere <= 0:
            sonuc[anahtar] = math.nan
            continue
        eslesme = sum(1 for i in range(pencere) if tuple(kelimeler[i:i + n]) == aranan)
        sonuc[anahtar] = round(eslesme / pencere, 5)
    return sonuc
