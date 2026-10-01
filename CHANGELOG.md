# Changelog

## [Unreleased]

### Changed

- Turkish syllable counts now read ordinals (`3. kat` → üçüncü), times and
  scores (`10:30` → on otuz) and numbers glued to letters (`3kg` → üç
  kilogram, `100m` → yüz metre, `3G` → üç ge). These forms used to be skipped
  or, in the readability formulas, counted as cardinals. The readability
  formulas and the syllable features change on texts that contain them; no
  verification row changed.
- Syllable features (both languages) now add the reading of a listed symbol to
  the number next to it (`%50` → yüzde elli, `$5` → five dollars), as the
  readability formulas already did. The symbol still does not count as a word.
- Registry metadata of `syllable_mean` and `syllable_cv` (description,
  formula, requirement, citation) had been copied from the syllable-bucket
  keys. `syllable_mean` now cites Flesch (1948), whose Formula A defines
  average word length in syllables (per 100 words; per word here) and which
  Ateşman (1997) adapted for Turkish; `syllable_cv` has no citation (not a
  named measure) and requires at least 2 syllabifiable words, as the code
  always did. Cited features: TR 141 → 140, EN 116 → 115; verification
  candidates: TR 92 → 91, EN 81 → 80. No values change.

### Removed

- The undocumented `LINGUISTIC_FEATURES_NO_ZEYREK_WARMUP` environment variable.
  The Zeyrek warm-up now always runs on import: skipping it and then analysing
  Turkish in the same process could crash on Windows.

## [0.1.0] - 2026-09-28

### Added

- Initial public release.
