"""``definitions`` açıklamaları: her (terim, ad) için kaynak ve tek cümlelik açıklama.

``source`` kuralı kimin koyduğunu söyler: ``tlf`` (kütüphanenin kendi kodu), ``spacy`` (spaCy
modelinin çıktısı: ``tr_core_news_md`` / ``en_core_web_sm``), ``zeyrek``, ``textstat``,
``wordfreq``. tlf'nin spaCy tokenları üzerinde uyguladığı kural ``tlf``'dir; hangi girdiyi
okuduğu açıklamada yazar. Açıklama en fazla bir cümle. Metinler 2026-10-06'da koddan okunarak yazıldı.
"""

from __future__ import annotations

__all__ = ["SOURCES", "DEFINITION_INFO"]

SOURCES: frozenset[str] = frozenset({"tlf", "spacy", "zeyrek", "textstat", "wordfreq"})

DEFINITION_INFO: dict[tuple[str, str], tuple[str, str]] = {
    # ── sentence ──
    ("sentence", "default"): ("tlf",
        ". ? ! … end a sentence; ':' only before a new sentence. "
        "Read on spaCy tokens, so 'Dr.' does not split."),
    ("sentence", "kincaid"): ("tlf",
        "Like default, but ';' also ends a sentence (Kincaid et al. 1975)."),
    ("sentence", "cetinkaya"): ("tlf",
        ". ? ! : ( ) … all end a sentence, ':' without condition (Çetinkaya & Uzun 2010)."),
    ("sentence", "spacy_parser"): ("spacy",
        "Sentence boundaries predicted by the spaCy model's dependency parser; tlf does not change them."),
    # ── word ──
    ("word", "space_unit"): ("tlf",
        "Whitespace-separated piece of the raw text with edge punctuation stripped, containing a "
        "letter or digit; the library's default word."),
    ("word", "space_unit_with_symbols"): ("tlf",
        "space_unit plus pieces made only of listed symbols (% $ + …)."),
    ("word", "pos_token"): ("tlf",
        "A spaCy token whose POS tag is not PUNCT or SYM; numbers count."),
    ("word", "zeyrek_analysed_word"): ("zeyrek",
        "A space_unit that Zeyrek can analyse; the first analysis is used."),
    ("word", "space_unit_numbers_read"): ("tlf",
        "space_unit, but a word with digits counts as the words it is read as (1968 = 5)."),
    # ── type ──
    ("type", "lowercase_surface"): ("tlf",
        "The word string lowercased by language (Turkish I→ı, İ→i); inflected forms are separate types."),
    ("type", "spacy_lemma"): ("spacy",
        "The lemma the spaCy model gives the word's first non-punctuation token, lowercased."),
    ("type", "zeyrek_lemma"): ("zeyrek",
        "Dictionary entry of Zeyrek's first analysis, lowercased, verbs without -mak/-mek; "
        "unanalysed words keep the part before the apostrophe."),
    # ── token ──
    ("token", "spacy_token"): ("spacy",
        "Every spaCy token except whitespace; punctuation and numbers count."),
    # ── syllable (per language) ──
    ("syllable", "vowel_count"): ("tlf",
        "Number of vowels (TDK rule); numbers and listed abbreviations counted as read aloud."),
    ("syllable", "textstat_cmudict"): ("textstat",
        "textstat.syllable_count (at least 1); numbers counted as read aloud; needs NLTK's cmudict."),
    # ── polysyllable ──
    ("polysyllable", "3_plus_syllables"): ("tlf",
        "A word of three or more syllables."),
    # ── letter ──
    ("letter", "unicode_letter"): ("tlf",
        "A character for which str.isalpha() is true."),
    ("letter", "alphabet_letter"): ("tlf",
        "A letter of the language's alphabet (Turkish 29, English 26) after lowercasing."),
    ("letter", "zeyrek_surface_letter"): ("zeyrek",
        "Characters of the surface strings in Zeyrek's analysis (root and suffixes)."),
    # ── character ──
    ("character", "token_string_length"): ("tlf",
        "len() of the lowercased word string, digits included."),
    ("character", "non_space_character"): ("tlf",
        "Every non-whitespace character of the raw text, punctuation included."),
    ("character", "raw_character"): ("tlf",
        "Every character of the raw text, whitespace included."),
    ("character", "sentence_joined_character"): ("tlf",
        "len() of the sentence's tokens joined by single spaces."),
    # ── long_word ──
    ("long_word", "7_plus_letters"): ("tlf",
        "A word with seven or more letters (Björnsson 1968)."),
    # ── paragraph ──
    ("paragraph", "blank_line"): ("tlf",
        "Text between blank lines; a single line break does not separate paragraphs."),
    # ── mark ──
    ("mark", "ten_mark_types"): ("tlf",
        "One of ten mark types (, . ; ! : dash … parentheses quotes ?); three dots are one ellipsis."),
    # ── POS-derived sets ──
    ("noun", "noun_propn"): ("tlf",
        "A word tagged NOUN or PROPN by spaCy."),
    ("verb", "verb_only"): ("tlf",
        "A word tagged VERB by spaCy; AUX is not counted."),
    ("verb", "zeyrek_final_type_verb"): ("zeyrek",
        "A word whose last type in Zeyrek's analysis is Verb."),
    ("lexical_word", "noun_propn_verb_adj_adv"): ("tlf",
        "A word tagged NOUN, PROPN, VERB, ADJ or ADV by spaCy; all adverbs, not only Lu's "
        "(2012) adjective-derived ones."),
    # ── suffix ──
    ("suffix", "zeyrek_visible_suffix"): ("zeyrek",
        "A suffix in Zeyrek's analysis with a non-empty surface string."),
    # ── Kalyoncu (2025) ──
    ("stem", "zeyrek_lemma_derivations"): ("tlf",
        "Zeyrek's lemma plus derivational suffixes; stops at voice, compound-verb, copula or "
        "verbal suffixes; unanalysed words lowercased."),
    ("verbal", "zeyrek_verbal_tag"): ("tlf",
        "A word whose Zeyrek analysis has an infinitive, participle or converb tag; noun + -ken "
        "excluded."),
    ("list_word", "kalyoncu_list"): ("tlf",
        "A word whose form, stem or stem + -mak/-mek is in Kalyoncu's (2025) 4,600-word list, "
        "circumflexes ignored."),
    # ── model outputs used directly ──
    ("pos_tag", "spacy_upos"): ("spacy",
        "The universal POS tag the spaCy model gives the word's first non-punctuation token."),
    ("morph_feature", "spacy_morph"): ("spacy",
        "Universal Dependencies features (Tense, Case …) of the word's first non-punctuation token, "
        "from the spaCy model."),
    ("dependency", "spacy_head"): ("spacy",
        "Head of each token in the spaCy parser's tree; arc length in word positions, "
        "depth in steps to the root."),
    ("zipf_score", "wordfreq_zipf"): ("wordfreq",
        "wordfreq's Zipf score of the lemma; a lemma not in the list scores 0."),
    ("zeyrek_tag", "zeyrek_tag"): ("zeyrek",
        "A morphological tag in Zeyrek's analysis (A3pl, Acc, Neg, Pass …)."),
}
