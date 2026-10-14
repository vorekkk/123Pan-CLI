# 配置、输出和 Skill 管理

## 凭据

`pan123 setup` 在交互终端输入 `PAN123_CLIENT_ID` 和隐藏的 `PAN123_CLIENT_SECRET`，向官方服务获取 token 验证成功后原子保存。首次交互业务命令在缺少开发者凭据时自动启动向导；JSON、非交互、帮助和版本不提示。OAuth 不触发开发者向导。

私有文件位于平台用户配置目录 `123pan-cli/credentials.json`，通过 `pan123 setup` 返回的路径定位；Secret 不进入普通 `config.json`。设置优先级由低到高：私有凭据、所选 JSON 配置、显式 `--env-file`、进程环境、命令参数。JSON 配置禁止 Secret。`.env` 不会被隐式读取。优先配置 `PAN123_` 前缀，兼容 `CLIENT_ID`/`CLIENT_SECRET` 别名。

常用环境：`PAN123_AUTH_MODE=developer|oauth`、`PAN123_OAUTH_CLIENT_ID`、`PAN123_OAUTH_CLIENT_SECRET`、`PAN123_OAUTH_REDIRECT_URI`、`PAN123_CONFIG_FILE`、`PAN123_CACHE_DIR`、`PAN123_API_TIMEOUT`、`PAN123_TRANSFER_TIMEOUT`、`PAN123_READ_MAX_RETRIES`。token 缓存按身份隔离，`pan123 auth clear`只清本地 token，不删除私有凭据。

显式重配只在验证成功后更换凭据。环境变量仍优先：要使用新保存的凭据，清除冲突的旧环境变量。OAuth 的 secret/code/refresh-token 通过对应 `--*-stdin` 标志提供，完整参数见命令参考。不要打印这些输入。

## 脚本输出

`--json` 返回 `{ok, schema_version:1, command, data}`；失败返回 `{ok:false, schema_version:1, command, error}`。`error` 包含 kind、message、exit_code、retryable，部分包含 api_code、http_status、trace_id、details。不要仅凭 HTTP 200 判定业务成功。

退出码：0 成功；2 参数/配置/确认；3 鉴权；4 网络/HTTP/业务；5 本地 I/O/冲突；6 等待超时；7 协议/完整性；130 中断；未分类错误可能为 1。对照实际 `error.kind` 判断，不用退出码推测具体业务错误。

全局参数支持命令前后：`--json`、`--verbose`、`--no-progress`、`--yes`、`--config`、`--env-file`、`--cache-dir`、`--auth-mode`、`--timeout`、`--transfer-timeout`、`--allow-fake-ip`。verbose 诊断不能包含凭据；不要把完整下载 URL 或分享能力链接公开到日志。

## 安装 Skill

```sh
pan123 skill install --agent codex
pan123 skill install --agent claude --agent cursor --scope project
pan123 skill status --agent codex --json
pan123 skill install --dest /absolute/path/to/skills/pan123-cli
pan123 skill uninstall --agent cursor
npm i -g pan123-cli-skill
npx pan123-cli-skill install --agent codex
```

`--scope user`为默认。Codex 用户目录 `$CODEX_HOME/skills/pan123-cli`（未设置时 `~/.codex/skills/pan123-cli`），项目 `.agents/skills/pan123-cli`；Claude 用户 `~/.claude/skills/pan123-cli`，项目 `.claude/skills/pan123-cli`；Cursor 用户 `~/.cursor/skills/pan123-cli`，项目 `.cursor/skills/pan123-cli`。`--dest` 是完整目标目录，优先于 agent/scope。

安装器写入 `.pan123-skill.json` 摘要清单。未修改的托管版本可以升级和卸载；用户修改或非托管同名目录报告冲突。`--force` 在修改前备份为同级 `pan123-cli.backup-<id>`，请核对后使用。重复安装返回 unchanged。Skill 安装后在工具下一轮对话/重启后确认发现情况。

npm 全局安装自动安装到检测到的工具，未检测到默认 Codex；本地依赖安装不自动写入用户 Skill 目录。安装脚本关闭时，运行 `pan123-skill install` 或 `npx pan123-cli-skill install`。npm 包不安装 CLI 或配置账号。标准 GitHub Skill 安装源：仓库 `vorekkk/123Pan-CLI`，路径 `skills/pan123-cli`。
