---
status: accepted
date: 2026-08-26
---

# 内容 Vault 命名为项目名称

项目根目录承载工程文件与机器契约，内容 Vault 固定为项目内同名目录 `sutra-pavilion/`；Obsidian 只打开内容 Vault，以保持文件树仅包含知识内容、来源内容、上下文、收件箱和模板。该同名嵌套结构是唯一内容根，不提供其他内容根、符号链接、副本、自动探测或兼容 fallback。公开命令接收项目根目录并校验 `sutra-pavilion/`；直接传入内容 Vault 以 `PATH_IS_CONTENT_VAULT` 失败。
