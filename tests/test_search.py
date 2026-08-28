"""Ticket 05：sutra search 正式/研究检索的公开 CLI 行为。"""

from conftest import (
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
)


def build_search_repo(tmp_path, name="search-repo"):
    """构造覆盖三种状态条目与来源对象的可检索仓库。"""
    repo = build_repo(tmp_path, name=name)
    write_minimal_myth_library(repo)
    write_minimal_source_repo(repo)
    write_attestation(repo)
    from conftest import write_raw
    write_raw(repo, "sutra-pavilion/CONTEXT-MAP.md", "# 上下文地图\n")
    return repo


_ENTRY_SEQ = iter(range(1, 99))


def _unique_ulid() -> str:
    return f"01JZSRCH{next(_ENTRY_SEQ):018d}"


def write_status_entry(repo, filename, status, stage, body=None, **overrides):
    fm = myth_entry_front_matter(
        id=_unique_ulid(),
        status=status, verification_stage=stage, **MYTH_TYPE_ATTRIBUTES["figure"],
        **overrides,
    )
    fm["slug"] = filename
    default_body = f"定义。{citation()}" if status == "published" else "草稿正文。"
    return write_myth_entry(repo, fm, filename=f"{filename}.md",
                            body=body if body is not None else default_body)


def test_formal_mode_returns_only_published_verified(tmp_path):
    repo = build_search_repo(tmp_path)
    write_status_entry(repo, "a-draft", "draft", "lead")
    write_status_entry(repo, "b-review", "review", "checked")
    write_status_entry(repo, "c-published", "published", "verified")
    proc = run_cli("search", "女娲", str(repo))
    assert proc.returncode == 0, output_of(proc)
    out = proc.stdout
    assert "c-published" in out
    assert "a-draft" not in out
    assert "b-review" not in out
    assert "结果：1" in out
    assert "published/verified" in out


def test_research_mode_returns_all_statuses_with_markers(tmp_path):
    repo = build_search_repo(tmp_path)
    write_status_entry(repo, "a-draft", "draft", "lead")
    write_status_entry(repo, "b-review", "review", "checked")
    write_status_entry(repo, "c-published", "published", "verified")
    proc = run_cli("search", "女娲", str(repo), "--mode", "research")
    assert proc.returncode == 0, output_of(proc)
    out = proc.stdout
    assert "draft/lead" in out
    assert "review/checked" in out
    assert "published/verified" in out
    assert "结果：3" in out


def test_research_mode_includes_source_objects_excluded_from_formal(tmp_path):
    repo = build_search_repo(tmp_path)
    proc = run_cli("search", "山海经", str(repo), "--mode", "research")
    assert proc.returncode == 0, output_of(proc)
    out = proc.stdout
    assert "record" in out
    assert "research-only/available" in out
    assert "attestation" in out

    proc = run_cli("search", "山海经", str(repo))
    out = proc.stdout
    assert "research-only" not in out
    assert "attestation" not in out


def test_title_alias_ranking_before_summary_terms_and_body(tmp_path):
    repo = build_search_repo(tmp_path)
    # body-only 命中
    write_status_entry(repo, "z-body", "published", "verified",
                       summary="无关摘要。", body=f"正文中提到昆仑。{citation()}")
    # search_terms 命中
    write_status_entry(repo, "y-term", "published", "verified",
                       summary="无关摘要。", search_terms=["昆仑山"],
                       body=f"无关正文。{citation()}")
    # summary 命中
    write_status_entry(repo, "x-summary", "published", "verified",
                       summary="关于昆仑的摘要。", body=f"无关正文。{citation()}")
    # alias 命中
    write_status_entry(repo, "w-alias", "published", "verified",
                       summary="无关摘要。",
                       name_forms=[
                           {"id": "a", "text": "女娲", "language": "zh-CN",
                            "display": True, "translated_as": []},
                           {"id": "b", "text": "昆仑", "language": "zh-CN",
                            "display": False, "translated_as": []},
                       ],
                       aliases=["昆仑"], body=f"无关正文。{citation()}")
    proc = run_cli("search", "昆仑", str(repo))
    assert proc.returncode == 0, output_of(proc)
    lines = [line for line in proc.stdout.splitlines() if "\t" in line]
    order = [line.split("\t")[0].rsplit("/", 1)[-1] for line in lines]
    assert order == ["w-alias.md", "x-summary.md", "y-term.md", "z-body.md"], order


def test_disputed_entries_carry_controversy_marker(tmp_path):
    repo = build_search_repo(tmp_path)
    write_status_entry(repo, "d-published", "published", "verified",
                       controversy_status="disputed")
    proc = run_cli("search", "女娲", str(repo))
    assert proc.returncode == 0, output_of(proc)
    assert "published/verified/disputed" in proc.stdout


def test_plain_aliases_match_in_first_layer_without_name_forms(tmp_path):
    """无 name_forms 的其他域条目，其 aliases 仍在第一层命中（研究模式验证）。"""
    from conftest import entry_front_matter, write_minimal_knowledge_repo

    repo = build_repo(tmp_path, name="alias-lit-repo")
    write_minimal_knowledge_repo(repo)
    from conftest import write_object
    write_object(
        repo,
        "sutra-pavilion/knowledge/domains/literature/libraries/chinese-mythology/entries/alias-only.md",
        entry_front_matter(id=_unique_ulid(), title="补天叙事", slug="alias-only",
                           aliases=["昆仑山"]),
        body="无关正文。",
    )
    proc = run_cli("search", "昆仑山", str(repo), "--mode", "research")
    assert proc.returncode == 0, output_of(proc)
    lines = [line for line in proc.stdout.splitlines() if "\t" in line]
    assert lines and lines[0].split("\t")[0].endswith("alias-only.md")


def test_case_insensitive_literal_match(tmp_path):
    repo = build_search_repo(tmp_path)
    write_status_entry(repo, "c-published", "published", "verified",
                       title="Xiwangmu", name_forms=[
                           {"id": "a", "text": "Xiwangmu", "language": "en",
                            "display": True, "translated_as": []},
                       ])
    proc = run_cli("search", "XIwangmu", str(repo))
    assert proc.returncode == 0, output_of(proc)
    assert "结果：1" in proc.stdout


def test_no_match_returns_zero_results_with_exit_zero(tmp_path):
    repo = build_search_repo(tmp_path)
    proc = run_cli("search", "不存在的词", str(repo))
    assert proc.returncode == 0
    assert "结果：0" in proc.stdout


def test_missing_query_or_bad_mode_is_usage_error(tmp_path):
    repo = build_search_repo(tmp_path)
    assert run_cli("search").returncode == 2
    assert run_cli("search", "x", str(repo), "--mode", "semantic").returncode == 2


def test_repo_with_contract_errors_blocks_search_with_exit_1(tmp_path):
    repo = build_search_repo(tmp_path)
    write_status_entry(repo, "c-published", "published", "verified",
                       body="悬空引用。[@01J8G7ZC9PQK3MWD2R5T8VY6ZZ; role=support; strength=5]")
    proc = run_cli("search", "女娲", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "CITATION_TARGET_MISSING" in out
    assert "结果：" not in out
    assert not [line for line in proc.stdout.splitlines() if "\t" in line]


def test_search_and_validate_share_repository_interpretation(tmp_path):
    """两个命令对项目根、内容 Vault 与缺失路径得出一致结果。"""
    repo = build_search_repo(tmp_path)
    for args in (["validate", str(repo / "sutra-pavilion")],
                 ["search", "女娲", str(repo / "sutra-pavilion")]):
        proc = run_cli(*args)
        assert proc.returncode == 1
        assert "PATH_IS_CONTENT_VAULT" in output_of(proc)
    for args in (["validate", str(tmp_path / "no-such")],
                 ["search", "女娲", str(tmp_path / "no-such")]):
        proc = run_cli(*args)
        assert proc.returncode == 1
        assert "PATH_MISSING" in output_of(proc)


def test_search_defaults_to_current_directory(tmp_path):
    repo = build_search_repo(tmp_path)
    proc = run_cli("search", "女娲", cwd=repo)
    assert proc.returncode == 0, output_of(proc)


def test_domain_and_library_are_never_search_results(tmp_path):
    repo = build_search_repo(tmp_path)
    proc = run_cli("search", "神话", str(repo), "--mode", "research")
    assert proc.returncode == 0, output_of(proc)
    for line in proc.stdout.splitlines():
        if "\t" in line:
            assert "_domain.md" not in line
            assert "_library.md" not in line
