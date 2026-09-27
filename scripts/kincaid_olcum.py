"""Kincaid ve ark. (1975) Ek A'daki 18 pasajı boru hattından geçirir.

Kaynağın yayımladığı değerlerle karşılaştırır ve ara değerleri (vuruş,
kelime, cümle) gösterir — fark çıktığında hangi girdiden geldiğini görmek
için.

Çalıştırma::

    python scripts/kincaid_olcum.py

Bu bir **test değil**, ölçüm aracı. Sonuçlar 0,05 toleransını tutmuyor;
nedeni plan belgesinde yazılı.
"""
from __future__ import annotations

import sys
from pathlib import Path

import turkish_linguistic_features as tlf

VERI = Path(__file__).resolve().parents[1] / "tests" / "veri" / "kincaid"

# Tablo 1 (basılı s.8-9) — ESKİ formüller: ARI, Fog Count, Flesch bandı.
TABLO1: dict[int, tuple[float, float, str | None]] = {
    1: (10.6, 12.4, "8-9"), 2: (20.3, 15.9, "16+"), 3: (13.3, 12.9, "13-16"),
    4: (8.8, 7.8, "8-9"), 5: (9.5, 8.0, "8-9"), 6: (12.4, 12.8, "13-16"),
    7: (12.7, 13.1, "13-16"), 8: (16.4, 17.9, "13-16"), 9: (9.7, 10.4, "7"),
    10: (13.1, 14.4, "13-16"), 11: (7.8, 7.0, "8-9"),
    12: (16.7, 16.0, "10-12"), 13: (13.4, 12.5, "10-12"),
    14: (12.0, 13.7, "13-16"), 15: (9.7, 11.6, "8-9"), 16: (13.5, 14.0, "16+"),
    17: (10.4, 10.4, "10-12"), 18: (10.9, 7.2, None),
}
TABLO1_ORT_ARI = 12.3

# Tablo 2 (basılı s.12) — YENİ formüller, "Flesch" sütunu = FKGL.
# Parantezli değerler basitleştirilmiş formülün; parantezsizler alındı.
TABLO2_FKGL: dict[int, float] = {
    1: 9.7, 2: 16.7, 3: 12.7, 4: 8.2, 5: 7.1, 6: 12.3, 7: 11.7, 8: 14.7,
    9: 8.0, 10: 11.7, 11: 8.1, 12: 11.8, 13: 10.0, 14: 12.5, 15: 8.4,
    16: 13.8, 17: 9.3, 18: 6.6,
}
TABLO2_ORT_FKGL = 10.7

# Flesch (1948) kendi sınıf tablosu: sınıf bandı → FRE aralığı.
FRE_BANDI = {"5": (90, 100), "6": (80, 90), "7": (70, 80), "8-9": (60, 70),
             "10-12": (50, 60), "13-16": (30, 50), "16+": (0, 30)}


def pasaj(no: int, baslikla: bool = False) -> str:
    govde = (VERI / f"passage_{no:02d}.txt").read_text(encoding="utf-8").strip()
    if not baslikla:
        return govde
    bas = VERI / f"passage_{no:02d}.title.txt"
    if not bas.exists():
        return govde
    return bas.read_text(encoding="utf-8").strip() + ". " + govde


def main(baslikla: bool = False) -> int:
    print(f"{'#':>2} {'vuruş':>6} {'kel':>4} | {'ARI kay':>7} {'ARI biz':>7} "
          f"{'fark':>6} | {'FKGL kay':>8} {'FKGL biz':>8} {'fark':>6} | FRE bant")
    fark_ari: list[float] = []
    fark_fkgl: list[float] = []
    bant_ici = bant_top = 0
    toplam_ari = toplam_fkgl = 0.0

    for n in range(1, 19):
        metin = pasaj(n, baslikla)
        oz = tlf.analyze(metin, lang="en")
        vurus = sum(len(p) for p in metin.split())
        a_k, f_k = TABLO1[n][0], TABLO2_FKGL[n]
        a_b, f_b = oz["ari"], oz["flesch_kincaid_grade"]
        fark_ari.append(abs(a_b - a_k))
        fark_fkgl.append(abs(f_b - f_k))
        toplam_ari += a_b
        toplam_fkgl += f_b

        bant = TABLO1[n][2]
        if bant is None:
            durum = "—"
        else:
            lo, hi = FRE_BANDI[bant]
            ok = lo <= oz["flesch_reading_ease"] <= hi
            bant_top += 1
            bant_ici += ok
            durum = f"{bant:>5} {'içinde' if ok else 'DIŞINDA'}"

        print(f"{n:2d} {vurus:6d} {len(metin.split()):4d} | {a_k:7.1f} "
              f"{a_b:7.2f} {a_b - a_k:+6.2f} | {f_k:8.1f} {f_b:8.2f} "
              f"{f_b - f_k:+6.2f} | {durum}")

    print(f"\nARI  ortalama  kaynak {TABLO1_ORT_ARI}  bizim {toplam_ari / 18:.2f}")
    print(f"FKGL ortalama  kaynak {TABLO2_ORT_FKGL}  bizim {toplam_fkgl / 18:.2f}")
    print(f"ARI  ortalama mutlak fark {sum(fark_ari) / 18:.2f}  "
          f"en büyük {max(fark_ari):.2f}")
    print(f"FKGL ortalama mutlak fark {sum(fark_fkgl) / 18:.2f}  "
          f"en büyük {max(fark_fkgl):.2f}")
    print(f"FRE bandının içinde: {bant_ici}/{bant_top}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--baslikla" in sys.argv))
