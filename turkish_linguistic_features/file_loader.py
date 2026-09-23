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
from typing import TYPE_CHECKING

import spacy

from .alfabe import _ALFABE

if TYPE_CHECKING:
    from spacy.tokenizer import Tokenizer

__all__ = ["segment_text", "save_csv"]

_LABEL_KEYS = ("label", "Label", "etiket", "Etiket", "ETIKET",
               "author", "Author", "yazar", "Yazar", "kategori", "category")
_TEXT_KEYS = ("text", "Text", "metin", "Metin", "METIN", "content")
_TITLE_KEYS = ("source", "Source", "kaynak", "Kaynak", "başlık",
               "title", "book", "file")

# Tokenizer önbelleği. ``spacy.blank(lang)`` kurulu model gerektirmiyor ve
# ölçüldü (2026-09-19): tokenizer'ı eğitilmiş modelinkiyle **birebir aynı**
# sayıyı veriyor. Yani parçalama, ``analyze()``ın sonradan yapacağı
# tokenizasyonla tam uyumlu ama model indirmeye bağlı değil.
_tokenizer_cache: dict[str, Tokenizer] = {}


def _get_tokenizer(lang: str) -> Tokenizer:
    if lang not in _ALFABE:
        raise ValueError(f"Desteklenmeyen dil: {lang!r}. Beklenen: {sorted(_ALFABE)}")
    if lang not in _tokenizer_cache:
        _tokenizer_cache[lang] = spacy.blank(lang).tokenizer
    return _tokenizer_cache[lang]


def segment_text(text: str, size: int = 1000, min_fill: float = 1.0,
                 unit: str = "word", lang: str = "tr") -> list[str]:
    r"""Metni sabit büyüklükte parçalara böler.

    🔴 Kelime sınırları **spaCy tokenizer'ı** ile bulunur (2026-09-19, Efe).
    Planın önceki sürümü ``re.finditer(r"\S+")`` diyordu; ölçüldü ve
    araştırma kullanımı için yeterince kesin değil: ``\S+`` ile "tam 1000
    kelime" diye kesilen 40 parça gerçekte **1018-1562** spaCy token çıktı
    (en uzunu en kısadan %53 uzun) ve aynı metinde bu aralıkta TTR **%7,6**
    oynuyor. Yani ``min_fill``'in önlemek için var olduğu uzunluk karışıklığı
    sayım yönteminden giriyordu.

    Maliyet ölçüldü ve önemsiz: 1,2 s/MB, yani ardından gelen ``analyze()``
    çağrılarının %1'i kadar. Cümle sınırında bölmek de denendi ve daha kötü:
    bozuk noktalamalı metinde tek "cümle" 2611 token olabiliyor, parça boyu
    385-2611'e yayılıyor.

    Parça içeriği **ham metin dilimidir**, yeniden birleştirilmiş token
    listesi değil.

    Parameters
    ----------
    text
        Bölünecek metin.
    size
        Parça başına token (``unit="word"``) ya da karakter (``"char"``).
    min_fill
        Son parça bu orandan az doluysa atılır. ``1.0`` (varsayılan) yalnız
        tam parçaları tutar; ``0.5`` yarım dolu son parçayı da tutar.

        Sözcüksel zenginlik öznitelikleri metin uzunluğuna duyarlıdır. 1000
        token'lık parçalarla 50 token'lık bir artığı aynı tabloda toplarsanız
        ölçtüğünüz fark metin değil parça uzunluğu olur.
    unit
        ``"word"`` ya da ``"char"``.
    lang
        Tokenizer dili; yalnız ``unit="word"`` için anlamlı.

        Planın önceki sürümünde bu parametre **yoktu** ve gerekçesi o zaman
        doğruydu: ``\S+`` dilden bağımsızdı, yani ``lang`` hiçbir şey
        yapmıyordu. Artık tokenizer'ı seçiyor, yani gerçek bir iş yapıyor.

    Returns
    -------
    list[str]
        Parçalar. Hiçbiri ``min_fill`` eşiğinin altında değildir.
    """
    if unit not in ("word", "char"):
        raise ValueError(f"unit 'word' ya da 'char' olmalı, {unit!r} değil")
    if size <= 0:
        raise ValueError(f"size pozitif olmalı: {size}")
    tokenizer = _get_tokenizer(lang)       # geçersiz dil burada patlar

    if unit == "char":
        parcalar = [(text[i:i + size], len(text[i:i + size]))
                    for i in range(0, len(text), size)]
    else:
        doc = tokenizer(text)
        parcalar = [(doc[i:i + size].text, len(doc[i:i + size]))
                    for i in range(0, len(doc), size)]

    esik = size * min_fill
    return [metin for metin, n in parcalar if n >= esik and metin.strip()]


def _csv_kayitlari(yol: Path) -> list[tuple[str, str, str]]:
    """CSV/TSV'den ``(etiket, kaynak, metin)`` üçlüleri."""
    ayirac = "\t" if yol.suffix.lower() == ".tsv" else ","
    with yol.open(encoding="utf-8", newline="") as f:
        satirlar = list(csv.DictReader(f, delimiter=ayirac))
    if not satirlar:
        return []

    def bul(adaylar: tuple[str, ...]) -> str | None:
        return next((a for a in adaylar if a in satirlar[0]), None)

    metin_sutunu = bul(_TEXT_KEYS)
    if metin_sutunu is None:
        raise ValueError(
            f"{yol.name}: metin sütunu bulunamadı. Beklenen başlıklardan biri: "
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
    """Klasörden ``(etiket, kaynak, metin)`` — iki düzen otomatik algılanır."""
    out: list[tuple[str, str, str]] = []
    # Düzen 2: etiket alt klasörü
    for alt in sorted(p for p in kok.iterdir() if p.is_dir()):
        for dosya in sorted(alt.glob("*.txt")):
            out.append((alt.name, dosya.stem, dosya.read_text(encoding="utf-8")))
    # Düzen 1: düz dosya, "Etiket_Başlık.txt"
    for dosya in sorted(kok.glob("*.txt")):
        etiket, _, baslik = dosya.stem.partition("_")
        # Alt çizgi yoksa etiket bilgisi yok demektir; uydurmuyoruz.
        out.append((etiket if baslik else "", baslik or dosya.stem,
                    dosya.read_text(encoding="utf-8")))
    return out


def _load_corpus(path: str | Path, segment_size: int = 1000,
                min_fill: float = 1.0, unit: str = "word",
                lang: str = "tr") -> list[dict[str, object]]:
    """Klasördeki ya da CSV'deki metinleri okuyup parçalara böler.

    Üç düzen otomatik algılanır::

        korpus/Etiket_Başlık.txt      düz dosya
        korpus/Etiket/dosya.txt       etiket alt klasörü
        korpus.csv                    etiket + metin sütunu

    CSV başlıkları Türkçe ve İngilizce kabul edilir (``etiket``/``label``,
    ``metin``/``text``…). Geriye dönük uyumluluk için ``yazar``/``author`` da
    etikete haritalanır, ama dönen kayıtta anahtar **her zaman** ``label``.

    Returns
    -------
    list[dict]
        ``{"label": ..., "source": ..., "segment_id": ..., "text": ...}``

    Notes
    -----
    ``max_files`` **yok**: ``Path.iterdir()`` sırası işletim sistemine göre
    değişir, yani iki koşu karşılaştırılamazdı. Deneme koşusu için dilimleyin —
    ``analyze_corpus("korpus/")[:200]``.

    Yalnız ``.txt`` okunur. ``.epub``/``.pdf`` kapsam dışı (2026-08-25);
    kullanıcı metni kendisi çıkarır.
    """
    kok = Path(path)
    if not kok.exists():
        raise FileNotFoundError(f"Yol bulunamadı: {kok}")

    ham = _csv_kayitlari(kok) if kok.is_file() else _klasor_kayitlari(kok)

    kayitlar: list[dict[str, object]] = []
    for etiket, kaynak, metin in ham:
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
