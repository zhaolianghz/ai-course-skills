#!/usr/bin/env python3
"""课件配图 fallback 卡生成器(降级链 L1/L2)。

配不出真图时不留白板:按结构类型产一张 cobalt 风占位卡(SVG),
带结构骨架 + 标题槽 + "⚠ 占位待补"角标。L2(prompt 类型)额外印出
可复制的绘图提示词,供拿去免费平台生成后贴回替换。

用法:
  python3 fallback_card.py --type workflow --title "取材→写稿→验收" --out card.svg
  python3 fallback_card.py --type prompt --title "黑盒隐喻" --prompt "..." --out card.svg
  python3 fallback_card.py --list

设计:纯 stdlib,无依赖、无网络、无 Key。SVG 用 cobalt 调色板(钴蓝 #1F2BE0 / 米纸底),
viewBox 矢量自适应,可直接内联进幻灯片 foot-logo 前。
"""
import argparse
import html
import sys

# cobalt-grid 同源调色板(和 references/svg-style.md 一致)
INK = "#1F2BE0"        # 钴蓝:主体/主线
SOFT = "#5560E5"       # 柔蓝:次要/箭头
PAPER = "#F0EBDE"      # 米纸底
TEXT = "#1a1a2e"
MUTE = "#8a8597"       # 占位虚线/弱标注
WARN = "#d6442c"       # 警告角标

W, H = 960, 600        # 卡画布(2:1.25,贴进 1920×1080 舞台留白充裕)

TYPES = {
    "workflow": "流程:输入→处理→输出",
    "compare": "前后对比:问题→改进",
    "states": "状态枚举:并列小块",
    "layers": "分层结构:能力栈",
    "metaphor": "概念隐喻:一个有记忆点的物件",
    "timeline": "路线/时间线:一条线串节点",
    "prompt": "提示词占位(L2):印 prompt 待人工生成替换",
}


def _esc(s: str) -> str:
    return html.escape(s or "", quote=True)


def _box(x, y, w, h, label, fill=PAPER, stroke=INK, dash=False, tcolor=TEXT):
    d = ' stroke-dasharray="8 6"' if dash else ""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="3"{d}/>'
        f'<text x="{x + w/2}" y="{y + h/2 + 8}" text-anchor="middle" '
        f'font-size="26" fill="{tcolor}" font-family="DM Mono,Noto Sans SC,monospace">{_esc(label)}</text>'
    )


def _arrow(x1, y1, x2, y2):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{SOFT}" '
            f'stroke-width="4" marker-end="url(#ah)"/>')


def _skeleton(kind: str) -> str:
    """按结构类型画骨架(占位三框/对比/分层…),内容用虚线框 + 弱标注表"待补"。"""
    if kind in ("workflow", "timeline"):
        bw, bh, y = 220, 120, 240
        xs = [70, 370, 670]
        labels = ["输入", "处理", "输出"] if kind == "workflow" else ["①", "②", "③"]
        parts = [_box(xs[i], y, bw, bh, labels[i], dash=True, stroke=MUTE, tcolor=MUTE) for i in range(3)]
        parts += [_arrow(xs[0] + bw, y + bh/2, xs[1], y + bh/2),
                  _arrow(xs[1] + bw, y + bh/2, xs[2], y + bh/2)]
        return "".join(parts)
    if kind == "compare":
        return "".join([
            _box(70, 240, 320, 120, "问题/旧", dash=True, stroke=MUTE, tcolor=MUTE),
            _box(570, 240, 320, 120, "改进/新", dash=True, stroke=INK, tcolor=SOFT),
            _arrow(400, 300, 560, 300)])
    if kind == "states":
        return "".join(_box(70 + i*220, 240, 180, 120, f"状态{i+1}", dash=True, stroke=MUTE, tcolor=MUTE)
                       for i in range(4))
    if kind == "layers":
        return "".join(_box(230, 180 + i*90, 500, 70, f"第{i+1}层", dash=True, stroke=MUTE, tcolor=MUTE)
                       for i in range(4))
    if kind == "metaphor":
        return "".join([
            _box(370, 230, 220, 150, "物件?", dash=True, stroke=INK, tcolor=SOFT),
            _arrow(250, 305, 365, 305), _arrow(595, 305, 710, 305),
            f'<text x="200" y="290" font-size="22" fill="{MUTE}" font-family="Noto Sans SC">输入</text>',
            f'<text x="715" y="290" font-size="22" fill="{MUTE}" font-family="Noto Sans SC">输出</text>'])
    if kind == "prompt":
        return _box(130, 220, 700, 160, "生成后贴回替换", dash=True, stroke=SOFT, tcolor=SOFT)
    return _box(230, 230, 500, 140, "结构待定", dash=True, stroke=MUTE, tcolor=MUTE)


def build(kind: str, title: str, prompt: str = "") -> str:
    skel = _skeleton(kind)
    title_t = (f'<text x="{W/2}" y="120" text-anchor="middle" font-size="40" '
               f'fill="{INK}" font-family="DM Mono,Noto Sans SC,monospace" '
               f'font-weight="700">{_esc(title)}</text>')
    badge = (f'<rect x="{W-210}" y="28" width="182" height="46" rx="23" fill="{WARN}"/>'
             f'<text x="{W-119}" y="58" text-anchor="middle" font-size="24" fill="#fff" '
             f'font-family="Noto Sans SC">⚠ 占位待补</text>')
    prompt_block = ""
    if kind == "prompt" and prompt:
        # 简单按宽度折行(每行约 30 个全角字符),印在卡底部
        lines, cur = [], ""
        for ch in prompt:
            cur += ch
            if len(cur) >= 30:
                lines.append(cur); cur = ""
        if cur:
            lines.append(cur)
        tspans = "".join(
            f'<tspan x="130" dy="{0 if i==0 else 30}">{_esc(ln)}</tspan>'
            for i, ln in enumerate(lines[:5]))
        prompt_block = (f'<text x="130" y="440" font-size="22" fill="{TEXT}" '
                        f'font-family="Noto Sans SC">{tspans}</text>')
    return (
        f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
        f'style="width:100%;max-height:620px" class="reveal" role="img" '
        f'aria-label="占位卡:{_esc(title)}">'
        f'<defs><marker id="ah" markerWidth="12" markerHeight="12" refX="9" refY="5" '
        f'orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{SOFT}"/></marker></defs>'
        f'<rect width="{W}" height="{H}" rx="20" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>'
        f'{title_t}{badge}{skel}{prompt_block}'
        f'</svg>'
    )


def main():
    ap = argparse.ArgumentParser(description="课件配图 fallback 占位卡生成器")
    ap.add_argument("--type", dest="kind", default="workflow", help="结构类型(见 --list)")
    ap.add_argument("--title", default="待补图", help="卡标题(认知锚点一句话)")
    ap.add_argument("--prompt", default="", help="L2:绘图提示词(type=prompt 时印在卡上)")
    ap.add_argument("--out", default="", help="输出 SVG 路径;省略则打到 stdout")
    ap.add_argument("--list", action="store_true", help="列出支持的结构类型")
    args = ap.parse_args()

    if args.list:
        for k, v in TYPES.items():
            print(f"  {k:10} — {v}")
        return

    if args.kind not in TYPES:
        print(f"未知类型 {args.kind};可用:{', '.join(TYPES)}", file=sys.stderr)
        sys.exit(2)

    svg = build(args.kind, args.title, args.prompt)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"已写出 {args.out}（{args.kind}）")
    else:
        print(svg)


if __name__ == "__main__":
    main()
