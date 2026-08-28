# 藏经阁项目结构设计

- 状态：已确认
- 日期：2026-08-23
- 修订日期：2026-08-27
- 范围：当前项目布局、内容契约、Obsidian 内容 Vault 和校验 CLI

## 1. 目标与边界

当前项目为人工维护与 AI 协作提供可安装、可校验的结构化知识库基础：Markdown 内容保留人工可读性，JSON Schema 和受控注册表定义机器契约，GitHub Actions 在 push 与 pull request 后调用公开 CLI 自动校验。

项目采用两个领域上下文：

- **知识上下文**：管理知识域、知识库、知识条目和类型化知识关系；
- **来源上下文**：管理来源族、来源记录、来源笔记及其权利、质量和可用状态。

本设计只描述当前已接线的目录、契约和校验行为。对象状态是内容数据；当前 CLI 不提供创建、审核、发布或归档命令，CI 只校验提交中的状态与契约。

神话研究领域基础已实现（相关执行计划已执行完毕并移除）：Attestation 证据链（ADR-0004）、来源权利契约、神话域分层契约与语义校验、正式/研究检索及 push / pull request CI 均已接线；中国神话首期真实内容已入库并发布。

## 2. 目录结构

项目根目录承载工程文件和机器契约，内容 Vault 固定为项目内 `sutra-pavilion/`（ADR-0003）：

```text
sutra-pavilion/
├── .github/workflows/ci.yml
├── .gitignore
├── AGENTS.md
├── README.md
├── pyproject.toml
├── contracts/
│   ├── knowledge/
│   │   ├── registry/
│   │   │   ├── entry-types.yaml
│   │   │   ├── relation-types.yaml
│   │   │   ├── claim-predicates.yaml
│   │   │   ├── domain-contracts.yaml
│   │   │   └── tags/                    # 按需创建标签注册表
│   │   └── schemas/
│   │       ├── domain.schema.json
│   │       ├── library.schema.json
│   │       ├── entry.schema.json
│   │       └── domains/<domain>/         # 域叠加契约，按需创建
│   │           ├── common.schema.json
│   │           └── entry-types/<type>.schema.json
│   └── sources/
│       ├── registry/source-types.yaml
│       └── schemas/
│           ├── source-family.schema.json
│           ├── source-record.schema.json
│           ├── source-note.schema.json
│           └── attestation.schema.json
├── docs/
│   ├── adr/
│   ├── agents/
│   └── design/project-structure.md
├── specs/
│   └── plans/README.md
├── src/sutra_pavilion/
│   ├── __init__.py
│   ├── cli.py
│   ├── repository.py                    # 仓库快照：扫描、解析、契约加载
│   ├── search.py                        # 正式/研究检索
│   └── validation.py                    # 契约规则
├── sutra-pavilion/                      # Obsidian 打开此目录
│   ├── .obsidian/app.json
│   ├── CONTEXT-MAP.md
│   ├── knowledge/
│   │   ├── CONTEXT.md
│   │   └── domains/<domain>/
│   │       ├── _domain.md
│   │       └── libraries/<library>/
│   │           ├── _library.md
│   │           └── entries/<slug>.md
│   ├── sources/
│   │   ├── CONTEXT.md
│   │   ├── catalog/families/<ULID>.md
│   │   ├── catalog/records/<ULID>.md
│   │   ├── attestations/<ULID>.md       # 文件名必须等于 ULID
│   │   └── notes/<来源记录 ULID>/<笔记 ULID>.md
│   ├── inbox/imports/README.md
│   └── templates/                       # 七类对象模板
└── tests/                               # 公开 CLI 行为测试
```

`knowledge/domains/`、`sources/catalog/` 和 `sources/notes/` 在出现第一个正式对象时按需创建；空内容项目仍会校验现有 Schema 与注册表。

## 3. Obsidian 约定

### 3.1 Vault 范围

Obsidian 只打开项目内 `sutra-pavilion/`。工程文件、机器契约、设计、规格和测试位于外层项目根目录，不进入 Obsidian 文件树。

内容 Vault 只提交共享核心设置 `sutra-pavilion/.obsidian/app.json`。个人工作区状态、缓存和设备相关文件不提交。项目根目录的 `.obsidian/` 只可能是本地编辑器状态，也不提交。

### 3.2 Markdown 与 Properties

知识域、知识库、知识条目、来源族、来源记录和来源笔记都使用 Markdown；其结构化字段位于顶层 YAML Front Matter。Schema 与注册表使用 JSON 或 YAML，并由校验器从 `contracts/` 加载。

### 3.3 链接与身份

Wiki Link 用于人工导航，不承担永久身份。七类对象使用 ULID；类型化关系通过 ULID 连接知识对象，结构化引用通过 ULID 连接来源记录。文件改名或移动不改变对象身份。

## 4. 权威目录与扫描边界

校验器只扫描以下路径：

| 对象 | 权威路径 |
|---|---|
| 知识域 | `sutra-pavilion/knowledge/domains/*/_domain.md` |
| 知识库 | `sutra-pavilion/knowledge/domains/*/libraries/*/_library.md` |
| 知识条目 | `sutra-pavilion/knowledge/domains/*/libraries/*/entries/*.md` |
| 来源族 | `sutra-pavilion/sources/catalog/families/*.md` |
| 来源记录 | `sutra-pavilion/sources/catalog/records/*.md` |
| 来源笔记 | `sutra-pavilion/sources/notes/*/*.md` |
| 具体见证（Attestation） | `sutra-pavilion/sources/attestations/*.md` |

上下文说明、模板、收件箱和其他路径不作为正式对象扫描。直接把内容 Vault 传给 CLI 会返回 `PATH_IS_CONTENT_VAULT`，避免空扫描被误报为通过。

## 5. 知识对象格式

### 5.1 公共约束

知识域、知识库和知识条目分别由 `domain.schema.json`、`library.schema.json` 和 `entry.schema.json` 校验。所有对象包含 `schema_version`、ULID、标题和语言；知识条目另外包含 slug、登记过的 `entry_type` 和状态。

知识条目可选字段包括摘要、别名、标签、检索词、类型属性、知识关系，以及名称形式（`name_forms`）、核验阶段（`verification_stage`）、争议状态（`controversy_status`）、发布许可（`publish_license`）和外部标识的形状声明。

存在 `contracts/knowledge/schemas/domains/<domain>/` 目录的域使用叠加契约：`common.schema.json` 只叠加必填、收紧与固定值约束（字段形状的真源在公共 `entry.schema.json`，不重复声明），`entry-types/<type>.schema.json` 约束该类型的顶层字段与 `attributes`（`attributes` 关闭自由字段）。当前 `myth-research` 域已落地五类类型契约（figure、tradition、episode、motif、claim）；没有叠加 Schema 的域保持公共契约行为。域 Schema 由条目所在的域目录 slug 选择，无需在条目中声明归属；启用分层契约的域登记于 `contracts/knowledge/registry/domain-contracts.yaml`（含其专属条目类型清单）：登记域的公共 Schema、登记类型的 Schema 文件缺失时按 `SCHEMA_FILE_MISSING` 失败（删除整个域 Schema 目录同样失败，因为注册表独立存在）；未登记的类型（work、place、concept 等）继续复用公共条目契约。

### 5.2 条目目录

知识条目平铺在所属知识库的 `entries/` 下。目录决定知识域和知识库归属；slug 与文件名可以变化，ULID 保持稳定。

### 5.3 状态字段

`status` 允许 `draft`、`review`、`published` 和 `archived`。校验器检查枚举值和神话域状态不变量，但不执行状态转换或平台身份判断；发布不绑定 CODEOWNER、指定审核者或人工平台批准。

神话域另有语义不变量：`status: published` 必须同时为 `verification_stage: verified`（`KNOWLEDGE_STATE_INVALID`）；已发布条目至少引用一个 Attestation，episode 与 claim 无论状态都至少引用一个；`name_forms` 是名称真源，`title` 与 `aliases` 必须是其确定性投影；`search_terms` 非空；episode 必须与 Tradition（`within_tradition`）、人物（`features`）和 Motif（`instantiates_motif`）各有至少一个结构关系；tradition、motif、claim 有正文章节最低要求；Claim 主客体必须是现有、不同且非 Claim 的知识条目，谓词须登记于 `claim-predicates.yaml`；神话域不得用通用 `influenced` 关系表达解释性结论。

### 5.4 关系

知识域、知识库和知识条目可以声明 `relations`。关系类型必须登记于 `contracts/knowledge/registry/relation-types.yaml`；目标必须是现有知识对象，且声明对象类型和目标对象类型必须符合注册表定义。

## 6. 来源对象格式

### 6.1 来源族

来源族用于归组同一作品或出版物的多个具体版本。它是可选对象，使用独立 ULID，但不能作为结构化引用目标。

### 6.2 来源记录

来源记录代表可准确引用的具体版次、版本或网页快照。必填字段由 `source-record.schema.json` 定义：来源类型（`source_type`，须登记）、来源角色（`source_role`：raw-material / critical-edition / scholarship / institutional-overview / discovery-clue）、访问方式（`access_method`）和统一权利结构 `rights`（`rights_statement`、`reuse_scope`、`access_status`；`restricted-cultural` 时必须补 `community_protocol` 与 `consent_note`；`link-quote` 时必须补 `permission_basis` 短引权利依据与 `excerpt_max_chars` 短引上限，Attestation 短引长度不得超过该上限）。`reuse_scope` 取六种受控值，不含 `unknown`。`source_type: book` 还必须具有 `edition`、`publisher`、`external_ids.url` 和 `acquisition.acquired_date`。可选字段包括作者、出版日期、来源族、获取信息、可追溯性和严谨度评分。

来源记录的 `family_id` 存在时必须指向现有来源族。

### 6.2a 具体见证（Attestation）

Attestation 是来源上下文的一等对象，也是知识条目结构化引用的唯一目标。它保存精确定位（`locator`）、证据层级、文本说明、能支持与不能支持的结论；可选短引（`excerpt`）受所属来源记录 `rights.reuse_scope` 限制——`metadata-only`、`permission-required`、`restricted-cultural` 下不得保存。Attestation 不复制来源记录的权利与书目事实。

### 6.3 来源笔记

来源笔记记录来源版本、创建者、创建时间和复核状态。每条笔记的 `source_id` 必须指向现有来源记录；来源笔记不是结构化引用的目标。

### 6.4 引用

知识条目正文只能引用 Attestation（ADR-0004），使用以下结构化引用：

```md
具体陈述。[@01K00000000000000000000000; role=support; strength=5]
```

引用目标必须是现有 Attestation 的 ULID；`role` 取 `support` / `context` / `counterevidence`，`strength` 为 1–5 的整数。定位只保存在 Attestation 的 `locator` 中。校验器拒绝格式错误、参数非法、目标缺失、目标不是 Attestation 以及旧的「来源记录 ULID + 定位」语法；只检查知识条目正文中的结构化引用。

## 7. 校验与检索 CLI

公开入口有两个，参数均为项目根目录（省略时使用当前目录），共享同一次仓库快照解释：

- `sutra validate [PATH]`：聚合全部错误，输出项目相对路径、稳定规则标识、原因、对象数量和错误总数；
- `sutra search <QUERY> [PATH] [--mode formal|research]`：大小写不敏感字面检索。默认 `formal` 只返回 `published ∧ verified` 的知识条目；`research` 返回全部条目、来源记录、Attestation 与来源笔记并标记 `research-only` 状态。仓库存在校验错误时返回 `1` 且不输出结果行；无匹配返回 `0` 和 `结果：0`。

当前校验包括：

- 路径存在性、目录类型和内容 Vault 误传；
- Front Matter 存在性、YAML 解析与顶层映射；
- Schema 文件解析、自检及对象 Schema；
- 注册表结构与受控值；
- 全仓 ULID 唯一性；
- 知识关系目标、类型和适用范围；
- 来源笔记到来源记录、来源记录到来源族、Attestation 到唯一来源记录的引用；
- Attestation 文件名一致性与短引权利边界；
- 知识条目正文到 Attestation 的结构化引用（旧「来源记录 + 定位」语法直接失败）；
- 神话域名称投影、发布状态、正文章节、关系条目类型适用范围和 Claim 语义。

退出码为：`0` 校验通过，`1` 发现内容或仓库契约错误，`2` 命令用法错误。GitHub Actions 运行 Ruff、pytest 和 `sutra validate .`。

## 8. Git 边界

Git 保存 Markdown 内容、长期来源笔记、Schema、注册表、模板、工具、设计和 ADR。Obsidian 个人状态、收件箱临时材料、Python 构建产物、缓存、本地环境和大型本地媒体由 `.gitignore` 排除。

## 9. 当前验收标准

- push 与 pull request 自动触发 GitHub Actions，依次运行 Ruff、全部行为测试和 `sutra validate .`；
- CI 中的 `sutra validate .` 实际解析现有 Schema 与注册表，非法 Front Matter、ULID、关系和引用使检查失败；
- 行为测试证明七类模板、稳定错误、内容 Vault 误传和正式/研究检索边界；
- Obsidian 打开 `sutra-pavilion/` 后只显示内容文件，Properties、链接和个人状态可用。

## 10. 已接受的架构决策

- [ADR-0001：以目录管理唯一归属与类型化关系](../adr/0001-directory-owned-knowledge.md)
- [ADR-0002：将来源库设为独立上下文和信任边界（已由 ADR-0004 取代）](../adr/0002-separate-source-context-and-trust-boundary.md)
- [ADR-0003：内容 Vault 命名为项目名称](../adr/0003-content-vault-named-after-project.md)
- [ADR-0004：以 Attestation 作为唯一证据原子](../adr/0004-attestation-as-single-evidence-atom.md)
