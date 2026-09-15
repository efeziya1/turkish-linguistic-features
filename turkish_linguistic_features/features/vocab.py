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

# Sözcüksel (analitik) olumsuzluk — negation_analytic_ratio için.
# Ekle olumsuzlama (-ma/-me) BURADA DEĞİL: o morphological_zeyrek.negation_ratio.
ANALYTIC_NEGATION: dict[str, tuple[str, ...]] = {
    "tr": ("değil", "hiç", "asla", "yok", "hiçbir", "hiçbiri", "ne"),
    "en": ("not", "n't", "no", "never", "neither", "nor", "none"),
}

# Otosemantik POS — lexical_density ve thematic_concentration'ın süzgeci.
# Bu kümenin DIŞINDAKİ her POS sinsemantik (işlev) sayılır.
AUTOSEMANTIC_POS: tuple[str, ...] = ("NOUN", "PROPN", "VERB", "ADJ", "ADV")

# Görünüş etiketleri — morph_aspect_* için UD Aspect değerleri.
ASPECT_TAGS: tuple[str, ...] = ("Perf", "Imp", "Prog")
