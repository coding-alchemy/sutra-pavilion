---
schema_version: 1
id: <ULID>
title: <条目标题>
slug: <slug>
aliases: []
summary: <一至三句话摘要>
entry_type: <条目类型>
language: zh-CN
status: draft
verification_stage: lead
controversy_status: none
publish_license: private-use-only
external_ids: {}
name_forms:
  - id: <名称形式-id>
    text: <条目标题>
    language: zh-CN
    script: Hans
    display: true
    usage: <名称使用语境>
    translated_as: []
tags: []
search_terms:
  - <检索扩展词>
attributes:
  entity_kind: <实体子类型>
  date_label: <时间表述>
  date_certainty: <时间确定性>
relations: []
---

<!-- 模板说明：将占位项替换为具体值，保存为所在知识库的 entries/<slug>.md（Vault 相对路径，项目内位于 sutra-pavilion/）。entry_type 必须已登记于 contracts/knowledge/registry/entry-types.yaml；tags 必须已登记于 contracts/knowledge/registry/tags/；relations 引用知识对象 ULID。name_forms 是名称结构化真源：必须恰有一个 display: true 且其 text 等于 title，aliases 必须等于其余名称文本按序去重的投影（校验器强制）。神话研究域（myth-research）要求本模板的域公共字段；其他知识域可以省略 verification_stage / controversy_status / publish_license / name_forms。正文关键事实只能引用 Attestation，引用语法见 docs/design/project-structure.md 第 6.4 节。attributes 块默认为 figure 类型示例，使用其他条目类型时按 contracts/knowledge/schemas/domains/myth-research/entry-types/ 下对应 Schema 替换。完成后删除本注释。 -->

## 正文

<正文内容>
