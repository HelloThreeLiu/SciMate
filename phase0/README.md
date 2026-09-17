# 阶段零 · 技能先行（第 1 个月）——工作区

> 对应《科研 Agent 应用 PRD》V1.9 第七章：三条工作线 = **1 条主线 + 2 条并行线**。
> 目标：用最低成本验证「科研人员到底需不需要 AI 帮忙」，同时把阶段一的开工前提验掉。

## 交付物索引

| 工作线 | 交付物 | 状态 |
|---|---|---|
| **主线** · 引用真实性核验技能 | [`skill-citation-verify/`](skill-citation-verify/) —— SKILL.md + 零依赖核验脚本 + 测试样本 + README/LICENSE（可发布） | ✅ 已开发完成，待发布 |
| **并行线 · 同等优先** · 打包可行性验证 | [`spike-packaging/`](spike-packaging/) —— Tauri 外壳 + PyInstaller 内核 sidecar + Windows 安装包 | ✅ 见 [`spike-packaging/REPORT.md`](spike-packaging/REPORT.md) |
| **并行线** · 撤稿数据源核查 | [`reports/撤稿数据源核查报告.md`](reports/撤稿数据源核查报告.md) —— OpenAlex + Crossref 实测 | ✅ 双路可得，结论已可写回 M2-7 |

## 阶段零成功标准（PRD 原文）与当前状态

| 标准 | 状态 |
|---|---|
| 有人真的安装并使用 | ⏳ 待发布后收集 |
| 收到至少 10 条有效反馈 | ⏳ 待发布后收集 |
| waitlist 转化率 | ⏳ 待建 waitlist 渠道 |
| 配 Key 成功率（V1.9 新增度量） | ⏳ 依赖 waitlist 表单（B5 待落地） |
| 用户平台分布（V1.9 新增度量） | ⏳ 同上 |
| 打包可行性验证（阶段一开工前提） | ✅ 本工作区已完成 |
| 撤稿数据源可得性核查（第 1 周） | ✅ 本工作区已完成 |

## 主线技能 · 快速上手

```bash
# 本地试跑（无需安装任何依赖，Python 3.9+ 即可）
cd skill-citation-verify
python scripts/verify_citations.py tests/sample_references.txt -o 报告.md
```

测试样本（`tests/sample_references.txt`）包含 10 条精心构造的引用：真实 DOI、已撤稿论文（Wakefield 1998）、编造 DOI、无 DOI 的 GB/T 格式、年份错误、泛化假引用、中文教材——**10/10 分类正确**，报告见 `tests/sample_report.md`。

## 发布前待办（不阻塞本仓库）

- [ ] 为技能建独立公开仓库并推送（当前在 `phase0/skill-citation-verify/`）
- [ ] 建 waitlist 收集渠道（表单含两项 V1.9 度量字段）
- [ ] B4：个人开发者 Windows 代码签名证书价格调研（顺手项，见 PRD 12.3）
