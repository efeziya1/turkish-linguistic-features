<!-- ÜRETİLMİŞ DOSYA — elle düzenlemeyin.
     Kaynak: scripts/dogrulama_raporu.py
     Yeniden üretmek için:
       uv run python scripts/dogrulama_raporu.py -->

# Doğrulama raporu

Bu rapor her özniteliğin ürettiği sayıyı, dayandığı kaynağın **yayımladığı
sayıyla** karşılaştırır. Amaç basit: bir sayıyı çalışmanızda kullanmadan önce
onun literatürdeki değeri tuttuğunu görebilmeniz.

## Durumlar ne anlama geliyor

| | Anlamı |
|---|---|
| ✅ **birebir** | Kaynağın yayımladığı sayıyla tolerans içinde aynı. |
| 🟡 **belgelenmiş sapma** | Fark var ve **nedeni yazılı**. Genellikle kaynağın ara değerleri yuvarlaması. Sapmanın sonuca etkisi satırda anlatılır. |
| ⚪ **kaynakta sayısal örnek yok** | Kaynak formülü veriyor ama uygulanmış bir örnek vermiyor; yalnız formül ve sınır durumları sınanıyor. |
| ⚪ **kaynak yok** | Adlandırılmış bir literatür ölçüsü değil (`punc_,_ratio` gibi saf tanım). |
| ❌ **uyuşmazlık** | Açıklanmamış fark. **Yayın kapısı:** bir tane bile varsa sürüm çıkmaz. |

Tolerans 0.05. Kaynaklar ara değerleri yuvarlayarak bastığı için mutlak
eşitlik beklenmiyor; farkın nereden geldiği bilinmiyorsa satır ❌ olur.

Bu rapor **testlerden üretilir** — `tests/test_kaynak_esligi.py` ile aynı
karşılaştırma tablosunu okur, yani ikisi ayrışamaz. Diğer bilinen-değer
testleri (T04B, T05–T07, T10, T13) kendi dosyalarında duruyor.


## Türkçe — 208 anahtar

| Durum | Anahtar sayısı |
|---|---|
| ✅ birebir | 2 |
| 🟡 belgelenmis sapma | 1 |
| ⚪ kaynakta sayisal ornek yok | 133 |
| ⚪ kaynak yok | 72 |

### Sayısal karşılaştırması olanlar

| Anahtar | Kaynak | Örnek | Beklenen | Bizim | Fark | Durum |
|---|---|---|---|---|---|---|
| `atesman` | Ateşman (1997) | Kalyoncu & Memiş (2024) Tablo 9 · Metin 2 | 23.094 | 23.094 | -0.000 | ✅ |
| `cetinkaya_uzun` | Çetinkaya (2010) | Kalyoncu & Memiş (2024) Tablo 9 · Metin 2 | 23.084 | 23.084 | -0.000 | ✅ |
| `bezirci_yilmaz` | Bezirci & Yılmaz (2010) | Kalyoncu & Memiş (2024) Tablo 9 · Metin 2 | 30.423 | 30.392 | -0.031 | 🟡 |

**`bezirci_yilmaz` sapması:** Makalenin H6 ara değeri yuvarlanmış; fark 0,031 ve iki değer de aynı okunabilirlik sınıfına (akademik, 16+) düşüyor.

### Sayısal örneği olmayanlar

205 anahtar. Kaynağı olanlar formül ve sınır durumu testleriyle sınanıyor; kaynağı olmayanlar adlandırılmış literatür ölçüsü değil.

| Anahtar | Kaynak | Durum |
|---|---|---|
| `n_lemma_count` | — | ⚪ |
| `avg_word_length` | — | ⚪ |
| `word_length_cv` | — | ⚪ |
| `entropy` | Shannon (1948), aktaran QUITA §6.1.12 | ⚪ |
| `yule_k` | Yule (1944), aktaran Malvern et al. (2004) denk. 3.9 | ⚪ |
| `simpson_d` | Simpson (1949), aktaran Bestgen (2023) | ⚪ |
| `ttr` | Malvern et al. (2004); QUITA §6.1.1 | ⚪ |
| `brunet_w` | Brunet (1978), aktaran Tweedie & Baayen (1998) s.328, denk. (10) | ⚪ |
| `hapax_ratio` | — | ⚪ |
| `hapax_percentage` | QUITA §6.1.6 | ⚪ |
| `mattr` | Covington & McFall (2010); varsayılan pencere 50, dil öğrenimi yazınının değeri — C&M'nin kendi önerisi 500 | ⚪ |
| `entropy_std` | — | ⚪ |
| `herdan_c` | Herdan (1960/1964), aktaran Tweedie & Baayen (1998) s.327, denk. (5) | ⚪ |
| `mtld` | McCarthy & Jarvis (2010) s.383–385 | ⚪ |
| `dugast_u` | Dugast (1978), aktaran Malvern et al. (2004) denk. 2.7 | ⚪ |
| `guiraud_r` | Guiraud (1954) s.53, alternatif biçim (bütün sözcük türleri), aktaran Daller (2010); asıl yasası V/√(2N), yalnız içerik sözcükleri | ⚪ |
| `ttr_moving_slope` | — | ⚪ |
| `heaps_beta` | Heaps (1978), aktaran Manning et al. (2008) §5.1.1 | ⚪ |
| `sichel_s` | Sichel (1975); formül Malvern et al. (2004) denk. 3.10 | ⚪ |
| `noun_variation` | Lu (2012) Tablo 2 | ⚪ |
| `verb_variation` | Lu (2012) Tablo 2 | ⚪ |
| `adj_variation` | Lu (2012) Tablo 2 | ⚪ |
| `adv_variation` | Lu (2012) Tablo 2 | ⚪ |
| `zipf_exponent` | Piantadosi (2014) denk. (2); aynı kaynak aynı korpustan r ve f(r) kestirimini eleştiriyor | ⚪ |
| `zipf_r2` | Piantadosi (2014) denk. (2); aynı kaynak aynı korpustan r ve f(r) kestirimini eleştiriyor | ⚪ |
| `zipf_mandelbrot_q` | Piantadosi (2014) denk. (2); aynı kaynak aynı korpustan r ve f(r) kestirimini eleştiriyor | ⚪ |
| `zipf_mandelbrot_s` | Piantadosi (2014) denk. (2); aynı kaynak aynı korpustan r ve f(r) kestirimini eleştiriyor | ⚪ |
| `wordfreq_mean` | van Heuven ve ark. (2014) (Zipf ölçeği) | ⚪ |
| `wordfreq_rare_ratio` | van Heuven ve ark. (2014) Tablo 1 (Zipf ≤ 3 = düşük frekans) | ⚪ |
| `vocd_d` | Malvern et al. (2004) s.56–57; yordam McCarthy & Jarvis (2010) s.383 | ⚪ |
| `hdd` | McCarthy & Jarvis (2007), aktaran McCarthy & Jarvis (2010) s.383 | ⚪ |
| `msttr` | Johnson (1944), aktaran Malvern et al. (2004) s.25 ve McCarthy & Jarvis (2010) s.385 | ⚪ |
| `h_point` | QUITA §6.1.2; Popescu & Altmann (2006) | ⚪ |
| `vocab_richness_r1` | Popescu et al. (2009) denk. 3.8 | ⚪ |
| `vocab_richness_r4` | Popescu et al. (2009) denk. 3.24 | ⚪ |
| `repeat_rate` | QUITA §6.1.4 | ⚪ |
| `rr_mcintosh` | QUITA §6.1.5 | ⚪ |
| `gini_coef` | QUITA §6.1.8 | ⚪ |
| `curve_length` | QUITA §6.1.10 | ⚪ |
| `curve_length_r` | QUITA §6.1.11 | ⚪ |
| `lambda_pa` | QUITA §6.1.7; Popescu, Čech & Altmann (2011) | ⚪ |
| `adjusted_modulus` | QUITA §6.1.13 | ⚪ |
| `writers_view_alpha` | Popescu, Mačutek & Altmann (2009) denk. 4.5 | ⚪ |
| `thematic_concentration` | QUITA §6.2.5 | ⚪ |
| `secondary_thematic_concentration` | QUITA §6.2.6 | ⚪ |
| `avg_sent_len_word` | — | ⚪ |
| `sentence_length_cv` | — | ⚪ |
| `sent_len_skewness` | — | ⚪ |
| `med_sent_len` | — | ⚪ |
| `avg_sent_len_char` | — | ⚪ |
| `short_sent_ratio` | — | ⚪ |
| `long_sent_ratio` | — | ⚪ |
| `sent_len_entropy` | — | ⚪ |
| `para_len_mean` | — | ⚪ |
| `para_len_cv` | — | ⚪ |
| `sents_per_para_mean` | — | ⚪ |
| `sents_per_para_cv` | — | ⚪ |
| `para_count_norm` | — | ⚪ |
| `pos_noun` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `pos_propn` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `pos_verb` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `pos_adj` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `pos_adv` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `pos_det` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `pos_adp` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `pos_intj` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `pos_cconj` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `pos_sconj` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `pos_num` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `pos_aux` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `pos_punct` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `question_per_sent` | — | ⚪ |
| `pronoun_freq` | — | ⚪ |
| `nominal_verbal_ratio` | — | ⚪ |
| `verb_dist_mean` | QUITA §6.2.1 | ⚪ |
| `verb_dist_cv` | QUITA §6.2.1 | ⚪ |
| `activity_ratio` | QUITA §6.2.2 | ⚪ |
| `lexical_density` | Lu (2012); tanım Halliday'ci geniş biçimde — bütün açık sınıf sözcükler | ⚪ |
| `pos_dist_std` | Deutsch, Jasbi & Shieber (2020) Tanım 3.3 (POSDdev); oranlar üzerinden, 13 UD etiketi | ⚪ |
| `pos_kl_div` | Deutsch, Jasbi & Shieber (2020) Tanım 3.4 (POSdiv), bit | ⚪ |
| `arc_len_mean` | Liu (2008) denk. (1); metin düzeyi Jing & Liu (2015) s.164, denk. (3) (MDD2) | ⚪ |
| `parse_depth_mean` | Jing & Liu (2015) s.164, denk. (2) ve (4) (MHD2) | ⚪ |
| `sentfinal_noun` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `sentfinal_propn` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `sentfinal_verb` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `sentfinal_adj` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `sentfinal_adv` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `sentfinal_det` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `sentfinal_adp` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `sentfinal_intj` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `sentfinal_cconj` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `sentfinal_sconj` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `sentfinal_num` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `sentfinal_aux` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `sentfinal_pron` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `sentfinal_other` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `surface_per_lemma` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_tense_past` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_tense_pres` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_tense_fut` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_aspect_perf` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_aspect_imp` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_aspect_prog` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_case_nom` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_case_acc` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_case_dat` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_case_loc` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_case_abl` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_case_gen` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_person_1` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_person_2` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_person_3` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_number_sing` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_number_plur` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_voice_pass` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `agglutination_depth` | Zeyrek (Zemberek morfotaktiğinin Python aktarımı); etiket kümesi Akın & Akın (2007) | ⚪ |
| `suffix_char_length_ratio` | Zeyrek (Zemberek morfotaktiğinin Python aktarımı); etiket kümesi Akın & Akın (2007) | ⚪ |
| `suffix_bigram_entropy` | Zeyrek (Zemberek morfotaktiğinin Python aktarımı); etiket kümesi Akın & Akın (2007) | ⚪ |
| `suffix_chain_cv` | Zeyrek (Zemberek morfotaktiğinin Python aktarımı); etiket kümesi Akın & Akın (2007) | ⚪ |
| `derivational_suffix_ratio` | Zeyrek (Zemberek morfotaktiğinin Python aktarımı); etiket kümesi Akın & Akın (2007) | ⚪ |
| `tense_past_def` | Zeyrek (Zemberek morfotaktiğinin Python aktarımı); etiket kümesi Akın & Akın (2007) | ⚪ |
| `tense_past_nar` | Zeyrek (Zemberek morfotaktiğinin Python aktarımı); etiket kümesi Akın & Akın (2007) | ⚪ |
| `tense_present` | Zeyrek (Zemberek morfotaktiğinin Python aktarımı); etiket kümesi Akın & Akın (2007) | ⚪ |
| `tense_future` | Zeyrek (Zemberek morfotaktiğinin Python aktarımı); etiket kümesi Akın & Akın (2007) | ⚪ |
| `modal_possibility_ratio` | Zeyrek (Zemberek morfotaktiğinin Python aktarımı); etiket kümesi Akın & Akın (2007) | ⚪ |
| `modal_necessity_ratio` | Zeyrek (Zemberek morfotaktiğinin Python aktarımı); etiket kümesi Akın & Akın (2007) | ⚪ |
| `negation_ratio` | Zeyrek (Zemberek morfotaktiğinin Python aktarımı); etiket kümesi Akın & Akın (2007) | ⚪ |
| `passive_ratio` | Zeyrek (Zemberek morfotaktiğinin Python aktarımı); etiket kümesi Akın & Akın (2007) | ⚪ |
| `plural_ratio` | Zeyrek (Zemberek morfotaktiğinin Python aktarımı); etiket kümesi Akın & Akın (2007) | ⚪ |
| `case_acc_ratio` | Zeyrek (Zemberek morfotaktiğinin Python aktarımı); etiket kümesi Akın & Akın (2007) | ⚪ |
| `case_dat_ratio` | Zeyrek (Zemberek morfotaktiğinin Python aktarımı); etiket kümesi Akın & Akın (2007) | ⚪ |
| `case_loc_ratio` | Zeyrek (Zemberek morfotaktiğinin Python aktarımı); etiket kümesi Akın & Akın (2007) | ⚪ |
| `case_abl_ratio` | Zeyrek (Zemberek morfotaktiğinin Python aktarımı); etiket kümesi Akın & Akın (2007) | ⚪ |
| `case_gen_ratio` | Zeyrek (Zemberek morfotaktiğinin Python aktarımı); etiket kümesi Akın & Akın (2007) | ⚪ |
| `case_ins_ratio` | Zeyrek (Zemberek morfotaktiğinin Python aktarımı); etiket kümesi Akın & Akın (2007) | ⚪ |
| `conditional_suffix_ratio` | Zeyrek (Zemberek morfotaktiğinin Python aktarımı); etiket kümesi Akın & Akın (2007) | ⚪ |
| `causative_suffix_ratio` | Zeyrek (Zemberek morfotaktiğinin Python aktarımı); etiket kümesi Akın & Akın (2007) | ⚪ |
| `question_particle_ratio` | Zeyrek (Zemberek morfotaktiğinin Python aktarımı); etiket kümesi Akın & Akın (2007) | ⚪ |
| `verb_suffix_diversity` | Zeyrek (Zemberek morfotaktiğinin Python aktarımı); etiket kümesi Akın & Akın (2007) | ⚪ |
| `vowel_ratio` | — | ⚪ |
| `front_vowel_ratio` | Göksel & Kerslake (2005) böl. 2 (ünlü dizgesi, ince/kalın) | ⚪ |
| `back_vowel_ratio` | Göksel & Kerslake (2005) böl. 2 (ünlü dizgesi, ince/kalın) | ⚪ |
| `harmony_fronting_ratio` | Göksel & Kerslake (2005) §3.1 (fronting harmony); istisnalar §3.4 — ölçü onları uyumsuz sayar | ⚪ |
| `harmony_rounding_ratio` | Göksel & Kerslake (2005) §3.1 (rounding harmony); aslında bir ek olayı, bütün-kelime örüntüsü olarak ölçülüyor | ⚪ |
| `syllable_mean` | Bezirci & Yılmaz (2010) Tablo 1-c | ⚪ |
| `syllable_cv` | Bezirci & Yılmaz (2010) Tablo 1-c | ⚪ |
| `syllable_1_ratio` | Bezirci & Yılmaz (2010) Tablo 1-c | ⚪ |
| `syllable_2_ratio` | Bezirci & Yılmaz (2010) Tablo 1-c | ⚪ |
| `syllable_3_ratio` | Bezirci & Yılmaz (2010) Tablo 1-c | ⚪ |
| `syllable_4_ratio` | Bezirci & Yılmaz (2010) Tablo 1-c | ⚪ |
| `syllable_5_ratio` | Bezirci & Yılmaz (2010) Tablo 1-c | ⚪ |
| `syllable_6plus_ratio` | Bezirci & Yılmaz (2010) Tablo 1-c | ⚪ |
| `sentence_syllable_mean` | — | ⚪ |
| `sentence_syllable_cv` | — | ⚪ |
| `ari` | Smith & Senter (1967) s.8, AMRL-TR-66-220; aynen Kincaid et al. (1975) s.14, Tablo 3 ("Old") | ⚪ |
| `coleman_liau` | Coleman & Liau (1975) s.284; formül iki denklemin bileşkesi, makalede bu hâliyle geçmez | ⚪ |
| `lix` | Björnsson (1968), aktaran Anderson (1983) s.490; uzun sözcük = 7+ harf | ⚪ |
| `long_word_ratio` | Anderson (1983); uzun sözcük = 7+ harf | ⚪ |
| `digit_vs_all` | — | ⚪ |
| `punc_,_ratio` | — | ⚪ |
| `punc_._ratio` | — | ⚪ |
| `punc_;_ratio` | — | ⚪ |
| `punc_!_ratio` | — | ⚪ |
| `punc_:_ratio` | — | ⚪ |
| `punc_-_ratio` | — | ⚪ |
| `punc_ellipsis_ratio` | — | ⚪ |
| `punc_paren_ratio` | — | ⚪ |
| `punc_quote_ratio` | — | ⚪ |
| `punc_question_ratio` | — | ⚪ |
| `punct_density` | — | ⚪ |
| `punct_entropy` | — | ⚪ |
| `consecutive_punct_ratio` | — | ⚪ |
| `whitespace_ratio` | — | ⚪ |
| `punct_variety` | — | ⚪ |
| `uppercase_ratio` | — | ⚪ |
| `all_caps_word_ratio` | — | ⚪ |
| `char_a` | — | ⚪ |
| `char_b` | — | ⚪ |
| `char_c` | — | ⚪ |
| `char_ç` | — | ⚪ |
| `char_d` | — | ⚪ |
| `char_e` | — | ⚪ |
| `char_f` | — | ⚪ |
| `char_g` | — | ⚪ |
| `char_ğ` | — | ⚪ |
| `char_h` | — | ⚪ |
| `char_ı` | — | ⚪ |
| `char_i` | — | ⚪ |
| `char_j` | — | ⚪ |
| `char_k` | — | ⚪ |
| `char_l` | — | ⚪ |
| `char_m` | — | ⚪ |
| `char_n` | — | ⚪ |
| `char_o` | — | ⚪ |
| `char_ö` | — | ⚪ |
| `char_p` | — | ⚪ |
| `char_r` | — | ⚪ |
| `char_s` | — | ⚪ |
| `char_ş` | — | ⚪ |
| `char_t` | — | ⚪ |
| `char_u` | — | ⚪ |
| `char_ü` | — | ⚪ |
| `char_v` | — | ⚪ |
| `char_y` | — | ⚪ |
| `char_z` | — | ⚪ |

## İngilizce — 182 anahtar

| Durum | Anahtar sayısı |
|---|---|
| ⚪ kaynakta sayisal ornek yok | 112 |
| ⚪ kaynak yok | 70 |

### Sayısal karşılaştırması olanlar

| Anahtar | Kaynak | Örnek | Beklenen | Bizim | Fark | Durum |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — |

### Sayısal örneği olmayanlar

182 anahtar. Kaynağı olanlar formül ve sınır durumu testleriyle sınanıyor; kaynağı olmayanlar adlandırılmış literatür ölçüsü değil.

| Anahtar | Kaynak | Durum |
|---|---|---|
| `n_lemma_count` | — | ⚪ |
| `avg_word_length` | — | ⚪ |
| `word_length_cv` | — | ⚪ |
| `entropy` | Shannon (1948), aktaran QUITA §6.1.12 | ⚪ |
| `yule_k` | Yule (1944), aktaran Malvern et al. (2004) denk. 3.9 | ⚪ |
| `simpson_d` | Simpson (1949), aktaran Bestgen (2023) | ⚪ |
| `ttr` | Malvern et al. (2004); QUITA §6.1.1 | ⚪ |
| `brunet_w` | Brunet (1978), aktaran Tweedie & Baayen (1998) s.328, denk. (10) | ⚪ |
| `hapax_ratio` | — | ⚪ |
| `hapax_percentage` | QUITA §6.1.6 | ⚪ |
| `mattr` | Covington & McFall (2010); varsayılan pencere 50, dil öğrenimi yazınının değeri — C&M'nin kendi önerisi 500 | ⚪ |
| `entropy_std` | — | ⚪ |
| `herdan_c` | Herdan (1960/1964), aktaran Tweedie & Baayen (1998) s.327, denk. (5) | ⚪ |
| `mtld` | McCarthy & Jarvis (2010) s.383–385 | ⚪ |
| `dugast_u` | Dugast (1978), aktaran Malvern et al. (2004) denk. 2.7 | ⚪ |
| `guiraud_r` | Guiraud (1954) s.53, alternatif biçim (bütün sözcük türleri), aktaran Daller (2010); asıl yasası V/√(2N), yalnız içerik sözcükleri | ⚪ |
| `ttr_moving_slope` | — | ⚪ |
| `heaps_beta` | Heaps (1978), aktaran Manning et al. (2008) §5.1.1 | ⚪ |
| `sichel_s` | Sichel (1975); formül Malvern et al. (2004) denk. 3.10 | ⚪ |
| `noun_variation` | Lu (2012) Tablo 2 | ⚪ |
| `verb_variation` | Lu (2012) Tablo 2 | ⚪ |
| `adj_variation` | Lu (2012) Tablo 2 | ⚪ |
| `adv_variation` | Lu (2012) Tablo 2 | ⚪ |
| `zipf_exponent` | Piantadosi (2014) denk. (2); aynı kaynak aynı korpustan r ve f(r) kestirimini eleştiriyor | ⚪ |
| `zipf_r2` | Piantadosi (2014) denk. (2); aynı kaynak aynı korpustan r ve f(r) kestirimini eleştiriyor | ⚪ |
| `zipf_mandelbrot_q` | Piantadosi (2014) denk. (2); aynı kaynak aynı korpustan r ve f(r) kestirimini eleştiriyor | ⚪ |
| `zipf_mandelbrot_s` | Piantadosi (2014) denk. (2); aynı kaynak aynı korpustan r ve f(r) kestirimini eleştiriyor | ⚪ |
| `wordfreq_mean` | van Heuven ve ark. (2014) (Zipf ölçeği) | ⚪ |
| `wordfreq_rare_ratio` | van Heuven ve ark. (2014) Tablo 1 (Zipf ≤ 3 = düşük frekans) | ⚪ |
| `vocd_d` | Malvern et al. (2004) s.56–57; yordam McCarthy & Jarvis (2010) s.383 | ⚪ |
| `hdd` | McCarthy & Jarvis (2007), aktaran McCarthy & Jarvis (2010) s.383 | ⚪ |
| `msttr` | Johnson (1944), aktaran Malvern et al. (2004) s.25 ve McCarthy & Jarvis (2010) s.385 | ⚪ |
| `h_point` | QUITA §6.1.2; Popescu & Altmann (2006) | ⚪ |
| `vocab_richness_r1` | Popescu et al. (2009) denk. 3.8 | ⚪ |
| `vocab_richness_r4` | Popescu et al. (2009) denk. 3.24 | ⚪ |
| `repeat_rate` | QUITA §6.1.4 | ⚪ |
| `rr_mcintosh` | QUITA §6.1.5 | ⚪ |
| `gini_coef` | QUITA §6.1.8 | ⚪ |
| `curve_length` | QUITA §6.1.10 | ⚪ |
| `curve_length_r` | QUITA §6.1.11 | ⚪ |
| `lambda_pa` | QUITA §6.1.7; Popescu, Čech & Altmann (2011) | ⚪ |
| `adjusted_modulus` | QUITA §6.1.13 | ⚪ |
| `writers_view_alpha` | Popescu, Mačutek & Altmann (2009) denk. 4.5 | ⚪ |
| `thematic_concentration` | QUITA §6.2.5 | ⚪ |
| `secondary_thematic_concentration` | QUITA §6.2.6 | ⚪ |
| `avg_sent_len_word` | — | ⚪ |
| `sentence_length_cv` | — | ⚪ |
| `sent_len_skewness` | — | ⚪ |
| `med_sent_len` | — | ⚪ |
| `avg_sent_len_char` | — | ⚪ |
| `short_sent_ratio` | — | ⚪ |
| `long_sent_ratio` | — | ⚪ |
| `sent_len_entropy` | — | ⚪ |
| `para_len_mean` | — | ⚪ |
| `para_len_cv` | — | ⚪ |
| `sents_per_para_mean` | — | ⚪ |
| `sents_per_para_cv` | — | ⚪ |
| `para_count_norm` | — | ⚪ |
| `pos_noun` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `pos_propn` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `pos_verb` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `pos_adj` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `pos_adv` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `pos_det` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `pos_adp` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `pos_intj` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `pos_cconj` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `pos_sconj` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `pos_num` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `pos_aux` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `pos_punct` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `question_per_sent` | — | ⚪ |
| `pronoun_freq` | — | ⚪ |
| `nominal_verbal_ratio` | — | ⚪ |
| `verb_dist_mean` | QUITA §6.2.1 | ⚪ |
| `verb_dist_cv` | QUITA §6.2.1 | ⚪ |
| `activity_ratio` | QUITA §6.2.2 | ⚪ |
| `lexical_density` | Lu (2012); tanım Halliday'ci geniş biçimde — bütün açık sınıf sözcükler | ⚪ |
| `pos_dist_std` | Deutsch, Jasbi & Shieber (2020) Tanım 3.3 (POSDdev); oranlar üzerinden, 13 UD etiketi | ⚪ |
| `pos_kl_div` | Deutsch, Jasbi & Shieber (2020) Tanım 3.4 (POSdiv), bit | ⚪ |
| `arc_len_mean` | Liu (2008) denk. (1); metin düzeyi Jing & Liu (2015) s.164, denk. (3) (MDD2) | ⚪ |
| `parse_depth_mean` | Jing & Liu (2015) s.164, denk. (2) ve (4) (MHD2) | ⚪ |
| `sentfinal_noun` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `sentfinal_propn` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `sentfinal_verb` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `sentfinal_adj` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `sentfinal_adv` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `sentfinal_det` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `sentfinal_adp` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `sentfinal_intj` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `sentfinal_cconj` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `sentfinal_sconj` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `sentfinal_num` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `sentfinal_aux` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `sentfinal_pron` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `sentfinal_other` | de Marneffe ve ark. (2021) Tablo 1 (UPOS etiket kümesi) | ⚪ |
| `surface_per_lemma` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_tense_past` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_tense_pres` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_tense_fut` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_aspect_perf` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_aspect_imp` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_aspect_prog` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_case_nom` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_case_acc` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_case_dat` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_case_loc` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_case_abl` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_case_gen` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_person_1` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_person_2` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_person_3` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_number_sing` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_number_plur` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `morph_voice_pass` | de Marneffe ve ark. (2021) Tablo 2 (evrensel morfolojik özellikler) | ⚪ |
| `vowel_ratio` | — | ⚪ |
| `front_vowel_ratio` | Göksel & Kerslake (2005) böl. 2 (ünlü dizgesi, ince/kalın) | ⚪ |
| `back_vowel_ratio` | Göksel & Kerslake (2005) böl. 2 (ünlü dizgesi, ince/kalın) | ⚪ |
| `harmony_fronting_ratio` | Göksel & Kerslake (2005) §3.1 (fronting harmony); istisnalar §3.4 — ölçü onları uyumsuz sayar | ⚪ |
| `harmony_rounding_ratio` | Göksel & Kerslake (2005) §3.1 (rounding harmony); aslında bir ek olayı, bütün-kelime örüntüsü olarak ölçülüyor | ⚪ |
| `syllable_mean` | Bezirci & Yılmaz (2010) Tablo 1-c | ⚪ |
| `syllable_cv` | Bezirci & Yılmaz (2010) Tablo 1-c | ⚪ |
| `syllable_1_ratio` | Bezirci & Yılmaz (2010) Tablo 1-c | ⚪ |
| `syllable_2_ratio` | Bezirci & Yılmaz (2010) Tablo 1-c | ⚪ |
| `syllable_3_ratio` | Bezirci & Yılmaz (2010) Tablo 1-c | ⚪ |
| `syllable_4_ratio` | Bezirci & Yılmaz (2010) Tablo 1-c | ⚪ |
| `syllable_5_ratio` | Bezirci & Yılmaz (2010) Tablo 1-c | ⚪ |
| `syllable_6plus_ratio` | Bezirci & Yılmaz (2010) Tablo 1-c | ⚪ |
| `sentence_syllable_mean` | — | ⚪ |
| `sentence_syllable_cv` | — | ⚪ |
| `ari` | Smith & Senter (1967) s.8, AMRL-TR-66-220; aynen Kincaid et al. (1975) s.14, Tablo 3 ("Old") | ⚪ |
| `coleman_liau` | Coleman & Liau (1975) s.284; formül iki denklemin bileşkesi, makalede bu hâliyle geçmez | ⚪ |
| `lix` | Björnsson (1968), aktaran Anderson (1983) s.490; uzun sözcük = 7+ harf | ⚪ |
| `long_word_ratio` | Anderson (1983); uzun sözcük = 7+ harf | ⚪ |
| `flesch_reading_ease` | Flesch (1948) Formül A; katsayı .846, birim 100 sözcükteki hece | ⚪ |
| `flesch_kincaid_grade` | Kincaid et al. (1975) s.14, Tablo 3, "New" | ⚪ |
| `smog` | McLaughlin (1969) s.643, Tablo 1, denk. (d); p = 30 cümlelik örneklemdeki çok heceli sözcük | ⚪ |
| `polysyllabic_word_ratio` | — | ⚪ |
| `digit_vs_all` | — | ⚪ |
| `punc_,_ratio` | — | ⚪ |
| `punc_._ratio` | — | ⚪ |
| `punc_;_ratio` | — | ⚪ |
| `punc_!_ratio` | — | ⚪ |
| `punc_:_ratio` | — | ⚪ |
| `punc_-_ratio` | — | ⚪ |
| `punc_ellipsis_ratio` | — | ⚪ |
| `punc_paren_ratio` | — | ⚪ |
| `punc_quote_ratio` | — | ⚪ |
| `punc_question_ratio` | — | ⚪ |
| `punct_density` | — | ⚪ |
| `punct_entropy` | — | ⚪ |
| `consecutive_punct_ratio` | — | ⚪ |
| `whitespace_ratio` | — | ⚪ |
| `punct_variety` | — | ⚪ |
| `uppercase_ratio` | — | ⚪ |
| `all_caps_word_ratio` | — | ⚪ |
| `char_a` | — | ⚪ |
| `char_b` | — | ⚪ |
| `char_c` | — | ⚪ |
| `char_d` | — | ⚪ |
| `char_e` | — | ⚪ |
| `char_f` | — | ⚪ |
| `char_g` | — | ⚪ |
| `char_h` | — | ⚪ |
| `char_i` | — | ⚪ |
| `char_j` | — | ⚪ |
| `char_k` | — | ⚪ |
| `char_l` | — | ⚪ |
| `char_m` | — | ⚪ |
| `char_n` | — | ⚪ |
| `char_o` | — | ⚪ |
| `char_p` | — | ⚪ |
| `char_q` | — | ⚪ |
| `char_r` | — | ⚪ |
| `char_s` | — | ⚪ |
| `char_t` | — | ⚪ |
| `char_u` | — | ⚪ |
| `char_v` | — | ⚪ |
| `char_w` | — | ⚪ |
| `char_x` | — | ⚪ |
| `char_y` | — | ⚪ |
| `char_z` | — | ⚪ |
