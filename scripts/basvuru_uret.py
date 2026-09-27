"""docs/reference/features.md dosyasını üretir.

Kapsam listesi registry'den gelir — elle tutulmaz, yani hiçbir öznitelik
başvurudan kaçamaz. Rapor üreticisiyle (``dogrulama_raporu.py``) aynı
kaynağı okur.

Kullanım::

    python scripts/basvuru_uret.py

Bu dosya elle DÜZENLENMEZ.
"""
from __future__ import annotations

from pathlib import Path

from turkish_linguistic_features.features.registry import (
    DYNAMIC_PREFIXES,
    GROUP_LABELS,
    STATIC_GROUP_KEYS,
    describe_feature,
)
from turkish_linguistic_features.features._registry_texts import BIBLIOGRAPHY

BASLIK = """<!-- GENERATED FILE — do not edit by hand.
     Source: scripts/basvuru_uret.py
     To regenerate:
       python scripts/basvuru_uret.py -->

# Feature reference

Every feature the library can produce, grouped as it is grouped in the code.
This page is **generated from the registry**, so it cannot fall out of step
with what `describe_feature()` returns.

**Reading the columns**

| Column | Meaning |
|---|---|
| Key | The `dict` key `analyze()` returns |
| Description | One-sentence definition |
| Formula | The computation, in words |
| Requires | Minimum data needed; below it the feature returns `nan`. A "word" is any token that is not punctuation or a symbol |
| Source | Short citation. `—` means it is not a named measure from the literature |

Whether a feature's number has been checked against the number its source
published is a separate question — see the
[verification report](../verification-report.md).

"""

# Dinamik grupların temsilci anahtarı (grup düzeyinde metin taşırlar).
DINAMIK_ORNEK = {"chars": "char_a", "custom_ngrams": None}


def _satir(anahtar: str) -> str:
    d = describe_feature(anahtar)
    kunye = d["citation"] or "—"
    return (f"| `{d['key']}` | {d['description']} | `{d['formula']}` "
            f"| {d['requires']} | {kunye} |\n")


def uret() -> str:
    p = [BASLIK]

    p.append("## Groups\n\n| Group | Keys | What it covers |\n|---|---|---|\n")
    for g, etiket in GROUP_LABELS.items():
        n = len(STATIC_GROUP_KEYS.get(g, ()))
        sayi = "dynamic" if g in DYNAMIC_PREFIXES else str(n)
        p.append(f"| `{g}` | {sayi} | {etiket} |\n")
    p.append("\n")

    for g, etiket in GROUP_LABELS.items():
        anahtarlar = STATIC_GROUP_KEYS.get(g, ())
        if g in DYNAMIC_PREFIXES:
            ornek = DINAMIK_ORNEK.get(g)
            onek = DYNAMIC_PREFIXES[g]
            p.append(f"\n## `{g}` — {etiket}\n\n")
            p.append(f"Dynamic group: keys are generated with the prefix "
                     f"`{onek}`. The description, formula and requirement "
                     f"below are stated at the group level, not per key.\n\n")
            if ornek:
                p.append("| Key | Description | Formula | Requires | Source |\n")
                p.append("|---|---|---|---|---|\n")
                p.append(_satir(ornek).replace(f"`{ornek}`",
                                               f"`{onek}…`"))
                p.append("\n")
            else:
                p.append("Created only when you pass `custom_ngrams` to "
                         "`analyze()`.\n\n")
            continue
        if not anahtarlar:
            continue
        p.append(f"\n## `{g}` — {etiket}\n\n")
        p.append(f"{len(anahtarlar)} keys.\n\n")
        p.append("| Key | Description | Formula | Requires | Source |\n")
        p.append("|---|---|---|---|---|\n")
        for k in anahtarlar:
            p.append(_satir(k))

    p.append("\n## Bibliography\n\n")
    p.append(f"{len(BIBLIOGRAPHY)} works. Every citation above names at "
             "least one of these verbatim, and every entry here is named by "
             "at least one citation — both directions are tested.\n\n")
    for ad in sorted(BIBLIOGRAPHY):
        p.append(f"**{ad}**\n:   {BIBLIOGRAPHY[ad]}\n\n")

    return "".join(p)


if __name__ == "__main__":
    hedef = Path(__file__).resolve().parents[1] / "docs" / "reference"
    hedef.mkdir(parents=True, exist_ok=True)
    yol = hedef / "features.md"
    yol.write_text(uret(), encoding="utf-8")
    print(f"Yazildi: {yol}")
