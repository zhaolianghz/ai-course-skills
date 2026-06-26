import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "create-courseware-master"


class CoursewareSkillPackageTests(unittest.TestCase):
    def test_skill_has_codex_compatible_frontmatter_and_resources(self):
        skill_md = SKILL / "SKILL.md"
        self.assertTrue(skill_md.exists(), "SKILL.md should live in an English, hyphenated skill folder")
        text = skill_md.read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)[1]

        self.assertIn("name: create-courseware-master", frontmatter)
        self.assertIn("description: Use when", frontmatter)
        self.assertLess(len(frontmatter), 900)

        for rel in [
            "references/checkpoints.md",
            "references/markdown-master.md",
            "references/index-update.md",
            "references/html-rendering.md",
            "schemas/courseware-fields.schema.json",
            "scripts/validate_courseware_fields.py",
            "scripts/validate_course_master.py",
        ]:
            self.assertTrue((SKILL / rel).exists(), f"missing bundled resource: {rel}")

    def test_courseware_schema_contains_all_course_types(self):
        schema = json.loads((SKILL / "schemas" / "courseware-fields.schema.json").read_text(encoding="utf-8"))
        course_types = schema["courseTypes"]
        self.assertEqual(set(course_types), {"实操课", "工具课", "案例课", "理论课", "复盘课"})

        for course_type, spec in course_types.items():
            fields = set(spec["required"])
            self.assertIn("课程类型", fields, course_type)
            self.assertIn("课程名", fields, course_type)
            self.assertIn("截图清单", fields, course_type)

    def test_field_validator_accepts_minimal_valid_practical_json(self):
        sample = {
            "课程类型": "实操课",
            "KP编码": "KP-1.1",
            "课程名": "提示词基础",
            "第X课时": "课时1",
            "课时主题": "写清楚任务",
            "一句话导入": "把模糊需求改成可执行指令。",
            "适学对象": "职场新人",
            "版本": "v0.1",
            "知识目标": "说出提示词的四个基本要素。",
            "技能目标": "能写出一个完整任务指令。",
            "成果目标": "产出一条可复用提示词。",
            "讲解小标题": "提示词不是提问，是交代任务",
            "讲解正文": "一个好提示词要说明角色、任务、材料和输出格式。",
            "关键提示": "不要只写一句帮我看看。",
            "步骤1标题": "明确任务",
            "步骤1操作": "把要完成的工作写成一句可验收的话。",
            "步骤1预期结果": "任务边界清楚。",
            "步骤1截图说明": "展示输入框里的任务描述。",
            "步骤2标题": "补充材料",
            "步骤2操作": "粘贴背景材料。",
            "步骤2预期结果": "AI 能看到上下文。",
            "步骤2截图说明": "展示材料区。",
            "步骤3标题": "规定输出",
            "步骤3操作": "指定格式和验收标准。",
            "步骤3预期结果": "输出结构稳定。",
            "步骤3截图说明": "展示生成结果。",
            "练习任务": "改写一条模糊提示词。",
            "通关标准": "包含任务、材料、格式三项。",
            "成果示范": "一条完整提示词截图。",
            "小结要点1标题": "任务先行",
            "小结要点1说明": "先说清楚要做什么。",
            "小结要点2标题": "材料充分",
            "小结要点2说明": "给 AI 足够上下文。",
            "小结要点3标题": "格式收口",
            "小结要点3说明": "规定输出样子。",
            "必做作业": "提交一条提示词。",
            "选做作业": "改写同事的一条提示词。",
            "下节预习": "了解上下文窗口。",
            "截图清单": ["步骤1截图", "步骤2截图", "步骤3截图", "成果截图"],
        }
        sample_path = ROOT / "tests" / "sample-courseware-fields.json"
        sample_path.write_text(json.dumps(sample, ensure_ascii=False), encoding="utf-8")
        try:
            result = subprocess.run(
                [sys.executable, str(SKILL / "scripts" / "validate_courseware_fields.py"), str(sample_path)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        finally:
            sample_path.unlink(missing_ok=True)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
