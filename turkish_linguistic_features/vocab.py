"""Sabit etiket ve kelime listeleri.

Bu dosya hiçbir şey import etmez. Kasıtlı: ``registry.py`` bu isimlere
ihtiyaç duyuyor ve çok erken import ediliyor; bağımlılığı olan bir modüle
koymak dairesel import yaratırdı.
"""

POS_TAGS: tuple[str, ...] = (
    "NOUN", "PROPN", "VERB", "ADJ", "ADV", "DET", "ADP",
    "INTJ", "CCONJ", "SCONJ", "NUM", "AUX", "PUNCT",
)   # 13 tane. PRON kasten yok — pronoun_freq ayrı feature.
    # `pos_bigrams` (13 × 13 sabit ızgara) 2026-09-18'de kaldırıldı — Karar Günlüğü.

# `dep_*` oranları ve DEP_RELATIONS 2026-09-17'de çıktı (Efe) — sonra yeniden bakılacak.

SENT_FINAL_POS: tuple[str, ...] = tuple(p for p in POS_TAGS if p != "PUNCT") + ("PRON",)  # 13

# Kelime sayılmayan etiketler (2026-09-16, Efe). Kelime bekleyen her ölçü
# bunları atar; lemma_tokens'a da girmezler (T21). SYM: %, $, + gibi.
NON_WORD_POS: tuple[str, ...] = ("PUNCT", "SYM")

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
