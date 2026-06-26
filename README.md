# 焕燃科技 · Claude Code Skills

公司课程研发用的 Claude Code 技能集。

## skills/课件母版创建
按课程研发 SOP 自动创建一门课的「课件内容母版」(markdown)。
触发:"做 KP-X.X 的课件" / "创建课件母版"。
流程:选题定位 → 取材 → 写母版 → 自检 → 登记索引(含两处人工卡点)。

### 安装
把 `skills/课件母版创建/` 放进项目的 `.claude/skills/` 下即可被 Claude Code 自动发现。

### 依赖(取材步骤需要,需自行配置)
- `ima-skills`(读 IMA 知识库)+ IMA 凭证(`~/.config/ima/`)——未配则取材降级为只联网/读仓库标准。
