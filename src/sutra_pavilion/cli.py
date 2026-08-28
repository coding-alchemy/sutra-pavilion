"""公开 CLI 适配层：参数解析、退出码和输出格式。

退出码约定：0 成功（含零结果）；1 内容或仓库契约错误；2 命令用法错误（argparse 默认）。
"""

import argparse

from sutra_pavilion import search as search_module
from sutra_pavilion import validation

EXIT_OK = 0
EXIT_VALIDATION_FAILED = 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sutra", description="藏经阁内容校验与检索工具")
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
    search_command = subcommands.add_parser(
        "search", help="按字面查询检索知识条目与来源材料"
    )
    search_command.add_argument("query", help="大小写不敏感的字面查询；不解释正则")
    search_command.add_argument(
        "path",
        nargs="?",
        default=".",
        help="待检索的项目根目录，省略时使用当前目录",
    )
    search_command.add_argument(
        "--mode",
        choices=[search_module.FORMAL, search_module.RESEARCH],
        default=search_module.FORMAL,
        help="formal 只检索 published 且 verified 的知识条目（默认）；"
             "research 检索全部条目、来源记录、Attestation 与来源笔记",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "validate":
        return _run_validate(args.path)
    return _run_search(args.query, args.path, args.mode)


def _run_validate(path: str) -> int:
    report = validation.validate(path)
    _print_report(report)
    return EXIT_OK if report.ok else EXIT_VALIDATION_FAILED


def _run_search(query: str, path: str, mode: str) -> int:
    results, errors = search_module.search(query, path, mode)
    if errors:
        for error in errors:
            print(error.format())
        print(f"错误：{len(errors)}")
        print("校验失败：请先修复上述错误再执行检索。")
        return EXIT_VALIDATION_FAILED
    for result in results:
        print(f"{result.rel_path}\t{result.kind}\t{result.status_label}\t{result.title}")
    print(f"结果：{len(results)}")
    return EXIT_OK


def _print_report(report: validation.ValidationReport) -> None:
    for error in report.errors:
        print(error.format())
    print(f"知识对象：{report.knowledge_objects}，来源对象：{report.source_objects}")
    print(f"错误：{len(report.errors)}")
    print("校验通过。" if report.ok else "校验失败：请按上述错误修复内容。")
