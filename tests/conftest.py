"""公开 CLI 测试接缝的共享工具。

所有行为测试都从子进程调用已安装的 `sutra` 命令，只断言退出码与可观察输出。
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

DOMAIN_ULID = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
LIBRARY_ULID = "01J8G7ZC9PQK3MWD2R5T8VY6BJ"
ENTRY_ULID = "01J8G7ZC9PQK3MWD2R5T8VY6BH"
ENTRY2_ULID = "01J8G7ZC9PQK3MWD2R5T8VY6BK"
RECORD_ULID = "01J8G7ZC9PQK3MWD2R5T8VY6C4"
RECORD2_ULID = "01J8G7ZC9PQK3MWD2R5T8VY6C5"
FAMILY_ULID = "01J8G7ZC9PQK3MWD2R5T8VY6C6"
NOTE_ULID = "01J8G7ZC9PQK3MWD2R5T8VY6C7"
ATTESTATION_ULID = "01J8G7ZC9PQK3MWD2R5T8VY6D1"
ATTESTATION2_ULID = "01J8G7ZC9PQK3MWD2R5T8VY6D2"

# 神话研究域 fixture 身份（Crockford Base32，不含 I/L/O/U）
MYTH_DOMAIN_ULID = "01JZMYTHRS0000000000000000"
MYTH_LIBRARY_ULID = "01JZMYTHCN0000000000000000"
MYTH_FIGURE_ULID = "01JZMYTHFG0000000000000000"
MYTH_TRADITION_ULID = "01JZMYTHTR0000000000000000"
MYTH_EPISODE_ULID = "01JZMYTHEP0000000000000000"
MYTH_MOTIF_ULID = "01JZMYTHMTF000000000000000"
MYTH_CLAIM_ULID = "01JZMYTHCK0000000000000000"

MYTH_ENTRIES_DIR = "sutra-pavilion/knowledge/domains/myth-research/libraries/chinese-mythology/entries"


def sutra_command() -> list[str]:
    """返回可执行的公开 CLI 命令。

    优先使用当前解释器所在虚拟环境的 console script，保证与 pytest
    使用同一环境；找不到时回退到 PATH 查找。
    """
    sibling = Path(sys.executable).parent / "sutra"
    if sibling.is_file():
        return [str(sibling)]
    if shutil.which("sutra") is None:
        pytest.fail('未找到已安装的 sutra 命令；请先执行 pip install -e ".[dev]"')
    return ["sutra"]


def run_cli(*args, cwd=None):
    """从子进程运行公开 CLI，返回原始结果对象。"""
    return subprocess.run(
        [*sutra_command(), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def make_empty_repo(tmp_path, name="empty-repo"):
    repo = tmp_path / name
    repo.mkdir()
    return repo


def build_repo(tmp_path, name="fixture-repo"):
    """构建完整最小仓库：复制真实仓库的 Schema 与注册表，再写入对象。"""
    repo = tmp_path / name
    repo.mkdir()
    for sub in ("contracts/knowledge/schemas", "contracts/knowledge/registry",
                "contracts/sources/schemas", "contracts/sources/registry"):
        src = REPO_ROOT / sub
        if src.is_dir():
            shutil.copytree(src, repo / sub, dirs_exist_ok=True)
    return repo


def write_object(repo: Path, rel_path: str, front_matter: dict, body: str = "") -> Path:
    """以 Front Matter + 正文形式写入一个对象文件。"""
    fm = yaml.safe_dump(front_matter, sort_keys=False, allow_unicode=True)
    return write_raw(repo, rel_path, f"---\n{fm}---\n\n{body}\n" if body else f"---\n{fm}---\n")


def write_raw(repo: Path, rel_path: str, content: str) -> Path:
    target = repo / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target


def domain_front_matter(**overrides) -> dict:
    fm = {
        "schema_version": 1,
        "id": DOMAIN_ULID,
        "title": "文学",
        "language": "zh-CN",
    }
    fm.update(overrides)
    return fm


def library_front_matter(**overrides) -> dict:
    fm = {
        "schema_version": 1,
        "id": LIBRARY_ULID,
        "title": "中国神话",
        "language": "zh-CN",
    }
    fm.update(overrides)
    return fm


def entry_front_matter(**overrides) -> dict:
    fm = {
        "schema_version": 1,
        "id": ENTRY_ULID,
        "title": "女娲",
        "slug": "nuwa",
        "entry_type": "figure",
        "language": "zh-CN",
        "status": "draft",
    }
    fm.update(overrides)
    return fm


def record_front_matter(**overrides) -> dict:
    fm = {
        "schema_version": 1,
        "id": RECORD_ULID,
        "title": "山海经校注",
        "source_type": "book",
        "source_role": "critical-edition",
        "access_method": "manual",
        "language": "zh-CN",
        "status": "available",
        "edition": "新编诸子集成",
        "publisher": "中华书局",
        "external_ids": {"url": "https://example.org/shanhaijing"},
        "acquisition": {"acquired_date": "2026-08-24"},
        "rights": {
            "rights_statement": "现代校勘受版权保护；仅登记元数据与短引。",
            "license_spdx": "",
            "reuse_scope": "link-quote",
            "access_status": "public",
            "permission_basis": "整理本页权利声明允许的短引。",
            "excerpt_max_chars": 200,
        },
    }
    fm.update(overrides)
    return fm


def attestation_front_matter(**overrides) -> dict:
    fm = {
        "schema_version": 1,
        "id": ATTESTATION_ULID,
        "title": "山海经西山经西王母见证",
        "source_record_id": RECORD_ULID,
        "language": "zh-CN",
        "locator": "卷二·西山经",
        "evidence_level": "direct",
        "text_note": "底本异文与断句说明。",
        "supports": ["西王母之名见于西山经"],
        "does_not_support": ["西王母图像与职能的演变"],
    }
    fm.update(overrides)
    return fm


def write_attestation(repo: Path, front_matter=None):
    """写入一个 Attestation；文件名默认等于其 ULID。"""
    fm = front_matter or attestation_front_matter()
    return write_object(repo, f"sutra-pavilion/sources/attestations/{fm['id']}.md", fm)


def citation(attestation_id=ATTESTATION_ULID, role="support", strength=5) -> str:
    """构造一条合法的新语法结构化引用正文片段。"""
    return f"[@{attestation_id}; role={role}; strength={strength}]"


def family_front_matter(**overrides) -> dict:
    fm = {
        "schema_version": 1,
        "id": FAMILY_ULID,
        "title": "山海经",
        "language": "zh-CN",
    }
    fm.update(overrides)
    return fm


def note_front_matter(**overrides) -> dict:
    fm = {
        "schema_version": 1,
        "id": NOTE_ULID,
        "source_id": RECORD_ULID,
        "title": "山海经校注阅读笔记",
        "language": "zh-CN",
        "review_status": "unreviewed",
        "created_by": "维护者",
        "created_at": "2026-08-24",
    }
    fm.update(overrides)
    return fm


def write_minimal_source_repo(repo: Path):
    """写入合法最小来源仓库：一个来源族、一个来源记录、一个来源笔记。"""
    write_object(
        repo, f"sutra-pavilion/sources/catalog/families/{FAMILY_ULID}.md",
        family_front_matter(summary="山海经相关版本族。"),
    )
    write_object(
        repo, f"sutra-pavilion/sources/catalog/records/{RECORD_ULID}.md",
        record_front_matter(family_id=FAMILY_ULID),
    )
    write_object(
        repo, f"sutra-pavilion/sources/notes/{RECORD_ULID}/{NOTE_ULID}.md",
        note_front_matter(),
    )


def write_minimal_knowledge_repo(repo: Path):
    """写入合法最小知识仓库：一个知识域、一个知识库、一个知识条目。"""
    write_object(
        repo, "sutra-pavilion/knowledge/domains/literature/_domain.md",
        domain_front_matter(summary="文学知识域。"),
    )
    write_object(
        repo, "sutra-pavilion/knowledge/domains/literature/libraries/chinese-mythology/_library.md",
        library_front_matter(summary="中国神话知识库。"),
    )
    write_object(
        repo,
        "sutra-pavilion/knowledge/domains/literature/libraries/chinese-mythology/entries/nuwa.md",
        entry_front_matter(summary="中国神话中的创世与造人神祇。"),
    )


def write_minimal_myth_library(repo: Path):
    """写入神话研究域与中国神话知识库骨架（不含条目）。"""
    write_object(
        repo, "sutra-pavilion/knowledge/domains/myth-research/_domain.md",
        domain_front_matter(id=MYTH_DOMAIN_ULID, title="神话研究", summary="神话研究知识域。"),
    )
    write_object(
        repo,
        "sutra-pavilion/knowledge/domains/myth-research/libraries/chinese-mythology/_library.md",
        library_front_matter(id=MYTH_LIBRARY_ULID, title="中国神话", summary="中国神话知识库。"),
    )


def myth_entry_front_matter(entry_type="figure", **overrides) -> dict:
    """带神话域公共字段的条目 Front Matter；类型属性按需叠加。"""
    fm = {
        "schema_version": 1,
        "id": MYTH_FIGURE_ULID,
        "title": "女娲",
        "slug": "myth-fixture",
        "entry_type": entry_type,
        "language": "zh-CN",
        "status": "draft",
        "summary": "神话测试条目摘要。",
        "aliases": [],
        "search_terms": ["神话检索词"],
        "verification_stage": "lead",
        "controversy_status": "none",
        "publish_license": "private-use-only",
        "external_ids": {},
        "name_forms": [{
            "id": "nuwa-zh-hans",
            "text": "女娲",
            "language": "zh-CN",
            "script": "Hans",
            "display": True,
            "usage": "现代规范展示名",
            "translated_as": [],
        }],
        "relations": [],
    }
    fm.update(overrides)
    return fm


def write_myth_entry(repo: Path, front_matter, filename=None, body=""):
    """把神话条目写入首期知识库的 entries 目录。"""
    filename = filename or f"{front_matter.get('slug', 'entry')}.md"
    return write_object(repo, f"{MYTH_ENTRIES_DIR}/{filename}", front_matter, body=body)


MYTH_TYPE_ATTRIBUTES = {
    "figure": {
        "external_ids": {},
        "attributes": {
            "entity_kind": "deity",
            "date_label": "先秦至两汉",
            "date_start": -300,
            "date_end": 220,
            "date_certainty": "range",
        },
    },
    "tradition": {
        "attributes": {"scope": "先秦至两汉早期文献语境。"},
    },
    "episode": {
        "attributes": {"version_note": "《淮南子·览冥训》所载版本。"},
        "relations": [
            {"type": "within_tradition", "target_id": MYTH_TRADITION_ULID},
            {"type": "features", "target_id": MYTH_FIGURE_ULID},
            {"type": "instantiates_motif", "target_id": MYTH_MOTIF_ULID},
        ],
    },
    "motif": {
        "attributes": {
            "subtypes": ["天空缺损修复型"],
            "catalog_alignments": [{
                "index_name": "Thompson Motif-Index",
                "version": "6th ed.",
                "identifier": "A1000 系列（示例）",
            }],
        },
    },
    "claim": {
        "attributes": {
            "statement": "补天叙事的两个早期文本版本相互独立。",
            "subject_id": MYTH_EPISODE_ULID,
            "predicate": "developed_from",
            "object_id": MYTH_FIGURE_ULID,
            "confidence": {"score": 3, "reason": "文本层次互见但证据有限。"},
            "scope": "先秦至两汉文献。",
            "attribution": "示例提出者。",
        },
    },
}

MYTH_TYPE_IDS = {
    "figure": MYTH_FIGURE_ULID,
    "tradition": MYTH_TRADITION_ULID,
    "episode": MYTH_EPISODE_ULID,
    "motif": MYTH_MOTIF_ULID,
    "claim": MYTH_CLAIM_ULID,
}

MYTH_TYPE_SLUGS = {
    "figure": "myth-figure",
    "tradition": "myth-tradition",
    "episode": "myth-episode",
    "motif": "myth-motif",
    "claim": "myth-claim",
}


def write_myth_episode_context(repo: Path):
    """写入 episode 三类结构关系所需的最小对象集（Tradition、Motif、Figure、Episode）。"""
    for entry_type in ("tradition", "motif", "figure", "episode"):
        write_typed_myth_entry(repo, entry_type)


MYTH_TYPE_BODIES = {
    "figure": "## 最小定义\n\n所有已列见证都能支持的简要定义。",
    "tradition": "## 范围说明\n\n示例范围。\n\n## 内部分期与争议\n\n示例分期与争议说明。",
    "episode": "## 本版本梗概\n\n示例梗概。",
    "motif": (
        "## 操作性定义\n\n什么情况计入本母体。\n\n"
        "## 排除标准\n\n什么情况不计入。"
    ),
    "claim": (
        "## 主张\n\n示例主张。\n\n## 反证\n\n示例反证。\n\n"
        "## 其他解释\n\n示例其他解释。"
    ),
}


def write_typed_myth_entry(repo: Path, entry_type: str, body=None, **overrides):
    """写入一个指定类型的合法神话条目 fixture。

    episode 与 claim 的最低引用要求（EPISODE_CITATION_MISSING /
    CLAIM_WITHOUT_EVIDENCE）由默认正文的一个 Attestation 引用满足。
    """
    extras = MYTH_TYPE_ATTRIBUTES[entry_type]
    fm = myth_entry_front_matter(
        entry_type=entry_type,
        id=MYTH_TYPE_IDS[entry_type],
        slug=MYTH_TYPE_SLUGS[entry_type],
        **extras,
    )
    fm.update(overrides)
    if body is None:
        body = MYTH_TYPE_BODIES[entry_type]
        if entry_type in ("episode", "claim"):
            body = f"{body}\n\n{citation()}"
    return write_myth_entry(repo, fm, body=body)


def fill_template(template_rel: str, values: dict[str, str]) -> str:
    """读取仓库模板并替换占位项，返回可直接写入对象文件的内容。"""
    text = (REPO_ROOT / template_rel).read_text(encoding="utf-8")
    for placeholder, value in values.items():
        assert placeholder in text, f"模板 {template_rel} 中不存在占位项 {placeholder}"
        text = text.replace(placeholder, value)
    return text


def output_of(proc):
    return proc.stdout + proc.stderr
