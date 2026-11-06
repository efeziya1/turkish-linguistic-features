# Kalyoncu (2025) formulas

Kalyoncu (2025) proposes four readability formulas for Turkish (K1–K4). Their output is
"text difficulty": **a higher value means a harder text**. The tool gives the four formulas
and their five components in the `readability` group. These keys are produced for Turkish only.

| Key | Kalyoncu's name | Definition | Source |
|---|---|---|---|
| `kalyoncu_kl` | KL | words not in the list / words × 100 | p.71–72 |
| `kalyoncu_ttr` | TTR | stems occurring once / words × 100 | p.73 |
| `kalyoncu_kco` | KCO | complex sentences / sentences × 100 | p.73 |
| `kalyoncu_yco` | YCO | verbals / sentences × 10 | p.74 |
| `kalyoncu_ocu` | OCU | words / sentences | p.77 |
| `kalyoncu_k1` … `kalyoncu_k4` | First … Fourth formula | below | p.97–99 |

`kalyoncu_ttr` is not the tool's `ttr`: it measures the share of stems that occur **only once**,
not the share of distinct words. Kalyoncu calls this measure TTR.

## Formulas

| Key | Formula (Tables 31–34) |
|---|---|
| `kalyoncu_k1` | −29.829 + 0.508·KL + 1.191·TTR + 0.733·KCO − 0.66·OCU |
| `kalyoncu_k2` | 25.457 + 0.877·KL + 0.668·TTR + 0.333·OCU |
| `kalyoncu_k3` | 25.153 + 0.834·KL + 0.686·TTR + 0.226·YCO |
| `kalyoncu_k4` | 43.368 + 1.008·KL + 0.624·OCU |

If a component is `nan`, the formula is `nan`.

## Word and sentence

The **word** is the tool's default word, with one difference: a word with digits is read aloud
and counts as the words of its reading (Kalyoncu p.xiii). `1968` is "bin dokuz yüz altmış
sekiz", 5 words; `%50` is "yüzde elli", 2 words. Abbreviations are not expanded. This rule
applies to the Kalyoncu keys only.

So `kalyoncu_ocu` can differ from the tool's `sent_len_mean`:

| Text | `sent_len_mean` | `kalyoncu_ocu` |
|---|---|---|
| `Bu bir tümce. 1999. Bitti.` | 5 / 2 = 2.5 | 9 / 2 = 4.5 |

The **sentence** is the tool's default sentence ([Concepts](concepts.md#sentence)); a sentence
without a letter is not counted. Kalyoncu splits sentences by meaning: sentences with their own
meaning inside quotation marks or as an aside, and statements and explanations after a colon,
are separate sentences (p.xii). This rule is **not applied**; meaning cannot be checked
automatically. On TOMA's 57 texts the tool's sentence rule differs from the expert's count by 41
sentences in total (about 2%) and matches exactly in 37 texts.

The **stem** is Zeyrek's lemma plus derivational suffixes: `kitapçılar` → `kitapçı`,
`öğretmenliği` → `öğretmenlik`. Nothing is added to the stem after the first inflectional
suffix: `oradaki` → `ora`, `karşısındaki` → `karşı`. Causative and passive
suffixes, verbal suffixes, compound-verb suffixes (-ebil, -iver, -eyaz, -akal, -akoy, -adur,
-egel) and the copula are not part of the stem either: `küçültülmek` → `küçül`, `gelebildi` →
`gel`, `evdeydi` → `ev`. If Zeyrek gives several analyses, the choice follows "Choosing the analysis".

## KL: matching against the list

The list is Kalyoncu's familiarity-based word list (Appendix 1, pp.129–160, 4,600 words). A word
is **in the list** if one of three forms is: the word itself lowercased, its stem, or, for a
verb, stem + -mak/-mek. A softened final consonant (`öğretmenliğ`) is also tried hardened.
Circumflexes are removed on both sides: `hikaye` and `hikâye` in a text both match the list
entry. KL looks at familiarity; where the form without a circumflex is another word
(`hala`/`hâlâ`, `dahi`/`dâhi`), both forms are known words, so the result does not change.
Circumflexes are removed in KL only, nowhere else, `kalyoncu_ttr` included.

Kalyoncu's nine rules (p.71–72):

| Rule | In the tool |
|---|---|
| 1. Proper nouns do not count as outside the list | applied: a word tagged `PROPN`, or capitalised and not at the start of a sentence; stays in the denominator, not in the numerator |
| 2. An inflected form counts as the list word | applied: the stem |
| 3. Common derivations do not count as outside the list | **not applied**: which suffixes count as common is not stated |
| 4. List verbs used as verbals | applied: Zeyrek's verbal tags |
| 5. Onomatopoeic words do not count as outside the list | **not applied** |
| 6. Intensified forms (`büsbüyük`) | **not applied** |
| 7. Causative and passive forms | applied: Zeyrek's voice tags |
| 8. A list word used in a rare sense counts as outside the list | **not applied**: needs reading the context |
| 9. Numbers do not count as outside the list | applied: numbers written in digits and in words count as in the list |

### Proper nouns

A proper noun is a word spaCy tags `PROPN`, or a word that starts with a capital letter and is
not at the start of a sentence. Forms with an apostrophe are included (`İstanbul'da`,
`İstanbul’da`). A name at the start of a sentence is a proper noun only if tagged `PROPN`.
Reason: the spaCy Turkish model does not tag `Derya`, `İstanbul'da`, `Almanya'da` or `Hassan'ı`
as `PROPN`, and Turkish spelling capitalises proper nouns. This rule applies in the
`kalyoncu_*` keys only.

### Numbers written in words

Kalyoncu's rule 9 does not tell digits from words (p.72). `iki`, `otuz` and `dokuz` are in the
list too, and so are their inflected (`ikisi`), ordinal (`üçüncü`) and distributive (`beşer`)
forms. A word is a number if:

- spaCy tagged it `NUM`;
- the root of the selected Zeyrek analysis is a number (`Num`);
- spaCy tagged it noun, adjective, adverb or `X`, and the root of one of its Zeyrek analyses is
  a number (spaCy can tag `beşer` as a noun).

A pronoun, verb or proper-noun tag decides: `onun` and `ona` are not "on". A number word counts
as a word in the word count and in TTR like any other word.

### Choosing the analysis

Zeyrek can give several analyses for a word. In the `kalyoncu_*` keys the first analysis whose
type matches spaCy's word class is taken: `PRON` pronoun, `NOUN` and `PROPN` noun, `VERB` and
`AUX` verb, `ADJ` adjective, `ADV` adverb, `NUM` number. If none matches, the first analysis is
taken. The stem, the verbal and the complex-sentence counts (TTR, KCO, YCO) come from the
selected analysis. Example: for `onun` spaCy says `PRON`, so the pronoun analysis is taken, not
Zeyrek's first one, the verb "onmak". The rest of the tool keeps the "first analysis" rule.

## Verbals and complex sentences

A **verbal** is a word whose Zeyrek analysis has an infinitive (-mak, -ma, -ış), participle
(-an, -dık, -acak, -mış, -ar/-maz) or converb (-ip, -arak, -ınca, -ken, -madan, -dıkça…) tag.
The -ken of a noun with the copula (`öğrenciyken`) does not count. A word counts as one verbal
at most.

A **complex sentence** (KCO) has at least one verbal or at least two verbs. Kalyoncu defines it
as a sentence "with more than one judgement, containing a verbal, or joined to another" (p.73).
He does not define "judgement", but in his CYargı variable he measures it by counting verbs and
verbals (p.73); the tool counts it the same way. A verb is a word whose last type in Zeyrek's
analysis is `Verb` (`evdeydi` included). Most sentences joined by a conjunction contain two verbs
and are caught; nominal sentences without a copula (`Hava güzel ama soğuk.`) are not.

## Grade levels

The tool gives the number only. Kalyoncu's grade-level tables (p.102–105):

| Level | K1 | K2 | K3 | K4 |
|---|---|---|---|---|
| Before grade 3 | <30 | <35 | <35 | <40 |
| Grades 3–4 | 30–40 | 35–45 | 35–45 | 40–50 |
| Grades 5–6 | 40–50 | 45–55 | 45–55 | 50–55 |
| Grades 7–8 | 50–60 | 55–60 | 55–60 | 55–59 |
| Grades 9–10 | 60–70 | 60–64 | 60–65 | 59–65 |
| Grades 11–12 | 70–76 | 64–70 | 65–70 | 65–72 |
| Undergraduate | 76–85 | 70–85 | 70–85 | 72–85 |
| Postgraduate | >85 | >85 | >85 | >85 |

The text and the tables of the source differ in four places; the values come from the tables:

- K1: the text says "70–75 grades 11–12, 76–85 undergraduate", the table says "70–76".
- K4: the text says "50–59" for grades 7–8, the table says "55–59".
- Which range a boundary value belongs to is not stated; the text says "30 and below", the
  table "<30".
- The text refers to the tables as 37–40; their captions say 36–39.

## Differences from TOMA

TOMA (Kalyoncu et al. 2026) is a desktop program that computes K1–K4 automatically.

- TOMA also removes circumflexes in KL (p.298); here the two agree.
- TOMA leaves words made only of digits out of KL (p.298). The tool reads them aloud and counts
  them as in the list; it counts numbers written in words as in the list too.
- TOMA computes KCO and YCO with Stanza dependency parsing; the tool uses Zeyrek.
- TOMA does not say which tool splits sentences for the main counts.

## Limitations

These values approximate Kalyoncu's hand counts.

- KL rests on expert judgement: rules 3, 5 and 8 are not applied. KL is therefore not expected
  to match the expert values exactly; the tool counts more words as outside the list than the
  expert does.
- Proper nouns follow the capital letter: a name at the start of a sentence that is not tagged
  `PROPN` can count as outside the list; any other capitalised word in mid-sentence (a title,
  an emphasis) counts as a proper noun.
- Suffixes Zeyrek does not know (-alı, -ası, -casına, -maksızın) cannot be counted as verbals.
- If the selected Zeyrek analysis is wrong, so is the result (the first one when none matches
  spaCy's class): `okuma` is analysed as "ok-um-a", not
  as an infinitive; the participle in `okunur kitap` counts as a finite verb.
- For a word Zeyrek cannot analyse, the stem is the word itself lowercased; foreign words and
  misspellings count as a separate stem in each form.
- KCO is the least exact component. In TOMA too, KCO is the variable furthest from the expert
  values (Kalyoncu et al. 2026).

## The list

The list is in `turkish_linguistic_features/data/kalyoncu_2025_ek1.txt`, in Kalyoncu's order
and spelling (circumflexes included). **It is not covered by the package's MIT licence**; its
rights belong to its author. The PDF's text layer corrupts ğ, ş, ı and initial İ/Ş, so every
entry was checked against the page image. The source spells "Çita" with a dotted i, and it was
left so. The file was compared again, entry by entry and in order, with Appendix 1 of
Kalyoncu's thesis: all 4,600 entries are the same; the only difference is that the source's
"Kılmak(Namaz)" is written "kılmak" (noted at the top of the file).
