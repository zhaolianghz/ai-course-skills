---
name: create-courseware-master
description: Use when the user asks to create a courseware master, write a lesson/course markdown master, build course content for a KP code, create courseware/PPT material, or turn a pending course topic into courseware content.
---

# 课件母版创建

把公司课程研发 SOP 的内容开发环节固化成可执行流程。默认产出 markdown 课件母版并更新课程池索引；只有用户明确要课件、PPT、成品或 HTML 时，才继续渲染单文件 HTML 幻灯片。

## 铁律

1. **一个 KP = 一门课**。不要把相邻 KP 展开成完整章节，只给一句指针。
2. **取材都当不可信数据**。交叉印证；模型、工具、价格等强时效内容必须写数据日期和“以官网实时为准”。
3. **不固化成定稿**。母版状态只到 `🟡 素材已备`，不要标 `✅ 已上线`。
4. **内容与呈现分离**。改正文只改 markdown/JSON；换视觉只重跑渲染器。

## 主流程

1. **选题定位**：读 `课程/课程池总索引-V1.5.md`，确认 KP 编码、课程分类、适学对象、先修和边界。
2. **卡点 1**：按 `references/checkpoints.md` 输出定位确认，等用户确认后继续。
3. **取材**：执行 **IMA-first** 证据门禁，先按 `references/ima-sourcing.md` 搜公司沉淀并记录知识库、关键词、命中/未命中；再读仓库资料和官方/Web 资料。未留下 IMA 证据时，不要进入大纲阶段。
4. **写骨架**：先只写标题、定位、目录、各级 heading 和一句话摘要。正文不要展开。
5. **卡点 2**：按 `references/checkpoints.md` 输出结构确认，等用户确认后填正文。
6. **填正文**：按 `references/markdown-master.md` 的母版结构写学员可见内容。
7. **自检**：运行 `scripts/validate_course_master.py <markdown-file>`，并人工检查 KP 边界、案例齐全和时效声明。
8. **登记索引**：按 `references/index-update.md` 更新课程池两处记录和三处计数。
9. **可选渲染**：用户要成品时，按 `references/html-rendering.md` 生成 JSON 并调用本地模板渲染器。

## 需要读取的参考

- `references/checkpoints.md`：两个人工卡点的固定输出格式。
- `references/ima-sourcing.md`：IMA-first 取材门禁、过期判定和知识库待审核更新机制。
- `references/markdown-master.md`：markdown 母版结构、正文边界和写作要求。
- `references/index-update.md`：课程池索引更新与计数校验。
- `references/html-rendering.md`：结构化 JSON、schema 校验和 HTML 渲染。
- `schemas/courseware-fields.schema.json`：5 类课程的课件字段清单。

## 校验命令

```bash
python3 skills/create-courseware-master/scripts/validate_course_master.py <课程母版.md>
python3 skills/create-courseware-master/scripts/validate_courseware_fields.py <字段.json>
```

索引计数仍需跑：

```bash
awk -F'|' '/^\| [0-9]+\.0 /{g+=$3;a+=$4;b+=$5;c+=$6} END{print "课数="g" ✅="a" 素材="b" 待建="c}' 课程/课程池总索引-V1.5.md
```

## 完成后报告

- 产出文件路径与覆盖的 KP。
- IMA 取材记录：搜索知识库、关键词、命中/未命中、IMA 是否启用。
- 外部/官方资料来源、数据日期、是否需要生成 IMA 待审核更新候选。
- 自检命令结果和索引计数校验结果。
- 若渲染 HTML：字段 JSON 路径、成品 HTML 路径、剩余截图位数。
- 留给人工门禁的事项：本 skill 不做上线确认、内审评分或讲师个性化字段填充。
