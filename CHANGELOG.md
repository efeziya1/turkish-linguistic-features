# Changelog

## [Unreleased]

### Changed

- Turkish syllable counts now read ordinals (`3. kat` → üçüncü), times and
  scores (`10:30` → on otuz) and numbers glued to letters (`3kg` → üç
  kilogram, `100m` → yüz metre, `3G` → üç ge). These forms used to be skipped
  or, in the readability formulas, counted as cardinals.
- Syllable features (both languages) now add the reading of a listed symbol to
  the number next to it (`%50` → yüzde elli, `$5` → five dollars), as the
  readability formulas already did. The symbol still does not count as a word. The readability
  formulas and the syllable features change on texts that contain them; no
  verification row changed.

### Removed

- The undocumented `LINGUISTIC_FEATURES_NO_ZEYREK_WARMUP` environment variable.
  The Zeyrek warm-up now always runs on import: skipping it and then analysing
  Turkish in the same process could crash on Windows.

## [0.1.0] - 2026-09-28

### Added

- Initial public release.
