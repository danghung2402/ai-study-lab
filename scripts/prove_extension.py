"""Rebuild content-only extensions and record verifiable results, never a grade."""
import argparse
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path

from build import ROOT, build, validate, validate_scenarios
from check import check

ADDED_ID = "bilingual-study-brief"


def shared_hashes():
    files = [ROOT / "AGENTS.md", ROOT / ".github/workflows/pages.yml"]
    for directory in ["templates", "static", "scripts"]:
        files += [p for p in (ROOT / directory).rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"]
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest() for p in sorted(files)}


def prove():
    notes_path = ROOT / "content/notes.json"
    scenario_path = ROOT / "content/scenarios.json"
    notes_bytes, scenario_bytes = notes_path.read_bytes(), scenario_path.read_bytes()
    notes = json.loads(notes_bytes)
    scenarios = json.loads(scenario_bytes)
    validate(notes)
    validate_scenarios(scenarios)
    hashes_before = shared_hashes()
    baseline = [note for note in notes if note["id"] != ADDED_ID]
    assert len(baseline) + 1 == len(notes), "Expected exactly one cross-language study note"
    target = ROOT / "verification/extension"
    build(baseline, target / "before")
    before = check(target / "before", baseline)
    build(notes, target / "after")
    after = check(target / "after", notes)
    title = next(note["title"] for note in notes if note["id"] == ADDED_ID)
    assert title in (target / "after/index.html").read_text(encoding="utf-8")
    assert title in (target / "after/paths.html").read_text(encoding="utf-8")
    assert (target / f"after/notes/{ADDED_ID}.html").exists()
    assert not (target / f"before/notes/{ADDED_ID}.html").exists()

    extended_scenarios = deepcopy(scenarios)
    extra = deepcopy(scenarios[0])
    extra.update(id="extension-probe", name="自訂專題任務（隔離驗證）", vi="Tình huống thử mở rộng")
    extra["fields"]["goal"] = "依既有六欄格式整理一個新的學習任務。"
    extended_scenarios.append(extra)
    build(notes, target / "scenario-after", extended_scenarios)
    check(target / "scenario-after", notes)
    lab = (target / "scenario-after/lab.html").read_text(encoding="utf-8")
    assert 'data-scenario="extension-probe"' in lab
    assert extra["name"] in lab

    rejected = []
    for name, mutate in [
        ("重複文章 id", lambda items: items.append(deepcopy(items[0]))),
        ("缺少核心概念", lambda items: items[0].pop("concept")),
        ("無效測驗答案", lambda items: items[0]["quiz"].update(answer=8)),
    ]:
        invalid = deepcopy(notes)
        mutate(invalid)
        try:
            validate(invalid)
        except ValueError:
            rejected.append(name)
        else:
            raise AssertionError(f"Invalid content accepted: {name}")
    hashes_after = shared_hashes()
    assert hashes_before == hashes_after, "Shared source changed during extension proof"
    assert notes_path.read_bytes() == notes_bytes, "Published notes were mutated by proof"
    assert scenario_path.read_bytes() == scenario_bytes, "Published scenarios were mutated by proof"
    canonical = json.dumps({"notes": notes, "scenarios": scenarios, "shared": hashes_before}, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    fingerprint = hashlib.sha256(canonical).hexdigest()
    return {
        "status": "passed", "date": datetime.now(timezone(timedelta(hours=8))).date().isoformat(),
        "before_notes": len(baseline), "after_notes": len(notes),
        "before_pages": before["pages"], "after_pages": after["pages"],
        "checked_links": after["links"], "unchanged_files": len(hashes_before),
        "scenario_before": len(scenarios), "scenario_after_test": len(extended_scenarios),
        "inputs_sha256": fingerprint, "shared_files_sha256": hashes_before,
        "hash_normalization": "UTF-8 text; CRLF normalized to LF; canonical JSON inputs",
        "checks": [
            "延伸前後都實際建置，檢查所有 HTML 與內部連結。",
            "新增筆記出現在首頁與學習路徑，並產生完整六節文章。",
            f"{len(hashes_before)} 個規則、樣板、樣式、互動及建置相關檔案的雜湊完全相同。",
            f"只加情境資料，隔離測試版從 {len(scenarios)} 個情境增加到 {len(extended_scenarios)} 個；正式版仍保留 {len(scenarios)} 個。",
            "錯誤資料被拒絕：" + "、".join(rejected) + "。",
            "驗證過程未修改正式筆記及情境資料。",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Re-run and compare without modifying the recorded proof")
    args = parser.parse_args()
    result = prove()
    destination = ROOT / "content/proof.json"
    if args.check:
        previous = json.loads(destination.read_text(encoding="utf-8"))
        for key in result:
            if key != "date":
                assert previous.get(key) == result[key], f"Stale proof: {key}; run prove_extension.py and rebuild"
        print("EXTENSION PROOF OK: current source matches the recorded proof")
    else:
        destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"EXTENSION PROOF SAVED: {result['before_notes']} -> {result['after_notes']} notes; {result['unchanged_files']} shared files unchanged")
