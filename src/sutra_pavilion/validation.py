"""校验深层模块：全部内容契约检查的唯一实现。

仓库扫描、Front Matter 解析、Schema 与注册表加载由 repository 模块的
仓库快照一次性完成；本模块只消费快照并执行契约规则，不重新解释目录
或对象身份。CLI 适配层只处理参数、退出码和输出。
"""

import re
from dataclasses import dataclass, field

from jsonschema import Draft202012Validator

from sutra_pavilion import repository
from sutra_pavilion.repository import (
    SCHEMA_FILES,
    ScannedObject,
    ValidationError,
    mapping_items,
    string_items,
)

# 结构化引用形式：[@<Attestation ULID>; role=<角色>; strength=<强度>]。
CITATION_PATTERN = re.compile(r"\[@([^\[\]]*)\]")


@dataclass
class ValidationReport:
    """一次校验运行的可观察结果。"""

    knowledge_objects: int = 0
    source_objects: int = 0
    errors: list[ValidationError] = field(default_factory=list)
    objects: tuple[ScannedObject, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors


def validate(path: str) -> ValidationReport:
    """校验给定项目根目录，返回聚合后的报告。"""
    return validate_snapshot(repository.load_snapshot(path))


def validate_snapshot(snapshot: repository.RepositorySnapshot) -> ValidationReport:
    """校验已有仓库快照；校验与检索共享同一次仓库解释。"""
    report = ValidationReport(
        knowledge_objects=snapshot.knowledge_objects,
        source_objects=snapshot.source_objects,
        errors=list(snapshot.errors),
        objects=snapshot.objects,
    )
    if snapshot.fatal is not None:
        report.errors.append(snapshot.fatal)
        return report
    _validate_objects(snapshot, report)
    return report


def _validate_objects(snapshot: repository.RepositorySnapshot, report: ValidationReport) -> None:
    """执行契约自检与全部对象校验。

    即使仓库没有任何正式对象，已存在的 Schema 和注册表文件也会被解析
    自检，保证空内容仓库的 CI 校验不是空操作。
    """
    for obj in report.objects:
        if obj.data is None:
            continue
        if obj.context == "knowledge":
            _validate_knowledge_object(obj, snapshot, report)
        elif obj.context == "sources":
            _validate_source_object(obj, snapshot, report)
    index = snapshot.identity_index()
    _validate_source_references(index, report)
    _validate_identity_and_relations(index, snapshot, report)
    _validate_citations(index, report)
    _validate_myth_semantics(index, snapshot, report)


def _validate_domain_schemas(
    obj: ScannedObject,
    snapshot: repository.RepositorySnapshot,
    report: ValidationReport,
) -> None:
    """按条目所在知识域目录 slug 叠加执行域公共与条目类型 Schema。

    其他知识域没有叠加 Schema 时保持公共契约行为，不强制神话字段。
    """
    slug = repository.domain_slug_of(obj.rel_path)
    if slug is None:
        return
    domain_contracts = snapshot.registries["domain_contracts"]
    contracted_types = (
        domain_contracts.get(slug) if isinstance(domain_contracts, dict) else None
    )
    if contracted_types is None:
        return
    common_rel, type_rel = repository.domain_schema_paths(
        slug, obj.data.get("entry_type") or ""
    )
    if common_rel in snapshot.schemas:
        _validate_against_schema(obj, common_rel, f"{slug} 域公共 Schema", snapshot.schemas, report)
    entry_type = obj.data.get("entry_type")
    if isinstance(entry_type, str) and entry_type in contracted_types \
            and type_rel in snapshot.schemas:
        _validate_against_schema(obj, type_rel, f"{slug}/{obj.data.get('entry_type')} 类型 Schema",
                                 snapshot.schemas, report)


def _validate_against_schema(
    obj: ScannedObject,
    schema_rel: str,
    schema_label: str,
    schemas: dict[str, dict],
    report: ValidationReport,
) -> None:
    """执行对象 Front Matter 对指定 Schema 文件的校验。"""
    schema = schemas.get(schema_rel)
    if schema is None:
        return
    for error in Draft202012Validator(schema).iter_errors(obj.data):
        field_path = _schema_error_field_path(error)
        report.errors.append(ValidationError(
            obj.rel_path, "SCHEMA_INVALID",
            f"字段 {field_path} 不符合 {schema_label}：{error.message}",
        ))


def _validate_source_object(
    obj: ScannedObject,
    snapshot: repository.RepositorySnapshot,
    report: ValidationReport,
) -> None:
    _validate_against_schema(obj, SCHEMA_FILES[obj.kind], f"{obj.kind} Schema", snapshot.schemas, report)
    source_types = snapshot.registries["source_types"]
    if obj.kind == "record" and source_types is not None:
        source_type = obj.data.get("source_type")
        if isinstance(source_type, str) and source_type not in source_types:
            report.errors.append(ValidationError(
                obj.rel_path, "SOURCE_TYPE_UNREGISTERED",
                f"来源类型 {source_type} 未登记于 contracts/sources/registry/source-types.yaml",
            ))


def _validate_source_references(index: dict[str, list[ScannedObject]], report: ValidationReport) -> None:
    """来源上下文内部的结构化引用：笔记指向记录、记录指向来源族、见证指向唯一记录。"""
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
        elif obj.kind == "attestation":
            _validate_attestation(obj, index, report)


def _validate_attestation(
    obj: ScannedObject,
    index: dict[str, list[ScannedObject]],
    report: ValidationReport,
) -> None:
    """Attestation 的文件名、来源归属与继承权利边界（ADR-0004）。"""
    obj_id = obj.data.get("id")
    if isinstance(obj_id, str):
        filename = obj.rel_path.rsplit("/", 1)[-1][: -len(".md")]
        if filename != obj_id:
            report.errors.append(ValidationError(
                obj.rel_path, "ATTESTATION_FILENAME_MISMATCH",
                f"Attestation 文件名必须等于其 ULID：{filename} ≠ {obj_id}",
            ))
    source_record_id = obj.data.get("source_record_id")
    if not _has_object_of_kind(index, source_record_id, "record"):
        report.errors.append(ValidationError(
            obj.rel_path, "ATTESTATION_SOURCE_MISSING",
            f"Attestation 的 source_record_id {source_record_id} 不指向任何现有来源记录",
        ))
    elif obj.data.get("excerpt"):
        rights = _rights_of(index, source_record_id)
        reuse_scope = rights.get("reuse_scope") if rights else None
        if reuse_scope in EXCERPT_FORBIDDEN_SCOPES:
            report.errors.append(ValidationError(
                obj.rel_path, "ATTESTATION_EXCERPT_NOT_ALLOWED",
                f"所属来源记录的 reuse_scope 为 {reuse_scope}，不得保存 excerpt 短引",
            ))
        elif reuse_scope == "link-quote":
            max_chars = rights.get("excerpt_max_chars") if rights else None
            excerpt = obj.data.get("excerpt")
            if isinstance(max_chars, int) and isinstance(excerpt, str) \
                    and len(excerpt) > max_chars:
                report.errors.append(ValidationError(
                    obj.rel_path, "ATTESTATION_EXCERPT_SCOPE_EXCEEDED",
                    f"excerpt 长度 {len(excerpt)} 超过所属来源记录 "
                    f"rights.excerpt_max_chars 上限 {max_chars}",
                ))


EXCERPT_FORBIDDEN_SCOPES = {"metadata-only", "permission-required", "restricted-cultural"}


def _rights_of(index: dict[str, list[ScannedObject]], record_id: str) -> dict | None:
    """取得来源记录的统一权利结构；Attestation 的权利边界唯一来源。"""
    for obj in index.get(record_id, []):
        if obj.kind == "record" and isinstance(obj.data, dict):
            rights = obj.data.get("rights")
            if isinstance(rights, dict):
                return rights
    return None


def _has_object_of_kind(index: dict[str, list[ScannedObject]], ulid: str, kind: str) -> bool:
    return any(obj.kind == kind for obj in index.get(ulid, []))


def _validate_citations(index: dict[str, list[ScannedObject]], report: ValidationReport) -> None:
    """知识条目正文中的结构化引用必须指向现有 Attestation（ADR-0004）。"""
    for obj in report.objects:
        if obj.data is None or obj.kind != "entry":
            continue
        for citation in _iter_citations(obj.body):
            if citation.rule is not None:
                report.errors.append(ValidationError(obj.rel_path, citation.rule, citation.reason))
            elif citation.target_id not in index:
                report.errors.append(ValidationError(
                    obj.rel_path, "CITATION_TARGET_MISSING",
                    f"引用目标 {citation.target_id} 不是任何现有对象的 ULID",
                ))
            elif not _has_object_of_kind(index, citation.target_id, "attestation"):
                kinds = "、".join(sorted({o.kind for o in index[citation.target_id]}))
                report.errors.append(ValidationError(
                    obj.rel_path, "CITATION_TARGET_NOT_ATTESTATION",
                    f"引用目标 {citation.target_id} 是 {kinds}，不是 Attestation；"
                    "知识条目只能引用 Attestation",
                ))


@dataclass
class _ParsedCitation:
    """一条正文引用的解析结果：rule 为 None 表示格式与参数合法。"""

    target_id: str = ""
    rule: str | None = None
    reason: str = ""


CITATION_ROLES = {"support", "context", "counterevidence"}


def _iter_citations(body: str):
    """逐个解析条目正文中的引用，返回格式、角色与强度全部合法的目标 ULID 或错误。"""
    for match in CITATION_PATTERN.finditer(body):
        content = match.group(1).strip()
        yield _parse_citation(content)


def _parse_citation(content: str) -> _ParsedCitation:
    expected = "[@<Attestation ULID>; role=support; strength=1-5]"
    first_part = content.split(",", 1)[0].strip()
    if "," in content and repository.ULID_STRICT_PATTERN.match(first_part):
        return _ParsedCitation(
            rule="CITATION_LEGACY_FORMAT",
            reason=(
                f"结构化引用 [@{content}] 使用了旧的「来源记录 ULID + 定位」语法；"
                f"定位只保存在 Attestation 的 locator 中，请改用 {expected}"
            ),
        )
    parts = [part.strip() for part in content.split(";") if part.strip()]
    if len(parts) != 3:
        return _ParsedCitation(
            rule="CITATION_MALFORMED", reason=f"结构化引用 [@{content}] 应形如 {expected}"
        )
    target, arguments = parts[0], parts[1:]
    if not repository.ULID_STRICT_PATTERN.match(target):
        return _ParsedCitation(
            rule="CITATION_MALFORMED", reason=f"结构化引用 [@{content}] 应形如 {expected}"
        )
    values: dict[str, str] = {}
    for argument in arguments:
        key, separator, value = argument.partition("=")
        if not separator or key not in ("role", "strength") or key in values:
            return _ParsedCitation(
                rule="CITATION_MALFORMED", reason=f"结构化引用 [@{content}] 应形如 {expected}"
            )
        values[key] = value
    role, strength = values["role"], values["strength"]
    if role not in CITATION_ROLES:
        return _ParsedCitation(
            rule="CITATION_ARGUMENT_INVALID",
            reason=f"引用 {target} 的 role 必须取 {'/'.join(sorted(CITATION_ROLES))}，实际为 {role}",
        )
    if not (strength.isdigit() and 1 <= int(strength) <= 5):
        return _ParsedCitation(
            rule="CITATION_ARGUMENT_INVALID",
            reason=f"引用 {target} 的 strength 必须是 1-5 的整数，实际为 {strength}",
        )
    return _ParsedCitation(target_id=target)


def _validate_identity_and_relations(
    index: dict[str, list[ScannedObject]],
    snapshot: repository.RepositorySnapshot,
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
    relation_types = snapshot.registries["relation_types"]
    for obj in report.objects:
        if obj.data is None or obj.context != "knowledge":
            continue
        for relation in mapping_items(obj.data.get("relations")):
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
            relation_type = relation.get("type")
            if (
                repository.domain_slug_of(obj.rel_path) == MYTH_DOMAIN_SLUG
                and relation_type in MYTH_FORBIDDEN_RELATION_TYPES
            ):
                report.errors.append(ValidationError(
                    obj.rel_path, "RELATION_TYPE_NOT_ALLOWED_IN_DOMAIN",
                    f"神话域不得用通用关系 {relation_type} 表达解释性结论，"
                    "请建立 claim 条目（谓词见 claim-predicates.yaml）",
                ))
                continue
            spec = (
                relation_types.get(relation_type)
                if isinstance(relation_types, dict) and isinstance(relation_type, str)
                else None
            )
            if spec is None:
                continue
            source_kinds, target_kinds, source_entry_types, target_entry_types = spec
            if obj.kind not in source_kinds or not any(t.kind in target_kinds for t in targets):
                target_kinds_found = "、".join(sorted({t.kind for t in targets}))
                report.errors.append(ValidationError(
                    obj.rel_path, "RELATION_NOT_APPLICABLE",
                    f"关系类型 {relation_type} 不适用于 {obj.kind} → {target_kinds_found}"
                    f"（适用范围：{'/'.join(sorted(source_kinds))} → "
                    f"{'/'.join(sorted(target_kinds))}）",
                ))
                continue
            if obj.kind == "entry" and source_entry_types is not None \
                    and obj.data.get("entry_type") not in source_entry_types:
                report.errors.append(ValidationError(
                    obj.rel_path, "RELATION_ENTRY_TYPE_NOT_APPLICABLE",
                    f"关系类型 {relation_type} 不适用于条目类型 "
                    f"{obj.data.get('entry_type')}（允许的来源条目类型："
                    f"{'/'.join(sorted(source_entry_types))}）",
                ))
            if target_entry_types is not None and not any(
                t.kind == "entry" and t.data is not None
                and t.data.get("entry_type") in target_entry_types
                for t in targets
            ):
                report.errors.append(ValidationError(
                    obj.rel_path, "RELATION_ENTRY_TYPE_NOT_APPLICABLE",
                    f"关系类型 {relation_type} 的目标不含允许的条目类型"
                    f"（允许的目标条目类型：{'/'.join(sorted(target_entry_types))}）",
                ))


MYTH_DOMAIN_SLUG = "myth-research"

# 神话域内禁止用通用关系表达解释性结论（神话研究领域设计 6.6）。
MYTH_FORBIDDEN_RELATION_TYPES = {"influenced"}

# 各条目类型的正文章节最低要求：标题含关键词且内容非空（设计 6.5）。
MYTH_BODY_SECTIONS = {
    "tradition": ["内部分期", "争议"],
    "motif": ["操作性定义", "排除标准"],
    "claim": ["反证", "其他解释"],
}


def _validate_myth_semantics(
    index: dict[str, list[ScannedObject]],
    snapshot: repository.RepositorySnapshot,
    report: ValidationReport,
) -> None:
    """神话域条目的跨字段与跨对象语义检查（设计 7）。

    只作用于 myth-research 域内的条目；其他知识域保持公共契约行为。
    """
    for obj in report.objects:
        if obj.data is None or obj.kind != "entry":
            continue
        if repository.domain_slug_of(obj.rel_path) != MYTH_DOMAIN_SLUG:
            continue
        _check_name_forms(obj, report)
        _check_publication_state(obj, report)
        _check_body_sections(obj, report)
        _check_citation_counts(obj, index, report)
        if obj.data.get("entry_type") == "episode":
            _check_episode_relations(obj, report)
        if obj.data.get("entry_type") == "claim":
            _check_claim(obj, index, snapshot, report)


def _check_name_forms(obj: ScannedObject, report: ValidationReport) -> None:
    """name_forms 是名称真源：title 与 aliases 必须是其确定性投影。"""
    forms = obj.data.get("name_forms")
    if not isinstance(forms, list):
        return  # 结构错误已由 Schema 报告
    dict_forms = [f for f in forms if isinstance(f, dict)]
    displays = [f for f in dict_forms if f.get("display") is True]
    if len(displays) != 1:
        report.errors.append(ValidationError(
            obj.rel_path, "NAME_DISPLAY_INVALID",
            f"name_forms 必须恰有一个 display: true 的名称形式，实际有 {len(displays)} 个",
        ))
        return
    display_text = displays[0].get("text")
    if display_text != obj.data.get("title"):
        report.errors.append(ValidationError(
            obj.rel_path, "NAME_DISPLAY_INVALID",
            f"展示名称形式 {display_text!r} 与 title {obj.data.get('title')!r} 不一致",
        ))
    others = [f for f in dict_forms if f is not displays[0]]
    expected_aliases: list[str] = []
    for form in others:
        text = form.get("text")
        if isinstance(text, str) and text not in expected_aliases:
            expected_aliases.append(text)
    aliases = obj.data.get("aliases")
    if isinstance(aliases, list) and aliases != expected_aliases:
        report.errors.append(ValidationError(
            obj.rel_path, "ALIASES_PROJECTION_MISMATCH",
            f"aliases 必须等于其余名称形式的有序去重投影，"
            f"期望 {expected_aliases}，实际 {aliases}",
        ))
    form_ids = {f.get("id") for f in dict_forms if isinstance(f.get("id"), str)}
    for form in dict_forms:
        for target in form.get("translated_as") or []:
            if isinstance(target, str) and target not in form_ids:
                report.errors.append(ValidationError(
                    obj.rel_path, "NAME_TRANSLATION_TARGET_MISSING",
                    f"名称形式 {form.get('id')} 的 translated_as 目标 {target} "
                    "不在同一条目的 name_forms 中",
                ))


def _check_publication_state(obj: ScannedObject, report: ValidationReport) -> None:
    """published 必须同时 verified；正式检索依赖该不变量（设计 6.4）。"""
    if obj.data.get("status") == "published" \
            and obj.data.get("verification_stage") != "verified":
        report.errors.append(ValidationError(
            obj.rel_path, "KNOWLEDGE_STATE_INVALID",
            f"status: published 必须同时为 verification_stage: verified，"
            f"实际为 {obj.data.get('verification_stage')}",
        ))


def _check_body_sections(obj: ScannedObject, report: ValidationReport) -> None:
    """类型契约要求的正文章节必须存在且非空（设计 6.5）。"""
    required = MYTH_BODY_SECTIONS.get(obj.data.get("entry_type"))
    if not required:
        return
    sections = _body_sections(obj.body)
    for keyword in required:
        content = next((text for title, text in sections if keyword in title), None)
        if content is None or not content.strip():
            report.errors.append(ValidationError(
                obj.rel_path, "ENTRY_BODY_SECTION_MISSING",
                f"条目类型 {obj.data.get('entry_type')} 的正文章节「{keyword}」缺失或为空",
            ))


def _body_sections(body: str) -> list[tuple[str, str]]:
    lines = body.splitlines()
    sections: list[tuple[str, str]] = []
    current_title: str | None = None
    current: list[str] = []
    for line in lines:
        if line.startswith("#"):
            if current_title is not None:
                sections.append((current_title, "\n".join(current)))
            current_title, current = line.lstrip("#").strip(), []
        elif current_title is not None:
            current.append(line)
    if current_title is not None:
        sections.append((current_title, "\n".join(current)))
    return sections


def _check_citation_counts(
    obj: ScannedObject,
    index: dict[str, list[ScannedObject]],
    report: ValidationReport,
) -> None:
    """已发布神话条目与 claim 的最低 Attestation 引用数量（设计 6.3）。"""
    valid_citations = sum(
        1 for citation in _iter_citations(obj.body)
        if citation.rule is None and _has_object_of_kind(index, citation.target_id, "attestation")
    )
    if obj.data.get("status") == "published" and valid_citations == 0:
        report.errors.append(ValidationError(
            obj.rel_path, "PUBLISHED_ENTRY_WITHOUT_ATTESTATION",
            "已发布神话条目至少要引用一个 Attestation",
        ))
    if obj.data.get("entry_type") == "claim" and valid_citations == 0:
        report.errors.append(ValidationError(
            obj.rel_path, "CLAIM_WITHOUT_EVIDENCE",
            "claim 条目至少要引用一个 Attestation 作为证据",
        ))
    if obj.data.get("entry_type") == "episode" and valid_citations == 0:
        report.errors.append(ValidationError(
            obj.rel_path, "EPISODE_CITATION_MISSING",
            "episode 条目至少要引用一个 Attestation（叙事必须绑定具体文本见证）",
        ))


EPISODE_REQUIRED_RELATION_TYPES = ("within_tradition", "features", "instantiates_motif")


def _check_episode_relations(obj: ScannedObject, report: ValidationReport) -> None:
    """episode 必须与 Tradition、人物和 Motif 各有至少一个结构关系（设计 6.5）。"""
    declared = {
        relation.get("type")
        for relation in mapping_items(obj.data.get("relations"))
        if isinstance(relation.get("type"), str)
    }
    missing = [name for name in EPISODE_REQUIRED_RELATION_TYPES if name not in declared]
    if missing:
        report.errors.append(ValidationError(
            obj.rel_path, "EPISODE_RELATION_MISSING",
            f"episode 条目必须与 Tradition（within_tradition）、人物（features）"
            f"和 Motif（instantiates_motif）各有至少一个结构关系，缺少：{'、'.join(missing)}",
        ))


def _check_claim(
    obj: ScannedObject,
    index: dict[str, list[ScannedObject]],
    snapshot: repository.RepositorySnapshot,
    report: ValidationReport,
) -> None:
    """Claim 谓词受控，主客体必须是现有、不同且非 Claim 的知识条目（设计 6.6）。"""
    attributes = obj.data.get("attributes")
    if not isinstance(attributes, dict):
        return  # 结构错误已由 Schema 报告
    claim_predicates = snapshot.registries["claim_predicates"]
    predicate = attributes.get("predicate")
    if claim_predicates is not None and isinstance(predicate, str) \
            and predicate not in claim_predicates:
        report.errors.append(ValidationError(
            obj.rel_path, "CLAIM_PREDICATE_UNREGISTERED",
            f"Claim 谓词 {predicate} 未登记于 claim-predicates.yaml；"
            "translated_as 不是 Claim 谓词，名称翻译记录在 name_forms.translated_as",
        ))
    endpoints = [
        ("subject_id", attributes.get("subject_id")),
        ("object_id", attributes.get("object_id")),
    ]
    resolved: list[object] = []
    for endpoint_field, endpoint in endpoints:
        targets = index.get(endpoint) if isinstance(endpoint, str) else None
        entry_targets = [t for t in (targets or []) if t.kind == "entry" and t.data is not None]
        if not entry_targets or any(t.data.get("entry_type") == "claim" for t in entry_targets):
            report.errors.append(ValidationError(
                obj.rel_path, "CLAIM_ENDPOINT_INVALID",
                f"Claim 的 {endpoint_field} 必须指向现有且非 claim 类型的知识条目，"
                f"实际为 {endpoint!r}",
            ))
        else:
            resolved.append(endpoint)
    if len(resolved) == 2 and resolved[0] == resolved[1]:
        report.errors.append(ValidationError(
            obj.rel_path, "CLAIM_ENDPOINT_INVALID",
            f"Claim 的主客体不能指向同一对象 {resolved[0]}",
        ))


def _validate_knowledge_object(
    obj: ScannedObject,
    snapshot: repository.RepositorySnapshot,
    report: ValidationReport,
) -> None:
    _validate_against_schema(obj, SCHEMA_FILES[obj.kind], f"{obj.kind} Schema", snapshot.schemas, report)
    if obj.kind == "entry":
        _validate_domain_schemas(obj, snapshot, report)
    entry_types = snapshot.registries["entry_types"]
    if obj.kind == "entry":
        entry_type = obj.data.get("entry_type")
        if entry_types is not None and isinstance(entry_type, str) and entry_type not in entry_types:
            report.errors.append(ValidationError(
                obj.rel_path, "ENTRY_TYPE_UNREGISTERED",
                f"条目类型 {entry_type} 未登记于 contracts/knowledge/registry/entry-types.yaml",
            ))
        for tag in string_items(obj.data.get("tags")):
            if tag not in snapshot.registries["tags"]:
                report.errors.append(ValidationError(
                    obj.rel_path, "TAG_UNREGISTERED",
                    f"标签 {tag} 未登记于 {repository.TAGS_DIR}/ 下的标签注册表",
                ))
    relation_types = snapshot.registries["relation_types"]
    if relation_types is not None:
        for relation in mapping_items(obj.data.get("relations")):
            relation_type = relation.get("type")
            if isinstance(relation_type, str) and relation_type not in relation_types:
                report.errors.append(ValidationError(
                    obj.rel_path, "RELATION_TYPE_UNREGISTERED",
                    f"关系类型 {relation_type} 未登记于 contracts/knowledge/registry/relation-types.yaml",
                ))


def _format_instance_path(path) -> str:
    parts = [str(part) for part in path]
    return "$." + ".".join(parts) if parts else "$"

_REQUIRED_PROPERTY_PATTERN = re.compile(r"'(.+?)' is a required property")
_ADDITIONAL_PROPERTY_PATTERN = re.compile(
    r"Additional properties are not allowed \('(.+?)' was unexpected\)"
)


def _schema_error_field_path(error) -> str:
    """缺失必填字段与多余字段的错误挂在父对象上，改写为具体字段路径以便定位。"""
    match = _REQUIRED_PROPERTY_PATTERN.match(error.message)
    if match:
        return f"{_format_instance_path(error.absolute_path)}.{match.group(1)}"
    match = _ADDITIONAL_PROPERTY_PATTERN.match(error.message)
    if match:
        return f"{_format_instance_path(error.absolute_path)}.{match.group(1)}"
    return _format_instance_path(error.absolute_path)
