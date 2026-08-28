"""仓库检查模块：扫描、解析、契约加载与身份索引的唯一实现。

校验与检索共享一次不可变仓库快照，不得各自重新解释目录或对象身份。
扫描范围只包括权威对象目录；上下文说明、模板、收件箱、生成物和测试
fixture 不是正式内容，不参与扫描。
"""

import datetime
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType

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
    ("sources", "attestation", "sutra-pavilion/sources/attestations/*.md"),
]

# 对象类型到基础 Schema 文件的映射，从待校验项目根目录下的 contracts/ 加载。
SCHEMA_FILES: dict[str, str] = {
    "domain": "contracts/knowledge/schemas/domain.schema.json",
    "library": "contracts/knowledge/schemas/library.schema.json",
    "entry": "contracts/knowledge/schemas/entry.schema.json",
    "family": "contracts/sources/schemas/source-family.schema.json",
    "record": "contracts/sources/schemas/source-record.schema.json",
    "note": "contracts/sources/schemas/source-note.schema.json",
    "attestation": "contracts/sources/schemas/attestation.schema.json",
}

# 受控注册表：(注册表键, 文件, 顶层字段)。
REGISTRY_FILES: list[tuple[str, str, str]] = [
    ("entry_types", "contracts/knowledge/registry/entry-types.yaml", "entry_types"),
    ("relation_types", "contracts/knowledge/registry/relation-types.yaml", "relation_types"),
    ("source_types", "contracts/sources/registry/source-types.yaml", "source_types"),
    ("claim_predicates", "contracts/knowledge/registry/claim-predicates.yaml", "claim_predicates"),
    ("domain_contracts", "contracts/knowledge/registry/domain-contracts.yaml", "domain_contracts"),
]

# 各注册表被消费的对象类型。注册表文件缺失且存在消费者时报告
# REGISTRY_FILE_MISSING，而不是把合法值误报为未登记。
REGISTRY_CONSUMER_KINDS: dict[str, set[str]] = {
    "entry_types": {"entry"},
    "relation_types": {"domain", "library", "entry"},
    "source_types": {"record"},
    "claim_predicates": {"entry"},
    "domain_contracts": {"entry"},
}

# 关系类型适用对象声明中允许出现的知识对象类型。
RELATION_KINDS = {"domain", "library", "entry"}

TAGS_DIR = "contracts/knowledge/registry/tags"

# 域叠加 Schema 的存放约定：由条目所在知识域目录 slug 选择，不需要的域不创建即不生效。
DOMAIN_SCHEMAS_DIR = "contracts/knowledge/schemas/domains"

ULID_STRICT_PATTERN = re.compile(r"^[0-9A-HJKMNP-TV-Z]{26}$")


class FrozenMapping(dict):
    """冻结的映射：保持 dict 语义（含 isinstance 与 JSON Schema 校验），禁止变更。"""

    def _immutable(self, *args, **kwargs):
        raise TypeError("仓库快照内容不可变；如需修改请重新扫描仓库")

    __setitem__ = __delitem__ = pop = popitem = clear = update = setdefault = _immutable
    __ior__ = _immutable


class FrozenList(list):
    """冻结的列表：保持 list 语义（含 JSON Schema array 校验），禁止变更。"""

    def _immutable(self, *args, **kwargs):
        raise TypeError("仓库快照内容不可变；如需修改请重新扫描仓库")

    __setitem__ = __delitem__ = append = extend = insert = remove = pop = clear = \
        sort = reverse = __iadd__ = __imul__ = _immutable


def freeze(value):
    """递归冻结 Front Matter 解析结果，供不可变快照共享。"""
    if isinstance(value, dict):
        return FrozenMapping({key: freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return FrozenList(freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class ValidationError:
    """携带仓库相对路径、稳定规则标识和可操作原因的统一错误结构。"""

    path: str
    rule: str
    reason: str

    def format(self) -> str:
        return f"{self.path}: {self.rule}: {self.reason}"


@dataclass(frozen=True)
class ScannedObject:
    """一个被扫描的正式对象；解析失败时 data 为 None。

    仓库快照的组成单元，冻结以保持一次扫描结果的不可变解释。
    """

    context: str
    kind: str
    rel_path: str
    data: dict | None
    body: str


@dataclass(frozen=True)
class RepositorySnapshot:
    """一次目录扫描、解析与契约加载得到的不可变仓库解释。

    fatal 不为 None 表示项目根不可用（路径缺失、非目录或误传内容
    Vault），此时对象与契约均未加载，消费方只应报告该错误。
    objects 与 errors 冻结为元组：校验与检索共享的同一次解释不可被
    任何消费者中途污染。
    """

    root: Path
    objects: tuple[ScannedObject, ...] = ()
    errors: tuple[ValidationError, ...] = ()
    schemas: dict[str, dict] = field(default_factory=dict)
    registries: dict[str, object] = field(default_factory=dict)
    fatal: ValidationError | None = None

    @property
    def knowledge_objects(self) -> int:
        return sum(1 for o in self.objects if o.context == "knowledge")

    @property
    def source_objects(self) -> int:
        return sum(1 for o in self.objects if o.context == "sources")

    def identity_index(self) -> dict[str, list[ScannedObject]]:
        """按 ULID 汇总全部可解析对象，供跨对象一致性检查使用。"""
        index: dict[str, list[ScannedObject]] = {}
        for obj in self.objects:
            obj_id = obj.data.get("id") if obj.data else None
            if isinstance(obj_id, str):
                index.setdefault(obj_id, []).append(obj)
        return index


def load_snapshot(path: str) -> RepositorySnapshot:
    """加载项目根目录的仓库快照：扫描、解析、Schema 与注册表。"""
    root = Path(path)
    if not root.exists():
        return RepositorySnapshot(
            root, fatal=ValidationError(path, "PATH_MISSING", f"校验路径不存在：{path}")
        )
    if not root.is_dir():
        return RepositorySnapshot(
            root,
            fatal=ValidationError(path, "PATH_NOT_DIRECTORY", "校验路径必须是项目根目录（目录）"),
        )
    if _looks_like_content_vault(root):
        return RepositorySnapshot(
            root,
            fatal=ValidationError(
                path, "PATH_IS_CONTENT_VAULT",
                "校验路径呈现内容 Vault 布局；请改用其项目根目录运行 sutra validate",
            ),
        )
    scan_errors: list[ValidationError] = []
    objects = _scan_objects(root, scan_errors)
    kinds = {obj.kind for obj in objects}
    schemas = _load_schemas(root, kinds, scan_errors)
    registries = _load_registries(root, scan_errors)
    for key, rel_path, _ in REGISTRY_FILES:
        if registries[key] is None and kinds & REGISTRY_CONSUMER_KINDS[key]:
            scan_errors.append(ValidationError(
                rel_path, "REGISTRY_FILE_MISSING",
                f"缺少注册表文件 {rel_path}，无法校验相关受控值",
            ))
    domain_contracts = registries["domain_contracts"]
    _check_domain_schema_presence(
        root, objects, schemas, domain_contracts if domain_contracts else {}, scan_errors
    )
    return RepositorySnapshot(
        root=root,
        objects=tuple(objects),
        errors=tuple(scan_errors),
        schemas=MappingProxyType(schemas),
        registries=MappingProxyType(_freeze_registries(registries)),
    )


def _freeze_registries(registries: dict[str, object]) -> dict[str, object]:
    """把注册表冻结为只读结构：集合变 frozenset，字典变冻结映射。"""
    frozen: dict[str, object] = {}
    for key, value in registries.items():
        if isinstance(value, set):
            frozen[key] = frozenset(value)
        elif key == "relation_types" and isinstance(value, dict):
            frozen[key] = FrozenMapping({
                name: tuple(
                    frozenset(kinds) if kinds is not None else None for kinds in spec
                )
                for name, spec in value.items()
            })
        elif isinstance(value, dict):
            frozen[key] = FrozenMapping(value)
        else:
            frozen[key] = value
    return frozen


def _check_domain_schema_presence(
    root: Path,
    objects: list[ScannedObject],
    schemas: dict[str, dict],
    domain_contracts: dict[str, frozenset[str]],
    errors: list[ValidationError],
) -> None:
    """以域契约注册表为准强制契约文件存在，不允许静默撤销契约层。

    注册表登记的域必须提供 common.schema.json；注册表列出的专属条目类型
    必须提供对应类型 Schema（删除整个域 Schema 目录同样失败，因为注册表
    独立于该目录存在）。未登记的条目类型复用公共条目契约，不受影响。
    """
    reported: set[str] = set()

    def report_missing(rel: str, reason: str) -> None:
        # 只在文件确实缺失时报告（存在但解析失败已由 SCHEMA_FILE_INVALID 覆盖），
        # 并按文件去重，避免每个条目重复一条。
        if rel in reported or (root / rel).is_file():
            return
        reported.add(rel)
        errors.append(ValidationError(rel, "SCHEMA_FILE_MISSING", reason))

    for obj in objects:
        if obj.data is None or obj.kind != "entry":
            continue
        slug = domain_slug_of(obj.rel_path)
        contracted_types = domain_contracts.get(slug) if slug else None
        if not contracted_types and slug not in domain_contracts:
            continue
        common_rel, type_rel = domain_schema_paths(slug, obj.data.get("entry_type") or "")
        if common_rel not in schemas:
            report_missing(
                common_rel, f"存在 {slug} 域条目但缺少域公共 Schema 文件 {common_rel}"
            )
        entry_type = obj.data.get("entry_type")
        if isinstance(entry_type, str) and entry_type in contracted_types \
                and type_rel not in schemas:
            report_missing(
                type_rel,
                f"存在条目类型 {entry_type} 的 {slug} 域条目"
                f"但缺少类型 Schema 文件 {type_rel}",
            )


def _looks_like_content_vault(root: Path) -> bool:
    """识别被误传给 CLI 的内容 Vault 目录，避免空扫描被误报为通过。"""
    return (
        (root / "CONTEXT-MAP.md").is_file()
        and (root / "knowledge").is_dir()
        and (root / "sources").is_dir()
        and not (root / "sutra-pavilion").is_dir()
    )


def _scan_objects(root: Path, errors: list[ValidationError]) -> list[ScannedObject]:
    objects: list[ScannedObject] = []
    for context, kind, pattern in SCAN_RULES:
        for path in sorted(root.glob(pattern)):
            rel_path = path.relative_to(root).as_posix()
            data, body, error = _read_front_matter(path, rel_path)
            if error is not None:
                errors.append(error)
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
            rel_path, "FRONT_MATTER_UNPARSEABLE", f"Front Matter 不是合法 YAML：{first_line(exc)}"
        )
    if not isinstance(data, dict):
        return None, body, ValidationError(
            rel_path, "FRONT_MATTER_NOT_MAPPING",
            f"Front Matter 顶层必须是键值映射，实际解析结果为 {type(data).__name__}",
        )
    return freeze(_normalize_yaml_dates(data)), body, None


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


def _load_schemas(
    root: Path, kinds: set[str], errors: list[ValidationError]
) -> dict[str, dict]:
    """解析并自检仓库中存在的全部基础 Schema 文件。

    文件存在即解析并做元 Schema 检查（无论是否有对应对象）；文件缺失
    仅在存在该类型对象时报告 SCHEMA_FILE_MISSING。
    """
    schemas: dict[str, dict] = {}
    for kind, rel_path in sorted(SCHEMA_FILES.items()):
        _load_schema_file(root, rel_path, f"存在 {kind} 对象", kind in kinds, schemas, errors)
    _load_domain_schemas(root, schemas, errors)
    return schemas


def _load_domain_schemas(
    root: Path, schemas: dict[str, dict], errors: list[ValidationError]
) -> None:
    """解析并自检全部域叠加 Schema（common 与 entry-types/*），无论是否有对象。

    域 Schema 是可选层：缺失不报错，存在即自检并在校验时叠加执行。
    """
    domains_dir = root / DOMAIN_SCHEMAS_DIR
    if not domains_dir.is_dir():
        return
    for path in sorted(domains_dir.glob("*/common.schema.json")):
        rel = path.relative_to(root).as_posix()
        _load_schema_file(root, rel, "", False, schemas, errors)
    for path in sorted(domains_dir.glob("*/entry-types/*.schema.json")):
        rel = path.relative_to(root).as_posix()
        _load_schema_file(root, rel, "", False, schemas, errors)


def domain_slug_of(rel_path: str) -> str | None:
    """从权威相对路径提取知识域目录 slug；非域内对象返回 None。"""
    parts = rel_path.split("/")
    if len(parts) > 4 and parts[0] == "sutra-pavilion" and parts[1] == "knowledge" \
            and parts[2] == "domains" and parts[4] == "libraries":
        return parts[3]
    return None


def domain_schema_paths(slug: str, entry_type: str) -> tuple[str, str]:
    """返回域公共与条目类型叠加 Schema 的约定路径。"""
    base = f"{DOMAIN_SCHEMAS_DIR}/{slug}"
    return f"{base}/common.schema.json", f"{base}/entry-types/{entry_type}.schema.json"


def _load_schema_file(
    root: Path,
    rel_path: str,
    consumer_hint: str,
    has_consumers: bool,
    schemas: dict[str, dict],
    errors: list[ValidationError],
) -> None:
    path = root / rel_path
    if not path.is_file():
        if has_consumers:
            errors.append(ValidationError(
                rel_path, "SCHEMA_FILE_MISSING",
                f"{consumer_hint}但缺少 Schema 文件 {rel_path}",
            ))
        return
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
    except (json.JSONDecodeError, UnicodeDecodeError, SchemaError) as exc:
        errors.append(ValidationError(
            rel_path, "SCHEMA_FILE_INVALID", f"Schema 文件无法解析：{first_line(exc)}"
        ))
        return
    schemas[rel_path] = freeze(schema)


def _load_registries(root: Path, errors: list[ValidationError]) -> dict[str, object]:
    """加载受控注册表；文件缺失的注册表记为 None，由消费方决定是否报错。

    relation_types 登记为「名称 → (适用来源对象类型, 适用目标对象类型)」，
    二者共同表达关系类型定义中的方向与适用对象。
    """
    registries: dict[str, object] = {
        "entry_types": set(),
        "relation_types": {},
        "source_types": set(),
        "claim_predicates": set(),
        "domain_contracts": {},
        "tags": set(),
    }
    for key, rel_path, field_name in REGISTRY_FILES:
        if not (root / rel_path).is_file():
            registries[key] = None
            continue
        if key == "relation_types":
            _merge_relation_types(root, rel_path, registries, errors)
        elif key == "domain_contracts":
            _merge_domain_contracts(root, rel_path, registries, errors)
        else:
            _merge_registry_values(root, rel_path, field_name, registries, key, errors)
    tags_dir = root / TAGS_DIR
    if tags_dir.is_dir():
        for path in sorted(tags_dir.glob("*.yaml")):
            rel = f"{TAGS_DIR}/{path.name}"
            _merge_registry_values(root, rel, "tags", registries, "tags", errors)
    return registries


def _merge_relation_types(
    root: Path,
    rel_path: str,
    registries: dict[str, object],
    errors: list[ValidationError],
) -> None:
    path = root / rel_path
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, UnicodeDecodeError) as exc:
        errors.append(ValidationError(
            rel_path, "REGISTRY_INVALID", f"注册表无法解析：{first_line(exc)}"
        ))
        return
    entries = loaded.get("relation_types") if isinstance(loaded, dict) else None
    if not isinstance(entries, list):
        errors.append(ValidationError(
            rel_path, "REGISTRY_INVALID",
            "注册表缺少字段 relation_types（每项含 name、source_kinds、target_kinds）",
        ))
        return
    types: dict[str, tuple[set[str], set[str], set[str] | None, set[str] | None]] = {}
    for entry in entries:
        valid = (
            isinstance(entry, dict)
            and isinstance(entry.get("name"), str)
            and _is_kind_list(entry.get("source_kinds"))
            and _is_kind_list(entry.get("target_kinds"))
        )
        if not valid:
            errors.append(ValidationError(
                rel_path, "REGISTRY_INVALID",
                f"关系类型条目结构无效：{entry}（需要 name 与 "
                f"source_kinds/target_kinds，取值 {'/'.join(sorted(RELATION_KINDS))}）",
            ))
            return
        source_entry_types = _optional_entry_type_list(entry.get("source_entry_types"))
        target_entry_types = _optional_entry_type_list(entry.get("target_entry_types"))
        if source_entry_types is _INVALID or target_entry_types is _INVALID:
            errors.append(ValidationError(
                rel_path, "REGISTRY_INVALID",
                f"关系类型 {entry.get('name')} 的 source_entry_types/target_entry_types "
                "必须是非空字符串列表",
            ))
            return
        types[entry["name"]] = (
            set(entry["source_kinds"]),
            set(entry["target_kinds"]),
            source_entry_types,
            target_entry_types,
        )
    registries["relation_types"] = types


_INVALID = object()


def _optional_entry_type_list(value: object):
    if value is None:
        return None
    if not isinstance(value, list) or not value:
        return _INVALID
    if any(not isinstance(item, str) or not item for item in value):
        return _INVALID
    return set(value)


def _merge_domain_contracts(
    root: Path,
    rel_path: str,
    registries: dict[str, object],
    errors: list[ValidationError],
) -> None:
    path = root / rel_path
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, UnicodeDecodeError) as exc:
        errors.append(ValidationError(
            rel_path, "REGISTRY_INVALID", f"注册表无法解析：{first_line(exc)}"
        ))
        return
    entries = loaded.get("domain_contracts") if isinstance(loaded, dict) else None
    if not isinstance(entries, list) or not entries:
        errors.append(ValidationError(
            rel_path, "REGISTRY_INVALID",
            "注册表缺少字段 domain_contracts（每项含 domain 与 entry_types）",
        ))
        return
    contracts: dict[str, frozenset[str]] = {}
    for entry in entries:
        entry_types = entry.get("entry_types", []) if isinstance(entry, dict) else None
        valid = (
            isinstance(entry, dict)
            and isinstance(entry.get("domain"), str)
            and entry["domain"]
            and isinstance(entry_types, list)
            and all(isinstance(item, str) and item for item in entry_types)
        )
        if not valid:
            errors.append(ValidationError(
                rel_path, "REGISTRY_INVALID",
                f"域契约条目结构无效：{entry}（需要 domain 与 entry_types 字符串列表）",
            ))
            return
        domain = entry["domain"]
        if domain in contracts:
            errors.append(ValidationError(
                rel_path, "REGISTRY_INVALID", f"域契约存在重复 domain：{domain}"
            ))
            return
        contracts[domain] = frozenset(entry_types)
    registries["domain_contracts"] = contracts


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
    errors: list[ValidationError],
) -> None:
    path = root / rel_path
    if not path.is_file():
        return
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, UnicodeDecodeError) as exc:
        errors.append(ValidationError(
            rel_path, "REGISTRY_INVALID", f"注册表无法解析：{first_line(exc)}"
        ))
        return
    values = loaded.get(field_name) if isinstance(loaded, dict) else None
    if not isinstance(values, list):
        errors.append(ValidationError(
            rel_path, "REGISTRY_INVALID", f"注册表缺少字段 {field_name}（字符串列表）"
        ))
        return
    if any(not isinstance(item, str) for item in values):
        errors.append(ValidationError(
            rel_path, "REGISTRY_INVALID",
            f"注册表 {field_name} 存在非字符串项："
            f"{next(item for item in values if not isinstance(item, str))!r}",
        ))
        return
    current = registries[key]
    if not isinstance(current, set):
        return
    current.update(values)


def string_items(value: object) -> list[str]:
    """取出字符串列表项；结构非法时交由 Schema 报错，这里返回空。"""
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def mapping_items(value: object) -> list[dict]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def first_line(exc: Exception) -> str:
    return str(exc).strip().splitlines()[0]
