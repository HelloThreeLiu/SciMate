# -*- coding: utf-8 -*-
"""
通用文档渲染器：把 Markdown 渲染成排版精良、可直接浏览/打印的 HTML 单文件。

用法：
  python md2html.py --md outputs/xxx.md --title "文档标题"
  python md2html.py --md outputs/xxx.md --title "..." --preset prd

--preset prd 会在指定标题后注入 PRD 专用的结构图（模块地图 / 流程条 / 三阶段时间轴）。
"""
import argparse
import io
import os
import re

import markdown

CSS = r"""
:root{
  --ink:#16202e; --ink-2:#3b4859; --muted:#6c7889;
  --line:#e3e9f1; --line-2:#eef3f9;
  --bg:#eef2f7; --card:#ffffff;
  --brand:#1e5fa8; --brand-2:#2f7fd1; --brand-soft:#ebf3fc; --brand-deep:#123f70;
  --p0:#b3261e; --p0-bg:#fdecea;
  --p1:#8a5a00; --p1-bg:#fdf5e4;
  --p2:#2b6b4c; --p2-bg:#e9f6ef;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0; padding:38px 18px 72px; background:var(--bg); color:var(--ink);
  font-family:"Segoe UI","Microsoft YaHei","PingFang SC","Hiragino Sans GB","Source Han Sans SC",sans-serif;
  font-size:15.5px; line-height:1.85; font-feature-settings:"kern" 1;
}
.sheet{
  max-width:960px; margin:0 auto; background:var(--card);
  border:1px solid var(--line); border-radius:14px;
  padding:0 0 56px; box-shadow:0 10px 34px rgba(23,52,86,.09); overflow:hidden;
}
.sheet-head{
  padding:44px 62px 34px; background:linear-gradient(135deg,#123f70 0%,#1e5fa8 55%,#2f7fd1 100%);
  color:#fff;
}
.sheet-head .eyebrow{
  font-size:11px; letter-spacing:.24em; text-transform:uppercase;
  color:#bcd8f5; font-weight:600; margin-bottom:14px;
}
.sheet-head h1{
  margin:0 0 12px; font-size:31px; line-height:1.35; font-weight:700;
  color:#fff; border:0; padding:0; letter-spacing:.01em;
}
.sheet-head .sub{margin:0; color:#d6e8fa; font-size:14.5px}
.inner{padding:8px 62px 0}

h1,h2,h3,h4,h5{line-height:1.45; color:var(--brand-deep); font-weight:700}
h2{
  font-size:22px; margin:52px 0 18px; padding:0 0 10px 14px;
  border-bottom:1px solid var(--line); border-left:5px solid var(--brand-2); border-radius:2px;
}
h3{font-size:17.5px; margin:34px 0 10px; color:#1b548f}
h3::before{content:""; display:inline-block; width:8px; height:8px; margin-right:9px;
  background:var(--brand-2); border-radius:2px; transform:translateY(-2px)}
h4{font-size:16px; margin:24px 0 8px; color:#21568c}
h5{font-size:15px; margin:0 0 6px}
p{margin:11px 0}
strong{color:#0d2a4a; font-weight:700}
a{color:var(--brand); text-decoration:none}
a:hover{text-decoration:underline; color:var(--brand-2)}
ul,ol{padding-left:24px; margin:12px 0}
li{margin:7px 0}
hr{border:0; border-top:1px dashed #d8e3ef; margin:44px 0}

blockquote{
  margin:20px 0; padding:16px 22px; background:var(--brand-soft);
  border-left:4px solid var(--brand-2); border-radius:0 10px 10px 0; color:var(--ink-2);
}
blockquote p{margin:8px 0}
blockquote strong{color:#123f70}

table{
  width:100%; border-collapse:separate; border-spacing:0; margin:20px 0 26px;
  font-size:14.3px; border:1px solid var(--line); border-radius:10px; overflow:hidden;
}
thead th{
  background:#e9f1fb; color:#123f70; text-align:left; font-weight:700;
  padding:11px 13px; border-bottom:1px solid #d5e3f3;
}
tbody td{padding:10px 13px; border-bottom:1px solid var(--line-2); vertical-align:top; line-height:1.7}
tbody tr:nth-child(even) td{background:#fafcfe}
tbody tr:last-child td{border-bottom:0}
code{background:#f1f5fa; border:1px solid #e2eaf3; border-radius:5px;
  padding:1px 6px; font-size:13.4px; color:#1b4d80;
  font-family:Consolas,"Cascadia Mono",Menlo,monospace}

.toc{
  background:#fafcfe; border:1px solid var(--line); border-radius:12px;
  padding:20px 24px 18px; margin:26px 0 10px;
}
.toc h4{margin:0 0 12px; font-size:11.5px; letter-spacing:.2em; text-transform:uppercase;
  color:var(--muted); font-weight:700}
.toc ol{margin:0; padding-left:20px; columns:2; column-gap:34px}
.toc li{margin:5px 0; font-size:14.3px; break-inside:avoid}
.toc a{color:#1b548f}

.chip{display:inline-block; padding:2px 9px; border-radius:999px; font-size:12px;
  font-weight:700; letter-spacing:.04em}
.chip-p0{background:var(--p0-bg); color:var(--p0)}
.chip-p1{background:var(--p1-bg); color:var(--p1)}
.chip-p2{background:var(--p2-bg); color:var(--p2)}

.modmap{display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin:22px 0 12px}
.modcard{border:1px solid var(--line); border-radius:12px; padding:18px 18px 16px;
  background:linear-gradient(180deg,#fbfdff,#f4f9fe)}
.modcard .num{display:inline-block; font-size:11.5px; font-weight:700; letter-spacing:.1em;
  color:var(--brand); background:#fff; border:1px solid #cfe2f6;
  padding:2px 9px; border-radius:999px; margin-bottom:11px}
.modcard p{margin:0 0 12px; font-size:13.8px; color:var(--ink-2); line-height:1.65}
.modcard-wide{grid-column:1/-1; background:linear-gradient(180deg,#f8fbfe,#eef5fc)}
.mapnote{font-size:13.8px; color:var(--muted); margin:0 0 26px;
  padding-left:14px; border-left:3px solid #dce8f5}

.flow{display:flex; flex-wrap:wrap; align-items:center; gap:7px; margin:20px 0 6px}
.flow .st{background:#fff; border:1px solid #d3e3f5; border-radius:999px;
  padding:7px 15px; font-size:13.6px; color:#1b548f; font-weight:600}
.flow .ar{color:#9ebcdc; font-weight:700}

.tl{position:relative; margin:24px 0 10px; padding-left:30px}
.tl::before{content:""; position:absolute; left:7px; top:8px; bottom:14px; width:2px;
  background:linear-gradient(180deg,var(--brand-2),#d7e6f6)}
.tl-item{position:relative; margin-bottom:22px}
.tl-item:last-child{margin-bottom:0}
.tl-item::before{content:""; position:absolute; left:-30px; top:6px; width:12px; height:12px;
  border-radius:50%; background:#fff; border:3px solid var(--brand-2)}
.tl-d{font-size:12.5px; color:var(--muted); font-weight:600; letter-spacing:.05em}
.tl-h{font-size:15.5px; font-weight:700; color:#123f70; margin:2px 0 4px}
.tl-b{font-size:14.2px; color:var(--ink-2); line-height:1.7}

.foot{margin-top:46px; padding-top:20px; border-top:1px solid var(--line);
  font-size:13px; color:var(--muted); text-align:center}

@media (max-width:820px){
  body{padding:14px 8px 44px; font-size:15px}
  .sheet-head{padding:30px 24px 26px}
  .sheet-head h1{font-size:24px}
  .inner{padding:6px 24px 0}
  .modmap{grid-template-columns:1fr}
  .toc ol{columns:1}
  table{font-size:13.4px}
  thead th,tbody td{padding:8px 9px}
}
@media print{
  body{background:#fff; padding:0; font-size:11.5pt}
  .sheet{box-shadow:none; border:0; border-radius:0; max-width:none}
  .sheet-head{background:#123f70 !important; -webkit-print-color-adjust:exact; print-color-adjust:exact}
  h2,h3,h4{page-break-after:avoid; break-after:avoid}
  table,.modcard,.tl-item,blockquote{page-break-inside:avoid; break-inside:avoid}
  .toc{page-break-after:always; break-after:page}
}
"""

PRD_MODMAP = """
<div class="modmap">
  <div class="modcard modcard-wide">
    <span class="num">底座 · V1.1 新增</span>
    <h5>技能宿主能力</h5>
    <p>技能加载与编排 &nbsp;·&nbsp; 执行环境（文件访问 · 代码沙箱 · 网络 · 外部数据源 · <b>模型接入与密钥管理</b>）&nbsp;·&nbsp; 权限提示<br>能力从生态借，价值由自己做——我们只做技能做不到的事</p>
    <span class="chip chip-p0">P0 必做</span>
  </div>
  <div class="modcard">
    <span class="num">模块一</span>
    <h5>数据处理与分析辅助</h5>
    <p>把原始数据变成可用的结论和图表</p>
    <span class="chip chip-p0">P0 必做</span>
  </div>
  <div class="modcard">
    <span class="num">模块二</span>
    <h5>学术文献检索与推荐</h5>
    <p>把找文献、读文献、管文献变成一次对话</p>
    <span class="chip chip-p0">P0 必做</span>
  </div>
  <div class="modcard">
    <span class="num">模块三</span>
    <h5>论文写作辅助</h5>
    <p>把想法、数据、文献写成规范的论文稿</p>
    <span class="chip chip-p0">P0 必做</span>
  </div>
</div>
<div class="mapnote">三个模块 + 所有技能共享同一个「课题空间」：数据、文献、稿件都放在一起，改一处可以联动到别处，不必来回倒腾文件。</div>
"""

PRD_FLOW = """
<div class="flow">
  <span class="st">建立课题空间</span><span class="ar">&rarr;</span>
  <span class="st">用一句话提需求</span><span class="ar">&rarr;</span>
  <span class="st">系统确认关键动作</span><span class="ar">&rarr;</span>
  <span class="st">拿到结果与出处</span><span class="ar">&rarr;</span>
  <span class="st">按需微调</span><span class="ar">&rarr;</span>
  <span class="st">导出落地</span>
</div>
<div class="mapnote">下面是四个具体场景，都按「用户说什么 &rarr; 系统做什么 &rarr; 用户得到什么」来写。</div>
"""

PRD_TIMELINE = """
<div class="tl">
  <div class="tl-item">
    <div class="tl-d">第 1 个月 &nbsp;·&nbsp; 阶段零 · V1.1 新增</div>
    <div class="tl-h">技能先行</div>
    <div class="tl-b">先验证需求，再投入开发。发布 1 个自研技能（已定「引用真实性核验（含撤稿检查）」），用最低成本确认科研人员到底需不需要 AI 帮忙。<b>注意：这一步验证的是「单个技能有没有人要」，不是「工作台成不成立」。</b><br><b>同期并行两件事，其中打包验证同等优先</b>：<b>内核打包可行性验证（第 1–2 周，只出 Windows 包）——它是阶段一的开工前提，验不过则桌面端方案要重谈</b>；撤稿数据源可得性核查（第 1 周）。</div>
  </div>
  <div class="tl-item">
    <div class="tl-d">第 2–6 个月 &nbsp;·&nbsp; 阶段一 · <b>V1.7 重写</b></div>
    <div class="tl-h">精简工作台 · 仅 Windows（文献 + 研究写作 + 引用核验）</div>
    <div class="tl-b">解决「有没有」。<b>V1.7 依据团队实际条件（1 人 + AI、无服务器）把范围砍到 6 条工作流</b>：课题空间 / 技能加载与简化编排 / 执行环境（文件 + 网络 + 模型接入，<b>不含沙箱</b>）/ 引用核验与文献写作能力。<b>砍掉整个模块一（数据处理）与两层沙箱</b>，工期 3 → 5 个月。<b>V1.8 起平台收窄为 Windows 优先</b>——开发在本机，macOS / Linux 无法本地验证，暂不承诺。<br><b>「数据不出本机」依然成立</b>——它只需要"文件不上传"，不需要沙箱。</div>
  </div>
  <div class="tl-item">
    <div class="tl-d">第 7–12 个月 &nbsp;·&nbsp; 阶段二 · V1.7 重定义</div>
    <div class="tl-h">补上数据能力</div>
    <div class="tl-b">把阶段一刻意推迟的两块补回来：<b>模块一整体（数据分析与绘图）</b>与<b>本机沙箱（microsandbox + 三级降级）</b>，让「三件事打通」的完整故事成立。<br><b>两者必须同一阶段</b>——数据分析要真跑 numpy / pandas / matplotlib，没有脚本执行能力，这个模块就是空壳。</div>
  </div>
  <div class="tl-item">
    <div class="tl-d">第 13–18 个月 &nbsp;·&nbsp; 阶段三 · V1.7 调整</div>
    <div class="tl-h">生态与协作</div>
    <div class="tl-b">解决「离不离得开」。<b>云端沙箱层（CubeSandbox，需 Linux 服务器 + 运维）</b>、版本协作、课题组共享空间、期刊模板库、严格的官方技能推荐清单。<br>机构合作的目标是<b>跑通 1–2 个 POC</b>，而非"落地"。</div>
  </div>
</div>
"""

PRESETS = {
    "prd": [
        ("<h3>3.1 功能总览</h3>", PRD_MODMAP),
        ("<h2>四、典型使用流程</h2>", PRD_FLOW),
        ("<h2>七、阶段性规划</h2>", PRD_TIMELINE),
    ]
}


def _insert_after_first(html, needle, block):
    idx = html.find(needle)
    if idx < 0:
        print("  [warn] 锚点未命中：%s" % needle[:44])
        return html
    end = idx + len(needle)
    return html[:end] + block + html[end:]


def render(md_path, html_path, title, subtitle="", eyebrow="Document", footer="",
           preset=None, toc=True):
    with io.open(md_path, "r", encoding="utf-8") as f:
        src = f.read()

    html = markdown.markdown(src, extensions=["tables", "sane_lists"])

    banner = (
        '<header class="sheet-head">\n'
        '  <div class="eyebrow">%s</div>\n'
        '  <h1>%s</h1>\n'
        '  <p class="sub">%s</p>\n'
        '</header>\n<div class="inner">\n' % (eyebrow, title, subtitle)
    )
    html = re.sub(r"<h1>.*?</h1>", banner, html, count=1, flags=re.S)

    for anchor, block in PRESETS.get(preset or "", []):
        html = _insert_after_first(html, anchor, block)

    toc_items = []

    def _h2(m):
        toc_items.append(m.group(1))
        return '<h2 id="sec-%d">%s</h2>' % (len(toc_items), m.group(1))

    html = re.sub(r"<h2>(.*?)</h2>", _h2, html)

    if toc and toc_items:
        items = "\n".join(
            '<li><a href="#sec-%d">%s</a></li>' % (i + 1, t)
            for i, t in enumerate(toc_items)
        )
        html = _insert_after_first(
            html, "<hr />", '\n<nav class="toc"><h4>本文档结构</h4><ol>%s</ol></nav>\n' % items
        )

    foot = ('\n<div class="foot">%s</div>\n' % footer) if footer else ""

    doc = (
        '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n'
        '<meta charset="utf-8" />\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1" />\n'
        '<title>%s</title>\n<style>%s</style>\n</head>\n<body>\n<div class="sheet">\n%s%s\n</div>\n</div>\n</body>\n</html>\n'
        % (title, CSS, html, foot)
    )

    with io.open(html_path, "w", encoding="utf-8") as f:
        f.write(doc)
    print("OK -> %s  (章节 %d)" % (html_path, len(toc_items)))
    return html_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--title", required=True)
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--eyebrow", default="Document")
    ap.add_argument("--footer", default="")
    ap.add_argument("--preset", default=None)
    ap.add_argument("--no-toc", action="store_true")
    a = ap.parse_args()
    out = a.out or os.path.splitext(a.md)[0] + ".html"
    render(a.md, out, a.title, a.subtitle, a.eyebrow, a.footer, a.preset, not a.no_toc)


if __name__ == "__main__":
    main()
