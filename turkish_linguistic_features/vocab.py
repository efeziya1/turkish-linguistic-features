"""Sabit etiket ve kelime listeleri.

Bu dosya hiçbir şey import etmez. Kasıtlı: ``registry.py`` bu isimlere
ihtiyaç duyuyor ve çok erken import ediliyor; bağımlılığı olan bir modüle
koymak dairesel import yaratırdı.
"""

POS_TAGS: tuple[str, ...] = (
    "NOUN", "PROPN", "VERB", "ADJ", "ADV", "DET", "ADP",
    "INTJ", "CCONJ", "SCONJ", "NUM", "AUX",
)   # 12 tane. PRON kasten yok — pronoun_ratio ayrı feature. PUNCT 2026-10-07'de çıktı (Efe):
    # öznitelikler kelime sayıyor, noktalama noktalama grubunda (`punct_*_ratio`).
    # `pos_bigrams` (13 × 13 sabit ızgara) 2026-09-18'de kaldırıldı — Karar Günlüğü.

# `dep_*` oranları ve DEP_RELATIONS 2026-09-17'de çıktı (Efe) — sonra yeniden bakılacak.

SENT_FINAL_POS: tuple[str, ...] = POS_TAGS + ("PRON",)  # 13

# UD'nin 17 sözcük türü etiketi. `custom_ngrams` öbeğinde büyük harfle yazılmış
# bu adlardan biri kelime değil etiket olarak aranır (2026-10-08, Efe).
UPOS_TAGS: frozenset[str] = frozenset({
    "ADJ", "ADP", "ADV", "AUX", "CCONJ", "DET", "INTJ", "NOUN", "NUM", "PART",
    "PRON", "PROPN", "PUNCT", "SCONJ", "SYM", "VERB", "X",
})

# Kelime sayılmayan etiketler (2026-09-16, Efe). Kelime bekleyen her ölçü
# bunları atar; lemma_tokens'a da girmezler (T21). SYM: %, $, + gibi.
NON_WORD_POS: tuple[str, ...] = ("PUNCT", "SYM")

# Kaynaktan gelen formüllerde "isim" = NOUN + PROPN (2026-09-16, Efe).
# Kaynakların hiçbiri UD'nin özel isim ayrımını yapmıyor; özel isim ismin
# alt türü. Tek istisna pos_noun_ratio / pos_propn_ratio: onlar etiket dağılımı.
NOUN_POS: tuple[str, ...] = ("NOUN", "PROPN")

# Sözcüksel (anlamlı) kelime — Ure (1971) lexical_density, Lu (2012) N_lex.
# Lu yalnız sıfattan türemiş zarfları sayıyor (-ly); bütün ADV sayılır, çünkü
# etiketleyici zarf türünü ayırmıyor (#4 kaldırıldı, 2026-10-27, Efe). Bu kümenin
# DIŞINDAKİ her POS işlev sayılır.
# Tematik yoğunlaşma da bu tanımı kullanır (tek tanım, 2026-10-15, Efe): QUITA
# (Kubát vd. 2014, s.50-51) tematik sözcük seçimini araştırmacıya bırakıyor.
LEXICAL_POS: tuple[str, ...] = ("NOUN", "PROPN", "VERB", "ADJ", "ADV")

# Görünüş etiketleri — aspect_*_ratio için UD Aspect değerleri.
ASPECT_TAGS: tuple[str, ...] = ("Perf", "Imp", "Prog")
