"""Korpus yükleme, parçalama ve CSV yazma (T27).

``_load_corpus`` klasördeki ya da CSV'deki metinleri okur, ``segment_text``
onları eşit büyüklükte parçalara böler. Parçalama **çıkarımdan ayrıdır**:
kayıtlara öznitelik iliştirilmez (K10); birleştirme ``_corpus.py``'de,
``analyze_corpus`` içinde olur.

``_load_corpus`` 2026-09-23'te public yüzeyden çıktı (alt çizgi aldı). Tek
başına çağrılınca "elimde kayıt listesi var, şimdi ne yapacağım?" sorusunu
bırakıyordu; ``analyze_corpus`` zinciri kapatıyor. Kod ve testleri duruyor —
üç dosya düzeni algılaması ve CSV başlık eşlemesi hâlâ çalışıyor.

Her parça bir **etiket** taşır. Etiketin ne anlama geldiğine kullanıcı karar
verir — kaynak, dönem, tür, yazar, dil seviyesi. Kütüphane yorumlamaz.
"""

from __future__ import annotations

import csv
from pathlib import Path

from .alfabe import _ALFABE
from .exceptions import LinguisticFeaturesError
from .features.readability import word_units

__all__ = ["segment_text", "save_csv"]

_LABEL_KEYS = ("label", "Label", "etiket", "Etiket", "ETIKET",
               "author", "Author", "yazar", "Yazar", "kategori", "category")
_TEXT_KEYS = ("text", "Text", "metin", "Metin", "METIN", "content")
_TITLE_KEYS = ("source", "Source", "kaynak", "Kaynak", "başlık",
               "title", "book", "file")


def segment_text(text: str, size: int = 1000, min_fill: float = 1.0,
                 unit: str = "word", lang: str = "tr") -> list[str]:
    """Metni sabit büyüklükte parçalara böler.

    ``unit="word"`` kütüphanenin **varsayılan kelimesini** sayar (2026-10-08,
    Efe): boşlukla ayrılan, kenar noktalaması atılan, harf ya da rakam içeren
    birim (``readability.word_units``). ``analyze`` aynı kelimeyi saydığı için
    ``size=1000`` parça ``analyze``'da tam 1000 kelime eder. Önceden spaCy tokenı
    sayılıyordu; noktalama da token olduğundan 100 token ~83 kelime ediyordu.

    Parça, ilk kelimesinin boşluk biriminin başından son kelimesininkinin sonuna
    kadar **ham metin dilimidir**; kenar noktalaması ve aradaki satır sonları
    olduğu gibi kalır.

    Parameters
    ----------
    text
        Bölünecek metin.
    size
        Parça başına kelime (``unit="word"``) ya da karakter (``"char"``).
    min_fill
        Son parça bu orandan az doluysa atılır. ``1.0`` (varsayılan) yalnız
        tam parçaları tutar; ``0.5`` yarım dolu son parçayı da tutar.

        Sözcüksel zenginlik öznitelikleri metin uzunluğuna duyarlıdır. 1000
        kelimelik parçalarla 50 kelimelik bir artığı aynı tabloda toplarsanız
        ölçtüğünüz fark metin değil parça uzunluğu olur.
    unit
        ``"word"`` ya da ``"char"``.
    lang
        Metnin dili. Kelime kuralı dile göre küçük farklar taşır (Türkçede
        ``3.`` sıra sayısı tek kelimedir).

    Returns
    -------
    list[str]
        Parçalar. Hiçbiri ``min_fill`` eşiğinin altında değildir.
    """
    if unit not in ("word", "char"):
        raise ValueError(f"unit must be 'word' or 'char', not {unit!r}")
    if size <= 0:
        raise ValueError(f"size must be positive: {size}")
    if lang not in _ALFABE:
        raise ValueError(f"Unsupported language: {lang!r}. Expected one of: {sorted(_ALFABE)}")

    if unit == "char":
        parcalar = [(text[i:i + size], len(text[i:i + size]))
                    for i in range(0, len(text), size)]
    else:
        kelimeler = [(bas, son) for _, kelime_mi, bas, son in word_units(text, lang) if kelime_mi]
        parcalar = []
        for i in range(0, len(kelimeler), size):
            kume = kelimeler[i:i + size]
            parcalar.append((text[kume[0][0]:kume[-1][1]], len(kume)))

    esik = size * min_fill
    return [metin for metin, n in parcalar if n >= esik and metin.strip()]


# Girdi UTF-8 olmalı. `utf-8-sig` baştaki BOM'u atar (Not Defteri ve Excel
# ekler); yoksa BOM ilk kelimeye ya da ilk CSV başlığına yapışırdı. BOM'suz
# UTF-8 dosyada `utf-8` ile birebir aynı sonucu verir.
_KODLAMA = "utf-8-sig"


def _kodlama_hatasi(hatalar: list[tuple[Path, UnicodeDecodeError]]) -> LinguisticFeaturesError:
    """Okunamayan dosyaların HEPSİNİ tek mesajda listeler — kullanıcı birini
    düzeltip yeniden çalıştırınca bir sonrakine takılmasın."""
    liste = "\n".join(f"  {yol} (byte {h.start})" for yol, h in hatalar)
    return LinguisticFeaturesError(
        f"{len(hatalar)} file(s) are not valid UTF-8:\n{liste}\n"
        "Re-save them as UTF-8 (in most editors: Save As -> Encoding: UTF-8)."
    )


def _csv_kayitlari(yol: Path) -> list[tuple[str, str, str]]:
    """CSV/TSV'den ``(etiket, kaynak, metin)`` üçlüleri."""
    ayirac = "\t" if yol.suffix.lower() == ".tsv" else ","
    try:
        with yol.open(encoding=_KODLAMA, newline="") as f:
            satirlar = list(csv.DictReader(f, delimiter=ayirac))
    except UnicodeDecodeError as h:
        raise _kodlama_hatasi([(yol, h)]) from h
    if not satirlar:
        return []

    def bul(adaylar: tuple[str, ...]) -> str | None:
        return next((a for a in adaylar if a in satirlar[0]), None)

    metin_sutunu = bul(_TEXT_KEYS)
    if metin_sutunu is None:
        raise ValueError(
            f"{yol.name}: no text column found. Expected one of these headers: "
            f"{list(_TEXT_KEYS)}"
        )
    etiket_sutunu = bul(_LABEL_KEYS)
    kaynak_sutunu = bul(_TITLE_KEYS)
    out = []
    for satir in satirlar:
        etiket = (satir.get(etiket_sutunu) or "") if etiket_sutunu else ""
        kaynak = (satir.get(kaynak_sutunu) or "") if kaynak_sutunu else yol.stem
        out.append((etiket, kaynak, satir[metin_sutunu] or ""))
    return out


def _klasor_kayitlari(kok: Path) -> list[tuple[str, str, str]]:
    """Klasörden ``(etiket, kaynak, metin)`` — iki düzen otomatik algılanır.

    Okunamayan dosyada durmaz: hepsini dener, bozukları toplar ve sonunda tek
    hata verir. Bozuk dosyayı atlayıp sürmek korpusu sessizce eksiltirdi.
    """
    out: list[tuple[str, str, str]] = []
    hatalar: list[tuple[Path, UnicodeDecodeError]] = []

    def oku(dosya: Path) -> str:
        try:
            return dosya.read_text(encoding=_KODLAMA)
        except UnicodeDecodeError as h:
            hatalar.append((dosya, h))
            return ""

    # Düzen 2: etiket alt klasörü
    for alt in sorted(p for p in kok.iterdir() if p.is_dir()):
        for dosya in sorted(alt.glob("*.txt")):
            out.append((alt.name, dosya.stem, oku(dosya)))
    # Düzen 1: düz dosya, "Etiket_Başlık.txt"
    for dosya in sorted(kok.glob("*.txt")):
        etiket, _, baslik = dosya.stem.partition("_")
        # Alt çizgi yoksa etiket bilgisi yok demektir; uydurmuyoruz.
        out.append((etiket if baslik else "", baslik or dosya.stem, oku(dosya)))
    if hatalar:
        raise _kodlama_hatasi(hatalar) from hatalar[0][1]
    return out


def _load_corpus(path: str | Path, segment_size: int | None = None,
                 min_fill: float = 1.0, unit: str = "word",
                 lang: str = "tr") -> list[dict[str, object]]:
    """Klasördeki ya da CSV'deki metinleri okur, istenirse parçalara böler.

    ``segment_size=None`` (varsayılan) **bölmez**: her kaynak dosya tek kayıt
    olur, ``segment_id`` her zaman ``0``. 2026-09-23'e kadar varsayılan
    ``1000``'di ve bu sessiz veri kaybına yol açıyordu — ``min_fill=1.0``
    ile 1500 kelimelik dosyanın son 500 kelimesi atılıyor, 1000'den kısa
    dosya ise hiç kayıt üretmiyordu. Parçalama artık açıkça istenmeli.

    Üç düzen otomatik algılanır::

        korpus/Etiket_Başlık.txt      düz dosya
        korpus/Etiket/dosya.txt       etiket alt klasörü
        korpus.csv                    etiket + metin sütunu

    CSV başlıkları Türkçe ve İngilizce kabul edilir (``etiket``/``label``,
    ``metin``/``text``…). Geriye dönük uyumluluk için ``yazar``/``author`` da
    etikete haritalanır, ama dönen kayıtta anahtar **her zaman** ``label``.

    Parameters
    ----------
    segment_size
        ``None`` ise bölme yok, dosya başına tek kayıt. Sayı verilirse parça
        başına token (``unit="word"``) ya da karakter (``"char"``).
    min_fill, unit
        Yalnız ``segment_size`` verildiğinde anlamlı; ``None`` iken yok
        sayılır. Ayrıntı → ``segment_text``.

    Returns
    -------
    list[dict]
        ``{"label": ..., "source": ..., "segment_id": ..., "text": ...}``

    Notes
    -----
    Parçalama **kaynak başına** yapılır: dosyalar birbirine eklenmez, her
    dosya kendi ``segment_id`` sayacıyla sıfırdan başlar. A dosyasının artığı
    B'nin başına karışmaz.

    ``max_files`` **yok**: ``Path.iterdir()`` sırası işletim sistemine göre
    değişir, yani iki koşu karşılaştırılamazdı. Deneme koşusu için dilimleyin —
    ``analyze_corpus("korpus/")[:200]``.

    Yalnız ``.txt`` okunur. ``.epub``/``.pdf`` kapsam dışı (2026-08-25);
    kullanıcı metni kendisi çıkarır.
    """
    kok = Path(path)
    if not kok.exists():
        raise FileNotFoundError(f"Path not found: {kok}")

    ham = _csv_kayitlari(kok) if kok.is_file() else _klasor_kayitlari(kok)

    kayitlar: list[dict[str, object]] = []
    for etiket, kaynak, metin in ham:
        if segment_size is None:
            kayitlar.append({"label": etiket, "source": kaynak,
                             "segment_id": 0, "text": metin})
            continue
        parcalar = segment_text(metin, size=segment_size, min_fill=min_fill,
                                unit=unit, lang=lang)
        for i, parca in enumerate(parcalar):
            kayitlar.append({"label": etiket, "source": kaynak,
                             "segment_id": i, "text": parca})
    return kayitlar


def save_csv(records: list[dict[str, object]], output_path: str | Path) -> None:
    """Kayıt listesini UTF-8 CSV olarak yazar.

    ``analyze_corpus()`` zincirinin son halkası::

        rows = analyze_corpus("korpus/")
        save_csv(rows, "sonuc.csv")

    Sütunlar ilk kaydın anahtarlarından alınır. Boş liste hiçbir şey yazmaz.

    ``csv.DictWriter`` etrafında ince bir sarmalayıcı; tek işi kodlamayı ve
    satır sonlarını doğru ayarlamak (K9). 2026-09-23'e kadar adı
    ``records_to_csv``'ydi ve ``__all__``'da değildi — zinciri kapatan adım
    public olmadığı için kullanıcı onu bulamıyordu. ``to_csv`` denmedi:
    pandas'ta o bir metot (``df.to_csv``), serbest fonksiyon olarak özneyi
    kaybeder ve pandas semantiği beklenmesine yol açar.

    Parameters
    ----------
    records
        Yazılacak kayıtlar. Hepsi aynı anahtarlara sahip olmalı.
    output_path
        Hedef dosya. Üst klasörü varsayılmaz, çağıran oluşturur.
    """
    if not records:
        return
    with Path(output_path).open("w", encoding="utf-8", newline="") as f:
        yazici = csv.DictWriter(f, fieldnames=list(records[0]))
        yazici.writeheader()
        yazici.writerows(records)
