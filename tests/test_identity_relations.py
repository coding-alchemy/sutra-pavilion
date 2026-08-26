"""Ticket 05：全局身份唯一性与知识关系完整性的公开 CLI 行为。"""

from conftest import (
    ENTRY2_ULID,
    ENTRY_ULID,
    RECORD_ULID,
    build_repo,
    domain_front_matter,
    entry_front_matter,
    output_of,
    run_cli,
    write_minimal_knowledge_repo,
    write_minimal_source_repo,
    write_object,
    write_raw,
)

ENTRY_REL = "sutra-pavilion/knowledge/domains/literature/libraries/chinese-mythology/entries/nuwa.md"
ENTRY2_REL = "sutra-pavilion/knowledge/domains/literature/libraries/chinese-mythology/entries/shanjing.md"


def write_entry2(repo, front_matter=None):
    return write_object(repo, ENTRY2_REL, front_matter or entry_front_matter(
        id=ENTRY2_ULID, title="山海经", slug="shanjing", entry_type="work",
    ))


def test_relation_to_existing_entry_passes(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_entry2(repo)
    write_object(repo, ENTRY_REL, entry_front_matter(relations=[
        {"type": "recorded_in", "target_id": ENTRY2_ULID},
    ]))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)


def test_relation_from_domain_to_entry_passes(tmp_path):
    """默认注册表保持既有行为：知识域可以声明指向知识条目的已登记关系。"""
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_object(
        repo, "sutra-pavilion/knowledge/domains/literature/_domain.md",
        domain_front_matter(relations=[{"type": "recorded_in", "target_id": ENTRY_ULID}]),
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)


def test_relation_to_library_target_passes(tmp_path):
    """默认注册表保持既有行为：知识条目可以指向现有知识库。"""
    from conftest import LIBRARY_ULID

    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_object(repo, ENTRY_REL, entry_front_matter(relations=[
        {"type": "influenced", "target_id": LIBRARY_ULID},
    ]))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)


def test_relation_not_applicable_when_registry_narrows_scope(tmp_path):
    """注册表明确收窄适用对象后，不适用的关系组合必须被拒绝。"""
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_raw(
        repo,
        "contracts/knowledge/registry/relation-types.yaml",
        "relation_types:\n"
        "  - name: recorded_in\n"
        "    source_kinds: [entry]\n"
        "    target_kinds: [entry]\n",
    )
    write_object(
        repo, "sutra-pavilion/knowledge/domains/literature/_domain.md",
        domain_front_matter(relations=[{"type": "recorded_in", "target_id": ENTRY_ULID}]),
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "RELATION_NOT_APPLICABLE" in out
    assert "sutra-pavilion/knowledge/domains/literature/_domain.md" in out


def test_dangling_relation_target_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_object(repo, ENTRY_REL, entry_front_matter(relations=[
        {"type": "recorded_in", "target_id": ENTRY2_ULID},
    ]))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "RELATION_TARGET_MISSING" in out
    assert ENTRY_REL in out


def test_relation_targeting_source_object_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_minimal_source_repo(repo)
    write_object(repo, ENTRY_REL, entry_front_matter(relations=[
        {"type": "recorded_in", "target_id": RECORD_ULID},
    ]))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "RELATION_TARGET_MISSING" in output_of(proc)


def test_relation_survives_target_file_rename_and_title_change(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_object(repo, ENTRY_REL, entry_front_matter(relations=[
        {"type": "recorded_in", "target_id": ENTRY2_ULID},
    ]))
    # 目标对象文件名与标题变化，仅 ULID 身份保持
    write_object(
        repo,
        "sutra-pavilion/knowledge/domains/literature/libraries/chinese-mythology/entries/renamed-file.md",
        entry_front_matter(id=ENTRY2_ULID, title="山海经（改名后）", slug="renamed"),
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)


def test_duplicate_ulid_within_knowledge_fails_listing_all_files(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_entry2(repo)
    write_object(repo, ENTRY2_REL, entry_front_matter(id=ENTRY_ULID, slug="shanjing"))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "ID_DUPLICATE" in out
    assert ENTRY_REL in out
    assert ENTRY2_REL in out


def test_duplicate_ulid_within_sources_fails(tmp_path):
    from conftest import record_front_matter

    repo = build_repo(tmp_path)
    write_minimal_source_repo(repo)
    write_object(
        repo, "sutra-pavilion/sources/catalog/records/01J8G7ZC9PQK3MWD2R5T8VY6C5.md",
        record_front_matter(id=RECORD_ULID, title="山海经校注（另一版）"),
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "ID_DUPLICATE" in output_of(proc)


def test_duplicate_ulid_across_contexts_fails(tmp_path):
    from conftest import record_front_matter

    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_minimal_source_repo(repo)
    # 知识条目与来源记录使用同一 ULID
    write_object(
        repo, "sutra-pavilion/sources/catalog/records/01J8G7ZC9PQK3MWD2R5T8VY6C5.md",
        record_front_matter(id=ENTRY_ULID),
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "ID_DUPLICATE" in output_of(proc)


def test_identity_and_relation_errors_aggregate_in_one_run(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_entry2(repo)
    # 一个重复 ULID + 一个悬空关系，均应报告
    write_object(repo, ENTRY2_REL, entry_front_matter(
        id=ENTRY_ULID, slug="shanjing",
        relations=[{"type": "recorded_in", "target_id": "01J8G7ZC9PQK3MWD2R5T8VY6ZZ"}],
    ))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "ID_DUPLICATE" in out
    assert "RELATION_TARGET_MISSING" in out
