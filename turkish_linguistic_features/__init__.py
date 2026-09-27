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
# Yalnızca İngilizce çalışan ve import süresine duyarlı kullanıcı için kaçış:
# LINGUISTIC_FEATURES_NO_ZEYREK_WARMUP=1 — README'de değil, yalnız
# docs/limitations.md'nin sorun giderme bölümünde anılır.
import os as _os

if not _os.environ.get("LINGUISTIC_FEATURES_NO_ZEYREK_WARMUP"):
    from .pipeline.zeyrek_backend import ZeyrekBackend as _ZB

    _ZB()._ensure_loaded()
# --------------------------------------------------------------------------

from ._analyze import analyze
from ._corpus import analyze_corpus
from ._warnings import MissingDependencyWarning, ParagraphStructureWarning
from .exceptions import LinguisticFeaturesError, ModelNotFoundError
from .features import describe_feature
from .file_loader import save_csv, segment_text
from .params import FeatureParams

__version__ = "0.1.0"

# API-SOZLESMESI.md §1 — on adın hepsi burada (T27 ile tamamlandı; ParagraphStructureWarning sonradan eklendi).
__all__ = [
    # Analiz
    "analyze",
    "analyze_corpus",
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
