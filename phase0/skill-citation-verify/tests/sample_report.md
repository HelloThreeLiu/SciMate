# 引用核验报告（引用真实性核验 · 含撤稿检查）

- 生成时间：2026-09-16 22:13:28
- 输入文件：`sample_references.txt`
- 核验条数：10 条 · 耗时 0 秒
- 数据源：OpenAlex（主路）+ Crossref（辅路，含 Retraction Watch 数据）

## 总览

| 状态 | 条数 | 占比 |
|---|---|---|
| 🚨 已撤稿 | 1 | 10% |
| ❌ DOI 查无此文（疑似编造） | 1 | 10% |
| ⚠️ DOI 未收录，同题文献疑存在 | 1 | 10% |
| ❓ 未能核实，请人工确认 | 2 | 20% |
| ✅ 已核实（标题匹配） | 2 | 20% |
| ✅ 已核实（DOI 直查） | 3 | 30% |

- **口径一（可核实引用中确认真实存在的比例）**：5/7 = 71%
- **口径二（被标注「未能核实 / 查无此文」的比例）**：3/10 = 30%

> 口径说明：DOI 直查 = 在权威数据库中按 DOI 精确命中；标题匹配 = 无 DOI 时按题名+作者+年份交叉匹配并要求作者/年份锚点，置信度达阈值才计为核实。两者都**不等于绝对真实**，最终请以人工抽查为准。「DOI 未收录」单独一档，不计入两口径。

## 逐条结果

### [2] 🚨 已撤稿
- **引用原文**：[2] Wakefield A J, Murch S H, Anthony A, et al. Ileal-lymphoid-nodular hyperplasia, non-specific colitis, and pervasive developmental disorder in children[J]. The Lancet, 1998, 351(9103): 637-641. doi:10.1016/S0140-6736(97)11096-0
- **匹配文献**：RETRACTED: Ileal-lymphoid-nodular hyperplasia, non-specific colitis, and pervasive developmental disorder in children（1998） — DOI: 10.1016/s0140-6736(97)11096-0
- **核实途径**：OpenAlex（DOI 直查）
- **🚨 撤稿警示**：OpenAlex 标记该文献已被撤稿；Crossref 撤稿记录：撤稿通知 DOI 10.1016/s0140-6736(10)60175-4（Retraction，来源 retraction-watch，2010-2-6）——**继续引用已撤稿论文可能造成严重学术问题，请立即处理**

### [3] ❌ DOI 查无此文（疑似编造）
- **引用原文**：[3] Zhang Y, Li X, Wang H. A novel deep learning framework for protein folding prediction with ultra-high accuracy[J]. Nature Biotechnology, 2025, 43(3): 456-470. doi:10.1038/s41587-025-99999-x
- **说明**：DOI 10.1038/s41587-025-99999-x 在 OpenAlex 与 Crossref 均查无此文，且未找到同题文献——疑似编造的引用，请务必人工确认

### [1] ⚠️ DOI 未收录，同题文献疑存在
- **引用原文**：[1] Vaswani A, Shazeer N, Parmar N, et al. Attention is all you need[C]//Advances in Neural Information Processing Systems. 2017: 5998-6008. doi:10.5555/3294771.3295384
- **匹配文献**：Attention Is All You Need（2025） — DOI: 10.65215/r5bs2d54
- **核实途径**：Crossref（书目检索）
- **说明**：引用中的 DOI（10.5555/3294771.3295384）未被 OpenAlex/Crossref 收录，但存在同题文献（相似度 1.0）——DOI 可能无效或未注册，请核对 DOI 是否抄写正确

### [6] ❓ 未能核实，请人工确认
- **引用原文**：[6] 周志华. 机器学习[M]. 北京: 清华大学出版社, 2016.
- **说明**：未能核实——两库均无足够置信的匹配（图书/中文教材常不在收录范围），请人工确认

### [10] ❓ 未能核实，请人工确认
- **引用原文**：[10] Liu W, Wang X. Some preliminary studies on artificial intelligence[J]. Journal of Generic Studies, 2020, 15(2): 1-12.
- **说明**：未能核实——两库均无足够置信的匹配（图书/中文教材常不在收录范围），请人工确认

### [5] ✅ 已核实（标题匹配）
- **引用原文**：[5] Devlin J, Chang M W, Lee K, Toutanova K. BERT: pre-training of deep bidirectional transformers for language understanding[C]//Proceedings of NAACL-HLT. 2019: 4171-4186.
- **匹配文献**：BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding（2019） — DOI: 10.18653/v1/n19-1423
- **核实途径**：OpenAlex（标题检索）
- **说明**：标题匹配相似度 1.0（无 DOI，属间接核实，请以原文为准）

### [8] ✅ 已核实（标题匹配）
- **引用原文**：[8] Goodfellow I, Bengio Y, Courville A. Deep learning[M]. Cambridge: MIT Press, 2016.
- **匹配文献**：Deep Learning（2016）
- **核实途径**：OpenAlex（标题检索）
- **说明**：标题匹配相似度 1.0（无 DOI，属间接核实，请以原文为准）

### [4] ✅ 已核实（DOI 直查）
- **引用原文**：[4] Kucsko G, Maurer P C, Yao N Y, et al. Nanometre-scale thermometry in a living cell[J]. Nature, 2013, 500(7460): 54-58. doi:10.1038/nature12373
- **匹配文献**：Nanometre-scale thermometry in a living cell（2013） — DOI: 10.1038/nature12373
- **核实途径**：OpenAlex（DOI 直查）

### [7] ✅ 已核实（DOI 直查）
- **引用原文**：[7] Hochreiter S, Schmidhuber J. Long short-term memory[J]. Neural Computation, 1995, 9(8): 1735-1780. doi:10.1162/neco.1997.9.8.1735
- **匹配文献**：Long Short-Term Memory（1997） — DOI: 10.1162/neco.1997.9.8.1735
- **核实途径**：OpenAlex（DOI 直查）
- **⚠️ 差异**：年份不符：引用写 1995，数据库为 1997

### [9] ✅ 已核实（DOI 直查）
- **引用原文**：[9] Kucsko G, Maurer P C, Yao N Y, et al. Nanometre-scale thermometry in a living cell[J]. Nature, 2015, 500(7460): 54-58. doi:10.1038/nature12373
- **匹配文献**：Nanometre-scale thermometry in a living cell（2013） — DOI: 10.1038/nature12373
- **核实途径**：OpenAlex（DOI 直查）
- **⚠️ 差异**：年份不符：引用写 2015，数据库为 2013

---
*本报告由脚本自动生成（OpenAlex + Crossref 公开接口），只陈述数据库可查证的事实；「未能核实」不代表引用有误，「已核实」也不替代人工判断。*