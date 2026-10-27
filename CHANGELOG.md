# Changelog

## v0.2.0 — 2026-10-27

- Add `make init` / `python3 scripts/init_personal.py` to create only missing personal content files with exclusive creation; preserve existing files during repeated or concurrent initialization and report directory conflicts.
- Allow optional `[section-titles]` overrides in each language's content file, preserving default headings, section order, styling and empty-section hiding; validate keys and nonempty string values.
- Update both guides with safe initialization and custom heading examples, and include commented heading configuration in the fictional content samples.
- Make the English README the default repository guide, with a Simplified Chinese language switch; builds still default to Chinese.
- Add regression coverage for initialization, existing bytes and timestamps, symlinks, missing sources, directory conflicts, bilingual headings, literal text and indexed validation errors.

Thanks to [Jaxon1216](https://github.com/Jaxon1216) for the safe initialization fix in [#4](https://github.com/auberginewly/aubergine-resume-typst/pull/4). Custom section titles are included in [#5](https://github.com/auberginewly/aubergine-resume-typst/pull/5).

Existing content requires no migration. Remove `[section-titles]` before using a content file with the older template. The default layout and fictional sample attachments are unchanged from v0.1.0.

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
