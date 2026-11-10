"""Check real generated pages, fragments and required article sections."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.ids = set()
        self.links = []
        self.h1 = 0
        self.blank_targets = []
        self.errors = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            if attrs["id"] in self.ids:
                self.errors.append(f'duplicate id {attrs["id"]}')
            self.ids.add(attrs["id"])
        if tag == "h1":
            self.h1 += 1
        for attr in ["href", "src"]:
            if attr in attrs:
                self.links.append(attrs[attr])
        if tag == "a" and attrs.get("target") == "_blank" and "noopener" not in attrs.get("rel", ""):
            self.errors.append("external new tab link lacks noopener")


def check(output, notes):
    files = sorted(output.rglob("*.html"))
    assert len(files) == len(notes) + 4, "Unexpected HTML page count"
    pages = {}
    errors = []
    links = 0
    for path in files:
        text = path.read_text(encoding="utf-8")
        parsed = Page(text)
        pages[path.resolve()] = parsed
        if parsed.h1 != 1:
            errors.append(f"{path.name}: expected exactly one h1")
        if re.search(r"\{\{[a-z_]+\}\}", text):
            errors.append(f"{path.name}: unfilled template")
        if '<html lang="zh-Hant">' not in text:
            errors.append(f"{path.name}: missing document language")
        errors.extend(f"{path.name}: {error}" for error in parsed.errors)
    for path, parsed in pages.items():
        for link in parsed.links:
            target = urlsplit(link)
            if target.scheme or target.netloc:
                continue
            links += 1
            if target.path.startswith("/"):
                errors.append(f"{path.name}: root-absolute link {link}")
                continue
            destination = (path.parent / unquote(target.path)).resolve() if target.path else path
            if destination.is_dir():
                destination /= "index.html"
            if not destination.is_relative_to(output.resolve()) or not destination.exists():
                errors.append(f"{path.name}: broken local link {link}")
            elif target.fragment and destination in pages and unquote(target.fragment) not in pages[destination].ids:
                errors.append(f"{path.name}: missing fragment {link}")
    for note in notes:
        path = (output / "notes" / f'{note["id"]}.html').resolve()
        expected = {"concept", "example", "practice", "pitfalls", "quiz", "sources"}
        if not expected.issubset(pages[path].ids):
            errors.append(f'{note["id"]}: missing required section')
    assert (output / "AGENTS.md").read_bytes() == (ROOT / "AGENTS.md").read_bytes(), "Published rules out of sync"
    if errors:
        raise SystemExit("CHECK FAILED:\n" + "\n".join(errors))
    print(f"CHECK OK: {len(files)} pages, {links} local links/assets, all 6 sections per note, published rules match source")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="dist")
    parser.add_argument("--content", default="content/notes.json")
    args = parser.parse_args()
    check(ROOT / args.output, json.loads((ROOT / args.content).read_text(encoding="utf-8")))
