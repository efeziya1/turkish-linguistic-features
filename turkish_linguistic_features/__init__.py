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

__version__ = "0.1.0"
__all__: list[str] = []
