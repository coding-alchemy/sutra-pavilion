# 藏经阁项目结构设计

- 状态：已确认
- 日期：2026-08-23
- 范围：通用知识体系、来源库、审核、检索、图谱演进和 Obsidian 集成

## 1. 目标

藏经阁用于单人维护、AI 辅助扩展的中等规模知识体系，目标容量为几十个知识库和数千篇知识条目。项目同时服务人工阅读、Obsidian 编辑、静态发布、全文检索和 AI/RAG，但第一阶段只建设内容结构、Schema、校验 CLI、审核流程和一个完整示例知识域。

项目采用两个领域上下文：

- **知识上下文**：管理知识域、知识库、知识条目、条目元数据、知识关系和发布生命周期。
- **来源上下文**：管理来源族、具体来源版本、来源笔记、质量评价、权利和可用状态。

两者通过引用连接。来源和来源笔记不是正式知识，只有经过人工审核的已发布条目才能进入正式知识检索。

## 2. 非目标

第一阶段不建设：

- 完整网站或管理后台；
- 图数据库；
- AI 自动发布；
- 无审核的大规模内容导入；
- 将搜索索引、RAG 分块或图谱导出提交到 Git；
- 将大型 PDF、扫描件和音视频直接提交到普通 Git。

## 3. 目录结构

仓库根目录同时作为 Obsidian Vault：

```text
sutra-pavilion/
├── .obsidian/                         # Obsidian 配置，选择性提交
├── .gitignore
├── README.md
├── CONTEXT-MAP.md                     # 两个领域上下文及其关系
├── pyproject.toml                     # Python 工具链
│
├── knowledge/                         # 知识上下文
│   ├── CONTEXT.md
│   ├── registry/
│   │   ├── entry-types.yaml
│   │   ├── relation-types.yaml
│   │   └── tags/
│   │       └── <namespace>.yaml
│   ├── schemas/
│   │   ├── domain.schema.json
│   │   ├── library.schema.json
│   │   ├── entry.schema.json
│   │   └── entry-types/
│   │       └── <entry-type>.schema.json
│   └── domains/
│       └── literature/
│           ├── _domain.md
│           └── libraries/
│               └── chinese-mythology/
│                   ├── _library.md
│                   ├── entries/
│                   │   └── nuwa.md
│                   └── assets/
│                       └── <entry-ulid>/
│
├── sources/                           # 来源上下文
│   ├── CONTEXT.md
│   ├── registry/
│   │   └── source-types.yaml
│   ├── schemas/
│   │   ├── source-family.schema.json
│   │   ├── source-record.schema.json
│   │   └── source-note.schema.json
│   ├── catalog/
│   │   ├── families/
│   │   │   └── <source-family-ulid>.md
│   │   └── records/
│   │       └── <source-record-ulid>.md
│   ├── notes/
│   │   └── <source-record-ulid>/
│   │       └── <note-ulid>.md
│   └── assets/
│       └── text/                      # 允许入库的小型原始文本
│
├── inbox/                             # 未进入正式上下文的材料
│   ├── imports/                       # 导入任务清单和结果报告
│   ├── raw/                           # 原始临时文件，默认忽略
│   └── extracted/                     # 可重建的 AI/OCR 提取结果，默认忽略
│
├── templates/                         # Obsidian 与 CLI 共用模板
│   ├── knowledge-entry.md
│   ├── source-family.md
│   ├── source-record.md
│   └── source-note.md
│
├── config/
│   ├── build.yaml
│   └── retrieval.yaml                # 检索字段权重和模式
│
├── docs/
│   ├── adr/
│   ├── design/
│   └── policies/
│       ├── editorial.md
│       ├── source-quality.md
│       ├── copyright.md
│       └── relationships.md
│
├── src/sutra_pavilion/                # Python 深层模块
│   ├── cli/
│   ├── knowledge/
│   ├── sources/
│   ├── validation/
│   ├── build/
│   └── retrieval/
│
├── tests/
│   ├── fixtures/
│   ├── unit/
│   └── integration/
│
└── .generated/                        # 可重建产物，全部忽略
    ├── metadata-index/
    ├── content-index/
    ├── rag/
    │   ├── formal/
    │   └── research/
    ├── graph/
    └── bibliographies/
```

## 4. Obsidian 约定

### 4.1 Vault 范围

Obsidian 直接打开仓库根目录，使 `knowledge/`、`sources/`、`inbox/`、上下文地图和 ADR 可以互相链接。`src/`、`tests/`、`.generated/`、Schema 和注册表应从 Obsidian 搜索与图谱中排除，但仍保留在同一仓库。

`.obsidian/` 只提交团队需要共享的设置、模板路径和允许的插件配置。个人工作区状态、缓存和设备相关文件不提交。

### 4.2 Markdown 优先

以下领域对象使用 Markdown：

- 知识域 `_domain.md`；
- 知识库 `_library.md`；
- 知识条目；
- 来源族；
- 来源记录；
- 来源笔记。

Schema、注册表和检索配置继续使用 YAML 或 JSON。这样既保留机器校验能力，也让所有需要人工理解和链接的领域对象成为 Obsidian Note。

### 4.3 链接与身份

Obsidian Wiki Link 用于导航和普通正文关联，例如：

```md
[[女娲]]参与了[[女娲补天]]，相关记载见[[山海经]]。
```

Wiki Link 不承担永久身份。所有知识对象和来源对象使用不可变 ULID，类型化关系引用 ULID；构建工具据此生成正式知识图谱。文件改名或移动只影响导航链接，不改变对象身份。

## 5. 知识对象格式

### 5.1 扁平 Front Matter

Obsidian 对顶层 Properties 支持更好，因此公共元数据直接位于 Front Matter 顶层，不套用 `meta:` 对象：

```yaml
---
schema_version: 1
id: 01K...
title: 女娲
slug: nuwa
aliases:
  - 女娲氏
summary: 中国神话中的创世与造人神祇。
entry_type: figure
language: zh-CN
status: draft
tags:
  - chinese-mythology
search_terms:
  - 中国创世女神
relations:
  - type: recorded_in
    target_id: 01K...
attributes:
  tradition: chinese-mythology
---
```

公共字段由 `entry.schema.json` 校验，`attributes` 由具体条目类型的 Schema 校验。标题、摘要、类型、标签、关系和其他语义元数据发生变化时，视为实质修改并重新审核。

### 5.2 条目目录

知识条目平铺在知识库的 `entries/` 下，类型与主题不参与目录嵌套。条目图片和小型媒体位于 `assets/<entry-ulid>/`，避免标题或 slug 改变造成资源身份变化。

### 5.3 生命周期

条目通过 `status` 表达状态，不因状态变化移动文件：

```text
draft → review → published → archived
```

- AI 可以创建和修改草稿、建议审核结论；
- 只有维护者可以执行发布；
- 事实、结论、关系、来源或语义元数据变化后必须重新审核；
- 排版、错别字和纯技术迁移不要求重新审核；
- 已归档条目保留身份、历史与证据链。

## 6. 来源对象格式

### 6.1 来源版本

一个来源记录对应一个可准确引用的具体版次、版本或网页快照。不同版本具有不同 ULID，并可归入同一可选来源族。ISBN、DOI、URL 等属于外部标识，只用于查找和重复检测，不能替代内部身份。

### 6.2 来源记录职责

来源记录保存：

- 标题、作者、来源类型和语言；
- 版次、出版社、发布日期；
- ISBN、DOI、URL 等外部标识；
- 版权、许可和允许的使用方式；
- 获取时间、文件位置和校验值；
- 可追溯性评分及理由；
- 严谨度评分及理由；
- 可用、不可访问、已撤回或已被替代等状态。

可追溯性和严谨度分别使用 1–5 分，并记录评分人和评分时间。AI 可以建议评分，但评分只有经过人工确认后生效。

### 6.3 来源笔记

值得长期保留的人工整理笔记或 AI 辅助笔记提交到 Git，并记录来源版本、创建者、创建时间、生成工具或模型和人工复核状态。临时提取结果留在 `inbox/extracted/`，不提交 Git。

来源笔记不是正式知识。它只能转化为条目草稿，再经过正常审核流程。

### 6.4 引用

关键事实或段落使用结构化引用：

```md
女娲补天的叙事在后世文献中经历了多次重构。[@01K..., 卷三]
```

每次引用记录来源 ULID、定位信息、证据角色和证据强度。构建工具将其渲染为脚注和参考文献；Obsidian 中可以额外使用 Wiki Link 导航到对应来源记录，但导航链接不替代结构化引用。

不同来源发生冲突时，条目保留并分别引用不同观点。若采用某一结论，需要说明判断依据和不确定性。

## 7. 检索设计

### 7.1 Meta 优先

检索分为两阶段：

1. 扫描条目元数据，筛选和排序候选条目；
2. 读取候选条目的正文分块和引用，形成有证据的结果。

默认权重顺序为：

1. 标题、别名；
2. 摘要、条目类型、标签、知识关系；
3. 检索扩展词；
4. 正文分块。

具体数值位于 `config/retrieval.yaml`，不写入内容文件。

### 7.2 两种检索模式

- **正式知识检索**：只索引 `published` 条目，回答必须回到正文和正式引用。
- **研究检索**：可以使用来源记录和来源笔记，输出必须提示内容尚未成为正式知识。

两个模式使用不同索引和输出标识，不能静默混合。

## 8. 构建和图谱

构建流程负责：

- 校验 Front Matter、Schema 和受控注册表；
- 校验 ULID 唯一性；
- 校验知识关系和引用目标存在；
- 校验已发布条目的摘要、来源和审核信息完整；
- 生成 Meta 索引、正文索引、RAG 分块和参考文献；
- 将类型化关系导出为节点与边；
- 分别生成正式知识和研究材料的检索产物。

目录层级仍是对象唯一归属的事实源。只有在实际出现复杂多跳查询或规模瓶颈后，才评估将导出的图数据加载到图数据库。

## 9. 校验和错误处理

- 已发布内容出现 Schema、引用、身份或关系错误时，构建失败；
- 草稿和待审条目的内容完整性问题可以警告，但结构错误仍失败；
- 缺失或重复 ULID 始终失败；
- 已被引用的来源记录不能硬删除，只能改变来源状态；
- 受限来源缺少权利信息时，禁止发布依赖其全文的内容；
- 外部导入先进入 `inbox/`，不得直接成为已发布条目。

## 10. Git 管理

Git 保存：

- Markdown 内容和长期来源笔记；
- Schema、注册表、模板、配置和工具；
- 来源位置、权利信息和校验值；
- 上下文地图、设计文档、政策和 ADR。

Git 默认不保存：

- `.generated/` 下的所有构建产物；
- 临时 AI/OCR 提取结果；
- 大型 PDF、扫描件、音视频；
- Obsidian 个人工作区、缓存和设备状态。

## 11. 第一阶段验收标准

第一阶段完成时应满足：

- 项目目录、Schema、注册表和模板可用；
- CLI 能创建对象、提交审核、发布、归档和校验全库；
- 文学知识域下存在一个完整的中国神话知识库示例；
- 示例覆盖人物、事件、作品、来源版本、引用、关系和媒体；
- Obsidian 能编辑和链接所有领域对象；
- 正式知识检索只使用已发布条目；
- 研究检索能够使用来源笔记并明确标识信任边界；
- 所有生成物都可由仓库内容重建。

中国神话示例的具体条目和 Schema 扩展，以后续提供的神话知识库需求文档为准。

## 12. 已接受的架构决策

- [ADR-0001：以目录管理唯一归属并渐进构建知识图谱](../adr/0001-directory-owned-knowledge-with-derived-graph.md)
- [ADR-0002：将来源库设为独立上下文和信任边界](../adr/0002-separate-source-context-and-trust-boundary.md)
- [ADR-0003：以仓库根目录作为 Obsidian Vault](../adr/0003-repository-root-as-obsidian-vault.md)
