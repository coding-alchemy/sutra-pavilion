"""校验深层模块：扫描、解析与全部内容契约检查的唯一实现。

CLI 适配层只处理参数、退出码和输出；本模块封装从项目根目录发现对象、
读取 Front Matter、执行 Schema 与注册表校验以及跨对象一致性检查的全部行为。

扫描范围只包括权威对象目录；上下文说明、模板、收件箱、生成物和测试
fixture 不是正式内容，不参与扫描。
"""

import datetime
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

# 内容 Vault 内权威对象目录的扫描规则：(上下文, 对象类型, 相对项目根目录的 glob)。
SCAN_RULES: list[tuple[str, str, str]] = [
    ("knowledge", "domain", "sutra-pavilion/knowledge/domains/*/_domain.md"),
    ("knowledge", "library", "sutra-pavilion/knowledge/domains/*/libraries/*/_library.md"),
    ("knowledge", "entry", "sutra-pavilion/knowledge/domains/*/libraries/*/entries/*.md"),
    ("sources", "family", "sutra-pavilion/sources/catalog/families/*.md"),
    ("sources", "record", "sutra-pavilion/sources/catalog/records/*.md"),
    ("sources", "note", "sutra-pavilion/sources/notes/*/*.md"),
]

# 对象类型到 Schema 文件的映射，从待校验项目根目录下的 contracts/ 加载。
SCHEMA_FILES: dict[str, str] = {
    "domain": "contracts/knowledge/schemas/domain.schema.json",
    "library": "contracts/knowledge/schemas/library.schema.json",
    "entry": "contracts/knowledge/schemas/entry.schema.json",
    "family": "contracts/sources/schemas/source-family.schema.json",
    "record": "contracts/sources/schemas/source-record.schema.json",
    "note": "contracts/sources/schemas/source-note.schema.json",
}

# 受控注册表：(注册表键, 文件, 顶层字段)。
REGISTRY_FILES: list[tuple[str, str, str]] = [
    ("entry_types", "contracts/knowledge/registry/entry-types.yaml", "entry_types"),
    ("relation_types", "contracts/knowledge/registry/relation-types.yaml", "relation_types"),
    ("source_types", "contracts/sources/registry/source-types.yaml", "source_types"),
]

# 各注册表被消费的对象类型。注册表文件缺失且存在消费者时报告
# REGISTRY_FILE_MISSING，而不是把合法值误报为未登记。
REGISTRY_CONSUMER_KINDS: dict[str, set[str]] = {
    "entry_types": {"entry"},
    "relation_types": {"domain", "library", "entry"},
    "source_types": {"record"},
}

# 关系类型适用对象声明中允许出现的知识对象类型。
RELATION_KINDS = {"domain", "library", "entry"}

TAGS_DIR = "contracts/knowledge/registry/tags"

# 结构化引用形式：[@<来源记录ULID>, <定位信息>]（见项目结构设计 6.4 节）。
CITATION_PATTERN = re.compile(r"\[@([^\[\]]*)\]")
ULID_STRICT_PATTERN = re.compile(r"^[0-9A-HJKMNP-TV-Z]{26}$")


@dataclass
class ValidationError:
    """携带仓库相对路径、稳定规则标识和可操作原因的统一错误结构。"""

    path: str
    rule: str
    reason: str

    def format(self) -> str:
        return f"{self.path}: {self.rule}: {self.reason}"


@dataclass
class ScannedObject:
    """一个被扫描的正式对象；解析失败时 data 为 None。"""

    context: str
    kind: str
    rel_path: str
    data: dict | None
    body: str


@dataclass
class ValidationReport:
    """一次校验运行的可观察结果。"""

    knowledge_objects: int = 0
    source_objects: int = 0
    errors: list[ValidationError] = field(default_factory=list)
    objects: list[ScannedObject] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def validate(path: str) -> ValidationReport:
    """校验给定项目根目录，返回聚合后的报告。"""
    root = Path(path)
    if not root.exists():
        return ValidationReport(errors=[
            ValidationError(path, "PATH_MISSING", f"校验路径不存在：{path}")
        ])
    if not root.is_dir():
        return ValidationReport(errors=[
            ValidationError(path, "PATH_NOT_DIRECTORY", "校验路径必须是项目根目录（目录）")
        ])
    if _looks_like_content_vault(root):
        return ValidationReport(errors=[
            ValidationError(
                path, "PATH_IS_CONTENT_VAULT",
                "校验路径呈现内容 Vault 布局；请改用其项目根目录运行 sutra validate",
            )
        ])
    report = ValidationReport()
    report.objects = _scan_objects(root, report)
    report.knowledge_objects = sum(1 for o in report.objects if o.context == "knowledge")
    report.source_objects = sum(1 for o in report.objects if o.context == "sources")
    _validate_objects(root, report)
    return report


def _looks_like_content_vault(root: Path) -> bool:
    """识别被误传给 CLI 的内容 Vault 目录，避免空扫描被误报为通过。"""
    return (
        (root / "CONTEXT-MAP.md").is_file()
        and (root / "knowledge").is_dir()
        and (root / "sources").is_dir()
        and not (root / "sutra-pavilion").is_dir()
    )


def _scan_objects(root: Path, report: ValidationReport) -> list[ScannedObject]:
    objects: list[ScannedObject] = []
    for context, kind, pattern in SCAN_RULES:
        for path in sorted(root.glob(pattern)):
            rel_path = path.relative_to(root).as_posix()
            data, body, error = _read_front_matter(path, rel_path)
            if error is not None:
                report.errors.append(error)
            objects.append(ScannedObject(context, kind, rel_path, data, body))
    return objects


def _read_front_matter(path: Path, rel_path: str) -> tuple[dict | None, str, ValidationError | None]:
    """读取并解析 Front Matter，返回 (映射, 正文, 错误)。"""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "", ValidationError(
            rel_path, "FRONT_MATTER_MISSING", "文件必须以 Front Matter 起始分隔符 --- 开始"
        )
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return None, "", ValidationError(
            rel_path, "FRONT_MATTER_MISSING", "未找到 Front Matter 结束分隔符 ---"
        )
    front_matter_text = "\n".join(lines[1:end])
    body = "\n".join(lines[end + 1:])
    try:
        data = yaml.safe_load(front_matter_text)
    except yaml.YAMLError as exc:
        return None, body, ValidationError(
            rel_path, "FRONT_MATTER_UNPARSEABLE", f"Front Matter 不是合法 YAML：{_first_line(exc)}"
        )
    if not isinstance(data, dict):
        return None, body, ValidationError(
            rel_path, "FRONT_MATTER_NOT_MAPPING",
            f"Front Matter 顶层必须是键值映射，实际解析结果为 {type(data).__name__}",
        )
    return _normalize_yaml_dates(data), body, None


def _normalize_yaml_dates(value):
    """把 YAML 隐式解析出的 date/datetime 统一为 ISO 字符串。

    Obsidian 原生日期属性写入的是不带引号的日期标量，PyYAML 会解析成
    datetime 对象；Schema 契约以字符串表达日期，因此在校验前归一化。
    """
    if isinstance(value, dict):
        return {key: _normalize_yaml_dates(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_yaml_dates(item) for item in value]
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    return value


def _validate_objects(root: Path, report: ValidationReport) -> None:
    """执行契约自检与全部对象校验。

    即使仓库没有任何正式对象，已存在的 Schema 和注册表文件也会被解析
    自检，保证空内容仓库的 CI 校验不是空操作。
    """
    kinds = {obj.kind for obj in report.objects}
    schemas = _load_schemas(root, kinds, report)
    registries = _load_registries(root, report)
    for key, rel_path, _ in REGISTRY_FILES:
        if registries[key] is None and kinds & REGISTRY_CONSUMER_KINDS[key]:
            report.errors.append(ValidationError(
                rel_path, "REGISTRY_FILE_MISSING",
                f"缺少注册表文件 {rel_path}，无法校验相关受控值",
            ))
    for obj in report.objects:
        if obj.data is None:
            continue
        if obj.context == "knowledge":
            _validate_knowledge_object(obj, schemas, registries, report)
        elif obj.context == "sources":
            _validate_source_object(obj, schemas, registries, report)
    index = _identity_index(report)
    _validate_source_references(index, report)
    _validate_identity_and_relations(index, registries, report)
    _validate_citations(index, report)


def _validate_against_schema(
    obj: ScannedObject,
    schemas: dict[str, Draft202012Validator],
    report: ValidationReport,
) -> None:
    """执行对象 Front Matter 对其类型 Schema 的校验。"""
    validator = schemas.get(obj.kind)
    if validator is None:
        return
    for error in validator.iter_errors(obj.data):
        field_path = _schema_error_field_path(error)
        report.errors.append(ValidationError(
            obj.rel_path, "SCHEMA_INVALID",
            f"字段 {field_path} 不符合 {obj.kind} Schema：{error.message}",
        ))


def _load_schemas(
    root: Path, kinds: set[str], report: ValidationReport
) -> dict[str, Draft202012Validator]:
    """解析并自检仓库中存在的全部 Schema 文件。

    文件存在即解析并做元 Schema 检查（无论是否有对应对象）；文件缺失
    仅在存在该类型对象时报告 SCHEMA_FILE_MISSING。
    """
    schemas: dict[str, Draft202012Validator] = {}
    for kind, rel_path in sorted(SCHEMA_FILES.items()):
        path = root / rel_path
        if not path.is_file():
            if kind in kinds:
                report.errors.append(ValidationError(
                    rel_path, "SCHEMA_FILE_MISSING",
                    f"存在 {kind} 对象但缺少 Schema 文件 {rel_path}",
                ))
            continue
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
        except (json.JSONDecodeError, UnicodeDecodeError, SchemaError) as exc:
            report.errors.append(ValidationError(
                rel_path, "SCHEMA_FILE_INVALID", f"Schema 文件无法解析：{_first_line(exc)}"
            ))
            continue
        schemas[kind] = Draft202012Validator(schema)
    return schemas


def _validate_source_object(
    obj: ScannedObject,
    schemas: dict[str, Draft202012Validator],
    registries: dict[str, object],
    report: ValidationReport,
) -> None:
    _validate_against_schema(obj, schemas, report)
    source_types = registries["source_types"]
    if obj.kind == "record" and source_types is not None:
        source_type = obj.data.get("source_type")
        if isinstance(source_type, str) and source_type not in source_types:
            report.errors.append(ValidationError(
                obj.rel_path, "SOURCE_TYPE_UNREGISTERED",
                f"来源类型 {source_type} 未登记于 contracts/sources/registry/source-types.yaml",
            ))


def _validate_source_references(index: dict[str, list[ScannedObject]], report: ValidationReport) -> None:
    """来源上下文内部的结构化引用：笔记指向记录、记录指向来源族。"""
    for obj in report.objects:
        if obj.data is None or obj.context != "sources":
            continue
        if obj.kind == "note":
            source_id = obj.data.get("source_id")
            if isinstance(source_id, str) and not _has_object_of_kind(index, source_id, "record"):
                report.errors.append(ValidationError(
                    obj.rel_path, "NOTE_SOURCE_MISSING",
                    f"来源笔记的 source_id {source_id} 不指向任何现有来源记录",
                ))
        elif obj.kind == "record":
            family_id = obj.data.get("family_id")
            if isinstance(family_id, str) and not _has_object_of_kind(index, family_id, "family"):
                report.errors.append(ValidationError(
                    obj.rel_path, "RECORD_FAMILY_MISSING",
                    f"来源记录的 family_id {family_id} 不指向任何现有来源族",
                ))


def _identity_index(report: ValidationReport) -> dict[str, list[ScannedObject]]:
    """按 ULID 汇总全部可解析对象，供跨对象一致性检查使用。"""
    index: dict[str, list[ScannedObject]] = {}
    for obj in report.objects:
        obj_id = obj.data.get("id") if obj.data else None
        if isinstance(obj_id, str):
            index.setdefault(obj_id, []).append(obj)
    return index


def _has_object_of_kind(index: dict[str, list[ScannedObject]], ulid: str, kind: str) -> bool:
    return any(obj.kind == kind for obj in index.get(ulid, []))


def _validate_citations(index: dict[str, list[ScannedObject]], report: ValidationReport) -> None:
    """知识条目正文中的结构化引用必须指向现有来源记录。"""
    for obj in report.objects:
        if obj.data is None or obj.kind != "entry":
            continue
        for target_id, malformed in _iter_citations(obj.body):
            if malformed is not None:
                report.errors.append(ValidationError(
                    obj.rel_path, "CITATION_MALFORMED",
                    f"结构化引用 [@{malformed}] 应形如 [@<来源记录ULID>, <定位信息>]",
                ))
            elif target_id not in index:
                report.errors.append(ValidationError(
                    obj.rel_path, "CITATION_TARGET_MISSING",
                    f"引用目标 {target_id} 不是任何现有对象的 ULID",
                ))
            elif not _has_object_of_kind(index, target_id, "record"):
                kinds = "、".join(sorted({obj.kind for obj in index[target_id]}))
                report.errors.append(ValidationError(
                    obj.rel_path, "CITATION_TARGET_NOT_RECORD",
                    f"引用目标 {target_id} 是 {kinds}，不是来源记录",
                ))


def _iter_citations(body: str):
    """逐个产出条目正文中的引用：(ULID, None) 为合法引用，(None, 原文) 为格式错误。"""
    for match in CITATION_PATTERN.finditer(body):
        content = match.group(1).strip()
        parts = [part.strip() for part in content.split(",", 1)]
        if len(parts) == 2 and parts[1] and ULID_STRICT_PATTERN.match(parts[0]):
            yield parts[0], None
        else:
            yield None, content


def _validate_identity_and_relations(
    index: dict[str, list[ScannedObject]],
    registries: dict[str, object],
    report: ValidationReport,
) -> None:
    """跨上下文的身份唯一性和知识关系完整性。"""
    for ulid, objects in sorted(index.items()):
        if len(objects) > 1:
            files = sorted(obj.rel_path for obj in objects)
            report.errors.append(ValidationError(
                files[0], "ID_DUPLICATE",
                f"ULID {ulid} 重复出现于：{'、'.join(files)}",
            ))
    knowledge_objects = {
        ulid: objects
        for ulid, objects in index.items()
        if any(obj.context == "knowledge" for obj in objects)
    }
    relation_types = registries["relation_types"]
    for obj in report.objects:
        if obj.data is None or obj.context != "knowledge":
            continue
        for relation in _mapping_items(obj.data.get("relations")):
            target_id = relation.get("target_id")
            if not isinstance(target_id, str):
                continue
            targets = knowledge_objects.get(target_id)
            if targets is None:
                report.errors.append(ValidationError(
                    obj.rel_path, "RELATION_TARGET_MISSING",
                    f"关系目标 {target_id} 不是现有知识对象的 ULID",
                ))
                continue
            spec = (
                relation_types.get(relation.get("type"))
                if isinstance(relation_types, dict) and isinstance(relation.get("type"), str)
                else None
            )
            if spec is None:
                continue
            source_kinds, target_kinds = spec
            if obj.kind not in source_kinds or not any(t.kind in target_kinds for t in targets):
                target_kinds_found = "、".join(sorted({t.kind for t in targets}))
                report.errors.append(ValidationError(
                    obj.rel_path, "RELATION_NOT_APPLICABLE",
                    f"关系类型 {relation.get('type')} 不适用于 {obj.kind} → {target_kinds_found}"
                    f"（适用范围：{'/'.join(sorted(source_kinds))} → "
                    f"{'/'.join(sorted(target_kinds))}）",
                ))


def _validate_knowledge_object(
    obj: ScannedObject,
    schemas: dict[str, Draft202012Validator],
    registries: dict[str, object],
    report: ValidationReport,
) -> None:
    _validate_against_schema(obj, schemas, report)
    entry_types = registries["entry_types"]
    if obj.kind == "entry":
        entry_type = obj.data.get("entry_type")
        if entry_types is not None and isinstance(entry_type, str) and entry_type not in entry_types:
            report.errors.append(ValidationError(
                obj.rel_path, "ENTRY_TYPE_UNREGISTERED",
                f"条目类型 {entry_type} 未登记于 contracts/knowledge/registry/entry-types.yaml",
            ))
        for tag in _string_items(obj.data.get("tags")):
            if tag not in registries["tags"]:
                report.errors.append(ValidationError(
                    obj.rel_path, "TAG_UNREGISTERED",
                    f"标签 {tag} 未登记于 {TAGS_DIR}/ 下的标签注册表",
                ))
    relation_types = registries["relation_types"]
    if relation_types is not None:
        for relation in _mapping_items(obj.data.get("relations")):
            relation_type = relation.get("type")
            if isinstance(relation_type, str) and relation_type not in relation_types:
                report.errors.append(ValidationError(
                    obj.rel_path, "RELATION_TYPE_UNREGISTERED",
                    f"关系类型 {relation_type} 未登记于 contracts/knowledge/registry/relation-types.yaml",
                ))


def _load_registries(root: Path, report: ValidationReport) -> dict[str, object]:
    """加载受控注册表；文件缺失的注册表记为 None，由消费方决定是否报错。

    relation_types 登记为「名称 → (适用来源对象类型, 适用目标对象类型)」，
    二者共同表达关系类型定义中的方向与适用对象。
    """
    registries: dict[str, object] = {
        "entry_types": set(),
        "relation_types": {},
        "source_types": set(),
        "tags": set(),
    }
    for key, rel_path, field_name in REGISTRY_FILES:
        if not (root / rel_path).is_file():
            registries[key] = None
            continue
        if key == "relation_types":
            _merge_relation_types(root, rel_path, registries, report)
        else:
            _merge_registry_values(root, rel_path, field_name, registries, key, report)
    tags_dir = root / TAGS_DIR
    if tags_dir.is_dir():
        for path in sorted(tags_dir.glob("*.yaml")):
            rel = f"{TAGS_DIR}/{path.name}"
            _merge_registry_values(root, rel, "tags", registries, "tags", report)
    return registries


def _merge_relation_types(
    root: Path,
    rel_path: str,
    registries: dict[str, object],
    report: ValidationReport,
) -> None:
    path = root / rel_path
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, UnicodeDecodeError) as exc:
        report.errors.append(ValidationError(
            rel_path, "REGISTRY_INVALID", f"注册表无法解析：{_first_line(exc)}"
        ))
        return
    entries = loaded.get("relation_types") if isinstance(loaded, dict) else None
    if not isinstance(entries, list):
        report.errors.append(ValidationError(
            rel_path, "REGISTRY_INVALID",
            "注册表缺少字段 relation_types（每项含 name、source_kinds、target_kinds）",
        ))
        return
    types: dict[str, tuple[set[str], set[str]]] = {}
    for entry in entries:
        valid = (
            isinstance(entry, dict)
            and isinstance(entry.get("name"), str)
            and _is_kind_list(entry.get("source_kinds"))
            and _is_kind_list(entry.get("target_kinds"))
        )
        if not valid:
            report.errors.append(ValidationError(
                rel_path, "REGISTRY_INVALID",
                f"关系类型条目结构无效：{entry}（需要 name 与 "
                f"source_kinds/target_kinds，取值 {'/'.join(sorted(RELATION_KINDS))}）",
            ))
            return
        types[entry["name"]] = (set(entry["source_kinds"]), set(entry["target_kinds"]))
    registries["relation_types"] = types


def _is_kind_list(value: object) -> bool:
    return (
        isinstance(value, list)
        and value
        and all(isinstance(item, str) and item in RELATION_KINDS for item in value)
    )


def _merge_registry_values(
    root: Path,
    rel_path: str,
    field_name: str,
    registries: dict[str, object],
    key: str,
    report: ValidationReport,
) -> None:
    path = root / rel_path
    if not path.is_file():
        return
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, UnicodeDecodeError) as exc:
        report.errors.append(ValidationError(
            rel_path, "REGISTRY_INVALID", f"注册表无法解析：{_first_line(exc)}"
        ))
        return
    values = loaded.get(field_name) if isinstance(loaded, dict) else None
    if not isinstance(values, list):
        report.errors.append(ValidationError(
            rel_path, "REGISTRY_INVALID", f"注册表缺少字段 {field_name}（字符串列表）"
        ))
        return
    if any(not isinstance(item, str) for item in values):
        report.errors.append(ValidationError(
            rel_path, "REGISTRY_INVALID",
            f"注册表 {field_name} 存在非字符串项："
            f"{next(item for item in values if not isinstance(item, str))!r}",
        ))
        return
    current = registries[key]
    if not isinstance(current, set):
        return
    current.update(values)


def _string_items(value: object) -> list[str]:
    """取出字符串列表项；结构非法时交由 Schema 报错，这里返回空。"""
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _mapping_items(value: object) -> list[dict]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _format_instance_path(path) -> str:
    parts = [str(part) for part in path]
    return "$." + ".".join(parts) if parts else "$"


_REQUIRED_PROPERTY_PATTERN = re.compile(r"'(.+?)' is a required property")
_ADDITIONAL_PROPERTY_PATTERN = re.compile(
    r"Additional properties are not allowed \('(.+?)' was unexpected\)"
)


def _schema_error_field_path(error) -> str:
    """缺失必填字段与多余字段的错误挂在父对象上，改写为具体字段路径以便定位。"""
    if not error.absolute_path:
        match = _REQUIRED_PROPERTY_PATTERN.match(error.message)
        if match:
            return f"$.{match.group(1)}"
        match = _ADDITIONAL_PROPERTY_PATTERN.match(error.message)
        if match:
            return f"$.{match.group(1)}"
    return _format_instance_path(error.absolute_path)


def _first_line(exc: Exception) -> str:
    return str(exc).strip().splitlines()[0]
