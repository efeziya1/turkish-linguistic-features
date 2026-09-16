"""Sabit etiket ve kelime listeleri — ``API-SOZLESMESI.md`` §5'ten birebir.

Bu dosya hiçbir şey import etmez. Kasıtlı: ``registry.py`` bu isimlere
ihtiyaç duyuyor ve çok erken import ediliyor; bağımlılığı olan bir modüle
koymak dairesel import yaratırdı.
"""

POS_TAGS: tuple[str, ...] = (
    "NOUN", "PROPN", "VERB", "ADJ", "ADV", "DET", "ADP",
    "INTJ", "CCONJ", "SCONJ", "NUM", "AUX", "PUNCT",
)   # 13 tane. PRON kasten yok — pronoun_freq ayrı feature.
    # posbg_ ızgarası 13 × 13 = 169 sütun üretir.

DEP_RELATIONS: tuple[str, ...] = (
    "acl", "advcl", "advmod", "amod", "appos", "aux", "case", "cc",
    "ccomp", "clf", "compound", "conj", "cop", "csubj", "dep", "det",
    "discourse", "dislocated", "expl", "fixed", "flat", "goeswith",
    "iobj", "list", "mark", "nmod", "nsubj", "nummod", "obj", "obl",
    "orphan", "parataxis", "punct", "reparandum", "root", "vocative",
    "xcomp", "other",
)   # 37 UD ilişkisi + "other" artık kovası = 38

SENT_FINAL_POS: tuple[str, ...] = tuple(p for p in POS_TAGS if p != "PUNCT") + ("PRON",)  # 13

# Kaynaktan gelen formüllerde "isim" = NOUN + PROPN (2026-09-16, Efe).
# Kaynakların hiçbiri UD'nin özel isim ayrımını yapmıyor; özel isim ismin
# alt türü. Tek istisna pos_noun / pos_propn: onlar etiket dağılımı.
NOUN_POS: tuple[str, ...] = ("NOUN", "PROPN")

# Sözcüksel (anlamlı) kelime — Ure (1971) lexical_density, Lu (2012) N_lex.
# Lu yalnız sıfattan türemiş zarfları sayıyor (-ly); Türkçeye aktarılamadığı
# için bütün ADV. Bu kümenin DIŞINDAKİ her POS işlev sayılır.
LEXICAL_POS: tuple[str, ...] = ("NOUN", "PROPN", "VERB", "ADJ", "ADV")

# Konu kelimesi — thematic_concentration / STC. QUITA kılavuzu s. 50: "We
# usually consider nouns, verbs and adjectives to be thematic words";
# Popescu ve ark. (2009) da zarf saymıyor.
THEMATIC_POS: tuple[str, ...] = ("NOUN", "PROPN", "VERB", "ADJ")

# Görünüş etiketleri — morph_aspect_* için UD Aspect değerleri.
ASPECT_TAGS: tuple[str, ...] = ("Perf", "Imp", "Prog")
