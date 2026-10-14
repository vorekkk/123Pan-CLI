# 123Pan CLI

直接调用 123 云盘官方 OpenAPI 的独立命令行工具，当前版本 **0.1.0**。支持 Python 3.12+，面向 macOS、Windows、Linux 的 x86_64 / ARM64。

已实现官方快照的 **72 个独立 HTTP 接口**及其命令变体，涵盖认证、OAuth、文件管理、分享、离线下载、用户信息、直链、图床、视频转码。普通文件的列表、上传、分片、秒传、下载已完成真实账户验证；其他业务域的真实验证状态见覆盖清单。

## 安装

仓库公开。`uv` / `pipx` 的安装命令会自动建立隔离环境，并把 `pan123` 放进 PATH，不需要克隆或手动建虚拟环境：

```bash
uv tool install pan123-cli          # PyPI 首发后可用
pipx install pan123-cli             # 同上
```

在 PyPI 首发之前，把包名换成仓库地址即可，效果相同：

```bash
uv tool install git+https://github.com/vorekkk/123Pan-CLI.git
pan123 --help
```

`pipx install git+https://github.com/vorekkk/123Pan-CLI.git` 等价可用；发布流程见[发布到 PyPI](./docs/发布.md)。若偏好源码目录，也可以克隆后用虚拟环境安装：

```bash
git clone https://github.com/vorekkk/123Pan-CLI.git
cd 123Pan-CLI
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/pan123 --help
```

Windows 源码安装使用 `py -3 -m venv .venv`，前缀分别为 `.venv\Scripts\python.exe` 与 `.venv\Scripts\pan123.exe`。详细的 PowerShell、cmd、pipx、wheel 用法见[安装与使用](./docs/安装与使用.md)。此版本是 Python 包，未提供无需 Python 的独立可执行程序；也尚未发布到 PyPI，因此安装命令需要带 `git+` 地址。

## 开始使用

首次在交互终端运行业务命令时，CLI 会引导输入 `PAN123_CLIENT_ID` 和隐藏的 `PAN123_CLIENT_SECRET`，鉴权验证通过后保存到用户私有凭据文件，并安装 AI Skill。也可以主动运行：

```bash
pan123 setup
pan123 file list --parent-id 0 --all --json
pan123 file upload --file './报告.pdf' --parent-id 123456
pan123 file download --file-id 123456 --output './报告副本.pdf'
```

环境变量或显式 `--env-file` 仍可覆盖保存的凭据。帮助、版本、`--json` 和非交互执行不会弹出向导；自动化任务预先配置环境变量。Secret 不写入普通 `config.json`。

### AI Skill 与 npm

CLI 首次交互运行会自动安装标准 `pan123-cli` Skill，检测 Codex、Claude Code、Cursor；多个目标时可多选。Skill 包含全部命令、API 字段映射和官方资料快照。也可独立安装：

```bash
npm i -g pan123-cli-skill
npx pan123-cli-skill install --agent codex
pan123 skill install --agent claude --agent cursor --scope project
pan123 skill status --json
```

npm 包只安装 Skill，CLI 仍通过 uv/pipx 安装。npm 全局安装自动写入检测到工具的用户 Skill 目录，无工具时默认 Codex；本地 npm 依赖安装不自动写入。禁用安装脚本时运行 `pan123-skill install` 补装。

`--dest` 指定完整 Skill 目录；`--force` 备份后处理冲突。支持 `install`、`status`、`uninstall`，检测用户修改并保护内容。标准 GitHub Skill 源为 `skills/pan123-cli`。详细说明见 [Skill 配置与安装](./skills/pan123-cli/references/configuration.md)。

示例 ID 需换为自己的目录或文件 ID。`list`、`upload`、`download` 是根命令别名；所有帮助页面均可离线查看。变更命令按帮助要求确认或使用 `--yes`。stdout JSON 便于脚本消费，进度写入 stderr，下载在大小与 MD5 校验通过后才发布正式文件。

控制接口固定为 `https://open-api.123pan.com`；上传、下载连接官方返回的 HTTPS 地址。凭据保存在本机，OAuth 令牌单独管理。

若本机代理使用 Fake-IP DNS（198.18.0.0/15），可明确加入 `--allow-fake-ip`，或设置 `PAN123_ALLOW_FAKE_IP=true`。默认仍要求公开 DNS 地址，并保持原始主机的 TLS 证书验证。

## 文档

- [安装与使用](./docs/安装与使用.md)：所有平台安装、配置和常用命令。
- [发布到 PyPI](./docs/发布.md)：Trusted Publishing 配置、发版步骤、dry run 与回滚规则。
- [完整 CLI 命令参考](./docs/CLI完整命令参考.md)：各业务域的输入、API 字段与约束；运行参数以 `--help` 为准。
- [技术栈与开发文档](./docs/123Pan-CLI技术栈与开发文档.md)：模块、鉴权、传输、测试与发布。
- [API 覆盖清单](./docs/API覆盖清单.json)：87 篇资料、74 篇接口文档、72 个独立接口的实现与验证状态。
- [真实联调记录](./docs/真实联调记录.md)及[实施进度](./docs/实施进度.md)。
- [官方资料快照](./docs/api-source/_manifest.json)：采集于 2026-09-11；配额与权限仍以当前官方和账号返回为准。

## 开发

```bash
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check src tests
.venv/bin/python -m ruff format --check src tests
.venv/bin/python -m mypy src/pan123_cli
.venv/bin/python -m build
.venv/bin/python scripts/check_wheel.py
```

GitHub Actions 配置 Python 3.12 / 3.13 / 3.14 的四个操作系统 runner，另有 Linux / Windows ARM64 的手动验证。实际结果见[实施进度](./docs/实施进度.md)。
