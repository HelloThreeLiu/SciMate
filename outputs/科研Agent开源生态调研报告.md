# 科研 Agent 开源生态调研报告

| 项目 | 内容 |
|---|---|
| **配套文档** | 《科研 Agent 应用 · 产品需求文档（PRD）》V1.0 |
| **本报告版本** | V1.2（新增第八章「Skill 生态实测」、第九章「路线建议」、第十章「技能宿主架构」） |
| **编制日期** | 2026 年 9 月 16 日 |
| **调研方式** | GitHub 官方 API 直读 + 网络检索，全部数据为当日实测值 |
| **回答的问题** | 有哪些同类项目？哪些地方可以直接借鉴？我的机会在哪？ |

**阅读提示**

这份报告只回答三件事：**别人做到哪了**、**哪些坑别人已经替你踩过**、**你该怎么做才能不一样**。如果您只想看结论，读第零章和第 三 章就够。

---

## 零、三分钟速览

> **一句话结论：这个赛道非常拥挤，但您要站的那个位置，目前是空的。**

**三个发现**

1. **您想到的三件事，每一件都有成熟项目在做，而且做得很深。**
   文献方向头号项目 `Future-House/paper-qa`（9,203 星）已被用于自动化科研流程；写作方向的国内项目 `binary-husky/gpt_academic` 有 **71,343 星**。

2. **但「三件事打通」这件事，没人对着普通科研人员做。**
   现有"端到端 AI 科学家"（AI-Scientist、Agent Laboratory、AI-Researcher）**全部面向机器学习/计算机领域**，要求会写代码、有 GPU，材料、化学、生物、医学、社科的研究生根本用不了。

3. **而且"数据分析"这一环，在文献/写作类项目里普遍缺失。**
   做文献的不做数据，做数据的不做文献。您 PRD 里那个"课题空间"（把数据、文献、稿件放一起）的设计，**目前没有项目认真做过**。

**四个立即可用的判断**

| 判断 | 理由 |
|---|---|
| **别自己从零写文献检索** | arXiv、OpenAlex、Semantic Scholar、Crossref 全部提供免费开放接口，中文项目 `Paper-Agent` 已经跑通三源检索 |
| **把"不编造"当卖点，而不是当功能** | 行业实测：GPT-4o 的引用有 78%–90% 是编的；2025 年全球约产生 14.7 万条虚构引用。这是最大的痛点 |
| **考虑先做成 SKILL.md 技能包，但只做 1 个** | Agent Skills 已被 40+ 个产品支持，`anthropics/skills` 有 **176,541 星**。但科研类 skill 已有**数十个**（见第八章），**不要再进"文献检索"和"论文润色"这两个已挤满的赛道** |
| **工作台要能加载别人的 skill，而不是自己造** | 技能是**上游供应链**不是竞争对手。做了宿主，就能收编整个生态；但**前提是先搭好执行环境**（文件 + 沙箱 + 网络 + MCP），否则加载技能只是纸面能力（见第十章） |

---

## 一、整体盘面：这个生态长什么样

把 20 多个项目按"能力层级"摆开，可以看出一个清晰的格局：

| 层级 | 干什么 | 代表项目 | 星标量级 | 和您的关系 |
|---|---|---|---|---|
| **端到端 AI 科学家** | 从想法到论文全自动 | AI-Scientist、Agent Laboratory、AI-Researcher | 5k–15k | 不是您，但要看懂它们的失败教训 |
| **文献检索与综述** | 找文献、读文献、写综述 | PaperQA2、OpenScholar、STORM、gpt-researcher | 9k–31k | **直接对应您的模块二** |
| **数据处理与分析** | 用自然语言分析数据 | Open Interpreter、pandas-ai、DeepAnalyze | 4k–68k | **直接对应您的模块一** |
| **论文写作辅助** | 润色、翻译、格式、审稿 | gpt_academic、ChatPaper、ARS | 19k–71k | **直接对应您的模块三** |
| **技能包 / 底座** | 给 Agent 提供能力与运行环境 | Agent Skills、scientific-agent-skills、OpenHands | 45k–176k | **您可以直接搭在它上面** |
| **清单 / 索引** | 帮你继续找项目 | Awesome-Agent-Scientists、awesome-autoresearch | 150–430 | 收藏起来，定期翻 |

> **一个值得注意的现象**：星标最高的层不是"做科研"的层，而是"给做科研的 Agent 提供能力"的层（`anthropics/skills` 17.6 万星、`scientific-agent-skills` 4.5 万星）。这说明**生态正在从"每个团队各造一个 Agent"转向"大家共享一套技能标准"**——这个判断会影响您的技术路线选择（详见第三章第 7 条）。

---

## 二、按模块盘点同类项目

### 2.1 文献检索与综述方向（对应您的模块二）

| 项目 | 星标 | 许可证 | 定位与看点 |
|---|---|---|---|
| [Future-House/paper-qa](https://github.com/Future-House/paper-qa) | 9,203 | Apache-2.0 | **科学文献 RAG 的参考实现**。把检索拆成可反复调用的工具，证据不够就换关键词重搜；给片段打"相关性分"做二次排序；证据不足时**直接回答"证据不足"**。附带**撤稿论文检查** |
| [AkariAsai/OpenScholar](https://github.com/AkariAsai/OpenScholar) | 1,595 | 需查 | **专治引用幻觉**。自建 4,500 万篇开放论文库，三路并行检索 + 生成后自我核验，把 GPT-4o 的 78%–90% 虚构引用率降到接近零 |
| [stanford-oval/storm](https://github.com/stanford-oval/storm) | 31,401 | MIT | 斯坦福出品，**多视角提问**生成类维基长文。会模拟"从业者/学者/怀疑论者"等不同角色分别提问，再综合 |
| [assafelovic/gpt-researcher](https://github.com/assafelovic/gpt-researcher) | 29,472 | Apache-2.0 | 通用深度研究 Agent，工程成熟度高，适合看它的**报告生成与引用组织** |
| [Tswoen/Paper-Agent](https://github.com/Tswoen/Paper-Agent) | 453 | 无 | **中文项目，与您最接近**。LangGraph 编排、三源检索（arXiv/OpenAlex/Semantic Scholar）、SSE 实时进度、SQLite 持久化、分档模型 + token 用量展示 |
| [LearningCircuit/local-deep-research](https://github.com/LearningCircuit/local-deep-research) | 9,097 | 需查 | **全本地化**深度研究，SQLCipher 加密存储，可接 10+ 检索源，能跑本地开源模型 |

**这一块的启示**：文献方向已经卷到"按段落级做引用核验"了。您**不应该**在这里做重投入，而应该直接站在这些项目或它们的开放数据源上。

### 2.2 数据处理与分析方向（对应您的模块一）

| 项目 | 星标 | 许可证 | 定位与看点 |
|---|---|---|---|
| [ruc-datalab/DeepAnalyze](https://github.com/ruc-datalab/DeepAnalyze) | 4,623 | MIT | **人大 + 清华出品，与您的场景最像**。8B 模型 + 开源训练数据，能自主完成数据准备、分析、建模、可视化，并生成"分析师级"研究报告 |
| [microsoft/data-formulator](https://github.com/microsoft/data-formulator) | 17,219 | 需查 | 微软的**交互式数据分析**，重点看它的界面设计：如何让不会写代码的人表达数据意图 |
| [sinaptik-ai/pandas-ai](https://github.com/sinaptik-ai/pandas-ai) | 23,797 | 需查 | 用自然语言对话做数据分析，**工程实现可参考**，但面向数据库/商业场景而非科研 |
| [openinterpreter/openinterpreter](https://github.com/openinterpreter/openinterpreter) | 68,337 | Apache-2.0 | 本地代码执行 Agent 的标杆。**"让 AI 在你电脑上写代码跑数据"这条路它已经趟平了** |

**这一块的启示**：科研数据分析的难点**不是"能不能算"，而是"选对方法 + 看懂结果"**。DeepAnalyze 走的是"训练专用模型"，您可以走更轻的路线——**用现成的统计库（pandas / statsmodels / scipy）+ 好的交互设计**，把重点放在"用大白话解释结果"上，这正是您 PRD 里 M1-5 的定位。

### 2.3 论文写作辅助方向（对应您的模块三）

| 项目 | 星标 | 许可证 | 定位与看点 |
|---|---|---|---|
| [binary-husky/gpt_academic](https://github.com/binary-husky/gpt_academic) | 71,343 | GPL-3.0 | **国内最大规模的学术写作工具**。PDF/LaTeX 翻译、润色、代码剖析、多模型并行对比、插件机制。它的成功很大程度来自**"自定义快捷按钮 + 函数插件"**这套可扩展设计 |
| [kaixindelele/ChatPaper](https://github.com/kaixindelele/ChatPaper) | 19,840 | 需查 | 论文全文总结 + 翻译 + 润色 + 审稿 + **审稿回复生成**。"审稿回复"这个功能点很值得抄 |
| [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | 48,223 | **CC BY-NC 4.0** | **定位与您几乎一模一样**。12 个 Agent 覆盖全流程：符合 PRISMA 规范的文献综述、写作、模拟同行评审、引用核验。README 第一句就是 "AI is your copilot, not the pilot" |
| [Galaxy-Dawn/claude-scholar](https://github.com/Galaxy-Dawn/claude-scholar) | 5,510 | 需查 | 半自动科研助手，覆盖 idea → 编码 → 实验 → 写作 → 投稿。**"半自动"路线值得参考** |
| [LigphiDonk/academic-figure-generator](https://github.com/LigphiDonk/academic-figure-generator) | 2,351 | MIT | 中文项目，专做**论文配图生成**。这个思路很好：**把一个高频细分需求做到极致** |

**这一块的启示**：`academic-research-skills` 的定位与您高度重合——但它**基于 Claude Code 插件形式**，要求用户已经装了 Claude Code，且**许可证是 CC BY-NC 4.0，禁止商用**。这两点恰恰给您留了空间。

### 2.4 端到端"AI 科学家"（不是您，但必须看懂）

| 项目 | 星标 | 许可证 | 定位 |
|---|---|---|---|
| [SakanaAI/AI-Scientist](https://github.com/SakanaAI/AI-Scientist) | 14,561 | 需查 | 首个全自动科研流水线，生成的论文通过了 ICLR 2025 workshop 双盲评审（6.33/10，高于 workshop 平均 4.87） |
| [SakanaAI/AI-Scientist-v2](https://github.com/SakanaAI/AI-Scientist-v2) | 7,153 | 需查 | v2 改用树搜索探索实验空间，单篇成本降到约 3 美元 |
| [SamuelSchmidgall/AgentLaboratory](https://github.com/SamuelSchmidgall/AgentLaboratory) | 5,849 | MIT | 强调 **"You are the pilot"**，把 AI 定位成研究助理而非科学家替代品 |
| [HKUDS/AI-Researcher](https://github.com/HKUDS/AI-Researcher) | 5,741 | 需查 | NeurIPS 2025 Spotlight，香港大学团队，明确对标 Google Co-Scientist 的开源替代 |
| [Future-House/robin](https://github.com/Future-House/robin) | 709 | Apache-2.0（部分） | 首个实现"文献检索→假设生成→实验设计→湿实验→数据分析"闭环的系统，《Nature》报道 |
| [microsoft/RD-Agent](https://github.com/microsoft/RD-Agent) | 14,643 | 需查 | 面向数据驱动的研发自动化，工业界视角 |

> **这一块给您的最大价值，是"不要做什么"的清单。**
> `AI-Scientist` 论文的 Limitations 部分和研究者的复现报告，明确列出了全自动流水线的固有失败模式：**实现错误、结果幻觉、走捷径、把 bug 说成发现、方法论编造、引用幻觉**。
> `academic-research-skills` 正是读了这篇论文之后，才把产品定位改成"人在环内"的。**您 PRD 里"不代写、不编造、不替用户下结论"的定位，方向是对的**——现在有实证研究支撑了。

---

## 三、七个"别人已经替你踩过"的设计决策（本报告最有价值的部分）

### 3.1 引用幻觉是头号敌人，必须做成强制机制，而不是"注意事项"

**证据**：一项 2026 年的审计研究统计了 250 万篇论文中的 1.11 亿条引用，保守估计**仅 2025 年就产生了约 14.7 万条虚构引用**，且 2024 年中期出现明显拐点。OpenScholar 团队的测试更直接：**GPT-4o 生成的引用中 78%–90% 是编造的**。

**别人怎么做**：

- PaperQA2：把"证据不足"作为**合法输出**，而不是强行给答案；额外做**撤稿状态检查**（自信地引用一篇被撤稿的论文，比什么都不引用更糟）。
- OpenScholar：生成初稿 → 自我审稿 → 迭代修订 → **引用逐条核验**，四道关卡。

**您该抄什么**（可直接改进 PRD 的 M2-1、M2-2、M2-5）：

1. 每条引用必须可点击、可打开、指向真实存在的文献；
2. "没找到"必须是系统可以坦然给出的答案，并明确提示；
3. **新增一条：撤稿状态检查**——这是 PRD 目前没有的，但成本极低、价值极高；
4. 把"引用核验通过率"作为对外公开的质量指标。

### 3.2 把定位写成一句话，到处重复

**别人怎么做**：

- `academic-research-skills`（48k 星）README 第一句：**"AI is your copilot, not the pilot."** 并且明确说"我们不帮你掩盖用了 AI，我们帮你写得更好"。
- `Agent Laboratory`（5.8k 星）：**"You are the pilot."**

**您该抄什么**：把这句写进 README 第一行、产品首页、以及**每次 AI 输出结果的页脚**。这不是文案工作，这是信任工程——科研用户最担心的就是"被工具带偏"。

### 3.3 渐进式阅读：先看摘要，再下全文，能省一个数量级的钱

**别人怎么做**：`Paper-Agent` 的流程是——检索 → **先读摘要判断相关性** → 达标的才下载全文 → PDF 转 Markdown → 分块 → 建立本地索引。不合格的文献根本不会进入昂贵的全文处理环节。

**您该抄什么**：这是成本控制最关键的一招。**别一上来就把整篇 PDF 塞给模型。** 您 PRD 的 5.2 性能章节里可以补上这条设计原则。

### 3.4 分级调用模型 + 把花费透明化

**别人怎么做**：`Paper-Agent` 给检索、阅读、分析、写作等不同阶段配置**不同档位的模型**，并在界面上**显示每个环节实际消耗了多少 token**。

**您该抄什么**：

- 检索与摘要用便宜模型，写作与推理用强模型；
- **把用量显示给用户**。科研人员往往自费或用有限的课题经费，对"花了多少"高度敏感，透明本身就是信任来源。

### 3.5 长任务必须"看得见、断得掉、接得上"

**别人怎么做**：`Paper-Agent` 用 SSE 把检索、阅读、分析、大纲、逐节写作的进度实时推送到界面；会话与中间产物用 SQLite 持久化，**刷新浏览器不丢失**；依赖挂了能"保存现场"，修好后从中断处继续。

**您该抄什么**：您 PRD 的 5.1 / 5.2 里写了"可撤销""显示进度"，但没写**"可中断、可恢复"**。这是长流程任务的生死线——一个跑了 20 分钟的文献综述任务因为网络抖动全没了，用户会直接流失。

### 3.6 "数据不出本机"是可以做出来的产品卖点，不只是合规要求

**别人怎么做**：

- `K-Dense BYOK`：桌面端运行，自带 API Key，**数据留在本机**，只有重计算才可选上云；
- `local-deep-research`：**SQLCipher 全盘加密**，可完全离线跑本地模型；
- `Chat2DB`：明确宣称"**只上传表结构，数据本地处理**，绝不上传数据和它给 LLM"。

**您该抄什么**：把"敏感数据本机处理"从您 PRD 附录里的待定项（P2）**提前到 P1**。对于未发表的实验数据，"能不能不上传"是信任的分水岭——而这恰恰是通用 AI 助手做不到的。

### 3.7 别做独立 App，先做成 SKILL.md 技能包

**为什么**：

- Agent Skills 是 Anthropic 在 2025 年 12 月发布的**开放标准**，核心就是"一个文件夹 + 一个 SKILL.md 文件"，本质是 YAML 头 + Markdown 正文，**用记事本就能写**；
- 到 2026 年已有 **40 多个产品支持**：Claude Code、Cursor、Codex、Gemini CLI、GitHub Copilot、VS Code、JetBrains、OpenHands……横跨互相竞争的产品，才是真标准；
- `anthropics/skills` 仓库 **176,541 星**，`K-Dense-AI/scientific-agent-skills` 靠 **166 个 SKILL.md** 拿到 **45,078 星**，`vercel-labs/skills` 31,720 星并提供了 `npx skills` 安装工具。

**您该抄什么**：把您的"科研技能"打包成标准 SKILL.md 目录，例如：

- `reference-format-gbt7714`（按国标排参考文献）
- `journal-preflight-check`（投稿前体检清单）
- `clean-experiment-data`（实验数据清洗规范）
- `interpret-statistics-plainly`（把统计结果翻译成大白话）

**这条策略的价值**：**一次编写，多个客户端可用**。您不需要先做出一个完整的 App 才有人用——**这是零成本的获客渠道**，而且能更快验证哪些技能真的被需要。

---

## 四、您的差异化机会在哪

综合上面的盘点，这个赛道有 **5 个明显空白**，而且它们恰好都在您 PRD 的射程内：

| 空白 | 现状 | 您的机会 |
|---|---|---|
| **学科空白** | 现有项目 90% 面向计算机/机器学习。AI-Scientist、Agent Laboratory、AI-Researcher 全部要求写代码 + 有 GPU | 面向**材料、化学、生物、医学、农学、社科**的研究生——他们人数更多，且完全没人服务 |
| **语言空白** | 除 gpt_academic、Paper-Agent、ChatPaper 外，几乎全部英文优先 | **中文母语者的"中式英语"润色**是刚需，且现有工具做得都不够细 |
| **打通空白** | 做文献的不做数据，做数据的不做文献，写作工具是独立的桌面软件 | **"课题空间"把三件事串起来**——目前没有项目认真做过这件事 |
| **门槛空白** | 端到端项目都要求会用命令行、会配环境、会写代码 | **零代码、说人话就能用**，这是您 PRD 里最该守住的差异化 |
| **诚信空白** | 几乎所有开源项目都不谈学术诚信，`academic-research-skills` 是少数例外 | **把"不代写、不编造"做成明确的产品承诺**，这在高校场景是准入证 |

**建议对外的一句话定位**（可直接用于 README 首行）：

> **给非计算机专业研究生用的、中文优先、数据 / 文献 / 写作三件事打通、敏感数据可以不出本机的科研工作台。我们不替你写论文，我们替你干掉体力活。**

**命名提示**：`SciMate` 这个名字目前在 GitHub 上基本是空的（只有几个 0–1 星的空仓库），**基本可以直接用**。但建议正式定名前再查一次商标和域名。

---

## 五、可以不重造的东西（直接拿来用的清单）

| 需要的能力 | 现成方案 | 说明 |
|---|---|---|
| 文献检索与元数据 | **arXiv、OpenAlex、Semantic Scholar、Crossref、PubMed** | 全部提供免费开放接口，`Paper-Agent` 已验证三源并行可行 |
| 全文 PDF → 结构化文本 | **GROBID、marker** | 把 PDF 变成可检索的 Markdown / XML，是文献模块的地基 |
| 文献管理互通 | **Zotero**（社区已有 MCP 服务） | 用户已有的文献库可以直接复用，避免重复导入 |
| 参考文献格式 | **CSL / citeproc** | 期刊模板生态现成，不要自己写格式引擎 |
| 统计分析 | **pandas / statsmodels / scipy / matplotlib** | 统计部分千万别自研，用成熟库 + AI 负责"选方法和解释" |
| 代码沙箱执行 | **E2B、OpenHands**（MIT） | 让 AI 写的分析代码在隔离环境里跑，安全且可控 |
| 工作流编排 | **LangGraph** | `Paper-Agent` 同款，适合需要状态管理和可中断恢复的场景 |
| 技能打包标准 | **agentskills.io** | 见 3.7，强烈建议采用 |

---

## 六、开源前必须搞清楚的三件事

### 6.1 许可证：别把 CC BY-NC 的代码抄进您的项目

> ⚠️ **特别提醒**：`academic-research-skills`（48,223 星，定位与您最接近）的许可证是 **CC BY-NC 4.0 —— 禁止商业使用**。它的思路可以学，但**代码不能拿**。如果您计划未来商用或接受赞助，这一点必须从第一天就守住。

| 项目 | 许可证 | 借鉴代码是否安全 |
|---|---|---|
| paper-qa | Apache-2.0 | ✅ 安全 |
| gpt-researcher | Apache-2.0 | ✅ 安全 |
| openinterpreter | Apache-2.0 | ✅ 安全 |
| storm | MIT | ✅ 安全 |
| Agent Laboratory | MIT | ✅ 安全 |
| DeepAnalyze | MIT | ✅ 安全 |
| scientific-agent-skills | MIT | ✅ 安全 |
| **academic-research-skills** | **CC BY-NC 4.0** | ❌ **禁止商用，只可参考思路** |
| gpt_academic | GPL-3.0 | ⚠️ 传染性强，抄代码会要求您也开源 |
| zotero-arxiv-daily | AGPL-3.0 | ⚠️ 传染性最强，谨慎 |
| AI-Scientist / v2、ChatPaper | 自定义（非标准） | ⚠️ 必须逐字读 LICENSE 文件 |

**建议**：您的项目采用 **Apache-2.0**——比 MIT 多一条明确的专利授权条款，对想用的企业和高校最友好，也是这一领域最主流的选择（paper-qa、gpt-researcher、opencode 都在用）。

### 6.2 学术署名：开源不等于可以随便发

如果您打算把这套系统写成论文发表，**请先确认学校、导师和课题组对"开源时间点"与"论文投稿顺序"的要求**。国内部分高校和期刊对"先开源后投稿"有明确规定，这一条建议在动手写代码之前就问清楚。

### 6.3 文献数据源的使用条款

即使接口是免费开放的，各家的**调用频率、商用范围、是否要求署名**规定不同（arXiv、OpenAlex、Semantic Scholar、Crossref 各有各的条款）。在把某个源写进产品之前，把它的使用条款读一遍——这是很多项目上线后才被发现的问题。

---

## 七、建议的下一步（三件事，按顺序做）

| 顺序 | 做什么 | 为什么 |
|---|---|---|
| **第 1 步** | **改 PRD**：把"文献检索"和"引用格式"从"要自研"改成"用开放接口 + CSL 模板"；把"敏感数据本机处理"从 P2 提到 P1；补上"撤稿检查""任务可中断恢复"两个点 | 半天的工作量，能砍掉大量重复劳动，并补上两个明显缺口 |
| **第 2 步** | **做一次 3 天的手工验证**：先不写代码，用现成工具（gpt_academic + DeepAnalyze + Paper-Agent）亲手跑一遍您 PRD 里的场景 A（数据→图）和场景 B（摸清新方向），记录**每一步卡在哪** | 这比再写一万字文档有用。真实卡点会直接告诉您第一版该做什么 |
| **第 3 步** | **决定路线**：做"独立产品"还是"SKILL.md 技能包 + 轻量外壳"？ | 前者重、可控、容易收费；后者轻、借生态、起量快。这个决定会影响后面所有排期 |

---

## 八、补充调研（V1.1 新增）：Skill 生态的真实规模

> **为什么有这一章**：V1.0 成稿后，用户提了一个关键问题——「是不是大多数被验证过的项目都是 Skill 形式？我是不是也可以先从 Skill 开始？」
> 为此做了第二轮针对性检索。结果是：**V1.0 严重低估了 Skill 形态在科研领域的实际规模**。这一章把实测数据补上，并修正前面的判断。

### 8.1 科研类 Skill 项目的真实现状

以下全部为 2026-09-16 GitHub 官方 API 实测值：

| 项目 | 星标 | 许可证 | 创建时间 | 说明 |
|---|---|---|---|---|
| [wanshuiyin/Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)（ARIS） | 16,165 | MIT | 2026-03 | 纯 Markdown skill，约 6 个月到这个量级 |
| [Orchestra-Research/AI-Research-SKILLs](https://github.com/Orchestra-Research/AI-Research-SKILLs) | 12,710 | MIT | 2025-11 | AI 研究与工程 skill 库 |
| [jihe520/MathModelAgent](https://github.com/jihe520/MathModelAgent) | 5,577 | 无 | 2025-01 | **中文**，数学建模 Agent + skills |
| [zLanqing/codex-claude-academic-skills](https://github.com/zLanqing/codex-claude-academic-skills) | 3,929 | 需查 | — | **中文**，已覆盖「文献阅读 → 论文写作 → 科学计算」 |
| [brycewang-stanford/Auto-Empirical-Research-Skills](https://github.com/brycewang-stanford/Auto-Empirical-Research-Skills) | 3,817 | 自定义 | 2026-04 | 实证研究 skill 集合 |
| [google-deepmind/science-skills](https://github.com/google-deepmind/science-skills) | 3,053 | Apache-2.0 | 2026-05 | **DeepMind 官方入场** |
| [LigphiDonk/academic-figure-generator](https://github.com/LigphiDonk/academic-figure-generator) | 2,351 | MIT | — | **中文**，论文配图 |
| [aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills) | 1,880 | 需查 | — | 医学研究方向 |
| [ai4s-research/open-science](https://github.com/ai4s-research/open-science) | 1,651 | 自定义 | 2026-07 | **local-first 桌面科研工作台** |
| [huangkiki/dailypaper-skills](https://github.com/huangkiki/dailypaper-skills) | 1,232 | Apache-2.0 | 2026-02 | 论文流水线 |
| [xuzhougeng/wisp-science](https://github.com/xuzhougeng/wisp-science) | 1,142 | **AGPL-3.0** | 2026-07 | **local-first 桌面科研工作台** |
| [LeonChaoX/qinyan-academic-skills](https://github.com/LeonChaoX/qinyan-academic-skills) | 899 | 需查 | — | 182 个可安装技能，多语言 |
| [InternScience/Awesome-Scientific-Skills](https://github.com/InternScience/Awesome-Scientific-Skills) | 548 | MIT | 2026-03 | 科研 skill 清单 |
| [Gostyan/docx-skill-4-cn-paper](https://github.com/Gostyan/docx-skill-4-cn-paper) | 413 | MIT | 2026-03 | **中文**论文排版格式 |

此外还有数十个更小的中文 skill（文献综述、组会 PPT、R 语言出版级绘图、论文辅导、报告打假等）。更值得注意的信号是：**已经出现 `kael-odin/awesome-academic-research-skills` 这类「面向中文用户的学术 Agent Skill 每日排行榜」仓库**——一个赛道卷到有人专门做排行榜，说明它已经进入拥挤期。

### 8.2 判断修正：不是「大多数」，但确实是增长最快的一极

关键是要把「验证」拆成两种含义，否则会得出错误结论：

| 「验证」指什么 | 判断标准 | 哪种形态占优 |
|---|---|---|
| **技术路线被验证** | 有 benchmark、被真实科研流水线采用、有同行评议论文 | **独立实现占绝对多数** |
| **产品被验证** | 有人真的装、真的用、真的反馈 | **Skill 形式增长更快** |

**支持第一条的证据**：被真实科研流水线采用、有 benchmark 的项目几乎全是独立实现——`paper-qa`（9,203 星，被 FutureHouse 的 Robin 用作底层文献引擎）、`storm`（31,401 星，斯坦福，NAACL 2024）、`DeepAnalyze`（4,623 星，有论文与评测基准）。

**支持第二条的证据**：ARIS 从 2026 年 3 月创建、纯 Markdown 形态，约半年到 16,165 星；DeepMind 也在 2026 年 5 月亲自下场发布 `science-skills`。

**所以对「大多数验证过的项目是不是 Skill 形式」的准确回答是**——**不是大多数，但它是增长最快、进入门槛最低的一极，而且已经开始拥挤。**

### 8.3 必须知道的新情况：「本地优先工作台」已经有先行者

V1.0 第四章判断「三件事打通 + 课题空间」是空白。第二轮检索后，这个判断需要**收窄**：

| 先行者 | 星标 | 与您 PRD 的重合点 |
|---|---|---|
| `xuzhougeng/wisp-science` | 1,142 | 自称 "local-first desktop AI research workbench for scientists" |
| `ai4s-research/open-science` | 1,651 | 自称 "local-first, model-agnostic AI research workspace" |
| `zLanqing/codex-claude-academic-skills` | 3,929 | 已覆盖「文献阅读 → 论文写作 → 科学计算」全流程 |

**判断修正**：空白从「完全没人做」变成「**有人在做，但都还小（1–4k 星），中文生态里没有明显赢家**」。**窗口还开着，但比 V1.0 判断的窄。**

---

## 九、路线建议：Skill 先行 + 工作台兜底

针对「是否可以先从 Skill 起步」——**答案是：可以，但必须分清它到底验证了什么。**

### 9.1 Skill 形式天然能承担 / 承担不了什么

| 维度 | Skill 形式 | 独立工作台 |
|---|---|---|
| 编写门槛 | 极低（YAML 头 + Markdown，记事本能写） | 高（前端 / 后端 / 数据库 / 部署） |
| 账号、并发、性能 | **由客户端承担** | 自己要解决 |
| 分发 | 装进 40+ 个现成客户端 | 自己拉新 |
| 验证周期 | 以「天」计 | 以「月」计 |
| 跨会话的项目空间 | 做不到（每次都是新上下文） | **正是它的价值** |
| 跨能力状态共享 | 做不到（数据 skill 拿不到文献 skill 的结果） | **可以** |
| 数据不出本机 | 做不到（内容仍会发给模型厂商） | 可以承诺 |
| 长任务中断 / 恢复 | 做不到 | 可以 |
| 向用户收费 | 几乎不可能 | 可以 |

**这张表的读法**：左列是「您不需要自己解决」的部分——这正是先做 skill 的最大好处；右列是「只有工作台能解决、也是您真正护城河」的部分。

**结论**：Skill 能验证「**单个技能有没有人真的需要**」，验证不了「**工作台这个产品成不成立**」。这是两件独立的事，不能互相替代。

### 9.2 建议的三层路线

| 层 | 时间 | 做什么 | 验证什么 |
|---|---|---|---|
| **第一层：Skill** | 现在，2–4 周 | 只做 **1 个**技能，且必须是现有 skill 没做好的 | 需求真伪 + 练 prompt 工程 |
| **第二层：工作台** | 验证成功后 | 只做 skill 做不到的：**课题空间 + 三件事串联 + 本机处理** | 产品是否成立 |
| **第三层：反向导出** | 有用户之后 | 把工作台的能力也导出成 skill，让其他客户端能消费 | 反哺分发 |

**第一层选哪一个技能？** 判断标准：现有 skill 做得差 + 高频 + 能体现「不编造」定位。

| 候选技能 | 现有情况 | 推荐度 |
|---|---|---|
| **引用核验（含撤稿检查）** | 现有 skill 几乎无人做，而这正是行业最大痛点 | 高 |
| **投稿前体检清单** | 高频、边界清晰、结果可验证 | 高 |
| 统计结果的大白话解释 | 现有 skill 都在做「生成图表」，没人做「解释结果」 | 中 |

**明确不建议做**：「文献检索」「论文润色」「论文配图」——这三类已经有几十个 skill 在做了，新项目进去只会被淹没。

### 9.3 选型时的许可证红线（补充）

| 项目 | 许可证 | 注意 |
|---|---|---|
| `xuzhougeng/wisp-science` | **AGPL-3.0** | 传染性最强，参考思路可以，抄代码风险高 |
| `ai4s-research/open-science` | 自定义（非标准） | 需逐字读 LICENSE |
| `brycewang-stanford/Auto-Empirical-Research-Skills` | 自定义（非标准） | 需逐字读 LICENSE |
| ARIS / AI-Research-SKILLs | MIT | 可安全参考 |
| DeepMind `science-skills` | Apache-2.0 | 可安全参考 |

---

## 十、架构建议：把工作台做成「技能宿主」

> **为什么有这一章**：用户提出——「既然 Skill 方向已有大量成熟案例，我的工作台是否也可以支持引入他们的 Skill？」
> 答案是**可以，而且这比"自己做全部功能"更聪明**。这一章说明技术可行性、四个必须解决的问题、以及它对 PRD 阶段一范围的直接影响。

### 10.1 核心思路转换：技能生态是上游供应链，不是竞争对手

| 路线 | 你在跟谁竞争 | 结果 |
|---|---|---|
| 自己做技能 | 跟 45,078 星的 `scientific-agent-skills`、3,053 星的 DeepMind `science-skills` 正面竞争 | 大概率被淹没 |
| **做技能宿主** | 只在「宿主能力」上竞争 | **吸收整个技能生态** |

**一句话**：不要做"另一个技能提供方"，要做"**科研场景下最好的技能运行环境**"。

### 10.2 技术上为什么可行：这个标准简单得不像话

Agent Skills 是开放标准（agentskills.io），一个技能就是**一个文件夹 + 一个 SKILL.md**：

```text
my-skill/
├── SKILL.md        # 必需：YAML 头 + Markdown 指令
├── scripts/        # 可选：可执行脚本
├── references/     # 可选：按需加载的参考资料
└── assets/         # 可选：模板、数据文件
```

- **只有两个必填字段**：`name`（小写字母/数字/连字符，≤64 字符，须与文件夹名一致）、`description`（≤1024 字符）
- **四个可选字段**：`license`、`compatibility`（环境要求）、`metadata`、`allowed-tools`（实验性）
- **加载分三阶段**（渐进式披露）：Discovery（启动时只读 name + description，约 100 tokens/技能）→ Activation（任务匹配时读入完整 SKILL.md）→ Execution（按需加载 references 或执行 scripts）

**没有 SDK、没有编译步骤、没有专有 API。** 这意味着：**您的团队只要实现一个"技能加载器"，就能吃下整个生态。**

### 10.3 但有四个必须解决的问题（别低估）

#### 问题 1：许可证——最容易踩坑的地方

**技能仓库的许可证 ≠ 每个 SKILL.md 的许可证**，两者可能不一致。

| 做法 | 风险 | 建议 |
|---|---|---|
| 工作台**预装/内置**第三方技能 | 高（属于再分发，需逐个核对每个技能的许可证） | ❌ 不推荐 |
| **只提供"从本地目录 / Git 仓库加载"能力** | 低（用户自己决定装什么，责任边界清晰） | ✅ **推荐** |
| 建立"官方推荐技能"名单 | 中（需建立白名单并逐个审查） | 慎重，要做就做严格审核 |

**红线**：`AGPL-3.0`（如 `wisp-science`）、`CC BY-NC`（不可商用，如 academic-research-skills）一律不得进入预装或推荐名单。
这个关系的本质，可以类比「**浏览器 vs 浏览器扩展**」——浏览器不预装扩展，但提供加载扩展的能力。

#### 问题 2：技能是「程序性知识」，不是「数据通道」

这是**最容易被低估的技术门槛**。SKILL.md 本质是"指令文本 + 脚本 + 参考材料"，它**默认宿主已经具备**：读写文件、执行命令、访问网络、调用 MCP 服务。

> ⚠️ **如果工作台只是一个网页应用，没有文件系统访问和代码执行能力，那么 skill 会退化成"一段提示词"**——里面写得再精妙的脚本也跑不起来。

**所以必须先建执行环境**（这是重活，但绕不过去）：

| 能力 | 现成方案 |
|---|---|
| 代码沙箱 | E2B（Apache-2.0）、OpenHands（MIT）、容器 |
| 文件访问 | 本地桌面端 / 用户授权目录 |
| MCP 支持 | 实现 MCP 客户端，让技能能挂载外部数据源 |
| 网络 | 受控出网 + 白名单 |

#### 问题 3：兼容性降级

大量技能依赖特定客户端专有能力（Claude Code 的 Task/Agent、TodoWrite、`allowed-tools` 字段、特定 MCP server）。移植过来**必然有一部分失效**。

**应对**：做一层**兼容性适配**——把不支持的调用映射到等价能力，映射不了的就优雅降级，并在加载技能时明确提示"此技能部分功能在当前环境下不可用"。**不要假装能用然后静默失败。**

#### 问题 4：上下文成本

渐进式披露解决了"装很多技能但不占满上下文"，但技能一多仍有成本：**装 100 个技能，光目录（name + description）就要约 1 万 tokens。**

**应对**：做**技能检索与推荐**，按当前任务匹配最相关的 3–5 个技能注入，而不是全量铺开。

### 10.4 目录约定：兼容社区惯例，降低迁移成本

| 客户端 | 读取路径 |
|---|---|
| Claude Code | `.claude/skills/` |
| Codex 及多数其他客户端 | `.agents/skills/` |
| 社区常见做法 | 保留一个规范目录，另一个用符号链接指过去 |

**建议**：工作台**同时兼容这两个路径**——用户已有的技能文件夹可以直接拿来用，零迁移成本。这是最容易做、收益最直接的一件事。

### 10.5 这直接改写了 PRD 的阶段一范围（重要）

原 PRD 阶段一列了 11 项 P0 功能。采用"技能宿主"架构后，可以大幅缩减：

| 原 PRD 功能 | 调整建议 | 理由 |
|---|---|---|
| M2-1 文献检索 | **借用技能 + 开放接口** | 生态里已有多个成熟实现 |
| M1-4 图表生成 | **借用技能** | 已有 R/ggplot2、中文科研绘图技能 |
| M3-5 格式与投稿准备 | **借用技能 + 补中文期刊模板** | 已有 GB/T 7714 排版技能 |
| M3-3 语言润色与翻译 | **借用技能 + 自己做中文优化** | 中文"中式英语"是少数值得自研的差异点 |
| M3-7 学术诚信提示 | **保留自研** | 体现产品定位，且没有现成技能 |
| **课题空间** | **保留自研** | 技能做不到（跨会话持久化） |
| **技能加载器 / 技能编排** | **保留自研** | 这就是宿主本身 |
| **本机处理** | **保留自研** | 技能做不到（内容仍会发给模型厂商） |
| **长任务中断恢复** | **保留自研** | 技能做不到 |

**结论**：改写后的阶段一，**真正要自己写的只剩 5 件事**——课题空间、技能加载器、技能编排、本机处理、长任务恢复。其余靠技能生态顶上。**工作量的量级会明显下降。**

### 10.6 新增的四类风险

| 风险 | 说明 | 应对 |
|---|---|---|
| **上游技能质量参差** | 随便装一个技能可能出错，甚至包含有害脚本 | 安装前审查 + 运行沙箱隔离 + 权限提示 |
| **上游技能"断供"** | 作者删库、改名或变更协议 | **锁定版本（记 Git commit），不追 main 分支** |
| **宿主能力被平台覆盖** | Claude Code / Cursor 自己也在往科研场景走，且 DeepMind 已发布官方技能 | 靠"**科研专用宿主**"定位 + 中文场景 + 本机处理构建差异 |
| **安全** | 技能可携带可执行脚本 | 绝不静默执行；沙箱运行；用户显式授权 |

### 10.7 一句话总结

> **做技能，你在跟 45,078 星的巨头抢饭吃；做宿主，你在收编它们的饭。**

但前提是：**先把执行环境（文件 + 沙箱 + 网络 + MCP）搭起来**，否则"加载技能"只是纸面能力。

---

## 附：本报告的数据核验说明

**所有星标、许可证、最近更新日期，均为 2026 年 9 月 16 日通过 GitHub 官方 API 直接读取的实测值。**

之所以强调这一点：本次调研中发现，搜索引擎结果里有**相当比例是 AI 生成的二手文章，且给出的星标数严重失真**。例如某篇被广泛转载的文章称 `scientific-agent-skills` 约 2.5 万星，实测为 **45,078 星**；称另一个项目约 2.1 万星，实测为 **48,223 星**。**引用失真的项目数据会直接导致错误的选型判断**——这一点，恰好也印证了本报告 3.1 节的核心论点。

**本报告调研的项目清单**（共 26 个）：

paper-qa、OpenScholar、storm、gpt-researcher、Paper-Agent、local-deep-research、agentic-literature-review、LitRevResearchAgent、DeepAnalyze、data-formulator、pandas-ai、openinterpreter、aviary、gpt_academic、ChatPaper、academic-research-skills、claude-scholar、academic-figure-generator、AI-Scientist、AI-Scientist-v2、AgentLaboratory、AI-Researcher、robin、RD-Agent、scientific-agent-skills、k-dense-byok、OpenHands、E2B、zotero-arxiv-daily、anthropics/skills、vercel-labs/skills、Awesome-Agent-Scientists、awesome-autoresearch、Awesome-Vibe-Research。

**V1.1 补充调研新增的项目**（共 17 个）：

ARIS（Auto-claude-code-research-in-sleep）、AI-Research-SKILLs、MathModelAgent、codex-claude-academic-skills、Auto-Empirical-Research-Skills、google-deepmind/science-skills、medical-research-skills、ai4s-research/open-science、dailypaper-skills、wisp-science、qinyan-academic-skills、Awesome-Scientific-Skills、docx-skill-4-cn-paper、paper2anything、posterly、AI-Powered-Literature-Review-Skills、awesome-academic-research-skills。

---

**报告结束**

*本报告为 V1.1。欢迎在评审时直接指出不同意的判断——尤其是第四章的差异化结论与第九章的路线建议，这两部分最需要用真实用户验证。*
