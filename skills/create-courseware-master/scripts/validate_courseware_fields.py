#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCHEMA_PATH = SKILL_DIR / "schemas" / "courseware-fields.schema.json"


def load_json(path: Path) -> dict:
    text = path.read_text(encoding="utf-8").strip()
    text = re.sub(r"^```[a-zA-Z0-9_-]*\n", "", text)
    text = re.sub(r"\n```$", "", text)
    match = re.search(r"\{.*\}", text, re.S)
    return json.loads(match.group(0) if match else text)


def missing_fields(fields: dict, schema: dict) -> list[str]:
    course_type = str(fields.get("课程类型", "")).strip()
    matched_type = next((name for name in schema["courseTypes"] if name in course_type), "")
    if not matched_type:
        return [f"课程类型 must include one of: {', '.join(schema['courseTypes'])}"]

    required = set(schema["commonRequired"])
    required.update(schema["courseTypes"][matched_type]["required"])

    missing = []
    for key in sorted(required):
        value = fields.get(key)
        if value is None:
            missing.append(key)
        elif isinstance(value, str) and not value.strip():
            missing.append(key)
        elif isinstance(value, list) and not value:
            missing.append(key)
    return missing


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_courseware_fields.py <fields.json>", file=sys.stderr)
        return 2

    fields_path = Path(sys.argv[1])
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        fields = load_json(fields_path)
    except Exception as exc:
        print(f"invalid json: {exc}", file=sys.stderr)
        return 2

    missing = missing_fields(fields, schema)
    if missing:
        print("missing required fields:")
        for key in missing:
            print(f"- {key}")
        return 1

    print(f"ok: {fields_path} satisfies courseware field requirements")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
