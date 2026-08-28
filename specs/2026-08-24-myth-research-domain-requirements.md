# 神话研究领域规范

- 文档版本：1.3
- 文档状态：已批准
- 创建日期：2026-08-24
- 修订日期：2026-08-27
- 适用范围：神话研究知识域的范围与知识库划分、知识模型、来源政策、存储与目录映射、采集流水线、检索协作、建设路线与伦理约束
- 取代关系：本文档与[中国神话首期建设规格](./2026-08-24-chinese-mythology-first-phase-requirements.md)共同取代《神话知识库初始建设需求》（原 docs/requirements/，已移除；内容经评审结论修订后重新分布到本文档）
- 架构基线与关联决策：[ADR-0001 目录唯一归属](../docs/adr/0001-directory-owned-knowledge.md)、[ADR-0003 内容 Vault 命名为项目名称](../docs/adr/0003-content-vault-named-after-project.md)、[ADR-0004 Attestation 唯一证据原子](../docs/adr/0004-attestation-as-single-evidence-atom.md)、[项目结构设计](../docs/design/project-structure.md)、[知识上下文术语表](../sutra-pavilion/knowledge/CONTEXT.md)、[来源上下文术语表](../sutra-pavilion/sources/CONTEXT.md)

---

## 1. 定位与范围

### 1.1 建立独立的神话研究知识域

神话研究是独立的知识域，不作为文学知识域下的单个知识库建设。依据[知识上下文术语表](../sutra-pavilion/knowledge/CONTEXT.md)对知识域的定义——具有独立研究方法和核心术语、足以容纳多个知识库的稳定学科或文化领域——神话研究的对象和方法满足全部条件：

- **独立方法**：文献考据、比较神话学、宗教研究、图像学、口述传统研究、考古与物质文化研究；
- **独立术语**：异文、母题、神格演变、民间合流、来源分层、仪式语境等自有概念体系；
- **多个知识库**：中国神话、佛教叙事、希腊—罗马神话等各自足以构成独立知识库。

范围判断的典型场景：“观音”同时涉及印度佛教、汉传佛教、民间信仰、图像史和文学接受。每个知识条目必须有一个由研究问题与证据范围决定的归属库；跨库研究使用有证据的 Claim 和类型化关系，不复制同一条目（见 3.2）。

本域研究口径的“神话”是叙事与文化研究术语，不用于否定任何活态信仰（见 1.6）。

### 1.2 域内知识库划分与建设顺序

| 知识库 | 覆盖内容 | 阶段 |
|---|---|---|
| 中国神话 | 经、史、子、集、类书、志怪、地方志、碑刻与口述传统中的中国神话材料 | 首期（见首期建设规格） |
| 佛教叙事 | 印度早期佛教与部派、巴利与南传、梵文与中亚、汉译佛典与中国撰述、藏传、东亚传播 | 第二期 |
| 希腊—罗马神话 | 诗史、赞歌、悲剧、地方崇拜、谱系、地志、铭文与陶瓶图像 | 第二期 |
| 北欧—日耳曼神话 | 诗体与散文埃达、斯卡尔德诗、萨迦、符文铭文与中世纪拉丁文记录 | 第二期 |
| 古埃及神话 | 金字塔文、棺材文、亡灵书、神庙铭文、纸草、墓葬图像与博物馆对象 | 第二期 |
| 印度神话 | 吠陀文献、史诗与传本、往世书、宗派传统、地方传统与耆那教叙事 | 第二期 |
| 古代近东神话 | 苏美尔、阿卡德、巴比伦、亚述、胡里—赫梯、乌加里特与迦南/腓尼基 | 第二期 |
| 道教神话 | 早期神仙叙事、道教经典、神仙传记、谱系位业、洞天福地、科仪与民间合流 | 第二期 |
| 凯尔特、伊朗与祆教、日本、斯拉夫、玛雅/阿兹特克、安第斯等 | 见 4.12 | 扩展期 |
| 非洲、北美原住民、澳洲原住民、太平洋岛屿、东南亚等活态口述传统 | 见 1.6 与 4.12 | 受限启用 |

库内组织原则（以中国神话为例，其他库同理）：

- 分层收录：先秦至两汉早期材料 → 正史与类书材料 → 志怪与传奇 → 地方与民间传统 → 少数民族与口述传统（单列社群、采录者、时间、地点、语言、授权与访问限制）；
- 核心研究问题是“某一形象在何时、何书、何种文类中如何出现”，不是“谁属于中国神系”；
- 道教材料须区分早期方仙与神仙叙事、道教经典、神仙传记、谱系位业、科仪雷法与民间合流；佛教材料按语言、文献传统、传承系统和传播阶段组织，不按“国内/国外”二分；希腊—罗马不把希腊名与罗马名合并为无版本差异的神祇卡；北欧区分“文献成书时代”“叙事可能保留的早期层次”与“现代重构”，并单设 reception 研究区；埃及按时期与地方神学组织，研究主键保留文本编号、对象号、转写、时期与出土地；印度史诗与往世书记录底本、校勘本、卷章或诗节号、语言与译者；近东区分苏美尔、阿卡德等语言传统并保留楔形文字文本编号与博物馆对象号。

建设顺序基于需求、资料条件和风险控制，不是价值排名：中国神话 → 佛教叙事与其余首期候选库 → 第二期传统 → 需要文化协议和田野伦理的活态或原住民传统。跨文化比较（比较研究阶段，见第 7 章）只在相关各库证据层达到基本完整度后进行。

### 1.3 建设目标

本域知识体系应支持以下任务：

- 查询神祇、人物、地点、器物、概念的名称、别名与出处；
- 按版本重建一个故事，而不是只给出混合后的通俗梗概；
- 追踪神格、名称、职能、图像和故事在不同语言、时代与宗教传统中的变化；
- 对比创世、洪水、冥界、世界树、屠龙、神圣王权等跨文化母题；
- 让 AI 助手对每个关键结论给出来源、定位、版本、译者或编辑者、访问日期与置信度；
- 识别未核验内容、权利不明内容、孤立条目和错误合并风险。

### 1.4 非目标

- 不把互联网百科或游戏设定批量搬入知识库；
- 不自动生成一套“唯一正确”的神谱；
- 不用 LLM 自动判定有争议的同源、影响或历史演变关系；
- 不镜像所有可访问的网站、现代译本或数据库；
- 不预先建设图数据库、向量数据库或 Obsidian 自研插件（图谱能力按 ADR-0001 渐进演进）。

### 1.5 收录标准

一条内容进入正式知识必须同时满足：`status: published`、`verification_stage: verified`，其研究结论能回溯到至少一个 Attestation 和所属来源记录，并由 push 或 pull request 触发的 CI 自动校验通过（见 3.4）。`verification_stage: lead` 是待核验线索，只能进入研究检索，绝不得发布或当作事实回答。

以下内容默认不进入正式知识：

- 无出处的短视频、营销号、论坛帖子和神话爱好者二手汇编；
- 游戏、影视、漫画、网络小说中的设定，除非研究主题就是现代接受史（reception 研究区）；
- LLM 自行补全的亲属关系、年代、神职或故事细节；
- 无法确定版本和译者的网络译文；
- 来源页面明确禁止自动获取而通过绕过限制取得的内容。

### 1.6 对活态宗教与原住民传统的表述

涉及佛教、道教、印度教、犹太教、基督教、伊斯兰教以及原住民传统时，区分：经典叙事、宗教教义与宇宙论、仪式与图像传统、圣徒/祖师/高僧传记、民间信仰与地方崇拜、文学戏曲和现代大众文化改写。

对于社群限定、秘密或神圣材料，即使法律上属于公版，也不能默认公开。应记录 `access_status`、`community_protocol` 和 `consent_note`，并参考 [Local Contexts Traditional Knowledge Labels](https://localcontexts.org/labels/traditional-knowledge-labels/) 与 [CARE Principles for Indigenous Data Governance](https://www.gida-global.org/care)。

扩展期活态口述传统启用前置条件：

- 有语言与区域背景资料；
- 能确认材料的采录和传播许可；
- 能识别社群限定或神圣内容；
- 有合适的社群或学术顾问；
- 能将殖民时期记录与当代社群自述分开。

规划这些范围时不得把内部多样的传统合并表述（不建立泛化“非洲神话”“印第安神系”），优先使用具体民族/语言/社群名称。

---

## 2. 与既有架构的映射

### 2.1 两个领域上下文

本域全部对象落入既有两上下文，不新建第三上下文：

- **知识上下文**（`sutra-pavilion/knowledge/`）：知识域、知识库、知识条目、条目元数据、知识关系与发布生命周期；
- **来源上下文**（`sutra-pavilion/sources/`）：来源族、来源记录、具体见证（Attestation，本域新增对象）、来源笔记、质量评价、权利与可用状态。

`contracts/` 位于项目根目录，保存两上下文的 Schema 和注册表，不属于 Obsidian 内容 Vault。当前 CLI 仅支持六类对象及“条目 → 来源记录”引用；本规范定义的 Attestation 链属于后续实现目标，未完成 §9.2 所列变更前不得宣称当前 CLI 已支持。

### 2.2 神话对象的上下文归属

| 需求侧对象 | 归属 | 项目内表达 |
|---|---|---|
| Tradition（传统） | 知识上下文 | 知识条目（新增条目类型 `tradition`），可被类型化关系引用 |
| Entity（实体） | 知识上下文 | 知识条目（复用人物、地点、概念、作品等既有类型，辅以神话类型属性；器物等若无合适类型，新增类型或以类型属性表达，设计阶段对照注册表决定） |
| Episode（叙事版本） | 知识上下文 | 知识条目（新增条目类型 `episode`，版本特定，异文不合并） |
| Motif（母题） | 知识上下文 | 知识条目（新增条目类型 `motif`，须含操作性定义、子类型与外部编目对齐；不是标签） |
| Claim（主张） | 知识上下文 | 知识条目（新增条目类型 `claim`，解释性关系的唯一载体） |
| Source（来源） | 来源上下文 | `sutra-pavilion/sources/catalog/records/` 下的来源记录；同一作品的多个版次可归入 `sutra-pavilion/sources/catalog/families/` 来源族 |
| Attestation（具体见证） | 来源上下文 | `sutra-pavilion/sources/attestations/` 下的一等对象（新增目录、Schema、扫描与校验，见 9.2）：某版本中的具体篇卷、段落、诗节、页、铭文或图像见证 |
| Research Note（研究笔记） | 来源上下文 | `sutra-pavilion/sources/notes/`，仅进入研究检索，可转化为条目草稿 |

新增条目类型（`tradition`、`episode`、`motif`、`claim`）须经审核加入 `contracts/knowledge/registry/entry-types.yaml`，并配套类型 Schema。

### 2.3 《山海经》三层规则

同名混淆的高发点是“作品—版本—见证”三个层次，必须严格分开，不得合并为一个 Source：

1. **抽象作品《山海经》**：知识条目（作品类型），承载关于这部作品的知识；
2. **某出版社某版《山海经》**：来源记录（可与其他版次归入“山海经”来源族），承载书目、版本、权利与获取信息；
3. **某版中的某篇某段**：Attestation，承载精确定位、原文/译文分层与文本说明。

**唯一证据链**：神话领域的知识条目与 Claim 只能引用 Attestation ULID；Attestation 必须且只能关联一个来源记录 ULID。不得在同一模型中同时允许条目直引来源记录。现有 CLI 的直引来源记录语法是迁移前基线，待 Attestation 支持完成后一次性替换。

### 2.4 目录与存储映射

项目根目录承载工程文件与 `contracts/`；Obsidian 只打开项目内 `sutra-pavilion/`。本域不新设第二个 Vault 或 `corpus/`，本域相关结构：

```text
<项目根>/
├── contracts/                         # Schema 与注册表，不进入 Obsidian
│   ├── knowledge/
│   └── sources/
├── sutra-pavilion/                    # 唯一内容 Vault，Obsidian 打开此目录
│   ├── knowledge/domains/myth-research/
│   │   └── libraries/chinese-mythology/
│   │       ├── _library.md
│   │       ├── entries/
│   │       └── assets/<entry-ulid>/
│   ├── sources/
│   │   ├── catalog/families/
│   │   ├── catalog/records/
│   │   ├── attestations/              # 目标目录；待 §9.2 实现并扫描
│   │   ├── notes/<source-record-ulid>/
│   │   └── assets/text/
│   ├── inbox/imports/
│   └── templates/
├── .local/                            # 大型原始材料候选位置（本地保留、不入 Git）
└── .generated/normalized/             # 可重建的标准化数据（不入 Git）
```

原需求 `corpus/` 的职责映射：

| 原需求 | 映射后 |
|---|---|
| `corpus/manifests/` 来源清单 | `sutra-pavilion/inbox/imports/`（获取任务、日志、清单）+ `sutra-pavilion/sources/catalog/records/`（正式登记） |
| `corpus/raw/` 原始文件 | 大型 XML、PDF、扫描件：`.local/`（或仓库外存储，属待决定项①）；小型文本：`sutra-pavilion/sources/assets/text/` |
| `corpus/normalized/` | `.generated/normalized/`（可从原始材料重建，不入 Git） |
| `corpus/mappings/` | `.generated/normalized/` 内的可重建映射产物 + Attestation 的定位字段 |
| `corpus/logs/` | `sutra-pavilion/inbox/imports/` |

“只增不改”原则保留：原始文件（`.local/` 或仓库外存储、`sutra-pavilion/sources/assets/text/`）不覆盖清洗，每次更新存新版本或记录提交 SHA，保留许可副本与获取日志，计算并登记 SHA-256。

**批量采集前置决定（阻塞建设路线阶段 B，不阻塞首期试点）**：

1. **原始材料存储位置**：默认候选为 `.local/`（`.gitignore` 已约定大型媒体统一放入且不入 Git）；若采用仓库外目录，须同时确定备份策略。批量采集开始前必须由用户明确；
2. **项目定位**：纯私人研究，或未来可能公开。影响条目发布许可、权利核验强度与阶段 F 发布流程（见 4.3、第 7 章阶段 F、9.1）。

### 2.5 Obsidian 能力边界与附件

Obsidian 只打开 `sutra-pavilion/`，其中的 `knowledge/`、`sources/`、`inbox/`、模板和上下文地图可互相链接；项目根目录的 `src/`、`tests/`、`docs/`、`specs/`、`.generated/` 与 `contracts/` 不进入其文件树。

| 能力 | 用途 | 设计边界 |
|---|---|---|
| 本地 Markdown 存储 | 主数据和正文 | `.obsidian` 是配置不是事实数据库；避免嵌套 Vault |
| Properties（顶层扁平 Front Matter） | 稳定字段、列表、日期 | 同名属性保持同一类型；遵循既有 entry schema 契约 |
| Internal links / Aliases | 人工导航、多语言名称召回 | Wiki Link 不承担永久身份；正式身份是 ULID（ADR-0003） |
| Search | 人工检索属性、路径和正文 | 不等价于 XML/PDF 全文检索，也不是语义推理引擎 |
| Templates | 插入固定模板（`sutra-pavilion/templates/`，Obsidian 与 CLI 共用） | 模板只负责文本插入 |
| Bases | 来源审计、待复核、权利状态视图 | `.base` 是可重建视图，输出不作持久事实 |
| Canvas / JSON Canvas | 神谱、传播路径、版本演变图 | 事实和关系必须另存 Markdown 条目 |
| Obsidian URI | 外部打开、创建、搜索笔记 | 不是主要读取接口 |

社区插件（Dataview、Templater 等）可以后加，但第一版必须在禁用它们时仍完整可读。

**附件与图片**：条目图片和小型媒体位于 `sutra-pavilion/knowledge/domains/<domain>/libraries/<library>/assets/<entry-ulid>/`。每张图片必须对应一个来源记录或 Attestation，并记录机构与对象号、原始对象页面、下载 URL、创作者或持有机构、权利声明与许可、获取日期、是否允许公开再分发。只写“图片来自网络”不合格。

### 2.6 Git 与备份

沿用项目结构设计的 Git 策略：

- 提交：Markdown 条目与来源记录、长期来源笔记、Schema、注册表、模板、配置、来源位置/权利信息/校验值、上下文地图、设计文档、政策和 ADR；
- 不提交：`.generated/` 全部产物、`sutra-pavilion/inbox/extracted/` 临时提取结果、`.local/` 大型原始材料、API key、账户 cookie、访问令牌、受限社群材料、不允许再分发的全文；
- 本地 Git 历史不是备份：`.local/` 或仓库外原始材料至少保留一个加密的异地或离线副本。

---

## 3. 知识模型

### 3.1 对象层次

```text
来源记录 Source Record（某具体版次/版本/快照）
  └─ 具体见证 Attestation（某版本、某篇卷、某段原文或某件文物）
       └─ 主张 Claim（这段材料能够支持什么结论）
            ├─ 实体 Entity（神祇、人物、群体、地点、器物、概念）
            ├─ 叙事 Episode（某一版本中的故事或事件）
            ├─ 传统 Tradition（时代、语言、地域、宗教与文类语境）
            └─ 母题 Motif（用于跨文化比较的分析概念）
```

各类型的表达边界：

| 类型 | 表达什么 | 不表达什么 |
|---|---|---|
| `tradition` | 某时段、地域、语言、宗教或文类语境 | 不把整个文明压成单一神系 |
| 实体（复用既有类型 + 神话类型属性） | 神祇、人物、群体、魔物、地点、器物或概念 | 不自动包含所有时代版本的故事 |
| `episode` | 某一可描述的叙事或事件及其版本 | 不把异文调和成唯一标准版 |
| `motif` | 跨文化比较的受控分析概念 | 不代替文本自身的分类和词汇 |
| `claim` | 一条可以被证据支持或反驳的研究主张 | 不允许无证据引用的确定性断言 |
| 来源记录 | 作品版次、论文、数据库或博物馆对象的书目、权利与获取信息 | 不存放未经定位的研究结论 |
| `attestation` | 某来源中的具体段落、诗节、页、铭文或图像见证 | 不把解释冒充原文 |
| 来源笔记 | 对多条 Claim 的综合、比较和研究日志 | 不成为唯一证据层，不自动成为正式知识 |

这个分层解决四个长期问题：异文不被抹平；跨文化演变可以被证明（演变是带证据、关系类型和置信度的主张，不是无来源字段）；版权状态可控；Obsidian 与 AI 助手各司其职（Obsidian 提供本地 Markdown、属性、链接和视图；AI 助手直接检索项目文件、核对来源并生成草稿，不依赖第三方插件内部索引）。

### 3.2 身份与标识

- 所有知识对象与来源对象使用不可变 **ULID**；文件名、标题和译名可以调整，ULID 一经使用不重用；
- 原需求的语义 ID（如 `ENT-xiwangmu`）降级为 **slug**（可读稳定键，用于文件命名与人工导航）或 `legacy_key`（导入既有语义 ID 时兼容）；
- 外部 ID（QID、CTS URN、馆藏号）只放在 `external_ids` 类字段，用于查找和重复检测，不能替代内部身份；
- 删除的 ULID 不复用；发生误合并时，保留旧对象的说明与重定向，建立两个新对象。

目录是知识条目归属的唯一事实：每个知识条目只位于一个知识库的 `entries/` 目录，目录路径决定其知识域和知识库归属，任何额外字段都不得覆盖或重复此事实。创建时按条目所要回答的主要研究问题与首要证据语境选择最具体的知识库；跨库使用只添加关系或 Claim，不复制条目。若“观音”在中国材料中的形象与印度佛教的 Avalokiteśvara 是否为同一对象尚无充分证据，应建立两个语境明确的条目，并用 `identified_with`、`developed_from` 或其他 Claim 表达有条件关系；不得因名称相近强行合并。知识域、知识库及来源上下文对象仍按各自权威目录归属，不适用“归属库”规则。

### 3.3 元数据继承与神话类型属性

所有神话条目继承项目公共条目元数据（`schema_version`、`id`、`title`、`slug`、`aliases`、`summary`、`entry_type`、`language`、`status`、`tags`、`search_terms`、`relations`），由 `entry.schema.json` 统一校验；`summary`、`slug`、`search_terms`、`schema_version` 为 Meta 优先检索所必需，不得省略。神话专属字段放入 `attributes`，由条目类型 Schema 校验。需要记录语言、文字、转写或翻译关系的名称以 `name_forms` 为唯一结构化事实源：其中必须恰有一个展示名称，其文本等于 `title`；`aliases` 等于其余 `name_forms[].text` 的扁平去重集合。`title` 与 `aliases` 是兼容公共条目契约和检索所需的投影，不由作者另行维护；校验器必须拒绝展示名称缺失、多个展示名称或投影不一致。

原需求字段向项目字段的映射：

| 原需求字段 | 项目字段 |
|---|---|
| `id: ENT-xiwangmu`（语义 ID） | `id`：ULID；`slug: xiwangmu`；既有语义 ID 作 `legacy_key` 兼容 |
| `type` | `entry_type`（中央注册表受控；本域新增类型见 2.2） |
| `title_zh` | 展示名称同时进入 `name_forms` 并投影为 `title`；异名、异译、原文名、转写名进入其余 `name_forms` 并投影为 `aliases` |
| （无） | `summary`、`slug`、`search_terms`、`schema_version` 新增必需 |
| `traditions` | 指向 `tradition` 条目的类型化关系；条目内冗余属性仅供检索（是否保留由设计定） |
| `languages` | `language`；多语言需求以类型属性承载（设计定） |
| `source_refs` | 结构化引用：Attestation ULID + 证据角色 + 证据强度（1–5）；定位仅存于 Attestation，Attestation 再关联唯一来源记录 |
| `verification_status` | 拆分为 `status` + `verification_stage` + `controversy_status`（见 3.4） |
| `rights_status` | 来源侧权利字段（见 4.3）；条目侧另设发布许可，两者分离 |
| `created` / `reviewed_at` | 保留为内容元数据；它们不能证明人工复核或发布（见 3.4） |
| `external_ids` | 保留，仅作外部标识 |

各类型的最小结构要求：

| 类型 | 必备内容 |
|---|---|
| 实体 | `entity_kind`（附录 A 词表）、外部 ID、时间属性 |
| `episode` | 版本归属说明、人物关系、母题关系、见证引用 |
| `motif` | 操作性定义（正文）、子类型、外部编目对齐（索引名 + 版本 + 编号） |
| `claim` | 可检验的主张句、主体/谓词/客体、证据引用、置信度、适用范围、反证与其他解释章节 |
| `tradition` | 范围（时段、地域、语言、宗教、文类）、核心来源、内部分期与争议 |
| `attestation` | 精确定位（篇卷/页行/对象号）、唯一 `source_record_id`、原文/工作译文/文本说明分层、证据层级、能支持与不能支持的结论 |
| 来源记录 | `source_role`、书目与版本、获取方式与哈希、权利信息、可追溯性与严谨度评分（见第 4 章） |

笔记模板不在本规范中直接规定；实施阶段在 `sutra-pavilion/templates/` 下按上述要求创建，并经评审后使用。原需求第七章模板不得直接复制。

### 3.4 三维状态模型

发布状态、核验程度和争议属性是三个独立维度，不得混用：

| 维度 | 取值 | 含义 |
|---|---|---|
| `status` | `draft` / `review` / `published` / `archived` | 发布生命周期：状态由内容变更表达；push 或 pull request 后由 CI 自动检查发布契约 |
| `verification_stage` | `lead` / `checked` / `verified` | 证据核验程度：`lead` 仅有线索；`checked` 已核对来源和定位；`verified` 已核对版本、定位、权利和关键解释 |
| `controversy_status` | `none` / `disputed` | 可靠来源之间是否存在实质分歧；是争议属性，不是生命周期阶段 |

回答与检索规则：

- **正式知识检索只使用 `status: published` 且 `verification_stage: verified` 的条目**；任一条件不满足均不用于正式回答；
- 研究检索可命中草稿与线索，但输出必须明确提示内容尚未成为正式知识、尚未核验；
- `verified` 不是“绝对真实”，而是“当前条目中的表述与所列证据相符，并明确了证据边界”；
- `disputed` 条目仍可发布，但正式回答必须并列呈现分歧，不自动选边。

`verified` 与 `published` 不绑定 GitHub 账号、团队、CODEOWNER 或人工平台审批。变更 push 到仓库或提交 pull request 后，GitHub Actions 必须自动运行 Ruff、全部行为测试和 `sutra validate .`；失败时该提交不满足发布条件。CI 只验证仓库契约与可自动判断的证据链，不要求 AI Agent 持有仓库规则、审核者或发布权限，也不以本地重复运行命令作为完成证据。

### 3.5 时间属性

神话材料常有不确定年代，不使用单一 `era` 文本，采用四字段组合作为类型属性：

```yaml
date_label: "约战国至西汉早期；具体层次有争议"
date_start: -0300
date_end: -0100
date_certainty: disputed
```

`date_start`/`date_end` 用于排序，`date_label` 用于学术表述，`date_certainty` 取 `exact`、`approximate`、`range`、`disputed`、`unknown`。

### 3.6 关系类型与主张表达

不使用简单“同一实体”字段压平历史差异。关系分三类：

**结构关系**：直接以条目类型化关系表达，加入 `relation-types` 注册表（如 `part_of`：叙事、群体或文本结构中的组成关系；实体在具体见证中的出现通过 Attestation 引用机制表达，不另设关系类型）。

**名称关系**：`translated_as` 只表示同一知识条目内两个 `name_forms` 之间的翻译关系，逻辑上记录在源名称形式上，端点均为 `name_forms[].id`。它不是 Claim 谓词，也不连接两个知识对象。

**解释性关系**：知识对象之间的解释性关系必须通过 `claim` 条目表达，谓词受控：

| 谓词 | 含义 |
|---|---|
| `identified_with` | 某历史材料或群体明确将两者视为同一 |
| `syncretized_with` | 两个传统在特定语境中发生融合 |
| `developed_from` | 有研究证据支持后者由前者发展而来 |
| `influenced_by` | 存在影响，但不等于身份相同或直接演变 |
| `literary_adaptation_of` | 文学作品对较早形象或故事的改写 |
| `counterpart_of` | 分析性对应，不声称历史同源 |
| `possibly_related_to` | 证据不足、存在争议的可能关系 |

每个 `name_forms` 记录含文本、语言/文字、转写方案（如适用）与使用语境。跨对象的身份、演变或对应只能用以对象 ULID 为端点的 Claim。每条解释性关系（Claim）至少包含：主体、谓词、客体、Attestation 证据、提出者或解释来源、时间/地域语境、置信度和争议说明。

---

## 4. 来源政策

### 4.1 先区分四种“可以获取”

| 状态 | 含义 | 可以做什么 |
|---|---|---|
| 可发现 | 搜索引擎、目录或知识图谱能找到记录 | 保存书目、ID 和回链 |
| 可阅读 | 网页或订阅界面允许人工查看 | 人工研究、按规则短引；不代表可自动抓取 |
| 可下载/接口访问 | 官方提供 API、数据包、Git、IIIF 或下载按钮 | 按接口条款、速率和许可处理 |
| 可再分发 | 明确许可允许复制或发布相应内容 | 在许可范围内保存全文或图片，并履行署名、非商业、相同方式分享等条件 |

每个来源记录都应记录 `access_method` 与 `reuse_scope`。权利未确认时一律为 `reuse_scope: metadata-only`，只保存书目、稳定 ID、定位与链接；`link-quote` 只能在维护者完成逐项权利核验后使用，并记录许可依据与允许的短引范围。

### 4.2 来源角色与评分体系

原需求的 A–E 等级实际描述**来源用途**而非质量排序，改为 `source_role`（来源角色），与既有三项评分并存、各表其义：

| `source_role` | 对象 | 用途 | 能否单独支撑关键结论 |
|---|---|---|---|
| `raw-material`（原 A） | 原典、铭文、写本、考古对象、口述记录原始档案 | 证明“材料实际写了或展示了什么” | 可以，但仍需解释版本与语境 |
| `critical-edition`（原 B） | 学术校勘本、权威译注、语料库、目录学工具书 | 确定文本、版本、词义和定位 | 通常可以 |
| `scholarship`（原 C） | 同行评议论文、学术专著、研究型百科 | 解释年代、演变、同源和争议 | 可以，重要争议宜多源互证 |
| `institutional-overview`（原 D） | 博物馆或大学科普、可靠参考网站 | 建立概览和发现线索 | 不宜单独支撑争议结论 |
| `discovery-clue`（原 E） | Wikidata、Wikipedia、博客、爱好者网站 | 别名、外部 ID、搜索入口 | 不可以，只作线索 |

并存评分（沿用项目既有定义，见[来源上下文术语表](../sutra-pavilion/sources/CONTEXT.md)）：

- **可追溯性评分 1–5**：来源身份、出处和流转记录可被核验的程度（来源记录上，含理由、评分人和评分时间）；
- **严谨度评分 1–5**：研究方法、论证过程或编辑审查严谨程度（来源记录上，同上）；
- **证据强度 1–5**：一次具体引用对当前陈述的支持程度（每次引用上，不继承来源整体评价）。

AI 可以建议评分，评分只有人工确认后生效。

### 4.3 权利模型：来源权利与条目发布许可分离

原需求把 `rights_status` 放进所有笔记，混淆了两个不同对象，必须拆开：

- **来源材料权利**（来源记录与 Attestation 上）：`rights_statement`（逐字记录来源页面权利说明或准确摘要）、`license_spdx`、`reuse_scope`（`redistributable` / `noncommercial` / `link-quote` / `metadata-only` / `permission-required` / `restricted-cultural`）、`access_method`；Attestation 继承并受限于其所属来源记录的权利边界。权利尚未确认不是独立的 `reuse_scope`，一律以 `metadata-only` 表达，并在权利说明中记录待核验状态；
- **条目发布许可**（知识条目上）：项目原创内容的发布授权，字段名由设计定（候选 `publish_license`）；在待决定项②（私人研究或可能公开）明确前，默认仅私人使用。

### 4.4 跨传统通用资源

| 资源 | 获取方式 | 合适用途 | 关键限制 |
|---|---|---|---|
| [Wikidata](https://www.wikidata.org/wiki/Wikidata:Data_access) / [Query Service](https://query.wikidata.org/) | MediaWiki API、SPARQL、数据转储 | QID、跨语言别名、外部 ID、候选关系 | 结构化数据为 CC0，但内容质量不均；仅作骨架和线索，关系必须回到学术或原始来源；遵守查询服务使用规范 |
| [Wikimedia Commons](https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia) | MediaWiki API、文件页下载 | 公版或开放许可图像发现 | 每个文件的许可、作者、来源和署名要求不同，不能把 Commons 当统一 CC0 图库 |
| Wikisource 各语言站 | [MediaWiki API](https://www.mediawiki.org/wiki/API:Main_page) | 公版或自由文本的章节检索、版本发现 | 每部作品与转录页面的版权状态、校勘质量和页面许可均需核验；API 有请求限制和礼貌使用要求 |
| [Project Gutenberg](https://www.gutenberg.org/) | 官方电子书下载、[离线目录](https://www.gutenberg.org/ebooks/offline_catalogs.html) | 公版旧译本和旧版研究著作 | 公版判断与读者所在地有关；电子书头尾许可说明需保留；Gutendex 是第三方便利接口，不是官方 API |
| [Europeana APIs](https://pro.europeana.eu/page/apis) | 注册 API key 后检索聚合记录 | 跨欧洲馆藏发现 | 元数据和媒体权利分开；读取每条记录的 rights 字段，不能用聚合站政策覆盖原机构 |
| [Library of Congress APIs](https://www.loc.gov/apis/) | JSON/YAML 接口、集合检索 | 旧版译本、民俗录音、地图和图像 | 逐项目读取 Rights and Access；馆方往往不能代权利人授权 |
| [IIIF Presentation API 3.0](https://iiif.io/api/presentation/3.0/) | 获取 Manifest、Canvas、图像服务 | 手稿、扫描书、博物馆对象的页序与稳定定位 | Manifest 中的 `rights` 和 `requiredStatement` 必须一起保存；IIIF 是传输标准，不是开放许可 |
| [TEI P5](https://tei-c.org/release/doc/tei-p5-doc/en/html/) | XML 文本编码规范 | 保存文本层次、校勘、责任与来源 | 转换为 Markdown 时不得丢失 `sourceDesc`、页行锚点、语言和责任声明 |

学术研究与书目发现（下列接口适合发现论文与书目，不代表能取得或再分发全文）：

| 资源 | 获取方式 | 用途 | 边界 |
|---|---|---|---|
| [OpenAlex](https://docs.openalex.org/) | API、数据快照 | 通过题名、作者、概念、引用和开放获取链接发现研究 | 书目图谱用于发现；论文事实、全文许可和版本仍回到出版者或仓储记录核验 |
| [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) | REST API | DOI、作者、出版信息、引用关系和许可字段 | 元数据中的 URL 或 license 字段不等于已获得全文复用权；遵守 polite 使用建议并保留 DOI |
| [DOAJ API](https://doaj.org/api/v4/docs) | API | 发现开放获取期刊和文章 | 每篇文章按其 license 字段使用，不能仅凭收录于 DOAJ 就假设统一许可 |
| [JSTOR Data for Research](https://www.jstor.org/dfr/) | 站内研究工具、按项目条件取得数据 | 文献计量、主题检索和受控文本分析 | 访问、下载和输出受项目及订阅条款约束；不把它当普通全文抓取接口 |

Google Scholar 可用于人工发现，但不应把没有官方公开文档支持的抓取方案写进自动采集流程。

### 4.5 中国古籍与道教来源

| 资源 | 获取方式 | 推荐用途 | 授权与技术边界 |
|---|---|---|---|
| [中国哲学书电子化计划 CTP](https://ctext.org/) / [官方 API](https://ctext.org/tools/api) | 人工网页检索；按官方说明使用 JSON API | 先秦汉代古籍、章节层级、CTP URN、异文线索 | 站点明确禁止用自动下载软件抓网页；API 有匿名、账户或机构层级的限额且仍可能变化。只能走官方 API 或人工使用，并缓存、节流、回链 |
| [Kanripo GitHub 组织](https://github.com/kanripo) | 按仓库克隆或下载 | 经史子集、道藏和佛藏相关文本的离线研究 | 公开仓库不自动等于统一开放许可；逐仓库检查说明、来源和许可。KR5 的实际覆盖应以当前目录和书目清单为准，不写成未经审计的“整部且唯一” |
| 中文 Wikisource | MediaWiki API、页面导出 | 《山海经》《楚辞》《淮南子》《搜神记》等公版文本的辅助获取 | 校勘与版本质量不一；保存页面修订 ID、底本说明、访问日期和许可；重要结论再与学术版本对照 |
| [中央研究院汉籍电子文献资料库](https://hanchi.ihp.sinica.edu.tw/) | 人工检索 | 正史、类书和汉籍定位 | 权威检索入口不等于开放批量数据；未见明确机器许可时只存书目、定位和短引 |
| [中国国家图书馆](https://www.nlc.cn/) / [中华古籍资源库](https://mylib.nlc.cn/web/guest/zhonghuagujiziyuanku) | 目录、数字影像、账户访问 | 版本、馆藏号、地方志和古籍影像核验 | 扫描、OCR 和下载权利逐项处理；批量用途需馆方明确许可 |

道教首批材料可从《列仙传》《神仙传》《抱朴子》《真诰》《真灵位业图》《云笈七签》以及《正统道藏》相关文献开始。每条神格演变至少记录：最早可确认的名称和文本见证；职能、位阶和图像的阶段变化；与地方神、历史人物、佛教神格或国家祭祀的关系；关系由哪位研究者或哪段原典提出。

### 4.6 佛教来源

| 资源 | 获取方式 | 推荐用途 | 授权与技术边界 |
|---|---|---|---|
| [CBETA](https://www.cbeta.org/) / [版权宣告](https://www.cbeta.org/copyright.php) / [官方 XML-P5](https://github.com/cbeta-org/xml-p5) | 官方下载、Git、TEI P5 XML | 汉文大藏经、汉译印度材料、中国撰述、传记与感应材料 | 主要许可为 CC BY-NC-SA 4.0 且限非营利用途，并有不适用该许可的近现代著作类别；再传播须带版本和版权说明。不能笼统写成“公版全藏” |
| [SuttaCentral](https://suttacentral.net/) / [sc-data](https://github.com/suttacentral/sc-data) / [bilara-data](https://github.com/suttacentral/bilara-data/tree/published) | 网站、Git、JSON、稳定 segment ID | 巴利与其他根本文本、多语翻译对齐、本生与早期佛教叙事 | 按具体 `_publication.json`、文件或仓库说明核验许可；不同译者和历史数据可能不同，不把整站统一推定为 CC0 |
| [BDRC](https://www.bdrc.io/) / [BUDA Library](https://library.bdrc.io/) | 网页、稳定 RID、部分 Linked Data 或 IIIF 能力 | 藏文书目、人物、地点、甘珠尔/丹珠尔版本和影像 | 元数据、扫描、OCR 和转写的权利不同；读取每条资源的 access/rights 字段。接口和速率在实际采集前二次核验 |
| [84000 Reading Room](https://84000.co/reading-room/) / [Terms of Use](https://84000.co/terms-of-use/) | 人工阅读和官方提供的下载 | 藏传经典的现代可读译文 | 现代译文受版权与站点条款约束；默认链接、书目和短引，不批量镜像全文 |
| [SAT 大正藏数据库](https://21dzk.l.u-tokyo.ac.jp/SAT/) | 人工检索、页栏行定位 | 复核大正藏底本图像和 `T` 编号定位 | 未确认统一开放接口或许可时不批量下载；保存页、栏、行和回链 |

佛、菩萨、天部与护法的名称对应不等于历史形态完全相同：译名连续性、图像性别变化、地方职能扩展和民间故事吸收应由不同 Claim 表达。

### 4.7 古印度与梵文来源

| 资源 | 获取方式 | 推荐用途 | 授权与技术边界 |
|---|---|---|---|
| [GRETIL](https://gretil.sub.uni-goettingen.de/gretil.html) | 网页目录、单篇文本下载 | 吠陀、史诗、往世书、佛教梵文与耆那文本发现 | 不存在可一概而论的全库许可；逐文件读取 header、底本和版权说明；未确认稳定 API |
| [SARIT](https://sarit.indology.info/) / [SARIT corpus](https://github.com/sarit/SARIT-corpus) | Git、TEI P5 XML | 结构化梵文文本、版本和校勘信息 | 可克隆用于研究不等于可把全部内容重新许可发布；逐 TEI Header 与来源说明确认复用范围 |
| [Vedic Heritage Portal](https://vedicheritage.gov.in/) | 官方门户、文本和音频浏览 | 吠陀分支导航、读音和仪式语境 | 未确认统一开放 API；编辑文本和音频默认人工引用、链接，不镜像 |
| [Muktabodha Digital Library](https://muktalib7.com/dli/) | 网站、账户或项目流程 | 湿婆、女神、怛特罗等宗派与仪轨材料 | 逐项遵守访问和版权说明；没有明确许可时不自动抓取 |

### 4.8 希腊—罗马来源

| 资源 | 获取方式 | 推荐用途 | 授权与技术边界 |
|---|---|---|---|
| [Perseus Digital Library](https://www.perseus.tufts.edu/) / [Scaife Viewer](https://scaife.perseus.org/) / [PerseusDL](https://github.com/PerseusDL) | 网页、CTS 标识、项目 Git 仓库 | 希腊/拉丁原文、部分译文、形态分析、卷章行定位 | 每个版本、校勘和译文许可不同；逐仓库和文本元数据核验，不把整个平台视为同一开放许可 |
| [Pleiades](https://pleiades.stoa.org/) / [下载页](https://pleiades.stoa.org/downloads) | 网页、结构化下载、对象 URI | 古代地点、名称、坐标、时期和文献关联 | 核心数据以 CC BY 3.0 为主，使用对象 URI 并署名；外链地图和图片另核权利 |
| [Loeb Classical Library](https://www.loebclassics.com/) | 订阅或机构访问 | 权威原文、英译、卷页和版本核验 | 现代校勘和译文受版权保护；不得批量抓取或镜像，只作人工核对和合规短引 |
| [ToposText](https://topostext.org/) | 网站和地图浏览 | 文本段落与古代地点的发现 | 作为导航层；每篇译文和下载内容按项目条款处理 |

### 4.9 北欧—日耳曼来源

| 资源 | 获取方式 | 推荐用途 | 授权与技术边界 |
|---|---|---|---|
| [Menota](https://www.menota.org/) / [CLARINO catalogue](https://clarino.uib.no/menota/catalogue) | 目录、部分 TEI/XML 下载 | 中世纪北欧手稿转写、校勘与规范 | Menota 标准和具体文本是不同权利对象；每个语料包逐项看许可 |
| [Handrit.is](https://handrit.is/) | 手稿目录、部分数字影像或 IIIF | 锁定埃达、萨迦手稿、年代、叶码和馆藏号 | 元数据与影像权利由持有机构或单件声明决定；高清、出版或商业用途可能需许可 |
| [Skaldic Project](https://skaldic.org/) | 网页检索 | 斯卡尔德诗、手稿见证、kenning、现代校勘和翻译 | 现代校勘、译文和注释通常受版权保护；默认定位和短引，不作无许可全文获取 |
| [Dictionary of Old Norse Prose](https://onp.ku.dk/onp/onp.php) | 网页词典与语料引证 | 专名异拼、词义和语境核验 | 词典编纂内容受版权保护；没有开放数据许可时不批量复制 |
| [Bækur.is](https://baekur.is/) | 冰岛数字化历史印本 | 早期印本、研究著作和页码证据 | 原书公版不自动等于扫描/OCR 可任意再发布；按条目条件处理 |

现代影视和游戏对奥丁、索尔、洛基等形象影响很大，应设置 reception 研究区，但不得把现代设定反写进原典条目。

### 4.10 古埃及来源

| 资源 | 获取方式 | 推荐用途 | 授权与技术边界 |
|---|---|---|---|
| [Thesaurus Linguae Aegyptiae](https://thesaurus-linguae-aegyptiae.de/) | 网页语料与词典检索 | 古埃及文本编号、转写、词形和上下文 | 古代文本与现代转写、翻译、标注的权利不同；无明确批量许可时只保存 ID、定位、短引和回链 |
| [Ramses Online](https://ramses.ulg.ac.be/) | 网页语料，部分功能可能需账户 | 新王国与拉美西斯时期文本、词法和变体 | 注册访问不等于可抓取；批量研究需按项目说明或联系项目 |
| [UCLA Encyclopedia of Egyptology](https://uee.ucla.edu/) | 同行评议开放条目与 PDF | 神祇、地方神学、年代与研究史 | 属于学术二级来源，不代替铭文或对象记录；每篇按其许可引用 |
| [Papyri.info](https://papyri.info/) / [IDP data](https://github.com/papyri/idp.data) | 网页、稳定 ID、EpiDoc/TEI 数据 | 晚期埃及和希腊罗马埃及纸草文本 | 逐仓库 LICENSE 与记录 provenance 处理；馆藏图像通常另行授权 |
| [Digital Giza](https://giza.fas.harvard.edu/) | 数据库、对象页、档案与出版物 | 墓葬、人物、对象、发掘记录和图像语境 | 照片、档案和出版物权利不同，逐项记录 |
| [ISAC Publications](https://isac.uchicago.edu/research/publications) | PDF 和数字出版物 | 发掘报告、铭文、图版与页码 | 免费下载不自动等于允许整卷再分发；查看版权页 |

### 4.11 古代近东来源

| 资源 | 获取方式 | 推荐用途 | 授权与技术边界 |
|---|---|---|---|
| [ORACC](http://oracc.museum.upenn.edu/) / [项目代码](https://github.com/oracc/oracc) | 子项目网页、数据包或项目工具 | 楔形文字、转写、词汇、翻译和项目级语料 | 代码或字体的公开声明不能覆盖所有子项目语料与图像；逐子项目核验许可和引用格式 |
| [ETCSL](https://etcsl.orinst.ox.ac.uk/) | 网页文本与编号 | 苏美尔文学转写与英译的研究入口 | 现代译文和数据库权利按站点说明处理；默认链接和短引，不整库镜像 |
| [CDLI](https://cdli.mpiwg-berlin.mpg.de/) | 对象目录、图像和文本记录 | 泥板对象号、馆藏、年代、图像与转写互证 | 数据与图像权利逐对象核验；正式采集前确认当前 API 或下载政策 |

### 4.12 第二期传统的机构级入口

| 传统 | 机构级入口 | 推荐用途 | 使用边界 |
|---|---|---|---|
| 凯尔特 | [CELT: Corpus of Electronic Texts, University College Cork](https://celt.ucc.ie/)；[Dúchas.ie](https://www.duchas.ie/) | 爱尔兰中世纪文本、历史文献与民俗采录的发现和定位 | CELT 中每个版本、转写和译文分别核许可；Dúchas 的手稿、转录、图片和社群材料按单项权利与使用条款处理 |
| 日本 | [日本国立国会图书馆数字馆藏](https://dl.ndl.go.jp/)；[国文学研究资料馆国书数据库](https://kokusho.nijl.ac.jp/) | 《古事记》《日本书纪》《风土记》旧版、古典籍书目、版本与数字影像 | 原书公版不自动覆盖现代元数据、扫描与校勘；保存书目 ID、版本、页码和单项权利，不默认批量镜像 |
| 伊朗与祆教 | [Avestan Digital Archive, Freie Universität Berlin](https://ada.geschkult.fu-berlin.de/) | 阿维斯陀手稿影像、书目和具体见证 | 手稿影像、目录和现代转写可能具有不同权利；以项目和持有机构声明为准 |
| 斯拉夫、波罗的与欧洲民俗 | [Europeana APIs](https://pro.europeana.eu/page/apis) 及各国国家图书馆目录 | 手稿、旧版文献、民俗录音与图像发现 | 聚合元数据不能代替原机构许可；重要文本需回到具体馆藏、版本和采录记录 |
| 玛雅、阿兹特克与安第斯 | 博物馆馆藏、[Library of Congress](https://www.loc.gov/apis/) 及具体大学研究项目 | 法典、殖民早期记录、碑铭、对象和旧版研究的发现 | 不预设统一接口；现代释读、图像和原住民知识分别核权利与文化协议，缺乏明确机器许可时采用人工登记 |

斯拉夫、波罗的与芬兰—乌戈尔等书面材料分散的传统须严格记录采录年代与重构者，不把现代民族浪漫主义整理本当古代原典。

### 4.13 博物馆与图像来源

| 资源 | 获取方式 | 推荐用途 | 授权边界 |
|---|---|---|---|
| [The Met Collection API](https://metmuseum.github.io/) / [Open Access](https://www.metmuseum.org/hubs/open-access) | 无需 key 的 JSON API | 神祇图像、器物、年代、文化、对象号 | 仅明确标记为 Public Domain/Open Access 的对象图像和相应数据按 CC0 使用；其他对象只存链接和元数据 |
| [Smithsonian Open Access](https://www.si.edu/openaccess) / [API](https://edan.si.edu/openaccess/apidocs/) | 申请 API key、开放对象下载 | 跨文化对象和图像 | 只对明确 Open Access 项使用 CC0；敏感文化材料仍需伦理审查 |
| [British Museum Collection](https://www.britishmuseum.org/collection) | 人工馆藏检索 | 希腊、埃及、近东文物和铭文 | 馆藏网页可见不等于统一开放；文本、图像和商业复用逐对象核验 |

### 4.14 机器获取示例

以下示例只展示官方接口或仓库的调用形态，目标路径按 2.4 的存储映射书写（`<原始材料库>` 为 `.local/raw/` 或仓库外目录，属待决定项①）。运行前仍要检查最新文档、许可、速率和本地网络权限。

Wikidata——先查候选实体，不直接生成事实：

```bash
curl -G 'https://www.wikidata.org/w/api.php' \
  --data-urlencode 'action=wbsearchentities' \
  --data-urlencode 'search=西王母' \
  --data-urlencode 'language=zh' \
  --data-urlencode 'format=json' \
  -H 'User-Agent: MythologyKB/0.1'
```

结果只用于取得候选 QID、别名和外部链接。QID 需人工确认，亲属与演变关系必须另找 raw-material 至 scholarship 角色的来源。正式运行批量请求时，应在 User-Agent 中加入该项目真实可用的联系地址，并遵守 Wikimedia 当前的机器人与请求规范。

Wikisource——获取指定页面的 wikitext：

```bash
curl -G 'https://zh.wikisource.org/w/api.php' \
  --data-urlencode 'action=parse' \
  --data-urlencode 'page=山海經/西山經' \
  --data-urlencode 'prop=wikitext' \
  --data-urlencode 'format=json' \
  -H 'User-Agent: MythologyKB/0.1'
```

入库时同时记录页面 URL、修订 ID、底本说明、页面许可和获取日期。

CBETA——克隆官方 TEI P5 仓库：

```bash
git clone --depth 1 https://github.com/cbeta-org/xml-p5.git <原始材料库>/cbeta-xml-p5
```

克隆后保存当前提交 SHA；正式处理前读取 CBETA 版权页，并排除不在核心 CC BY-NC-SA 许可范围内的类别。

SuttaCentral——取得发布分支：

```bash
git clone --depth 1 --branch published \
  https://github.com/suttacentral/bilara-data.git \
  <原始材料库>/suttacentral-bilara
```

解析时保留 segment ID、文本语言、译者和对应 publication 元数据。

Perseus——取得某个官方语料仓库：

```bash
git clone --depth 1 \
  https://github.com/PerseusDL/canonical-greekLit.git \
  <原始材料库>/perseus-greek
```

仓库内不同作品和版本的许可可能不同，需把 CTS URN、版本元数据和许可一起登记。

The Met——先搜索，再按 objectID 取详情：

```bash
curl -G 'https://collectionapi.metmuseum.org/public/collection/v1/search' \
  --data-urlencode 'q=Osiris' \
  --data-urlencode 'hasImages=true'

curl 'https://collectionapi.metmuseum.org/public/collection/v1/objects/544622'
```

只有当对象详情明确显示公版/开放访问时，才下载并再利用图像。

---

## 5. 采集、整理与校核流水线

### 5.1 总流程

```text
登记来源（sutra-pavilion/sources/catalog/records/）
  → 权利与访问检查
  → 官方 API / 数据包 / 人工下载
  → 原始文件只读保存（.local/ 或仓库外；小型文本入 sutra-pavilion/sources/assets/text/）
  → 记录获取日志（sutra-pavilion/inbox/imports/）、版本、提交 SHA 与哈希
  → 标准化到 .generated/normalized/
  → 人工抽检 OCR、段落和语言
  → 建 Attestation（sutra-pavilion/sources/attestations/）
  → 提取候选条目（人物 / 叙事版本 / 主张 / 母题 / 传统）
  → 人工核验、审核并发布（status: published）
  → 构建与脚本运行质量检查
  → AI 助手仅从合格状态生成引用型回答
```

### 5.2 来源登记

下载之前，先在来源记录（或 `sutra-pavilion/inbox/imports/` 清单）中记录：

- 机构、项目与稳定 URL；
- 作品、版本、编辑者、译者、语言；
- 访问方式：网页、API、Git、数据包、IIIF、纸本或人工扫描；
- 是否需要账户或 API key；
- 速率和缓存要求；
- 原作、校勘、译文、元数据、扫描图和数据库各自的权利；
- 是否允许公开再分发全文或图像；
- 获取日期与复核日期。

如果这些问题尚无答案，允许登记，但不得启动自动批量采集。

### 5.3 原始文件保存

原始文件遵循“只增不改”：

- 下载文件不直接清洗覆盖；
- 每次更新存新版本或记录 Git commit；
- 保留 HTTP 响应头、数据包说明和许可证副本或链接；
- 对文件计算并登记 SHA-256（`shasum -a 256 <file>`）。

标准化后的文本放 `.generated/normalized/`，其中每个段落必须能映射回原始文件和定位。

### 5.4 OCR 与文本修正

扫描件 OCR 必须保留三层：

1. 原始图像或其稳定链接；
2. 未修正 OCR；
3. 人工修正版及差异记录。

不要把 LLM 修正后的文本覆盖原 OCR。古文字、梵文变音符号、希腊文重音、古诺斯字符、藏文和汉文异体字尤其容易被错误规范化。

### 5.5 AI 助手的职责边界

AI 助手（Codex、ZCode 等）可以：

- 根据已有字段生成符合 Schema 的草稿；
- 从已下载语料中找候选名称和段落；
- 比较两个版本并列出差异；
- 检查缺字段、断链、重复身份和许可状态；
- 将 XML/JSON 转为保留定位的中间格式；
- 根据已核验 Claim 生成带引用的研究摘要；
- 建议来源评分（人工确认后生效）。

AI 助手不得自动决定：

- 两个神格是否“其实是同一个”；
- 某故事是否由另一文化直接传播而来；
- 有争议文本的最终年代；
- 现代译文是否属于合理使用或可全文复制；
- 社群限定材料是否适合公开；
- 任何条目的发布（`status: published` 只能由维护者执行）。

### 5.6 版本更新

外部来源更新时：

1. 获取新版本并记录时间、commit 或版本号；
2. 与旧版本做差异比较；
3. 判断定位是否变化；
4. 更新受影响的 Attestation；
5. 重新审查依赖它的 Claim；
6. 不因原文标点变化自动改写所有研究结论。

---

## 6. 检索与 AI 协作

### 6.1 两种检索语境与证据顺序

沿用项目的两阶段 Meta 优先检索（标题/别名 → 摘要/类型/标签/关系 → 检索词 → 正文分块）与两种检索语境：

- **正式知识检索**：只索引同时满足 `status: published` 与 `verification_stage: verified` 的条目，回答必须回到正文和正式引用；
- **研究检索**：可使用来源记录、Attestation 与来源笔记，输出必须提示内容尚未成为正式知识。

两个模式使用不同索引和输出标识，不能静默混合。

证据顺序：回答事实问题时按“条目（含 Claim）→ 结构化引用 → Attestation（具体见证与定位）→ 来源记录（版本与权利）”逐级回溯。正式知识检索只能使用 `verification_stage: verified`；研究检索可依次使用 `verified`、`checked`，`lead` 只能作为待核验线索。`controversy_status: disputed` 必须并列呈现争议。没有证据时明确说知识库未收录，不从常识补写为已证实事实。

### 6.2 检索策略

第一阶段直接使用 `rg`，不预设几百个 Markdown 文件会“无法搜索”（字段名以下例为准，最终以 Schema 定稿为准）：

```bash
# 名称、异名和正文综合搜索
rg -n -i '西王母|Xiwangmu|金母' sutra-pavilion/knowledge sutra-pavilion/sources

# 找到所有 Claim 条目
rg -l '^entry_type: claim$' sutra-pavilion/knowledge

# 找到已核验主张
rg -l '^verification_stage: verified$' sutra-pavilion/knowledge

# 找所有证据中引用某一来源记录的条目
rg -n '<Attestation ULID>' sutra-pavilion/knowledge

# 查找仅允许保留元数据的来源记录（其中包含权利待核验项）
rg -n 'reuse_scope: metadata-only' sutra-pavilion/sources/catalog/records

# 从标准化数据与条目中查同一词
rg -n -i 'Avalokiteśvara|觀自在|觀世音' .generated/normalized sutra-pavilion/knowledge
```

当规模和性能测试表明有必要时，再生成 JSONL 或 SQLite 派生索引（`.generated/` 下）。生成索引必须满足：Markdown 与原始材料仍是真源；索引可一键重建；每行带内部 ULID、路径和最近更新时间；检查重复身份和失效路径；不要求人工同时维护两套事实。

### 6.3 回答格式

建议要求 AI 助手使用下列结构：

```markdown
## 结论

简明回答，并标明适用的时代、地域和版本。

## 证据

1. 主张：……
   - 原始来源：作品、篇卷/页行/对象号
   - 版本或译者：……
   - 库内见证：<Attestation 引用>
   - 置信度：high / medium / low

## 异说与限制

列出其他版本、研究分歧和知识库缺口。
```

### 6.4 提问模板

- 「查找库内西王母的所有 Attestation，按材料年代排序；只归纳这些材料实际支持的形象变化。」
- 「比较《山海经》和《淮南子》中相关宇宙修复叙事；每个差异都链接到具体 Attestation。」
- 「列出观自在、观世音、Avalokiteśvara 的名称形式及其 `translated_as` 关系，并将对象间的 `identified_with`、`developed_from` Claim 分开呈现。」
- 「汇总所有宇宙修复母题的 Episode，区分结构相似与有历史传播证据的关系。」
- 「检查过去 30 天新增条目：列出无引用、权利不明、以及 verified 但无复核记录的文件。」
- 「从已登记且允许机器访问的来源更新某一语料；先给出来源记录、许可、接口和预计写入路径，不修改原始材料旧文件。」
- 「生成古埃及某神的概览，按时期和地方语境分组；现代科普只能作为导航，不作终证。」

### 6.5 Obsidian 与 AI 助手的职责边界

| 工作 | Obsidian | AI 助手 |
|---|---|---|
| 阅读和人工链接 | 强 | 可直接编辑 Markdown |
| 属性表和待办视图 | Bases | 可生成或检查源文件 |
| 关系可视化 | Canvas | 可生成 JSON Canvas 草稿，但事实仍回写条目 |
| 跨格式全文搜索 | 有限 | 可用 `rg`、解析器和脚本搜索 XML/JSON/TXT 与原始材料 |
| 批量质量检查 | 视图辅助 | 更适合运行可重复脚本 |
| 学术判断 | 人工负责 | 提供候选、对比和证据汇总 |

---

## 7. 分阶段建设路线（域级）

### 阶段 A：首期垂直试点

按[中国神话首期建设规格](./2026-08-24-chinese-mythology-first-phase-requirements.md)执行：围绕“女娲补天的不同文本版本”完成一条完整证据链。不进行多传统采样。

**验收**：随机询问任一结论，都能回到具体来源和定位；没有使用模糊“同一实体”字段；每个来源记录有权利信息。

### 阶段 B：来源登记与采集器试运行

- 为首期各知识库选 1–3 个高价值来源；
- 逐个确认访问方式、许可和版本；
- 每个接口先处理少量记录；
- 保存原始响应、日志、提交 SHA 和哈希；
- 检查分段后能否回溯原定位。

**前置条件**：待决定项①（原始材料存储位置）与②（私人或公开）已经明确。

**验收**：出现 403/429 时采集器停止并记录；原始文件未被标准化程序覆盖；每条标准化记录能映射到原始来源。

### 阶段 C：按知识库扩展

每次只扩一个明确范围，例如“《山海经》某版本中的实体与叙事”，而不是“完成中国神话”。推荐批次：

1. 建来源记录目录和版本说明；
2. 建 Attestation；
3. 从见证提取候选条目；
4. 人工消歧；
5. 建必要 Claim；
6. 更新 Tradition 导航与覆盖表；
7. 输出缺口与争议清单。

**验收**：新实体 100% 至少连接一个 Attestation；新 Episode 明确版本；不因别名相同自动合并。

### 阶段 D：比较研究

只有当两个传统各自的证据层达到基本完整度后，才做跨文化比较：

- 建 Motif 操作性定义；
- 确定比较样本和排除标准；
- 分开记录结构相似、类型相似、接触可能和有证据传播；
- 每个历史联系结论建立 Claim；
- 对反证和替代解释留专门章节。

**验收**：相似性结论不会自动被表述为传播或同源；每个传播 Claim 至少有 scholarship 角色的研究来源，重要争议多源互证。

### 阶段 E：规模化检索与自动检查

当直接 `rg` 已不能满足具体性能或统计需求时：

- 生成 JSONL 或 SQLite 派生索引；
- 为字段契约写校验脚本；
- 检查重复身份、失效链接、孤立来源记录、无证据 Claim、许可未知和久未复核；
- 结果写入 `.generated/` 报告产物；
- 为转换与校验脚本建立自动化测试。

**验收**：删除派生索引后可以从 Markdown 重建；重建结果与当前文件数量和身份一致。

### 阶段 F：长期维护与发布

维护周期：

- 每次采集后：检查来源记录、权利、定位和原始材料完整性；
- 每月：检查断链、重复身份、无证据主张和权利不明内容；
- 每季度：复核接口、许可、项目地址和高频使用来源；
- 每年：审查 Tradition 覆盖表、术语、伦理政策和公开发布范围。

如果计划公开（取决于待决定项②）：

- 将私有研究内容与公开发布内容分开处理；
- 默认不发布受限全文和扫描；
- 对 `noncommercial`、`permission-required`、`restricted-cultural` 和因权利未确认而采用 `metadata-only` 的内容逐项处理；
- 生成来源、许可、署名和移除请求说明。

---

## 8. 质量控制、版权与伦理

### 8.1 最小质量指标

| 指标 | 建议门槛 |
|---|---|
| Claim 具有 Attestation 引用 | 100% |
| Attestation 具有精确篇卷/页行/对象号 | 试点期 100%；规模化后抽检不低于 95% |
| 来源记录具有权利信息 | 100% |
| `verification_stage: verified` 条目的当前提交通过 CI 证据链与契约校验 | 100% |
| 同名对象误合并抽检 | 发现即拆分并记录重定向 |
| 权利不明内容进入公开发布 | 0 |
| `status: published` 条目的当前提交通过 CI | 100% |

### 8.2 CI 自动检查清单

push 与 pull request 触发的 CI 自动检查：

- ULID 是否重复；
- `entry_type` 是否在受控注册表；
- 同名字段是否出现不同类型；
- Claim 是否缺证据引用；
- Attestation 是否缺精确定位；
- 实体/Episode 是否没有任何 Attestation；
- 来源记录是否缺机构、版本、URL、获取日期或权利；
- 权利不明内容是否被引用到公开稿；
- 内部引用是否失效；
- 外部 URL 是否长期不可达；
- 受限文化材料是否缺 `community_protocol`。

CI 使用仓库内同一套 Ruff、行为测试和 `sutra validate .`，检查结果与具体提交关联。不得把 CODEOWNER、指定审核者、人工平台批准或向 AI Agent 授予 GitHub 审核/仓库规则权限设为知识发布条件；本地运行同类命令只用于可选诊断，不作为完成门禁或验收证据。

### 8.3 版权判断原则

分别判断以下对象：

1. 古代原作；
2. 现代标点、校勘和编排；
3. 现代译文；
4. 数据库的结构和标注；
5. 扫描图像或摄影作品；
6. 元数据；
7. 网站服务和 API 条款。

“原作公版”只解决第一项，不能自动推导后六项。

### 8.4 默认安全策略

- 明确可再分发：按许可保存并履行条件；
- 限非商业：只进入私有研究层，并标记 `noncommercial`；
- 仅可人工阅读：保存书目、定位、短引和回链；
- 权利不明：保存元数据，不保存全文或高清图；
- 社群限制：法律许可不能覆盖文化协议，按更严格限制处理；
- 登录、付费或机构订阅内容：不得自动批量抓取或共享凭证。

### 8.5 学术诚实

- 明确区分原文、工作译文、他人译文和模型生成摘要；
- 不伪造页码、诗节号、对象号或引用；
- 无法访问原文时，写明使用的是二手引文；
- 研究观点标明提出者和出版信息；
- 争议问题并列可靠观点，避免把模型偏好写成定论；
- 每次“同源”“演变”“融合”判断都说明证据类型和置信度。

---

## 9. 开放决策与后续修订

### 9.1 待用户决定事项

| 编号 | 事项 | 影响范围 | 默认候选 |
|---|---|---|---|
| ① | 大型原始材料的存储位置 | 阻塞阶段 B 批量采集；不阻塞首期试点（试点小型文本可入 `sutra-pavilion/sources/assets/text/`） | `.local/`（`.gitignore` 已约定），或仓库外目录 + 备份策略 |
| ② | 项目定位：纯私人研究或未来可能公开 | 条目发布许可、权利核验强度、阶段 F 发布流程 | 未知，须用户明确 |

### 9.2 待本规范批准后需同步的设计与实现

以下变更均属实现前的设计与计划工作，须在本规范获用户批准后再编写执行计划；不得把本清单视为当前 CLI 已有能力：

1. [项目结构设计](../docs/design/project-structure.md)、README 与领域文档：保持“项目根 + `contracts/`、内容 Vault 为 `sutra-pavilion/`”的现行边界；补充神话对象的目标路径，并把项目结构设计 §3.3、§6.4、§7 及领域术语中的“条目直引来源记录”同步改为“条目引用 Attestation、Attestation 归属来源记录”，不恢复根 Vault 或旧 `knowledge/`、`sources/` 路径。
2. [ADR-0002](../docs/adr/0002-separate-source-context-and-trust-boundary.md)：以新 ADR 取代其“知识条目直引来源记录”的现行决策，明确 Attestation 是知识与来源上下文之间唯一的引用原子；目录、Schema、扫描和校验必须与该 ADR 同步落地。
3. 来源侧契约：新增 Attestation Schema、`sutra-pavilion/sources/attestations/` 扫描规则、`source_record_id` 完整性校验、对应模板，以及将知识条目与 Claim 的结构化引用从来源记录原子切换为 Attestation 原子；旧直引语法不得与新模型并存。
4. 知识侧契约：新增 `tradition`、`episode`、`motif`、`claim` 条目类型、其 Schema 与受控关系；仅对知识条目按目录校验归属；新增以 `name_forms` 为真源、`aliases` 为派生投影的校验，`translated_as` 只作为名称内部关系，跨对象解释关系只由 Claim 承载。
5. 状态与发布流程：新增 `verification_stage`、`controversy_status` 及 `published ∧ verified` 的正式检索过滤；push 与 pull request 由 GitHub Actions 自动执行 Ruff、行为测试和 `sutra validate .`，不配置 CODEOWNER、指定审核者或人工平台审批门禁，也不要求 AI Agent 获得 GitHub 审核或仓库规则权限。
6. 权利与模板：统一来源 `reuse_scope` 的默认值为 `metadata-only`，不提供 `unknown` 取值；把 `link-quote` 的许可依据、短引范围和 Attestation 继承规则写入来源与 Attestation Schema、模板和校验。
7. 测试与验收：新增 Attestation 扫描、Schema、模板、引用链、正式检索过滤、知识条目目录唯一归属、名称真源与端点、权利默认值的正反行为测试；至少证明 `checked` 不进入正式检索、`reuse_scope: unknown` 校验失败、名称投影或 `translated_as` 端点不一致时校验失败。验收抽查一条 `published ∧ verified` 内容，确认其能回溯到 Attestation 和来源记录，且对应提交的 GitHub Actions 检查通过。

---

## 10. 附录

### 附录 A：实体子类型词表（`entity_kind` 候选值）

```text
deity              神祇
hero               英雄或传奇人物
historical-person  被宗教化/神话化的历史人物
ancestor           祖先或始祖
spirit             精灵、鬼神或地方灵体
monster            怪物或异类
group              神群、族群或集体角色
place              地点、世界或宇宙区域
object             器物、武器、法宝或圣物
concept            宇宙论、灵魂观、位阶或抽象概念
```

### 附录 B：初始母题词表（slug 候选）

母题必须有操作性定义，下列只作为首批候选（slug 承担原语义 ID 的可读键角色）：

```text
creation             创世
anthropogony         造人/人类起源
divine-succession    神代更替
cosmic-body          身体化生宇宙
flood                洪水
apocalypse-renewal   毁灭与重生
cosmic-tree          世界树/宇宙树
cosmic-mountain      宇宙山
underworld           冥界之旅
solar-conflict       太阳异常与冲突
dragon-slaying       屠龙/斗蛇
theft-of-fire        盗火或盗取神物
divine-birth         神异诞生
transformation       变形
dismemberment        肢解与再构
sacred-kingship      神圣王权
cosmic-repair        宇宙修复
descent              神灵下降/化身
ritual-combat        仪式性争斗
```

对齐 Thompson、ATU 或区域性母题索引时记录具体版本和编号。相同母题标签只表示分析上的可比性，不表示历史同源。

### 附录 C：单个来源启用前检查

- [ ] 来源由哪家机构或项目负责？
- [ ] 是否有官方 API、导出、Git、IIIF 或数据包？
- [ ] 网页抓取是否被 ToS、robots 或 API 文档禁止？
- [ ] 原作、校勘、译文、元数据、扫描和图片分别是什么权利？
- [ ] 集合级政策和单项 rights 是否一致？
- [ ] 是否要求账户、API key、署名、非商业或相同方式分享？
- [ ] 是否有速率、User-Agent、缓存和重试要求？
- [ ] 是否存在社群、神圣或隐私限制？
- [ ] 能否保存稳定 ID、定位、版本和获取日期？
- [ ] 采集失败时是否会停止，而不是绕过限制？

### 附录 D：需要定期复核的事项

以下内容容易变化，不应写成永久事实：

- 数据库地址、仓库名、分支名和接口端点；
- API key、速率和批量导出政策；
- 具体文本、译文和图像的许可；
- BDRC/BUDA、SAT、GRETIL、Menota、TLA、ORACC 等项目的机器访问能力；
- Obsidian Bases 语法和性能特征；
- AI 助手权限配置和不同客户端的能力边界。

来源记录必须记录实际复核日期；不得把一次核验表述为“已永久核实”。

---

## 结语

本域的核心不是条目数量，而是可追溯性：

> 每个故事属于某个版本；每个版本来自某个来源记录；每个结论由具体见证支持；每种关系都有适用范围和置信度。

执行计划在本规范与首期建设规格获得用户批准后，建于 `specs/plans/<topic>/`；领域基础计划与中国神话首期计划均已执行完毕，其文件与执行记录已于 2026-08-27 按用户指示移除，后续新计划按本节规则重建。
