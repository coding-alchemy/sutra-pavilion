"""契约文件自检与 YAML 日期归一化的公开 CLI 行为。

即使仓库没有任何正式对象，已存在的 Schema 与注册表文件也必须通过
解析自检；Obsidian 原生写入的不带引号日期不得被误拒。
"""

import shutil

from conftest import (
    RECORD_ULID,
    build_repo,
    output_of,
    record_front_matter,
    run_cli,
    write_minimal_source_repo,
    write_object,
    write_raw,
)

RECORD_REL = f"sutra-pavilion/sources/catalog/records/{RECORD_ULID}.md"


def make_contract_only_repo(tmp_path, name="contract-only-repo"):
    repo = tmp_path / name
    repo.mkdir()
    shutil.copytree("contracts/knowledge/schemas", repo / "contracts/knowledge/schemas")
    shutil.copytree("contracts/knowledge/registry", repo / "contracts/knowledge/registry")
    shutil.copytree("contracts/sources/schemas", repo / "contracts/sources/schemas")
    shutil.copytree("contracts/sources/registry", repo / "contracts/sources/registry")
    return repo


def test_valid_contract_files_with_zero_objects_pass(tmp_path):
    repo = make_contract_only_repo(tmp_path)
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)


def test_corrupt_schema_fails_even_with_zero_objects(tmp_path):
    repo = make_contract_only_repo(tmp_path)
    (repo / "contracts/knowledge/schemas/entry.schema.json").write_text("{ not json", encoding="utf-8")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "SCHEMA_FILE_INVALID" in out
    assert "contracts/knowledge/schemas/entry.schema.json" in out


def test_structurally_invalid_schema_reports_rule_not_traceback(tmp_path):
    repo = make_contract_only_repo(tmp_path)
    (repo / "contracts/knowledge/schemas/entry.schema.json").write_text("[]", encoding="utf-8")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "SCHEMA_FILE_INVALID" in out
    assert "Traceback" not in out
    assert "错误：1" in out


def test_corrupt_registry_fails_even_with_zero_objects(tmp_path):
    repo = make_contract_only_repo(tmp_path)
    (repo / "contracts/knowledge/registry/entry-types.yaml").write_text(
        "entry_types: [unclosed\n", encoding="utf-8"
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "REGISTRY_INVALID" in out
    assert "contracts/knowledge/registry/entry-types.yaml" in out


def test_malformed_relation_type_registry_fails(tmp_path):
    """关系注册表条目缺少适用对象声明时，注册表本身无效。"""
    repo = make_contract_only_repo(tmp_path)
    (repo / "contracts/knowledge/registry/relation-types.yaml").write_text(
        "relation_types:\n  - name: recorded_in\n", encoding="utf-8"
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "REGISTRY_INVALID" in output_of(proc)


def test_registry_with_non_string_item_fails(tmp_path):
    """注册表中的非字符串项（如数字）必须使注册表无效，不得静默忽略。"""
    repo = make_contract_only_repo(tmp_path)
    (repo / "contracts/knowledge/registry/entry-types.yaml").write_text(
        "entry_types:\n  - 123\n", encoding="utf-8"
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "REGISTRY_INVALID" in out
    assert "contracts/knowledge/registry/entry-types.yaml" in out


def test_bare_empty_directory_still_passes(tmp_path):
    repo = tmp_path / "bare-dir"
    repo.mkdir()
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)


def test_unquoted_yaml_dates_are_normalized_not_rejected(tmp_path):
    """Obsidian 原生日期属性写入不带引号的日期标量，必须通过校验。"""
    repo = build_repo(tmp_path)
    write_minimal_source_repo(repo)
    write_raw(
        repo, RECORD_REL,
        "---\n"
        "schema_version: 1\n"
        f"id: {RECORD_ULID}\n"
        "title: 山海经校注\n"
        "source_type: book\n"
        "source_role: critical-edition\n"
        "access_method: manual\n"
        "language: zh-CN\n"
        "status: available\n"
        "published_date: 2022-03-15\n"
        "edition: 新编诸子集成\n"
        "publisher: 中华书局\n"
        "external_ids:\n"
        "  url: https://example.org/shanhaijing\n"
        "acquisition:\n"
        "  acquired_date: 2026-08-24\n"
        "rights:\n"
        "  rights_statement: 现代校勘受版权保护。\n"
        "  license_spdx: \"\"\n"
        "  reuse_scope: link-quote\n"
        "  access_status: public\n"
        "  permission_basis: 整理本页权利声明允许的短引。\n"
        "  excerpt_max_chars: 200\n"
        "traceability:\n"
        "  score: 4\n"
        "  reason: 版本可核验\n"
        "  rated_by: 维护者\n"
        "  rated_at: 2026-08-24\n"
        "---\n",
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)


def test_invalid_date_value_still_fails(tmp_path):
    """归一化只处理真实日期对象；不符合日期模式的普通字符串仍被拒绝。"""
    repo = build_repo(tmp_path)
    write_minimal_source_repo(repo)
    write_object(repo, RECORD_REL, record_front_matter(published_date="2022/03/15"))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "$.published_date" in output_of(proc)
