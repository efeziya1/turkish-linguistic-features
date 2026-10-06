"""tests/veri/zeyrek/golden.json dosyasını üretir: Zeyrek'in sözcük başına çözümleme listesi.

Sözcükler ``tests/veri/zeyrek/sozcukler.txt``'ten. Her sözcük için Zeyrek'in döndürdüğü
çözümlemeler **sırasıyla** yazılır; tlf ilkini aldığı için sıra da sonucun parçası.
``tests/test_zeyrek.py::test_golden_set`` bu dosyayla karşılaştırır.

Kullanım::

    python scripts/generate_zeyrek_golden.py

Bu dosya elle DÜZENLENMEZ. Yeniden üretmek ancak Zeyrek ya da tlf'nin Zeyrek katmanı bilerek
değiştiğinde yapılır; farkı commit mesajında açıklayın.
"""
from __future__ import annotations

import json
from pathlib import Path

from turkish_linguistic_features.pipeline.zeyrek_backend import ZeyrekBackend

KLASOR = Path(__file__).resolve().parents[1] / "tests" / "veri" / "zeyrek"


def sozcukler() -> list[str]:
    """Liste dosyasındaki sözcükler, yorum ve tekrar atılmış, dosyadaki sırayla."""
    satirlar = (KLASOR / "sozcukler.txt").read_text(encoding="utf-8").splitlines()
    return list(dict.fromkeys(s.strip() for s in satirlar if s.strip() and not s.startswith("#")))


def cozumlemeler(backend: ZeyrekBackend, sozcuk: str) -> list[str]:
    """Zeyrek'in çözümlemeleri sırasıyla: ``sözlük_girdisi|Etiket:yüzey+Etiket:yüzey``."""
    backend._ensure_loaded()
    assert backend._analyzer is not None
    return [f"{c.dict_item.id_}|" + "+".join(f"{m.id_}:{y}" for m, y in c.morphemes)
            for c in backend._analyzer._parse(sozcuk)]


def uret() -> dict[str, list[str]]:
    backend = ZeyrekBackend()
    return {s: cozumlemeler(backend, s) for s in sozcukler()}


if __name__ == "__main__":
    hedef = KLASOR / "golden.json"
    hedef.write_text(json.dumps(uret(), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Yazildi: {hedef}")
