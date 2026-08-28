"""Ticket 06：证据链端到端与两种检索模式的集成验收（fixture 明确标注为测试材料，不冒充真实研究内容）。"""

from conftest import (
    ATTESTATION_ULID,
    MYTH_ENTRIES_DIR,
    MYTH_EPISODE_ULID,
    MYTH_TYPE_ATTRIBUTES,
    RECORD_ULID,
    build_repo,
    citation,
    myth_entry_front_matter,
    output_of,
    run_cli,
    write_attestation,
    write_minimal_myth_library,
    write_minimal_source_repo,
    write_myth_entry,
    write_typed_myth_entry,
)

FIGURE_REL = f"{MYTH_ENTRIES_DIR}/myth-figure.md"
ATTESTATION_REL = f"sutra-pavilion/sources/attestations/{ATTESTATION_ULID}.md"
RECORD_REL = f"sutra-pavilion/sources/catalog/records/{RECORD_ULID}.md"


def build_chain_repo(tmp_path, name="e2e-chain-repo"):
    repo = build_repo(tmp_path, name=name)
    write_minimal_myth_library(repo)
    write_minimal_source_repo(repo)
    write_attestation(repo)
    # 已发布且已核验的人物条目：引用 Attestation
    write_typed_myth_entry(repo, "figure", status="published", verification_stage="verified",
                           body=f"最小定义（测试材料）。{citation()}")
    # 草稿叙事版本、正式传统与母题（episode 三类结构关系的目标）
    write_typed_myth_entry(repo, "tradition")
    write_typed_myth_entry(repo, "motif")
    write_typed_myth_entry(repo, "episode", status="draft", verification_stage="lead")
    return repo


def test_full_chain_validates_and_traces_back_to_unique_record(tmp_path):
    repo = build_chain_repo(tmp_path)
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)

    # 回溯：条目正文引用 → Attestation → 唯一来源记录
    entry_text = (repo / FIGURE_REL).read_text(encoding="utf-8")
    assert f"[@{ATTESTATION_ULID}; role=support; strength=5]" in entry_text
    attestation_text = (repo / ATTESTATION_REL).read_text(encoding="utf-8")
    assert ATTESTATION_ULID in attestation_text
    assert RECORD_ULID in attestation_text  # source_record_id
    record_text = (repo / RECORD_REL).read_text(encoding="utf-8")
    assert RECORD_ULID in record_text


def test_formal_search_finds_published_entry_with_dispute_free_label(tmp_path):
    repo = build_chain_repo(tmp_path)
    proc = run_cli("search", "女娲", str(repo))
    assert proc.returncode == 0, output_of(proc)
    out = proc.stdout
    assert FIGURE_REL in out
    assert "published/verified" in out
    assert "结果：1" in out


def test_research_search_exposes_draft_episode_and_source_objects(tmp_path):
    repo = build_chain_repo(tmp_path)
    proc = run_cli("search", "山海经", str(repo), "--mode", "research")
    assert proc.returncode == 0, output_of(proc)
    out = proc.stdout
    assert "attestation" in out
    assert "research-only" in out


def test_legacy_direct_record_reference_is_rejected_end_to_end(tmp_path):
    repo = build_chain_repo(tmp_path)
    write_myth_entry(
        repo,
        myth_entry_front_matter(id=MYTH_EPISODE_ULID, slug="myth-episode",
                                **MYTH_TYPE_ATTRIBUTES["episode"]),
        body=f"旧直引。[@{RECORD_ULID}, 卷三]",
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    assert "CITATION_LEGACY_FORMAT" in output_of(proc)
    proc = run_cli("search", "女娲", str(repo))
    assert proc.returncode == 1
    assert "结果：" not in proc.stdout
