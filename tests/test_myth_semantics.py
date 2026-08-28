"""Ticket 04：神话域名称、状态、正文、关系与 Claim 语义校验的公开 CLI 行为。"""

from conftest import (
    MYTH_ENTRIES_DIR,
    MYTH_EPISODE_ULID,
    MYTH_FIGURE_ULID,
    MYTH_TRADITION_ULID,
    MYTH_TYPE_ATTRIBUTES,
    build_repo,
    citation,
    myth_entry_front_matter,
    output_of,
    run_cli,
    write_attestation,
    write_minimal_myth_library,
    write_minimal_source_repo,
    write_myth_entry,
    write_myth_episode_context,
    write_typed_myth_entry,
)

FIGURE_REL = f"{MYTH_ENTRIES_DIR}/myth-figure.md"


def build_myth_repo(tmp_path, name="myth-repo"):
    repo = build_repo(tmp_path, name=name)
    write_minimal_myth_library(repo)
    write_minimal_source_repo(repo)
    write_attestation(repo)
    return repo


def figure_extras():
    return MYTH_TYPE_ATTRIBUTES["figure"]


def write_published_figure(repo, body=None, **overrides):
    fm = myth_entry_front_matter(status="published", verification_stage="verified",
                                 **figure_extras())
    fm.update(overrides)
    return write_myth_entry(repo, fm, filename="myth-figure.md",
                            body=body if body is not None else f"定义。{citation()}")


def test_legal_published_verified_figure_passes(tmp_path):
    repo = build_myth_repo(tmp_path)
    write_published_figure(repo)
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)


# ---------- 名称投影 ----------

def test_zero_display_name_form_fails(tmp_path):
    repo = build_myth_repo(tmp_path)
    write_typed_myth_entry(repo, "figure", name_forms=[{
        "id": "nuwa-zh-hans", "text": "女娲", "language": "zh-CN",
        "display": False, "translated_as": [],
    }])
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "NAME_DISPLAY_INVALID" in output_of(proc)


def test_multiple_display_name_forms_fail(tmp_path):
    repo = build_myth_repo(tmp_path)
    write_typed_myth_entry(repo, "figure", name_forms=[
        {"id": "a", "text": "女娲", "language": "zh-CN", "display": True, "translated_as": []},
        {"id": "b", "text": "女娲氏", "language": "zh-CN", "display": True, "translated_as": []},
    ])
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "NAME_DISPLAY_INVALID" in output_of(proc)


def test_display_text_mismatching_title_fails(tmp_path):
    repo = build_myth_repo(tmp_path)
    write_typed_myth_entry(repo, "figure", name_forms=[{
        "id": "a", "text": "女媧", "language": "zh-CN", "display": True, "translated_as": [],
    }])
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "NAME_DISPLAY_INVALID" in output_of(proc)


def test_alias_projection_order_and_dedup(tmp_path):
    repo = build_myth_repo(tmp_path)
    forms = [
        {"id": "a", "text": "女娲", "language": "zh-CN", "display": True, "translated_as": []},
        {"id": "b", "text": "娲皇", "language": "zh-CN", "display": False, "translated_as": []},
        {"id": "c", "text": "女娲氏", "language": "zh-CN", "display": False, "translated_as": []},
        {"id": "d", "text": "娲皇", "language": "zh-Hant", "display": False, "translated_as": []},
    ]
    # 顺序错误
    write_typed_myth_entry(repo, "figure", name_forms=forms, aliases=["女娲氏", "娲皇"])
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "ALIASES_PROJECTION_MISMATCH" in output_of(proc)
    # 合法投影：按序去重
    repo = build_myth_repo(tmp_path, name="alias-ok")
    write_typed_myth_entry(repo, "figure", name_forms=forms, aliases=["娲皇", "女娲氏"])
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)


def test_translated_as_to_other_entry_fails(tmp_path):
    repo = build_myth_repo(tmp_path)
    write_typed_myth_entry(repo, "figure", name_forms=[
        {"id": "a", "text": "女娲", "language": "zh-CN", "display": True,
         "translated_as": ["other-entry-form"]},
    ])
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "NAME_TRANSLATION_TARGET_MISSING" in output_of(proc)


# ---------- 发布状态 ----------

def test_published_without_verified_fails(tmp_path):
    repo = build_myth_repo(tmp_path)
    write_published_figure(repo, verification_stage="checked")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "KNOWLEDGE_STATE_INVALID" in out
    assert FIGURE_REL in out


def test_template_default_state_is_not_formal_knowledge(tmp_path):
    repo = build_myth_repo(tmp_path)
    write_typed_myth_entry(repo, "figure")  # 默认 draft + lead + none
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)


# ---------- 正文章节 ----------

def test_tradition_without_period_section_fails(tmp_path):
    repo = build_myth_repo(tmp_path)
    write_typed_myth_entry(repo, "tradition",
                           body="## 范围\n\n只有范围，缺少分期与争议。")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "ENTRY_BODY_SECTION_MISSING" in out
    assert "内部分期" in out


def test_motif_with_empty_definition_section_fails(tmp_path):
    repo = build_myth_repo(tmp_path)
    write_typed_myth_entry(repo, "motif", body=(
        "## 操作性定义\n\n## 排除标准\n\n什么情况不计入。"
    ))
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "ENTRY_BODY_SECTION_MISSING" in output_of(proc)


# ---------- 引用数量 ----------

def test_published_entry_without_attestation_citation_fails(tmp_path):
    repo = build_myth_repo(tmp_path)
    write_published_figure(repo, body="没有任何引用的定义。")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "PUBLISHED_ENTRY_WITHOUT_ATTESTATION" in output_of(proc)


def test_episode_without_attestation_citation_fails(tmp_path):
    repo = build_myth_repo(tmp_path)
    write_typed_myth_entry(repo, "episode", body="## 本版本梗概\n\n没有任何引用的梗概。")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "EPISODE_CITATION_MISSING" in output_of(proc)


def test_claim_without_evidence_citation_fails(tmp_path):
    repo = build_myth_repo(tmp_path)
    write_typed_myth_entry(repo, "claim", body="## 主张\n\n没有证据引用的主张。")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "CLAIM_WITHOUT_EVIDENCE" in output_of(proc)


# ---------- 结构关系 ----------

def test_within_tradition_from_figure_to_tradition_passes(tmp_path):
    repo = build_myth_repo(tmp_path)
    write_typed_myth_entry(repo, "tradition")
    write_typed_myth_entry(repo, "figure", relations=[
        {"type": "within_tradition", "target_id": MYTH_TRADITION_ULID},
    ])
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)


def test_within_tradition_wrong_source_type_fails(tmp_path):
    repo = build_myth_repo(tmp_path)
    write_typed_myth_entry(repo, "tradition", relations=[
        {"type": "within_tradition", "target_id": MYTH_TRADITION_ULID},
    ])
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "RELATION_ENTRY_TYPE_NOT_APPLICABLE" in output_of(proc)


def test_myth_domain_influenced_relation_fails(tmp_path):
    repo = build_myth_repo(tmp_path)
    write_typed_myth_entry(repo, "figure", relations=[
        {"type": "influenced", "target_id": MYTH_FIGURE_ULID},
    ])
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "RELATION_TYPE_NOT_ALLOWED_IN_DOMAIN" in output_of(proc)



# ---------- Claim ----------

def write_legal_claim(repo, **attribute_overrides):
    attributes = dict(MYTH_TYPE_ATTRIBUTES["claim"]["attributes"])
    attributes.update(attribute_overrides)
    return write_typed_myth_entry(
        repo, "claim", attributes=attributes,
        body=f"证据。{citation()}\n\n## 反证\n\n示例反证。\n\n## 其他解释\n\n示例。",
    )


def test_claim_with_translated_as_predicate_fails(tmp_path):
    repo = build_myth_repo(tmp_path)
    write_myth_episode_context(repo)
    write_legal_claim(repo, predicate="translated_as")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "CLAIM_PREDICATE_UNREGISTERED" in output_of(proc)


def test_claim_with_dangling_endpoint_fails(tmp_path):
    repo = build_myth_repo(tmp_path)
    write_myth_episode_context(repo)
    write_legal_claim(repo, subject_id="01J8G7ZC9PQK3MWD2R5T8VY6ZZ")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "CLAIM_ENDPOINT_INVALID" in output_of(proc)


def test_claim_with_claim_endpoint_fails(tmp_path):
    repo = build_myth_repo(tmp_path)
    write_myth_episode_context(repo)
    from conftest import write_object
    write_object(
        repo, f"{MYTH_ENTRIES_DIR}/claim2.md",
        myth_entry_front_matter(
            entry_type="claim", id="01JZMYTHC20000000000000000", slug="claim2",
            **MYTH_TYPE_ATTRIBUTES["claim"],
        ),
        body=f"证据。{citation()}\n\n## 反证\n\n反证。\n\n## 其他解释\n\n解释。",
    )
    # 主张的 object_id 指向另一个 claim 条目
    write_legal_claim(repo, object_id="01JZMYTHC20000000000000000")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "CLAIM_ENDPOINT_INVALID" in output_of(proc)


def test_claim_with_self_endpoint_fails(tmp_path):
    repo = build_myth_repo(tmp_path)
    write_myth_episode_context(repo)
    write_legal_claim(repo, subject_id=MYTH_EPISODE_ULID, object_id=MYTH_EPISODE_ULID)
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "CLAIM_ENDPOINT_INVALID" in output_of(proc)


def test_legal_claim_with_two_endpoints_passes(tmp_path):
    repo = build_myth_repo(tmp_path)
    write_myth_episode_context(repo)
    write_legal_claim(repo)
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)


# ---------- 聚合 ----------

def test_independent_semantic_errors_aggregate(tmp_path):
    repo = build_myth_repo(tmp_path)
    write_published_figure(repo, verification_stage="checked",
                           body="没有引用。")  # KNOWLEDGE_STATE_INVALID + PUBLISHED_ENTRY_WITHOUT_ATTESTATION
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "KNOWLEDGE_STATE_INVALID" in out
    assert "PUBLISHED_ENTRY_WITHOUT_ATTESTATION" in out


# ---------- 评审修复：域契约缺失 fail-closed 与 Episode 关系 ----------

def test_missing_entry_type_schema_file_fails_closed(tmp_path):
    repo = build_myth_repo(tmp_path)
    write_typed_myth_entry(repo, "episode")
    (repo / "contracts/knowledge/schemas/domains/myth-research/entry-types/episode.schema.json").unlink()
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "SCHEMA_FILE_MISSING" in out
    assert "entry-types/episode.schema.json" in out


def test_missing_domain_common_schema_file_fails_closed(tmp_path):
    repo = build_myth_repo(tmp_path)
    write_typed_myth_entry(repo, "figure")
    (repo / "contracts/knowledge/schemas/domains/myth-research/common.schema.json").unlink()
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "SCHEMA_FILE_MISSING" in out
    assert "common.schema.json" in out


def test_episode_without_all_three_relations_fails(tmp_path):
    repo = build_myth_repo(tmp_path)
    write_myth_episode_context(repo)
    write_typed_myth_entry(repo, "figure")
    write_typed_myth_entry(repo, "episode", relations=[
        {"type": "within_tradition", "target_id": MYTH_TRADITION_ULID},
    ])
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "EPISODE_RELATION_MISSING" in out
    assert "features" in out and "instantiates_motif" in out


def test_episode_with_all_three_relations_passes(tmp_path):
    repo = build_myth_repo(tmp_path)
    write_myth_episode_context(repo)
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)


def test_empty_search_terms_rejected(tmp_path):
    repo = build_myth_repo(tmp_path)
    write_typed_myth_entry(repo, "figure", search_terms=[])
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "SCHEMA_INVALID" in out
    assert "$.search_terms" in out


def test_unapproved_attribute_field_rejected(tmp_path):
    repo = build_myth_repo(tmp_path)
    extras = {"external_ids": {}, "attributes": {
        "entity_kind": "deity",
        "date_label": "先秦至两汉",
        "date_certainty": "range",
        "favorite_color": "青",
    }}
    write_typed_myth_entry(repo, "figure", **extras)
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "$.attributes.favorite_color" in output_of(proc)


# ---------- 第三轮评审：域契约注册表边界 ----------

def test_deleting_whole_domain_schema_directory_fails_closed(tmp_path):
    """删除整个域 Schema 目录仍必须失败：注册表独立于该目录强制契约存在。"""
    repo = build_myth_repo(tmp_path)
    write_typed_myth_entry(repo, "figure")
    import shutil
    shutil.rmtree(repo / "contracts/knowledge/schemas/domains/myth-research")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "SCHEMA_FILE_MISSING" in out
    assert "common.schema.json" in out


def test_myth_domain_reuses_registered_base_entry_type_without_type_schema(tmp_path):
    """设计允许复用 work/place/concept 等既有类型：无专属类型 Schema 仍应通过。"""
    repo = build_myth_repo(tmp_path)
    write_myth_episode_context(repo)
    fm = myth_entry_front_matter(entry_type="work", slug="myth-work", id="01JZMYTHWK0000000000000000")
    write_myth_entry(repo, fm, body="作品说明。")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)


def test_registry_unlisted_type_schema_deletion_fails_but_work_entry_passes(tmp_path):
    """登记类型的 Schema 被删必须失败；未登记类型不受影响。"""
    repo = build_myth_repo(tmp_path)
    write_typed_myth_entry(repo, "episode")
    (repo / "contracts/knowledge/schemas/domains/myth-research/entry-types/episode.schema.json").unlink()
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "SCHEMA_FILE_MISSING" in output_of(proc)


def test_duplicate_domain_contract_is_rejected_instead_of_overriding(tmp_path):
    """同名域配置不得以后项覆盖前项并撤销已登记类型契约。"""
    repo = build_myth_repo(tmp_path)
    write_myth_episode_context(repo)
    registry = repo / "contracts/knowledge/registry/domain-contracts.yaml"
    registry.write_text(
        registry.read_text(encoding="utf-8")
        + "\n  - domain: myth-research\n    entry_types: []\n",
        encoding="utf-8",
    )
    episode_schema = (
        repo
        / "contracts/knowledge/schemas/domains/myth-research/entry-types/episode.schema.json"
    )
    episode_schema.unlink()
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "REGISTRY_INVALID" in output_of(proc)


def test_unregistered_domain_type_schema_is_not_applied(tmp_path):
    """未列入域契约注册表的 work 继续只使用公共条目契约。"""
    repo = build_myth_repo(tmp_path)
    schema = (
        repo
        / "contracts/knowledge/schemas/domains/myth-research/entry-types/work.schema.json"
    )
    schema.write_text(
        '{"type": "object", "required": ["should_not_apply"]}',
        encoding="utf-8",
    )
    fm = myth_entry_front_matter(
        entry_type="work",
        slug="myth-work",
        id="01JZMYTHWK0000000000000000",
    )
    write_myth_entry(repo, fm, body="作品说明。")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)
