# aubergine-resume-typst

**English** · [简体中文](README.zh-CN.md)

A bilingual Typst resume template with TOML content files, configurable fonts, and a shared layout. Edit it yourself or ask an agent to help with the content, then preview and export from the same entry point.

The layout includes lightly tinted company cards, education badges, separate projects under one employer, and clickable links. It defaults to a page with A4 width that grows with the content; a single A4 page is also available.

[Preview](#preview) · [Quick start](#quick-start) · [Agent workflow](#editing-with-an-agent) · [Content](#content-and-validation) · [Layout and fonts](#layout-and-fonts) · [FAQ](#faq) · [Development](#development)

## Preview

These screenshots use the **original font preset**, which requires your own fonts. Click an image for the full preview or open the PDF to inspect selectable text and links.

<table>
  <tr><th width="50%">Chinese · Original fonts</th><th width="50%">English · Original fonts</th></tr>
  <tr>
    <td valign="top"><a href="docs/preview-original.png"><img src="docs/preview-original.png" alt="Chinese fictional resume with company cards and education badges" width="100%"></a></td>
    <td valign="top"><a href="docs/preview-original-en.png"><img src="docs/preview-original-en.png" alt="English fictional resume with company cards and projects" width="100%"></a></td>
  </tr>
  <tr><td align="center"><a href="docs/example-original.pdf">Chinese PDF</a></td><td align="center"><a href="docs/example-original-en.pdf">English PDF</a></td></tr>
</table>

The default build uses the **bundled open-source fonts** and needs no commercial fonts.

<details>
<summary>Show the bundled open-source font previews</summary>

<table>
  <tr><th width="50%">Chinese · Open-source fonts</th><th width="50%">English · Open-source fonts</th></tr>
  <tr>
    <td valign="top"><a href="docs/preview.png"><img src="docs/preview.png" alt="Chinese sample using Source Han Serif, Source Han Sans and Inter" width="100%"></a></td>
    <td valign="top"><a href="docs/preview-en.png"><img src="docs/preview-en.png" alt="English sample using the bundled fonts" width="100%"></a></td>
  </tr>
  <tr><td align="center"><a href="docs/example.pdf">Chinese PDF</a></td><td align="center"><a href="docs/example-en.pdf">English PDF</a></td></tr>
</table>

</details>

All examples describe fictional event planning and editorial work. Dates use `20XX`; star counts demonstrate formatting. Chiikawa names provide the theme, and the three Chinese character badges are original lettering assets. No official character artwork is included; this project is unaffiliated with the rights holders.

Example PDFs and screenshots are also available in [Releases](https://github.com/auberginewly/aubergine-resume-typst/releases). See the [changelog](CHANGELOG.md) for version history.

## Quick start

### 1. Get the template

Choose **Use this template → Create a new repository** on GitHub. You can select Private for your personal copy. Alternatively, [download the ZIP](https://github.com/auberginewly/aubergine-resume-typst/archive/refs/heads/main.zip) or clone it:

```bash
git clone https://github.com/auberginewly/aubergine-resume-typst.git
cd aubergine-resume-typst
```

Run the following commands from the repository root.

### 2. Install the tools

Export needs [Typst](https://github.com/typst/typst/releases) and GNU Make. Live browser preview also needs [Tinymist](https://github.com/Myriad-Dreamin/tinymist/releases). Python 3.9+ is needed for personal-file initialization, the environment checker, original-font preflight, and tests. On macOS:

```bash
brew install typst tinymist python
```

On Linux, install the corresponding tools for your distribution. The Makefile uses POSIX commands such as `cp`, `mkdir`, and `rm`. On Windows, use an environment providing GNU Make and those commands, or use the native Typst commands below.

```bash
make doctor                                      # Export tools, configured fonts and font checksums
make doctor DOCTOR_FLAGS=--preview                # Also require Tinymist
make doctor DOCTOR_FLAGS=--tests                  # Also require the Poppler test tools
make doctor FONT_PRESET=original                  # Inspect the original font settings
make doctor TYPST_FLAGS=--ignore-system-fonts      # Check without system fonts
```

Missing required tools, configured fonts, or altered bundled fonts cause a nonzero exit code. Missing optional tools are reported without blocking export. You can also run `python scripts/doctor.py` directly; Make is optional for native Typst export. Diagnostic messages include tool names and TOML field paths; explanatory messages are currently in Chinese.

### 3. Create your personal content files

Keep the public examples intact by initializing the ignored personal directory:

```bash
make init
```

This creates only missing `resume/private/content.toml` and `resume/private/content.en.toml` files from the public examples. It is safe to run again: existing files are preserved and reported as skipped, even when only one language file exists. Without Make, run `python3 scripts/init_personal.py` (or `python scripts/init_personal.py` on Windows).

Replace the fictional entries with your own facts. The two language files are maintained separately; changing the language does not translate the content.

| What to edit | File |
| --- | --- |
| Your Chinese content | `resume/private/content.toml` |
| Your English content | `resume/private/content.en.toml` |
| Default fonts, page mode and density | [`resume/settings.toml`](resume/settings.toml) |
| Original font preset and its page settings | [`resume/settings.original.toml`](resume/settings.original.toml) |

### 4. Preview and export

```bash
make preview CONTENT=resume/private/content.toml
make CONTENT=resume/private/content.toml
make en CONTENT=resume/private/content.en.toml
```

Personal PDFs are written to `output/pdf/personal.pdf` and `personal-en.pdf`. To use the original fonts, run `make original CONTENT=resume/private/content.toml` or `make original-en CONTENT=resume/private/content.en.toml`; their filenames are `personal-original.pdf` and `personal-original-en.pdf`.

`CONTENT` also works with `watch`, `info`, and `check`. Without it, commands continue to read the public fictional examples:

| Font preset | Chinese | English | Public example outputs |
| --- | --- | --- | --- |
| Bundled open-source | `make` | `make en` | `output/pdf/resume.pdf`, `resume-en.pdf` |
| Original, supplied by you | `make original` | `make original-en` | `output/pdf/resume-original.pdf`, `resume-original-en.pdf` |

Preview requires a running process; press `Ctrl+C` to stop it. Browser preview does not export a PDF. Run the export command when ready, or use `make watch CONTENT=resume/private/content.toml` to keep the PDF updated.

`RESUME_LANG` accepts `zh` or `en`; `FONT_PRESET` accepts `open-source` or `original`. Explicitly select the English personal file when switching language:

```bash
make preview RESUME_LANG=en FONT_PRESET=original CONTENT=resume/private/content.en.toml
make info RESUME_LANG=en CONTENT=resume/private/content.en.toml
```

<details>
<summary>Native Typst commands and VS Code</summary>

```bash
# Public Chinese example, bundled fonts
typst compile --root . --font-path fonts resume.typ output.pdf

# Personal English content, bundled fonts
typst compile --root . --font-path fonts --input lang=en --input content=resume/private/content.en.toml resume.typ output-en.pdf

# Original font preset, fonts supplied by you
typst compile --root . --font-path fonts --input settings=resume/settings.original.toml resume.typ output-original.pdf
```

In VS Code, open the whole repository, install the recommended Tinymist extension, and preview `resume.typ`. Project root and font paths are configured. The editor defaults to the public Chinese example; use the explicit `make preview` parameters to select personal files, a language, or another font preset.

</details>

## Editing with an agent

Ask the agent to read [`AGENTS.md`](AGENTS.md) first. Specify the language, content path, font preset, and goal. Most edits belong in TOML; change settings for density and page mode, and change the template only when the visual structure needs to change.

These prompts can be copied and adapted.

### Replace the example with your facts

```text
Read AGENTS.md and README.md. Create resume/private/content.en.toml
from the English example if needed, then update it using these facts:

Facts: [paste your education, work, projects and contact information]
Target role: [role]

Use only the facts I provided. Do not invent dates, metrics, skills,
responsibilities or achievements. List missing information explicitly.
Keep the current fonts, company cards and continuous page mode.
Do not delete detail or reduce font size merely to shorten the resume.
Export with make en CONTENT=resume/private/content.en.toml and render
the PDF to inspect text, alignment, links and the bottom boundary.
Report what changed, the PDF path and any remaining questions.
Keep the public examples intact. Do not commit or upload my personal files.
```

### Polish one entry

```text
Read AGENTS.md. Polish [company or project] in resume/private/content.en.toml.
Goal: [what this entry should communicate more clearly]
Preserve scope, dates, attribution and results. Explain the work, method
and outcome using the available facts; do not add unsupported numbers.
Keep other entries, fonts and layout unchanged. Export with
make en CONTENT=resume/private/content.en.toml and inspect the PDF.
```

### Translate confirmed Chinese content

```text
Use resume/private/content.toml as the confirmed factual source and update
resume/private/content.en.toml with natural, concise English wording.
Preserve dates, numbers, contribution status and attribution. Do not add
claims absent from the Chinese version or edit the Chinese facts.
Flag institution or role names that need an agreed English translation.
Export with make en CONTENT=resume/private/content.en.toml and inspect
headings, wrapping, cards and links.
```

### Adjust the layout

```text
Read AGENTS.md. Inspect the English personal resume.
Content: resume/private/content.en.toml
Font preset: [open-source / original]
Goal: [slightly tighter spacing / one A4 page / a specific layout change]

Prefer the matching settings file. Change the template only if necessary.
For one page, assess density=1.00 and min-density=0.90 first. If the content
does not fit, identify what needs editing; do not crop or keep shrinking it.
Export using the explicit CONTENT path. After template changes, run
make test and render the PDF to inspect the result.
```

Check factual accuracy and translation as well as the PDF. Personal content belongs in ignored `resume/private/`, and personal exports belong in ignored `output/`. `docs/` contains only public fictional samples.

## Content and validation

For the complete field examples, see the [Chinese sample](resume/content.toml) and [English sample](resume/content.en.toml).

Content must be valid TOML. Strings support plain text, `**bold**`, and `[label](https://example.com)` links. Arbitrary Markdown and Typst code are not executed. Put the top-level `skills` array before table declarations such as `[profile]`.

`summary` is an array of paragraphs; `bullets` is an array of bullet points. Use `\"` inside a double-quoted string, or TOML triple-quoted strings for multiline text.

```bash
make check
make check RESUME_LANG=en
make check CONTENT=resume/private/content.en.toml
```

The same content validator runs during compilation and live preview. `make check` validates fields without creating a PDF. Errors include one-based field paths, such as `experience[2].title`; TOML syntax errors point to the file and line. It checks structure and types, not factual accuracy or page capacity.

| Field or section | Expected value |
| --- | --- |
| `[profile]` | Nonempty string `name`; optional string contact fields |
| `skills`, `summary`, `bullets`, education `tags` | Arrays of strings; may be empty or omitted where supported |
| `[[education]]` | Required nonempty strings `school`, `detail`, `date` |
| `[[experience]]`, `[[open-source]]`, `[[projects]]`, nested projects | Required nonempty string `title`; other text fields are optional strings |
| `[[publications]]` | Required nonempty strings `title`, `detail` |
| `tone` | `warm`, `cool`, or `neutral` |
| `stars` | A nonnegative integer, such as `2345`, without quotes or k/w suffixes |

Field names are case-sensitive. Unknown fields are rejected to catch spelling errors.

Only `name` is required in `[profile]`. Omit or leave blank any contact field; its icon and spacing disappear. `phone-display` falls back to `phone`, `github-name` to the final URL segment, and `website-label` to the URL without its protocol and outer slashes. Empty or missing sections are hidden.

### Company cards and multiple projects

```toml
[[experience]]
title = "Fictional Community Club"
detail = "Event Planning Intern"
department = "Neighborhood Events"
date = "20XX.XX — 20XX.XX"
logo = "chii.svg"
tone = "warm"
url = "https://example.com/work"
link-label = "Sample work"

[[experience.projects]]
title = "Meadow Concert"
summary = ["A fictional event publication."]
bullets = ["**Editing**: Describe the work and its outcome."]

[[experience.projects]]
title = "Town Walks"
summary = ["A separate fictional guide."]
bullets = ["**Layout**: Describe this project's contribution."]
```

Place logos in `resume/assets/logos/` and specify the filename. SVG, PNG, and other Typst-supported image formats work. Omit `logo` to keep a card without an image. Cards have a 31pt minimum height and grow when text wraps. The role, department, dates and right-side link are optional.

Use `[[projects]]` and `[[open-source]]` for standalone entries. `repository` holds a full URL, shown as a clickable address to the right. Optional integer `stars` follow the title: `2345` becomes `2.3k Stars`, and `12000` becomes `1.2w Stars`. Counts do not refresh online; record their verification date and source in a comment. Describe pending contributions as submitted and not yet merged.

## Layout and fonts

The default settings use a continuous page, 210mm wide, with 14mm horizontal and 11mm vertical margins. At density 1.00, body text is 10.5pt. Content growth does not automatically shrink the text.

```toml
page-mode = "continuous"
density = 1.00
auto-fit = false
min-density = 0.90
```

For one A4 page, explicitly select `page-mode = "single"` and `auto-fit = true`. The template chooses the largest fitting density between `min-density` and `density`; 0.90 corresponds to 9.45pt body text. If it still does not fit, export fails with a capacity error. Edit the content or return to continuous mode. The supported range is `0.85 ≤ min-density ≤ density ≤ 1.20`; auto-fit only applies to single-page mode. `make info CONTENT=…` reports the actual density, body size and content height.

| Usage | Bundled default | Original preset, supplied by you |
| --- | --- | --- |
| Chinese body | Source Han Serif | Adobe Song Std |
| Chinese headings and bold | Source Han Sans | Adobe Heiti Std |
| English | TeX Gyre Termes | TeX Gyre Termes |
| Contacts | Inter | Helvetica Neue Medium |

The original contacts use weight 500, blue text and 9.4pt base size. Original Chinese education badges use a 0.32pt stroke for weight; the open-source preset uses a real bold font without a stroke.

Open-source fonts and their licenses are bundled; see [font documentation](fonts/README.md). Adobe fonts and Helvetica Neue are not distributed. Supply fonts you are licensed to use in ignored `fonts/local/` or install them locally. Original-font export checks the actual configured families before compiling.

Customize the chosen settings file using the family names reported by `typst fonts --font-path fonts`:

```toml
[fonts]
body = ["TeX Gyre Termes", "Source Han Serif"]
heading = ["TeX Gyre Termes", "Source Han Sans"]
contact = ["Inter", "Source Han Sans"]
```

These are ordered, nonempty font name arrays. Omit `[fonts]` to use defaults. The family names of the bundled Chinese fonts do not include `CN`. Test independence from system fonts with `make TYPST_FLAGS=--ignore-system-fonts`.

## FAQ

<details>
<summary>What if the original fonts are missing?</summary>

Run `typst fonts --font-path fonts` to confirm the family names. Put fonts you are licensed to use in `fonts/local/`, or install them locally, then compile again. For the bundled open-source fonts, run `make` or `make en`.

</details>

<details>
<summary>Does the English version update automatically with the Chinese version?</summary>

No. The two content files are maintained separately so each language can use appropriate wording. An agent can update the English file from confirmed Chinese facts; check role names, dates, numbers and contribution status afterwards.

</details>

<details>
<summary>What if the resume does not fit one page, or the preview stops updating?</summary>

Single-page capacity errors appear in the compilation or preview terminal. Edit the content or return to `continuous` mode. If the preview shows old content, check the terminal for TOML syntax, font or capacity errors. Browser preview updates do not export a PDF; run the export command to generate it.

</details>

## Development

[Template checks](https://github.com/auberginewly/aubergine-resume-typst/actions/workflows/test.yml) runs on every push and pull request: bundled font checksums, the environment checker, isolated tests, and both public language builds on Linux without system fonts. CI uses Typst 0.15.1 and needs no commercial fonts.

Tests require Python 3.9+, Typst, GNU Make, and Poppler's `pdfinfo`, `pdffonts`, and `pdftotext`. Example screenshots also need `pdftoppm`. On macOS, install Poppler with `brew install poppler`.

```bash
make test
# If you have supplied the original fonts locally:
RUN_ORIGINAL_FONT_TESTS=1 make test
```

Tests use synthetic data in `tests/fixtures/`, independent of your content and settings. They cover language output, embedded fonts, boundaries, density and auto-fit, optional sections, contacts, nested projects, long cards, links, star formatting, field errors and the personal-file workflow. Original-font integration is opt-in. A temporary workspace also tests unequal language sections and custom fonts without copying local commercial fonts.

Tool paths can be overridden with uppercase environment variables, for example `PDFTOTEXT=/path/to/pdftotext make test`. After layout changes, render and visually inspect the PDFs as well.

To refresh public examples, first confirm the default content is entirely fictional and suitable for publication:

```bash
make example
make example RESUME_LANG=en
make example FONT_PRESET=original
make example RESUME_LANG=en FONT_PRESET=original
```

These commands update the corresponding PDFs and PNGs in `docs/`. `example` rejects custom `CONTENT` paths; the default public content must still be reviewed before publishing. Regenerate lettering badges with `python3 scripts/generate_badges.py`. `make clean` removes only `output/`.

```text
resume.typ                    Shared entry point
resume/content*.toml          Public fictional samples
resume/private/               Personal content, ignored by Git
resume/settings*.toml         Page and font presets
resume/assets/                Icons and lettering badges
typst/template.typ            Layout and measurement
typst/validate.typ            Content validation
fonts/                        Bundled fonts, licenses and checksums
docs/                         Public PDFs and screenshots
scripts/                      Environment/font checks and badge generation
tests/                        Template and personal-workflow tests
tests/fixtures/               Independent synthetic test data
output/                       Local exports, ignored by Git
```

## License

Source code is [MIT licensed](LICENSE). Bundled fonts retain their own licenses; see [font documentation](fonts/README.md). Feather icons retain their [MIT license](resume/assets/icons/LICENSE.txt).
