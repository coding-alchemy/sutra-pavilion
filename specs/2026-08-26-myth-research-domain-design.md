# 神话研究领域设计

- 文档版本：0.2
- 文档状态：已批准
- 创建日期：2026-08-26
- 修订日期：2026-08-27
- 适用范围：神话研究知识域的 Attestation 证据链、知识条目契约、来源权利、检索接口、校验模块与迁移边界
- 上游需求：[神话研究领域规范](./2026-08-24-myth-research-domain-requirements.md)、[中国神话首期建设规格](./2026-08-24-chinese-mythology-first-phase-requirements.md)
- 架构基线：[项目结构设计](../docs/design/project-structure.md)、[ADR-0001](../docs/adr/0001-directory-owned-knowledge.md)、[ADR-0002](../docs/adr/0002-separate-source-context-and-trust-boundary.md)、[ADR-0003](../docs/adr/0003-content-vault-named-after-project.md)
- 关联决策：[ADR-0004：以 Attestation 作为唯一证据原子](../docs/adr/0004-attestation-as-single-evidence-atom.md)

---

## 1. 目标与核心结果

本设计把已批准的神话研究需求接入现有藏经阁，而不另建一套神话专用系统。完成后，用户可以观察到三个核心结果：

1. 任一正式知识陈述都沿“知识条目 → Attestation → 来源记录”回溯，条目不再直接引用来源记录；
2. `sutra search` 默认只返回 `status: published ∧ verification_stage: verified` 的条目，研究内容必须显式选择研究模式；
3. `sutra validate` 能拒绝证据链、名称投影、Claim 端点、权利范围和神话类型契约中的实质错误。

本设计继续使用一个项目根、一个 `sutra-pavilion/` 内容 Vault、知识与来源两个上下文、Markdown 主数据、JSON Schema、受控注册表和同一个 CLI。中国神话首期只提供首批内容与验收样本，不形成第二套技术架构，因此不另建首期设计文档。

## 2. 权威基线与影响映射

| 已有接口、行为或限制 | 当前基线 | 本设计中的变化 |
|---|---|---|
| 内容归属 | 只有知识条目由所在 `entries/` 目录确定归属库 | 保持不变；不增加 `home_library_id` |
| 来源边界 | 来源族、来源记录、来源笔记属于独立来源上下文 | 保持不变；Attestation 加入来源上下文 |
| 正文引用 | `[@<来源记录 ULID>, <定位>]` | 一次性替换为 Attestation 引用；定位只存 Attestation |
| 对象扫描 | `validation.py` 固定扫描六类对象 | 增加 `sources/attestations/*.md`，成为第七类对象 |
| 知识契约 | 一个公共 `entry.schema.json`；`attributes` 未按类型校验 | 保留公共 Schema，叠加神话域公共 Schema 和按条目类型 Schema |
| 条目名称 | `title` 与 `aliases` 可独立编辑 | `name_forms` 为真源，`title` 与 `aliases` 为确定性投影 |
| 内容状态 | 只有 `status` | 增加核验与争议维度；状态与证据链由 CI 自动校验，不绑定平台审核身份 |
| 来源权利 | `rights` 字段可选，字段名与新需求不一致 | 来源记录必填来源角色、访问方式与统一权利结构 |
| CLI | 只有 `sutra validate [PATH]` | 保留该接口，新增无索引的 `sutra search`；不新增第二套命令框架 |
| 测试接缝 | 行为测试通过已安装的 `sutra` 子进程验证 | 继续以公开 CLI 为主要测试接缝 |

约束如下：

- 当前内容目录尚无正式知识对象，迁移对象主要是 Schema、模板、测试 fixture 和设计示例；
- [项目结构设计](../docs/design/project-structure.md)描述当前已接线行为，在本设计实现完成前不得提前写成“已支持”；
- GitHub Actions 在 push 与 pull request 后调用公开 CLI；AI Agent 无需 GitHub 审核者、CODEOWNER 或仓库规则权限；
- 大型原始材料位置与未来是否公开仍是上游需求的开放决定，不阻塞女娲试点；公开决定前，条目发布许可固定为私人使用。

需求到设计与直接验证的映射：

| 已批准要求 | 设计落位 | 直接验证 |
|---|---|---|
| Attestation 唯一证据链 | 6.1、6.3、9 | 10.1 |
| 神话条目类型、名称与 Claim | 6.4–6.6 | 10.3、10.5、10.6 |
| `published ∧ verified` 正式检索 | 4.3、6.4 | 10.2 |
| 来源角色与权利默认值 | 6.1、6.2 | 10.4 |
| 当前内容版本的 CI 自动校验 | 8 | 10.7 |
| 旧直引一次性迁移 | 9 | 10.1 |
| 中国神话女娲试点 | 6.5、10 | 10.6、10.8 |

## 3. 最小方案与取舍

### 3.1 采用方案

在现有校验深层模块中增加一个内部“仓库快照”接缝，让校验和检索共享同一次目录扫描、Front Matter 解析和身份索引。公共 CLI 只有两个用户接口：

```text
sutra validate [PATH]
sutra search <QUERY> [PATH] [--mode formal|research]
```

`validate` 继续聚合全部错误；`search` 默认使用 `formal`，直接扫描 Markdown，不预建 JSONL、SQLite、向量库或图数据库。

### 3.2 更简单但不满足目标的方案

更简单的方案是把 Attestation 写成来源笔记，并继续让条目直接引用来源记录。它少一个对象类型和 Schema，但无法保证定位、可支持范围及原文/译文分层属于同一证据原子，也无法阻止不同陈述共享一个模糊来源定位，因此不能证明核心证据链。

另一个表面更简单的方案是删除 `aliases`，只保留 `name_forms`。现有公共条目契约、Obsidian 导航和 Meta 优先检索已经消费 `aliases`；删除它会扩大兼容性改动。故保留 `title`、`aliases` 作为机器生成或校验的投影，不让作者维护第二份名称事实。

### 3.3 拒绝的扩展

- 不建立第三个“神话上下文”；神话对象仍分别归入知识和来源上下文；
- 不引入通用工作流引擎、维护者数据库或内容内 `status_history`；
- 不为只有一种实现的本地文件扫描增加 Adapter；
- 不在首期实现派生索引、语义检索、自动回答生成或批量采集；
- 不允许旧来源记录引用与新 Attestation 引用长期并存。

## 4. 模块、接口与接缝

```text
CLI Adapter
  ├─ sutra validate ─┐
  └─ sutra search ───┼─> 仓库检查模块 ─> 仓库快照
                     │                    ├─> 校验模块 ─> ValidationReport
                     │                    └─> 检索模块 ─> SearchResult
                     └─> 输出与退出码

GitHub push / pull request ─> Actions CI ─> Ruff + pytest + sutra validate
```

### 4.1 仓库检查模块

这是进程内深层模块，封装目录扫描、Front Matter 解析、Schema/注册表加载和 ULID 索引。它的内部接口返回一次不可变仓库快照；校验与检索只能消费该快照，不得各自重新解释目录或对象身份。

该接缝有两个真实消费者：校验和检索。测试仍穿过 `sutra validate` 与 `sutra search`，不直接断言快照内部结构。

### 4.2 校验模块

校验模块继续返回聚合后的 `ValidationReport`，保持现有错误格式、退出码和“尽可能一次列出全部问题”的行为。新增检查仍按“Schema 结构 → 注册表 → 跨对象语义”顺序执行，避免同一根因产生误导性级联错误。

### 4.3 检索模块

`sutra search` 的接口规则：

- `QUERY` 为必填的大小写不敏感字面查询；首期不解释正则或查询语言；
- `PATH` 与 `validate` 一样必须是项目根，省略时使用当前目录；
- `--mode formal` 为默认值，只搜索同时满足 `published` 与 `verified` 的知识条目；
- `--mode research` 显式搜索全部可解析知识条目、来源记录、Attestation 和来源笔记，并在每项结果上输出对象类型及未发布/未核验标记；
- 匹配顺序为标题/别名 → 摘要/类型/标签/关系 → 检索词 → 正文，同一层按项目相对路径稳定排序；
- `controversy_status: disputed` 的结果必须带争议标记；CLI 只返回材料，不生成研究结论；
- 仓库存在校验错误时返回退出码 `1`，不输出可能绕过契约的正式检索结果；命令用法错误仍返回 `2`。

每条结果的稳定输出为“项目相对路径、对象类型、状态标记、标题”四列；匹配层级只决定排序，不成为持久字段。无匹配返回退出码 `0` 和结果数 `0`。

首期直接使用 `rg` 仍可用于人工研究和诊断，但不得把未经状态过滤的 `rg` 结果当作正式知识回答。

## 5. 目录与契约文件

目标增量如下；未列出的现有目录保持不变：

```text
contracts/
├── knowledge/
│   ├── registry/
│   │   ├── entry-types.yaml
│   │   ├── relation-types.yaml
│   │   └── claim-predicates.yaml
│   └── schemas/
│       ├── entry.schema.json
│       └── domains/myth-research/
│           ├── common.schema.json
│           └── entry-types/
│               ├── figure.schema.json
│               ├── tradition.schema.json
│               ├── episode.schema.json
│               ├── motif.schema.json
│               └── claim.schema.json
└── sources/schemas/
    ├── source-record.schema.json
    └── attestation.schema.json

sutra-pavilion/
├── knowledge/domains/myth-research/
│   ├── _domain.md
│   └── libraries/chinese-mythology/
│       ├── _library.md
│       └── entries/*.md
├── sources/
│   ├── catalog/records/*.md
│   └── attestations/<ULID>.md
└── templates/
    ├── knowledge-entry.md
    └── attestation.md
```

神话域 Schema 由目录中的域 slug `myth-research` 选择，不在条目中增加重复的 profile 或归属字段。公共 `entry.schema.json` 只声明跨域可识别的字段形状；`domains/myth-research/common.schema.json` 要求神话域公共字段；`entry-types/*.schema.json` 校验相应条目类型的顶层必需字段、`attributes` 和结构关系。没有神话域叠加 Schema 的其他知识域保持当前行为。

所有存在的 Schema 即使没有内容对象也必须被解析和自检，保持空内容仓库的 CI 不是空操作。

## 6. 数据设计

### 6.1 Attestation

Attestation 是来源上下文中的一等对象，权威路径为 `sutra-pavilion/sources/attestations/<ULID>.md`。最小 Front Matter：

| 字段 | 约束 |
|---|---|
| `schema_version` | 首版为 `1` |
| `id` | 全仓唯一 ULID；文件名必须等于该 ULID |
| `title` | 人工可读的短标题 |
| `source_record_id` | 必填且只允许指向一个现有来源记录 |
| `language` | BCP 47 语言标签 |
| `locator` | 非空精确定位；篇卷、页行、诗节、对象号或稳定网页锚点 |
| `evidence_level` | `direct` / `indirect` / `contextual` |
| `excerpt` | 可选的必要短引；受所属来源记录的 `reuse_scope` 限制 |
| `working_translation` | 可选对象；同时存在 `text` 与 `responsible_by` |
| `text_note` | 异文、断句、难词或图像说明；必填 |
| `supports` | 非空字符串列表，限定该见证能够支持的结论 |
| `does_not_support` | 非空字符串列表，明确证据边界 |

Attestation 不复制来源记录的书目、评分或权利字段。它通过 `source_record_id` 取得有效权利边界；如果某段内容具有不同权利主体或许可，应建立独立来源记录，而不是在 Attestation 上维护第二份权利事实。

当来源记录的 `reuse_scope` 为 `metadata-only`、`permission-required` 或 `restricted-cultural` 时，Attestation 不得包含 `excerpt`；`link-quote`、`redistributable` 或 `noncommercial` 才允许保存与范围相符的短引。CLI 不自动判断合理使用，只验证已登记范围与实际保存字段不冲突。

### 6.2 来源记录与权利

保留现有 `source_type` 表示载体类型，新增 `source_role` 表示研究用途，两者不得混用。来源记录新增必填字段：

```yaml
source_role: critical-edition
access_method: manual
rights:
  rights_statement: "现代校勘、标点与排版受版权保护；当前仅登记元数据"
  license_spdx: ""
  reuse_scope: metadata-only
  access_status: restricted
```

`source_role` 取已批准需求中的五个值：`raw-material`、`critical-edition`、`scholarship`、`institutional-overview`、`discovery-clue`。不增加空泛的“其他”类别；新角色必须修订需求或设计后再加入。

`reuse_scope` 只能是 `redistributable`、`noncommercial`、`link-quote`、`metadata-only`、`permission-required`、`restricted-cultural`。不提供 `unknown`；权利尚未确认时使用 `metadata-only`，并在 `rights_statement` 明确写出待核验状态。`license_spdx` 允许空字符串，因为并非所有使用依据都有 SPDX 标识。

`rights.access_status` 取 `public`、`restricted`、`closed`。当 `reuse_scope: restricted-cultural` 时，`rights.community_protocol` 与 `rights.consent_note` 同时必填。首期使用的 `book` 来源记录还必须具有 `edition`、`publisher`、`external_ids.url` 和 `acquisition.acquired_date`；其他来源类型只在出现真实样本后增加相应条件，不预建空泛字段集合。

现有 `traceability` 与 `rigor` 评分结构保持不变。它们在来源登记阶段可以缺省，但被首期正式条目引用的来源必须在内容验收中同时具备两项人工确认评分。

### 6.3 结构化引用

知识条目正文继续使用紧凑的内联引用，但新语法不再携带定位：

```md
女娲炼五色石以补苍天。[@01K00000000000000000000000; role=support; strength=5]
```

规则如下：

- 第一个值必须是 Attestation ULID；
- `role` 取 `support`、`context`、`counterevidence`；
- `strength` 为 1–5 的整数，评价该见证按所声明 `role` 支持、补充或反驳当前陈述的程度；
- 定位只从 Attestation 的 `locator` 获取，引用中不得重复；
- 旧 `[@<来源记录 ULID>, <定位>]` 语法直接失败，不保留兼容分支；
- `published` 的神话条目至少有一个合法 Attestation 引用；首期 Claim 至少有两个，作为首期内容验收而非所有 Claim 的全局数量规则。

### 6.4 神话域公共条目字段

公共 `entry.schema.json` 增加但不在其他域强制要求以下字段；神话域公共 Schema 将其设为必填：

| 字段 | 设计 |
|---|---|
| `summary` | 非空，供 Meta 优先检索 |
| `aliases` | 可为空；必须等于非展示名称形式的有序去重投影 |
| `search_terms` | 非空字符串列表 |
| `verification_stage` | `lead` / `checked` / `verified` |
| `controversy_status` | `none` / `disputed` |
| `publish_license` | 当前固定为 `private-use-only`；公开决定后通过设计修订扩展 |
| `external_ids` | 可选键值映射，只用于查找与消歧 |
| `name_forms` | 非空名称形式列表，是结构化名称真源 |

每个 `name_forms` 元素为：

```yaml
- id: nuwa-zh-hans
  text: 女娲
  language: zh-CN
  script: Hans
  display: true
  usage: 现代规范展示名
  translated_as: []
```

`id` 是条目内唯一、稳定的 ASCII 小写标识，不是全仓对象 ULID。每个条目必须恰有一个 `display: true`；它的 `text` 等于 `title`。`aliases` 按 `name_forms` 顺序收集其余 `text`，以第一次出现为准去重。`translated_as` 只允许指向同一条目内另一名称形式 ID，不能指向知识对象 ULID，也不进入 Claim 谓词注册表。

任何 `status: published` 条目都必须同时为 `verification_stage: verified`；正式检索仍保留双条件过滤，防止错误内容绕过状态契约。`checked` 只用于尚未发布的 `draft` / `review` 内容。新模板默认使用 `status: draft`、`verification_stage: lead`、`controversy_status: none` 和 `publish_license: private-use-only`。

### 6.5 神话条目类型

| `entry_type` | 类型 Schema 的最小约束 |
|---|---|
| `figure` | 顶层 `external_ids`，以及 `attributes.entity_kind`、`attributes.date_label`、`attributes.date_certainty`；`attributes.date_start` 与 `attributes.date_end` 同时出现或同时缺省 |
| `tradition` | `attributes.scope` 包含时间表述、地域、语言、宗教语境和文类；正文含内部分期与争议 |
| `episode` | `attributes.version_note`；至少一个 Tradition、人物和 Motif 的结构关系；至少一个 Attestation 引用 |
| `motif` | `attributes.subtypes` 与 `attributes.catalog_alignments`；正文含操作性定义及排除标准 |
| `claim` | 可检验陈述、主体、谓词、客体、置信度与理由、适用范围、归属说明；正文含“反证”和“其他解释”章节 |

当前注册表新增 `tradition`、`episode`、`motif`、`claim`；女娲继续使用已有 `figure`，不新增同义的 `deity` 条目类型。其他实体继续优先复用 `place`、`work`、`concept` 等已有类型，只有出现当前类型无法表达的真实对象时才新增类型 Schema。

每个 `catalog_alignments` 元素包含 `index_name`、`version` 与 `identifier`，不得只写一个脱离版本的编号。`tradition.scope` 和 Claim 的适用范围都保留人工可读表述；只有日期排序字段需要机器可比较，不为地域、宗教或文类预建尚无消费者的全局本体。

JSON Schema 校验 Front Matter 字段和关系形状；校验模块另外检查正文必需章节、引用数量及关系目标。正文章节缺失不能因为 Front Matter 合法而被忽略。

### 6.6 结构关系与 Claim

`relation-types.yaml` 的现有 `source_kinds` / `target_kinds` 保留，并增加可选的 `source_entry_types` / `target_entry_types`，用于在对象种类都是 `entry` 时继续约束条目类型。神话域首批结构关系：

| 关系 | 来源范围 | 目标范围 |
|---|---|---|
| `within_tradition` | `figure` / `episode` / `motif` / `claim` | `tradition` |
| `features` | `episode` | `figure` |
| `instantiates_motif` | `episode` | `motif` |
| `part_of` | 任意知识条目 | 任意知识条目 |

神话域不允许使用现有通用 `influenced` 关系表达解释性结论；影响、身份、演变、融合、改写和对应全部进入 Claim。

Claim 的 `attributes` 至少包含：

```yaml
statement: <可检验陈述>
subject_id: <知识条目 ULID>
predicate: developed_from
object_id: <知识条目 ULID>
confidence:
  score: 3
  reason: <理由>
scope: <时间、地域或材料范围>
attribution: <提出者或解释来源>
```

`subject_id` 与 `object_id` 必须指向两个现有的非 Claim 知识条目，不能指向名称形式、来源对象或任何 Claim。`predicate` 从 `claim-predicates.yaml` 读取，首批只登记 `identified_with`、`syncretized_with`、`developed_from`、`influenced_by`、`literary_adaptation_of`、`counterpart_of`、`possibly_related_to`；`translated_as` 不在其中。

## 7. 校验行为与稳定错误

除 JSON Schema 产生的 `SCHEMA_INVALID` 外，新增跨对象规则至少使用以下稳定错误标识：

| 错误标识 | 触发条件 |
|---|---|
| `ATTESTATION_SOURCE_MISSING` | `source_record_id` 不指向现有来源记录 |
| `ATTESTATION_FILENAME_MISMATCH` | Attestation 文件名与自身 ULID 不一致 |
| `ATTESTATION_EXCERPT_NOT_ALLOWED` | 权利范围不允许却保存 `excerpt` |
| `CITATION_TARGET_NOT_ATTESTATION` | 神话条目引用的目标不是 Attestation |
| `CITATION_LEGACY_FORMAT` | 仍使用来源记录 ULID + 定位旧语法 |
| `NAME_DISPLAY_INVALID` | 展示名称缺失、重复或与 `title` 不同 |
| `ALIASES_PROJECTION_MISMATCH` | `aliases` 不是其余名称形式的确定性投影 |
| `NAME_TRANSLATION_TARGET_MISSING` | `translated_as` 目标不在同一条目的名称形式中 |
| `KNOWLEDGE_STATE_INVALID` | `status: published` 未同时满足 `verification_stage: verified` |
| `ENTRY_BODY_SECTION_MISSING` | 类型契约要求的正文章节缺失或为空 |
| `RELATION_TYPE_NOT_ALLOWED_IN_DOMAIN` | 神话域使用解释性通用关系代替 Claim |
| `RELATION_ENTRY_TYPE_NOT_APPLICABLE` | 结构关系的条目类型组合不合法 |
| `CLAIM_ENDPOINT_INVALID` | Claim 主客体缺失、类型错误或指向自身 |
| `CLAIM_PREDICATE_UNREGISTERED` | Claim 使用未登记谓词或 `translated_as` |

校验器只报告仓库契约和内容证据链错误，不检查 GitHub 身份或审批；CI 直接调用该校验器。

## 8. CI 自动校验

GitHub Actions 在每次 push 与 pull request 后自动执行：

- `ruff check src tests`；
- `python -m pytest`；
- `sutra validate .`。

CI 结果与具体提交关联；任何检查失败，该提交不满足发布条件。发布流程不要求 CODEOWNER、指定审核者、人工平台批准或受保护分支试验 PR，也不要求 AI Agent 获得 GitHub push、审核或仓库规则权限；由用户或既有非 AI 发布流程提交变更即可触发 CI。开发者可以为诊断自愿运行公开 CLI，但本地运行结果不是完成门禁或验收证据。

## 9. 一次性迁移顺序

实现必须在同一阶段完成以下切换，不设置双读兼容期：

1. 增加 Attestation Schema、扫描规则、模板和测试 fixture；
2. 按每个现有“来源记录 + 定位”组合创建 Attestation；当前仓库没有正式内容对象，预计只需迁移测试与示例；
3. 把知识正文引用改为 Attestation 新语法；
4. 将校验目标从来源记录切换为 Attestation，并删除旧格式通过测试；
5. 加入神话域公共及类型 Schema、名称投影、Claim、权利和检索行为；
6. 同步当前项目结构设计、README、模板、上下文地图和 ADR 导航，使“当前能力”只描述已落地行为。

任何一步完成后如果仍允许条目直引来源记录，迁移即未完成。

## 10. 直接验收

设计实现后必须通过公开接口证明：

1. 合法条目可以从正文引用回溯到 Attestation，再回溯到唯一来源记录；旧直引和悬空引用失败；
2. `sutra search 女娲 --mode formal` 只返回 `published ∧ verified`，相同查询在研究模式可返回并明确标记 `draft`、`review`、`lead`、`checked`；
3. 缺少展示名称、多个展示名称、`aliases` 投影不一致或跨条目 `translated_as` 均失败；
4. `reuse_scope: unknown` 失败，`metadata-only` 来源下保存短引失败；
5. Claim 使用 `translated_as`、悬空主客体或非法结构关系类型组合时失败；
6. 女娲试点的两个 Episode 保持独立，并分别引用对应 Attestation；Claim 至少引用两个 Attestation，争议检索结果带标记；
7. 包含当前内容的提交在 push 或 pull request 后触发 CI，Ruff、全部行为测试和 `sutra validate .` 均成功；
8. 禁用 Obsidian 社区插件后，条目、Attestation 和来源记录仍可完整阅读。

CI 成功是自动契约门禁，但不能替代证据回溯、版本分离、争议呈现和 Obsidian 阅读等核心行为验收；不要求执行者在本地重复运行 CI 命令。

## 11. 非目标与后续门禁

- 本设计不采集真实来源、不编写女娲正文、不生成执行计划、不修改实现代码；
- 本设计不决定大型原始材料最终位置，也不批准公开发布；首期继续使用小型材料和 `private-use-only`；
- 本设计批准后，先在 `specs/plans/myth-research-domain/` 编写领域基础执行计划并获用户批准；领域基础完成后，再为 `specs/plans/chinese-mythology-first-phase/` 编写首期内容计划（两项计划均已执行完毕，文件已于 2026-08-27 按用户指示移除）；
- 未获得本设计明确批准前，不得创建上述执行计划或修改实现代码。
