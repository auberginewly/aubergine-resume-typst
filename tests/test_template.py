"""模板行为回归测试：只用 Python 标准库、Typst 与 Poppler。"""
from pathlib import Path
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock
import runpy
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures"
HEADINGS = ("教育背景", "个人技能", "实习经历", "开源贡献", "项目经历", "论文成果")


def executable(name):
    configured = os.environ.get(name.upper(), name)
    found = shutil.which(configured)
    if not found:
        raise RuntimeError("缺少工具：" + name + "。请参照 README 安装依赖。")
    return found


def run(*args, success=True):
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    if success:
        if result.returncode:
            raise AssertionError(result.stderr or result.stdout)
        if "warning:" in result.stderr:
            raise AssertionError("不允许静默字体回退或其他编译警告：\n" + result.stderr)
    return result


def plain(value):
    value = re.sub(r"\[([^\]]+)\]\((https?://[^\s)]+)\)", r"\1", value)
    return re.sub(r"\s+", "", value.replace("**", ""))


def create_workspace(destination, include_tests=False):
    """创建无个人内容、无本地商业字体的构建副本。"""
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    for name in ("Makefile", "resume.typ", ".gitignore"):
        shutil.copy2(ROOT / name, destination / name)
    for name in ("typst", "scripts", "resume/assets"):
        shutil.copytree(ROOT / name, destination / name, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(ROOT / "fonts", destination / "fonts",
                    ignore=shutil.ignore_patterns("local"))
    for name in ("content.toml", "content.en.toml", "settings.toml", "settings.original.toml"):
        shutil.copy2(FIXTURES / name, destination / "resume" / name)
    if include_tests:
        shutil.copytree(ROOT / "tests", destination / "tests",
                        ignore=shutil.ignore_patterns("__pycache__"))
    return destination


class TemplateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.typst = executable("typst")
        cls.pdfinfo = executable("pdfinfo")
        cls.pdffonts = executable("pdffonts")
        cls.pdftotext = executable("pdftotext")
        cls.flags = ["--root", str(ROOT), "--font-path", str(ROOT / "fonts"), "--ignore-system-fonts"]
        (ROOT / "tmp").mkdir(exist_ok=True)
        cls.temp = tempfile.TemporaryDirectory(prefix="template-tests-", dir=ROOT / "tmp")
        cls.directory = Path(cls.temp.name)
        cls.source = cls.directory / "fixture-main.typ"
        cls.source.write_text(
            '#import "/typst/template.typ": resume\n'
            '#let language = sys.inputs.at("lang", default: "zh")\n'
            '#let content = if language == "en" { "/tests/fixtures/content.en.toml" } else { "/tests/fixtures/content.toml" }\n'
            '#let settings = sys.inputs.at("settings", default: "/tests/fixtures/settings.toml")\n'
            '#resume(toml(content), toml(settings))\n', encoding="utf-8",
        )
        cls.default_pdf = cls.directory / "default.pdf"
        run(cls.typst, "compile", *cls.flags, str(cls.source), str(cls.default_pdf))
        cls.data = cls.evaluate('toml("tests/fixtures/content.toml")')
        cls.default_text = cls.extract(cls.default_pdf)
        cls.default_metrics = cls.metrics(cls.source)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    @classmethod
    def evaluate(cls, expression, source=None, inputs=()):
        args = [cls.typst, "eval", *cls.flags, *inputs]
        if source:
            args.extend(["--in", str(source)])
        return json.loads(run(*args, expression).stdout)

    @classmethod
    def metrics(cls, source, inputs=()):
        return cls.evaluate("query(<resume-layout>).first().value", source, inputs)

    @classmethod
    def extract(cls, pdf):
        return run(cls.pdftotext, "-layout", str(pdf), "-").stdout

    def fixture(self, name, data="data", settings="settings"):
        source = self.directory / (name + ".typ")
        source.write_text(
            '#import "/typst/template.typ": resume\n'
            '#let data = toml("/tests/fixtures/content.toml")\n'
            '#let settings = toml("/tests/fixtures/settings.toml")\n'
            '#resume(' + data + ', ' + settings + ')\n', encoding="utf-8",
        )
        return source

    def compile(self, source, inputs=(), success=True):
        output = self.directory / (source.stem + "-" + str(len(list(self.directory.glob("*.pdf")))) + ".pdf")
        result = run(self.typst, "compile", *self.flags, *inputs, str(source), str(output), success=success)
        return output, result

    def test_default_layout_and_fonts(self):
        info = run(self.pdfinfo, str(self.default_pdf)).stdout
        self.assertRegex(info, r"Pages:\s+1\b")
        dimensions = re.search(r"Page size:\s+([\d.]+) x ([\d.]+) pts", info)
        width, height = map(float, dimensions.groups())
        self.assertAlmostEqual(width, 210 * 72 / 25.4, delta=0.1)
        self.assertAlmostEqual(height, self.default_metrics["height-pt"] + 22 * 72 / 25.4, delta=0.1)
        self.assertEqual(self.default_metrics["page-mode"], "continuous")
        self.assertEqual(self.default_metrics["density"], 1.0)
        self.assertEqual(self.default_metrics["body-pt"], 10.5)
        fonts = run(self.pdffonts, str(self.default_pdf)).stdout
        for family in ("SourceHanSerifCN-Regular", "SourceHanSerifCN-Bold", "SourceHanSansCN-Bold", "TeXGyreTermes-Regular", "TeXGyreTermes-Bold", "Inter"):
            self.assertIn(family, fonts)
        for family in ("AdobeSong", "AdobeHeiti", "Helvetica"):
            self.assertNotIn(family, fonts)
        for line in fonts.splitlines()[2:]:
            self.assertRegex(line, r"\byes\s+yes\s+yes\b", "所有字体必须嵌入、子集化且有 Unicode 映射")
        bbox = run(self.pdftotext, "-bbox", str(self.default_pdf), "-").stdout
        tree = ET.fromstring(bbox)
        words = list(tree.iter("{http://www.w3.org/1999/xhtml}word"))
        self.assertTrue(words)
        for word in words:
            self.assertGreaterEqual(float(word.attrib["xMin"]), 14 * 72 / 25.4 - 1)
            self.assertLessEqual(float(word.attrib["xMax"]), width - 14 * 72 / 25.4 + 1)
            self.assertGreaterEqual(float(word.attrib["yMin"]), 0)
            self.assertLessEqual(float(word.attrib["yMax"]), height - 10 * 72 / 25.4)

    def test_all_content_and_project_order(self):
        normalized = plain(self.default_text)
        paragraphs = list(self.data.get("skills", []))
        for section in ("experience", "open-source", "projects", "publications"):
            for item in self.data.get(section, []):
                paragraphs.append(item["title"])
                paragraphs.extend(item.get("summary", []))
                paragraphs.extend(item.get("bullets", []))
                for project in item.get("projects", []):
                    paragraphs.append(project["title"])
                    paragraphs.extend(project.get("summary", []))
                    paragraphs.extend(project.get("bullets", []))
        for paragraph in paragraphs:
            self.assertIn(plain(paragraph), normalized)
        for heading in HEADINGS:
            self.assertIn(heading, self.default_text)
        for company in self.data["experience"]:
            positions = [normalized.index(plain(project["title"])) for project in company.get("projects", [])]
            self.assertEqual(positions, sorted(positions))
            for first, second in zip(company.get("projects", []), company.get("projects", [])[1:]):
                for bullet in first.get("bullets", []):
                    self.assertLess(normalized.index(plain(bullet)), normalized.index(plain(second["title"])))
        for item in self.data["open-source"] + self.data["projects"]:
            self.assertIn(item["repository"].removeprefix("https://"), normalized)
        expected_stars = self.evaluate('{ import "/typst/template.typ": format-stars; format-stars(' + str(self.data["open-source"][0]["stars"]) + ") }")
        self.assertIn(expected_stars + "Stars", normalized)
        self.assertTrue(all("stars" not in project for project in self.data["projects"]))

    def test_long_page_and_manual_density(self):
        source = self.fixture("growing", 'data + (skills: data.skills * 15)')
        _, _ = self.compile(source)
        expanded = self.metrics(source)
        self.assertGreater(expanded["height-pt"], self.default_metrics["height-pt"])
        self.assertEqual(expanded["body-pt"], 10.5)
        _, _ = self.compile(self.source, ("--input", "density=0.90"))
        tighter = self.metrics(self.source, ("--input", "density=0.90"))
        self.assertAlmostEqual(tighter["body-pt"], 9.45)
        self.assertLess(tighter["height-pt"], self.default_metrics["height-pt"])

    def test_single_page_and_actual_auto_fit(self):
        short = self.fixture("short", 'data + (experience: (), "open-source": (), projects: (), publications: ())')
        pdf, _ = self.compile(short, ("--input", "page-mode=single"))
        self.assertRegex(run(self.pdfinfo, str(pdf)).stdout, r"Page size:.*\(A4\)")
        self.assertEqual(self.metrics(short, ("--input", "page-mode=single"))["density"], 1.0)
        # 使用独立合成案例跨越一页阈值，不依赖默认示例文案长短。
        source = self.fixture("fit-boundary", '(profile: (name: "适配测试"), skills: ("测试行，验证一页自动适配。",) * 60)')
        inputs = ("--input", "page-mode=single", "--input", "auto-fit=true")
        pdf, _ = self.compile(source, inputs)
        fit = self.metrics(source, inputs)
        self.assertGreaterEqual(fit["density"], 0.90)
        self.assertLess(fit["density"], 1.0)
        self.assertLessEqual(fit["height-pt"], fit["available-pt"])
        self.assertRegex(run(self.pdfinfo, str(pdf)).stdout, r"Pages:\s+1\b")

    def test_overflow_and_invalid_settings(self):
        source = self.fixture("overflow", 'data + (skills: data.skills * 60)')
        _, result = self.compile(source, ("--input", "page-mode=single", "--input", "auto-fit=true"), success=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("超出一页的可读容量", result.stderr)
        _, result = self.compile(source, ("--input", "page-mode=single"), success=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("当前密度放不下一页", result.stderr)
        for inputs, message in [(("--input", "density=0.70"), "密度范围"), (("--input", "page-mode=invalid"), "page-mode 可选")]:
            _, result = self.compile(self.source, inputs, success=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(message, result.stderr)
        invalid = self.fixture("invalid-fonts", settings='settings + (fonts: (body: ()),)')
        _, result = self.compile(invalid, success=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("必须是非空字体名称数组", result.stderr)

    def test_empty_sections_and_no_contacts(self):
        source = self.fixture("minimal", '(profile: (name: "最小示例"), skills: (), education: (), experience: (), "open-source": (), projects: (), publications: ())')
        pdf, _ = self.compile(source)
        text = self.extract(pdf)
        self.assertEqual(text.strip(), "最小示例")
        contacts = self.evaluate('{ import "/typst/template.typ": contact-line; contact-line((name: "测试",)) == none }')
        self.assertTrue(contacts)
        # 缺失键也视为空章节。
        source = self.fixture("absent", '(profile: (name: "仅姓名"),)')
        pdf, _ = self.compile(source)
        self.assertEqual(self.extract(pdf).strip(), "仅姓名")

    def test_content_errors_identify_field_paths(self):
        invalid = (
            ('(:)', '缺少 [profile]'),
            ('(profile: "invalid",)', 'profile 必须是 TOML 表'),
            ('(profile: (:),)', 'profile.name 缺少必填字段'),
            ('(profile: (name: "  "),)', 'profile.name 不能为空'),
            ('(profile: (name: "Fixture", phone: 123),)', 'profile.phone 必须是字符串'),
            ('data + (skils: (),)', 'skils 是未知字段'),
            ('data + (skills: "invalid",)', 'skills 必须是字符串数组'),
            ('data + (skills: (1,),)', 'skills[1] 必须是字符串'),
            ('data + (experience: (title: "invalid"),)', 'experience 必须是条目数组'),
            ('data + (experience: ((),),)', 'experience[1] 必须是 TOML 表'),
            ('data + (experience: ((title: "First"), (:)))', 'experience[2].title 缺少必填字段'),
            ('data + (experience: ((title: "Fixture", tone: "pink"),))', 'experience[1].tone 只能填写'),
            ('data + (experience: ((title: "Fixture", projects: ((summary: (),),)),))', 'experience[1].projects[1].title'),
            ('data + (projects: ((title: "Fixture", stars: "4k"),))', 'projects[1].stars 必须是不小于 0 的整数'),
            ('data + (projects: ((title: "Fixture", stars: -1),))', 'projects[1].stars 必须是不小于 0 的整数'),
            ('data + (education: ((school: "Fixture", date: "20XX", detail: "Degree", tags: (1,)),))', 'education[1].tags[1]'),
            ('data + (publications: ((title: "Fixture",),))', 'publications[1].detail 缺少必填字段'),
            ('data + (projects: ((title: "Fixture", summmary: ()),))', 'projects[1].summmary 是未知字段'),
            ('data + ("section-titles": (),)', 'section-titles 必须是 TOML 表'),
            ('data + ("section-titles": (experince: "Work"),)', 'section-titles.experince 是未知字段'),
            ('data + ("section-titles": (details: "Work"),)', 'section-titles.details 是未知字段'),
            ('data + ("section-titles": (experience: 123),)', 'section-titles.experience 必须是字符串'),
            ('data + ("section-titles": (experience: "  "),)', 'section-titles.experience 不能为空'),
        )
        for index, (content, message) in enumerate(invalid):
            with self.subTest(message=message):
                _, result = self.compile(self.fixture("invalid-content-" + str(index), content), success=False)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)

    def test_section_title_overrides_and_language_defaults(self):
        for language, experience, projects, defaults in (
            ("zh", "工作经历", "个人项目", ("教育背景", "个人技能", "开源贡献", "论文成果")),
            ("en", "Employment", "Selected Work", ("Education", "Skills", "Open Source", "Publications")),
        ):
            with self.subTest(language=language):
                content = 'toml("/tests/fixtures/content.en.toml")' if language == "en" else 'data'
                titles = '("section-titles": (experience: "' + experience + '", projects: "' + projects + '"),)'
                source = self.fixture("titles-" + language, content + ' + ' + titles)
                pdf, _ = self.compile(source, ("--input", "lang=" + language))
                text = self.extract(pdf)
                headings = (defaults[0], defaults[1], experience, defaults[2], projects, defaults[3])
                positions = [text.index(heading) for heading in headings]
                self.assertEqual(positions, sorted(positions))
                self.assertNotIn("实习经历" if language == "zh" else "Experience", text)
                # 空覆盖表与未配置时具有相同输出和测量结果。
                empty = self.fixture("empty-titles-" + language, content + ' + ("section-titles": (:),)')
                empty_pdf, _ = self.compile(empty, ("--input", "lang=" + language))
                default_pdf, _ = self.compile(self.source, ("--input", "lang=" + language))
                self.assertEqual(self.extract(empty_pdf), self.extract(default_pdf))
                self.assertEqual(self.metrics(empty, ("--input", "lang=" + language)),
                                 self.metrics(self.source, ("--input", "lang=" + language)))

    def test_all_section_titles_and_literal_text(self):
        titles = dict(zip(("education", "skills", "experience", "open-source", "projects", "publications"),
                          ("Academic Background", "Capabilities", "Career", "Community Work", "Portfolio", "Writing")))
        entries = ', '.join(json.dumps(key) + ': ' + json.dumps(value) for key, value in titles.items())
        source = self.fixture("all-titles", 'data + ("section-titles": (' + entries + '),)')
        for language in ("zh", "en"):
            pdf, _ = self.compile(source, ("--input", "lang=" + language))
            text = self.extract(pdf)
            for title in titles.values():
                self.assertIn(title, text)
            self.assertNotIn("教育背景", text)
            self.assertNotIn("Education", text)
        literal = self.fixture("literal-title", 'data + ("section-titles": (experience: "#pagebreak() **Work**"),)')
        pdf, _ = self.compile(literal)
        self.assertIn("#pagebreak() **Work**", self.extract(pdf))

    def test_overridden_titles_do_not_show_empty_sections(self):
        minimal = '(profile: (name: "Empty sections"), skills: (), experience: (), '
        minimal += '"section-titles": (education: "Hidden Education", skills: "Hidden Skills", '
        minimal += 'experience: "Hidden Work", "open-source": "Hidden Open Source", '
        minimal += 'projects: "Hidden Projects", publications: "Hidden Publications"))'
        source = self.fixture("hidden-titles", minimal)
        for language in ("zh", "en"):
            pdf, _ = self.compile(source, ("--input", "lang=" + language))
            self.assertEqual(self.extract(pdf).strip(), "Empty sections")

    def test_partial_contacts_and_label_fallbacks(self):
        profiles = (
            ('(name: "邮箱测试", email: "mail@example.com", phone: "  ",)', "mail@example.com", ("GitHub", "tel:")),
            ('(name: "电话测试", phone: "+8600000000000",)', "+8600000000000", ("GitHub", "mailto:")),
            ('(name: "链接测试", github: "https://example.com/sample/", website: "https://example.com/",)', "GitHub @sample", ("https://",)),
        )
        for index, (profile, expected, absent) in enumerate(profiles):
            source = self.fixture("contact-" + str(index), '(profile: ' + profile + ',)')
            pdf, _ = self.compile(source)
            text = self.extract(pdf)
            self.assertIn(expected, text)
            for value in absent:
                self.assertNotIn(value, text)

    def test_logo_and_no_logo_company_cards(self):
        for tone in ("warm", "cool", "neutral"):
            source = self.fixture("no-logo-" + tone, '(profile: (name: "卡片测试"), experience: ((title: "无图标公司", tone: "' + tone + '"),))')
            pdf, _ = self.compile(source)
            self.assertIn("无图标公司", self.extract(pdf))
        for company in self.data["experience"]:
            self.assertTrue((ROOT / "resume/assets/logos" / company["logo"]).is_file())

    def test_long_company_cards_do_not_overlap(self):
        item = ('(title: "Hachiware International Foundation for Community Events, '
                'Cultural Exchange and Neighborhood Development TITLE_END", '
                'detail: "ROLE_START Community Events and Public Program Coordination Intern", '
                'department: "International Partnerships and Neighborhood Programs DEPARTMENT_END", '
                'date: "20XX.XX - 20XX.XX", url: "https://example.com", '
                '"link-label": "Details", '
                'summary: ("SUMMARY_START A body paragraph follows the card.",))')
        for scale, logo in ((1.0, ""), (1.0, "chii.svg"), (0.90, "chii.svg"), (1.10, "chii.svg")):
            company = item if not logo else item + ' + (logo: "' + logo + '",)'
            source = self.fixture("long-card-" + str(scale) + ("-logo" if logo else ""),
                                  '(profile: (name: "Layout probe"), experience: (' + company + ',))')
            inputs = ("--input", "lang=en", "--input", "density=" + str(scale))
            pdf, _ = self.compile(source, inputs)
            words = list(ET.fromstring(run(self.pdftotext, "-bbox", str(pdf), "-").stdout)
                         .iter("{http://www.w3.org/1999/xhtml}word"))
            positions = {word.text: word.attrib for word in words}
            self.assertLess(float(positions["TITLE_END"]["yMax"]),
                            float(positions["ROLE_START"]["yMin"]), "公司名与岗位不得重叠")
            self.assertGreaterEqual(float(positions["SUMMARY_START"]["yMin"])
                                    - float(positions["DEPARTMENT_END"]["yMax"]), 3 * scale,
                                    "部门不得溢出卡片并压到正文")
        repeated = self.fixture("long-cards-single", '(profile: (name: "Layout probe"), experience: (' + item + ',) * 14)')
        _, result = self.compile(repeated, ("--input", "lang=en", "--input", "page-mode=single", "--input", "auto-fit=true"), success=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("超出一页的可读容量", result.stderr)

    def test_custom_fonts_and_defaults(self):
        source = self.fixture("custom-fonts", settings='settings + (fonts: (body: ("Source Han Sans",), heading: ("Source Han Serif",), contact: ("TeX Gyre Termes",)))')
        pdf, _ = self.compile(source)
        fonts = run(self.pdffonts, str(pdf)).stdout
        self.assertIn("SourceHanSansCN-Regular", fonts)
        self.assertIn("SourceHanSerifCN-Bold", fonts)
        self.assertNotIn("Inter", fonts)
        defaults = self.fixture("font-defaults", settings='(page-mode: "continuous", density: 1.0, auto-fit: false, min-density: 0.9)')
        _, _ = self.compile(defaults)

    def test_stars_rounding_and_literal_content(self):
        rounded = self.evaluate('{ import "/typst/template.typ": format-stars; (0, 999, 1000, 4749, 4750, 10000, 39926).map(format-stars) }')
        self.assertEqual(rounded, ["0", "999", "1k", "4.7k", "4.8k", "1w", "4w"])
        source = self.fixture("literal", '(profile: (name: "文字解析"), skills: ("#pagebreak() **加粗链接 [示例](https://example.com/inline)**",))')
        pdf, _ = self.compile(source)
        text = self.extract(pdf)
        self.assertIn("#pagebreak()", text)
        self.assertIn("加粗链接", text)
        self.assertNotIn("**", text)
        urls = run(self.pdfinfo, "-url", str(pdf)).stdout
        self.assertIn("https://example.com/inline", urls)

    def test_build_commands_and_dependencies(self):
        expected = {"pdf": "typst compile", "preview": "tinymist preview", "watch": "typst watch", "info": "typst eval", "example": "pdftoppm", "test": "tests/test_template.py"}
        for target, command in expected.items():
            output = run("make", "--dry-run", "--always-make", target).stdout
            self.assertIn(command, output)
            self.assertNotIn("versions/", output)
            self.assertNotIn("xelatex", output)
        self.assertIn("--font-path fonts", run("make", "--dry-run", "--always-make", "preview").stdout)

    def test_english_content_and_headings(self):
        data = self.evaluate('toml("tests/fixtures/content.en.toml")')
        pdf, _ = self.compile(self.source, ("--input", "lang=en"))
        text = self.extract(pdf)
        for heading in ("Education", "Skills", "Experience", "Open Source", "Projects", "Publications"):
            self.assertIn(heading, text)
        self.assertIsNone(re.search(r"[\u4e00-\u9fff]", text))
        normalized = plain(text)
        paragraphs = list(data["skills"])
        for section in ("experience", "open-source", "projects", "publications"):
            for item in data[section]:
                paragraphs.append(item["title"])
                paragraphs.extend(item.get("summary", []))
                paragraphs.extend(item.get("bullets", []))
                for project in item.get("projects", []):
                    paragraphs.append(project["title"])
                    paragraphs.extend(project.get("summary", []))
                    paragraphs.extend(project.get("bullets", []))
        for paragraph in paragraphs:
            self.assertIn(plain(paragraph), normalized)
        self.assertIn(data["profile"]["name"] + " - Resume", run(self.pdfinfo, str(pdf)).stdout)
        info = self.metrics(self.source, ("--input", "lang=en"))
        self.assertEqual(info["body-pt"], 10.5)
        _, invalid = self.compile(self.source, ("--input", "lang=unknown"), success=False)
        self.assertNotEqual(invalid.returncode, 0)
        self.assertIn("lang 可选", invalid.stderr)

    def test_original_preset_configuration_and_stroke_validation(self):
        settings = self.evaluate('toml("tests/fixtures/settings.original.toml")')
        self.assertEqual(settings["fonts"]["body"], ["TeX Gyre Termes", "Adobe Song Std"])
        self.assertEqual(settings["fonts"]["heading"], ["TeX Gyre Termes", "Adobe Heiti Std"])
        self.assertEqual(settings["fonts"]["contact"], ["Helvetica Neue", "Adobe Heiti Std"])
        self.assertEqual(settings["fonts"]["tag-han-stroke"], 0.32)
        source = self.fixture("invalid-tag-stroke", settings='settings + (fonts: (tag-han-stroke: -1),)')
        _, result = self.compile(source, success=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("fonts.tag-han-stroke", result.stderr)
        for target in ("en", "original", "original-en"):
            output = run("make", "--dry-run", "--always-make", target).stdout
            self.assertIn("--input lang=" + ("en" if "en" in target else "zh"), output)
            if "original" in target:
                self.assertIn("settings.original.toml", output)
                self.assertIn("check_original_fonts.py", output)

    def test_missing_original_fonts_fail_explicitly(self):
        namespace = runpy.run_path(str(ROOT / "scripts/check_original_fonts.py"))
        configured = subprocess.CompletedProcess([], 0, stdout=json.dumps(["Fixture Body", "Fixture Contact"]), stderr="")
        installed = subprocess.CompletedProcess([], 0, stdout="Fixture Body\n", stderr="")
        with mock.patch.object(namespace["subprocess"], "run", side_effect=[configured, installed]):
            with self.assertRaisesRegex(SystemExit, "原版字体未备齐：Fixture Contact"):
                namespace["main"]([])

    @unittest.skipUnless(os.environ.get("RUN_ORIGINAL_FONT_TESTS") == "1", "原版字体集成测试需本地自备字体")
    def test_original_fonts_in_both_languages(self):
        flags = [value for value in self.flags if value != "--ignore-system-fonts"]
        for language in ("zh", "en"):
            pdf = self.directory / ("original-" + language + ".pdf")
            run(self.typst, "compile", *flags, "--input", "settings=/tests/fixtures/settings.original.toml",
                "--input", "lang=" + language, str(self.source), str(pdf))
            fonts = run(self.pdffonts, str(pdf)).stdout
            for family in ("HelveticaNeue-Medium", "TeXGyreTermes-Regular", "TeXGyreTermes-Bold"):
                self.assertIn(family, fonts)
            if language == "zh":
                for family in ("AdobeSongStd-Light", "AdobeHeitiStd-Regular"):
                    self.assertIn(family, fonts)
            self.assertNotIn("InterVariable", fonts)
            self.assertNotIn("SourceHanSerifCN", fonts)

    def test_demo_metadata_and_url_destinations(self):
        info = run(self.pdfinfo, str(self.default_pdf)).stdout
        self.assertIn("Author:          " + self.data["profile"]["name"], info)
        urls = run(self.pdfinfo, "-url", str(self.default_pdf)).stdout
        destinations = [line.split()[-1] for line in urls.splitlines()[1:] if line.strip()]
        self.assertTrue(destinations)
        for url in destinations:
            self.assertTrue(url.startswith(("https://example.com", "mailto:hello@example.com", "tel:+8600000000000")), url)


class BuildBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (ROOT / "tmp").mkdir(exist_ok=True)
        cls.temp = tempfile.TemporaryDirectory(prefix="build-boundaries-", dir=ROOT / "tmp")
        cls.workspace = create_workspace(Path(cls.temp.name) / "workspace")
        cls.typst = executable("typst")

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_invalid_build_selectors_fail_before_build(self):
        for selector in ("FONT_PRESET=origina1", "FONT_PRESET=", "RESUME_LANG=unknown"):
            result = subprocess.run(["make", "--dry-run", "pdf", selector], cwd=self.workspace,
                                    text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0, selector + " 应明确报错")
            self.assertIn(selector.split("=")[0], result.stderr)

    def test_check_validates_selected_content_without_exporting(self):
        selected = self.workspace / "resume/private"
        selected.mkdir(exist_ok=True)
        content = selected / "check.toml"
        content.write_text('[profile]\nname = "Check Fixture"\n[[experience]]\n', encoding="utf-8")
        before = list((self.workspace / "output").rglob("*.pdf"))
        command = ["make", "check", "CONTENT=resume/private/check.toml", "TYPST=" + self.typst]
        result = subprocess.run(command, cwd=self.workspace, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("experience[1].title 缺少必填字段", result.stderr)
        content.write_text('[profile]\nname = "Check Fixture"\n', encoding="utf-8")
        result = subprocess.run(command, cwd=self.workspace, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("内容字段检查通过", result.stdout)
        self.assertEqual(list((self.workspace / "output").rglob("*.pdf")), before)

    def test_check_validates_section_titles(self):
        selected = self.workspace / "resume/private"
        selected.mkdir(exist_ok=True)
        content = selected / "titles.toml"
        command = ["make", "check", "CONTENT=resume/private/titles.toml", "TYPST=" + self.typst]
        for value, message in (('123', '必须是字符串'), ('"  "', '不能为空'), ('"Work History"', None)):
            content.write_text('[profile]\nname = "Title Fixture"\n[section-titles]\nexperience = ' + value + '\n',
                               encoding="utf-8")
            result = subprocess.run(command, cwd=self.workspace, text=True, capture_output=True)
            if message:
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("section-titles.experience " + message, result.stderr)
            else:
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_original_preflight_reads_custom_fonts(self):
        settings = self.workspace / "resume/settings.original.toml"
        saved = settings.read_text()
        try:
            settings.write_text((self.workspace / "resume/settings.toml").read_text())
            command = ["make", "--always-make", "original", "TYPST_FLAGS=--ignore-system-fonts", "TYPST=" + self.typst]
            result = subprocess.run(command, cwd=self.workspace, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn("warning:", result.stderr)
            self.assertTrue((self.workspace / "output/pdf/resume-original.pdf").is_file())
        finally:
            settings.write_text(saved)

    def test_missing_configured_font_fails_explicitly(self):
        settings = self.workspace / "resume/settings.original.toml"
        saved = settings.read_text()
        try:
            settings.write_text((self.workspace / "resume/settings.toml").read_text().replace('"Inter"', '"Missing Fixture Contact Font"'))
            result = subprocess.run(["make", "--always-make", "original", "TYPST_FLAGS=--ignore-system-fonts", "TYPST=" + self.typst],
                                    cwd=self.workspace, text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing Fixture Contact Font", result.stderr)
            self.assertNotIn("Adobe Song Std", result.stderr)
        finally:
            settings.write_text(saved)


if __name__ == "__main__":
    unittest.main(verbosity=2)
