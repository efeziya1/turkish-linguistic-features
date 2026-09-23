def test_paket_import_edilebilir():
    import turkish_linguistic_features
    assert turkish_linguistic_features.__version__


def test_zorunlu_bagimliliklar_kurulu():
    """K1: numpy, spaCy, zeyrek ve textstat zorunlu — dördü de import edilebilmeli."""
    import numpy
    import spacy
    import textstat
    import zeyrek
    assert numpy.__version__ and spacy.__version__
    assert zeyrek is not None and textstat is not None


def test_import_dil_modeli_gerektirmez():
    """K1: import zinciri modele bağımlı olmamalı.

    Model indirmek 50 MB ve dakikalar sürüyor. `import turkish_linguistic_features`
    bunu beklememeli — model ilk `analyze()` çağrısında yüklenir.
    Alt süreçte çalıştırılıyor ki bu süreçte önbelleğe alınmış bir model
    sonucu gizlemesin.
    """
    import subprocess
    import sys
    kod = "import turkish_linguistic_features; print(turkish_linguistic_features.__version__)"
    sonuc = subprocess.run([sys.executable, "-c", kod],
                           capture_output=True, text=True)
    assert sonuc.returncode == 0, sonuc.stderr
