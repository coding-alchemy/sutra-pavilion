"""Ticket 03：知识对象校验与知识模板的公开 CLI 行为。"""

from conftest import (
    ENTRY2_ULID,
    ENTRY_ULID,
    build_repo,
    domain_front_matter,
    entry_front_matter,
    fill_template,
    output_of,
    run_cli,
    write_minimal_knowledge_repo,
    write_object,
    write_raw,
)

ENTRY_REL = "sutra-pavilion/knowledge/domains/literature/libraries/chinese-mythology/entries/nuwa.md"


def write_entry(repo, front_matter=None):
    return write_object(repo, ENTRY_REL, front_matter or entry_front_matter())


def test_minimal_knowledge_repository_passes(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)
    assert "知识对象：3" in proc.stdout


def test_missing_front_matter_delimiter_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_raw(repo, ENTRY_REL, "title: 没有分隔符的 Front Matter\n\n正文\n")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "FRONT_MATTER_MISSING" in output_of(proc)
    assert ENTRY_REL in output_of(proc)


def test_unterminated_front_matter_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_raw(repo, ENTRY_REL, "---\nid: 01ARZ3NDEKTSV4RRFFQ69G5FAV\n")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "FRONT_MATTER_MISSING" in output_of(proc)


def test_unparseable_front_matter_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_raw(repo, ENTRY_REL, "---\ntitle: [未闭合\n---\n")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "FRONT_MATTER_UNPARSEABLE" in output_of(proc)
    assert ENTRY_REL in output_of(proc)


def test_non_mapping_front_matter_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_raw(repo, ENTRY_REL, "---\n- 一个\n- 列表\n---\n")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "FRONT_MATTER_NOT_MAPPING" in output_of(proc)


def test_invalid_ulid_fails_with_field_path(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_entry(repo, entry_front_matter(id="not-a-ulid"))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "SCHEMA_INVALID" in out
    assert ENTRY_REL in out
    assert "$.id" in out


def test_missing_required_field_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    fm = entry_front_matter()
    del fm["slug"]
    write_entry(repo, fm)
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "SCHEMA_INVALID" in output_of(proc)
    assert "$.slug" in output_of(proc)


def test_unknown_entry_type_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_entry(repo, entry_front_matter(entry_type="deity"))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "ENTRY_TYPE_UNREGISTERED" in out
    assert ENTRY_REL in out


def test_unknown_relation_type_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_entry(repo, entry_front_matter(relations=[
        {"type": "part_of_series", "target_id": ENTRY2_ULID},
    ]))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "RELATION_TYPE_UNREGISTERED" in output_of(proc)


def test_unregistered_tag_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_entry(repo, entry_front_matter(tags=["chinese-mythology"]))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "TAG_UNREGISTERED" in output_of(proc)


def test_relation_on_domain_uses_registry(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_object(
        repo, "sutra-pavilion/knowledge/domains/literature/_domain.md",
        domain_front_matter(relations=[
            {"type": "unknown_relation", "target_id": ENTRY2_ULID},
        ]),
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "RELATION_TYPE_UNREGISTERED" in output_of(proc)


def test_filled_knowledge_templates_produce_valid_objects(tmp_path):
    repo = build_repo(tmp_path)
    write_raw(
        repo, "sutra-pavilion/knowledge/domains/literature/_domain.md",
        fill_template("sutra-pavilion/templates/knowledge-domain.md", {
            "<ULID>": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
            "<知识域标题>": "文学",
            "<一至三句话概括本知识域的范围>": "文学知识域示例。",
            "<知识域说明正文>": "示例正文。",
        }),
    )
    write_raw(
        repo,
        "sutra-pavilion/knowledge/domains/literature/libraries/chinese-mythology/_library.md",
        fill_template("sutra-pavilion/templates/knowledge-library.md", {
            "<ULID>": "01J8G7ZC9PQK3MWD2R5T8VY6BJ",
            "<知识库标题>": "中国神话",
            "<一至三句话概括本知识库的主题>": "中国神话知识库示例。",
            "<知识库说明正文>": "示例正文。",
        }),
    )
    write_raw(
        repo, ENTRY_REL,
        fill_template("sutra-pavilion/templates/knowledge-entry.md", {
            "<ULID>": ENTRY_ULID,
            "<条目标题>": "女娲",
            "<slug>": "nuwa",
            "<一至三句话摘要>": "中国神话中的创世与造人神祇。",
            "<条目类型>": "figure",
            "<名称形式-id>": "nuwa-zh-hans",
            "<名称使用语境>": "现代规范展示名",
            "<正文内容>": "示例正文。",
        }),
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)
    assert "知识对象：3" in proc.stdout


def test_missing_registry_file_reported_not_mislabeled(tmp_path):
    """注册表文件缺失且有消费者时报告 REGISTRY_FILE_MISSING，不误报合法类型。"""
    repo = tmp_path / "no-registry-repo"
    repo.mkdir()
    write_minimal_knowledge_repo(repo)
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "REGISTRY_FILE_MISSING" in out
    assert "contracts/knowledge/registry/entry-types.yaml" in out
    assert "ENTRY_TYPE_UNREGISTERED" not in out


def test_template_originals_are_not_scanned(tmp_path):
    import shutil

    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    shutil.copytree("sutra-pavilion/templates", repo / "sutra-pavilion/templates")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)


def test_context_docs_and_inbox_are_not_scanned(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_raw(repo, "sutra-pavilion/knowledge/CONTEXT.md", "---\ntitle: 上下文说明\nbroken\n")
    write_raw(repo, "sutra-pavilion/inbox/raw/draft.md", "---\n- 不是映射\n---\n")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)
