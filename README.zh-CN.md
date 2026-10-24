# aubergine-resume-typst

[English](README.md) · **简体中文**

一份把内容和排版分开的中英文 Typst 简历模板。用 TOML 填写经历，也可以交给 Agent 协助编辑，再通过同一个入口预览、导出。

保留浅底公司卡片、教育标签、独立项目和可点击链接。支持固定 A4 宽度的长页，以及可选的一页 A4 模式；提供开源字体与原版字体两套预设。

[样式预览](#样式预览) · [快速开始](#快速开始) · [Agent 协作](#与-agent-协作编辑) · [填写内容](#填写内容) · [页面与字体](#页面与字体) · [常见问题](#常见问题)

## 样式预览

下面是**原版字体**的中文与英文示例。点击截图查看大图，或打开对应 PDF 查看文字与链接。

<table>
  <tr>
    <th width="50%">中文 · 原版字体</th>
    <th width="50%">English · Original fonts</th>
  </tr>
  <tr>
    <td valign="top">
      <a href="docs/preview-original.png"><img src="docs/preview-original.png" alt="中文简历完整截图：教育标签、三种公司卡片、项目与论文排版" width="100%"></a>
    </td>
    <td valign="top">
      <a href="docs/preview-original-en.png"><img src="docs/preview-original-en.png" alt="English resume screenshot with education, experience cards, projects and publications" width="100%"></a>
    </td>
  </tr>
  <tr>
    <td align="center"><a href="docs/example-original.pdf">查看中文 PDF</a></td>
    <td align="center"><a href="docs/example-original-en.pdf">View English PDF</a></td>
  </tr>
</table>

默认编译使用随仓库提供的**开源字体**，无需准备商业字体。原版字体预设需要自行提供字体，两者的字体搭配见[页面与字体](#页面与字体)。

<details>
<summary>展开查看开源字体版的中英文截图</summary>

<table>
  <tr>
    <th width="50%">中文 · 开源字体</th>
    <th width="50%">English · Open-source fonts</th>
  </tr>
  <tr>
    <td valign="top">
      <a href="docs/preview.png"><img src="docs/preview.png" alt="中文简历截图，使用思源宋体、思源黑体和 Inter" width="100%"></a>
    </td>
    <td valign="top">
      <a href="docs/preview-en.png"><img src="docs/preview-en.png" alt="English resume screenshot using the bundled open-source font preset" width="100%"></a>
    </td>
  </tr>
  <tr>
    <td align="center"><a href="docs/example.pdf">查看中文 PDF</a></td>
    <td align="center"><a href="docs/example-en.pdf">View English PDF</a></td>
  </tr>
</table>

</details>

所有截图均为虚构的活动策划与内容编辑示例，时间使用 `20XX` 占位，Star 数量仅展示格式。Chiikawa 角色名作为填空主题；「吉／哈／乌」为自制文字徽标，不含官方角色图片，本项目与相关权利方无关联。

也可从 [Releases](https://github.com/auberginewly/aubergine-resume-typst/releases) 下载示例 PDF 与截图；版本变化见 [更新记录](CHANGELOG.md)。

## 快速开始

### 1. 获取模板

点击仓库右上角 **Use this template → Create a new repository**，创建自己的仓库；用于个人简历时可以选择 Private。也可以[下载 ZIP](https://github.com/auberginewly/aubergine-resume-typst/archive/refs/heads/main.zip) 后解压，或直接克隆：

```bash
git clone https://github.com/auberginewly/aubergine-resume-typst.git
cd aubergine-resume-typst
```

后面的命令都在仓库根目录执行。

### 2. 准备工具

开源字体版导出需要 [Typst](https://github.com/typst/typst/releases) 和 GNU Make。原版字体版还需 Python 3.9+ 运行字体检查脚本，实时预览另需 [Tinymist](https://github.com/Myriad-Dreamin/tinymist/releases)。macOS 可使用 Homebrew：

```bash
brew install typst tinymist
```

Linux 用户安装对应平台的 Typst、Tinymist 与 GNU Make 后，在仓库根目录运行下面的命令。Makefile 使用 `cp`、`mkdir`、`rm` 等 POSIX 命令；Windows 用户需要在提供这些命令的环境中运行 Make，也可使用下方的原生 Typst 命令直接编译。

个人文件初始化和环境检查需要 Python 3.9+；若系统没有 Python，可在 macOS 上执行 `brew install python`。安装后运行：

```bash
make doctor                                      # 检查导出工具、当前字体与字体校验值
make doctor DOCTOR_FLAGS=--preview               # 另外要求 Tinymist
make doctor DOCTOR_FLAGS=--tests                 # 另外要求测试所需 Poppler
make doctor FONT_PRESET=original                 # 检查原版字体设置
make doctor TYPST_FLAGS=--ignore-system-fonts     # 排除系统字体后检查
```

缺少导出必需工具或当前字体时会报错并返回非零退出码；默认只提示未安装的预览、测试工具。原生 Windows 用户也可直接运行 `python scripts/doctor.py`，导出仍可使用下方的原生 Typst 命令。

### 3. 填写自己的内容

先初始化被 Git 忽略的个人目录，保留公开示例：

```bash
make init
```

命令只会从公开示例创建缺失的 `resume/private/content.toml` 和 `resume/private/content.en.toml`。可以重复运行：已有文件保持原样并提示跳过；只存在一种语言时，仅补齐另一份文件。不使用 Make 时，可运行 `python3 scripts/init_personal.py`（Windows 可用 `python scripts/init_personal.py`）。

随后编辑 `resume/private/content.toml` 和 `resume/private/content.en.toml`。两个文件都需要用自己的事实替换示例；默认命令仍读取公开虚构示例，不会自动切换到个人内容。

| 想改什么 | 编辑哪个文件 |
| --- | --- |
| 中文个人内容 | `resume/private/content.toml`，由上一步创建 |
| 英文个人内容 | `resume/private/content.en.toml`，由上一步创建 |
| 开源字体、页面模式与整体松紧 | [`resume/settings.toml`](resume/settings.toml) |
| 原版字体、页面模式与整体松紧 | [`resume/settings.original.toml`](resume/settings.original.toml) |

中英文内容分别维护。切换语言会切换章节标题与 PDF 文档标题，不会自动翻译文字。不传 `CONTENT` 时会同时选择对应语言的公开示例；使用个人文件时，需要显式指定对应的 `CONTENT` 路径。

### 4. 预览并导出

```bash
make preview CONTENT=resume/private/content.toml
make CONTENT=resume/private/content.toml
make en CONTENT=resume/private/content.en.toml
```

个人文件导出到 `output/pdf/personal.pdf`、`personal-en.pdf`；原版字体对应 `personal-original.pdf`、`personal-original-en.pdf`。`CONTENT` 也适用于 `preview`、`watch`、`info` 和原版字体命令。

预览进程需要保持运行，按 `Ctrl+C` 停止。浏览器预览不会自动生成 PDF；定稿后再运行导出命令，或用 `make watch CONTENT=resume/private/content.toml` 持续更新个人 PDF。

不传 `CONTENT` 时，下面的命令仍导出公开虚构示例：

| 字体预设 | 中文导出 | 英文导出 | 输出位置 |
| --- | --- | --- | --- |
| 开源字体 | `make` | `make en` | `output/pdf/resume.pdf`、`resume-en.pdf` |
| 原版字体，需自备 | `make original` | `make original-en` | `output/pdf/resume-original.pdf`、`resume-original-en.pdf` |

`RESUME_LANG` 仅接受 `zh` / `en`，`FONT_PRESET` 仅接受 `open-source` / `original`；无效值会明确报错。预览、持续编译与布局信息也支持选择语言和字体：

```bash
make preview RESUME_LANG=en FONT_PRESET=original
make watch RESUME_LANG=en FONT_PRESET=original
make info RESUME_LANG=en FONT_PRESET=original
```

<details>
<summary>直接使用 Typst，或在 VS Code 中编辑</summary>

不使用 Make 时，可在仓库根目录运行：

```bash
# 中文，开源字体
typst compile --root . --font-path fonts resume.typ output.pdf

# 自己的中文内容，路径相对于仓库根目录
typst compile --root . --font-path fonts --input content=resume/private/content.toml resume.typ output.pdf

# 英文，开源字体
typst compile --root . --font-path fonts --input lang=en resume.typ output-en.pdf

# 中文，原版字体，需自行准备字体
typst compile --root . --font-path fonts --input settings=resume/settings.original.toml resume.typ output-original.pdf
```

用 VS Code 打开整个仓库，安装推荐的 Tinymist 扩展，再打开 `resume.typ` 的预览。仓库已配置项目根目录与字体路径；默认入口显示中文开源字体版。需要其他组合时，使用上面的 `make preview` 命令可明确选择参数。

</details>

## 与 Agent 协作编辑

项目的编辑约定在 [`AGENTS.md`](AGENTS.md)。开始时先让 Agent 阅读它，再说明要编辑的语言、字体预设和目标。无需先让 Agent 重建模板；通常只需要更新内容 TOML，排版要求变化时再调整设置。

建议每轮提供一段经历或一个明确目标，检查内容和 PDF 后再继续下一轮。下面的提示词可以直接复制，替换方括号中的信息。

### 用自己的资料替换示例

```text
请先阅读 AGENTS.md 和 README.zh-CN.md，再用以下资料更新中文简历。

编辑文件：resume/private/content.toml；若不存在，先从中文示例复制。
资料：[粘贴我的教育、经历、项目和联系方式]
求职方向：[填写目标岗位]

要求：
- 只使用我提供的事实，不编造职责、时间、指标、技术栈或成果。
- 缺少必要信息时列出待补充项；不要把虚构示例当成我的经历。
- 本轮只改中文内容，保留现有字体、公司卡片和章节结构。
- 保持长页模式，不为了压成一页擅自删内容或缩字。
- 使用 make CONTENT=resume/private/content.toml 导出，渲染 PDF 检查文字、对齐和底部边界。
- 交付修改摘要、PDF 路径和仍需补充的信息。
- 不覆盖 docs/ 中的公开示例，不提交或上传我的个人资料。
```

若使用原版字体，把导出命令改为 `make original CONTENT=resume/private/content.toml`；字体缺失时应先说明缺少哪些字体。

### 润色一段经历

```text
请阅读 AGENTS.md，润色 resume/private/content.toml 中的 [公司或项目名]。

目标：[例如突出活动组织与内容编辑能力，减少重复表述]

保持职责范围、时间、成果和贡献归属不变，用“问题／工作内容、方法、结果”
组织描述。没有数据的地方不要补数字。先检查已有内容能支持哪些表述；
如果需要更多事实，请列出具体问题。其他经历、字体和排版保持原样。
完成后使用 make CONTENT=resume/private/content.toml 编译并检查 PDF。
```

### 同步英文版

```text
请以 resume/private/content.toml 中已确认的中文内容为事实来源，
更新 resume/private/content.en.toml，使用自然、简洁的英文简历表达。

不增加中文版本没有的职责、指标或成果；日期和贡献状态保持一致。
机构或岗位存在多个合理译法时，列出需要我确认的名称。
保留两个独立内容文件，不修改中文事实。
使用 make en CONTENT=resume/private/content.en.toml 导出，检查英文标题、换行、链接和卡片是否溢出。
```

### 调整篇幅与排版

```text
请先阅读 AGENTS.md，检查 resume/private/content.toml 的排版。

本轮目标：[例如正文略微收紧／切换为一页 A4／调整公司卡片]
使用字体：[开源／原版]

优先修改对应的 settings 文件，只有目标涉及视觉结构时才改模板。
如果需要一页，先评估内容是否能在 density=1.00、min-density=0.90 下容纳；
放不下时指出需要精简的段落及理由，不继续缩小字号，也不裁剪内容。
导出时显式使用 CONTENT=resume/private/content.toml。
修改模板后运行 make test，并渲染 PDF 检查最终效果。
```

Agent 修改后的检查重点是：事实是否准确、重点是否清楚、中英文是否一致，以及 PDF 是否存在缺字、异常换行或边界溢出。个人内容放在被忽略的 `resume/private/`，日常个人导出放在被忽略的 `output/`；`docs/` 用于仓库的公开虚构示例。

## 填写内容

内容文件使用合法 TOML。只支持普通文字、`**加粗**` 和 `[文字](https://地址)`；不会执行字符串中的 Typst 代码。

```toml
summary = ["**项目简介**：一句话介绍项目，附上 [作品说明](https://example.com/guide)。"]
bullets = [
  "**我负责的部分**：说明工作内容、采用的方法和可验证的结果。",
  "**另一项成果**：补充相关产出。",
]
```

`summary` 的每项是一段正文，`bullets` 的每项是一条圆点描述。双引号写成 `\"`；多行字符串可使用 TOML 三引号。顶层 `skills` 必须放在 `[profile]` 等表声明之前。

### 内容字段检查

编译、实时预览和导出会共用同一份字段校验。只想检查 TOML 内容而不生成 PDF，可以运行：

```bash
make check                                      # 中文公开示例
make check RESUME_LANG=en                        # 英文公开示例
make check CONTENT=resume/private/content.toml   # 个人内容
```

字段错误会指出从 1 开始的条目位置，例如 `experience[2].title 缺少必填字段`；`tone` 拼写错误、数字联系方式、非数组的段落、错误的 Stars 类型和未知字段也会明确报错。TOML 语法错误则由 Typst 指向文件及行号。

| 内容 | 字段约定 |
| --- | --- |
| `[profile]` | `name` 为非空字符串；其他联系方式为可选字符串 |
| 顶层 `skills`，条目的 `summary` / `bullets`，教育 `tags` | 字符串数组，可为空或省略 |
| `[[education]]` | `school`、`detail`、`date` 为必填非空字符串 |
| `[[experience]]`、`[[open-source]]`、`[[projects]]` 及嵌套项目 | `title` 为必填非空字符串；其他文字字段为可选字符串 |
| `[[publications]]` | `title`、`detail` 为必填非空字符串 |
| `tone` | `warm` / `cool` / `neutral` |
| `stars` | 不小于 0 的整数，例如 `stars = 2345`，不写 `"2.3k"` |

校验只判断字段和类型，不判断事实真伪，也不判断内容能否放进一页；布局仍需编译并查看 PDF。字段名区分大小写，不支持的字段会提示检查拼写。

### 联系方式与章节

`[profile]` 中只有 `name` 必填。电话、邮箱、GitHub、网站可逐项省略或留空，对应图标和间距会自动隐藏；全部省略时只显示姓名。

- `phone-display` 不填时显示 `phone`。
- `github-name` 不填时使用 URL 的最后一段。
- `website-label` 不填时去掉协议与首尾斜线。
- 章节条目为空或未填写时，章节标题自动隐藏。

教育的 `tags` 是可选数组，学校、标签、专业和学历同排，日期右对齐。完整字段可参考[中文公开示例](resume/content.toml)和[英文公开示例](resume/content.en.toml)。

### 公司卡片与多个项目

```toml
[[experience]]
title = "吉伊生活社（虚构）"
detail = "活动策划实习生"
department = "街区活动组"
date = "20XX.XX — 20XX.XX"
logo = "chii.svg"
tone = "warm"
url = "https://example.com/work"
link-label = "示例作品"
summary = ["**职责示例**：介绍这段虚构经历。"]

[[experience.projects]]
title = "草地音乐会｜活动特刊"
summary = ["**项目简介**：音乐会特刊的介绍。"]
bullets = ["**工作内容**：这个项目的工作与产出。"]

[[experience.projects]]
title = "小镇散步册｜季节路线指南"
summary = ["**项目简介**：散步指南的介绍。"]
bullets = ["**工作内容**：另一个项目的工作与产出。"]
```

Logo 放在 `resume/assets/logos/`，填写文件名即可。支持 SVG、PNG 等 Typst 支持的图片格式；省略 `logo` 后仍保留浅底卡片。三个示例文字徽标可直接替换。

`tone` 可选 `warm`（暖色）、`cool`（冷色）、`neutral`（中性，默认）。部门、日期和右侧链接也可省略。同公司的项目用 `[[experience.projects]]`，各自连续展示标题、简介与成果。公司卡片以 31pt 为最小高度，较长的公司名、岗位或部门换行时自动增高。

### 项目与开源贡献

使用 `[[projects]]`、`[[open-source]]` 填写条目，字段可参考示例。`repository` 保存完整仓库 URL，在标题右侧显示可点击地址；标题可写成「项目名｜项目定位」。

开源项目填写整数 `stars` 后，数量紧接定位显示，如 `2345` → `2.3k Stars`、`12000` → `1.2w Stars`。个人项目可省略 `stars`。数量不会自动联网刷新，实际填写时请在内容注释中记录核验日期与来源。

贡献状态写在描述中；尚未合并的工作明确注明「PR 已提交，尚未合并」。

## 页面与字体

### 长页与一页 A4

```toml
page-mode = "continuous"
density = 1.00
auto-fit = false
min-density = 0.90
```

默认 `continuous` 模式：页面宽 210mm，左右边距 14mm，上下边距 11mm，高度随内容增长。密度为 1.00 时，正文 10.5pt；内容增加不会自动缩字。

需要一页 A4 时，在所用的 settings 文件中改为：

```toml
page-mode = "single"
density = 1.00
auto-fit = true
min-density = 0.90
```

一页模式会在 `min-density` 与 `density` 之间选择能容纳内容的最大比例。默认下限 0.90 对应正文 9.45pt，超出容量会明确报错。

`density` 同比例调整字号、行距与段距，须满足 `0.85 ≤ min-density ≤ density ≤ 1.20`。自动适配只在 `single` 模式生效。`make info` 可查看实际采用的密度、字号和内容高度。

### 两套字体预设

| 用途 | 开源字体，默认 | 原版字体，需自备 |
| --- | --- | --- |
| 中文正文 | 思源宋体 | Adobe Song Std |
| 中文标题与加粗 | 思源黑体 | Adobe Heiti Std |
| 英文 | TeX Gyre Termes | TeX Gyre Termes |
| 联系方式 | Inter | Helvetica Neue Medium |

原版联系方式使用 500 字重、蓝色、9.4pt；Adobe 宋体没有独立粗体，教育标签中文通过 `fonts.tag-han-stroke = 0.32` 描边加重。开源版使用真实粗体，默认描边为 0。

开源字体及许可证随仓库提供。原版字体由使用者自行取得授权，放入被 Git 忽略的 `fonts/local/`，或安装到系统；仓库不分发 Adobe 商业字体或 Helvetica Neue。`make original` / `make original-en` 会根据当前设置文件检查 `body`、`heading`、`contact` 中的字体是否齐备；修改字体后，检查也随配置更新。

<details>
<summary>自定义字体与字体路径</summary>

在所用的 settings 文件中修改字体家族名：

```toml
[fonts]
body = ["TeX Gyre Termes", "Source Han Serif"]
heading = ["TeX Gyre Termes", "Source Han Sans"]
contact = ["Inter", "Source Han Sans"]
```

每项是非空字体名数组，从前向后匹配；省略 `[fonts]` 时采用开源预设。名称应使用 Typst 识别的家族名，而非文件名：

```bash
typst fonts --font-path fonts
```

`body` 控制正文与教育标签，`heading` 控制姓名、标题和加粗，`contact` 控制联系方式。`Source Han Serif` / `Source Han Sans` 的家族名不含文件名中的 `CN`。

验证默认编译不依赖系统字体：

```bash
make clean
make TYPST_FLAGS=--ignore-system-fonts
```

</details>

## 常见问题

<details>
<summary>原版字体提示缺失，怎么办？</summary>

先运行 `typst fonts --font-path fonts` 确认家族名。将有授权的字体放入 `fonts/local/`，或安装到系统后重新编译。只需开箱使用时运行 `make` / `make en`，采用随附的开源字体。

</details>

<details>
<summary>英文版会自动跟着中文更新吗？</summary>

不会。两份内容文件独立维护，适合分别调整中英文表达。可以让 Agent 以已确认的中文事实为依据更新英文，再检查岗位名称、日期、指标和贡献状态是否一致。

</details>

<details>
<summary>一页放不下，或者预览不更新怎么办？</summary>

一页容量不足时会在编译或预览终端报错；请精简内容或切回 `continuous`。预览停留在旧内容时，先检查终端中的 TOML 语法、字体或容量错误。保存后只更新浏览器预览的情况，需要再运行导出命令生成 PDF。

</details>

## 开发与维护

每次 push 和 Pull Request 都会运行 [Template checks](https://github.com/auberginewly/aubergine-resume-typst/actions/workflows/test.yml)：校验随附字体、执行隔离测试，并在不读取系统字体的 Linux 环境中编译中英文示例。CI 使用 Typst 0.15.1，不需要商业字体。

测试需要 Python 3.9+、Typst，以及 Poppler 的 `pdfinfo`、`pdffonts`、`pdftotext`；刷新截图还需 `pdftoppm`。macOS 可运行 `brew install poppler`。

```bash
make test
# 本地原版字体齐备后，额外验证中英文原版字体
RUN_ORIGINAL_FONT_TESTS=1 make test
```

测试使用 `tests/fixtures/` 中独立的合成数据，覆盖中英文内容完整导出、标题切换、字体嵌入、页面与边界、密度与一页适配、可选联系方式、空章节、多个项目、长公司卡片、无 Logo 卡片、行内链接和 Stars。默认开源测试不读取系统字体，原版集成测试需显式开启。

另有个人填写流程测试：在不包含本地商业字体的临时副本中，删除可选章节、让中英文条目数量不同、修改密度和字体，再验证四种导出与模板测试。日常编辑不会改变固定测试数据，也无需为了通过测试补回不需要的章节。当前填写内容的语法和布局通过 `make` / `make en` 等导出命令检查；测试不会判断用户经历的事实是否准确。

工具不在 PATH 时，可通过对应大写环境变量指定，例如 `PDFTOTEXT=/path/to/pdftotext make test`。模板修改后，还应渲染 PDF 检查字形、卡片、标签、对齐和底部边界。

<details>
<summary>刷新公开示例与文字徽标</summary>

确认内容全部为可公开的虚构示例后，再执行：

```bash
make example
make example RESUME_LANG=en
make example FONT_PRESET=original
make example RESUME_LANG=en FONT_PRESET=original
```

命令会更新 `docs/` 中对应的 PDF 和 PNG；`example` 拒绝自定义 `CONTENT`，防止把个人导出复制进公开文档。公开内容文件本身仍需人工确认适合发布。修改文字徽标后，用 `python3 scripts/generate_badges.py` 重新生成。`make clean` 只删除日常 `output/` 导出，不删除公开示例。

</details>

### 目录

```text
resume.typ                    唯一主入口
resume/content.toml           中文公开示例
resume/content.en.toml        英文公开示例
resume/private/               个人内容，忽略提交
resume/settings.toml          开源字体与页面配置
resume/settings.original.toml 原版字体与页面配置
resume/assets/                图标与自制文字徽标
typst/template.typ            排版、内容测量与语言切换
typst/validate.typ            内容字段校验
fonts/                        开源字体、许可证与校验值
docs/                         公开虚构示例 PDF 与截图
scripts/                      环境检查、字体检查与徽标生成
tests/                        模板行为与个人填写流程测试
tests/fixtures/               独立的合成测试内容与设置
output/                       日常导出，忽略提交
```

## License

源码采用 [MIT License](LICENSE)。字体遵循各自随附许可证，详见[字体说明](fonts/README.md)；Feather 图标保留其 [MIT 许可证](resume/assets/icons/LICENSE.txt)。
