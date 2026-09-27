# Reference

Look-up material. Not meant to be read front to back.

| Page | Contents |
|---|---|
| [Feature reference](features.md) | All 208 feature keys: description, formula, requirement, source |
| [Public API](api.md) | The nine public names, with full signatures |

!!! info "This section is in English · Bu bölüm İngilizcedir"

    Feature descriptions, formulas and citations are kept in one language so
    that no translation layer sits between a number and the source it is
    compared against. The `describe_feature()` output you see in Python is
    the same text you see here.

    Öznitelik tanımları, formüller ve künyeler tek dilde tutulur ki bir sayı
    ile karşılaştırıldığı kaynak arasına çeviri katmanı girmesin. Python'da
    `describe_feature()` ile gördüğünüz metnin aynısı burada.

## Generated, not written

`features.md` is produced by `scripts/basvuru_uret.py` from the registry.
Its coverage list comes from the same place the
[verification report](../verification-report.md) takes its own, so a
feature cannot exist in the code and be missing from the documentation.

To regenerate after changing the registry:

```bash
python scripts/basvuru_uret.py
python scripts/dogrulama_raporu.py
```

## Related

- Whether a number matches the one its source published →
  [verification report](../verification-report.md)
- How to read that report →
  [TR](../tr/aciklama/dogrulama.md) · [EN](../en/explanation/verification.md)
- Where the sentence thresholds come from →
  [threshold calibration](../esik-kalibrasyonu.md) (Turkish)
