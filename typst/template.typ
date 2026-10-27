// 数据驱动的中文简历模板。内容只解析加粗与 HTTP(S) 行内链接，不执行代码。
#import "validate.typ": validate-content
#let default-fonts = (
  body: ("TeX Gyre Termes", "Source Han Serif"),
  heading: ("TeX Gyre Termes", "Source Han Sans"),
  contact: ("Inter", "Source Han Sans"),
  tag-han-stroke: 0.0,
)

#let resolve-fonts(settings) = {
  let custom = settings.at("fonts", default: (:))
  let fonts = default-fonts + custom
  for key in ("body", "heading", "contact") {
    let names = fonts.at(key)
    assert(type(names) == array and names.len() > 0,
      message: "fonts." + key + " 必须是非空字体名称数组。")
    assert(names.all(name => type(name) == str and name.trim() != ""),
      message: "字体名称必须是非空字符串。")
  }
  assert(type(fonts.tag-han-stroke) in (int, float) and fonts.tag-han-stroke >= 0 and fonts.tag-han-stroke <= 1,
    message: "fonts.tag-han-stroke 必须为 0 到 1 之间的描边宽度（pt）。")
  fonts
}

// 正整数 Star 数量按一位小数四舍五入，万以上用 w，千以上用 k。
#let format-stars(count) = {
  let value = int(str(count).replace(",", ""))
  let divisor = if value >= 10000 { 10000 } else if value >= 1000 { 1000 } else { 1 }
  let suffix = if value >= 10000 { "w" } else if value >= 1000 { "k" } else { "" }
  let rounded = calc.floor(value / divisor * 10 + 0.5) / 10
  (if rounded == calc.floor(rounded) { str(int(rounded)) } else { str(rounded) }) + suffix
}

// 联系方式可逐项省略；先过滤空项，再插入间距。
#let contact-line(profile, scale: 1.0, font: default-fonts.contact, language: "zh") = {
  let unit = 1pt * scale
  let color = rgb("#285477")
  let contacts = ()
  let value(key) = profile.at(key, default: "").trim()
  if value("phone") != "" {
    contacts.push(("phone", "tel:" + value("phone"),
      if value("phone-display") != "" { value("phone-display") } else { value("phone") }))
  }
  if value("email") != "" {
    contacts.push(("mail", "mailto:" + value("email"), value("email")))
  }
  if value("github") != "" {
    let name = if value("github-name") != "" { value("github-name") }
      else { value("github").trim("/").split("/").last() }
    contacts.push(("github", value("github"), "GitHub @" + name))
  }
  if value("website") != "" {
    let label = if value("website-label") != "" { value("website-label") }
      else { value("website").replace(regex("^https?://"), "").trim("/") }
    contacts.push(("globe", value("website"), label))
  }
  if contacts.len() == 0 { return none }
  let item(icon, url, label) = link(url)[
    #box(width: 9 * unit, height: 9 * unit, baseline: 1.8 * unit)[
      #image(
        bytes(read("/resume/assets/icons/" + icon + ".svg").replace("currentColor", color.to-hex())),
        format: "svg", width: 9 * unit, height: 9 * unit,
        alt: if language == "en" { (phone: "Phone", mail: "Email", github: "GitHub", globe: "Website").at(icon) }
          else { (phone: "电话", mail: "邮箱", github: "GitHub", globe: "网站").at(icon) },
      )
    ]
    #h(2.5 * unit)
    #label
  ]
  text(font: font, size: 9.4 * unit, weight: 500,
    fill: color, top-edge: 7.36 * unit, bottom-edge: -1.84 * unit)[
    #show link: set text(fill: color)
    #for (index, contact) in contacts.enumerate() {
      if index > 0 { h(1.2em) }
      item(..contact)
    }
  ]
}

#let rich(value, font: default-fonts.heading) = {
  let inline(value) = {
    let cursor = 0
    for found in value.matches(regex("\\[([^\\]]+)\\]\\((https?://[^\\s)]+)\\)")) {
      text(value.slice(cursor, found.start))
      link(found.captures.at(1), found.captures.at(0))
      cursor = found.end
    }
    text(value.slice(cursor))
  }
  let parts = value.split("**")
  for (i, part) in parts.enumerate() {
    if calc.odd(i) { text(font: font, weight: "bold", inline(part)) } else { inline(part) }
  }
}

#let contents(data, scale, fonts: default-fonts, language: "zh") = {
  let labels = if language == "en" {
    (education: "Education", skills: "Skills", experience: "Experience", "open-source": "Open Source",
      projects: "Projects", publications: "Publications", details: "Details", project: "Project")
  } else {
    (education: "教育背景", skills: "个人技能", experience: "实习经历", "open-source": "开源贡献",
      projects: "项目经历", publications: "论文成果", details: "详细产出", project: "项目链接")
  }
  labels += data.at("section-titles", default: (:))
  let body-font = fonts.body
  let bold-font = fonts.heading
  let styled(value) = rich(value, font: bold-font)
  let unit = 1pt * scale
  let ink = rgb("#222222")
  let blue = rgb("#285477")
  set text(font: body-font, size: 10.5 * unit,
    fill: ink, lang: language, top-edge: 0.8em, bottom-edge: -0.2em)
  set par(leading: 2.2 * unit, spacing: 0pt, justify: false)
  show link: set text(fill: blue)

  let section(title) = block(above: 7.5 * unit, below: 3.5 * unit, breakable: false)[
    #text(font: bold-font, size: 12.5 * unit, weight: "bold", title)
    #v(1.5 * unit)
    #line(length: 100%, stroke: 0.4pt + rgb("#aab2b9"))
  ]
  // 固定高度并明确基线，标签中心落在相邻正文的字面中心。
  // bounds 让数字和中文都按实际字形居中，避免默认行框使标签显得下沉。
  let tag(label) = box(fill: rgb("#eaf1f8"), radius: 1.5 * unit,
    height: 11 * unit, baseline: (at: bottom, shift: 1.5 * unit), inset: (x: 3 * unit, y: 0pt))[
    #align(center + horizon)[
      #text(font: body-font, size: 8.8 * unit, weight: "bold",
        top-edge: "bounds", bottom-edge: "bounds",
        fill: blue)[
        #show regex("\\p{Han}+"): set text(stroke: if fonts.tag-han-stroke > 0 {
          fonts.tag-han-stroke * unit + blue
        } else { none })
        #label
      ]
    ]
  ]
  let entry(title, detail: "", date: "", url: "", label: labels.project, repository: "", stars: "") = {
    block(above: 3 * unit, below: 2.5 * unit, breakable: false)[
      #if repository != "" {
        // 项目定位后显示 Stars，右侧显示完整仓库地址。
        grid(columns: (1fr, auto), column-gutter: 8 * unit,
          text(font: bold-font, weight: "bold")[
            #styled(title)#if stars != "" [ ｜ #box[#format-stars(stars) Stars]]
          ],
          text(size: 9 * unit)[
            #link(repository, repository.replace(regex("^https?://"), ""))
            #if url != "" and url != repository [#h(1em)#link(url, label)]
          ])
        if detail != "" { v(2 * unit); text(size: 9.2 * unit, styled(detail)) }
      } else {
        grid(columns: (1fr, auto), column-gutter: 8 * unit,
          text(font: bold-font, weight: "bold", styled(title)),
          text(size: 9 * unit, if date != "" { date }
            else if detail == "" and url != "" { link(url, label) }))
        if detail != "" or (url != "" and date != "") {
          v(2 * unit)
          grid(columns: (1fr, auto), column-gutter: 8 * unit,
            text(size: 9.2 * unit, styled(detail)),
            if url != "" { text(size: 9 * unit, link(url, label)) })
        }
      }
    ]
  }
  // 浅底公司卡片：31pt 为最小高度，文字换行后随内容增高。
  let company-header(item) = {
    let logo = item.at("logo", default: "")
    let tint = (warm: rgb("#fff9f4"), cool: rgb("#f7faff"), neutral: rgb("#f8f9fa"))
      .at(item.at("tone", default: "neutral"))
    let date = item.at("date", default: "")
    let department = item.at("department", default: "")
    let url = item.at("url", default: "")
    let height = 31 * unit
    block(width: 100%, fill: tint, radius: 3 * unit,
      inset: (x: 8.5 * unit, y: 0pt), above: 3 * unit, below: 5 * unit, breakable: false)[
      #grid(columns: if logo != "" { (19 * unit, 1fr, auto, 0pt) } else { (1fr, auto, 0pt) },
        rows: (auto,),
        column-gutter: if logo != "" { (8.5 * unit, 8.5 * unit, 0pt) } else { (8.5 * unit, 0pt) },
        ..if logo != "" { (grid.cell(align: center + horizon)[
          #image("/resume/assets/logos/" + logo, width: 17 * unit, height: 16 * unit, fit: "contain")
        ],) } else { () },
        grid.cell(align: left + horizon, inset: (y: 4 * unit))[
          #stack(spacing: 2 * unit,
            text(font: bold-font, size: 10.5 * unit, weight: "bold", item.title),
            text(size: 9 * unit)[#styled(item.at("detail", default: ""))#if date != "" [ ｜ #date]#if department != "" [ ｜ #department]],
          )
        ],
        grid.cell(align: right + horizon)[
          #if url != "" { text(size: 8.4 * unit, link(url)[#item.at("link-label", default: labels.details) →]) }
        ],
        // 零宽占位只约束最小行高，不限制其他单元格的自然高度。
        box(width: 0pt, height: height),
      )
    ]
  }
  let paragraphs(items) = {
    for item in items { block(below: 2 * unit, styled(item)) }
  }
  let bullets(items) = {
    for item in items {
      block(below: 2.8 * unit)[
        #grid(columns: (6 * unit, 1fr), column-gutter: 2 * unit, [•], styled(item))
      ]
    }
  }

  align(center)[
    #text(font: bold-font, size: 20 * unit, weight: "bold", data.profile.name)
    #let contacts = contact-line(data.profile, scale: scale, font: fonts.contact, language: language)
    #if contacts != none { v(4 * unit); contacts }
  ]

  if data.at("education", default: ()).len() > 0 {
    section(labels.education)
    for item in data.education {
      block(above: 3 * unit, below: 2.5 * unit, breakable: false)[
        #grid(columns: (1fr, auto), column-gutter: 8 * unit,
          [#text(font: bold-font, weight: "bold", item.school)#h(0.5em)#for label in item.at("tags", default: ()) {
            tag(label)
            h(0.35em)
          }#h(0.15em)#styled(item.detail)],
          text(size: 9 * unit, item.date))
      ]
    }
  }
  if data.at("skills", default: ()).len() > 0 {
    section(labels.skills)
    paragraphs(data.skills)
  }
  for key in ("experience", "open-source", "projects") {
    let title = labels.at(key)
    let items = data.at(key, default: ())
    if items.len() > 0 {
      section(title)
      for item in items {
        if key == "experience" {
          company-header(item)
        } else {
          entry(item.title, detail: item.at("detail", default: ""),
            date: item.at("date", default: ""), url: item.at("url", default: ""),
            label: item.at("link-label", default: labels.project),
            repository: item.at("repository", default: ""), stars: item.at("stars", default: ""))
        }
        paragraphs(item.at("summary", default: ()))
        bullets(item.at("bullets", default: ()))
        for project in item.at("projects", default: ()) {
          block(above: 5 * unit, below: 2.5 * unit, breakable: false,
            text(font: bold-font, weight: "bold", project.title))
          paragraphs(project.at("summary", default: ()))
          bullets(project.at("bullets", default: ()))
        }
      }
    }
  }
  if data.at("publications", default: ()).len() > 0 {
    section(labels.publications)
    for item in data.publications {
      entry(item.title, detail: item.detail)
      paragraphs(item.at("summary", default: ()))
    }
  }
}

#let resume(data, settings) = {
  validate-content(data)
  let language = sys.inputs.at("lang", default: "zh")
  assert(language in ("zh", "en"), message: "lang 可选 zh 或 en。")
  let density = float(sys.inputs.at("density", default: str(settings.density)))
  let minimum = settings.min-density
  let page-mode = sys.inputs.at("page-mode", default: settings.at("page-mode", default: "continuous"))
  assert(page-mode in ("continuous", "single"), message: "page-mode 可选 continuous 或 single。")
  let fonts = resolve-fonts(settings)
  let auto-fit = sys.inputs.at("auto-fit", default: if settings.auto-fit { "true" } else { "false" }) == "true"
  assert(minimum >= 0.85 and minimum <= density and density <= 1.2,
    message: "密度范围需满足 0.85 ≤ min-density ≤ density ≤ 1.20。")
  set document(title: data.profile.name + if language == "en" { " - Resume" } else { "的简历" }, author: data.profile.name)
  if page-mode == "continuous" {
    set page(width: 210mm, height: auto, margin: (x: 14mm, y: 11mm), numbering: none)
    context {
      let body = block(width: 182mm, breakable: false,
        contents(data, density, fonts: fonts, language: language))
      [
        #metadata((page-mode: page-mode, density: density, body-pt: 10.5 * density,
          width-pt: 210mm / 1pt, height-pt: measure(body).height / 1pt)) <resume-layout>
        #body
      ]
    }
  } else {
    set page(paper: "a4", margin: (x: 14mm, y: 11mm), numbering: none)
    layout(size => {
      let height-at(scale) = measure(block(width: size.width, breakable: false,
        contents(data, scale, fonts: fonts, language: language))).height
      let chosen = density
      if auto-fit and height-at(chosen) > size.height {
        assert(height-at(minimum) <= size.height,
          message: "当前内容超出一页的可读容量。请精简重复描述，或降低 min-density（建议正文不低于 9pt）。")
        let low = minimum
        let high = density
        for _ in range(12) {
          let mid = (low + high) / 2
          if height-at(mid) <= size.height { low = mid } else { high = mid }
        }
        chosen = low
      }
      assert(height-at(chosen) <= size.height,
        message: "当前密度放不下一页，请开启 auto-fit 或调低 density。")
      [
        #metadata((page-mode: page-mode, density: chosen, body-pt: 10.5 * chosen,
          height-pt: height-at(chosen) / 1pt, available-pt: size.height / 1pt)) <resume-layout>
        #block(width: size.width, breakable: false, contents(data, chosen, fonts: fonts, language: language))
      ]
    })
  }
}
