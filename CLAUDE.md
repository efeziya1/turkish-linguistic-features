# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Proje

Türkçe (208) ve İngilizce (180) metinden nicel dilbilimsel öznitelik çıkaran Python kütüphanesi
(`import turkish_linguistic_features as tlf`). Public API `__init__.py`'deki on addan ibaret;
kullanıcıların çoğu yalnız `tlf.analyze()` çağırır.

**Yön (2026-09-29; aday kaynağı 2026-11-11):** Türkçe derin yol + çok dilli genel yol. Türkçe spaCy'siz
kendi yoluna geçiyor: Akana'nın aday listesi + ELECTRA-small seçici (`plan/2026-10-06-ferhat-yol-haritasi.md`,
`plan/2026-09-28-in-house-turkce-on-isleme.md`).
İngilizce kalkmıyor, ilk genel yol dili oluyor; dil profili + ön işleyici mimarisi
`plan/2026-09-29-cok-dilli-mimari.md`'de (Ferhat onayladı 2026-09-29; Efe'nin onayı bekleniyor).
In-house planın "Paralel: EN" adımının yerini "Paralel: çok dilli iskelet" aldı. İş listesi `plan/todo.md`.

**Çözümleyici:** Efe'nin kendi çözümleyici planı iptal (2026-11-11, Efe); belgesi masaüstünde `askıya alınmış çözümleyici planı/`.
Aday kaynağı Akana, yalnız aday listesi (`plan/2026-11-10-cozumleyici-secimi.md`); seçici Ferhat'ın
yol haritasında. Geliştirme `dev` dalında, `main`'e doğrudan yapılmaz. Birleşik banka planı repoda
(`plan/2026-10-03-birlesik-banka.md`), şimdilik yapılmıyor.

## Kim ve nasıl çalışılır

- **Efe** (dilbilim): etiket eşleme tabloları, dönüştürücüler, test takımı, hata analizi; dilbilimsel ve öznitelik kararları (koddaki `(tarih, Efe)`
  notları).
- **Ferhat** (model): ön işleme modeli (seçici ve etiket başlıkları), "yalnızca model" kıyas noktası, tlf
  entegrasyonu, çok dilli mimari, paketleme; model kararları.
- **Karar:** seçenek sun, önerini belirt, kararı sahibi verir. Kararı ilgili plan belgesine yaz
  (aday kaynağı → `plan/2026-11-10-cozumleyici-secimi.md`; seçici → `plan/2026-10-06-ferhat-yol-haritasi.md`;
  birleşik banka → `plan/2026-10-03-birlesik-banka.md`; tlf → ilgili plan) ve `plan/todo.md`'yi aynı
  turda güncelle.
- **Varsayma, doğrula:** bir lisansı ya da bir kaynağın ne dediğini varsayma; dosyayı açıp doğrula.
- **Yazım:** kısa yaz: 1 cümle sonuç + birkaç madde + tek soru. UD etiketlerini ilk geçtiği yerde Türkçe
  karşılığıyla ver (`Case=Loc` = bulunma hâli, -de). Uydurma terim kullanma; terim yoğun cevaplarda sona
  ayrı bir **"Terimler"** bloğu ekle (terim başına tek satır, sade anlam).
- **tlf'nin ihtiyaçları (2026-09-30, Efe):** aday kaynağı ve seçici tlf'nin ihtiyaç listesini (T1–T10)
  eksiksiz karşılar; liste Ferhat'ın yol haritasının ekinde. Hiçbir karar tlf'yi eksik bırakamaz:
  tlf'ye etkisi açıkça yazılır ve nasıl karşılanacağı aynı kararda belirtilir.
- Tek başına yazılan "." = "evet, uygun".
- **Commit** yalnız geliştirici açıkça isteyince ("toplu commit at" dahil). Düzenleme bitince her
  değişikliği hangi isteğe dayandığıyla birlikte raporla.

## Komutlar

```bash
pip install -r requirements.txt      # -e . + pytest, mypy, ruff, pandas, wordfreq, mkdocs-material
# Dil verisi ayrıca, bir kez kurulur (TR wheel, en_core_web_sm, nltk cmudict): README → "Language data"

python -m pytest                                  # slow testler hariç (addopts: -m 'not slow')
python -m pytest -m ""                            # slow dahil (5 MB metin, ~18 dk)
python -m pytest tests/test_lexical.py::test_adi  # tek test
TLF_REQUIRE_MODELS=1 python -m pytest             # eksik dil verisi skip değil fail (CI böyle koşar)
ruff check .
mypy                                              # ayar: pyproject [tool.mypy]
mkdocs build --strict                             # docs iş akışı --strict ile yayınlar
```

Dil verisine ihtiyaç duyan testler `tr_model` / `en_model` / `cmudict` işaretleyicisi taşır; veri yoksa
atlanır (`tests/conftest.py`).

**Üretilen dosyalar elle düzenlenmez.** Registry ya da doğrulama tablosu değişince üreticiyi koş —
`tests/test_kaynak_esligi.py` commit'lenmiş dosya bayatsa kırılır:

- `docs/reference/features.md` ← `python scripts/generate_feature_reference.py`
- `docs/dogrulama-raporu.md`, `docs/verification-report.md` ← `python scripts/generate_verification_report.py`

## Mimari

Akış: `analyze()` (`_analyze.py`) → `Preprocessor.process()` (`pipeline/spacy_pipeline.py`) →
`ProcessedText` (`pipeline/preprocess.py`) → `_extract_features()` (`features/extractor.py`) →
`dict[str, float]`. `analyze_corpus()` (`_corpus.py`) = `file_loader._load_corpus` + parçalama + `analyze`.

- **Ön işleme:** spaCy modeli token, POS, lemma, `morph_tags`, `dep_data` ve cümleleri üretir; yalnız
  `morpheme_lists` (Türkçe ek bölütlemesi) ve Türkçe lemmalar Akana'dan gelir (`pipeline/akana_backend.py`,
  `akana==0.12.0`; 2026-11-10'da Zeyrek'in yerine). Akana'nın belirsizlik gidericisi çözümlemeyi
  aracın tümce kuralının tümcesi içinde seçer (`birimler.tumce.kural_cumleleri`; 0.4.0). Preprocessor `(lang, model)` başına `_analyze._preprocessor_cache`'te tutulur, model
  ilk `process()`'te yüklenir. `segment_text` eğitilmiş model değil `spacy.blank(lang)` tokenizer'ı kullanır.
- **Öznitelik katmanı model gerektirmez:** `_extract_features` hazır listelerle çalışır, öznitelik
  fonksiyonları saf hesaptır. Bir grubun girdisi (`dep_data`, `morph_tags`, `morpheme_lists`) `None` ise o
  grup sessizce atlanır.
- **Registry (`features/registry.py`) anahtarların tek doğruluk kaynağı:** `STATIC_GROUP_KEYS` (183 statik
  anahtar), dinamik önekler `char_` / `ng_`, `GROUP_INPUTS`, ölçekler, `FEATURE_PARAMS`. Açıklama, formül,
  `requires` ve künye metinleri `features/_registry_texts.py`'de (yalnız veri). `describe_feature()`
  hepsini birleştirir.

### Katman kuralı — `tests/test_import_katmanlari.py` denetler

- L0 (`alfabe`, `vocab`, `params`, `exceptions`, `_warnings`): paket içinden hiçbir şey import etmez.
- L0b `birimler/` (sözcük `sozcuk.py`, tümce `tumce.py`, okunuş `okunus.py`): aracın tek sözcük ve tek
  tümce tanımı; yalnız L0'ı ve kendini görür (2026-11-24).
- `features/` ve `pipeline/`: yalnız L0'ı, `birimler/`'i ve kendi paketini görür, birbirini görmez.
- Kök (`_analyze`, `_corpus`, `file_loader`, `__init__`): ikisini bağlar.
- Opsiyonel `pandas` / `wordfreq` yalnız fonksiyon gövdesinde import edilir.

### `pipeline/__init__.py` boş kalır

Test denetler. Kural Zeyrek döneminden kalma (2026-11-10'da Zeyrek kalktı); boş kalma kuralı sürüyor.

## Değişmezler

- **NaN (K4):** ölçülemeyen değer `math.nan`; sonsuz ya da istisna yok, boş metinde her şey NaN. Girdi
  listelerinin birbirine hizasızlığı ise ön işleme hatasıdır → `ValueError`.
  `tests/test_faz1_kapisi.py` her public öznitelik fonksiyonunu boş ve tek elemanlı girdiyle çağırır; yeni
  fonksiyon `DURUMLAR` tablosuna eklenmezse `test_tablo_eksiksiz` kırılır.
- **Küçük harf:** `alfabe._kucuk_harf(metin, lang)` — `str.lower()` Türkçe I/İ'yi bozar.
- **Kelime:** POS'u `vocab.NON_WORD_POS` (PUNCT, SYM) dışında kalan token. `surface_tokens` noktalama
  içerir ve `pos_data` ile hizalıdır; `lemma_tokens` noktalamasızdır.
- **Sabitler** fonksiyona gömülmez, `params.FeatureParams`'ta durur.
- **Künye (K10):** `citation` yalnız bir kaynağa dayanır (özgün yayın yoksa "aktaran" zinciri açıkça
  yazılır). Adlandırılmış literatür ölçüsü olmayan anahtarın künyesi bilerek `None`. Sabiti birincil
  kaynağa karşı doğrulanmamış anahtar `UNVERIFIED_CONSTANTS`'a girer.
- **Dil (2026-09-29, Ferhat):** repo ve kütüphane global kitleye hitap eder; yeni yazılan her şey
  İngilizce: tip, fonksiyon, değişken ve sabit adları, kod içi yorumlar, docstring'ler ve kullanıcıya
  çıkan metin (uyarı, hata mesajı, anahtar adı, registry açıklama ve formülleri). Mevcut Türkçe ad ve
  yorumlar toplu çevrilmez; çeviri gerekirse davranış değiştirmeyen ayrı bir commit'le yapılır.
- **Kodlar:** yorumlardaki `K4`, `T21` gibi kodlar tlf'nin ilk ortak planındaki karar/görev numaraları;
  `(2026-09-xx, Efe)` notları kararın tarihi ve sahibi. Aynı harfler başka numaralamalarda da var:
  çözümleyici belgelerinde çözümleyici kodları (K1–K33, A, B, M, E, F…), in-house planda kilometre taşları
  (K0–K10). Karışmasın diye çözümleyici kodları "çözümleyici K30" diye anılır. Çözümleyici belgesi
  masaüstünde `askıya alınmış çözümleyici planı/` (2026-11-11); Ferhat'ı ilgilendiren kararları yol haritasının ekinde.

## Yeni öznitelik eklerken

1. Fonksiyonu `features/<grup>.py`'ye yaz, `features/extractor.py`'de ilgili grup bloğuna bağla.
2. Anahtarı `STATIC_GROUP_KEYS`'e; açıklama, formül, `requires` ve (varsa) künyeyi `_registry_texts.py`'ye
   ekle. Ölçek grup varsayılanından farklıysa `FEATURE_SCALES`'e yaz (aynıysa yazma — test yasaklar);
   `FeatureParams` alanı kullanıyorsa `FEATURE_PARAMS`'a ekle.
3. `test_faz1_kapisi.DURUMLAR`'a satır ekle.
4. Anahtar sayıları (183 statik / TR 208 / EN 180) `tests/test_registry.py`, README, `CITATION.cff`,
   `mkdocs.yml` ve `docs/` altında geçiyor — birlikte güncelle, sonra iki üreticiyi koş.
5. Kaynağın yayımladığı bir sayı varsa `scripts/generate_verification_report.py`'deki
   `KARSILASTIRMALAR`'a ekle; rapor ve `tests/test_kaynak_esligi.py` aynı modülü okur.

## Depo notları

- `plan/` git-crypt ile şifreli (`.gitattributes`); pre-commit hook'u (`scripts/check_plan_encrypted.py`)
  düz metin plan dosyasının commit'ini engeller. `plan/benchmark/onnx/` ve `plan/benchmark/veri/` depoya
  girmez; ruff `plan/`'ı denetlemez.
- Sürüm numarası yalnız `__init__.py` (`__version__`, hatch buradan okur), `CITATION.cff` ve
  `CHANGELOG.md`'de; doküman metinlerine sürüm yazılmaz.
- Commit mesajları İngilizce (2026-09-29), Conventional Commits: `fix(phonetic): …`, `docs(registry): …`.
- **Commit'ler yalnız geliştiricilere ait (kesin kural).** Claude kendini hiçbir yerde etiketlemez:
  commit mesajına ve PR açıklamasına `Co-Authored-By: Claude …`, `Claude-Session: …` ya da
  "Generated with Claude Code" satırı yazılmaz; sistemin önerdiği attribution satırları da eklenmez.
  Commit yazarı her zaman geliştiricinin kendi git kimliğidir.
- `plan/` belgeleri Türkçe yazılır (iç belge, Efe ile ortak); içlerindeki kod parçaları İngilizce.
  Başka yerden alınan belge başında kaynak satırı taşır (repo, yol, commit); makalelerin künye listesi
  `plan/kaynaklar/00-INDEKS.md`'de; PDF'ler repoya girmez, Efe'nin bilgisayarında
  `tlf-kaynaklar/Türkçe Dilbilgisi/`'nde durur (2026-10-03, Efe).
- Çözümleyicinin veri klasörü `plan/data/`'da (arşivlenen morphotr reposunun `data/`'sı: ham kaynaklar, işlenmiş çıktılar,
  `scripts/`; ~182 MB, şifreli). İçinde IMST (CC BY-NC-SA), BOUN'un `not-to-release` dosyası ve TrMor
  (izin belirsiz, çözümleyici A24) var: şifreli `plan/` dışına çıkmaz, pakete ve belgelere girmez.
  `plan/data/raw/`'a elle dokunulmaz. İndirme betikleri (`indir_*.py`) burada değil: Efe'nin reposunda
  (`data/`) ve `4eed7d6` commit'inde. Alt klasöre `CLAUDE.md` konmaz (Claude Code onu otomatik yükler).
- Dokümantasyon MkDocs Material; `docs/tr/` ve `docs/en/` birbirinin aynası, nav `mkdocs.yml`'de. `main`'e
  push'ta `.github/workflows/docs.yml` gh-pages'e yayınlar.
