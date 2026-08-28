---
schema_version: 1
id: <ULID>
title: <来源标题>
source_type: <来源类型>
source_role: <来源角色>
access_method: <访问方式>
language: zh-CN
status: available
edition: <版次>
publisher: <出版社或机构>
external_ids:
  url: <稳定记录页链接>
acquisition:
  acquired_date: <获取日期>
rights:
  rights_statement: <权利说明或待核验状态>
  license_spdx: ""
  reuse_scope: <复用范围>
  access_status: <访问状态>
  permission_basis: <许可依据：权利声明的出处或法律依据>
  excerpt_max_chars: <短引上限字符数>
---

<!-- 模板说明：将占位项替换为具体值，保存为 sources/catalog/records/<ULID>.md（Vault 相对路径，项目内位于 sutra-pavilion/）。source_type 必须已登记于 contracts/sources/registry/source-types.yaml；status 取值 available / inaccessible / withdrawn / superseded。source_role 取 raw-material / critical-edition / scholarship / institutional-overview / discovery-clue（研究用途，不与 source_type 混用）。rights.reuse_scope 取 redistributable / noncommercial / link-quote / metadata-only / permission-required / restricted-cultural（权利未确认时用 metadata-only 并在 rights_statement 写明）；access_status 取 public / restricted / closed；reuse_scope 为 restricted-cultural 时必须补 community_protocol 与 consent_note。source_type 为 book 时 edition、publisher、external_ids.url 与 acquisition.acquired_date 必填。reuse_scope 为 link-quote 时必须填写 permission_basis（短引主张的权利依据）与 excerpt_max_chars（短引上限字符数），Attestation 的短引长度不得超过该上限；redistributable / noncommercial 的权利依据由 rights_statement 与 license_spdx 表达。可选结构化字段见 contracts/sources/schemas/source-record.schema.json：authors、published_date、family_id、acquisition（file_location/checksum）、traceability、rigor。完成后删除本注释。 -->

## 说明

<一至三句话概括本来源版本>
