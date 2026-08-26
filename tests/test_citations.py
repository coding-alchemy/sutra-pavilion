"""Ticket 06：结构化来源引用校验与错误聚合的公开 CLI 行为。"""

from conftest import (
    DOMAIN_ULID,
    ENTRY2_ULID,
    FAMILY_ULID,
    NOTE_ULID,
    RECORD2_ULID,
    RECORD_ULID,
    build_repo,
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


def write_citing_entry(repo, body):
    return write_object(repo, ENTRY_REL, entry_front_matter(), body=body)


def test_citation_to_existing_record_with_locator_passes(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_minimal_source_repo(repo)
    write_citing_entry(repo, f"女娲补天的叙事见后世文献。[@{RECORD_ULID}, 卷三]")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)


def test_citation_with_comma_in_locator_passes(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_minimal_source_repo(repo)
    write_citing_entry(repo, f"叙事分析。[@{RECORD_ULID}, 卷三, 页 5]")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)


def test_dangling_citation_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_minimal_source_repo(repo)
    write_citing_entry(repo, "[@01J8G7ZC9PQK3MWD2R5T8VY6ZZ, 卷三]")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "CITATION_TARGET_MISSING" in out
    assert ENTRY_REL in out


def test_citation_to_family_is_wrong_kind(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_minimal_source_repo(repo)
    write_citing_entry(repo, f"[@{FAMILY_ULID}, 卷三]")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "CITATION_TARGET_NOT_RECORD" in output_of(proc)


def test_citation_to_note_is_wrong_kind(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_minimal_source_repo(repo)
    write_citing_entry(repo, f"[@{NOTE_ULID}, 段落 2]")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "CITATION_TARGET_NOT_RECORD" in output_of(proc)


def test_citation_to_knowledge_object_is_wrong_kind(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_minimal_source_repo(repo)
    write_citing_entry(repo, f"[@{DOMAIN_ULID}, 卷三]")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "CITATION_TARGET_NOT_RECORD" in output_of(proc)


def test_malformed_citation_ulid_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_minimal_source_repo(repo)
    write_citing_entry(repo, "[@山海经, 卷三]")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "CITATION_MALFORMED" in output_of(proc)


def test_citation_without_locator_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_minimal_source_repo(repo)
    write_citing_entry(repo, f"[@{RECORD_ULID}]")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "CITATION_MALFORMED" in output_of(proc)


def test_citations_in_domain_body_are_not_checked(tmp_path):
    """引用只检查知识条目正文，知识域说明不承载结构化引用。"""
    from conftest import domain_front_matter

    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_object(
        repo, "sutra-pavilion/knowledge/domains/literature/_domain.md",
        domain_front_matter(summary="领域说明"),
        body="这里的 [@01J8G7ZC9PQK3MWD2R5T8VY6ZZ, 卷三] 只是示例文字。",
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)


def test_multiple_independent_errors_aggregate_with_total(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_minimal_source_repo(repo)
    write_citing_entry(repo, "[@01J8G7ZC9PQK3MWD2R5T8VY6ZZ, 卷三]")
    write_object(
        repo, ENTRY2_REL,
        entry_front_matter(id=ENTRY2_ULID, title="山海经", slug="shanjing", entry_type="work"),
        body=f"另一条悬空引用。[@{RECORD2_ULID}, 页 1]",
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert out.count("CITATION_TARGET_MISSING") == 2
    assert "错误：2" in out


def test_templates_context_inbox_fixtures_and_generated_not_scanned(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_minimal_source_repo(repo)
    dangling = "[@01J8G7ZC9PQK3MWD2R5T8VY6ZZ, 卷三]"
    for rel in (
        "sutra-pavilion/templates/knowledge-entry.md",
        "sutra-pavilion/knowledge/CONTEXT.md",
        "sutra-pavilion/inbox/raw/draft.md",
        "sutra-pavilion/inbox/extracted/tmp.md",
        "tests/fixtures/note.md",
        ".generated/idx/index.md",
    ):
        write_raw(repo, rel, f"---\nbroken\n---\n\n{dangling}\n")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)
