---
name: pan123-cli
description: 使用 pan123 命令行工具操作 123 云盘官方 OpenAPI，包括文件检索、上传下载、分享、离线任务、直链、图片及转码，并处理鉴权、分页和异步任务。用户要求管理 123 云盘或编写 pan123 自动化脚本时使用。
---

# 123 云盘 CLI

使用 Python 命令 `pan123` 完成用户授权的云盘任务。此 Skill 只提供操作知识，不包含 CLI 运行时、账号或权限。

## 开始

1. 运行 `pan123 --version` 确认可执行文件存在。尚未安装时使用 `uv tool install git+https://github.com/vorekkk/123Pan-CLI.git`（Python >=3.12）；PyPI 版本发布后可使用 `uv tool install pan123-cli`。不要把 npm Skill 包当作 CLI。
2. 缺少鉴权时让用户在本地终端运行 `pan123 setup`，或在进程环境设置 `PAN123_CLIENT_ID`、`PAN123_CLIENT_SECRET`。不要要求用户把 Secret、token、分享密码贴到聊天，也不要把它们写入命令参数、仓库或日志。
3. 先读 [配置和输出](references/configuration.md)。根据任务读 [工作流程](references/workflows.md)，再查 [完整命令](references/commands.md)。未确定参数时执行该命令的 `--help`，实际安装版本优先于参考资料。
4. 脚本使用 `--json --no-progress`，检查退出码及 `ok`。失败响应中的 `error.kind`、`api_code`、`trace_id`用于诊断，不重复执行可能已成功的写请求。

## 任务选择

- 文件查找、文件夹、复制/移动/重命名、上传/下载：[工作流程](references/workflows.md)，命令 `file ...`。
- 分享及付费分享：命令 `share ...`，核对密码、期限、流量和收费字段。
- 离线下载：命令 `offline ...`，创建后查询任务状态，不把提交成功当作下载完成。
- 直链空间、流量、黑名单、缓存：命令 `directlink ...`，需要账号权益；链接本身可能授予访问能力。
- 图片及转码：命令 `image ...`、`transcode ...`；异步状态查询使用实际命令提供的 `--wait`。
- 账号与鉴权：命令 `user ...`、`auth ...`、`oauth ...`。开发者与 OAuth 凭据不可混用。
- 底层协议、字段或版本差异：[API 映射](references/api-mapping.md)，必要时读 `references/api-source/` 内对应官方资料快照。

## 操作约束

先确认业务对象：列表/详情读取 ID，再执行用户请求的操作；不能按名称推测 file ID。删除、覆盖、永久删除、清空回收站、计费设置须属于用户明确授权范围；CLI 的确认参数不代表新增授权。`--yes`仅在已授权且已核对目标的自动化流程中使用。

优先高层上传下载命令及推荐 V2 接口。分页使用支持的 `--all`，不能把一页结果当完整云盘。不要假造客户端 IP、绕过权益或把官方域名校验关掉来解决报错。

上传后读取详情核对 ID、名称、大小；下载成功以命令完成及本地校验为准。异步任务以终态成功为准，超时表示尚未确认完成。具体命令、字段与官方限制都在完整命令及 API 映射中。

## 资料与验证边界

本 Skill 与 CLI 版本绑定，完整参数来自实际 parser/catalog。官方 API 资料快照日期为 2026-09-11，功能覆盖和真实联调情况来自仓库 2026-10-14 的覆盖清单；快照不能证明当前服务行为。映射中 `not_verified` 表示未真实验证，离线契约通过不代表账号拥有权益。遇到与快照不符的响应，保留脱敏错误并查当前官方文档，不自行猜字段。

Skill 安装不配置账号，也不自动执行云盘写操作。管理本地安装使用 `pan123 skill install|status|uninstall`；npm 分发使用 `npx pan123-cli-skill install --agent codex`。见 [配置和输出](references/configuration.md)。
