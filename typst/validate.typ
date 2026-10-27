// 在所有入口统一校验内容，错误指向 TOML 字段，不输出个人字段值。
#let validate-content(data) = {
  let table(value, path, allowed) = {
    assert(type(value) == dictionary, message: path + " 必须是 TOML 表。")
    for key in value.keys() {
      assert(key in allowed, message: path + "." + key + " 是未知字段，请检查拼写或参考示例。")
    }
  }
  let string-field(item, key, path, required: false) = {
    if required {
      assert(key in item, message: path + "." + key + " 缺少必填字段。")
    }
    if key in item {
      let value = item.at(key)
      assert(type(value) == str, message: path + "." + key + " 必须是字符串，请使用引号。")
      if required {
        assert(value.trim() != "", message: path + "." + key + " 不能为空。")
      }
    }
  }
  let string-array(value, path) = {
    assert(type(value) == array, message: path + " 必须是字符串数组，如 [\"第一项\", \"第二项\"]。")
    for (index, item) in value.enumerate() {
      assert(type(item) == str, message: path + "[" + str(index + 1) + "] 必须是字符串。")
    }
  }
  let records(value, path) = {
    let declaration = path.replace(regex("\\[[0-9]+\\]"), "")
    assert(type(value) == array, message: path + " 必须是条目数组，请使用 [[" + declaration + "]]。")
  }
  let prose(item, path) = {
    for key in ("summary", "bullets") {
      if key in item { string-array(item.at(key), path + "." + key) }
    }
  }
  let project(item, path) = {
    table(item, path, ("title", "summary", "bullets"))
    string-field(item, "title", path, required: true)
    prose(item, path)
  }

  let sections = ("education", "experience", "open-source", "projects", "publications")
  table(data, "内容", ("profile", "skills", "section-titles", ..sections))
  if "section-titles" in data {
    let titles = data.at("section-titles")
    table(titles, "section-titles", ("skills", ..sections))
    for key in titles.keys() {
      string-field(titles, key, "section-titles", required: true)
    }
  }
  assert("profile" in data, message: "缺少 [profile]，请填写 name。")
  let contacts = ("name", "phone", "phone-display", "email", "github", "github-name", "website", "website-label")
  table(data.profile, "profile", contacts)
  for key in contacts { string-field(data.profile, key, "profile", required: key == "name") }
  if "skills" in data { string-array(data.skills, "skills") }

  for section in sections {
    if section not in data { continue }
    let items = data.at(section)
    records(items, section)
    for (index, item) in items.enumerate() {
      let path = section + "[" + str(index + 1) + "]"
      if section == "education" {
        table(item, path, ("school", "detail", "date", "tags"))
        for key in ("school", "detail", "date") { string-field(item, key, path, required: true) }
        if "tags" in item { string-array(item.tags, path + ".tags") }
      } else if section == "publications" {
        table(item, path, ("title", "detail", "summary"))
        for key in ("title", "detail") { string-field(item, key, path, required: true) }
        prose(item, path)
      } else {
        let strings = ("title", "detail", "date", "url", "link-label")
        let specific = if section == "experience" { ("department", "logo", "tone") } else { ("repository", "stars") }
        table(item, path, (..strings, ..specific, "summary", "bullets", "projects"))
        for key in strings { string-field(item, key, path, required: key == "title") }
        for key in specific.filter(key => key != "stars") { string-field(item, key, path) }
        if "tone" in item {
          assert(item.tone in ("warm", "cool", "neutral"), message: path + ".tone 只能填写 warm、cool 或 neutral。")
        }
        if "stars" in item {
          assert(type(item.stars) == int and item.stars >= 0, message: path + ".stars 必须是不小于 0 的整数，不带引号或 k/w 后缀。")
        }
        prose(item, path)
        if "projects" in item {
          records(item.projects, path + ".projects")
          for (project-index, nested) in item.projects.enumerate() {
            project(nested, path + ".projects[" + str(project-index + 1) + "]")
          }
        }
      }
    }
  }
}
