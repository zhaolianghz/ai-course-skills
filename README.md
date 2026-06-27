# 焕燃科技 · Claude Code Skills

公司课程研发用的 Claude Code 技能集。

## skills/课件母版创建
按课程研发 SOP 自动创建一门课的「课件内容母版」(markdown)。
触发:"做 KP-X.X 的课件" / "创建课件母版"。
流程:选题定位 → 取材 → 写母版 → 自检 → 登记索引(含两处人工卡点);可选渲染 HTML 幻灯片成品。

## skills/课件配图
给课件/课程决定"配什么图、怎么配"。把抽象认知点(流程/结构/状态/隐喻)变成示意图,而非装饰图。
触发:"给这页/这门课加图" / "配图" / "这页太干"。
含:8 种结构类型库 + shot list 先行 + cobalt 风 SVG 规范 + QA 自检。
方法论借鉴 ian-xiaohei-illustrations(借方法不借皮:它怪诞非教学,本 skill 是 cobalt 教学化)。

## 安装
把对应 skill 目录放进项目的 `.claude/skills/` 下,即被 Claude Code 自动发现。

## 依赖(取材步骤需要,自行配置)
- `ima-skills`(读 IMA 知识库)+ IMA 凭证(`~/.config/ima/`)——未配则取材降级为只联网/读仓库标准。
