#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""引用真实性核验脚本（含撤稿检查）——阶段零技能版（M2-7 先行验证）

设计约束（对应 PRD M2-7 与《撤稿数据源核查报告》）：
- 仅用 Python 标准库，零依赖，任何装有 Python 3.9+ 的机器可直接运行；
- 主路 OpenAlex（DOI 直查 / 标题检索，is_retracted 撤稿判定），
  辅路 Crossref（撤稿细节对账 + 无 DOI 引用的书目模糊匹配）；
- 编造的 DOI 会被两家同时 404；但 404 ≠ 编造（部分真实 DOI 未被收录），
  必须再做严格标题匹配才能定性；
- 标题匹配必须有「锚点」（≥2 个作者姓氏命中，或 1 个姓氏 + 年份精确一致），
  防止泛化标题误命中；
- 匹配置信度不足时标注「未能核实，请人工确认」，绝不模糊放行；
- 并发 + 重试 + 本地缓存（串行实测仅约 0.5 请求/秒，见核查报告）。

用法：
  python verify_citations.py <references.txt> [-o report.md] [--json out.json]
输入文件每行一条参考文献（可由 AI 客户端先从稿件中抽取）。
"""

import argparse
import concurrent.futures as cf
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

CONTACT_MAILTO = os.environ.get("CITATION_VERIFY_MAILTO", "citation-verify@scimate.local")
OPENALEX = "https://api.openalex.org"
CROSSREF = "https://api.crossref.org"
CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".verify_cache.json")
CACHE_TTL_DAYS = 30
MAX_WORKERS = 5
TIMEOUT = 30

DOI_RE = re.compile(r"\b(10\.\d{4,9}/[^\s\"<>\[\]，。；、]+)", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(19[5-9]\d|20[0-4]\d)\b")
PUB_TYPE_RE = re.compile(r"\[[JCMDSA]/?(OL)?\]|//(J|C|M|D|S|A)")  # GB/T 7714 文献类型标识

STOPWORDS = {
    "the", "a", "an", "of", "and", "in", "on", "for", "to", "with", "via",
    "based", "using", "from", "by", "at", "is", "are", "as", "its", "their",
}


# ---------------------------------------------------------------- 基础设施

def _http_json(url, params=None):
    """GET 请求返回 JSON；带重试与礼貌 mailto。404 抛 LookupError。"""
    if params:
        url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    last_err = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": f"scimate-citation-verify (mailto:{CONTACT_MAILTO})"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise LookupError(url)
            if e.code in (429, 500, 502, 503) and attempt < 2:
                time.sleep(2 ** attempt * 1.5)
                continue
            raise
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_err = e
            if attempt < 2:
                time.sleep(2 ** attempt * 1.5)
                continue
            raise
    raise last_err


class Cache:
    """按查询键缓存的极简 JSON 存储，降低对上游频控的压力。"""

    def __init__(self, path):
        self.path = path
        self.data = {}
        try:
            with open(path, encoding="utf-8") as f:
                self.data = json.load(f)
        except (OSError, ValueError):
            pass

    def get(self, key):
        hit = self.data.get(key)
        if not hit:
            return None
        if time.time() - hit.get("t", 0) > CACHE_TTL_DAYS * 86400:
            return None
        return hit["v"]

    def put(self, key, value):
        self.data[key] = {"t": time.time(), "v": value}

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False)
        except OSError:
            pass


# ---------------------------------------------------------------- 文本工具

def clean_doi(raw):
    doi = raw.strip().rstrip(".,;")
    # DOI 内可含成对括号（如 10.1016/S0140-6736(97)11096-0）；截掉不成对的尾部
    while doi.count(")") != doi.count("("):
        if doi.count(")") > doi.count("("):
            doi = doi[: doi.rfind(")")]
        else:
            doi = doi[: len(doi) - (doi.count("(") - doi.count(")"))] if doi.count("(") > doi.count(")") else doi
    return doi


def norm_title(s):
    s = html.unescape(s or "").lower()
    s = re.sub(r"[^0-9a-z\u4e00-\u9fff]+", " ", s)
    return " ".join(s.split())


def tokens(s):
    return {t for t in norm_title(s).split() if t not in STOPWORDS and len(t) > 1}


def title_similarity(a, b):
    """Jaccard 相似度（并集做分母，比 min 基准严格，防止泛化标题误命中）。"""
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def guess_year(ref):
    years = YEAR_RE.findall(ref)
    return int(years[0]) if years else None


def guess_title(ref):
    """从一条参考文献里猜标题：优先 GB/T 类型标识前的片段，其次 APA 年份模式，最后取最长句段。"""
    r = ref.strip()
    r = re.sub(r"^\s*\[?\d{1,3}[\].、]\s*", "", r)  # 去掉行首编号 [1] / 1. / 1、
    r = re.sub(r"doi\s*[:：]\s*\S+$", "", r, flags=re.IGNORECASE).strip(" .")
    m = PUB_TYPE_RE.search(r)
    if m and m.start() > 8:
        # GB/T 7714：「作者. 题名[J]. 刊名…」——题名是类型标识前的最后一个片段
        parts = [p.strip(" ,;:") for p in r[: m.start()].split(". ")]
        if len(parts) >= 2:
            if len(parts[-1].split()) >= 3:
                return parts[-1]
            joined = ". ".join(parts[1:]).strip()
            if joined:
                return joined
        elif parts and len(parts[0].split()) >= 4:
            return parts[0]
    m2 = re.search(r"\(\s*(19[5-9]\d|20[0-4]\d)\s*\)\.?\s*(.+)", r)  # APA: (2023). Title...
    if m2:
        tail = re.split(r"\.\s", m2.group(2), maxsplit=1)[0]
        if len(tail.split()) >= 4:
            return tail
    parts = [p.strip(" ,;:") for p in r.split(". ")]
    cands = [p for p in parts if len(p.split()) >= 5 and not YEAR_RE.fullmatch(p)]
    if cands:
        return max(cands, key=lambda p: len(p.split()))
    return r[:120]


def surname_hits(ref, names):
    """结果作者姓氏在引用原文中的命中数（去重）。"""
    surnames = set()
    for n in names or []:
        if not n:
            continue
        parts = n.replace(",", " ").split()
        if parts:
            surnames.add(parts[-1].lower())
    return sum(1 for s in surnames if len(s) > 2 and s in ref.lower())


# ---------------------------------------------------------------- 上游查询

def openalex_by_doi(doi):
    return _http_json(f"{OPENALEX}/works/https://doi.org/{urllib.parse.quote(doi)}")


def openalex_search_title(title, year=None):
    filt = f"title.search:{title}"
    if year:
        filt += f",publication_year:{year - 1}|{year}|{year + 1}"
    d = _http_json(f"{OPENALEX}/works", {
        "filter": filt, "per-page": 5,
        "select": "id,doi,display_name,publication_year,authorships,is_retracted,biblio"})
    return d.get("results", [])


def crossref_by_doi(doi):
    return _http_json(f"{CROSSREF}/works/{urllib.parse.quote(doi)}")["message"]


def crossref_search(ref):
    d = _http_json(f"{CROSSREF}/works", {
        "query.bibliographic": ref[:400], "rows": 5,
        "select": "DOI,title,author,issued,container-title,volume"})
    return d.get("message", {}).get("items", [])


# ---------------------------------------------------------------- 核验逻辑

def oa_author_names(work):
    return [a["author"]["display_name"] for a in work.get("authorships", []) if a.get("author")]


def crossref_retraction_detail(msg):
    """从 Crossref 记录中提取撤稿通知细节（含 Retraction Watch 数据）。"""
    title = (msg.get("title") or [""])[0]
    rels = msg.get("updated-by") or []
    retracts = [r for r in rels
                if "retract" in str(r.get("type", "")).lower()
                or "retract" in str(r.get("label", "")).lower()]
    if retracts:
        r0 = retracts[0]
        dp = (r0.get("updated", {}).get("date-parts") or [[None]])[0]
        when = "-".join(str(x) for x in dp) if dp and dp[0] else "日期未知"
        return ("Crossref 撤稿记录：撤稿通知 DOI {}（{}，来源 {}，{}）".format(
            r0.get("DOI", "—"), r0.get("label", "retraction"),
            r0.get("source", "crossref"), when))
    if title.upper().startswith("RETRACTED"):
        return "Crossref 记录标题带 RETRACTED 前缀"
    return None


def compare_metadata(ref, title, year, work):
    """返回 (综合分, 差异列表, 题名相似度)。"""
    diffs = []
    t_guess = title or guess_title(ref)
    sim = round(title_similarity(t_guess, work.get("display_name", "")), 2)
    found_year = work.get("publication_year")
    ref_year = year or guess_year(ref)
    if found_year and ref_year and found_year != ref_year:
        diffs.append(f"年份不符：引用写 {ref_year}，数据库为 {found_year}")
    authors = oa_author_names(work)
    if authors and surname_hits(ref, authors[:8]) == 0:
        diffs.append(f"作者对不上：数据库作者为 {', '.join(authors[:4])} 等")
    if sim < 0.5:
        diffs.append(f"题名相似度偏低（{sim}），请人工确认是否同一篇")
    year_ok = found_year is None or ref_year is None or found_year == ref_year
    author_ok = not authors or surname_hits(ref, authors[:8]) > 0
    score = 0.5 * min(sim / 0.7, 1.0) + 0.25 * year_ok + 0.25 * author_ok
    return round(score, 2), diffs, sim


def try_title_match(ref, strict):
    """标题/书目模糊匹配。strict=True 用于 DOI 查无此文时的复核（阈值更高）。
    返回 (score, sim, work, source) 或 None。"""
    year = guess_year(ref)
    title = guess_title(ref)
    best = None
    sim_floor, score_floor = (0.65, 0.7) if strict else (0.45, 0.6)
    try:
        for w in openalex_search_title(title, year):
            score, _, sim = compare_metadata(ref, title, year, w)
            if best is None or score > best[0]:
                best = (score, sim, w, "OpenAlex（标题检索）")
    except Exception:  # noqa: BLE001
        pass
    try:
        for it in crossref_search(ref):
            t = (it.get("title") or [""])[0]
            yr = (it.get("issued", {}).get("date-parts", [[None]])[0][0])
            sim = title_similarity(title, t)
            auth = [a.get("family") or a.get("name") or "" for a in it.get("author", [])]
            yr_ok = yr is not None and year is not None and yr == year
            au_hit = surname_hits(ref, auth[:8])
            score = round(0.5 * min(sim / 0.7, 1.0)
                          + 0.25 * yr_ok + 0.25 * (au_hit > 0), 2)
            if best is None or score > best[0]:
                best = (score, sim, {"display_name": t, "publication_year": yr,
                                     "doi": it.get("DOI"), "authorships":
                                     [{"author": {"display_name": n}} for n in auth]},
                        "Crossref（书目检索）")
    except Exception:  # noqa: BLE001
        pass

    if best is None:
        return None
    score, sim, work, src = best
    # 锚点要求：≥2 个作者姓氏命中，或 1 个姓氏 + 年份精确一致（strict 时再加一档阈值）
    authors = oa_author_names(work)
    au_hit = surname_hits(ref, authors[:8])
    yr = work.get("publication_year")
    ryear = year or guess_year(ref)
    anchored = au_hit >= 2 or (au_hit >= 1 and yr is not None and ryear is not None and yr == ryear)
    if score >= score_floor and sim >= sim_floor and anchored:
        return best
    return None


def verify_one(idx, ref):
    """核验单条引用。状态取值：
    ok_doi / ok_match / doi_unindexed / retracted / not_found_doi / unverifiable / error
    """
    out = {"idx": idx, "ref": ref.strip(), "status": "unverifiable", "source": "",
           "matched": None, "doi": None, "retraction": None, "diffs": [],
           "score": 0.0, "note": ""}
    m = DOI_RE.search(ref)
    if m:
        doi = clean_doi(m.group(1))
        out["doi"] = doi
        try:
            # ---- 主路：OpenAlex DOI 直查 ----
            try:
                work = openalex_by_doi(doi)
                out.update(source="OpenAlex（DOI 直查）", matched=work)
                score, diffs, _ = compare_metadata(ref, None, None, work)
                out.update(score=score, diffs=diffs)
                if work.get("is_retracted"):
                    out["status"] = "retracted"
                    out["retraction"] = "OpenAlex 标记该文献已被撤稿"
                    try:  # 补充 Crossref 撤稿细节（仅撤稿时多花一次请求）
                        out["retraction"] += "；" + crossref_retraction_detail(crossref_by_doi(doi))
                    except Exception:  # noqa: BLE001
                        pass
                else:
                    out["status"] = "ok_doi"
                return out
            except LookupError:
                pass
            # ---- 辅路：Crossref DOI 直查 ----
            try:
                msg = crossref_by_doi(doi)
                title = (msg.get("title") or [""])[0]
                year = (msg.get("issued", {}).get("date-parts", [[None]])[0][0])
                auth = [a.get("family") or a.get("name") or "" for a in msg.get("author", [])]
                work = {"display_name": title, "publication_year": year, "doi": msg.get("DOI"),
                        "authorships": [{"author": {"display_name": n}} for n in auth]}
                out.update(source="Crossref（DOI 直查）", matched=work)
                retr = crossref_retraction_detail(msg)
                if retr:
                    out.update(status="retracted", retraction=retr)
                else:
                    out["status"] = "ok_doi"
                return out
            except LookupError:
                pass
            # ---- 两库 DOI 均查无：先严格标题复核，再定性 ----
            best = try_title_match(ref, strict=True)
            if best:
                score, sim, work, src = best
                out.update(source=src, matched=work, score=score)
                out["status"] = "doi_unindexed"
                out["note"] = (f"引用中的 DOI（{doi}）未被 OpenAlex/Crossref 收录，"
                               f"但存在同题文献（相似度 {sim}）——DOI 可能无效或未注册，请核对 DOI 是否抄写正确")
                return out
            out["status"] = "not_found_doi"
            out["note"] = (f"DOI {doi} 在 OpenAlex 与 Crossref 均查无此文，且未找到同题文献——"
                           "疑似编造的引用，请务必人工确认")
            return out
        except Exception as e:  # noqa: BLE001 —— 网络/上游异常不整批崩溃
            out["status"] = "error"
            out["note"] = f"DOI 查询出错：{e}"
            return out
    # ---- 无 DOI：标题/书目模糊匹配 ----
    try:
        best = try_title_match(ref, strict=False)
    except Exception as e:  # noqa: BLE001
        out["status"] = "error"
        out["note"] = f"查询出错：{e}"
        return out
    if best:
        score, sim, work, src = best
        _, diffs, _ = compare_metadata(ref, None, None, work)
        out.update(source=src, matched=work, score=score, diffs=diffs)
        if work.get("is_retracted"):
            out["status"] = "retracted"
            out["retraction"] = "OpenAlex 标记该文献已被撤稿"
        else:
            out["status"] = "ok_match"
            out["note"] = f"标题匹配相似度 {sim}（无 DOI，属间接核实，请以原文为准）"
        return out
    out["note"] = ("未能核实——两库均无足够置信的匹配，请人工确认"
                   "（常见原因：图书/中文文献未被收录、题名过泛、引用信息有误）")
    return out


# ---------------------------------------------------------------- 报告生成

STATUS_LABEL = {
    "ok_doi": "✅ 已核实（DOI 直查）",
    "ok_match": "✅ 已核实（标题匹配）",
    "doi_unindexed": "⚠️ DOI 未收录，同题文献疑存在",
    "retracted": "🚨 已撤稿",
    "not_found_doi": "❌ DOI 查无此文（疑似编造）",
    "unverifiable": "❓ 未能核实，请人工确认",
    "error": "⚠️ 查询出错（网络/上游）",
}
STATUS_ORDER = ["retracted", "not_found_doi", "doi_unindexed", "unverifiable",
                "error", "ok_match", "ok_doi"]


def render_report(results, input_name, elapsed):
    lines = ["# 引用核验报告（引用真实性核验 · 含撤稿检查）", ""]
    lines.append(f"- 生成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- 输入文件：`{input_name}`")
    lines.append(f"- 核验条数：{len(results)} 条 · 耗时 {elapsed:.0f} 秒")
    lines.append("- 数据源：OpenAlex（主路）+ Crossref（辅路，含 Retraction Watch 数据）")
    lines.append("")

    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    n = len(results) or 1
    lines.append("## 总览")
    lines.append("")
    lines.append("| 状态 | 条数 | 占比 |")
    lines.append("|---|---|---|")
    for st in STATUS_ORDER:
        if counts.get(st):
            lines.append(f"| {STATUS_LABEL[st]} | {counts[st]} | {round(counts[st] * 100 / n)}% |")
    lines.append("")

    verified = counts.get("ok_doi", 0) + counts.get("ok_match", 0)
    verifiable = verified + counts.get("retracted", 0) + counts.get("not_found_doi", 0)
    unverified = counts.get("unverifiable", 0) + counts.get("not_found_doi", 0)
    c1 = f"{verified}/{verifiable} = {round(verified * 100 / verifiable)}%" if verifiable else "—（无可核实条目）"
    c2 = f"{unverified}/{n} = {round(unverified * 100 / n)}%"
    lines.append(f"- **口径一（可核实引用中确认真实存在的比例）**：{c1}")
    lines.append(f"- **口径二（被标注「未能核实 / 查无此文」的比例）**：{c2}")
    lines.append("")
    lines.append("> 口径说明：DOI 直查 = 在权威数据库中按 DOI 精确命中；标题匹配 = 无 DOI 时按题名+作者+年份"
                 "交叉匹配并要求作者/年份锚点，置信度达阈值才计为核实。两者都**不等于绝对真实**，"
                 "最终请以人工抽查为准。「DOI 未收录」单独一档，不计入两口径。")
    lines.append("")

    lines.append("## 逐条结果")
    for r in sorted(results, key=lambda x: STATUS_ORDER.index(x["status"])):
        lines.append("")
        lines.append(f"### [{r['idx']}] {STATUS_LABEL[r['status']]}")
        lines.append(f"- **引用原文**：{r['ref']}")
        w = r.get("matched") or {}
        shown_doi = (w.get("doi") or r.get("doi") or "")
        shown_doi = shown_doi.replace("https://doi.org/", "").strip()
        if w:
            extra = f" — DOI: {shown_doi}" if shown_doi else ""
            lines.append(f"- **匹配文献**：{w.get('display_name', '—')}（{w.get('publication_year', '—')}）{extra}")
        if r.get("source"):
            lines.append(f"- **核实途径**：{r['source']}")
        if r.get("retraction"):
            lines.append(f"- **🚨 撤稿警示**：{r['retraction']}——**继续引用已撤稿论文可能造成严重学术问题，请立即处理**")
        for d in r.get("diffs", []):
            lines.append(f"- **⚠️ 差异**：{d}")
        if r.get("note"):
            lines.append(f"- **说明**：{r['note']}")
    lines.append("")
    lines.append("---")
    lines.append("*本报告由脚本自动生成（OpenAlex + Crossref 公开接口），只陈述数据库可查证的事实；"
                 "「未能核实」不代表引用有误，「已核实」也不替代人工判断。*")
    return "\n".join(lines)


# ---------------------------------------------------------------- 主流程

def load_references(path):
    refs, ignored = [], 0
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            if DOI_RE.search(s) or (YEAR_RE.search(s) and len(s) >= 25) or len(s) >= 40:
                refs.append(s)
            else:
                ignored += 1
    return refs, ignored


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="引用真实性核验（含撤稿检查）")
    ap.add_argument("input", help="参考文献文本文件，每行一条")
    ap.add_argument("-o", "--output", default=None, help="Markdown 报告输出路径")
    ap.add_argument("--json", dest="as_json", default=None, help="同时输出 JSON 结果")
    args = ap.parse_args()

    refs, ignored = load_references(args.input)
    if not refs:
        print("未在输入文件中识别到参考文献行。请确认格式：每行一条引用（含年份或 DOI）。")
        return 2
    if ignored:
        print(f"（已跳过 {ignored} 行不像引用的内容）")

    cache = Cache(CACHE_FILE)
    results = []
    t0 = time.time()
    print(f"开始核验 {len(refs)} 条引用（并发 {MAX_WORKERS} 路）……")

    def run(i_ref):
        i, ref = i_ref
        key = "v2:" + urllib.parse.quote(ref[:300])
        hit = cache.get(key)
        if hit is not None:
            hit["idx"] = i
            return hit
        r = verify_one(i, ref)
        cache.put(key, r)
        return r

    with cf.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        for r in ex.map(run, enumerate(refs, 1)):
            results.append(r)
            print(f"  [{r['idx']}/{len(refs)}] {STATUS_LABEL[r['status']]}")
    cache.save()
    elapsed = time.time() - t0

    report = render_report(results, os.path.basename(args.input), elapsed)
    out_path = args.output or os.path.splitext(args.input)[0] + "-核验报告.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)
    if args.as_json:
        with open(args.as_json, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n完成：报告已写入 {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
