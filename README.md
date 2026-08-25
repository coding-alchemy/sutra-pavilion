# 藏经阁

藏经阁是一个以 Git 和 Markdown 为基础、面向人工维护与 AI 协作的结构化知识库项目。当前版本提供内容目录、机器契约、Obsidian 内容 Vault 和统一校验 CLI，用于可靠地编写并检查知识对象与来源对象。

## 当前能力

- 以“知识域 → 知识库 → 知识条目”组织知识内容；
- 独立维护来源族、来源记录和来源笔记；
- 使用 JSON Schema 校验六类对象的 Front Matter；
- 使用受控注册表校验条目类型、关系类型、来源类型和标签；
- 校验 ULID 唯一性、关系目标、来源内部引用和正文结构化引用；
- 在本地与 GitHub Actions 中使用同一个 `sutra validate` 入口。

知识条目通过结构化引用连接具体来源记录。来源材料和来源笔记不会自动成为正式知识。

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

六类权威对象位于：

- `sutra-pavilion/knowledge/domains/<domain>/_domain.md`
- `sutra-pavilion/knowledge/domains/<domain>/libraries/<library>/_library.md`
- `sutra-pavilion/knowledge/domains/<domain>/libraries/<library>/entries/<slug>.md`
- `sutra-pavilion/sources/catalog/families/<ULID>.md`
- `sutra-pavilion/sources/catalog/records/<ULID>.md`
- `sutra-pavilion/sources/notes/<来源记录 ULID>/<笔记 ULID>.md`

完整目录、对象格式和校验边界见[项目结构设计](./docs/design/project-structure.md)。

## Obsidian 集成

在 Obsidian 中选择“打开文件夹作为仓库”，打开项目内的 `sutra-pavilion/`。工程文件、`contracts/`、`docs/`、`specs/` 和测试不会出现在 Obsidian 文件树中。

团队只共享 `sutra-pavilion/.obsidian/app.json`。个人 workspace、外观、快捷键、图谱配置、缓存和社区插件目录均由 `.gitignore` 排除。项目根目录不是内容 Vault，其本地 `.obsidian/` 状态也不进入 Git。

Obsidian Wiki Link 用于人工导航；ULID、类型化关系和结构化引用用于机器校验。核心元数据使用顶层 YAML Properties，以便 Obsidian 原生读取和编辑。

已知限制：本地图谱过滤按笔记保存，无法通过共享核心设置统一表达。

## 快速开始

需要 Python 3.12+：

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

sutra validate .
ruff check src tests
python -m pytest
```

`pip install -e .`（不带 `[dev]`）只安装运行依赖。

### CLI 约定

- `sutra validate [PATH]`：校验一个藏经阁项目；`PATH` 省略时使用当前目录。
- 参数必须是项目根目录；直接传入内容 Vault 会返回 `PATH_IS_CONTENT_VAULT`。
- 退出码：`0` 校验通过；`1` 发现内容或仓库契约错误；`2` 命令用法错误。
- 每个错误输出 `项目相对路径: 规则标识: 可操作原因`，最后输出对象数和错误总数。

## 当前状态

本地初始化已完成：CLI、Schema、注册表、六类模板、内容 Vault、测试与 CI 工作流均已落地；Obsidian 人工验收已确认通过。远端 CI 会在提交推送后按 `.github/workflows/ci.yml` 运行 Ruff、pytest 和真实仓库校验。

## 文档导航

- [领域上下文地图](./sutra-pavilion/CONTEXT-MAP.md)
- [知识上下文术语表](./sutra-pavilion/knowledge/CONTEXT.md)
- [来源上下文术语表](./sutra-pavilion/sources/CONTEXT.md)
- [项目结构设计](./docs/design/project-structure.md)
- [ADR-0001：以目录管理唯一归属与类型化关系](./docs/adr/0001-directory-owned-knowledge.md)
- [ADR-0002：将来源库设为独立上下文和信任边界](./docs/adr/0002-separate-source-context-and-trust-boundary.md)
- [ADR-0003：内容 Vault 命名为项目名称](./docs/adr/0003-content-vault-named-after-project.md)
