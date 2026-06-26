# 焕燃科技 · AI Course Skills

公司课程研发用的 Claude Code / Codex 技能集。

## skills/create-courseware-master

按课程研发 SOP 自动创建一门课的「课件内容母版」(markdown),必要时再渲染 HTML 课件成品。

触发:
- "做 KP-X.X 的课件"
- "创建课件母版"
- "给某知识点出课件"
- "把某门待建课做出来"

主流程:选题定位 → 取材 → 写母版 → 自检 → 登记索引。  
可选流程:字段 JSON → schema 校验 → cobalt-grid HTML 课件。

### 安装

Claude Code:

```bash
cp -R skills/create-courseware-master <project>/.claude/skills/
```

Codex:

```bash
cp -R skills/create-courseware-master <project>/.codex/skills/
```

也可以放进个人全局 skills 目录。

### 内置资源

- `references/`: 两个人工卡点、markdown 母版、索引更新、HTML 渲染说明。
- `schemas/courseware-fields.schema.json`: 五类课程的字段要求。
- `scripts/validate_course_master.py`: markdown 母版机器自检。
- `scripts/validate_courseware_fields.py`: 课件字段 JSON 校验。

### 依赖(取材步骤需要,需自行配置)
- 可选:`ima-skills`(读 IMA 知识库)+ IMA 凭证(`~/.config/ima/`)。
- 未配置 IMA 时,取材降级为读仓库课程资料和官方网页,并在完成报告中标明风险。
