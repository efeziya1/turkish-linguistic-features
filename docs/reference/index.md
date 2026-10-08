# Reference

Look-up material. Not meant to be read front to back.

| Page | Contents |
|---|---|
| [Feature reference](features.md) | Every feature key (174 fixed keys and the dynamic `char_` and `ngram_` families): description, formula, requirement, source |
| [Public API](api.md) | The eleven public names, with full signatures |

## Generated, not written

`features.md` is produced by `scripts/generate_feature_reference.py` from the registry.
Its coverage list comes from the same place the
[verification report](../verification-report.md) takes its own, so a
feature cannot exist in the code and be missing from the documentation.

To regenerate after changing the registry:

```bash
python scripts/generate_feature_reference.py
python scripts/generate_verification_report.py
```

## Related

- Whether a number matches the one its source published →
  [verification report](../verification-report.md)
- How to read that report →
  [TR](../tr/aciklama/dogrulama.md) · [EN](../en/explanation/verification.md)
- Where the sentence thresholds come from →
  [threshold calibration](../threshold-calibration.md)
