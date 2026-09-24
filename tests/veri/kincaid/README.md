# Kincaid et al. (1975), Appendix A — the eighteen test passages

## Source

Kincaid, J. P., Fishburne, R. P., Rogers, R. L., & Chissom, B. S. (1975).
*Derivation of new readability formulas (Automated Readability Index, Fog
Count and Flesch Reading Ease Formula) for Navy enlisted personnel.*
Research Branch Report 8-75. Millington, TN: Naval Air Station Memphis.
DOI [10.21236/ADA006655](https://doi.org/10.21236/ADA006655) · DTIC ADA006655

The passages are printed in **Appendix A, pages 23–30** of that report. The
readability values they are compared against are printed elsewhere in the
same report:

| Values | Where |
|---|---|
| ARI, Fog Count, Flesch band — **old** formulas | Table 1, pages 8–9 |
| ARI, Fog Count, Flesch-Kincaid — **new** formulas | Table 2, page 12 |

Note that the text and the published numbers live in **different places**.
Anyone checking a value must look at Table 1 or Table 2, not at Appendix A.

## Copyright

This report is a work of the United States Navy, prepared by US Government
employees as part of their official duties. As such it is **in the public
domain** in the United States and carries no copyright restriction. The
report is distributed without restriction by DTIC.

That is why these passages may be stored here in full, unlike the Turkish
readability samples used elsewhere in the test suite, which are quoted only
in part under fair use.

## Files

| Pattern | Contents |
|---|---|
| `passage_NN.txt` | The body of passage NN, as one paragraph |
| `passage_NN.title.txt` | The passage's all-caps heading, kept separately |

The heading is stored separately because the report does not say whether it
was included when the published values were computed. Both variants were
measured; see `plan/kincaid-uctan-uca.md` for the result.

## How these files were produced

Text was extracted from the PDF with `pypdf`, split on the `Passage N
(RGL = x.x)` markers, and stripped of page numbers and the `Appendix A`
running head. Line breaks inside a passage were joined with a single space;
the original double spaces after sentences were kept because the Automated
Readability Index counts every non-space character and the report's own
typing instructions (Appendix B) say double spaces were *not* typed.

Extraction is clean: zero replacement characters, and every passage was
checked against the raw PDF text. Two headings carry OCR damage
(`passage_07.title.txt` is missing a word, `passage_08.title.txt` has a
stray apostrophe) but no body text is affected.
