"""Ticket 01：安装、命令发现与空仓库校验的公开 CLI 行为。"""

from conftest import make_empty_repo, output_of, run_cli


def test_help_returns_zero_and_lists_validate():
    proc = run_cli("--help")
    assert proc.returncode == 0
    assert "validate" in proc.stdout


def test_validate_help_returns_zero():
    proc = run_cli("validate", "--help")
    assert proc.returncode == 0


def test_unknown_command_is_usage_error_with_exit_2():
    proc = run_cli("no-such-command")
    assert proc.returncode == 2


def test_unknown_option_is_usage_error_with_exit_2():
    proc = run_cli("validate", "--no-such-option")
    assert proc.returncode == 2


def test_missing_subcommand_is_usage_error_with_exit_2():
    proc = run_cli()
    assert proc.returncode == 2


def test_empty_repository_passes_with_zero_error_summary(tmp_path):
    repo = make_empty_repo(tmp_path)
    proc = run_cli("validate", str(repo))
    assert proc.returncode == 0, output_of(proc)
    assert "错误：0" in proc.stdout


def test_validate_defaults_to_current_directory(tmp_path):
    repo = make_empty_repo(tmp_path)
    proc = run_cli("validate", cwd=repo)
    assert proc.returncode == 0, output_of(proc)
    assert "错误：0" in proc.stdout


def test_missing_path_is_repository_error_with_exit_1(tmp_path):
    proc = run_cli("validate", str(tmp_path / "no-such-repo"))
    assert proc.returncode == 1
    assert "PATH_MISSING" in output_of(proc)


def test_file_path_is_repository_error_with_exit_1(tmp_path):
    target = tmp_path / "not-a-repo.md"
    target.write_text("无关文件", encoding="utf-8")
    proc = run_cli("validate", str(target))
    assert proc.returncode == 1
    assert "PATH_NOT_DIRECTORY" in output_of(proc)
