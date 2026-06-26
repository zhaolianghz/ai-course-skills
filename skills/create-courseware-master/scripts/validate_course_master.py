#!/usr/bin/env python3
import re
import sys
from pathlib import Path


PLACEHOLDER_PATTERNS = [
    "APPEND",
    "{{",
    "TODO",
    "待补",
]


def headings(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if line.startswith("## ") and not line.startswith("### ")
    ]


def directory_items(text: str) -> list[str]:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == "## 目录":
            items = []
            for later in lines[index + 1 :]:
                stripped = later.strip()
                if stripped.startswith("## "):
                    break
                if not stripped:
                    continue
                stripped = re.sub(r"^[-*]\s+", "", stripped)
                stripped = re.sub(r"^\d+[、.]\s*", "", stripped)
                items.append(stripped)
            return items
    return []


def directory_has_double_numbering(text: str) -> list[str]:
    """Detect 目录 items like '1、1.' where a hand-written N、 is followed by a markdown N. prefix."""
    offenders = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^\d+、\s*\d+\.\s+", stripped):
            offenders.append(stripped)
    return offenders


def numbered_headings_are_continuous(heads: list[str]) -> bool:
    numbers = []
    for head in heads:
        match = re.match(r"##\s+(\d+)[、.]\s+", head)
        if match:
            numbers.append(int(match.group(1)))
    return numbers == list(range(1, len(numbers) + 1))


def validate(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors = []

    for pattern in PLACEHOLDER_PATTERNS:
        if pattern in text:
            errors.append(f"placeholder remains: {pattern}")

    if not re.search(r"^# .+", text, re.M):
        errors.append("missing level-1 title")
 
    double_numbered = directory_has_double_numbering(text)
    if double_numbered:
        errors.append("目录条目出现双序号（N、N.），飞书会叠加自动编号: " + "; ".join(double_numbered[:3]))

    heads = headings(text)
    if not heads:
        errors.append("missing level-2 sections")

    if not numbered_headings_are_continuous(heads):
        errors.append("numbered level-2 headings are not continuous")

    directory = directory_items(text)
    if not directory:
        errors.append("missing or empty ## 目录")
    else:
        normalized_heads = [re.sub(r"^##\s+", "", head) for head in heads if head != "## 目录"]
        missing = [item for item in directory if not any(item in head for head in normalized_heads)]
        if missing:
            errors.append("directory items not found in headings: " + ", ".join(missing))

    if "案例" not in text:
        errors.append("missing at least one case/example marker: 案例")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_course_master.py <course-master.md>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    errors = validate(path)
    if errors:
        print(f"validation failed: {path}")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"ok: {path} passes machine checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
