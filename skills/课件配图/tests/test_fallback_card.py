"""课件配图 fallback_card.py 测试。

不渲染像素、不联网——只校验:每种结构类型都能产出合法 SVG(标签闭合、含 cobalt 调色、
带占位角标),L2 prompt 类型把提示词印进卡,未知类型退出码 2,--list 列全类型。
"""
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "fallback_card.py"

# 直接 import 模块测纯函数(比起进程更快、能断言内部),用 spec 从路径加载
import importlib.util

_spec = importlib.util.spec_from_file_location("fallback_card", SCRIPT)
fc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fc)

ALL_TYPES = list(fc.TYPES)


@pytest.mark.parametrize("kind", ALL_TYPES)
def test_every_type_builds_valid_svg(kind):
    svg = fc.build(kind, "测试锚点")
    # 单根 svg、标签闭合
    assert svg.count("<svg") == 1 and svg.count("</svg>") == 1
    # cobalt 同源调色(钴蓝)+ 米纸底
    assert fc.INK in svg and fc.PAPER in svg
    # 占位角标(发布门禁据此识别未完成)
    assert "占位待补" in svg
    # 标题进了图
    assert "测试锚点" in svg
    # viewBox 矢量自适应
    assert "viewBox" in svg and "max-height:620px" in svg


def test_workflow_has_arrows_and_three_boxes():
    svg = fc.build("workflow", "取材→写稿→验收")
    assert svg.count("marker-end") == 2          # 两个箭头
    assert svg.count("<rect") >= 4               # 卡边框 + 角标 + 3 步框
    for label in ("输入", "处理", "输出"):
        assert label in svg


def test_compare_uses_warn_and_ink_sides():
    svg = fc.build("compare", "前后")
    assert "问题/旧" in svg and "改进/新" in svg
    assert "marker-end" in svg                   # 中间箭头


def test_system_has_core_satellites_and_relation_lines():
    svg = fc.build("system", "模块关系")
    assert "核心模块" in svg
    for lbl in ("模块A", "模块B", "模块C"):
        assert lbl in svg
    # 3 条关系线(无箭头):核心↔左/右/底卫星
    assert svg.count("<line ") == 3


def test_tree_has_parent_children_and_branches():
    svg = fc.build("tree", "层级嵌套")
    assert "父节点" in svg
    for lbl in ("子节点1", "子节点2", "子节点3"):
        assert lbl in svg
    # 树状分叉:父↓bus + 横 bus + 3 条子↓ = 5 条 line
    assert svg.count("<line ") == 5


def test_prompt_type_prints_prompt_text():
    p = "一台贴着问号的机器,左输入右输出,cobalt蓝+米纸底,极简大量留白"
    svg = fc.build("prompt", "黑盒隐喻", prompt=p)
    assert "生成后贴回替换" in svg
    # 提示词被折行印出(取前若干字断言,避开折行 tspan 边界)
    assert "一台贴着问号的机器" in svg


def test_prompt_text_html_escaped():
    """提示词含 < & " 时必须转义,不破坏 SVG。"""
    svg = fc.build("prompt", "x", prompt='a<b>&"c')
    assert "<b>" not in svg                       # 原始尖括号不得直出
    assert "&lt;" in svg and "&amp;" in svg


def test_title_html_escaped():
    svg = fc.build("workflow", '<script>alert(1)</script>')
    assert "<script>" not in svg
    assert "&lt;script&gt;" in svg


# ── CLI 行为 ──────────────────────────────────────────────────────────

def test_cli_list_shows_all_types():
    r = subprocess.run([sys.executable, str(SCRIPT), "--list"],
                       capture_output=True, text=True)
    assert r.returncode == 0
    for k in ALL_TYPES:
        assert k in r.stdout


def test_cli_unknown_type_exits_2():
    r = subprocess.run([sys.executable, str(SCRIPT), "--type", "nope", "--title", "x"],
                       capture_output=True, text=True)
    assert r.returncode == 2
    assert "未知类型" in r.stderr


def test_cli_writes_file(tmp_path):
    out = tmp_path / "card.svg"
    r = subprocess.run([sys.executable, str(SCRIPT), "--type", "workflow",
                        "--title", "T", "--out", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0 and out.exists()
    assert out.read_text(encoding="utf-8").count("</svg>") == 1


def test_cli_stdout_when_no_out():
    r = subprocess.run([sys.executable, str(SCRIPT), "--type", "states", "--title", "T"],
                       capture_output=True, text=True)
    assert r.returncode == 0 and "<svg" in r.stdout
