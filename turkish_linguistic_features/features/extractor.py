"""Bütün öznitelik modüllerini tek çağrıda birleştirir (T20).

``_extract_features`` hazır token listelerini alır ve registry'de kayıtlı
anahtarları üretir. **Alt çizgi kasıtlı:** public API'nin parçası değil,
``analyze()`` onu içeriden çağırır (T24).

Katman saflığı (K3) burada da geçerli — bu modül spaCy modeli **gerektirmez**,
tokenizasyonu çağıran taraf yapmıştır. Faz 2'nin tamamı model indirmeden
doğrulanabiliyor; bir öznitelik bozulduğunda hatanın NLP'de mi formülde mi
olduğu tek bakışta belli oluyor.

**Grup girdisi yoksa grup sessizce atlanır.** ``dep_data`` verilmezse
``syntactic_dep`` (16), ``morph_tags`` verilmezse ``morphological`` (19),
``morpheme_lists`` verilmezse ``morphological_zeyrek`` (24) hiç üretilmez —
hata da verilmez. Bu üç alan ``pos_data`` ile **hizalı** olmak zorunda, boş
liste geçerli bir "hizalı" değer değil. ``analyze()`` yolunda ``Preprocessor``
üçünü de doldurur (T21), yani taban şema bundan etkilenmez.

K4: ölçülemeyen değer ``math.nan``. Boş metinde **hiçbir** öznitelik
ölçülemez, hepsi NaN döner.
"""

from __future__ import annotations

import math
from typing import Any

from ..alfabe import _kucuk_harf
from ..params import DEFAULT_PARAMS, FeatureParams, resolve_sent_thresholds
from ..vocab import NON_WORD_POS
from .dependency import dependency_features
from .frequency_structure import (
    adjusted_modulus,
    curve_length,
    curve_length_indicator,
    gini_coef,
    h_point,
    lambda_pa,
    repeat_rate,
    rr_mcintosh,
    secondary_thematic_concentration,
    thematic_concentration,
    vocab_richness_r1,
    vocab_richness_r4,
    writers_view,
)
from .lexical import (
    _hizala,
    advanced_lexical_richness,
    brunet_w,
    dugast_u,
    guiraud_r,
    hapax_percentage,
    hapax_ratio,
    hdd,
    heaps_beta,
    msttr,
    mtld,
    pos_lexical_variation,
    rank_word_freq_table,
    rare_word_metrics,
    reference_frequency_sophistication,
    shannon_entropy,
    simpsons_d,
    ttr_moving_slope,
    type_token_ratio,
    vocd_d,
    word_length_stats,
    yules_k,
    zipf,
    zipf_mandelbrot,
)
from .morphological import spacy_morph_ratios, surface_per_lemma, zeyrek_morfoloji
from .phonetic import (
    sentence_syllable_stats,
    syllable_count_stats,
    syllable_length_distribution,
    vowel_harmony_ratios,
    vowel_ratios,
)
from .punctuation import (
    all_caps_word_ratio,
    char_freq_vector,
    consecutive_punct_ratio,
    digit_ratio,
    punct_density,
    punct_entropy,
    punct_variety,
    punctuation_ratios,
    uppercase_ratio,
    whitespace_ratio,
)
from .readability import (
    english_readability_formulas,
    general_readability_formulas,
    kural_cumleleri,
    turkish_readability_formulas,
)
from .registry import GROUP_LABELS
from .syntactic import (
    activity_ratio,
    avg_sent_len_char,
    lexical_density,
    nominal_verbal_ratio,
    paragraph_stats,
    pos_distribution_stats,
    pos_ratios,
    pronoun_freq,
    question_per_sent,
    sent_len_entropy,
    sentence_distribution_stats,
    sentence_stats,
    verb_distance_stats,
    word_ngram_ratios,
)

__all__ = ["_extract_features"]


def _lemma_pos(lemma_tokens: list[str],
               pos_data: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """``thematic_concentration`` için **lemma → POS** listesi.

    ``frequency_structure`` lemma sıklıklarıyla çalışır, ``pos_data`` ise yüzey
    biçim taşır; ikisi doğrudan eşleşmez ve lemma "kitap" ``pos_data``'da
    bulunamadığı için TC sessizce 0 çıkardı (2026-09-16, Efe). Çözüm:
    ``pos_data``'dan ``NON_WORD_POS`` atılır — kalan etiketler ``lemma_tokens``
    ile hizalıdır (T21) — ve lemmalarla eşlenir.

    Hizasızlık kontrolünü ``lexical._hizala`` yapıyor; hizasızlık metnin
    özelliği değil ön işleme hatasıdır → ``ValueError`` (K4).
    """
    return list(zip(lemma_tokens, _hizala(lemma_tokens, pos_data), strict=False))


def _extract_features(
    raw_text: str,
    surface_tokens: list[str],
    lemma_tokens: list[str],
    pos_data: list[tuple[str, str]],
    sentences_as_tokens: list[list[str]] | None = None,
    morpheme_lists: list[list[Any]] | None = None,
    morph_tags: list[tuple[str, str]] | None = None,
    lang: str = "tr",
    custom_ngrams: list[list[str]] | None = None,
    groups: list[str] | None = None,
    params: FeatureParams | None = None,
    dep_data: Any = None,
) -> dict[str, float]:
    """Registry'de kayıtlı öznitelikleri üretir.

    Parameters
    ----------
    raw_text, surface_tokens, lemma_tokens, pos_data
        Ön işlemenin çıktısı. ``surface_tokens`` noktalama içerir ve
        ``pos_data`` ile hizalıdır (T21).
    groups
        Yalnız bu grupları üret. ``None`` hepsi demektir.
    custom_ngrams
        Aranacak kelime öbekleri. Verilmezse ``ng_*`` anahtarı üretilmez —
        bu grup taban şemanın parçası değildir.

    Returns
    -------
    dict[str, float]
        Anahtar → değer. Türkçe taban 208, İngilizce 180; ``dep_data``
        verilmezse her ikisinden de 16 eksik.

    Raises
    ------
    ValueError
        ``groups`` bilinmeyen bir grup adı içeriyorsa, ya da girdi listeleri
        birbirleriyle hizalı değilse.
    """
    if params is None:
        params = DEFAULT_PARAMS
    # Cümle eşikleri alan alan çözümlenir, nesne komple değiştirilmez —
    # kullanıcının verdiği bir alan yüzünden başka alanın kalibrasyonu
    # düşmesin (2026-09-24, Efe).
    kisa_esik, uzun_esik = resolve_sent_thresholds(params, lang)

    if groups is None:
        secili: frozenset[str] | None = None
    else:
        bilinmeyen = [g for g in groups if g not in GROUP_LABELS]
        if bilinmeyen:
            raise ValueError(
                f"Unknown group(s): {bilinmeyen}. Available: {list(GROUP_LABELS)}"
            )
        secili = frozenset(groups)

    def istiyor(grup: str) -> bool:
        return secili is None or grup in secili

    feats: dict[str, float] = {}
    # Cümle listesi — varsayılan kural (2026-10-06, Efe): `sentence`, `syntactic` ve `phonetic`
    # grupları spaCy'nin ayrıştırıcı cümlelerini değil, okunabilirlik formüllerinin varsayılan
    # kuralını kullanır. `sentences_as_tokens` (spaCy cümleleri) bu yüzden okunmaz; `syntactic_dep`
    # kendi cümle-yerel `dep_data`'sını kullanır.
    cumleler = kural_cumleleri(surface_tokens, lang)

    # Kelime listesi — tek kural (2026-09-16, Efe): kelime bekleyen her grup
    # bunu okur. `surface_tokens` noktalama içerir ve `pos_data` ile hizalıdır,
    # bu yüzden süzgeç POS etiketi üzerinden çalışır.
    kelimeler = [tok for tok, p in pos_data if p not in NON_WORD_POS]
    # Dile göre küçük harf: `str.lower()` Türkçede "I"yı "i" yapar, "İ"ye
    # birleşik nokta (U+0307) ekler — ttr ve kelime uzunluğu kayardı.
    kucuk_kelimeler = [_kucuk_harf(tok, lang) for tok in kelimeler]

    # ── lexical (32) — yüzey biçim sayar ──────────────────────────────
    if istiyor("lexical"):
        freqs, N, V, items = rank_word_freq_table(kucuk_kelimeler, lang)
        ort_uzunluk, uzunluk_cv = word_length_stats(kucuk_kelimeler)
        feats.update({
            # `lemma_tokens` zaten noktalamasız (T21). Lemma yoksa
            # "ölçüldü ve sıfır çıktı" değil, ölçülemedi (K4).
            "n_lemma_count": float(len(set(lemma_tokens))) if lemma_tokens else math.nan,
            "avg_word_length": ort_uzunluk,
            "word_length_cv": uzunluk_cv,
            "entropy": shannon_entropy(freqs),
            "yule_k": yules_k(freqs) if N else math.nan,
            "simpson_d": simpsons_d(freqs),
        })
        feats.update(type_token_ratio(N, V))
        feats.update(brunet_w(N, V, params.brunet_w_a))
        feats.update(hapax_ratio(items))
        feats.update(hapax_percentage(items))
        feats.update(advanced_lexical_richness(kucuk_kelimeler, params.mattr_window))
        feats.update(mtld(kucuk_kelimeler, params.mtld_threshold, params.mtld_min_tokens))
        feats.update(dugast_u(kucuk_kelimeler))
        feats.update(guiraud_r(kucuk_kelimeler))
        feats.update(ttr_moving_slope(kucuk_kelimeler, params.ttr_slope_chunk_size))
        feats.update(heaps_beta(kucuk_kelimeler, params.heaps_min_tokens, params.heaps_step))
        feats.update(rare_word_metrics(kucuk_kelimeler))
        feats.update(pos_lexical_variation(lemma_tokens, pos_data))
        feats.update(zipf(freqs))
        feats.update(zipf_mandelbrot(freqs))
        feats.update(reference_frequency_sophistication(lemma_tokens, pos_data, lang))
        feats.update(vocd_d(kucuk_kelimeler, params.vocd_sample_min, params.vocd_sample_max,
                            params.vocd_num_samples, params.vocd_num_runs,
                            params.vocd_min_tokens, params.vocd_random_seed))
        feats.update(hdd(kucuk_kelimeler, params.hdd_sample_size))
        feats.update(msttr(kucuk_kelimeler, params.msttr_segment_size))

    # ── frequency_structure (13) — lemma sıklıkları ───────────────────
    # Birim grup içinde tek olmak zorunda: TC h-point'i kullanıyor.
    if istiyor("frequency_structure"):
        lemma_pos = _lemma_pos(lemma_tokens, pos_data)
        lemmalar = [lem for lem, _ in lemma_pos]
        l_freqs, l_N, l_V, l_items = rank_word_freq_table(lemmalar, lang)
        h = h_point(l_freqs)
        f1 = int(l_freqs[0]) if l_V else 0
        feats["h_point"] = h
        feats.update(vocab_richness_r1(l_freqs, l_N, h))
        feats.update(vocab_richness_r4(l_freqs, l_N, l_V))
        rr = repeat_rate(l_freqs, l_N)
        feats.update(rr)
        feats.update(rr_mcintosh(rr["repeat_rate"], l_V))
        feats.update(gini_coef(l_freqs, l_N, l_V))
        egri = curve_length(l_freqs)
        feats.update(egri)
        feats.update(curve_length_indicator(l_freqs, h))
        feats.update(lambda_pa(egri["curve_length"], l_N))
        feats.update(adjusted_modulus(f1, l_V, h, l_N))
        feats.update(writers_view(f1, l_V, h))
        feats.update(thematic_concentration(l_items, lemma_pos, h, lang))
        feats.update(secondary_thematic_concentration(l_items, lemma_pos, h, lang))

    # ── sentence (8) ──────────────────────────────────────────────────
    if istiyor("sentence"):
        feats.update(sentence_stats(cumleler))
        feats.update(avg_sent_len_char(cumleler))
        feats.update(sentence_distribution_stats(cumleler, kisa_esik, uzun_esik))
        feats.update(sent_len_entropy(cumleler))

    # ── paragraph (5) ─────────────────────────────────────────────────
    if istiyor("paragraph"):
        feats.update(paragraph_stats(raw_text))

    # ── pos (13) ──────────────────────────────────────────────────────
    if istiyor("pos"):
        feats.update(pos_ratios(pos_data))

    # ── syntactic (9) ─────────────────────────────────────────────────
    if istiyor("syntactic"):
        feats.update(question_per_sent(cumleler))
        feats.update(pronoun_freq(pos_data))
        feats.update(nominal_verbal_ratio(pos_data))
        feats.update(verb_distance_stats(pos_data))
        feats.update(activity_ratio(pos_data))
        feats.update(lexical_density(pos_data))
        feats.update(pos_distribution_stats(pos_data, cumleler))

    # ── syntactic_dep (16) — girdi yoksa atlanır ──────────────────────
    if istiyor("syntactic_dep") and dep_data is not None:
        feats.update(dependency_features(dep_data, params))

    # ── morphological (19) — spaCy tarafı, girdi yoksa atlanır ────────
    # `morph_tags` `pos_data` ile hizalı olmak zorunda; verilmemişse grup
    # `syntactic_dep` gibi sessizce atlanır. `analyze()` yolunda `Preprocessor`
    # alanı her zaman doldurur (T21), yani taban şema bundan etkilenmez.
    if istiyor("morphological") and morph_tags is not None:
        feats.update(surface_per_lemma(surface_tokens, pos_data, lemma_tokens, lang))
        feats.update(spacy_morph_ratios(morph_tags, pos_data))

    # ── morphological_zeyrek (24) — yalnız Türkçe ─────────────────────
    # K11: dil şemayı belirler. İngilizcede grup hiç üretilmez; Zeyrek
    # İngilizce çözümlemiyor, kurmak bir şeyi değiştirmez.
    if istiyor("morphological_zeyrek") and lang == "tr" and morpheme_lists is not None:
        feats.update(zeyrek_morfoloji(morpheme_lists, pos_data, params))

    # ── phonetic (TR 15 · EN 13) ──────────────────────────────────────
    if istiyor("phonetic"):
        feats.update(vowel_ratios(raw_text, lang))
        # Ünlü uyumu Türkçeye özgü (Göksel & Kerslake 2005); İngilizcede
        # anlamı yok, anahtar hiç üretilmez — Zeyrek ve okunabilirlikle aynı.
        if lang == "tr":
            feats.update(vowel_harmony_ratios(surface_tokens, lang))
        feats.update(syllable_count_stats(surface_tokens, lang))
        feats.update(syllable_length_distribution(surface_tokens, lang))
        feats.update(sentence_syllable_stats(cumleler, lang))

    # ── readability (TR 7 · EN 8) — dil ayrımı burada ─────────────────
    if istiyor("readability"):
        feats.update(general_readability_formulas(raw_text, surface_tokens, lang))
        if lang == "tr":
            feats.update(turkish_readability_formulas(raw_text, surface_tokens))
        else:
            feats.update(english_readability_formulas(raw_text, surface_tokens))

    # ── punctuation (18) ──────────────────────────────────────────────
    if istiyor("punctuation"):
        feats.update(digit_ratio(raw_text))
        feats.update(punctuation_ratios(raw_text, len(kelimeler)))
        feats.update(punct_density(raw_text))
        feats.update(punct_entropy(raw_text))
        feats.update(consecutive_punct_ratio(raw_text))
        feats.update(whitespace_ratio(raw_text))
        feats.update(punct_variety(raw_text))
        feats.update(uppercase_ratio(surface_tokens))
        feats.update(all_caps_word_ratio(surface_tokens))

    # ── chars (dinamik: TR 29 · EN 26) ────────────────────────────────
    if istiyor("chars"):
        feats.update(char_freq_vector(raw_text, lang))

    # ── custom_ngrams (dinamik, taban şemada yok) ─────────────────────
    if istiyor("custom_ngrams") and custom_ngrams:
        feats.update(word_ngram_ratios(kelimeler, custom_ngrams, lang))

    return feats
