"""turkish_linguistic_features — Türkçe ve İngilizce nicel dilsel öznitelik çıkarımı."""

from ._analyze import analyze, ngram_matches
from ._corpus import analyze_corpus
from ._warnings import MissingDependencyWarning, ParagraphStructureWarning
from .exceptions import LinguisticFeaturesError, ModelNotFoundError
from .features import describe_feature
from .file_loader import save_csv, segment_text
from .params import FeatureParams

__version__ = "0.3.0"

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
