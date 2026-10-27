# AGENTS.md

## 项目用途

独立中英文 Typst 简历模板。默认内容全部为非技术岗位虚构示例，以 Chiikawa 角色名作填空主题；三个公司 Logo 是自制文字徽标。内容采用活动策划与内容编辑方向，不沿用真实技术经历的技术栈、业务场景或成果叙述；时间使用 20XX 占位。维护公开示例时，不得写入维护者或其他人的真实姓名、联系方式、学校、公司或经历，不使用其他简历材料填充事实。

## 用户填写个人简历

用户明确要求用自己提供的真实资料填写个人简历时，优先在被忽略的 `resume/private/content.toml` / `content.en.toml` 中编辑；必要时先从公开示例复制。用户另有指定时遵从其文件选择；这与维护公开虚构示例是两种工作场景。只使用用户提供或明确确认的事实，信息不足时列出待补充项，不沿用虚构示例的职责、时间或成果。

使用 `make CONTENT=resume/private/content.toml` 或 `make en CONTENT=resume/private/content.en.toml` 显式选择个人内容，导出文件名为 `personal*.pdf`。不传 CONTENT 时仍编译公开示例。个人 PDF 导出到忽略的 `output/`，不覆盖 `docs/` 中的公开示例。未经用户明确要求，不提交、上传或发布含个人资料的内容文件或 PDF。中英文仅在用户要求的范围内同步，保留事实与贡献归属。

## 编辑入口

- `resume.typ`：唯一主入口，`--input lang=en` 切换英文，`--input content=resume/private/content.toml` 选择个人文件。
- `resume/content.toml` / `resume/content.en.toml`：中文／英文独立内容，普通文字，只支持 `**加粗**` 和 `[文字](https://地址)`。
- `resume/settings.toml`：开源字体、页面、密度与自动适配。
- `resume/settings.original.toml`：原版字体；用 `--input settings=resume/settings.original.toml` 选择。
- `typst/template.typ`：排版与内容测量，不放个人经历。

普通内容修改只改内容文件，松紧优先修改设置；只有视觉结构或模板行为变化才修改模板。同公司多个项目使用 `[[experience.projects]]`，每个项目连续展示自己的简介和成果。

## 视觉与字体

保留通栏浅底圆角公司卡片、左侧 Logo、公司名、下行岗位／日期／部门及右侧链接。暖色 `#fff9f4`、冷色 `#f7faff`、中性 `#f8f9fa`；无 Logo 仍显示卡片。公司卡片最小高度为 31pt，文字换行时随内容增高，不允许卡片文字与正文重叠。

默认长页，宽 210mm、水平页边距 14mm、垂直页边距 11mm。密度 1.00、正文 10.5pt，不因内容变长缩字。只有明确选择 single 时才限制一页；自动适配不得低于配置下限，超容量报错。

默认思源宋体正文、思源黑体标题与加粗、TeX Gyre Termes 英文、Inter 联系方式。设置的字体家族名以 `typst fonts --font-path fonts` 输出为准。开源预设须在关闭系统字体后无警告编译。原版预设使用 Adobe 宋体／黑体与 Helvetica Neue，仅从忽略的 fonts/local/ 或系统读取，禁止提交商业字体。原版标签中文沿用 0.32pt 描边加重，联系方式为 Helvetica Neue Medium、蓝色、9.4pt。

内容校验集中在 `typst/validate.typ`，编译、预览及 `make check CONTENT=...` 共用；报错必须指出字段路径和条目位置。新增内容字段时同步更新校验、模板和文档，不通过删除用户条目来绕过错误。

联系方式可全部省略；空章节隐藏。保留教育标签、链接、Stars 格式化与内容不执行 Typst 代码的边界。

内容文件的可选 `[section-titles]` 表支持 education、skills、experience、open-source、projects、publications 六个章节的非空纯文本标题覆盖；未配置时保留对应语言默认值，空章节仍隐藏。更改章节名称时优先使用此配置，不修改模板。

## 验证与导出

```bash
make
make en
make original
make original-en
make info
make check
make doctor
make test
make example
```

测试使用 `tests/fixtures/` 的固定合成数据，与用户内容及 settings 文件独立。不要为了通过测试补回用户删除的章节，也不要求中英文条目数量相同。`make test` 同时验证干净临时副本中的个人填写流程。

首次使用先运行 `make doctor`；预览和测试可分别加 `DOCTOR_FLAGS=--preview`、`DOCTOR_FLAGS=--tests`。doctor 读取当前字体设置，缺少必需依赖时必须失败，不把可选工具缺失当成导出失败。

测试需 Python 3.9+、Typst、Poppler；默认开源测试不读系统字体，原版集成测试需显式 RUN_ORIGINAL_FONT_TESTS=1。模板修改后必须渲染 PDF 并检查中文、卡片、对齐、行距与底部边界，不能以编译成功代替视觉检查。

`output/`、`tmp/`、`fonts/local/`、`resume/private/` 为忽略的本地产物。`make example` 只接受对应语言的默认公开内容路径，不接受自定义 CONTENT。`docs/` 中两种语言、两套字体的 PDF 与 PNG 都是公开虚构示例；不要用真实简历覆盖后提交。刷新示例前确认内容与 PDF 元数据、链接都适合公开。未经用户要求不要创建远端仓库或发布。

源码 MIT；字体与图标保留各自许可证。新仓库提交使用公开身份与隐私邮箱，不沿用工作邮箱。
