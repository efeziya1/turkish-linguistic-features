# Bir özniteliğin kaynağını bul

Bir sayıyı çalışmanızda kullanacaksanız nereden geldiğini yazmanız gerekir.
Kütüphane bunu size hazır verir.

## `describe_feature`

```python
import json
import turkish_linguistic_features as tlf

print(json.dumps(tlf.describe_feature("mattr"), ensure_ascii=False, indent=2))
```

```json
{
  "key": "mattr",
  "group": "lexical",
  "group_label": "Lexical richness & frequency",
  "description": "moving-average TTR",
  "formula": "mean TTR of every sliding window of mattr_window words",
  "scale": "ratio_0_1",
  "inputs": ["surface_tokens", "lemma_tokens", "pos_data"],
  "params": ["mattr_window"],
  "requires": "at least 100 words (2 x mattr_window)",
  "citation": "Covington & McFall (2010); default window 50 — C&M recommend a window of 500; 50 is used here so that texts of 100+ words can be measured (mattr needs 2 × window)",
  "references": [
    "Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot: The moving-average type–token ratio (MATTR). Journal of Quantitative Linguistics, 17(2), 94–100. DOI 10.1080/09296171003643098"
  ],
  "definitions": {
    "word": {"name": "space_unit", "source": "tlf", "description": "Whitespace-separated piece of the raw text with edge punctuation stripped, containing a letter or digit; the library's default word."},
    "type": {"name": "lowercase_surface", "source": "tlf", "description": "The word string lowercased by language (Turkish I→ı, İ→i); inflected forms are separate types."}
  }
}
```

## Alanlar ne işe yarar

| Alan | Ne için |
|---|---|
| `description` | Bir cümlelik tanım |
| `formula` | Hesabın kendisi, sözel |
| `scale` | Ölçek: `ratio_0_1`, `score`, `count`… Grafik eksenini buna göre kurun |
| `inputs` | Hangi ön işleme adımına ihtiyaç duyduğu |
| `params` | Hangi `FeatureParams` alanının onu etkilediği |
| `requires` | Sayı üretmesi için gereken en az veri; sağlanmazsa `nan` |
| `citation` | **Kısa işaretçi** — yöntem bölümünde parantez içi |
| `references` | **Tam bibliyografik kayıt** — kaynakçaya kopyalanacak olan |
| `definitions` | `formula`daki terimlerin ne demek olduğu ve tanımın nereden geldiği: her terim için `{"name", "source" (kuralı kim koyuyor: tlf, spacy, zeyrek, textstat, wordfreq), "description" (tek cümle: nasıl sayıldığı)}`; yalnız o formülün kullandığı terimler; dile göre değişen terimde (`syllable`) `describe_feature(key, lang="tr")` dili seçer |

## Künye ne bilmediğimizi de söyler

Yukarıdaki örnekte künye şunu yazıyor:

> default window 50 — C&M recommend a window of 500; 50 is used here so
> that texts of 100+ words can be measured (mattr needs 2 × window)

Yani: yöntem Covington & McFall'ın, **ama varsayılan pencere boyu onlardan
gelmiyor.** Bu ayrımı künyeden okuyabilmeniz kasıtlıdır. Bir sayıyı
kaynağa dayanıyormuş gibi göstermek, kaynağı hiç vermemekten kötüdür.

Aynı kalıbın başka biçimleri:

- `"Herdan (1960/1964), as cited in Tweedie & Baayen (1998) p.327, eq. (5)"`
  — **birincil kaynağa ulaşılamadı**, formül aktaran kaynaktan alındı.
  148 künyenin **14'ü** böyledir ve hepsi `as cited in` ile işaretlidir.
- `"McLaughlin (1969) p.641; polysyllabic = 3+ syllables — the ratio form of
  SMOG's input, not the source's own measure"` — ölçü kaynaktan türetilmiş
  ama kaynağın kendi ölçüsü değil.

## Kaynağı olmayan öznitelikler

```python
tlf.describe_feature("punc_,_ratio")
```

```json
{
  "key": "punc_,_ratio",
  "group": "punctuation",
  "description": "comma marks per word",
  "formula": "marks / words",
  "citation": null,
  "references": []
}
```

`citation` `None` ise o anahtar **adlandırılmış bir literatür ölçüsü
değildir,** saf bir tanımdır: `punc_,_ratio` ("virgül / kelime"),
`char_a` ("a harfinin payı"), `avg_sent_len_word` ("cümle başına kelime").
Bir dış etiket şemasının kategorisini sayan anahtarların künyesi ise `None`
değildir, şemayı gösterir (`morph_case_loc` → UD; `case_loc_ratio` →
Zeyrek).

Türkçedeki 212 anahtarın **68'inin** künyesi yoktur: 29'u harf sıklık
vektörü (Türkçe alfabenin her harfi için bir anahtar), 17'si noktalama
oranı, 22'si uzunluk ve dağılım gibi başka saf tanımlar.

## Yöntem bölümüne yazarken

```python
oz = tlf.analyze(metin, lang="tr")
kullandiklarim = ["mattr", "atesman", "avg_sent_len_word"]

kaynaklar = set()
for k in kullandiklarim:
    kaynaklar.update(tlf.describe_feature(k)["references"])

for r in sorted(kaynaklar):
    print(r)
```

Bu size yalnız **kullandığınız** özniteliklerin kaynakçasını verir — 50
eserin tamamını değil.

## Sayı gerçekten tutuyor mu

Künye kaynağı söyler; **tuttuğunu** söylemez. Onun için ayrı bir belge var:

- **[Doğrulama raporu](../../dogrulama-raporu.md)** — her öznitelik için,
  kaynağın yayımladığı sayıyla karşılaştırma.
- Nasıl okunacağı: **[Doğrulama sistemi](../aciklama/dogrulama.md)**.
