"""中国神话首期：真实仓库内容与检索边界的行为验收（Ticket 04/05/07 过程证据）。

首期内容已发布（published ∧ verified，2026-08-27）：正式检索应返回首期条目且
不出现任何来源对象；研究检索额外暴露来源记录与 Attestation 并标记 research-only。
"""

from conftest import REPO_ROOT, output_of, run_cli

ENTRIES = "sutra-pavilion/knowledge/domains/myth-research/libraries/chinese-mythology/entries"


def test_chinese_mythology_homepage_exposes_first_phase_reading_entries():
    homepage = (
        REPO_ROOT
        / "sutra-pavilion/knowledge/domains/myth-research/libraries/chinese-mythology/_library.md"
    ).read_text(encoding="utf-8")

    assert "本骨架不包含内容条目" not in homepage
    for link in (
        "[[entries/nuwa|女娲]]",
        "[[entries/episode-sky-repair-huainanzi|女娲补天（《淮南子·览冥训》版本）]]",
        "[[entries/episode-sky-repair-lunheng|女娲补天（《论衡·谈天篇》版本）]]",
        "[[entries/claim-gonggong-sky-repair-linkage|补天与共工触山的联缀争议]]",
        "[[entries/motif-cosmic-repair|宇宙修复母题]]",
        "[[entries/tradition-cn-early-texts|中国早期文献神话]]",
    ):
        assert link in homepage


def test_myth_research_homepage_links_to_chinese_mythology_library():
    homepage = (
        REPO_ROOT / "sutra-pavilion/knowledge/domains/myth-research/_domain.md"
    ).read_text(encoding="utf-8")

    assert "[[libraries/chinese-mythology/_library|中国神话]]" in homepage


def test_vault_context_map_links_to_readable_chinese_mythology():
    context_map = (REPO_ROOT / "sutra-pavilion/CONTEXT-MAP.md").read_text(encoding="utf-8")

    assert (
        "[[knowledge/domains/myth-research/libraries/chinese-mythology/_library|中国神话]]"
        in context_map
    )


def test_nuwa_entry_links_to_both_story_versions_and_dispute():
    nuwa = (REPO_ROOT / ENTRIES / "nuwa.md").read_text(encoding="utf-8")

    for link in (
        "[[episode-sky-repair-huainanzi|《淮南子·览冥训》补天版本]]",
        "[[episode-sky-repair-lunheng|《论衡·谈天篇》补天版本]]",
        "[[claim-gonggong-sky-repair-linkage|补天与共工触山的联缀争议]]",
    ):
        assert link in nuwa


def test_every_first_phase_entry_links_back_to_library_homepage():
    homepage_link = (
        "[[knowledge/domains/myth-research/libraries/chinese-mythology/_library|中国神话首页]]"
    )

    for entry_file in (REPO_ROOT / ENTRIES).glob("*.md"):
        assert homepage_link in entry_file.read_text(encoding="utf-8"), entry_file.name


def test_real_repository_first_phase_counts():
    proc = run_cli("validate", str(REPO_ROOT))
    assert proc.returncode == 0, output_of(proc)
    assert "知识对象：8" in proc.stdout  # 域/库骨架 2 + 首期条目 6
    assert "来源对象：5" in proc.stdout  # 来源记录 2 + Attestation 3


def test_formal_search_returns_only_published_verified_entries():
    proc = run_cli("search", "女娲", str(REPO_ROOT))
    assert proc.returncode == 0, output_of(proc)
    out = proc.stdout
    lines = [line for line in out.splitlines() if "\t" in line]
    assert len(lines) == 5  # 人物与两个 Episode（标题层）、Claim（检索词层）、Tradition（正文层）
    assert all("published/verified" in line for line in lines)
    assert not any("research-only" in line for line in lines)
    assert "结果：5" in out


def test_research_search_finds_all_first_phase_objects_with_markers():
    proc = run_cli("search", "女娲", str(REPO_ROOT), "--mode", "research")
    assert proc.returncode == 0, output_of(proc)
    out = proc.stdout
    assert f"{ENTRIES}/nuwa.md" in out
    assert f"{ENTRIES}/episode-sky-repair-huainanzi.md" in out
    assert f"{ENTRIES}/episode-sky-repair-lunheng.md" in out
    assert "tradition-cn-early-texts.md" in out  # 研究模式不受状态过滤


def test_exactly_two_episodes_and_one_disputed_claim():
    proc = run_cli("search", "补天", str(REPO_ROOT), "--mode", "research")
    assert proc.returncode == 0, output_of(proc)
    lines = [line for line in proc.stdout.splitlines() if "\t" in line]
    episodes = [line for line in lines if "episode-sky-repair" in line]
    assert len(episodes) == 2, episodes
    assert any("/disputed" in line for line in lines)


def test_attestations_and_records_are_research_only():
    for query, expect_kind in (("儒书", "attestation"), ("论衡校释", "record")):
        proc = run_cli("search", query, str(REPO_ROOT), "--mode", "research")
        assert proc.returncode == 0, output_of(proc)
        assert expect_kind in proc.stdout
        assert "research-only" in proc.stdout
    # 正式模式不出现任何来源对象
    proc = run_cli("search", "儒书", str(REPO_ROOT))
    assert "research-only" not in proc.stdout
    assert "attestation" not in proc.stdout


def test_citations_trace_to_unique_source_records():
    """证据链回溯：条目正文引用 → Attestation → 唯一来源记录。"""
    import re

    entries_dir = REPO_ROOT / ENTRIES
    attestation_ids = set()
    for attestation_file in (REPO_ROOT / "sutra-pavilion/sources/attestations").glob("*.md"):
        text = attestation_file.read_text(encoding="utf-8")
        attestation_ids.add(re.search(r"^id: (\S+)$", text, re.MULTILINE).group(1))
        record_id = re.search(r"^source_record_id: (\S+)$", text, re.MULTILINE).group(1)
        assert (REPO_ROOT / f"sutra-pavilion/sources/catalog/records/{record_id}.md").is_file()
    cited = set()
    for entry_file in entries_dir.glob("*.md"):
        for match in re.finditer(r"\[@(\S+); role=", entry_file.read_text(encoding="utf-8")):
            cited.add(match.group(1))
    assert cited
    assert cited <= attestation_ids  # 所有引用都指向现有 Attestation
