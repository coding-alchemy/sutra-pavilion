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
        "language": "zh-CN",
        "status": "available",
    }
    fm.update(overrides)
    return fm


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


def fill_template(template_rel: str, values: dict[str, str]) -> str:
    """读取仓库模板并替换占位项，返回可直接写入对象文件的内容。"""
    text = (REPO_ROOT / template_rel).read_text(encoding="utf-8")
    for placeholder, value in values.items():
        assert placeholder in text, f"模板 {template_rel} 中不存在占位项 {placeholder}"
        text = text.replace(placeholder, value)
    return text


def output_of(proc):
    return proc.stdout + proc.stderr
