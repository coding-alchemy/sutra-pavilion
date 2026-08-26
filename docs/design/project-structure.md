# 藏经阁项目结构设计

- 状态：已确认
- 日期：2026-08-23
- 修订日期：2026-08-26
- 范围：当前项目布局、内容契约、Obsidian 内容 Vault 和校验 CLI

## 1. 目标与边界

当前项目为人工维护与 AI 协作提供可安装、可校验的结构化知识库基础：Markdown 内容保留人工可读性，JSON Schema 和受控注册表定义机器契约，公开 CLI 在本地与 CI 中执行相同行为。

项目采用两个领域上下文：

- **知识上下文**：管理知识域、知识库、知识条目和类型化知识关系；
- **来源上下文**：管理来源族、来源记录、来源笔记及其权利、质量和可用状态。

本设计只描述当前已接线的目录、契约和校验行为。对象状态是内容数据；状态转换由维护者编辑文件完成，当前 CLI 不提供创建、审核、发布或归档命令。

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
│   │   │   └── tags/                    # 按需创建标签注册表
│   │   └── schemas/
│   │       ├── domain.schema.json
│   │       ├── library.schema.json
│   │       └── entry.schema.json
│   └── sources/
│       ├── registry/source-types.yaml
│       └── schemas/
│           ├── source-family.schema.json
│           ├── source-record.schema.json
│           └── source-note.schema.json
├── docs/
│   ├── adr/
│   ├── agents/
│   └── design/project-structure.md
├── specs/
│   └── plans/README.md
├── src/sutra_pavilion/
│   ├── __init__.py
│   ├── cli.py
│   └── validation.py
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
│   │   └── notes/<来源记录 ULID>/<笔记 ULID>.md
│   ├── inbox/imports/README.md
│   └── templates/                       # 六类对象模板
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

Wiki Link 用于人工导航，不承担永久身份。六类对象使用 ULID；类型化关系通过 ULID 连接知识对象，结构化引用通过 ULID 连接来源记录。文件改名或移动不改变对象身份。

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

上下文说明、模板、收件箱和其他路径不作为正式对象扫描。直接把内容 Vault 传给 CLI 会返回 `PATH_IS_CONTENT_VAULT`，避免空扫描被误报为通过。

## 5. 知识对象格式

### 5.1 公共约束

知识域、知识库和知识条目分别由 `domain.schema.json`、`library.schema.json` 和 `entry.schema.json` 校验。所有对象包含 `schema_version`、ULID、标题和语言；知识条目另外包含 slug、登记过的 `entry_type` 和状态。

知识条目可选字段包括摘要、别名、标签、检索词、类型属性和知识关系。`attributes` 当前只要求为对象；没有类型专属 Schema。

### 5.2 条目目录

知识条目平铺在所属知识库的 `entries/` 下。目录决定知识域和知识库归属；slug 与文件名可以变化，ULID 保持稳定。

### 5.3 状态字段

`status` 允许 `draft`、`review`、`published` 和 `archived`。校验器检查枚举值，但不执行状态转换、权限或发布完整性规则。

### 5.4 关系

知识域、知识库和知识条目可以声明 `relations`。关系类型必须登记于 `contracts/knowledge/registry/relation-types.yaml`；目标必须是现有知识对象，且声明对象类型和目标对象类型必须符合注册表定义。

## 6. 来源对象格式

### 6.1 来源族

来源族用于归组同一作品或出版物的多个具体版本。它是可选对象，使用独立 ULID，但不能作为结构化引用目标。

### 6.2 来源记录

来源记录代表可准确引用的具体版次、版本或网页快照。必填字段由 `source-record.schema.json` 定义；来源类型必须登记。可选字段包括作者、出版信息、外部标识、来源族、权利、获取信息、可追溯性和严谨度。

来源记录的 `family_id` 存在时必须指向现有来源族。

### 6.3 来源笔记

来源笔记记录来源版本、创建者、创建时间和复核状态。每条笔记的 `source_id` 必须指向现有来源记录；来源笔记不是结构化引用的目标。

### 6.4 引用

知识条目正文使用以下结构化引用：

```md
具体陈述。[@01K00000000000000000000000, 卷三]
```

引用必须包含来源记录 ULID 和非空定位信息。校验器拒绝格式错误、目标缺失或目标不是来源记录的引用；只检查知识条目正文中的结构化引用。

## 7. 校验 CLI

公开入口是 `sutra validate [PATH]`，参数为项目根目录，省略时使用当前目录。CLI 聚合全部错误后输出项目相对路径、稳定规则标识、原因、对象数量和错误总数。

当前校验包括：

- 路径存在性、目录类型和内容 Vault 误传；
- Front Matter 存在性、YAML 解析与顶层映射；
- Schema 文件解析、自检及对象 Schema；
- 注册表结构与受控值；
- 全仓 ULID 唯一性；
- 知识关系目标、类型和适用范围；
- 来源笔记到来源记录、来源记录到来源族的引用；
- 知识条目正文到来源记录的结构化引用。

退出码为：`0` 校验通过，`1` 发现内容或仓库契约错误，`2` 命令用法错误。GitHub Actions 运行 Ruff、pytest 和 `sutra validate .`。

## 8. Git 边界

Git 保存 Markdown 内容、长期来源笔记、Schema、注册表、模板、工具、设计和 ADR。Obsidian 个人状态、收件箱临时材料、Python 构建产物、缓存、本地环境和大型本地媒体由 `.gitignore` 排除。

## 9. 当前验收标准

- `sutra validate .` 在当前空内容项目上返回 `0`，并实际解析现有 Schema 与注册表；
- 六类模板填入合法值后可在权威目录通过公开 CLI；
- 非法 Front Matter、Schema、注册表、ULID、关系、来源引用和正文引用返回稳定错误；
- 直接传入内容 Vault 返回 `PATH_IS_CONTENT_VAULT`；
- Ruff 与全部行为测试通过；
- Obsidian 打开 `sutra-pavilion/` 后只显示内容文件，Properties、链接和个人状态可用。

## 10. 已接受的架构决策

- [ADR-0001：以目录管理唯一归属与类型化关系](../adr/0001-directory-owned-knowledge.md)
- [ADR-0002：将来源库设为独立上下文和信任边界](../adr/0002-separate-source-context-and-trust-boundary.md)
- [ADR-0003：内容 Vault 命名为项目名称](../adr/0003-content-vault-named-after-project.md)
