"""Ticket 02：Attestation 证据链与结构化引用校验的公开 CLI 行为。"""

from conftest import (
    ATTESTATION_ULID,
    DOMAIN_ULID,
    ENTRY2_ULID,
    FAMILY_ULID,
    NOTE_ULID,
    RECORD2_ULID,
    RECORD_ULID,
    attestation_front_matter,
    build_repo,
    citation,
    entry_front_matter,
    output_of,
    record_front_matter,
    run_cli,
    write_attestation,
    write_minimal_knowledge_repo,
    write_minimal_source_repo,
    write_object,
    write_raw,
)

ENTRY_REL = "sutra-pavilion/knowledge/domains/literature/libraries/chinese-mythology/entries/nuwa.md"
ENTRY2_REL = "sutra-pavilion/knowledge/domains/literature/libraries/chinese-mythology/entries/shanjing.md"
ATTESTATION_REL = f"sutra-pavilion/sources/attestations/{ATTESTATION_ULID}.md"


def write_evidence_chain(repo, body=None):
    """写入合法最小证据链：来源记录 + Attestation + 引用它的知识条目。"""
    write_minimal_knowledge_repo(repo)
    write_minimal_source_repo(repo)
    write_attestation(repo)
    body = body if body is not None else f"女娲补天的叙事见后世文献。{citation()}"
    return write_object(repo, ENTRY_REL, entry_front_matter(), body=body)


def test_citation_to_existing_attestation_passes(tmp_path):
    repo = build_repo(tmp_path)
    write_evidence_chain(repo)
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)
    assert "来源对象：4" in proc.stdout


def test_citation_roles_and_argument_order_pass(tmp_path):
    repo = build_repo(tmp_path)
    write_evidence_chain(repo, (
        f"直接支持。{citation(role='support', strength=1)} "
        f"语境补充。[@{ATTESTATION_ULID}; strength=3; role=context] "
        f"反证。{citation(role='counterevidence', strength=2)}"
    ))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)


def test_attribution_only_citation_without_attestation_fails(tmp_path):
    """只有来源记录时，新语法引用会失败：条目只能引用 Attestation。"""
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_minimal_source_repo(repo)
    write_object(repo, ENTRY_REL, entry_front_matter(), body=citation())
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "CITATION_TARGET_MISSING" in out
    assert ENTRY_REL in out


def test_legacy_record_citation_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_evidence_chain(repo, f"旧语法。[@{RECORD_ULID}, 卷三]")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "CITATION_LEGACY_FORMAT" in out
    assert ENTRY_REL in out


def test_citation_to_record_is_wrong_kind(tmp_path):
    repo = build_repo(tmp_path)
    write_evidence_chain(repo, citation(RECORD_ULID))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "CITATION_TARGET_NOT_ATTESTATION" in output_of(proc)


def test_citation_to_family_note_or_knowledge_object_is_wrong_kind(tmp_path):
    for index, target in enumerate((FAMILY_ULID, NOTE_ULID, DOMAIN_ULID)):
        repo = build_repo(tmp_path, name=f"wrong-kind-{index}")
        write_evidence_chain(repo, citation(target))
        proc = run_cli("validate", str(repo))
        assert proc.returncode == 1
        assert "CITATION_TARGET_NOT_ATTESTATION" in output_of(proc)


def test_malformed_citation_ulid_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_evidence_chain(repo, citation("山海经"))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "CITATION_MALFORMED" in output_of(proc)


def test_citation_missing_arguments_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_evidence_chain(repo, f"叙事。[@{ATTESTATION_ULID}]")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "CITATION_MALFORMED" in output_of(proc)


def test_citation_with_extra_argument_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_evidence_chain(repo, f"叙事。[@{ATTESTATION_ULID}; role=support; strength=5; note=x]")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "CITATION_MALFORMED" in output_of(proc)


def test_invalid_citation_role_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_evidence_chain(repo, citation(role="evidence"))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "CITATION_ARGUMENT_INVALID" in out
    assert "role" in out


def test_invalid_citation_strength_fails(tmp_path):
    for index, strength in enumerate(("0", "6", "high")):
        repo = build_repo(tmp_path, name=f"bad-strength-{index}")
        write_evidence_chain(repo, citation(strength=strength))
        proc = run_cli("validate", str(repo))
        assert proc.returncode == 1
        out = output_of(proc)
        assert "CITATION_ARGUMENT_INVALID" in out
        assert "strength" in out


def test_attestation_with_dangling_source_record_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_minimal_source_repo(repo)
    write_attestation(repo, attestation_front_matter(
        source_record_id="01J8G7ZC9PQK3MWD2R5T8VY6ZZ",
    ))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "ATTESTATION_SOURCE_MISSING" in out
    assert ATTESTATION_REL in out


def test_attestation_filename_mismatch_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_minimal_source_repo(repo)
    write_object(
        repo, "sutra-pavilion/sources/attestations/wrong-name.md",
        attestation_front_matter(),
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "ATTESTATION_FILENAME_MISMATCH" in out
    assert "sutra-pavilion/sources/attestations/wrong-name.md" in out


def test_excerpt_forbidden_under_restrictive_reuse_scope(tmp_path):
    for index, scope in enumerate(("metadata-only", "permission-required", "restricted-cultural")):
        repo = build_repo(tmp_path, name=f"forbidden-{index}")
        write_evidence_chain(repo)
        write_object(
            repo, f"sutra-pavilion/sources/catalog/records/{RECORD_ULID}.md",
            record_front_matter(rights={
                "rights_statement": "权利受限。",
                "license_spdx": "",
                "reuse_scope": scope,
                "access_status": "public",
            }),
        )
        write_object(repo, ATTESTATION_REL, attestation_front_matter(excerpt="必要短引。"))
        proc = run_cli("validate", str(repo))
        assert proc.returncode == 1
        out = output_of(proc)
        assert "ATTESTATION_EXCERPT_NOT_ALLOWED" in out
        assert scope in out


def test_excerpt_allowed_permissive_reuse_scope(tmp_path):
    for index, scope in enumerate(("link-quote", "redistributable", "noncommercial")):
        repo = build_repo(tmp_path, name=f"permissive-{index}")
        write_evidence_chain(repo)
        rights = {
            "rights_statement": "允许范围内的短引。",
            "license_spdx": "",
            "reuse_scope": scope,
            "access_status": "public",
            "permission_basis": "来源页权利声明允许范围内使用。",
        }
        if scope == "link-quote":
            rights["excerpt_max_chars"] = 200
        write_object(
            repo, f"sutra-pavilion/sources/catalog/records/{RECORD_ULID}.md",
            record_front_matter(rights=rights),
        )
        write_object(repo, ATTESTATION_REL, attestation_front_matter(excerpt="必要短引。"))
        proc = run_cli("validate", str(repo))
        assert proc.returncode == 0, output_of(proc)


def test_unknown_reuse_scope_fails_in_schema(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_source_repo(repo)
    write_object(
        repo, f"sutra-pavilion/sources/catalog/records/{RECORD_ULID}.md",
        record_front_matter(rights={
            "rights_statement": "权利不明。",
            "license_spdx": "",
            "reuse_scope": "unknown",
            "access_status": "public",
        }),
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "SCHEMA_INVALID" in out
    assert "$.rights.reuse_scope" in out


def test_book_record_without_edition_and_url_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_minimal_source_repo(repo)
    fm = record_front_matter()
    del fm["edition"], fm["publisher"], fm["external_ids"], fm["acquisition"]
    write_object(repo, f"sutra-pavilion/sources/catalog/records/{RECORD_ULID}.md", fm)
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "$.edition" in out
    assert "$.publisher" in out


def test_citations_in_domain_body_are_not_checked(tmp_path):
    """引用只检查知识条目正文，知识域说明不承载结构化引用。"""
    from conftest import domain_front_matter

    repo = build_repo(tmp_path)
    write_evidence_chain(repo)
    write_object(
        repo, "sutra-pavilion/knowledge/domains/literature/_domain.md",
        domain_front_matter(summary="领域说明"),
        body="这里的 [@01J8G7ZC9PQK3MWD2R5T8VY6ZZ, 卷三] 只是示例文字。",
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)


def test_multiple_independent_errors_aggregate_with_total(tmp_path):
    repo = build_repo(tmp_path)
    write_evidence_chain(repo)
    write_object(
        repo, ENTRY2_REL,
        entry_front_matter(id=ENTRY2_ULID, title="山海经", slug="shanjing", entry_type="work"),
        body=(
            f"一条悬空引用。{citation('01J8G7ZC9PQK3MWD2R5T8VY6ZZ')}\n\n"
            f"一条旧语法引用。[@{RECORD2_ULID}, 页 1]"
        ),
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert out.count("CITATION_TARGET_MISSING") == 1
    assert out.count("CITATION_LEGACY_FORMAT") == 1
    assert "错误：2" in out


def test_templates_context_inbox_fixtures_and_generated_not_scanned(tmp_path):
    repo = build_repo(tmp_path)
    write_evidence_chain(repo)
    dangling = citation("01J8G7ZC9PQK3MWD2R5T8VY6ZZ")
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


def test_filled_attestation_template_produces_valid_object(tmp_path):
    from conftest import fill_template

    repo = build_repo(tmp_path)
    write_minimal_source_repo(repo)
    write_raw(
        repo, ATTESTATION_REL,
        fill_template("sutra-pavilion/templates/attestation.md", {
            "<ULID>": ATTESTATION_ULID,
            "<来源记录 ULID>": RECORD_ULID,
            "<见证标题>": "山海经西山经西王母见证",
            "<精确定位：篇卷、页行、诗节、对象号或稳定网页锚点>": "卷二·西山经",
            "<异文、断句、难词或图像说明>": "底本异文与断句说明。",
            "<本见证能支持的结论>": "西王母之名见于西山经",
            "<本见证不能支持的结论>": "西王母图像与职能的演变",
            "<补充说明与上下文>": "示例说明。",
        }),
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)


# ---------- 评审修复：link-quote 许可依据与短引上限 ----------

def test_link_quote_without_permission_basis_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_evidence_chain(repo)
    fm = record_front_matter()
    del fm["rights"]["permission_basis"]
    del fm["rights"]["excerpt_max_chars"]
    write_object(repo, f"sutra-pavilion/sources/catalog/records/{RECORD_ULID}.md", fm)
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "$.rights.permission_basis" in out
    assert "$.rights.excerpt_max_chars" in out


def test_link_quote_excerpt_over_limit_fails(tmp_path):
    repo = build_repo(tmp_path)
    write_evidence_chain(repo)
    write_object(
        repo, f"sutra-pavilion/sources/catalog/records/{RECORD_ULID}.md",
        record_front_matter(rights={
            "rights_statement": "允许范围内的短引。",
            "license_spdx": "",
            "reuse_scope": "link-quote",
            "access_status": "public",
            "permission_basis": "整理本页权利声明允许的短引。",
            "excerpt_max_chars": 5,
        }),
    )
    write_object(repo, ATTESTATION_REL, attestation_front_matter(excerpt="超过五个字符的短引。"))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "ATTESTATION_EXCERPT_SCOPE_EXCEEDED" in out
    assert ATTESTATION_REL in out


def test_link_quote_excerpt_within_limit_passes(tmp_path):
    repo = build_repo(tmp_path)
    write_evidence_chain(repo)
    write_object(repo, ATTESTATION_REL, attestation_front_matter(excerpt="短引。"))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)


def test_redistributable_with_spdx_license_needs_no_permission_basis(tmp_path):
    """redistributable 的权利依据由 rights_statement 与 license_spdx 表达。"""
    repo = build_repo(tmp_path)
    write_evidence_chain(repo)
    write_object(
        repo, f"sutra-pavilion/sources/catalog/records/{RECORD_ULID}.md",
        record_front_matter(rights={
            "rights_statement": "机构声明开放再分发。",
            "license_spdx": "CC-BY-4.0",
            "reuse_scope": "redistributable",
            "access_status": "public",
        }),
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)
