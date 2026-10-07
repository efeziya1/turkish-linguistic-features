"""Sözdizimi yüzeyi: POS oranları, POS ızgarası, cümle ve paragraf istatistikleri.

Bu modül T11'in anahtarlarını üretir:

- ``pos`` (12): ``pos_noun_ratio`` … ``pos_intj_ratio``
- ``sentence`` (6) ve ``paragraph`` (2)
- ``syntactic`` grubunun 5'i: ``verb_dist_mean``, ``activity_ratio``,
  ``lexical_density``, ``posddev``, ``posdiv`` (kalan 2'si T12:
  ``question_sent_ratio``, ``pronoun_ratio``)
- ``custom_ngrams`` (dinamik): ``ngram_{...}_count``, T12

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

from ..alfabe import _kucuk_harf
from ..vocab import LEXICAL_POS, NON_WORD_POS, POS_TAGS, UPOS_TAGS
from .readability import kelime_birimleri

_PARA_SPLIT = re.compile(r"\n[ \t]*\n")   # boş satır = paragraf sınırı

# Tek paragraf çıkan metinde uyarı eşiği, kelime (2026-09-24, Efe). Kısa
# metnin gerçekten tek paragraf olması normaldir; uyarı orada gürültü olur.
# 1000 depoda hâlihazırda kullanılan büyüklük: `segment_text` varsayılanı ve
# kalibrasyon korpusunun segment boyu. Ölçüldü (2026-09-24): dokümanın örnek
# metinleri 7-24 kelime, paragrafı silinmiş bir roman dosyası 52.521 — araya
# konan her eşik ikisini ayırıyor, bu yüzden yeni bir sayı uydurulmadı.
_PARA_UYARI_KELIME = 1000
_SENT_END = re.compile(r"[.!?…]+")        # cümle sonu işareti


def _entropy_nats(sayimlar: Counter) -> float:
    """Sayım dağılımının Shannon entropisi, nat cinsinden (ln). Boşsa NaN."""
    toplam = sum(sayimlar.values())
    if toplam == 0:
        return math.nan
    return -sum((c / toplam) * math.log(c / toplam) for c in sayimlar.values())


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

    Cümle uzunluğu literatürde kelimeyle ölçülür. ``_extract_features`` bu
    fonksiyonlara 2026-10-06'dan beri (Efe) cümle başına varsayılan kelime
    birimlerini verir (``readability.cumle_birimleri``); onlarda noktalama zaten
    yoktur, token süzgeci yalnız token listesi verilirse iş görür.
    ``pos_distribution_stats`` bu yardımcıyı **kullanmaz**: orada cümleler
    ``pos_data`` ile token token dilimlenir, süzülmüş liste hizayı bozar.
    """
    return [[t for t in cumle if not _noktalama_mi(t)]
            for cumle in cumleler
            if any(ch.isalpha() for t in cumle for ch in t)]


# ── POS oranları ve ızgara ────────────────────────────────────────────


def pos_ratios(pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """12 POS etiketinin kelime oranı: ``etiket sayısı / kelime sayısı``.

    ``analyze()`` yolunda girdi kelime düzeyindedir (2026-10-07, Efe): her varsayılan
    kelime kendi ilk kelime tokenının etiketini taşır, noktalama yoktur. ``POS_TAGS``
    dışındaki etiketler (PRON, X) paydaya girer ama sütunu yoktur, bu yüzden 12 oranın
    toplamı 1'den küçük olabilir.
    """
    if not pos_data:
        return {f"pos_{t.lower()}_ratio": math.nan for t in POS_TAGS}
    sayimlar = Counter(p for _, p in pos_data)
    n = len(pos_data)
    return {f"pos_{t.lower()}_ratio": round(sayimlar.get(t, 0) / n, 5) for t in POS_TAGS}


# ── fiil mesafesi ve activity ─────────────────────────────────────────


def verb_distance_stats(pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """Ardışık fiiller arasındaki kelime mesafesinin ortalaması.

    QUITA "Verb Distances (VD)". ``arc_len_mean`` ile KARIŞTIRMA: o bağımlılık
    yayının uzunluğu, bu yüzey konum mesafesi.

    Yalnız ``VERB`` sayılır, ``AUX`` sayılmaz (2026-09-15). Ek-fiil (``-dir``,
    ``imek``) ve ``değil`` yardımcı ögedir, sözcüksel fiil değil; onları fiil
    saymak ad cümlesini eylem cümlesi gibi ölçer. İngilizcede de aynı hata
    ``have``/``be``/``will`` ile fiil sayısını şişirirdi.

    2'den az fiil → NaN. ``verb_dist_cv`` 2026-10-08'de kaldırıldı (Efe).
    """
    idx = [i for i, (_, p) in enumerate(pos_data) if p == "VERB"]
    if len(idx) < 2:
        return {"verb_dist_mean": math.nan}
    d = np.diff(np.array(idx, dtype=np.float64))
    return {"verb_dist_mean": round(float(d.mean()), 4)}


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

    ``posddev`` — 12 ``pos_*_ratio`` oranından oluşan vektörün standart sapması.
    Tek bir POS her şeyse büyük, POS'lar eşit dağılmışsa küçüktür.

    ``posdiv`` — her cümlenin POS dağılımının belge POS dağılımına
    Kullback-Leibler ıraksaması, cümle sayısına bölünmüş, nat cinsinden (ln).
    Düzleştirme yok: cümlede geçen bir POS belgede de geçtiği için payda
    hiçbir zaman sıfır olmaz.

    Cümle sınırı ``pos_data``'da yok; cümle uzunluklarıyla dilimlenir. Token
    sayıları uyuşmazsa ön işleme hatasıdır → ``ValueError`` (2026-09-16, Efe).
    Boş girdide ikisi de NaN.
    """
    n = sum(len(c) for c in sentences_as_tokens)
    if n != len(pos_data):
        raise ValueError(
            f"total sentence tokens ({n}) is not aligned with pos_data ({len(pos_data)})"
            f" — preprocessing error"
        )
    if not pos_data:
        return {"posddev": math.nan, "posdiv": math.nan}

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
            kl_toplam += p * math.log(p / q)

    kl = kl_toplam / cumle_sayisi
    return {"posddev": round(float(oranlar.std()), 5), "posdiv": round(abs(kl), 5)}


# ── cümle istatistikleri ──────────────────────────────────────────────


def sentence_stats(cumleler: list[list[str]]) -> dict[str, float]:
    """Cümle uzunluğu (**kelime** sayısı): ortalama ve medyan.

    Uzunluk ``_cumle_kelimeleri`` üzerinden ölçülür — noktalama tokenı
    kelime sayılmaz, alfabesiz cümle cümle sayılmaz. Cümle yoksa NaN.
    ``sentence_length_cv`` (2026-10-07) ve ``sent_len_skewness`` (2026-10-08)
    kaldırıldı (Efe).
    """
    kelimeler = _cumle_kelimeleri(cumleler)
    if not kelimeler:
        return {"sent_len_mean": math.nan, "sent_len_median": math.nan}
    u = np.array([len(c) for c in kelimeler], dtype=np.float64)
    return {
        "sent_len_mean": round(float(u.mean()), 4),
        "sent_len_median": round(float(np.median(u)), 4),
    }


def sentence_distribution_stats(cumleler: list[list[str]], short_threshold: int,
                                long_threshold: int) -> dict[str, float]:
    """Eşikten **kesin** kısa ve **kesin** uzun cümlelerin oranı.

    Uzunluk **kelimeyle** ölçülür (``_cumle_kelimeleri``); tam eşikteki cümle
    iki tarafa da girmez. Cümle yoksa NaN.

    Eşikler dile göre farklıdır ve çağıran taraf çözümler
    (``params.resolve_sent_thresholds``): ``FeatureParams``'ta verilmeyen alan
    dilin kalibre edilmiş değerinde kalır (TR 4/17, EN 8/32), verilen alan
    kullanıcıdan gelir. Bu fonksiyon çözümlenmiş iki sayıyı alır.
    """
    kelimeler = _cumle_kelimeleri(cumleler)
    if not kelimeler:
        return {"short_sent_ratio": math.nan, "long_sent_ratio": math.nan}
    n = len(kelimeler)
    kisa = sum(1 for c in kelimeler if len(c) < short_threshold)
    uzun = sum(1 for c in kelimeler if len(c) > long_threshold)
    return {"short_sent_ratio": round(kisa / n, 6), "long_sent_ratio": round(uzun / n, 6)}


def sent_len_char_mean(cumleler: list[list[str]]) -> dict[str, float]:
    """Cümle başına ortalama karakter, tokenler arasındaki tek boşluklar dahil. Cümle yoksa NaN."""
    if not cumleler:
        return {"sent_len_char_mean": math.nan}
    uzunluklar = [len(" ".join(c)) for c in cumleler]
    return {"sent_len_char_mean": round(sum(uzunluklar) / len(uzunluklar), 4)}


def sent_len_entropy(cumleler: list[list[str]]) -> dict[str, float]:
    """Cümle uzunluğu dağılımının Shannon entropisi (nat) — ritim çeşitliliği.

    Uzunluk **kelimeyle** ölçülür (``_cumle_kelimeleri``); her farklı uzunluk
    bir kategori. Hep aynı uzunlukta cümle → 0. 2'den az cümle → NaN (tek
    değerden çeşitlilik ölçülmez).
    """
    kelimeler = _cumle_kelimeleri(cumleler)
    if len(kelimeler) < 2:
        return {"sent_len_entropy": math.nan}
    return {"sent_len_entropy": round(_entropy_nats(Counter(len(c) for c in kelimeler)), 5)}


# ── paragraf ──────────────────────────────────────────────────────────


def paragraph_stats(raw_text: str, lang: str = "tr") -> dict[str, float]:
    """Paragraf uzunluğu, paragraf başına cümle ve 1000 kelimede paragraf sayısı.

    Üç kural: paragraf = boş satır (tek satır sonu saymaz); paragraf başına
    kelime = varsayılan kelime birimi (``readability.kelime_birimleri``: boşlukla
    ayrılan birim, kenar noktalaması atılır, yalnız noktalamadan oluşan birim
    sayılmaz; 2026-10-06, Efe); paragraf başına cümle = ``[.!?…]+`` sayımı, hiç
    yoksa 1. ``\\r\\n`` önce ``\\n``'e çevrilir — aksi halde Windows'ta yazılmış
    korpus farklı bölünür.

    ``para_len_mean`` ile ``sent_len_mean`` aynı kelime tanımını kullanır.

    Paragraf yoksa hepsi NaN. CV'ler 2026-10-07'de kaldırıldı (Efe).

    Çok cümleli bir metin tek paragraf çıkıyorsa ``ParagraphStructureWarning``
    basılır — sayılar değişmez (2026-09-24, Efe). Girdide paragraf sınırı
    olmaması yaygın: PDF/EPUB dökümlerinde satır sonları silinmiş oluyor ve
    ``para_len_mean`` sessizce bütün metnin kelime sayısına eşitleniyor.
    """
    paras = [p for p in _PARA_SPLIT.split(raw_text.replace("\r\n", "\n")) if p.strip()]
    if not paras:
        return {"para_len_mean": math.nan, "sents_per_para_mean": math.nan}
    # K11 istisnası: yerel sayım — paragrafı token akışına hizalamak ikinci geçiş ister
    kelime = np.array([len(kelime_birimleri(p, lang)[0]) for p in paras], dtype=np.float64)
    cumle = np.array([max(len(_SENT_END.findall(p)), 1) for p in paras], dtype=np.float64)
    if len(paras) == 1 and kelime[0] > _PARA_UYARI_KELIME:
        from .._warnings import uyar_paragraf_yok
        uyar_paragraf_yok(int(cumle[0]), int(kelime[0]))
    return {
        "para_len_mean": round(float(kelime.mean()), 4),
        "sents_per_para_mean": round(float(cumle.mean()), 4),
    }


# ── T12: soru cümlesi, zamir, kullanıcı n-gramları ────────────────────

# Cümle sonunda atlanan kapanış işaretleri: her tür tırnak ve kapanan parantez.
_KAPANIS = "\"'“”‘’«»‹›)]}"


def question_sent_ratio(sentences_as_tokens: list[list[str]]) -> dict[str, float]:
    """Soru işaretiyle biten cümle / toplam cümle → ``question_sent_ratio``.

    Cümlenin **sonundaki** tırnak ve kapanan parantezler atlanır; kalan son
    işaret ``?`` içeriyorsa (``?``, ``?!``, ``!?``, ``…?``) cümle soru sayılır
    (2026-09-15, Efe). Yalnız noktalamaya bakılır: ``?`` taşımayan ``mı``lı
    cümle sayılmaz, cümle ortasındaki ``?`` sayılmaz. Cümle yoksa NaN.
    """
    if not sentences_as_tokens:
        return {"question_sent_ratio": math.nan}
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
    return {"question_sent_ratio": round(soru / len(sentences_as_tokens), 5)}


def pronoun_ratio(pos_data: list[tuple[str, str]]) -> dict[str, float]:
    """spaCy ``PRON`` etiketli kelime / kelime sayısı → ``pronoun_ratio``.

    Payda ``pos_ratios`` ile aynı. Boşsa NaN.
    """
    if not pos_data:
        return {"pronoun_ratio": math.nan}
    pron = sum(1 for _, p in pos_data if p == "PRON")
    return {"pronoun_ratio": round(pron / len(pos_data), 5)}


def word_ngram_counts(
    sentences: list[list[tuple[str, str]]], ngrams: list[list[str]], lang: str = "tr",
) -> dict[str, float]:
    """Kullanıcı tanımlı n-gramların metindeki sayısı → ``ngram_{...}_count``.

    Öbek **her uzunlukta** olabilir: ``[["diye"]]`` tek kelime,
    ``[["ne", "var", "ki"]]`` üç kelime (2026-09-15, Efe).

    Kurallar (2026-10-08, Efe):

    - Değer **düz sayımdır**, oran değil; isteyen kelime sayısına böler.
    - Öbekteki büyük harfli bir UD etiketi (``NOUN``, ``VERB`` …, ``UPOS_TAGS``)
      o etiketli herhangi bir kelimeyle eşleşir; geri kalan her öge kelimedir
      ve dile göre küçük harfe inen yazılı biçimle eşleşir (lemma değil).
      ``["kadın", "VERB"]`` = "kadın" ve hemen ardından bir fiil.
    - Arama cümle içindedir: öbek cümle sınırını aşmaz.
    - Üst üste binen eşleşmeler sayılır: ``ha ha ha`` içinde ``ha ha`` = 2.
    - Anahtarda kelimeler küçük harf, etiketler büyük harf kalır:
      ``ngram_kadın_VERB_count``.

    ``sentences`` her cümlenin ``(kelime, etiket)`` listesidir (``WordView``).
    Boş öbek → ``ValueError``. ``custom_ngrams`` verilmezse **boş sözlük**
    döner — bu grup taban şemanın parçası değildir.
    """
    sonuc: dict[str, float] = {}
    for obek in ngrams:
        anahtar, eslesmeler = _ngram_eslesmeleri(sentences, obek, lang)
        sonuc[anahtar] = float(len(eslesmeler))
    return sonuc


def word_ngram_matches(sentences: list[list[tuple[str, str]]], phrase: list[str],
                       lang: str = "tr") -> dict[str, int]:
    """Bir öbeğin eşleşmeleri ve sıklıkları → ``{"kadın geldi": 2, …}``.

    Eşleştirme ``word_ngram_counts`` ile aynıdır; değerlerin toplamı o öbeğin
    ``ngram_{...}_count`` değeridir. Anahtar eşleşen kelimelerin küçük harfli,
    boşlukla birleşmiş hâli. Sıra: sıklık büyükten küçüğe, eşitlikte metindeki
    ilk geçiş (2026-10-08, Efe). Cümle ve konum bilgisi bilerek verilmez.
    """
    sayim = Counter(" ".join(e) for e in _ngram_eslesmeleri(sentences, phrase, lang)[1])
    return dict(sayim.most_common())


def _ngram_eslesmeleri(sentences: list[list[tuple[str, str]]], obek: list[str],
                       lang: str) -> tuple[str, list[tuple[str, ...]]]:
    """Öbeğin anahtarı ve metin sırasıyla eşleşen kelime dizileri (küçük harf)."""
    if not obek:
        raise ValueError("custom_ngrams contains an empty phrase")
    aranan = [(o, True) if o in UPOS_TAGS else (_kucuk_harf(o, lang), False) for o in obek]
    n = len(aranan)
    anahtar = "ngram_" + "_".join(o for o, _ in aranan) + "_count"
    eslesmeler: list[tuple[str, ...]] = []
    for cumle in sentences:
        c = [(_kucuk_harf(k, lang), p) for k, p in cumle]
        for i in range(len(c) - n + 1):
            if all((c[i + j][1] if etiket else c[i + j][0]) == o
                   for j, (o, etiket) in enumerate(aranan)):
                eslesmeler.append(tuple(k for k, _ in c[i:i + n]))
    return anahtar, eslesmeler
