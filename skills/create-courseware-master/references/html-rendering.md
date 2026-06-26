# HTML 幻灯片渲染

只有用户明确要“课件 / PPT / 成品 / HTML”时执行本步骤。默认母版产物是 markdown。

## 流程

1. 根据课程类型生成结构化字段 JSON。
2. 用 schema 校验 JSON：

   ```bash
   python3 skills/create-courseware-master/scripts/validate_courseware_fields.py <字段.json>
   ```

3. 调用本地课件模板渲染器：

   ```bash
   python3 课程/课件模板/渲染器.py <字段.json> <输出.html>
   ```

4. 统计剩余未填槽和截图位，写进完成报告。

## 模板口径

- 默认使用 `课程/课件模板/` 下的 cobalt-grid 单文件 HTML 模板。
- 课程类型自动选择：实操课、工具课、案例课、理论课、复盘课。
- 截图走方案 B：HTML 里保留截图位和“该截什么”说明，讲师后补真实截图。
- 讲师、班级等个性化字段留空，不替讲师编造。

## Dify 口径

默认走 Claude/Codex 直连：agent 生成字段 JSON，本地渲染器出 HTML。Dify 仅作为未来对外自助 SaaS 预研模式；不要把 Dify 节点作为本 skill 的依赖。
