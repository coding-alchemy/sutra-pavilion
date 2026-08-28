"""检索深层模块：只消费仓库快照的正式/研究两模式字面检索。

不预建 JSONL、SQLite、向量或图索引；匹配优先级为标题/别名 →
摘要/类型/标签/关系 → 检索词 → 正文，同层按项目相对路径稳定排序。
CLI 不生成研究结论，只返回材料与状态标记。
"""

from dataclasses import dataclass

from sutra_pavilion import repository, validation
from sutra_pavilion.repository import ScannedObject

FORMAL = "formal"
RESEARCH = "research"

# 研究模式检索的知识与来源对象类型；来源族、知识域和知识库不进入结果。
RESEARCH_KINDS = {"entry", "record", "attestation", "note"}


@dataclass
class SearchResult:
    """一条检索结果：四列稳定输出（路径、对象类型、状态、标题）与匹配层级。"""

    rel_path: str
    kind: str
    status_label: str
    title: str
    layer: int  # 1 标题/别名，2 摘要/类型/标签/关系，3 检索词，4 正文；只决定排序


def search(query: str, path: str, mode: str = FORMAL):
    """检索项目根目录，返回 (结果列表, 错误列表)。

    仓库存在契约错误（含项目根不可用）时返回空结果与错误列表，
    CLI 必须以退出码 1 结束且不输出结果行。
    """
    snapshot = repository.load_snapshot(path)
    if snapshot.fatal is not None:
        return [], [snapshot.fatal]
    report = validation.validate_snapshot(snapshot)
    if not report.ok:
        return [], list(report.errors)
    needle = query.casefold()
    results = [
        result for obj in snapshot.objects
        if _in_scope(obj, mode)
        for result in [_match(obj, needle)]
        if result is not None
    ]
    results.sort(key=lambda r: (r.layer, r.rel_path))
    return results, []


def _in_scope(obj: ScannedObject, mode: str) -> bool:
    if mode == FORMAL:
        return (
            obj.kind == "entry"
            and obj.data is not None
            and obj.data.get("status") == "published"
            and obj.data.get("verification_stage") == "verified"
        )
    return obj.kind in RESEARCH_KINDS and obj.data is not None


def _match(obj: ScannedObject, needle: str) -> SearchResult | None:
    data = obj.data or {}
    title = data.get("title") if isinstance(data.get("title"), str) else obj.rel_path
    layer = _match_layer(obj, data, needle)
    if layer is None:
        return None
    return SearchResult(
        rel_path=obj.rel_path,
        kind=obj.kind,
        status_label=_status_label(obj, data),
        title=title,
        layer=layer,
    )


def _match_layer(obj: ScannedObject, data: dict, needle: str) -> int | None:
    if _contains(
        needle,
        data.get("title"),
        *_list(data.get("aliases")),
        *_name_form_texts(data),
    ):
        return 1
    if obj.kind == "entry":
        if _contains(
            needle, data.get("summary"), data.get("entry_type"),
            *_list(data.get("tags")),
            *[f"{r.get('type')} {r.get('target_id')}" for r in _relations(data)],
        ):
            return 2
        if _contains(needle, *_list(data.get("search_terms"))):
            return 3
    else:
        if _contains(needle, *_other_front_matter_strings(obj, data)):
            return 2
    if needle in obj.body.casefold():
        return 4
    return None


def _status_label(obj: ScannedObject, data: dict) -> str:
    if obj.kind == "entry":
        stage = data.get("verification_stage") or "-"
        label = f"{data.get('status')}/{stage}"
        if data.get("controversy_status") == "disputed":
            label = f"{label}/disputed"
        return label
    if obj.kind == "record":
        return f"research-only/{data.get('status')}"
    if obj.kind == "attestation":
        return "research-only"
    return f"research-only/{data.get('review_status')}"


def _name_form_texts(data: dict) -> list[str]:
    forms = data.get("name_forms")
    if not isinstance(forms, list):
        return []
    return [f["text"] for f in forms if isinstance(f, dict) and isinstance(f.get("text"), str)]


def _list(value) -> list:
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def _relations(data: dict) -> list[dict]:
    value = data.get("relations")
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


# 非条目对象第二层匹配覆盖除 id、title 之外的全部 Front Matter 字符串值。
_TOP_LEVEL_SKIP = {"id", "title"}


def _other_front_matter_strings(obj: ScannedObject, data: dict) -> list[str]:
    values: list[str] = []

    def walk(value) -> None:
        if isinstance(value, str):
            values.append(value)
        elif isinstance(value, list):
            for item in value:
                walk(item)
        elif isinstance(value, dict):
            for item in value.values():
                walk(item)

    for key, value in data.items():
        if key not in _TOP_LEVEL_SKIP:
            walk(value)
    return values


def _contains(needle: str, *values: object) -> bool:
    return any(
        needle in value.casefold() for value in values if isinstance(value, str)
    )
