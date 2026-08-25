"""内容 Vault 布局边界的公开 CLI 行为。

旧根布局路径不再被当作正式内容扫描；把内容 Vault 目录直接传给
CLI 时返回可操作错误，而不是零对象校验通过的假阳性。
"""

from conftest import (
    build_repo,
    output_of,
    run_cli,
    write_minimal_knowledge_repo,
    write_minimal_source_repo,
    write_raw,
)


def test_old_root_knowledge_layout_is_not_scanned(tmp_path):
    """只存在旧根布局 knowledge/ 路径时，不被误当作新布局内容。"""
    repo = build_repo(tmp_path)
    write_raw(
        repo,
        "knowledge/domains/literature/libraries/chinese-mythology/entries/nuwa.md",
        "---\n- 不是映射\n---\n",
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)
    assert "知识对象：0" in proc.stdout


def test_old_root_sources_layout_is_not_scanned(tmp_path):
    """只存在旧根布局 sources/ 路径时，不被误当作新布局内容。"""
    repo = build_repo(tmp_path)
    write_raw(repo, "sources/catalog/records/broken.md", "---\n- 不是映射\n---\n")
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)
    assert "来源对象：0" in proc.stdout


def test_old_vault_layout_is_not_scanned(tmp_path):
    """旧 vault/ 内容目录不作为新布局的兼容扫描路径。"""
    repo = build_repo(tmp_path)
    write_raw(
        repo,
        "vault/knowledge/domains/literature/libraries/chinese-mythology/entries/nuwa.md",
        "---\n- 不是映射\n---\n",
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)
    assert "知识对象：0" in proc.stdout


def test_content_vault_path_fails_with_actionable_error(tmp_path):
    """直传内容 Vault 目录返回 1 和稳定规则标识，提示改用项目根目录。"""
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_minimal_source_repo(repo)
    write_raw(repo, "sutra-pavilion/CONTEXT-MAP.md", "# 上下文地图\n")
    proc = run_cli("validate", str(repo / "sutra-pavilion"))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "PATH_IS_CONTENT_VAULT" in out
    assert "项目根目录" in out


def test_error_paths_use_content_vault_and_contracts_prefixes(tmp_path):
    """错误路径继续使用项目根目录相对形式，带内容 Vault 与 contracts/ 前缀。"""
    repo = build_repo(tmp_path)
    write_minimal_knowledge_repo(repo)
    write_raw(
        repo,
        "sutra-pavilion/knowledge/domains/literature/libraries/chinese-mythology/entries/nuwa.md",
        "---\nid: not-a-ulid\n---\n",
    )
    (repo / "contracts/knowledge/registry/entry-types.yaml").write_text(
        "entry_types: [unclosed\n", encoding="utf-8"
    )
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 1
    out = output_of(proc)
    assert "contracts/knowledge/registry/entry-types.yaml" in out
    assert "sutra-pavilion/knowledge/domains/literature/libraries/chinese-mythology/entries/nuwa.md" in out
