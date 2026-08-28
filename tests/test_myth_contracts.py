"""Ticket 03：神话域分层契约、注册表与骨架的公开 CLI 行为。"""

from conftest import (
    MYTH_ENTRIES_DIR,
    MYTH_FIGURE_ULID,
    REPO_ROOT,
    build_repo,
    fill_template,
    myth_entry_front_matter,
    output_of,
    run_cli,
    write_minimal_myth_library,
    write_myth_entry,
    write_raw,
    write_typed_myth_entry,
)

FIGURE_REL = f"{MYTH_ENTRIES_DIR}/myth-figure.md"


def test_real_repository_with_skeletons_and_first_phase_passes():
    """真实仓库：域/库骨架 + 中国神话首期内容（6 条目 + 2 来源 + 3 见证）。"""
    proc = run_cli("validate", str(REPO_ROOT))
    assert proc.returncode == 0, output_of(proc)
    assert "知识对象：8" in proc.stdout
    assert "来源对象：5" in proc.stdout


def test_all_five_myth_entry_types_pass_layered_schemas(tmp_path):
    from conftest import (
        MYTH_CLAIM_ULID,
        MYTH_TYPE_ATTRIBUTES,
        MYTH_TYPE_BODIES,
        MYTH_TYPE_SLUGS,
        attestation_front_matter,
        citation,
        myth_entry_front_matter,
        write_minimal_source_repo,
        write_object,
    )

    repo = build_repo(tmp_path)
    write_minimal_myth_library(repo)
    write_minimal_source_repo(repo)
    write_object(
        repo, f"sutra-pavilion/sources/attestations/{attestation_front_matter()['id']}.md",
        attestation_front_matter(),
    )
    for entry_type in ("figure", "tradition", "episode", "motif"):
        write_typed_myth_entry(repo, entry_type)
    claim_fm = myth_entry_front_matter(
        entry_type="claim", id=MYTH_CLAIM_ULID, slug="myth-claim",
        **MYTH_TYPE_ATTRIBUTES["claim"],
    )
    write_object(
        repo, f"{MYTH_ENTRIES_DIR}/{MYTH_TYPE_SLUGS['claim']}.md", claim_fm,
        body=f"证据综述。{citation()}\n\n{MYTH_TYPE_BODIES['claim']}",
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)
    assert "知识对象：7" in proc.stdout


def test_missing_myth_common_field_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_myth_library(repo)
    fm = myth_entry_front_matter(
        external_ids={},
        attributes={
            "entity_kind": "deity",
            "date_label": "先秦至两汉",
            "date_certainty": "range",
        },
    )
    del fm["search_terms"]
    write_myth_entry(repo, fm)
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "SCHEMA_INVALID" in out
    assert "$.search_terms" in out
    assert "myth-research 域公共 Schema" in out


def test_publish_license_is_fixed_in_myth_domain(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_myth_library(repo)
    write_myth_entry(repo, myth_entry_front_matter(
        publish_license="cc-by-sa",
        external_ids={},
        attributes={
            "entity_kind": "deity",
            "date_label": "先秦至两汉",
            "date_certainty": "range",
        },
    ))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "$.publish_license" in output_of(proc)


def test_figure_type_attribute_contract_enforced(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_myth_library(repo)
    write_myth_entry(repo, myth_entry_front_matter(
        external_ids={},
        attributes={
            "entity_kind": "dragon",
            "date_label": "先秦至两汉",
            "date_start": -300,
            "date_certainty": "range",
        },
    ))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "$.attributes.entity_kind" in out
    assert "$.attributes.date_end" in out


def test_motif_catalog_alignment_requires_versioned_identifier(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_myth_library(repo)
    write_typed_myth_entry(repo, "motif", attributes={
        "subtypes": ["天空缺损修复型"],
        "catalog_alignments": [{"index_name": "Thompson Motif-Index", "identifier": "A1000"}],
    })
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "catalog_alignments" in output_of(proc)


def test_missing_claim_predicate_registry_reported(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_myth_library(repo)
    write_typed_myth_entry(repo, "claim")
    (repo / "contracts/knowledge/registry/claim-predicates.yaml").unlink()
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "REGISTRY_FILE_MISSING" in out
    assert "claim-predicates.yaml" in out


def test_broken_domain_schema_fails_even_with_zero_objects(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_myth_library(repo)
    write_raw(
        repo,
        "contracts/knowledge/schemas/domains/myth-research/entry-types/motif.schema.json",
        "{ not json",
    )
    write_typed_myth_entry(repo, "figure")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "SCHEMA_FILE_INVALID" in out
    assert "domains/myth-research/entry-types/motif.schema.json" in out


def test_literature_entries_do_not_require_myth_fields(tmp_path):
    from conftest import write_minimal_knowledge_repo

    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_minimal_myth_library(repo)
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)


def test_filled_knowledge_entry_template_is_legal_myth_draft(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_myth_library(repo)
    content = fill_template("sutra-pavilion/templates/knowledge-entry.md", {
        "<ULID>": MYTH_FIGURE_ULID,
        "<条目标题>": "女娲",
        "<slug>": "myth-figure",
        "<一至三句话摘要>": "中国神话中的创世与造人神祇。",
        "<条目类型>": "figure",
        "<名称形式-id>": "nuwa-zh-hans",
        "<名称使用语境>": "现代规范展示名",
        "<检索扩展词>": "女娲补天",
        "<实体子类型>": "deity",
        "<时间表述>": "先秦至两汉",
        "<时间确定性>": "range",
        "<正文内容>": "示例正文。",
    })
    write_raw(repo, FIGURE_REL, content)
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)
