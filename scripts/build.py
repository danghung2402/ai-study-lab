"""Validate the single content source and generate a portable static site."""
import argparse
from collections import Counter
from datetime import date
from html import escape
import json
from pathlib import Path
import re
import shutil
from urllib.parse import quote, urlparse

ROOT = Path(__file__).resolve().parents[1]
STATIC_PAGES = {"index.html", "paths.html", "rules.html", "about.html", "lab.html", "evidence.html"}
BRIEF_FIELDS = [
    ("goal", "任務目標", "Mục tiêu", "你希望 AI 幫你完成什麼？"),
    ("audience", "使用對象", "Đối tượng", "誰會閱讀或使用這份成果？"),
    ("sources", "輸入與資料來源", "Tài liệu đầu vào", "指出檔案、頁碼、網址或已提供的內容。"),
    ("deliverable", "交付成果", "Sản phẩm cần nhận", "說明格式、結構與數量，讓成果看得見。"),
    ("constraints", "限制與規則", "Giới hạn và quy tắc", "例如語言、來源範圍與禁止編造。每點一行。"),
    ("acceptance", "驗收標準", "Tiêu chí kiểm tra", "完成後，你會怎麼確認做對了？每點一行。"),
]
CATEGORIES = {
    "提示設計": ("prompt", "{ ? }", "把想法說清楚，是和 AI 合作的第一步。先練習交辦，再整理需要的背景。"),
    "代理工作流": ("agent", "[ ↗ ]", "理解模型與工具的分工，把做事方法寫進規則，並為每次成果安排驗收。"),
    "網站實作": ("web", "</>", "從網頁的基本分工，到可以分享的公開網址，讓作品真正被使用。"),
}


def strings(value, low, high, name):
    if not isinstance(value, list) or not low <= len(value) <= high:
        raise ValueError(f"{name}: expected {low}–{high} items")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{name}: all items must be non-empty strings")


def required_text(obj, keys, name):
    if not isinstance(obj, dict):
        raise ValueError(f"{name}: expected an object")
    for key in keys:
        if not isinstance(obj.get(key), str) or not obj[key].strip():
            raise ValueError(f"{name}.{key}: required non-empty text")


def validate(notes):
    if not isinstance(notes, list) or not notes:
        raise ValueError("notes.json must contain a non-empty array")
    seen = set()
    for note in notes:
        required_text(note, ["id", "title", "summary", "category", "level", "updated"], "note")
        slug = note["id"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug in seen:
            raise ValueError(f"Invalid or duplicate id: {slug}")
        seen.add(slug)
        if note["category"] not in CATEGORIES or note["level"] not in ["入門", "實作"]:
            raise ValueError(f"{slug}: unknown category or level")
        if type(note.get("minutes")) is not int or not 3 <= note["minutes"] <= 30:
            raise ValueError(f"{slug}: minutes must be 3–30")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", note["updated"]):
            raise ValueError(f"{slug}: expected ISO date")
        date.fromisoformat(note["updated"])
        for key, low, high in [("tags", 2, 4), ("goals", 2, 3), ("concept", 2, 20), ("steps", 3, 6), ("pitfalls", 2, 4)]:
            strings(note.get(key), low, high, f"{slug}.{key}")
        required_text(note.get("example"), ["title", "text"], f"{slug}.example")
        if not isinstance(note["example"].get("code"), str):
            raise ValueError(f"{slug}.example.code: expected a string")
        quiz = note.get("quiz")
        required_text(quiz, ["question", "explanation"], f"{slug}.quiz")
        strings(quiz.get("options"), 3, 3, f"{slug}.quiz.options")
        if type(quiz.get("answer")) is not int or quiz["answer"] not in range(3):
            raise ValueError(f"{slug}: answer must be 0, 1 or 2")
        for key in ["sources", "glossary"]:
            if not isinstance(note.get(key), list) or not note[key]:
                raise ValueError(f"{slug}.{key}: expected at least one item")
        for source in note["sources"]:
            required_text(source, ["title", "url"], f"{slug}.source")
            url = source["url"]
            if url.startswith("course:"):
                match = re.fullmatch(r"course:09#page=(\d+)(?:-(\d+))?", url)
                if not match or not 1 <= int(match[1]) <= int(match[2] or match[1]) <= 36:
                    raise ValueError(f"{slug}: invalid course page reference")
            elif urlparse(url).scheme != "https" or not urlparse(url).netloc:
                raise ValueError(f"{slug}: external sources must use HTTPS")
        for term in note["glossary"]:
            required_text(term, ["zh", "en", "vi"], f"{slug}.glossary")


def render(name, context):
    source = (ROOT / "templates" / name).read_text(encoding="utf-8")
    def replace(match):
        key = match.group(1)
        if key not in context:
            raise ValueError(f"{name}: missing template field {key}")
        return str(context[key])
    return re.sub(r"\{\{([a-z_]+)\}\}", replace, source)


def card(note, index, root=""):
    kind, drawing, _ = CATEGORIES[note["category"]]
    title = escape(note["title"])
    slug = note["id"]
    search = escape(" ".join([note["title"], note["summary"], *note["tags"]]))
    tags = "".join(f'<span>#{escape(tag)}</span>' for tag in note["tags"][:2])
    return f'''<article class="note-card {kind}" data-card data-id="{slug}" data-category="{escape(note['category'])}" data-search="{search}">
<div class="card-top" aria-hidden="true"><span class="card-number">{index:02d}</span><span class="card-drawing">{escape(drawing)}</span></div>
<button type="button" class="card-bookmark" data-bookmark="{slug}" data-title="{title}" aria-label="收藏：{title}" aria-pressed="false">☆</button>
<div class="card-body"><div class="card-meta"><span class="category-label {kind}">{escape(note['category'])}</span><span>{note['minutes']} 分鐘 · {escape(note['level'])}</span></div><h3><a href="{root}notes/{slug}.html">{title}</a></h3><p>{escape(note['summary'])}</p><div class="card-footer"><div class="card-tags">{tags}</div><span class="read-arrow" aria-hidden="true">↗</span></div></div><div class="card-status" hidden></div></article>'''


def list_items(items):
    return "".join(f"<li>{escape(item)}</li>" for item in items)


def note_context(note, notes):
    context = {key: escape(str(value)) for key, value in note.items() if isinstance(value, (str, int))}
    context.update({"note_title": escape(note["title"]), "category_query": quote(note["category"]),
                    "category_class": CATEGORIES[note["category"]][0], "goals": list_items(note["goals"]),
                    "concept": "".join(f"<p>{escape(p)}</p>" for p in note["concept"]),
                    "steps": list_items(note["steps"]), "pitfalls": list_items(note["pitfalls"])})
    example = note["example"]
    context.update({"example_title": escape(example["title"]), "example_text": escape(example["text"]), "example_code": ""})
    if example["code"]:
        context["example_code"] = '<div class="code-block"><div class="code-bar"><span>EXAMPLE</span><button type="button" class="copy-code">複製範例</button></div><pre><code>' + escape(example["code"]) + '</code></pre></div>'
    quiz = note["quiz"]
    context.update({"quiz_question": escape(quiz["question"]), "quiz_answer": quiz["answer"],
                    "quiz_explanation": escape(quiz["explanation"]),
                    "quiz_options": "".join(f'<label class="quiz-option"><input type="radio" name="quiz-{note["id"]}" value="{i}"><span>{escape(option)}</span></label>' for i, option in enumerate(quiz["options"]))})
    sources = []
    for source in note["sources"]:
        if source["url"].startswith("course:"):
            pages = source["url"].split("page=")[1]
            sources.append(f'<li>{escape(source["title"])}<span class="source-note">使用者提供的課堂講義，第 {pages} 頁。原始 PDF 未公開轉載。</span></li>')
        else:
            sources.append(f'<li><a href="{escape(source["url"])}" target="_blank" rel="noopener noreferrer">{escape(source["title"])} ↗</a></li>')
    context["sources"] = "".join(sources)
    context["glossary"] = "".join(f'<div><dt>{escape(t["zh"])}</dt><dd lang="en">{escape(t["en"])}</dd><dd lang="vi">{escape(t["vi"])}</dd></div>' for t in note["glossary"])
    others = [n for n in notes if n["id"] != note["id"]]
    related = [n for n in others if n["category"] == note["category"]]
    related += [n for n in others if n["category"] != note["category"]]
    context["related"] = "".join(card(n, notes.index(n) + 1, "../") for n in related[:2])
    return context


def path_sections(notes):
    sections = []
    for index, (category, (kind, _, description)) in enumerate(CATEGORIES.items(), 1):
        selected = [n for n in notes if n["category"] == category]
        items = "".join(f'<li class="path-note" data-path-note="{n["id"]}"><a href="notes/{n["id"]}.html"><span class="path-order">{i}</span><div><h3>{escape(n["title"])}</h3><p>{n["minutes"]} 分鐘 · {escape(n["level"])}</p></div><span class="path-note-status">待探索</span><span class="path-arrow" aria-hidden="true">↗</span></a></li>' for i, n in enumerate(selected, 1))
        sections.append(f'<section class="path-section {kind}"><div class="path-intro"><span class="path-index">0{index}</span><h2>{category}</h2><p>{description}</p><small>{len(selected)} 篇筆記 · 約 {sum(n["minutes"] for n in selected)} 分鐘</small></div><ol class="path-notes">{items}</ol></section>')
    return "".join(sections)


def validate_scenarios(scenarios):
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("scenarios.json must contain at least one scenario")
    seen = set()
    for scenario in scenarios:
        required_text(scenario, ["id", "name", "vi", "description"], "scenario")
        slug = scenario["id"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug in seen:
            raise ValueError(f"Invalid or duplicate scenario id: {slug}")
        seen.add(slug)
        required_text(scenario.get("fields"), [field[0] for field in BRIEF_FIELDS], slug)
        if set(scenario["fields"]) != {field[0] for field in BRIEF_FIELDS}:
            raise ValueError(f"{slug}: expected exactly six brief fields")


def lab_context(scenarios):
    buttons = "".join(f'<button type="button" class="scenario-card" data-scenario="{s["id"]}" aria-pressed="{str(i == 0).lower()}"><span class="scenario-number">0{i+1}</span><strong>{escape(s["name"])}</strong><small lang="vi">{escape(s["vi"])}</small><span class="scenario-description">{escape(s["description"])}</span></button>' for i, s in enumerate(scenarios))
    fields = []
    for i, (key, label, vi, help_text) in enumerate(BRIEF_FIELDS, 1):
        fields.append(f'<div class="brief-field"><label for="brief-{key}"><span class="field-number">0{i}</span><span>{label}<small lang="vi">{vi}</small></span><span class="required-mark">必填</span></label><p id="help-{key}">{help_text}</p><textarea id="brief-{key}" name="{key}" rows="{4 if key in ("constraints", "acceptance") else 3}" required aria-describedby="help-{key}">{escape(scenarios[0]["fields"][key])}</textarea></div>')
    return {"scenario_buttons": buttons, "brief_fields": "".join(fields),
            "scenario_json": json.dumps(scenarios, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")}


def proof_context(proof, scenario_count):
    passed = proof.get("status") == "passed"
    return {
        "proof_status": "✓ 可重現驗證已通過" if passed else "尚未執行延伸驗證",
        "before_notes": proof.get("before_notes", "—"), "after_notes": proof.get("after_notes", "—"),
        "before_pages": proof.get("before_pages", "—"), "after_pages": proof.get("after_pages", "—"),
        "checked_links": proof.get("checked_links", "—"), "unchanged_files": proof.get("unchanged_files", "—"),
        "proof_date": escape(proof.get("date", "尚未執行")), "scenario_count": scenario_count,
        "proof_checks": list_items(proof.get("checks", ["請執行 scripts/prove_extension.py 產生實際驗證結果。"])),
    }


def build(notes, output, scenarios=None):
    validate(notes)
    if scenarios is None:
        scenarios = json.loads((ROOT / "content/scenarios.json").read_text(encoding="utf-8"))
    validate_scenarios(scenarios)
    output = output.resolve()
    # Remove only generated output within this checkout; never a source directory.
    allowed = output == ROOT / "dist" or (ROOT / "verification").resolve() in output.parents
    if not allowed or output.is_symlink():
        raise ValueError("Output must be dist or a subdirectory of verification in this project")
    if output.exists():
        shutil.rmtree(output)
    shutil.copytree(ROOT / "static", output)
    (output / "notes").mkdir()
    shutil.copy2(ROOT / "AGENTS.md", output / "AGENTS.md")
    proof_path = ROOT / "content/proof.json"
    proof = json.loads(proof_path.read_text(encoding="utf-8")) if proof_path.exists() else {"status": "not-run"}
    (output / "proof.json").write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    study_note = next((n for n in notes if n["id"] == "bilingual-study-brief"), notes[0])
    common = {"total": len(notes), "scenario_count": len(scenarios), "study_note_url": f'notes/{study_note["id"]}.html'}

    def page(filename, body, title, description, page_name, root=""):
        context = {**common, "body": body, "title": escape(title), "description": escape(description), "page": page_name, "root": root}
        context["page_script"] = '<script defer src="assets/brief-core.js"></script><script defer src="assets/lab.js"></script>' if page_name == "lab" else ""
        for key in ["home", "paths", "rules", "about", "lab"]:
            context[f"active_{key}"] = 'aria-current="page"' if page_name == key else ""
        (output / filename).write_text(render("base.html", context), encoding="utf-8")

    counts = Counter(n["category"] for n in notes)
    buttons = "".join(f'<button type="button" class="category-tab" data-category="{category}" aria-pressed="false">{category} <span>{counts[category]}</span></button>' for category in CATEGORIES)
    home = render("home.html", {**common, "cards": "".join(card(n, i) for i, n in enumerate(notes, 1)), "category_buttons": buttons})
    page("index.html", home, "讀懂 AI 講義，也學會清楚交辦", "給在台留學生的跨語言 AI 學習筆記與交辦練習工具。", "home")
    page("paths.html", render("paths.html", {"paths": path_sections(notes)}), "學習路徑", "三條學習路徑，從清楚交辦到實際製作網站。", "paths")
    page("rules.html", render("rules.html", {"rules_text": escape((ROOT / "AGENTS.md").read_text(encoding="utf-8"))}), "專案規則", "閱讀本站 AGENTS.md，了解內容格式、設計與可延伸的維護方式。", "rules")
    page("about.html", render("about.html", common), "關於本站", "了解 AI 學習實驗室的目的、內容來源與資料儲存方式。", "about")
    page("lab.html", render("lab.html", {**common, **lab_context(scenarios)}), "交辦練習室", "以中越提示填好六欄，產生有來源、限制與驗收標準的 AI 交辦稿。", "lab")
    page("evidence.html", render("evidence.html", {**common, **proof_context(proof, len(scenarios))}), "專案驗證", "查看規則、內容與網站成果的對應，以及可重現的內容延伸驗證。", "evidence")
    for note in notes:
        page(f'notes/{note["id"]}.html', render("note.html", note_context(note, notes)), note["title"], note["summary"], "note", "../")
    print(f"BUILD OK: {len(notes)} notes, {len(notes) + len(STATIC_PAGES)} HTML pages -> {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content", default="content/notes.json")
    parser.add_argument("--output", default="dist")
    args = parser.parse_args()
    try:
        build(json.loads((ROOT / args.content).read_text(encoding="utf-8")), ROOT / args.output)
    except (ValueError, KeyError, TypeError, OSError) as error:
        raise SystemExit(f"BUILD ERROR: {error}") from error
