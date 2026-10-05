# Changelog

## [Unreleased]

### Changed

- The verification tolerance changed from a fixed absolute 0.05 to 1% relative
  to the published value (`math.isclose(rel_tol=0.01)`, with a 1e-9 absolute
  floor only as float-arithmetic safety for expected values of 0). The fixed
  difference was far too loose for ratios in 0-1 (`ttr`) and far too tight for
  values in the hundreds (`curve_length` ≈ 134). One row moves: `ttr` QUITA
  §6.1.1 Text 2 (published 0.590, ours 0.599, difference 1.5%; the source's
  own counts give 121/202 = 0.599) goes from ✅ to 🟡, with its reason now
  written in the report. Turkish report: 47 ✅ + 1 🟡 → 46 ✅ + 2 🟡; English
  report: 36 ✅ + 2 🟡 → 35 ✅ + 3 🟡. No row became ❌ and every other row
  keeps its status.
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

### Fixed

- `segment_text(unit="word")` no longer counts whitespace and line-break
  tokens. `analyze` discards them, so a text with hard line breaks produced
  segments with fewer real tokens than `size` (about 11% fewer in a text
  wrapped every 8 words: 178 instead of 200). Each segment now holds exactly
  `size` tokens by the same count `analyze` uses. Segment boundaries, and so
  segment counts and values, change for texts with line breaks or repeated
  spaces; single-spaced text is unaffected.
- Three registry description texts ran words together ("notclipped",
  "words,vocd_num_runs", "removed,root"); they appear in `describe_feature()`
  and in the feature reference.
- The `describe_feature(...)["params"]` examples in the parameter guide showed
  a list; the function returns a tuple.

### Removed

- The undocumented `LINGUISTIC_FEATURES_NO_ZEYREK_WARMUP` environment variable.
  The Zeyrek warm-up now always runs on import: skipping it and then analysing
  Turkish in the same process could crash on Windows.

## [0.1.0] - 2026-09-28

### Added

- Initial public release.
