# 领域文档

本仓库采用多上下文领域文档布局。

## 开始工作前

1. 阅读内容 Vault 中的 `sutra-pavilion/CONTEXT-MAP.md`（ADR-0003：内容 Vault 命名为项目名称）；
2. 根据任务涉及的上下文读取：
   - `sutra-pavilion/knowledge/CONTEXT.md`：知识上下文；
   - `sutra-pavilion/sources/CONTEXT.md`：来源上下文；
3. 阅读 `docs/adr/` 下与任务有关的系统级架构决策；
4. 同时涉及两个上下文时，读取两份 `CONTEXT.md` 及其在上下文地图中的关系。

文件不存在时静默继续，不为形式完整而预先创建领域文档。

## 布局

- `sutra-pavilion/CONTEXT-MAP.md`：上下文导航及关系；
- `sutra-pavilion/knowledge/CONTEXT.md`：知识对象、内容生命周期、证据和检索语境术语；
- `sutra-pavilion/sources/CONTEXT.md`：来源目录、质量状态和研究材料术语；
- `docs/adr/`：跨上下文架构决策。

## 术语规则

Issue、ticket、规格、计划、测试和实现必须使用对应 `CONTEXT.md` 定义的术语，不使用其明确列入 `_Avoid_` 的同义表达。

需要的概念尚未定义时，先判断是否误用了项目词汇；确认属于真实领域缺口后，再通过领域建模流程处理。

## ADR 冲突

产物与既有 ADR 冲突时必须明确指出冲突和影响，不得静默覆盖。变更既有决策仍受 `AGENTS.md` 的人工批准和变更守恒约束。
