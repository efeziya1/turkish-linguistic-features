"""turkish_linguistic_features — Türkçe ve İngilizce nicel dilsel öznitelik çıkarımı."""
# --- BU BLOK DOSYANIN İLK KODU OLMALI -------------------------------------
# Windows'ta spaCy'nin native uzantıları Zeyrek'inkinden önce yüklenirse
# paylaşılan durum bozuluyor ve ilgisiz çağrılar traceback'siz çöküyor.
# Aşağıdaki 'from .x import y' satırları spaCy'yi çekiyor, bu yüzden ısınma
# onlardan ÖNCE gelmek zorunda.
#
# `zeyrek` zorunlu bağımlılık (K1) olduğu için bu blok KOŞULSUZ çalışır —
# try/except ImportError YOK. Opsiyonelken blok sessizce atlanabiliyordu ve
# atlandığında yükleme sırası garantisi de kayboluyordu; yani koruma, tam
# ihtiyaç duyulan senaryoda devre dışı kalıyordu.
#
# Blok ayrıca zeyrek#42 yamasını yükler (bkz. pipeline/zeyrek_backend.py).
#
# No opt-out: skipping the warm-up and later analysing Turkish in the same
# process can crash on Windows (2026-10-01, Efe). The block goes away together
# with Zeyrek (multilingual plan, step 9).
from .pipeline.zeyrek_backend import ZeyrekBackend as _ZB

_ZB()._ensure_loaded()
# --------------------------------------------------------------------------

from ._analyze import analyze, ngram_matches
from ._corpus import analyze_corpus
from ._warnings import MissingDependencyWarning, ParagraphStructureWarning
from .exceptions import LinguisticFeaturesError, ModelNotFoundError
from .features import describe_feature
from .file_loader import save_csv, segment_text
from .params import FeatureParams

__version__ = "0.1.0"

# Genel API — on bir adın hepsi burada.
__all__ = [
    # Analiz
    "analyze",
    "analyze_corpus",
    "ngram_matches",
    # Yapılandırma
    "FeatureParams",
    # Korpus
    "segment_text",
    "save_csv",
    # Keşif
    "describe_feature",
    # Hatalar
    "LinguisticFeaturesError",
    "ModelNotFoundError",
    "MissingDependencyWarning",
    "ParagraphStructureWarning",
]
