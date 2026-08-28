"""评审修复：仓库快照的不可变契约。

只断言冻结行为本身，不遍历内部结构（Ticket 01 非目标仍生效）。
"""

import dataclasses

import pytest

from conftest import build_repo, write_minimal_myth_library
from sutra_pavilion import repository


def test_snapshot_objects_and_errors_are_frozen(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_myth_library(repo)
    snapshot = repository.load_snapshot(str(repo))
    assert snapshot.knowledge_objects == 2
    with pytest.raises((AttributeError, TypeError)):
        snapshot.objects.clear()  # type: ignore[attr-defined]
    with pytest.raises((AttributeError, TypeError)):
        snapshot.objects.append(None)  # type: ignore[arg-type,union-attr]
    with pytest.raises(dataclasses.FrozenInstanceError):
        snapshot.objects = ()  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        snapshot.errors = ()  # type: ignore[misc]
    # 同一目录的重新加载不受影响，快照内容保持原样
    assert len(snapshot.objects) == 2
    assert repository.load_snapshot(str(repo)).knowledge_objects == 2


def test_snapshot_front_matter_and_registries_are_deep_frozen(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_myth_library(repo)
    snapshot = repository.load_snapshot(str(repo))
    entry = next(o for o in snapshot.objects if o.kind == "library")
    with pytest.raises(TypeError):
        entry.data["title"] = "被污染"
    with pytest.raises(TypeError):
        entry.data.clear()
    with pytest.raises((TypeError, AttributeError)):
        snapshot.schemas.clear()
    with pytest.raises((TypeError, AttributeError)):
        snapshot.registries["entry_types"].add("deity")
    with pytest.raises((TypeError, AttributeError)):
        snapshot.objects[0].data.setdefault("x", 1)
    front_matter = entry.data
    with pytest.raises(TypeError):
        front_matter |= {"polluted": True}
    library_schema = snapshot.schemas["contracts/knowledge/schemas/library.schema.json"]
    with pytest.raises(TypeError):
        library_schema["required"].append("polluted")
    # 冻结不影响读取语义
    assert entry.data.get("title") == "中国神话"
