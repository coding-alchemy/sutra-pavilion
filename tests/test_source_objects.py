"""Ticket 04：来源对象校验与来源模板的公开 CLI 行为。"""

import shutil

import pytest

from conftest import (
    FAMILY_ULID,
    NOTE_ULID,
    RECORD_ULID,
    build_repo,
    entry_front_matter,
    fill_template,
    note_front_matter,
    output_of,
    record_front_matter,
    run_cli,
    write_minimal_knowledge_repo,
    write_minimal_source_repo,
    write_object,
    write_raw,
)

FAMILY_REL = f"sutra-pavilion/sources/catalog/families/{FAMILY_ULID}.md"
RECORD_REL = f"sutra-pavilion/sources/catalog/records/{RECORD_ULID}.md"
NOTE_REL = f"sutra-pavilion/sources/notes/{RECORD_ULID}/{NOTE_ULID}.md"


def write_record(repo, front_matter=None):
    return write_object(repo, RECORD_REL, front_matter or record_front_matter())


def test_minimal_source_repository_passes(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_source_repo(repo)
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)
    assert "来源对象：3" in proc.stdout


def test_invalid_front_matter_fails_for_source_objects(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_source_repo(repo)
    write_raw(repo, RECORD_REL, "---\ntitle: [未闭合\n---\n")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "FRONT_MATTER_UNPARSEABLE" in out
    assert RECORD_REL in out


def test_invalid_ulid_fails_for_source_objects(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_source_repo(repo)
    write_record(repo, record_front_matter(id="bad"))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "SCHEMA_INVALID" in out
    assert "$.id" in out


def test_unknown_source_type_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_source_repo(repo)
    write_record(repo, record_front_matter(source_type="manuscript"))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "SOURCE_TYPE_UNREGISTERED" in out
    assert RECORD_REL in out


def test_missing_required_source_field_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_source_repo(repo)
    fm = record_front_matter()
    del fm["title"]
    write_record(repo, fm)
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "$.title" in output_of(proc)


def test_invalid_availability_status_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_source_repo(repo)
    write_record(repo, record_front_matter(status="lost"))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "SCHEMA_INVALID" in output_of(proc)


def test_note_with_dangling_source_id_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_source_repo(repo)
    write_object(
        repo, NOTE_REL,
        note_front_matter(source_id="01J8G7ZC9PQK3MWD2R5T8VY6ZZ"),
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "NOTE_SOURCE_MISSING" in out
    assert NOTE_REL in out


def test_record_with_dangling_family_id_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_source_repo(repo)
    write_record(repo, record_front_matter(family_id="01J8G7ZC9PQK3MWD2R5T8VY6ZZ"))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "RECORD_FAMILY_MISSING" in out
    assert RECORD_REL in out


def test_source_and_knowledge_registries_are_separate(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_source_repo(repo)
    write_minimal_knowledge_repo(repo)
    # 知识条目类型的合法值不能充当来源类型，反之亦然
    write_record(repo, record_front_matter(source_type="figure"))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "SOURCE_TYPE_UNREGISTERED" in output_of(proc)


def test_missing_source_registry_reported_not_mislabeled(tmp_path):
    """source-types 注册表缺失且有来源记录时报告 REGISTRY_FILE_MISSING，不误报合法类型。"""
    repo = tmp_path / "no-registry-source-repo"
    repo.mkdir()
    write_minimal_source_repo(repo)
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "REGISTRY_FILE_MISSING" in out
    assert "contracts/sources/registry/source-types.yaml" in out
    assert "SOURCE_TYPE_UNREGISTERED" not in out


def test_filled_source_templates_produce_valid_objects(tmp_path):
    repo = build_repo(tmp_path)
    write_raw(
        repo, FAMILY_REL,
        fill_template("sutra-pavilion/templates/source-family.md", {
            "<ULID>": FAMILY_ULID,
            "<来源族标题>": "山海经",
            "<一至三句话概括本来源族>": "山海经相关版本族。",
            "<来源族说明正文>": "示例正文。",
        }),
    )
    write_raw(
        repo, RECORD_REL,
        fill_template("sutra-pavilion/templates/source-record.md", {
            "<ULID>": RECORD_ULID,
            "<来源标题>": "山海经校注",
            "<来源类型>": "book",
            "<来源角色>": "critical-edition",
            "<访问方式>": "manual",
            "<版次>": "新编诸子集成",
            "<出版社或机构>": "中华书局",
            "<稳定记录页链接>": "https://example.org/shanhaijing",
            "<获取日期>": "2026-08-24",
            "<权利说明或待核验状态>": "现代校勘受版权保护；仅登记元数据与短引。",
            "<复用范围>": "link-quote",
            "<访问状态>": "public",
            "<许可依据：权利声明的出处或法律依据>": "整理本页权利声明允许的短引。",
            "<短引上限字符数>": "200",
            "<一至三句话概括本来源版本>": "某出版社某版次。",
        }),
    )
    write_raw(
        repo, NOTE_REL,
        fill_template("sutra-pavilion/templates/source-note.md", {
            "<ULID>": NOTE_ULID,
            "<来源记录 ULID>": RECORD_ULID,
            "<笔记标题>": "山海经校注阅读笔记",
            "<创建者>": "维护者",
            "<创建日期>": "2026-08-24",
            "<笔记正文>": "示例笔记正文。",
        }),
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)
    assert "来源对象：3" in proc.stdout


@pytest.mark.parametrize("missing_field", ["created_by", "created_at"])
def test_note_missing_provenance_fields_fails(tmp_path, missing_field):
    """长期笔记缺少创建者或创建时间任一字段即被拒绝（两字段分别保持必填）。"""
    repo = build_repo(tmp_path)
    write_minimal_source_repo(repo)
    fm = note_front_matter()
    del fm[missing_field]
    write_object(repo, NOTE_REL, fm)
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "SCHEMA_INVALID" in out
    assert f"$.{missing_field}" in out


def test_source_templates_are_not_scanned(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_source_repo(repo)
    shutil.copytree("sutra-pavilion/templates", repo / "sutra-pavilion/templates")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)


def test_knowledge_entry_type_not_valid_as_source_type_via_schema(tmp_path):
    """来源与知识对象使用分离的 Schema 入口：来源对象不出现知识字段。"""
    repo = build_repo(tmp_path)
    write_minimal_source_repo(repo)
    write_record(repo, record_front_matter(entry_type="figure"))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "$.entry_type" in output_of(proc)


def test_knowledge_objects_reject_source_fields(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_object(
        repo,
        "sutra-pavilion/knowledge/domains/literature/libraries/chinese-mythology/entries/nuwa.md",
        entry_front_matter(source_type="book"),
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "$.source_type" in output_of(proc)
