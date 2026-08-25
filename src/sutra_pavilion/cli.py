"""公开 CLI 适配层：参数解析、退出码和输出格式。

退出码约定：0 成功；1 内容或仓库契约错误；2 命令用法错误（argparse 默认）。
"""

import argparse

from sutra_pavilion import validation

EXIT_OK = 0
EXIT_VALIDATION_FAILED = 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sutra", description="藏经阁内容校验工具")
    subcommands = parser.add_subparsers(dest="command", required=True)
    validate_command = subcommands.add_parser(
        "validate", help="校验一个藏经阁仓库的基础内容契约"
    )
    validate_command.add_argument(
        "path",
        nargs="?",
        default=".",
        help="待校验的项目根目录，省略时使用当前目录",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return _run_validate(args.path)


def _run_validate(path: str) -> int:
    report = validation.validate(path)
    _print_report(report)
    return EXIT_OK if report.ok else EXIT_VALIDATION_FAILED


def _print_report(report: validation.ValidationReport) -> None:
    for error in report.errors:
        print(error.format())
    print(f"知识对象：{report.knowledge_objects}，来源对象：{report.source_objects}")
    print(f"错误：{len(report.errors)}")
    print("校验通过。" if report.ok else "校验失败：请按上述错误修复内容。")
