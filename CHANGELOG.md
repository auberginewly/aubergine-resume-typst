# Changelog

## Unreleased

- Allow optional `[section-titles]` overrides in each language's content file, preserving default headings, section order, styling and empty-section hiding; validate keys and nonempty string values.

## v0.1.0 — 2026-10-23

First public release of the bilingual Typst resume template.

- Chinese and English fictional samples with lightly tinted company cards, education badges, nested projects, links and star counts.
- Bundled open-source fonts and an optional original font preset using fonts supplied by the user.
- Continuous pages with A4 width, optional single-page auto-fit, and explicit overflow errors.
- Separate, ignored personal content selected through `CONTENT` or Typst's `--input content=…`; distinct personal PDF filenames and protection against exporting custom content into public examples.
- `make doctor` for tools, configured fonts and bundled font integrity; `make check` for field validation with indexed diagnostics.
- Chinese and English documentation, setup instructions, and copyable agent editing prompts.
- GitHub Actions checks on Linux, font checksums, isolated template tests, and personal-workflow tests.

Release assets contain four fictional sample PDFs and their screenshots: Chinese/English in the bundled open-source and original font presets. Raw commercial fonts are not included.
