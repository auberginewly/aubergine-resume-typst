TYPST ?= typst
TINYMIST ?= tinymist
PYTHON ?= python3
PDFTOPPM ?= pdftoppm
RESUME_LANG ?= zh
FONT_PRESET ?= open-source
ifneq ($(FONT_PRESET),open-source)
ifneq ($(FONT_PRESET),original)
$(error FONT_PRESET 可选 open-source 或 original，当前为 "$(FONT_PRESET)")
endif
endif
ifneq ($(RESUME_LANG),zh)
ifneq ($(RESUME_LANG),en)
$(error RESUME_LANG 可选 zh 或 en，当前为 "$(RESUME_LANG)")
endif
endif
SOURCE := resume.typ
LANG_SUFFIX := $(if $(filter en,$(RESUME_LANG)),-en,)
FONT_SUFFIX := $(if $(filter original,$(FONT_PRESET)),-original,)
SETTINGS := $(if $(filter original,$(FONT_PRESET)),resume/settings.original.toml,resume/settings.toml)
DEFAULT_CONTENT := $(if $(filter en,$(RESUME_LANG)),resume/content.en.toml,resume/content.toml)
CONTENT ?= $(DEFAULT_CONTENT)
OUTPUT_NAME := $(if $(filter $(DEFAULT_CONTENT),$(CONTENT)),resume,personal)
PDF := output/pdf/$(OUTPUT_NAME)$(FONT_SUFFIX)$(LANG_SUFFIX).pdf
EXAMPLE := docs/example$(FONT_SUFFIX)$(LANG_SUFFIX).pdf
PREVIEW := docs/preview$(FONT_SUFFIX)$(LANG_SUFFIX)
FLAGS := --root . --font-path fonts --input lang=$(RESUME_LANG) --input "settings=$(SETTINGS)" --input "content=$(CONTENT)"
TYPST_FLAGS ?=
DOCTOR_FLAGS ?=
CHECK_FONTS := $(if $(filter original,$(FONT_PRESET)),TYPST="$(TYPST)" $(PYTHON) scripts/check_original_fonts.py --settings "$(SETTINGS)" $(filter --ignore-system-fonts,$(TYPST_FLAGS)),:)

.PHONY: all pdf init en original original-en preview watch info check doctor example check-example clean test FORCE
all: pdf
pdf: $(PDF)

init:
	$(PYTHON) scripts/init_personal.py

# 输入路径、编译参数变化也必须生效，不能只依赖源文件修改时间。
$(PDF): $(SOURCE) Makefile FORCE
	@mkdir -p $(dir $@)
	@$(CHECK_FONTS)
	$(TYPST) compile $(FLAGS) $(TYPST_FLAGS) $(SOURCE) $@

en:
	$(MAKE) RESUME_LANG=en pdf

original:
	$(MAKE) FONT_PRESET=original pdf

original-en:
	$(MAKE) RESUME_LANG=en FONT_PRESET=original pdf

preview:
	@$(CHECK_FONTS)
	$(TINYMIST) preview $(FLAGS) --open $(SOURCE)

watch:
	@mkdir -p $(dir $(PDF))
	@$(CHECK_FONTS)
	$(TYPST) watch $(FLAGS) $(TYPST_FLAGS) $(SOURCE) $(PDF)

info:
	@$(CHECK_FONTS)
	$(TYPST) eval $(FLAGS) $(TYPST_FLAGS) --in $(SOURCE) 'query(<resume-layout>).first().value' --pretty

doctor:
	TYPST="$(TYPST)" TINYMIST="$(TINYMIST)" $(PYTHON) scripts/doctor.py --settings "$(SETTINGS)" $(filter --ignore-system-fonts,$(TYPST_FLAGS)) $(DOCTOR_FLAGS)

check:
	$(TYPST) eval $(FLAGS) $(TYPST_FLAGS) '{ import "/typst/validate.typ": validate-content; validate-content(toml(sys.inputs.at("content"))); "内容字段检查通过。" }'

# 公开示例均须为虚构内容；语言和字体预设通过变量选择。
check-example:
	@test "$(CONTENT)" = "$(DEFAULT_CONTENT)" || { echo 'example 仅接受默认公开示例；个人内容请用 make CONTENT=... 导出到 output/。' >&2; exit 1; }

example: check-example $(PDF)
	@mkdir -p docs
	cp $(PDF) $(EXAMPLE)
	$(PDFTOPPM) -f 1 -singlefile -scale-to 2200 -png $(EXAMPLE) $(PREVIEW)

clean:
	rm -rf output

test:
	$(PYTHON) tests/test_init.py
	$(PYTHON) tests/test_template.py
	$(PYTHON) tests/test_personalization.py
	$(PYTHON) tests/test_doctor.py
