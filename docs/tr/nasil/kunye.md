# Bir özniteliğin kaynağını bul

Bir sayıyı çalışmanızda kullanacaksanız nereden geldiğini yazmanız gerekir.
Araç bunu size hazır verir: Her özniteliğin tanımı, formülü ve künyesi (İng. *citation*)
öznitelik dizininde (İng. *registry*) durur, `describe_feature` onu okur.

## `describe_feature`

```python
tlf.describe_feature("mattr")
```

```text
{'key': 'mattr',
 'group': 'lexical',
 'group_label': 'Lexical richness & frequency',
 'description': 'moving-average TTR',
 'formula': 'mean TTR of every sliding window of mattr_window words',
 'scale': 'ratio_0_1',
 'inputs': ('raw_text',),
 'params': ('mattr_window',),
 'requires': 'at least 100 words (2 x mattr_window)',
 'citation': 'Covington & McFall (2010); default window 50 — C&M recommend a window of '
             '500 (p.97); 50 is used here so that texts of 100+ words can be measured '
             '(mattr needs 2 × window)',
 'references': ('Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot: '
                'The moving-average type–token ratio (MATTR). Journal of Quantitative '
                'Linguistics, 17(2), 94–100. DOI 10.1080/09296171003643098',),
 'definitions': {'word': {'name': 'space_unit',
                          'source': 'tlf',
                          'description': 'Whitespace-separated piece of the raw text '
                                         'with edge punctuation stripped, containing a '
                                         "letter or digit; the library's default "
                                         'word.'},
                 'type': {'name': 'lowercase_surface',
                          'source': 'tlf',
                          'description': 'The word string lowercased by language '
                                         '(Turkish I→ı, İ→i); inflected forms are '
                                         'separate types.'}}}
```

## Alanlar ne işe yarar

| Alan | Ne için |
|---|---|
| `description` | Bir tümcelik tanım |
| `formula` | Hesabın kendisi, sözel |
| `scale` | Ölçek: `ratio_0_1`, `score`, `count`… |
| `inputs` | Hangi ön işleme adımına ihtiyaç duyduğu |
| `params` | Hangi `FeatureParams` alanının onu etkilediği |
| `requires` | Sayı üretmesi için gereken en az veri; sağlanmazsa `nan` |
| `citation` | **Künye**: kısa kaynak gösterimi, yöntem bölümünde parantez içinde verilen |
| `references` | **Kaynakça kaydı** (İng. *reference*): eserin tam kaydı, kaynakçaya kopyalanacak olan |
| `definitions` | `formula`daki terimlerin ne demek olduğu ve tanımın nereden geldiği: her terim için `{"name", "source" (kuralı kim koyuyor: tlf, spacy, zeyrek, textstat, wordfreq), "description" (tek tümce: nasıl sayıldığı)}`; yalnız o formülün kullandığı terimler; dile göre değişen terimde (`syllable`, `type`) `describe_feature(key, lang="tr")` dili seçer |

## Künye ne bilmediğimizi de söyler

Yukarıdaki örnekte künye şunu yazıyor:

> default window 50 — C&M recommend a window of 500 (p.97); 50 is used here so
> that texts of 100+ words can be measured (mattr needs 2 × window)

Yani: yöntem Covington & McFall'ın, **ama varsayılan pencere boyu onlardan
gelmiyor.** Bu ayrımı künyeden okuyabilmeniz kasıtlıdır.

Künye kaynağın yalnız adını değil, formülün kaynakta **nerede** olduğunu da gösterir:
Türkçedeki 203 künyenin 179'u sayfa, tablo, denklem ya da bölüm numarası verir
(`p.97`, `eq. (5)`). Böylece formülü kaynağında bulup aracın uygulamasıyla
karşılaştırabilirsiniz.

Aynı kalıbın başka biçimleri:

- `"Herdan (1960/1964), as cited in Tweedie & Baayen (1998) p.327, eq. (5)"`
  — **birincil kaynağa ulaşılamadı**, formül aktaran kaynaktan (İng. *as cited in*)
  alındı. İki dilde **13** künye böyledir (Türkçede 12; on üçüncüsü yalnız İngilizcede
  hesaplanan LIX) ve hepsi `as cited in` ile işaretlidir.
- `"McLaughlin (1969) p.641; polysyllabic = 3+ syllables — the ratio form of
  SMOG's input, not the source's own measure"` — ölçü kaynaktan türetilmiş
  ama kaynağın kendi ölçüsü değil.

## Kaynağı olmayan öznitelikler

```python
d = tlf.describe_feature("punct_dash_ratio")
d["citation"], d["references"]
```

```text
(None, ())
```

`citation` `None` ise o anahtar **bir alanyazın ölçüsü (İng. *literature measure*)
değildir,** yalın bir tanımdır (İng. *plain definition*): `punct_dash_ratio` ("tire / bütün noktalama işaretleri"),
`uppercase_ratio` ("büyük harfle başlayan sözcüklerin payı"), `lemma_count`
("farklı sözlükbirim sayısı").
Bir dış etiket şemasının kategorisini sayan anahtarların künyesi ise `None`
değildir, şemayı gösterir (`case_loc_ratio` → UD; `zeyrek_case_loc_ratio` →
Zeyrek).

Türkçedeki 214 anahtarın **11'inin** künyesi yoktur.

## Kaynakçayı oluşturmak

```python
kullandiklarim = ["mattr", "atesman", "sent_len_mean"]

kaynaklar = set()
for k in kullandiklarim:
    kaynaklar.update(tlf.describe_feature(k)["references"])

for r in sorted(kaynaklar):
    print(r)
```

Bu size yalnız **kullandığınız** özniteliklerin kaynakçasını verir — 58
eserin tamamını değil.

## Sayı gerçekten tutuyor mu

Künye kaynağı söyler; **tuttuğunu** söylemez. Onun için ayrı bir belge var:

- **[Doğrulama raporu](../../dogrulama-raporu.md)** — her öznitelik için,
  kaynağın yayımladığı sayıyla karşılaştırma.
- Nasıl okunacağı: **[Doğrulama sistemi](../aciklama/dogrulama.md)**.
