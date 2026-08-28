# 藏经阁

藏经阁是一个以 Git 和 Markdown 为基础、面向人工维护与 AI 协作的结构化知识库项目。当前版本提供内容目录、机器契约、Obsidian 内容 Vault 和统一校验 CLI，用于可靠地编写并检查知识对象与来源对象。

## 当前能力

- 以“知识域 → 知识库 → 知识条目”组织知识内容；
- 独立维护来源族、来源记录、来源笔记和具体见证（Attestation）；
- 使用 JSON Schema 校验七类对象的 Front Matter，神话研究域叠加域公共与条目类型契约；
- 使用受控注册表校验条目类型、关系类型（含条目类型适用范围）、来源类型、Claim 谓词和标签；
- 校验 ULID 唯一性、关系目标、来源内部引用、Attestation 归属与权利边界、名称投影、发布状态和正文结构化引用；
- GitHub Actions 在 push 与 pull request 后自动运行 Ruff、全部行为测试和 `sutra validate .`。

知识条目正文只能引用 Attestation（ADR-0004）：条目 → 具体见证 → 唯一来源记录。来源记录必须登记来源角色（source_role）、访问方式和统一权利结构；`reuse_scope` 不提供 `unknown`，权利未确认时用 `metadata-only` 并在 `rights_statement` 写明。来源材料和来源笔记不会自动成为正式知识。

## 项目布局

项目根目录承载工程文件和机器契约，项目内同名目录 `sutra-pavilion/` 是 Obsidian 内容 Vault（ADR-0003）：

```text
sutra-pavilion/              # Git / Python 项目根目录
├── contracts/               # Schema 与受控注册表
├── docs/                    # 当前设计、Agent 导航和 ADR
├── specs/                   # 规格与执行计划
├── src/sutra_pavilion/      # CLI 与校验实现
├── sutra-pavilion/          # Obsidian 打开的内容 Vault
│   ├── .obsidian/
│   ├── CONTEXT-MAP.md
│   ├── knowledge/
│   ├── sources/
│   ├── inbox/
│   └── templates/
└── tests/                   # 公开 CLI 行为测试
```

七类权威对象位于：

- `sutra-pavilion/knowledge/domains/<domain>/_domain.md`
- `sutra-pavilion/knowledge/domains/<domain>/libraries/<library>/_library.md`
- `sutra-pavilion/knowledge/domains/<domain>/libraries/<library>/entries/<slug>.md`
- `sutra-pavilion/sources/catalog/families/<ULID>.md`
- `sutra-pavilion/sources/catalog/records/<ULID>.md`
- `sutra-pavilion/sources/notes/<来源记录 ULID>/<笔记 ULID>.md`
- `sutra-pavilion/sources/attestations/<ULID>.md`（文件名必须等于 ULID）

完整目录、对象格式和校验边界见[项目结构设计](./docs/design/project-structure.md)。

## Obsidian 集成

在 Obsidian 中选择“打开文件夹作为仓库”，打开项目内的 `sutra-pavilion/`。工程文件、`contracts/`、`docs/`、`specs/` 和测试不会出现在 Obsidian 文件树中。

团队只共享 `sutra-pavilion/.obsidian/app.json`。个人 workspace、外观、快捷键、图谱配置、缓存和社区插件目录均由 `.gitignore` 排除。项目根目录不是内容 Vault，其本地 `.obsidian/` 状态也不进入 Git。

Obsidian Wiki Link 用于人工导航；ULID、类型化关系和结构化引用用于机器校验。核心元数据使用顶层 YAML Properties，以便 Obsidian 原生读取和编辑。

已知限制：本地图谱过滤按笔记保存，无法通过共享核心设置统一表达。

## 可选的本地诊断

需要 Python 3.12+：

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

sutra validate .
```

`pip install -e .`（不带 `[dev]`）只安装运行依赖。

### CLI 约定

- `sutra validate [PATH]`：校验一个藏经阁项目；`PATH` 省略时使用当前目录。
- `sutra search <QUERY> [PATH] [--mode formal|research]`：大小写不敏感的字面检索，不解释正则。默认 `formal` 只返回 `published` 且 `verified` 的知识条目；`research` 返回全部条目、来源记录、Attestation 和来源笔记，并逐条标记 `research-only` 与未发布/未核验状态。
- 参数必须是项目根目录；直接传入内容 Vault 会返回 `PATH_IS_CONTENT_VAULT`。
- 退出码：`0` 校验通过或检索完成（含零结果）；`1` 发现内容或仓库契约错误（此时不输出检索结果行）；`2` 命令用法错误。
- 校验错误输出 `项目相对路径: 规则标识: 可操作原因`，最后输出对象数和错误总数；检索结果固定输出路径、对象类型、状态、标题四列。

## 当前状态

基础能力与神话研究领域基础已落地（相关执行计划已于 2026-08-27 执行完毕并移除）：仓库快照模块、Attestation 证据链、来源权利契约、神话域分层契约与语义校验、正式/研究检索、push / pull request CI、内容 Vault 中的神话域与知识库骨架，以及七类对象模板。

中国神话首期内容已入库并发布（2 个来源记录、3 条 Attestation、6 个 `published ∧ verified` 知识条目）；项目公开范围与大型原始材料位置仍是[上游开放决定](./specs/2026-08-24-myth-research-domain-requirements.md)。发布不要求 CODEOWNER、指定审核者或向 AI Agent 授予 GitHub 审核/仓库规则权限。

## 文档导航

- [领域上下文地图](./sutra-pavilion/CONTEXT-MAP.md)
- [知识上下文术语表](./sutra-pavilion/knowledge/CONTEXT.md)
- [来源上下文术语表](./sutra-pavilion/sources/CONTEXT.md)
- [项目结构设计](./docs/design/project-structure.md)
- [ADR-0001：以目录管理唯一归属与类型化关系](./docs/adr/0001-directory-owned-knowledge.md)
- [ADR-0002：将来源库设为独立上下文和信任边界](./docs/adr/0002-separate-source-context-and-trust-boundary.md)
- [ADR-0003：内容 Vault 命名为项目名称](./docs/adr/0003-content-vault-named-after-project.md)
- [ADR-0004：以 Attestation 作为唯一证据原子](./docs/adr/0004-attestation-as-single-evidence-atom.md)
- [神话研究领域设计](./specs/2026-08-26-myth-research-domain-design.md)
